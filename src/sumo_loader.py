import pandas as pd

def load_trace():

    return pd.read_csv(
        "sumo/mobility_trace.csv"
    )

def get_vehicle_snapshot(
    trace,
    vehicle_id
):

    rows = trace[
        trace["vehicle"] == vehicle_id
    ]

    if len(rows) == 0:
        return None

    return rows.iloc[0]