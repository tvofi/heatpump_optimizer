import sys; sys.path.insert(0,"tools/audit/seat")
import merge_train as m
from pathlib import Path
H="4fa863b557a51614acb55fac72d3e914f79ec70d"
t=m.Train("tvofi/heatpump_optimizer",Path("."),None,"",(),1)
runs=t._check_runs(H); req=t.required(pr_head=True)
print("required",req)
g=m.gating_names(req)
print("red over gating", m.classify(m.latest_runs(runs), g)[2])
print("gate_raise_only", m.gate_raise_only(t, runs))
for c in m.gate_suites(runs): print(" suite", c.get("id"), m.run_state(c))
base=t.run(["git","merge-base","origin/main",H])[1].strip()
names=t.run(["git","diff","--no-renames","--name-only",base,H])[1].split()
try: print("raise_hold", t.raise_hold(3208,H,names))
except m.Stop as s: print("Stop", s.step, s.why)
