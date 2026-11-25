#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 246043395831f540 (tariff.py:128 CMP_BOUND).
# Metric: marginal_price_per_kw of an enabled CapacityTariff(price_per_kw=50) at peaks_averaged 0; baseline 0.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_246043395831f540.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT peaks0_baseline=0.0, peaks0_mutant=raises ZeroDivisionError, null_case_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:CapacityTariff.marginal_price_per_kw (line 128).
# Perturbation: '        if not self.enabled or self.peaks_averaged <= 0:' -> '        if not self.enabled or self.peaks_averaged < 0:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: peaks_averaged == 0: 0.0 -> ZeroDivisionError.
# Null control: peaks_averaged 3 and -1, and a disabled tariff (both arms agree).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '        if not self.enabled or self.peaks_averaged <= 0:'
NEW = '        if not self.enabled or self.peaks_averaged < 0:'
B, M, LINE = load('tariff', OLD, NEW, 128)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


def mp(m, n, en=True):
    return m.CapacityTariff(enabled=en, price_per_kw=50.0, peaks_averaged=n).marginal_price_per_kw
CASES = [
    ("peaks0", lambda m: mp(m, 0), False),
    ("peaks3", lambda m: mp(m, 3), True),
    ("peaksneg1", lambda m: mp(m, -1), True),
    ("disabled0", lambda m: mp(m, 0, False), True),
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
