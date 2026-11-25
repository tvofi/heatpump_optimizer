#!/usr/bin/env python3
# Box D3-g36 probe for mutant 85eb19919a6b995a (CMP_BOUND, sysid.py:1212, _declared_night_halfwidth).
# Metric: _declared_night_halfwidth (the arm gate's declared-plant interval) over 12 declared plants x cadences: (UA, C_r) in {(0.15,10),(0.01,1000),(5,0.001),(1e-4,1000)} x dt in {0.5, 0.0011, 2.0} h, plus min |r1 - r0| seen.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_85eb19919a6b995a.py
# Expected: RESULT moved=0 of 12 inputs ; RESULT min_abs_r1_minus_r0=0.000e+00 K (r1 == r0 exactly on 9 of 12 plants, 1.8e-3 K on the rest: the denominator is 0 or far above 1e-12, never the 1e-12 tie where the swap differs)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_declared_night_halfwidth (line 1212 `hold = (baseline - r0) / (r1 - r0) if abs(r1 - r0) > 1e-12 else 0.0`); reached from SystemIdentification._unadoptable (line 1711).
# Perturbation: `hold = (baseline - r0) / (r1 - r0) if abs(r1 - r0) > 1e-12 else 0.0` -> `hold = (baseline - r0) / (r1 - r0) if abs(r1 - r0) >= 1e-12 else 0.0`, applied in memory to the baseline source (g36_common.load(key)). Direction: none found: the swap differs only when |r1 - r0| == 1e-12 exactly.
# Null control: n/a (equivalence probe); the instrumented r1 - r0 values are printed so a later seat can target the boundary.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "85eb19919a6b995a"
T0 = c.start()
B, M = c.load(), c.load(KEY)

p = c.plant()
pair = (float(p.slab_thermal_mass), float(p.slab_heat_transfer))
orig, seen = B._valve_drive, []


def spy(*a, **k):
    r = orig(*a, **k)
    seen.append((float(a[2]) if len(a) > 2 else None, float(r.upper_floor_temperature)))
    return r


moved, diffs, n = 0, [], 0
for ua, cr in ((0.15, 10.0), (0.01, 1000.0), (5.0, 0.001), (1e-4, 1000.0)):
    for dt in (0.5, 0.0011, 2.0):
        seen.clear()
        B.__dict__["_valve_drive"] = spy
        a = B._declared_night_halfwidth(B.SysIdConfig(enabled=True), (ua, cr), pair, None, (20.0, 0.0, dt), 2, 3.0)
        B.__dict__["_valve_drive"] = orig
        for (q0, t0), (q1, t1) in zip(seen, seen[1:]):  # noqa
            if q0 == 0.0 and q1 == 1.0:  # the (r0, r1) generator of line 1208-1211
                diffs.append(abs(t1 - t0))
                print(f"# UA={ua} C_r={cr} dt={dt}: |r1-r0|={abs(t1 - t0):.3e} K, hw baseline={a!r}")
                break
        b = M._declared_night_halfwidth(M.SysIdConfig(enabled=True), (ua, cr), pair, None, (20.0, 0.0, dt), 2, 3.0)
        n += 1
        moved += int(a != b and not (a != a and b != b))
print(f"RESULT moved={moved} count")
print(f"RESULT inputs={n} count")
print(f"RESULT min_abs_r1_minus_r0={min(diffs):.3e} K")
c.footer(T0)
