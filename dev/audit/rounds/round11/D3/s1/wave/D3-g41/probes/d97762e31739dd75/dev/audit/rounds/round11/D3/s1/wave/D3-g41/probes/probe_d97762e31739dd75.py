#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor d97762e31739dd75 (box D3-g41, round 11, seat D3-s1).
# Metric: count of inputs on which ThermalModel._simulate_step_two_zone's next state (every ThermalState field) or its
#   _step_wood_refused differs between `dT_wood > dT_wood_cap` and `>=`, on a two-tank (4-way, wood tank) plant; plus the
#   forced tie: _two_tank_rates patched (both arms) to return dT_wood == dT_wood_cap == 0 with the wood tank at its cap.
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_d97762e31739dd75.py
# EXPECTED RESULT moved_inputs=0 count ; tie_moved=0 count (at the tie the cap assignment is a no-op and refused = 0)
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._simulate_step_two_zone, line 4003
#   `if dT_wood > dT_wood_cap:`.
# Perturbation: key d97762e31739dd75 CMP_BOUND `>` -> `>=`, in memory, patched onto ThermalModel. Direction if it moved:
#   refused heat 0 -> nonzero at the tie.
# Null control: baseline against itself.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g41 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB).
# Each RESULT is computed by calling the production symbol on the stated inputs, both arms in one process.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, types
from pathlib import Path
from unittest import mock

_T0W, _T0C = time.perf_counter(), time.process_time()


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402


def mutant(fn, old, new):
    """``fn`` re-compiled from its own source with the one-line mutant applied, bound to the live module globals."""
    src = textwrap.dedent(inspect.getsource(fn))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor moved: {o!r}"
    mod = sys.modules[fn.__module__]
    ns = {}
    exec(compile(src.replace(o, n, 1), mod.__file__, "exec"), dict(mod.__dict__), ns)
    f = ns[fn.__name__]
    g = types.FunctionType(f.__code__, mod.__dict__, f.__name__, f.__defaults__, f.__closure__)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


def outcome(fn, *a, **k):
    """('ok', value) or ('raise', exception type name)."""
    try:
        return ("ok", fn(*a, **k))
    except Exception as e:  # noqa: BLE001 - the exception type IS the measured outcome
        return ("raise", type(e).__name__)


def same(a, b):
    if a[0] != b[0]:
        return False
    if a[0] == "raise":
        return a[1] == b[1]
    x, y = a[1], b[1]
    if x is None or y is None:
        return x is None and y is None
    if hasattr(x, "__dataclass_fields__"):
        import dataclasses
        return all(same(("ok", getattr(x, f.name)), ("ok", getattr(y, f.name))) for f in dataclasses.fields(x))
    xa, ya = np.asarray(x), np.asarray(y)
    if xa.dtype == object or ya.dtype == object:
        return bool(x == y)
    return xa.shape == ya.shape and bool(np.array_equal(xa, ya, equal_nan=True))


def show(o):
    if o[0] == "raise":
        return f"raise:{o[1]}"
    v = o[1]
    if v is None:
        return "None"
    if isinstance(v, np.ndarray):
        return np.array2string(v, precision=6, separator=",").replace(" ", "")
    return repr(v)


def tail():
    w, c = time.perf_counter() - _T0W, time.process_time() - _T0C
    print(f"RESULT thread_factor={c / w if w > 0 else 0.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = "na"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = line.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

from custom_components.heatpump_optimizer import thermal_model as tm, defrost as dfr  # noqa: E402
TM = tm.ThermalModel
T_BUF = np.array([25.0, 35.0, 40.0, 50.0, 60.0])
OUTS = (-25.0, -10.0, -2.0, 0.0, 7.0, 15.0, 20.0, 26.9, 27.0, 27.5, 30.0, 35.0)


def batch(model, fn, out, hum, tb, elig):
    with mock.patch.object(TM, "_batch_cop", fn):
        return outcome(model._batch_cop, out, hum, tb, elig)


def derate(grid_fn, n=100):
    d = dfr.DefrostDerate(factors=dfr._grid(1.0), counts=dfr._grid(n))
    for i in range(len(d.factors)):
        for j in range(len(d.factors[i])):
            d.factors[i][j] = grid_fn(i, j)
    return d

mut = mutant(TM._simulate_step_two_zone, "            if dT_wood > dT_wood_cap:", "            if dT_wood >= dT_wood_cap:")
p = tm.ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual", wood_tank_configured=True)
assert p.two_tank_modelled, "fixture is not a two-tank plant"
CAP = tm.WOOD_TANK_MAX_TEMP


def step(fn, st, pw, out, dt, rates=None):
    model = TM(p)
    with mock.patch.object(TM, "_simulate_step_two_zone", fn):
        if rates is not None:
            with mock.patch.object(tm, "_two_tank_rates", rates):
                o = outcome(model._simulate_step_two_zone, st, pw, out, dt_hours=dt)
        else:
            o = outcome(model._simulate_step_two_zone, st, pw, out, dt_hours=dt)
    return o, getattr(model, "_step_wood_refused", None)


tried = moved = reached = null = 0
for wood in (CAP - 20.0, CAP - 1.0, CAP - 1e-9, CAP, CAP + 1.0):
    for buf in (30.0, 50.0, 70.0):
        for pw in (0.0, 1.0, 3.0):
            for out in (-10.0, 0.0, 10.0):
                for dt in (0.25, 1 / 12):
                    st = tm.ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0, slab_temperature=22.0,
                                         buffer_tank_temperature=buf, wood_tank_temperature=wood)
                    (b, rb), (m, rm) = step(TM._simulate_step_two_zone, st, pw, out, dt), step(mut, st, pw, out, dt)
                    tried += 1; reached += b[0] == "ok"
                    moved += not (same(b, m) and rb == rm)
                    n, rn = step(TM._simulate_step_two_zone, st, pw, out, dt)
                    null += not (same(b, n) and rb == rn)
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT inputs_ok={reached} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null} count")
real = tm._two_tank_rates
tie = lambda *a: (real(*a)[0], 0.0)  # noqa: E731 - dT_wood forced to the cap (0 at the cap)
st = tm.ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0, slab_temperature=22.0,
                     buffer_tank_temperature=50.0, wood_tank_temperature=CAP)
(b, rb), (m, rm) = step(TM._simulate_step_two_zone, st, 2.0, 0.0, 0.25, tie), step(mut, st, 2.0, 0.0, 0.25, tie)
print(f"RESULT tie_refused_baseline={rb!r} kWh")
print(f"RESULT tie_refused_mutant={rm!r} kWh")
print(f"RESULT tie_moved={int(not (same(b, m) and rb == rm))} count")
print(f"RESULT tie_state_ok={int(b[0] == 'ok')}")
tail()
