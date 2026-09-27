"""R9-F2.3 evidence: every _deferred_energy_cost call in valve_storage_smart_write,
with its optimized_end's gap to the PUBLISHED trajectory's last state.
objective_identities.py reads only the LAST call; this prints them all.
Run from the tree under test: PYTHONPATH=tests/hastub python3 smart_write_calls.py"""
import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import golden
from heatpump_optimizer import optimizer as optmod
HPO = optmod.HeatPumpOptimizer
calls, results = [], []
_d, _o = HPO._deferred_energy_cost, HPO.optimize
def d(self, baseline_end, optimized_end, *a, **k):
    calls.append((optimized_end.__dict__.copy(), k.get("include_dhw", a[2] if len(a) > 2 else False)))
    return _d(self, baseline_end, optimized_end, *a, **k)
def o(self, *a, **k):
    r = _o(self, *a, **k); results.append(r); return r
HPO._deferred_energy_cost, HPO.optimize = d, o
golden.capture("valve_storage_smart_write", golden.SCENARIOS["valve_storage_smart_write"])
res = results[-1]
traj = {"room_temperature": res.room_temp_trajectory, "slab_temperature": res.slab_temp_trajectory,
        "upper_floor_temperature": res.upper_temp_trajectory, "lower_floor_temperature": res.lower_temp_trajectory,
        "buffer_tank_temperature": res.buffer_temp_trajectory}
for i, (end, inc) in enumerate(calls):
    gaps = {k: abs(float(end[k]) - float(v[-1])) for k, v in traj.items() if v and end.get(k) is not None}
    print(f"RESULT call{i}_include_dhw={bool(inc)}")
    print(f"RESULT call{i}_max_gap_to_published_end={max(gaps.values()):.6f} K")
print(f"RESULT deferred_calls={len(calls)} count")
