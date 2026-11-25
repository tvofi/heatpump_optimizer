#!/usr/bin/env python3
# Box D3-g36 probe for mutant ae8f84354933d191 (CLAMP_DROP, sysid.py:2375, SystemIdentification.identify_slab).
# Metric: identify_slab outcome when the arm-time UA prior is 0.0 kW/K (declared plant otherwise the ThermalParameters defaults, data from UA 0.15).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_ae8f84354933d191.py
# Expected: RESULT baseline=ua=0.150000000... (fit completes from log(1e-3)) ; RESULT mutant=raises:ValueError (log(0) = -inf seeds NaN into the rollout) ; RESULT moved=1 ; RESULT null_moved=0 (prior 1e-3, 0.15, where max() is the identity); prior 5e-4 also moves (start below the clamp)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2375 `np.log(max(ua0, 1e-3)),`).
# Perturbation: `np.log(max(ua0, 1e-3)),` -> `np.log((ua0)),`, applied in memory to the baseline source (g36_common.load(key)). Direction: a zero UA prior turns a completed fit into an uncaught ValueError out of identify_slab.
# Null control: priors 1e-3 and 0.15 kW/K, where max(ua0, 1e-3) is the identity and both arms fit identically.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "ae8f84354933d191"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:  # a mutant that raises is a moved outcome
        return f"raises:{type(e).__name__}"

cr0 = float(c.plant().room_thermal_mass)
a, b = outcome(B, prior=(0.0, cr0)), outcome(M, prior=(0.0, cr0))
nm = sum(outcome(B, prior=(u, cr0)) != outcome(M, prior=(u, cr0)) for u in (1e-3, 0.15))
sa, sb = outcome(B, prior=(5e-4, cr0)), outcome(M, prior=(5e-4, cr0))
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={nm} count")
print(f"RESULT small_prior_baseline={sa}")
print(f"RESULT small_prior_mutant={sb}")
c.footer(T0)
