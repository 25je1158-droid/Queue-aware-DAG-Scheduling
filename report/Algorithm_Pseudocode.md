# Proposed Queue-Aware Online DAG Scheduling Heuristic

```text
Input:
    SUMO mobility trace
    DAG G = (V, E) for each vehicle
    MEC server set M with CPU capacities F[m]
    communication coverage radius R
    simulation step Δt

Initialize:
    task states = NEW
    server waiting queues = empty
    server running sets = empty
    application release times from each vehicle's first trace sample

For each simulation time t:
    1. Read each active vehicle's latest position and speed from the trace.

    2. For each server:
           complete uploads whose upload timer has expired
           place those tasks in the server's waiting queue

    3. For each active vehicle:
           READY = tasks whose state is NEW and whose every predecessor is DONE
           sort READY by descending task-specific critical-path rank

           For each task i in READY:
               CANDIDATES = empty
               For each MEC server m:
                   calculate vehicle-server distance d
                   if d > coverage radius: continue
                   estimate uplink rate and upload time
                   estimate active + queued + candidate workload delay
                   estimate remaining vehicle-server contact time
                   if upload time + workload delay exceeds contact time: continue
                   add (m, predicted finish delay) to CANDIDATES

               if CANDIDATES is not empty:
                   choose server with minimum predicted upload + workload delay
                   mark task as UPLOADING and start its upload timer

    4. For each MEC server m:
           while a waiting task exists and a parallel slot is free:
               move the next waiting task to RUNNING
           if RUNNING is not empty:
               calculate each running task's critical-path weight
               allocate F[m] in proportion to those weights
               reduce remaining CPU cycles according to allocated CPU and Δt
               mark completed tasks DONE and record finish time

    5. If every task in an application's DAG is DONE:
           record application completion time

    6. Update task, queue, server and application metrics.

Output:
    task-level, application-level and server-level CSV metrics
    baseline comparison results and graphs
```

The procedure is an online greedy heuristic. It makes decisions from the current simulation state and does not search every possible global schedule.
