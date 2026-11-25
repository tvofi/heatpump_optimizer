#!/usr/bin/env python3
# Box D3-g36 probe for mutant 027e7746bfe5b7bb (RETURN_DEL, sysid.py:1792, SystemIdentification.step).
# Metric: (return value, phase, samples, result.reason) over two step() calls on a STEP- or RELAX-phase experiment whose room leaves the excursion band, across 6 inputs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_027e7746bfe5b7bb.py
# Expected: RESULT moved=0 of 6 inputs (equivalent: abort() always sets PHASE_ABORTED here, and the fall-through matches neither the STEP nor the RELAX branch and reaches the final `return None`)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.step (line 1792 `return None`).
# Perturbation: `return None` -> `pass`, applied in memory to the baseline source (g36_common.load(key)). Direction: none found; the probe searches step/relax, elapsed before and after the phase length, excursion up and down, fit and probe kinds.
# Null control: n/a (equivalence probe); the positive control is mutant 8840eb67a646cd97's probe, the same shape one branch earlier, which moves.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "027e7746bfe5b7bb"
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

def run(mod, phase, h, room, kind):
    s = sid(mod, phase, h)
    s.kind = kind
    a = call(s, room=room)
    b = call(s, room=20.0)
    return a, b, s.phase, len(s.samples), s.result.reason
inputs = [(p, h, r, k) for p in ("step", "relax") for h, r, k in ((2.5, 25.0, "fit"), (0.1, 15.0, "fit"), (2.5, 25.0, "ceiling_probe"))]
moved = 0
for inp in inputs:
    x, y = run(B, *inp), run(M, *inp)
    moved += int(x != y)
    print(f"# {inp}: baseline {x} mutant {y}")
print(f"RESULT moved={moved} count")
print(f"RESULT inputs={len(inputs)} count")
c.footer(T0)
