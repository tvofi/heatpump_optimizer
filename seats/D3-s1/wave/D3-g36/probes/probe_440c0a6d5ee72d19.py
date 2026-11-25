#!/usr/bin/env python3
# Box D3-g36 probe for mutant 440c0a6d5ee72d19 (CMP_BOUND, sysid.py:2315, SystemIdentification.identify_slab).
# Metric: identify_slab outcome (completed fit's UA, or the refusal reason) on a 6-sample declared-plant night (1 settle, 2 step, 3 relax at 0.5 h), rolled through the module's own two-state model.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_440c0a6d5ee72d19.py
# Expected: RESULT baseline=ua=0.150000000... (fit completes) ; RESULT mutant=refused:not enough samples ; RESULT moved=1 ; RESULT null_moved=0 (7 samples)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2315 `if len(usable) < 6:`).
# Perturbation: `if len(usable) < 6:` -> `if len(usable) <= 6:`, applied in memory to the baseline source (g36_common.load(key)). Direction: a 6-sample night that fits on the baseline is refused.
# Null control: the 7-sample night (1/3/3), where both arms fit identically.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "440c0a6d5ee72d19"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:  # a mutant that raises is a moved outcome
        return f"raises:{type(e).__name__}"

a = outcome(B, n_settle=1, n_step=2, n_relax=3)
b = outcome(M, n_settle=1, n_step=2, n_relax=3)
na = outcome(B, n_settle=1, n_step=3, n_relax=3)
nb = outcome(M, n_settle=1, n_step=3, n_relax=3)
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={int(na != nb)} count")
c.footer(T0)
