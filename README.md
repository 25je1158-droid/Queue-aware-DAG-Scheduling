# GitHub Upload Instructions

1. Download and extract `Queue_Aware_DAG_Final_Project.zip`.
2. Open your existing GitHub repository.
3. Replace the repository contents with the extracted project contents, preserving the folder structure.
4. Remove old duplicate prototype files from the repository if they are still present in `src/`; the active entry points are the three Python files supplied in the new `src/` folder.
5. Make sure the `sumo/` folder is uploaded completely, especially `mobility_trace.csv`, `network.net.xml`, `routes.rou.xml` and `vec.sumocfg`.
6. Make sure the complete `report/`, `results/` and `tests/` folders are uploaded.
7. Commit the changes with a message such as `Complete queue-aware DAG MEC scheduling project`.

## Verify after uploading

From the repository root, run:

```bash
python -m pip install -r requirements.txt
python src/phase2_simulation.py
python src/algorithm_comparison.py
python src/run_sensitivity_experiments.py
pytest -q
```

Do not upload only the ZIP file as a single repository file. Extract it and upload the folders and files inside it.
