from communication import distance, transmission_rate


def estimate_assignment(task, vehicle, server, task_ready_time):
    """Estimate upload, queue wait, execution and finish times."""
    d = distance(vehicle, server)
    if d > server.radius:
        return None

    rate = transmission_rate(d)
    if rate <= 0:
        return None

    upload_time = float(task["data_size"]) / rate
    upload_finish = task_ready_time + upload_time

    # A server can execute one task at a time in this first queue model.
    execution_start = max(upload_finish, server.available_at)
    queue_wait = max(0.0, server.available_at - upload_finish)

    execution_time = float(task["cpu_cycles"]) / server.cpu
    finish_time = execution_start + execution_time

    return {
        "server": server,
        "distance": d,
        "upload_time": upload_time,
        "queue_wait": queue_wait,
        "execution_start": execution_start,
        "execution_time": execution_time,
        "finish_time": finish_time,
        "total_delay": finish_time - task_ready_time
    }


def choose_server(task, vehicle, servers, task_ready_time=0.0):
    """Choose the feasible server that gives the earliest task finish time."""
    best = None

    for server in servers:
        result = estimate_assignment(
            task, vehicle, server, task_ready_time
        )
        if result is not None:
            if best is None or result["finish_time"] < best["finish_time"]:
                best = result

    if best is None:
        return None, None

    # Reserve the chosen server so later tasks see its updated queue.
    best["server"].reserve(
        best["execution_start"],
        best["finish_time"]
    )
    return best["server"], best
