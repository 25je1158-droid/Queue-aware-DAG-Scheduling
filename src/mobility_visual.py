import pandas as pd
import matplotlib.pyplot as plt

trace = pd.read_csv(
    'sumo/mobility_trace.csv'
)

vehicles = trace['vehicle'].unique()

plt.figure(figsize=(8,6))

for vehicle in vehicles[:10]:

    route = trace[
        trace['vehicle'] == vehicle
    ]

    plt.plot(
        route['x'],
        route['y']
    )

plt.xlabel('X Position')
plt.ylabel('Y Position')

plt.title(
    'SUMO Vehicle Mobility Trace'
)

plt.grid(True)

plt.savefig(
    'results/mobility_trace.png'
)

print('Mobility plot saved')
