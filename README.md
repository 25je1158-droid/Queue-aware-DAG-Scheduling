# Queue-Aware Online DAG Scheduling and Task Offloading in Vehicular Edge Computing

A simulation-based framework for scheduling dependent application tasks across heterogeneous Multi-Access Edge Computing (MEC) servers while considering server queue congestion, vehicle mobility, and wireless transmission delay.

## 1. Project Overview

Vehicular Edge Computing (VEC) enables vehicles to offload computationally intensive tasks to nearby edge servers instead of executing every task locally.

However, selecting an edge server based only on distance or available computing capacity may not provide good application completion time. A server that appears suitable may already have a long waiting queue. Task dependencies, changing vehicle connectivity, and competition for CPU resources can also affect execution time.

This project develops a **queue-aware online DAG scheduling and task-offloading framework** to address these challenges through simulation.

The framework considers task dependencies, server queue congestion, heterogeneous computing resources, CPU sharing, vehicle mobility, and wireless upload delay when making scheduling decisions.

## 2. Project Objective

**To design a queue-aware online DAG scheduling and task-offloading framework that aims to minimize end-to-end application completion time by jointly considering task scheduling, edge server selection, and resource allocation under dynamic queue congestion, heterogeneous resources, and task dependency constraints.**

### Key objectives

- Represent applications as Directed Acyclic Graphs (DAGs).
- Schedule tasks only after their predecessor tasks have completed.
- Select MEC servers by considering queue congestion and estimated execution time.
- Support heterogeneous MEC servers with different CPU capacities.
- Allocate CPU resources among concurrently running tasks.
- Consider wireless upload delay and vehicle-to-server connectivity duration.
- Compare the proposed queue-aware policy against baseline server-selection policies.
- Evaluate performance through simulation experiments and repeated runs.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Simulation and scheduling implementation |
| SUMO | Vehicle mobility simulation and trace generation |
| CSV | Mobility traces and experiment results |
| Matplotlib | Result visualization and graphs |
| Pytest | Automated testing |

## 4. System Architecture

The project follows a trace-driven simulation architecture.

```text
             SUMO Mobility Simulation
                       |
                       v
              Vehicle Mobility Trace
                       |
                       v
                Python MEC Simulator
                       |
                       v
               DAG Task Generation
                       |
                       v
             Dependency-Aware Scheduler
                       |
                       v
             Queue-Aware MEC Selection
                       |
                       v
              CPU Resource Allocation
                       |
                       v
              Task Execution Simulation
                       |
                       v
              Performance Evaluation
                       |
                       v
             CSV Results and Graphs
```

The SUMO mobility trace is generated separately and replayed by the Python simulation. The MEC simulation does not run SUMO through live TraCI co-simulation.

## 5. DAG Task Model

An application is represented as a Directed Acyclic Graph (DAG).

A DAG consists of:
- **Tasks (vertices):** Individual computational operations.
- **Dependencies (directed edges):** Execution-order constraints between tasks.

The current simulation uses a five-task application structure:

```text
             T1
            /  \
           T2  T3
            \  /
             T4
              |
             T5
```

The dependency relationships are:

- T1 must finish before T2 and T3 can start.
- T2 and T3 must both finish before T4 can start.
- T4 must finish before T5 can start.

A task becomes eligible for scheduling only when all its predecessor tasks have completed.

The simulation also calculates task-specific critical-path ranks using generated CPU-cycle demands and the fastest MEC CPU rate. These ranks help prioritize tasks that are important to the application's remaining execution path.

## 6. MEC Server Model

The simulation considers three heterogeneous MEC servers.

| MEC Server | CPU Capacity |
|---|---:|
| MEC Server 1 | 8 billion cycles/second |
| MEC Server 2 | 12 billion cycles/second |
| MEC Server 3 | 16 billion cycles/second |

Each server maintains its own task queue.

The simulation supports:
- Waiting tasks.
- Running tasks.
- Completed tasks.
- Up to two concurrently running tasks per MEC server.
- Dynamic CPU sharing among active tasks.

CPU allocation is critical-path-weighted. The allocated CPU shares are constrained so that their total does not exceed the corresponding server's CPU capacity.

## 7. Proposed Queue-Aware Scheduling Approach

The proposed scheduler is an online heuristic. It makes scheduling decisions using the current simulation state rather than solving an exact global optimization problem.

Its main decision stages are:

### Step 1: Identify ready tasks

The scheduler checks the DAG dependencies and identifies tasks whose predecessor tasks have completed.

### Step 2: Calculate task priorities

