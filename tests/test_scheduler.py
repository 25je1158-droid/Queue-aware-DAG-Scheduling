import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import phase2_simulation as sim


def make_vehicle():
    rows = [(0.0, 100.0, 100.0, 0.0), (1.0, 100.0, 100.0, 0.0)]
    vehicle = sim.VehicleState("test", 100.0, 100.0, 0.0, rows)
    vehicle.application_start = 0.0
    vehicle.task_states = {name: "new" for name in ("T1", "T2", "T3", "T4", "T5")}
    return vehicle


def test_dag_ready_tasks_respect_precedence():
    vehicle = make_vehicle()
    assert sim.task_is_ready(vehicle, "T1")
    assert not sim.task_is_ready(vehicle, "T2")
    assert not sim.task_is_ready(vehicle, "T4")
    vehicle.task_states["T1"] = "done"
    assert sim.task_is_ready(vehicle, "T2")
    assert sim.task_is_ready(vehicle, "T3")
    assert not sim.task_is_ready(vehicle, "T4")
    vehicle.task_states["T2"] = "done"
    vehicle.task_states["T3"] = "done"
    assert sim.task_is_ready(vehicle, "T4")


def test_task_specific_critical_path_ranks_are_computed():
    vehicle = make_vehicle()
    tasks = sim.create_tasks([vehicle])
    assert tasks[("test", "T1")].critical_rank > tasks[("test", "T2")].critical_rank
    assert tasks[("test", "T2")].critical_rank > tasks[("test", "T4")].critical_rank
    assert tasks[("test", "T4")].critical_rank > tasks[("test", "T5")].critical_rank


def test_cpu_allocation_never_exceeds_server_capacity():
    server = sim.MECServer(1, 0.0, 0.0, 100.0)
    first = sim.Task("T1", "v1", 100.0, 1000.0, 20.0,
                     state="queued", remaining_cycles=1000.0, critical_rank=2.0)
    second = sim.Task("T2", "v2", 100.0, 1000.0, 20.0,
                      state="queued", remaining_cycles=1000.0, critical_rank=1.0)
    server.admit(first, 0.0)
    server.admit(second, 0.0)
    server.advance(0.0, 0.1)
    allocated = (first.allocated_cpu_total + second.allocated_cpu_total) / 0.1
    assert allocated <= server.cpu + 1e-9
    assert abs(allocated - server.cpu) < 1e-9


def test_transmission_rate_is_positive_and_decreases_with_distance():
    near = sim.transmission_rate(10.0)
    far = sim.transmission_rate(200.0)
    assert near > 0
    assert far > 0
    assert near > far


def test_contact_time_is_infinite_for_stationary_vehicle():
    vehicle = make_vehicle()
    server = sim.MECServer(1, 100.0, 100.0, 1e9)
    assert sim.estimate_contact_time(vehicle, server) == float("inf")


def test_mobility_constraint_rejects_server_with_insufficient_contact_time():
    vehicle = sim.VehicleState(
        "moving", 290.0, 0.0, 10.0,
        [(0.0, 290.0, 0.0, 10.0), (1.0, 290.0, 0.0, 10.0)],
    )
    server = sim.MECServer(1, 0.0, 0.0, 1e9)
    task = sim.Task("T1", "moving", 1e6, 2e9, 20.0,
                    remaining_cycles=2e9, critical_rank=1.0)
    selected, _, _ = sim.choose_server(task, vehicle, [server])
    assert selected is None


def test_predicted_finish_increases_when_queue_workload_increases():
    server = sim.MECServer(1, 0.0, 0.0, 1e9)
    empty_estimate = server.predicted_finish(1e9)
    queued = sim.Task("T1", "v1", 1e6, 2e9, 20.0,
                      state="queued", remaining_cycles=2e9, critical_rank=1.0)
    server.admit(queued, 0.0)
    loaded_estimate = server.predicted_finish(1e9)
    assert loaded_estimate > empty_estimate
