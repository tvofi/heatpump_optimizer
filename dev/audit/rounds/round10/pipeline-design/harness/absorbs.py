#!/usr/bin/env python3
"""Baseline step 8: every merge of main into a merged PR's branch (whole life), by who made it and when
relative to the first and the final verdict."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, collections, re
D = PD_DATA; REPO = PD_REPO
def git(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True).stdout
mainfp = set(git("log", "--first-parent", "--format=%H", "--since=2026-10-01", "origin/main").split())
rows = json.load(open(D + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(D + "merges.json")) if m["pr"]}
who = collections.Counter(); phase = collections.Counter(); prs = collections.defaultdict(set)
for r in rows:
    m = ms[r["pr"]]; mp = git("log", "-1", "--format=%P", m["sha"]).split()
    o = git("log", "--format=%H\t%P\t%an\t%ct\t%s", f"{mp[0]}..{m['head']}").strip().splitlines()
    rev = [x for x in m["review"] if x["t"] <= r["t_merge"] + 60]
    t1 = rev[0]["t"] if rev else None; fm = [x for x in rev if x["v"] == "merge"]; tv = fm[-1]["t"] if fm else None
    for l in o:
        h, p, an, ct, s = l.split("\t", 4); ps = p.split(); ct = int(ct)
        if len(ps) < 2 or ps[1] not in mainfp: continue
        if s.startswith("ci: merge main"): k = "merge-main bot"
        elif an == "hpo-fixer": k = "fixer seat (hpo-fixer), on the handoff branch"
        elif s.startswith("Merge remote-tracking branch 'origin/main'"): k = "remerge_main.sh / open_pr.sh (tvofi, 'Merge remote-tracking branch')"
        elif s.startswith("Merge branch 'main'") or "origin/main" in s: k = f"other 'main' merge by {an}"
        else: k = f"'{s[:22]}' by {an}"
        ph = "before PR open" if ct < r["t_open"] else "open..first verdict" if t1 and ct <= t1 else "repair rounds" if tv and ct <= tv else "after final verdict"
        who[k] += 1; phase[(k, ph)] += 1; prs[k].add(r["pr"])
tot = sum(who.values()); print("merges of main into the 215 merged branches:", tot)
for k, n in who.most_common(8):
    print(f"  {n:4d} in {len(prs[k]):3d} PRs  {k}: ", {ph: phase[(k, ph)] for ph in ("before PR open", "open..first verdict", "repair rounds", "after final verdict") if phase[(k, ph)]})
