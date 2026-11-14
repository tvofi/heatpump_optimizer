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

ZOMBIES (carry 5). A run that answers HTTP 409 to its cancel while listed active is
remembered in `$HPO_STATE_DIR/cancel-zombies.json` {id: first-seen}, printed once as
`cancel_superseded: zombie <id> (409, not retried)`, skipped without a POST or a commit
read on later passes, counted in the summary line's `zombies` and not a failure; an id
gone from the active listings drops out of the file. Any other failure is retried.

PRIORITY (`sweep --priority [--train-state DIR]`, owner 2026-11-11, carries 4 and 6): while a
critical-path, hotfix or outside PR (`ci_priority.tier`, mapping from the roster) has a
QUEUED run, queued runs of non-priority PRs are candidates -- never a run in progress, a
main run, a PR the train holds (queue or spool under DIR), the train's current PR, or any PR
holding a `Fix review: merge` comment. The setting's `priority_cancel` (false) decides
whether candidates are cancelled; off, the sweep HOLDS (cancels nothing, prints one
summary line). On, each cancel is recorded in `priority-held.json` and re-run (POST
.../rerun) once no priority run is queued; one line per cancel and per re-run naming the
PR, the run and the priority PR that caused it.

`concurrency:` is unchanged and still models the bot rule (`tests/entities.py`).
The workflow job runs the BASE's copy of this program with `actions: write`.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

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


CONFLICT = {"_http": 409}  # what `gh` answers for a cancel GitHub refuses with HTTP 409


def gh(args: list[str], method: str = "GET") -> "object | None":
    p = subprocess.run(["gh", "api", "-X", method, *args], capture_output=True, text=True)
    if p.returncode != 0:
        if method == "POST" and "HTTP 409" in p.stderr + p.stdout:
            return CONFLICT
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
        post_cancel(api, a.repo, rid, {}, time.time())
    print(f"cancel_superseded: {len(ids)} superseded run(s) of {a.workflow} on {a.branch}")
    return 0


SEAT = Path(__file__).resolve().parents[1] / "audit" / "seat"
ZOMBIES = "cancel-zombies.json"
HELD = "priority-held.json"
HELD_MAX_AGE_S = 24 * 3600


def zombie_file() -> "Path | None":
    d = os.environ.get("HPO_STATE_DIR")
    return Path(d) / ZOMBIES if d else None


def zombies_read(path: "Path | None") -> dict:
    """{run id: first-seen epoch} of the runs that answered 409 while listed active."""
    try:
        got = json.loads(path.read_text()) if path else {}
    except (OSError, ValueError):
        return {}
    return {int(k): v for k, v in got.items()} if isinstance(got, dict) else {}


def zombies_write(path: "Path | None", z: dict) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({str(k): v for k, v in sorted(z.items())}))
        os.replace(tmp, path)
    except OSError as e:
        print(f"CANCEL-SWEEP: zombie file unwritable: {e}")


def post_cancel(api, repo: str, rid: int, zombies: dict, now: float) -> str:
    """POST one cancel; "ok", "zombie" (409: recorded in `zombies`, printed once) or "failed"."""
    got = api([f"repos/{repo}/actions/runs/{rid}/cancel"], "POST")
    if got is CONFLICT:
        zombies[rid] = now
        print(f"cancel_superseded: zombie {rid} (409, not retried)")
        return "zombie"
    if got is None:
        print(f"cancel_superseded: could not cancel {rid}")
        return "failed"
    print(f"cancel_superseded: cancelled {rid}")
    return "ok"


