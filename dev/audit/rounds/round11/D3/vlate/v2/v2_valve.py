#!/usr/bin/env python3
"""VD3L V2 for D3-s1-68: whole-module mutant of thermal_model.py:2593 (max->min dt divisor),
driven through the PUBLIC ThermalModel.simulate_step on a two-zone, manual-valve, single-tank
plant with the pump off. Metric: the buffer tank's temperature after one 0.25 h step from a
tank 1 K above the emitter floor (min(upper, slab)); a store that delivers more than it holds
falls below that floor (energy from nowhere). Null: 300 L at 60 C, tank-bound cap never binds."""
import os, sys, dataclasses
sys.path.insert(0, os.path.dirname(__file__))
from mutload import load
b, m = load("thermal_model", 2593, ") / max(dt_hours, 1e-6)", ") / min(dt_hours, 1e-6)")
mv = load("mixing_valve")

def step(mod, vol, tbuf, steps=1):
    p = dataclasses.replace(mod.ThermalParameters(), two_zone_enabled=True, mixing_valve_mode=mv.MODE_MANUAL,
                            mixing_valve_target=40.0, buffer_tank_volume=vol)
    model = mod.ThermalModel(p)
    s = mod.ThermalState(buffer_tank_temperature=tbuf, upper_floor_temperature=20.5, slab_temperature=21.0)
    floor = min(s.upper_floor_temperature, s.slab_temperature)
    for _ in range(steps):
        s = model.simulate_step(s, 0.0, -8.0, dt_hours=0.25)
    return round(s.buffer_tank_temperature, 4), round(s.buffer_tank_temperature - floor, 4), round(s.room_temperature, 4)

for name, f in (("base", b), ("mut", m)):
    print(f"RESULT 68_{name}_tbuf,below_floor_margin,room={step(f, 40.0, 21.5)}")
nb, nm = step(b, 300.0, 60.0), step(m, 300.0, 60.0)
print(f"RESULT 68_null_delta_tbuf={abs(nb[0]-nm[0])}")
