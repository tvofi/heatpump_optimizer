#!/usr/bin/env python3
# Box D3-g36 probe for mutant 0137ee1f014fb759 (CMP_BOUND, sysid.py:2325, SystemIdentification.identify_slab).
# Metric: identify_slab outcome on a 22-sample declared-plant night at 0.5 h cadence with one interval of exactly 3.6 s (dt = 1e-3 h).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_0137ee1f014fb759.py
# Expected: RESULT baseline=refused:slab mode too slow... (cadence-gap refusal) ; RESULT mutant=ua=0.150000000 conf=0.418... (fit completes) ; RESULT moved=1 ; RESULT null_moved=0 (all 0.5 h)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify_slab (line 2325 `if bool(np.any((dts <= 1e-3) | (dts > 2.0))):`).
# Perturbation: `if bool(np.any((dts <= 1e-3) | (dts > 2.0))):` -> `if bool(np.any((dts < 1e-3) | (dts > 2.0))):`, applied in memory to the baseline source (g36_common.load(key)). Direction: the 1e-3 h interval stops being a cadence gap: a refused night is fitted and can be adopted.
# Null control: the same night with every interval 0.5 h, and a 0 s duplicate (refused by both).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "0137ee1f014fb759"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:  # a mutant that raises is a moved outcome
        return f"raises:{type(e).__name__}"

d = np.full(21, 0.5); d[5] = 1e-3
z = np.full(21, 0.5); z[5] = 0.0
a, b = outcome(B, dts=d), outcome(M, dts=d)
na, nb = outcome(B), outcome(M)
za, zb = outcome(B, dts=z), outcome(M, dts=z)
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={int(na != nb)} count")
print(f"RESULT zero_dt_moved={int(za != zb)} count")
c.footer(T0)