def priority_plan(prs: list[dict], runs: list[dict], tiers: dict, protected: set, setting: dict,
                  *, repo: str) -> dict:
    """Pure part of the priority rule (owner, tvofi 2026-11-11, "no critical path, outside or
    hotfix PR should wait in CI queue"; carry 6 amends it).

    `tiers` maps a pull request number to its ci_priority tier; `protected` is the numbers a
    queued run of which is never touched: a PR holding a posted merge verdict at its head, one in
    the merge train's queue or spool, and the train's current one. Returns
    {"priority": [(pr, run id)] queued priority runs, "victims": [(run id, pr, cause pr, cause run)]
     queued runs of non-priority PRs (cancellable only when the setting's priority_cancel is on),
    "main_queued": n, "queued": n}. A run of main, one already in progress and one of an event
    outside EVENTS are never victims."""
    by_branch = {}
    for pr in prs:
        h = pr.get("head") or {}
        if pr.get("state", "open") == "open" and (h.get("repo") or {}).get("full_name") == repo and h.get("ref"):
            by_branch[h["ref"]] = int(pr["number"])
    queued = [r for r in runs if r.get("status") == "queued"]
    prio, victims = [], []
    main_q = sum(1 for r in queued if r.get("head_branch") == "main")
    for r in sorted(queued, key=lambda r: int(r["id"])):
        pr = by_branch.get(r.get("head_branch"))
        if pr is not None and r.get("event") in EVENTS and tiers.get(pr) in setting["never_cancel"]:
            prio.append((pr, int(r["id"])))
    if prio:
        for r in sorted(queued, key=lambda r: int(r["id"])):
            pr = by_branch.get(r.get("head_branch"))
            hr = (r.get("head_repository") or {}).get("full_name")
            if (pr is None or r.get("event") not in EVENTS or (hr and hr != repo) or pr in protected
                    or tiers.get(pr, "instrument") in setting["never_cancel"]):
                continue
            victims.append((int(r["id"]), pr, prio[0][0], prio[0][1]))
    return {"priority": prio, "victims": victims, "main_queued": main_q, "queued": len(queued)}


def held_read(path: "Path | None") -> dict:
    """{run id: {pr, cause_pr, cause_run, at}} of the runs this sweep cancelled for a priority run."""
    try:
        got = json.loads(path.read_text()) if path else {}
    except (OSError, ValueError):
        return {}
    return {int(k): v for k, v in got.items() if isinstance(v, dict)} if isinstance(got, dict) else {}


def held_write(path: "Path | None", held: dict) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({str(k): v for k, v in sorted(held.items())}))
        os.replace(tmp, path)
    except OSError as e:
        print(f"CANCEL-SWEEP: held file unwritable: {e}")


def priority_step(api, *, repo: str, plan_: dict, held: dict, allow_cancel: bool, now: float,
                  dry_run: bool = False) -> dict:
    """Act on `priority_plan`'s answer, one line per cancel and per re-run.

    With a priority run queued and `allow_cancel`, each victim is cancelled and recorded in
    `held`. With none queued, each held run is re-run (POST .../rerun) and dropped on success;
    a record older than HELD_MAX_AGE_S is dropped unrun. Returns {"cancelled": n, "rerun": n}."""
    out = {"cancelled": 0, "rerun": 0}
    if plan_["priority"]:
        if not allow_cancel:
            return out
        for rid, pr, cpr, crun in plan_["victims"]:
            if rid in held:
                continue
            if dry_run:
                print(f"cancel_superseded: would cancel queued run {rid} of #{pr}: priority #{cpr} run {crun} is queued")
                continue
            got = api([f"repos/{repo}/actions/runs/{rid}/cancel"], "POST")
            if got is None or got is CONFLICT:
                print(f"cancel_superseded: could not cancel queued run {rid} of #{pr} for priority #{cpr}")
                continue
            held[rid] = {"pr": pr, "cause_pr": cpr, "cause_run": crun, "at": now}
            out["cancelled"] += 1
            print(f"cancel_superseded: cancelled queued run {rid} of #{pr}: priority #{cpr} run {crun} is queued")
        return out
    for rid, rec in sorted(held.items()):
        if now - float(rec.get("at") or 0) > HELD_MAX_AGE_S:
            del held[rid]
            continue
        if dry_run:
            print(f"cancel_superseded: would re-run run {rid} of #{rec.get('pr')}")
            continue
        got = api([f"repos/{repo}/actions/runs/{rid}/rerun"], "POST")
        if got is None or got is CONFLICT:
            print(f"cancel_superseded: could not re-run run {rid} of #{rec.get('pr')}; retried next pass")
            continue
        del held[rid]
        out["rerun"] += 1
        print(f"cancel_superseded: re-ran run {rid} of #{rec.get('pr')}: no priority run is queued "
              f"(it was cancelled for #{rec.get('cause_pr')} run {rec.get('cause_run')})")
    return out


