#!/usr/bin/env python3
"""Baseline step 9: was each merge of main into a branch needed? A merge is 'clean' when plain
`git merge-tree --write-tree p1 p2` exits 0 (no conflict GitHub would have reported DIRTY for)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, collections
D = PD_DATA; REPO = PD_REPO
def run(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True)
mainfp = set(run("log", "--first-parent", "--format=%H", "--since=2026-10-01", "origin/main").stdout.split())
rows = json.load(open(D + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(D + "merges.json")) if m["pr"]}
res = collections.Counter(); files = collections.Counter()
for r in rows:
    m = ms[r["pr"]]; mp = run("log", "-1", "--format=%P", m["sha"]).stdout.split()
    rev = [x for x in m["review"] if x["t"] <= r["t_merge"] + 60]; fm = [x for x in rev if x["v"] == "merge"]; tv = fm[-1]["t"] if fm else None
    for l in run("log", "--format=%H\t%P\t%an\t%ct\t%s", f"{mp[0]}..{m['head']}").stdout.strip().splitlines():
        h, p, an, ct, s = l.split("\t", 4); ps = p.split()
        if len(ps) < 2 or ps[1] not in mainfp: continue
        k = "merge-main bot" if s.startswith("ci: merge main") else "fixer seat" if an == "hpo-fixer" else "remerge_main/open_pr (tvofi)" if s.startswith("Merge remote-tracking") else "other"
        ph = "before open" if int(ct) < r["t_open"] else "after final verdict" if tv and int(ct) > tv else "open..final verdict"
        mt = run("merge-tree", "--write-tree", "--name-only", ps[0], ps[1])
        clean = mt.returncode == 0
        res[(k, ph, "clean" if clean else "conflict")] += 1
        if not clean:
            for f in mt.stdout.splitlines()[1:]:
                if f.strip() and not f.startswith(("Auto-merging", "CONFLICT")): files[f.strip()] += 1
for k in sorted({x[0] for x in res}):
    for ph in ("before open", "open..final verdict", "after final verdict"):
        c, x = res[(k, ph, "clean")], res[(k, ph, "conflict")]
        if c + x: print(f"  {k:30s} {ph:20s} clean {c:4d}  conflict {x:3d}")
print("files in conflict (count of merges):", files.most_common(14))
