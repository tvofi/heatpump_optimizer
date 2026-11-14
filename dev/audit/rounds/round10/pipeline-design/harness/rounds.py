#!/usr/bin/env python3
"""Baseline step 3: split each review round and the verdict-to-merge segment.
Reads data/merges.json, data/prs.json, data/runs, the bus dispatch registry and git commit times."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, glob, sys, subprocess, collections, statistics as st
from datetime import datetime
D = PD_DATA; REPO = PD_REPO
REG = _os.environ.get("PD_BUS_REG", _os.path.expanduser("~/.zcode/bus/dispatched"))
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()) if s else None
a, b = ts(sys.argv[1]), ts(sys.argv[2])
def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
def line(name, v, unit="h"):
    v = [x for x in v if x is not None]
    if not v: print(f"  {name:52s} n=0"); return
    print(f"  {name:52s} n={len(v):3d} p50={q(v,.5):6.2f} p75={q(v,.75):6.2f} p90={q(v,.9):6.2f} mean={st.mean(v):6.2f} sum={sum(v):7.1f} {unit}")
merges = [m for m in json.load(open(D + "merges.json")) if m["pr"] and m["kind"] not in ("record", "bot") and a <= m["t_merge"] <= b]
prs = {int(k): v for k, v in json.load(open(D + "prs.json")).items()}
runs = {}
for f in glob.glob(D + "runs/*.json"):
    for r in json.load(open(f))["runs"]: runs[r["id"]] = r
by_branch = collections.defaultdict(list)
for r in runs.values(): by_branch[r["head_branch"]].append(r)
disp = collections.defaultdict(list)
for l in open(REG):
    p = l.split()
    if len(p) >= 5 and p[0].isdigit():
        try: disp[int(p[0])].append((ts(p[4]), p[1]))
        except Exception: pass
cache = {}
def commit(sha):
    if sha not in cache:
        o = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%ct\t%P\t%s", sha], capture_output=True, text=True).stdout.strip()
        if not o: cache[sha] = None
        else:
            c, p, s = o.split("\t", 2); cache[sha] = (int(c), p.split(), s)
    return cache[sha]
H = 3600.0
R = collections.defaultdict(list); post = collections.defaultdict(list); n_rounds = 0
for m in merges:
    p = prs.get(m["pr"]); 
    if not p: continue
    tm = m["t_merge"]; t_open = ts(p["createdAt"])
    rev = [x for x in m["review"] if x["t"] <= tm + 60]
    ds = sorted(disp.get(m["pr"], []))
    prev_t = None
    for i, v in enumerate(rev):
        # the dispatch that produced this verdict: latest dispatch before it (after previous verdict)
        cand = [d for d in ds if d[0] <= v["t"] and (prev_t is None or d[0] >= prev_t - 60)]
        t_d = cand[0][0] if cand else None   # first dispatch after the previous verdict
        t_dl = cand[-1][0] if cand else None
        hc = commit(v["head"])
        t_head = hc[0] if hc else None
        if i == 0:
            R["r1: PR open -> reviewer dispatched"].append((t_d - t_open) / H if t_d else None)
            R["r1: dispatched -> verdict (review itself)"].append((v["t"] - t_dl) / H if t_dl else None)
        else:
            n_rounds += 1
            same_head = v["head"][:10] == rev[i-1]["head"][:10]
            R["rN: blocked -> next verdict (whole round)"].append((v["t"] - prev_t) / H)
            R["rN:   blocked -> repaired head pushed"].append((t_head - prev_t) / H if t_head and not same_head and t_head >= prev_t else None)
            R["rN:   repaired head -> reviewer dispatched"].append((t_d - t_head) / H if t_d and t_head and not same_head and t_d >= t_head >= prev_t else None)
            R["rN:   blocked -> reviewer dispatched (any)"].append((t_d - prev_t) / H if t_d else None)
            R["rN:   dispatched -> verdict (review itself)"].append((v["t"] - t_dl) / H if t_dl else None)
            R["rN: same-head re-verdict (body/CI only) share"].append(1.0 if same_head else 0.0)
            R["rN by prev class: " + str(rev[i-1]["cls"])].append((v["t"] - prev_t) / H)
        prev_t = v["t"]
    fm = [x for x in rev if x["v"] == "merge"]
    if not fm: continue
    t_vm = fm[-1]["t"]; vhead = fm[-1]["head"]
    rr = sorted([x for x in by_branch.get(m["branch"], []) if t_vm <= ts(x["created_at"]) <= tm + 60], key=lambda x: x["created_at"])
    post["final verdict -> merged"].append((tm - t_vm) / H)
    post["  ci.yml runs started after the final verdict"].append(len(rr))
    post["  .. of which at a new head (head moved after verdict)"].append(len({x["head_sha"] for x in rr if not x["head_sha"].startswith(vhead[:10])}))
    post["  merged head == verdict head (1/0)"].append(1.0 if (m["head"] or "").startswith(vhead[:10]) else 0.0)
    allr = [x for x in by_branch.get(m["branch"], []) if ts(x["created_at"]) <= tm]
    at_head = [x for x in allr if x["head_sha"] == m["head"] and x["conclusion"] == "success"]
    if at_head:
        g = min(ts(x["updated_at"]) for x in at_head)
        post["  first green run at merged head -> merged"].append((tm - g) / H)
        post["  final verdict -> first green run at merged head"].append((g - t_vm) / H)
    hc = commit(m["head"])
    if hc: post["  merged head committed -> merged"].append((tm - hc[0]) / H)
print(f"window {sys.argv[1]}..{sys.argv[2]}: {len(merges)} merges, {n_rounds} repair rounds")
for k in R:
    if "share" in k: print(f"  {k:52s} {sum(R[k]):.0f}/{len(R[k])}")
    elif k.startswith("rN by"): continue
    else: line(k, R[k])
print("repair round wall by the blocked class that opened it:")
for k in sorted((k for k in R if k.startswith("rN by")), key=lambda k: -len(R[k]))[:14]: line(k[18:], R[k])
for k in post: line(k, post[k], "" if "runs" in k or "1/0" in k or "which" in k else "h")
