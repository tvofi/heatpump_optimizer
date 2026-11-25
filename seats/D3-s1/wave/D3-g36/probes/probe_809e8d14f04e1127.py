#!/usr/bin/env python3
# Box D3-g36 probe for mutant 809e8d14f04e1127 (GUARD_OFF, sysid.py:2315, SystemIdentification.identify_slab).
# Metric: identify_slab refusal reason on a 5-sample declared-plant night (1 settle, 2 step, 2 relax).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_809e8d14f04e1127.py
# Expected: RESULT baseline=refused:not enough samples ; RESULT mutant=refused:not enough usable intervals ; RESULT completed_either=0 ; RESULT moved=1 ; RESULT null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2315 `if len(usable) < 6:`).
# Perturbation: `if len(usable) < 6:` -> `if False:`, applied in memory to the baseline source (g36_common.load(key)). Direction: the 5-sample refusal's reason string moves from 'not enough samples' to _slab_series' 'not enough usable intervals'; completed stays False in both arms.
# Null control: the 6-sample night, which both arms fit identically.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "809e8d14f04e1127"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:  # a mutant that raises is a moved outcome
        return f"raises:{type(e).__name__}"

a = outcome(B, n_settle=1, n_step=2, n_relax=2)
b = outcome(M, n_settle=1, n_step=2, n_relax=2)
na = outcome(B, n_settle=1, n_step=2, n_relax=3)
nb = outcome(M, n_settle=1, n_step=2, n_relax=3)
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT completed_either={int(not a.startswith('refused') or not b.startswith('refused'))} count")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={int(na != nb)} count")
c.footer(T0)