def train_pinned(state_dir: "str | None") -> set:
    """Pull requests in the merge train's queue or spool under <state_dir>: `queue-add.jsonl`
    lines and any `queue*.json` list, each entry's `pr`. Unreadable files add nothing; the
    verdict-comment check in `priority_pass` is the guard that does not depend on them."""
    out: set = set()
    if not state_dir:
        return out
    for f in sorted(Path(state_dir).glob("queue*")):
        try:
            text = f.read_text()
            if f.suffix == ".jsonl":
                rows = []
                for x in text.splitlines():
                    try:
                        rows.append(json.loads(x))
                    except ValueError:
                        pass  # one torn line pins nothing and spares the rest
            else:
                rows = json.loads(text)
        except (OSError, ValueError):
            continue
        for e in rows if isinstance(rows, list) else []:
            if isinstance(e, dict) and str(e.get("pr", "")).isdigit():
                out.add(int(e["pr"]))
    return out


def has_merge_verdict(api, repo: str, pr: int) -> "bool | None":
    """Whether pull request <pr> holds a `Fix review: merge` comment at any head (conservative: an
    older head's verdict still protects); None when its comments cannot be read."""
    got = api(["--paginate", "--slurp", f"repos/{repo}/issues/{pr}/comments?per_page=100"])
    if not isinstance(got, list):
        return None
    return any(str(c.get("body") or "").startswith("Fix review: merge")
               for page in got for c in (page if isinstance(page, list) else []))


def priority_pass(a: argparse.Namespace, api, prs: list, runs: list, now: float) -> str:
    """The CI-priority rule of the sweep (carries 4 and 6). Returns the summary suffix."""
    sys.path.insert(0, str(SEAT))
    import ci_priority
    import roster_lib as rl
    try:
        setting = ci_priority.load_setting()
        root = SEAT.parents[1]
        roster = rl.show_roster(str(root), rl.default_roster_ref(rl.git_in(str(root)))[0])
        crit = {rl.norm_group(str(c)) for c in rl.critical_path(roster)}
    except Exception as e:  # noqa: BLE001 - an unreadable rule cancels nothing
        print(f"CANCEL-SWEEP: priority rule unreadable: {str(e)[:120]}; priority step skipped")
        return ", priority unreadable"
    tiers = {}
    for pr in prs:
        h = pr.get("head") or {}
        g = rl.group_for_branch(roster, h.get("ref") or "") or rl.group_for_pr(roster, pr.get("number"))
        tiers[int(pr["number"])] = ci_priority.tier(g, crit, roster, setting)
    return priority_act(a, api, prs, runs, tiers, setting, now)


