#!/usr/bin/env python3
"""Baseline step 2: lead-time split and CI runs per merged change. Reads data/merges.json,
data/prs.json, data/runs/*.json. Usage: baseline.py FROM_ISO UNTIL_ISO [--csv out]"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, glob, sys, statistics as st, collections
from datetime import datetime
D = PD_DATA
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()) if s else None
a, b = ts(sys.argv[1]), ts(sys.argv[2])
merges = json.load(open(D + "merges.json")); prs = {int(k): v for k, v in json.load(open(D + "prs.json")).items()}
runs = {}
for f in glob.glob(D + "runs/*.json"):
    for r in json.load(open(f))["runs"]: runs[r["id"]] = r
by_branch = collections.defaultdict(list)
for r in runs.values(): by_branch[r["head_branch"]].append(r)
def q(v, p):
    v = sorted(v); 
    if not v: return float("nan")
    k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
def line(name, v, unit="h"):
    v = [x for x in v if x is not None]
    if not v: print(f"  {name:44s} n=0"); return
    print(f"  {name:44s} n={len(v):3d} p50={q(v,.5):7.2f} p75={q(v,.75):7.2f} p90={q(v,.9):7.2f} mean={st.mean(v):7.2f} sum={sum(v):8.1f} {unit}")
rows = []
for m in merges:
    if not m["pr"] or m["kind"] in ("record", "bot") or not (a <= m["t_merge"] <= b): continue
    p = prs.get(m["pr"]); 
    if not p: continue
    tm = m["t_merge"]; t_open = ts(p["createdAt"])
    rev = [x for x in m["review"] if x["t"] <= tm + 60]; ver = [x for x in m["verdict"] if x["t"] <= tm + 60]
    hb = [t for t in m["handoff_body"] if t <= tm]
    t_h0 = hb[0] if hb else None
    fm = [x for x in rev if x["v"] == "merge"]
    t_v1 = rev[0]["t"] if rev else None; t_vm = fm[-1]["t"] if fm else None
    pm = [x for x in ver if x["v"] == "merge"]; t_pm = pm[-1]["t"] if pm else None
    H = 3600.0
    r = dict(pr=m["pr"], kind=m["kind"], size=m["size"], gkind=m["gkind"], rounds=len(rev),
             first_pass=(rev[0]["v"] == "merge") if rev else None,
             blocked=[x["cls"] for x in rev if x["v"] == "blocked"],
             handoff_to_open=(t_open - t_h0) / H if t_h0 and t_open >= t_h0 else None,
             open_to_v1=(t_v1 - t_open) / H if t_v1 else None,
             v1_to_vm=(t_vm - t_v1) / H if t_vm and t_v1 else None,
             vm_to_posted=(t_pm - t_vm) / H if t_pm and t_vm and t_pm >= t_vm else None,
             vm_to_merge=(tm - t_vm) / H if t_vm else None,
             open_to_merge=(tm - t_open) / H,
             handoff_to_merge=(tm - min(t_h0, t_open)) / H if t_h0 else (tm - t_open) / H,
             first_commit_to_merge=(tm - m["t_first_commit"]) / H if m["t_first_commit"] else None,
             absorbs=m["absorbs"], bot_commits=m["bot_commits"], row_commits=m["row_commits"], n_own=m["n_own"],
             files=m["files"], t_merge=tm, t_open=t_open, branch=m["branch"], t_vm=t_vm, t_v1=t_v1, head=m["head"])
    # CI runs of this PR's branch between open and merge (+10 min)
    rr = [x for x in by_branch.get(m["branch"], []) if t_open - 60 <= ts(x["created_at"]) <= tm + 600]
    r["runs"] = len(rr); r["attempts"] = sum(x["run_attempt"] for x in rr)
    r["events"] = collections.Counter(x["event"] for x in rr)
    r["heads"] = len({x["head_sha"] for x in rr})
    seen = set(); same = 0
    for x in sorted(rr, key=lambda x: x["created_at"]):
        if x["head_sha"] in seen: same += 1
        seen.add(x["head_sha"])
    r["runs_same_head"] = same + sum(x["run_attempt"] - 1 for x in rr)
    r["concl"] = collections.Counter(x["conclusion"] for x in rr)
    r["run_wall_h"] = sum((ts(x["updated_at"]) - ts(x["run_started_at"])) for x in rr if x["conclusion"] != "cancelled" or True) / H
    succ = sorted(ts(x["updated_at"]) for x in rr if x["conclusion"] == "success")
    r["open_to_first_green_run"] = (succ[0] - t_open) / H if succ else None
    rows.append(r)
json.dump(rows, open(D + f"baseline-{sys.argv[1][:10]}.json", "w"), default=dict)
print(f"window {sys.argv[1]} .. {sys.argv[2]}: {len(rows)} non-record PR merges; kinds {dict(collections.Counter(r['kind'] for r in rows))}")
for label, sel in [("ALL", rows), ("size S", [r for r in rows if r["size"] == "S"]), ("size M", [r for r in rows if r["size"] == "M"]), ("size L/XL", [r for r in rows if r["size"] in ("L", "XL")]),
                   ("product (gkind!=instrument)", [r for r in rows if any(f.startswith("custom_components/") for f in r["files"])])]:
    print(f"== {label} (n={len(sel)})")
    line("handoff -> PR open", [r["handoff_to_open"] for r in sel])
    line("PR open -> first verdict returned", [r["open_to_v1"] for r in sel])
    line("first verdict -> final merge verdict", [r["v1_to_vm"] for r in sel])
    line("  .. same, PRs with >=1 blocked only", [r["v1_to_vm"] for r in sel if r["rounds"] > 1])
    line("final verdict returned -> posted", [r["vm_to_posted"] for r in sel])
    line("final merge verdict -> merged", [r["vm_to_merge"] for r in sel])
    line("PR open -> merged", [r["open_to_merge"] for r in sel])
    line("handoff -> merged", [r["handoff_to_merge"] for r in sel])
    line("first branch commit -> merged", [r["first_commit_to_merge"] for r in sel])
    line("PR open -> first green ci.yml run", [r["open_to_first_green_run"] for r in sel])
    wv = [r for r in sel if r["rounds"]]
    print(f"  review rounds: mean {st.mean(r['rounds'] for r in wv):.2f}; first-pass {sum(1 for r in wv if r['first_pass'])}/{len(wv)}; no verdict {len(sel)-len(wv)}; rounds hist {sorted(collections.Counter(r['rounds'] for r in sel).items())}")
    line("ci.yml runs per PR (open..merge)", [r["runs"] for r in sel], "runs")
    line("  .. runs at an already-run head", [r["runs_same_head"] for r in sel], "runs")
    line("  .. distinct heads run", [r["heads"] for r in sel], "heads")
    line("main absorbs on branch", [r["absorbs"] for r in sel], "merges")
    line("ci.yml run wall per PR", [r["run_wall_h"] for r in sel])
    ev = collections.Counter(); cc = collections.Counter()
    for r in sel: ev.update(r["events"]); cc.update(r["concl"])
    print("  events", dict(ev), "conclusions", dict(cc))
allb = collections.Counter(c for r in rows for c in r["blocked"])
print("blocked classes", allb.most_common(25))
