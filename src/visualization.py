import matplotlib.pyplot as plt

def save_comparison_graph(
    x,
    random_values,
    nearest_values,
    cpu_values,
    queue_values
):

    plt.figure(figsize=(9,6))

    plt.plot(
        x,
        random_values,
        marker='o',
        linewidth=2,
        label='Random'
    )

    plt.plot(
        x,
        nearest_values,
        marker='s',
        linewidth=2,
        label='Nearest MEC'
    )

    plt.plot(
        x,
        cpu_values,
        marker='^',
        linewidth=2,
        label='Highest CPU'
    )

    plt.plot(
        x,
        queue_values,
        marker='D',
        linewidth=2,
        label='Queue Aware'
    )

    plt.xlabel(
        'Number of Vehicles'
    )

    plt.ylabel(
        'Application Completion Time'
    )

    plt.title(
        'Completion Time Comparison'
    )

    plt.legend()

    plt.grid(True)

    plt.savefig(
        'results/completion_time.png'
    )

    plt.close()
