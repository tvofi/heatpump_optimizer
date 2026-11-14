"""Reviewer's instrument (not the finder's): on main's Carry 9 valve-top install
(tests/profiles.replay_install), is the branch's held-start reference main's
valve-top ceiling, is it a fixed point, and does a held-start solve book no start gap?
Run: PYTHONPATH=tests/hastub:tests:custom_components python3 held_valve_top_probe.py"""
import sys
from dataclasses import replace, fields
from datetime import datetime
import numpy as np
from heatpump_optimizer import optimizer as O, thermal_model as T
from profiles import replay_install

DISABLE = "--no-valve-top" in sys.argv
if DISABLE:  # perturbation: main's ceiling removed, the level bisection only
    O._held_at_valve_top = lambda *a, **k: None

def fdiff(a, b):
    out = 0.0
    for f in fields(a):
        x, y = getattr(a, f.name), getattr(b, f.name)
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            out = max(out, abs(float(x) - float(y)))
    return out

STARTS = {"at": (21.0, 22.0, 21.0, 21.0, 40.0), "cold": (19.2, 20.0, 19.5, 18.9, 28.0),
          "warm": (22.4, 24.0, 22.8, 22.0, 45.0)}
CASES = {"5": (5.0, {}), "-5": (-5.0, {}), "-15": (-15.0, {}), "-15 cap25": (-15.0, {"buffer_max_temperature": 25.0}),
         "null valve none -15": (-15.0, {"mixing_valve_mode": "none"}),
         "fallback pump1kW -15": (-15.0, {"heat_pump_max_power": 1.0})}
worst_idem = worst_gap = 0.0
for cname, (outdoor, over) in CASES.items():
    params = T.ThermalParameters.from_config(replay_install(**over))
    model = T.ThermalModel(params)
    opt = O.HeatPumpOptimizer(model, O.OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0))
    n = opt.config.n_steps
    w = O.WeatherSeries(outdoor_temps=np.full(n, outdoor), wind_speeds=np.full(n, 3.0),
                        precipitation=np.zeros(n), solar_radiation=np.zeros(n))
    for sname, (room, slab, up, low, tank) in STARTS.items():
        st = T.ThermalState(room_temperature=room, slab_temperature=slab, outdoor_temperature=outdoor,
                            upper_floor_temperature=up, lower_floor_temperature=low,
                            buffer_tank_temperature=tank, wood_tank_temperature=20.0)
        r1 = O._held_reference(model, st, w, None, 21.0)
        r2 = O._held_reference(model, r1, w, None, 21.0)
        top = O._thermostat_held_state(model, st, w, 21.0)
        idem = fdiff(r1, r2)
        gaps = {}
        for held in (True, False):
            seen = []
            real = opt._start_gap_cost
            def gap(*a, _real=real, **k):
                v = _real(*a, **k); seen.append(v); return v
            opt._start_gap_cost = gap
            from profiles import solve_inputs  # noqa
            inp = solve_inputs(initial_state=replace(st), prices=0.9 + 0.4*np.sin(np.arange(n)*2*np.pi/n),
                               outdoor_temps=w.outdoor_temps, wind_speeds=w.wind_speeds,
                               precipitation=w.precipitation, solar_radiation=w.solar_radiation,
                               start_time=datetime(2026, 1, 14, 12, 0))
            opt.optimize(inputs=replace(inp, held_start=held))
            opt._start_gap_cost = real
            gaps[held] = seen
        if not cname.startswith(("null", "fallback")):
            pass
        worst_idem = max(worst_idem, idem)
        worst_gap = max([worst_gap] + [abs(g) for g in gaps[True]])
        print(f"RESULT case={cname!r} start={sname} held_zones=({r1.room_temperature:.3f},{r1.upper_floor_temperature:.3f},"
              f"{r1.lower_floor_temperature:.3f}) tank={r1.buffer_tank_temperature:.2f} "
              f"zones_eq_thermostat_held={(r1.room_temperature, r1.upper_floor_temperature, r1.lower_floor_temperature) == (top.room_temperature, top.upper_floor_temperature, top.lower_floor_temperature)} "
              f"idempotence_maxdiff={idem:.3g} gap_held={[round(g, 9) for g in gaps[True]]} gap_measured={[round(g, 4) for g in gaps[False]]}")
print(f"RESULT summary valve_top_disabled={DISABLE} worst_idempotence={worst_idem:.3g} worst_held_gap={worst_gap:.3g}")
