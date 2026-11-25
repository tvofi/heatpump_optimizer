#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant 37b3c9a03326d207 (tariff.py:489 GUARD_OFF).
# Metric: len(_one_per_day(ranked)) for a ranking holding two undated ('') peaks; baseline keeps both (#1512: undated entries are never merged).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_37b3c9a03326d207.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT two_undated_baseline=[(3.0, ''), (2.0, '')], mutant=[(3.0, '')]
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_one_per_day (line 489).
# Perturbation: '        if not day:' -> '        if False:', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: undated peaks: all kept -> merged into one '' day (the lower one dropped).
# Null control: dated peaks on distinct days (both arms agree).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '        if not day:'
NEW = '        if False:'
B, M, LINE = load('tariff', OLD, NEW, 489)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


CASES = [
    ("two_undated", lambda m: m._one_per_day([(3.0, ""), (2.0, "")]), False),
    ("undated_plus_dated", lambda m: m._one_per_day([(3.0, ""), (2.0, ""), (1.0, "2026-01-05")]), False),
    ("distinct_days", lambda m: m._one_per_day([(3.0, "2026-01-04"), (2.0, "2026-01-05")]), True),
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
