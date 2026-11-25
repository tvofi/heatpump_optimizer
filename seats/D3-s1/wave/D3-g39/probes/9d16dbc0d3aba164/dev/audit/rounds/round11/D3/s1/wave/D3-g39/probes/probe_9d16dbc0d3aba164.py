#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 9d16dbc0d3aba164 (tariff.py:904 GUARD_OFF).
# Metric: _peak_excess on an empty plan (size-0 power and baseline arrays), for 60/15-minute windows, with and without window_factors; baseline None.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_9d16dbc0d3aba164.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT every case equal across arms (metering_windows returns the empty array, excess is empty, np.any is False -> None)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_peak_excess (line 904).
# Perturbation: '    if house.size == 0:' -> '    if False:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: empty plan: early None -> None through the window scaffolding (no change expected unless a helper raises on empty).
# Null control: a 4-step plan with one window above the threshold (both arms return the same excess).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '    if house.size == 0:'
NEW = '    if False:'
B, M, LINE = load('tariff', OLD, NEW, 904)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


def pe(m, n, wm=60, dt=0.25, factors=None, off=0):
    bill = m.PeakBilling(threshold_kw=1.0, price_per_kw=50.0, window_minutes=wm, dt_hours=dt,
                         offset_steps=off, window_factors=factors)
    r = m._peak_excess(np.full(n, 3.0), np.zeros(n), bill)
    return None if r is None else tuple(np.round(r, 6))
CASES = [
    ("empty_60", lambda m: pe(m, 0), False),
    ("empty_15", lambda m: pe(m, 0, 15), False),
    ("empty_off2", lambda m: pe(m, 0, 60, 0.25, None, 2), False),
    ("empty_factors", lambda m: pe(m, 0, 60, 0.25, np.zeros(0)), False),
    ("empty_factors1", lambda m: pe(m, 0, 60, 0.25, np.ones(1)), False),
    ("four_steps", lambda m: pe(m, 4), True),
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
