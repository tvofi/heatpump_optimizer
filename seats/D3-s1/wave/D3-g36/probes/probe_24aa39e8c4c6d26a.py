#!/usr/bin/env python3
# Box D3-g36 probe for mutant 24aa39e8c4c6d26a (CMP_BOUND, sysid.py:2325, SystemIdentification.identify_slab).
# Metric: identify_slab outcome on a 22-sample declared-plant night at 0.5 h cadence with one interval of exactly 2.0 h.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_24aa39e8c4c6d26a.py
# Expected: RESULT baseline=ua=0.150000000 conf=0.374... (fit completes) ; RESULT mutant=refused:slab mode too slow... (cadence-gap refusal) ; RESULT moved=1 ; RESULT null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2325 `if bool(np.any((dts <= 1e-3) | (dts > 2.0))):`).
# Perturbation: `if bool(np.any((dts <= 1e-3) | (dts > 2.0))):` -> `if bool(np.any((dts <= 1e-3) | (dts >= 2.0))):`, applied in memory to the baseline source (g36_common.load(key)). Direction: a 2.0 h interval, which conditions_met's own `1e-3 < dt <= 2.0` admits, becomes a cadence gap: a fitted night is refused.
# Null control: the same night with every interval 0.5 h, and a 2.5 h gap (refused by both).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "24aa39e8c4c6d26a"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:  # a mutant that raises is a moved outcome
        return f"raises:{type(e).__name__}"

d = np.full(21, 0.5); d[5] = 2.0
g = np.full(21, 0.5); g[5] = 2.5
a, b = outcome(B, dts=d), outcome(M, dts=d)
na, nb = outcome(B), outcome(M)
ga, gb = outcome(B, dts=g), outcome(M, dts=g)
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={int(na != nb)} count")
print(f"RESULT gap_2p5_moved={int(ga != gb)} count")
c.footer(T0)
