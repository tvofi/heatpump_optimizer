"""Reviewer's own replay (round 4, adapted from the round-3 reviewer's replay_gap.py): recorded runs at a38bd141 cut at T, with the Train wall clock set to T."""
import json, sys, importlib.util
from pathlib import Path
tree, T = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("mt", f"{tree}/tools/audit/seat/merge_train.py"); mt = importlib.util.module_from_spec(spec); sys.modules["mt"]=mt; spec.loader.exec_module(mt)
crs=[json.loads(l) for l in open("ev/check-runs-head.jsonl")]
snap=[]
for c in crs:
    if (c.get("started_at") or "")>T: continue
    c=dict(c)
    if (c.get("completed_at") or "9")>T: c.update(status="in_progress", conclusion=None)
    snap.append(c)
att={42404526059:("completed","2026-11-07T20:02:31Z"),42404527136:("completed","2026-11-07T19:19:16Z"),42406706258:("completed","2026-11-07T19:53:39Z")}
runs=[]
for r in map(json.loads, open("ev/ci-runs-head.jsonl")):
    r=dict(r); st,done=att[r["id"]]
    r["status"]= "completed" if done<=T and (r["id"]==42404526059 or T<"2026-11-07T20:03:33Z") else "in_progress"
    runs.append(r)
req=sys.argv[3].split(",") if len(sys.argv)>3 else None
def run(argv, cwd=None, stdin=None):
    a=" ".join(argv)
    if "actions/workflows/ci.yml/runs" in a: return 0, "\n".join(json.dumps(r) for r in runs)
    if "check-runs" in a: return 0, "\n".join(json.dumps(c) for c in snap)
    return 9, "unstubbed"
import datetime
wall=datetime.datetime.fromisoformat(T.replace("Z","+00:00")).timestamp()
t=mt.Train("o/r", Path("."), None, "", (), 1, run=run, sleep=lambda s:None, log=lambda m: print("log:",m), **({"wall":(lambda: wall)} if "wall" in mt.Train.__init__.__code__.co_varnames else {}))
t.required=lambda pr_head=True: ["gate"]
f=getattr(mt,"classify_cmd",None)
print(T, *(f(t, "a38bd141ec8b42fc8d2bcd17090be1814ca97d83", None, False) if f else mt.classify(mt.latest_runs(snap), ["gate"])))
