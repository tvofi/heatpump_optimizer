#!/usr/bin/env python3
# Metric: calls of const.buffer_cooling_rate_bounds made by 1000 reads of ThermalParameters.buffer_tank_heat_loss_coefficient (cost), and the value returned
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g44/probes/probe_3d468643db7d9ee4.py
# EXPECTED: value identical baseline vs mutant; calls 1 -> 1000 (CPU cost only)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g44 (see ../MACHINE.txt; 4 vCPU, load provisional).
# Instrumented symbol: thermal_model:ThermalParameters.buffer_tank_heat_loss_coefficient line 668: cached is not None and cached[0] == key -> False (cache never hits) (in memory, recompiled from the file).
# Perturbation: key 3d468643db7d9ee4; direction: same value, bounds-call count rises 1 -> 1000
# Null control: the same recompile with old==new.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from mutlib import tm, mutant, LINES
from custom_components.heatpump_optimizer import const, mixing_valve as mv
src = LINES[667]; print("RESULT site=%r" % src.strip())
old = "cached is not None and cached[0] == key"; new = "False"
mut = mutant("ThermalParameters", "buffer_tank_heat_loss_coefficient", 668, old, new)
def run(fn, vol=750.0, rate=0.0):
    p = tm.ThermalParameters(buffer_tank_volume=vol, buffer_cooling_rate=rate, mixing_valve_mode=mv.MODE_MANUAL)
    g = fn.__globals__; orig = g["buffer_cooling_rate_bounds"]; calls = []
    g["buffer_cooling_rate_bounds"] = lambda v: (calls.append(1), orig(v))[1]
    try:
        vals = {fn(p) for _ in range(1000)}
    finally:
        g["buffer_cooling_rate_bounds"] = orig
    return vals, len(calls)
(bv, bc), (mv_, mc) = run(tm.ThermalParameters.buffer_tank_heat_loss_coefficient.fget), run(mut)
print(f"RESULT value_equal={int(bv == mv_)} count"); print(f"RESULT bounds_calls_baseline={bc} count"); print(f"RESULT bounds_calls_mutant={mc} count")
