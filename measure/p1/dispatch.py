"""Dispatch runs: recheck-gate's own duration and the gap from run start to the first heavy lane's start."""
import json, sys, statistics, datetime as dt
from pathlib import Path
D = Path(sys.argv[1]) / "raw"
p = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = []
for r in json.load(open(D / "runs_workflow_dispatch.json"))["workflow_runs"]:
    jobs = {j["name"]: j for j in json.load(open(D / f"jobs_{r['id']}.json"))["jobs"]}
    g = jobs.get("recheck-gate")
    if not g or g["conclusion"] != "success":
        continue
    gs = (p(g["completed_at"]) - p(g["started_at"])).total_seconds()
    heavy = [j for n, j in jobs.items() if n in ("briefs", "typing", "mutation", "slow", "mutation-nightly") and j["conclusion"] != "skipped"]
    first = min((p(j["started_at"]) for j in heavy), default=None)
    wait = (first - p(r["run_started_at"])).total_seconds() if first else None
    ran = sorted(n for n, j in jobs.items() if j["conclusion"] != "skipped")
    rows.append((r["id"], r["head_branch"], gs, wait, "slow" in ran or "mutation-nightly" in ran))
    print(r["id"], r["head_branch"][:30], f"gate {gs:.0f}s", f"first-lane-after-start {wait}", "nightly-arm" if rows[-1][4] else "recheck-arm")
g = [x[2] for x in rows]; w = [x[3] for x in rows if x[3] is not None]
print(f"n={len(rows)} recheck-gate median {statistics.median(g)} s; run start -> first gated lane start median {statistics.median(w)} s max {max(w)}")
