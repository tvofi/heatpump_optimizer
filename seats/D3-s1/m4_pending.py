#!/usr/bin/env python3
"""D3-s1 box D3-u1d: list full-net results of this box's slice that have no
D3.M4 answer yet in m4_answers-D3-u1d.json, with the production line's context.

Metric: none (a work list). Run: python3 dev/audit/rounds/round11/D3/s1/m4_pending.py [--ctx N]
Reads state/keys-D3-u1d-surv.txt, state/results/complete/, m4_answers-D3-u1d.json.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1d.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
ctx = int(sys.argv[sys.argv.index("--ctx") + 1]) if "--ctx" in sys.argv else 1
ans_p = HERE / "m4_answers-D3-u1d.json"
ans = json.loads(ans_p.read_text()) if ans_p.exists() else {}
for k in (HERE / "state" / "keys-D3-u1d-surv.txt").read_text().split():
    p = HERE / "state" / "results" / "complete" / (k + ".json")
    if k in ans or not p.exists():
        continue
    r = json.loads(p.read_text())
    m = r["mutant"]
    print(f"== {k} {r['verdict']} by={','.join(r['killed_by']) or '-'} {m['anchor'].split('heatpump_optimizer/')[1]} L{m['line']} => {m['new'].strip()}")
    if r["verdict"] == "SURVIVED":
        src = (ROOT / m["file"]).read_text().splitlines()
        for i in range(max(0, m["line"] - 1 - ctx), min(len(src), m["line"] + ctx)):
            print(f"   {i + 1}: {src[i].rstrip()[:150]}")
