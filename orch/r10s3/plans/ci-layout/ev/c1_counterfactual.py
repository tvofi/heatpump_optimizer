"""What the C1 coverage->closures composition costs the PR wall clock, two ways out.

    python3 -I measure/rev/c1_counterfactual.py measure/p2/raw --boost 480 > measure/rev/c1_counterfactual_480.txt
    python3 -I measure/rev/c1_counterfactual.py measure/p2/raw --sweep > measure/rev/c1_sweep.txt

Revision 1 (review item 8): the bare cost of tests/boost_drift_replay.py is a
PARAMETER. Phase 2 charged the 239.1 s recorded in tests/closures.json and called
it an upper bound; the CI runner's bare recordings measured 221 / 430 / 424 / 480 s
(design review ev/boost_bare_seconds.txt, closures job logs), so it is not one.
--boost S charges S seconds; --sweep prints the V1/V2 medians for S from 0 to
900 s and the S at which V1's median gain falls to V2's and to zero. Not modelled,
and only in V1's favour: V1 also removes strace from coverage's own run of the
script (coverage's end is held at its measured time).

Over the same PR runs as critpath.py, holding every other job's measured times fixed:
  V1 drop C1: `closures` starts when closure-scope ends (+ its measured queue) and
     records boost_drift_replay.py bare itself, charged BOOST seconds on every run
     (charged even where a scoped run's diff would not reach it); `composed-proof`
     and the coverage composed upload leave the PR graph.
  V2 split: `closures-record` starts when closure-scope ends; a short `closures`
     judge (needs coverage + closures-record) consumes the composed recording and
     runs the under-approximation check, charged a flat 120 s; composed-proof stays.
Prints per-run gains and medians. A negative gain means the variant is slower.
"""
import json, statistics, sys
from datetime import datetime
from pathlib import Path
import argparse
ap = argparse.ArgumentParser(); ap.add_argument("raw", type=Path)
ap.add_argument("--boost", type=float, default=239.1); ap.add_argument("--sweep", action="store_true")
A = ap.parse_args(); JUDGE = 120.0
raw = A.raw
def t(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None
runs = json.loads((raw / "tests_runs_pull_request.json").read_text())["workflow_runs"]
def replay(BOOST, show):
    g1, g2 = [], []
    if show: print("run id       wall   V1 gain  V2 gain")
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
        if show: print(f"{r['id']}  {end - t(r['run_started_at']):5.0f}  {end - v1:7.0f}  {end - v2:7.0f}")
    return g1, g2
if A.sweep:
    print("boost_s  V1_median  V1_slower  V2_median")
    rows = []
    for b in range(0, 901, 30):
        g1, g2 = replay(float(b), False); rows.append((b, statistics.median(g1), statistics.median(g2)))
        print(f"{b:7d}  {statistics.median(g1):9.0f}  {sum(g < 0 for g in g1):9d}  {statistics.median(g2):9.0f}")
    for b in (239.1, 427, 480):
        g1, g2 = replay(b, False)
        print(f"at {b:5} s: V1 median {statistics.median(g1):.0f}, slower {sum(g < 0 for g in g1)}/{len(g1)} (worst {min(g1):.0f}); V2 median {statistics.median(g2):.0f}")
    eq = next((b for b in range(0, 2001) if statistics.median(replay(float(b), False)[0]) <= statistics.median(replay(float(b), False)[1])), None)
    z = next((b for b in range(0, 4001, 5) if statistics.median(replay(float(b), False)[0]) <= 0), None)
    print(f"V1 median gain falls to V2's at boost >= {eq} s; to zero at boost >= {z} s")
    sys.exit(0)
g1, g2 = replay(A.boost, True)
print(f"\nboost charged {A.boost} s")
print(f"\nruns {len(g1)}")
print(f"V1 drop C1:  median gain {statistics.median(g1):.0f} s, min {min(g1):.0f}, max {max(g1):.0f}, runs slower {sum(g < 0 for g in g1)}")
print(f"V2 split:    median gain {statistics.median(g2):.0f} s, min {min(g2):.0f}, max {max(g2):.0f}, runs slower {sum(g < 0 for g in g2)}")
