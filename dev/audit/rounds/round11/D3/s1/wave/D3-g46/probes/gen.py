import json,subprocess,sys
S1="/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1"
KEYS=[l.split("\t")[0] for l in open("../keys.tsv").read().splitlines()[1:]]
TPL='''#!/usr/bin/env python3
# Metric: number of swept inputs on which {fn} output differs (baseline vs mutant); sweep size printed as n_inputs.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g46/probes/probe_{key}.py
# EXPECTED RESULT n_differing>0 if candidate (see report); n_differing=0 if equivalent-candidate.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g46 (4 vCPU Xeon @ 2.10GHz). Counts exact.
# Instrumented symbol: thermal_model.py:{line} in {fn}
# Perturbation: `{old}` -> `{new}` applied in memory (module recompiled from source with that one edit).
# Null control: the unmutated module compared with itself (n_differing_null=0).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mut
OLD={old!r}; NEW={new!r}
m=_mut.mutant({line},OLD,NEW)
n=d=nn=0; ex=None
for args in _mut.{gen}():
    n+=1
    b=_mut.run(_mut.base.{fn},args); u=_mut.run(m.{fn},args); b2=_mut.run(_mut.base.{fn},args)
    if b!=b2: nn+=1
    if b!=u:
        d+=1
        if ex is None: ex=(args, b, u)
print("RESULT n_inputs=%d"%n); print("RESULT n_differing_null=%d"%nn)
print("RESULT n_differing=%d"%d); print("first_difference", ex)
'''
rows=[]
for l in open("../keys.tsv").read().splitlines()[1:]:
    f=l.split("\t"); k=f[0]
    r=json.load(open(f"{S1}/state/results/complete/{k}.json"))["mutant"]
    gen={"_valve_two_zone_delivery":"vz_inputs","_wood_share_vec":"ws_inputs","dew_point_for_pressure":"dp_inputs","dhw_coil_draw_reduction":"dc_inputs"}[f[4]]
    open(f"probe_{k}.py","w").write(TPL.format(key=k,fn=f[4],line=r["line"],old=r["old"],new=r["new"],gen=gen))
    rows.append((k,f[4],r["line"]))
print(len(rows))
