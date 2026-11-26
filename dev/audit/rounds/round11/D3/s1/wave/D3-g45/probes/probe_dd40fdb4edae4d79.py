#!/usr/bin/env python3
# Metric: flow setpoint (degC) returned by _valve_flow_set when a per-step valve_target (45.0) is passed while the configured mixing_valve_target is 35.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_dd40fdb4edae4d79.py
# EXPECTED RESULT flow_set_baseline > flow_set_mutant (baseline follows the per-step 45.0 curve; mutant the configured 35.0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:2270 _valve_flow_set `if valve_target is not None:`.
# Perturbation: key dd40fdb4edae4d79, GUARD_OFF `if False:` (the per-step target is ignored), in-memory module copy. Direction: down.
# Null control: valve_target=None -> both arms use the configured target: identical.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import mutmod
base, mut = mutmod.load(2270, "if valve_target is not None:", "if False:")
def fs(m, vt):
    p = m.ThermalParameters(); p.mixing_valve_target = 35.0
    return m._valve_flow_set(p, vt, 0.0, 0.3, 2.0)
for vt in (45.0, 25.0, None):
    print(f"RESULT flow_set_vt{vt}_baseline={fs(base,vt)!r} mutant={fs(mut,vt)!r}")
print(f"RESULT null_delta={abs(fs(base,None)-fs(mut,None))!r}")
print(f"RESULT inputs_moved={sum(fs(base,v)!=fs(mut,v) for v in (45.0,25.0))} of 2 count")
