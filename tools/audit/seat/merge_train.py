#!/usr/bin/env python3
"""The merge train: land a queue of verdicted pull requests, one at a time or as a batch.

    python3 tools/audit/seat/merge_train.py run <queue.json> [--mandate LABEL]
        [--approver-role ROLE] [--ignore-red NAME]... [--repo OWNER/REPO]
        [--state-dir DIR] [--min-runs N]
    python3 tools/audit/seat/merge_train.py batch <queue.json> [run's options]
        [--base main|batch/<name>] [--tag TAG] [--skip-bad] [--overlap]
    python3 tools/audit/seat/merge_train.py wait-ci <40-hex sha> [--min-runs N]
    python3 tools/audit/seat/merge_train.py --self-test

The queue is a JSON list, merged in order:

    [{"pr": 1869, "verdict": "<40-hex head the merge verdict names>",
      "verdict_comment": "<the verdict comment's id, quoted in a mandate approval; the comment itself must cite an absolute evidence path -- app_approve.sh's evidence gate reads the comment and refuses a verdict naming no qualifying absolute directory>",
      "branch": "<optional; read from the pull request>",
      "worktree": "<optional; the recarry makes one under the state directory, holding the pull request's BRANCH (see step 1)>",
      "issues": [<optional; the issues the body intends to close, for preflight>]}]

PER PULL REQUEST, IN ORDER; THE TRAIN STOPS AT THE FIRST REFUSAL, because every
later pull request would be graded against a `main` the refused one never joined:
  1. recarry  -- a head that does not contain `origin/main` gets main merged in by
                 `remerge_main.sh` (an automatic merge, no resolution), pushed by
                 `app_push.sh --recarry`, whose prepr skip-or-run line is logged; a conflict
                 or a push that did not land stops the train. The recarry worktree
                 is the pull request's BRANCH checked out at `origin/<branch>`
                 (-B, so an existing local branch is reset), never a detached
                 HEAD: `app_push.sh` pushes only a committed tip, and a detached
                 auto-merge sha is not the committed tip of anything (#1943);
  2. ci       -- every check run at the head completes (all pages, at least
                 --min-runs); a latest run that is not success, skipped or
                 neutral stops it, except the `--ignore-red` names (default
                 `nightly-status`, which grades `main`, not the head). A head
                 whose TIP is a GITHUB_TOKEN push (author `github-actions[bot]`)
                 is refused before any check is read: such a push's
                 `pull_request` runs are held `action_required`, so the
                 required contexts only one writes stay ABSENT at it until a
                 held run is approved, and the merge would be refused with
                 nothing saying why (R9-RC-AUTOFIX-GOVERNANCE).
                 The required follow-up is an App push -- step 1's recarry is
                 one, which is why the refusal fires only where the head
                 already contains main;
  3. carry    -- `app_approve.sh --carry <verdict> <head>` must say `CARRY: yes`:
                 the head differs from the verdicted one only by automatic merges;
  4. main     -- `origin/main` is still inside the head after CI (else main moved:
                 recovered up to --main-moved-tries times, below);
  5. policy   -- no changed file (`--no-renames`, so a rename names the path it
                 left; a failing merge-base or diff stops the train) is policy, as `policy_lint.mjs --corpus-filter`
                 defines it (probed with a sentinel pair first, as preflight.sh
                 does). A POLICY HEAD LANDS ONLY UNDER A VALID MANDATE: the
                 owner's APPROVED review at exactly this head, cited by id to
                 a mandate whose window is open AT THE MERGE, both re-read by
                 `land` when it merges -- the mandate read is `budget_raise_gate.py`'s own (mandate_state,
                 decision 0013 amended 2026-10-02, tvofi's scope for policy
                 merging `all`). With no such mandate the train refuses exactly
                 as it did before one existed (tvofi, 2026-10-09, #201 comment 6083743563:
                 batch merging of policy under an exceptional mandate, falling
                 back when there is none -- after its window no code edit is
                 needed);
  6. approve  -- `app_approve.sh` at the head. When its refusal is exactly its own
                 code-owned line for this pull request (anchored: a blocked
                 verdict's echoed reason can carry the same words), and `--mandate` was given,
                 the train approves as the account `gh` is logged in as, with a
                 body naming the mandate label, the role, the verdict comment and
                 the carried head. Without `--mandate`, or on any other refusal
                 (missing evidence included), it stops. A budget RAISE --
                 `Train.raise_hold`: budget_raise_gate's own `raises_between`
                 from the merge base, the direction CI's gate reads, never a
                 `*_budgets.json` path, so a file that only gains rows is none
                 -- is the owner's (0013): it lands only on the owner's approval
                 already at the head, judged as the gate's `decide` judges it
                 (the body's raise justification included) with its mandate
                 read at the merge, and else stops with the gate's reason;
  7. ready, preflight of the title (`REFUSE` stops), merge with
     `--match-head-commit` (retried; `main` re-checked before each attempt;
     every refusal logged in GitHub's words, a base-moved one -- or, serially,
     every attempt refused with main moved past the head -- recovered as a
     moved main), the closing-issue read-back, and `worktree_gc.sh`. The
     recarry worktrees a run made are removed before its closing line.

It prints one line per step and ends `TRAIN DONE` or `TRAIN STOPPED #<pr> <step>:
<reason>` (exit 1). A real run publishes `TRAIN HOLD refs/heads/train-hold`
before anything merges and releases it just before the closing line: CI
cannot see this process's pidfile, and tests.yml's record beat auto-merges
record pull requests otherwise, moving main mid-train (#2291/#2295/#2299,
2026-10-15; issue #2302). Every GitHub write is the orchestrator's: run this
only from the orchestrator's machine and identity (decisions 0011, 0013).
Replaces the session-local train3.py / mergewhen.sh / waitci.sh of round 9;
the stale-base guard mergewhen.sh carried is subsumed by step 4, which refuses
any head that does not contain the `main` it merges into.

BATCH (R9-RO-12; tvofi chose B and D of the merge-batching pre-study, 2026-10-07).
Same queue file; no head is re-merged with main. In order:
  0. main     -- every required context at main's tip completed green, or
                 nothing is admitted (a proof on a red main blames its entries);
  1. admit    -- each head's own files (three-dot from main) are classed by
                 merge_fastpath.py's `file_class`: a workflow, claim, grader or
                 any `*_budgets.json` change goes SERIAL (a routing by path, not
                 a raise reading: serially, step 6's `raise_hold` decides
                 whether the change is a raise), and so does a head
                 whose tip is a GITHUB_TOKEN push (`bot-head`): its
                 `pull_request` runs are held, so no proof can carry it, and its serial recarry -- once the batch's own merges
                 moved main -- is the App push that cures it (refused there as
                 before when main never moved). The
                 rest must be green at their head (all check runs, less
                 --ignore-red), carry their verdict, carry their row and pass
                 step 5's policy decision -- else it stops; `land` re-reads
                 that decision at the merge, so admission is only the early
                 refusal, not the verdict;
  2. build    -- P_i = the merge of P_(i-1) and head i that GitHub will make
                 (git's text merge in place of every .gitattributes driver, which
                 GitHub never runs), P_0 = origin/main; a head that does not merge
                 cleanly goes serial, which covers every pairwise conflict;
  3. prove    -- B: two or more entries push P_n to batch/<tag>-<n> as the App
                 (`app_push.sh --branch-only`), dispatch DISPATCH on it, and wait
                 for every required context of `main-protect-checks` less
                 PR_ONLY. Red drops the one entry whose files are in the closure
                 of every script the red jobs name and proves the rest again;
                 unattributed, every all-but-one set is proved side by side and
                 the green one dropping the latest entry merges; none green
                 stops, nothing merged. D: a batch of one is not proved;
  4. merge    -- each entry as `run` approves and merges it, only while main's
                 tree equals P_(i-1)'s (the first only while main's tip is still
                 green, re-read), and main's tree must equal P_i's after. A
                 FOREIGN merge before an entry's merge (the batch's own leave
                 the tree equal to the proof's) rebuilds and re-proves what is
                 left on the new main, up to --main-moved-tries times;
  5. serial   -- routed and dropped entries go through `run`'s steps, in queue
                 order; after a D merge, only once main's run on it is green.
The spent batch/ branches are deleted when the batch completes; a delete the
remote refuses is logged as NOT deleted, never as done. Residuals: GitHub's
merge takes no expected base, so a merge landing between the guard and ours is
caught only by step 4's after-check; and a proved pair's second merge lands
before main's push run on the first finishes, so a red that run would show
does not hold the second back -- accepted, because the proof graded the tree
both merges make, and main's run on the last merge grades it again.
A single merge thus rests on main's FULL push run, red there reverted first
(orchestrator.md section 11). `--base batch/<name>` REHEARSES on a throwaway
base: steps 1's carry, row and policy reads, 4's approval and 5 are skipped.

`--skip-bad` (batch only) answers a train stopped by ONE bad entry -- the
orchestrator re-fired the whole queue for it three times in a day. A Stop an
entry raises in its own admission, recarry, carry, CI wait or merge logs
`SKIP #<pr> <phase>: <reason>` (the reason echoed exactly as the stop would
have printed it) and the train continues with the next entry; the run closes
with `<state-dir>/skipped.json` ([{pr, phase, reason}...]) and a
`SKIP REPORT: N skipped of M` line, and the exit code is 1 -- the queue ran
to its end, but a caller that treats rc 0 as "nothing to look at" must be
told some entries were left behind. Two Stops are never skippable: a red
MAIN (the step-0 gate and the merge guard's re-read stay global -- a proof
on a red main blames its entries), and a Stop arriving AFTER the merge API
call, which is fatal for its entry alone: logged `SKIP #<pr> post-merge`,
the entry is never retried (the merge may already have landed), and the next
entry's guard still refuses to merge onto a tree nobody read. Without the
flag every Stop stops the train, exactly as before.

`--overlap` (batch only) is the owner's P7 decision: do not wait on main's CI
before a merge. Two measured facts shape it. Main's post-merge required run
blocks the next entry through `main_green` -- under the flag that gate is
LOG-ONLY (the batch's own green proofs and each head's own required contexts
remain the gates). And after a recarry the RULESET still blocks `gh pr merge`
until the pull request's OWN required contexts conclude at the recarry head
(~40 min; no flag can bypass a ruleset) -- so the win is overlap, not
skipping: under the flag every SERIAL entry is re-carried UP FRONT, at batch
start, pushing each branch so all their pull_request runs fire concurrently;
entries then land one at a time in queue order, each when its own contexts
conclude. Queue order holds absolutely: an earlier entry still pending is
never jumped by a later eligible one. An entry recarried up front guards its
merge on the base it was recarried onto remaining main's ancestor -- main may
advance only by this batch's own merges, and anything else stops the train.
Without the flag the serial path is byte-for-byte today's: recarry one, wait,
merge, next.

`--approval-carry` (run and batch) answers a cost measured three times on
2026-10-12: a recarry moves a head from h0 to h, the owner's APPROVED review no
longer names the live head, and a budget-raise entry then hard-stops for an
approval the owner already gave -- which the orchestrator then re-posts by
hand. Under the flag, when THIS invocation's recarry moved the head from h0 to
h, the `git diff --name-only h0..h` delta names no branch-own file (a clean
merge of main's commits only -- a conflict resolution is branch-own by
definition and never qualifies), and the pull request's latest owner APPROVED
review sits at h0 with a body citing exactly one mandate comment, the train
re-posts that approval at h: the prior body plus one line -- "Carried by the
train's clean recarry from h0 (delta: main's commits only); prior owner review
<id>; mandate re-read in force at merge: <label>." The mandate is RE-READ at
the merge moment by budget_raise_gate's own mandate_state through the train's
existing read, never cached from admission. Each of these leaves the entry
exactly where today's train left it, stop included: the flag off, the mandate
not in force, a branch-own file in the delta, no qualifying prior review, or a
re-post that fails its byte-identical read-back. The approval may name any head
this invocation's recarries moved through (a main-moved recovery recarries
again). And an owner approval ALREADY at the live head is the owner's, with
nothing re-posted, flag or not -- GitHub re-anchors an approval's commit_id
across a clean base merge, which is why #2209's carry found no approval at h0
(its review named 8a8e66e7 in the body; the API reports the recarried 8876da3b).

THE 2026-10-15 OPTIONS (R10-TICK-TRAIN, tvofi: "handle main moved and collect and
merge bot PRs automatically"; run and batch):
  --main-moved-tries N (default 3; 0 is the old stop) -- a foreign merge that
      moves main under a settled head is recovered: serially by a recarry onto
      the new main and a fresh CI wait (carry, approval, policy gate and
      --match-head-commit all re-read at the new head); in a batch by
      re-proving the remaining entries on the new main. Past N it stops as
      before, naming the spent bound. A post-merge skip disables the batch
      recovery: that tree is the batch's own unexplained one.
  --bot-prs -- the open record/autofix pull request merges in the train's own
      sequence (before the batch's base is read, before each recarry), behind
      record_row.py's identical `--automerge-check --require-green` guard at
      its head and --match-head-commit; a refusal or a pending check never
      merges it and never stops the train. Its CI beat still merges one the
      train has not taken; the recovery above answers that move.
  --pre-flight -- queue_pre_flight.py's reads first; a PARK or FAIL entry is
      left out (`PARK #<pr>` line, skipped.json, rc 1) instead of stopping the
      train at its turn.
  --free-holders -- a recarry branch checked out in another worktree that is
      clean (no untracked file) with HEAD at origin/<branch> is detached
      (`git -C <holder> switch <branch>` restores it); anything else is the
      HOLDER stop, its reason appended.
"""

from __future__ import annotations

import argparse
import datetime
import functools
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HEX = frozenset("0123456789abcdef")

# EVERY SCRIPT THE TRAIN RUNS, AND WHERE THE ROW IT REQUIRES LIVES (#1990's RCA,
# dev/audit/rca/R9-RCA-1990.md). R9-RO-6 moved app_approve.sh and preflight.sh to
# tools/pr/ and R9-RO-5 lifted the delivery rows under dev/programme/; the train
# kept the old strings, so every run stopped at the carry, and its self-test --
# whose stub answers any argv containing a script's basename -- stayed 43/43
# green. A script resolves to the first candidate in the tree, the old path
# first, the convention the move set for the scripts it moved; the self-test
# refuses a name none of whose candidates exists, and a bare script path in a
# `self.run` argv that bypasses this table.
TOOLS = {
    "app_approve": ("tools/audit/app_approve.sh", "tools/pr/app_approve.sh"),
    "app_push": ("tools/audit/app_push.sh", "tools/pr/app_push.sh"),
    "preflight": ("tools/audit/preflight.sh", "tools/pr/preflight.sh"),
    "remerge_main": ("tools/audit/seat/remerge_main.sh",),
    "worktree_gc": ("tools/audit/worktree_gc.sh",),
}
ROW_DIR = "dev/programme/delivery"


def tool(name: str) -> str:
    for c in TOOLS[name]:
        if (ROOT / c).is_file():
            return c
    return TOOLS[name][-1]


def is_sha(s: str) -> bool:
    return len(s) == 40 and set(s) <= HEX
GREEN = ("success", "skipped", "neutral")
# One check-runs read per head every five minutes (tvofi, 2026-10-07: every
# seat shares one API quota, and it ran out); 24 reads wait two hours.
POLL_SECONDS = 300
# The heartbeat (tvofi, 2026-10-13): the batch train sat silent 2+ hours inside
# --overlap's up-front recarry phase (each recarry logs only on completion, and
# app_push's prepr takes 5-15 min per entry) and inside wait_ci's poll cycle,
# and two HEALTHY trains were killed as dead. Every HEARTBEAT_SECONDS of
# elapsed wait one `beat:` line goes out -- time-based, not poll-based, so a
# poll slower or faster than the beat never hides it. Log lines only: no gate,
# wait, merge decision or exit code reads them.
HEARTBEAT_SECONDS = 240
# The main-moved recovery's bound (R10-TICK-TRAIN, tvofi 2026-10-15: #2284 sat
# green 14/14 and was stopped because a record PR auto-merged). Each recovery
# costs one full CI wait at the new head (~40 min), so three bound a busy
# main's entry to about two hours before it stops as before.
MAIN_MOVED_TRIES = 3
# THE RECORD-BEAT HOLD (R10-TRAIN-HOLD, issue #2302). CI cannot see this
# process's pidfile, and the record beat in tests.yml auto-merges record pull
# requests on its own schedule: #2291, #2295 and #2299 each landed mid-train
# on 2026-10-15 and stopped or re-carried #2284 and #2290. A real run
# publishes this ref while it is live and deletes it at its closing line; the
# beat skips while the ref is younger than its own HOLD_MAX_AGE_S and treats
# an older one as stale, so a crashed train cannot block records forever. The
# ref points at a commit created at publication, whose committer date is the
# age the beat reads; it is refreshed at the start of every queue item, before
# every recarry, and before every sleep inside wait_ci, so the age is the last
# REFRESH's, not the run's, and the beat's bound prices that gap -- one phase
# (a recarry or a poll), never a whole CI wait and never a whole batch. A
# `batch/` rehearsal publishes nothing: it merges nothing into main.
HOLD_REF = "refs/heads/train-hold"
# The recarry re-read's settle (R9-RC-RECARRY-READBACK). app_push.sh --recarry
# now confirms a push GitHub has not yet indexed inside its own bounded
# read-back, so a non-PUSHED recarry is a real refusal -- or a lag that outran
# app_push's budget. Before declaring a stop the train re-reads the head once
# after this settle: a push that landed moves the head, so a head that is no
# longer the pre-recarry one proves the push landed despite the refusal. One
# GET /pulls/{n} on this host measured TTFB 0.06-0.36s, so 2s is ~6x the worst
# observed -- enough for one more read against a multi-minute pass, and paid
# only on a refusal (never on the common path).
RECARRY_RESETTLE = 2
# THE BATCH PROOF (`batch`). The required contexts are read from this ruleset at
# run time. These three are written only by a pull-request event -- a body's
# contract, a diff's closure scope, a budget raise -- so no dispatch writes
# them; each is a required context, green at every head the batch admits.
RULESET = "main-protect-checks"
PR_ONLY = ("closure-scope", "pr-contract", "budget-raise-gate")
# Every other required context comes from one of these, each dispatchable; a
# PR-like `fast` needs tests.yml's recheck input (GATE_SCOPE=auto against
# main's merge base, which is the batch's whole diff).
DISPATCH = (("tests.yml", ("-f", "recheck=true")), ("governance.yml", ()), ("codeql.yml", ()),
            ("hassfest.yml", ()), ("validate.yml", ()))
FAILED_SCRIPT = re.compile(r">>> FAILED: .*?(tests/[\w./-]+\.(?:py|mjs|sh))\b")


