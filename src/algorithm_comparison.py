"""
Algorithm comparison for the queue-aware DAG scheduling project.

Run from the repository root:
    python3 src/algorithm_comparison.py

Compares four policies on the same SUMO mobility trace and same generated
workload:
  1. Random reachable MEC server
  2. Nearest reachable MEC server
  3. Highest-CPU reachable MEC server
  4. Proposed queue-aware earliest-finish-time server selection

This is a simulation-based comparison, not a proof of global optimality.
"""
from __future__ import annotations

import csv
import os
import random
from typing import Dict, List, Optional, Tuple

try:
    import phase2_simulation as sim
except ImportError as exc:
    raise ImportError(
        "Could not import src/phase2_simulation.py. Keep this file in the "
        "same src folder as phase2_simulation.py."
    ) from exc


OUTPUT_DIR = "results"
POLICIES = (
    "Random",
    "Nearest",
    "Highest CPU",
    "Proposed Queue-Aware",
)
POLICY_SEED = 2026


def choose_server(policy: str, task, vehicle, servers, rng):
    """Return (server, upload_duration) among currently reachable servers."""
    candidates = []
    for server in servers:
        distance = sim.distance(vehicle, server)
        if distance <= sim.COVERAGE_RADIUS:
            rate = max(1.0, sim.transmission_rate(distance))
            upload_time = task.data_bits / rate
            candidates.append((server, distance, upload_time))

    if not candidates:
        return None, 0.0

    if policy == "Random":
        server, _, upload_time = rng.choice(candidates)
        return server, upload_time

    if policy == "Nearest":
        server, _, upload_time = min(candidates, key=lambda item: item[1])
        return server, upload_time

    if policy == "Highest CPU":
        server, _, upload_time = max(candidates, key=lambda item: item[0].cpu)
        return server, upload_time

    # Proposed policy: minimize estimated upload + queue + execution finish delay.
    if policy == "Proposed Queue-Aware":
        server, _, upload_time = min(
            candidates,
            key=lambda item: item[2] + item[0].predicted_finish(task.total_cycles),
        )
        return server, upload_time

    raise ValueError("Unknown scheduling policy: " + policy)


def run_one_policy(policy: str, trace) -> dict:
    """Run a fresh simulation for one policy and return aggregate metrics."""
    vehicles = sim.create_vehicles(trace)
    if not vehicles:
        raise RuntimeError("No vehicles found in the SUMO mobility trace.")

    # create_tasks uses a fixed internal seed, so each policy receives identical
    # task sizes and CPU-cycle demands.
    tasks = sim.create_tasks(vehicles)
    servers = [sim.MECServer(*config) for config in sim.SERVER_CONFIG]
    uploading = []
    rng = random.Random(POLICY_SEED)

    sim_time = min(vehicle.trace_rows[0][0] for vehicle in vehicles)
    total_tasks = len(tasks)
    max_steps = int(sim.MAX_SIMULATION_TIME / sim.TIME_STEP) + 1

    for _ in range(max_steps):
        # Update every vehicle from its SUMO trace at the current simulation time.
        for vehicle in vehicles:
            vehicle.update_position(sim_time)

        # Finish communication uploads and put tasks into the selected MEC queue.
        for task in list(uploading):
            task.upload_remaining -= sim.TIME_STEP
            if task.upload_remaining <= 1e-12:
                server = next(s for s in servers if s.id == task.server_id)
                server.admit(task, sim_time)
                uploading.remove(task)

        # Schedule all dependency-ready tasks using the selected policy.
        for vehicle in vehicles:
            if not vehicle.active:
                continue
            for task_id in ("T1", "T2", "T3", "T4", "T5"):
                if not sim.task_is_ready(vehicle, task_id):
                    continue
                task = tasks[(vehicle.vehicle_id, task_id)]
                task.ready_time = sim_time
                server, upload_time = choose_server(
                    policy, task, vehicle, servers, rng
                )
                if server is None:
                    continue
                task.server_id = server.id
                task.upload_time = upload_time
                task.upload_remaining = upload_time
                task.upload_start = sim_time
                task.state = "uploading"
                vehicle.task_states[task_id] = "uploading"
                uploading.append(task)

        # Advance MEC execution and record completed DAG tasks.
        for server in servers:
            finished = server.advance(sim_time, sim.TIME_STEP)
            for task in finished:
                vehicle = next(
                    v for v in vehicles if v.vehicle_id == task.vehicle_id
                )
                vehicle.task_states[task.task_id] = "done"
                vehicle.task_completion[task.task_id] = task.finish_time
                if all(state == "done" for state in vehicle.task_states.values()):
                    vehicle.application_finish = max(
                        vehicle.task_completion.values()
                    )

        # Keep DAG state synchronized with actual task state.
        for vehicle in vehicles:
            for task_id in vehicle.task_states:
                task = tasks[(vehicle.vehicle_id, task_id)]
                if task.state in ("queued", "running", "done"):
                    vehicle.task_states[task_id] = task.state

        completed_count = sum(1 for task in tasks.values() if task.state == "done")
        if completed_count == total_tasks:
            break

        sim_time = round(sim_time + sim.TIME_STEP, 10)

    completed_apps = [
        v for v in vehicles if v.application_finish is not None
    ]
    app_times = [
        v.application_finish - (v.application_start or 0.0)
        for v in completed_apps
    ]
    completed_tasks = [t for t in tasks.values() if t.state == "done"]
    queue_waits = [t.queue_wait for t in completed_tasks]
    upload_times = [t.upload_time for t in completed_tasks]
    execution_times = [
        t.finish_time - t.execution_start
        for t in completed_tasks
        if t.finish_time is not None and t.execution_start is not None
    ]
    deadline_violations = sum(
        1 for t in completed_tasks if t.finish_time > t.deadline
    )
    server_utilizations = [
        min(1.0, server.busy_seconds / max(sim_time, sim.TIME_STEP))
        for server in servers
    ]

    return {
        "policy": policy,
        "vehicles": len(vehicles),
        "applications_completed": len(completed_apps),
        "application_completion_rate_percent":
            100.0 * len(completed_apps) / max(1, len(vehicles)),
        "tasks_completed": len(completed_tasks),
        "total_tasks": total_tasks,
        "task_completion_rate_percent":
            100.0 * len(completed_tasks) / max(1, total_tasks),
        "avg_application_completion_seconds":
            sum(app_times) / len(app_times) if app_times else "",
        "avg_queue_wait_seconds":
            sum(queue_waits) / len(queue_waits) if queue_waits else "",
        "avg_upload_seconds":
            sum(upload_times) / len(upload_times) if upload_times else "",
        "avg_execution_seconds":
            sum(execution_times) / len(execution_times) if execution_times else "",
        "deadline_violations": deadline_violations,
        "avg_server_busy_fraction_percent":
            100.0 * sum(server_utilizations) / len(server_utilizations),
        "simulation_end_seconds": sim_time,
    }


