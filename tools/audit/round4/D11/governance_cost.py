#!/usr/bin/env python3
"""D11 / round 4 -- what the governance loop costs per merge, and how many rounds it takes.

METRIC, over the same window as merge_census.py (2026-09-09T09:37:08Z ..
2026-09-12T10:44:09Z, every merge, n=164):
  governance_seconds_per_merge  sum of (completed_at - started_at) over the check
                                runs whose names are governance jobs
                                (policy-docs, env-matrix, wave-script,
                                pr-contract, record, record-status, briefs) at
                                the merged head. Median and mean.
  gate_seconds_per_merge        the same sum over every other non-skipped check
                                run at that head -- the code gate.
  governance_share              governance seconds / all seconds.
  body_rounds                   count of `pr-contract` runs at the merged head.
                                `pull_request: [edited]` re-runs it on every body
                                edit, so this is the number of rounds the body
                                contract took, per merge.

These are DURATIONS REPORTED BY GITHUB, not wall clock on this box, so they are
contention-immune: no `load1` or `thread_factor` applies and none is quoted.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/governance_cost.py

EXPECTED at baseline 7dd68dd (tolerance: exact, the window is closed):
  merges=164 governance_seconds_median=75 gate_seconds_median=758
  governance_share=0.058 body_rounds_mean=1.63 body_rounds_max=8 api_failures=0
MACHINE: any; reads the same cache the other D11 harnesses fill.

PERTURBATION. Move `pr-contract` out of the governance set in GOV below and
`governance_share` must fall; that is the control that the split is reading
names rather than reporting a constant.
"""

import datetime
import os
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

GOV = {"policy-docs", "env-matrix", "wave-script", "pr-contract", "record",
       "record-status", "briefs"}
W0 = os.environ.get("D11_WINDOW_START", "2026-09-09T09:37:08Z")
W1 = os.environ.get("D11_WINDOW_END", L.BASELINE_UTC)


def dur(c):
    if not c.get("started_at") or not c.get("completed_at"):
        return 0.0
    a = datetime.datetime.fromisoformat(c["started_at"].replace("Z", "+00:00"))
    b = datetime.datetime.fromisoformat(c["completed_at"].replace("Z", "+00:00"))
    return max(0.0, (b - a).total_seconds())


def main():
    prs = L.merged_prs()
    win = sorted(n for n, p in prs.items() if W0 <= p["mergedAt"] <= W1)
    g, t, rounds = [], [], []
    for n in win:
        rs = L.check_runs(prs[n]["headRefOid"])
        if rs is None:
            continue
        g.append(sum(dur(c) for c in rs if c["name"] in GOV))
        t.append(sum(dur(c) for c in rs
                     if c["name"] not in GOV and c["conclusion"] != "skipped"))
        rounds.append(len([c for c in rs if c["name"] == "pr-contract"]))
    print(f"window {W0} .. {W1}  merges measured: {len(g)}")
    print(f"body rounds distribution: {dict(sorted(Counter(rounds).items()))}")
    L.result("merges", len(g))
    L.result("governance_seconds_median", round(statistics.median(g)), "s/merge")
    L.result("governance_seconds_mean", round(statistics.mean(g)), "s/merge")
    L.result("gate_seconds_median", round(statistics.median(t)), "s/merge")
    L.result("gate_seconds_mean", round(statistics.mean(t)), "s/merge")
    L.result("governance_share", round(sum(g) / (sum(g) + sum(t)), 3))
    L.result("body_rounds_mean", round(statistics.mean(rounds), 2))
    L.result("body_rounds_median", int(statistics.median(rounds)))
    L.result("body_rounds_max", max(rounds))
    L.footer()


if __name__ == "__main__":
    main()
