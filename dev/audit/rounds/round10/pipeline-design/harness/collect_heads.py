#!/usr/bin/env python3
"""Revise step 1: per merged PR, the PR-branch head each merge verdict judged (a verdict may name the code head on
the handoff branch: the PR head is then the branch head, among those CI ran at, that contains it), every head
after it with what kind of commits made it, and the `gate` check-runs at the judged heads (GraphQL, read-only).
Writes data/heads.json."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
import json, glob, subprocess, collections, sys, time
from datetime import datetime
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
def git(*a):
    r = subprocess.run(["git", "-C", PD_REPO, *a], capture_output=True, text=True); return r.returncode, r.stdout
rows = json.load(open(PD_DATA + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(PD_DATA + "merges.json")) if m["pr"]}
runs = {}
for f in glob.glob(PD_DATA + "runs/*.json"):
    for r in json.load(open(f))["runs"]: runs[r["id"]] = r
by_branch = collections.defaultdict(list)
for r in runs.values(): by_branch[r["head_branch"]].append(r)
mainfp = set(git("rev-list", "--first-parent", "--since=2026-10-01", "origin/main")[1].split())
out = {}; want = set()
for r in rows:
    m = ms[r["pr"]]; rev = [x for x in m["review"] if x["t"] <= r["t_merge"] + 60]
    idx = [i for i, x in enumerate(rev) if x["v"] == "merge"]
    if not idx: continue
    mp = git("log", "-1", "--format=%P", m["sha"])[1].split()
    # the PR branch's own first-parent line, oldest first
    line = [l.split("\t") for l in git("log", "--first-parent", "--reverse", "--format=%H\t%ct\t%P\t%an\t%s", f"{mp[0]}..{m['head']}")[1].strip().splitlines()]
    pos = {l[0]: i for i, l in enumerate(line)}
    def pr_head(h):
        full = git("rev-parse", "--verify", "-q", h + "^{commit}")[1].strip()
        if full in pos: return full
        for l in line:                       # the first PR-branch commit that contains the judged code head
            if git("merge-base", "--is-ancestor", full or h, l[0])[0] == 0: return l[0]
        return None
    def kinds_after(p):
        ks = []
        for l in line[pos[p] + 1:] if p in pos else []:
            h, ct, par, an, s = l; ps = par.split()
            if len(ps) > 1 and any(x in mainfp for x in ps[1:]): k = "main"
            elif s.startswith("record: the delivery row"): k = "row"
            elif s.startswith("ci: ") or s.startswith("claims:"): k = "bot"
            elif len(ps) > 1: k = "handoff-merge"
            else: k = "commit"
            authored = False
            if k in ("handoff-merge", "commit"):
                # authored work: the merge brings in commits that are not on main and not already on the branch
                new = git("rev-list", "--no-merges", f"{h}", f"^{ps[0]}", f"^{mp[0]}")[1].split() if len(ps) > 1 else [h]  # not on the branch before, not on main before the PR merged
                authored = bool(new)
            ks.append({"sha": h, "t": int(ct), "kind": k, "authored": authored, "pushed": any(x["head_sha"] == h for x in by_branch.get(m["branch"], []))})
        return ks
    first, last = rev[idx[0]], rev[idx[-1]]
    later_block = any(x["v"] == "blocked" for x in rev[idx[0] + 1:])
    p1, pL = pr_head(first["head"]), pr_head(last["head"])
    out[r["pr"]] = {"t_first": first["t"], "t_last": last["t"], "p_first": p1, "p_last": pL, "later_block": later_block,
                    "after_first": kinds_after(p1) if p1 else None, "after_last": kinds_after(pL) if pL else None,
                    "verdict_named_pr_head": bool(p1) and p1.startswith(first["head"][:10]), "t_merge": r["t_merge"], "merged_head": m["head"],
                    "head_t": {l[0]: int(l[1]) for l in line}}
    for p in (p1, pL):
        if p: want.add(p)
json.dump(out, open(PD_DATA + "heads.json", "w"))
print("PRs", len(out), "judged PR heads to read", len(want), "unmapped first", sum(1 for v in out.values() if not v["p_first"]), file=sys.stderr)
if "--no-fetch" in sys.argv: sys.exit(0)
gate = {}
F = 'checkSuites(first:30,filterBy:{appId:15368}){nodes{workflowRun{event databaseId createdAt} checkRuns(first:2,filterBy:{checkName:"gate"}){nodes{conclusion status startedAt completedAt}}}}'
want = sorted(want)
for i in range(0, len(want), 4):
    chunk = want[i:i + 4]
    q = 'query{repository(owner:"tvofi",name:"heatpump_optimizer"){' + " ".join(f'c{j}:object(oid:"{s}"){{... on Commit{{oid {F}}}}}' for j, s in enumerate(chunk)) + "} rateLimit{remaining cost}}"
    for attempt in (1, 2, 3):
        r = subprocess.run(["gh", "api", "graphql", "-f", "query=" + q], capture_output=True, text=True)
        if r.returncode == 0: break
        time.sleep(5)
    else:
        print("FAIL", r.stderr[:200], file=sys.stderr); break
    j = json.loads(r.stdout)
    for v in j["data"]["repository"].values():
        if v: gate[v["oid"]] = [{"event": (s.get("workflowRun") or {}).get("event"), "created": (s.get("workflowRun") or {}).get("createdAt"),
                                 "gate": s["checkRuns"]["nodes"]} for s in v["checkSuites"]["nodes"]]
    if i % 80 == 0: print(i, j["data"]["rateLimit"], file=sys.stderr)
    time.sleep(0.7)
json.dump(gate, open(PD_DATA + "gate_heads.json", "w")); print("gate read for", len(gate), file=sys.stderr)
