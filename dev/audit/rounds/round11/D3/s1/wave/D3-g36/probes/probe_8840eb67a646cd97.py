#!/usr/bin/env python3
# Box D3-g36 probe for mutant 8840eb67a646cd97 (RETURN_DEL, sysid.py:1785, SystemIdentification.step).
# Metric: phase after a settling step() that over-excursions once settle_hours has elapsed, and the power step() returns on the next cycle (room back at baseline).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_8840eb67a646cd97.py
# Expected: RESULT baseline_phase=aborted ; RESULT mutant_phase=step ; RESULT baseline_next_return=None ; RESULT mutant_next_return=1.8 (kW injected after the abort) ; RESULT null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.step (line 1785 `return None`).
# Perturbation: `return None` -> `pass`, applied in memory to the baseline source (g36_common.load(key)). Direction: an experiment aborted for comfort is resurrected into PHASE_STEP and injects its step power on the next cycle, while result.reason still says it aborted.
# Null control: the same excursion before settle_hours has elapsed (0.1 h), where both arms stay aborted.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "8840eb67a646cd97"
T0 = c.start()
B, M = c.load(), c.load(KEY)

H = np.linspace(0.5, 2.0, 24)


def sid(mod, phase, started_h=2.0):
    s = mod.SystemIdentification(mod.SysIdConfig(enabled=True))
    if phase != "idle":
        s.arm(c.NOW)
        s.phase, s.phase_started, s._baseline_temp = phase, c.NOW - timedelta(hours=started_h), 20.0
    return s


def call(s, room=20.0, cop=3.0, plan=1.0):
    return s.step(c.NOW, room, 0.0, 0.5, H, 0, 6.0, cop=cop, plan_power_kw=plan)

def run(mod, h):
    s = sid(mod, "settling", h)
    call(s, room=25.0)
    ph = s.phase
    nxt = call(s, room=20.0)
    return ph, nxt, s.result.reason
b, m, bn, mn = run(B, 2.0), run(M, 2.0), run(B, 0.1), run(M, 0.1)
print(f"RESULT baseline_phase={b[0]}")
print(f"RESULT mutant_phase={m[0]}")
print(f"RESULT baseline_next_return={b[1]}")
print(f"RESULT mutant_next_return={m[1]}")
print(f"RESULT mutant_reason_after={m[2]!r}")
print(f"RESULT null_moved={int(bn != mn)} count")
c.footer(T0)
