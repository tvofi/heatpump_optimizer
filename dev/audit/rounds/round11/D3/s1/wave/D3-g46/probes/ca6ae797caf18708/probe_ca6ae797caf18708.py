#!/usr/bin/env python3
# Metric: number of swept inputs on which dew_point_for_pressure output differs (baseline vs mutant); sweep size printed as n_inputs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46/probes/probe_ca6ae797caf18708.py
# EXPECTED RESULT n_differing>0 if candidate (see report); n_differing=0 if equivalent-candidate.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46 (4 vCPU Xeon @ 2.10GHz). Counts exact.
# Instrumented symbol: thermal_model.py:2827 in dew_point_for_pressure
# Perturbation: `    ln = math.log(max(vapor_pressure_hpa, 1e-9) / 6.112)` -> `    ln = math.log((vapor_pressure_hpa) / 6.112)` applied in memory (module recompiled from source with that one edit).
# Null control: the unmutated module compared with itself (n_differing_null=0).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mut
OLD='    ln = math.log(max(vapor_pressure_hpa, 1e-9) / 6.112)'; NEW='    ln = math.log((vapor_pressure_hpa) / 6.112)'
m=_mut.mutant(2827,OLD,NEW)
n=d=nn=0; ex=None
for args in _mut.dp_inputs():
    n+=1
    b=_mut.run(_mut.base.dew_point_for_pressure,args); u=_mut.run(m.dew_point_for_pressure,args); b2=_mut.run(_mut.base.dew_point_for_pressure,args)
    if b!=b2: nn+=1
    if b!=u:
        d+=1
        if ex is None: ex=(args, b, u)
print("RESULT n_inputs=%d"%n); print("RESULT n_differing_null=%d"%nn)
print("RESULT n_differing=%d"%d); print("first_difference", ex)
