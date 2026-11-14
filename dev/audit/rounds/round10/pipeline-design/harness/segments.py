#!/usr/bin/env python3
"""Baseline step 10: the corrected segments (from the FIRST merge verdict), the repair round's inside split,
the mechanical-class rounds, the fast-round floor, and the train's share of post-verdict remerges."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, subprocess, statistics as st, collections, re
def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
F = lambda v: f"n={len(v)} mean={st.mean(v):.2f} p50={q(v,.5):.2f} p90={q(v,.9):.2f} sum={sum(v):.0f} h"
def git(*a): return subprocess.run(["git", "-C", PD_REPO, *a], capture_output=True, text=True).stdout
rows = json.load(open(PD_DATA + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(PD_DATA + "merges.json")) if m["pr"]}
MECH = {"ci-red", "root-cause-unanswered", "carry-missing", "merge-conflict", "main-conflict", "introduced-red", "red-checks", "ci-cancelled",
        "policy-unapproved", "red-unanswered", "body", "under-scoped", "pin-missing", "conflict", "self-test-red"}
first = []; pre = []; n_pre = 0; after = collections.Counter(); prs_after = 0; rd = []; A = []; B = []; mech = [0, 0.0]
for r in rows:
    rev = [x for x in ms[r["pr"]]["review"] if x["t"] <= r["t_merge"] + 60]
    idx = [i for i, x in enumerate(rev) if x["v"] == "merge"]
    if not idx: continue
    i0 = idx[0]; first.append((r["t_merge"] - rev[i0]["t"]) / 3600); pre.append((rev[i0]["t"] - rev[0]["t"]) / 3600); n_pre += i0
    extra = rev[i0 + 1:]; prs_after += bool(extra)
    for x in extra: after[x["v"]] += 1
    for i in range(1, len(rev)):
        tb = rev[i - 1]["t"]; v = rev[i]; d = (v["t"] - tb) / 3600; rd.append(d)
        if (rev[i - 1]["cls"] or "?") in MECH: mech[0] += 1; mech[1] += d
        if v["head"][:10] == rev[i - 1]["head"][:10]: continue
        o = git("log", "-1", "--format=%ct\t%P", v["head"]).strip()
        if not o: continue
        th, par = o.split("\t"); th = int(th); par = par.split()
        if th < tb or len(par) < 2: continue
        t2 = git("log", "-1", "--format=%ct", par[1]).strip()
        if t2 and tb <= int(t2) <= th: A.append((int(t2) - tb) / 3600); B.append((th - int(t2)) / 3600)
print("FIRST merge verdict -> merged:", F(first))
print("first verdict -> FIRST merge verdict:", F(pre), "| repair rounds before it:", n_pre)
print("verdicts after a first merge verdict:", dict(after), "in", prs_after, "PRs")
print("repair round wall: n", len(rd), "mean", round(st.mean(rd), 2), "p10", round(q(rd, .1), 2), "p50", round(q(rd, .5), 2))
print("  blocked -> the repair commit (second parent of the pushed head):", F(A))
print("  repair commit -> pushed on the PR:", F(B))
print("  rounds opened by a mechanical class:", mech[0], "of", len(rd), "hours", round(mech[1]))
logs = ""
for p in (_os.path.join(PD_STATE, "merge_train", "train.log"), _os.path.join(_os.environ.get("HPO_STATE_DIR", PD_STATE), "train.log")):
    if _os.path.exists(p): logs += open(p, errors="replace").read()
heads = set(m.group(1) for m in re.finditer(r"recarry: main merged, head ([0-9a-f]{7,12})", logs))
mainfp = set(git("log", "--first-parent", "--format=%H", "--since=2026-10-20", "origin/main").split())
tot = collections.Counter(); prs = collections.defaultdict(set)
for r in rows:
    m = ms[r["pr"]]; fm = [x for x in m["review"] if x["v"] == "merge" and x["t"] <= r["t_merge"] + 60]
    if not fm or (m["head"] or "").startswith(fm[-1]["head"][:10]): continue
    for l in git("log", "--first-parent", "--format=%H\t%P\t%s", f"{fm[-1]['head']}..{m['head']}").strip().splitlines():
        h, p, s = l.split("\t", 2); ps = p.split()
        if len(ps) > 1 and ps[1] in mainfp and s.startswith("Merge remote-tracking"):
            k = "the train's recarry (head named in a train log)" if any(h.startswith(t) for t in heads) else "a remerge outside the train logs read"
            tot[k] += 1; prs[k].add(r["pr"])
print("remerges of main after the final verdict:", {k: (n, len(prs[k])) for k, n in tot.items()}, "(commits, PRs); train logs read:", bool(logs))
