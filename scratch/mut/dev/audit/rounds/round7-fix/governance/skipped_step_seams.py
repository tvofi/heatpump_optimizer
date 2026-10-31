#!/usr/bin/env python3
"""Enumerate the seam class D11-01 belongs to, from GitHub's own record.

METRIC (one line). Every (job, step) of a workflow file whose conclusion is
`skipped` in a run of the last N, TALLIED BY WHETHER an earlier step of the same
job concluded `failure` or `cancelled`, and anchored to that failing step by
name. The first tally is the class D11-01 belongs to -- a step skipped by the
step-failure rule rather than by a condition its author wrote -- and every seam
in it is printed with its run count so each can be dispositioned. The second is
the control: a step skipped with no earlier failure is a job's own `if:` guard,
and a rule that returned those too would be counting every skip in the file.

COMMAND.  GITHUB_TOKEN=$(gh auth token) python3 \
            tools/audit/round7-fix/governance/skipped_step_seams.py --runs 60 \
            [--workflow <file>.yml] [--tally <substring>]
          (needs `gh`, authenticated; every call is a GET. `--workflow` defaults
          to `governance.yml`.)  `--tally` prints the conclusion tally for the
          steps whose name contains the substring -- the control for a step the
          seam rule does NOT return.

BASELINE. A sample of 60 runs of `governance.yml` listed 2026-09-23 at
`origin/main` 6e2a0f2a printed the `record` job's two filer steps as seams, both
skipped by `Every merged pull request has a disposition`, beside the runner's
own `Post Run <action>` teardown steps -- and the two `always()` steps of the
same job (histogram, sunset) as NOT seams. Every count here moves with the
window (`--runs` is "the last N runs at the moment it is run": two samples taken
twenty minutes apart printed 8 and 5 seam pairs), so the counts are dated rather
than carried; the CLASS is what the dispositions are keyed on.
`delivery-status-publish`'s ledger step is not a seam: its tally is `success` in
every run of both samples and `skipped` in none. `policy-docs`'s fragment check
is a seam in one sample and not the next (its predecessor is `Lint the policy
corpus`), and it is not this defect: that job's conclusion already carries the
failure. The same rule over 25 runs each of `tests.yml`, `hassfest.yml`,
`validate.yml` and `codeql.yml` returns the runner's teardown steps and nothing
else, with `tests.yml`'s own `if:` guards in the control arm, so the two arms
separate there.

WHY IT EXISTS. `fixer.md` step 8: a fix demonstrated with an instance owes a
rule that enumerates the class's seams, run, with every returned seam
dispositioned. This is that rule -- derived from the runs' own job and step
records, not from a list of step names, so an unguarded step lands in the seam
list the first time a run trips it.
"""
import argparse
import collections
import json
import subprocess
import sys
import time

REPO = "tvofi/heatpump_optimizer"
WF = "governance.yml"
FAILED = {"failure", "cancelled", "timed_out", "startup_failure"}
api_failures = []


def gh(args):
    for attempt in range(4):
        p = subprocess.run(["gh", "api"] + args, capture_output=True, text=True)
        if p.returncode == 0:
            return json.loads(p.stdout)
        low = (p.stderr or "").lower()
        if "rate limit" in low or "secondary" in low or "timeout" in low:
            time.sleep(4 + 4 * attempt)
            continue
        api_failures.append("rc=%s %s" % (p.returncode, (p.stderr or "").strip()[:80]))
        return None
    api_failures.append("rate-limited: %s" % args[0][:80])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=100)
    ap.add_argument("--workflow", default=WF)
    ap.add_argument("--tally", default=None,
                    help="print every step whose name contains this substring "
                         "with its conclusion tally (the control for a step the "
                         "seam rule did NOT return)")
    a = ap.parse_args()
    runs = gh(["repos/%s/actions/workflows/%s/runs?per_page=%d"
               % (REPO, a.workflow, a.runs)])
    if not runs:
        print("RESULT api_failures=%d count" % len(api_failures))
        return 2
    raw = runs.get("workflow_runs", [])
    print("HARNESS skipped_step_seams -- %s, %d run(s) listed, events=%s"
          % (a.workflow, len(raw), sorted({r["event"] for r in raw})))
    seam = collections.Counter()
    control = collections.Counter()
    jobs_seen = collections.Counter()
    tally = collections.Counter()
    why = {}
    runs_with_steps = 0
    for r in raw:
        jobs = gh(["repos/%s/actions/runs/%d/jobs?per_page=100" % (REPO, r["id"])])
        if not jobs:
            continue
        for j in jobs.get("jobs", []):
            steps = j.get("steps") or []
            if steps:
                runs_with_steps += 1
            jobs_seen[j["name"]] += 1
            for k, s in enumerate(steps):
                if a.tally and a.tally in (s.get("name") or ""):
                    tally[(j["name"], s.get("name"), s.get("conclusion"))] += 1
                if s.get("conclusion") != "skipped":
                    continue
                failed = [p.get("name") for p in steps[:k]
                          if p.get("conclusion") in FAILED]
                if failed:
                    seam[(j["name"], s.get("name"))] += 1
                    why[(j["name"], s.get("name"))] = failed[0]
                else:
                    control[(j["name"], s.get("name"))] += 1
        time.sleep(0.2)
    print("RESULT runs_listed=%d count" % len(raw))
    print("RESULT jobs_with_steps=%d count" % runs_with_steps)
    print("RESULT api_failures=%d count" % len(api_failures))
    print("# SEAMS: steps skipped while an earlier step of the same job failed")
    for (job, step), n in seam.most_common():
        print("SEAM %4d  %-28s %-58s <- %s"
              % (n, job, step, why.get((job, step), "?")))
    print("RESULT seam_pairs=%d count" % len(seam))
    print("# CONTROL: steps skipped with no earlier failing step (their own `if:`)")
    for (job, step), n in control.most_common():
        print("GUARD %4d  %-28s %s" % (n, job, step))
    print("RESULT guarded_pairs=%d count" % len(control))
    for f in api_failures[:5]:
        print("  api-failure: %s" % f)
    if a.tally:
        print("# TALLY for steps whose name contains %r" % a.tally)
        for (job, step, concl), n in sorted(tally.items()):
            print("TALLY %4d  %-28s %-22s %s" % (n, job, concl, step))
        print("RESULT tallied_pairs=%d count" % len(tally))
    return 0


if __name__ == "__main__":
    sys.exit(main())
