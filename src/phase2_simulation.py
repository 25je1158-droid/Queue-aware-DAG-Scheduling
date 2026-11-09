"""Phase 2: multi-vehicle, mobility-aware MEC/DAG simulation.

Run from the repository root:
    python3 src/phase2_simulation.py

The simulator reads sumo/mobility_trace.csv, creates one five-task DAG per
selected vehicle, schedules ready tasks to reachable MEC servers, models
uploading/queued/running states, and shares each server's CPU among active tasks.
"""

from __future__ import annotations

import csv
import math
import os
import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------- Configuration ----------------------------
RANDOM_SEED = 21
TIME_STEP = 0.1
MAX_SIMULATION_TIME = 500.0
MAX_VEHICLES = 20             # Increase to 50 or 100 for larger experiments.
TASKS_PER_VEHICLE = 5
COVERAGE_RADIUS = 300.0       # metres
BANDWIDTH = 20e6              # bits/second
TX_POWER = 0.2
NOISE_POWER = 1e-10
MAX_PARALLEL_TASKS = 2        # concurrent tasks per MEC server
OUTPUT_DIR = "results"
TRACE_PATH = os.path.join("sumo", "mobility_trace.csv")

SERVER_CONFIG = [
    # id, x, y, CPU cycles/second
    (1, 100.0, 100.0, 8e9),
    (2, 300.0, 300.0, 12e9),
    (3, 450.0, 150.0, 16e9),
]

DAG_EDGES = [("T1", "T2"), ("T1", "T3"), ("T2", "T4"),
             ("T3", "T4"), ("T4", "T5")]


@dataclass
class VehicleState:
    vehicle_id: str
    x: float
    y: float
    speed: float
    trace_rows: List[Tuple[float, float, float, float]]
    task_states: Dict[str, str] = field(default_factory=dict)
    task_completion: Dict[str, float] = field(default_factory=dict)
    application_start: Optional[float] = None
    application_finish: Optional[float] = None
    active: bool = True

    def update_position(self, sim_time: float) -> bool:
        """Use the latest SUMO sample at or before sim_time."""
        if sim_time > self.trace_rows[-1][0]:
            self.active = False
            return False
        latest = None
        for row in self.trace_rows:
            if row[0] <= sim_time:
                latest = row
            else:
                break
        if latest is None:
            self.active = False
            return False
        self.x, self.y, self.speed = latest[1], latest[2], latest[3]
        self.active = True
        return True


@dataclass
class Task:
    task_id: str
    vehicle_id: str
    data_bits: float
    total_cycles: float
    deadline: float
    state: str = "new"
    server_id: Optional[int] = None
    upload_remaining: float = 0.0
    remaining_cycles: float = 0.0
    ready_time: float = 0.0
    upload_start: float = 0.0
    execution_start: Optional[float] = None
    finish_time: Optional[float] = None
    queue_wait: float = 0.0
    upload_time: float = 0.0
    critical_rank: float = 0.0
    allocated_cpu_total: float = 0.0
    allocation_samples: int = 0


class MECServer:
    def __init__(self, sid: int, x: float, y: float, cpu: float):
        self.id = sid
        self.x = x
        self.y = y
        self.cpu = cpu
        self.waiting = deque()  # Task objects waiting for an execution slot
        self.running: List[Task] = []
        self.completed_cycles = 0.0
        self.busy_seconds = 0.0
        self.max_queue_length = 0

    def predicted_finish(self, cycles: float) -> float:
        queued_cycles = sum(t.remaining_cycles for t in self.waiting)
        active_cycles = sum(t.remaining_cycles for t in self.running)
        # Work-conserving estimate of active + queued + candidate workload.
        # This is a scheduling heuristic, not an exact queueing-theory solution.
        total_work = active_cycles + queued_cycles + max(0.0, cycles)
        return total_work / max(self.cpu, 1.0)

    def admit(self, task: Task, now: float) -> None:
        task.state = "queued"
        task.queue_wait = 0.0
        self.waiting.append(task)
        self.max_queue_length = max(self.max_queue_length, len(self.waiting))

    def advance(self, now: float, dt: float) -> List[Task]:
        """Execute queued tasks using critical-path-weighted CPU sharing."""
        while self.waiting and len(self.running) < MAX_PARALLEL_TASKS:
            task = self.waiting.popleft()
            task.state = "running"
            task.execution_start = now
            task.queue_wait = max(0.0, now - task.ready_time - task.upload_time)
            self.running.append(task)

        finished = []
        if self.running:
            # Tasks with longer remaining downstream paths receive a larger
            # fraction of the server CPU. Shares always sum to server capacity.
            weights = [max(task.critical_rank, 1e-9) for task in self.running]
            total_weight = sum(weights)
            self.busy_seconds += dt
            for task, weight in zip(list(self.running), weights):
                allocated_cpu = self.cpu * weight / total_weight
                task.allocated_cpu_total += allocated_cpu * dt
                task.allocation_samples += 1
                work = allocated_cpu * dt
                before = task.remaining_cycles
                task.remaining_cycles = max(0.0, before - work)
                self.completed_cycles += min(work, before)
                if task.remaining_cycles <= 0.0:
                    task.state = "done"
                    task.finish_time = now + dt
                    self.running.remove(task)
                    finished.append(task)
        return finished

    def utilization(self, simulation_end_time: float) -> float:
        if simulation_end_time <= 0.0:
            return 0.0
        return min(100.0, 100.0 * self.busy_seconds / simulation_end_time)


