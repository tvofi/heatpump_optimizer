#!/usr/bin/env python3
# Metric: number of swept inputs on which _wood_share_vec output differs (baseline vs mutant); sweep size printed as n_inputs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46/probes/probe_efd15cba428cdcf2.py
# EXPECTED RESULT n_differing>0 if candidate (see report); n_differing=0 if equivalent-candidate.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46 (4 vCPU Xeon @ 2.10GHz). Counts exact.
# Instrumented symbol: thermal_model.py:2939 in _wood_share_vec
# Perturbation: `    r2 = (~r1) & (hp_temp > flow_set)` -> `    r2 = (~r1) & (hp_temp >= flow_set)` applied in memory (module recompiled from source with that one edit).
# Null control: the unmutated module compared with itself (n_differing_null=0).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mut
OLD='    r2 = (~r1) & (hp_temp > flow_set)'; NEW='    r2 = (~r1) & (hp_temp >= flow_set)'
m=_mut.mutant(2939,OLD,NEW)
n=d=nn=0; ex=None
for args in _mut.ws_inputs():
    n+=1
    b=_mut.run(_mut.base._wood_share_vec,args); u=_mut.run(m._wood_share_vec,args); b2=_mut.run(_mut.base._wood_share_vec,args)
    if b!=b2: nn+=1
    if b!=u:
        d+=1
        if ex is None: ex=(args, b, u)
print("RESULT n_inputs=%d"%n); print("RESULT n_differing_null=%d"%nn)
print("RESULT n_differing=%d"%d); print("first_difference", ex)
