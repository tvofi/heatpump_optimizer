#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor c5e678a5d1812e40 (box D3-g41, round 11, seat D3-s1).
# Metric: ThermalModel._simulate_step_two_zone's next buffer temperature (or the exception) on a throttled single-tank
#   plant whose tank charges toward buffer_max_temp, across dt_hours including 0 and below the 1e-6 floor; count of
#   inputs that differ between `/ max(dt_hours, 1e-6)` and `/ (dt_hours)`.
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_c5e678a5d1812e40.py
# EXPECTED RESULT production_moved=0 count (dt_hours >= 1e-6: the floor is inert) ; dt0 and dt<1e-6 may move
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._simulate_step_two_zone, line 4019
#   `dT_cap = max(0.0, p.buffer_max_temp - T_buf) / max(dt_hours, 1e-6)`.
# Perturbation: key c5e678a5d1812e40 CLAMP_DROP `max(dt_hours, 1e-6)` -> `(dt_hours)`, in memory. Direction: at dt 0,
#   finite -> ZeroDivisionError; below 1e-6, the cap admits more heat (tank lands exactly at the cap).
# Null control: dt_hours in production's range (0.25, 1/12, 1/60 and the substep sizes), where the floor is inert.
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

mut = mutant(TM._simulate_step_two_zone,
             "            dT_cap = max(0.0, p.buffer_max_temp - T_buf) / max(dt_hours, 1e-6)",
             "            dT_cap = max(0.0, p.buffer_max_temp - T_buf) / (dt_hours)")
p = tm.ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual")
assert not p.two_tank_modelled


def step(fn, st, pw, out, dt):
    with mock.patch.object(TM, "_simulate_step_two_zone", fn):
        return outcome(TM(p)._simulate_step_two_zone, st, pw, out, dt_hours=dt)


prod = (0.25, 1 / 12, 1 / 60, 0.25 / 8, 1e-3, 1e-6)
tiny = (5e-7, 1e-7, 1e-9, 0.0)
pm = tm_ = 0
for dt in prod + tiny:
    mv = 0
    for buf in (40.0, 69.0, 69.9999999, 70.0, 75.0):
        for pw in (1.0, 5.0):
            st = tm.ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0, slab_temperature=22.0,
                                 buffer_tank_temperature=buf)
            b, m = step(TM._simulate_step_two_zone, st, pw, 0.0, dt), step(mut, st, pw, 0.0, dt)
            mv += not same(b, m)
            if buf == 69.9999999 and pw == 5.0:
                bb = b[1].buffer_tank_temperature if b[0] == "ok" else b[1]
                mb = m[1].buffer_tank_temperature if m[0] == "ok" else m[1]
                print(f"RESULT dt{dt:g}_buf_baseline={bb!r} ; dt{dt:g}_buf_mutant={mb!r}")
    print(f"RESULT moved_dt{dt:g}={mv} count (of 10)")
    if dt in prod:
        pm += mv
    else:
        tm_ += mv
print(f"RESULT production_moved={pm} count")
print(f"RESULT below_floor_moved={tm_} count")
tail()
