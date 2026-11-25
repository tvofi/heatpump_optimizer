#!/usr/bin/env python3
# Box D3-g36 probe for mutant 291748b42a54c1f6 (BOOLOP, sysid.py:846, _lm_solve).
# Metric: identify_slab outcome (UA, capacity, tau, confidence, half-width) on a noise-free 22-sample night generated with free gains G = -8 kW (data the ridge prior at +0.3 kW fits poorly, so LM proposes worse finite steps).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_291748b42a54c1f6.py
# Expected: RESULT baseline=ua=0.690204524... ; RESULT mutant=ua=0.690204566... ; RESULT moved=1 ; RESULT null_moved=0 (default night)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_lm_solve (line 846 `if np.isfinite(next_cost) and next_cost < cost:`); called by identify_slab at line 2380.
# Perturbation: `if np.isfinite(next_cost) and next_cost < cost:` -> `if np.isfinite(next_cost) or next_cost < cost:`, applied in memory to the baseline source (g36_common.load(key)). Direction: a finite step that raises the cost is accepted, so LM returns a different (higher-cost) point: the published UA moves by ~4e-8 kW/K here.
# Null control: the default noise-free night (G = 0.3 kW), where every proposed step lowers the cost.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "291748b42a54c1f6"
T0 = c.start()
B, M = c.load(), c.load(KEY)


def outcome(mod, **kw):
    try:
        return c.fit(c.slab_sid(mod, **kw).identify_slab())
    except Exception as e:
        return f"raises:{type(e).__name__}"


a, b = outcome(B, g=-8.0), outcome(M, g=-8.0)
print(f"RESULT baseline={a}")
print(f"RESULT mutant={b}")
print(f"RESULT moved={int(a != b)} count")
print(f"RESULT null_moved={int(outcome(B) != outcome(M))} count")
a2, b2 = outcome(B, g=1.5, noise=0.1), outcome(M, g=1.5, noise=0.1)
print(f"RESULT noisy_baseline={a2}")
print(f"RESULT noisy_mutant={b2}")
c.footer(T0)
