from sumo_loader import (
    load_trace,
    get_first_vehicle
)

from vehicle import Vehicle
from mec_server import MECServer

from dag_manager import build_dag
from dag_manager import ready_tasks

from scheduler import choose_server

# ----------------------------------
# LOAD SUMO MOBILITY TRACE
# ----------------------------------

trace = load_trace()

vehicle_data = get_first_vehicle(
    trace
)

vehicle = Vehicle(

    vehicle_data["id"],

    vehicle_data["x"],

    vehicle_data["y"],

    vehicle_data["speed"]

)

print("\nSUMO VEHICLE LOADED")

print(
    f"Vehicle ID : {vehicle.id}"
)

print(
    f"Position   : ({vehicle.x:.2f}, {vehicle.y:.2f})"
)

print(
    f"Speed      : {vehicle.speed:.2f}"
)

# ----------------------------------
# MEC SERVERS
# ----------------------------------

servers = [

    MECServer(
        1,
        100,
        100,
        8e9,
        250
    ),

    MECServer(
        2,
        300,
        300,
        12e9,
        250
    ),

    MECServer(
        3,
        450,
        150,
        16e9,
        250
    )

]

# ----------------------------------
# DAG
# ----------------------------------

G = build_dag()

# ----------------------------------
# TASK DEFINITIONS
# ----------------------------------

tasks = {

    "T1": {
        "data_size": 10e6,
        "cpu_cycles": 8e9
    },

    "T2": {
        "data_size": 12e6,
        "cpu_cycles": 7e9
    },

    "T3": {
        "data_size": 15e6,
        "cpu_cycles": 10e9
    },

    "T4": {
        "data_size": 8e6,
        "cpu_cycles": 6e9
    },

    "T5": {
        "data_size": 5e6,
        "cpu_cycles": 4e9
    }

}

# ----------------------------------
# DAG EXECUTION
# ----------------------------------

completed = set()

application_completion_time = 0

print("\nQUEUE AWARE DAG SCHEDULING")
print("-" * 60)

while len(completed) < len(tasks):

    ready = ready_tasks(
        G,
        completed
    )

    print(
        f"\nReady Tasks : {ready}"
    )

    for task_id in ready:

        task = tasks[task_id]

        server, completion_time = choose_server(

            task,

            vehicle,

            servers

        )

        if server is None:

            print(
                f"{task_id}: No feasible MEC server"
            )

            continue

        server.add_task(
            task["cpu_cycles"]
        )

        application_completion_time += (
            completion_time
        )

        completed.add(task_id)

        print(
            f"\nTask {task_id}"
        )

        print(
            f"Vehicle Position "
            f"({vehicle.x:.2f}, "
            f"{vehicle.y:.2f})"
        )

        print(
            f"Assigned MEC : "
            f"{server.id}"
        )

        print(
            f"Queue Delay  : "
            f"{server.waiting_time():.4f}"
        )

        print(
            f"Completion   : "
            f"{completion_time:.4f} sec"
        )

    for s in servers:

        s.process()

# ----------------------------------
# FINAL RESULTS
# ----------------------------------

print("\n")
print("=" * 60)

print(
    "APPLICATION FINISHED"
)

print("=" * 60)

print(
    f"Total Completion Time: "
    f"{application_completion_time:.4f} sec"
)

print(
    f"Tasks Completed: "
    f"{len(completed)}"
)

print(
    f"SUMO Vehicle Used: "
    f"{vehicle.id}"
)