@functools.lru_cache(maxsize=None)
def _fastpath():
    """merge_fastpath.py, whose file classes route a pull request serial."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("merge_fastpath", ROOT / "tools/audit/merge_fastpath.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Stop(Exception):
    def __init__(self, step: str, why: str, cls: "str | None" = None) -> None:
        super().__init__(f"{step}: {why}")
        self.step, self.why, self.cls = step, why, cls


# THE BLOCK CLASSES (tvofi, 2026-10-13, after train-batch3 stopped all eight
# entries on one unexplained worktree refusal): every stop whose shape the
# train has seen before carries its class, its verified cause and the exact
# remedy IN THE LINE ITSELF -- a skip is self-describing and the orchestrator
# never re-derives the fix from raw git output. The class goes in brackets
# right after the step (`TRAIN STOPPED #7 recarry [HOLDER]: ...`), so a line
# greps by class and the old `TRAIN STOPPED <step>:` prefix is unchanged.
# GitHub's refusals that mean the base moved under the merge (the REST 405
# "Base branch was modified", the GraphQL "is not up to date" family).
BASE_MOVED = re.compile(r"base branch was modified|not up to date|head branch is behind|is behind the base", re.I)
HOLDER = "HOLDER"                    # the recarry's branch is checked out in another worktree
BOT_HEAD = "BOT-HEAD"                # a GITHUB_TOKEN push is the head: its pull_request runs are held
STALE_VERDICT_CARRY = "STALE-VERDICT-CARRY"  # the verdict sha no longer carries: the branch moved post-verdict
ROW_MISSING = "ROW-MISSING"          # no delivery row in the three-dot diff
BOT_ROUTE = "bot-head"               # batch: a GITHUB_TOKEN tip goes serial, where its recarry cures it
MAIN_MOVED = "MAIN-MOVED"            # origin/main moved under a settled head or a proof


class MainMoved(Stop):
    """A foreign merge moved origin/main under a head (or a proof) the train
    had settled. `--main-moved-tries` recovers it: the serial path re-carries
    onto the new main and waits CI again, the batch re-proves what is left on
    it -- every guard re-read at the new head. Past the bound it stops as a
    plain Stop always did."""

    def __init__(self, step: str, why: str) -> None:
        super().__init__(step, why, cls=MAIN_MOVED)


def classified(s: Stop) -> str:
    """<why>, prefixed `[<class>] ` when the stop is one of the known shapes."""
    return f"[{s.cls}] {s.why}" if s.cls else s.why


# The one reader of the owner's recorded mandate, old path first (the TOOLS
# convention above).
GATE_PATHS = (".claude/workflows/budget_raise_gate.py", "tools/policy/budget_raise_gate.py")


@functools.lru_cache(maxsize=None)
def _mandate_gate():
    """budget_raise_gate.py, imported, never copied (fixer.md step 17): the
    grammar of a mandate, its scope sets, its window, the owner's pinned
    identity and the loose revocation are the gate's and live in no other
    file. The API plumbing in `Train._mandate_read` is the train's own
    because every command the train runs goes through `self.run`, which the
    self-test stubs; that is plumbing, not a second reading of the concept."""
    p = next((ROOT / c for c in GATE_PATHS if (ROOT / c).is_file()), None)
    if p is None:
        raise Stop("policy", f"budget_raise_gate.py is in no place the train looks "
                   f"({', '.join(GATE_PATHS)}), so no mandate can be read")
    import importlib.util
    spec = importlib.util.spec_from_file_location("budget_raise_gate", str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# A fixture comment id for both self-tests (the run arms and the batch arms
# approve-and-mandate through these builders, so they read one shape).
MID = 4100000001


def policy_fixture_builders():
    """(gate module, owner_review, mandate, revoke) -- the objects the policy
    stop reads, built from the gate's own pinned constants so a fixture can
    never disagree with the pin it is checked against."""
    g = _mandate_gate()
    own = {"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE}

    def iso(dt: datetime.datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def owner_review(sha: str, at: datetime.datetime, cite: bool = True, state: str = "APPROVED") -> dict:
        return {"user": own, "state": state, "commit_id": sha, "submitted_at": iso(at),
                "body": (f"Agent approval (the orchestrator, not {g.OWNER_LOGIN} in person) "
                         f"under mandate {MID}." if cite
                         else f"Approved: the policy change reads right.")}

    def mandate(at: datetime.datetime, scope: str = "all", from_min: int = -60, until_min: "int | None" = 60) -> dict:
        created = iso(at + datetime.timedelta(minutes=from_min))
        until = "programme-end" if until_min is None else iso(at + datetime.timedelta(minutes=until_min))
        return {"id": MID, "user": own, "created_at": created, "updated_at": created,
                "issue_url": f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/{g.MANDATE_ISSUE}",
                "body": f"MANDATE: agents may approve as {g.OWNER_LOGIN}, scope {scope}, "
                        f"from {created} until {until}"}

    def revoke(comment_id: int = MID) -> dict:
        return {"id": comment_id + 1, "user": own, "body": f"MANDATE REVOKED {comment_id}"}
    return g, owner_review, mandate, revoke


# The self-tests' budget worlds: {path: (text at the merge base, text at the
# head)}, None for an end the file is absent at. RAISE_FIXTURE is a real raise
# (a cap goes up); NEW_ROWS_FIXTURE is #2401's shape, a budget file that only
# gains rows, which budget_raise_gate reads as no raise at all.
RAISE_FIXTURE = {"tests/structure_budgets.json": ('{\n "m": 3\n}\n', '{\n "m": 4\n}\n')}
NEW_ROWS_FIXTURE = {"tests/ci_budgets.json": (
    '{\n "archscore.hub_solve_writes": 41,\n "reason": "r"\n}\n',
    '{\n "archscore.hub_solve_writes": 41,\n "archscore.shape_copies": 66,\n "reason": "new row"\n}\n')}
JUSTIFIED_BODY = ("## Summary\n\nRaise.\n\n## Raise justification\n\n- Payments tried: none left.\n"
                  "- Architecture score: dS +0.4 IMPROVES\n")


def budget_fixture(budgets: "dict | None", argv: list[str], base: str) -> "tuple[int, str] | None":
    """A stubbed `run`'s answer to raise_hold's tree and blob reads from a
    budget world (above): the base tree is <base>, any other sha the head.
    None: not a read this world answers."""
    if not budgets:
        return None
    if argv[:4] == ["git", "ls-tree", "-r", "--name-only"]:
        end = 0 if argv[4] == base else 1
        return 0, "".join(f"{p}\n" for p, ends in budgets.items() if ends[end] is not None)
    if argv[:2] == ["git", "show"] and ":" in argv[2]:
        sha, path = argv[2].split(":", 1)
        if path in budgets:
            text = budgets[path][0 if sha == base else 1]
            return (0, text) if text is not None else (128, f"fatal: path '{path}' does not exist in '{sha}'")
    return None


class Train:
    def __init__(self, repo: str, state: Path, mandate: str | None, role: str,
                 ignore: tuple[str, ...], min_runs: int, run=None, sleep=time.sleep,
                 log=print, polls: int = 24, merge_tries: int = 8, base: str = "main",
                 skip_bad: bool = False, overlap: bool = False,
                 approval_carry: bool = False, main_moved_tries: int = 0,
                 bot_prs: bool = False, pre_flight: bool = False,
                 free_holders: bool = False,
                 clock: "callable" = time.monotonic) -> None:
        self.repo, self.state, self.mandate, self.role = repo, state, mandate, role
        if base != "main" and not base.startswith("batch/"):
            raise ValueError(f"--base {base}: main, or a batch/ rehearsal base")
        # A batch/ base is a REHEARSAL: no ruleset guards it and nothing merged
        # there reaches main, so the verdict, row, policy and approval reads --
        # which grade a merge into main -- are not made (`batch`).
        self.base, self.real = base, base == "main"
        self.ignore, self.min_runs, self.polls, self.merge_tries = ignore, min_runs, polls, merge_tries
        self.run = run or self._run
        self.sleep, self.log, self.clock = sleep, log, clock
        # `batch --skip-bad` only: a per-entry Stop is skipped and reported
        # rather than stopping the train. Default (False) stays fail-fast.
        self.skip_bad = skip_bad
        # `batch --overlap` only: main_green is log-only and the serial entries
        # are recarried up front. Default (False) is today's serial train.
        self.overlap = overlap
        # `--approval-carry`: re-post an owner approval a clean recarry moved
        # out from under, under a mandate re-read at the merge. Default (False)
        # is today's train: a budget stop stops, however clean the recarry was.
        self.approval_carry = approval_carry
        # The 2026-10-15 options (R10-TICK-TRAIN, tvofi): each 0/False here is
        # today's train; the CLI's --main-moved-tries defaults to MAIN_MOVED_TRIES.
        self.main_moved_tries, self.bot_prs = main_moved_tries, bot_prs
        self.pre_flight, self.free_holders = pre_flight, free_holders
        self.skipped: list[dict] = []
        self.made_wts: list[Path] = []  # recarry worktrees THIS run created (release_worktrees)
        self.held = False  # this run's HOLD_REF is published (hold_refresh/hold_release)
        self.hold_armed = False  # a train/batch owns the ref; `wait-ci` never publishes one

    @staticmethod
    def _run(argv: list[str], cwd: Path = ROOT, stdin: str | None = None) -> tuple[int, str]:
        r = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def out(self, *argv: str, cwd: Path = ROOT, stdin: str | None = None) -> str:
        return self.run(list(argv), cwd=cwd, stdin=stdin)[1].strip()

    def ok(self, *argv: str, cwd: Path = ROOT) -> bool:
        return self.run(list(argv), cwd=cwd)[0] == 0

    def head(self, pr: int) -> str:
        return self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "headRefOid", "--jq", ".headRefOid")

    def contains_main(self, h: str) -> bool:
        self.run(["git", "fetch", "-q", "origin", "main", h])
        return self.ok("git", "merge-base", "--is-ancestor", "origin/main", h)

    # R9-RC-AUTOFIX-GOVERNANCE. A GITHUB_TOKEN push (the autofix jobs' pin and
    # re-record commits, the merge-main bot's resolution) does create
    # pull_request runs, but they are held action_required (actor
    # github-actions[bot]) until approved -- every bot head from
    # 2026-10-15T10:23Z, e.g. Tests run 38781421410 at 720d3636: attempt 1
    # action_required, attempt 2 approved by hpo-runs[bot]. Until then the
    # required contexts only a pull_request run writes are ABSENT. On
    # 2026-10-09 no such run was created at all (63084989/#2066 and
    # a9ba0b88/#2070: 4 dispatched runs each, the same 5 of the 17 required
    # contexts of main-protect-checks absent). The autofix job's approve step
    # approves the held runs, fail-soft while its secrets are absent; this
    # train does not read whether it did, so it still refuses such a tip.
    # Dispatch cannot write those contexts: governance.yml answers
    # workflow_dispatch, but pr-contract.yml and budget-raise-gate.yml take
    # pull_request/merge_group only. An App push is a follow-up that does, and
    # the train's own recarry (step 1) is one -- so the refusal fires only where
    # the head already contains main and no recarry is possible.
    def bot_tip(self, h: str) -> "str | None":
        """The subject of <h>'s tip commit when a GITHUB_TOKEN push put it there
        (author github-actions[bot], the login every such push carries), else
        None. An unreadable head commit stops the train: a head whose author
        cannot be read is a head this check cannot clear."""
        code, o = self.run(["gh", "api", f"repos/{self.repo}/commits/{h}", "--jq",
                            '[(.author.login // .commit.author.name), '
                            '(.commit.message | split("\\n")[0])] | @tsv'])
        if code or "\t" not in o:
            raise Stop("ci", f"the head commit at {h[:8]} could not be read: {o.strip()[-160:]}")
        who, _, subject = o.strip().partition("\t")
        return subject if who in ("github-actions", "github-actions[bot]") else None

    def bot_refusal(self, pr: int, h: str, subject: str) -> Stop:
        return Stop("ci", f"#{pr} head {h[:8]} is a GITHUB_TOKEN push (github-actions[bot]: "
                    f"'{subject}'): its pull_request runs are held action_required, so the required "
                    "contexts only they write are ABSENT until one is approved -- the head can look "
                    "settled and be unmergeable, with nothing saying why. The required follow-up is an App push at this "
                    "head: run the train again once main has moved (its recarry is one), or "
                    "have the orchestrator App-push the branch", cls=BOT_HEAD)

    def branch_holder(self, br: str) -> "str | None":
        """The worktree path that has branch <br> checked out, from
        `git worktree list --porcelain`; None when no worktree holds it (then
        the worktree add failed for a reason this class does not describe)."""
        code, o = self.run(["git", "worktree", "list", "--porcelain"])
        if code:
            return None
        path = None
        for ln in o.splitlines():
            if ln.startswith("worktree "):
                path = ln[len("worktree "):].strip()
            elif ln.startswith("branch refs/heads/") and ln[len("branch refs/heads/"):].strip() == br:
                return path
        return None

    def holder_refusal(self, wt: Path, br: str) -> Stop:
        holder = self.branch_holder(br)
        if holder is None:
            return Stop("recarry", f"could not make a worktree at {wt}")
        return Stop("recarry",
                    f"could not make a worktree at {wt}: branch {br} is already checked out in "
                    f"another worktree at {holder}. Free it: git worktree remove {holder} "
                    f"(safe when its work is pushed; verify with git -C {holder} status)",
                    cls=HOLDER)

    def freeable(self, path: str, br: str) -> "str | None":
        """None when the worktree at <path> holding <br> can be detached with
        nothing lost -- no change and no untracked file (`status --porcelain`
        empty: an untracked file is somebody's claim), and HEAD exactly
        origin/<br>'s tip, so the branch's whole state is on the remote --
        else the reason it cannot. Reads only."""
        code, st = self.run(["git", "-C", path, "status", "--porcelain"])
        if code or st.strip():
            return "it has uncommitted or untracked files" if not code else "its status cannot be read"
        self.run(["git", "fetch", "-q", "origin", br])
        here = self.run(["git", "-C", path, "rev-parse", "HEAD"])[1].strip()
        there = self.run(["git", "rev-parse", f"origin/{br}"])[1].strip()
        if not is_sha(here) or here != there:
            return f"its HEAD {here[:8]} is not origin/{br} {there[:8]} (unpushed work)"
        return None

    def free_holder(self, pr: int, wt: Path, br: str) -> None:
        """`--free-holders`: the recarry's `worktree add` failed; when the
        branch is held by a worktree `freeable` clears, detach that worktree
        (its files stay; `git -C <holder> switch <br>` restores it) and add
        again. Any other case raises today's HOLDER refusal, its reason
        appended."""
        holder = self.branch_holder(br)
        why = "--free-holders is off" if not self.free_holders else (
            "no worktree holds it" if holder is None else self.freeable(holder, br))
        if why is None and self.ok("git", "-C", holder, "checkout", "-q", "--detach") \
                and self.ok("git", "worktree", "add", "-q", "-B", br, str(wt), f"origin/{br}"):
            self.log(f"#{pr} recarry [HOLDER] freed: {holder} held {br}, clean at origin/{br}; "
                     f"detached it (restore: git -C {holder} switch {br})")
            return
        s = self.holder_refusal(wt, br)
        if s.cls and self.free_holders:
            s.why += f" -- not freed: {why or 'the detach or the second add failed'}"
        raise s

    @staticmethod
    def carried(item: dict, h: str) -> None:
        """The carry record: THIS invocation's recarry moved the head off <h>.
        `carried_from` is the first such head, `carried_chain` every one (a
        main-moved recovery recarries again), which the approval carry reads."""
        item.setdefault("carried_from", h)
        item.setdefault("carried_chain", []).append(h)

    def sweep_bots(self) -> None:
        """`--bot-prs`: merge the open record/autofix pull request NOW, in the
        train's own sequence, rather than let its CI beat merge it under a head
        the train has settled. The guard is record_row.py's own, the identical
        command the beat runs (`--automerge-check --require-green` at the head
        it judged), and the merge is pinned there by --match-head-commit; the
        ruleset still gates it (the approver App's review is the beat's to
        post). Nothing here stops the train: an unreadable lookup, a guard
        refusal (never merged), a pending check (left for the next sweep or
        the beat) and a merge GitHub refuses are logged as BOT lines."""
        if not (self.bot_prs and self.real):
            return
        rr = [sys.executable, "-I", str(ROOT / "tools/audit/seat/record_row.py"), "--repo", self.repo]
        if not os.environ.get("GH_TOKEN"):  # record_row reads its token from the env, never argv
            code, tok = self.run(["gh", "auth", "token"])
            if code or not tok.strip():
                self.log("BOT: no gh token to read the record pull request with; not swept")
                return
            os.environ["GH_TOKEN"] = tok.strip()
        code, o = self.run([*rr, "--find-open", "--owner", self.repo.split("/")[0]])
        n = (o.strip().splitlines() or [""])[-1].strip()
        if code or not n.isdigit():
            self.log(f"BOT: the open record pull request could not be looked up: {o.strip()[-160:]}")
            return
        if n == "0":
            return
        h = self.head(int(n))
        code, o = self.run([*rr, "--automerge-check", "--require-green", "--pr", n, "--head", h])
        last = (o.strip().splitlines() or ["(no output)"])[-1][:200]
        if code:
            self.log(f"BOT #{n} {'pending' if code == 3 else 'refused by the guard'} at {h[:8]}: {last}; not merged")
            return
        self.run(["gh", "pr", "merge", n, "--repo", self.repo, "--merge", "--match-head-commit", h])
        st = self.out("gh", "pr", "view", n, "--repo", self.repo, "--json", "state,mergeCommit",
                      "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
        self.log(f"BOT #{n} {st}" if st.startswith("MERGED") else f"BOT #{n} not merged at {h[:8]} ({st[:80]})")

    def carry_refusal(self, pr: int, verdict: str, h: str, o: str) -> Stop:
        """The `--carry` refusal, classified when its shape is the known one:
        the verdict sha is no longer an ancestor of the head (a bot push
        advanced the branch after the verdict) -- then the line carries the
        exact remedy and the delta the fresh verdict will re-read. Any other
        carry refusal is echoed exactly as today, unclassified."""
        if "is not an ancestor of" not in o:
            return Stop("carry", (o.strip().splitlines() or ["(no output)"])[-1][:200])
        self.run(["git", "fetch", "-q", "origin", verdict])
        code, d = self.run(["git", "diff", "--no-renames", "--name-only", verdict, h])
        names = d.split() if code == 0 else []
        delta = ", ".join(names[:12]) + (" ..." if len(names) > 12 else "") if names else "unreadable"
        return Stop("carry", f"#{pr} verdict {verdict[:12]} does not carry to head {h[:8]}: the branch moved "
                    f"after the verdict. Re-verdict at the live head {h[:8]}: the delta is {delta}",
                    cls=STALE_VERDICT_CARRY)

    def _check_runs(self, h: str) -> "list[dict] | None":
        """One paginated read of the check runs at <h>, parsed; None on a failed
        or unparseable read (wait_ci's fetch, shared with main_green's
        log-only overlap read)."""
        code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
                              f"repos/{self.repo}/commits/{h}/check-runs?per_page=100"])
        try:
            return [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else None
        except ValueError:
            return None

    @staticmethod
    def _by_name(runs: "list[dict]") -> dict:
        """The runs keyed by name, the latest started winning (wait_ci's order)."""
        last: dict[str, dict] = {}
        for c in sorted(runs, key=lambda c: c.get("started_at") or ""):
            last[c["name"]] = c
        return last

    def wait_ci(self, h: str, only: "list[str] | None" = None,
                beat: "str | None" = None) -> list[str]:
        """The names whose latest run at <h> is not green, once every run completed.

        Green is a fixed list -- success, skipped, neutral -- so a conclusion
        GitHub adds later, or `action_required` and `stale` today, reads red.
        With `only`, those names alone are waited for and judged, and each must
        have a run: a batch proof judges the required contexts (`required`).

        `beat` is the phrase after "waiting" in the heartbeat line (default
        "CI at <sha[:8]>"; a proof passes "proof <branch>"): every
        HEARTBEAT_SECONDS of elapsed wait one `beat:` line goes out through
        self.log, so a silent phase is distinguishable from a dead process
        (tvofi, 2026-10-13: two healthy trains killed after 2+ hours of
        silence). The beat is time-based -- computed from the wait's start
        against the poll clock -- never poll-based, so a poll cadence slower
        or faster than HEARTBEAT_SECONDS cannot hide it. Log only: no return
        value, gate or wait duration changes. One write rides the loop: while
        the wait goes on, the train-hold ref is refreshed before each sleep
        (`hold_refresh`), so a wait that runs to its `polls` ceiling still
        keeps the record beat held; a wait that settles writes nothing."""
        start = self.clock()
        due = start + HEARTBEAT_SECONDS
        what = beat or f"CI at {h[:8]}"
        for k in range(1, self.polls + 1):
            runs = self._check_runs(h)
            last = self._by_name(runs or ())
            if only is not None and runs is not None and all(
                    last.get(n, {}).get("status") == "completed" for n in only):
                return sorted(n for n in only if last[n]["conclusion"] not in GREEN)
            if only is None and runs and len(runs) >= self.min_runs and all(
                    c.get("status") == "completed" for c in runs):
                return sorted(n for n, c in last.items() if c["conclusion"] not in GREEN)
            now = self.clock()
            # A poll slower than the beat prints ONE beat, whose elapsed names
            # the true wait; a boundary-exact tick never prints twice.
            while now >= due:
                if only is not None:
                    req = len(only)
                    done = sum(last.get(n, {}).get("status") == "completed" for n in only)
                else:
                    req = len(runs or ())
                    done = sum(c.get("status") == "completed" for c in runs or ())
                self.log(f"beat: waiting {what} (poll {k}, t+{int(now - start)}s, "
                         f"required: {req}, concluded: {done}/{req})")
                due = now + HEARTBEAT_SECONDS
            # Sleep only until the next beat is due: POLL_SECONDS (300) behind
            # HEARTBEAT_SECONDS (240) held the first beat to the second poll,
            # t+305s (tvofi, 2026-10-14) -- a beat never waits on a poll.
            # Before the wait the hold is refreshed (R10-TRAIN-HOLD): a wait is
            # the longest silence a train has, so the beat's bound prices the
            # refresh gap, not a whole wait. Returning above (CI settled) costs
            # no write.
            self.hold_refresh()
            self.sleep(min(POLL_SECONDS, HEARTBEAT_SECONDS))
        return ["TIMEOUT"]

    def policy_paths(self, files: list[str]) -> list[str]:
        _pl = ROOT / ".claude/workflows/policy_lint.mjs"
        if not _pl.is_file():
            _pl = ROOT / "tools/policy/policy_lint.mjs"
        filt = ["node", str(_pl), "--corpus-filter"]
        probe = self.run(filt, stdin="CLAUDE.md\ntools/audit/not-a-policy-path.zzz\n")[1].split()
        if probe != ["CLAUDE.md"]:
            raise Stop("policy", "policy_lint.mjs --corpus-filter failed its sentinel probe, so what is policy is undefined here")
        return self.run(filt, stdin="".join(f + "\n" for f in files))[1].split()

    def _mandate_read(self, cid: int) -> "tuple[dict | None, list[dict]]":
        """The cited comment (None on GitHub's 404) and the tracking issue's
        comments since it was written, where a revocation would be --
        budget_raise_gate._mandate's routes, run through `self.run` so the
        self-test answers them and nothing here touches the remote elsewhere."""
        g = _mandate_gate()
        code, o = self.run(["gh", "api", f"repos/{self.repo}/issues/comments/{cid}"])
        if code:
            if "HTTP 404" in o:
                return None, []
            raise Stop("policy", f"mandate {cid} could not be read: " + o.strip()[-160:])
        comment = json.loads(o)
        if not str(comment.get("issue_url") or "").endswith(g.MANDATE_ISSUE_URL):
            return comment, []
        code, o = self.run(["gh", "api", "--paginate", "--slurp",
                            f"repos/{self.repo}/issues/{g.MANDATE_ISSUE}/comments"
                            f"?per_page=100&since={comment.get('created_at')}"])
        if code:
            raise Stop("policy", "the mandate thread could not be read: " + o.strip()[-160:])
        return comment, [c for page in json.loads(o) for c in page]

    def policy_gate(self, pr: int, h: str, files: list[str]) -> "str | None":
        """THE policy decision, ONE function so the run pass and the batch
        cannot drift (step 5; tvofi's ruling of 2026-10-09, #201 comment
        6083743563: the train lands policy under a valid mandate and falls
        back to refusing when there is none -- after the window closes the
        pre-mandate refusal returns with no code edit). A head changing no
        policy file (as `policy_paths` decides, sentinel probe unchanged)
        is not stopped. A head changing one lands only when BOTH hold, each
        re-read at the merge moment by the caller (`land`; batch admission
        calls this too, as an early refusal that costs no proof):

          1. the owner's APPROVED review sits at EXACTLY this head -- never
             a stale approval, the review is the substitute for the human
             the stop existed to keep in the loop; policy content that
             moved after the review is refused as that change, since the
             carry behaviour (a blob-identical bot commit, an automatic
             main merge) binds a verdict, not an owner's review of content;
          2. a mandate covering policy merging is in force AT THE MERGE,
             read by budget_raise_gate's own rules (mandate_state: the
             pinned owner's grammar comment on the tracking issue, its
             window open now, never edited, not revoked, scope `all`), and
             cited by id in that head's owner approval -- the citation is
             how the stop knows which mandate the owner pointed at, and it
             keeps the landing from reading as self-approval.

    Every refusal names which of these it found, and returns None; success
    returns the mandate's own line for the log."""
        pol = self.policy_paths(files)
        if not pol:
            return None
        head_pol = f"policy paths changed ({', '.join(pol)})"
        g = _mandate_gate()
        now = datetime.datetime.now(datetime.timezone.utc)
        at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        def merge_mandate(review, cid, comment, thread):
            return g.mandate_state(cid, comment, thread, now, at, "merge",
                                   g.MANDATE_COVERS_POLICY, "policy merging")
        read: dict = {}

        def mandate_fn(cid):
            if cid not in read:
                read[cid] = self._mandate_read(cid)
            return read[cid]
        try:
            code, o = self.run(["gh", "api", "--paginate", "--slurp",
                                f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
            if code:
                raise Stop("policy", head_pol + ": the reviews could not be read: " + o.strip()[-160:])
            reviews = [r for page in json.loads(o) for r in page]
            ok, why = g.approval(reviews, h, mandate_fn, merge_mandate)
            if not ok:
                raise Stop("policy", head_pol + ": " + (self._policy_move(h, pol, reviews) or why))
            cited = {int(a or b) for r in reviews
                     if g._is_owner(r.get("user")) and r.get("state") == "APPROVED"
                     and r.get("commit_id") == h
                     for a, b in g.MANDATE_CITE.findall(r.get("body") or "")}
            if not cited:
                raise Stop("policy", head_pol + ": the owner's approval at this head cites no mandate "
                           "id, and the train lands policy only under a mandate in force named by it")
            states = [merge_mandate(None, cid, *mandate_fn(cid)) for cid in sorted(cited)]
            live = next((why for w, why in states if w), None)
            if live is None:
                raise Stop("policy", head_pol + ": " + "; ".join(why for _, why in states))
            return live
        except Stop:
            raise
        except Exception as e:  # fail closed: an unread approval or mandate lands nothing
            raise Stop("policy", head_pol + f": the policy read failed "
                       f"({str(e).splitlines()[0][:160] if str(e) else type(e).__name__}); "
                       "an unread mandate grants nothing") from None

    def _policy_move(self, h: str, pol: list[str], reviews: list[dict]) -> str:
        """When the approval read refused, name whether the policy CONTENT
        moved after the owner's last approval: fetch the reviewed commit and
        diff it to the merge head. A moved policy file is the case the stop
        was written for -- fresh review or nothing. '' when the diff says
        otherwise or cannot be read: the caller then names approval()'s own
        refusal (a head moved only by blobs that did not touch policy is
        still 'not this head' -- the train does not re-review)."""
        g = _mandate_gate()
        last = next((r for r in reversed(reviews)
                     if g._is_owner(r.get("user")) and r.get("state") == "APPROVED"), None)
        c = str((last or {}).get("commit_id") or "")
        if not is_sha(c) or c == h or not self.ok("git", "fetch", "-q", "origin", c):
            return ""
        code, o = self.run(["git", "diff", "--no-renames", "--name-only", c, h])
        if code:
            return ""
        moved = [f for f in o.split() if f in pol]
        return (f"policy content changed after the owner's review at {c[:12]} "
                f"({', '.join(moved)}): a fresh owner review, not a carry") if moved else ""

    def _reviews(self, pr: int, what: str) -> list[dict]:
        code, o = self.run(["gh", "api", "--paginate", "--slurp",
                            f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
        if code:
            raise Stop("approve", f"the reviews could not be read for {what}: " + o.strip()[-160:])
        return [r for page in json.loads(o) for r in page]

    def _body(self, pr: int) -> str:
        """The pull request's body; an unreadable one stops (a raise's
        justification that cannot be read justifies nothing)."""
        code, o = self.run(["gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "body", "--jq", ".body"])
        if code:
            raise Stop("approve", "the body could not be read for the raise justification: " + o.strip()[-160:])
        return o

    def raise_hold(self, pr: int, h: str, files: "list[str]") -> "tuple[list[str], bool, str]":
        """(raises, held, why) for <pr> at <h>: the train's ONE reading of a
        budget raise, shared by `approve` and queue_pre_flight.py.

        The raises are budget_raise_gate's own `raises_between` from the merge
        base with origin/main -- the direction CI's budget-raise-gate reads,
        never a `*_budgets.json` path: a budget file that only gains rows
        (#2401) raises nothing, ([], True, why), and takes the ordinary
        approve path. A raise holds only under the owner's approval at <h> as
        the gate's `decide` judges it -- `approval` with the gate's own
        `justification` of the body, read on this branch alone -- its mandate
        judged AT THE MERGE rather than at the review's submission. GitHub
        re-anchors an approval's commit_id across a clean merge of the base
        (#2209: review 5526967770 names 8a8e66e7 in its body, the API reports
        the recarried 8876da3b), so after a recarry the owner's approval can
        already name the live head; it is the owner's there, and nothing is
        re-posted. `why` is the gate's own reason either way. A read that
        fails, or a budget path the diff names that neither tree holds, is a
        Stop: an unread budget is never a routine one."""
        g = _mandate_gate()
        if not any(f.endswith(g.SUFFIX) for f in files):
            return [], True, "no budget file changed"
        trees: dict[str, set[str]] = {}

        def read(argv: "list[str]") -> str:
            code, o = self.run(argv)
            if code:
                raise Stop("approve", f"the budget read failed ({' '.join(argv)[:80]}: {o.strip()[-160:]}); "
                           "an unread budget is never a routine one")
            return o

        def ls(sha: str) -> "list[str]":
            trees[sha] = set(read(["git", "ls-tree", "-r", "--name-only", sha]).splitlines())
            return sorted(trees[sha])

        def show(sha: str, path: str) -> "str | None":
            return read(["git", "show", f"{sha}:{path}"]) if path in trees[sha] else None
        base = read(["git", "merge-base", "origin/main", h]).strip()
        if not is_sha(base):
            raise Stop("approve", f"the budget read failed: the merge base reads '{base[:60]}'")
        try:
            _paths, raises = g.raises_between(base, h, ls, show)
        except Stop:
            raise
        except Exception as e:  # fail closed: a budget the gate cannot read raises everything
            raise Stop("approve", f"the budget read failed ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})") from None
        unseen = [f for f in files if f.endswith(g.SUFFIX) and not any(f in t for t in trees.values())]
        if unseen:
            raise Stop("approve", f"the budget read failed: the diff names {', '.join(unseen)}, which neither "
                       f"{base[:12]} nor {h[:12]} lists; an unread budget is never a routine one")
        if not raises:
            return [], True, "no budget raise (budget_raise_gate.raises_between: 0); the ordinary path"
        now = datetime.datetime.now(datetime.timezone.utc)
        at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            ok, why = g.approval(self._reviews(pr, "the owner's approval"), h, self._mandate_read,
                                 lambda _r, cid, c, t: g.mandate_state(cid, c, t, now, at, "merge"),
                                 justify=lambda: g.justification(self._body(pr)))
        except Stop:
            raise
        except Exception as e:  # fail closed: an unread approval is none
            raise Stop("approve", f"the owner-approval read failed ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__})") from None
        head = f"{len(raises)} budget raise(s), first {raises[0]}"
        return raises, ok, (f"{head}: {why}" if ok else f"{head}: a raise is the owner's (0013): {why}")

    def _owner_approval_at(self, pr: int, shas: "list[str]") -> "tuple[dict | None, int | None]":
        """The owner's latest APPROVED review when it names one of <shas>
        exactly and its body cites exactly one mandate comment -- (review,
        cited id); else (None, None). A review citing no mandate, two mandates
        (one does not decide, the gate's own rule), or sitting on another
        commit qualifies for nothing."""
        g = _mandate_gate()
        reviews = self._reviews(pr, "the carry")
        prior = next((r for r in reversed(reviews)
                      if g._is_owner(r.get("user")) and r.get("state") == "APPROVED"), None)
        if prior is None or prior.get("commit_id") not in shas:
            return None, None
        cited = {int(a or b) for a, b in g.MANDATE_CITE.findall(prior.get("body") or "")}
        return (prior, cited.pop()) if len(cited) == 1 else (None, None)

    def _post_carry(self, pr: int, h: str, body: str) -> str:
        """Post <body> as an approval at <h> and READ IT BACK: the newest review
        at <h> must carry this body byte-for-byte, or the post is a Stop, not a
        pass -- a carried approval nobody can read back approves nothing."""
        bf = self.state / f"carry{pr}.md"
        bf.write_text(body)
        if self.head(pr) != h:
            raise Stop("approve", "head moved before the carried approval")
        code, o = self.run(["gh", "pr", "review", str(pr), "--repo", self.repo, "--approve",
                            "--body-file", str(bf)])
        if code:
            raise Stop("approve", "the carried review was refused: " + o[-200:])
        try:
            code, o = self.run(["gh", "api", "--paginate", "--slurp",
                                f"repos/{self.repo}/pulls/{pr}/reviews?per_page=100"])
            back = [r for page in json.loads(o) for r in page] if code == 0 else []
        except ValueError:
            back = []
        if not any(r.get("state") == "APPROVED" and r.get("commit_id") == h
                   and (r.get("body") or "") == body for r in back):
            raise Stop("approve", "the carried approval did not read back byte-identical; "
                       "a failed read-back is a Stop, not a pass")
        return "carry"

    def _carry_owner_approval(self, pr: int, h: str, item: dict, files: list[str]) -> "str | None":
        """`--approval-carry`: a clean recarry moved the head h0 -> h under an
        owner approval that still names h0; re-post that approval at h. None
        means NO carry and the caller stops exactly as today. Every condition
        is the owner's (2026-10-12): the recarry of THIS invocation moved the
        head; the h0..h delta names no branch-own file (a conflict resolution
        is branch-own by definition and re-reviews); the owner's latest
        APPROVED review sits at h0 citing one mandate; and that mandate is
        RE-READ in force at the merge moment -- `self.mandate_read` here, never
        an admission's cached answer, `mandate_state`'s own rules. h0 is any
        head this invocation's recarries moved through (`carried_chain`: a
        main-moved recovery recarries more than once), the one the approval
        names; the delta is read from it."""
        if not self.approval_carry or not self.mandate:
            return None
        chain = [c for c in item.get("carried_chain") or [item.get("carried_from")] if is_sha(c or "") and c != h]
        if not chain:
            return None
        try:
            prior, cid = self._owner_approval_at(pr, chain)
            if prior is None:
                return None
            h0 = prior["commit_id"]
            code, out = self.run(["git", "diff", "--no-renames", "--name-only", h0, h])
            if code:
                raise Stop("approve", f"the recarry delta {h0[:12]}..{h[:12]} could not be "
                           "read: " + out.strip()[-160:])
            if [f for f in out.split() if f in files]:
                return None  # a branch-own file moved: a resolution, and a resolution re-reviews
            g = _mandate_gate()
            now = datetime.datetime.now(datetime.timezone.utc)
            comment, thread = self._mandate_read(cid)  # fresh, at the merge: never admission's read
            live, _why = g.mandate_state(cid, comment, thread, now,
                                         now.strftime("%Y-%m-%dT%H:%M:%SZ"), "merge")
            if not live:
                return None
        except Stop:
            raise
        except Exception as e:  # fail closed: an unread carry grants nothing
            raise Stop("approve", f"the carry read failed ({str(e).splitlines()[0][:160] if str(e) else type(e).__name__}); "
                       "an unread carry grants nothing") from None
        body = (str(prior.get("body") or "").rstrip()
                + f"\n\nCarried by the train's clean recarry from {h0} (delta: main's commits only); "
                  f"prior owner review {prior.get('id')}; "
                  f"mandate re-read in force at merge: {self.mandate}.\n")
        return self._post_carry(pr, h, body)

    def approve(self, pr: int, h: str, item: dict, files: list[str]) -> str:
        code, o = self.run(["bash", tool("app_approve"), self.repo, str(pr), h])
        if code == 0 and "REFUSE" not in o:
            return "app"
        # Only app_approve.sh's own code-owned refusal line, anchored and for this
        # pull request: a blocked verdict's echoed reason can carry the same words.
        owned = re.search(r"(?m)^app_approve: REFUSE: #%d touches code-owned paths \(([^)]*)\);" % pr, o)
        if owned is None:
            raise Stop("approve", "app_approve.sh refused: " + (o.splitlines() or ["(no output)"])[-1][:200])
        if not self.mandate:
            raise Stop("approve", f"code-owned ({owned.group(1).strip()}) and no --mandate given: the owner's review")
        raises, held, why = self.raise_hold(pr, h, files)
        if raises:
            if held:
                self.log(f"#{pr} the owner's approval is at the head: {why}")
                return "owner"
            carried = self._carry_owner_approval(pr, h, item, files)
            if carried is None:
                raise Stop("approve", f"code-owned and {why}")
            return carried
        paths = ", ".join(f"`{p}`" for p in owned.group(1).split())
        body = (f"Agent approval for code-owned {paths}, given by {self.role} under {self.mandate}, at head {h}.\n\n"
                f"Basis: `Fix review: merge {item['verdict']}` (comment {item.get('verdict_comment', '?')}), carried to {h} "
                f"by `app_approve.sh --carry` (automatic main merges only). CI at {h} is green"
                + (f" apart from {', '.join('`%s`' % n for n in self.ignore)}, which grade main." if self.ignore else ".") + "\n")
        bf = self.state / f"approve{pr}.md"
        bf.write_text(body)
        if self.head(pr) != h:
            raise Stop("approve", "head moved before the mandate approval")
        code, o = self.run(["gh", "pr", "review", str(pr), "--repo", self.repo, "--approve", "--body-file", str(bf)])
        if code:
            raise Stop("approve", "the mandate review was refused: " + o[-200:])
        return "mandate"

    def recarry(self, item: dict) -> str:
        """Step 1: the pull request's head, with `origin/main` merged in by
        `remerge_main.sh` when the head does not contain it (pushed by
        `app_push.sh --recarry`, whose prepr line is logged). A conflict or a
        push that did not land stops the train. The recarry worktree is the
        pull request's BRANCH checked out at `origin/<branch>` (-B, so an
        existing local branch is reset), never a detached HEAD:
        `app_push.sh` pushes only a committed tip, and a detached auto-merge
        sha is not the committed tip of anything (#1943)."""
        pr, v = int(item["pr"]), item["verdict"]
        if not is_sha(v):
            raise Stop("queue", f"verdict '{v}' is not a 40-hex sha")
        self.sweep_bots()  # a record PR merged now is inside this recarry, not under it
        h = self.head(pr)
        if not is_sha(h):
            raise Stop("head", f"could not read the head: {h[:120]}")
        if not self.contains_main(h):
            self.hold_refresh()  # a recarry is 5-15 min in app_push's prepr; --overlap's up-front loop is not a wait
            br = item.get("branch") or self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "headRefName", "--jq", ".headRefName")
            wt = Path(item.get("worktree") or self.state / "wt" / str(pr))
            if not wt.exists():
                self.run(["git", "fetch", "-q", "origin", br])
                # The worktree must hold the pull request's BRANCH, not a
                # detached HEAD: remerge_main.sh's app_push pushes only a
                # committed tip (HEAD == refs/heads/<branch>), and a detached
                # auto-merge sha is nobody's committed tip -- #1893, #1894,
                # #1896 all stopped there. -B, not -b: the orchestrator's
                # checkout often already holds the branch, and the recarry
                # wants it reset to origin's state before the merge.
                if not self.ok("git", "worktree", "add", "-q", "-B", br, str(wt), f"origin/{br}"):
                    self.free_holder(pr, wt, br)
                if not item.get("worktree"):
                    self.made_wts.append(wt)
            body = self.state / f"rb{pr}.md"
            body.write_text(self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "body", "--jq", ".body") + "\n")
            # The recarry itself takes 5-15 min inside app_push's prepr and logs
            # only on completion; this line makes it visible mid-flight.
            self.log(f"#{pr} recarry START (branch {br})")
            code, o = self.run(["bash", tool("remerge_main"), str(pr), str(wt), br, str(body)])
            if "MERGE CONFLICT" in o:
                raise Stop("recarry", "main does not merge without a resolution; that is a fixer's, and a re-review")
            if "PUSHED" not in o:
                # R9-RC-RECARRY-READBACK: app_push.sh --recarry confirms a race
                # inside its own bounded read-back, so no PUSHED here is a real
                # refusal -- OR a lag that outran app_push's budget (rare, but
                # the cost of a false stop is the whole pass: #2071 died here and
                # took four other verdicted pull requests, rc=1). Re-read the
                # head ONCE after a settle before declaring a stop: the recarry
                # moves the head, so a head that is no longer the pre-recarry h
                # proves the push landed despite the refusal. Nothing is proved
                # by the moved head EXCEPT that the branch advanced, which is the
                # only question a recarry refusal leaves open.
                self.sleep(RECARRY_RESETTLE)
                moved = self.head(pr)
                if not (is_sha(moved) and moved != h):
                    # The refusal is several lines (each prepr step, then
                    # app_push's die). The last 200 characters were only the die.
                    raise Stop("recarry", "the main merge pushed nothing: " + o.strip()[-2000:])
                self.carried(item, h)
                h = moved
                self.log(f"#{pr} recarry: app_push refused but the head moved to {h[:8]}; the push landed, not a stop")
            else:
                self.carried(item, h)
                h = self.head(pr)
            # app_push.sh --recarry's one line: prepr SKIPPED or RUNS, and why.
            path = next((ln.strip() for ln in o.splitlines() if "RECARRY:" in ln), "no RECARRY line")
            self.log(f"#{pr} recarry: main merged, head {h[:8]}; {path}")
        bot = self.bot_tip(h)  # after any recarry: the App push it makes cures a bot head
        if bot:
            raise self.bot_refusal(pr, h, bot)
        return h

    def one(self, item: dict, req: "list[str] | None" = None) -> None:
        self.hold_refresh()  # per item: a long item must not age the hold stale
        req = req if req is not None else self.required()
        self.serial(item, self.recarry(item), None, req)

    def serial(self, item: dict, h: str, rb: "str | None", req: "list[str] | None") -> None:
        """`at_head`, recovering a MainMoved up to --main-moved-tries times: a
        foreign merge moved main under the settled head (step 4, or the guard
        before a merge), so the entry is re-carried onto the new main and every
        step from the CI wait on runs again at the new head -- the carry, the
        approval and --match-head-commit all re-read there. Past the bound, the
        stop is today's."""
        for n in range(self.main_moved_tries + 1):
            try:
                return self.at_head(item, h, rb, req)
            except MainMoved as s:
                if n == self.main_moved_tries:
                    if n:
                        s.why += f" ({n} recarr{'y' if n == 1 else 'ies'} onto a moved main spent: --main-moved-tries)"
                    raise
                self.log(f"#{item['pr']} [MAIN-MOVED] {s.step}: {s.why}; recarry "
                         f"{n + 1}/{self.main_moved_tries} onto the new main, then CI again")
                h, rb = self.recarry(item), None

    def one_overlap(self, item: dict, req: "list[str] | None") -> None:
        """`--overlap`'s serial step for one entry: its head was re-carried UP
        FRONT (a dropped entry, routed only by the proof, re-carries here at
        its turn), so its pull_request runs fired with the others' and this
        waits only for ITS required contexts. The queue's order holds: the
        caller lands entries one at a time, an earlier still-pending entry
        never jumped by a later eligible one."""
        h = item.get("rc_head") or self.recarry(item)
        self.serial(item, h, item.get("rc_base"), req)

    def at_head(self, item: dict, h: str, rb: "str | None", req: "list[str] | None") -> None:
        """Steps 2-7 at a settled head: wait its CI, carry the verdict, land
        it. `rb` None is today's serial guard (the head contains main). `rb`
        set (--overlap, recarried up front onto `rb`): the merge's guard is
        that main advanced only by this batch's own merges -- every earlier
        entry landed onto a main descending from `rb`, so an `rb` that is no
        longer main's ancestor is a change nobody graded. The file list is the
        three-dot diff either way: a head recarried up front meets current
        main exactly at `rb`, its merge-base."""
        # R9-ADMIT-REQ: the head wait judges the ruleset's required contexts
        # only, as admission and settle/proof do -- a non-required lane (e.g.
        # the 180-min composed-proof) must never hold a landing whose
        # required set is green.
        red = [n for n in self.wait_ci(h, only=req) if n not in self.ignore]
        self.log(f"#{item['pr']} {h[:8]} ci red={red}")
        if red:
            raise Stop("ci", "red at the head: " + ", ".join(red))
        self.run(["git", "fetch", "-q", "origin", h])
        o = self.run(["bash", tool("app_approve"), "--carry", item["verdict"], h])[1]
        if "CARRY: yes" not in o:
            raise self.carry_refusal(item["pr"], item["verdict"], h, o)
        if rb is None and not self.contains_main(h):
            raise MainMoved("main", "origin/main moved during CI and is not in the head; run the train again")
        code, base = self.run(["git", "merge-base", "origin/main", h])
        if code or not is_sha(base.strip()):
            raise Stop("files", "git merge-base failed: " + base.strip()[-160:])
        # --no-renames: a rename lists both paths, so moving a policy file out of
        # the corpus still names the policy path it left.
        code, out = self.run(["git", "diff", "--no-renames", "--name-only", base.strip(), h])
        if code:
            raise Stop("files", "git diff failed: " + out.strip()[-160:])
        files = out.split()
        row = f"{ROW_DIR}/{item['pr']}.md"
        if row not in files:
            raise Stop("row", f"#{item['pr']} has no {row} in the three-dot diff; "
                       "the train writes none and the stamp's --require-rows "
                       "bar refuses an unrowed merge. Remedy: add the row on-branch "
                       "(moves the head: fresh verdict owed) or a separate row PR "
                       "(2158-pattern)", cls=ROW_MISSING)
        def guard() -> None:
            if rb is not None:
                self.run(["git", "fetch", "-q", "origin", "main"])
                if not self.ok("git", "merge-base", "--is-ancestor", rb, "origin/main"):
                    raise MainMoved("merge", "origin/main moved outside this batch before the merge; run the train again")
                return
            if not self.contains_main(h):
                raise MainMoved("merge", "origin/main moved before the merge; run the train again")
        try:
            self.land(item["pr"], h, item, files, guard)
        except MainMoved:
            raise
        except Stop as s:
            # Serial only (a batch's proved heads never contain main): every
            # attempt refused AND main has moved past the head -- the #2290
            # shape, recarried up front onto a main the batch's own merges
            # then moved -- is answered by a recarry, not a stop.
            if s.step == "merge" and s.why.startswith("not merged after") and not self.contains_main(h):
                raise MainMoved("merge", s.why + "; origin/main has moved past the head") from None
            raise

    def land(self, pr: int, h: str, item: dict, files: list[str], guard) -> str:
        """Approve, preflight and merge <pr> at <h>, `guard()` raising Stop before
        each attempt when the base is not where the merge expects it; the merge sha."""
        if self.head(pr) != h:
            raise Stop("approve", "head moved")
        if self.real:
            under = self.policy_gate(pr, h, files)  # step 5, re-read at the merge itself
            if under:
                self.log(f"#{pr} policy head lands under {under}")
            self.log(f"#{pr} approved ({self.approve(pr, h, item, files)})")
        self.run(["gh", "pr", "ready", str(pr), "--repo", self.repo])
        title = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "title", "--jq", ".title")
        pf = self.run(["bash", tool("preflight"), *map(str, item.get("issues", []))], stdin=title + "\n")[1]
        if re.search(r"(?m)^\s*REFUSE\b", pf) or not re.search(r"(?m)^\s*clean\b", pf):
            raise Stop("preflight", "the title did not pass preflight.sh: " + pf.strip()[-200:])
        said = "(no output)"
        for k in range(1, self.merge_tries + 1):
            self.sleep(30)
            guard()
            code, said = self.run(["gh", "pr", "merge", str(pr), "--repo", self.repo, "--merge",
                                   "--match-head-commit", h])
            said = " ".join(said.split())[-240:] or "(no output)"
            st = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "state,mergeCommit",
                          "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
            if st.startswith("MERGED"):
                self.log(f"#{pr} {st}")
                break
            # Every refusal is logged with GitHub's own words (train-b5, #2290:
            # eight silent attempts, "not merged" and no reason). One that says
            # the base moved is a MainMoved -- the recovery's to answer.
            self.log(f"#{pr} merge attempt {k}/{self.merge_tries} refused (rc={code}): {said}")
            if BASE_MOVED.search(said):
                raise MainMoved("merge", f"GitHub refused the merge because the base moved: {said}")
        else:
            raise Stop("merge", f"not merged after {self.merge_tries} attempts; the last refusal: {said}")
        owner, name = self.repo.split("/")
        q = ('query={repository(owner:"%s",name:"%s"){pullRequest(number:%d){closingIssuesReferences(first:10)'
             "{nodes{number state}}}}}" % (owner, name, pr))
        self.log(f"#{pr} closes {self.out('gh', 'api', 'graphql', '-f', q)[-160:]}")
        if self.real:
            self.run(["bash", tool("worktree_gc"), self.repo])
        return st.split()[-1]

    def release_worktrees(self) -> None:
        """Before the run's closing line (and again, a no-op, in `train`/`batch`'s
        finally), remove the recarry worktrees THIS run created under
        its state dir, so the next run's pre-flight does not find the train's
        own worktree holding a branch (train-b5, #2290: PARKed by
        ~/hpo-orch/train-b5/wt/2290). Never forced: one with changes stays,
        logged NOT released; a queue entry's own `worktree` is never touched."""
        for wt in self.made_wts:
            code, o = self.run(["git", "worktree", "remove", str(wt)])
            self.log(f"released {wt}" if code == 0 else
                     f"NOT released {wt} (rc={code}: {o.strip()[-160:]}); remove it by hand")
        self.made_wts = []

    def hold_refresh(self) -> None:
        """Publish, or refresh, the record-beat hold ref (R10-TRAIN-HOLD).

        The ref points at a commit made NOW, through the API and never a
        `git push`: its committer date is the publication time the record
        beat reads as the hold's age, and creating the ref through the API
        starts no push-triggered run. A failure is logged and the train runs
        on -- the pre-fix behaviour -- because the hold guards a bookkeeping
        beat, and stopping a merge train for it is the worse failure."""
        if not (self.real and self.hold_armed):
            return
        tip = self.out("git", "rev-parse", "origin/main")
        tree = self.out("git", "rev-parse", tip + "^{tree}") if is_sha(tip) else ""
        if not (is_sha(tip) and is_sha(tree)):
            self.held = False
            self.log(f"NOT held: origin/main is unreadable ({tip[:40]!r}); the record beat is not held")
            return
        code, said = self.run(
            ["gh", "api", "--method", "POST", f"repos/{self.repo}/git/commits",
             "--input", "-", "--jq", ".sha"],
            stdin=json.dumps({"message": f"train hold pid={os.getpid()}",
                              "tree": tree, "parents": [tip]}))
        sha = next((w for w in said.split() if is_sha(w)), "")  # not said.strip(): a gh warning may trail it
        if code or not is_sha(sha):
            self.held = False
            self.log(f"NOT held: the hold commit was refused (rc={code}: {said.strip()[-160:]})")
            return
        # A hold this run owns is a PATCH; the first one is a create, and a
        # stale ref a crashed train left is taken over by the PATCH fallback.
        method = "PATCH" if self.held else "POST"
        ref_url = (f"repos/{self.repo}/git/refs/heads/train-hold" if method == "PATCH"
                   else f"repos/{self.repo}/git/refs")
        payload = {"sha": sha, "force": True} if method == "PATCH" else {"ref": HOLD_REF, "sha": sha}
        code, said = self.run(["gh", "api", "--method", method, ref_url, "--input", "-"],
                              stdin=json.dumps(payload))
        if code and method == "POST":
            code, said = self.run(
                ["gh", "api", "--method", "PATCH", f"repos/{self.repo}/git/refs/heads/train-hold",
                 "--input", "-"], stdin=json.dumps({"sha": sha, "force": True}))
        if code:
            self.held = False
            self.log(f"NOT held: the hold ref was refused (rc={code}: {said.strip()[-160:]})")
            return
        self.held = True
        self.log(f"TRAIN HOLD {HOLD_REF} {sha[:8]}: the record beat waits")

    def hold_release(self) -> None:
        """Delete the hold ref at the closing line, so the record beat resumes.

        Idempotent: every closing path calls it, the last one finding the ref
        already gone. A refused delete is logged with the expiry that bounds
        the damage, never raised -- the train's merges have already landed."""
        if not self.held:
            return
        self.held = False
        code, said = self.run(["gh", "api", "--method", "DELETE",
                               f"repos/{self.repo}/git/refs/heads/train-hold"])
        self.log("TRAIN HOLD released" if not code else
                 f"NOT released: {HOLD_REF} stays (rc={code}: {said.strip()[-160:]}); "
                 "it expires at the beat's own bound, or delete it by hand")

    def train(self, queue: list[dict]) -> int:
        try:
            return self._train(queue)
        finally:
            self.release_worktrees()
            self.hold_release()

    def _train(self, queue: list[dict]) -> int:
        self.log(f"TRAIN pid={os.getpid()} queue={len(queue)} "
                 f"({' '.join('#%d' % int(i['pr']) for i in queue) or 'empty'})")
        self.state.mkdir(parents=True, exist_ok=True)
        self.hold_armed = True
        self.hold_refresh()  # before anything can merge: the record beat waits
        for item in self.preflight(queue):
            try:
                self.one(item)
            except Stop as s:
                self.release_worktrees()  # before the closing line, which stays last
                self.hold_release()
                self.log(f"TRAIN STOPPED #{item.get('pr')} {s.step}: {classified(s)}")
                return 1
        self.release_worktrees()
        self.hold_release()
        self.log("TRAIN DONE")
        return 1 if self.skipped else 0

    def preflight(self, queue: list[dict]) -> list[dict]:
        """`--pre-flight`: queue_pre_flight.py's admission reads over the whole
        queue before anything waits or merges; a PARK or FAIL entry is logged
        `PARK #<pr> <step>: <why>`, left out and reported in skipped.json
        (phase `pre-flight`) instead of stopping the train at its turn. The
        reads are the train's own methods on THIS train; the two the train now
        cures itself pass -- a bot tip (its recarry is the App push) and, under
        --free-holders, a holder `freeable` clears. A rehearsal reads none."""
        if not (self.pre_flight and self.real):
            return list(queue)
        sys.modules.setdefault("merge_train", sys.modules[__name__])  # one Stop class, not two
        if str(Path(__file__).resolve().parent) not in sys.path:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
        import queue_pre_flight
        pf = queue_pre_flight.PreFlight(self.repo, train=self, checkout=ROOT, bot_cured=True,
                                        free_holders=self.free_holders)
        keep = []
        for item in queue:
            status, step, why = pf.entry(item)
            if status == "PASS":
                keep.append(item)
                continue
            self.log(f"PARK #{item.get('pr')} {step}: {why}")
            self.skipped.append({"pr": item.get("pr"), "phase": "pre-flight", "reason": f"{step}: {why}"})
        (self.state / "skipped.json").write_text(json.dumps(self.skipped, indent=2) + "\n")
        self.log(f"PRE-FLIGHT: {len(keep)} of {len(queue)} admitted")
        return keep

    # ------------------------------------------------------------- the batch
    def git(self, *argv: str) -> str:
        code, o = self.run(["git", *argv])
        if code:
            raise Stop("git", f"git {' '.join(argv)[:80]}: {o.strip()[-160:]}")
        return o.strip()

    def tree(self, rev: str) -> str:
        return self.git("rev-parse", f"{rev}^{{tree}}")

    def required(self) -> list[str]:
        code, rid = self.run(["gh", "api", f"repos/{self.repo}/rulesets", "--jq",
                              f'.[] | select(.name == "{RULESET}") | .id'])
        code2, o = self.run(["gh", "api", f"repos/{self.repo}/rulesets/{rid.strip()}", "--jq",
                             '.rules[] | select(.type == "required_status_checks")'
                             ' | .parameters.required_status_checks[].context'])
        names = sorted({n.strip() for n in o.splitlines() if n.strip()} - set(PR_ONLY))
        if code or code2 or not rid.strip().isdigit() or not names:
            raise Stop("proof", f"could not read {RULESET}'s required contexts; no proof is judged against a guessed list")
        return names

    def admit(self, item: dict, base: str, graders: list[str], mf, req: list[str]) -> dict:
        """The pull request as a batch entry: its head, its own files, and the
        merge_fastpath classes that route it serial (empty: it joins the batch)."""
        pr, v = int(item["pr"]), item["verdict"]
        if not is_sha(v):
            raise Stop("queue", f"verdict '{v}' is not a 40-hex sha")
        h = self.head(pr)
        if not is_sha(h):
            raise Stop("head", f"could not read the head: {h[:120]}")
        target = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "baseRefName", "--jq", ".baseRefName")
        if target != self.base:
            raise Stop("base", f"#{pr} targets {target}, not {self.base}")
        # A GITHUB_TOKEN tip cannot join a proof (its pull_request runs are held,
        # so its required contexts may be ABSENT) but the SERIAL path cures it: its recarry at its
        # turn, once the batch's own merges moved main, is the App push. A head
        # still containing main then is refused there, as before.
        bot = self.bot_tip(h)
        self.run(["git", "fetch", "-q", "origin", h])
        files = self.git("diff", "--no-renames", "--name-only", self.git("merge-base", base, h), h).split()
        route = sorted({c for f in files if (c := mf.file_class(f, graders))} | ({BOT_ROUTE} if bot else set()))
        a = dict(item, pr=pr, head=h, files=files, route=route)
        if route:
            self.log(f"#{pr} serial: {', '.join(route)}")
            return a
        # R9-ADMIT-REQ: admission waits the ruleset's required contexts only,
        # as settle/proof already does -- a non-required lane (e.g. the 180-min
        # composed-proof) must never hold a batch whose required set is green.
        red = [n for n in self.wait_ci(h, only=req) if n not in self.ignore]
        if red:
            raise Stop("ci", f"#{pr} red at its head: " + ", ".join(red))
        if self.real:
            o = self.run(["bash", tool("app_approve"), "--carry", v, h])[1]
            if "CARRY: yes" not in o:
                s = self.carry_refusal(pr, v, h, o)
                if s.cls is None:  # the unclassified echo keeps today's `#<pr>` prefix
                    s.why = f"#{pr} {s.why}"
                raise s
            if f"{ROW_DIR}/{pr}.md" not in files:
                raise Stop("row", f"#{pr} has no {ROW_DIR}/{pr}.md in the three-dot diff. "
                           "Remedy: add the row on-branch (moves the head: fresh verdict "
                           "owed) or a separate row PR (2158-pattern)", cls=ROW_MISSING)
            under = self.policy_gate(pr, h, files)  # early refusal; land re-reads at the merge
            if under:
                self.log(f"#{pr} policy head admitted under {under}")
        self.log(f"#{pr} admitted at {h[:8]}")
        return a

    def build(self, base: str, entries: list[dict]) -> tuple[list[dict], list[str], list[dict]]:
        """Proof commits over <base>: P_i is the merge GitHub will make of P_(i-1)
        and entry i's head -- git's own text merge in place of every driver
        main's .gitattributes names, since GitHub runs none. An entry that does
        not merge cleanly onto the entries before it is returned to go serial,
        which covers every pairwise conflict and the three-way ones besides."""
        attrs = self.run(["git", "show", f"{base}:.gitattributes"])[1]
        drivers = [x for n in sorted(set(re.findall(r"\bmerge=([\w-]+)", attrs)))
                   for x in ("-c", f"merge.{n}.driver=git merge-file %A %O %B")]
        kept, proofs, conflicted, last = [], [], [], base
        for a in entries:
            code, o = self.run(["git", *drivers, "merge-tree", "--write-tree", last, a["head"]])
            if code == 1:
                self.log(f"#{a['pr']} serial: conflict onto {last[:8]}")
                conflicted.append(a)
                continue
            tree = o.split()[0] if o.split() else ""
            if code or not is_sha(tree):
                raise Stop("build", f"git merge-tree on #{a['pr']}: {o.strip()[-160:]}")
            last = self.git("commit-tree", tree, "-p", last, "-p", a["head"], "-m",
                            f"batch proof: #{a['pr']} at {a['head'][:12]} onto {last[:12]}")
            kept.append(a)
            proofs.append(last)
        return kept, proofs, conflicted

    def launch(self, branch: str, sha: str) -> None:
        """Push <sha> to <branch> as the App and dispatch every required context's workflow on it."""
        wt = self.state / "batch-wt"
        if wt.exists():
            self.git("-C", str(wt), "checkout", "-q", "-B", branch, sha)
        elif not self.ok("git", "worktree", "add", "-q", "-B", branch, str(wt), sha):
            raise Stop("proof", f"could not make the proof worktree at {wt}")
        o = self.run(["bash", tool("app_push"), "--branch-only", self.repo, str(wt), branch])[1]
        self.branches.append(branch)
        if "PUSHED" not in o:
            raise Stop("proof", f"the App did not push {branch}: {o.strip()[-300:]}")
        for wf, extra in DISPATCH:
            code, o = self.run(["gh", "workflow", "run", wf, "--repo", self.repo, "--ref", branch, *extra])
            if code:
                raise Stop("proof", f"dispatching {wf} on {branch} was refused: {o.strip()[-160:]}")
        self.log(f"proof {branch} at {sha[:8]}: pushed, {len(DISPATCH)} workflows dispatched")

    def culprit(self, sha: str, base: str, kept: list[dict], red: list[str]) -> int | None:
        """The one entry whose own files lie in the closure of every script the
        proof's failing jobs name, under main's table or the proof's; None when
        no script is named (a job with no script) or more than one entry owns them."""
        code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
                              f"repos/{self.repo}/commits/{sha}/check-runs?per_page=100"])
        runs = [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else []
        scripts: set[str] = set()
        for c in runs:
            if c.get("name") in red and c.get("conclusion") not in GREEN:
                # gh refuses a log carrying terminal escapes -- every Actions log
                # does -- unless told to pass them (measured on the R9-RO-12 proof).
                log = self.run(["gh", "api", "--allow-escape-sequences",
                                f"repos/{self.repo}/actions/jobs/{c['id']}/logs"])[1]
                scripts |= set(FAILED_SCRIPT.findall(log))
        if not scripts:
            return None
        unit = _fastpath().closure.unit_of
        tables = [json.loads(self.git("show", f"{rev}:tests/closures.json"))["closures"] for rev in (base, sha)]
        owners = {a["pr"] for a in kept for s in scripts for t in tables
                  if {unit(f) for f in a["files"]} & set(t.get(s, ()))}
        self.log(f"proof {sha[:8]} failing scripts {sorted(scripts)}, owned by {sorted(owners)}")
        return owners.pop() if len(owners) == 1 else None

    def settle(self, tag: str, base: str, kept: list[dict], req: list[str]) -> tuple[list[dict], list[str], list[dict]]:
        """The entries whose proof is green, their proofs, and the entries dropped
        to go serial. B: two or more are proved; D: one merges unproved."""
        dropped: list[dict] = []
        n = 0
        while True:
            kept, proofs, conflicted = self.build(base, kept)
            dropped += conflicted
            if len(kept) < 2:
                return kept, proofs, dropped
            n += 1
            branch = f"batch/{tag}-{n}"
            self.launch(branch, proofs[-1])
            red = self.wait_ci(proofs[-1], only=req, beat=f"proof {branch}")
            self.log(f"proof batch/{tag}-{n} {proofs[-1][:8]} red={red}")
            if "TIMEOUT" in red:
                raise Stop("proof", f"batch/{tag}-{n} never completed its required contexts; nothing merged")
            if not red:
                return kept, proofs, dropped
            pr = self.culprit(proofs[-1], base, kept, red)
            if pr is None and len(kept) == 2:
                pr = kept[1]["pr"]  # two sets of one: D merges the first unproved
            if pr is not None:
                self.log(f"#{pr} dropped to serial: the proof is red at {', '.join(red)}")
                dropped += [a for a in kept if a["pr"] == pr]
                kept = [a for a in kept if a["pr"] != pr]
                continue
            # Every all-but-one set, proved side by side; the green set dropping
            # the latest entry wins, so the queue's order keeps its priority.
            subs = []
            for a in kept:
                sub, p, c = self.build(base, [b for b in kept if b is not a])
                if not c and p:
                    n += 1
                    sbranch = f"batch/{tag}-{n}"
                    self.launch(sbranch, p[-1])
                    subs.append((a, sub, p, sbranch))
            green = [(a, sub, p) for a, sub, p, sbranch in subs
                     if not self.wait_ci(p[-1], only=req, beat=f"proof {sbranch}")]
            if not green:
                raise Stop("proof", f"red at {', '.join(red)} with every one of "
                           f"{', '.join('#%d' % a['pr'] for a in kept)} dropped; nothing merged: take them through run")
            a, sub, p = green[-1]
            self.log(f"#{a['pr']} dropped to serial: the set without it is green at {p[-1][:8]}")
            return sub, p, dropped + [a]

    def main_green(self, tip: str, req: list[str], why: str) -> None:
        """Stop unless every required context at the base's tip completed green.
        D's bound -- main's FULL push run, reverted first -- names one merge only
        on a base that was green under it; a proof is only red for its entries
        on such a base (review of #2044: a red main D-merged the wrong entry).
        Under `--overlap` the read is LOG-ONLY (the owner's P7 decision: do not
        wait on main's CI before a merge) -- a red base is logged, and the
        batch's own proofs and each head's own required contexts remain the
        gates that hold."""
        # R9-ADMIT-REQ: under --overlap the read is ONE pass, non-blocking --
        # the loop below would hold every batch through main's push-run window
        # (40-60 min measured) before admission, the wait the flag exists to
        # drop. The not-green names are logged and the batch starts.
        if self.overlap:
            last = self._by_name(self._check_runs(tip) or ())
            red = sorted(n for n in req if last.get(n, {}).get("conclusion") not in GREEN)
            if red:
                self.log(f"OVERLAP: {self.base} at {tip[:12]} is not green ({', '.join(red)}) {why}; "
                         "--overlap logs it and does not wait")
            return
        red = self.wait_ci(tip, only=req)
        if red:
            raise Stop("main", f"{self.base} at {tip[:12]} is not green ({', '.join(red)}) {why}; nothing more lands")

    def is_merged(self, pr: int) -> bool:
        """Whether GitHub already reports <pr> MERGED -- the post-merge test for
        `--skip-bad`: a Stop that arrives after the merge API call must never be
        answered by retrying the entry (the merge may already have landed)."""
        return self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "state,mergeCommit",
                        "--jq", '"\\(.state) \\(.mergeCommit.oid)"').startswith("MERGED")

    def skip(self, pr: int, phase: str, why: str, cls: "str | None" = None) -> None:
        """`--skip-bad`: record one skipped entry -- logged as
        `SKIP #<pr> <phase>: <reason>` (the reason echoed verbatim from the Stop
        that would otherwise have printed `TRAIN STOPPED`, its block class in
        brackets when the shape is a known one) and collected for skipped.json.
        A red main is never skippable: the caller re-raises it."""
        self.log(f"SKIP #{pr} {phase}: " + (f"[{cls}] {why}" if cls else why))
        row = {"pr": pr, "phase": phase, "reason": why}
        if cls:
            row["class"] = cls
        self.skipped.append(row)

    def skip_report(self, total: int) -> None:
        """`--skip-bad`'s closing report: the skipped list under the state dir
        and one line the orchestrator's tooling can grep."""
        (self.state / "skipped.json").write_text(json.dumps(self.skipped, indent=2) + "\n")
        self.log(f"SKIP REPORT: {len(self.skipped)} skipped of {total}")

    def batch(self, queue: list[dict], tag: str) -> int:
        try:
            return self._batch(queue, tag)
        finally:
            self.release_worktrees()
            self.hold_release()

    def _batch(self, queue: list[dict], tag: str) -> int:
        # The banner is the FIRST output, before any blocking call: a
        # daemonized launch is attributable from the log's first line even if
        # everything after it hangs (tvofi, 2026-10-14, tag traintest).
        self.log(f"BATCH {tag} pid={os.getpid()} base={self.base} queue={len(queue)} "
                 f"({' '.join('#%d' % int(i['pr']) for i in queue) or 'empty'})"
                 f"{' --overlap' if self.overlap else ''}{' --skip-bad' if self.skip_bad else ''}")
        self.state.mkdir(parents=True, exist_ok=True)
        self.hold_armed = True
        self.hold_refresh()  # before the sweep: the record beat waits for the batch
        self.branches: list[str] = []
        self.skipped: list[dict] = []
        try:
            mf = _fastpath()
            self.sweep_bots()  # before the base is read: a record PR merged now is under every proof
            self.run(["git", "fetch", "-q", "origin", self.base])
            base = self.git("rev-parse", f"origin/{self.base}")
            req = self.required()
            self.main_green(base, req, "before admission")
            admitted = self.preflight(queue)
            graders = mf.grader_specs(mf.workflow_texts(base, git=lambda *a: self.git(*a)))
            # --skip-bad stops at the ENTRY: an admission refusal (a red head, a
            # bot tip, a policy or budget refusal) skips that pull request, with
            # its reason echoed as printed today, and the rest are still
            # admitted. A red main stopped above, before any entry was read.
            entries = []
            for item in admitted:
                if not self.skip_bad:
                    entries.append(self.admit(item, base, graders, mf, req))
                    continue
                try:
                    entries.append(self.admit(item, base, graders, mf, req))
                except Stop as s:
                    if s.step == "main":
                        raise
                    self.skip(int(item["pr"]), s.step, s.why, s.cls)
            serial = [a for a in entries if a["route"]]
            # --overlap: re-carry every serial entry UP FRONT, before anything
            # merges, pushing each branch so all their pull_request runs fire
            # concurrently (the ruleset still waits on each head's own required
            # contexts at its recarry head; the flag overlaps that wait, it
            # cannot bypass it). Entries land later, one at a time, in queue
            # order (`one_overlap`).
            if self.overlap and serial:
                self.run(["git", "fetch", "-q", "origin", self.base])
                rb = self.git("rev-parse", f"origin/{self.base}")
                # A bot-routed head still contains main now; it recarries at its turn.
                todo = [a for a in serial if a["pr"] not in {s["pr"] for s in self.skipped}
                        and BOT_ROUTE not in a["route"]]
                self.log(f"OVERLAP: recarrying {', '.join('#%d' % a['pr'] for a in todo)} up front, "
                         "their pull_request runs fire together")
                for a in todo:
                    self.log(f"#{a['pr']} overlap: recarry start")
                    try:
                        a["rc_head"], a["rc_base"] = self.recarry(a), rb
                    except Stop as s:
                        if s.step == "main" or not self.skip_bad:
                            raise
                        self.skip(a["pr"], s.step, s.why, s.cls)
            kept, proofs, dropped = self.settle(tag, base, [a for a in entries if not a["route"]], req)
            lone = kept[0]["pr"] if len(kept) == 1 else None  # the unproved merge, by number
            if lone:
                self.log(f"#{kept[0]['pr']} D: a batch of one merges at its verdicted head, unproved; "
                         f"{self.base}'s FULL push run is its gate, and a red there is reverted first")
            prev, tip, first, moves, recover = base, base, True, 0, True
            todo = list(zip(kept, proofs))
            while todo:
                a, p = todo.pop(0)

                def guard(prev=prev, pr=a["pr"], first=first) -> None:
                    self.run(["git", "fetch", "-q", "origin", self.base])
                    now = self.git("rev-parse", f"origin/{self.base}")
                    if self.tree(now) != self.tree(prev):
                        raise MainMoved("merge", f"{self.base} moved: its tree is not the one #{pr}'s proof was built on; run the batch again")
                    # Later merges land on a tree this batch's own green proof graded.
                    if first:
                        self.main_green(now, req, f"right before #{pr}'s merge")
                # --skip-bad at the merge: a Stop is fatal for THIS entry only.
                # One that arrives after the merge API call is logged post-merge
                # and the entry is never retried -- the merge may already have
                # landed, and merging it again is not an option GitHub offers.
                # A red main (the guard's re-read) stays global.
                try:
                    self.land(a["pr"], a["head"], a, a["files"], guard)
                    self.run(["git", "fetch", "-q", "origin", self.base])
                    tip = self.git("rev-parse", f"origin/{self.base}")
                    if self.tree(tip) != self.tree(p):
                        raise Stop("tree", f"after #{a['pr']} {self.base} is {tip[:12]}, whose tree is not proof {p[:12]}'s; "
                                   "read that merge before anything else lands")
                    self.log(f"#{a['pr']} {self.base} {tip[:8]} tree == proof {p[:8]}")
                    prev, first = p, False
                except Stop as s:
                    # A FOREIGN merge (the batch's own leave main's tree equal
                    # to the proof's) moved main before this entry's merge: P_i
                    # were built on a main that is gone, so what is left is
                    # rebuilt and re-proved on the new one, its first merge
                    # re-reading main green -- never merged on the old proof.
                    # Not after a post-merge skip: that tree is the batch's own
                    # unexplained one, and nothing lands on it unread.
                    if isinstance(s, MainMoved) and recover and moves < self.main_moved_tries:
                        moves += 1
                        self.run(["git", "fetch", "-q", "origin", self.base])
                        prev = self.git("rev-parse", f"origin/{self.base}")
                        rest = [a] + [b for b, _ in todo]
                        self.log(f"[MAIN-MOVED] before #{a['pr']}'s merge: re-proving "
                                 f"{', '.join('#%d' % b['pr'] for b in rest)} on {prev[:8]} "
                                 f"({moves}/{self.main_moved_tries})")
                        k2, p2, d2 = self.settle(f"{tag}-m{moves}", prev, rest, req)
                        dropped += d2
                        if len(k2) == 1:
                            lone = k2[0]["pr"]
                            self.log(f"#{lone} D: alone after the re-proof, it merges unproved")
                        todo, first = list(zip(k2, p2)), True
                        continue
                    if isinstance(s, MainMoved) and moves:
                        s.why += f" ({moves} re-proof(s) on a moved main spent: --main-moved-tries)"
                    if not self.skip_bad or s.step == "main":
                        raise
                    phase = "post-merge" if self.is_merged(a["pr"]) else s.step
                    recover = recover and phase != "post-merge"
                    self.skip(a["pr"], phase, s.why, s.cls)
            order = {int(item["pr"]): i for i, item in enumerate(queue)}
            bad = {s["pr"] for s in self.skipped}
            later = sorted([a for a in serial + dropped if a["pr"] not in bad], key=lambda a: order[a["pr"]])
            if lone and later and self.real:
                # A red push run must point at one merge: the unproved one is graded alone.
                self.main_green(tip, req, f"after #{lone}'s unproved merge: revert it first")
            if later and not self.real:
                self.log(f"rehearsal: serial {', '.join('#%d' % a['pr'] for a in later)} not run")
            elif later:
                self.log(f"serial: {', '.join('#%d' % a['pr'] for a in later)}")
                for a in later:
                    try:
                        self.one_overlap(a, req) if self.overlap else self.one(a, req)
                    except Stop as s:
                        if s.step == "main" or not self.skip_bad:
                            raise Stop(s.step, f"#{a['pr']} {s.why}", cls=s.cls) from None
                        self.skip(a["pr"], "post-merge" if self.is_merged(a["pr"]) else s.step,
                                  f"#{a['pr']} {s.why}", s.cls)
        except Stop as s:
            self.release_worktrees()  # before the closing lines, which stay last
            self.hold_release()
            self.log(f"TRAIN STOPPED {s.step}: {classified(s)}")
            if self.skip_bad:
                self.skip_report(len(queue))
            return 1
        self.release_worktrees()
        if self.branches:  # the proofs are spent; their shas are in the log above
            code, out = self.run(["git", "push", "-q", "origin", "--delete", *self.branches])
            names = ", ".join(self.branches)
            self.log(f"deleted {names}" if code == 0 else
                     f"NOT deleted {names} (rc={code}: {out.strip()[-160:]}); the merges stand, delete them by hand")
        if self.skip_bad:
            self.skip_report(len(queue))
        self.hold_release()
        self.log("TRAIN DONE")
        return 1 if self.skipped else 0


# ----------------------------------------------------------------- self-test
def _self_test() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_env, throwaway_git_init
    passed = failed = 0
    H0, H1, H2, V = "a" * 40, "b" * 40, "9" * 39 + "a", "c" * 40
    BOT_SUBJ = "ci: pin killed mutants"

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")


    def fake(world: dict):
        calls: list[list[str]] = []

        def run(argv, cwd=ROOT, stdin=None):
            calls.append(argv)
            a = " ".join(argv)
            if argv[:2] == ["git", "ls-tree"] and world.get("ls_fail"):
                return 128, "fatal: not a tree object"
            if argv[:2] == ["git", "show"] and world.get("show_fail") and argv[2].endswith("_budgets.json"):
                return 128, "fatal: unable to read 0123abcd"
            got = budget_fixture(world.get("budgets"), argv, world.get("base", (0, "e" * 40 + "\n"))[1].strip())
            if got is not None:
                return got
            if "record_row.py" in a:  # --bot-prs: the record PR lookup and its guard
                if "--find-open" in argv:
                    return world.get("bot_find", (0, "0"))
                world.setdefault("bot_guarded", []).append(argv[argv.index("--head") + 1])
                return world.get("bot_guard", (0, "AUTOMERGE OK #9"))
            # THE RECORD-BEAT HOLD (issue #2302): the commit the hold ref points
            # at, and the ref create/update. `hold_sha` empty (the default) is
            # the API refusing, which the train must survive.
            if argv[:2] == ["gh", "api"] and "/git/commits" in a:
                world.setdefault("hold_commits", []).append(json.loads(stdin or "{}"))
                return world.get("hold_commit", (0, world.get("hold_sha", "")))
            if argv[:2] == ["gh", "api"] and "/git/refs" in a:
                world.setdefault("hold_refs", []).append(argv)
                if "/git/refs/heads/train-hold" in a:  # PATCH or DELETE an existing ref
                    return world.get("hold_update", (0, "{}"))
                return world.get("hold_create", (0, "{}"))
            if argv[:3] == ["gh", "auth", "token"]:
                return 0, "tok"
            if argv[:3] == ["gh", "pr", "view"] and argv[3] == "9":  # the record PR
                return 0, ("e" * 40 if "headRefOid" in a else
                           "MERGED " + "9" * 40 if 9 in world.get("bot_merged", ()) else "OPEN None")
            if argv[:3] == ["gh", "pr", "merge"] and argv[3] == "9":
                world.setdefault("bot_merged", []).append(9)
                return 0, ""
            if argv[:3] == ["gh", "pr", "view"] and "--json" in argv and argv[argv.index("--json") + 1] == "body":
                return 0, world.get("pr_body", "")
            if argv[:3] == ["gh", "pr", "merge"] and world.get("merge_outs"):
                return world["merge_outs"].pop(0)
            if argv[:3] == ["gh", "pr", "view"] and "state,headRefOid" in a:  # pre-flight's read
                return 0, json.dumps({"state": "OPEN", "headRefOid": world["heads"][0],
                                      "headRefName": "fix/x"})
            if argv[:2] == ["git", "show"]:  # pre-flight's row status read
                return 0, world.get("row_text", "- [#7](https://example.test/7) — **open**, t")
            if argv[:3] == ["gh", "pr", "view"] and "headRefOid" in a:
                h = world["heads"].pop(0) if len(world["heads"]) > 1 else world["heads"][0]
                world["_last_head"] = h
                return 0, h
            if "merge-base --is-ancestor" in a:
                return (0 if world["contains"].pop(0) else 1) if world["contains"] else 0, ""
            if "remerge_main.sh" in a:
                return 0, world.get("remerge", "PUSHED")
            if "check-runs" in a:
                # `pending_reads`: the first N reads report in_progress, so a
                # wait that outlives one poll can be driven without a clock.
                reads = world["ci_reads"] = world.get("ci_reads", 0) + 1
                runs = world.get("runs", [])
                if reads <= world.get("pending_reads", 0):
                    runs = [dict(c, status="in_progress") for c in runs]
                return 0, "\n".join(json.dumps(c) for c in runs)
            if argv[:2] == ["gh", "api"] and "/commits/" in a:  # bot_tip's read, post-jq
                sha = a.split("/commits/")[1].split()[0].split("?")[0].split("/")[0]
                subj = world.get("bot_tips", {}).get(sha)
                return 0, f"{'github-actions[bot]' if subj else 'tvofi'}\t{subj or 'fix: x'}"
            if argv[:3] == ["git", "rev-parse", "origin/main"]:  # the hold's parent
                return 0, world.get("main_tip", "d" * 40)
            if argv[:2] == ["git", "rev-parse"] and argv[2].endswith("^{tree}"):
                return 0, world.get("main_tree", "e" * 40)
            if argv[:3] == ["git", "merge-base", "origin/main"]:
                return world.get("base", (0, "e" * 40 + "\n"))
            if argv[:2] == ["git", "diff"] and len(argv) > 4 and argv[4] == world.get("reviewed"):
                return 0, "\n".join(world.get("content_diff", []))
            if argv[:2] == ["git", "diff"] and world.get("carry_delta") \
                    and argv[4:6] == list(world["carry_delta"][:2]):
                return 0, world["carry_delta"][2]  # the recarry's h0..h tree delta
            if "--carry" in a:
                return 0, world.get("carry", "CARRY: yes")
            if argv[:2] == ["git", "diff"]:
                if "diff_fail" in world:
                    return world["diff_fail"]
                if "renamed" in world:  # git lists a rename's old path only with --no-renames
                    old, new = world["renamed"]
                    names = f"{old}\n{new}" if "--no-renames" in argv else new
                    return 0, names + f"\n{ROW_DIR}/7.md"
                return 0, "\n".join(world.get(
                    "files",
                    ["custom_components/x.py", f"{ROW_DIR}/7.md",
                     f"{ROW_DIR}/8.md"]))
            if "--corpus-filter" in a:
                if world.get("broken_filter"):
                    return 0, ""
                return 0, "\n".join(f for f in (stdin or "").split() if f in ("CLAUDE.md", "AGENTS.md", "dev/governance/roles/fixer.md"))
            if argv[:2] == ["gh", "api"] and "/pulls/" in a and "/reviews" in a:
                return 0, json.dumps([world.get("reviews", [])])
            if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                return (0, json.dumps(world["mandate"])) if world.get("mandate") \
                    else (1, "gh: Not Found (HTTP 404)")
            if argv[:2] == ["gh", "api"] and "/issues/201/comments" in a:
                return 0, json.dumps([world.get("thread", [])])
            if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
                return (0, "7") if world.get("required", "fast\n") else (1, "HTTP 404")
            if "rulesets/7" in a:
                return 0, world.get("required", "fast\n")
            if "app_approve.sh" in a:
                return world.get("approve", (0, "APPROVED"))
            if argv[:3] == ["gh", "pr", "review"]:
                # What GitHub would hold after the post: the next reviews read
                # returns it -- unless the read-back is meant to fail.
                if "--approve" in argv and not world.get("drop_posted"):
                    world.setdefault("reviews", []).append(
                        {"user": {"login": "orchestrator", "id": 1, "type": "User"},
                         "state": "APPROVED", "commit_id": world.get("_last_head", H0),
                         "body": Path(argv[argv.index("--body-file") + 1]).read_text(), "id": 987654321})
                return 0, "reviewed"
            if "preflight.sh" in a:
                return 0, world.get("preflight", "  clean    no refusal")
            if "state,mergeCommit" in a:
                return 0, world["merge"].pop(0) if world.get("merge") else "MERGED " + "d" * 40
            if argv[:2] == ["gh", "api"] and re.search(r"/issues/\d+/comments", a):  # pre-flight's findings read
                return 0, json.dumps([world.get("verdict_comments", [])])
            return 0, ""
        return run, calls

    green = [{"name": "fast", "status": "completed", "conclusion": "success", "started_at": "1"},
             {"name": "nightly-status", "status": "completed", "conclusion": "failure", "started_at": "1"}]
    item = {"pr": 7, "verdict": V, "verdict_comment": "42", "worktree": "/nonexistent-wt", "branch": "fix/x"}

    def go(world: dict, mandate: str | None = None, q=None, min_runs: int = 1,
           wrap=None, approval_carry: bool = False, base: str = "main",
           **opts) -> tuple[int, list[str], list[list[str]]]:
        world.setdefault("heads", [H0])
        world.setdefault("contains", [])
        world.setdefault("runs", green)
        lines: list[str] = []
        timeline: list[tuple[str, str]] = []  # calls and log lines, in order
        run, calls = fake(world)
        if wrap:
            run = wrap(run)
        base_run = run

        def run_traced(argv, cwd=ROOT, stdin=None):
            timeline.append(("call", " ".join(argv)))
            return base_run(argv, cwd=cwd, stdin=stdin)

        def logline(s: str) -> None:
            lines.append(s)
            timeline.append(("log", s))

        with tempfile.TemporaryDirectory() as d:
            rc = Train("o/r", Path(d), mandate, "the orchestrator", ("nightly-status",), min_runs,
                       run=run_traced, sleep=lambda s: None, log=logline, polls=2, merge_tries=3,
                       approval_carry=approval_carry, base=base, **opts).train(q or [dict(item)])
            for key, name in (("approve_body", "approve7.md"), ("carry_body", "carry7.md")):
                f = Path(d) / name
                world[key] = f.read_text() if f.exists() else ""
        world["timeline"] = timeline
        return rc, lines, calls

    def merged(calls) -> bool:
        return any(c[:3] == ["gh", "pr", "merge"] for c in calls)

    def approved(calls) -> bool:
        return any(c[:3] == ["gh", "pr", "review"] for c in calls)

    rc, lines, calls = go({})
    check("a green, carried, non-policy pull request merges (null control)", rc == 0 and merged(calls) and lines[-1] == "TRAIN DONE")
    check("a wait that settles on its first poll beats nothing (heartbeat null control)",
          not any(ln.startswith("beat:") for ln in lines))
    rc, lines, calls = go({"files": ["custom_components/x.py"]})
    check(f"a pull request with no {ROW_DIR}/<N>.md row is refused",
          rc == 1 and "row:" in lines[-1] and f"{ROW_DIR}/7.md" in lines[-1]
          and not merged(calls))
    check("the row refusal is self-describing: class ROW-MISSING and both remedies in the line",
          "[ROW-MISSING]" in lines[-1] and "add the row on-branch" in lines[-1]
          and "2158-pattern" in lines[-1])
    check("nightly-status red is ignored by default", "red=[]" in " ".join(lines))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"}]})
    check("a red required check stops the train before any approval", rc == 1 and "ci:" in lines[-1] and not merged(calls)
          and not any("app_approve.sh" in " ".join(c) and "--carry" not in c for c in calls))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"},
                                    {"name": "fast", "status": "completed", "conclusion": "success", "started_at": "2"}]})
    check("a re-run that went green supersedes the earlier red", rc == 0 and merged(calls))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "in_progress", "conclusion": None, "started_at": "1"}]})
    check("CI that never completes stops it as TIMEOUT", rc == 1 and "TIMEOUT" in lines[-1])
    # THE HEARTBEAT (tvofi, 2026-10-13): two healthy trains were killed after
    # 2+ hours of silence in wait_ci and the overlap recarry phase. One beat
    # line per HEARTBEAT_SECONDS of ELAPSED wait -- time-based against the
    # stubbed clock, never poll-based, so a poll cadence off the beat cadence
    # still beats exactly on time.
    hang = [{"name": "fast", "status": "in_progress", "conclusion": None, "started_at": "1"}]
    def hung_run(argv, cwd=ROOT, stdin=None):
        # The pair wraps the whole conditional: `return 0, X if c else (0, "")`
        # made a non-check-runs call answer `(0, (0, ""))`, a tuple where the
        # trainer reads a string (found by the R10-TRAIN-HOLD session/arming
        # mutant, which is the only reader to reach it).
        return (0, "\n".join(json.dumps(c) for c in hang)) if "check-runs" in " ".join(argv) else (0, "")
    ticks = iter([0, 100, 240, 300, 480, 700, 960, 1100])
    lines: list[str] = []
    with tempfile.TemporaryDirectory() as d:
        t = Train("o/r", Path(d), None, "", (), 1, run=hung_run, sleep=lambda s: None,
                  log=lines.append, polls=7, clock=lambda: next(ticks))
        red = t.wait_ci(H0)
    beats = [ln for ln in lines if ln.startswith("beat:")]
    check("the heartbeat beats once per HEARTBEAT_SECONDS of elapsed wait, not per poll "
          "(clock jumps 100/240/300/480/700/960: beats at t+240, t+480, t+960), and the "
          "wait still times out exactly as before",
          red == ["TIMEOUT"] and len(beats) == 3
          and beats[0] == f"beat: waiting CI at {H0[:8]} (poll 2, t+240s, required: 1, concluded: 0/1)"
          and beats[1] == f"beat: waiting CI at {H0[:8]} (poll 4, t+480s, required: 1, concluded: 0/1)"
          and beats[2] == f"beat: waiting CI at {H0[:8]} (poll 6, t+960s, required: 1, concluded: 0/1)")
    hang[0]["status"], hang[0]["conclusion"] = "completed", "success"
    ticks = iter([0, 240, 480, 700])
    lines = []
    with tempfile.TemporaryDirectory() as d:
        t = Train("o/r", Path(d), None, "", (), 1, run=hung_run, sleep=lambda s: None,
                  log=lines.append, polls=3, clock=lambda: next(ticks))
        red = t.wait_ci(H0, only=["fast", "tests"], beat="proof batch/t-1")
    beats = [ln for ln in lines if ln.startswith("beat:")]
    check("a proof wait beats with the proof branch in the line and names its own "
          "concluded count among the required contexts",
          red == ["TIMEOUT"] and len(beats) == 2
          and beats[0] == "beat: waiting proof batch/t-1 (poll 1, t+240s, required: 2, concluded: 1/2)"
          and beats[1] == "beat: waiting proof batch/t-1 (poll 2, t+480s, required: 2, concluded: 1/2)")
    # THE BEAT LEADS THE POLL (tvofi, 2026-10-14, tag traintest): a beat due
    # mid-interval fired only at the NEXT poll boundary -- POLL_SECONDS (300)
    # behind HEARTBEAT_SECONDS (240), so the first beat landed at t+305s
    # (measured at main 981a45802: main_green's required-only wait, 11/14
    # concluded) and every one of them sat in a block buffer. The poll sleeps
    # only until the next beat is due: a beat never waits on a poll, and a
    # silent interval never exceeds HEARTBEAT_SECONDS.
    hang[0]["status"], hang[0]["conclusion"] = "in_progress", None
    clk = [0.0]
    lines = []
    with tempfile.TemporaryDirectory() as d:
        t = Train("o/r", Path(d), None, "", (), 1, run=hung_run,
                  sleep=lambda s: clk.__setitem__(0, clk[0] + s),
                  log=lines.append, polls=3, clock=lambda: clk[0])
        red = t.wait_ci(H0)
    beats = [ln for ln in lines if ln.startswith("beat:")]
    check("a beat is never held behind a poll boundary: the poll sleeps to the next beat, "
          "so beats land at t+240 and t+480 (not t+300/t+600 behind POLL_SECONDS)",
          red == ["TIMEOUT"] and len(beats) == 2
          and beats[0] == f"beat: waiting CI at {H0[:8]} (poll 2, t+240s, required: 1, concluded: 0/1)"
          and beats[1] == f"beat: waiting CI at {H0[:8]} (poll 3, t+480s, required: 1, concluded: 0/1)")
    # THE ENTRY IS UNBUFFERED (tvofi, 2026-10-14, tag traintest): the train ran
    # 8+ minutes healthy under a daemonizing wrapper whose dup2 made stdout a
    # file -- block-buffered -- so every beat sat in an 8KB buffer the kill
    # dropped, and a log with only the wrapper's launch line read as dead. The
    # entry point reconfigures stdout line-buffered before any queue read; the
    # instrument is self-sufficient and cannot rely on the launcher's flags.
    sys.stdout.reconfigure(line_buffering=False)
    try:
        main(["batch", "/nonexistent/queue.json"])
    except FileNotFoundError:
        pass
    check("the entry point reconfigures stdout line-buffered before reading the queue, so a "
          "redirected launch's beats reach the log as they print",
          getattr(sys.stdout, "line_buffering", None) is True)
    rc, lines, calls = go({"carry": "CARRY: no a -> b: a commit of the branch's own"})
    check("a verdict that does not carry stops it", rc == 1 and "carry:" in lines[-1] and not merged(calls))
    # BLOCK CLASS STALE-VERDICT-CARRY: app_approve --carry's ancestor line names
    # the shape -- the branch moved after the verdict (a bot push) -- so the
    # stop carries the class, the remedy and the delta the fresh verdict reads.
    rc, lines, calls = go({"carry": f"REFUSE: {V} is not an ancestor of {H0}"})
    check("a carry refusal whose shape is the stale-verdict ancestor line carries its "
          "class, the re-verdict remedy and the delta",
          rc == 1 and "[STALE-VERDICT-CARRY]" in lines[-1]
          and "verdict at the live head" in lines[-1] and H0[:8] in lines[-1]
          and "custom_components/x.py" in lines[-1] and not merged(calls))
    # BLOCK CLASS HOLDER: all eight entries of train-batch3 stopped here -- the
    # branch was still checked out in a previous session's worktree. The line
    # names the holder path and the exact freeing commands.
    def held(base_run):
        def run(argv, cwd=ROOT, stdin=None):
            a = " ".join(argv)
            if "worktree add" in a:
                return 1, "fatal: '" + "fix/x" + "' is already used by worktree at '/other/wt'"
            if "worktree list" in a:
                return 0, ("worktree /repo\nHEAD 0000000000000000000000000000000000000000\n"
                           "branch refs/heads/main\n\n"
                           "worktree /other/wt\nHEAD 1111111111111111111111111111111111111111\n"
                           "branch refs/heads/fix/x\n")
            return base_run(argv, cwd=cwd, stdin=stdin)
        return run
    rc, lines, calls = go({"contains": [False], "heads": [H0]}, wrap=held)
    check("HOLDER: a recarry whose branch is checked out in another worktree names the "
          "holder path and the exact freeing remedy, classified",
          rc == 1 and "[HOLDER]" in lines[-1] and "recarry" in lines[-1]
          and "another worktree at /other/wt" in lines[-1]
          and "git worktree remove /other/wt" in lines[-1]
          and "git -C /other/wt status" in lines[-1])
    rc, lines, calls = go({"contains": [False], "heads": [H0]},
                          wrap=lambda br: (lambda argv, cwd=ROOT, stdin=None:
                                           (1, "fatal: cannot lock ref") if "worktree add" in " ".join(argv)
                                           and "worktree list" not in " ".join(argv) else br(argv, cwd=cwd, stdin=stdin)))
    check("a worktree add that fails with no holder stays today's plain refusal, unclassified",
          rc == 1 and "could not make a worktree" in lines[-1] and "[HOLDER]" not in lines[-1])
    rc, lines, calls = go({"contains": [True, False]})
    check("main moving during CI stops it", rc == 1 and "main:" in lines[-1] and not merged(calls))
    # MAIN MOVED (R10-TICK-TRAIN, tvofi 2026-10-15: #2284 was green 14/14 and
    # stopped because a record PR auto-merged). The recovery re-carries onto
    # the new main and waits CI again, up to --main-moved-tries; every guard
    # is re-read at the new head.
    def remerges(calls) -> int:
        return sum("remerge_main.sh" in " ".join(c) for c in calls)
    rc, lines, calls = go({"contains": [False, False, False, True], "heads": [H0, H1, H1, H2]},
                          main_moved_tries=1)
    check("main moving during CI is recovered: a second recarry onto the new main, CI again, "
          "and the merge pinned at the new head",
          rc == 0 and remerges(calls) == 2 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H2 for c in calls)
          and not any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls)
          and any(ln.startswith("#7 [MAIN-MOVED] main:") and "recarry 1/1" in ln for ln in lines)
          and sum("check-runs" in " ".join(c) for c in calls) >= 2)
    rc, lines, calls = go({"contains": [False, False, False, False], "heads": [H0, H1, H1, H2]},
                          main_moved_tries=1)
    check("the recovery is bounded: main moving again past --main-moved-tries stops as today, "
          "naming the spent bound", rc == 1 and remerges(calls) == 2 and not merged(calls)
          and lines[-1].startswith("TRAIN STOPPED #7 main: [MAIN-MOVED] origin/main moved during CI")
          and "1 recarry onto a moved main spent" in lines[-1])
    rc, lines, calls = go({"contains": [False, False], "heads": [H0, H1]})
    check("--main-moved-tries 0 (the constructor's default) is today's train: one recarry, then the stop",
          rc == 1 and remerges(calls) == 1 and not merged(calls) and lines[-1] ==
          "TRAIN STOPPED #7 main: [MAIN-MOVED] origin/main moved during CI and is not in the head; run the train again")
    rc, lines, calls = go({"contains": [True, True, False, False, True], "heads": [H0, H0, H0, H1]},
                          main_moved_tries=1)
    check("main moving between the approval and the merge is recovered too: recarried, CI again, "
          "re-approved and merged at the new head only",
          rc == 0 and remerges(calls) == 1 and [c[-1] for c in calls if c[:3] == ["gh", "pr", "merge"]] == [H1]
          and sum("app_approve.sh" in " ".join(c) and "--carry" not in c for c in calls) == 2
          and any("[MAIN-MOVED] merge:" in ln for ln in lines))
    # --bot-prs: the record/autofix pull request merges in the train's own
    # sequence, before the recarry, behind record_row.py's own guard.
    had_token = os.environ.get("GH_TOKEN")
    rc, lines, calls = go({"bot_find": (0, "9")}, bot_prs=True)
    order = [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]]
    check("--bot-prs: the open record PR passing record_row.py's guard at its head merges FIRST, "
          "pinned there, and the queue then lands",
          rc == 0 and order == ["9", "7"] and any(ln.startswith("BOT #9 MERGED") for ln in lines)
          and any(c[:4] == ["gh", "pr", "merge", "9"] and c[-1] == "e" * 40 for c in calls)
          and any("--automerge-check" in c and "--require-green" in c and c[c.index("--head") + 1] == "e" * 40
                  for c in calls))
    for code, word in ((3, "pending"), (1, "refused by the guard")):
        rc, lines, calls = go({"bot_find": (0, "9"), "bot_guard": (code, "AUTOMERGE X #9: y")}, bot_prs=True)
        check(f"--bot-prs: a guard exit {code} never merges the record PR ({word}), and the train goes on",
              rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7"]
              and any(ln.startswith(f"BOT #9 {word}") for ln in lines))
    rc, lines, calls = go({"bot_find": (0, "0")}, bot_prs=True)
    check("--bot-prs with no open record PR (the lookup answers 0) guards nothing and merges nothing "
          "but the queue",
          rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7"]
          and not any("--automerge-check" in c for c in calls) and not any(ln.startswith("BOT") for ln in lines))
    rc, lines, calls = go({"bot_find": (0, "9")})
    check("without --bot-prs no record PR is looked up (the default is today's train)",
          rc == 0 and not any("record_row.py" in " ".join(c) for c in calls))
    if had_token is None:
        os.environ.pop("GH_TOKEN", None)
    # --pre-flight: queue_pre_flight's reads first; a failing entry PARKs.
    bad = dict(item, pr=6, verdict="f" * 39 + "g")
    rc, lines, calls = go({}, q=[bad, dict(item)], pre_flight=True)
    check("--pre-flight: an entry the pre-flight refuses is PARKed and left out; the rest lands; rc 1",
          rc == 1 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7"]
          and any(ln.startswith("PARK #6 queue:") for ln in lines) and lines[-1] == "TRAIN DONE")
    seen_pf: list = []
    with tempfile.TemporaryDirectory() as d:
        pf_q = [bad, dict(item)]
        got = Train("o/r", Path(d), None, "", (), 1, run=lambda argv, cwd=ROOT, stdin=None: (seen_pf.append(argv), (0, ""))[1],
                    base="batch/r", pre_flight=True).preflight(pf_q)
    check("--pre-flight on a batch/ rehearsal reads nothing and parks nothing: its reads grade a "
          "merge into main, which a rehearsal never makes",
          got == pf_q and seen_pf == [])
    rc, lines, calls = go({}, q=[bad, dict(item)])
    check("... without --pre-flight the same entry stops the train at its turn (null control)",
          rc == 1 and not merged(calls) and "queue:" in lines[-1])
    rc, lines, calls = go({"bot_tips": {H0: BOT_SUBJ}, "contains": [False], "heads": [H0, H1]}, pre_flight=True)
    check("--pre-flight passes a bot tip the train cures itself (its recarry is the App push)",
          rc == 0 and merged(calls) and not any(ln.startswith("PARK") for ln in lines))
    # --free-holders: a clean holder at origin/<branch> is detached, nothing else.
    seen: list[list[str]] = []

    def holding(state: str, at: str, here: str = "1" * 40):
        seen.clear()

        def wrap(base_run):
            freed = []
            def run(argv, cwd=ROOT, stdin=None):
                seen.append(argv)
                a = " ".join(argv)
                if "worktree add" in a:
                    return (0, "") if freed else (1, "fatal: 'fix/x' is already used by worktree at '/other/wt'")
                if "worktree list" in a:
                    return 0, "worktree /other/wt\nHEAD " + "1" * 40 + "\nbranch refs/heads/fix/x\n"
                if argv[:4] == ["git", "-C", "/other/wt", "status"]:
                    return 0, state
                if argv[:4] == ["git", "-C", "/other/wt", "rev-parse"]:
                    return (0 if is_sha(here) else 128), here
                if argv[:3] == ["git", "rev-parse", "origin/fix/x"]:
                    return (0 if is_sha(at) else 128), at
                if argv[:4] == ["git", "-C", "/other/wt", "checkout"]:
                    freed.append(1)
                    return 0, ""
                return base_run(argv, cwd=cwd, stdin=stdin)
            return run
        return wrap
    detached = lambda _calls: any(c[:4] == ["git", "-C", "/other/wt", "checkout"] for c in seen)
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding("", "1" * 40), free_holders=True)
    check("--free-holders: a clean holder at origin/<branch> is detached, logged with its restore, "
          "and the recarry goes on to the merge",
          rc == 0 and merged(calls) and detached(calls)
          and any("[HOLDER] freed: /other/wt" in ln and "switch fix/x" in ln for ln in lines))
    for st, at, why in ((" M x.py\n", "1" * 40, "uncommitted or untracked"),
                        ("?? note.md\n", "1" * 40, "uncommitted or untracked"),
                        ("", "2" * 40, "unpushed work")):
        rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding(st, at), free_holders=True)
        check(f"--free-holders refuses a holder with {why} ({st.strip() or 'HEAD off origin'}): "
              "today's HOLDER stop, the reason appended, nothing detached",
              rc == 1 and "[HOLDER]" in lines[-1] and f"not freed: " in lines[-1] and why in lines[-1]
              and not detached(calls) and not merged(calls))
    UNREAD = "fatal: not a git repository"
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding("", UNREAD, here=UNREAD),
                          free_holders=True)
    check("--free-holders refuses a holder whose HEAD and origin/<branch> both fail to read: two "
          "equal failures are no sha, and nothing is detached",
          rc == 1 and "[HOLDER]" in lines[-1] and "unpushed work" in lines[-1]
          and not detached(calls) and not merged(calls))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, wrap=holding("", "1" * 40))
    check("without --free-holders even a freeable holder stops exactly as today (null control)",
          rc == 1 and "[HOLDER]" in lines[-1] and "not freed" not in lines[-1] and not detached(calls))
    _g, owner_review, mandate, revoke = policy_fixture_builders()
    NOW = datetime.datetime.now(datetime.timezone.utc)
    POL = {"files": ["custom_components/x.py", f"{ROW_DIR}/7.md", "dev/governance/roles/fixer.md"]}
    no_app = lambda: not any("app_approve.sh" in " ".join(c) and "--carry" not in c for c in calls)
    rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW)})
    check("a policy head whose owner approval at this exact head cites a mandate in force lands",
          rc == 0 and merged(calls) and lines[-1] == "TRAIN DONE"
          and any("policy" in ln and f"mandate {MID}" in ln for ln in lines))
    rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW, cite=False)], "mandate": mandate(NOW)})
    check("a policy head with NO mandate is refused as before -- the approval is at the head, "
          "so the refusal names the mandate, not the review (the fallback is the point)",
          rc == 1 and "policy:" in lines[-1] and "dev/governance/roles/fixer.md" in lines[-1]
          and "cites no mandate" in lines[-1] and not approved(calls) and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [], "mandate": mandate(NOW)})
    check("a policy head with a mandate but no owner approval at its head is refused, named as the review",
          rc == 1 and "policy:" in lines[-1] and "no decisive review" in lines[-1]
          and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW, until_min=-1)})
    check("a mandate whose window has passed behaves as no mandate (expiry arm)",
          rc == 1 and "policy:" in lines[-1] and "expired" in lines[-1]
          and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW),
                           "thread": [revoke()]})
    check("a revoked mandate refuses the policy head, named as revoked",
          rc == 1 and "policy:" in lines[-1] and "revoked" in lines[-1] and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW, scope="budget-raise")})
    check("a mandate scoped budget-raise does not cover policy merging",
          rc == 1 and "policy:" in lines[-1] and "does not cover policy merging" in lines[-1]
          and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW, scope="code-owned")})
    check("a code-owned mandate licenses approvals, not the train landing policy (MANDATE_COVERS_POLICY is `all`)",
          rc == 1 and "policy:" in lines[-1] and "does not cover policy merging" in lines[-1]
          and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [owner_review("f" * 40, NOW)], "mandate": mandate(NOW),
                           "reviewed": "f" * 40, "content_diff": ["dev/governance/roles/fixer.md"]})
    check("policy content that moved after the owner's review is refused and named as that change",
          rc == 1 and "policy:" in lines[-1] and "changed after the owner's review" in lines[-1]
          and not merged(calls) and no_app())
    rc, lines, calls = go({**POL, "reviews": [owner_review("f" * 40, NOW)], "mandate": mandate(NOW),
                           "reviewed": "f" * 40, "content_diff": ["custom_components/y.py"]})
    check("an approval not at this exact head is refused as that, when the policy blobs did not move",
          rc == 1 and "policy:" in lines[-1] and "not this head" in lines[-1]
          and not merged(calls) and no_app())
    rc, lines, calls = go({"heads": [H0, H1]})
    check("a head that moves before the approval stops it", rc == 1 and "head moved" in lines[-1]
          and not approved(calls) and not merged(calls))
    rc, lines, calls = go({"broken_filter": True})
    check("a policy filter that fails its sentinel probe stops it", rc == 1 and "sentinel" in lines[-1] and not merged(calls))
    owned = (1, "app_approve: REFUSE: #7 touches code-owned paths (tests/run.sh .github/workflows/tests.yml); the owner's GitHub review approves it")
    rc, lines, calls = go({"approve": owned})
    check("code-owned without --mandate stops it", rc == 1 and "no --mandate" in lines[-1] and not approved(calls))
    w = {"approve": owned}
    rc, lines, calls = go(w, mandate="mandate 5951564627 (tvofi, #201)")
    check("code-owned with --mandate approves and merges", rc == 0 and approved(calls) and merged(calls))
    b = w["approve_body"]
    check("the mandate body names the label, role, paths, verdict comment and head",
          all(s in b for s in ("mandate 5951564627 (tvofi, #201)", "the orchestrator", "`tests/run.sh`", "comment 42", H0, V)))
    rc, lines, calls = go({"approve": owned, "budgets": RAISE_FIXTURE,
                           "files": ["tests/structure_budgets.json", f"{ROW_DIR}/7.md"]},
                          mandate="m")
    check("code-owned with a budget RAISE is not mandate-approved", rc == 1 and "budget" in lines[-1] and not approved(calls))
    # --approval-carry: the recarry moved an owner-approved head, the owner
    # approved a budget raise there, and the orchestrator no longer re-posts it
    # by hand. `carry` is the fully-qualifying world; each arm below breaks
    # exactly one safety condition and demands today's stop back.
    RID = 4100000002
    CB = "mandate 5951564627 (tvofi, #201)"
    BUDGET = ["tests/structure_budgets.json", f"{ROW_DIR}/7.md"]

    def carry_world(**over):
        # The fully-qualifying carry world, fresh per arm: the mutable keys
        # (contains, heads) must never be shared between `go` calls -- a
        # recarry consumes them.
        return dict({"approve": owned, "files": BUDGET, "budgets": RAISE_FIXTURE, "contains": [False],
                     "heads": [H0, H1],
                     "carry_delta": (H0, H1, "docs/a-main-only-file.md\n")}, **over)

    w = carry_world(reviews=[dict(owner_review(H0, NOW), id=RID)], mandate=mandate(NOW))
    rc, lines, calls = go(w, mandate=CB, approval_carry=True)
    check("approval-carry fires: the clean recarry's head gets the owner's approval re-posted "
          "with the carry line, and the entry merges",
          rc == 0 and merged(calls) and any("approved (carry)" in ln for ln in lines)
          and all(x in w["carry_body"] for x in (
              "Agent approval", "Carried by the train's clean recarry from " + H0,
              "(delta: main's commits only)", f"prior owner review {RID}",
              f"mandate re-read in force at merge: {CB}")))
    # R10-TICK (f), #2209: GitHub RE-ANCHORS an approval across a clean base
    # merge -- review 5526967770's body names 8a8e66e7, the API reports its
    # commit_id as the recarried 8876da3b -- so at the carry the owner's
    # approval named h, not h0, and `prior.commit_id != h0` returned no carry.
    # An owner approval already at the live head is the owner's (the gate's
    # raise reading, its mandate re-read at the merge): nothing to re-post.
    JUST = JUSTIFIED_BODY
    for flag in (True, False):
        w = carry_world(reviews=[dict(owner_review(H1, NOW), id=RID)], mandate=mandate(NOW), pr_body=JUST)
        rc, lines, calls = go(w, mandate=CB, approval_carry=flag)
        check(f"#2209's shape (approval-carry {'on' if flag else 'off'}): the owner's approval GitHub "
              "re-anchored to the recarried head is the owner's at that head -- the budget entry "
              "lands with nothing re-posted",
              rc == 0 and merged(calls) and any("approved (owner)" in ln for ln in lines)
              and not approved(calls) and w["carry_body"] == "")
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H1, NOW), id=RID)],
                                      mandate=mandate(NOW, until_min=-1), pr_body=JUST), mandate=CB, approval_carry=True)
    check("#2209's shape MUTATION (the mandate re-read at the merge): a re-anchored approval "
          "under an expired mandate stops exactly as today",
          rc == 1 and "a raise is the owner's" in lines[-1] and not merged(calls))
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H1, NOW), id=RID)], mandate=mandate(NOW),
                                      pr_body=JUST.replace("Payments tried", "Paid")), mandate=CB, approval_carry=True)
    check("#2209's shape MUTATION (the gate's own justification): a mandated approval at the head "
          "whose body lacks the raise justification's payment line is not the owner's -- it stops "
          "exactly as today, as budget-raise-gate would refuse it",
          rc == 1 and "a raise is the owner's" in lines[-1] and not merged(calls) and not approved(calls))
    w = carry_world(reviews=[dict(owner_review(H0, NOW), id=RID)], mandate=mandate(NOW),
                    contains=[False, False, False, True], heads=[H0, H1, H1, H2],
                    carry_delta=(H0, H2, "docs/a-main-only-file.md\n"))
    rc, lines, calls = go(w, mandate=CB, approval_carry=True, main_moved_tries=1)
    check("approval-carry across a main-moved recovery: the owner's approval at the FIRST head "
          "carries to the second recarry's head, its delta read from that first head",
          rc == 0 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H2 for c in calls)
          and "Carried by the train's clean recarry from " + H0 in w["carry_body"])
    # The MIDDLE head (R11): #2209's re-anchor put the owner's approval on the
    # first recarry's head H1, then main moved during CI and a second recarry
    # made H2. H1 is neither the first head nor the live one.
    w = carry_world(reviews=[dict(owner_review(H1, NOW), id=RID)], mandate=mandate(NOW),
                    contains=[False, False, False, True], heads=[H0, H1, H1, H2],
                    carry_delta=(H1, H2, "docs/a-main-only-file.md\n"))
    rc, lines, calls = go(w, mandate=CB, approval_carry=True, main_moved_tries=1)
    check("approval-carry from the MIDDLE of the carry chain: an approval re-anchored to the first "
          "recarry's head carries to the second's, its delta read from that middle head",
          rc == 0 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H2 for c in calls)
          and "Carried by the train's clean recarry from " + H1 in w["carry_body"])
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H0, NOW), id=RID)],
                                      mandate=mandate(NOW),
                                      carry_delta=(H0, H1, f"{ROW_DIR}/7.md\ntests/structure_budgets.json\n")),
                          mandate=CB, approval_carry=True)
    check("approval-carry MUTATION (the diff-empty check): a recarry delta naming a branch-own "
          "file is a conflict resolution, and it stops exactly as today",
          rc == 1 and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H0, NOW), id=RID)],
                                      mandate=mandate(NOW, until_min=-1)), mandate=CB, approval_carry=True)
    check("approval-carry MUTATION (the mandate in-force check): a mandate expired before the "
          "merge re-reads as none, and it stops exactly as today",
          rc == 1 and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go(carry_world(reviews=[], mandate=mandate(NOW)), mandate=CB, approval_carry=True)
    check("approval-carry with no owner APPROVED review at h0 behaves as today", rc == 1
          and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review("f" * 40, NOW), id=RID)],
                                      mandate=mandate(NOW)), mandate=CB, approval_carry=True)
    check("approval-carry with the owner's approval on another commit does not carry", rc == 1
          and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H0, NOW, cite=False), id=RID)],
                                      mandate=mandate(NOW)), mandate=CB, approval_carry=True)
    check("approval-carry with an owner review citing no mandate does not carry", rc == 1
          and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
    w = carry_world(reviews=[dict(owner_review(H0, NOW), id=RID)], mandate=mandate(NOW))
    rc, lines, calls = go(w, mandate=CB)
    check("approval-carry FLAG OFF: the same qualifying world stops exactly as today -- the "
          "default train is byte-identical", rc == 1 and "a raise is the owner's" in lines[-1]
          and not approved(calls) and not merged(calls) and w["carry_body"] == ""
          and w["approve_body"] == "")
    w = carry_world(approve=owned, files=BUDGET, reviews=[dict(owner_review(H0, NOW), id=RID)],
                    mandate=mandate(NOW), contains=[], heads=[H0], pr_body=JUST)
    rc, lines, calls = go(w, mandate=CB, approval_carry=True)
    check("approval-carry with no recarry of this invocation (the head never moved) does not carry: "
          "the owner's approval already at the head is the owner's, and nothing is re-posted",
          rc == 0 and merged(calls) and any("approved (owner)" in ln for ln in lines)
          and not approved(calls) and w["carry_body"] == "")
    rc, lines, calls = go(carry_world(approve=owned, files=BUDGET, reviews=[], mandate=mandate(NOW),
                                      contains=[], heads=[H0]), mandate=CB, approval_carry=True)
    check("... and with no owner approval at that head it stops exactly as today (null control)",
          rc == 1 and "a raise is the owner's" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go(carry_world(reviews=[dict(owner_review(H0, NOW), id=RID)],
                                      mandate=mandate(NOW), drop_posted=True),
                          mandate=CB, approval_carry=True)
    check("approval-carry whose re-post fails the byte-identical read-back is a Stop, not a pass",
          rc == 1 and "byte-identical" in lines[-1] and approved(calls) and not merged(calls))
    # R10-TRAIN-RAISE-HOLD (#2401: trains t11-t13 stopped while CI's
    # budget-raise-gate printed budget_raises=0 PASS). A raise is the gate's
    # DIRECTION reading (raise_hold), never a `*_budgets.json` path: a budget
    # file that only gains rows takes the ordinary mandate approval, and a
    # raise's Stop carries the gate's own reason.
    NEW_ROWS = ["tests/ci_budgets.json", f"{ROW_DIR}/7.md"]
    w = {"approve": owned, "files": NEW_ROWS, "budgets": NEW_ROWS_FIXTURE, "reviews": [], "pr_body": "## Summary\n"}
    rc, lines, calls = go(w, mandate=CB)
    check("#2401's shape: a budget file that only gains rows is no raise -- the ordinary "
          "mandate approval is posted and the entry merges, with no owner review and no "
          "raise justification owed", rc == 0 and approved(calls) and merged(calls)
          and "Agent approval for code-owned" in w["approve_body"])
    rc, lines, calls = go({"approve": owned, "files": NEW_ROWS, "budgets": NEW_ROWS_FIXTURE,
                           "reviews": [dict(owner_review(H0, NOW), id=RID)], "mandate": mandate(NOW),
                           "pr_body": "## Summary\n"}, mandate=CB)
    check("... and with #2401's own reviews (a mandated owner approval at the head, a body with no "
          "raise justification) it still merges: the justification is a raise's alone",
          rc == 0 and merged(calls))
    PLANT = {"approve": owned, "files": BUDGET, "budgets": RAISE_FIXTURE}
    rc, lines, calls = go(dict(PLANT, reviews=[dict(owner_review(H0, NOW), id=RID)], mandate=mandate(NOW),
                               pr_body="## Summary\n\n## Raise justification\n\nWe need it.\n"), mandate=CB)
    check("a planted raise whose mandated approval sits at the head but whose body is deficient "
          "stops, naming the raise and BOTH missing lines",
          rc == 1 and not merged(calls) and not approved(calls)
          and "tests/structure_budgets.json: m: 3 -> 4" in lines[-1]
          and "`Payments tried:`" in lines[-1] and "`Architecture score: dS`" in lines[-1])
    rc, lines, calls = go(dict(PLANT, reviews=[dict(owner_review(H0, NOW), id=RID)], mandate=mandate(NOW),
                               pr_body=JUST), mandate=CB)
    check("a planted raise with a healthy body under the mandate in force lands as the owner's, "
          "nothing re-posted", rc == 0 and merged(calls) and not approved(calls)
          and any("approved (owner)" in ln for ln in lines))
    rc, lines, calls = go(dict(PLANT, reviews=[], mandate=mandate(NOW), pr_body=JUST), mandate=CB)
    check("a planted raise with no owner review stops, and the Stop carries the gate's why",
          rc == 1 and not merged(calls) and "a raise is the owner's" in lines[-1]
          and "no decisive review by" in lines[-1])
    rc, lines, calls = go(dict(PLANT, reviews=[dict(owner_review(H0, NOW - datetime.timedelta(minutes=30)), id=RID)],
                               mandate=mandate(NOW, until_min=-10), pr_body=JUST), mandate=CB)
    check("a planted raise approved while its mandate was in force, the mandate expired before the "
          "merge, stops: the mandate is judged AT THE MERGE, not at the review",
          rc == 1 and not merged(calls) and "expired" in lines[-1])
    rc, lines, calls = go(dict(PLANT, budgets=None, reviews=[dict(owner_review(H0, NOW), id=RID)],
                               mandate=mandate(NOW), pr_body=JUST), mandate=CB)
    check("fail closed: a budget path the diff names that neither tree holds is a Stop, never "
          "a no-raise", rc == 1 and not merged(calls) and not approved(calls)
          and "budget read failed" in lines[-1])
    rc, lines, calls = go(dict(PLANT, ls_fail=True, reviews=[dict(owner_review(H0, NOW), id=RID)],
                               mandate=mandate(NOW), pr_body=JUST), mandate=CB)
    check("fail closed: a tree that cannot be listed is a Stop", rc == 1 and not merged(calls)
          and not approved(calls) and "budget read failed" in lines[-1])
    rc, lines, calls = go(dict(PLANT, show_fail=True, reviews=[dict(owner_review(H0, NOW), id=RID)],
                               mandate=mandate(NOW), pr_body=JUST), mandate=CB)
    check("fail closed: a budget blob the tree lists but git cannot read is a Stop even under the "
          "owner's approval -- never its error text read as an unparsable file the approval then holds",
          rc == 1 and not merged(calls) and not approved(calls) and "budget read failed" in lines[-1])
    rc, lines, calls = go({"approve": (1, "REFUSE: the verdict cites no qualifying evidence: x")}, mandate="m")
    check("a missing-evidence refusal is not overridden by a mandate", rc == 1 and "app_approve.sh refused: REFUSE: the verdict cites" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1], "remerge": "MERGE CONFLICT 7"})
    check("a recarry conflict stops it, named as one", rc == 1 and "without a resolution" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"contains": [False], "heads": [H0], "remerge": "REFUSE: body"})
    check("a recarry that pushed nothing and left the head where it was stops it (the refusal is real)",
          rc == 1 and "pushed nothing" in lines[-1] and not merged(calls))
    # R9-RC-RECARRY-READBACK: app_push now settles a race inside its own budget,
    # so a non-PUSHED output with the head MOVED means the push landed anyway
    # (a lag that outran app_push's budget). The train re-reads the head once and
    # carries on instead of stopping -- the #2071 race that killed the pass.
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1], "remerge": "REFUSE: body"})
    check("a recarry refusal whose head nonetheless moved is treated as landed, not a stop",
          rc == 0 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls)
          and any("the push landed, not a stop" in ln for ln in lines))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]})
    check("a head behind main is recarried, then merged at the new head",
          rc == 0 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]})
    start_i = next((i for i, ln in enumerate(lines) if ln == "#7 recarry START (branch fix/x)"), None)
    done_i = next((i for i, ln in enumerate(lines) if "recarry: main merged" in ln), None)
    check("the recarry announces itself BEFORE remerge_main.sh runs, naming the branch "
          "(5-15 min of prepr silence is visible mid-flight)",
          rc == 0 and start_i is not None and done_i is not None and start_i < done_i)
    for way in ("SKIPPED: HEAD is the clean merge", "RUNS: HEAD has 3 parent(s)"):
        rc, lines, calls = go({"contains": [False], "heads": [H0, H1],
                               "remerge": f"app_push: RECARRY: prepr {way}\napp_push: PUSHED"})
        check(f"the recarry logs app_push's path line (prepr {way.split(':')[0]})",
              rc == 0 and any(ln.endswith(f"app_push: RECARRY: prepr {way}") for ln in lines))
    # R9-RC-AUTOFIX-GOVERNANCE: a GITHUB_TOKEN push (author github-actions[bot])
    # gets pull_request runs held action_required, so the required contexts
    # only they write are ABSENT at such a head until one is approved, and the
    # merge is refused with nothing saying why (the measurement is bot_tip's
    # comment).
    BOT = "ci: pin killed mutants"
    rc, lines, calls = go({"bot_tips": {H0: BOT}})
    check("a head whose tip is a GITHUB_TOKEN bot push is refused before CI is even read -- "
          "waiting cannot repair it; the required follow-up is an App push",
          rc == 1 and "ci:" in lines[-1] and "GITHUB_TOKEN" in lines[-1] and BOT in lines[-1]
          and "App push" in lines[-1]
          and not merged(calls) and not approved(calls)
          and not any("check-runs" in " ".join(c) for c in calls))
    check("the bot-head stop is classified BOT-HEAD in the line itself (the remedy text was already exact)",
          "[BOT-HEAD]" in lines[-1])
    rc, lines, calls = go({"bot_tips": {H0: BOT}, "contains": [False], "heads": [H0, H1]})
    check("a bot head behind main is not refused: the recarry's App push IS the follow-up, "
          "and the train goes on at the new head (null control for the refusal above)",
          rc == 0 and merged(calls) and any("recarry" in ln for ln in lines)
          and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls))
    # The route the stubs cannot see: the real remerge_main.sh pushes with --recarry.
    rm = (ROOT / TOOLS["remerge_main"][0]).read_text()
    check("remerge_main.sh pushes the recarry with app_push.sh --recarry and passes its RECARRY line on",
          re.search(r'bash "\$_push" --recarry ', rm) is not None and "RECARRY|" in rm)
    # End-to-end absorbed-branch recarry against a REAL fixture repo (#1943):
    # the train's `git worktree add` runs for real, the remerge stub performs
    # remerge_main.sh's actual merge on that worktree, and then applies
    # app_push.sh's committed-tip gate verbatim (HEAD == refs/heads/<branch>)
    # -- the gate that stopped #1893, #1894 and #1896 on a DETACHED recarry
    # worktree, where the auto-merge sha is nobody's committed tip.
    with tempfile.TemporaryDirectory() as gd:
        g = Path(gd) / "repo"
        g.mkdir()
        def rg(*argv: str, cwd: Path | None = None) -> tuple[int, str]:
            r = subprocess.run(["git", *argv], cwd=cwd or g, capture_output=True, text=True,
                               env=throwaway_git_env())
            return r.returncode, (r.stdout + r.stderr).strip()
        throwaway_git_init(g, "-q", "-b", "main")
        rg("config", "user.email", "fixture@example.test")
        rg("config", "user.name", "fixture")
        (g / "one.txt").write_text("one\n")
        rg("add", ".")
        rg("commit", "-qm", "one")
        c1 = rg("rev-parse", "HEAD")[1]
        rg("branch", "fix/x", c1)
        (g / "two.txt").write_text("two\n")
        rg("add", ".")
        rg("commit", "-qm", "two")
        rg("update-ref", "refs/remotes/origin/fix/x", c1)
        rg("update-ref", "refs/remotes/origin/main", rg("rev-parse", "HEAD")[1])
        wt = Path(gd) / "wt"

        def gate() -> tuple[bool, str]:
            if not wt.exists():
                return False, "no worktree"
            head = rg("rev-parse", "HEAD", cwd=wt)[1]
            code, tip = rg("rev-parse", "--verify", "refs/heads/fix/x", cwd=wt)
            return (code == 0 and head == tip), head if code == 0 else f"no local branch ({tip})"

        def real_remerge() -> str:
            rg("reset", "-q", "--hard", "origin/fix/x", cwd=wt)
            if rg("merge", "--no-edit", "-q", "origin/main", cwd=wt)[0]:
                return "MERGE CONFLICT"
            good, head = gate()
            return "app_push: PUSHED" if good else \
                f"app_push: REFUSE: worktree HEAD ({head}) is not the committed tip of 'fix/x'"

        def wrap(base_run):
            def run(argv, cwd=ROOT, stdin=None):
                if argv[:2] == ["git", "worktree"]:
                    r = subprocess.run(argv, cwd=g, capture_output=True, text=True)
                    return r.returncode, r.stdout + r.stderr
                if "remerge_main.sh" in " ".join(argv):
                    return 0, real_remerge()
                return base_run(argv, cwd=cwd, stdin=stdin)
            return run

        it = dict(item, worktree=str(wt))
        rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, q=[it], wrap=wrap)
        on_branch = wt.exists() and rg("symbolic-ref", "-q", "HEAD", cwd=wt)[0] == 0
        gate_ok, why = gate()
        check("an absorbed-branch recarry lands in a real fixture repo: the worktree is the branch, the tip gate passes, the merge runs",
              rc == 0 and merged(calls) and on_branch and gate_ok)
    rc, lines, calls = go({"preflight": "  REFUSE   'Closes #12' closes #12"})
    check("a title preflight refusal stops it before the merge", rc == 1 and "preflight:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"preflight": "  REFUSE   'Closes #12' closes #12\n  clean    no refusal"})
    check("a REFUSE line stops it even beside a clean line", rc == 1 and "preflight:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"merge": ["OPEN None", "OPEN None", "MERGED " + "e" * 40]})
    check("the merge is retried until GitHub reports MERGED", rc == 0 and sum(c[:3] == ["gh", "pr", "merge"] for c in calls) == 3)
    rc, lines, calls = go({"merge": ["OPEN None"] * 3})
    check("a merge GitHub never takes stops it", rc == 1 and "merge:" in lines[-1])
    # train-b5, #2290: eight silent refusals. Each is now logged in GitHub's
    # words, the stop names the last, and a base-moved refusal is recovered.
    REF = (1, "X Pull request tvofi/r#7 is not mergeable: the merge commit cannot be cleanly created.")
    rc, lines, calls = go({"merge": ["OPEN None"] * 3, "merge_outs": [REF] * 3})
    check("every refused merge attempt is logged with GitHub's own words, and the stop names the last",
          rc == 1 and sum(ln.startswith("#7 merge attempt ") and "cannot be cleanly created" in ln
                          for ln in lines) == 3
          and "the last refusal: X Pull request" in lines[-1])
    MOVED = (1, "GraphQL: Base branch was modified. Review and try the merge again. (mergePullRequest)")
    rc, lines, calls = go({"merge": ["OPEN None", "MERGED " + "e" * 40], "merge_outs": [MOVED],
                           "contains": [True, True, True, False, True], "heads": [H0, H0, H0, H1]},
                          main_moved_tries=1)
    check("a refusal saying the base moved is a MainMoved: recarried, CI again, merged at the new head",
          rc == 0 and remerges(calls) == 1 and [c[-1] for c in calls if c[:3] == ["gh", "pr", "merge"]] == [H0, H1]
          and any("[MAIN-MOVED] merge: GitHub refused the merge because the base moved" in ln for ln in lines))
    rc, lines, calls = go({"merge": ["OPEN None"] * 3 + ["MERGED " + "e" * 40], "merge_outs": [REF] * 3,
                           "contains": [True, True, True, True, True, False, False, True],
                           "heads": [H0, H0, H0, H1]}, main_moved_tries=1)
    check("every attempt refused while main moved past the head (the #2290 shape) is recarried, not stopped",
          rc == 0 and remerges(calls) == 1 and any(c[:3] == ["gh", "pr", "merge"] and c[-1] == H1 for c in calls)
          and any("[MAIN-MOVED] merge: not merged after 3 attempts" in ln and "moved past the head" in ln
                  for ln in lines))
    rc, lines, calls = go({"merge": ["OPEN None"] * 3, "merge_outs": [REF] * 3}, main_moved_tries=1)
    check("... while the same refusals on a head that still contains main stop as before (null control)",
          rc == 1 and remerges(calls) == 0 and "not merged after 3 attempts" in lines[-1])
    # The train releases the recarry worktrees it made (train-b5 left wt/2290
    # holding the branch, and the next pre-flight PARKed the entry on it).
    own = {k: v for k, v in item.items() if k != "worktree"}
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]}, q=[dict(own)])
    removed = [c for c in calls if c[:3] == ["git", "worktree", "remove"]]
    check("a recarry worktree the train made under its state dir is removed at the run's end, never forced",
          rc == 0 and len(removed) == 1 and removed[0][3].endswith("/wt/7") and "--force" not in removed[0]
          and any(ln.startswith("released ") for ln in lines))
    rc, lines, calls = go({"contains": [False], "heads": [H0, H1]})
    check("... and a queue entry's own worktree is never touched (null control)",
          rc == 0 and not any(c[:3] == ["git", "worktree", "remove"] for c in calls))
    rc, lines, calls = go({}, q=[dict(item), dict(item, pr=8)])
    check("the queue runs in order", rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7", "8"])
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"}]},
                          q=[dict(item), dict(item, pr=8)])
    check("the first refusal stops the queue", rc == 1 and not any(c[:4] == ["gh", "pr", "view", "8"] for c in calls))
    owned7 = (1, "app_approve: REFUSE: #7 touches code-owned paths (tests/run.sh); the owner's GitHub review approves it, not the App")
    echo = (1, "app_approve: REFUSE: the newest allowlisted verdict on #7 is 'Fix review: blocked aaaa policy: "
               "#7 touches code-owned paths (tests/run.sh); and ## Approval is missing', not 'Fix review: merge " + H0 + "'")
    rc, lines, calls = go({"approve": echo}, mandate="m")
    check("a blocked verdict echoing the code-owned words is not mandate-approved (B1)",
          rc == 1 and "app_approve.sh refused" in lines[-1] and not approved(calls) and not merged(calls))
    quoted = (1, "app_approve: REFUSE: the newest allowlisted verdict on #7 is 'Fix review: blocked x approve: "
                 "app_approve: REFUSE: #7 touches code-owned paths (tests/run.sh); the owner', not z")
    rc, lines, calls = go({"approve": quoted}, mandate="m")
    check("a blocked verdict QUOTING app_approve's own code-owned line mid-line is not mandate-approved (anchor)",
          rc == 1 and "app_approve.sh refused" in lines[-1] and not approved(calls) and not merged(calls))
    rc, lines, calls = go({"approve": owned7, "base": (0, "not-a-sha\n")}, mandate="m")
    check("a merge base that exits 0 but is not a sha stops the train", rc == 1 and "files:" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7}, mandate="m")
    check("the anchored code-owned refusal line still takes the mandate path (null control)", rc == 0 and approved(calls))
    rc, lines, calls = go({"approve": (1, owned7[1].replace("#7 ", "#8 "))}, mandate="m")
    check("another pull request's code-owned line does not take the mandate path for this one",
          rc == 1 and "app_approve.sh refused" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "heads": [H0, H0, H1]}, mandate="m")
    check("a head that moves between the App's refusal and the mandate review stops it",
          rc == 1 and "head moved before the mandate approval" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "renamed": ("AGENTS.md", "docs-agents.md")}, mandate="m")
    check("a rename that moves a policy file out of the corpus is refused as policy (B2)",
          rc == 1 and "policy:" in lines[-1] and "AGENTS.md" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "diff_fail": (128, "fatal: bad object")}, mandate="m")
    check("a failing git diff stops the train (B3)", rc == 1 and "files:" in lines[-1] and not approved(calls))
    rc, lines, calls = go({"approve": owned7, "base": (1, "fatal: no merge base")}, mandate="m")
    check("a failing git merge-base stops the train (B3)", rc == 1 and "files:" in lines[-1] and not approved(calls))
    rc, lines, calls = go({}, min_runs=3)
    check("the required-only head wait does not apply --min-runs: the required set is complete "
          "below it, and a head still short of non-required lanes is not held (R9-ADMIT-REQ)",
          rc == 0 and merged(calls))
    for c in ("action_required", "stale"):
        rc, lines, calls = go({"runs": [{"name": "fast", "status": "completed", "conclusion": c, "started_at": "1"}]})
        check(f"{c} is not green", rc == 1 and lines[-1].endswith("red at the head: fast") and not merged(calls))
    rc, lines, calls = go({"runs": green + [{"name": "y", "status": "completed", "conclusion": c, "started_at": "1"}
                                            for c in ("skipped",)] + [{"name": "z", "status": "completed",
                                                                        "conclusion": "neutral", "started_at": "1"}]})
    check("skipped and neutral are green (null control)", rc == 0 and merged(calls))
    check("the CI read pages past the first 100 runs",
          any("--paginate" in c and any("check-runs" in x for x in c) for c in calls))
    rc, lines, calls = go({"contains": [True, True, False]})
    check("main moving after approval and before the merge stops it", rc == 1 and "merge:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"preflight": "  ok       policy corpus -- current"})
    check("a preflight that never says clean stops it", rc == 1 and "preflight:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({}, q=[dict(item, verdict="xyz")])
    check("a queue entry with a malformed verdict sha is refused", rc == 1 and "queue:" in lines[-1])
    # THE TREE THE STUB CANNOT SEE (#1990's RCA). Every check above runs against
    # a stub that answers on a basename, so a script path that no longer exists
    # passes all of them; these read the real tree.
    for name, cands in TOOLS.items():
        check(f"the train's {name} script is in the tree ({' or '.join(cands)})",
              any((ROOT / c).is_file() for c in cands))
    check("the train's mandate reader budget_raise_gate.py is in the tree ("
          + " or ".join(GATE_PATHS) + ")", any((ROOT / c).is_file() for c in GATE_PATHS))
    check(f"the delivery-row directory the train requires, {ROW_DIR}/, is in the tree",
          (ROOT / ROW_DIR).is_dir())
    bare = re.findall(r'self\.run\(\[\s*"bash",\s*"([^"]+)"', Path(__file__).read_text())
    check("every script the train runs resolves through TOOLS, none by a bare path"
          + (f" (bare: {', '.join(bare)})" if bare else ""), not bare)
    # THE RECORD-BEAT HOLD (issue #2302). A record pull request that auto-merges
    # mid-train moves main under it (#2291/#2295/#2299, 2026-10-15, stopped or
    # re-carried #2284/#2290); CI cannot see the train's local pidfile, so the
    # train publishes refs/heads/train-hold while it is live. These read the
    # call/log timeline: the commit and ref create must precede the first merge,
    # and the delete must close the train before its closing line.
    def hold_idx(world: dict, kind: str) -> list[int]:
        stop = {"create": "/git/refs --input -", "update": "/git/refs/heads/train-hold",
                "delete": "/git/refs/heads/train-hold", "commit": "/git/commits"}
        return [i for i, (k, v) in enumerate(world["timeline"])
                if k == "call" and "gh api" in v and stop[kind] in v
                and (kind == "delete") == ("--method DELETE" in v)]

    def tl_idx(world: dict, kind: str, text: str) -> list[int]:
        return [i for i, (k, v) in enumerate(world["timeline"]) if k == kind and v == text]

    w = {"hold_sha": "f" * 40}
    rc, lines, calls = go(w)
    creates, commits = hold_idx(w, "create"), hold_idx(w, "commit")
    deletes = hold_idx(w, "delete")
    merges = [i for i, (k, v) in enumerate(w["timeline"]) if k == "call" and v.startswith("gh pr merge")]
    done = tl_idx(w, "log", "TRAIN DONE")
    check("a real train holds the record beat before its first merge and releases it "
          "before the closing line (issue #2302)",
          bool(rc == 0 and commits and creates and deletes and merges and done)
          and commits[0] < creates[0] < merges[0] < deletes[0] < done[0]
          and "TRAIN HOLD refs/heads/train-hold" in " ".join(lines)
          and "TRAIN HOLD released" in lines)
    w = {"hold_sha": "f" * 40,
         "runs": [{"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"}]}
    rc, lines, calls = go(w)
    deletes = hold_idx(w, "delete")
    stopped = [i for i, (k, v) in enumerate(w["timeline"])
               if k == "log" and v.startswith("TRAIN STOPPED")]
    check("a train stopped mid-queue still releases the hold before its closing line "
          "(a stopped train must not block the record beat)",
          bool(rc == 1 and deletes and stopped) and deletes[-1] < stopped[-1])
    w = {"hold_sha": "f" * 40}
    rc, lines, calls = go(w, q=[dict(item), dict(item, pr=8)], base="batch/rehearsal")
    check("a batch/ rehearsal publishes no hold (null control: it merges nothing into main)",
          rc == 0 and not any(k == "call" and "/git/refs" in v for k, v in w["timeline"]))
    w = {"hold_sha": "f" * 40}
    rc, lines, calls = go(w, q=[dict(item), dict(item, pr=8)])
    creates, updates = hold_idx(w, "create"), hold_idx(w, "update")
    merges = [i for i, (k, v) in enumerate(w["timeline"]) if k == "call" and v.startswith("gh pr merge")]
    check("the hold is refreshed once per queue item, so one long item cannot age it stale",
          rc == 0 and len(creates) == 1 and len(updates) == 2 and len(merges) >= 2
          and merges[0] < updates[1] < merges[1] and max(creates + updates) < hold_idx(w, "delete")[0])
    w = {}  # the API refuses the hold commit: the train must still merge
    rc, lines, calls = go(w)
    check("an unreadable hold commit does not stop the train: logged, no ref, no delete",
          rc == 0 and merged(calls) and not any(k == "call" and "/git/refs" in v
                                                for k, v in w["timeline"])
          and any(ln.startswith("NOT held:") for ln in lines))
    # A WAIT IS THE LONGEST SILENCE (review F1). One CI wait runs to 24 polls
    # of HEARTBEAT_SECONDS, and a --batch proof and a main_green wait are the
    # same loop, so the ref is refreshed from the loop itself: the bound then
    # prices the refresh gap, not a whole wait.
    w = {"hold_sha": "f" * 40, "pending_reads": 1}
    rc, lines, calls = go(w)  # polls=2: read 1 in progress, read 2 green
    reads = [i for i, (k, v) in enumerate(w["timeline"]) if k == "call" and "check-runs" in v]
    check("a CI wait that outlives one poll refreshes the hold mid-wait, so the bound "
          "can be shorter than a wait",
          rc == 0 and merged(calls) and len(reads) >= 2
          and any(reads[0] < u < reads[1] for u in hold_idx(w, "update")))
    # A recarry takes 5-15 min inside app_push's prepr, and --overlap runs one
    # per serial entry BEFORE any wait: a refresh only per item or per wait
    # would let the up-front loop age the ref stale.
    w = {"hold_sha": "f" * 40, "contains": [False]}
    rc, lines, calls = go(w)
    check("a recarry refreshes the hold, so --overlap's up-front recarry loop cannot age it",
          rc == 0 and merged(calls) and len(hold_idx(w, "update")) == 2)
    # `wait-ci` is a bare CI watch, not a train: it has no closing line to
    # release a ref, so it must never publish one.
    w = {"hold_sha": "f" * 40, "runs": green, "pending_reads": 1}
    run0, calls0 = fake(w)
    Train("o/r", Path(tempfile.gettempdir()), None, "", (), 1, run=run0,
          sleep=lambda s: None, polls=2).wait_ci(H0)
    check("a bare wait-ci publishes no hold: only a train or batch arms the ref",
          not any("/git/refs" in " ".join(c) or "/git/commits" in " ".join(c) for c in calls0))
    _batch_self_test(check)
    print(f"merge_train self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def _batch_self_test(check) -> None:
    """`batch` against REAL git: a remote that plays GitHub (its merges are
    `git merge --no-ff` with no driver configured) and the train's clone. The
    fake CI grades a tree by a ratchet: the files under units/ may not outnumber
    cap.txt. Every other GitHub call is a stub keyed on argv."""
    from throwaway_git import throwaway_git_clone, throwaway_git_env, throwaway_git_init  # on sys.path: _self_test
    R0 = "fast (3.14)"

    def g(cwd: Path, *a: str) -> tuple[int, str]:
        r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, env=throwaway_git_env())
        return r.returncode, (r.stdout + r.stderr).strip()

    def world(d: Path, base: str, prs: dict[int, dict[str, str]], cap: int = 2) -> dict:
        R, L = d / "remote", d / "local"
        R.mkdir()
        throwaway_git_init(R, "-q", "-b", base)
        for k, v in (("user.email", "f@example.test"), ("user.name", "f"), ("uploadpack.allowAnySHA1InWant", "true")):
            g(R, "config", k, v)
        tree = {"cap.txt": f"{cap}\n", "units/u0": "0\n", "a.txt": "a\n", "b.txt": "b\n",
                "led.json": "1\n2\n3\n4\n5\n6\n", ".gitattributes": "led.json merge=led\n",
                ".github/workflows/t.yml": "      run: |\n        git checkout \"$PINNED\" -- \\\n          'tools/grader.sh'\n",
                "tools/grader.sh": "g\n",
                "tests/closures.json": json.dumps({"closures": {"tests/ratchet.py": ["tests/ratchet.py", "units/b"]}})}
        for f, t in tree.items():
            (R / f).parent.mkdir(parents=True, exist_ok=True)
            (R / f).write_text(t)
        g(R, "add", "-A")
        g(R, "commit", "-qm", "base")
        heads = {}
        for n, edits in prs.items():
            g(R, "checkout", "-q", "-b", f"pr{n}", base)
            for f, t in {**edits, f"{ROW_DIR}/{n}.md": f"- [#{n}]\n"}.items():
                (R / f).parent.mkdir(parents=True, exist_ok=True)
                (R / f).write_text(t)
            g(R, "add", "-A")
            g(R, "commit", "-qm", f"pr {n}")
            heads[n] = g(R, "rev-parse", "HEAD")[1]
            g(R, "checkout", "-q", base)
        throwaway_git_clone(R, L, "-q")
        for k, v in (("user.email", "f@example.test"), ("user.name", "f"),
                     ("merge.led.driver", "printf LOCAL > %A")):  # a driver GitHub never runs
            g(L, "config", k, v)
        return {"R": R, "L": L, "base": base, "red": set(), "base_sha": g(R, "rev-parse", base)[1], "heads": heads, "merged": {}, "pushed": [], "dispatched": [],
                "approved": [], "gc": 0, "ci_red": "policy-docs", "after_merge": {}, "target": base,
                "required": f"{R0}\npolicy-docs\npr-contract\n"}

    def ci(w: dict, sha: str) -> list[dict]:
        L = w["L"]
        units = g(L, "ls-tree", "-r", "--name-only", sha, "units/")[1].split()
        over = len(units) > int(g(L, "show", f"{sha}:cap.txt")[1] or 0) or sha in w["red"]
        # The --overlap no-jump arm's clock: an entry the world holds PENDING
        # reports its runs in_progress until its head has been polled twice
        # (wait_ci's first poll sees it incomplete, its second green).
        pend = (w.get("cr_reads", {}).get(sha, 0) < 2
                and any(sha == w["heads"].get(p) for p in w.get("pending_prs", ())))
        runs = [{"name": n, "id": i, "status": "in_progress" if pend else "completed", "started_at": "1",
                 "conclusion": "failure" if over and n == w["ci_red"] else "success"}
                for i, n in ((11, R0), (12, "policy-docs"))]
        if sha == w["base_sha"]:  # main's own push run writes every required context
            runs += [{"name": n, "id": 15, "status": "completed", "started_at": "1", "conclusion": "success"}
                     for n in w["required"].split() if n == "never-dispatched"]
            if w.get("pending_main"):  # a fresh push run: a required context still running
                for r in runs:
                    if r["name"] == R0:
                        r["status"], r["conclusion"] = "in_progress", None
        if sha in w["heads"].values():  # a pull-request event writes these; no dispatch does
            runs += [{"name": "pr-contract", "id": 13, "status": "completed", "started_at": "1", "conclusion": "failure"},
                     {"name": "nightly-status", "id": 14, "status": "completed", "started_at": "1", "conclusion": "failure"}]
        if w.get("stuck_nonreq") and sha in w["heads"].values():
            # a non-required lane that never concludes (the composed-proof class)
            runs += [{"name": "composed-proof", "id": 16, "status": "in_progress", "started_at": "1",
                      "conclusion": None}]
        return runs

    def stub(w: dict):
        def run(argv, cwd=ROOT, stdin=None):
            w.setdefault("calls", []).append(argv)  # the hold's order on the primary path
            a = " ".join(argv)
            # THE RECORD-BEAT HOLD on the batch arm: `batch` defaults to
            # `--base main`, so this world can prove the ref is published
            # before anything merges. `hold_sha` empty (the default) is the API
            # refusing, which the batch must survive like the serial train.
            if argv[:2] == ["gh", "api"] and "/git/commits" in a and "/commits/" not in a:
                return 0, w.get("hold_sha", "")
            if argv[:2] == ["gh", "api"] and "/git/refs" in a:
                return 0, "{}"
            if "record_row.py" in a:  # --bot-prs: an open record PR #9 whose guard passes
                w.setdefault("bot_calls", []).append(argv)
                return (0, "9") if "--find-open" in argv else (0, "AUTOMERGE OK #9")
            if argv[:3] == ["gh", "auth", "token"]:
                return 0, "tok"
            if argv[:3] in (["gh", "pr", "view"], ["gh", "pr", "merge"]) and argv[3] == "9":
                if argv[2] == "merge":  # the record PR lands on the base as GitHub would
                    (w["R"] / "rec.txt").write_text("row\n")
                    g(w["R"], "add", "-A")
                    g(w["R"], "commit", "-qm", "record")
                    w["bot_merged"] = g(w["R"], "rev-parse", "HEAD")[1]
                    return 0, ""
                return 0, ("e" * 40 if "headRefOid" in a else
                           f"MERGED {w['bot_merged']}" if w.get("bot_merged") else "OPEN None")
            if argv[0] == "git" and "--delete" in argv:  # the proof branches live only in w["pushed"]
                w["deleted"] = argv[argv.index("--delete") + 1:]
                return w.get("delete_rc", (0, ""))
            if argv[0] == "git":
                if argv[1:3] == ["fetch", "-q"]:
                    return g(w["L"], "fetch", "-q", "origin", *argv[4:])
                return g(w["L"], *argv[1:])
            if argv[:3] == ["gh", "pr", "view"]:
                n = int(argv[3])
                if "headRefOid" in a:
                    return 0, w["heads"][n]
                if "headRefName" in a:
                    return 0, f"pr{n}"  # the branch the world cut for this pull request
                if "baseRefName" in a:
                    return 0, w["target"]
                if "state,mergeCommit" in a:
                    return 0, f"MERGED {w['merged'][n]}" if n in w["merged"] else "OPEN None"
                return 0, "fix: x"
            if argv[:3] == ["gh", "pr", "merge"]:
                n, h = int(argv[3]), argv[-1]
                if w["heads"][n] != h:
                    return 1, "head moved"
                code, o = g(w["R"], "merge", "--no-ff", "--no-edit", "-q", h)
                if code:
                    g(w["R"], "merge", "--abort")
                    return 1, o
                w["after_merge"].get(n, lambda: None)()
                w["merged"][n] = g(w["R"], "rev-parse", "HEAD")[1]
                return 0, ""
            if "check-runs" in a:
                sha = a.split("/commits/")[1].split("/")[0]
                w["cr_reads"] = w.get("cr_reads", {})
                w["cr_reads"][sha] = w["cr_reads"].get(sha, 0) + 1
                return 0, "\n".join(json.dumps(c) for c in ci(w, sha))
            if argv[:2] == ["gh", "api"] and "/commits/" in a:  # bot_tip's read, post-jq
                sha = a.split("/commits/")[1].split()[0].split("?")[0].split("/")[0]
                subj = w.get("bot_heads", {}).get(sha)
                return 0, f"{'github-actions[bot]' if subj else 'tvofi'}\t{subj or 'fix: x'}"
            if "/actions/jobs/" in a and "--allow-escape-sequences" not in argv:
                return 1, "the response contains terminal escape sequences; pass --allow-escape-sequences"
            if "/actions/jobs/11/logs" in a:
                return 0, '2026-10-07T00:00:00Z >>> FAILED: "$PYTHON" tests/ratchet.py'
            if "/actions/jobs/" in a:
                return 0, "no script here"
            if argv[:2] == ["gh", "api"] and a.endswith("rulesets --jq " + argv[-1]):
                return (0, "7") if w["required"] else (1, "HTTP 404")
            if "rulesets/7" in a:
                return 0, w["required"]
            if argv[:3] == ["gh", "workflow", "run"]:
                w["dispatched"].append((argv[3], argv[argv.index("--ref") + 1]))
                return 0, ""
            if "--branch-only" in a:
                w["pushed"].append((argv[-1], g(Path(argv[-2]), "rev-parse", "HEAD")[1]))
                return 0, "app_push: PUSHED"
            if "--carry" in a:
                return 0, "CARRY: yes"
            if "app_approve.sh" in a:
                w["approved"].append(int(argv[-2]))
                return 0, "APPROVED"
            if "--corpus-filter" in a:
                return 0, "\n".join(f for f in (stdin or "").split() if f == "CLAUDE.md")
            if argv[:2] == ["gh", "api"] and "/pulls/" in a and "/reviews" in a:
                n = a.split("/pulls/")[1].split("/")[0]
                w.setdefault("reviews_reads", []).append(n)
                rf = w.get("reviews_for")
                return 0, json.dumps([rf(w["heads"][int(n)]) if rf else []])
            if argv[:2] == ["gh", "api"] and "/issues/comments/" in a:
                return (0, json.dumps(w["mandate"])) if w.get("mandate") else (1, "gh: Not Found (HTTP 404)")
            if argv[:2] == ["gh", "api"] and "/issues/201/comments" in a:
                return 0, json.dumps([w.get("thread", [])])
            if "preflight.sh" in a:
                return 0, "  clean    no refusal"
            if "worktree_gc.sh" in a:
                w["gc"] += 1
            if "remerge_main.sh" in a:
                if not w.get("remerge"):
                    return 0, "MERGE CONFLICT"
                # A real recarry, as remerge_main.sh's app_push --recarry would:
                # merge origin/main in the worktree (the branch is checked out
                # there) and push it, moving the head the stub reports.
                wt, br = Path(argv[3]), argv[4]
                code, o = g(wt, "merge", "--no-edit", "-q", "origin/main")
                if code:
                    return 0, "MERGE CONFLICT"
                sha = g(wt, "rev-parse", "HEAD")[1]
                code, o = g(wt, "push", "-q", "origin", f"HEAD:refs/heads/{br}")
                if code:
                    return 0, "push refused: " + o
                w["heads"][int(argv[2])] = sha
                w.setdefault("recarries", []).append(int(argv[2]))
                return 0, "app_push: PUSHED\nRECARRY: stub (the test world's)"
            return 0, ""
        return run

    def go(prs, base="batch/base", cap=2, setup=None, ignore=("nightly-status", "pr-contract"),
           skip_bad=False, overlap=False, main_moved_tries=0, **opts):
        with tempfile.TemporaryDirectory() as d:
            w = world(Path(d), base, prs, cap)
            (setup or (lambda w: None))(w)
            w["base_sha"] = g(w["R"], "rev-parse", base)[1]
            lines: list[str] = []
            t = Train("o/r", Path(d) / "state", None, "the orchestrator", ignore, 1, run=stub(w),
                      sleep=lambda s: w.get("on_sleep", lambda: None)(), log=lines.append, polls=2, merge_tries=2,
                      base=base, skip_bad=skip_bad, overlap=overlap, main_moved_tries=main_moved_tries, **opts)
            q = [{"pr": n, "verdict": w["heads"][n]} for n in prs]
            rc = t.batch(q, "t")
            w["rc"], w["lines"] = rc, lines
            w["skip_json"] = (json.loads((Path(d) / "state" / "skipped.json").read_text())
                              if (Path(d) / "state" / "skipped.json").is_file() else None)
            w["tree_ok"] = [ln for ln in lines if "tree == proof" in ln]
            w["wt_left"] = [ln for ln in g(w["L"], "worktree", "list", "--porcelain")[1].splitlines()
                            if ln.startswith("worktree ") and "/state/wt/" in ln]
            w["main_tree"] = g(w["R"], "rev-parse", f"{base}^{{tree}}")[1]
            w["led"] = g(w["R"], "show", f"{base}:led.json")[1]
            w["proof_trees"] = [g(w["L"], "rev-parse", f"{sha}^{{tree}}")[1] for _, sha in w["pushed"]]
            w["proof_names"] = [g(w["L"], "ls-tree", "--name-only", sha)[1].split() for _, sha in w["pushed"]]
            return w

    unit = {"units/a": "a\n"}
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}})
    check("batch null control: two clean pull requests are proved once and both merge, the base's tree "
          "equal to P_i after each", w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and len(w["pushed"]) == 1
          and len(w["tree_ok"]) == 2 and w["main_tree"] == (w["proof_trees"] or [""])[-1] and w["lines"][-1] == "TRAIN DONE")
    check("the proof is pushed to batch/<tag>-1 and every DISPATCH workflow runs on that branch",
          w["pushed"][0][0] == "batch/t-1" and sorted(w["dispatched"]) == sorted((f, "batch/t-1") for f, _ in DISPATCH))
    check("batch announces itself in its FIRST line -- tag, pid, base, the queue's PRs -- before any "
          "blocking call, so a daemonized launch is attributable from the log's first line",
          w["lines"][0].startswith("BATCH t pid=") and "base=batch/base" in w["lines"][0]
          and "#1" in w["lines"][0] and "#2" in w["lines"][0])
    check("a rehearsal base approves nothing and collects no worktree", w["approved"] == [] and w["gc"] == 0)
    w = go({1: {"led.json": "X\n2\n3\n4\n5\n6\n"}, 2: {"led.json": "1\n2\n3\n4\n5\nY\n"}})
    check("a merge driver configured in the clone does not reach the proof: GitHub runs none, and the tree "
          "still equals after each merge", w["rc"] == 0 and len(w["tree_ok"]) == 2
          and w["led"] == "X\n2\n3\n4\n5\nY")
    w = go({1: unit, 2: {"units/b": "b\n"}})
    check("PERTURBATION: two pull requests each green alone, together past the ratchet: the proof is red, "
          "neither pair merges as one; the later goes serial and the first merges unproved (D)",
          w["rc"] == 0 and len(w["pushed"]) == 1 and list(w["merged"]) == [1]
          and any("#2 dropped to serial" in ln for ln in w["lines"])
          and any("rehearsal: serial #2 not run" in ln for ln in w["lines"]))
    w = go({1: unit, 2: {"units/b": "b\n"}, 3: {"a.txt": "A\n"}}, setup=lambda w: w.update(ci_red=R0))
    check("a red fast job naming a script owned by one entry's files drops that entry, and the rest are re-proved",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 3] and len(w["pushed"]) == 2
          and any("owned by [2]" in ln for ln in w["lines"]) and len(w["tree_ok"]) == 2)
    w = go({1: unit, 2: {"units/b": "b\n"}, 3: {"a.txt": "A\n"}})
    check("a red with no script: every all-but-one set is proved, and the green one dropping the latest entry merges",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 3] and len(w["pushed"]) == 4
          and any("#2 dropped to serial: the set without it is green" in ln for ln in w["lines"]))
    w = go({1: unit, 2: {"units/b": "b\n"}, 3: {"units/c": "c\n"}})
    check("every all-but-one set red stops the batch with nothing merged",
          w["rc"] == 1 and not w["merged"] and "proof:" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {".github/workflows/t.yml": "x\n"}, 3: {"tests/golden/claimed_drift.txt": "x\n"},
            4: {"tests/x_budgets.json": "{}\n"}, 5: {"tools/grader.sh": "h\n"}, 6: {"b.txt": "B\n"}})
    check("workflow, claim, budget and grader changes go serial, by merge_fastpath's classes",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 6]
          and all(any(f"#{n} serial: {c}" in ln for ln in w["lines"])
                  for n, c in ((2, "workflow"), (3, "claim"), (4, "budget"), (5, "grader"))))
    w = go({1: {"a.txt": "A\n"}, 2: {"a.txt": "B\n"}, 3: {"b.txt": "B\n"}})
    check("an entry that conflicts with one before it goes serial; the rest are proved and merge",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 3] and any("#2 serial: conflict" in ln for ln in w["lines"]))
    w = go({1: {"a.txt": "A\n"}})
    check("D: a batch of one merges at its head with no proof and no dispatch",
          w["rc"] == 0 and list(w["merged"]) == [1] and not w["pushed"] and not w["dispatched"]
          and any(" D: " in ln for ln in w["lines"]) and len(w["tree_ok"]) == 1)
    # THE HOLD ON THE PRIMARY PATH (re-review M8/M10). `batch` defaults to
    # `--base main`, its start publish is the only hold write before a D merge
    # (no wait sleeps, no proof), and nothing else in this suite asked whether
    # the batch armed the ref: deleting the arming and/or the start publish
    # left the suite green. These read the stub's own call order.
    w = go({1: {"a.txt": "A\n"}}, base="main",
           setup=lambda w: w.__setitem__("hold_sha", "f" * 40))
    _calls = w["calls"]
    _commits = [i for i, c in enumerate(_calls)
                if c[:2] == ["gh", "api"] and "/git/commits" in " ".join(c)]
    _refs = [i for i, c in enumerate(_calls)
             if c[:2] == ["gh", "api"] and "git/refs" in " ".join(c)]
    _merges = [i for i, c in enumerate(_calls) if c[:3] == ["gh", "pr", "merge"]]
    check("a real-base batch publishes the record-beat hold before it merges anything "
          "(the primary path is armed, not only the serial one)",
          w["rc"] == 0 and list(w["merged"]) == [1]
          and bool(_commits) and bool(_refs) and bool(_merges)
          and _commits[0] < _refs[0] < _merges[0])
    _bg, brev, bman, _brev_revoke = policy_fixture_builders()
    bnow = datetime.datetime.now(datetime.timezone.utc)
    w = go({1: {"CLAUDE.md": "policy text\n", "a.txt": "A\n"}}, base="main")
    check("batch fallback: a policy head with no owner approval at its head stops admission before any "
          "proof is spent (the no-mandate fallback, on the batch side)",
          w["rc"] == 1 and "policy:" in w["lines"][-1] and "no decisive review" in w["lines"][-1]
          and not w["pushed"] and not w["merged"])
    w = go({1: {"CLAUDE.md": "policy text\n", "a.txt": "A\n"}}, base="main",
           setup=lambda w: w.update(reviews_for=lambda h: [brev(h, bnow)], mandate=bman(bnow)))
    check("batch mandate: the same head is admitted and merges, its approval and mandate RE-READ at the "
          "merge itself (admission reads, land reads again)",
          w["rc"] == 0 and list(w["merged"]) == [1] and w.get("reviews_reads") == ["1", "1"]
          and w["approved"] == [1])

    # --bot-prs in the batch: the record PR merges BEFORE the base is read, so
    # it is under every proof (R16) -- and never from a rehearsal, whose
    # merges reach no main (R14).
    had_token = os.environ.get("GH_TOKEN")
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, base="main", bot_prs=True)
    bot = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("BOT #9 MERGED")), None)
    proof = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("proof ")), None)
    check("batch --bot-prs: the record PR merges before the base is read -- before the proof, "
          "which carries its commit -- and both entries land on that proof",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and bot is not None and proof is not None
          and bot < proof and "rec.txt" in (w["proof_names"] or [[]])[0])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, bot_prs=True)
    check("batch --bot-prs on a batch/ rehearsal looks nothing up and merges no record PR -- a "
          "rehearsal writes nothing to main -- while the rehearsal itself still lands",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and not w.get("bot_calls")
          and not w.get("bot_merged") and not any(ln.startswith("BOT") for ln in w["lines"]))
    if had_token is None:
        os.environ.pop("GH_TOKEN", None)

    def moved(w):
        def push():  # after #1's merge and its tree check, before #2's attempt
            if 1 in w["merged"] and not (w["R"] / "c.txt").exists():
                (w["R"] / "c.txt").write_text("c\n")
                g(w["R"], "add", "-A")
                g(w["R"], "commit", "-qm", "someone else")
        w["on_sleep"] = push
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=moved)
    check("the base moving between two merges stops the batch before the second",
          w["rc"] == 1 and list(w["merged"]) == [1] and "merge:" in w["lines"][-1] and "moved" in w["lines"][-1])
    # MAIN MOVED in the batch: a FOREIGN merge between two of the batch's
    # merges -- the proof was built on a main that is gone -- re-proves what
    # is left on the new main; the batch's own merges are not foreign (the
    # tree-equals-proof check above them is unchanged).
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}, 3: {"units/b": "b\n"}}, setup=moved, main_moved_tries=1)
    check("--main-moved-tries: a foreign merge before the second merge re-proves the rest on the new "
          "main (a fresh proof branch), and they merge on THAT proof's trees",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2, 3]
          and any(ln.startswith("[MAIN-MOVED] before #2's merge: re-proving #2, #3") for ln in w["lines"])
          and [b for b, _ in w["pushed"]] == ["batch/t-1", "batch/t-m1-1"]
          and w["main_tree"] == w["proof_trees"][-1] and len(w["tree_ok"]) == 3)

    def moved_red(w):
        moved(w)
        push = w["on_sleep"]

        def push_red():  # the foreign commit is RED: only a main_green re-read sees it
            push()
            if (w["R"] / "c.txt").exists():
                w["red"].add(g(w["R"], "rev-parse", w["base"])[1])
        w["on_sleep"] = push_red
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}, 3: {"units/b": "b\n"}}, setup=moved_red, main_moved_tries=1)
    check("--main-moved-tries: the FIRST merge on the re-proof re-reads the moved main green -- a "
          "red foreign tip stops it right before #2, nothing landing on a red main",
          w["rc"] == 1 and list(w["merged"]) == [1]
          and any(ln.startswith("[MAIN-MOVED] before #2's merge") for ln in w["lines"])
          and w["lines"][-1].startswith("TRAIN STOPPED main:") and "right before #2" in w["lines"][-1])

    def moving(w):
        def push():  # a foreign commit on EVERY wait once #1 merged: main never settles
            if 1 in w["merged"]:
                n = len(list((w["R"]).glob("f*.txt")))
                (w["R"] / f"f{n}.txt").write_text("f\n")
                g(w["R"], "add", "-A")
                g(w["R"], "commit", "-qm", "someone else again")
        w["on_sleep"] = push
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}, 3: {"units/b": "b\n"}}, setup=moving, main_moved_tries=1)
    check("the batch recovery is bounded: a main still moving after the re-proof stops, naming the spent bound",
          w["rc"] == 1 and list(w["merged"]) == [1] and "re-proof(s) on a moved main spent" in w["lines"][-1])

    def mangled(w):
        def amend():
            (w["R"] / "c.txt").write_text("c\n")
            g(w["R"], "add", "-A")
            g(w["R"], "commit", "-q", "--amend", "--no-edit")
        w["after_merge"][1] = amend
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=mangled)
    check("a merge whose tree is not the proof's stops the batch",
          w["rc"] == 1 and list(w["merged"]) == [1] and "tree:" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=lambda w: w.update(target="main"))
    check("a pull request aimed at another base stops the batch", w["rc"] == 1 and "base:" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=lambda w: w.update(required=""))
    check("required contexts that cannot be read stop the batch before any proof",
          w["rc"] == 1 and not w["pushed"] and "proof:" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
           setup=lambda w: w.update(required=f"{R0}\npolicy-docs\nnever-dispatched\n"))
    check("a required context the head never receives is a TIMEOUT, which stops it rather than "
          "dropping an entry -- now at admission itself, before any proof is spent (R9-ADMIT-REQ)",
          w["rc"] == 1 and not w["merged"] and not w["pushed"] and "ci:" in w["lines"][-1]
          and "TIMEOUT" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, ignore=("nightly-status",))
    check("a red NON-required context (pr-contract, PR_ONLY) does not hold admission: "
          "admission waits only the ruleset's required set, as settle/proof already does (R9-ADMIT-REQ)",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=lambda w: w.update(stuck_nonreq=True))
    check("admission concludes while a non-required lane is still pending: a batch whose required "
          "contexts are green is never held by a lane the ruleset does not require (R9-ADMIT-REQ)",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
           setup=lambda w: w.update(ci_red="policy-docs", red={w["heads"][1], w["heads"][2]}))
    check("a red REQUIRED context still stops admission (the fixed wait judges the required set, "
          "and the ignore list still applies)",
          w["rc"] == 1 and "ci:" in w["lines"][-1] and not w["pushed"] and not w["merged"])
    # A GITHUB_TOKEN tip (R9-RC-AUTOFIX-GOVERNANCE) never joins a proof; it
    # goes SERIAL, where its recarry -- once the batch's own merges moved main
    # -- is the App push that cures it (R10-TICK-TRAIN).
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, base="main",
           setup=lambda w: w.update(remerge=True, bot_heads={w["heads"][2]: "ci: pin killed mutants"}))
    check("a batch entry whose head is a GITHUB_TOKEN bot push goes serial, not into a proof, and "
          "its recarry after #1's merge is the App push: it lands",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and not w["pushed"] and w.get("recarries") == [2]
          and any(ln == "#2 serial: bot-head" for ln in w["lines"]))
    w = go({1: {"a.txt": "A\n"}}, base="main",
           setup=lambda w: w.update(remerge=True, bot_heads={w["heads"][1]: "ci: pin killed mutants"}))
    check("... and with nothing merged before it, main never moved: no recarry is possible and it "
          "is refused as before, [BOT-HEAD] (null control)",
          w["rc"] == 1 and not w["merged"] and "[BOT-HEAD]" in w["lines"][-1] and "GITHUB_TOKEN" in w["lines"][-1])
    w = go({1: unit, 2: {"units/b": "b\n"}, 3: {"b.txt": "B\n"}}, base="main",
           setup=lambda w: w.update(ci_red=R0))
    check("on main: entries are approved, the dropped one goes through the serial run (here its recarry stops)",
          w["rc"] == 1 and sorted(w["merged"]) == [1, 3] and sorted(w["approved"]) == [1, 3]
          and "recarry: #2 " in w["lines"][-1])
    def redmain(w):  # main reddens after both heads were cut green (review-2044's probe)
        (w["R"] / "units/u9").write_text("9\n")
        g(w["R"], "add", "-A")
        g(w["R"], "commit", "-qm", "main reddens")
    w = go({1: {"a.txt": "A\n"}}, cap=1, setup=redmain)
    check("a lone entry is not merged while main's tip is red (D's bound needs a green main)",
          w["rc"] == 1 and not w["merged"] and "main:" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, cap=1, setup=redmain)
    check("a pair on a red main merges nothing and is not bisected: no proof, no drop",
          w["rc"] == 1 and not w["merged"] and not w["pushed"] and not any("dropped" in ln for ln in w["lines"]))
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, cap=1)
    check("... the same pair on a green main is proved and merges (null control)",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and "deleted batch/t-1" in w["lines"][-2]
          and w.get("deleted") == ["batch/t-1"])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, cap=1,
           setup=lambda w: w.update(delete_rc=(1, "error: unable to delete 'batch/t-1'")))
    check("a proof branch the remote would not delete is reported left, never deleted (R9-RO-9a)",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2]
          and w["lines"][-2].startswith("NOT deleted batch/t-1")
          and not any(ln.startswith("deleted ") for ln in w["lines"]))

    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
           setup=lambda w: w.update(on_sleep=lambda: w["red"].add(w["base_sha"])))
    check("main's tip going red after the proof and before the first merge stops it: the gate is re-read right before",
          w["rc"] == 1 and not w["merged"] and "right before #1" in w["lines"][-1])

    def red_after(w):
        w["after_merge"][1] = lambda: w["red"].add(g(w["R"], "rev-parse", "HEAD")[1])
    w = go({1: {"a.txt": "A\n"}, 2: {".github/workflows/t.yml": "x\n"}}, base="main", setup=red_after)
    check("after an unproved merge the train waits for main's run on it, and a red there stops it before anything else lands",
          w["rc"] == 1 and list(w["merged"]) == [1] and "revert it first" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {".github/workflows/t.yml": "x\n"}}, base="main")
    check("... and a green run there lets the serial entry go on (null control: its recarry stops here)",
          w["rc"] == 1 and list(w["merged"]) == [1] and "recarry: #2 " in w["lines"][-1])
    try:
        Train("o/r", Path("."), None, "", (), 1, base="fix/x")
        refused = False
    except ValueError:
        refused = True
    check("a base that is neither main nor batch/ is refused", refused)
    for wf, _ in DISPATCH:
        text = (ROOT / ".github/workflows" / wf).read_text() if (ROOT / ".github/workflows" / wf).is_file() else ""
        check(f"{wf} is in this tree and takes workflow_dispatch", "\n  workflow_dispatch:" in text)

    # --overlap (batch only): the owner's P7 decision. Main advancing after the
    # branches were cut forces every serial entry through a recarry; the test
    # world's remerge does a real one (merge, push, move the head).
    def main_moved(w):
        (w["R"] / "m.txt").write_text("m\n")
        g(w["R"], "add", "-A")
        g(w["R"], "commit", "-qm", "main moved")
    ovl = {1: {".github/workflows/t.yml": "x\n"}, 2: {".github/workflows/u.yml": "y\n"}, 3: {"a.txt": "A\n"}}
    real_remerge = lambda w: (main_moved(w), w.update(remerge=True))
    w = go(ovl, base="main", setup=real_remerge, overlap=True)
    merges = [i for i, ln in enumerate(w["lines"]) if " MERGED " in ln]
    recarries = [i for i, ln in enumerate(w["lines"]) if "recarry: main merged" in ln]
    check("--overlap: every serial entry is re-carried UP FRONT -- both recarries happen "
          "before the first merge, and the entries still land in queue order",
          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and len(recarries) == 2
          and merges and max(recarries) < min(merges))
    check("the recarry worktrees the batch made in the real clone are gone when it ends "
          "(the next run's pre-flight finds no train worktree holding a branch)",
          w["rc"] == 0 and w["wt_left"] == [] and sum(ln.startswith("released ") for ln in w["lines"]) == 2)
    check("--overlap: each up-front recarry announces itself before it runs, so the "
          "5-15 min of app_push prepr per entry is visible mid-flight",
          all(any(ln == f"#{p} overlap: recarry start" for ln in w["lines"]) for p in (1, 2)))
    w = go(ovl, base="main", setup=real_remerge)
    merges = [i for i, ln in enumerate(w["lines"]) if " MERGED " in ln]
    recarries = [i for i, ln in enumerate(w["lines"]) if "recarry: main merged" in ln]
    check("without --overlap the serial path is byte-for-byte today's: the first recarry "
          "happens only after the earlier entries merged (recarry one, wait, merge, next)",
          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2]
          and merges and recarries and min(merges) < min(recarries))
    w = go(ovl, base="main", setup=lambda w: (main_moved(w), w.update(remerge=True, pending_prs={1})),
           overlap=True)
    m1 = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("#1 MERGED")), None)
    m2 = next((i for i, ln in enumerate(w["lines"]) if ln.startswith("#2 MERGED")), None)
    check("--overlap never jumps the queue: #2's contexts were green from the start, yet "
          "still-pending #1 merged first, after waiting a poll for its own",
          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and m1 is not None and m1 < m2
          and w["cr_reads"].get(w["heads"][1], 0) >= 2)
    w = go(ovl, base="main", setup=lambda w: (main_moved(w), w.update(remerge=True),
                                              w["red"].add(g(w["R"], "rev-parse", "main")[1])),
           overlap=True)
    check("--overlap does not wait on main's CI: a red base at step 0 is logged, not fatal",
          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2]
          and any(ln.startswith("OVERLAP: main at") and "logs it and does not wait" in ln
                  for ln in w["lines"]))
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
           setup=lambda w: w.update(pending_main=True), overlap=True)
    check("--overlap starts the batch while main's fresh push run is still in progress: the "
          "pre-admission read is ONE pass, logged, never a completion wait (R9-ADMIT-REQ)",
          w["rc"] == 0 and sorted(w["merged"]) == [1, 2]
          and any(ln.startswith("OVERLAP: ") and "is not green" in ln and "before admission" in ln
                  for ln in w["lines"]))

    w = go({1: {".github/workflows/t.yml": "x\n"}, 2: {"b.txt": "B\n"}, 3: {"a.txt": "A\n"}}, base="main",
           setup=lambda w: w.update(remerge=True, bot_heads={w["heads"][2]: "ci: pin killed mutants"}),
           overlap=True)
    check("--overlap leaves a bot-routed head out of the up-front recarry (main has not moved, so "
          "none is possible); it recarries at its turn, after the earlier merges, and lands",
          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2] and w.get("recarries") == [2]
          and any(ln.startswith("OVERLAP: recarrying #1 up front") for ln in w["lines"]))

    # THE WIRE, not the stubbed runs: wait_ci itself is counted. The arms above
    # exercise the real wait_ci against stubbed gh output, so a main_green that
    # still CALLS the looping wait first (the 2026-10-14 wedge: required
    # contexts with no runs at all never complete) passes every stubbed arm.
    # This one reddens that code: under --overlap the looping wait must not be
    # invoked at main's tip at all; without the flag, exactly once.
    real_wait_ci = Train.wait_ci

    def counted_wait_ci(self, h, only=None, beat=None):
        tip_reads.append(h)
        return real_wait_ci(self, h, only, beat)

    Train.wait_ci = counted_wait_ci
    try:
        tip_reads = []
        w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
               setup=lambda w: w.update(pending_main=True), overlap=True)
        overlap_tip_reads = sum(h == w["base_sha"] for h in tip_reads)
        tip_reads = []
        w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=lambda w: w.update(pending_main=True))
        nonoverlap_tip_reads = sum(h == w["base_sha"] for h in tip_reads)
    finally:
        Train.wait_ci = real_wait_ci
    check("THE WIRE: under --overlap main_green never invokes the looping wait_ci at main's tip "
          "(zero reads; the pre-fix code invoked it once and wedged there); without the flag the "
          "blocking wait is called exactly once (R9-ADMIT-REQ)",
          overlap_tip_reads == 0 and nonoverlap_tip_reads == 1)
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=lambda w: w.update(pending_main=True))
    check("... and without --overlap the same pending main is still waited to completion, which stops it",
          w["rc"] == 1 and "main:" in w["lines"][-1] and "TIMEOUT" in w["lines"][-1]
          and not w["merged"] and w["cr_reads"].get(w["base_sha"], 0) >= 2)
    w = go(ovl, base="main", setup=lambda w: (main_moved(w), w.update(remerge=True, stuck_nonreq=True)),
           overlap=True)
    check("--overlap's at_head wait concludes while a non-required lane stays in_progress at the "
          "head (the composed-proof class): the serial landing waits the required set only (R9-ADMIT-REQ)",
          w["rc"] == 0 and list(w["merged"]) == [3, 1, 2])

    # --skip-bad (batch only): a bad entry is skipped, logged and reported, the
    # train carries on, and the exit code says an entry was left behind.
    plain = _parser().parse_args(["batch", "q.json"])
    new_flags = ("--approval-carry", "--bot-prs", "--pre-flight", "--free-holders")
    flagged = _parser().parse_args(["batch", "q.json", "--skip-bad", "--overlap", *new_flags,
                                    "--main-moved-tries", "0"])
    check("the CLI defaults keep today's train but for the main-moved recovery: none of --skip-bad, "
          "--overlap, --approval-carry, --bot-prs, --pre-flight or --free-holders is on until the flag "
          f"says so; --main-moved-tries is {MAIN_MOVED_TRIES} unless given (0 is today's stop)",
          not any((plain.skip_bad, plain.overlap, plain.approval_carry, plain.bot_prs, plain.pre_flight,
                   plain.free_holders)) and plain.main_moved_tries == MAIN_MOVED_TRIES
          and all((flagged.skip_bad, flagged.overlap, flagged.approval_carry, flagged.bot_prs,
                   flagged.pre_flight, flagged.free_holders)) and flagged.main_moved_tries == 0)
    # THE GUARD THE STUB CANNOT SEE: --bot-prs runs record_row.py's own CLI,
    # the one the record beat runs; these read the real tree.
    rr = (ROOT / "tools/audit/seat/record_row.py").read_text()
    beat = (ROOT / ".github/workflows/tests.yml").read_text()
    check("record_row.py takes every option the bot sweep passes, and the record beat merges behind "
          "the same --automerge-check ... --head ... --require-green guard",
          all(f'"{o}"' in rr for o in ("--find-open", "--owner", "--automerge-check", "--require-green",
                                       "--head", "--pr", "--repo"))
          and "--automerge-check --repo \"$REPO\" --pr \"$NUM\" --head \"$HEAD\"" in beat
          and "guard --require-green" in beat)
    rplain = _parser().parse_args(["run", "q.json"])
    rflag = _parser().parse_args(["run", "q.json", "--approval-carry"])
    check("--approval-carry is a run flag too, and off by default",
          not rplain.approval_carry and rflag.approval_carry)
    badmid = {1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}, 3: {"c.txt": "C\n"}}
    redmid = lambda w: w.update(red={w["heads"][2]})
    w = go(badmid, setup=redmid, skip_bad=True)
    check("--skip-bad: a queue of [good, bad, good] merges the two goods, reports the bad, "
          "and rc is non-zero -- the queue ran to its end with an entry left behind",
          w["rc"] == 1 and sorted(w["merged"]) == [1, 3] and len(w["pushed"]) == 1
          and any(ln.startswith("SKIP #2 ci:") and "red at its head" in ln for ln in w["lines"])
          and any(ln == "SKIP REPORT: 1 skipped of 3" for ln in w["lines"])
          and [s["pr"] for s in (w["skip_json"] or [])] == [2]
          and w["lines"][-1] == "TRAIN DONE")
    w = go({1: {"a.txt": "A\n"}}, base="main", skip_bad=True,
           setup=lambda w: w.update(bot_heads={w["heads"][1]: "ci: pin killed mutants"}))
    check("a skip carries its block class in the line and in skipped.json",
          any(ln.startswith("SKIP #1 ci: [BOT-HEAD]") for ln in w["lines"])
          and (w["skip_json"] or [{}])[0].get("class") == "BOT-HEAD")
    w = go(badmid, setup=redmid)
    check("without --skip-bad the same bad entry still stops the train before anything "
          "merges (the default did not change)",
          w["rc"] == 1 and not w["merged"] and not w["pushed"]
          and any(ln.startswith("TRAIN STOPPED ci:") and "#2" in ln for ln in w["lines"]))
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, cap=1, setup=redmain, skip_bad=True)
    w2 = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
            setup=lambda w: w.update(on_sleep=lambda: w["red"].add(w["base_sha"])), skip_bad=True)
    check("--skip-bad: a red main still stops everything -- at step 0 and through the "
          "merge guard's re-read, both outside the per-entry skip",
          w["rc"] == 1 and not w["merged"] and not w["pushed"]
          and any(ln.startswith("TRAIN STOPPED main:") for ln in w["lines"])
          and w2["rc"] == 1 and not w2["merged"]
          and any(ln.startswith("TRAIN STOPPED main:") and "right before #1" in ln for ln in w2["lines"]))
    # The CLI's default bound too (R4): the next entry's guard sees the tree
    # change and raises MainMoved, which must not re-prove onto that tree.
    for tries in (0, MAIN_MOVED_TRIES):
        w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, setup=mangled, skip_bad=True, main_moved_tries=tries)
        check(f"--skip-bad (--main-moved-tries {tries}): a Stop after the merge API call is fatal for that "
              "entry only -- logged post-merge, never retried, and the next entry is neither merged nor "
              "re-proved onto the unread tree",
              w["rc"] == 1 and list(w["merged"]) == [1] and len(w["pushed"]) == 1
              and not any(ln.startswith("[MAIN-MOVED] before") for ln in w["lines"])
              and any(ln.startswith("SKIP #1 post-merge:") and "tree is not proof" in ln for ln in w["lines"])
              and any(ln.startswith("SKIP #2 merge:") and "moved" in ln for ln in w["lines"])
              and [s["phase"] for s in (w["skip_json"] or [])] == ["post-merge", "merge"])


