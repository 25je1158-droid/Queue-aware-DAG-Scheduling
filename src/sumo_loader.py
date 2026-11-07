import pandas as pd

def load_trace():

    return pd.read_csv(
        "sumo/mobility_trace.csv"
    )

def get_first_vehicle(trace):

    first = trace.iloc[0]

    return {

        "id": first["vehicle"],

        "x": float(first["x"]),

        "y": float(first["y"]),

        "speed": float(first["speed"])

    }