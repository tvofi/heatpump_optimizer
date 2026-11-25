#!/usr/bin/env python3
# Box D3-g36 probe for mutant b3c0e51c511b2618 (CLAMP_DROP, sysid.py:1778, SystemIdentification.step).
# Metric: the thermal power_kw booked on a settling sample with plan_power_kw=2.0 and cop=0.05 (and cop=0.0).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_b3c0e51c511b2618.py
# Expected: RESULT baseline_kw=0.2 ; RESULT mutant_kw=0.1 ; RESULT baseline_kw_cop0=0.2 ; RESULT mutant_kw_cop0=0.0 ; RESULT null_moved=0 (cop 3.0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.step (line 1778 `thermal_cop = max(cop, 0.1)`).
# Perturbation: `thermal_cop = max(cop, 0.1)` -> `thermal_cop = (cop)`, applied in memory to the baseline source (g36_common.load(key)). Direction: the 0.1 COP floor is lost: a settling row books less thermal heat (0 at cop 0) than the floor does.
# Null control: cop=3.0, where both arms book 6.0 kW.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "b3c0e51c511b2618"
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

def kw(mod, cop):
    s = sid(mod, "settling", 0.1)
    call(s, cop=cop, plan=2.0)
    return s.samples[-1].power_kw
b1, m1, b0, m0, bn, mn = kw(B, 0.05), kw(M, 0.05), kw(B, 0.0), kw(M, 0.0), kw(B, 3.0), kw(M, 3.0)
print(f"RESULT baseline_kw={b1:.6g} kW")
print(f"RESULT mutant_kw={m1:.6g} kW")
print(f"RESULT baseline_kw_cop0={b0:.6g} kW")
print(f"RESULT mutant_kw_cop0={m0:.6g} kW")
print(f"RESULT null_moved={int(bn != mn)} count")
c.footer(T0)
