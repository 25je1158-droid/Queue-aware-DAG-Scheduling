# Objective 2: implementation scope and validation notes

## What the current prototype demonstrates

- Applications are represented as DAGs and tasks are released subject to predecessor completion.
- MEC servers have heterogeneous CPU capacities and finite parallel execution slots.
- Server selection estimates upload delay and queued/running workload.
- CPU capacity is shared among running tasks using critical-path-based weights.
- Vehicle positions are supplied by SUMO mobility traces.
- Baseline comparisons, sensitivity experiments, CSV metrics, and plots are provided.

## Correct description of the proposed method

The implemented scheduler is a **queue-aware online heuristic**. It jointly
considers task readiness/critical-path priority, server workload and upload
delay, and weighted CPU sharing. It should not be described as an exact global
optimizer unless a formal optimization solver and corresponding optimality
validation are added.

## SUMO integration scope

The supplied project currently supports trace-driven mobility replay. The
additional `sumo/live_trace_generator.py` file runs SUMO through TraCI and
generates a fresh mobility CSV. The MEC simulation then replays that CSV.
This is live SUMO trace generation, not synchronized SUMO–MEC co-simulation.

## Recommended validation before submission

1. Generate at least three independent mobility traces using different SUMO seeds.
2. Run the MEC simulation separately on each trace.
3. Preserve the seed, vehicle count, simulation duration, and configuration for every run.
4. Report mean and standard deviation for application completion time, queue waiting time,
   deadline violations, and server utilization.
5. Compare the proposed queue-aware method against every baseline under identical traces.
6. Include the generated trace and raw result CSV files with the submitted project.

Do not claim experimental results for runs that have not actually been executed.
