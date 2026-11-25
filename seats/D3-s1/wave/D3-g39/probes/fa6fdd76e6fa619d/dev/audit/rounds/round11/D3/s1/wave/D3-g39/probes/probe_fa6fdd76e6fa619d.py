#!/usr/bin/env python3
# Box D3-g39 step-4 probe for mutant fa6fdd76e6fa619d (sysid.py:610 CMP_BOUND).
# Metric: slab_mode_tau_fast's return (hours) at c_s exactly 1e-9 (the guard's bound); baseline 0.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_fa6fdd76e6fa619d.py
#   (run from a baseline worktree at the SHA below, never the gate's tree while a gate runs)
# EXPECTED RESULT boundary_c_s_baseline=0.0, boundary_c_s_mutant!=0.0, null_case_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g39 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB); provisional.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_tau_fast (line 610).
# Perturbation: '    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):' -> '    if not (c_r > 1e-9 and c_s >= 1e-9 and k_s > 1e-9):', applied in memory to a sibling copy of the module
#   (_mutload.load; the file on disk is not written). Direction: c_s == 1e-9: 0.0 (unset plant) -> a finite tau.
# Null control: c_s = 0.0 and c_s = 2e-9 (both arms agree); ordinary plant (2, 3, 0.5).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mutload import load, arm  # noqa: E402
import math  # noqa: E402,F401
from datetime import datetime  # noqa: E402,F401
import numpy as np  # noqa: E402,F401

OLD = '    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):'
NEW = '    if not (c_r > 1e-9 and c_s >= 1e-9 and k_s > 1e-9):'
B, M, LINE = load('sysid', OLD, NEW, 610)


def show(v):
    if isinstance(v, float):
        return repr(v)
    return str(v)


CASES = [
    ("boundary_c_s", lambda m: m.slab_mode_tau_fast(2.0, 1e-9, 0.5), False),
    ("just_above_c_s", lambda m: m.slab_mode_tau_fast(2.0, 2e-9, 0.5), True),
    ("zero_c_s", lambda m: m.slab_mode_tau_fast(2.0, 0.0, 0.5), True),
    ("ordinary", lambda m: m.slab_mode_tau_fast(2.0, 3.0, 0.5), True),
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
