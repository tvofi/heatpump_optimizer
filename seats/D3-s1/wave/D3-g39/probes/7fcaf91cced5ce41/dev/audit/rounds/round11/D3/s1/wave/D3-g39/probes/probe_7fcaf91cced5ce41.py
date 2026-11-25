#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 7fcaf91cced5ce41 (tariff.py:235 GUARD_OFF).
# Metric: PeakTracker peaks after a 07:00 window of samples [2.0, X] closes (X non-finite or negative); baseline drops X (peak 2.0).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_7fcaf91cced5ce41.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT nan_peaks baseline peak 2.0, mutant nan; neg_peaks baseline 2.0, mutant 0.5
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:PeakTracker.observe (line 235).
# Perturbation: '        if not np.isfinite(house_power_kw) or house_power_kw < 0:' -> '        if False:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: non-finite/negative sample: dropped -> folded into the window mean (nan or a lowered peak).
# Null control: samples [2.0, 1.0] (both arms agree).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '        if not np.isfinite(house_power_kw) or house_power_kw < 0:'
NEW = '        if False:'
B, M, LINE = load('tariff', OLD, NEW, 235)


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
CASES = [
    ("nan_peaks", lambda m: run(m, [2.0, float("nan")]), False),
    ("inf_peaks", lambda m: run(m, [2.0, float("inf")]), False),
    ("neg_peaks", lambda m: run(m, [2.0, -1.0]), False),
    ("ok_peaks", lambda m: run(m, [2.0, 1.0]), True),
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
