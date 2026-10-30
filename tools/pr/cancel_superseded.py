#!/usr/bin/env python3
"""Cancel the runs of one workflow that a pull request's live head has superseded.

    python3 -I tools/pr/cancel_superseded.py run --repo OWNER/REPO --workflow tests.yml \
        --pr N --head-sha SHA --branch BRANCH --run-id ID --sender LOGIN [--dry-run]
    python3 -I tools/pr/cancel_superseded.py sweep --repo OWNER/REPO [--dry-run]
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

`sweep` (P266) is the same rule applied from OUTSIDE any run, by the orchestrator's
pass: while the newer run is still queued for a runner it cancels nothing from
inside, so the superseded first push of a two-push open stayed active. One
open-PR listing and one runs listing per ACTIVE status (every status in `ACTIVE`,
pending and requested included), each paged `PAGE` at a time up to `MAX_PAGES`
pages, with a `CANCEL-SWEEP: truncated` line when the last page is still full.
API cost per sweep: 1 PR listing + 5 run listings (one page each below 100 items;
at most MAX_PAGES pages per listing) + one commit read per open PR with something
to cancel + one POST per cancel. Per open same-repo PR
branch it cancels what `candidates()` selects against the live head (no run at
the live head yet: every active run at another head). It never cancels a run at
the live head, a run on main, or an event outside `EVENTS` (push, workflow_run,
schedule, pull_request_target), nor on a branch whose live head was authored by
`github-actions[bot]` (the autofix rule). A run on a branch with no open PR is
reported as a ghost, never cancelled. Prints one line per action and
`CANCEL-SWEEP: cancelled n, kept m (live head), skipped k (bot head / not a PR),
ghosts g`. A critical-path or hotfix superseded run stays cancellable.

`concurrency:` is unchanged and still models the bot rule (`tests/entities.py`).
The workflow job runs the BASE's copy of this program with `actions: write`.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys

BOT = "github-actions[bot]"
ACTIVE = ("queued", "in_progress", "waiting", "pending", "requested")
EVENTS = ("pull_request", "workflow_dispatch")
PAGE, MAX_PAGES = 100, 10


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


def sweep_plan(prs: list[dict], runs: list[dict], bot_heads: set[str], *, repo: str) -> dict:
    """Pure part of `sweep`: {"cancel": ids, "kept": n, "skipped": n, "ghosts": [ids]}.

    `prs` are open pull requests (number, head.sha, head.ref, head.repo); `bot_heads`
    the live-head shas whose commit was authored by github-actions[bot]."""
    live = {}
    for pr in prs:
        h = pr.get("head") or {}
        if pr.get("state", "open") == "open" and (h.get("repo") or {}).get("full_name") == repo and h.get("ref"):
            live[h["ref"]] = h.get("sha")
    cancel, kept, skipped, ghosts = [], 0, 0, []
    by_branch: dict[str, list[dict]] = {}
    for r in runs:
        if r.get("status") not in ACTIVE:
            continue
        b = r.get("head_branch")
        hr = (r.get("head_repository") or {}).get("full_name")
        if b == "main" or r.get("event") not in EVENTS or (hr and hr != repo):
            skipped += 1
            continue
        if b not in live:
            ghosts.append(int(r["id"]))
            continue
        by_branch.setdefault(b, []).append(r)
    for b, rs in sorted(by_branch.items()):
        sha = live[b]
        kept += sum(1 for r in rs if r.get("head_sha") == sha)
        # A run at the live head bounds the cancel by id (an older head's run only);
        # with none yet, every active run at another head is superseded.
        bound = max([int(r["id"]) for r in rs if r.get("head_sha") == sha] or [sys.maxsize])
        ids = candidates(rs, live_sha=sha, branch=b, run_id=bound)
        if sha in bot_heads:
            skipped += len(ids)
            continue
        cancel += ids
    return {"cancel": sorted(cancel), "kept": kept, "skipped": skipped, "ghosts": sorted(ghosts)}


def listing(api, path: str, query: dict, key: str | None = None) -> "tuple[list | None, bool]":
    """(items, truncated): every page up to MAX_PAGES; (None, False) when a page is unreadable."""
    out: list = []
    for pg in range(1, MAX_PAGES + 1):
        args = [path] + [x for k, v in {**query, "per_page": PAGE, "page": pg}.items()
                         for x in ("-f", f"{k}={v}")]
        got = api(args)
        rs = got.get(key) if key and isinstance(got, dict) else got
        if not isinstance(rs, list):
            return None, False
        out += rs
        if len(rs) < PAGE:
            return out, False
    return out, True


def sweep(a: argparse.Namespace, api=gh) -> int:
    prs, cut = listing(api, f"repos/{a.repo}/pulls", {"state": "open"})
    truncated = ["pulls"] * cut
    runs: list[dict] = []
    for st in ACTIVE:
        rs, cut = listing(api, f"repos/{a.repo}/actions/runs", {"status": st}, "workflow_runs")
        if rs is None:
            prs = None
            break
        truncated += [f"runs status={st}"] * cut
        runs += rs
    if not isinstance(prs, list):
        print("CANCEL-SWEEP: unreadable answer; cancelling nothing")
        return 0
    for t in truncated:
        print(f"CANCEL-SWEEP: truncated: {t} still full after {MAX_PAGES} pages; counts are a lower bound")
    bot_heads: set[str] = set()
    first = sweep_plan(prs, runs, set(), repo=a.repo)
    if first["cancel"]:
        # the live-head author is read only for the PRs that have something to cancel
        by_id = {int(r["id"]): r for r in runs}
        for pr in prs:
            h = pr.get("head") or {}
            if any((by_id[i].get("head_branch") == h.get("ref")) for i in first["cancel"]):
                c = api([f"repos/{a.repo}/commits/{h.get('sha')}"])
                if not isinstance(c, dict):
                    print("CANCEL-SWEEP: unreadable commit; cancelling nothing")
                    return 0
                if ((c.get("author") or {}).get("login") == BOT
                        or ((c.get("commit") or {}).get("author") or {}).get("name") == BOT):
                    bot_heads.add(h.get("sha"))
    res = sweep_plan(prs, runs, bot_heads, repo=a.repo)
    for rid in res["cancel"]:
        if a.dry_run:
            print(f"cancel_superseded: would cancel {rid}")
            continue
        ok = api([f"repos/{a.repo}/actions/runs/{rid}/cancel"], "POST")
        print(f"cancel_superseded: cancelled {rid}" if ok is not None
              else f"cancel_superseded: could not cancel {rid}")
    for rid in res["ghosts"]:
        print(f"cancel_superseded: ghost {rid} (no open pull request on its branch)")
    print(f"CANCEL-SWEEP: cancelled {len(res['cancel'])}, kept {res['kept']} (live head), "
          f"skipped {res['skipped']} (bot head / not a PR), ghosts {len(res['ghosts'])}")
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
    check("a caller on a branch named main cancels nothing, though main has older runs",
          ids(branch="main", runs=[_r(OLD, OLD_SHA, branch="main"),
                                   _r(OLD_DISPATCH, OLD_SHA, "workflow_dispatch", branch="main")]), [])
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
    # sweep: the #2927 shape (two superseded first-push runs, the live head's run queued).
    S_OLD, S_LIVE = "e" * 40, "f" * 40
    sb = "fix/two-push"
    sprs = [{"number": 7, "state": "open", "head": {"sha": S_LIVE, "ref": sb, "repo": {"full_name": REPO}}}]
    sruns = [_r(101, S_OLD, status="in_progress", branch=sb), _r(102, S_OLD, "workflow_dispatch", "queued", sb),
             _r(103, S_LIVE, status="queued", branch=sb)]

    def sw(prs=sprs, runs=sruns, bots=()):
        return sweep_plan(prs, runs, set(bots), repo=REPO)
    check("sweep: the #2927 shape cancels both old runs and keeps the queued live one",
          (sw()["cancel"], sw()["kept"]), ([101, 102], 1))
    check("sweep: with no run yet at the live head every active run at another head is cancelled",
          sw(runs=sruns[:2])["cancel"], [101, 102])
    check("sweep: a bot-authored live head cancels nothing", sw(bots=[S_LIVE])["cancel"], [])
    push_main = _r(90, S_OLD, "push", branch="main")
    push_pr = _r(91, S_OLD, "push", branch=sb)
    check("sweep: a push run on main and a push run on a PR branch are never cancelled",
          sw(runs=sruns + [push_main, push_pr])["cancel"], [101, 102])
    ghost = _r(95, S_OLD, branch="fix/no-pr")
    res = sw(runs=sruns + [ghost])
    check("sweep: a run on a branch with no open PR is a ghost, never cancelled",
          (res["cancel"], res["ghosts"]), ([101, 102], [95]))
    check("sweep null: only live-head runs cancels nothing", sw(runs=[sruns[2], _r(104, S_LIVE, branch=sb)])["cancel"], [])
    check("sweep: a fork PR head is not swept", sw(prs=[{**sprs[0], "head": {**sprs[0]["head"], "repo": {"full_name": "x/fork"}}}])["cancel"], [])
    # mutant: dropping the event filter makes the push fixtures cancellable, so the arm above would fail.
    global EVENTS
    saved, EVENTS = EVENTS, EVENTS + ("push",)
    try:
        mutant = sw(runs=sruns + [push_pr])["cancel"]
    finally:
        EVENTS = saved
    check("sweep mutant: without the event filter the push run IS cancelled (the arm detects it)",
          91 in mutant, True)
    # sweep, pinned arm by arm (each names the mutant it kills).
    check("sweep: a run at an older head with a HIGHER id than the live head's run is never cancelled",
          sw(runs=sruns + [_r(110, S_OLD, branch=sb)])["cancel"], [101, 102])
    done = _r(96, S_OLD, status="completed", branch=sb)
    res = sw(runs=sruns + [done, _r(97, S_LIVE, status="completed", branch=sb),
                           _r(98, S_OLD, status="completed", branch="fix/no-pr"),
                           _r(99, S_OLD, status="completed", branch="main")])
    check("sweep: a finished run is neither kept, a ghost, skipped nor cancelled",
          (res["cancel"], res["kept"], res["ghosts"], res["skipped"]), ([101, 102], 1, [], 0))
    check("sweep: a pending or requested run at a superseded head is cancelled",
          sw(runs=[_r(81, S_OLD, status="pending", branch=sb), _r(82, S_OLD, status="requested", branch=sb),
                   sruns[2]])["cancel"], [81, 82])
    forkrun = {**_r(83, S_OLD, branch=sb), "head_repository": {"full_name": "x/fork"}}
    check("sweep: a run from a fork head repository on a PR branch's name is never cancelled",
          sw(runs=sruns + [forkrun])["cancel"], [101, 102])
    res = sw(runs=sruns + [push_main, push_pr, _r(92, S_OLD, "schedule", branch="main")])
    check("sweep: main and non-PR-event runs count as skipped, not as ghosts",
          (res["skipped"], res["ghosts"]), (3, []))
    # only the `b == "main"` disjunct can skip these: both events are in EVENTS and the repo matches.
    res = sw(runs=sruns + [_r(93, S_OLD, "workflow_dispatch", "queued", "main"),
                           _r(94, S_OLD, "pull_request", "queued", "main")])
    check("sweep: a PR-event run on main is skipped by the branch test alone, not a ghost, never cancelled",
          (res["skipped"], res["ghosts"], res["cancel"]), (2, [], [101, 102]))
    spost: list[str] = []
    author = {"login": "hpo-author[bot]", "name": "x"}

    def sstub(args, method="GET", prs=None, fail=(), runs=None):
        q = {args[i].split("=")[0]: args[i].split("=")[1] for i in range(2, len(args), 2) if "=" in args[i]}
        if args[0].endswith("/pulls"):
            return None if "pulls" in fail else (sprs if prs is None else prs)
        if args[0].endswith("/actions/runs") and method == "GET":
            if "runs" in fail and q["status"] == "waiting":
                return None
            return {"workflow_runs": [r for r in (sruns if runs is None else runs)
                                      if r["status"] == q["status"] and q["page"] == "1"]}
        if "/commits/" in args[0]:
            return None if "commit" in fail else {"author": {"login": author["login"]},
                                                   "commit": {"author": {"name": author["name"]}}}
        spost.append(args[0])
        return {}

    def quiet(a, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = sweep(a, lambda x, m="GET": sstub(x, m, **kw))
        return rc, sorted(spost), buf.getvalue()
    sns = argparse.Namespace(repo=REPO, dry_run=False)
    want = sorted(f"repos/{REPO}/actions/runs/{i}/cancel" for i in (101, 102))
    rc, got, out = quiet(sns)
    check("sweep end to end: POSTs exactly the two old runs", (rc, got), (0, want))
    spost.clear()
    sns.dry_run = True
    quiet(sns)
    check("sweep --dry-run posts nothing", spost, [])
    sns.dry_run = False
    check("sweep: an unreadable answer cancels nothing and exits 0",
          (sweep(sns, lambda a, m="GET": None), spost), (0, []))
    for what in ("pulls", "runs", "commit"):
        spost.clear()
        rc, got, out = quiet(sns, fail=(what,))
        check(f"sweep: an unreadable {what} answer cancels nothing and says unreadable, not a zero count",
              (rc, got, "unreadable" in out, "cancelled 0" in out), (0, [], True, False))
    for who in ({"login": BOT, "name": "x"}, {"login": "u", "name": BOT}):
        author.update(who)
        spost.clear()
        check(f"sweep end to end: a live head authored by the bot ({who}) cancels nothing",
              quiet(sns)[1], [])
    author.update({"login": "hpo-author[bot]", "name": "x"})
    spost.clear()
    quiet(sns, runs=[_r(81, S_OLD, status="pending", branch=sb), _r(82, S_OLD, status="requested", branch=sb),
                     sruns[2]])
    check("sweep end to end: every ACTIVE status is listed, so pending and requested runs are POSTed",
          sorted(spost), sorted(f"repos/{REPO}/actions/runs/{i}/cancel" for i in (81, 82)))
    # pagination: a full page 1 must be followed by page 2; a still-full last page is reported.
    seen: list[str] = []
    full = [_r(300 + i, S_LIVE, branch=sb) for i in range(PAGE)]

    def pstub(args, method="GET"):
        pg = [x for x in args if x.startswith("page=")][0]
        seen.append(pg)
        if args[0].endswith("/pulls"):
            return sprs
        return {"workflow_runs": full if pg == "page=1" or "always" in seen else []}
    with contextlib.redirect_stdout(io.StringIO()):
        sweep(sns, pstub)
    check("sweep: a full page is followed by the next page, and a short page stops", "page=2" in seen, True)
    seen.clear()
    seen.append("always")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sweep(sns, pstub)
    check("sweep: a listing still full after MAX_PAGES prints a truncated line",
          "truncated: runs status=queued" in buf.getvalue(), True)
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
    w = sub.add_parser("sweep")
    w.add_argument("--repo", required=True)
    w.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv[1:])
    return sweep(a) if a.cmd == "sweep" else run(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
