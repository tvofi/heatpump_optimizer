#!/usr/bin/env python3
# Metric: Reach: the trajectory always carries n+1 entries (reach_scan.py RESULT breach_traj_eq_n=0 over 6 real solves).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_c859178a.py
# EXPECTED c859178ad2524ff80
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4876 `planned = trajectory[1:] if trajectory.size > n_steps else trajectory`.
# Perturbation: key c859178ad2524ff8, `planned = trajectory[1:] if trajectory.size > n_steps else trajectory` -> `planned = trajectory[1:] if trajectory.size >= n_steps else trajectory` (CMP_BOUND), in memory. Direction: an n_steps-long trajectory (no initial entry) breaching only at step 0: breach 1.0 -> 0.0.
# Null control: the production shape, n+1 entries: identical under both arms.
# Reachability: result.sensor_trajectory carries n+1 entries in every production solve (reach_scan.py).
from breach_rig import publish, mutant, BASE
mut = mutant("trajectory[1:] if trajectory.size > n_steps", "trajectory[1:] if trajectory.size >= n_steps")
kw = dict(tmin=[20.0] * 4, n=4, caps=[1.0] * 4)
b = publish(BASE, traj=[19.0, 20.5, 20.5, 20.5], **kw); m = publish(mut, traj=[19.0, 20.5, 20.5, 20.5], **kw)
print(f"RESULT n_long_baseline={b.get('power_cap_breach_c') if isinstance(b, dict) else b} C")
print(f"RESULT n_long_mutant={m.get('power_cap_breach_c') if isinstance(m, dict) else m} C")
t1 = [21.0, 19.0, 20.5, 20.5, 19.4]
print(f"RESULT null_delta={int(publish(BASE, traj=t1, **kw) != publish(mut, traj=t1, **kw))} count")
print("RESULT reach_traj_len_eq_n=0 count  (reach_scan.py RESULT breach_traj_eq_n)")
import g22_rig; g22_rig.tail()
