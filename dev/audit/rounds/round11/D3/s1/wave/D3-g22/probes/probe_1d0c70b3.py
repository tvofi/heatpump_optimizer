#!/usr/bin/env python3
# Metric: dhw_floor_breach_c (C) published for a DHW-blocked plan whose DHW trajectory has as many entries as the
#   requirement (no initial-state entry) and the tank short only at step 0; and for the production shape (n+1 vs n).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1d0c70b3.py
# EXPECTED RESULT eq_len_baseline=5.0, eq_len_mutant=0.0; RESULT null_delta=0 count (n+1 entries)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4913
#   `planned = planned[1:] if planned.size > req.size else planned`.
# Perturbation: key 1d0c70b3b63230eb, `>` -> `>=` (CMP_BOUND), in memory. Direction: an equal-length trajectory
#   loses its first step (breach 5.0 -> 0.0).
# Null control: the production shape, trajectory n+1 and requirement n.
# Reachability: reach_scan.py RESULT breach_dhw_traj_eq_req=0 (dtraj 49 vs req 48 in all 6 real solves).
from breach_rig import publish, mutant, BASE
import g22_rig as rig
mut = mutant("planned[1:] if planned.size > req.size else planned", "planned[1:] if planned.size >= req.size else planned")
kw = dict(traj=[21.0] * 5, tmin=[20.0] * 4, n=4, db=True, req=[50.0] * 4)
b = publish(BASE, dtraj=[45.0, 52.0, 52.0, 52.0], **kw)["dhw_floor_breach_c"]
m = publish(mut, dtraj=[45.0, 52.0, 52.0, 52.0], **kw)["dhw_floor_breach_c"]
print(f"RESULT eq_len_baseline={b} C")
print(f"RESULT eq_len_mutant={m} C")
d = [55.0, 45.0, 52.0, 52.0, 49.0]
print(f"RESULT null_delta={int(publish(BASE, dtraj=d, **kw) != publish(mut, dtraj=d, **kw))} count")
print("RESULT reach_dtraj_len_eq_req=0 count  (reach_scan.py RESULT breach_dhw_traj_eq_req)")
rig.tail()
