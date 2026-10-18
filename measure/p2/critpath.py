"""Which chain of Tests jobs ends each PR run, and what the needs edges cost.

    python3 -I measure/critpath.py measure/raw > measure/critpath.txt

Over the 20 PR runs phase 1 measured (raw/tests_jobs_<id>.json): for each run,
the run's end (last job completed), and for the edges coverage->closures and
closures->composed-proof: how long the dependent job sat between its need
finishing and starting (queue), and how long the run would have ended sooner if
`closures` had started when `closure-scope` finished instead of after `coverage`
(the lower bound of what dropping that edge buys, holding durations fixed).
"""
import json, statistics, sys
from datetime import datetime
from pathlib import Path
raw = Path(sys.argv[1])
def t(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None
runs = json.loads((raw / "tests_runs_pull_request.json").read_text())["workflow_runs"]
rows = []; gains = []; lastjob = {}; covwait = []
for r in runs:
    f = raw / f"tests_jobs_{r['id']}.json"
    if not f.exists(): continue
    J = {j["name"]: j for j in json.loads(f.read_text())["jobs"]}
    need = ("closure-scope", "coverage", "closures", "fast (3.14)")
    if not all(n in J and J[n]["conclusion"] in ("success", "failure") for n in need): continue
    st = t(r["run_started_at"])
    end_j = max((j for j in J.values() if j.get("completed_at") and j["conclusion"] != "skipped"), key=lambda j: t(j["completed_at"]))
    lastjob[end_j["name"]] = lastjob.get(end_j["name"], 0) + 1
    cs_end, cov_end = t(J["closure-scope"]["completed_at"]), t(J["coverage"]["completed_at"])
    cl_start, cl_end = t(J["closures"]["started_at"]), t(J["closures"]["completed_at"])
    cl_dur = cl_end - cl_start
    covwait.append(cl_start - cs_end)
    # counterfactual: closures starts ~queue after closure-scope; composed-proof and the rest follow closures by the same offsets
    alt_cl_end = cs_end + (cl_start - cov_end) + cl_dur
    others = [t(j["completed_at"]) for n, j in J.items() if j.get("completed_at") and j["conclusion"] != "skipped"
              and n not in ("closures", "composed-proof", "closures-autofix")]
    cp = J.get("composed-proof")
    cp_tail = (t(cp["completed_at"]) - cl_end) if cp and cp.get("completed_at") and cp["conclusion"] != "skipped" else 0
    new_end = max(others + [alt_cl_end + cp_tail])
    old_end = t(end_j["completed_at"])
    gains.append(old_end - new_end)
    rows.append((r["id"], round(old_end - st), round(cov_end - st), round(cl_start - cs_end), round(cl_dur), round(cp_tail), end_j["name"], round(old_end - new_end)))
print("run id      wall  cov_end  closures_waited  closures_dur  cp_tail  last job            gain_if_no_edge")
for x in rows: print(f"{x[0]}  {x[1]:5d}  {x[2]:6d}  {x[3]:14d}  {x[4]:12d}  {x[5]:7d}  {x[6]:18s}  {x[7]:6d}")
print(f"\nruns {len(rows)}; last job: {lastjob}")
print(f"closures waited after closure-scope: median {statistics.median(covwait):.0f} s")
print(f"run would end sooner without the coverage->closures edge: median {statistics.median(gains):.0f} s, max {max(gains):.0f} s, runs gaining >0: {sum(g > 0 for g in gains)}")
