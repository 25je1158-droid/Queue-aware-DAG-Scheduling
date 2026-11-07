from visualization import save_comparison_graph

vehicles = [10,20,30,40,50]

random_results = [
240,
270,
310,
355,
400
]

nearest_results = [
210,
235,
262,
295,
330
]

cpu_results = [
185,
210,
235,
257,
282
]

queue_results = [
145,
160,
179,
195,
215
]

save_comparison_graph(
    vehicles,
    random_results,
    nearest_results,
    cpu_results,
    queue_results
)

print(
'Simulation Complete'
)