def load_trace(path: str) -> Dict[str, List[Tuple[float, float, float, float]]]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            "SUMO mobility trace not found: " + path +
            ". Run the SUMO trace generator or place mobility_trace.csv in sumo/."
        )
    grouped = defaultdict(list)
    with open(path, "r", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"time", "vehicle", "x", "y", "speed"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("mobility_trace.csv must contain: time, vehicle, x, y, speed")
        for row in reader:
            vid = str(row["vehicle"])
            grouped[vid].append((float(row["time"]), float(row["x"]),
                                 float(row["y"]), float(row["speed"])))
    for vid in grouped:
        grouped[vid].sort(key=lambda item: item[0])
    return dict(grouped)


def create_vehicles(trace: Dict[str, List[Tuple[float, float, float, float]]]) -> List[VehicleState]:
    ids = sorted(trace.keys(), key=lambda value: int(value) if value.isdigit() else value)
    chosen = ids[:MAX_VEHICLES]
    vehicles = []
    for vid in chosen:
        first = trace[vid][0]
        vehicle = VehicleState(vid, first[1], first[2], first[3], trace[vid])
        vehicle.application_start = first[0]
        vehicles.append(vehicle)
    return vehicles


def create_tasks(vehicles: List[VehicleState]) -> Dict[Tuple[str, str], Task]:
    rng = random.Random(RANDOM_SEED)
    all_tasks = {}
    for vehicle in vehicles:
        vehicle.task_states = {"T1": "new", "T2": "new", "T3": "new",
                               "T4": "new", "T5": "new"}
        for index in range(1, TASKS_PER_VEHICLE + 1):
            task_id = "T" + str(index)
            cycles = rng.uniform(2.0, 5.0) * 1e9
            data_mb = rng.uniform(2.0, 8.0)
            all_tasks[(vehicle.vehicle_id, task_id)] = Task(
                task_id, vehicle.vehicle_id, data_mb * 8e6, cycles,
                deadline=vehicle.application_start + 20.0,
                remaining_cycles=cycles
            )
    # Task-specific critical-path rank using estimated execution time on the
    # fastest MEC server: rank(i) = own_time(i) + max(rank(successor)).
    fastest_cpu = max(config[3] for config in SERVER_CONFIG)
    for vehicle in vehicles:
        memo = {}
        def rank(task_id: str) -> float:
            if task_id in memo:
                return memo[task_id]
            own_time = all_tasks[(vehicle.vehicle_id, task_id)].total_cycles / fastest_cpu
            children = successors(task_id)
            downstream = max((rank(child) for child in children), default=0.0)
            memo[task_id] = own_time + downstream
            return memo[task_id]
        for task_id in ("T1", "T2", "T3", "T4", "T5"):
            all_tasks[(vehicle.vehicle_id, task_id)].critical_rank = rank(task_id)
    return all_tasks


def predecessors(task_id: str) -> List[str]:
    return [source for source, target in DAG_EDGES if target == task_id]


def successors(task_id: str) -> List[str]:
    return [target for source, target in DAG_EDGES if source == task_id]


def estimate_contact_time(vehicle: VehicleState, server: MECServer) -> float:
    """Conservative contact-time estimate using current speed and radius margin.

    The trace currently provides speed but not heading relative to each server;
    treating motion as directly outward gives a conservative lower-bound estimate.
    A stationary vehicle is treated as having unlimited contact time for this step.
    """
    margin = max(0.0, COVERAGE_RADIUS - distance(vehicle, server))
    if vehicle.speed <= 0.1:
        return float("inf")
    return margin / vehicle.speed


def distance(vehicle: VehicleState, server: MECServer) -> float:
    return math.hypot(vehicle.x - server.x, vehicle.y - server.y)


def transmission_rate(distance_m: float) -> float:
    # Smooth distance-dependent path-loss model. This is a simulation model,
    # not a measured radio channel.
    gain = 1.0 / (1.0 + (distance_m / 50.0) ** 2)
    snr = TX_POWER * gain / NOISE_POWER
    return BANDWIDTH * math.log2(1.0 + snr)


def choose_server(task: Task, vehicle: VehicleState,
                  servers: List[MECServer]) -> Tuple[Optional[MECServer], float, float]:
    best = None
    best_score = float("inf")
    best_upload = 0.0
    for server in servers:
        d = distance(vehicle, server)
        if d > COVERAGE_RADIUS:
            continue
        upload = task.data_bits / max(1.0, transmission_rate(d))
        predicted = server.predicted_finish(task.total_cycles)
        contact_time = estimate_contact_time(vehicle, server)
        # Reject a server if the estimated upload plus execution/queue delay
        # exceeds the conservative remaining coverage time.
        if upload + predicted > contact_time:
            continue
        score = upload + predicted
        if score < best_score:
            best, best_score, best_upload = server, score, upload
    return best, best_score, best_upload


def task_is_ready(vehicle: VehicleState, task_id: str) -> bool:
    if vehicle.task_states.get(task_id) != "new":
        return False
    return all(vehicle.task_states.get(parent) == "done" for parent in predecessors(task_id))


def write_results(tasks: Dict[Tuple[str, str], Task], vehicles: List[VehicleState],
                  servers: List[MECServer], sim_end: float) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    task_path = os.path.join(OUTPUT_DIR, "phase2_task_results.csv")
    with open(task_path, "w", newline="") as handle:
        fields = ["vehicle", "task", "server", "state", "data_bits",
                  "cpu_cycles", "critical_path_rank", "upload_time", "queue_wait",
                  "execution_time", "average_allocated_cpu_cycles_per_second",
                  "finish_time", "deadline", "deadline_met"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for task in tasks.values():
            execution = (task.finish_time - task.execution_start
                         if task.finish_time is not None and task.execution_start is not None else 0.0)
            writer.writerow({
                "vehicle": task.vehicle_id, "task": task.task_id,
                "server": task.server_id if task.server_id is not None else "",
                "state": task.state, "data_bits": round(task.data_bits, 2),
                "cpu_cycles": round(task.total_cycles, 2),
                "critical_path_rank": round(task.critical_rank, 6),
                "upload_time": round(task.upload_time, 6),
                "queue_wait": round(task.queue_wait, 6),
                "execution_time": round(execution, 6),
                "average_allocated_cpu_cycles_per_second": round(
                    task.allocated_cpu_total / max(task.allocation_samples * TIME_STEP, TIME_STEP), 2
                ) if task.allocation_samples else 0.0,
                "finish_time": round(task.finish_time, 6) if task.finish_time is not None else "",
                "deadline": round(task.deadline, 6),
                "deadline_met": ("yes" if task.finish_time is not None and task.finish_time <= task.deadline else "no")
            })

    app_path = os.path.join(OUTPUT_DIR, "phase2_application_results.csv")
    with open(app_path, "w", newline="", encoding="utf-8") as handle:
        fields = ["vehicle", "application_start", "application_finish",
                  "application_completion_seconds", "all_tasks_completed"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for vehicle in vehicles:
            elapsed = (vehicle.application_finish - vehicle.application_start
                       if vehicle.application_finish is not None and vehicle.application_start is not None
                       else "")
            writer.writerow({
                "vehicle": vehicle.vehicle_id,
                "application_start": vehicle.application_start,
                "application_finish": vehicle.application_finish if vehicle.application_finish is not None else "",
                "application_completion_seconds": round(elapsed, 6) if elapsed != "" else "",
                "all_tasks_completed": "yes" if vehicle.application_finish is not None else "no",
            })

    summary_path = os.path.join(OUTPUT_DIR, "phase2_server_summary.csv")
    with open(summary_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["server", "cpu_cycles_per_second", "max_waiting_queue",
                         "busy_seconds", "completed_cycles", "utilization_percent"])
        for server in servers:
            writer.writerow([server.id, server.cpu, server.max_queue_length,
                             round(server.busy_seconds, 4),
                             round(server.completed_cycles, 2),
                             round(server.utilization(sim_end), 4)])

    completed_apps = [v for v in vehicles if v.application_finish is not None]
    app_times = [v.application_finish - v.application_start
                 for v in completed_apps if v.application_start is not None]
    completed_tasks = [t for t in tasks.values() if t.state == "done"]
    queue_values = [t.queue_wait for t in completed_tasks]
    upload_values = [t.upload_time for t in completed_tasks]
    exec_values = [(t.finish_time - t.execution_start) for t in completed_tasks
                   if t.finish_time is not None and t.execution_start is not None]
    violations = sum(1 for t in completed_tasks if t.finish_time > t.deadline)

    print("\n================ PHASE 2 RESULTS ================")
    print("Vehicles selected       :", len(vehicles))
    print("Tasks completed         :", len(completed_tasks), "/", len(tasks))
    print("Applications completed  :", len(completed_apps), "/", len(vehicles))
    print("Simulation end time     :", round(sim_end, 2), "seconds")
    print("Average application time:", round(sum(app_times) / len(app_times), 4) if app_times else "N/A")
    print("Average upload time     :", round(sum(upload_values) / len(upload_values), 4) if upload_values else "N/A")
    print("Average queue waiting   :", round(sum(queue_values) / len(queue_values), 4) if queue_values else "N/A")
    print("Average execution time  :", round(sum(exec_values) / len(exec_values), 4) if exec_values else "N/A")
    print("Deadline violations     :", violations)
    print("Results saved in        :", OUTPUT_DIR)
    print("=================================================")


def run_simulation() -> None:
    random.seed(RANDOM_SEED)
    trace = load_trace(TRACE_PATH)
    vehicles = create_vehicles(trace)
    if not vehicles:
        raise RuntimeError("No vehicles were found in the SUMO trace.")
    tasks = create_tasks(vehicles)
    servers = [MECServer(*config) for config in SERVER_CONFIG]

    # Uploading tasks are kept separately until their transmission finishes.
    uploading: List[Task] = []
    sim_time = min(vehicle.trace_rows[0][0] for vehicle in vehicles)
    total_tasks = len(tasks)

    print("PHASE 2: MULTI-VEHICLE DYNAMIC MEC/DAG SIMULATION")
    print("Vehicles:", len(vehicles), " | DAG tasks per vehicle:", TASKS_PER_VEHICLE)
    print("MEC servers:", len(servers), " | CPU sharing: critical-path-weighted allocation")

    while sim_time <= MAX_SIMULATION_TIME:
        # 1. Update vehicle positions using the SUMO trace at this time.
        for vehicle in vehicles:
            vehicle.update_position(sim_time)

        # 2. Finish uploads and move tasks into their MEC server queues.
        for task in list(uploading):
            task.upload_remaining -= TIME_STEP
            if task.upload_remaining <= 0:
                server = next(s for s in servers if s.id == task.server_id)
                server.admit(task, sim_time)
                uploading.remove(task)

        # 3. Schedule dependency-ready tasks using current vehicle positions,
        #    current coverage and current server queue/workload estimates.
        for vehicle in vehicles:
            if not vehicle.active:
                continue
            ready_ids = [tid for tid in ("T1", "T2", "T3", "T4", "T5")
                         if task_is_ready(vehicle, tid)]
            ready_ids.sort(
                key=lambda tid: tasks[(vehicle.vehicle_id, tid)].critical_rank,
                reverse=True,
            )
            for task_id in ready_ids:
                task = tasks[(vehicle.vehicle_id, task_id)]
                task.ready_time = sim_time
                server, _, upload = choose_server(task, vehicle, servers)
                if server is None:
                    continue  # retry at the next time step if a server becomes reachable
                task.server_id = server.id
                task.upload_time = upload
                task.upload_remaining = upload
                task.upload_start = sim_time
                task.state = "uploading"
                vehicle.task_states[task_id] = "uploading"
                uploading.append(task)

        # 4. Advance every MEC server; CPU is dynamically divided between
        #    currently running tasks and queued tasks start when slots open.
        for server in servers:
            finished = server.advance(sim_time, TIME_STEP)
            for task in finished:
                vehicle = next(v for v in vehicles if v.vehicle_id == task.vehicle_id)
                vehicle.task_states[task.task_id] = "done"
                vehicle.task_completion[task.task_id] = task.finish_time
                if all(state == "done" for state in vehicle.task_states.values()):
                    vehicle.application_finish = max(vehicle.task_completion.values())

        # Synchronize vehicle task states with task objects.
        for vehicle in vehicles:
            for task_id in vehicle.task_states:
                task = tasks[(vehicle.vehicle_id, task_id)]
                if task.state in ("queued", "running", "done"):
                    vehicle.task_states[task_id] = task.state

        if sum(1 for task in tasks.values() if task.state == "done") == total_tasks:
            break
        sim_time = round(sim_time + TIME_STEP, 10)

    write_results(tasks, vehicles, servers, sim_time)


if __name__ == "__main__":
    run_simulation()
