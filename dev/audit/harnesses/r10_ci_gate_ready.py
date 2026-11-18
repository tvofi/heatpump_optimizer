#!/usr/bin/env python3
"""When ci.yml's `gate` became ready, under its `needs:` and under a proposed one.

    python3 dev/audit/harnesses/r10_ci_gate_ready.py --last 10 --event push \\
        --needs prelude,pr-contract [--null prelude]

R10-CI-LAYOUT-P2 carry 26 (owner request 2026-10-24: fewer edges into `gate`).
tools/audit/seat/ci_critpath.py reads every `<caller> / <job>` of a
reusable-workflow caller as unmapped, with no needs, so its counterfactual
over ci.yml measures nothing. This reads the API's jobs instead:

THE RULE. A job's caller key is its API name up to the first ` / ` (a caller
that ran is `tests / fast (3.14)`; one that was skipped is `pr-contract`).
A key's end is the latest `completed_at` of its jobs, skipped ones included:
GitHub records a skipped job when it decided the skip. For a needs list L,
ready(L) = the latest end over the keys in L. Per run it prints
ready(gate's needs at the run's head) - ready(--needs): 0 on every run means
the proposed `gate` would have started at the same instant. Attempt 1 only:
a re-run of `gate` (gate.py --refresh) re-records every skipped caller at the
re-run's time, so a later attempt's ends say when it re-ran, not when the
graph released `gate`. `--null` is the
control: a list that omits the units must read > 0 on runs whose units
outlast the prelude, or the comparison is not reading the graph.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime

REPO = "tvofi/heatpump_optimizer"


def gh(path):
    return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def gate_needs(sha):
    import yaml
    text = subprocess.run(["gh", "api", f"repos/{REPO}/contents/.github/workflows/ci.yml?ref={sha}",
                           "-H", "Accept: application/vnd.github.raw"], capture_output=True, text=True, check=True).stdout
    return yaml.safe_load(text)["jobs"]["gate"]["needs"]


def ends(jobs):
    out = {}
    for j in jobs:
        if j.get("completed_at"):
            k = j["name"].split(" / ", 1)[0]
            out[k] = max(out.get(k, 0), ts(j["completed_at"]))
    return out


def ready(end, keys):
    missing = [k for k in keys if k not in end]
    return (None, missing) if missing else (max(end[k] for k in keys), [])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--last", type=int, default=10)
    ap.add_argument("--event", required=True)
    ap.add_argument("--needs", required=True)
    ap.add_argument("--null")
    a = ap.parse_args(argv)
    proposed = a.needs.split(",")
    runs = gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?event={a.event}&status=completed&per_page={a.last * 3}")
    runs = [r for r in runs["workflow_runs"] if r["conclusion"] not in ("cancelled", "skipped")][:a.last]
    zero = nulls = 0
    for r in runs:
        jobs = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/1/jobs?per_page=100")["jobs"]
        end = ends(jobs)
        old, m1 = ready(end, gate_needs(r["head_sha"]))
        new, m2 = ready(end, proposed)
        if m1 or m2:
            print(f"run {r['id']}: UNREAD, no job for {m1 + m2}")
            continue
        d = old - new
        zero += d == 0
        line = f"run {r['id']} ({r['display_title'][:40]}): ready(gate needs) - ready({a.needs}) = {d:.0f} s"
        if a.null:
            nl, _ = ready(end, a.null.split(","))
            nulls += old - nl > 0
            line += f"; null ready - ready({a.null}) = {old - nl:.0f} s"
        print(line)
    print(f"RESULT runs={len(runs)} zero_delta={zero}" + (f" null_positive={nulls}" if a.null else ""))
    return 0 if runs and zero == len(runs) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
