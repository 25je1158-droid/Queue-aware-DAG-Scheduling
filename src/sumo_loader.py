import pandas as pd


def load_trace(path="sumo/mobility_trace.csv"):
    """Load and validate the SUMO vehicle mobility trace."""
    trace = pd.read_csv(path)
    required = ["time", "vehicle", "x", "y", "speed"]
    missing = [column for column in required if column not in trace.columns]
    if missing:
        raise ValueError("SUMO trace is missing columns: " + ", ".join(missing))

    trace = trace.copy()
    trace["time"] = pd.to_numeric(trace["time"])
    trace["x"] = pd.to_numeric(trace["x"])
    trace["y"] = pd.to_numeric(trace["y"])
    trace["speed"] = pd.to_numeric(trace["speed"])
    return trace.sort_values(["vehicle", "time"]).reset_index(drop=True)


def get_first_vehicle(trace):
    """Return the first vehicle's first recorded state (backward compatibility)."""
    first_id = trace.iloc[0]["vehicle"]
    return get_vehicle_state(trace, first_id, float(trace.iloc[0]["time"]))


def get_vehicle_state(trace, vehicle_id, simulation_time):
    """Get the recorded state closest in time to the requested simulation time."""
    vehicle_rows = trace[trace["vehicle"] == vehicle_id]
    if vehicle_rows.empty:
        raise ValueError("Vehicle ID not found in SUMO trace: " + str(vehicle_id))

    index = (vehicle_rows["time"] - simulation_time).abs().idxmin()
    row = trace.loc[index]
    return {
        "id": row["vehicle"],
        "time": float(row["time"]),
        "x": float(row["x"]),
        "y": float(row["y"]),
        "speed": float(row["speed"])
    }
