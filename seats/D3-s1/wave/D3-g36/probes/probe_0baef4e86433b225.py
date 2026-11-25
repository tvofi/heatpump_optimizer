#!/usr/bin/env python3
# Box D3-g36 probe for mutant 0baef4e86433b225 (GUARD_OFF, sysid.py:1752, SystemIdentification.step).
# Metric: samples recorded by two step() calls on an experiment that is not active (never armed: idle; finished: done).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_0baef4e86433b225.py
# Expected: RESULT baseline_idle_samples=0 ; RESULT mutant_idle_samples=2 ; RESULT baseline_done_samples=0 ; RESULT mutant_done_samples=2 ; RESULT return_moved=0 (both return None)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.step (line 1752 `if not self.active:`).
# Perturbation: `if not self.active:` -> `if False:`, applied in memory to the baseline source (g36_common.load(key)). Direction: an inactive experiment starts appending SysIdSample rows on every coordinator cycle (unbounded growth of self.samples while idle).
# Null control: an active settling experiment (both arms record 1 sample per call).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "0baef4e86433b225"
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

def n(mod, phase):
    s = sid(mod, "idle")
    if phase == "done":
        s.phase = "done"
    r = [call(s), call(s)]
    return len(s.samples), r
bi, bd, mi, md = n(B, "idle"), n(B, "done"), n(M, "idle"), n(M, "done")
sa, sb = sid(B, "settling", 0.1), sid(M, "settling", 0.1)
call(sa); call(sb)
print(f"RESULT baseline_idle_samples={bi[0]} count")
print(f"RESULT mutant_idle_samples={mi[0]} count")
print(f"RESULT baseline_done_samples={bd[0]} count")
print(f"RESULT mutant_done_samples={md[0]} count")
print(f"RESULT return_moved={int(bi[1] != mi[1] or bd[1] != md[1])} count")
print(f"RESULT null_moved={int(len(sa.samples) != len(sb.samples))} count")
c.footer(T0)
