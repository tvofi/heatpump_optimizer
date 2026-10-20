#!/usr/bin/env python3
"""Reviewer's own arithmetic check of plan.json against the body's figures.

Run: python3 -I arith.py <plan.json> <durations.json>
Prints one RESULT line per claim. Nothing is imported from tools/plan.
"""
import json
import sys
from datetime import datetime, timezone

plan = json.load(open(sys.argv[1]))
dur = json.load(open(sys.argv[2]))


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


s = plan["summary"]
groups = {n: g for n, g in plan["groups"].items() if not g.get("done")}

# 1. closure from the groups, independently of summary
last = max(ts(g["finish"]) for g in groups.values())
start = ts(plan["generated"]["start"])
wall_h = (last - start).total_seconds() / 3600.0
print(f"RESULT closure_from_groups={last.strftime('%Y-%m-%dT%H:%M:%SZ')} "
      f"wall_hours={wall_h:.4f} | body claims 2026-10-30T03:17Z 226.28")

# 2. critical path: recompute longest chain by per-group duration over after-edges
dur_min = {n: g["duration_minutes"] for n, g in groups.items()}


def is_done(n):
    return plan["groups"][n].get("done")


memo = {}


def longest(n):
    """(minutes, path) of the longest chain ENDING at n (deps first)."""
    if n in memo:
        return memo[n]
    best = (0, [])
    for a in plan["groups"][n].get("after") or []:
        if a not in groups:
            continue
        m, p = longest(a)
        if m > best[0]:
            best = (m, p)
    res = (best[0] + dur_min[n], best[1] + [n])
    memo[n] = res
    return res


best = (0, [])
for n in groups:
    m, p = longest(n)
    if m > best[0]:
        best = (m, p)
print(f"RESULT critical_chain_minutes={best[0]} hours={best[0]/60:.4f} links={len(best[1])} "
      f"| body claims 226.28 h over 12 links")
print(f"RESULT critical_chain={'>'.join(best[1])}")
cp = plan["critical_path"]
cp_min = sum(dur_min[n] for n in cp)
print(f"RESULT plan_critical_path_links={len(cp)} hours={cp_min/60:.4f} "
      f"same_as_recomputed={cp == best[1]}")

# 3. queueing: wall == chain means no capacity queueing. Also count groups whose
#    start is later than the latest finish of any dependency (pure dep wait),
#    versus groups that waited with dependencies all merged (capacity wait).
capacity_waits = []
for n, g in groups.items():
    dep_finish = [ts(plan["groups"][a]["finish"]) for a in g.get("after") or []
                  if a in groups]
    if not dep_finish:
        continue
    latest = max(dep_finish)
    if ts(g["start"]) > latest:
        capacity_waits.append((n, int((ts(g["start"]) - latest).total_seconds() // 60)))
print(f"RESULT wall_equals_chain={abs(wall_h*60 - best[0]) < 1e-9} "
      f"groups_started_after_all_deps_merged={len(capacity_waits)} "
      f"(>0 means slot/queueing delay somewhere)")

# 4. batches and stamps from the lists
print(f"RESULT batches={len(plan['batches'])} stamps={len(plan['stamps'])} "
      f"patch_stamps={sum(1 for x in plan['stamps'] if x['kind']=='patch')} "
      f"minor_stamps={sum(1 for x in plan['stamps'] if x['kind']=='minor')}")
print(f"RESULT summary_batches={s['batches']} summary_stamps={s['stamps']}")

# 5. gate minutes, independently: one gate run per batch + one per stamp
ci = dur["ci"]
fast = ci["fast (3.14)"]["median_minutes"]
clo = ci["closures"]["median_minutes"]
ana = ci["Analyze (python)"]["median_minutes"]
rate = ci["Analyze (python)"]["cancelled_rate"]
gate = fast + clo + ana * (1.0 + rate)
runs = len(plan["batches"]) + len(plan["stamps"])
print(f"RESULT gate_per_run={gate:.6f} runs={runs} gate_minutes={runs*gate:.4f} "
      f"| body claims 51 runs, 5778.4; plan summary {s['ci_minutes']}")

# 6. per-run medians against the body's figures
print(f"RESULT medians fast={fast} closures={clo} analyze={ana} cancelled_rate={rate}")
print(f"RESULT n fast={ci['fast (3.14)']['n']} closures={ci['closures']['n']} "
      f"analyze={ci['Analyze (python)']['n']} cancelled={ci['Analyze (python)'].get('cancelled')}")
print(f"RESULT iqr fast={ci['fast (3.14)']['iqr']} closures={ci['closures']['iqr']} "
      f"analyze={ci['Analyze (python)']['iqr']}")
print(f"RESULT durations_measured_at={dur['provenance'].get('measured_at')} "
      f"merges={dur['provenance'].get('merges')}")

# 7. inherited coordinator record
ic = plan["generated"]["inherited_coordinator"]
print(f"RESULT inherited_coordinator cap={ic['cap']} groups={ic['groups']} "
      f"exceeds_cap={ic['exceeds_cap']} | body claims 3 groups, cap 2")
print(f"RESULT inherited_in_progress={s['inherited_in_progress']} "
      f"inherited_dep_violations={len(plan['generated']['inherited_dependency_violations'])}")
print(f"RESULT roster_ref={plan['generated']['roster_ref']} "
      f"roster_blob={plan['generated']['roster_blob']}")

# 8. every open group scheduled exactly once; start <= finish
print(f"RESULT groups_open={len(groups)} summary_groups_open={s['groups_open']} "
      f"all_scheduled={all(g['start'] and g['finish'] for g in groups.values())} "
      f"start_le_finish={all(ts(g['start']) <= ts(g['finish']) for g in groups.values())}")
