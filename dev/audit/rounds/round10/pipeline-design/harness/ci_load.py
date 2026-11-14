#!/usr/bin/env python3
"""Baseline step 4: ci.yml run walls by event and day, main push outcomes, and what a merge costs on main."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, glob, collections, statistics as st, sys
from datetime import datetime, timezone
D = PD_DATA
def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()) if s else None
def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
runs = {}
for f in glob.glob(D + "runs/*.json"):
    for r in json.load(open(f))["runs"]: runs[r["id"]] = r
rs = list(runs.values()); print("ci.yml runs", len(rs), "attempts", sum(r["run_attempt"] for r in rs))
day = lambda r: r["created_at"][:10]
ev = collections.Counter((day(r), r["event"]) for r in rs)
days = sorted({day(r) for r in rs})
print("runs per day by event:")
for d in days: print(" ", d, {e: ev[(d, e)] for e in ("pull_request", "pull_request_review", "push", "workflow_dispatch", "merge_group") if ev[(d, e)]})
def wall(r): return (ts(r["updated_at"]) - ts(r["created_at"])) / 60.0
# a "code run" proxy: wall >= 15 min and concluded (edit/review runs exit in a few minutes)
print("walls (created->updated, minutes), attempt-1 runs concluded success:")
for e in ("push", "pull_request", "workflow_dispatch"):
    for d in days:
        v = [wall(r) for r in rs if r["event"] == e and day(r) == d and r["conclusion"] == "success" and r["run_attempt"] == 1]
        long = [x for x in v if x >= 15]
        if v: print(f"  {e:18s} {d} n={len(v):3d} long(>=15m) n={len(long):3d} p50={q(long,.5) if long else 0:6.1f} p90={q(long,.9) if long else 0:6.1f} max={max(v):6.1f}")
push = sorted([r for r in rs if r["event"] == "push"], key=lambda r: r["created_at"])
print("main push runs:", len(push), dict(collections.Counter(r["conclusion"] for r in push)), "attempts>1:", sum(1 for r in push if r["run_attempt"] > 1))
print("  by day:", {d: dict(collections.Counter(r["conclusion"] for r in push if day(r) == d)) for d in days})
# longest run of consecutive non-success on main
streak = best = 0
for r in push:
    streak = 0 if r["conclusion"] == "success" else streak + 1; best = max(best, streak)
print("  longest consecutive non-success push runs:", best)
# concurrency of ci.yml runs with wall >= 15 min (code runs), sampled each 5 min
ev2 = []
for r in rs:
    if r["conclusion"] in (None,) : continue
    s, e = ts(r["run_started_at"]), ts(r["updated_at"])
    if e - s >= 900: ev2.append((s, e))
t0 = ts("2026-11-07T00:00:00Z"); t1 = ts("2026-11-14T00:00:00Z"); hist = collections.Counter(); byday = collections.defaultdict(list)
for t in range(t0, t1, 300):
    n = sum(1 for s, e in ev2 if s <= t < e); hist[min(n, 12)] += 1
    byday[datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")].append(n)
tot = sum(hist.values())
print("concurrent long (>=15 min) ci.yml runs, share of 5-min samples:", {k: round(v / tot, 3) for k, v in sorted(hist.items())})
print("  mean concurrent long runs by day:", {d: round(st.mean(v), 2) for d, v in sorted(byday.items())})
print("run wall hours (started->updated) by event over the window:", {e: round(sum((ts(r['updated_at']) - ts(r['run_started_at'])) for r in rs if r['event'] == e and r['conclusion']) / 3600) for e in ("push", "pull_request", "pull_request_review", "workflow_dispatch")})
print("conclusions by event:", {e: dict(collections.Counter(r["conclusion"] for r in rs if r["event"] == e)) for e in ("push", "pull_request", "pull_request_review", "workflow_dispatch")})
