from sumo_loader import load_trace, get_first_vehicle, get_vehicle_state
from vehicle import Vehicle
from mec_server import MECServer
from dag_manager import build_dag, ready_tasks
from scheduler import choose_server
from metrics import Metrics


def main():
    # 1. Read the complete SUMO trace. The first vehicle is used in this
    # first version, but its position is refreshed for each task's ready time.
    trace = load_trace()
    first_vehicle = get_first_vehicle(trace)
    vehicle_id = first_vehicle["id"]

    print("\nSUMO MOBILITY TRACE LOADED")
    print("Vehicle ID:", vehicle_id)
    print("Number of trace records:", len(trace))

    # 2. Create heterogeneous MEC servers.
    servers = [
        MECServer(1, 100, 100, 8e9, 250),
        MECServer(2, 300, 300, 12e9, 250),
        MECServer(3, 450, 150, 16e9, 250)
    ]

    # 3. Create the application DAG.
    graph = build_dag()
    tasks = {
        "T1": {"data_size": 10e6, "cpu_cycles": 8e9},
        "T2": {"data_size": 12e6, "cpu_cycles": 7e9},
        "T3": {"data_size": 15e6, "cpu_cycles": 10e9},
        "T4": {"data_size": 8e6, "cpu_cycles": 6e9},
        "T5": {"data_size": 5e6, "cpu_cycles": 4e9}
    }

    completed = set()
    finish_times = {}
    metrics = Metrics()

    print("\nQUEUE-AWARE ONLINE DAG SCHEDULING")
    print("-" * 65)

    # 4. Schedule tasks only after all their parent tasks have completed.
    while len(completed) < len(tasks):
        ready = ready_tasks(graph, completed)
        if not ready:
            raise RuntimeError("No ready task found. Check the DAG for a cycle.")

        for task_id in ready:
            predecessors = list(graph.predecessors(task_id))
            if predecessors:
                task_ready_time = max(finish_times[p] for p in predecessors)
            else:
                task_ready_time = 0.0

            # Use the vehicle's SUMO position at this task's ready time.
            state = get_vehicle_state(trace, vehicle_id, task_ready_time)
            vehicle = Vehicle(state["id"], state["x"], state["y"], state["speed"])

            server, result = choose_server(
                tasks[task_id], vehicle, servers, task_ready_time
            )

            if server is None:
                raise RuntimeError(
                    "No MEC server is within coverage for task " + task_id
                )

            finish_times[task_id] = result["finish_time"]
            completed.add(task_id)
            metrics.add_task_result(result)

            print("\nTask:", task_id)
            print("Ready at:          %.4f sec" % task_ready_time)
            print("Vehicle position:  (%.2f, %.2f)" % (vehicle.x, vehicle.y))
            print("Selected MEC:      %s" % server.id)
            print("Upload time:       %.4f sec" % result["upload_time"])
            print("Queue waiting:     %.4f sec" % result["queue_wait"])
            print("Execution start:   %.4f sec" % result["execution_start"])
            print("Execution time:    %.4f sec" % result["execution_time"])
            print("Task finish:       %.4f sec" % result["finish_time"])

    # 5. The application finishes when its final DAG task finishes.
    application_makespan = max(finish_times.values()) if finish_times else 0.0

    print("\n" + "=" * 65)
    print("APPLICATION FINISHED")
    print("=" * 65)
    print("Tasks completed:             %d" % len(completed))
    print("Application completion time: %.4f sec" % application_makespan)
    print("Average queue waiting time:  %.4f sec" % metrics.avg_queue_delay())
    print("Average upload time:         %.4f sec" % metrics.avg_upload_time())
    print("Average execution time:      %.4f sec" % metrics.avg_execution_time())

    print("\nMEC SERVER UTILIZATION (based on simulated makespan)")
    for server in servers:
        print(
            "Server %d: %.2f%%" %
            (server.id, server.utilization(application_makespan))
        )


if __name__ == "__main__":
    main()
