#!/usr/bin/env python3
# Probe for D3.M3 full-gate survivor d3ea4bcc330436ef (box D3-g41, round 11, seat D3-s1).
# Metric: count of batch inputs on which tariff.peak_cost_batch's per-row cost array differs (value or exception) between
#   baseline and mutant; secondary: rows sent to _plateau_aware_topk_sum_batch (work, not value).
# Command (from the tree root): PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g41/probes/probe_d3ea4bcc330436ef.py
# EXPECTED RESULT moved_inputs=0 count (excess = max(0, .), so a row with no positive excess costs 0 either way)
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:peak_cost_batch, line 1196
#   `above = np.flatnonzero(np.any(excess > 0, axis=1))`.
# Perturbation: key d3ea4bcc330436ef CMP_BOUND `excess > 0` -> `excess >= 0`, in memory. Direction if it moved: a below-
#   threshold row's cost 0 -> nonzero.
# Null control: the baseline function against itself.
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
mut = mutant(tf.peak_cost_batch, "    above = np.flatnonzero(np.any(excess > 0, axis=1))",
             "    above = np.flatnonzero(np.any(excess >= 0, axis=1))")
rng = np.random.default_rng(11)
tried = moved = null = 0
for n in (0, 1, 4, 8, 24, 96):
    for B in (1, 3, 7):
        mats = [rng.uniform(0, 4, (B, n)), np.zeros((B, n)), np.full((B, n), 2.5)]
        if n:
            m2 = rng.uniform(0, 4, (B, n)); m2[0, 0] = np.nan; mats.append(m2)
        for M in mats:
            for thr in (0.0, 1.0, 2.5, 5.0, 100.0, np.inf):
                for price in (0.0, 1.0, 37.5):
                    for k in (1, 3):
                        for dd in (False, True):
                            for wf in (None, np.ones(max(n, 1)), np.zeros(max(n, 1))):
                                bill = tf.PeakBilling(threshold_kw=thr, price_per_kw=price, window_minutes=15,
                                                      dt_hours=0.25, peaks_averaged=k, window_factors=wf,
                                                      window_days=(np.arange(n) // 4) if dd else None, distinct_days=dd)
                                base = np.zeros(n)
                                b, m = outcome(tf.peak_cost_batch, M, base, bill), outcome(mut, M, base, bill)
                                tried += 1
                                moved += not same(b, m)
                                null += not same(b, outcome(tf.peak_cost_batch, M, base, bill))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null} count")
rows = []
real = tf._plateau_aware_topk_sum_batch
spy = lambda c, k: (rows.append(c.shape[0]), real(c, k))[1]  # noqa: E731
M = np.array([[1.0, 1.0, 1.0, 1.0], [3.0, 3.0, 3.0, 3.0], [0.5, 0.5, 0.5, 0.5]])
bill = tf.PeakBilling(threshold_kw=2.0, price_per_kw=10.0, window_minutes=15, dt_hours=0.25, distinct_days=False)
with mock.patch.object(tf, "_plateau_aware_topk_sum_batch", spy):
    vb = tf.peak_cost_batch(M, np.zeros(4), bill); rb = sum(rows); rows.clear()
    vm = mut(M, np.zeros(4), bill); rm = sum(rows)
print(f"RESULT work_rows_costed_baseline={rb} count")
print(f"RESULT work_rows_costed_mutant={rm} count")
print(f"RESULT work_case_value_baseline={show(('ok', vb))}")
print(f"RESULT work_case_value_mutant={show(('ok', vm))}")
# The case the sweep moves on: a row wholly below the threshold (excess all 0) with more than k windows tied at that 0
# peak goes, under the mutant, to the smooth top-k arm instead of the 0 the baseline returns for a row with no excess.
first = None
for n in (4, 8, 24, 96):
    for k in (1, 3):
        M = np.vstack([np.full(n, 1.0), np.full(n, 3.0)])
        bill = tf.PeakBilling(threshold_kw=2.0, price_per_kw=37.5, window_minutes=15, dt_hours=0.25, peaks_averaged=k,
                              distinct_days=False)
        b, m = tf.peak_cost_batch(M, np.zeros(n), bill), mut(M, np.zeros(n), bill)
        print(f"RESULT below_row_cost_n{n}_k{k}_baseline={b[0]!r} ; mutant={m[0]!r} (price units; row 2's cost {b[1]!r} / {m[1]!r})")
        if first is None and b[0] != m[0]:
            first = (n, k, b[0], m[0])
print(f"RESULT first_moved_case={first}")
sc = tf.peak_cost_smooth(np.full(24, 1.0), np.zeros(24), tf.PeakBilling(threshold_kw=2.0, price_per_kw=37.5,
                         window_minutes=15, dt_hours=0.25, peaks_averaged=3, distinct_days=False))
print(f"RESULT scalar_peak_cost_smooth_below_row={sc!r} (the scalar twin the batch must match, #948)")
# The sweep's every moved input holds a NaN window: NaN excess is not > 0, so the baseline leaves a row whose other windows
# sit at or below the threshold uncosted (0); the mutant's `>= 0` admits it on the zero windows and the NaN reaches top-k.
import warnings  # noqa: E402
warnings.simplefilter("ignore", RuntimeWarning)
row = np.array([[np.nan, 1.0, 1.0, 1.0], [3.0, 3.0, 3.0, 3.0]])
bill = tf.PeakBilling(threshold_kw=2.0, price_per_kw=37.5, window_minutes=15, dt_hours=0.25, peaks_averaged=1,
                      distinct_days=False)
b, m = tf.peak_cost_batch(row, np.zeros(4), bill), mut(row, np.zeros(4), bill)
sc = outcome(tf.peak_cost_smooth, row[0], np.zeros(4), bill)
print(f"RESULT nan_row_cost_baseline={b[0]!r} ; nan_row_cost_mutant={m[0]!r}")
print(f"RESULT nan_row_scalar_peak_cost_smooth={show(sc)}")
print(f"RESULT nan_row_finite_row_cost_baseline={b[1]!r} ; mutant={m[1]!r}")
tail()
