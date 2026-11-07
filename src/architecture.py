import matplotlib.pyplot as plt

steps = [
'Vehicle\nMobility',
'Connectivity',
'Ready\nTask',
'MEC\nSelection',
'Queue\nAware',
'Execution',
'Queue\nUpdate',
'DAG\nUpdate'
]

fig, ax = plt.subplots(figsize=(12,2))

for i,s in enumerate(steps):

    ax.text(
        i,
        0,
        s,
        bbox=dict(facecolor='lightblue')
    )

    if i < len(steps)-1:

        ax.arrow(
            i+0.25,
            0,
            0.4,
            0,
            head_width=0.05
        )

ax.axis('off')

plt.savefig(
'results/architecture.png'
)