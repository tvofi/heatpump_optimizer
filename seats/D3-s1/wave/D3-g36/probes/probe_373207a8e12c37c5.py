#!/usr/bin/env python3
# Box D3-g36 probe for mutant 373207a8e12c37c5 (CLAMP_DROP, sysid.py:842, _lm_solve).
# Metric: the clipped component _lm_solve returns with clip=(1, -5.0, 10.0) (the profile solve _slab_ua_profile_halfwidth makes) for a residual whose optimum puts that component at 20.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_373207a8e12c37c5.py
# Expected: RESULT baseline_x1=10.0 (projected to the band) ; RESULT mutant_x1=20.0 ; RESULT moved=1 ; RESULT null_moved=0 (optimum 3.0, inside the band) ; RESULT slab_hw_moved=0 on the default and noisy nights (the profiled intercept never reaches the band there)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_lm_solve (line 842 `np.clip(candidate[clip[0]], clip[1], clip[2])`); reached from identify_slab through _slab_outcome -> _slab_ua_profile_halfwidth -> _profiled_cost.
# Perturbation: `np.clip(candidate[clip[0]], clip[1], clip[2])` -> `(candidate[clip[0]])`, applied in memory to the baseline source (g36_common.load(key)). Direction: the profiled intercept G is no longer held in [-5, 10] kW.
# Null control: an optimum inside the band (3.0), where the projection is the identity.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "373207a8e12c37c5"
T0 = c.start()
B, M = c.load(), c.load(KEY)

def x1(mod, t):
    tt = np.array([0.0, t])
    x, _ = mod._lm_solve(lambda x: x - tt, np.zeros(2), clip=(1, -5.0, 10.0))
    return float(x[1])


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:
        return f"raises:{type(e).__name__}"


b, m = x1(B, 20.0), x1(M, 20.0)
print(f"RESULT baseline_x1={b:.6f}")
print(f"RESULT mutant_x1={m:.6f}")
print(f"RESULT moved={int(b != m)} count")
print(f"RESULT null_moved={int(x1(B, 3.0) != x1(M, 3.0))} count")
hw = sum(outcome(B, **kw) != outcome(M, **kw) for kw in ({}, {"noise": 0.05}, {"g": -8.0}))
print(f"RESULT slab_hw_moved={hw} count  # identify_slab nights: default, noise 0.05, gains -8 kW")
c.footer(T0)
