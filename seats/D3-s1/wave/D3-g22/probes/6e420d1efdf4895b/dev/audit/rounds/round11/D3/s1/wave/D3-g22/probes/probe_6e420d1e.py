#!/usr/bin/env python3
# Metric: dhw_floor_breach_c (C) published for a DHW-blocked plan with steps == 0 (an empty requirement, or a
#   one-entry trajectory), and for the production shape.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_6e420d1e.py
# EXPECTED RESULT empty_req_baseline=0.0, empty_req_mutant=ValueError (np.max of an empty array)
# EXPECTED RESULT null_delta=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4915 (the DHW `if steps > 0:`).
# Perturbation: key 6e420d1efdf4895b, `if steps > 0:` -> `if steps >= 0:` (CMP_BOUND), in memory.
#   Direction: steps == 0 publishes 0.0 on the baseline and raises under the mutant.
# Null control: the production shape, trajectory n+1 and requirement n >= 1.
# Reachability: the requirement carries n_steps >= 1 entries in every real solve (reach_scan.py req=48);
#   an empty requirement and a one-entry trajectory are not produced.
from breach_rig import publish, mutant, BASE
import g22_rig as rig
mut = mutant("steps = min(planned.size, req.size)\n            if steps > 0:",
             "steps = min(planned.size, req.size)\n            if steps >= 0:")
kw = dict(traj=[21.0] * 5, tmin=[20.0] * 4, n=4, db=True)


def v(r):
    return r["dhw_floor_breach_c"] if isinstance(r, dict) else r


print(f"RESULT empty_req_baseline={v(publish(BASE, req=[], dtraj=[55.0, 50.0], **kw))} C")
print(f"RESULT empty_req_mutant={v(publish(mut, req=[], dtraj=[55.0, 50.0], **kw))} C")
print(f"RESULT one_entry_traj_baseline={v(publish(BASE, req=[50.0] * 4, dtraj=[55.0], **kw))} C")
print(f"RESULT one_entry_traj_mutant={v(publish(mut, req=[50.0] * 4, dtraj=[55.0], **kw))} C")
d = [55.0, 45.0, 52.0, 52.0, 49.0]
print(f"RESULT null_delta={int(publish(BASE, req=[50.0] * 4, dtraj=d, **kw) != publish(mut, req=[50.0] * 4, dtraj=d, **kw))} count")
rig.tail()