def priority_act(a: argparse.Namespace, api, prs: list, runs: list, tiers: dict, setting: dict,
                 now: float) -> str:
    """`priority_pass` past the roster read: the train's pins, the live verdict lookup (carry 6:
    a PR holding a `Fix review: merge` comment is never cancelled), the cancels or re-runs."""
    protected = train_pinned(getattr(a, "train_state", None))
    plan_ = priority_plan(prs, runs, tiers, protected, setting, repo=a.repo)
    if plan_["victims"] and setting["priority_cancel"]:
        for pr in sorted({v[1] for v in plan_["victims"]}):
            if has_merge_verdict(api, a.repo, pr) is not False:
                protected.add(pr)  # a verdict, or comments that could not be read
        plan_ = priority_plan(prs, runs, tiers, protected, setting, repo=a.repo)
    hfile = (zombie_file().with_name(HELD) if zombie_file() else None)
    held = held_read(hfile)
    got = priority_step(api, repo=a.repo, plan_=plan_, held=held, allow_cancel=setting["priority_cancel"],
                        now=now, dry_run=a.dry_run)
    if not a.dry_run:
        held_write(hfile, held)
    if plan_["priority"]:
        print(f"CANCEL-SWEEP: priority run(s) queued: {len(plan_['priority'])} of {plan_['queued']} queued "
              f"({plan_['main_queued']} on main); " + ("cancelling queued non-priority runs"
              if setting["priority_cancel"] else "holding (priority_cancel is off), nothing cancelled"))
    return f", priority cancelled {got['cancelled']}, re-ran {got['rerun']}, held {len(held)}"


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
    zfile = zombie_file()
    zombies = zombies_read(zfile)
    active = {int(r["id"]) for r in runs}
    zombies = {k: v for k, v in zombies.items() if k in active}  # gone from the listings: dropped
    runs = [r for r in runs if int(r["id"]) not in zombies]  # no POST and no commit read for one
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
    done = 0
    for rid in res["cancel"]:
        if a.dry_run:
            print(f"cancel_superseded: would cancel {rid}")
            continue
        done += post_cancel(api, a.repo, rid, zombies, time.time()) == "ok"
    if not a.dry_run:
        zombies_write(zfile, zombies)
    prio = priority_pass(a, api, prs, runs, time.time()) if getattr(a, "priority", False) else ""
    for rid in res["ghosts"]:
        print(f"cancel_superseded: ghost {rid} (no open pull request on its branch)")
    print(f"CANCEL-SWEEP: cancelled {len(res['cancel']) if a.dry_run else done}, kept {res['kept']} (live head), "
          f"skipped {res['skipped']} (bot head / not a PR), ghosts {len(res['ghosts'])}, "
          f"zombies {len(zombies)}{prio}")
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
    # Carry 5: a run answering 409 while listed active is remembered; the next pass makes no POST for it.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        os.environ["HPO_STATE_DIR"] = td
        zposts: list[str] = []
        zmode = {"answer": CONFLICT}

        def zstub(args, method="GET"):
            if args[0].endswith("/pulls"):
                return sprs
            if args[0].endswith("/actions/runs") and method == "GET":
                q = {args[i].split("=")[0]: args[i].split("=")[1] for i in range(2, len(args), 2) if "=" in args[i]}
                return {"workflow_runs": [r for r in sruns if r["status"] == q["status"] and q["page"] == "1"]}
            if "/commits/" in args[0]:
                return {"author": {"login": "hpo-author[bot]"}, "commit": {"author": {"name": "x"}}}
            zposts.append(args[0])
            return zmode["answer"] if args[0].endswith("/101/cancel") else {}
        zbuf = io.StringIO()
        with contextlib.redirect_stdout(zbuf):
            sweep(sns, zstub)
        first = list(zposts)
        zposts.clear()
        with contextlib.redirect_stdout(zbuf := io.StringIO()):
            sweep(sns, zstub)
        check("zombie: the 409 run is POSTed on the first pass, never on the second",
              (any(x.endswith("/101/cancel") for x in first), any(x.endswith("/101/cancel") for x in zposts)), (True, False))
        check("zombie: the second pass counts it in the summary line and prints no failure",
              ("zombies 1" in zbuf.getvalue(), "could not cancel" in zbuf.getvalue(), "zombie 101" in zbuf.getvalue()),
              (True, False, False))
        zmode["answer"] = None  # null control: a non-409 failure (rc 1, HTTP 500) is retried
        zposts.clear()
        os.remove(zombie_file())
        with contextlib.redirect_stdout(io.StringIO()):
            sweep(sns, zstub)
            sweep(sns, zstub)
        check("zombie null: a non-409 failure is retried on the next pass (POSTed twice)",
              sum(x.endswith("/101/cancel") for x in zposts), 2)
        os.environ.pop("HPO_STATE_DIR")
        # a run gone from the active listings drops out of the file
        zombies_write(Path(td) / ZOMBIES, {101: 1.0, 777: 1.0})
        os.environ["HPO_STATE_DIR"] = td
        zmode["answer"] = {}
        with contextlib.redirect_stdout(io.StringIO()):
            sweep(sns, zstub)
        check("zombie: an id no longer listed active drops out of the file, a listed one stays",
              sorted(zombies_read(zombie_file())), [101])
        os.environ.pop("HPO_STATE_DIR")
    # Carries 4 and 6: the priority rule.
    PS = {"never_cancel": ["main-push", "cp-hotfix"], "priority_cancel": True}
    pb = ["fix/cp", "fix/np", "fix/verd", "fix/other"]
    pprs = [{"number": 10 + i, "state": "open", "head": {"sha": "a" * 40, "ref": b, "repo": {"full_name": REPO}}}
            for i, b in enumerate(pb)]
    tiers = {10: "cp-hotfix", 11: "instrument", 12: "instrument", 13: "tier1"}

    def pq(branch, i, status="queued", event="pull_request"):
        return _r(i, "a" * 40, event, status, branch)
    base_runs = [pq("fix/cp", 500), pq("fix/np", 501), pq("fix/verd", 502), pq("fix/other", 503),
                 pq("fix/np", 504, "in_progress"), pq("main", 505, event="push")]
    pp = priority_plan(pprs, base_runs, tiers, {12}, PS, repo=REPO)
    check("priority: a queued priority run cancels the queued non-priority runs, not in-progress, main or verdicted ones",
          ([v[0] for v in pp["victims"]], pp["main_queued"]), ([501, 503], 1))
    check("priority: the victim line names the priority PR and run",
          pp["victims"][0][2:], (10, 500))
    check("priority null: no priority run queued selects nothing",
          priority_plan(pprs, base_runs[1:], tiers, set(), PS, repo=REPO)["victims"], [])
    check("priority carry 6: a queued run of a verdicted/spooled/train PR is never selected",
          [v[1] for v in priority_plan(pprs, base_runs, tiers, {11, 12, 13}, PS, repo=REPO)["victims"]], [])
    check("priority: a priority run in progress (not queued) does not trigger",
          priority_plan(pprs, [pq("fix/cp", 500, "in_progress")] + base_runs[1:], tiers, set(), PS, repo=REPO)["victims"], [])
    held: dict = {}
    pposts: list[str] = []

    def pstub2(args, method="GET"):
        pposts.append(args[0])
        return {}
    with contextlib.redirect_stdout(io.StringIO()) as pbuf:
        r1 = priority_step(pstub2, repo=REPO, plan_=pp, held=held, allow_cancel=True, now=1000.0)
        pposts_cancel = list(pposts)
        pposts.clear()
        nop = priority_plan(pprs, base_runs[1:], tiers, set(), PS, repo=REPO)
        r2 = priority_step(pstub2, repo=REPO, plan_=nop, held=held, allow_cancel=True, now=1100.0)
    check("priority: the cancel is recorded, then re-run once no priority run is queued",
          (r1["cancelled"], sorted(pposts_cancel), r2["rerun"], sorted(pposts), held),
          (2, sorted(f"repos/{REPO}/actions/runs/{i}/cancel" for i in (501, 503)), 2,
           sorted(f"repos/{REPO}/actions/runs/{i}/rerun" for i in (501, 503)), {}))
    pposts.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        priority_step(pstub2, repo=REPO, plan_=pp, held={}, allow_cancel=False, now=1.0)
    check("priority carry 6: with priority_cancel off a queued priority run cancels nothing (hold)", pposts, [])
    vposts: list[str] = []

    def vstub(args, method="GET"):
        if method == "POST":
            vposts.append(args[0])
            return {}
        if "/comments" in args[-1]:
            num = int(args[-1].split("issues/")[1].split("/")[0])
            return None if num == 11 and "unread" in vposts else [[{"body": "Fix review: merge x" if num in (12, 13) else "hi"}]]
        return []
    vns = argparse.Namespace(repo=REPO, train_state=None, dry_run=False)
    with contextlib.redirect_stdout(io.StringIO()):
        priority_act(vns, vstub, pprs, base_runs, tiers, PS, 1.0)
    check("priority carry 6: the live verdict lookup protects #12 and #13 (Fix review: merge comments); "
          "only #11's queued run is cancelled", vposts, [f"repos/{REPO}/actions/runs/501/cancel"])
    vposts[:] = ["unread"]
    with contextlib.redirect_stdout(io.StringIO()):
        priority_act(vns, vstub, pprs, base_runs, tiers, PS, 1.0)
    check("priority carry 6: comments that cannot be read protect too (nothing cancelled)", vposts, ["unread"])
    vposts.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        priority_act(vns, vstub, pprs, base_runs, tiers, {**PS, "priority_cancel": False}, 1.0)
    check("priority carry 6: with priority_cancel off the sweep cancels nothing", vposts, [])
    check("verdict guard: a Fix review: merge comment protects; none does not; unreadable is None",
          (has_merge_verdict(lambda a: [[{"body": "Fix review: merge abc"}]], REPO, 1),
           has_merge_verdict(lambda a: [[{"body": "hi"}]], REPO, 1),
           has_merge_verdict(lambda a: None, REPO, 1)), (True, False, None))
    with tempfile.TemporaryDirectory() as td2:
        Path(td2, "queue-add.jsonl").write_text('{"pr": 21}\nnot json\n{"pr": "22"}\n')
        Path(td2, "queue.json").write_text('[{"pr": 23}, {"x": 1}]')
        check("train pins: spool lines and queue entries are read, junk is skipped",
              train_pinned(td2), {21, 22, 23})
    check("train pins: no state dir pins nothing", train_pinned(None), set())
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
    w.add_argument("--priority", action="store_true",
                   help="apply the CI-priority rule (ci_priority.py): hold or cancel queued non-priority runs")
    w.add_argument("--train-state", help="the merge train's state dir: its queue and spool pin PRs")
    a = ap.parse_args(argv[1:])
    return sweep(a) if a.cmd == "sweep" else run(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