Task-specific critical-path ranks are calculated using task CPU-cycle demands and the fastest MEC CPU rate.

### Step 3: Evaluate MEC servers

Candidate servers are evaluated using factors including:

- Current queue congestion.
- Estimated waiting and execution time.
- Heterogeneous CPU capacity.
- Wireless upload delay.
- Estimated vehicle connectivity duration.

### Step 4: Check mobility feasibility

A conservative contact-time approximation is used to screen server choices based on estimated vehicle connectivity duration.

### Step 5: Allocate CPU resources

CPU resources are shared among active tasks using critical-path-weighted allocation, while respecting the server's CPU capacity.

### Step 6: Execute and update

The simulation updates task execution, queue states, task completion, and DAG readiness as simulation time advances.

**Important:** The proposed method is a heuristic for the scheduling problem. It is not an exact global optimizer, and the project does not claim a proof of global optimality.

## 8. Baseline Algorithms

The proposed Queue-Aware policy is compared with four server-selection policies:

| Algorithm | Description |
|---|---|
| Random | Selects a server randomly |
| Nearest | Selects a server based on distance |
| Highest CPU | Selects the server with the highest CPU capacity |
| Queue-Aware (Proposed) | Considers queue congestion and estimated execution-related factors |

The comparison uses the same mobility trace and generated workload for each policy.

## 9. SUMO Mobility Integration

SUMO is used to generate vehicle mobility information.

The generated mobility trace is stored in:

`sumo/mobility_trace.csv`

The Python MEC simulation reads and replays this CSV trace to incorporate vehicle mobility into the scheduling process.

### Important implementation detail

The current implementation uses **offline CSV trace replay**. SUMO is not controlled live during the MEC simulation.

The supplied mobility trace is already included in the repository, so installing SUMO is optional for running the existing Python simulation.

SUMO is required only if you want to generate a new mobility trace.

## 10. Repository Structure

```text
Queue-aware-DAG-Scheduling/
│
├── README.md
├── INSTRUCTIONS.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── phase2_simulation.py
│   ├── algorithm_comparison.py
│   └── run_sensitivity_experiments.py
│
├── sumo/
│   ├── vec.sumocfg
│   ├── network.net.xml
│   ├── routes.rou.xml
│   ├── trips.trips.xml
│   ├── mobility_trace.csv
│   └── trace_generator.py
│
├── tests/
│   ├── test_scheduler.py
│   └── test_trace.py
│
├── results/
│   ├── phase2_task_results.csv
│   ├── phase2_application_results.csv
│   ├── phase2_server_summary.csv
│   ├── algorithm_comparison.csv
│   ├── sensitivity_runs.csv
│   ├── sensitivity_summary.csv
│   └── generated graphs
│
└── report/
    ├── Abstract.txt
    ├── Conclusion.txt
    ├── Final_Report.md
    ├── Mathematical_Formulation.md
    ├── Implementation_Mapping.md
    ├── Experimental_Results.md
    └── figures/
```

## 11. Installation and Requirements

### Requirements

- Python 3.9 or newer.
- pip package manager.
- SUMO (optional, only for generating a new mobility trace).

### Step 1: Clone the repository

```bash
git clone https://github.com/25je1158-droid/Queue-aware-DAG-Scheduling.git
```

### Step 2: Enter the project directory

