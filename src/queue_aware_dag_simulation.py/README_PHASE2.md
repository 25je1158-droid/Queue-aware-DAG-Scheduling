# Phase 2 — Dynamic multi-vehicle MEC and DAG simulation

## What this phase adds

- Reads multiple vehicle trajectories from `sumo/mobility_trace.csv`.
- Updates each selected vehicle's position using the SUMO trace as simulation time advances.
- Creates one five-task DAG per vehicle, preserving the dependencies T1→T2, T1→T3, T2→T4, T3→T4, T4→T5.
- Checks which MEC servers are currently within coverage before offloading a ready task.
- Estimates upload delay and server workload when choosing a server.
- Models task states: new, uploading, queued, running, and done.
- Models a finite number of concurrent tasks per MEC server.
- Dynamically shares a server's CPU equally among its running tasks; the share changes when tasks start or finish.
- Produces task-level and server-level CSV results.

## Files to add

Copy `src/phase2_simulation.py` into the `src` folder of your existing repository. Do not overwrite your original `main.py` or other files for this phase. This Phase 2 simulator is a separate entry point so that the existing project remains available as a backup.

## Run from the repository root

```bash
pip3 install pandas networkx matplotlib
python3 src/phase2_simulation.py
```

Only Python's standard library is used by this Phase 2 entry point; the install command is retained for the rest of the repository's tools. The expected input is `sumo/mobility_trace.csv` with columns:

```text
time,vehicle,x,y,speed
```

## Output files

The program creates:

- `results/phase2_task_results.csv` — server assignment, upload time, queue wait, execution time, finish time and deadline indicator for each task.
- `results/phase2_server_summary.csv` — MEC CPU capacity, maximum waiting queue and busy time.

## Configuration

At the top of `src/phase2_simulation.py`:

- `MAX_VEHICLES = 20` controls how many vehicles are included. Start with 20; increase to 50 or 100 after confirming the run works.
- `TIME_STEP = 0.1` controls simulation granularity.
- `COVERAGE_RADIUS = 250.0` controls the modeled MEC coverage distance.
- `MAX_PARALLEL_TASKS = 2` controls how many tasks can run concurrently at each MEC server.

## Important modeling notes

This is a discrete-time simulation model, not a live SUMO/TraCI connection. It replays the vehicle positions recorded in the SUMO CSV trace. The radio path-loss, bandwidth, noise, CPU-sharing, and task workload values are simulation assumptions and should be documented in the report. The CPU allocation model is equal sharing among active tasks, not an optimization solver. The deadline value is currently a fixed 20 seconds per task and should be calibrated to the project's experiment design.

For a fair evaluation, use the same trace, workload seed, server capacities, and deadlines when comparing this proposed method with the baseline algorithms in Phase 3.
