"""Reviewer's probe: do the two triaged divisor-floor mutants (R7, R8) differ
from the head on ANY input the public simulate_step accepts, and at which dt?
Runs the head's thermal_model with the floor patched in-process."""
import sys, re, types, importlib, math
sys.path[:0] = ["tests/hastub", "custom_components", "tests"]
import numpy as np
import heatpump_optimizer.thermal_model as tm
SRC = open(tm.__file__).read()
import inspect
def variant(old, new):
    fn = "_single_valve_rates" if "dT_cap" in old else "_tank_bounded_draw"
    fsrc = inspect.getsource(getattr(tm, fn)); assert fsrc.count(old) == 1
    ns = dict(tm.__dict__); exec(fsrc.replace(old, new), ns)
    return (fn, ns[fn])
ORIG = {f: getattr(tm, f) for f in ("_single_valve_rates", "_tank_bounded_draw")}
R7 = variant("    dT_cap = headroom_k / max(dt_hours, 1e-6)", "    dT_cap = headroom_k / dt_hours")
R8 = variant("        / max(dt_hours, 1e-6)\n    )\n    return np.minimum(drawn", "        / dt_hours\n    )\n    return np.minimum(drawn")
def step(mod, dt, buf, slab, power):
    for f, g in ORIG.items(): setattr(tm, f, g)
    if mod is not tm: setattr(tm, mod[0], mod[1])
    mod = tm
    p = mod.ThermalParameters(two_zone_enabled=False); p.mixing_valve_mode="manual"; p.buffer_tank_volume=750.0
    m = mod.ThermalModel(p)
    s = mod.ThermalState(room_temperature=20.0, upper_floor_temperature=20.0, lower_floor_temperature=20.0,
        slab_temperature=slab, outdoor_temperature=0.0, buffer_tank_temperature=buf, dhw_temperature=48.0)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            o = m.simulate_step(s, power, 0.0, dt_hours=dt)
            return (o.buffer_tank_temperature, o.slab_temperature, m._step_buffer_refused)
        except Exception as e:
            return ("raise", type(e).__name__)
pmax = tm.ThermalParameters().buffer_max_temp
cases = []
for dt in (0.25, 1e-3, 1e-6, 1e-7, 0.0):
    for (buf, slab, power, label) in ((pmax, 25.0, 5.0, "tank at max, charging"),
                                     (pmax - 1e-9, 25.0, 5.0, "tank 1e-9 K under max, charging"),
                                     (25.0, 25.0, 0.0, "tank == slab, idle"),
                                     (25.0 + 1e-9, 25.0, 0.0, "tank 1e-9 K over slab, idle")):
        h = step(tm, dt, buf, slab, power)
        for name, mod in (("R7", R7), ("R8", R8)):
            v = step(mod, dt, buf, slab, power)
            same = (h == v) or (all(isinstance(a, float) for a in h+v) and all((a == b) or (math.isnan(a) and math.isnan(b)) for a, b in zip(h, v)))
            print(f"RESULT dt={dt:g} {label:32s} {name} {'same' if same else 'DIFFERS'}  head={h} mutant={v}")
