#!/usr/bin/env python3
# Metric: dhw_floor_breach_c (C) _publish_breach_reports publishes for a DHW-blocked plan, over the four
#   (requirement None/set) x (DHW trajectory empty/non-empty) cells, plus a real solve on a DHW-disabled install whose
#   mode entity blocks hot water (requirement None, trajectory []).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_6ab21fd9.py
# EXPECTED RESULT cell_reqNone_trajSet_baseline=0.0, _mutant=IndexError (the only moving cell)
# EXPECTED RESULT cells_moved=1 count; RESULT real_dhw_off_blocked_delta=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: optimizer:HeatPumpOptimizer._publish_breach_reports, line 4908
#   `if requirement is not None and dhw_trajectory:`.
# Perturbation: key 6ab21fd9f9fe4953, `and` -> `or` (BOOLOP), in memory. Direction: 0.0 -> exception, only
#   when the requirement is None while the DHW trajectory is non-empty.
# Null control: requirement set and trajectory set (both arms take the branch).
# Reachability: a DHW trajectory is produced only by the DHW solve, which sets self._dhw_requirement from
#   _dhw_build (optimizer.py:5747) in the same pass; the DHW-off install yields requirement None with trajectory [],
#   where the mutant's branch runs on empty arrays and publishes the same 0.0.
from breach_rig import publish, mutant, BASE
import g22_rig as rig
from g22_rig import HeatPumpOptimizer
from unittest import mock
mut = mutant("if requirement is not None and dhw_trajectory:", "if requirement is not None or dhw_trajectory:")
kw = dict(traj=[21.0] * 5, tmin=[20.0] * 4, n=4, db=True)
moved = 0
for rn, req in (("None", None), ("Set", [50.0] * 4)):
    for tn, dt in (("Empty", []), ("Set", [55.0, 52.0, 49.0, 51.0, 50.0])):
        b, m = publish(BASE, req=req, dtraj=dt, **kw), publish(mut, req=req, dtraj=dt, **kw)
        bv = b.get("dhw_floor_breach_c") if isinstance(b, dict) else b
        mv = m.get("dhw_floor_breach_c") if isinstance(m, dict) else m
        print(f"RESULT cell_req{rn}_traj{tn}_baseline={bv} C")
        print(f"RESULT cell_req{rn}_traj{tn}_mutant={mv} C")
        moved += bv != mv
print(f"RESULT cells_moved={moved} count")
opt, run = rig.january()
opt.model.params.dhw_enabled = False
rb = run(dhw_blocked=True).predictive_info.get("dhw_floor_breach_c")
with mock.patch.object(HeatPumpOptimizer, "_publish_breach_reports", mut):
    rm = run(dhw_blocked=True).predictive_info.get("dhw_floor_breach_c")
print(f"RESULT real_dhw_off_blocked_baseline={rb} C")
print(f"RESULT real_dhw_off_blocked_mutant={rm} C")
print(f"RESULT real_dhw_off_blocked_delta={int(rb != rm)} count")
rig.tail()
