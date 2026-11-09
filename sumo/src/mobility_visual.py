import pandas as pd
import matplotlib.pyplot as plt

trace = pd.read_csv(
    "sumo/mobility_trace.csv"
)

vehicles = trace["vehicle"].unique()

plt.figure(figsize=(8,6))

for v in vehicles[:10]:

    route = trace[
        trace["vehicle"] == v
    ]

    plt.plot(
        route["x"],
        route["y"],
        label=v
    )

plt.xlabel("X Position")

plt.ylabel("Y Position")

plt.title(
    "SUMO Vehicle Mobility"
)

plt.grid(True)

plt.savefig(
    "results/mobility_trace.png"
)

print(
    "Mobility plot saved"
)