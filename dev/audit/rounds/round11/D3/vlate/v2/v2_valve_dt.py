import os, sys, dataclasses
sys.path.insert(0, os.path.dirname(__file__))
from mutload import load
b, m = load("thermal_model", 2593, ") / max(dt_hours, 1e-6)", ") / min(dt_hours, 1e-6)")
mv = load("mixing_valve")
p = dataclasses.replace(b.ThermalParameters(), mixing_valve_mode=mv.MODE_MANUAL, mixing_valve_target=35.0, buffer_tank_volume=20.0)
st = b.ThermalState(buffer_tank_temperature=24.0, upper_floor_temperature=21.0, slab_temperature=22.0)
for dt in (0.25, 0.1, 0.05, 0.02, 0.01, 0.005):
    qb = sum(b._valve_two_zone_delivery(p, st, 0.0, 0.0, 0.0, 35.0, -10.0, 0.2, dt, False)[:2])
    qm = sum(m._valve_two_zone_delivery(p, st, 0.0, 0.0, 0.0, 35.0, -10.0, 0.2, dt, False)[:2])
    print(f"RESULT 68_direct dt={dt} base={qb:.6f} mut={qm:.6f} delta={qm-qb:.6f}")
# what substep dt does simulate_step use for this very plant/state?
seen = []
orig = b._valve_two_zone_delivery
def spy(*a, **k):
    seen.append(a[8]); return orig(*a, **k)
b._valve_two_zone_delivery = spy
p2 = dataclasses.replace(p, two_zone_enabled=True)
b.ThermalModel(p2).simulate_step(b.ThermalState(buffer_tank_temperature=24.0, upper_floor_temperature=21.0, slab_temperature=22.0), 0.0, -10.0, dt_hours=0.25)
print(f"RESULT 68_substep_dt_for_finder_plant={sorted(set(round(x,5) for x in seen))} calls={len(seen)}")
