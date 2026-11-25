import os, sys, dataclasses, itertools
sys.path.insert(0, os.path.dirname(__file__))
from mutload import load
b, m = load("thermal_model", 2593, ") / max(dt_hours, 1e-6)", ") / min(dt_hours, 1e-6)")
mv = load("mixing_valve")
calls = {"n": 0}
orig = m._valve_two_zone_delivery
def spy(*a, **k):
    calls["n"] += 1
    return orig(*a, **k)
m._valve_two_zone_delivery = spy
def run(mod, vol, tbuf, target, steps):
    p = dataclasses.replace(mod.ThermalParameters(), two_zone_enabled=True, mixing_valve_mode=mv.MODE_MANUAL,
                            mixing_valve_target=target, buffer_tank_volume=vol)
    model = mod.ThermalModel(p)
    s = mod.ThermalState(buffer_tank_temperature=tbuf, upper_floor_temperature=20.5, slab_temperature=21.0)
    for _ in range(steps):
        s = model.simulate_step(s, 0.0, -8.0, dt_hours=0.25)
    return s.buffer_tank_temperature, s.room_temperature, s.upper_floor_temperature
best = (0, None)
n = 0
for vol, tbuf, target, steps in itertools.product((5.0, 20.0, 40.0, 100.0), (21.2, 22.0, 24.0, 28.0, 35.0), (30.0, 40.0, 50.0), (1, 4)):
    rb, rm = run(b, vol, tbuf, target, steps), run(m, vol, tbuf, target, steps)
    d = max(abs(x - y) for x, y in zip(rb, rm)); n += 1
    if d > best[0]: best = (d, (vol, tbuf, target, steps, rb, rm))
print(f"RESULT 68_sweep_cells={n} mutant_calls={calls['n']} max_state_delta={best[0]:.6f} at={best[1]}")
