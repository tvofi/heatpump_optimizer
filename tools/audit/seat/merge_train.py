#!/usr/bin/env python3
"""The merge train: land a queue of verdicted pull requests, one at a time or as a batch.

    python3 tools/audit/seat/merge_train.py run <queue.json> [--mandate LABEL]
        [--approver-role ROLE] [--ignore-red NAME]... [--repo OWNER/REPO]
        [--state-dir DIR] [--min-runs N]
    python3 tools/audit/seat/merge_train.py batch <queue.json> [run's options]
        [--base main|batch/<name>] [--tag TAG]
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
                 is refused before any check is read: such a push fires no
                 `pull_request` run at all, so the required contexts only one
                 writes stay ABSENT at it forever and the merge would be
                 refused with nothing saying why (R9-RC-AUTOFIX-GOVERNANCE).
                 The required follow-up is an App push -- step 1's recarry is
                 one, which is why the refusal fires only where the head
                 already contains main;
  3. carry    -- `app_approve.sh --carry <verdict> <head>` must say `CARRY: yes`:
                 the head differs from the verdicted one only by automatic merges;
  4. main     -- `origin/main` is still inside the head after CI (else main moved);
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
                 (missing evidence included), or when a `*_budgets.json` changed
                 (a raise is the owner's, 0013), it stops;
  7. ready, preflight of the title (`REFUSE` stops), merge with
     `--match-head-commit` (retried; `main` re-checked before each attempt),
     the closing-issue read-back, and `worktree_gc.sh`.

It prints one line per step and ends `TRAIN DONE` or `TRAIN STOPPED #<pr> <step>:
<reason>` (exit 1). Every GitHub write is the orchestrator's: run this only
from the orchestrator's machine and identity (decisions 0011, 0013).
Replaces the session-local train3.py / mergewhen.sh / waitci.sh of round 9;
the stale-base guard mergewhen.sh carried is subsumed by step 4, which refuses
any head that does not contain the `main` it merges into.

BATCH (R9-RO-12; tvofi chose B and D of the merge-batching pre-study, 2026-10-07).
Same queue file; no head is re-merged with main. In order:
  0. main     -- every required context at main's tip completed green, or
                 nothing is admitted (a proof on a red main blames its entries);
  1. admit    -- each head's own files (three-dot from main) are classed by
                 merge_fastpath.py's `file_class`: a workflow, claim, grader or
                 any `*_budgets.json` change goes SERIAL. A head whose tip is a
                 GITHUB_TOKEN push is refused here, before any proof is spent
                 (a batch never recarries, so nothing in it can cure one). The
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
                 green, re-read), and main's tree must equal P_i's after;
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
    def __init__(self, step: str, why: str) -> None:
        super().__init__(f"{step}: {why}")
        self.step, self.why = step, why


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


class Train:
    def __init__(self, repo: str, state: Path, mandate: str | None, role: str,
                 ignore: tuple[str, ...], min_runs: int, run=None, sleep=time.sleep,
                 log=print, polls: int = 24, merge_tries: int = 8, base: str = "main") -> None:
        self.repo, self.state, self.mandate, self.role = repo, state, mandate, role
        if base != "main" and not base.startswith("batch/"):
            raise ValueError(f"--base {base}: main, or a batch/ rehearsal base")
        # A batch/ base is a REHEARSAL: no ruleset guards it and nothing merged
        # there reaches main, so the verdict, row, policy and approval reads --
        # which grade a merge into main -- are not made (`batch`).
        self.base, self.real = base, base == "main"
        self.ignore, self.min_runs, self.polls, self.merge_tries = ignore, min_runs, polls, merge_tries
        self.run = run or self._run
        self.sleep, self.log = sleep, log

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
    # re-record commits, the merge-main bot's resolution) fires NO pull_request
    # workflow run at all -- GitHub suppresses events from GITHUB_TOKEN -- so at
    # such a head the only runs are the four the autofix job dispatches, and the
    # required contexts only a pull_request run writes stay ABSENT forever: the
    # head settles, every run it has is green, and the merge is refused with
    # nothing saying why (measured 2026-10-09 at 63084989/#2066 and
    # a9ba0b88/#2070: 4 dispatched runs each, zero pull_request runs, the same
    # 5 of the 17 required contexts of main-protect-checks absent). Dispatch
    # cannot close the gap: governance.yml answers workflow_dispatch, but
    # pr-contract.yml and budget-raise-gate.yml take pull_request/merge_group
    # only. The one follow-up that repairs such a head is an App push, and the
    # train's own recarry (step 1) is one -- so the refusal fires only where the
    # head already contains main and no recarry is possible.
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
                    f"'{subject}'): no pull_request run fires at it, so the required contexts "
                    "only one writes never report -- the head looks settled and is unmergeable, "
                    "with nothing saying why. The required follow-up is an App push at this "
                    "head: run the train again once main has moved (its recarry is one), or "
                    "have the orchestrator App-push the branch")

    def wait_ci(self, h: str, only: "list[str] | None" = None) -> list[str]:
        """The names whose latest run at <h> is not green, once every run completed.

        Green is a fixed list -- success, skipped, neutral -- so a conclusion
        GitHub adds later, or `action_required` and `stale` today, reads red.
        With `only`, those names alone are waited for and judged, and each must
        have a run: a batch proof judges the required contexts (`required`)."""
        for _ in range(self.polls):
            # One JSON object per line across every page: past 100 runs a head
            # would otherwise read as complete on its first page alone.
            code, raw = self.run(["gh", "api", "--paginate", "--jq", ".check_runs[]",
                                  f"repos/{self.repo}/commits/{h}/check-runs?per_page=100"])
            try:
                runs = [json.loads(x) for x in raw.splitlines() if x.strip()] if code == 0 else None
            except ValueError:
                runs = None
            last: dict[str, dict] = {}
            for c in sorted(runs or (), key=lambda c: c.get("started_at") or ""):
                last[c["name"]] = c
            if only is not None and runs is not None and all(
                    last.get(n, {}).get("status") == "completed" for n in only):
                return sorted(n for n in only if last[n]["conclusion"] not in GREEN)
            if only is None and runs and len(runs) >= self.min_runs and all(
                    c.get("status") == "completed" for c in runs):
                return sorted(n for n, c in last.items() if c["conclusion"] not in GREEN)
            self.sleep(POLL_SECONDS)
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
        budgets = [f for f in files if f.endswith("_budgets.json")]
        if budgets:
            raise Stop("approve", f"code-owned and a budget file changed ({', '.join(budgets)}): a raise is the owner's (0013)")
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

    def one(self, item: dict) -> None:
        pr, v = int(item["pr"]), item["verdict"]
        if not is_sha(v):
            raise Stop("queue", f"verdict '{v}' is not a 40-hex sha")
        h = self.head(pr)
        if not is_sha(h):
            raise Stop("head", f"could not read the head: {h[:120]}")
        if not self.contains_main(h):
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
                    raise Stop("recarry", f"could not make a worktree at {wt}")
            body = self.state / f"rb{pr}.md"
            body.write_text(self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "body", "--jq", ".body") + "\n")
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
                h = moved
                self.log(f"#{pr} recarry: app_push refused but the head moved to {h[:8]}; the push landed, not a stop")
            else:
                h = self.head(pr)
            # app_push.sh --recarry's one line: prepr SKIPPED or RUNS, and why.
            path = next((ln.strip() for ln in o.splitlines() if "RECARRY:" in ln), "no RECARRY line")
            self.log(f"#{pr} recarry: main merged, head {h[:8]}; {path}")
        bot = self.bot_tip(h)  # after any recarry: the App push it makes cures a bot head
        if bot:
            raise self.bot_refusal(pr, h, bot)
        red = [n for n in self.wait_ci(h) if n not in self.ignore]
        self.log(f"#{pr} {h[:8]} ci red={red}")
        if red:
            raise Stop("ci", "red at the head: " + ", ".join(red))
        self.run(["git", "fetch", "-q", "origin", h])
        o = self.run(["bash", tool("app_approve"), "--carry", v, h])[1]
        if "CARRY: yes" not in o:
            raise Stop("carry", (o.strip().splitlines() or ["(no output)"])[-1][:200])
        if not self.contains_main(h):
            raise Stop("main", "origin/main moved during CI and is not in the head; run the train again")
        code, base = self.run(["git", "merge-base", "origin/main", h])
        if code or not is_sha(base.strip()):
            raise Stop("files", "git merge-base failed: " + base.strip()[-160:])
        # --no-renames: a rename lists both paths, so moving a policy file out of
        # the corpus still names the policy path it left.
        code, out = self.run(["git", "diff", "--no-renames", "--name-only", base.strip(), h])
        if code:
            raise Stop("files", "git diff failed: " + out.strip()[-160:])
        files = out.split()
        row = f"{ROW_DIR}/{pr}.md"
        if row not in files:
            raise Stop("row", f"#{pr} has no {row} in the three-dot diff; "
                       "the train writes none and the stamp's --require-rows "
                       "bar refuses an unrowed merge")
        def guard() -> None:
            if not self.contains_main(h):
                raise Stop("merge", "origin/main moved before the merge; run the train again")
        self.land(pr, h, item, files, guard)

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
        for _ in range(self.merge_tries):
            self.sleep(30)
            guard()
            self.run(["gh", "pr", "merge", str(pr), "--repo", self.repo, "--merge", "--match-head-commit", h])
            st = self.out("gh", "pr", "view", str(pr), "--repo", self.repo, "--json", "state,mergeCommit",
                          "--jq", '"\\(.state) \\(.mergeCommit.oid)"')
            if st.startswith("MERGED"):
                self.log(f"#{pr} {st}")
                break
        else:
            raise Stop("merge", f"not merged after {self.merge_tries} attempts")
        owner, name = self.repo.split("/")
        q = ('query={repository(owner:"%s",name:"%s"){pullRequest(number:%d){closingIssuesReferences(first:10)'
             "{nodes{number state}}}}}" % (owner, name, pr))
        self.log(f"#{pr} closes {self.out('gh', 'api', 'graphql', '-f', q)[-160:]}")
        if self.real:
            self.run(["bash", tool("worktree_gc"), self.repo])
        return st.split()[-1]

    def train(self, queue: list[dict]) -> int:
        self.state.mkdir(parents=True, exist_ok=True)
        for item in queue:
            try:
                self.one(item)
            except Stop as s:
                self.log(f"TRAIN STOPPED #{item.get('pr')} {s.step}: {s.why}")
                return 1
        self.log("TRAIN DONE")
        return 0

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

    def admit(self, item: dict, base: str, graders: list[str], mf) -> dict:
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
        bot = self.bot_tip(h)  # a batch never recarries, so nothing here can cure a bot head
        if bot:
            raise self.bot_refusal(pr, h, bot)
        self.run(["git", "fetch", "-q", "origin", h])
        files = self.git("diff", "--no-renames", "--name-only", self.git("merge-base", base, h), h).split()
        route = sorted({c for f in files if (c := mf.file_class(f, graders))})
        a = dict(item, pr=pr, head=h, files=files, route=route)
        if route:
            self.log(f"#{pr} serial: {', '.join(route)}")
            return a
        red = [n for n in self.wait_ci(h) if n not in self.ignore]
        if red:
            raise Stop("ci", f"#{pr} red at its head: " + ", ".join(red))
        if self.real:
            o = self.run(["bash", tool("app_approve"), "--carry", v, h])[1]
            if "CARRY: yes" not in o:
                raise Stop("carry", f"#{pr} " + (o.strip().splitlines() or ["(no output)"])[-1][:200])
            if f"{ROW_DIR}/{pr}.md" not in files:
                raise Stop("row", f"#{pr} has no {ROW_DIR}/{pr}.md in the three-dot diff")
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
            self.launch(f"batch/{tag}-{n}", proofs[-1])
            red = self.wait_ci(proofs[-1], only=req)
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
                    self.launch(f"batch/{tag}-{n}", p[-1])
                    subs.append((a, sub, p))
            green = [(a, sub, p) for a, sub, p in subs if not self.wait_ci(p[-1], only=req)]
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
        on such a base (review of #2044: a red main D-merged the wrong entry)."""
        red = self.wait_ci(tip, only=req)
        if red:
            raise Stop("main", f"{self.base} at {tip[:12]} is not green ({', '.join(red)}) {why}; nothing more lands")

    def batch(self, queue: list[dict], tag: str) -> int:
        self.state.mkdir(parents=True, exist_ok=True)
        self.branches: list[str] = []
        try:
            mf = _fastpath()
            self.run(["git", "fetch", "-q", "origin", self.base])
            base = self.git("rev-parse", f"origin/{self.base}")
            req = self.required()
            self.main_green(base, req, "before admission")
            graders = mf.grader_specs(mf.workflow_texts(base, git=lambda *a: self.git(*a)))
            entries = [self.admit(item, base, graders, mf) for item in queue]
            serial = [a for a in entries if a["route"]]
            kept, proofs, dropped = self.settle(tag, base, [a for a in entries if not a["route"]], req)
            lone = len(kept) == 1
            if lone:
                self.log(f"#{kept[0]['pr']} D: a batch of one merges at its verdicted head, unproved; "
                         f"{self.base}'s FULL push run is its gate, and a red there is reverted first")
            prev, tip = base, base
            for a, p in zip(kept, proofs):
                def guard(prev=prev, pr=a["pr"], first=prev == base) -> None:
                    self.run(["git", "fetch", "-q", "origin", self.base])
                    now = self.git("rev-parse", f"origin/{self.base}")
                    if self.tree(now) != self.tree(prev):
                        raise Stop("merge", f"{self.base} moved: its tree is not the one #{pr}'s proof was built on; run the batch again")
                    # Later merges land on a tree this batch's own green proof graded.
                    if first:
                        self.main_green(now, req, f"right before #{pr}'s merge")
                self.land(a["pr"], a["head"], a, a["files"], guard)
                self.run(["git", "fetch", "-q", "origin", self.base])
                tip = self.git("rev-parse", f"origin/{self.base}")
                if self.tree(tip) != self.tree(p):
                    raise Stop("tree", f"after #{a['pr']} {self.base} is {tip[:12]}, whose tree is not proof {p[:12]}'s; "
                               "read that merge before anything else lands")
                self.log(f"#{a['pr']} {self.base} {tip[:8]} tree == proof {p[:8]}")
                prev = p
            order = {int(item["pr"]): i for i, item in enumerate(queue)}
            later = sorted(serial + dropped, key=lambda a: order[a["pr"]])
            if lone and later and self.real:
                # A red push run must point at one merge: the unproved one is graded alone.
                self.main_green(tip, req, f"after #{kept[0]['pr']}'s unproved merge: revert it first")
            if later and not self.real:
                self.log(f"rehearsal: serial {', '.join('#%d' % a['pr'] for a in later)} not run")
            elif later:
                self.log(f"serial: {', '.join('#%d' % a['pr'] for a in later)}")
                for a in later:
                    try:
                        self.one(a)
                    except Stop as s:
                        raise Stop(s.step, f"#{a['pr']} {s.why}") from None
        except Stop as s:
            self.log(f"TRAIN STOPPED {s.step}: {s.why}")
            return 1
        if self.branches:  # the proofs are spent; their shas are in the log above
            code, out = self.run(["git", "push", "-q", "origin", "--delete", *self.branches])
            names = ", ".join(self.branches)
            self.log(f"deleted {names}" if code == 0 else
                     f"NOT deleted {names} (rc={code}: {out.strip()[-160:]}); the merges stand, delete them by hand")
        self.log("TRAIN DONE")
        return 0


