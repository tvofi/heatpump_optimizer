#!/usr/bin/env python3
"""D13 / round 9 / seat s1 -- D13.M5: CI seconds per merge, governance vs gate.

METRIC: per window merge (API-mode population, v6.6.0..1936d5ca), at the PR
HEAD (as tools/audit/round4/D11/governance_cost.py measures): governance
seconds = sum of production governance_cost.py:dur over check runs whose name
is in the governance set; gate seconds = the same over every other run that
CONCLUDED and was not skipped. Taken twice: with the production
governance_cost.py:GOV, and with the set RE-DERIVED at the window's head from
the workflow files by GOV's own stated rule (governance_cost.py's comment above
GOV: every job in governance.yml, plus `briefs` in tests.yml, plus the jobs of
pr-contract.yml and budget-raise-gate.yml "governance jobs held in their own
files") -- read here as: every job of governance.yml, pr-contract.yml and any
budget-raise-gate*.yml, plus `briefs`. The delta names each job the pinned set
misses and the seconds it moves from governance to gate.
COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D13/s1/gov_cost.py
PERTURBATION: D13_GOV_DROP=pr-contract removes one name from the production
  GOV in memory; governance_share must fall.
EXPECTED at 1936d5ca: exact (GitHub-reported durations, closed window).
MACHINE: any. BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")
import glob  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402

import yaml  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "round4", "D11"))
import r9lib as L  # noqa: E402
import governance_cost as GC  # noqa: E402  production instrument under test


def jobs(path):
    d = yaml.safe_load(open(path))
    return set((d.get("jobs") or {}).keys())


def rederive():
    s = set(jobs(".github/workflows/governance.yml"))
    s |= jobs(".github/workflows/pr-contract.yml")
    for f in glob.glob(".github/workflows/budget-raise-gate*.yml"):
        s |= jobs(f)
    s.add("briefs")
    return s


def split(runs, gov):
    g = sum(GC.dur(c) for c in runs if c["name"] in gov)
    t = sum(GC.dur(c) for c in runs if c["name"] not in gov
            and c.get("conclusion") not in (None, "skipped"))
    return g, t


def main():
    snap = L.load_snapshot()
    seen, merges = set(), []
    for c in snap["commits"]:
        if not c.get("pulls"):
            continue
        n = str(c["pulls"][0]["number"])
        if n not in seen:
            seen.add(n)
            merges.append((n, c))
    prod = set(GC.GOV) - {os.environ.get("D13_GOV_DROP", "")}
    der = rederive()
    L.result("gov_prod", ",".join(sorted(prod)))
    L.result("gov_rederived_minus_prod", ",".join(sorted(der - prod)) or "-")
    L.result("gov_prod_minus_rederived", ",".join(sorted(prod - der)) or "-")
    names = set()
    for surf in ("head", "merge"):
        gs, ts, gs2, ts2 = [], [], [], []
        miss_secs = {}
        for pr, c in merges:
            runs = (snap["prs"][pr].get("runs_head") if surf == "head"
                    else c.get("runs")) or []
            names |= {r["name"] for r in runs}
            g, t = split(runs, prod)
            g2, t2 = split(runs, der)
            gs.append(g); ts.append(t); gs2.append(g2); ts2.append(t2)
            for r in runs:
                if r["name"] in der - prod:
                    miss_secs[r["name"]] = miss_secs.get(r["name"], 0) + GC.dur(r)
        n = len(gs)
        L.result(f"{surf}_merges", n)
        L.result(f"{surf}_gov_seconds_mean_prod", round(statistics.mean(gs), 1), "s/merge")
        L.result(f"{surf}_gate_seconds_mean_prod", round(statistics.mean(ts), 1), "s/merge")
        L.result(f"{surf}_gov_seconds_median_prod", round(statistics.median(gs), 1), "s/merge")
        L.result(f"{surf}_gate_seconds_median_prod", round(statistics.median(ts), 1), "s/merge")
        L.result(f"{surf}_governance_share_prod", round(sum(gs) / (sum(gs) + sum(ts)), 4))
        L.result(f"{surf}_governance_share_rederived", round(sum(gs2) / (sum(gs2) + sum(ts2)), 4))
        L.result(f"{surf}_missed_seconds_total", round(sum(miss_secs.values()), 1), "s")
        for k, v in sorted(miss_secs.items()):
            print(f"  {surf}: {k} ran {v:.0f} s over the window, counted as gate by prod GOV")
    # job names seen at any surface that no workflow file defines as a job id
    defined = set()
    for f in glob.glob(".github/workflows/*.yml"):
        defined |= jobs(f)
    L.result("check_run_names_seen", len(names))
    L.footer(snap["api_failures"])


if __name__ == "__main__":
    main()
