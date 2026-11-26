#!/usr/bin/env python3
# Metric: max absolute difference over the clamped stores (("room_thermal_mass","slab_thermal_mass","upper_floor_thermal_mass","lower_floor_thermal_mass")) after ThermalParameters.clamp(), baseline vs mutant, over boundary inputs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_1a9ac2bac45ef9e0.py
# EXPECTED RESULT max_abs_diff=0.0 (equivalent: at value == floor the branch assigns the floor, i.e. the same value)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:270 ThermalParameters.clamp `if not np.isfinite(value) or value < THERMAL_MASS_FLOOR:`.
# Perturbation: key 1a9ac2bac45ef9e0, CMP_BOUND `if not np.isfinite(value) or value < THERMAL_MASS_FLOOR:` -> `if not np.isfinite(value) or value <= THERMAL_MASS_FLOOR:`, in-memory module copy. Direction: none expected (equivalent).
# Null control: a value strictly below the floor: both arms floor it.
import sys, math; sys.path.insert(0, __import__("os").path.dirname(__file__))
import mutmod
base, mut = mutmod.load(270, "if not np.isfinite(value) or value < THERMAL_MASS_FLOOR:", "if not np.isfinite(value) or value <= THERMAL_MASS_FLOOR:")
FLOOR = base.THERMAL_MASS_FLOOR
NAMES = ("room_thermal_mass","slab_thermal_mass","upper_floor_thermal_mass","lower_floor_thermal_mass")
vals = [FLOOR, math.nextafter(FLOOR, 0.0), math.nextafter(FLOOR, 1.0), FLOOR / 2, 0.0, -1.0, float("nan"), float("inf"), "x", None, FLOOR * 1.0000000001, 1.0]
worst = 0.0; moved = 0
for v in vals:
    for n in NAMES:
        out = []
        for m in (base, mut):
            p = m.ThermalParameters(); setattr(p, n, v); p.clamp(); out.append(getattr(p, n))
        d = abs(out[0] - out[1]); worst = max(worst, d); moved += d != 0.0
        if d: print(f"MOVED {n}={v!r}: {out}")
print(f"RESULT inputs_tried={len(vals)*len(NAMES)} count")
print(f"RESULT inputs_moved={moved} count")
print(f"RESULT max_abs_diff={worst!r}")
