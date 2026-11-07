import matplotlib.pyplot as plt

steps = [

    "Vehicle\nMobility",

    "Connectivity",

    "Ready\nTasks",

    "Server\nSelection",

    "Queue\nAware",

    "Execution",

    "Queue\nUpdate",

    "DAG\nUpdate"

]

fig, ax = plt.subplots(
    figsize=(13,2)
)

for i, step in enumerate(steps):

    ax.text(
        i,
        0,
        step,
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round",
            facecolor="lightblue"
        )
    )

    if i < len(steps)-1:

        ax.arrow(
            i+0.3,
            0,
            0.4,
            0,
            head_width=0.04,
            length_includes_head=True
        )

ax.axis("off")

plt.savefig(
    "results/architecture.png"
)

print("Architecture saved")