#!/usr/bin/env python3
# Metric: max |baseline-mutant| of ThermalParameters._windowed_draw_pattern() over hourly patterns whose masked total is exactly 1e-6
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g44/probes/probe_3d4899a05eb126c3.py
# EXPECTED: moved>0 only at total==1e-6 exactly (boundary)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g44 (see ../MACHINE.txt; 4 vCPU, load provisional).
# Instrumented symbol: thermal_model:ThermalParameters._windowed_draw_pattern line 940: total <= 1e-6 -> total < 1e-6 (in memory, recompiled from the file).
# Perturbation: key 3d4899a05eb126c3; direction: baseline returns base pattern, mutant returns 24/total-scaled pattern at the tie
# Null control: the same recompile with old==new.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from mutlib import tm, mutant
from custom_components.heatpump_optimizer import dhw_schedule as ds
mut = mutant("ThermalParameters", "_windowed_draw_pattern", 940, "total <= 1e-6", "total < 1e-6")
nul = mutant("ThermalParameters", "_windowed_draw_pattern", 940, "total <= 1e-6", "total <= 1e-6")
W = ds.FULL_DAY  # a (start, end) tuple
def pat(v, h=3):
    x = [0.0] * 24; x[h] = v; return x
tried = moved = nm = 0; ex = None
for v in (1e-6, 1e-6 * (1 + 1e-12), 2e-6, 5e-7, 0.0, 0.5):
    p = tm.ThermalParameters(dhw_schedule_enabled=True, dhw_windows=[W], dhw_hourly_draw_pattern=pat(v))
    b, m, n = tm.ThermalParameters._windowed_draw_pattern(p), mut(p), nul(p)
    tried += 1; moved += b != m; nm += b != n
    if v == 1e-6: ex = (max(b), max(m))
    print(f"RESULT total_{v!r}_moved={int(b != m)}")
print(f"RESULT inputs_tried={tried} count"); print(f"RESULT inputs_moved={moved} count"); print(f"RESULT null_moved={nm} count")
print(f"RESULT tie_max_baseline_vs_mutant={ex}")
