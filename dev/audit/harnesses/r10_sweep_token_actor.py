#!/usr/bin/env python3
"""R10-HOTFIX-SWEEP-TOKEN-ACTOR: which ci.yml completions any sweep judged, cross-tabbed by the run's actor.

    python3 -I dev/audit/harnesses/r10_sweep_token_actor.py census --since ISO --until ISO [--slack-min N]
    python3 -I dev/audit/harnesses/r10_sweep_token_actor.py --self-test

census   every ci.yml run created in [since, until) and completed, classed by its `actor`: `token`
         where it is github-actions[bot] (a GITHUB_TOKEN push's approved pull_request run, a
         github.token dispatch), `other` for an App or a person. A run is COVERED when a sweep
         named it: a gate-sweep.yml run created in [since, until + slack) whose `sweep` job log
         carries `RUN_ID: <id>` (gate-sweep.yml's step env, the workflow_run's id), or a
         `sweep-self` job of the run itself, in any attempt, that ran (not skipped; ci.yml's
         self-sweep, R10-HOTFIX-SWEEP-TOKEN-ACTOR). Only a run with a pull request is counted:
         the sweep SKIPs any other at once, so neither side names it usefully. Prints one
         `UNCOVERED` line per uncovered run (id, actor, event, PR, created), then
         `RESULT census other=<covered>/<n> token=<covered>/<n> gate_sweep_runs=<k> unread_logs=<u>`.
         Before the fix token reads 0/n; after it, every token run whose head was live reads covered.
         `unread_logs` > 0 (a log GitHub no longer serves) makes the other/token counts lower bounds.
--self-test  the coverage rule over fixtures, each arm with its null: prints `RESULT self-test checks=<n> failed=<f>`.

Live reads go through `gh api` (the seat's token), retried three times.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta

REPO = "tvofi/heatpump_optimizer"
TOKEN_ACTOR = "github-actions[bot]"     # tools/ci/sweep.py SWEEP_ACTOR
SELF_JOB = "sweep-self"                 # tools/ci/sweep.py SELF_JOB
RUN_ID_RE = re.compile(r"RUN_ID: (\d+)")


def gh(path: str, raw: bool = False):
    for k in range(3):
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout if raw else json.loads(p.stdout)
        if "404" in p.stderr or "410" in p.stderr:
            return None
        time.sleep(2 ** k)
    return None


def runs(workflow: str, since: str, until: str) -> list:
    out, page = [], 1
    while True:
        body = gh(f"repos/{REPO}/actions/workflows/{workflow}/runs?created={since}..{until}&per_page=100&page={page}")
        got = (body or {}).get("workflow_runs") or []
        out += got
        if len(got) < 100:
            return out
        page += 1


def named_ids(log: str) -> set:
    return {int(m) for m in RUN_ID_RE.findall(log or "")}


def self_swept(jobs: list) -> bool:
    return any(j.get("name") == SELF_JOB and j.get("conclusion") not in (None, "skipped") for j in jobs)


def covered(run: dict, gs_named: set, jobs: list) -> bool:
    return run["id"] in gs_named or self_swept(jobs)


def census(since: str, until: str, slack_min: int) -> int:
    ci = [r for r in runs("ci.yml", since, until) if r.get("status") == "completed"
          and r.get("created_at", "") < until and r.get("pull_requests")]
    t_end = (datetime.strptime(until, "%Y-%m-%dT%H:%M:%SZ") + timedelta(minutes=slack_min)).strftime("%Y-%m-%dT%H:%M:%SZ")
    sweeps = runs("gate-sweep.yml", since, t_end)
    named, unread = set(), 0
    for s in sweeps:
        jobs = (gh(f"repos/{REPO}/actions/runs/{s['id']}/jobs?per_page=100") or {}).get("jobs") or []
        logs = [gh(f"repos/{REPO}/actions/jobs/{j['id']}/logs", raw=True) for j in jobs if j.get("name") == "sweep"]
        unread += sum(1 for x in logs if x is None)
        for x in logs:
            named |= named_ids(x)
    tally = {"other": [0, 0], "token": [0, 0]}
    for r in sorted(ci, key=lambda r: r["id"]):
        cls = "token" if (r.get("actor") or {}).get("login") == TOKEN_ACTOR else "other"
        jobs = (gh(f"repos/{REPO}/actions/runs/{r['id']}/jobs?filter=all&per_page=100") or {}).get("jobs") or []
        c = covered(r, named, jobs)
        tally[cls][0] += c
        tally[cls][1] += 1
        if not c:
            print(f"UNCOVERED run={r['id']} actor={(r.get('actor') or {}).get('login')} event={r.get('event')} "
                  f"pr={r['pull_requests'][0]['number']} created={r.get('created_at')} attempt={r.get('run_attempt')}")
    print(f"RESULT census other={tally['other'][0]}/{tally['other'][1]} token={tally['token'][0]}/{tally['token'][1]} "
          f"gate_sweep_runs={len(sweeps)} unread_logs={unread}")
    return 0


def self_test() -> int:
    checks = []
    log = "2026-11-09T22:30:01Z   RUN_ID: 42711494947\n2026-11-09T22:30:02Z SWEEP-DONE run=42711494947\n"
    r = {"id": 42711494947}
    checks.append(("a gate-sweep log's RUN_ID names the run", covered(r, named_ids(log), [])))
    checks.append(("null: a log naming another run does not", not covered(r, named_ids(log.replace("494947", "494948")), [])))
    checks.append(("a sweep-self job that ran covers its run", covered(r, set(), [{"name": SELF_JOB, "conclusion": "success"}])))
    checks.append(("null: a skipped sweep-self does not", not covered(r, set(), [{"name": SELF_JOB, "conclusion": "skipped"}])))
    checks.append(("null: another job that ran does not", not covered(r, set(), [{"name": "refresh", "conclusion": "success"}])))
    for name, good in checks:
        if not good:
            print(f"FAIL {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"RESULT self-test checks={len(checks)} failed={bad}")
    return 1 if bad else 0


def main(argv) -> int:
    if argv == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="r10_sweep_token_actor.py")
    ap.add_argument("mode", choices=["census"])
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--slack-min", type=int, default=120)
    a = ap.parse_args(argv)
    return census(a.since, a.until, a.slack_min)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
