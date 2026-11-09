import random

from communication import distance


def random_server(
    vehicle,
    servers
):

    return random.choice(
        servers
    )


def nearest_server(
    vehicle,
    servers
):

    return min(
        servers,
        key=lambda s:
        distance(vehicle,s)
    )


def max_cpu_server(
    vehicle,
    servers
):

    return max(
        servers,
        key=lambda s:s.cpu
    )