def _parser() -> argparse.ArgumentParser:
    """The CLI parser, built apart from `main` so the self-test can pin the
    defaults a caller actually gets: both new flags off without the flag."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default="tvofi/heatpump_optimizer")
    common.add_argument("--min-runs", type=int, default=15, help="a head with fewer check runs is not yet fully queued")
    p = argparse.ArgumentParser(prog="merge_train.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    train_opts = argparse.ArgumentParser(add_help=False)
    train_opts.add_argument("--mandate", help="the owner's mandate, as quoted in a code-owned approval; omit to never approve one")
    train_opts.add_argument("--approval-carry", action="store_true",
                            help="after THIS invocation's recarry moves a head h0 -> h with no branch-own file "
                                 "in the h0..h delta, and the owner's latest APPROVED review sits at h0 citing "
                                 "one mandate, re-post that approval at h under a mandate RE-READ in force at "
                                 "the merge; a re-post that fails its byte-identical read-back is a stop. "
                                 "Default: off -- a budget stop stops, however clean the recarry was.")
    train_opts.add_argument("--main-moved-tries", type=int, default=MAIN_MOVED_TRIES,
                            help="a foreign merge that moves main under a settled head is recovered this many "
                                 "times per entry (serial: recarry and wait CI again; batch: re-prove what is "
                                 f"left on the new main); 0 stops as before. Default {MAIN_MOVED_TRIES}.")
    train_opts.add_argument("--bot-prs", action="store_true",
                            help="merge the open record/autofix pull request in the train's own sequence (before "
                                 "the batch's base is read and before each recarry), behind record_row.py's own "
                                 "--automerge-check --require-green guard. Default: off.")
    train_opts.add_argument("--pre-flight", action="store_true",
                            help="run queue_pre_flight.py's admission reads first and PARK a failing entry "
                                 "(skipped.json, rc 1) instead of stopping at its turn. Default: off.")
    train_opts.add_argument("--free-holders", action="store_true",
                            help="when the recarry's branch is checked out in another worktree that is clean "
                                 "(no untracked file) with HEAD at origin/<branch>, detach it and go on. "
                                 "Default: off -- the HOLDER refusal.")
    train_opts.add_argument("--approver-role", default="the orchestrator")
    train_opts.add_argument("--ignore-red", action="append", help="a check whose red does not stop the train (default nightly-status)")
    train_opts.add_argument("--state-dir", default=os.path.join(os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo"), "merge_train"))
    r = sub.add_parser("run", parents=[common, train_opts])
    r.add_argument("queue")
    b = sub.add_parser("batch", parents=[common, train_opts])
    b.add_argument("queue")
    b.add_argument("--base", default="main", help="main, or a batch/ branch to rehearse on (no approval, row, policy or carry read)")
    b.add_argument("--tag", default=time.strftime("%Y%m%d-%H%M%S", time.gmtime()), help="proof branches are batch/<tag>-<n>")
    b.add_argument("--skip-bad", action="store_true",
                   help="an entry refused at its own admission, recarry, carry, CI wait or merge is logged "
                        "SKIP and the train continues; skipped.json and a SKIP REPORT line close the run, "
                        "and rc is 1 when anything was skipped. A red main still stops everything. "
                        "Default: stop at the first refusal.")
    b.add_argument("--overlap", action="store_true",
                   help="do not wait on main's CI before a merge (main_green is log-only) and re-carry "
                        "every serial entry up front so their pull_request runs fire concurrently; each "
                        "lands, in queue order, when its own required contexts conclude. "
                        "Default: recarry one, wait, merge, next.")
    w = sub.add_parser("wait-ci", parents=[common])
    w.add_argument("sha")
    return p


def main(argv: list[str]) -> int:
    # A daemonized launch's stdout is a file, and Python block-buffers a file:
    # every beat and banner sat in an 8KB buffer a kill dropped, and a healthy
    # train read as dead (tvofi, 2026-10-14, tag traintest: 8+ minutes, a log
    # holding only the wrapper's launch line). The instrument is
    # self-sufficient -- it cannot rely on the launcher passing -u -- so the
    # entry point goes line-buffered before anything else runs.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if argv[:1] == ["--self-test"]:
        return _self_test()
    a = _parser().parse_args(argv)
    if a.cmd == "wait-ci":
        red = Train(a.repo, Path("."), None, "", (), a.min_runs).wait_ci(a.sha)
        print("DONE", a.sha, "red:", " ".join(red) or "none")
        return 1 if red else 0
    queue = json.loads(Path(a.queue).read_text())
    ignore = tuple(a.ignore_red) if a.ignore_red else ("nightly-status",)
    opts = dict(approval_carry=a.approval_carry, main_moved_tries=a.main_moved_tries,
                bot_prs=a.bot_prs, pre_flight=a.pre_flight, free_holders=a.free_holders)
    if a.cmd == "batch":
        return Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, ignore, a.min_runs,
                     base=a.base, skip_bad=a.skip_bad, overlap=a.overlap, **opts).batch(queue, a.tag)
    return Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, ignore, a.min_runs,
                 **opts).train(queue)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
