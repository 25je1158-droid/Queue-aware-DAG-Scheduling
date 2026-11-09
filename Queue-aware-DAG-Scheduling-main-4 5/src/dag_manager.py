import networkx as nx

def build_dag():

    G = nx.DiGraph()

    G.add_edges_from([

        ('T1','T2'),
        ('T1','T3'),
        ('T2','T4'),
        ('T3','T4'),
        ('T4','T5')

    ])

    return G


def ready_tasks(G, completed):

    ready = []

    for task in G.nodes():

        if task in completed:
            continue

        predecessors = list(
            G.predecessors(task)
        )

        if all(
            p in completed
            for p in predecessors
        ):
            ready.append(task)

    return ready
