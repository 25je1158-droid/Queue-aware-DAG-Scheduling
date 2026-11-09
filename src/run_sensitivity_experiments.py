"""Run repeated-load experiments for the queue-aware DAG scheduler.

Run from the repository root:
    python src/run_sensitivity_experiments.py

This script reuses the same SUMO trace and compares all policies under
identical task workloads for each (vehicle-count, random-seed) scenario.
"""
from __future__ import annotations

import csv
import os
import statistics

import algorithm_comparison as comparison
import phase2_simulation as sim

VEHICLE_COUNTS = (10, 20, 40)
RANDOM_SEEDS = (21, 42, 84)
OUTPUT_DIR = "results"


def main() -> None:
    trace = sim.load_trace(sim.TRACE_PATH)
    raw_rows = []
    original_vehicle_limit = sim.MAX_VEHICLES
    original_seed = sim.RANDOM_SEED

    try:
        for vehicle_count in VEHICLE_COUNTS:
            for seed in RANDOM_SEEDS:
                sim.MAX_VEHICLES = vehicle_count
                sim.RANDOM_SEED = seed
                for policy in comparison.POLICIES:
                    print("Scenario: vehicles={}, seed={}, policy={}".format(
                        vehicle_count, seed, policy
                    ))
                    row = comparison.run_one_policy(policy, trace)
                    row["vehicle_count_scenario"] = vehicle_count
                    row["random_seed"] = seed
                    raw_rows.append(row)
    finally:
        sim.MAX_VEHICLES = original_vehicle_limit
        sim.RANDOM_SEED = original_seed

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_path = os.path.join(OUTPUT_DIR, "sensitivity_runs.csv")
    with open(raw_path, "w", newline="", encoding="utf-8") as handle:
        fields = ["vehicle_count_scenario", "random_seed"] + [
            key for key in raw_rows[0] if key not in ("vehicle_count_scenario", "random_seed")
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(raw_rows)

    metric_keys = (
        "avg_application_completion_seconds",
        "avg_queue_wait_seconds",
        "deadline_violations",
        "application_completion_rate_percent",
    )
    summary_rows = []
    for vehicle_count in VEHICLE_COUNTS:
        for policy in comparison.POLICIES:
            subset = [r for r in raw_rows
                      if r["vehicle_count_scenario"] == vehicle_count and r["policy"] == policy]
            row = {"vehicle_count_scenario": vehicle_count, "policy": policy,
                   "runs": len(subset)}
            for metric in metric_keys:
                values = [float(r[metric]) for r in subset if r[metric] != ""]
                row[metric + "_mean"] = statistics.mean(values) if values else ""
                row[metric + "_stdev"] = statistics.stdev(values) if len(values) > 1 else 0.0
            summary_rows.append(row)

    summary_path = os.path.join(OUTPUT_DIR, "sensitivity_summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    try:
        import matplotlib.pyplot as plt
        for metric, title, ylabel, filename in (
            ("avg_application_completion_seconds_mean", "Sensitivity: application completion time", "Seconds", "sensitivity_completion_time.png"),
            ("avg_queue_wait_seconds_mean", "Sensitivity: queue waiting time", "Seconds", "sensitivity_queue_wait.png"),
        ):
            fig, ax = plt.subplots(figsize=(9, 5))
            for policy in comparison.POLICIES:
                rows = [r for r in summary_rows if r["policy"] == policy]
                ax.plot([r["vehicle_count_scenario"] for r in rows],
                        [float(r[metric]) for r in rows], marker="o", label=policy)
            ax.set_title(title)
            ax.set_xlabel("Number of vehicles")
            ax.set_ylabel(ylabel)
            ax.legend()
            fig.tight_layout()
            fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=160)
            plt.close(fig)
    except ImportError:
        print("matplotlib is unavailable; CSV files were still generated.")

    print("Saved:", raw_path)
    print("Saved:", summary_path)


if __name__ == "__main__":
    main()
