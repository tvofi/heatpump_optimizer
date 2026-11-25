#!/usr/bin/env python3
# Metric: Reach: temp_min_bounds carries n_steps entries and the trajectory n+1 (reach_scan.py tmin=48, traj=49).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_e658b77d.py
# EXPECTED e658b77d3e5ca8f60
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4879 `if steps > 0:`.
# Perturbation: key e658b77d3e5ca8f6, `if steps > 0:` -> `if steps >= 0:` (CMP_BOUND), in memory. Direction: steps == 0 (empty temp_min_bounds): breach 0.0 -> ValueError (np.max of an empty array).
# Null control: a 4-step plan with bounds: steps 4, both arms identical.
# Reachability: production passes temp_min_bounds of n_steps >= 1 entries (reach_scan.py: tmin=48 in all 6 solves).
from breach_rig import publish, mutant, BASE
mut = mutant("breach = 0.0\n        if steps > 0:", "breach = 0.0\n        if steps >= 0:")
kw = dict(traj=[21.0], tmin=[], n=0, caps=[])
b, m = publish(BASE, **kw), publish(mut, **kw)
print(f"RESULT empty_bounds_baseline={b.get('power_cap_breach_c') if isinstance(b, dict) else b} C")
print(f"RESULT empty_bounds_mutant={m.get('power_cap_breach_c') if isinstance(m, dict) else m} C")
kw = dict(traj=[21.0, 19.0, 20.5, 20.5, 19.4], tmin=[20.0] * 4, n=4, caps=[1.0] * 4)
print(f"RESULT null_delta={int(publish(BASE, **kw) != publish(mut, **kw))} count")
import g22_rig; g22_rig.tail()
