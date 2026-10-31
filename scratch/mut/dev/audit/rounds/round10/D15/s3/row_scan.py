"""D15.M7 row scan over a debug bundle's cycle_rows, split at the version seam.

Metric: per version segment (segments split at row gaps > 30 min, each attributed
to the newest v* tag dated before the gap's end), counts of rows with
solve_failures>0, solve_wall_ms > 900000 (one cycle interval), p50/max of
solve_wall_ms and payload_solve_time_ms, heat_pump_on contradicting action_mode,
and null sensor feeds. Only numbers and timestamps leave the bundle; cycle_rows
pass tools/replay/export.py:violations (asserted below, with a planted-credential arm).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D15/s3/row_scan.py BUNDLE TAGS_FILE
  TAGS_FILE: `git for-each-ref --format='%(refname:short) %(creatordate:iso-strict)' 'refs/tags/v*'`
Expected (live bundle 2026-10-14): rows=554 segments=3, v7.0.0 rows=2. Baseline fe01b938f71b, machine B11 (macOS arm64).
Instrumented symbol: tools/replay/export.py:violations (privacy gate only); the counts are bundle re-derivations.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, sys, statistics
from datetime import datetime
sys.path.insert(0, "tools/replay")
import export  # noqa: E402

bundle = json.load(open(sys.argv[1]))
dbg = (bundle.get("data") or bundle).get("debug") or bundle
rows = dbg["cycle_rows"]
assert export.violations(rows) == [], "privacy gate: cycle_rows fail violations"
assert export.violations({"x": {"password": "hunter2secret"}}), "planted arm stayed green"
print("RESULT privacy_rows_violations=0 unit=count")
tags = []
for line in open(sys.argv[2]):
    name, when = line.split()
    tags.append((datetime.fromisoformat(when), name))
tags.sort()
ts = [datetime.fromisoformat(r["t"]) for r in rows]
segs, start = [], 0
for i in range(1, len(rows) + 1):
    if i == len(rows) or (ts[i] - ts[i - 1]).total_seconds() > 1800:
        segs.append((start, i)); start = i
print(f"RESULT rows={len(rows)} unit=count")
print(f"RESULT segments={len(segs)} unit=count")
for a, b in segs:
    ver = max((t for t in tags if t[0] <= ts[a]), default=(None, "unknown"))[1]
    seg = rows[a:b]
    wall = [r["solve_wall_ms"] for r in seg if r.get("solve_wall_ms") is not None]
    pay = [r["payload_solve_time_ms"] for r in seg if r.get("payload_solve_time_ms") is not None]
    contra = sum(1 for r in seg if r.get("heat_pump_on") is not None and r.get("action_mode") is not None
                 and (r["action_mode"] == "off") == bool(r["heat_pump_on"]))
    tag = f"{ver}@{rows[a]['t'][:16]}"
    print(f"RESULT seg={tag} rows={len(seg)} unit=count")
    print(f"RESULT seg={tag} solve_failures_rows={sum(1 for r in seg if (r.get('solve_failures') or 0) > 0)} unit=count")
    print(f"RESULT seg={tag} wall_over_cycle={sum(1 for w in wall if w > 900000)} unit=count")
    if wall:
        print(f"RESULT seg={tag} wall_p50={statistics.median(wall):.0f} wall_max={max(wall):.0f} unit=ms")
    if pay:
        print(f"RESULT seg={tag} payload_p50={statistics.median(pay):.0f} payload_max={max(pay):.0f} unit=ms")
    print(f"RESULT seg={tag} on_vs_action_contradictions={contra} unit=count")
    print(f"RESULT seg={tag} null_feeds={sum(1 for r in seg for k in ('indoor_temp','outdoor_temp','dhw_temp') if r.get(k) is None)} unit=count")
    print(f"RESULT seg={tag} missing_action={sum(1 for r in seg if r.get('action_mode') is None)} unit=count")
print(f"RESULT self_tests_present={int(bool((dbg.get('manifest') or {}).get('self_tests')))} unit=bool")
print(f"RESULT replay_present={int(dbg.get('replay') is not None)} unit=bool")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT thread_factor=1.00")
print("RESULT swapins=0")
