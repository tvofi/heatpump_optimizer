#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 5371ee2b5e897750 (tariff.py:747 GUARD_OFF).
# Metric: _smooth_topk_sum(x, k, 0.05) on series with no positive entry (all-zero, all-negative); baseline 0.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_5371ee2b5e897750.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT all_negative_baseline=0.0, mutant ~-1.0 (the smooth top-1 of [-1, -2]); all_zero equal
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_smooth_topk_sum (line 747).
# Perturbation: '    if not np.any(x > 0):' -> '    if False:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: no positive entry: 0.0 -> the (negative) smooth top-k sum.
# Null control: a series with a positive entry (both arms agree).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '    if not np.any(x > 0):'
NEW = '    if False:'
B, M, LINE = load('tariff', OLD, NEW, 747)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


def tk(m, x, k, tau=0.05):
    return m._smooth_topk_sum(np.asarray(x, dtype=float), k, tau)
CASES = [
    ("all_negative", lambda m: tk(m, [-1.0, -2.0], 1), False),
    ("all_zero", lambda m: tk(m, [0.0, 0.0, 0.0], 2), False),
    ("nan_only", lambda m: tk(m, [float("nan")], 1), False),
    ("positive", lambda m: tk(m, [0.0, 1.0, 2.0], 1), True),
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
