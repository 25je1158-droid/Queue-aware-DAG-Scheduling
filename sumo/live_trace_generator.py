#!/usr/bin/env python3
"""
Generate a live SUMO/TraCI mobility trace in the CSV format used by
src/phase2_simulation.py.

Run from the repository root:
    python sumo/live_trace_generator.py

Optional:
    python sumo/live_trace_generator.py --gui --seed 42 --output sumo/mobility_trace_live.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path


def import_traci():
    """Import TraCI from SUMO_HOME when available, otherwise from Python."""
    sumo_home = os.environ.get("SUMO_HOME")
    if sumo_home:
        tools_dir = str(Path(sumo_home) / "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
    try:
        import traci  # type: ignore
        return traci
    except ImportError as exc:
        raise SystemExit(
            "TraCI could not be imported. Install SUMO and set SUMO_HOME, "
            "or install the Python traci package in this environment."
        ) from exc


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=repo_root / "sumo" / "vec.sumocfg",
        help="SUMO .sumocfg file (default: sumo/vec.sumocfg)",
    )
    parser.add_argument(
        "--output", type=Path, default=repo_root / "sumo" / "mobility_trace.csv",
        help="Output CSV (default overwrites sumo/mobility_trace.csv)",
    )
    parser.add_argument("--step-length", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--gui", action="store_true", help="Use sumo-gui")
    args = parser.parse_args()

    config = args.config.resolve()
    if not config.is_file():
        raise SystemExit(f"SUMO configuration not found: {config}")

    traci = import_traci()
    binary_name = "sumo-gui" if args.gui else "sumo"
    binary = os.environ.get("SUMO_BINARY", binary_name)

    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        binary, "-c", str(config),
        "--step-length", str(args.step_length),
        "--seed", str(args.seed),
        "--no-step-log", "true",
        "--duration-log.disable", "true",
    ]

    rows_written = 0
    # SUMO resolves network/route files relative to the configuration directory.
    previous_cwd = Path.cwd()
    os.chdir(config.parent)
    try:
        traci.start(command)
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["time", "vehicle", "x", "y", "speed"])
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                sim_time = float(traci.simulation.getTime())
                for vehicle_id in traci.vehicle.getIDList():
                    x, y = traci.vehicle.getPosition(vehicle_id)
                    speed = traci.vehicle.getSpeed(vehicle_id)
                    writer.writerow([
                        f"{sim_time:.3f}", vehicle_id,
                        f"{x:.6f}", f"{y:.6f}", f"{speed:.6f}",
                    ])
                    rows_written += 1
        traci.close()
    except Exception:
        try:
            traci.close()
        except Exception:
            pass
        raise
    finally:
        os.chdir(previous_cwd)

    print(f"Generated {rows_written} mobility samples: {args.output}")
    if rows_written == 0:
        print("WARNING: SUMO produced no vehicle samples; check routes and simulation time.")


if __name__ == "__main__":
    main()
