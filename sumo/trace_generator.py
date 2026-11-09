"""Generate sumo/mobility_trace.csv from the included SUMO scenario.

Run from the repository root with SUMO and its TraCI Python tools installed:
    python sumo/trace_generator.py
"""
from __future__ import annotations

import csv
import os
import shutil
import sys
from pathlib import Path

SUMO_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SUMO_DIR / "vec.sumocfg"
OUTPUT_FILE = SUMO_DIR / "mobility_trace.csv"

# SUMO commonly installs TraCI under $SUMO_HOME/tools.
sumo_home = os.environ.get("SUMO_HOME")
if sumo_home:
    tools_dir = Path(sumo_home) / "tools"
    if tools_dir.exists():
        sys.path.insert(0, str(tools_dir))

try:
    import traci
except ImportError as exc:
    raise SystemExit(
        "TraCI could not be imported. Install SUMO and add SUMO_HOME/tools "
        "to Python's import path. The included CSV trace can be used without SUMO."
    ) from exc

sumo_binary = os.environ.get("SUMO_BINARY") or shutil.which("sumo")
if not sumo_binary:
    raise SystemExit(
        "The SUMO executable was not found. Add 'sumo' to PATH or set SUMO_BINARY."
    )

if not CONFIG_FILE.exists():
    raise SystemExit("SUMO configuration not found: {}".format(CONFIG_FILE))

traci.start([sumo_binary, "-c", str(CONFIG_FILE)])
try:
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time", "vehicle", "x", "y", "speed"])

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            sim_time = traci.simulation.getTime()
            for vehicle_id in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(vehicle_id)
                speed = traci.vehicle.getSpeed(vehicle_id)
                writer.writerow([sim_time, vehicle_id, x, y, speed])
finally:
    traci.close()

print("SUMO mobility trace generated:", OUTPUT_FILE)
