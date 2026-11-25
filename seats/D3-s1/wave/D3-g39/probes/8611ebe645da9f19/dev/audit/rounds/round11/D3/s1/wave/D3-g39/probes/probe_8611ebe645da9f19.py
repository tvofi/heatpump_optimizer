#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 8611ebe645da9f19 (tariff.py:391 CMP_BOUND).
# Metric: PeakTracker.threshold_kw with len(peaks) == peaks_averaged (the only length the swap re-routes); baseline peaks[n-1].
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_8611ebe645da9f19.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT every case equal across arms (peaks[-1] is peaks[n-1] when len == n)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:PeakTracker.threshold_kw (line 391).
# Perturbation: '        if len(self.peaks) < n:' -> '        if len(self.peaks) <= n:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: len == n: peaks[n-1] -> peaks[-1], the same element.
# Null control: len < n and len > n (both arms agree).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '        if len(self.peaks) < n:'
NEW = '        if len(self.peaks) <= n:'
B, M, LINE = load('tariff', OLD, NEW, 391)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


def th(m, peaks, n):
    t = m.PeakTracker(); t.peaks = list(peaks)
    return t.threshold_kw(m.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=n))
CASES = [
    ("len_eq_n3", lambda m: th(m, [3.0, 2.0, 1.0], 3), False),
    ("len_eq_n1", lambda m: th(m, [3.0], 1), False),
    ("len_eq_n0", lambda m: th(m, [3.0], 0), False),
    ("len_eq_unsorted", lambda m: th(m, [1.0, 3.0, 2.0], 3), False),
    ("len_eq_nan", lambda m: th(m, [3.0, float("nan")], 2), False),
    ("len_lt", lambda m: th(m, [3.0, 2.0], 3), True),
    ("len_gt", lambda m: th(m, [4.0, 3.0, 2.0, 1.0], 3), True),
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
