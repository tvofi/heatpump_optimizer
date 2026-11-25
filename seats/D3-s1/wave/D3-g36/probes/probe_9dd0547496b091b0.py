#!/usr/bin/env python3
# Box D3-g36 probe for mutant 9dd0547496b091b0 (CLAMP_DROP, sysid.py:1782, SystemIdentification.step).
# Metric: the thermal power_kw booked on a settling sample with plan_power_kw=-1.0, cop=3.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_9dd0547496b091b0.py
# Expected: RESULT baseline_kw=0 ; RESULT mutant_kw=-3 ; RESULT null_moved=0 (plan 1.0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.step (line 1782 `self.samples[-1].power_kw = max(plan_power_kw, 0.0) * thermal_cop`).
# Perturbation: `self.samples[-1].power_kw = max(plan_power_kw, 0.0) * thermal_cop` -> `self.samples[-1].power_kw = (plan_power_kw) * thermal_cop`, applied in memory to the baseline source (g36_common.load(key)). Direction: a negative planned power is booked as negative heat into the fit's settle rows instead of 0.
# Null control: plan_power_kw=1.0, where both arms book 3.0 kW.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "9dd0547496b091b0"
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

def kw(mod, plan):
    s = sid(mod, "settling", 0.1)
    call(s, plan=plan)
    return s.samples[-1].power_kw
b, m, bn, mn = kw(B, -1.0), kw(M, -1.0), kw(B, 1.0), kw(M, 1.0)
print(f"RESULT baseline_kw={b:.6g} kW")
print(f"RESULT mutant_kw={m:.6g} kW")
print(f"RESULT null_moved={int(bn != mn)} count")
c.footer(T0)
