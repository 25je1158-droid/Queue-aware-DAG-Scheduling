from communication import distance
from communication import transmission_rate

def estimate_cost(
    task,
    vehicle,
    server
):

    d = distance(
        vehicle,
        server
    )

    upload_time = (
        task["data_size"] /
        transmission_rate(d)
    )

    queue_delay = (
        server.waiting_time()
    )

    computation_time = (
        task["cpu_cycles"] /
        server.cpu
    )

    total = (
        upload_time +
        queue_delay +
        computation_time
    )

    return total


def choose_server(
    task,
    vehicle,
    servers
):

    best_server = None

    best_cost = float("inf")

    for server in servers:

        d = distance(
            vehicle,
            server
        )

        if d > server.radius:

            continue

        cost = estimate_cost(
            task,
            vehicle,
            server
        )

        if cost < best_cost:

            best_cost = cost

            best_server = server

    return best_server,best_cost
