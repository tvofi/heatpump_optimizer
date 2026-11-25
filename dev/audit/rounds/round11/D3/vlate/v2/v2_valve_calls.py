"""VD3L V2 D3-s1-68: over every call simulate_step makes into _valve_two_zone_delivery (baseline
module, sweep of plants), evaluate the baseline and the whole-module mutant function on the SAME
arguments and count calls whose (q_rad+q_floor) differ. Also report the dt_hours seen."""
import os, sys, dataclasses, itertools
sys.path.insert(0, os.path.dirname(__file__))
from mutload import load
b, m = load("thermal_model", 2593, ") / max(dt_hours, 1e-6)", ") / min(dt_hours, 1e-6)")
mv = load("mixing_valve")
orig = b._valve_two_zone_delivery
stats = {"n": 0, "diff": 0, "maxd": 0.0, "dts": set()}
def spy(*a, **k):
    rb = orig(*a, **k); rm = m._valve_two_zone_delivery(*a, **k)
    stats["n"] += 1; stats["dts"].add(round(a[8], 5))
    d = abs((rb[0] + rb[1]) - (rm[0] + rm[1]))
    if d > 1e-12: stats["diff"] += 1; stats["maxd"] = max(stats["maxd"], d)
    return rb
b._valve_two_zone_delivery = spy
import random; random.seed(7)
for _i in range(600):
    vol=random.choice((2.0,5.0,20.0,60.0,150.0,300.0,800.0)); tbuf=21.0+random.choice((0.01,0.05,0.2,0.5,1,3,8,20)); target=random.choice((25.0,30.0,40.0,55.0)); steps=random.choice((1,4,16)); pw=random.choice((0.0,0.0,0.3,2.0)); out=random.choice((-25.0,-8.0,5.0))
    p = dataclasses.replace(b.ThermalParameters(), two_zone_enabled=True, mixing_valve_mode=mv.MODE_MANUAL,
                            mixing_valve_target=target, buffer_tank_volume=vol)
    model = b.ThermalModel(p)
    s = b.ThermalState(buffer_tank_temperature=tbuf, upper_floor_temperature=20.5, slab_temperature=21.0)
    for _ in range(steps):
        s = model.simulate_step(s, pw, out, dt_hours=random.choice((0.25, 1.0)))
print(f"RESULT 68_calls={stats['n']} calls_where_arms_differ={stats['diff']} max_delivered_delta_kw={stats['maxd']:.6f} dt_hours_seen={sorted(stats['dts'])}")
