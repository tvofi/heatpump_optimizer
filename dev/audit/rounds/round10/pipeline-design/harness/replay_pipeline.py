#!/usr/bin/env python3
"""Replay of candidate pipelines over round 10's recorded merges (2026-11-07..11-14).
For each merged PR the recorded inputs are kept: first merge verdict, every verdict after it, the ci.yml
runs at each head, the merge time, and whether main's `gate` went red at that merge (a red-streak start).
  today : the recorded merge time (null control: must print the measured mean).
  C1    : heads are not moved by a clean merge of main; an approved, green head merges at the next batch
          proof (proof wall W) or at once when it is alone; claim and real-conflict entries keep today's time.
  C2    : an approved, green head lands on the integration branch at once; proofs of the integration tip run
          back to back (wall W); main fast-forwards to each green proof; a red proof bisects over prefixes.
Usage: replay_pipeline.py [W_minutes ...]"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, glob, sys, collections, statistics as st, subprocess
from datetime import datetime
D = PD_DATA
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
def F(v): return f"n={len(v)} mean={st.mean(v):5.2f} p50={q(v,.5):5.2f} p90={q(v,.9):5.2f} sum={sum(v):6.0f} h"
rows = json.load(open(D + "baseline-2026-11-07.json")); ms = {m["pr"]: m for m in json.load(open(D + "merges.json")) if m["pr"]}
runs = {}
for f in glob.glob(D + "runs/*.json"):
    for r in json.load(open(f))["runs"]: runs[r["id"]] = r
by_sha = collections.defaultdict(list)
for r in runs.values(): by_sha[r["head_sha"]].append(r)
gate = json.load(open(D + "main_gate.json"))
# red-streak starts on main, by merge commit sha
seq = []
for l in reversed(gate["log"]):
    sha, ct, subj = l.split(" ", 2); g = None
    for s in gate["suites"].get(sha, []):
        wr = s.get("workflowRun") or {}
        if wr.get("event") == "push" and (wr.get("workflow") or {}).get("name") == "CI":
            for c in s["checkRuns"]["nodes"]: g = c["conclusion"]
    seq.append((sha, g))
red_start = set(); prev = "SUCCESS"; streak_len = {}; cur = None
for sha, g in seq:
    if g in ("SUCCESS", "FAILURE"):
        if g == "FAILURE" and prev == "SUCCESS": red_start.add(sha); cur = sha; streak_len[sha] = 1
        elif g == "FAILURE" and cur: streak_len[cur] += 1
        prev = g
# a red followed by green at the very next judged merge, with no fix between, is treated as transient (re-run cures it)
TRANSIENT = {s for s, n in streak_len.items() if n == 1}
SERIAL_CLAIM = ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt")
ent = []; known_wait = []
for r in rows:
    m = ms[r["pr"]]; rev = [x for x in m["review"] if x["t"] <= r["t_merge"] + 60]
    idx = [i for i, x in enumerate(rev) if x["v"] == "merge"]
    if not idx: continue
    later_block = [x for x in rev[idx[0] + 1:] if x["v"] == "blocked"]
    v = rev[idx[-1]] if later_block else rev[idx[0]]          # a block after approval is kept as a real repair
    full = next((s for s in by_sha if s.startswith(v["head"][:12])), None)
    ok = sorted(ts(x["updated_at"]) for x in by_sha.get(full, []) if x["conclusion"] == "success")
    green = ok[0] if ok else None
    if green: known_wait.append(max(0, green - v["t"]) / 3600)
    ent.append(dict(pr=r["pr"], files=r["files"], tv=v["t"], green=green, tm=r["t_merge"], claim=any(f in SERIAL_CLAIM for f in r["files"]),
                    conflict=any(c in ("merge-conflict", "main-conflict", "conflict") for c in r["blocked"]),
                    red=(m["sha"] in red_start) and (m["sha"] not in TRANSIENT or bool(int(__import__("os").environ.get("ALL_REAL", "0")))), flake=m["sha"] in TRANSIENT, t_first_merge=rev[idx[0]]["t"]))
FB = float(__import__("os").environ.get("FALLBACK_Q", ".5")); fallback = (q(known_wait, FB) if FB <= 1 else st.mean(known_wait)) * 3600
print("known waits for green at the reviewed head (h):", F(known_wait), "p75", round(q(known_wait,.75),2))
for e in ent:
    e["ready"] = max(e["tv"], e["green"]) if e["green"] else e["tv"] + fallback   # approved and green at the reviewed head
print(f"entries {len(ent)}; a green run at the reviewed head is recorded for {sum(1 for e in ent if e['green'])}; the others take the median wait of those ({fallback/3600:.2f} h)")
print(f"red-streak starts among these merges: real {sum(1 for e in ent if e['red'])}, transient (one red, green at the next merge) {sum(1 for e in ent if e['flake'])}")
H = 3600.0
today = [(e["tm"] - e["t_first_merge"]) / H for e in ent]
print("today, first merge verdict -> on main (null control, equals the measured segment):", F(today))
ready = [(e["ready"] - e["t_first_merge"]) / H for e in ent]
print("floor, first merge verdict -> approved and green at the reviewed head:            ", F(ready))

import math
sys.path.insert(0, _os.path.join(PD_REPO, "tools", "audit"))
try:
    import merge_fastpath as mf
    _g = mf.grader_specs(mf.workflow_texts("HEAD", git=lambda *a: subprocess.run(["git", "-C", PD_REPO, *a], capture_output=True, text=True).stdout))
    for e in ent: e["serial"] = sorted({c for f in e["files"] if (c := mf.file_class(f, _g))})
except Exception as ex:
    print("merge_fastpath unavailable:", ex); 
    for e in ent: e["serial"] = []
print("entries in a serial class today:", sum(1 for e in ent if e["serial"]), "of", len(ent))

def c2(W, par=3, cap=None):
    """Land at ready. One proof of the tip at a time; a red range is bisected with up to `par` prefix proofs
    in parallel per round; the green prefix promotes, the culprit is evicted, the rest re-prove with the next tip."""
    w = W * 60; order = sorted(ent, key=lambda e: e["ready"]); n = len(order)
    onmain = {}; flaked = set(); reruns = [0]; proofs = bis = 0; t = order[0]["ready"]; g = 0; evicted = set(); biggest = 0; red_lag = []
    while g < n:
        if order[g]["pr"] in evicted: g += 1; continue
        t = max(t, order[g]["ready"])
        k = g
        while k < n and order[k]["ready"] <= t: k += 1
        rng = [e for e in order[g:k] if e["pr"] not in evicted]; biggest = max(biggest, len(rng))
        t += w; proofs += 1
        if any(e["flake"] and e["pr"] not in flaked for e in rng) and not int(__import__("os").environ.get("ALL_REAL", "0")):
            flaked.update(e["pr"] for e in rng); t += w // 2; reruns[0] += 1     # failed jobs re-run once
        bad = [j for j, e in enumerate(rng) if e["red"]]
        if not bad:
            for e in rng: onmain[e["pr"]] = t
            g = k; continue
        j = bad[0]
        if len(rng) > 1:
            rounds = max(1, math.ceil(math.log(len(rng), par + 1))); t += rounds * w
            used = min(len(rng) - 1, par) * rounds; proofs += used; bis += used
        for e in rng[:j]: onmain[e["pr"]] = t          # the green prefix promotes
        c = rng[j]; evicted.add(c["pr"]); onmain[c["pr"]] = max(c["tm"], t)   # repaired on today's clock
        red_lag.append((t - c["ready"]) / 3600)
        # entries after the culprit stay landed and are proved with the next tip
        g = g + j + 1 if order[g + j]["pr"] == c["pr"] else g
        while g < n and order[g]["pr"] in onmain and order[g]["pr"] != c["pr"]: g += 1
        g = min(g, n)
        # recompute g as the first entry not yet on main
        g = next((x for x in range(n) if order[x]["pr"] not in onmain), n)
    return onmain, proofs, bis, biggest, red_lag, reruns[0]

def c1(W):
    """Heads are not moved by a clean merge of main. A batchable entry merges when approved and green; an entry
    in a serial class joins the next batch proof (wall W) and merges after it; claim and conflict entries and
    entries that reddened main keep today's recorded time."""
    w = W * 60; done = {}; p = 0
    ser = sorted([e for e in ent if e["serial"] and not (e["claim"] or e["conflict"])], key=lambda e: e["ready"]); i = 0; t = 0
    while i < len(ser):
        t = max(t, ser[i]["ready"]); b = []
        while i < len(ser) and ser[i]["ready"] <= t: b.append(ser[i]); i += 1
        t += w; p += 1
        for e in b: done[e["pr"]] = t
    for e in ent:
        if e["claim"] or e["conflict"]: done[e["pr"]] = e["tm"]
        elif not e["serial"]: done[e["pr"]] = e["ready"]
        if e["red"]: done[e["pr"]] = max(done[e["pr"]], e["tm"])
    return done, p

for W in [int(x) for x in sys.argv[1:]] or [60, 105]:
    onmain, proofs, bis, biggest, red_lag, reruns = c2(W)
    land = [(e["ready"] - e["t_first_merge"]) / H for e in ent]
    tomain = [(onmain[e["pr"]] - e["t_first_merge"]) / H for e in ent]
    lag = [(onmain[e["pr"]] - e["ready"]) / H for e in ent if not e["red"]]
    print(f"C2 W={W}: verdict -> landed (slot frees, successors start):", F(land))
    print(f"          verdict -> on main:                            ", F(tomain))
    print(f"          main lags a landing by:                        ", F(lag), f"max {max(lag):.2f} h")
    print(f"          proofs {proofs} incl. {bis} bisection proofs for {len(ent)} changes; largest proved range {biggest}; failed-job re-runs {reruns}; culprits {len(red_lag)}" + (f", known after mean {st.mean(red_lag):.2f} h, max {max(red_lag):.2f} h" if red_lag else ""))
    done, p = c1(W)
    v = [(done[e["pr"]] - e["t_first_merge"]) / H for e in ent]
    print(f"C1 W={W}: verdict -> on main:                            ", F(v), f"| batch proofs {p}, push runs on main {len(ent)}")
