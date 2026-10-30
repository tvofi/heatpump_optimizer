# Review packet #3004
head: b63829d1c163aff58823157d7691894f46301ae5
base: 437f1ba9b521199b360d84effe6a621573d34663

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124324652699 neutral
arch-score / arch-score id=124324357585 success
arm id=124324090219 skipped
budget-raise-gate / budget-raise-gate id=124324357685 success
cancel-superseded id=124324093473 success
codeql / Analyze (actions) id=124324357584 success
codeql / Analyze (javascript-typescript) id=124324357539 success
codeql / Analyze (python) id=124324357726 in_progress
governance / delivery-status id=124324357690 success
governance / delivery-status-publish id=124324360285 skipped
governance / env-matrix id=124324357742 in_progress
governance / instrument-self-tests id=124324357725 in_progress
governance / policy-docs id=124324357550 success
governance / record id=124324359194 skipped
governance / wave-script id=124324357652 success
hassfest / hassfest id=124324357651 success
kernel-points id=124324359426 skipped
prelude id=124324093831 success
refresh id=124324093830 success
tests / arch-instrument id=124324844769 success
tests / briefs id=124324357622 success
tests / browser id=124324844967 in_progress
tests / closure-scope id=124324358106 success
tests / closures id=124324844698 in_progress
tests / coverage id=124324844675 in_progress
tests / fast (3.14) id=124324844889 in_progress
tests / mutation id=124324357648 success
tests / mutation-autofix id=124324839948 skipped
tests / mutation-pins id=124324838940 skipped
tests / nightly-ha id=124324846257 skipped
tests / nightly-status id=124324357827 success
tests / replay id=124324847189 skipped
tests / typing id=124324844681 success
validate / validate-hacs id=124324357480 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item b42363f1: R10-FLY-CANCEL-SWEEP: R10-FLY-CANCEL-SWEEP resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/pr/cancel_superseded.py --self-test
             `tools/pr/cancel_superseded.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head

FIGURES: 3 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3004.md b/dev/programme/delivery/3004.md
new file mode 100644
index 000000000..6979d84ef
--- /dev/null
+++ b/dev/programme/delivery/3004.md
@@ -0,0 +1 @@
+- [#3004](https://github.com/tvofi/heatpump_optimizer/pull/3004) — **open**, R10-FLY-CANCEL-SWEEP: cancel superseded runs by sweep (R10-FLY-CANCEL-SWEEP)
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 3b46d4c77..c45039bb1 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -86,6 +86,7 @@ sweep's standing-seat liveness step keep them alive.
 - [`record_row.py`](instruments/record_row.py.md) — the record-autofix generator
 - [`ref_privacy.py`](instruments/ref_privacy.py.md) — the one owner of what a push may say about the host (#2310)
 - [`remerge_main.sh`](instruments/remerge_main.sh.md) — merges origin/main into an open PR (claimnotes merge driver), drops inherited claims, pushes as the App with `app_push.sh --recarry`
+- [`cancel_superseded.py sweep`](instruments/cancel_superseded.py.md) — cancels each open PR branch's active runs at a superseded head (`tools/pr/cancel_superseded.py`, one predicate), never a live-head, main, non-PR-event or bot-head run; ghosts reported; the sweep's step 4e
 - [`run_twins.py`](instruments/run_twins.py.md) — counts a workflow's cancelled `pull_request` runs that sat beside a same-SHA sibling (two events at one head, not a supersession)
 - [`resume_doc.py`](instruments/resume_doc.py.md) — generates the resume markdown from the roster plus live PR state, under a byte budget
 - [`review_carry.py`](instruments/review_carry.py.md) — answers, from two shas and their commit range, whether a moved head still needs its own review
diff --git a/tools/audit/seat/instruments/cancel_superseded.py.md b/tools/audit/seat/instruments/cancel_superseded.py.md
new file mode 100644
index 000000000..c0227224f
--- /dev/null
+++ b/tools/audit/seat/instruments/cancel_superseded.py.md
@@ -0,0 +1,15 @@
+# `cancel_superseded.py sweep`
+
+- `python3 -I tools/pr/cancel_superseded.py sweep --repo OWNER/REPO [--dry-run]` --
+  cancels, per open same-repo pull request branch, the active (queued, in progress,
+  waiting, pending, requested) `pull_request` / `workflow_dispatch` runs at a head other than the live
+  one, using `candidates()`. Never a live-head run, a run on main, any other event,
+  or a branch whose live head `github-actions[bot]` authored; a run on a branch with
+  no open PR is a ghost, reported. Ends with one `CANCEL-SWEEP:` line.
+  When: each orchestrator sweep pass (step 4e), because the in-run cancel cannot
+  fire while the newer run is still queued for a runner (P266).
+  API cost per sweep: 1 PR listing + 5 run listings (one per ACTIVE status; one page
+  each below 100 items, at most 10 pages per listing, a still-full last page prints
+  `CANCEL-SWEEP: truncated`) + one commit read per open PR with something to cancel
+  + one POST per cancel.
+  Refusal: none; an unreadable answer cancels nothing and exits 0.
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 89a683fab..0a2ddacef 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -68,7 +68,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4d) Queue priority, for the train, review, fixer and CI queues alike: a push to main; then critical path and hotfix; then production pull requests with instrument pull requests saving 12 h or more; then other instruments by savings. A group's critical-path standing is the roster's `critical` list (`tools/audit/seat/roster_lib.py` `critical_path`); the gate order is `tools/pr/gate_priority.py`'s.
 
-(4e) CI capacity. Cancel each superseded workflow run, one whose head is no longer its pull request's head: read `gh run list --json databaseId,headSha,headBranch,status,event` against each open pull request's `headRefOid`, and `gh run cancel` the stale ones. Never cancel a run on main or on a critical-path or hotfix pull request's live head. `tools/pr/cancel_superseded.py` does the same from inside one workflow run.
+(4e) CI capacity. Cancel each superseded workflow run, one whose head is no longer its pull request's head: read `gh run list --json databaseId,headSha,headBranch,status,event` against each open pull request's `headRefOid`, and `gh run cancel` the stale ones. Never cancel a run on main or on a critical-path or hotfix pull request's live head. `tools/pr/cancel_superseded.py` does the same from inside one workflow run, and its `sweep --repo R` does it from here, for every open pull request in one pass (never a main or push-event run, never a bot-authored live head).
 
 (5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Read {{tick_log}}'s newest pass unfiltered: every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line, none truncated, and give each an action this sweep (`dev/governance/roles/standing-tick.md`); the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board. Then run `python3 -I tools/audit/seat/owed_unactioned.py --tick {{tick_log}} --state {{orch_scratch}}/owed-unactioned.json --acks {{seat_ledger}}`: it reads the tick's whole owed family (never a `grep | head` or `tail` of it) and exits 1 on each owed line that has stood two sweeps with no live `OWED-ACK` line. Each such line gets its action this sweep, or an `OWED-ACK` line in {{seat_ledger}} naming its next action and what it waits on; an acknowledgement lapses after its ttl, so the next sweep re-checks the handling. The sweep is not done while it exits 1, and its 2 is `UNREADABLE`, never clean (`dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`).
 
diff --git a/tools/pr/cancel_superseded.py b/tools/pr/cancel_superseded.py
index a82de590e..88245ebbc 100644
--- a/tools/pr/cancel_superseded.py
+++ b/tools/pr/cancel_superseded.py
@@ -3,6 +3,7 @@
 
     python3 -I tools/pr/cancel_superseded.py run --repo OWNER/REPO --workflow tests.yml \
         --pr N --head-sha SHA --branch BRANCH --run-id ID --sender LOGIN [--dry-run]
+    python3 -I tools/pr/cancel_superseded.py sweep --repo OWNER/REPO [--dry-run]
     python3 tools/pr/cancel_superseded.py --self-test
 
 R10-CI-CONCURRENCY. A workflow's `concurrency:` group cancels a pull request's
@@ -30,12 +31,32 @@ IT CANCELS NOTHING UNLESS ALL OF THESE HOLD, and prints which one failed:
 An unreadable answer from GitHub cancels nothing. Always exits 0 when it ran
 (fail-soft: the cancel is an optimisation, never a gate).
 
+`sweep` (P266) is the same rule applied from OUTSIDE any run, by the orchestrator's
+pass: while the newer run is still queued for a runner it cancels nothing from
+inside, so the superseded first push of a two-push open stayed active. One
+open-PR listing and one runs listing per ACTIVE status (every status in `ACTIVE`,
+pending and requested included), each paged `PAGE` at a time up to `MAX_PAGES`
+pages, with a `CANCEL-SWEEP: truncated` line when the last page is still full.
+API cost per sweep: 1 PR listing + 5 run listings (one page each below 100 items;
+at most MAX_PAGES pages per listing) + one commit read per open PR with something
+to cancel + one POST per cancel. Per open same-repo PR
+branch it cancels what `candidates()` selects against the live head (no run at
+the live head yet: every active run at another head). It never cancels a run at
+the live head, a run on main, or an event outside `EVENTS` (push, workflow_run,
+schedule, pull_request_target), nor on a branch whose live head was authored by
+`github-actions[bot]` (the autofix rule). A run on a branch with no open PR is
+reported as a ghost, never cancelled. Prints one line per action and
+`CANCEL-SWEEP: cancelled n, kept m (live head), skipped k (bot head / not a PR),
+ghosts g`. A critical-path or hotfix superseded run stays cancellable.
+
 `concurrency:` is unchanged and still models the bot rule (`tests/entities.py`).
 The workflow job runs the BASE's copy of this program with `actions: write`.
 """
 from __future__ import annotations
 
 import argparse
+import contextlib
+import io
 import json
 import subprocess
 import sys
@@ -43,6 +64,7 @@ import sys
 BOT = "github-actions[bot]"
 ACTIVE = ("queued", "in_progress", "waiting", "pending", "requested")
 EVENTS = ("pull_request", "workflow_dispatch")
+PAGE, MAX_PAGES = 100, 10
 
 
 def candidates(runs: list[dict], *, live_sha: str, branch: str, run_id: int) -> list[int]:
@@ -111,6 +133,106 @@ def run(a: argparse.Namespace, api=gh) -> int:
     return 0
 
 
+def sweep_plan(prs: list[dict], runs: list[dict], bot_heads: set[str], *, repo: str) -> dict:
+    """Pure part of `sweep`: {"cancel": ids, "kept": n, "skipped": n, "ghosts": [ids]}.
+
+    `prs` are open pull requests (number, head.sha, head.ref, head.repo); `bot_heads`
+    the live-head shas whose commit was authored by github-actions[bot]."""
+    live = {}
+    for pr in prs:
+        h = pr.get("head") or {}
+        if pr.get("state", "open") == "open" and (h.get("repo") or {}).get("full_name") == repo and h.get("ref"):
+            live[h["ref"]] = h.get("sha")
+    cancel, kept, skipped, ghosts = [], 0, 0, []
+    by_branch: dict[str, list[dict]] = {}
+    for r in runs:
+        if r.get("status") not in ACTIVE:
+            continue
+        b = r.get("head_branch")
+        hr = (r.get("head_repository") or {}).get("full_name")
+        if b == "main" or r.get("event") not in EVENTS or (hr and hr != repo):
+            skipped += 1
+            continue
+        if b not in live:
+            ghosts.append(int(r["id"]))
+            continue
+        by_branch.setdefault(b, []).append(r)
+    for b, rs in sorted(by_branch.items()):
+        sha = live[b]
+        kept += sum(1 for r in rs if r.get("head_sha") == sha)
+        # A run at the live head bounds the cancel by id (an older head's run only);
+        # with none yet, every active run at another head is superseded.
+        bound = max([int(r["id"]) for r in rs if r.get("head_sha") == sha] or [sys.maxsize])
+        ids = candidates(rs, live_sha=sha, branch=b, run_id=bound)
+        if sha in bot_heads:
+            skipped += len(ids)
+            continue
+        cancel += ids
+    return {"cancel": sorted(cancel), "kept": kept, "skipped": skipped, "ghosts": sorted(ghosts)}
+
+
+def listing(api, path: str, query: dict, key: str | None = None) -> "tuple[list | None, bool]":
+    """(items, truncated): every page up to MAX_PAGES; (None, False) when a page is unreadable."""
+    out: list = []
+    for pg in range(1, MAX_PAGES + 1):
+        args = [path] + [x for k, v in {**query, "per_page": PAGE, "page": pg}.items()
+                         for x in ("-f", f"{k}={v}")]
+        got = api(args)
+        rs = got.get(key) if key and isinstance(got, dict) else got
+        if not isinstance(rs, list):
+            return None, False
+        out += rs
+        if len(rs) < PAGE:
+            return out, False
+    return out, True
+
+
+def sweep(a: argparse.Namespace, api=gh) -> int:
+    prs, cut = listing(api, f"repos/{a.repo}/pulls", {"state": "open"})
+    truncated = ["pulls"] * cut
+    runs: list[dict] = []
+    for st in ACTIVE:
+        rs, cut = listing(api, f"repos/{a.repo}/actions/runs", {"status": st}, "workflow_runs")
+        if rs is None:
+            prs = None
+            break
+        truncated += [f"runs status={st}"] * cut
+        runs += rs
+    if not isinstance(prs, list):
+        print("CANCEL-SWEEP: unreadable answer; cancelling nothing")
+        return 0
+    for t in truncated:
+        print(f"CANCEL-SWEEP: truncated: {t} still full after {MAX_PAGES} pages; counts are a lower bound")
+    bot_heads: set[str] = set()
+    first = sweep_plan(prs, runs, set(), repo=a.repo)
+    if first["cancel"]:
+        # the live-head author is read only for the PRs that have something to cancel
+        by_id = {int(r["id"]): r for r in runs}
+        for pr in prs:
+            h = pr.get("head") or {}
+            if any((by_id[i].get("head_branch") == h.get("ref")) for i in first["cancel"]):
+                c = api([f"repos/{a.repo}/commits/{h.get('sha')}"])
+                if not isinstance(c, dict):
+                    print("CANCEL-SWEEP: unreadable commit; cancelling nothing")
+                    return 0
+                if ((c.get("author") or {}).get("login") == BOT
+                        or ((c.get("commit") or {}).get("author") or {}).get("name") == BOT):
+                    bot_heads.add(h.get("sha"))
+    res = sweep_plan(prs, runs, bot_heads, repo=a.repo)
+    for rid in res["cancel"]:
+        if a.dry_run:
+            print(f"cancel_superseded: would cancel {rid}")
+            continue
+        ok = api([f"repos/{a.repo}/actions/runs/{rid}/cancel"], "POST")
+        print(f"cancel_superseded: cancelled {rid}" if ok is not None
+              else f"cancel_superseded: could not cancel {rid}")
+    for rid in res["ghosts"]:
+        print(f"cancel_superseded: ghost {rid} (no open pull request on its branch)")
+    print(f"CANCEL-SWEEP: cancelled {len(res['cancel'])}, kept {res['kept']} (live head), "
+          f"skipped {res['skipped']} (bot head / not a PR), ghosts {len(res['ghosts'])}")
+    return 0
+
+
 # --- self-test ---------------------------------------------------------------
 # The recorded pair: run 39090494028 (Tests, pull_request, sender
 # github-actions[bot], attempt 2 by hpo-runs[bot], head 3b76e0b0) and the
@@ -196,6 +318,132 @@ def self_test() -> int:
     ns.dry_run = False
     check("an unreadable listing cancels nothing and exits 0",
           (run(ns, lambda a, m="GET": None), posts), (0, []))
+    # sweep: the #2927 shape (two superseded first-push runs, the live head's run queued).
+    S_OLD, S_LIVE = "e" * 40, "f" * 40
+    sb = "fix/two-push"
+    sprs = [{"number": 7, "state": "open", "head": {"sha": S_LIVE, "ref": sb, "repo": {"full_name": REPO}}}]
+    sruns = [_r(101, S_OLD, status="in_progress", branch=sb), _r(102, S_OLD, "workflow_dispatch", "queued", sb),
+             _r(103, S_LIVE, status="queued", branch=sb)]
+
+    def sw(prs=sprs, runs=sruns, bots=()):
+        return sweep_plan(prs, runs, set(bots), repo=REPO)
+    check("sweep: the #2927 shape cancels both old runs and keeps the queued live one",
+          (sw()["cancel"], sw()["kept"]), ([101, 102], 1))
+    check("sweep: with no run yet at the live head every active run at another head is cancelled",
+          sw(runs=sruns[:2])["cancel"], [101, 102])
+    check("sweep: a bot-authored live head cancels nothing", sw(bots=[S_LIVE])["cancel"], [])
+    push_main = _r(90, S_OLD, "push", branch="main")
+    push_pr = _r(91, S_OLD, "push", branch=sb)
+    check("sweep: a push run on main and a push run on a PR branch are never cancelled",
+          sw(runs=sruns + [push_main, push_pr])["cancel"], [101, 102])
+    ghost = _r(95, S_OLD, branch="fix/no-pr")
+    res = sw(runs=sruns + [ghost])
+    check("sweep: a run on a branch with no open PR is a ghost, never cancelled",
+          (res["cancel"], res["ghosts"]), ([101, 102], [95]))
+    check("sweep null: only live-head runs cancels nothing", sw(runs=[sruns[2], _r(104, S_LIVE, branch=sb)])["cancel"], [])
+    check("sweep: a fork PR head is not swept", sw(prs=[{**sprs[0], "head": {**sprs[0]["head"], "repo": {"full_name": "x/fork"}}}])["cancel"], [])
+    # mutant: dropping the event filter makes the push fixtures cancellable, so the arm above would fail.
+    global EVENTS
+    saved, EVENTS = EVENTS, EVENTS + ("push",)
+    try:
+        mutant = sw(runs=sruns + [push_pr])["cancel"]
+    finally:
+        EVENTS = saved
+    check("sweep mutant: without the event filter the push run IS cancelled (the arm detects it)",
+          91 in mutant, True)
+    # sweep, pinned arm by arm (each names the mutant it kills).
+    check("sweep: a run at an older head with a HIGHER id than the live head's run is never cancelled",
+          sw(runs=sruns + [_r(110, S_OLD, branch=sb)])["cancel"], [101, 102])
+    done = _r(96, S_OLD, status="completed", branch=sb)
+    res = sw(runs=sruns + [done, _r(97, S_LIVE, status="completed", branch=sb),
+                           _r(98, S_OLD, status="completed", branch="fix/no-pr"),
+                           _r(99, S_OLD, status="completed", branch="main")])
+    check("sweep: a finished run is neither kept, a ghost, skipped nor cancelled",
+          (res["cancel"], res["kept"], res["ghosts"], res["skipped"]), ([101, 102], 1, [], 0))
+    check("sweep: a pending or requested run at a superseded head is cancelled",
+          sw(runs=[_r(81, S_OLD, status="pending", branch=sb), _r(82, S_OLD, status="requested", branch=sb),
+                   sruns[2]])["cancel"], [81, 82])
+    forkrun = {**_r(83, S_OLD, branch=sb), "head_repository": {"full_name": "x/fork"}}
+    check("sweep: a run from a fork head repository on a PR branch's name is never cancelled",
+          sw(runs=sruns + [forkrun])["cancel"], [101, 102])
+    res = sw(runs=sruns + [push_main, push_pr, _r(92, S_OLD, "schedule", branch="main")])
+    check("sweep: main and non-PR-event runs count as skipped, not as ghosts",
+          (res["skipped"], res["ghosts"]), (3, []))
+    # only the `b == "main"` disjunct can skip these: both events are in EVENTS and the repo matches.
+    res = sw(runs=sruns + [_r(93, S_OLD, "workflow_dispatch", "queued", "main"),
+                           _r(94, S_OLD, "pull_request", "queued", "main")])
+    check("sweep: a PR-event run on main is skipped by the branch test alone, not a ghost, never cancelled",
+          (res["skipped"], res["ghosts"], res["cancel"]), (2, [], [101, 102]))
+    spost: list[str] = []
+    author = {"login": "hpo-author[bot]", "name": "x"}
+
+    def sstub(args, method="GET", prs=None, fail=(), runs=None):
+        q = {args[i].split("=")[0]: args[i].split("=")[1] for i in range(2, len(args), 2) if "=" in args[i]}
+        if args[0].endswith("/pulls"):
+            return None if "pulls" in fail else (sprs if prs is None else prs)
+        if args[0].endswith("/actions/runs") and method == "GET":
+            if "runs" in fail and q["status"] == "waiting":
+                return None
+            return {"workflow_runs": [r for r in (sruns if runs is None else runs)
+                                      if r["status"] == q["status"] and q["page"] == "1"]}
+        if "/commits/" in args[0]:
+            return None if "commit" in fail else {"author": {"login": author["login"]},
+                                                   "commit": {"author": {"name": author["name"]}}}
+        spost.append(args[0])
+        return {}
+
+    def quiet(a, **kw):
+        buf = io.StringIO()
+        with contextlib.redirect_stdout(buf):
+            rc = sweep(a, lambda x, m="GET": sstub(x, m, **kw))
+        return rc, sorted(spost), buf.getvalue()
+    sns = argparse.Namespace(repo=REPO, dry_run=False)
+    want = sorted(f"repos/{REPO}/actions/runs/{i}/cancel" for i in (101, 102))
+    rc, got, out = quiet(sns)
+    check("sweep end to end: POSTs exactly the two old runs", (rc, got), (0, want))
+    spost.clear()
+    sns.dry_run = True
+    quiet(sns)
+    check("sweep --dry-run posts nothing", spost, [])
+    sns.dry_run = False
+    check("sweep: an unreadable answer cancels nothing and exits 0",
+          (sweep(sns, lambda a, m="GET": None), spost), (0, []))
+    for what in ("pulls", "runs", "commit"):
+        spost.clear()
+        rc, got, out = quiet(sns, fail=(what,))
+        check(f"sweep: an unreadable {what} answer cancels nothing and says unreadable, not a zero count",
+              (rc, got, "unreadable" in out, "cancelled 0" in out), (0, [], True, False))
+    for who in ({"login": BOT, "name": "x"}, {"login": "u", "name": BOT}):
+        author.update(who)
+        spost.clear()
+        check(f"sweep end to end: a live head authored by the bot ({who}) cancels nothing",
+              quiet(sns)[1], [])
+    author.update({"login": "hpo-author[bot]", "name": "x"})
+    spost.clear()
+    quiet(sns, runs=[_r(81, S_OLD, status="pending", branch=sb), _r(82, S_OLD, status="requested", branch=sb),
+                     sruns[2]])
+    check("sweep end to end: every ACTIVE status is listed, so pending and requested runs are POSTed",
+          sorted(spost), sorted(f"repos/{REPO}/actions/runs/{i}/cancel" for i in (81, 82)))
+    # pagination: a full page 1 must be followed by page 2; a still-full last page is reported.
+    seen: list[str] = []
+    full = [_r(300 + i, S_LIVE, branch=sb) for i in range(PAGE)]
+
+    def pstub(args, method="GET"):
+        pg = [x for x in args if x.startswith("page=")][0]
+        seen.append(pg)
+        if args[0].endswith("/pulls"):
+            return sprs
+        return {"workflow_runs": full if pg == "page=1" or "always" in seen else []}
+    with contextlib.redirect_stdout(io.StringIO()):
+        sweep(sns, pstub)
+    check("sweep: a full page is followed by the next page, and a short page stops", "page=2" in seen, True)
+    seen.clear()
+    seen.append("always")
+    buf = io.StringIO()
+    with contextlib.redirect_stdout(buf):
+        sweep(sns, pstub)
+    check("sweep: a listing still full after MAX_PAGES prints a truncated line",
+          "truncated: runs status=queued" in buf.getvalue(), True)
     print(f"cancel_superseded self-test: {n} checks, {fails} failed")
     return 1 if fails else 0
 
@@ -212,7 +460,11 @@ def main(argv: list[str]) -> int:
     r.add_argument("--run-id", type=int, required=True)
     r.add_argument("--event", default="pull_request")
     r.add_argument("--dry-run", action="store_true")
-    return run(ap.parse_args(argv[1:]))
+    w = sub.add_parser("sweep")
+    w.add_argument("--repo", required=True)
+    w.add_argument("--dry-run", action="store_true")
+    a = ap.parse_args(argv[1:])
+    return sweep(a) if a.cmd == "sweep" else run(a)
 
 
 if __name__ == "__main__":

