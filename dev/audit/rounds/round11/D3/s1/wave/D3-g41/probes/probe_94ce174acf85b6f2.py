#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor 94ce174acf85b6f2 (box D3-g41, round 11, seat D3-s1).
# Metric: ThermalModel._batch_cop COP for a step with no humidity (hum_i None) when the live ambient humidity is known
#   (params.ambient_humidity = 90, published by coordinator.py:6812), with a humidity-dependent learned derate;
#   baseline vs mutant, and parity with the scalar compute_cop(humidity=None).
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_94ce174acf85b6f2.py
# EXPECTED RESULT moved>0: baseline derates at 90 % RH, the mutant at DefrostDerate's dry-bucket centre
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._batch_cop, line 4460
#   `if hum_i is None:` (-> hum_i = p.ambient_humidity).
# Perturbation: key 94ce174acf85b6f2 GUARD_OFF `if hum_i is None:` -> `if False:`, in memory. Direction: up (less derate).
# Null control: ambient_humidity None (fallback is None either way) and finite hum_i.
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

mut = mutant(TM._batch_cop, "            if hum_i is None:", "            if False:")
d = derate(lambda i, j: (0.9, 0.6)[min(j, 1)])
for amb in (90.0, None):
    p = tm.ThermalParameters(two_zone_enabled=True, defrost_derate=d, ambient_humidity=amb)
    model = TM(p)
    tag = "amb90" if amb else "amb_none"
    moved = tried = pb = pm = 0
    for out in OUTS:
        b, m = batch(model, TM._batch_cop, out, None, T_BUF, False), batch(model, mut, out, None, T_BUF, False)
        tried += 1; moved += not same(b, m)
        s = TM(p).compute_cop(out, humidity=None)
        pb += not bool(np.all(b[1] == s)); pm += not bool(np.all(m[1] == s))
        if out == -2.0:
            print(f"RESULT {tag}_cop_m2_baseline={show(b)}")
            print(f"RESULT {tag}_cop_m2_mutant={show(m)}")
            print(f"RESULT {tag}_cop_m2_scalar={s!r}")
    print(f"RESULT {tag}_moved={moved} count (of {tried})")
    print(f"RESULT {tag}_parity_breaks_baseline={pb} count")
    print(f"RESULT {tag}_parity_breaks_mutant={pm} count")
    nm = sum(not same(batch(model, TM._batch_cop, o, 50.0, T_BUF, False), batch(model, mut, o, 50.0, T_BUF, False)) for o in OUTS)
    print(f"RESULT {tag}_finite_hum_null_moved={nm} count")
tail()
