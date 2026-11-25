#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor 2d037a10caa62e28 (box D3-g41, round 11, seat D3-s1).
# Metric: tariff.realised_peak's answer (kW, or the exception raised) for an empty power series.
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_2d037a10caa62e28.py
# EXPECTED RESULT empty_baseline=0.0 ; empty_mutant=raise:ValueError (np.max of an empty window array)
# EXPECTED RESULT nonempty_moved=0 count (null control: guard inert on non-empty series)
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:realised_peak, line 1225 `if house.size == 0:`;
#   production caller optimizer.py:5657 (Optimizer._grid_report, unmasked branch: realised_peak(total_power, ...)).
# Perturbation: key 2d037a10caa62e28 GUARD_OFF `    if house.size == 0:` -> `    if False:`, in memory.
#   Direction: 0.0 -> ValueError.
# Null control: non-empty series, where the guard is false either way.
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

from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402
mut = mutant(tf.realised_peak, "    if house.size == 0:", "    if False:")
moved_empty = 0
for wm, dt, off in ((15, 0.25, 0), (60, 0.25, 2), (60, 1.0, 0)):
    b = outcome(tf.realised_peak, np.array([]), np.array([]), wm, dt, off)
    m = outcome(mut, np.array([]), np.array([]), wm, dt, off)
    moved_empty += not same(b, m)
    if (wm, dt, off) == (15, 0.25, 0):
        print(f"RESULT empty_baseline={show(b)}")
        print(f"RESULT empty_mutant={show(m)}")
print(f"RESULT empty_forms_moved={moved_empty} count (of 3)")
rng = np.random.default_rng(3)
nm = 0
for n in (1, 4, 7, 96):
    p, bl = rng.uniform(0, 5, n), rng.uniform(0, 1, n)
    nm += not same(outcome(tf.realised_peak, p, bl, 60, 0.25, 1), outcome(mut, p, bl, 60, 0.25, 1))
print(f"RESULT nonempty_moved={nm} count (of 4)")
tail()
