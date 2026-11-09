import matplotlib.pyplot as plt

algorithms = [
'Random',
'Nearest',
'CPU',
'Queue Aware'
]

violations=[
18,
13,
9,
4
]

plt.figure(figsize=(8,5))

plt.bar(
algorithms,
violations,
color=[
'red',
'orange',
'gold',
'green'
]
)

plt.ylabel(
'Violation %'
)

plt.title(
'Deadline Violations'
)

plt.savefig(
'results/deadline_violation.png'
)

print('Saved')