```bash
cd Queue-aware-DAG-Scheduling
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 12. How to Run the Project

Run all commands from the project root directory.

### A. Run the main multi-vehicle simulation

```bash
python src/phase2_simulation.py
```

This runs the main MEC scheduling simulation using the included SUMO mobility trace.

The simulation writes task-level, application-level, and server-level results under the `results/` directory.

### B. Run algorithm comparison

```bash
python src/algorithm_comparison.py
```

This compares the following policies:

1. Random
2. Nearest
3. Highest CPU
4. Proposed Queue-Aware

The comparison uses the same mobility trace and generated workload for each policy.

### C. Run sensitivity experiments

```bash
python src/run_sensitivity_experiments.py
```

The sensitivity experiment evaluates all four policies for:

- 10 vehicles.
- 20 vehicles.
- 40 vehicles.

It uses three task-generation seeds:

- 21
- 42
- 84

The script writes raw experiment runs and mean/standard-deviation summaries to the `results/` directory.

### D. Run automated tests

```bash
pytest -q
```

The tests cover:

- DAG dependency readiness.
- Critical-path ranking.
- CPU-capacity conservation.
- Transmission-rate behavior.
- Mobility contact-time estimation.
- SUMO mobility trace format.

## 13. SUMO Mobility Trace Regeneration (Optional)

The repository already includes a mobility trace. Therefore, SUMO is not required to run the existing Python simulation.

To generate a new trace:

1. Install SUMO.
2. Make sure the SUMO `tools` directory containing `traci` is available to Python.
3. Ensure the SUMO executable is available through `PATH`, or configure `SUMO_BINARY` with its full path.
4. Run:

```bash
python sumo/trace_generator.py
```

The generated trace replaces:

`sumo/mobility_trace.csv`

The Python simulation then replays the generated CSV trace offline.

## 14. Simulation Configuration

The current main simulation uses the following default assumptions:

| Parameter | Default Value |
|---|---:|
| Simulation time step | 0.1 seconds |
| Selected vehicles in main run | 20 |
| Tasks per application | 5 |
| Input data per task | 2–8 MB |
| CPU cycles per task | 2–5 billion cycles |
| Task deadline | 20 seconds after application release |
| MEC server CPU capacities | 8, 12 and 16 billion cycles/second |
| MEC coverage radius | 300 metres |
| Maximum concurrent running tasks per server | 2 |

These values are simulation assumptions. They should not be interpreted as measured properties of a real deployed vehicular network.

## 15. Performance Evaluation

The project evaluates scheduling performance using task-level, application-level, and server-level outputs.

The generated result files include:

| File | Purpose |
|---|---|
| `phase2_task_results.csv` | Task-level simulation results |
| `phase2_application_results.csv` | Application-level performance |
| `phase2_server_summary.csv` | MEC server-level summary |
| `algorithm_comparison.csv` | Comparison of scheduling policies |
| `sensitivity_runs.csv` | Individual sensitivity experiment runs |
| `sensitivity_summary.csv` | Mean and standard-deviation summaries |

For the measured values, graphs, and interpretation, refer to:

`report/Experimental_Results.md`

Results should be interpreted using the actual generated data. A performance improvement should not be described as statistically significant unless the repeated-run analysis supports that conclusion.

**Experiment limitation:** The current sensitivity scenarios reuse the same fixed SUMO mobility trace. Vehicle count and task-generation seed are varied, but separate traffic-density mobility traces are not generated for each scenario.

## 16. Mathematical Formulation and Implementation

The scheduling problem is motivated by minimizing end-to-end application completion time while considering:

- Task precedence constraints.
- MEC server selection.
- Server queue congestion.
- Heterogeneous CPU capacities.
- CPU resource allocation.
- Wireless transmission delay.
- Vehicle mobility and estimated connectivity duration.

The implementation uses an online heuristic to make scheduling decisions under these conditions.

For the detailed mathematical formulation and its connection to the implementation, refer to:

- `report/Mathematical_Formulation.md`
- `report/Implementation_Mapping.md`

## 17. Project Limitations

The current implementation has the following scope and limitations:

1. The proposed scheduler is a heuristic and does not guarantee global optimality.
2. SUMO integration uses offline CSV trace replay rather than live TraCI co-simulation.
3. Vehicle connectivity is estimated using a conservative contact-time approximation.
4. Sensitivity experiments reuse the same mobility trace rather than generating separate traffic-density traces.
5. Simulation parameters represent modeling assumptions and are not measurements from a real vehicular network.

These limitations provide directions for future development.

## 18. Future Enhancements

Possible extensions include:

- Live SUMO–TraCI integration with the MEC simulator.
- Generation of mobility traces under different traffic densities.
- More advanced resource-allocation optimization.
- Improved mobility prediction and connectivity estimation.
- Evaluation with larger DAGs and different application structures.
- Additional scheduling baselines and broader experimental scenarios.

## 19. References

The following IEEE Xplore documents were supplied as references in the project proposal:

1. [IEEE Xplore Document 11002512](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11002512)
2. [IEEE Xplore Document 10930689](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10930689)

For the final academic bibliography, verify and include the author names, paper titles, publication venue, year, and DOI from the original IEEE records or papers. Do not infer missing citation details.

## 20. Author and Project

**Project:** Queue-Aware Online DAG Scheduling and Task Offloading in Vehicular Edge Computing

**Repository:** [Queue-aware-DAG-Scheduling](https://github.com/25je1158-droid/Queue-aware-DAG-Scheduling)

This repository contains the simulation implementation, SUMO mobility trace files, experiment scripts, automated tests, generated results, and project documentation.

---

*This project is an academic simulation study of queue-aware DAG scheduling and task offloading in vehicular edge computing.*
