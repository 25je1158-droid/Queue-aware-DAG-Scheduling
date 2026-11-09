# SUMO scenario

The Python MEC simulation uses `mobility_trace.csv`, a pre-generated trace with columns `time, vehicle, x, y, speed`.

The scenario files are:
- `vec.sumocfg`: SUMO configuration;
- `network.net.xml`: road network;
- `routes.rou.xml`: vehicle routes;
- `trips.trips.xml`: trip definitions retained as a scenario input artifact;
- `trace_generator.py`: optional TraCI-based trace generator.

The supplied CSV trace is sufficient to run the project. SUMO is only needed if you want to regenerate it. See the root README for setup instructions.
