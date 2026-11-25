#!/usr/bin/env python3
# Metric: count of (state,command,dt) inputs where (stored command, effective displace) after update_ecl110_displace_state differs baseline vs mutant
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g44/probes/probe_36117bb3a189672b.py
# EXPECTED: inputs_moved>0 iff reachable; null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g44 (see ../MACHINE.txt; 4 vCPU, load provisional).
# Instrumented symbol: thermal_model:ThermalModel.update_ecl110_displace_state line 3576: 'np.clip(effective, p.ecl110_displace_min, p.ecl110_displace_max)' -> 'effective' (in memory, recompiled from the file).
# Perturbation: key 36117bb3a189672b; direction: effective displace left out of limits when the incoming state was out of limits
# Null control: the same recompile with old==new (null_moved must be 0).
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from mutlib import tm, mutant

import itertools
base = tm.ThermalModel.update_ecl110_displace_state
mut = mutant("ThermalModel", "update_ecl110_displace_state", 3576, 'np.clip(effective, p.ecl110_displace_min, p.ecl110_displace_max)', 'effective')
nul = mutant("ThermalModel", "update_ecl110_displace_state", 3576, 'np.clip(effective, p.ecl110_displace_min, p.ecl110_displace_max)', 'np.clip(effective, p.ecl110_displace_min, p.ecl110_displace_max)')
def call(fn, p, eff, cmd, dt):
    m = tm.ThermalModel(p)
    st = tm.ThermalState(room_temperature=21.0, outdoor_temperature=0.0)
    st.ecl110_effective_displace = eff
    s = fn(m, st, cmd, dt)
    return (s.ecl110_displace_command, s.ecl110_effective_displace)
moved = nmoved = tried = 0; ex = None
p = tm.ThermalParameters()
lo, hi = p.ecl110_displace_min, p.ecl110_displace_max
print(f"RESULT displace_limits=({lo},{hi})")
for eff, cmd, dt in itertools.product([lo - 5, lo, 0.0, hi, hi + 5], [lo - 9, lo, 0.0, hi, hi + 9], [0.0, 0.05, 0.25, 1.0, 24.0]):
    b, mm, n = call(base, p, eff, cmd, dt), call(mut, p, eff, cmd, dt), call(nul, p, eff, cmd, dt)
    tried += 1; moved += b != mm; nmoved += b != n
    if b != mm and ex is None: ex = (eff, cmd, dt, b, mm)
# in-range state (what a normal run holds): does the mutant still move?
inr = sum(call(base, p, e, c, d) != call(mut, p, e, c, d) for e, c, d in itertools.product([lo, 0.0, hi], [lo, 0.0, hi + 9], [0.05, 0.25, 24.0]) )
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT inputs_moved={moved} count")
print(f"RESULT inputs_moved_state_in_range={inr} count")
print(f"RESULT null_moved={nmoved} count")
print(f"RESULT example(eff,cmd,dt,baseline,mutant)={ex}")
