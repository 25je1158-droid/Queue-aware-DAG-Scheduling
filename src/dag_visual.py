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

nx.draw(
    G,
    with_labels=True,
    node_size=3000
)

plt.savefig(
"results/dag.png"
)