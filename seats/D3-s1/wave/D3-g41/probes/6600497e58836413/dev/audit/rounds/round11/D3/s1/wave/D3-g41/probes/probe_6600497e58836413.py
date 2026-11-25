#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor 6600497e58836413 (box D3-g41, round 11, seat D3-s1).
# Metric: (a) tariff.window_factors' return for n_windows = 0 with an active #13 mask (None vs an array); (b) count of
#   downstream consumer outputs (billed_windows, peak_cost, peak_cost_smooth, the _grid_report peak figure from each of its
#   two branches) that differ between the baseline and mutant factors.
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_6600497e58836413.py
# EXPECTED RESULT direct_n0_baseline=None ; direct_n0_mutant=[] (size-0 float array)
# EXPECTED RESULT downstream_moved=0 count (every consumer reads a size-0 factor array as None: billed_windows line 873)
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:window_factors, line 674
#   `if start_time is None or n_windows <= 0 or not mask_active(tariff):`; production caller optimizer.py:4155
#   (Optimizer._peak_window_factors), where n_windows = metering_windows(np.zeros(n_steps)).size is 0 only for n_steps 0.
# Perturbation: key 6600497e58836413 CMP_BOUND `n_windows <= 0` -> `n_windows < 0`, in memory. Direction: None -> [].
# Null control: n_windows in (1, 24), where both arms return the same factors; and n_windows = -1.
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

from datetime import datetime, timezone  # noqa: E402
from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402
mut = mutant(tf.window_factors,
             "    if start_time is None or n_windows <= 0 or not mask_active(tariff):",
             "    if start_time is None or n_windows < 0 or not mask_active(tariff):")
mask = tf.CapacityTariff(enabled=True, window_minutes=60, months=frozenset({1, 2}), peak_hours=(7, 8, 9),
                         weekdays_only=True, offpeak_factor=0.5)
assert tf.mask_active(mask)
start = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
b0, m0 = outcome(tf.window_factors, mask, start, 0, 0.25), outcome(mut, mask, start, 0, 0.25)
print(f"RESULT direct_n0_baseline={show(b0)}")
print(f"RESULT direct_n0_mutant={show(m0)}")
nullm = sum(not same(outcome(tf.window_factors, mask, start, n, 0.25), outcome(mut, mask, start, n, 0.25))
            for n in (1, 24, -1))
print(f"RESULT null_moved={nullm} count (of 3: n_windows 1, 24, -1)")
fb, fm = b0[1], m0[1]
down = tried = 0
empty = np.array([])
for thr in (0.0, 2.0):
    billb = tf.PeakBilling(threshold_kw=thr, price_per_kw=40.0, window_minutes=60, dt_hours=0.25, window_factors=fb)
    billm = tf.PeakBilling(threshold_kw=thr, price_per_kw=40.0, window_minutes=60, dt_hours=0.25, window_factors=fm)
    for f in (tf.peak_cost, tf.peak_cost_smooth):
        tried += 1
        down += not same(outcome(f, empty, empty, billb), outcome(f, empty, empty, billm))
tried += 1
down += not same(outcome(tf.billed_windows, empty, fb), outcome(tf.billed_windows, empty, fm))
# _grid_report's two branches (optimizer.py:5656-5674): factors None -> realised_peak; else billed window max or 0.0
def grid_peak(factors):
    if factors is None:
        return tf.realised_peak(empty, empty, 60, 0.25, 0)
    w = tf.metering_windows(empty, 60, 0.25, 0)
    return float(np.max(tf.billed_windows(w, factors))) if w.size else 0.0
tried += 1
gb, gm = outcome(grid_peak, fb), outcome(grid_peak, fm)
down += not same(gb, gm)
print(f"RESULT grid_peak_baseline={show(gb)} kW")
print(f"RESULT grid_peak_mutant={show(gm)} kW")
print(f"RESULT downstream_tried={tried} count")
print(f"RESULT downstream_moved={down} count")
tail()
