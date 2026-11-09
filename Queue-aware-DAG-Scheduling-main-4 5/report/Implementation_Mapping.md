# Mapping of the Mid-Evaluation Report to the GitHub Implementation

| Report requirement | Implementation location | What it does |
|---|---|---|
| SUMO vehicle mobility | `sumo/mobility_trace.csv`, `sumo/trace_generator.py` | Stores and optionally regenerates vehicle time, position and speed samples. |
| DAG application model | `src/phase2_simulation.py` (`DAG_EDGES`) | Defines the five-task dependency graph. |
| Ready-task identification | `task_is_ready()` | Allows a task to be scheduled only when all predecessors are done. |
| Critical-path priority | `create_tasks()`, `critical_rank` | Computes task-specific remaining-path rank from task cycles and fastest MEC CPU. |
| Heterogeneous MEC resources | `SERVER_CONFIG` | Defines three MEC servers with different CPU capacities. |
| Vehicle-server distance | `distance()` | Computes Euclidean distance from the current SUMO position. |
| Wireless upload delay | `transmission_rate()` | Estimates a distance-dependent uplink rate and upload time. |
| Dynamic queue congestion | `MECServer.waiting`, `MECServer.running` | Maintains queued and executing task states. |
| Queue-aware server selection | `choose_server()` | Selects the feasible candidate with the lowest upload-plus-predicted-workload delay. |
| Mobility feasibility | `estimate_contact_time()` | Rejects assignments whose estimated service time exceeds estimated remaining contact time. |
| Dynamic CPU allocation | `MECServer.advance()` | Allocates server CPU in proportion to running-task critical-path ranks. |
| DAG application completion | `application_finish` and `phase2_application_results.csv` | Records completion after all five tasks finish. |
| Baseline evaluation | `src/algorithm_comparison.py` | Compares Random, Nearest, Highest CPU and Proposed Queue-Aware policies. |
| Repeated experiments | `src/run_sensitivity_experiments.py` | Runs three vehicle-count scenarios and three task-generation seeds. |
| Correctness checks | `tests/` | Tests precedence, rank, CPU capacity, channel behavior, contact-time and trace parsing. |

## Important implementation boundaries

- The main simulation uses a pre-generated SUMO CSV trace. It does not run a live SUMO-TraCI co-simulation.
- The queue prediction is an approximation based on remaining cycles in running and waiting tasks.
- The wireless channel is a simplified distance-dependent model.
- The contact-time estimate uses scalar speed and distance margin; vehicle heading is not present in the trace.
- CPU allocation is a critical-path-weighted heuristic, not a global optimizer.
- The baseline comparison changes the server-selection policy while keeping the task-generation procedure, DAG priority policy and CPU-sharing rule common to all policies. This makes the comparison focused on server selection.
- The current implementation models MEC offloading; it does not implement a local vehicle CPU execution alternative or task migration after offloading.
