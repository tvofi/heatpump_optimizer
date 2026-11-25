#!/usr/bin/env python3
# Box D3-g36 probe for mutant 9460d3802a8903d6 (CLAMP_DROP, sysid.py:2376, SystemIdentification.identify_slab).
# Metric: identify_slab outcome (UA, total capacity C_r+C_s, tau, confidence, UA half-width) on the 22-sample default night when the arm-time room-capacity prior C_r0 is 0.003 kWh/K (every multi-start seed cr0*mult is under the 1e-2 floor).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_9460d3802a8903d6.py
# Expected: RESULT baseline=ua=0.123915027 cap=5.010000000 tau=40.43... ; RESULT mutant=ua=0.123915027 cap=5.001000000 tau=40.36... ; RESULT moved=1 ; RESULT null_moved=0 (C_r0 = 10, every seed above the floor)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2376 `np.log(max(cr0 * mult, 1e-2)),`); the three starts then tie on cost exactly (C_r is unidentifiable that small) and `cost < best_cost` keeps the first, so the seed decides the published C_r.
# Perturbation: `np.log(max(cr0 * mult, 1e-2)),` -> `np.log((cr0 * mult)),`, applied in memory to the baseline source (g36_common.load(key)). Direction: the published capacity and tau move down (C_r fitted at the 1e-3 seed instead of the 1e-2 floor); UA is unchanged.
# Null control: C_r0 = 10 kWh/K (the default), where max(cr0*mult, 1e-2) is the identity for every mult.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "9460d3802a8903d6"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:
        return f"raises:{type(e).__name__}"


ua0 = float(c.plant().heat_loss_coefficient)
a, b = outcome(B, prior=(ua0, 0.003)), outcome(M, prior=(ua0, 0.003))
na, nb = outcome(B, prior=(ua0, 10.0)), outcome(M, prior=(ua0, 10.0))
za, zb = outcome(B, prior=(ua0, 0.0)), outcome(M, prior=(ua0, 0.0))
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={int(na != nb)} count")
print(f"RESULT zero_prior_baseline={za}")
print(f"RESULT zero_prior_mutant={zb}")
c.footer(T0)