def write_csv(rows: List[dict]) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "algorithm_comparison.csv")
    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def create_graphs(rows: List[dict]) -> List[str]:
    """Create graphs from measured simulation outputs; skip cleanly if unavailable."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; CSV results were saved, graphs skipped.")
        return []

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    graph_files = []

    graph_specs = [
        ("avg_application_completion_seconds",
         "Average application completion time", "Seconds",
         "comparison_completion_time.png"),
        ("avg_queue_wait_seconds",
         "Average queue waiting time", "Seconds",
         "comparison_queue_wait.png"),
        ("avg_server_busy_fraction_percent",
         "Average MEC server busy fraction", "Percent",
         "comparison_server_utilization.png"),
        ("deadline_violations",
         "Number of task deadline violations", "Tasks",
         "comparison_deadline_violations.png"),
    ]

    labels = [row["policy"] for row in rows]
    for key, title, ylabel, filename in graph_specs:
        values = [
            float(row[key]) if row[key] != "" else 0.0 for row in rows
        ]
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(labels, values)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Scheduling policy")
        ax.tick_params(axis="x", rotation=12)
        fig.tight_layout()
        path = os.path.join(OUTPUT_DIR, filename)
        fig.savefig(path, dpi=160)
        plt.close(fig)
        graph_files.append(path)

    return graph_files


def main():
    trace_path = sim.TRACE_PATH
    trace = sim.load_trace(trace_path)
    print("QUEUE-AWARE DAG SCHEDULING: ALGORITHM COMPARISON")
    print("SUMO trace:", trace_path)
    print("Policies:", ", ".join(POLICIES))
    print("Each policy uses the same mobility trace and generated task workload.")
    print()

    rows = []
    for policy in POLICIES:
        print("Running:", policy)
        row = run_one_policy(policy, trace)
        rows.append(row)
        print(
            "  completed applications:",
            str(row["applications_completed"]) + "/" + str(row["vehicles"]),
            "| completed tasks:",
            str(row["tasks_completed"]) + "/" + str(row["total_tasks"]),
        )

    csv_path = write_csv(rows)
    graph_paths = create_graphs(rows)

    print("\n================ COMPARISON SUMMARY ================")
    for row in rows:
        app_time = row["avg_application_completion_seconds"]
        app_time_text = (
            str(round(app_time, 4)) + " s" if app_time != "" else "N/A"
        )
        print(
            "{:<24} completion={} | avg app time={} | queue wait={} s | "
            "deadline violations={}".format(
                row["policy"],
                str(row["applications_completed"]) + "/" + str(row["vehicles"]),
                app_time_text,
                round(row["avg_queue_wait_seconds"], 4)
                if row["avg_queue_wait_seconds"] != "" else "N/A",
                row["deadline_violations"],
            )
        )
    print("CSV:", csv_path)
    if graph_paths:
        print("Graphs:")
        for path in graph_paths:
            print(" -", path)
    print("====================================================")
    print("Note: results are simulation outputs under the configured assumptions.")


if __name__ == "__main__":
    main()
