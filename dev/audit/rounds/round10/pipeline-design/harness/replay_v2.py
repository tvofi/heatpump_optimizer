#!/usr/bin/env python3
"""Replay, revision 1 (answers R2, R4, R5, R6, R7, R11). One event loop, five rule sets, over the 215 recorded merges.

Kept from the record for every pull request: its merge verdicts; the PR head each judged (collect_heads.py); the
`gate` check-run at that head; what kind of commits followed that head; whether main's gate went red at its merge;
the direct pushes to main (main_moves.py).
Only heads made by a merge of main are removed by a candidate; a delivery-row or bot head after approval keeps its cycle.
A pull request LANDS AT ITS FIRST APPROVED HEAD only if nothing but mechanical commits followed it (merges of main,
the delivery row, bot commits). If the fixer authored commits after the first approval, or a blocked verdict
followed it, it lands at its LAST merge verdict's head.  ready = max(verdict, gate green at that head).
A head whose gate never concluded (superseded first) is imputed as head time + that day's median push-to-green;
a head whose gate concluded red and never green keeps today's recorded clock.

Rule sets:
  today   recorded number of mechanical head moves after the landing verdict, each costing that day's median
          push-to-green, plus the measured merge latency. THE NULL: it must reproduce the measured mean
          (first merge verdict to main) within TOL, or the loop does not model today and no saving is claimed.
  day1a   the first day-1 pull requests alone: no clean absorb by open_pr.sh, handoff_push.sh, remerge callers or a
          seat; the train still routes serial entries to one recarry each.
  day1    no clean absorb; grader, workflow and budget entries join a push-judged batch proof (one at a time, wall W),
          a lone batchable entry merges as today; a claim entry is recarried once; GitHub merges.
  day1+   the fallback end state (R7): as day1, and every entry is behind a proof before GitHub merges it.
  integ   the integration branch: lands at ready; serial proofs of the tip; main promoted on green.
          --seats: a red range is searched by cloud seats in one seat wall S instead of FULL prefix proofs.
          successors start at: landing | a seat's green gate at the landing (+S) | promotion.
A direct push to main (stamp, ledger App) restarts the proof in flight in day1, day1+ and integ.
Red: a recorded red-streak start of one red then green is transient (failed jobs re-run, half a wall);
the others are culprits: found by prefix bisection, ONE FULL proof at a time, then evicted to today's clock.
Usage: replay_v2.py [W minutes ...]   env: SEAT_H (default 1.1), TOL (default 0.20), ALL_REAL=1, CYCLE=median, OWN_RED=cycle, ROW=early"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
import json, sys, math, collections, statistics as st, subprocess
from datetime import datetime, timezone
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
def F(v): return f"mean {st.mean(v):5.2f}  p50 {q(v,.5):5.2f}  p90 {q(v,.9):5.2f}"
H = 3600.0; SEAT = float(_os.environ.get("SEAT_H", "1.1")) * H; TOL = float(_os.environ.get("TOL", "0.20")); ALL_REAL = _os.environ.get("ALL_REAL") == "1"
rows = {r["pr"]: r for r in json.load(open(PD_DATA + "baseline-2026-11-07.json"))}
ms = {m["pr"]: m for m in json.load(open(PD_DATA + "merges.json")) if m["pr"]}
heads = {int(k): v for k, v in json.load(open(PD_DATA + "heads.json")).items()}
gate = json.load(open(PD_DATA + "gate_heads.json")); moves = json.load(open(PD_DATA + "main_moves.json"))
mg = json.load(open(PD_DATA + "main_gate.json"))
def gate_at(sha):
    """(first SUCCESS time, any concluded FAILURE) of the gate check-run at a head."""
    ok = []; bad = False
    for s in gate.get(sha, []):
        for c in s["gate"]:
            if c["conclusion"] == "SUCCESS" and c["completedAt"]: ok.append(ts(c["completedAt"]))
            elif c["conclusion"] == "FAILURE": bad = True
    return (min(ok) if ok else None), bad
# main's reds, as in replay_pipeline.py
seq = []
for l in reversed(mg["log"]):
    sha, ct, subj = l.split(" ", 2); g = None
    for s in mg["suites"].get(sha, []):
        wr = s.get("workflowRun") or {}
        if wr.get("event") == "push" and (wr.get("workflow") or {}).get("name") == "CI":
            for c in s["checkRuns"]["nodes"]: g = c["conclusion"]
    seq.append((sha, g))
red_start = {}; prev = "SUCCESS"; cur = None
for sha, g in seq:
    if g in ("SUCCESS", "FAILURE"):
        if g == "FAILURE" and prev == "SUCCESS": cur = sha; red_start[sha] = 1
        elif g == "FAILURE" and cur: red_start[cur] += 1
        prev = g
day = lambda t: datetime.fromtimestamp(t, timezone.utc).strftime("%m-%d")
# push-to-green per day, over every judged head with a green gate (independent of the heads the model removes)
ptg = collections.defaultdict(list)
for pr, hd in heads.items():
    for p in {hd["p_first"], hd["p_last"]}:
        if p and p in hd["head_t"]:
            g, _ = gate_at(p)
            if g and g >= hd["head_t"][p]: ptg[day(hd["head_t"][p])].append(g - hd["head_t"][p])
allptg = [x for v in ptg.values() for x in v]
OWN_RED = _os.environ.get("OWN_RED", "today")   # today: a head red on its own gate keeps the recorded clock; cycle: one more cycle cures it
ROW = _os.environ.get("ROW", "kept")            # kept: a row or bot head after approval keeps its cycle; early: the row is on the head before review
CYC = _os.environ.get("CYCLE", "mean")          # the expected cost of one more head is the mean, not the median
def cyc(t):
    v = ptg.get(day(t)); v = v if v and len(v) >= 5 else allptg
    return st.mean(v) if CYC == "mean" else q(v, .5)
SER = {}
try:
    sys.path.insert(0, _os.path.join(PD_REPO, "tools", "audit"))
    import merge_fastpath as mf
    _g = mf.grader_specs(mf.workflow_texts("origin/main", git=lambda *a: subprocess.run(["git", "-C", PD_REPO, *a], capture_output=True, text=True).stdout))
    for pr, r in rows.items(): SER[pr] = {c for f in r["files"] if (c := mf.file_class(f, _g))}
except Exception as e:
    print("merge_fastpath unavailable:", e)
ent = []; cls = collections.Counter(); imputed = redown = 0
for pr, hd in heads.items():
    r = rows[pr]; m = ms[pr]
    af = hd["after_first"] or []
    c = "B" if hd["later_block"] else "A" if any(x["authored"] for x in af) else "M" if af else "U"
    late = c in ("A", "B"); p = hd["p_last"] if late else hd["p_first"]; tv = hd["t_last"] if late else hd["t_first"]
    after = (hd["after_last"] if late else hd["after_first"]) or []
    g, bad = gate_at(p) if p else (None, False); own_red = False
    if g: ready = max(tv, g); src = "gate"
    elif (bad or not p) and OWN_RED == "cycle" and p:                 # sensitivity: the red is cured by one re-dispatch at the same head
        fails = [ts(c["completedAt"]) for su in gate.get(p, []) for c in su["gate"] if c["conclusion"] == "FAILURE" and c["completedAt"]]
        ready = max(tv, max(fails)) + cyc(tv); own_red = True; redown += 1; src = "red-cured-in-one-cycle"
    elif bad or not p: ready = None; own_red = True; redown += 1; src = "red-or-unmapped"
    else: ready = max(tv, hd["head_t"].get(p, tv) + cyc(tv)); imputed += 1; src = "imputed"
    k = sum(1 for x in after if x["kind"] == "main" and x.get("pushed"))             # recorded heads made by a merge of main that CI ran at, after the landing verdict
    k2 = sum(1 for x in after if x["kind"] in ("row", "bot") and x.get("pushed"))   # row and bot heads: no candidate removes them
    conflict = any(x["authored"] for x in after) or any(cc in ("merge-conflict", "main-conflict", "conflict") for cc in r["blocked"])
    sha = m["sha"]; n = red_start.get(sha, 0)
    ent.append(dict(pr=pr, cls=c, t0=hd["t_first"], tv=tv, ready=ready, own_red=own_red, k=k, k2=k2, tm=r["t_merge"], src=src,
                    serial=SER.get(pr, set()), claim="claim" in SER.get(pr, set()), conflict=conflict, hotfix=r["kind"] == "hotfix",
                    culprit=n > 1 or (n == 1 and ALL_REAL), flake=n == 1 and not ALL_REAL))
    cls[c] += 1
U = [(e["tm"] - e["ready"]) / H for e in ent if e["cls"] == "U" and e["ready"] and e["src"] == "gate" and e["tm"] >= e["ready"]]
L = st.mean(U) * H
direct = sorted(x["t"] for x in moves if x["kind"] in ("stamp", "ledger App push"))
actual = [(e["tm"] - e["t0"]) / H for e in ent]
print(f"entries {len(ent)}; classes {dict(cls)} (U head never moved, M mechanical moves only, A fixer commits after approval, B blocked after approval)")
print(f"ready from the gate check-run {sum(1 for e in ent if e['src']=='gate')}; imputed (gate never concluded at the head) {imputed}; red on its own head or unmapped, {'cured by one more cycle' if OWN_RED == 'cycle' else 'kept on the recorded clock'} {redown}")
print(f"merge latency, gate green to main where the head never moved: n={len(U)} mean {st.mean(U):.2f} h p50 {q(U,.5):.2f} h; push-to-green over judged heads: mean {round(st.mean(allptg)/H,2)} h, median {round(q(allptg,.5)/H,2)} h; mean by day {dict((d, round(st.mean(v)/H,2)) for d, v in sorted(ptg.items()))}")
print(f"direct pushes to main in the window (stamps, ledger App): {len(direct)}; culprits {sum(e['culprit'] for e in ent)}, transient reds {sum(e['flake'] for e in ent)}")
print(f"MEASURED first merge verdict -> main: {F(actual)}")

def today():
    out = {}
    for e in ent:
        if e["ready"] is None: out[e["pr"]] = e["tm"]; continue
        t = e["ready"] + L
        for _ in range(e["k"] + e["k2"]): t += cyc(t)
        out[e["pr"]] = t
    return out

def proofs(W, mode, seats=False, preempt_hotfix=False):
    """mode: day1 | day1+ | integ. Returns (slot/landing time, on-main time, stats)."""
    w = W * 60; done = {}; land = {}; stat = collections.Counter(); lag = []
    def restart(t0, dur):                       # a proof started at t0 of length dur, restarted by each direct push inside it
        t = t0
        while True:
            hit = [d for d in direct if t < d <= t + dur]
            if not hit: return t + dur
            stat["restarts"] += 1; t = hit[0]
    live = []
    for e in ent:
        if e["ready"] is None: done[e["pr"]] = land[e["pr"]] = e["tm"]; continue
        r = e["ready"]
        for _ in range(e["k2"] if ROW == "kept" else 0): r += cyc(r)                         # the row and bot heads stay
        if mode != "integ":
            if e["conflict"]: done[e["pr"]] = land[e["pr"]] = e["tm"]; continue           # a real conflict keeps today's clock
            if e["claim"]: r += cyc(r); stat["claim recarries"] += 1                          # GitHub cannot run the driver
            if mode == "day1a":                                                              # NO-ABSORB alone: the train still recarries a serial entry once
                if e["serial"] - {"claim"} and not e["claim"]: r += cyc(r); stat["train recarries"] += 1
                live.append((r, e, False)); continue
            if mode == "day1" and not e["serial"] - {"claim"} and not e["claim"]:
                live.append((r, e, False)); continue
        live.append((r, e, True))
    live.sort(key=lambda x: x[0]); t = 0; i = 0; n = len(live); evicted = set(); queue = []
    # lone batchable entries in day1 merge unproved at once
    prove = [x for x in live if x[2]]; free = [x for x in live if not x[2]]
    for r, e, _ in free:
        done[e["pr"]] = land[e["pr"]] = (max(e["tm"], r + L) if e["culprit"] else r + L); stat["merged unproved"] += 1
        if e["culprit"]: stat["main reddened by an unproved entry"] += 1
    g = 0; order = prove; n = len(order)
    if mode == "integ":
        for r, e, _ in order: land[e["pr"]] = r + L
    while g < n:
        r0 = order[g][0] + (L if mode == "integ" else 0); t = max(t, r0); k = g
        while k < n and order[k][0] + (L if mode == "integ" else 0) <= t: k += 1
        rng = [x[1] for x in order[g:k]]; stat["largest range"] = max(stat["largest range"], len(rng))
        t = restart(t, w); stat["proofs"] += 1
        if any(e["flake"] for e in rng if e["pr"] not in evicted and not e.get("_fl")):
            for e in rng: e["_fl"] = True
            t = restart(t, w // 2); stat["failed-job re-runs"] += 1
        bad = [j for j, e in enumerate(rng) if e["culprit"]]
        if not bad:
            for e in rng:
                done[e["pr"]] = t + (L if mode != "integ" else 0)
                if mode != "integ": land[e["pr"]] = done[e["pr"]]
            g = k; continue
        j = bad[0]; c = rng[j]
        if len(rng) > 1:
            if seats: t += SEAT; stat["seat runs"] += len(rng) - 1; t = restart(t, w) if j else t; stat["proofs"] += 1 if j else 0
            else:
                steps = math.ceil(math.log2(len(rng)))
                for _ in range(steps): t = restart(t, w)
                stat["proofs"] += steps; stat["bisection proofs"] += steps
        for e in rng[:j]:
            done[e["pr"]] = t + (L if mode != "integ" else 0)
            if mode != "integ": land[e["pr"]] = done[e["pr"]]
        evicted.add(c["pr"]); done[c["pr"]] = max(c["tm"], t); land[c["pr"]] = done[c["pr"]]; stat["evicted"] += 1
        stat_c.append((t - c["ready"]) / H)
        order = order[:g] + [x for x in order[g:] if x[1]["pr"] not in done]; n = len(order)
    return land, done, stat

for e in ent: e.pop("_fl", None)
T = today(); tm = [(T[e["pr"]] - e["t0"]) / H for e in ent]
dev = (st.mean(tm) - st.mean(actual)) / st.mean(actual)
print(f"NULL  today's rules through the loop:      {F(tm)}   deviation from measured {dev*100:+.1f} % (tolerance {TOL*100:.0f} %): {'PASS' if abs(dev) <= TOL else 'FAIL'}")
for c in "UMAB":
    a = [(e["tm"] - e["t0"]) / H for e in ent if e["cls"] == c]; b = [(T[e["pr"]] - e["t0"]) / H for e in ent if e["cls"] == c]
    if a: print(f"        class {c}: n={len(a):3d} measured mean {st.mean(a):6.2f}  loop {st.mean(b):6.2f}")
base = st.mean(tm)
for W in [int(x) for x in sys.argv[1:]] or [45, 60, 75, 105]:
    print(f"--- proof wall {W} min")
    for name, kw in (("day1a (no clean absorb by instruments and seats; the train still recarries serial entries)", dict(mode="day1a")), ("day1 ", dict(mode="day1")), ("day1+", dict(mode="day1+")), ("integ, FULL-proof bisection", dict(mode="integ")), ("integ, seat search       ", dict(mode="integ", seats=True))):
        for e in ent: e.pop("_fl", None)
        stat_c = []
        land, done, s = proofs(W, **kw)
        lv = [(land[e["pr"]] - e["t0"]) / H for e in ent]; dv = [(done[e["pr"]] - e["t0"]) / H for e in ent]
        line = f"{name}: to main {F(dv)}"
        if kw["mode"] == "integ":
            lg = [(done[e["pr"]] - land[e["pr"]]) / H for e in ent if not e["culprit"] and e["ready"]]
            sg = [(min(done[e["pr"]], land[e["pr"]] + SEAT) - e["t0"]) / H for e in ent]
            line += f" | landed mean {st.mean(lv):5.2f} | landed + seat gate mean {st.mean(sg):5.2f} | main trails mean {st.mean(lg):5.2f} max {max(lg):5.2f}"
        print(" ", line)
        print("       ", {k: v for k, v in s.items()}, ("culprit known after mean %.2f max %.2f h" % (st.mean(stat_c), max(stat_c))) if stat_c else "")
        key = "to main" if kw["mode"] != "integ" else "landed"
        v = dv if kw["mode"] != "integ" else lv
        print(f"        saving against the loop's today ({base:.2f} h): slot freed at {'main' if kw['mode']!='integ' else 'landing'} {base - st.mean(v):5.2f} h; at main {base - st.mean(dv):5.2f} h" + (f"; at landing + seat gate {base - st.mean(sg):5.2f} h" if kw["mode"] == "integ" else ""))
