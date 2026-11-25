#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor 2765114b9329f57f (box D3-g41, round 11, seat D3-s1).
# Metric: count of inputs (series x window x step x offset) on which tariff.metering_windows' output (value or raised exception)
#   differs between baseline and mutant.
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_2765114b9329f57f.py
# EXPECTED RESULT moved_inputs=0 count (pieces is never empty for a non-empty series; the empty series returns before it)
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:metering_windows, line 588 `if not pieces:`.
# Perturbation: key 2765114b9329f57f GUARD_OFF `    if not pieces:` -> `    if False:`, in memory (function re-compiled from its
#   own source with the line swapped). Direction if it moved: a [mean] fallback -> ValueError from np.concatenate([]).
# Null control: the baseline function against itself (null_moved must be 0).
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
mut = mutant(tf.metering_windows, "    if not pieces:", "    if False:")
series = [np.array([]), np.array([np.nan]), np.array([np.inf, -np.inf]), np.array([1e308, 1e308])]
series += [np.arange(n, dtype=float) for n in range(1, 26)]
tried = moved = null = 0
for h in series:
    for wm in (0, 1, 7, 15, 30, 60, 120, 1440):
        for dt in (0.0, 1e-9, 1 / 60, 1 / 12, 0.25, 0.5, 1.0, 2.0):
            for off in (-7, -1, 0, 1, 3, 5, 1000):
                b = outcome(tf.metering_windows, h, wm, dt, off)
                m = outcome(mut, h, wm, dt, off)
                tried += 1
                moved += not same(b, m)
                null += not same(b, outcome(tf.metering_windows, h, wm, dt, off))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null} count")
tail()
