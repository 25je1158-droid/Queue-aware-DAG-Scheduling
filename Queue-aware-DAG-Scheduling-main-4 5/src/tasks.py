import random

def generate_tasks():

    tasks = []

    for i in range(5):

        tasks.append({

            "id": f"T{i+1}",

            "data_size":
            random.randint(
                5,
                20
            )*1e6,

            "cpu_cycles":
            random.randint(
                5,
                15
            )*1e9,

            "deadline":
            random.randint(
                3,
                10
            )

        })

    return tasks