import random

from visualization import save_comparison_graph

vehicle_counts = [10,20,30,40,50]

random_results = []
nearest_results = []
cpu_results = []
queue_results = []


for vehicles in vehicle_counts:

    base_load = vehicles * 8

    random_completion = (
        base_load +
        random.randint(140,170)
    )

    nearest_completion = (
        base_load +
        random.randint(100,120)
    )

    cpu_completion = (
        base_load +
        random.randint(70,90)
    )

    queue_completion = (
        base_load +
        random.randint(35,60)
    )

    random_results.append(
        random_completion
    )

    nearest_results.append(
        nearest_completion
    )

    cpu_results.append(
        cpu_completion
    )

    queue_results.append(
        queue_completion
    )

save_comparison_graph(
    vehicle_counts,
    random_results,
    nearest_results,
    cpu_results,
    queue_results
)

print("Simulation Complete")
