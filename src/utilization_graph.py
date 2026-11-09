import matplotlib.pyplot as plt

algorithms = [
'Random',
'Nearest',
'CPU',
'Queue Aware'
]

utilization = [
55,
67,
75,
88
]

plt.figure(figsize=(8,5))

plt.bar(
algorithms,
utilization
)

plt.ylabel(
'Utilization %'
)

plt.title(
'MEC Utilization'
)

plt.savefig(
'results/utilization.png'
)

print('Saved')
