"""Scenario grid for simulate_trajectory_batch mutants: baseline vs mutant max-abs output difference."""
import numpy as np
from mutlib import tm, mutant
from custom_components.heatpump_optimizer import mixing_valve as mv

KEY = "simulate_trajectory_batch"


def scenarios():
    rng = np.random.default_rng(7)
    out = []
    for wood in (False, True):
        for vol, bufT, ot_c, pw, dt in [(750.0, 69.5, -5.0, 3.0, 0.25), (750.0, 45.0, -10.0, 0.0, 0.25),
                                        (300.0, 30.0, 5.0, 4.0, 0.25), (750.0, 69.9, 10.0, 12.0, 0.25),
                                        (5.0, 45.0, -5.0, 0.5, 0.25), (750.0, 45.0, -5.0, 3.0, 1e-7),
                                        (750.0, 20.0, 15.0, 0.0, 0.25), (750.0, 90.0, -5.0, 6.0, 0.25)]:
            for zones in (True, False):
                kw = dict(two_zone_enabled=zones, buffer_tank_volume=vol, mixing_valve_mode=mv.MODE_MANUAL,
                          mixing_valve_target=23.0, buffer_max_temp=70.0, cop_flow_carnot=True,
                          max_electrical_power=12.0, radiator_power_fraction=0.5)
                if wood:
                    kw.update(wood_tank_configured=True, wood_tank_volume=500.0, topology_layout_override=tm.TOPOLOGY_TWO_TANK_4WAY)
                p = tm.ThermalParameters(**kw)
                st = tm.ThermalState(room_temperature=21.0, slab_temperature=25.0, upper_floor_temperature=21.0,
                                     lower_floor_temperature=21.0, buffer_tank_temperature=bufT, outdoor_temperature=ot_c,
                                     wood_tank_temperature=(55.0 if wood else None))
                n = 12
                P = np.vstack([np.full(n, pw), rng.uniform(0, max(pw, 1e-9), n), np.zeros(n)])
                w = tm.WeatherSeries(outdoor_temps=np.full(n, ot_c))
                out.append((p, st, P, w, dt))
    # boundary-hunting extras: tiny buffers, near-limit temperatures, tiny dt (dt<1e-6 is where max(dt,1e-6) bites)
    for wood in (False, True):
        for k in range(40):
            vol = float(rng.choice([0.5, 5.0, 40.0, 750.0]))
            bufT = float(rng.choice([20.0, 21.0, 21.0000001, 30.0, 69.9999995, 70.0, 70.0000005, 85.0]))
            dt = float(rng.choice([0.25, 1.0, 1e-7, 5e-7]))
            pw = float(rng.choice([0.0, 1e-9, 0.5, 6.0]))
            kw = dict(two_zone_enabled=bool(k % 2), buffer_tank_volume=vol, mixing_valve_mode=mv.MODE_MANUAL,
                      mixing_valve_target=float(rng.choice([21.0, 23.0, 40.0])), buffer_max_temp=70.0, cop_flow_carnot=True,
                      max_electrical_power=12.0, radiator_power_fraction=0.5)
            if wood:
                kw.update(wood_tank_configured=True, wood_tank_volume=500.0, topology_layout_override=tm.TOPOLOGY_TWO_TANK_4WAY)
            p = tm.ThermalParameters(**kw)
            wt = float(rng.choice([tm.WOOD_TANK_MAX_TEMP - 5e-7, tm.WOOD_TANK_MAX_TEMP - 1e-7, 60.0, 90.0])) if wood else None
            st = tm.ThermalState(room_temperature=21.0, slab_temperature=float(rng.choice([21.0, 25.0])), upper_floor_temperature=21.0,
                                 lower_floor_temperature=21.0, buffer_tank_temperature=bufT, outdoor_temperature=-5.0, wood_tank_temperature=wt)
            n = 4
            out.append((p, st, np.full((2, n), pw), tm.WeatherSeries(outdoor_temps=np.full(n, -5.0)), dt))
    return out


def run(fn, sc):
    p, st, P, w, dt = sc
    m = tm.ThermalModel(p)
    with np.errstate(all="ignore"):
        try:
            r = fn(m, st, P, w, dt_hours=dt, start_hour=7.0)
        except Exception as e:  # noqa
            return "EXC " + type(e).__name__
    return r


def diff(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return 0.0 if a == b else float("inf")
    d = 0.0
    for k in a:
        x, y = a[k], b[k]
        if x is None and y is None:
            continue
        x, y = np.asarray(x, float), np.asarray(y, float)
        if x.shape != y.shape:
            return float("inf")
        bad = ~((x == y) | (np.isnan(x) & np.isnan(y)))
        if bad.any():
            dd = np.abs(np.where(bad, x - y, 0))
            d = max(d, float(np.nan_to_num(dd, nan=np.inf).max()) if np.isfinite(dd[bad]).all() or True else 0)
    return d


def main(key, line, old, new, label):
    base = tm.ThermalModel.simulate_trajectory_batch
    mut = mutant("ThermalModel", KEY, line, old, new)
    mx, moved, tried = 0.0, 0, 0
    for sc in scenarios():
        a, b = run(base, sc), run(mut, sc)
        d = diff(a, b)
        tried += 1
        if d > 0:
            moved += 1
        mx = max(mx, d)
    nul = mutant("ThermalModel", KEY, line, old, old)
    nd = max(diff(run(base, sc), run(nul, sc)) for sc in scenarios())
    print(f"RESULT scenarios_tried={tried} count")
    print(f"RESULT scenarios_moved={moved} count")
    print(f"RESULT max_abs_diff={mx:.9g}")
    print(f"RESULT null_max_abs_diff={nd:.9g}")
