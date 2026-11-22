#!/usr/bin/env python3
# Metric: the space release steps HeatPumpOptimizer._safety_release_steps returns when temp_min_bounds is one
#   entry shorter than the power schedule (the padding branch), and for the production shape (equal lengths).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_af94ce8b.py
# EXPECTED RESULT short_bounds_baseline=[0, 1, 2], short_bounds_mutant=IndexError; RESULT null_delta=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._safety_release_steps, line 5225 `if i < len(temp_min_bounds)`.
# Perturbation: key af94ce8be7140e87, `i < len(temp_min_bounds)` -> `i <= len(temp_min_bounds)` (CMP_BOUND),
#   in memory. Direction: short bounds raise IndexError at i == len(bounds) instead of padding with bounds[-1].
# Null control: bounds of n entries (production).
# Reachability: _safety_release_steps' callers (optimizer.py:4515, 4542) pass the solve's temp_min_bounds, n_steps long,
#   with an n-step power schedule (reach_scan.py tmin=48 for n=48).
from types import SimpleNamespace
import g22_rig as rig
from g22_rig import np, HeatPumpOptimizer
mut = rig.mutant(HeatPumpOptimizer, "_safety_release_steps", "if i < len(temp_min_bounds)", "if i <= len(temp_min_bounds)")
o = rig.bare_optimizer()
o._dhw_requirement = None


def call(fn, bounds, n=3):
    res = SimpleNamespace(power_schedule=[0.0] * n, sensor_trajectory=lambda tz: [21.0] + [20.0] * n,
                          dhw_temp_trajectory=[], dhw_power_schedule=[])
    try:
        return fn(o, res, np.asarray(bounds, float), np.zeros(n), None)
    except Exception as e:
        return type(e).__name__


print(f"RESULT short_bounds_baseline={call(HeatPumpOptimizer._safety_release_steps, [20.0, 20.0])}")
print(f"RESULT short_bounds_mutant={call(mut, [20.0, 20.0])}")
b3 = [20.0, 20.0, 20.0]
print(f"RESULT null_delta={int(call(HeatPumpOptimizer._safety_release_steps, b3) != call(mut, b3))} count")
rig.tail()
