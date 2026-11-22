#!/usr/bin/env python3
# Metric: dhw_floor_breach_c (C) published for a DHW-blocked plan whose trimmed DHW trajectory is longer than the
#   requirement (trajectory n+2, requirement n), and for the production shape (n+1 vs n).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_d600d488.py
# EXPECTED RESULT long_traj_baseline=2.0, long_traj_mutant=ValueError (broadcast of n against n+1)
# EXPECTED RESULT null_delta=0 count; RESULT short_traj_delta=0 count (planned shorter than req: min == planned.size)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4914
#   `steps = min(planned.size, req.size)`.
# Perturbation: key d600d4886444a718, `min(planned.size, req.size)` -> `(planned.size)` (CLAMP_DROP), in memory.
#   Direction: only a trajectory longer than requirement+1 moves (0/2.0 -> ValueError).
# Null control: the production shape, trajectory n+1 and requirement n.
# Reachability: reach_scan.py RESULT breach_dhw_planned_longer_than_req_after_trim=0 over 6 real solves.
from breach_rig import publish, mutant, BASE
import g22_rig as rig
mut = mutant("steps = min(planned.size, req.size)", "steps = (planned.size)")
kw = dict(traj=[21.0] * 5, tmin=[20.0] * 4, n=4, db=True, req=[50.0] * 4)


def v(r):
    return r["dhw_floor_breach_c"] if isinstance(r, dict) else r


long = [55.0, 48.0, 52.0, 52.0, 52.0, 40.0]
print(f"RESULT long_traj_baseline={v(publish(BASE, dtraj=long, **kw))} C")
print(f"RESULT long_traj_mutant={v(publish(mut, dtraj=long, **kw))} C")
d = [55.0, 45.0, 52.0, 52.0, 49.0]
print(f"RESULT null_delta={int(publish(BASE, dtraj=d, **kw) != publish(mut, dtraj=d, **kw))} count")
s = [55.0, 45.0, 52.0]
print(f"RESULT short_traj_delta={int(publish(BASE, dtraj=s, **kw) != publish(mut, dtraj=s, **kw))} count")
rig.tail()
