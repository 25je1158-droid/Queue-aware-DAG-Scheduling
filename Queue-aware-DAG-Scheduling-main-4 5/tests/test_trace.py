import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import phase2_simulation as sim


def test_included_sumo_trace_has_required_fields_and_vehicles():
    trace = sim.load_trace(str(ROOT / "sumo" / "mobility_trace.csv"))
    assert trace
    assert len(trace) >= 20
    first_vehicle = next(iter(trace.values()))
    assert first_vehicle
    assert len(first_vehicle[0]) == 4
