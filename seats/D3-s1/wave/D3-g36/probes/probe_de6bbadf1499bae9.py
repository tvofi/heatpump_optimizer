#!/usr/bin/env python3
# Box D3-g36 probe for mutant de6bbadf1499bae9 (CMP_BOUND, sysid.py:2381, SystemIdentification.identify_slab).
# Metric: identify_slab outcome (fit UA/confidence/half-width, or refusal reason) on the 22-sample declared-plant night with ONE non-finite or overflowing room reading (row 3 = 1e160, nan, inf), where every multi-start cost is non-finite and ties.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_de6bbadf1499bae9.py
# Expected: RESULT moved=3 of 3 inputs; baseline 1e160 -> refused:fit failed, nan -> ua=0.15 conf=nan (completes!), inf -> ua=0.15 conf=0 hw=inf; mutant -> refused:fitted parameters outside plausible bounds for all 3 ; RESULT null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2381 `if cost < best_cost:`).
# Perturbation: `if cost < best_cost:` -> `if cost <= best_cost:`, applied in memory to the baseline source (g36_common.load(key)). Direction: on a tie of non-finite costs (inf <= inf) a later start replaces best_x, so the outcome on a corrupted night moves from fit failed / a completed fit to a bounds refusal.
# Null control: the finite night (noise-free and 0.02 C noise), where no exact tie occurs and both arms fit identically.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "de6bbadf1499bae9"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, bad=None, **kw):
    try:
        s = c.slab_sid(mod, **kw)
        if bad is not None:
            s.samples[3].room_temp = bad
        return c.fit(s.identify_slab())
    except Exception as e:
        return f"raises:{type(e).__name__}"


moved = 0
for bad in (1e160, float("nan"), float("inf")):
    a, b = outcome(B, bad), outcome(M, bad)
    moved += int(a != b)
    print(f"RESULT baseline_{bad}={a}")
    print(f"RESULT mutant_{bad}={b}")
print(f"RESULT moved={moved} count")
nm = int(outcome(B) != outcome(M)) + int(outcome(B, noise=0.02) != outcome(M, noise=0.02))
print(f"RESULT null_moved={nm} count")
c.footer(T0)
