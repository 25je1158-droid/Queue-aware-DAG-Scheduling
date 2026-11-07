import matplotlib.pyplot as plt

def save_comparison_graph(
    x,
    random_values,
    nearest_values,
    cpu_values,
    queue_values
):

    plt.figure(
        figsize=(8,5)
    )

    plt.plot(
        x,
        random_values,
        marker='o',
        label='Random'
    )

    plt.plot(
        x,
        nearest_values,
        marker='o',
        label='Nearest'
    )

    plt.plot(
        x,
        cpu_values,
        marker='o',
        label='Max CPU'
    )

    plt.plot(
        x,
        queue_values,
        marker='o',
        label='Queue Aware'
    )

    plt.xlabel(
        'Number of Vehicles'
    )

    plt.ylabel(
        'Application Completion Time'
    )

    plt.legend()

    plt.grid(True)

    plt.savefig(
        'results/completion_time.png'
    )
