#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 7f9297e43c9449d8 (tariff.py:491 CMP_BOUND).
# Metric: _one_per_day output on same-day ties (equal kW, incl. 0.0 vs -0.0 and nan); baseline keeps the first.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_7f9297e43c9449d8.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT every case equal across arms by value (a tie replaces (kw, day) by an equal (kw, day))
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_one_per_day (line 491).
# Perturbation: '        elif day not in best or kw > best[day][0]:' -> '        elif day not in best or kw >= best[day][0]:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: tie: first entry kept -> last entry kept; the tuples are equal.
# Null control: same-day 3.0 then 2.0 (both arms keep 3.0). signbit_tie_info is reported, not counted as a
#   null: it is the -0.0/0.0 sign bit of a value-equal tie, which no tracker path can produce (sums start at 0.0).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '        elif day not in best or kw > best[day][0]:'
NEW = '        elif day not in best or kw >= best[day][0]:'
B, M, LINE = load('tariff', OLD, NEW, 491)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


def od(m, r):
    # by value: `+ 0.0` maps -0.0 to 0.0 (value-identity), so a signed-zero tie is compared
    # as the kW it bills; the sign bit is reported separately by signbit_tie below.
    return [(repr(k + 0.0), d) for k, d in m._one_per_day(r)]


def signbit(m, r):
    return [bool(np.signbit(k)) for k, _ in m._one_per_day(r)]
CASES = [
    ("tie", lambda m: od(m, [(2.0, "2026-01-05"), (2.0, "2026-01-05")]), False),
    ("tie_signed_zero", lambda m: od(m, [(0.0, "2026-01-05"), (-0.0, "2026-01-05")]), False),
    ("tie_nan", lambda m: od(m, [(float("nan"), "2026-01-05"), (float("nan"), "2026-01-05")]), False),
    ("tie_then_lower", lambda m: od(m, [(2.0, "d"), (2.0, "d"), (1.0, "d")]), False),
    ("tie_billed", lambda m: m._billed_peak_kw([kw for kw, _ in m._one_per_day([(2.0, "a"), (2.0, "a"), (1.0, "b")])], m.CapacityTariff(enabled=True, price_per_kw=50.0)), False),
    ("signbit_tie_info", lambda m: signbit(m, [(0.0, "2026-01-05"), (-0.0, "2026-01-05")]), None),
    ("ordered", lambda m: od(m, [(3.0, "d"), (2.0, "d")]), True),
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
