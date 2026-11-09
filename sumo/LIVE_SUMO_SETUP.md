# Live SUMO–TraCI mobility trace generation

This add-on provides live SUMO execution through TraCI and writes the same
CSV schema consumed by `src/phase2_simulation.py`:

`time,vehicle,x,y,speed`

## Requirements

1. Install Eclipse SUMO, including `sumo` (and optionally `sumo-gui`).
2. Make the SUMO `tools` directory available to Python by setting `SUMO_HOME`,
   or install the Python TraCI package in the same Python environment.
3. Ensure the `sumo/vec.sumocfg`, `sumo/network.net.xml`, and
   `sumo/routes.rou.xml` files are present.

## Generate a live trace

From the project root:

```bash
python sumo/live_trace_generator.py
```

To view SUMO while it runs:

```bash
python sumo/live_trace_generator.py --gui
```

To preserve the existing trace and write a separate one:

```bash
python sumo/live_trace_generator.py --output sumo/mobility_trace_live.csv --seed 42
```

The default command overwrites `sumo/mobility_trace.csv`. Back up the existing
file first if you want to retain the original trace.

## Run the MEC/DAG simulation

The existing simulator reads `sumo/mobility_trace.csv` by default:

```bash
python src/phase2_simulation.py
```

If you generated `mobility_trace_live.csv`, either copy it over
`sumo/mobility_trace.csv` or change `TRACE_PATH` in
`src/phase2_simulation.py` to point to the new file.

## Important scope note

This add-on makes mobility-trace generation live through SUMO/TraCI. The
existing MEC simulator still consumes the resulting CSV as a trace-driven
input; it is not a fully synchronized, time-stepped SUMO–MEC co-simulation.
The scheduling policy remains a heuristic rather than a proof of globally
optimal joint scheduling, server selection, and CPU allocation. Describe
these distinctions accurately in the report.
