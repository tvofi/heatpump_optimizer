#!/usr/bin/env python3
"""Cancel the runs of one workflow that a pull request's live head has superseded.

    python3 -I tools/pr/cancel_superseded.py run --repo OWNER/REPO --workflow tests.yml \
        --pr N --head-sha SHA --branch BRANCH --run-id ID --sender LOGIN [--dry-run]
    python3 tools/pr/cancel_superseded.py --self-test

R10-CI-CONCURRENCY. A workflow's `concurrency:` group cancels a pull request's
older run only when BOTH runs are in the pull request's group. A run sent by
`github-actions[bot]` (an autofix push approved by hpo-runs, or a
`workflow_dispatch`) gets a group of its own by run id, on purpose: a bot-sent
NEWER run must never cancel the older run that is still running the other
autofix jobs (`tests.yml`, the `concurrency:` comment; a98d5a05a). The same
exemption also puts a bot-sent OLDER run out of reach of a newer App push, and
that run then finishes for a head nobody reads (tests: 986 + 203 billed tail
minutes in the 2026-10-14..18 window, `dev/audit/harnesses/superseded_runs.py`
classes B and D). This closes the second half only, by API, from the live run.

IT CANCELS NOTHING UNLESS ALL OF THESE HOLD, and prints which one failed:
  - the calling run is a `pull_request` run whose sender is not
    `github-actions[bot]` (a bot-sent newer run cancels nothing);
  - the branch is not `main`;
  - the pull request is open, from this repository, and its head right now is
    the calling run's head SHA (the LIVE-HEAD check: a run on a head that has
    already been superseded has no standing to cancel anything);
  - a candidate run is on the same branch, of event `pull_request` or
    `workflow_dispatch`, queued / in progress / waiting, at a DIFFERENT head
    SHA (a same-SHA twin is never cancelled: R9-CI-2a), and was created before
    the calling run (its id is lower: a newer head's run is never cancelled).
An unreadable answer from GitHub cancels nothing. Always exits 0 when it ran
(fail-soft: the cancel is an optimisation, never a gate).

`concurrency:` is unchanged and still models the bot rule (`tests/entities.py`).
The workflow job runs the BASE's copy of this program with `actions: write`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

BOT = "github-actions[bot]"
ACTIVE = ("queued", "in_progress", "waiting", "pending", "requested")
EVENTS = ("pull_request", "workflow_dispatch")


def candidates(runs: list[dict], *, live_sha: str, branch: str, run_id: int) -> list[int]:
    """Ids of the runs the live head supersedes; the pure part of the program."""
    out = []
    for r in runs:
        if (r.get("head_branch") == branch
                and r.get("event") in EVENTS
                and r.get("status") in ACTIVE
                and r.get("head_sha") != live_sha
                and int(r["id"]) < run_id):
            out.append(int(r["id"]))
    return sorted(out)


def plan(*, event: str, sender: str, branch: str, pr: dict | None, head_sha: str,
         repo: str, runs: list[dict], run_id: int) -> tuple[list[int], str]:
    """(ids to cancel, the reason when none)."""
    if event != "pull_request":
        return [], f"event {event!r} is not pull_request"
    if sender == BOT:
        return [], "sender is github-actions[bot]: a bot-sent run cancels nothing"
    if branch == "main":
        return [], "branch is main"
    if not pr or pr.get("state") != "open":
        return [], "pull request unreadable or not open"
    if ((pr.get("head") or {}).get("repo") or {}).get("full_name") != repo:
        return [], "head is not in this repository"
    if (pr.get("head") or {}).get("sha") != head_sha:
        return [], "this run's head is not the pull request's live head"
    return candidates(runs, live_sha=head_sha, branch=branch, run_id=run_id), ""


def gh(args: list[str], method: str = "GET") -> "object | None":
    p = subprocess.run(["gh", "api", "-X", method, *args], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"cancel_superseded: gh api {args[0]} rc={p.returncode}: {p.stderr.strip()[-160:]}")
        return None
    try:
        return json.loads(p.stdout) if p.stdout.strip() else {}
    except ValueError:
        return None


def run(a: argparse.Namespace, api=gh) -> int:
    pr = api([f"repos/{a.repo}/pulls/{a.pr}"])
    listing = api([f"repos/{a.repo}/actions/workflows/{a.workflow}/runs",
                   "-f", f"branch={a.branch}", "-f", "per_page=100"])
    runs = (listing or {}).get("workflow_runs") if isinstance(listing, dict) else None
    if not isinstance(pr, dict) or runs is None:
        print("cancel_superseded: unreadable answer; cancelling nothing")
        return 0
    ids, why = plan(event=a.event, sender=a.sender, branch=a.branch, pr=pr,
                    head_sha=a.head_sha, repo=a.repo, runs=runs, run_id=a.run_id)
    if why:
        print(f"cancel_superseded: nothing to do: {why}")
        return 0
    for rid in ids:
        if a.dry_run:
            print(f"cancel_superseded: would cancel {rid}")
            continue
        ok = api([f"repos/{a.repo}/actions/runs/{rid}/cancel"], "POST")
        print(f"cancel_superseded: cancelled {rid}" if ok is not None
              else f"cancel_superseded: could not cancel {rid}")
    print(f"cancel_superseded: {len(ids)} superseded run(s) of {a.workflow} on {a.branch}")
    return 0


# --- self-test ---------------------------------------------------------------
# The recorded pair: run 39090494028 (Tests, pull_request, sender
# github-actions[bot], attempt 2 by hpo-runs[bot], head 3b76e0b0) and the
# dispatched run 39090491271 at the same head were still running when run
# 39091600343 (App push, same branch, head 8d76a9ed) started at 02:52:07Z.
OLD, OLD_DISPATCH, NEW = 39090494028, 39090491271, 39091600343
OLD_SHA, NEW_SHA = "3b76e0b08d468a4e0fdbf2f62665daf296c790eb", "8d76a9edf1ec3356ba7d8e55601e8e8c17553977"
BRANCH, REPO = "fix/r10-leaf-imports", "tvofi/heatpump_optimizer"


def _r(i, sha, event="pull_request", status="in_progress", branch=BRANCH):
    return {"id": i, "head_sha": sha, "event": event, "status": status, "head_branch": branch}


def _pr(sha=NEW_SHA, state="open", repo=REPO):
    return {"state": state, "head": {"sha": sha, "repo": {"full_name": repo}}}


def self_test() -> int:
    runs = [_r(OLD, OLD_SHA), _r(OLD_DISPATCH, OLD_SHA, "workflow_dispatch"), _r(NEW, NEW_SHA)]
    base = dict(event="pull_request", sender="hpo-author[bot]", branch=BRANCH, pr=_pr(),
                head_sha=NEW_SHA, repo=REPO, runs=runs, run_id=NEW)
    fails = n = 0

    def check(label: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}, want {want!r}"))

    def ids(**kw) -> list[int]:
        return plan(**{**base, **kw})[0]
    # The failing check first: the recorded pair selects the old runs.
    check("recorded pair 39090494028/39091600343: the old bot-sent run and its dispatch are selected",
          ids(), sorted([OLD, OLD_DISPATCH]))
    check("the calling run itself is never selected", NEW in ids(), False)
    # Null controls.
    check("a same-SHA twin of the live head is never cancelled",
          ids(runs=runs + [_r(NEW - 5, NEW_SHA)]), sorted([OLD, OLD_DISPATCH]))
    check("a run on the live head only is never cancelled (nothing older at another SHA)",
          ids(runs=[_r(NEW - 5, NEW_SHA), _r(NEW, NEW_SHA)]), [])
    check("a bot-sent newer run cancels nothing", ids(sender=BOT), [])
    check("a dispatch is not a caller", ids(event="workflow_dispatch"), [])
    check("a run on main is never cancelled",
          ids(runs=runs + [_r(NEW - 9, OLD_SHA, "push", branch="main")]), sorted([OLD, OLD_DISPATCH]))
    check("a run on another branch is never cancelled",
          ids(runs=[_r(OLD, OLD_SHA, branch="fix/other")]), [])
    check("a merge_group or push run on this branch is never cancelled",
          ids(runs=[_r(OLD, OLD_SHA, "merge_group"), _r(OLD_DISPATCH, OLD_SHA, "push")]), [])
    check("a finished run is not cancelled",
          ids(runs=[_r(OLD, OLD_SHA, status="completed")]), [])
    check("a newer head's run (higher id) is never cancelled",
          ids(runs=[_r(NEW + 7, "c" * 40)]), [])
    check("a run on main as the caller's branch cancels nothing", ids(branch="main"), [])
    # The live-head check: a run whose head is no longer the pull request's.
    check("stale head: a run that is not on the live head cancels nothing",
          ids(pr=_pr(sha="d" * 40)), [])
    check("a closed pull request cancels nothing", ids(pr=_pr(state="closed")), [])
    check("a fork head cancels nothing", ids(pr=_pr(repo="someone/fork")), [])
    check("an unreadable pull request cancels nothing", ids(pr=None), [])
    # The program end to end over a stub gh: what it POSTs.
    posts: list[str] = []

    def stub(args, method="GET"):
        if args[0].endswith(f"pulls/7"):
            return _pr()
        if "/runs" in args[0] and method == "GET":
            return {"workflow_runs": runs}
        posts.append(args[0])
        return {}
    ns = argparse.Namespace(repo=REPO, workflow="tests.yml", pr=7, head_sha=NEW_SHA, branch=BRANCH,
                            run_id=NEW, sender="hpo-author[bot]", event="pull_request", dry_run=False)
    rc = run(ns, stub)
    check("end to end: cancels exactly the two old runs by POST", (rc, sorted(posts)),
          (0, sorted(f"repos/{REPO}/actions/runs/{i}/cancel" for i in (OLD, OLD_DISPATCH))))
    posts.clear()
    ns.dry_run = True
    run(ns, stub)
    check("--dry-run posts nothing", posts, [])
    ns.dry_run = False
    check("an unreadable listing cancels nothing and exits 0",
          (run(ns, lambda a, m="GET": None), posts), (0, []))
    print(f"cancel_superseded self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    for k in ("repo", "workflow", "head-sha", "branch", "sender"):
        r.add_argument(f"--{k}", required=True)
    r.add_argument("--pr", type=int, required=True)
    r.add_argument("--run-id", type=int, required=True)
    r.add_argument("--event", default="pull_request")
    r.add_argument("--dry-run", action="store_true")
    return run(ap.parse_args(argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
