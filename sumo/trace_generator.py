import csv
import traci

traci.start([
    "sumo",
    "-c",
    "vec.sumocfg"
])

with open(
    "mobility_trace.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "time",
            "vehicle",
            "x",
            "y",
            "speed"
        ]
    )

    while traci.simulation.getMinExpectedNumber() > 0:

        traci.simulationStep()

        sim_time = traci.simulation.getTime()

        for vid in traci.vehicle.getIDList():

            x,y = traci.vehicle.getPosition(vid)

            speed = traci.vehicle.getSpeed(vid)

            writer.writerow(
                [
                    sim_time,
                    vid,
                    x,
                    y,
                    speed
                ]
            )

traci.close()

print("Trace Generated")