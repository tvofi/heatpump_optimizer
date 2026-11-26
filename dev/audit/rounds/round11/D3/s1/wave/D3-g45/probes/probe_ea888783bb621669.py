#!/usr/bin/env python3
# Metric: dhw_draw_power (kW) when the DHW set-point is below the inlet reference (delta_t < 0); expected: baseline 0.0, mutant negative
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_ea888783bb621669.py
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:855 ThermalParameters.dhw_draw_power `liters_per_hour * WATER_SPECIFIC_HEAT * max(delta_t, 0.0)`.
# Perturbation: key ea888783bb621669, `liters_per_hour * WATER_SPECIFIC_HEAT * max(delta_t, 0.0)` -> `liters_per_hour * WATER_SPECIFIC_HEAT * (delta_t)`, in an in-memory module copy (mutmod.load). 
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import mutmod
base, mut = mutmod.load(855, "liters_per_hour * WATER_SPECIFIC_HEAT * max(delta_t, 0.0)", "liters_per_hour * WATER_SPECIFIC_HEAT * (delta_t)")
# Direction: negative draw power (a tank that is 'cooled' by consumption).
# Null control: set-point above the inlet reference (delta_t > 0): identical.
def pw(m, sp, ref):
    p = m.ThermalParameters(); p.dhw_setpoint = sp; p.dhw_inlet_temp = ref; return p.dhw_draw_power
for sp, ref in ((40.0, 50.0), (10.0, 10.0), (55.0, 10.0)):
    print(f"RESULT draw_power_sp{sp}_ref{ref}_baseline={pw(base,sp,ref)!r} mutant={pw(mut,sp,ref)!r}")
print(f"RESULT null_moved={int(pw(base,55.0,10.0)!=pw(mut,55.0,10.0))} count")
print(f"RESULT inputs_moved={sum(pw(base,s,r)!=pw(mut,s,r) for s,r in ((40.0,50.0),(10.0,10.0),(55.0,10.0)))} of 3 count")
