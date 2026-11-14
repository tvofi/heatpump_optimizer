#!/usr/bin/env python3
"""Revise step 2 (R1, R3, R9): every merge of main into a merged PR's branch, judged twice:
with the checkout's merge drivers (what a seat's `git merge` or `merge-tree` sees) and driver-free (the two drivers
replaced by `git merge-file`, the text merge GitHub computes). Per merge: who made it, the phase, whether the train
log names the resulting head, and the ci.yml runs at that head. Writes data/absorb_heads.json and prints the tables.
A NULL arm (`--null`) relabels every absorb head as an ordinary head: the CI saving it prints must be zero."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, glob, subprocess, collections, re, sys
from datetime import datetime
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
def git(*a, cfg=()):
    r = subprocess.run(["git", "-C", PD_REPO, *cfg, *a], capture_output=True, text=True); return r.returncode, r.stdout
PLAIN = ("-c", "merge.claimnotes.driver=git merge-file -q %A %O %B", "-c", "merge.ledgermerge.driver=git merge-file -q %A %O %B")
NULL = "--null" in sys.argv
rows = json.load(open(PD_DATA + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(PD_DATA + "merges.json")) if m["pr"]}
runs = {}
for f in glob.glob(PD_DATA + "runs/*.json"):
    for r in json.load(open(f))["runs"]: runs[r["id"]] = r
by_sha = collections.defaultdict(list)
for r in runs.values(): by_sha[r["head_sha"]].append(r)
mainfp = set(git("rev-list", "--first-parent", "--since=2026-10-01", "origin/main")[1].split())
logs = ""
for p in (_os.path.join(PD_STATE, "merge_train", "train.log"), _os.path.join(_os.environ.get("HPO_STATE_DIR", PD_STATE), "train.log")):
    if _os.path.exists(p): logs += open(p, errors="replace").read()
train_heads = set(m.group(1) for m in re.finditer(r"recarry: main merged, head ([0-9a-f]{7,12})", logs))
cache = PD_DATA + "absorb_heads.json"
if _os.path.exists(cache) and "--recompute" not in sys.argv:
    A = json.load(open(cache))
else:
    A = []
    for r in rows:
        m = ms[r["pr"]]; mp = git("log", "-1", "--format=%P", m["sha"])[1].split()
        rev = [x for x in m["review"] if x["t"] <= r["t_merge"] + 60]; fm = [x for x in rev if x["v"] == "merge"]
        t1 = fm[0]["t"] if fm else None; hb = [t for t in m["handoff_body"] if t <= r["t_merge"]]
        for l in git("log", "--min-parents=2", "--format=%H\t%P\t%an\t%ct\t%s", f"{mp[0]}..{m['head']}")[1].strip().splitlines():
            h, p, an, ct, s = l.split("\t", 4); ps = p.split(); ct = int(ct)
            mpar = [x for x in ps[1:] if x in mainfp]
            if not mpar: continue
            who = ("merge-main bot" if s.startswith("ci: merge main") else "fixer seat" if an == "hpo-fixer"
                   else "train recarry" if any(h.startswith(t) for t in train_heads) else "other instrument (tvofi)" if an == "tvofi" else "other seat")
            phase = "before PR open" if ct < r["t_open"] else "after first approval" if t1 and ct > t1 else "open to first approval"
            a = git("merge-tree", "--write-tree", ps[0], mpar[0])[0]
            b, o = git("merge-tree", "--write-tree", "--name-only", ps[0], mpar[0], cfg=PLAIN)
            files = [f.strip() for f in o.splitlines()[1:] if f.strip() and not f.startswith(("Auto-merging", "CONFLICT"))] if b else []
            A.append({"pr": r["pr"], "sha": h, "t": ct, "who": who, "phase": phase, "with_drivers": a == 0, "driver_free": b == 0,
                      "conflict_files": files, "after_first_handoff": bool(hb) and ct > hb[0]})
    json.dump(A, open(cache, "w"))
tot = len(A); wd = sum(x["with_drivers"] for x in A); df = sum(x["driver_free"] for x in A)
print(f"merges of main into the {len(rows)} merged branches: {tot}; clean with the checkout's drivers {wd}; clean driver-free (GitHub's text merge) {df}")
print("by maker: n / clean with drivers / clean driver-free / of the driver-free clean, by phase (before open, open..approval, after approval)")
for w in sorted({x["who"] for x in A}, key=lambda w: -sum(1 for x in A if x["who"] == w)):
    v = [x for x in A if x["who"] == w]; c = [x for x in v if x["driver_free"]]
    print(f"  {w:26s} {len(v):4d} / {sum(x['with_drivers'] for x in v):4d} / {len(c):4d} /", [sum(1 for x in c if x["phase"] == p) for p in ("before PR open", "open to first approval", "after first approval")])
only = collections.Counter(f for x in A if x["with_drivers"] and not x["driver_free"] for f in x["conflict_files"])
print("clean only with the drivers:", sum(1 for x in A if x["with_drivers"] and not x["driver_free"]), "files:", only.most_common(6))
fx = [x for x in A if x["who"] == "fixer seat" and x["driver_free"]]
print("fixer-seat clean merges after the topic's first handoff:", sum(1 for x in fx if x["after_first_handoff"]), "of", len(fx))
# ---- CI: run wall at heads a driver-free clean merge of main created (R3)
def wall(r): return max(0, ts(r["updated_at"]) - ts(r["run_started_at"])) / 3600
allpr = [r for r in runs.values() if r["event"] in ("pull_request", "pull_request_review", "workflow_dispatch") and r["conclusion"]]
push = [r for r in runs.values() if r["event"] == "push" and r["conclusion"]]
tot_h = sum(wall(r) for r in runs.values() if r["conclusion"])
absorb = {} if NULL else {x["sha"]: x for x in A if x["driver_free"] and x["phase"] != "before PR open"}
at = collections.defaultdict(lambda: [0, 0.0])
for r in allpr:
    x = absorb.get(r["head_sha"])
    if x: at[x["who"]][0] += 1; at[x["who"]][1] += wall(r)
# a run cancelled because the next head was such a merge
prev_cancel = [0, 0.0]
branch_runs = collections.defaultdict(list)
for r in allpr: branch_runs[r["head_branch"]].append(r)
for b, rs in branch_runs.items():
    heads = sorted({(min(ts(x["created_at"]) for x in rs if x["head_sha"] == h), h) for h in {x["head_sha"] for x in rs}})
    for (t0, h0), (t1, h1) in zip(heads, heads[1:]):
        if h1 in absorb:
            for r in rs:
                if r["head_sha"] == h0 and r["conclusion"] == "cancelled": prev_cancel[0] += 1; prev_cancel[1] += wall(r)
print(f"ci.yml run wall in the window: {tot_h:.0f} h over {sum(1 for r in runs.values() if r['conclusion'])} concluded runs; push runs {sum(wall(r) for r in push):.0f} h over {len(push)}")
s_n = sum(v[0] for v in at.values()); s_h = sum(v[1] for v in at.values())
print(f"runs at a head made by a driver-free clean merge of main after PR open: {s_n} runs, {s_h:.0f} h ({s_h / tot_h * 100:.1f} % of run wall)")
for w, v in sorted(at.items(), key=lambda kv: -kv[1][1]): print(f"    {w:26s} {v[0]:4d} runs {v[1]:6.0f} h ({v[1] / tot_h * 100:.1f} %)")
print(f"runs cancelled by such a merge arriving: {prev_cancel[0]} runs, {prev_cancel[1]:.0f} h ({prev_cancel[1] / tot_h * 100:.1f} %)")
print(f"{'NULL (absorb heads relabelled as ordinary): ' if NULL else ''}run wall a no-clean-absorb rule removes: {s_h:.0f} h = {s_h / tot_h * 100:.1f} % of {tot_h:.0f} h (the {prev_cancel[1]:.0f} h burned in cancelled runs are not counted: those runs would complete instead)")
cp = [wall(r) for r in runs.values() if r["event"] == "push" and r["conclusion"] in ("success", "failure")]
dp = [w for w in (wall(r) for r in runs.values() if r["event"] == "workflow_dispatch" and r["conclusion"] == "success") if w >= 0.25]
print(f"mean wall of a concluded push run: {sum(cp) / len(cp):.2f} h over {len(cp)}; of a successful dispatch run of 15 min or more: {sum(dp) / len(dp):.2f} h over {len(dp)}")
