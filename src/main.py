import random

from vehicle import Vehicle
from mec_server import MECServer

from dag_manager import build_dag
from dag_manager import ready_tasks

from scheduler import choose_server

# --------------------
# VEHICLE GENERATION
# --------------------

vehicles = []

for i in range(10):

    vehicles.append(

        Vehicle(

            i,

            random.randint(0, 500),

            random.randint(0, 500),

            random.randint(10, 25)

        )
    )

# --------------------
# MEC SERVER GENERATION
# --------------------

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

# --------------------
# DAG GENERATION
# --------------------

G = build_dag()

# --------------------
# TASK GENERATION
# --------------------

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

# --------------------
# DAG EXECUTION
# --------------------

completed = set()

vehicle = vehicles[0]

application_completion_time = 0

print("\nQUEUE AWARE DAG SCHEDULING")
print("-" * 50)

while len(completed) < len(tasks):

    ready = ready_tasks(
        G,
        completed
    )

    print(
        f"\nReady Tasks: {ready}"
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
                f"{task_id}: No server available"
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

            f"Task {task_id}"

            f" -> MEC {server.id}"

            f" | Queue Delay: "

            f"{server.waiting_time():.4f}"

            f" | Completion: "

            f"{completion_time:.4f}s"

        )

    for s in servers:

        s.process()

print("\n")
print("=" * 50)
print(
    "APPLICATION FINISHED"
)
print("=" * 50)

print(
    f"Total Completion Time: "
    f"{application_completion_time:.4f} sec"
)

print(
    f"Tasks Completed: "
    f"{len(completed)}"
)