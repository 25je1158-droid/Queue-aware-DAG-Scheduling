import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

G.add_edges_from([
    ("T1","T2"),
    ("T1","T3"),
    ("T2","T4"),
    ("T3","T4"),
    ("T4","T5")
])

plt.figure(figsize=(6,4))

pos = nx.spring_layout(
    G,
    seed=42
)

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=3000,
    node_color="skyblue",
    arrows=True
)

plt.title(
    "DAG Task Structure"
)

plt.savefig(
    "results/dag.png"
)

print("DAG saved")