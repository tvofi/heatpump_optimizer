"""Seconds each PR run would have ended sooner had composed-proof's `none` arm
(the job ran < 60 s: it decided there was nothing to prove) not run at all:
run end with every job, minus run end without that job."""
import json, sys, statistics, datetime as dt
from pathlib import Path
D = Path(sys.argv[1]) / "raw"
p = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
runs = json.load(open(D / "runs_pull_request.json"))["workflow_runs"]
used = [r for r in runs if r["id"] not in (39156531115, 39151682075)][:20]
gain, arms = [], {"none": 0, "self": 0}
for r in used:
    jobs = [j for j in json.load(open(D / f"jobs_{r['id']}.json"))["jobs"]
            if j["conclusion"] in ("success", "failure") and j["completed_at"]]
    cp = [j for j in jobs if j["name"] == "composed-proof"]
    if not cp:
        continue
    secs = (p(cp[0]["completed_at"]) - p(cp[0]["started_at"])).total_seconds()
    arm = "none" if secs < 60 else "self"
    arms[arm] += 1
    if arm == "none":
        end = max(p(j["completed_at"]) for j in jobs)
        rest = max(p(j["completed_at"]) for j in jobs if j["name"] != "composed-proof")
        gain.append((end - rest).total_seconds())
print("composed-proof arms over the PR runs it concluded in:", arms)
print("none-arm runs: seconds the run would have ended sooner:", sorted(gain))
print(f"median {statistics.median(gain)} s, max {max(gain)} s, n={len(gain)}")
