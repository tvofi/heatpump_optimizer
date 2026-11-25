#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 81557beca8f0a974 (tariff.py:279 CMP_BOUND).
# Metric: PeakTracker weighted accumulators and closed peak when samples carry dt_hours 0.0 / -0.0 (the only values the swap admits); baseline skips them.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_81557beca8f0a974.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT every case equal across arms (adding kw*0 to wsum and 0 to weight is the identity)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:PeakTracker.observe (line 279).
# Perturbation: '        if dt_hours is not None and np.isfinite(dt_hours) and dt_hours > 0:' -> '        if dt_hours is not None and np.isfinite(dt_hours) and dt_hours >= 0:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: dt_hours == 0: skipped -> adds 0.0 to both accumulators (no observable change expected).
# Null control: dt_hours 0.25 (both arms fold it).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '        if dt_hours is not None and np.isfinite(dt_hours) and dt_hours > 0:'
NEW = '        if dt_hours is not None and np.isfinite(dt_hours) and dt_hours >= 0:'
B, M, LINE = load('tariff', OLD, NEW, 279)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


def run(m, samples, dt=None):
    t = m.PeakTracker()
    tar = m.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3)
    for i, kw in enumerate(samples):
        t.observe(datetime(2026, 1, 10, 7, 10 * i), kw, tar, dt_hours=dt)
    t.observe(datetime(2026, 1, 10, 9, 0), 0.5, tar)  # close the 07:00 window
    return (tuple(round(p, 6) if math.isfinite(p) else repr(p) for p in t.peaks), t._window_samples)
def acc(m, dts, kws=(2.0, 1.0)):
    t = m.PeakTracker()
    tar = m.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3)
    for i, (kw, dt) in enumerate(zip(kws, dts)):
        t.observe(datetime(2026, 1, 10, 7, 10 * i), kw, tar, dt_hours=dt)
    return (repr(t._window_wsum), repr(t._window_weight), repr(t._window_mean()))
CASES = [
    ("dt0_acc", lambda m: acc(m, [0.0, 0.0]), False),
    ("dtneg0_acc", lambda m: acc(m, [-0.0, -0.0]), False),
    ("dt0_mixed_acc", lambda m: acc(m, [0.25, 0.0]), False),
    ("dt0_peaks", lambda m: run(m, [2.0, 1.0], 0.0), False),
    ("dt0_bigkw_acc", lambda m: acc(m, [0.0, 0.0], (1e308, 1e-300)), False),
    ("dt025_acc", lambda m: acc(m, [0.25, 0.25]), True),
]

moved = 0
nulls_moved = 0
for label, fn, is_null in CASES:
    b, m = show(arm(fn, B)), show(arm(fn, M))
    print(f"RESULT {label}_baseline={b}")
    print(f"RESULT {label}_mutant={m}")
    if b != m and is_null is not None:
        if is_null:
            nulls_moved += 1
        else:
            moved += 1
print(f"RESULT cases_moved={moved}")
print(f"RESULT null_cases_moved={nulls_moved}")
