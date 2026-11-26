#!/usr/bin/env python3
# Metric: ThermalParameters.buffer_tank_heat_loss_coefficient (kW/K) for a configured buffer_cooling_rate above the volume's upper bound
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g44/probes/probe_05b5a15efaaf70de.py
# EXPECTED: mutant > baseline when rate > high; null equal
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g44 (see ../MACHINE.txt; 4 vCPU, load provisional).
# Instrumented symbol: thermal_model:ThermalParameters.buffer_tank_heat_loss_coefficient line 677: min(max(rate, low), high) -> max(rate, low) (in memory, recompiled from the file).
# Perturbation: key 05b5a15efaaf70de; direction: coefficient rises (cap lost)
# Null control: the same recompile with old==new.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from mutlib import tm, mutant, LINES
from custom_components.heatpump_optimizer import const, mixing_valve as mv
print("RESULT site=%r" % LINES[676].strip())
old = "min(max(float(rate), low), high)"; new = "max(float(rate), low)"
mut = mutant("ThermalParameters", "buffer_tank_heat_loss_coefficient", 677, old, new); nul = mutant("ThermalParameters", "buffer_tank_heat_loss_coefficient", 677, old, old)
moved = nm = tried = 0; ex = None
for vol in (5.0, 100.0, 750.0):
    lo, hi = const.buffer_cooling_rate_bounds(vol)
    for rate in (0.0, lo, (lo + hi) / 2, hi, hi * 1.0001, hi * 3, 50.0):
        p = tm.ThermalParameters(buffer_tank_volume=vol, buffer_cooling_rate=rate, mixing_valve_mode=mv.MODE_MANUAL)
        b = tm.ThermalParameters.buffer_tank_heat_loss_coefficient.fget(p)
        p2 = tm.ThermalParameters(buffer_tank_volume=vol, buffer_cooling_rate=rate, mixing_valve_mode=mv.MODE_MANUAL)
        m, n = mut(p2), nul(tm.ThermalParameters(buffer_tank_volume=vol, buffer_cooling_rate=rate, mixing_valve_mode=mv.MODE_MANUAL))
        tried += 1; moved += b != m; nm += b != n
        if rate == 50.0 and vol == 750.0: ex = (b, m)
print(f"RESULT inputs_tried={tried} count"); print(f"RESULT inputs_moved={moved} count"); print(f"RESULT null_moved={nm} count")
print(f"RESULT example_rate50_vol750_baseline_vs_mutant={ex}")
