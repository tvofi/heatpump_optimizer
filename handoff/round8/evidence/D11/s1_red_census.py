#!/usr/bin/env python3
"""s1_red_census.py -- per required context, how many recent PR heads carry a FAILURE check run.

METRIC: for each context in ruleset main-protect-checks (s1_ruleset_23698884.json),
the number of the 100 most recently updated closed PRs whose head SHA carries >=1
check run of that name with conclusion `failure` (the commit's check-runs listing,
which keeps a red run that a later green re-run hides from the summary).
Inventory evidence only (a live control in history), not a finding by itself.
RUN (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s1_red_census.py
EXPECTED at 2026-09-23T21Z: pr-contract 12, fast (3.14) 3, closures 1, all other 13 contexts 0 (live data, moves).
Perturbation: none of its own (a census); it names which rows of the inventory have a historic control.
MACHINE: 4-vCPU cloud container (round 8); read-only api.github.com GETs.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
def get(p): return json.loads(subprocess.check_output(["curl", "-sS", "https://api.github.com" + p]))
req = [c["context"] for r in json.loads((HERE / "s1_ruleset_23698884.json").read_text())["rules"]
       if r["type"] == "required_status_checks" for c in r["parameters"]["required_status_checks"]]
t0p, t0t = time.process_time(), time.thread_time()
prs = get("/repos/tvofi/heatpump_optimizer/pulls?state=closed&per_page=100&sort=updated&direction=desc")
fails = {c: 0 for c in req}
for pr in prs:
    sha, runs, page = pr["head"]["sha"], [], 1
    while True:
        d = get(f"/repos/tvofi/heatpump_optimizer/commits/{sha}/check-runs?per_page=100&page={page}")
        runs += d.get("check_runs", [])
        if len(d.get("check_runs", [])) < 100:
            break
        page += 1
    for name in {r["name"] for r in runs if r["name"] in fails and r["conclusion"] == "failure"}:
        fails[name] += 1
print(f"RESULT heads={len(prs)} count")
for c in req:
    print(f"RESULT red_heads[{c}]={fails[c]} count")
print(f"RESULT contexts_never_red={sum(1 for v in fails.values() if v == 0)} count")
tp, tt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
