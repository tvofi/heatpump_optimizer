"""What the C1 coverage->closures composition costs the PR wall clock, two ways out.

    python3 -I measure/c1_counterfactual.py measure/raw > measure/c1_counterfactual.txt

Over the same PR runs as critpath.py, holding every other job's measured times fixed:
  V1 drop C1: `closures` starts when closure-scope ends (+ its measured queue) and
     records boost_drift_replay.py bare itself, charged at its full recorded 239.1 s
     (tests/closures.json `recorded`; an UPPER bound: charged on every run, though a
     scoped run records it only when its diff reaches it); `composed-proof` and the
     coverage composed upload leave the PR graph.
  V2 split: `closures-record` starts when closure-scope ends; a short `closures`
     judge (needs coverage + closures-record) consumes the composed recording and
     runs the under-approximation check, charged a flat 120 s; composed-proof stays.
Prints per-run gains and medians. A negative gain means the variant is slower.
"""
import json, statistics, sys
from datetime import datetime
from pathlib import Path
BOOST, JUDGE = 480, 120.0
raw = Path(sys.argv[1])
def t(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None
runs = json.loads((raw / "tests_runs_pull_request.json").read_text())["workflow_runs"]
g1, g2 = [], []
print("run id       wall   V1 gain  V2 gain")
for r in runs:
    f = raw / f"tests_jobs_{r['id']}.json"
    if not f.exists(): continue
    J = {j["name"]: j for j in json.loads(f.read_text())["jobs"]}
    if not all(n in J and J[n]["conclusion"] in ("success", "failure") for n in ("closure-scope", "coverage", "closures")): continue
    done = [j for j in J.values() if j.get("completed_at") and j["conclusion"] != "skipped"]
    end = max(t(j["completed_at"]) for j in done)
    cs_end, cov_end = t(J["closure-scope"]["completed_at"]), t(J["coverage"]["completed_at"])
    cl_s, cl_e = t(J["closures"]["started_at"]), t(J["closures"]["completed_at"])
    q = cl_s - cov_end; dur = cl_e - cl_s
    cp = J.get("composed-proof"); cp_tail = (t(cp["completed_at"]) - cl_e) if cp and cp.get("completed_at") and cp["conclusion"] != "skipped" else 0
    rest = [t(j["completed_at"]) for n, j in J.items() if j in done and n not in ("closures", "composed-proof", "closures-autofix")]
    v1 = max(rest + [cs_end + q + dur + BOOST])
    rec_end = cs_end + q + dur
    v2_cl = max(cov_end, rec_end) + q + JUDGE
    v2 = max(rest + [v2_cl + cp_tail])
    g1.append(end - v1); g2.append(end - v2)
    print(f"{r['id']}  {end - t(r['run_started_at']):5.0f}  {end - v1:7.0f}  {end - v2:7.0f}")
print(f"\nruns {len(g1)}")
print(f"V1 drop C1:  median gain {statistics.median(g1):.0f} s, min {min(g1):.0f}, max {max(g1):.0f}, runs slower {sum(g < 0 for g in g1)}")
print(f"V2 split:    median gain {statistics.median(g2):.0f} s, min {min(g2):.0f}, max {max(g2):.0f}, runs slower {sum(g < 0 for g in g2)}")
