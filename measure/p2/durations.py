"""Per-workflow, per-job executed counts and durations over the saved PR runs.

    python3 -I measure/durations.py measure/raw > measure/durations.txt

Reads raw/runs_<wf>_pr.json and raw/jobs_<id>.json (fetch.sh, fetch2.sh). Duration =
completed_at - started_at of jobs that concluded success or failure; nearest-rank p90.
Also prints, per workflow, the red jobs (what made 9 of 10 Governance runs red, say).
"""
import json, sys, statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
def p90(xs):
    xs = sorted(xs); return xs[max(0, -(-len(xs) * 9 // 10) - 1)] if xs else None

raw = Path(sys.argv[1])
for wf in ("governance", "codeql", "hassfest", "validate", "pr-contract", "arch-score", "budget-raise-gate"):
    runs = json.loads((raw / f"runs_{wf}_pr.json").read_text())["workflow_runs"]
    per = defaultdict(list); execd = defaultdict(int); seen = defaultdict(int); red = defaultdict(int)
    walls = []
    for r in runs:
        f = raw / f"jobs_{r['id']}.json"
        if not f.exists(): continue
        jobs = json.loads(f.read_text())["jobs"]
        ends = [ts(j["completed_at"]) for j in jobs if j.get("completed_at")]
        if ends and r.get("run_started_at"): walls.append(max(ends) - ts(r["run_started_at"]))
        for j in jobs:
            seen[j["name"]] += 1
            if j["conclusion"] != "skipped": execd[j["name"]] += 1
            if j["conclusion"] in ("failure", "timed_out"): red[j["name"]] += 1
            if j["conclusion"] in ("success", "failure") and j.get("started_at") and j.get("completed_at"):
                per[j["name"]].append(max(0, ts(j["completed_at"]) - ts(j["started_at"])))
    print(f"## {wf}: {len(runs)} PR runs; run wall median {statistics.median(walls):.0f} s, p90 {p90(walls):.0f} s")
    for n in sorted(seen):
        d = per[n]
        med = f"{statistics.median(d):.0f}" if d else "-"
        print(f"  {n:40s} executed {execd[n]}/{seen[n]}  red {red[n]}  median {med} s  p90 {p90(d) if d else '-'} s")
    print()
