"""Per PR run: which job finishes last, how long after the last REQUIRED tests.yml job,
and per small job its queue latency (started_at minus the latest completed_at of its needs)."""
import json, sys, statistics, datetime as dt
from pathlib import Path
D = Path(sys.argv[1]) / "raw"
REQ = {"fast (3.14)", "browser", "briefs", "closure-scope", "closures", "typing", "mutation"}
NEEDS = {"coverage-ratchet": ["coverage"], "lane-proofs": ["closure-scope", "fast (3.14)", "coverage", "browser"],
         "composed-proof": ["coverage", "closures"], "mutation-pin-plan": ["mutation"],
         "mutation-pins (1)": ["mutation-pin-plan"], "mutation-autofix": ["mutation-pins (1)"],
         "graders-head-copy": ["coverage"], "fast (3.14)": ["closure-scope"], "browser": ["closure-scope"],
         "coverage": ["closure-scope"], "closures": ["closure-scope", "coverage"]}
p = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
runs = json.load(open(D / "runs_pull_request.json"))["workflow_runs"]
used = [r for r in runs if r["id"] not in (39156531115, 39151682075)][:20]
tails, last, lat = [], {}, {}
for r in used:
    jobs = [j for j in json.load(open(D / f"jobs_{r['id']}.json"))["jobs"] if j["conclusion"] != "skipped" and j["completed_at"]]
    by = {j["name"]: j for j in jobs}
    end = max(jobs, key=lambda j: p(j["completed_at"]))
    req_end = max((p(j["completed_at"]) for j in jobs if j["name"] in REQ), default=None)
    last[end["name"]] = last.get(end["name"], 0) + 1
    if req_end and r["conclusion"] != "cancelled":
        tails.append(((p(end["completed_at"]) - req_end).total_seconds(), end["name"], r["id"]))
    for n, ns in NEEDS.items():
        if n in by and all(x in by for x in ns) and by[n]["started_at"]:
            q = (p(by[n]["started_at"]) - max(p(by[x]["completed_at"]) for x in ns)).total_seconds()
            if q >= 0: lat.setdefault(n, []).append(q)
print("last-finishing job per PR run:", dict(sorted(last.items(), key=lambda kv: -kv[1])))
print("seconds the run ran past its last required tests.yml job (non-cancelled):")
for t in sorted(tails): print(f"  {t[0]:7.0f}  {t[1]}  run {t[2]}")
print("queue latency after the last need completed (s): job n median max")
for n, v in sorted(lat.items()): print(f"  {n:22s} {len(v):2d} {statistics.median(v):6.1f} {max(v):6.0f}")
