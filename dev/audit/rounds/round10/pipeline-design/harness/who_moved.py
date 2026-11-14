#!/usr/bin/env python3
"""Baseline step 7: who moved a head after its final merge verdict. For each merged PR whose merged head
differs from the head its last merge verdict names, every commit on the first-parent line verdict..merged
is classed by author, committer, subject and whether its second parent is a main first-parent commit."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, collections, re, sys
from datetime import datetime
D = PD_DATA; REPO = PD_REPO
def git(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
mainfp = set(git("log", "--first-parent", "--format=%H", "--since=2026-10-20", "origin/main").split())
rows = json.load(open(D + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(D + "merges.json")) if m["pr"]}
who = collections.Counter(); per_pr = collections.Counter(); ex = collections.defaultdict(list); hours = collections.defaultdict(float); n_moved = 0
for r in rows:
    m = ms[r["pr"]]; fm = [x for x in m["review"] if x["v"] == "merge" and x["t"] <= r["t_merge"] + 60]
    if not fm or (m["head"] or "").startswith(fm[-1]["head"][:10]): continue
    n_moved += 1
    o = git("log", "--first-parent", "--format=%H\t%P\t%an\t%cn\t%s", f"{fm[-1]['head']}..{m['head']}").strip().splitlines()
    kinds = set()
    for l in o:
        h, p, an, cn, s = l.split("\t", 4); ps = p.split()
        if len(ps) > 1 and ps[1] in mainfp:
            if s.startswith("ci: merge main"): k = "main-merge by the merge-main bot (ci: merge main)"
            elif an == "hpo-fixer": k = "main-merge by a fixer seat (hpo-fixer)"
            elif re.match(r"Merge (remote-tracking branch 'origin/main'|branch 'main'|origin/main)", s): k = f"main-merge, subject 'Merge origin/main...' by {an}"
            elif s.startswith("Merge commit"): k = f"main-merge, subject 'Merge commit <sha>' by {an}"
            else: k = f"main-merge other by {an}"
        elif len(ps) > 1: k = f"handoff/other merge by {an}"
        elif s.startswith("ci: "): k = "bot commit (ci: ...)"
        elif s.startswith("record: the delivery row"): k = "delivery-row commit"
        else: k = f"plain commit by {an}"
        who[k] += 1; kinds.add(k)
        if len(ex[k]) < 3: ex[k].append(f"#{r['pr']} {h[:9]} {s[:60]}")
    for k in kinds: per_pr[k] += 1; hours[k] += r["vm_to_merge"]
print(f"PRs whose head moved after the final merge verdict: {n_moved} of {len(rows)}")
for k, n in who.most_common():
    print(f"  {n:4d} commits in {per_pr[k]:3d} PRs  {k}   e.g. {ex[k][:2]}")