# ----------------------------------------------------------------- self-test
def _self_test() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_env, throwaway_git_init
    passed = failed = 0
    H0, H1, V = "a" * 40, "b" * 40, "c" * 40

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def fake(world: dict):
        calls: list[list[str]] = []

        def run(argv, cwd=ROOT, stdin=None):
            calls.append(argv)
            a = " ".join(argv)
            if argv[:3] == ["gh", "pr", "view"] and "headRefOid" in a:
                return 0, world["heads"].pop(0) if len(world["heads"]) > 1 else world["heads"][0]
            if "merge-base --is-ancestor" in a:
                return (0 if world["contains"].pop(0) else 1) if world["contains"] else 0, ""
            if "remerge_main.sh" in a:
                return 0, world.get("remerge", "PUSHED")
            if "check-runs" in a:
                return 0, "\n".join(json.dumps(c) for c in world.get("runs", []))
            if argv[:2] == ["gh", "api"] and "/commits/" in a:  # bot_tip's read, post-jq
                sha = a.split("/commits/")[1].split()[0].split("?")[0].split("/")[0]
                subj = world.get("bot_tips", {}).get(sha)
                return 0, f"{'github-actions[bot]' if subj else 'tvofi'}\t{subj or 'fix: x'}"
            if argv[:3] == ["git", "merge-base", "origin/main"]:
                return world.get("base", (0, "e" * 40 + "\n"))
            if argv[:2] == ["git", "diff"] and len(argv) > 4 and argv[4] == world.get("reviewed"):
                return 0, "\n".join(world.get("content_diff", []))
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
            if "app_approve.sh" in a:
                return world.get("approve", (0, "APPROVED"))
            if argv[:3] == ["gh", "pr", "review"]:
                return 0, "reviewed"
            if "preflight.sh" in a:
                return 0, world.get("preflight", "  clean    no refusal")
            if "state,mergeCommit" in a:
                return 0, world["merge"].pop(0) if world.get("merge") else "MERGED " + "d" * 40
            return 0, ""
        return run, calls

    green = [{"name": "fast", "status": "completed", "conclusion": "success", "started_at": "1"},
             {"name": "nightly-status", "status": "completed", "conclusion": "failure", "started_at": "1"}]
    item = {"pr": 7, "verdict": V, "verdict_comment": "42", "worktree": "/nonexistent-wt", "branch": "fix/x"}

    def go(world: dict, mandate: str | None = None, q=None, min_runs: int = 1,
           wrap=None) -> tuple[int, list[str], list[list[str]]]:
        world.setdefault("heads", [H0])
        world.setdefault("contains", [])
        world.setdefault("runs", green)
        lines: list[str] = []
        run, calls = fake(world)
        if wrap:
            run = wrap(run)
        with tempfile.TemporaryDirectory() as d:
            rc = Train("o/r", Path(d), mandate, "the orchestrator", ("nightly-status",), min_runs, run=run,
                       sleep=lambda s: None, log=lines.append, polls=2, merge_tries=3).train(q or [dict(item)])
            world["approve_body"] = (Path(d) / "approve7.md").read_text() if (Path(d) / "approve7.md").exists() else ""
        return rc, lines, calls

    def merged(calls) -> bool:
        return any(c[:3] == ["gh", "pr", "merge"] for c in calls)

    def approved(calls) -> bool:
        return any(c[:3] == ["gh", "pr", "review"] for c in calls)

    rc, lines, calls = go({})
    check("a green, carried, non-policy pull request merges (null control)", rc == 0 and merged(calls) and lines[-1] == "TRAIN DONE")
    rc, lines, calls = go({"files": ["custom_components/x.py"]})
    check(f"a pull request with no {ROW_DIR}/<N>.md row is refused",
          rc == 1 and "row:" in lines[-1] and f"{ROW_DIR}/7.md" in lines[-1]
          and not merged(calls))
    check("nightly-status red is ignored by default", "red=[]" in " ".join(lines))
    rc, lines, calls = go({"runs": green + [{"name": "typing", "status": "completed", "conclusion": "failure", "started_at": "1"}]})
    check("a red required check stops the train before any approval", rc == 1 and "ci:" in lines[-1] and not merged(calls)
          and not any("app_approve.sh" in " ".join(c) and "--carry" not in c for c in calls))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "completed", "conclusion": "failure", "started_at": "1"},
                                    {"name": "fast", "status": "completed", "conclusion": "success", "started_at": "2"}]})
    check("a re-run that went green supersedes the earlier red", rc == 0 and merged(calls))
    rc, lines, calls = go({"runs": [{"name": "fast", "status": "in_progress", "conclusion": None, "started_at": "1"}]})
    check("CI that never completes stops it as TIMEOUT", rc == 1 and "TIMEOUT" in lines[-1])
    rc, lines, calls = go({"carry": "CARRY: no a -> b: a commit of the branch's own"})
    check("a verdict that does not carry stops it", rc == 1 and "carry:" in lines[-1] and not merged(calls))
    rc, lines, calls = go({"contains": [True, False]})
    check("main moving during CI stops it", rc == 1 and "main:" in lines[-1] and not merged(calls))
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
    rc, lines, calls = go({"approve": owned,
                           "files": ["tests/structure_budgets.json", f"{ROW_DIR}/7.md"]},
                          mandate="m")
    check("code-owned with a budget file is not mandate-approved", rc == 1 and "budget" in lines[-1] and not approved(calls))
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
    for way in ("SKIPPED: HEAD is the clean merge", "RUNS: HEAD has 3 parent(s)"):
        rc, lines, calls = go({"contains": [False], "heads": [H0, H1],
                               "remerge": f"app_push: RECARRY: prepr {way}\napp_push: PUSHED"})
        check(f"the recarry logs app_push's path line (prepr {way.split(':')[0]})",
              rc == 0 and any(ln.endswith(f"app_push: RECARRY: prepr {way}") for ln in lines))
    # R9-RC-AUTOFIX-GOVERNANCE: a GITHUB_TOKEN push (author github-actions[bot])
    # fires NO pull_request workflow run at all, so the required contexts only
    # one writes never report at such a head: it settles with them ABSENT and
    # the merge is refused with nothing saying why (measured 2026-10-09 at
    # 63084989/#2066 and a9ba0b88/#2070: 4 dispatched runs each, zero
    # pull_request runs, the same 5 of the 17 required contexts absent).
    BOT = "ci: pin killed mutants"
    rc, lines, calls = go({"bot_tips": {H0: BOT}})
    check("a head whose tip is a GITHUB_TOKEN bot push is refused before CI is even read -- "
          "waiting cannot repair it; the required follow-up is an App push",
          rc == 1 and "ci:" in lines[-1] and "GITHUB_TOKEN" in lines[-1] and BOT in lines[-1]
          and "App push" in lines[-1]
          and not merged(calls) and not approved(calls)
          and not any("check-runs" in " ".join(c) for c in calls))
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
    rc, lines, calls = go({}, q=[dict(item), dict(item, pr=8)])
    check("the queue runs in order", rc == 0 and [c[3] for c in calls if c[:3] == ["gh", "pr", "merge"]] == ["7", "8"])
    rc, lines, calls = go({"runs": green + [{"name": "typing", "status": "completed", "conclusion": "failure", "started_at": "1"}]},
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
    check("fewer check runs than --min-runs is not complete CI", rc == 1 and "TIMEOUT" in lines[-1] and not merged(calls))
    for c in ("action_required", "stale"):
        rc, lines, calls = go({"runs": green + [{"name": "x", "status": "completed", "conclusion": c, "started_at": "1"}]})
        check(f"{c} is not green", rc == 1 and lines[-1].endswith("red at the head: x") and not merged(calls))
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
        runs = [{"name": n, "id": i, "status": "completed", "started_at": "1",
                 "conclusion": "failure" if over and n == w["ci_red"] else "success"}
                for i, n in ((11, R0), (12, "policy-docs"))]
        if sha == w["base_sha"]:  # main's own push run writes every required context
            runs += [{"name": n, "id": 15, "status": "completed", "started_at": "1", "conclusion": "success"}
                     for n in w["required"].split() if n == "never-dispatched"]
        if sha in w["heads"].values():  # a pull-request event writes these; no dispatch does
            runs += [{"name": "pr-contract", "id": 13, "status": "completed", "started_at": "1", "conclusion": "failure"},
                     {"name": "nightly-status", "id": 14, "status": "completed", "started_at": "1", "conclusion": "failure"}]
        return runs

    def stub(w: dict):
        def run(argv, cwd=ROOT, stdin=None):
            a = " ".join(argv)
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
                return 0, "MERGE CONFLICT"
            return 0, ""
        return run

    def go(prs, base="batch/base", cap=2, setup=None, ignore=("nightly-status", "pr-contract")):
        with tempfile.TemporaryDirectory() as d:
            w = world(Path(d), base, prs, cap)
            (setup or (lambda w: None))(w)
            w["base_sha"] = g(w["R"], "rev-parse", base)[1]
            lines: list[str] = []
            t = Train("o/r", Path(d) / "state", None, "the orchestrator", ignore, 1, run=stub(w),
                      sleep=lambda s: w.get("on_sleep", lambda: None)(), log=lines.append, polls=2, merge_tries=2, base=base)
            q = [{"pr": n, "verdict": w["heads"][n]} for n in prs]
            rc = t.batch(q, "t")
            w["rc"], w["lines"] = rc, lines
            w["tree_ok"] = [ln for ln in lines if "tree == proof" in ln]
            w["main_tree"] = g(w["R"], "rev-parse", f"{base}^{{tree}}")[1]
            w["led"] = g(w["R"], "show", f"{base}:led.json")[1]
            w["proof_trees"] = [g(w["L"], "rev-parse", f"{sha}^{{tree}}")[1] for _, sha in w["pushed"]]
            return w

    unit = {"units/a": "a\n"}
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}})
    check("batch null control: two clean pull requests are proved once and both merge, the base's tree "
          "equal to P_i after each", w["rc"] == 0 and sorted(w["merged"]) == [1, 2] and len(w["pushed"]) == 1
          and len(w["tree_ok"]) == 2 and w["main_tree"] == (w["proof_trees"] or [""])[-1] and w["lines"][-1] == "TRAIN DONE")
    check("the proof is pushed to batch/<tag>-1 and every DISPATCH workflow runs on that branch",
          w["pushed"][0][0] == "batch/t-1" and sorted(w["dispatched"]) == sorted((f, "batch/t-1") for f, _ in DISPATCH))
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
    check("a required context the proof never receives is a TIMEOUT, which stops it rather than dropping an entry",
          w["rc"] == 1 and not w["merged"] and "never completed" in w["lines"][-1])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}}, ignore=("nightly-status",))
    check("an entry red at its own head is refused at admission (pr-contract not ignored here)",
          w["rc"] == 1 and "ci:" in w["lines"][-1] and not w["pushed"])
    w = go({1: {"a.txt": "A\n"}, 2: {"b.txt": "B\n"}},
           setup=lambda w: w.update(bot_heads={w["heads"][2]: "ci: pin killed mutants"}))
    check("a batch entry whose head is a GITHUB_TOKEN bot push is refused at admission, "
          "before any proof is spent (R9-RC-AUTOFIX-GOVERNANCE)",
          w["rc"] == 1 and "ci:" in w["lines"][-1] and "GITHUB_TOKEN" in w["lines"][-1]
          and not w["pushed"] and not w["merged"])
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


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default="tvofi/heatpump_optimizer")
    common.add_argument("--min-runs", type=int, default=15, help="a head with fewer check runs is not yet fully queued")
    p = argparse.ArgumentParser(prog="merge_train.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    train_opts = argparse.ArgumentParser(add_help=False)
    train_opts.add_argument("--mandate", help="the owner's mandate, as quoted in a code-owned approval; omit to never approve one")
    train_opts.add_argument("--approver-role", default="the orchestrator")
    train_opts.add_argument("--ignore-red", action="append", help="a check whose red does not stop the train (default nightly-status)")
    train_opts.add_argument("--state-dir", default=os.path.join(os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo"), "merge_train"))
    r = sub.add_parser("run", parents=[common, train_opts])
    r.add_argument("queue")
    b = sub.add_parser("batch", parents=[common, train_opts])
    b.add_argument("queue")
    b.add_argument("--base", default="main", help="main, or a batch/ branch to rehearse on (no approval, row, policy or carry read)")
    b.add_argument("--tag", default=time.strftime("%Y%m%d-%H%M%S", time.gmtime()), help="proof branches are batch/<tag>-<n>")
    w = sub.add_parser("wait-ci", parents=[common])
    w.add_argument("sha")
    a = p.parse_args(argv)
    if a.cmd == "wait-ci":
        red = Train(a.repo, Path("."), None, "", (), a.min_runs).wait_ci(a.sha)
        print("DONE", a.sha, "red:", " ".join(red) or "none")
        return 1 if red else 0
    queue = json.loads(Path(a.queue).read_text())
    ignore = tuple(a.ignore_red) if a.ignore_red else ("nightly-status",)
    if a.cmd == "batch":
        return Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, ignore, a.min_runs,
                     base=a.base).batch(queue, a.tag)
    return Train(a.repo, Path(a.state_dir), a.mandate, a.approver_role, ignore, a.min_runs).train(queue)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
