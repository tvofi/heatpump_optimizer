#!/usr/bin/env python3
"""The heartbeat's dispatch list: one command, read-only, everything needing a decision.

    python3 tools/audit/seat/orchestrator_tick.py [--repo OWNER/REPO] [--checkout DIR]
        [--queue FILE] [--train-log FILE] [--workers-file FILE]
        [--roster-file PATH | --roster-ref GITREF] [--mandate-id N]
        [--stall-hours H] [--behind-max N] [--only TRAIN,PRS,WORKERS,PLAN,MAIN]
        [--json]
    python3 tools/audit/seat/orchestrator_tick.py --self-test

The orchestrator's heartbeat runs this every few minutes. It prints a DISPATCH
LIST -- everything on the board that needs a decision or a seat -- from repo
state, read back from the live sources at tick time, never from memory: the
GitHub API for PR/CI/mergeability state, the tree for rows/carries/pins, the
log file for train state. It does NOT act: no pushes, no merges, no closes.
The queue file's verdict/head fields are the orchestrator's MEMORY; the tick's
job is to verify them against reality (each queued PR's actual state and head
is re-read from the API and diffed against the queue's claim). A section whose
read fails is reported UNREADABLE, never silently skipped -- a silent skip is
the stall class this instrument exists to kill.

Sections, each measured:
  TRAIN   is `merge_train.py` alive (pgrep, self excluded); the active queue's
          entries vs merged-into-main (an entry whose PR is already MERGED is
          stale, to drop); the log tail (--train-log, last 5 lines) and its
          sibling .rc; prepr.sh slots (nudge.md step 8's cap, mechanically).
  PRS     every open PR: the latest check-run per name at its head (transport
          truth: lowercase conclusions, latest-run-wins) as GREEN / RUN / RED;
          RED not answered in the body's ## Red checks; missing delivery row
          in the three-dot diff; a queue verdict with the head moved past it
          and no carry; DIRTY/BLOCKED mergeable state; ZERO check runs at a
          head (the bot-push shape -- approve_held_runs.sh, nudge.md step 11);
          required contexts absent at the head; twin open PRs at one head
          (the shared-head class); a claim-file touch whose `claims-for:` is
          not VERSION; a head left behind main by more than --behind-max
          merges (recarry cost; the default 25 flags only the badly stale --
          the train recarries the rest itself).
  ETA     landing deviations, three sources by precision: the train beat's
          age vs 2x the watcher heartbeat (wedged-or-dead), required lanes
          pending past 2x the recorded critical-path median
          (tests/ci_budgets.json), and the orchestrator's optional ETAS file
          beside the queue (pr=<n> expected-by=<ISO> note=<text>).
  WORKERS the orchestrator's seats file (JSON: seat, pr, head, dispatched_at,
          agent_kind): liveness judged from the WORK the seat was dispatched
          for -- the PR head moved since dispatch (DONE?) or the head is
          unchanged with no new CI completion since dispatch (STALLED?, after a
          --grace-hours window in which no news is normal -- a PR gate runs
          40-55 m). No PR yet is OK inside --stall-hours and STALLED?
          beyond it.
  PLAN    roster groups not done whose predecessors are all done (newly
          unblocked -- start a fixer; nudge.md step 16) and groups blocked,
          naming the blocker. Read through roster_lib, the one schema reader.
  STATE   state-doc staleness, read-only: the handover's updated-for sha vs
          origin/main's tip, and merged PRs since it with no delivery row --
          each nonzero names the owed action (`state_docs.py --push`), the
          write itself stays in the per-merge beat.
  REPLAN  detection only, the item names the owed action: queued-stale
          (pinned verdict vs live head), merged entries to prune, repeated
          TRAIN STOPPED at one pr+step, roster groups contested by an open
          PR's files, done resumes whose commit is not in main, owner-gated
          age, and the throughput stall (verdicted green entry, no train,
          main idle) -- "fire the train".
  MAIN    main's tip sha; any non-green required context (the ruleset re-read
          every tick -- nudge.md step 4: never a remembered list); EVERY
          completed-with-failure lane at the tip, required or not, becomes a
          fixer DISPATCH BRIEF (context, job id + error line, suspected class,
          dispatch instruction; bot lanes lead with the ci-autofix rule) --
          a main-side issue the orchestrator cannot resolve in one short turn
          is fixer work, and the orchestrator's duty is routing, not
          diagnosing; the
          mandate read (budget_raise_gate's own mandate_state, the one reader
          -- the newest grammar-matching owner comment on #201 within
          --mandate-since-days, or exactly --mandate-id); action-pin drift
          (one action pinned at two refs across the workflow set); how far
          the checkout sits behind origin/main.

Ported from dev/governance/roles/nudge.md (superseded here where mechanical):
steps 3 (train status, stale queues), 4 (ruleset re-read), 8 (prepr slots),
11/15 (zero-runs stall, latest-per-name, pending is not a pass), 16 (unblocked
groups, deferred stays deferred), 17 (an ancestor checkout is not current).
Left behind as the orchestrator's judgement, not reportable from tree/API
reads: verdict-bus watching, reviewer-owed dispatch, the 15-minute
worktree-recency rules, post-merge duties, stamps, hold overlays.

API cost, measured: a live full tick made 67 calls at 27 open PRs and 84 at
21 -- roughly two to four calls per open PR (list, body reads, check-runs per
head) plus about a dozen fixed reads (ruleset, mandate, quota, issues,
search) plus one check-run output read per red lane at main's tip, capped
at five. Run it at the orchestrator's five-minute cadence, never in a poll
loop. --only limits which sections run (the mandate and required-context
reads land before PRS and are shared).

Output: the first line is provenance ("BOARD measured from origin/main at
<sha>, <UTC>"); then one line per fact, flagged lines prefixed `-> ` (the
orchestrator acts top-down); `--json` for machine use. Exit 0 unless --self-test fails:
the list is a report, not a gate. The null control (an all-clear board)
prints the empty dispatch list and exits 0.
"""

from __future__ import annotations

import argparse
import datetime
import fnmatch
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SELF = "tools/audit/seat/orchestrator_tick.py"
SEAT = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
RULESET = "main-protect-checks"
#: Per merge_train.py: written only by a PR event; no dispatch writes them.
PR_ONLY = ("closure-scope", "pr-contract", "budget-raise-gate")
GREEN = ("success", "skipped", "neutral")
ROW_DIR = "dev/programme/delivery/"
CLAIM_FILES = ("tests/golden/claimed_drift.txt",
               "tests/golden/card_claimed_drift.txt")
#: The stamp is a commented line in the fixture ("# claims-for: <VERSION>",
#: env_drift's own rule) -- read it the way env_drift does, commented or not.
CLAIMS_FOR = re.compile(r"^#?\s*claims-for:\s*(\S+)", re.M)
HANDOVER = "dev/programme/HANDOVER.md"
UPDATED_FOR = re.compile(r"^updated-for:\s*([0-9a-f]{40})", re.M)
MERGE_PR = re.compile(r"Merge pull request #(\d+)")
CLOSES = re.compile(r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s*"
                    r"(#\d+(?:\s*,\s*#\d+)*)")
#: A negation before the keyword ("does not fix #N", "leaves #N open") is
#: the opposite of a declared close -- the repo's own record documents the
#: class (the closing-keyword traps). Searched in the window since the
#: previous sentence end.
CLOSES_NEGATION = re.compile(r"\b(not|never|leaves?|leave|without|avoid"
                             r"|refrain|instead)\b", re.I)
CODEOWNERS = ".github/CODEOWNERS"
OWNER = "@tvofi"
#: Per-item API caps: a tick must stay cheap steady-state; when an item's
#: candidates exceed the cap it says so and takes the oldest first.
CAP_MERGES = 10
CAP_CLOSES = 10
CAP_REVIEWS = 10
#: The mandate-window warning fires inside this remaining time.
MANDATE_WARN = datetime.timedelta(hours=2)
#: The quota warning fires below this fraction of the hour's core budget.
RATE_FLOOR = 0.2
#: Non-standard conclusions: completed, but neither red nor pending, and
#: they block a merge invisibly (wait-ci's GREEN set does not know them).
NONSTANDARD = ("cancelled", "startup_failure", "timed_out")
#: The mandate citation a review body carries (budget_raise_gate's own shape).
MANDATE_CITE = re.compile(r"\bmandate(?: comment)?:?\s*#?(\d{6,})", re.I)
#: The plan's disposition region (record-check keys on the region, not a row).
PLAN = "dev/programme/plan-2026-09-open-issues.md"
PLAN_REGION = "Delivery-status"
#: The body-treadmill: heads younger than this are not re-take items yet.
BODY_GRACE = datetime.timedelta(hours=1)
CAP_ISSUES = 15
#: The policy corpus the tick's own session loaded at start: a merge to any
#: of these leaves every live session acting on stale text.
POLICY_PATHS = ("CLAUDE.md", "AGENTS.md", "dev/governance/rules",
                "dev/governance/roles", "dev/governance/dimensions",
                ".claude/skills/steward",
                ".github/PULL_REQUEST_TEMPLATE.md", ".cursor/rules")
USES = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+/[\w.-]+)@(\S+)", re.M)
NIGHTLY_CLASS = re.compile(r"autofix|record|nightly|closures", re.I)
#: A main-red lane becomes a FIXER DISPATCH BRIEF, required or not: a
#: main-side issue the orchestrator cannot resolve in one short turn is
#: fixer work (root-cause per defect-root-cause.md runs beside the fix,
#: never inside it) -- the tick's brief is the dispatch seed, and the
#: orchestrator's remaining duty is routing, not diagnosing.
BRIEF_CAP = 5
#: The watcher heartbeat the tick assumes; a train beat older than 2x this
#: while the python is alive is the wedged-or-dead suspicion (a beat-age
#: check flags at minute 16 what a 4h wedge sat inside a 5-min poll loop).
HEARTBEAT_SECONDS = 480
CI_BUDGETS = "tests/ci_budgets.json"
BOT_LANE = re.compile(r"autofix|nightly|record", re.I)
ERR_LINE = re.compile(r"error|FAILED|refused|fail", re.I)
DEFERRED_STAGES = ("deferred", "refused")
UNBLOCKABLE_STAGES = (None, "", "not-started")
#: The shared actions whose pin the whole lane rides; a pin drift on one of
#: these is the class that reddened a composed proof on a twin SHA.
STATE_ACTIONS = ("actions/checkout", "actions/setup-node", "actions/cache",
                 "actions/upload-artifact", "actions/download-artifact",
                 "github/codeql-action/init", "github/codeql-action/analyze")


def _after(done: "str | None", dispatched) -> bool:
    """True when `done` is after `dispatched`: both instants compared as
    instants (a raw string compare breaks on a non-Z zone offset)."""
    if not done:
        return False
    try:
        return (datetime.datetime.fromisoformat(str(done).replace("Z", "+00:00"))
                > datetime.datetime.fromisoformat(
                    str(dispatched).replace("Z", "+00:00")))
    except ValueError:
        return str(done) > str(dispatched)


def _module(name: str, *candidates: str):
    """Import a production module by its tree path -- never a copy of it
    (fixer.md step 17; tests/README.md: a second reading pins nothing)."""
    p = next((ROOT / c for c in candidates if (ROOT / c).is_file()), None)
    if p is None:
        return None
    spec = importlib.util.spec_from_file_location(name, str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Tick:
    """One heartbeat. Every read goes through the injected runners, so the
    self-test drives every arm offline against stubbed gh/git/pgrep."""

    def __init__(self, repo: str, checkout: str, queue: "list[str] | str | None" = None,
                 policy_state: str | None = None,
                 train_log: str | None = None, workers_file: str | None = None,
                 roster_file: str | None = None,
                 roster_ref: str | None = "origin/handoff/audit-r9-fixplan",
                 mandate_id: int | None = None, stall_hours: float = 2.0,
                 grace_hours: float = 0.5, behind_max: int = 25,
                 mandate_since_days: int = 14,
                 now: datetime.datetime | None = None,
                 gh=None, git=None, proc=None, bus=None) -> None:
        self.repo, self.checkout = repo, checkout
        self.queues = ([queue] if isinstance(queue, str) else list(queue or []))
        self.policy_state = policy_state
        self.train_log = train_log
        self.workers_file = workers_file
        self.roster_file, self.roster_ref = roster_file, roster_ref
        self.mandate_id, self.mandate_since_days = mandate_id, mandate_since_days
        self.stall_hours, self.grace_hours = stall_hours, grace_hours
        self.behind_max = behind_max
        self.now = now or datetime.datetime.now(datetime.timezone.utc)
        self._gh, self._git, self._proc, self._bus = gh, git, proc, bus
        self.sections: dict[str, list] = {}
        self.findings: list[dict] = []
        self.api_calls = 0

    # ------------------------------------------------------------- runners
    def gh(self, argv: list[str]) -> tuple[int, str]:
        self.api_calls += 1
        if self._gh is not None:
            return self._gh(argv)
        r = subprocess.run(["gh", *argv], capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def git(self, argv: list[str]) -> tuple[int, str]:
        if self._git is not None:
            return self._git(argv)
        r = subprocess.run(["git", *argv], cwd=self.checkout,
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def proc(self, pattern: str) -> list[tuple[int, str]]:
        if self._proc is not None:
            return self._proc(pattern)
        r = subprocess.run(["pgrep", "-fl", pattern],
                           capture_output=True, text=True)
        out = []
        for line in r.stdout.splitlines():
            pid, _, cmd = line.partition(" ")
            if pid.isdigit() and int(pid) != os.getpid():
                out.append((int(pid), cmd.strip()))
        return out

    def bus(self) -> "tuple[int, list[str]]":
        """bus.sh orphans' read-only output: pushed handoff refs no open PR
        carries. A subprocess over the tree's own instrument, never a copy.
        (rc, stdout lines): stderr is never data -- a subcommand this tree's
        bus.sh does not know (it lands with a PR) prints usage there."""
        if self._bus is not None:
            return self._bus()
        r = subprocess.run(["bash", str(SEAT / "bus.sh"), "orphans"],
                           cwd=self.checkout, capture_output=True, text=True)
        return r.returncode, [l.strip() for l in r.stdout.splitlines()
                              if l.strip()]

    # -------------------------------------------------------------- output
    def line(self, section: str, text: str, flag: bool = False) -> None:
        self.sections.setdefault(section, []).append({"flag": flag, "text": text})
        if flag:
            self.findings.append({"section": section, "text": text})

    def unreadable(self, section: str, what: str, detail: str) -> None:
        self.line(section, f"UNREADABLE: {what} ({detail})", flag=True)

    # ------------------------------------------------------------- helpers
    def check_runs(self, sha: str) -> "list[dict] | None":
        """Every check run at <sha>, one object per line across pages; the
        caller takes latest-per-name by started_at (merge_train.wait_ci's
        own reading, same GREEN set)."""
        code, raw = self.gh(["api", "--paginate", "--jq", ".check_runs[]",
                             f"repos/{self.repo}/commits/{sha}/check-runs?per_page=100"])
        if code:
            return None
        try:
            return [json.loads(x) for x in raw.splitlines() if x.strip()]
        except ValueError:
            return None

    @staticmethod
    def latest(runs: list[dict]) -> dict:
        return {c["name"]: c for c in sorted(runs, key=lambda c: c.get("started_at") or "")}

    @staticmethod
    def judge(runs_by_name: dict) -> tuple[list[str], list[str], list[str]]:
        """(green, running, red): lowercase conclusions, latest-run-wins,
        pending is not a pass (nudge.md step 15)."""
        green, run, red = [], [], []
        for n, c in runs_by_name.items():
            if c.get("status") != "completed":
                run.append(n)
            elif (c.get("conclusion") or "") in GREEN:
                green.append(n)
            else:
                red.append(n)
        return sorted(green), sorted(run), sorted(red)

    def fetch_head(self, head: str) -> bool:
        return self.git(["fetch", "-q", "origin", "main", head])[0] == 0

    def three_dot_files(self, head: str) -> "list[str] | None":
        """The PR's own files: merge-base(main, head) -> head. The three-dot
        diff, never two-dot, which shows main's own newer commits."""
        code, o = self.git(["merge-base", "origin/main", head])
        if code:
            return None
        code, o = self.git(["diff", "--name-only", o.strip(), head])
        return o.split() if code == 0 else None

    @staticmethod
    def body_section(body: str, heading: str) -> str:
        m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)",
                      body, re.M | re.S)
        return m.group(1) if m else ""

    def _queue(self) -> "list[dict] | None":
        out: list[dict] = []
        for path in self.queues:
            try:
                with open(path, encoding="utf-8") as fh:
                    out.extend(json.load(fh))
            except (OSError, ValueError) as e:
                self.unreadable("TRAIN", f"queue {path}", str(e)[:120])
                return None
        return out

    # -------------------------------------------------------------- TRAIN
    @staticmethod
    def _seat_procs(entries: list, needle: str, python_only: bool) -> list:
        """Real seat processes only: a train runs a python binary (an editor
        or grep naming the script is not a train); and no entry may be the
        parent shell wrapper the launcher leaves behind (each live seat
        otherwise counts twice: the zsh -c parent and the child)."""
        out = []
        for pid, cmd in entries:
            if needle not in cmd or "orchestrator_tick" in cmd:
                continue
            if python_only and not re.match(r"\S*python3?\S*\s", cmd):
                continue
            if re.search(r"\b(zsh|bash|sh)\s+-c\b", cmd) or \
                    "shell-snapshots" in cmd:
                continue
            out.append((pid, cmd))
        return out

    def train(self) -> None:
        S = "TRAIN"
        live = self._seat_procs(self.proc("merge_train.py"), "merge_train.py",
                                python_only=True)
        if live:
            self.line(S, f"train alive: pid {live[0][0]} ({len(live)} process(es)); "
                         "it holds every merge -- load nothing else")
            if len(live) > 1:
                self.line(S, f"{len(live)} live merge_train processes -- a merge "
                             "race (two trains interleave); kill all but one",
                          flag=True)
        else:
            self.line(S, "train not alive")
            if self.queues and (q := self._queue()):
                self.line(S, "a nonempty queue file and no live train is a dead "
                         "train (see the queue line below)")
        preprs = self._seat_procs(self.proc("prepr.sh"), "prepr.sh",
                                  python_only=False)
        self.line(S, f"prepr slots: {len(preprs)} running (cap 4)"
                  + ("" if len(preprs) < 4 else " -- do not start a fifth"),
                  flag=len(preprs) >= 4)
        queue = self._queue()
        if queue is not None:
            if not queue:
                self.line(S, "queue empty" if self.queues else "no --queue given")
            stale, open_ = [], 0
            for item in queue:
                pr = item.get("pr")
                code, o = self.gh(["api", f"repos/{self.repo}/pulls/{pr}",
                                   "--jq", ".state"])
                if code:
                    self.unreadable(S, f"state of queued #{pr}", o.strip()[-100:])
                    open_ += 1
                    continue
                if o.strip() == "merged":
                    stale.append(pr)
                else:
                    open_ += 1
            if stale:
                self.line(S, "stale queue entries (already MERGED, drop them): "
                          + ", ".join("#" + str(p) for p in stale), flag=True)
            if open_:
                self.line(S, f"queue holds {open_} unmerged entr(y/ies)"
                          + ("" if live
                             else " -- and no train is running: load one or merge"),
                          flag=not live)
        if not self.train_log:
            self.line(S, "no --train-log given: train state unread")
            return
        try:
            with open(self.train_log, encoding="utf-8", errors="replace") as fh:
                lines = [l.rstrip() for l in fh.readlines() if l.strip()]
        except OSError as e:
            self.unreadable(S, f"train log {self.train_log}", str(e)[:120])
            return
        self.line(S, "log tail: " + " | ".join(lines[-5:]))
        last = lines[-1] if lines else ""
        if "TRAIN STOPPED" in last:
            self.line(S, f"last run stopped: {last}", flag=True)
        rc_path = Path(self.train_log).with_suffix(".rc")
        if rc_path.exists():
            try:
                rc = rc_path.read_text(encoding="utf-8").strip()
            except OSError as e:
                self.unreadable(S, f"rc file {rc_path}", str(e)[:120])
                return
            self.line(S, f"rc: {rc}")
            digits = "".join(ch for ch in rc.split("=")[-1]
                             if ch.isdigit() or ch == "-")
            if digits and int(digits) != 0:
                self.line(S, f"last train exited {digits}", flag=True)

    # ---------------------------------------------------------------- PRS
    def prs(self, required: "list[str] | None") -> None:
        S = "PRS"
        code, o = self.gh(["pr", "list", "--repo", self.repo, "--limit", "200",
                           "--json", "number,headRefOid,headRefName,"
                           "mergeStateStatus,title,createdAt,updatedAt"])
        if code:
            self.unreadable(S, "open pull requests", o.strip()[-120:])
            return
        try:
            prs = json.loads(o)
        except ValueError as e:
            self.unreadable(S, "open pull requests", str(e)[:120])
            return
        self.line(S, f"{len(prs)} open pull request(s)")
        queue = self._queue() or []
        verdicts = {int(i["pr"]): i.get("verdict") for i in queue if i.get("pr")}
        by_head: dict[str, list[int]] = {}
        self._files: dict = getattr(self, "_files", {})
        for pr in sorted(prs, key=lambda p: p["number"]):
            n, head = pr["number"], pr.get("headRefOid") or ""
            if head:
                by_head.setdefault(head, []).append(n)
            self._last_files = None
            self.one_pr(S, pr, verdicts.get(n), required)
            self._files[n] = self._last_files
        self.owner_reviews(S, prs)
        self.body_staleness(S, prs)
        for head, ns in sorted(by_head.items()):
            if len(ns) > 1:
                self.line(S, "twin open PRs at one head "
                          f"{head[:12]}: {', '.join('#' + str(x) for x in ns)}"
                          " (duplicate CI, ambiguous red)", flag=True)

    def one_pr(self, S: str, pr: dict, verdict: "str | None",
               required: "list[str] | None") -> None:
        n, head = pr["number"], pr.get("headRefOid") or ""
        runs = self.check_runs(head)
        if runs is None:
            self.unreadable(S, f"check runs at #{n}", "api read failed")
            run, red = [], []
        else:
            latest = self.latest(runs)
            _, run, red = self.judge(latest)
            if not runs:
                self.line(S, f"#{n}: ZERO check runs at head (the bot-push "
                             "shape: run approve_held_runs.sh, not a fixer)",
                          flag=True)
            elif required is not None:
                absent = [r for r in required
                          if r not in latest and r not in PR_ONLY]
                if absent:
                    self.line(S, f"#{n}: required contexts ABSENT at head: "
                                 f"{', '.join(absent)} (settled? re-dispatch)",
                              flag=True)
        if run and runs:
            pend = getattr(self, "_pending", None)
            if pend is None:
                pend = self._pending = {}
            lat = self.latest(runs)
            for nm in run:
                pend[(n, nm)] = (lat[nm].get("started_at"), head)
        if red:
            latest = self.latest(runs or [])
            for name in red:
                if (latest.get(name, {}).get("conclusion") or "") in NONSTANDARD:
                    self.line(S, f"#{n}: rerun {name} on PR #{n} "
                                 f"({latest[name]['conclusion']}) -- not red, "
                                 "not pending, but it blocks the merge "
                                 "invisibly", flag=True)
        state = "GREEN" if not run and not red else (
            f"RUN:{','.join(run)}" if run else f"RED:{','.join(red)}")
        self.line(S, f"#{n} [{pr.get('headRefName')}] {state}")
        if red:
            code, o = self.gh(["pr", "view", str(n), "--repo", self.repo,
                               "--json", "body", "--jq", ".body"])
            if code:
                self.unreadable(S, f"body of #{n}", o.strip()[-100:])
            else:
                missing = [r for r in red
                           if r not in self.body_section(o, "Red checks")]
                if missing:
                    self.line(S, f"#{n}: RED unanswered in ## Red checks: "
                                 f"{', '.join(missing)}", flag=True)
        ms = (pr.get("mergeStateStatus") or "").upper()
        if ms in ("DIRTY", "BLOCKED"):
            self.line(S, f"#{n}: mergeable state {ms}"
                      + (" (the claim-file merge GitHub cannot run: absorb "
                         "main locally with the claimnotes driver)"
                         if ms == "DIRTY" else ""), flag=True)
        if not self.fetch_head(head):
            self.unreadable(S, f"fetch of #{n}'s head", "git fetch failed")
            return
        files = self.three_dot_files(head)
        self._last_files = files
        if files is None:
            self.unreadable(S, f"three-dot diff of #{n}", "git read failed")
        else:
            if not any(f.startswith(ROW_DIR) and f.endswith(".md") for f in files):
                self.line(S, f"#{n}: no delivery row in its three-dot diff",
                          flag=True)
            touched = [f for f in files if f in CLAIM_FILES]
            if touched:
                self.claims(S, n, head, touched)
            code, o = self.git(["rev-list", "--count", f"{head}..origin/main"])
            if code == 0 and o.strip().isdigit() and int(o) > self.behind_max:
                self.line(S, f"#{n}: {o.strip()} commits behind main "
                             "(recarry due before it can merge)", flag=True)
        if verdict and verdict != head:
            code, _ = self.git(["merge-base", "--is-ancestor", verdict, head])
            if code != 0:
                self.line(S, f"#{n}: head moved past the queue's verdict "
                             f"{verdict[:12]} with no carry (re-review or "
                             "re-verdict)", flag=True)
            else:
                self.line(S, f"#{n}: head is verdict {verdict[:12]} plus "
                             "automatic merges (carry is re-checked at merge)")

    def body_staleness(self, S: str, prs: list[dict]) -> None:
        """The body treadmill: a head that moved after the PR's last update.
        One batched GraphQL read for every open PR's updatedAt -- the any-event
        time, an honest PROXY for the body edit (a label-only event between
        the body edit and the head push weakens the signal, never invents it);
        the head commit dates come from the local object db. Heads younger
        than an hour are skipped (the reviewer is still settling)."""
        if not prs:
            return
        owner, name = self.repo.split("/", 1)
        aliases = " ".join(f"p{p['number']}: pullRequest(number: {p['number']})"
                           "{{updatedAt}}" for p in prs[:50])
        code, o = self.gh(["api", "graphql", "-f",
                           "query=query{repository(owner:\"" + owner
                           + "\",name:\"" + name + "\"){" + aliases + "}}"])
        body_at: dict[int, str] = {}
        if code == 0:
            try:
                data = json.loads(o)["data"]["repository"]
                body_at = {int(k[1:]): v.get("updatedAt")
                           for k, v in data.items() if v}
            except (ValueError, KeyError, AttributeError):
                body_at = {}
        head_date: dict[str, str] = {}
        for pr in prs:
            n, head = pr["number"], pr.get("headRefOid") or ""
            at = body_at.get(n)
            if not at:
                continue
            if head not in head_date:
                code2, o2 = self.git(["show", "-s", "--format=%cI", head])
                head_date[head] = o2.strip() if code2 == 0 else ""
            when = head_date[head]
            if not when or when <= at:
                continue
            try:
                age = self.now - datetime.datetime.fromisoformat(
                    when.replace("Z", "+00:00"))
            except ValueError:
                continue
            if age < BODY_GRACE:
                continue
            code3, o3 = self.git(["rev-list", "--count",
                                  f"--since={at}", head])
            k = o3.strip() if code3 == 0 and o3.strip().isdigit() else "?"
            self.line(S, f"#{n}: re-take the body (the head moved {k} "
                         "commit(s) past the PR's last update -- the body-edit "
                         "time is proxied by updatedAt, any PR event)",
                      flag=True)

    def owner_reviews(self, S: str, prs: list[dict]) -> None:
        """Stale owner review: on every open CODE-OWNED PR, the latest tvofi
        APPROVED review's commit_id vs the live head -- a stale one stopped
        the train at approval. Cap {CAP_REVIEWS}, oldest first; a PR whose
        diff is not code-owned costs nothing."""
        lines = self.codeowners()
        if lines is None:
            self.unreadable(S, "CODEOWNERS at origin/main", "git show failed")
            return
        checked = 0
        for pr in sorted(prs, key=lambda p: p.get("createdAt") or ""):
            n, head = pr["number"], pr.get("headRefOid") or ""
            files = (self._files or {}).get(n)
            if files is None or not self.is_code_owned(files, lines):
                continue
            if checked >= CAP_REVIEWS:
                self.line(S, f"owner-review check capped at {CAP_REVIEWS} "
                             "code-owned PRs (oldest first); the rest unchecked "
                             "this tick")
                return
            checked += 1
            code, o = self.gh(["api", f"repos/{self.repo}/pulls/{n}/reviews"])
            if code:
                self.unreadable(S, f"reviews of #{n}", o.strip()[-80:])
                continue
            try:
                reviews = json.loads(o)
            except ValueError:
                self.unreadable(S, f"reviews of #{n}", "bad json")
                continue
            mine = [r for r in reviews
                    if (r.get("user") or {}).get("login") == OWNER[1:]
                    and r.get("state") == "APPROVED"
                    and r.get("commit_id")]
            if not mine:
                self.line(S, f"#{n}: code-owned with no {OWNER} review at any "
                             "head (the approval the ruleset requires is owed)",
                          flag=True)
                continue
            last = mine[-1]
            if last["commit_id"] != head:
                self.line(S, f"#{n}: stale {OWNER} review (at "
                             f"{last['commit_id'][:12]}, head {head[:12]}) -- "
                             "re-point the owner review at the head", flag=True)
            live = getattr(self, "_mandate_live", None)
            m = MANDATE_CITE.search(last.get("body") or "")
            if live and m and int(m.group(1)) != int(live):
                self.line(S, f"#{n}: owner review cites mandate {m.group(1)}, "
                             f"not the in-force mandate {live} -- it approves "
                             "nothing; re-post the review citing the "
                             "in-force mandate", flag=True)

    def codeowners(self) -> "list | None":
        code, o = self.git(["show", f"origin/main:{CODEOWNERS}"])
        if code:
            return None
        out = []
        for line in o.splitlines():
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split()
            out.append((parts[0], parts[1:]))
        return out

    @staticmethod
    def is_code_owned(files: list[str], lines: list) -> bool:
        """Last-matching-pattern-wins, CODEOWNERS' own rule; a pattern with no
        owner or an owner list without the pinned owner leaves the file not
        code-owned. Directory patterns are prefixes; the rest are fnmatch."""
        for f in files or []:
            hit = None
            for pat, owners in lines:
                p = pat.lstrip("/")
                if (pat.endswith("/") and f.startswith(p)) or fnmatch.fnmatch(f, p):
                    hit = owners
            if hit and any(o.startswith(OWNER) for o in hit):
                return True
        return False

    def claims(self, S: str, n: int, head: str, touched: list[str]) -> None:
        """A branch claiming nothing leaves both claim files byte-identical;
        one that touches a claim file must stamp `claims-for:` == VERSION
        (rule 3; VERSION is untouched in branches, rule 4)."""
        try:
            version = (Path(self.checkout) / "VERSION").read_text().strip()
        except OSError as e:
            self.unreadable(S, "VERSION", str(e)[:80])
            return
        for f in touched:
            code, o = self.git(["show", f"{head}:{f}"])
            if code:
                self.unreadable(S, f"{f} at #{n}'s head", "git show failed")
                continue
            m = CLAIMS_FOR.search(o)
            got = m.group(1) if m else "(no claims-for: line)"
            if got != version:
                self.line(S, f"#{n}: {f} claims-for {got} != VERSION {version} "
                             "(stale claim stamp)", flag=True)
            else:
                self.line(S, f"#{n}: claims drift in {f} stamped for VERSION")

    # ------------------------------------------------------------- WORKERS
    def workers(self) -> None:
        S = "WORKERS"
        if not self.workers_file:
            return
        try:
            with open(self.workers_file, encoding="utf-8") as fh:
                workers = json.load(fh)
        except (OSError, ValueError) as e:
            self.unreadable(S, f"workers file {self.workers_file}", str(e)[:120])
            return
        if not workers:
            self.line(S, "no workers dispatched")
        for w in workers:
            self.one_worker(S, w)

    def one_worker(self, S: str, w: dict) -> None:
        seat = w.get("seat") or "?"
        pr, head = w.get("pr"), w.get("head")
        try:
            at = datetime.datetime.fromisoformat(
                str(w.get("dispatched_at", "")).replace("Z", "+00:00"))
        except ValueError:
            self.line(S, f"{seat}: UNREADABLE dispatched_at "
                         f"{w.get('dispatched_at')!r}", flag=True)
            return
        hours = (self.now - at).total_seconds() / 3600.0
        tail = f"({hours:.1f}h since dispatch)"
        if not pr:
            if hours > self.stall_hours:
                self.line(S, f"{seat}: STALLED? no PR pushed after "
                             f"{self.stall_hours}h {tail}", flag=True)
            else:
                self.line(S, f"{seat}: OK (no PR yet, inside stall window) {tail}")
            return
        code, o = self.gh(["api", f"repos/{self.repo}/pulls/{pr}",
                           "--jq", ".head.sha"])
        if code:
            self.unreadable(S, f"head of worker {seat}'s #{pr}", o.strip()[-100:])
            return
        cur = o.strip()
        if head and cur != head:
            self.line(S, f"{seat}: DONE? #{pr}'s head moved since dispatch {tail}",
                      flag=True)
            return
        runs = self.check_runs(cur)
        if runs is None:
            self.unreadable(S, f"check runs at worker {seat}'s #{pr}",
                            "api read failed")
            return
        new_ci = [c.get("name") for c in runs
                  if _after(c.get("completed_at"), w.get("dispatched_at"))]
        if new_ci:
            self.line(S, f"{seat}: OK (CI completed at #{pr}'s head since "
                         f"dispatch: {len(new_ci)} run(s)) {tail}")
        elif hours <= self.grace_hours:
            self.line(S, f"{seat}: OK (recently dispatched, inside the "
                         f"{self.grace_hours}h CI grace) {tail}")
        else:
            self.line(S, f"{seat}: STALLED? head unchanged and no new CI "
                         f"completion since dispatch {tail}", flag=True)

    def _roster(self, S: str):
        """The roster through roster_lib, the one schema reader; (rl, roster)
        or (None, None) with the UNREADABLE line already reported."""
        rl = _module("roster_lib_tick", "tools/audit/seat/roster_lib.py")
        if rl is None:
            self.unreadable(S, "roster", "roster_lib.py not found in the tree")
            return None, None
        if self.roster_file:
            try:
                roster = rl.load_roster_file(self.roster_file)
            except (OSError, ValueError) as e:
                self.unreadable(S, f"roster file {self.roster_file}", str(e)[:120])
                return None, None
        else:
            code, o = self.git(["show", f"{self.roster_ref or 'origin/main'}:"
                                f"{rl.ROSTER_PATH}"])
            if code:
                self.unreadable(S, f"roster at {self.roster_ref}", o.strip()[-120:])
                return None, None
            try:
                roster = json.loads(o)
            except ValueError as e:
                self.unreadable(S, f"roster at {self.roster_ref}", str(e)[:120])
                return None, None
        return rl, roster

    # ---------------------------------------------------------------- PLAN
    def plan(self) -> None:
        S = "PLAN"
        rl, roster = self._roster(S)
        if rl is None:
            return
        groups = rl.groups_of(roster)
        open_g = rl.open_groups(roster)
        self.line(S, f"{len(open_g)} open group(s) of {len(groups)}")
        for gid, g in groups.items():
            if gid not in open_g:
                continue
            stage = (g.get("resume") or {}).get("stage")
            blockers = [a for a in (g.get("after") or []) if a in open_g]
            if stage in DEFERRED_STAGES or g.get("deferred") or g.get("refused"):
                self.line(S, f"{gid}: deferred/refused (stage {stage}) -- "
                             "stays deferred")
            elif blockers:
                self.line(S, f"{gid}: blocked by {', '.join(blockers)} "
                             f"(stage {stage})")
            elif stage in UNBLOCKABLE_STAGES:
                self.line(S, f"{gid}: UNBLOCKED, not started -- start a fixer "
                             f"on {rl.branch_of(g)}", flag=True)
            else:
                self.line(S, f"{gid}: in progress (stage {stage})")

    # ---------------------------------------------------------------- MAIN
    def main(self) -> None:
        S = "MAIN"
        code, o = self.gh(["api", f"repos/{self.repo}/commits/main", "--jq", ".sha"])
        tip = o.strip() if code == 0 else ""
        if not tip:
            self.unreadable(S, "main's tip", o.strip()[-120:] or "api read failed")
            return
        req = self.required(S)
        runs = self.check_runs(tip)
        if runs is None:
            self.unreadable(S, f"check runs at main {tip[:12]}", "api read failed")
        else:
            latest = self.latest(runs)
            green, _, red = self.judge(latest)
            if req is not None:
                absent = [r for r in req if r not in latest and r not in PR_ONLY]
                if absent:
                    self.line(S, f"main {tip[:12]}: required contexts ABSENT: "
                                 f"{', '.join(absent)}", flag=True)
                req_bad = [n for n in red if n in req]
            else:
                req_bad = red
            if req_bad:
                self.line(S, f"main {tip[:12]}: REQUIRED not green: "
                             f"{', '.join(req_bad)} -- a red main admits nothing",
                          flag=True)
            else:
                self.line(S, f"main {tip[:12]} green "
                             f"({len(green)} context(s) concluded green)")
            nightly = [n for n in red
                       if n not in (req or []) and NIGHTLY_CLASS.search(n)]
            if nightly:
                self.line(S, f"main {tip[:12]}: non-required red (nightly/record "
                             f"class): {', '.join(nightly)}", flag=True)
            for i, name in enumerate(red):
                if i >= BRIEF_CAP:
                    self.line(S, f"dispatch briefs capped at {BRIEF_CAP} red "
                                 "lanes this tick; the rest are owed", flag=True)
                    break
                self.line(S, self.red_brief(name, latest.get(name, {})),
                          flag=True)
        self.mandate(S)
        self.pins(S)
        self.policy_drift(S)
        code, o = self.gh(["api", "rate_limit", "--jq", ".resources.core"])
        if code == 0:
            try:
                core = json.loads(o)
                remaining, limit = int(core.get("remaining", 0)), int(core.get("limit", 1))
            except (ValueError, TypeError):
                remaining, limit = 0, 1
            if limit and remaining < RATE_FLOOR * limit:
                self.line(S, f"API quota low: {remaining}/{limit} remaining this "
                             "hour -- the 5-min poll discipline degrades next",
                          flag=True)
        code, o = self.git(["rev-list", "--count", "HEAD..origin/main"])
        if code == 0 and o.strip().isdigit() and int(o) > 0:
            self.line(S, f"checkout is {o.strip()} commit(s) behind origin/main "
                         "(an ancestor checkout is not current)", flag=True)
        elif code != 0:
            self.unreadable(S, "checkout staleness", o.strip()[-80:])

    def policy_drift(self, S: str) -> None:
        """The newest commit on main touching any policy path, remembered in
        a one-line state file beside the queue: when it moved since the last
        tick, every live session is acting on the copy it loaded at start --
        re-read the changed policy files before the next owner-facing claim.
        One git log per tick; the state file is the tick's only write, and it
        lives outside the repo."""
        code, o = self.git(["log", "-1", "--format=%H %ct %s", "origin/main",
                            "--", *POLICY_PATHS])
        if code or not o.strip():
            self.unreadable(S, "the policy corpus's newest commit",
                            o.strip()[-80:])
            return
        sha, ct, subject = (o.strip().split(" ", 2) + ["", ""])[:3]
        prev = None
        if self.policy_state and Path(self.policy_state).exists():
            try:
                prev = Path(self.policy_state).read_text().strip() or None
            except OSError:
                prev = None
        if prev is not None and prev != sha:
            self.line(S, f"policy corpus moved at {sha[:12]} ({subject}): "
                         "re-read the changed policy files from fresh "
                         "origin/main before your next owner-facing claim "
                         "or verdict", flag=True)
        elif prev is None:
            self.line(S, f"policy corpus at {sha[:12]} (first tick: baseline "
                         "recorded)")
        else:
            self.line(S, f"policy corpus unchanged at {sha[:12]}")
        if self.policy_state:
            try:
                Path(self.policy_state).write_text(sha + "\n")
            except OSError as e:
                self.unreadable(S, "policy state file", str(e)[:80])

    def required(self, S: str) -> "list[str] | None":
        """The ruleset's required contexts, re-read every tick (nudge.md step
        4: never a remembered list); merge_train.required's own route. One
        read per tick: MAIN and PRS share it."""
        if getattr(self, "_req", None) is not None:
            return self._req
        code, rid = self.gh(["api", f"repos/{self.repo}/rulesets", "--jq",
                             f'.[] | select(.name == "{RULESET}") | .id'])
        if code == 0 and rid.strip().isdigit():
            code2, o = self.gh(["api", f"repos/{self.repo}/rulesets/{rid.strip()}",
                                "--jq", '.rules[] | select(.type == '
                                '"required_status_checks") | .parameters.'
                                'required_status_checks[].context'])
            if code2 == 0:
                names = sorted({x.strip() for x in o.splitlines() if x.strip()}
                               - set(PR_ONLY))
                if names:
                    self.line(S, f"required contexts ({RULESET}): "
                                 f"{len(names)} read live")
                    self._req = names
                    return names
        self.unreadable(S, "required contexts",
                        f"ruleset {RULESET} could not be read; "
                        "required-absence arms skipped, never guessed")
        return None

    def red_brief(self, name: str, cr: dict) -> str:
        """The fixer dispatch brief for one red lane at main's tip: four
        fields -- the context, the job id and its error line (the check-run's
        own output, one read, capped), the suspected class, and the dispatch
        instruction. Bot lanes lead with the ci-autofix rule and quote the
        job's summary line."""
        cid = cr.get("id")
        summary = text = ""
        if cid:
            code, o = self.gh(["api", f"repos/{self.repo}/check-runs/{cid}",
                               "--jq", ".output"])
            if code == 0:
                try:
                    out = json.loads(o)
                    summary = (out.get("summary") or "").strip()
                    text = (out.get("text") or "").strip()
                except ValueError:
                    pass
        blob = summary + "\n" + text
        err = next((l.strip() for l in blob.splitlines() if ERR_LINE.search(l)),
                   (summary or text or "no error line read"))[:160]
        if re.search(r"closures\.json|UNDER-SCOPED|closure", blob, re.I):
            cls = "gate-file change"
        elif re.search(r"skip-|autofix", blob, re.I):
            cls = "bot-head"
        elif re.search(r"HTTP 4\d\d|API rate|bad credentials", blob, re.I):
            cls = "upstream API shift"
        else:
            cls = "unknown"
        parts = []
        if BOT_LANE.search(name):
            parts.append('ci-autofix: read the bot\'s job summary; a '
                         'repair-in-flight waits, a skip-* summary means the '
                         'repair did not happen and a fixer is dispatched -- '
                         f'summary: "{summary[:160]}"')
        parts.append(f"main-red {name}: job {cid}, error line: \"{err}\"")
        parts.append(f"suspected class: {cls}")
        parts.append("dispatch a fixer seat with this brief; orchestrator "
                     "diagnosis is capped at one short turn (root-cause per "
                     "defect-root-cause.md runs beside the fix, never inside "
                     "it)")
        return " | ".join(parts)

    def mandate(self, S: str) -> None:
        """The one mandate reading, reported for MAIN: the fetch+evaluate
        half is mandate_read(), run BEFORE the PRS section so a stale-review
        or mandate-cite check never reads an unset live id."""
        read = self.mandate_read()
        if read is None:
            return
        g, m, thread, ok, why = read
        self.line(S, f"mandate: {'in force' if ok else 'NOT in force'}: {why}",
                  flag=not ok)
        if ok:
            mm = g.MANDATE_GRAMMAR.fullmatch(
                ((m.get("body") or "").strip().splitlines() or [""])[0].strip())
            until = mm.group(3) if mm else None
            end = None if until in (None, "programme-end") else g._when(until)
            if end is not None:
                left = end - self.now
                if left < MANDATE_WARN:
                    self.line(S, f"mandate window ends in "
                                 f"{left.total_seconds() / 60:.0f} min -- renew "
                                 "with the owner before it lapses mid-train",
                              flag=True)

    def mandate_read(self) -> "tuple | None":
        """The one mandate reading: budget_raise_gate's mandate_state over the
        tracking issue's comments -- the newest grammar-matching owner comment
        within --mandate-since-days, or exactly --mandate-id. The search
        window is stated in the output so a quiet window is never mistaken
        for an all-clear. Cached per tick; (g, m, thread, ok, why), or None
        with the UNREADABLE/no-mandate lines already reported."""
        if getattr(self, "_mandate_cached", None) is not None:
            return self._mandate_cached
        g = _module("budget_raise_gate_tick", "tools/policy/budget_raise_gate.py")
        if g is None or not hasattr(g, "mandate_state"):
            self.unreadable("MAIN", "mandate", "budget_raise_gate.py not importable")
            self._mandate_cached = None
            return None
        S = "MAIN"
        if self.mandate_id:
            code, o = self.gh(["api",
                               f"repos/{self.repo}/issues/comments/{self.mandate_id}"])
            if code:
                self.unreadable(S, f"mandate comment {self.mandate_id}",
                                o.strip()[-100:])
                self._mandate_cached = None
                return None
            try:
                cands, since = [json.loads(o)], None
            except ValueError as e:
                self.unreadable(S, f"mandate comment {self.mandate_id}",
                                str(e)[:100])
                self._mandate_cached = None
                return None
        else:
            start = (self.now - datetime.timedelta(
                days=self.mandate_since_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            cands = self._thread(start)
            if cands is None:
                self._mandate_cached = None
                return None
        cands = [c for c in cands
                 if g._is_owner(c.get("user"))
                 and g.MANDATE_GRAMMAR.fullmatch(
                     ((c.get("body") or "").strip().splitlines()
                      or [""])[0].strip())]
        if not cands:
            self.line(S, f"no mandate-grammar comment by the owner on #201 in "
                         f"the last {self.mandate_since_days}d (searched live "
                         "this tick) -- policy and raise merges refuse",
                      flag=self.mandate_id is None)
            self._mandate_cached = None
            return None
        m = cands[-1]
        thread = self._thread(m.get("created_at") or "", exclude=m.get("id"))
        self._mandate_live = m.get("id")
        ok, why = g.mandate_state(m.get("id"), m, thread or [], self.now,
                                  self.now.isoformat(), when="tick",
                                  covers=g.MANDATE_COVERS_POLICY,
                                  what="policy merging")
        out = (g, m, thread or [], ok, why)
        self._mandate_cached = out
        return out

    def _thread(self, since: str, exclude=None) -> "list | None":
        """The comments a revocation would live in: the tracking issue's
        comments `since` an instant (merge_train._mandate_read's second
        route). None: the read failed and is already reported."""
        code, o = self.gh(["api", "--paginate", "--slurp",
                           f"repos/{self.repo}/issues/201/comments"
                           f"?per_page=100&since={since}"])
        if code:
            self.unreadable("MAIN", f"#201's comments since {since}",
                            o.strip()[-100:])
            return None
        try:
            out = [c for page in json.loads(o) for c in page]
        except ValueError as e:
            self.unreadable("MAIN", f"#201's comments since {since}", str(e)[:100])
            return None
        return [c for c in out if c.get("id") != exclude]

    def pins(self, S: str) -> None:
        """Action-pin drift: one shared action pinned at two different refs
        across the workflow set (the twin-SHA red class)."""
        wf = Path(self.checkout) / ".github" / "workflows"
        if not wf.is_dir():
            self.unreadable(S, "workflow pins", f"no {wf}")
            return
        seen: dict[str, set[str]] = {}
        try:
            files = sorted(p for p in wf.iterdir() if p.suffix in (".yml", ".yaml"))
        except OSError as e:
            self.unreadable(S, "workflow pins", str(e)[:80])
            return
        for p in files:
            try:
                text = p.read_text(encoding="utf-8")
            except OSError as e:
                self.unreadable(S, f"workflow {p.name}", str(e)[:80])
                continue
            for action, ref in USES.findall(text):
                if action in STATE_ACTIONS:
                    seen.setdefault(action, set()).add(ref)
        for action, refs in sorted(seen.items()):
            if len(refs) > 1:
                self.line(S, f"action-pin drift: {action} pinned at "
                             f"{', '.join(sorted(refs))}", flag=True)

    # --------------------------------------------------------------- STATE
    def state(self) -> None:
        """State-doc staleness as a dispatch item, read-only: the handover's
        `updated-for:` sha vs origin/main's tip, and merged PRs since it that
        lack a delivery row at origin/main. The WRITE stays in the per-merge
        beat (state_docs.py --push): a timer push would race merge beats and
        double the truth -- the tick only names the owed action."""
        S = "STATE"
        self.git(["fetch", "-q", "origin", "main"])
        code, o = self.git(["show", f"origin/main:{HANDOVER}"])
        if code:
            self.unreadable(S, f"{HANDOVER} at origin/main", o.strip()[-100:])
            return
        m = UPDATED_FOR.search(o)
        if not m:
            self.line(S, "no updated-for: line in " + HANDOVER
                      + " at origin/main (the line is manual by design)",
                      flag=True)
            return
        sha = m.group(1)
        code, n = self.git(["rev-list", "--count", f"{sha}..origin/main"])
        if code or not n.strip().isdigit():
            self.unreadable(S, "commit count since updated-for", n.strip()[-80:])
            return
        behind = int(n)
        code, o = self.git(["log", "--merges", "--format=%s", f"{sha}..origin/main"])
        missing: list[str] = []
        if code == 0:
            for pr in MERGE_PR.findall(o):
                rc, _ = self.git(["cat-file", "-e",
                                  f"origin/main:{ROW_DIR}{pr}.md"])
                if rc != 0:
                    missing.append(pr)
        if behind == 0 and not missing:
            self.line(S, f"state docs current with origin/main "
                         f"(updated-for {sha[:12]})")
            return
        if behind:
            self.line(S, f"HANDOVER updated-for {sha[:12]} is {behind} "
                         "commit(s) behind origin/main", flag=True)
        if missing:
            self.line(S, "merged PRs without a delivery row at origin/main: "
                      + ", ".join("#" + x for x in missing), flag=True)
        self.line(S, "run python3 tools/audit/seat/state_docs.py --push "
                     "(the write stays in the per-merge beat; the tick only "
                     "names it)", flag=True)
        self.unrecorded(S, sha)
        self.closes(S, sha)

    def unrecorded(self, S: str, since: str) -> None:
        """Merge commits on main with no #201 comment carrying the merge sha:
        the record beat's other half. Cap 10 search calls, stated in the body."""
        code, o = self.git(["log", "--merges", "--format=%H %s",
                            f"-{CAP_MERGES}", "origin/main"])
        if code:
            self.unreadable(S, "recent merge commits", o.strip()[-80:])
            return
        unrec, capped = [], False
        for line in o.splitlines():
            sha, _, subj = line.partition(" ")
            if len(unrec) >= CAP_MERGES:
                capped = True
                break
            # GitHub search is GET-only: the -f POST form 404s, so the
            # method is stated and the self-test's gh stub asserts it.
            code2, o2 = self.gh(["api", "--method", "GET", "search/issues",
                                 "--jq", ".total_count",
                                 "-f", f"q={sha} repo:{self.repo} type:comment"])
            if code2:
                self.unreadable(S, f"#201 search for {sha[:12]}",
                                o2.strip()[-80:])
                break
            if o2.strip() == "0":
                unrec.append(sha[:12])
        if unrec:
            self.line(S, "record beat owed: state_docs.py --push + #201 "
                         "comment for " + ", ".join(unrec), flag=True)
        if capped:
            self.line(S, f"unrecorded-merge check capped at {CAP_MERGES}; "
                         "older merges unchecked this tick")

    def closes(self, S: str, since: str) -> None:
        """Declared Closes vs actually closed, per PR merged in the last 24h
        (the multi-closes-first-only defect: `Closes #A #B` auto-closes only
        #A). Cap 10 PRs, oldest first; 2 calls per PR (stated in the body)."""
        code, o = self.git(["log", "--merges", "--format=%s",
                            "--since=24 hours ago", "origin/main"])
        if code:
            self.unreadable(S, "merges of the last 24h", o.strip()[-80:])
            return
        # git log is newest-first; "oldest first" is the tail of that list
        prs = [x for x in MERGE_PR.findall(o)][-CAP_CLOSES:]
        for n in prs:
            code, body = self.gh(["pr", "view", n, "--repo", self.repo,
                                  "--json", "body", "--jq", ".body"])
            if code:
                self.unreadable(S, f"body of merged #{n}", body.strip()[-80:])
                continue
            clean = re.sub(r"`[^`]*`", " ", body or "")  # code spans are prose
            declared = set()
            for m2 in CLOSES.finditer(clean):
                window = clean[:m2.start()]
                # the clause since the last separator, not the sentence: a
                # negation poisons only the keyword it directly precedes
                sep = max(window.rfind(c) for c in ".;:\n")
                window = window[sep + 1:]
                if CLOSES_NEGATION.search(window):
                    continue  # a negation is the opposite of a declared close
                declared.update(x.lstrip("#")
                                for x in re.findall(r"#(\d+)", m2.group(1)))
            q = ('query{repository(owner:"' + self.repo.split("/")[0]
                 + '",name:"' + self.repo.split("/")[1] + '"){pullRequest(number: '
                 + n + '){closingIssuesReferences(first:10){nodes{number}}}}}')
            code, o2 = self.gh(["api", "graphql", "-f", f"query={q}"])
            if code:
                self.unreadable(S, f"closing issues of merged #{n}",
                                o2.strip()[-80:])
                continue
            try:
                nodes = (json.loads(o2)["data"]["repository"]["pullRequest"]
                         ["closingIssuesReferences"]["nodes"])
            except (ValueError, KeyError) as e:
                self.unreadable(S, f"closing issues of merged #{n}", str(e)[:80])
                continue
            actual = {str(x["number"]) for x in nodes}
            bad = sorted(declared ^ actual, key=lambda x: int(x))
            if bad:
                self.line(S, f"#{n}: closes mismatch (declared {sorted(declared, key=int)} "
                             f"vs closed {sorted(actual, key=int)}) -- check "
                             f"{' '.join('#' + x for x in bad)}", flag=True)

    # -------------------------------------------------------------- REPLAN
    #: A brief path token: a tree path a brief_lint-resolvable citation has
    #: to look like (slash + known top level, extension or trailing slash).
    BRIEF_PATH = re.compile(
        r"\b((?:tests|tools|dev|custom_components|docs|\.github|\.claude)"
        r"/[\w./-]+)")#: Relative path extraction reused in the docstring example.
    STOP_LINE = re.compile(r"TRAIN STOPPED (\w+): #(\d+)")
    #: The stall class that eats afternoons: green+verdicted queue entries
    #: with no live train and no main progress for this long.
    STALL_AFTER = datetime.timedelta(minutes=20)

    def replan(self) -> None:
        """Detection only -- the item names the owed action, the orchestrator
        replans. Seven triggers: queued-stale (pinned verdict vs live head),
        queue-external-merge (prune), repeated stop (same pr+step twice in
        the log: pull the entry, dispatch a fixer), group-contested (a
        roster group's brief paths intersect an open PR's files),
        group-stale (a done resume whose commit is not in main), owner-gated
        age, and the throughput stall (verdicted green entries, no train,
        no main progress)."""
        S = "REPLAN"
        queue = self._queue()
        if queue is None:
            return
        heads: dict[int, str] = {}
        stale = pruned = 0
        for item in queue:
            pr = item.get("pr")
            code, h = self.gh(["api", f"repos/{self.repo}/pulls/{pr}",
                               "--jq", ".head.sha"])
            if code:
                self.unreadable(S, f"head of queued #{pr}", h.strip()[-80:])
                continue
            heads[pr] = h.strip()
            code, st = self.gh(["api", f"repos/{self.repo}/pulls/{pr}",
                                "--jq", ".state"])
            state = st.strip() if code == 0 else ""
            if state == "merged":
                self.line(S, f"#{pr} MERGED -- prune it from the queue", flag=True)
                pruned += 1
            elif item.get("verdict") and heads[pr] != item["verdict"]:
                self.line(S, f"#{pr} QUEUED-STALE: pinned verdict "
                             f"{item['verdict'][:12]} vs live head "
                             f"{heads[pr][:12]} -- re-admit after re-verdict",
                          flag=True)
                stale += 1
        # repeated stop: same pr and step twice in one log
        if self.train_log:
            try:
                text = Path(self.train_log).read_text(encoding="utf-8",
                                                      errors="replace")
            except OSError as e:
                self.unreadable(S, f"train log {self.train_log}", str(e)[:80])
                text = ""
            stops: dict[tuple, int] = {}
            for step, pr in self.STOP_LINE.findall(text):
                stops[(step, pr)] = stops.get((step, pr), 0) + 1
            for (step, pr), n in stops.items():
                if n >= 2:
                    self.line(S, f"#{pr} stopped {n}x at step '{step}' -- pull "
                                 "the entry, dispatch a fixer instead of "
                                 "re-firing", flag=True)
        rl, roster = self._roster(S)
        if rl is not None and roster:
            groups = rl.groups_of(roster)
            open_g = rl.open_groups(roster)
            files: dict[int, list[str]] = dict(getattr(self, "_files", {}) or {})
            if not files and queue:
                # cap the API fetches to queued PRs only
                for item in queue[:CAP_REVIEWS]:
                    code, o = self.gh(["api", f"repos/{self.repo}/pulls/"
                                       f"{item.get('pr')}/files",
                                       "--jq", ".[].filename"])
                    if code == 0:
                        files[item.get("pr")] = o.split()
            # contested: a brief's tree paths inside an open PR's files
            pr_files = {pr: fs for pr, fs in files.items() if fs}
            for gid, g in groups.items():
                if gid not in open_g:
                    continue
                brief_paths = set(self.BRIEF_PATH.findall(g.get("brief") or ""))
                for pr, fs in pr_files.items():
                    if brief_paths & set(fs):
                        self.line(S, f"group {gid} contested by PR #{pr} "
                                     f"({', '.join(sorted(brief_paths & set(fs)))}) "
                                     "-- order the group after the PR or merge "
                                     "it first", flag=True)
                        break
            # stale done resume: commit not in main's history
            for gid, g in groups.items():
                if gid in open_g:
                    continue
                sha = (g.get("resume") or {}).get("commit")
                if sha and len(sha) == 40:
                    code, _ = self.git(["merge-base", "--is-ancestor",
                                        sha, "origin/main"])
                    if code != 0:
                        self.line(S, f"group {gid} resume is done but commit "
                                     f"{sha[:12]} is not in origin/main's "
                                     "history -- re-derive the resume",
                                  flag=True)
            # owner-gated age
            gated = [g for gid, g in groups.items()
                     if gid in open_g and g.get("owner_gate")]
            if gated:
                issues = sorted(i for g in gated for i in (g.get("issues") or []))
                age = ""
                if issues:
                    code, o = self.gh(["api", f"repos/{self.repo}/issues/{issues[0]}",
                                       "--jq", ".created_at"])
                    if code == 0:
                        try:
                            at = datetime.datetime.fromisoformat(
                                o.strip().replace("Z", "+00:00"))
                            age = (f"; oldest issue #{issues[0]} is "
                                   f"{(self.now - at).days}d old")
                        except ValueError:
                            pass
                self.line(S, f"{len(gated)} group(s) blocked on owner "
                             f"disposition{age} -- surface them to the owner",
                          flag=True)
        # throughput stall: verdicted+green entries, no train, no main progress
        if queue and not self._seat_procs(self.proc("merge_train.py"),
                                          "merge_train.py", python_only=True):
            for item in queue:
                pr, v = item.get("pr"), item.get("verdict")
                h = heads.get(pr)
                if not v or h is None or v != h:
                    continue
                runs = self.check_runs(h)
                if runs is None:
                    continue
                green, run, red = self.judge(self.latest(runs))
                if run or red:
                    continue
                code, o = self.git(["log", "-1", "--format=%cI", "origin/main"])
                try:
                    at = datetime.datetime.fromisoformat(
                        o.strip().replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    break
                idle = self.now - at
                if idle > self.STALL_AFTER:
                    self.line(S, f"THROUGHPUT STALL: #{pr} is verdicted and "
                                 f"green at its live head, no train is live, "
                                 f"and main last moved {idle.total_seconds() / 60:.0f}m "
                                 "ago -- fire the train", flag=True)
                break  # one candidate is enough to name the action
        self.dispositions(S)
        self.orphans(S)

    def dispositions(self, S: str) -> None:
        """Every open issue must be disposed in a record artifact: a delivery
        row, a roster group, or the plan's Delivery-status region -- prose and
        comments are not dispositions (the record check keys on the region).
        Cap 15 oldest per tick; local reads after one issues call."""
        code, o = self.gh(["api", "--paginate",
                           f"repos/{self.repo}/issues?state=open&per_page=100",
                           "--jq", '.[] | select(.pull_request == null) | .number'])
        if code:
            self.unreadable(S, "open issues", o.strip()[-80:])
            return
        open_issues = sorted({int(x) for x in o.split() if x.strip().isdigit()})
        if not open_issues:
            return
        rows = set()
        code, o = self.git(["grep", "-oh", "#[0-9]\+", "origin/main", "--",
                            ROW_DIR.rstrip("/")])
        if code == 0:
            rows = {int(x) for x in re.findall(r"#(\d+)", o)}
        plan = set()
        code, o = self.git(["show", f"origin/main:{PLAN}"])
        if code == 0:
            m = re.search(r"^## " + PLAN_REGION + r"\s*$(.*?)(?=^## |\Z)",
                          o, re.M | re.S)
            if m:
                plan = {int(x) for x in re.findall(r"#(\d+)", m.group(1))}
        roster_ids = set()
        rl, roster = self._roster(S)
        if rl is not None and roster:
            text = json.dumps(roster)
            roster_ids = {int(x) for x in re.findall(r"#?(\d{2,6})", text)
                          if int(x) < 5000}
        unaccounted = [n for n in open_issues
                       if n not in rows and n not in plan and n not in roster_ids]
        if len(unaccounted) > CAP_ISSUES:
            self.line(S, f"{len(unaccounted)} open issue(s) with no disposition; "
                         f"naming the {CAP_ISSUES} oldest", flag=True)
        for n in unaccounted[:CAP_ISSUES]:
            self.line(S, f"disposition #{n}: scheduled, deferred, or refused",
                      flag=True)

    def orphans(self, S: str) -> None:
        """bus.sh orphans: pushed handoff refs carrying work no open PR
        carries (the class that sat unnoticed for hours). A non-zero exit is
        the subcommand being unavailable, not data -- ONE finding, never the
        usage text parsed as refs."""
        try:
            rc, refs = self.bus()
        except OSError as e:
            self.unreadable(S, "bus.sh orphans", str(e)[:80])
            return
        if rc != 0:
            self.line(S, f"bus.sh orphans unavailable (exit {rc}): the "
                         "subcommand depends on #2112, unmerged -- fold its "
                         "refs when it lands", flag=True)
            return
        for ref in refs[:20]:
            self.line(S, f"orphaned handoff ref {ref} -- no open PR carries "
                         "it: dispatch or prune", flag=True)

    # ----------------------------------------------------------------- ETA
    def eta(self) -> None:
        """ETA deviation, three sources by precision: the train beat's age
        (log mtime vs 2x the watcher heartbeat while the python is alive --
        wedged-or-dead suspicion); required lanes pending past 2x the
        recorded critical-path median (tests/ci_budgets.json -- the one
        measured baseline; per-lane medians are not invented); and the
        orchestrator's optional ETAS file beside the queue
        (`pr=<n> expected-by=<ISO> note=<text>`), absent file, no findings."""
        S = "ETA"
        live = self._seat_procs(self.proc("merge_train.py"), "merge_train.py",
                                python_only=True)
        if live and self.train_log:
            try:
                age = self.now.timestamp() - Path(self.train_log).stat().st_mtime
            except OSError as e:
                self.unreadable(S, f"train log mtime {self.train_log}",
                                str(e)[:80])
                age = None
            if age is not None:
                if age > 2 * HEARTBEAT_SECONDS:
                    self.line(S, f"train beat stale {age / 60:.0f}m "
                                 f"(threshold {2 * HEARTBEAT_SECONDS // 60}m) "
                                 "while the train python is alive -- "
                                 "wedged-or-dead suspicion: read the log, "
                                 "kill or wait, do not diagnose", flag=True)
                else:
                    self.line(S, f"train beat fresh ({age / 60:.0f}m old)")
        pending = getattr(self, "_pending", None)
        if pending:
            try:
                med = json.loads(
                    (Path(self.checkout) / CI_BUDGETS).read_text()
                ).get("critical_path_minutes")
            except (OSError, ValueError):
                med = None
            if not med:
                self.unreadable(S, "critical_path_minutes",
                                f"{CI_BUDGETS} unreadable at the checkout")
            else:
                for (n, name), (started, sha) in list(pending.items())[:20]:
                    try:
                        st = datetime.datetime.fromisoformat(
                            str(started).replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    mins = (self.now - st).total_seconds() / 60
                    if mins > 2 * med:
                        self.line(S, f"lane {name} at #{n} pending "
                                     f"{mins:.0f}m vs median {med} -- "
                                     "re-run or diagnose", flag=True)
        if self.queues:
            etas = Path(self.queues[0]).parent / "etas.txt"
            if etas.exists():
                try:
                    lines = etas.read_text(encoding="utf-8").splitlines()
                except OSError as e:
                    self.unreadable(S, "etas file", str(e)[:80])
                    lines = []
                for ln in lines:
                    m = re.match(r"\s*pr=(\d+)\s+expected-by=(\S+)\s+note=(.*)",
                                 ln)
                    if not m:
                        continue
                    try:
                        by = datetime.datetime.fromisoformat(
                            m.group(2).replace("Z", "+00:00"))
                    except ValueError:
                        self.line(S, f"etas line unreadable: {ln[:60]}",
                                  flag=True)
                        continue
                    if by < self.now:
                        self.line(S, f"ETA missed for #{m.group(1)}: expected "
                                     f"{m.group(2)}, note: {m.group(3).strip()}",
                                  flag=True)

    # ----------------------------------------------------------------- run
    def run(self, only: "list[str] | None" = None) -> dict:
        # the board's provenance line: the sha and time this tick read
        self.git(["fetch", "-q", "origin", "main"])
        code, o = self.git(["rev-parse", "origin/main"])
        self.provenance = {"sha": o.strip() if code == 0 else "",
                           "at": self.now.isoformat()}
        order = ["TRAIN", "PRS", "ETA", "WORKERS", "PLAN", "MAIN", "STATE",
                 "REPLAN"]
        todo = [s for s in order if not only or s in only]
        for s in todo:  # stable section order in the report
            self.sections.setdefault(s, [])
        req = None
        if "MAIN" in todo and "PRS" in todo:
            code, o = self.gh(["api", f"repos/{self.repo}/commits/main",
                               "--jq", ".sha"])
            if code == 0 and o.strip():
                req = self.required("MAIN")
            # the mandate read lands before PRS: the stale-review and
            # mandate-cite checks read the live id, and PRS runs first
            self.mandate_read()
        for s in todo:
            if s == "TRAIN":
                self.train()
            elif s == "PRS":
                self.prs(req)
            elif s == "ETA":
                self.eta()
            elif s == "WORKERS":
                self.workers()
            elif s == "PLAN":
                self.plan()
            elif s == "MAIN":
                self.main()
            elif s == "STATE":
                self.state()
            elif s == "REPLAN":
                self.replan()
        return self.report()

    def report(self) -> dict:
        return {"repo": self.repo, "generated_at": self.now.isoformat(),
                "measured_from": getattr(self, "provenance", None),
                "api_calls": self.api_calls, "findings": self.findings,
                "sections": self.sections}


def render(report: dict) -> str:
    """The compact text form: one line per fact, `-> ` on a flagged finding.
    The first line is the board's own provenance: a stale board names the
    sha and time it was measured from."""
    out = []
    m = report.get("measured_from") or {}
    out.append("BOARD measured from origin/main at "
               + (m.get("sha") or "?")[:12] + ", " + str(m.get("at") or "?"))
    for section, lines in report["sections"].items():
        out.append(f"== {section} ==")
        for l in lines:
            out.append(("-> " if l["flag"] else "   ") + l["text"])
    if not report["findings"]:
        out.append("DISPATCH LIST: empty (nothing needs a decision)")
    else:
        out.append(f"DISPATCH LIST: {len(report['findings'])} finding(s)")
    return "\n".join(out)


# ------------------------------------------------------------- self-test
class Stub:
    """A stubbed runner: handlers keyed by substrings of the joined argv
    (every string must sit in it) or callables; first match wins; an
    unmatched call fails LOUDLY so an arm cannot pass on a silent default."""

    def __init__(self) -> None:
        self.h: list = []
        self.calls: list[list] = []

    def on(self, match, rc=0, out=""):
        self.h.append((match, rc, out))
        return self

    def __call__(self, argv):
        self.calls.append(list(argv))
        hay = " ".join(argv)
        for m, rc, out in self.h:
            if callable(m):
                if m(argv):
                    return rc, out
            elif all(x in hay for x in
                     (m if isinstance(m, (tuple, list)) else (m,))):
                return rc, out
        return 1, f"NO STUB for {' '.join(argv[:5])}"


NOW = datetime.datetime(2026, 10, 12, 18, 0, 0, tzinfo=datetime.timezone.utc)


def iso(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


H1, H2, V = "a" * 40, "b" * 40, "c" * 40


def run_obj(name, status="completed", conclusion="success",
            started=NOW, done=NOW, cid=None) -> dict:
    return {"name": name, "status": status, "conclusion": conclusion,
            "id": cid or (sum(map(ord, name)) * 7 + 4100000000),
            "started_at": iso(started),
            "completed_at": iso(done) if status == "completed" else None}


def pr_obj(n, head, ms="CLEAN", branch=None) -> dict:
    return {"number": n, "headRefOid": head, "headRefName": branch or f"fix/{n}",
            "mergeStateStatus": ms, "title": "t", "createdAt": iso(NOW),
            "updatedAt": iso(NOW)}


def check(label: str, arms: list[tuple[str, bool]]) -> tuple[int, int]:
    for name, ok in arms:
        if not ok:
            print(f"  FAIL {label}: {name}")
    return len(arms), sum(1 for _, ok in arms if not ok)


def self_test() -> int:
    total = failed = 0
    g = _module("budget_raise_gate_tick", "tools/policy/budget_raise_gate.py")
    gate_ok = g is not None and hasattr(g, "mandate_state")
    owner = ({"login": g.OWNER_LOGIN, "id": g.OWNER_ID, "type": g.OWNER_TYPE}
             if gate_ok else {})
    mid = 4100000001

    def mandate_body(start: str, until: str) -> str:
        return (f"MANDATE: agents may approve as {owner.get('login')}, scope all, "
                f"from {start} until {until}")

    MAN = {"id": mid, "user": owner,
           "body": mandate_body(iso(NOW - datetime.timedelta(days=1)),
                                iso(NOW + datetime.timedelta(days=1))),
           "created_at": iso(NOW - datetime.timedelta(days=1)),
           "updated_at": iso(NOW - datetime.timedelta(days=1)),
           f"issue_url": f"https://api.github.com/repos/{g.DEFAULT_REPO}/issues/201"}

    def tick(prs=None, runs_at=None, states=None, queue=None, bodies=None,
             train_log=None, workers=None, roster=None, behind=0,
             required_names=("tests", "closures"), gh_extra=None,
             with_mandate=True, handover=H1, merges="", merges24="",
             rows="", behind_handover=0,
             reviews=None, search_counts=None, rate=(4000, 5000),
             graphql=None, procs=None, body_upd=None,
             head_commit_at=None, open_issues="", grep_rows=None,
             plan_text="", bus_refs=None, bus_rc=0, policy_now=None,
             policy_state=None, codeowners_text=None, **kw) -> Tick:
        """A Tick over stubbed gh/git/proc; everything defaults to all-clear."""
        prs = prs if prs is not None else []
        runs_at, states, bodies = runs_at or {}, states or {}, bodies or {}
        gh = Stub()
        for m, rc2, out in (gh_extra or []):
            gh.on(m, rc=rc2, out=out)
        gh.on(("pr", "list"), out=json.dumps(prs))
        gh.on("commits/main", out=H1)
        if required_names is not None:
            gh.on(".[] | select(.name", out="42")
            gh.on("rulesets/42", out="\n".join(required_names))
        else:
            gh.on("rulesets", rc=1, out="no ruleset")
        for sha, runs in runs_at.items():
            gh.on(f"commits/{sha}/check-runs",
                  out="\n".join(json.dumps(r) for r in runs))
        for pr, (state, head) in states.items():
            gh.on((f"pulls/{pr} ", "--jq", ".state"), out=state)
            gh.on((f"pulls/{pr} ", "--jq", ".head.sha"), out=head)
        for n, body in bodies.items():
            gh.on((f"view {n} ", "--jq", ".body"), out=body)
        if with_mandate and gate_ok:
            gh.on("issues/201/comments", out=json.dumps([[MAN]]))
        gh.on("rate_limit", out=json.dumps({"remaining": rate[0],
                                            "limit": rate[1]}))
        for pr, rv in (reviews or {}).items():
            gh.on(f"pulls/{pr}/reviews", out=json.dumps(rv))
        # GitHub search answers GET only: a stub that 404s any search call
        # NOT carrying --method GET, so an arm fails loudly on the POST form
        gh.on(lambda argv: "search/issues" in argv and "--method" not in argv,
              rc=1, out="HTTP 404: search is GET-only")
        for q, total in (search_counts or {}).items():
            gh.on(("--method", "GET", "search/issues", f"q={q}"),
                  out=str(total))
        gh.on(("--method", "GET", "search/issues"), out="1")
        for q, nodes in (graphql or {}).items():
            gh.on("closingIssuesReferences", out=json.dumps(
                {"data": {"repository": {"pullRequest":
                 {"closingIssuesReferences": {"nodes": nodes}}}}}))
        if body_upd is not None:
            gh.on("updatedAt", out=json.dumps(
                {"data": {"repository": {f"p{n}": {"updatedAt": at}}
                          for n, at in body_upd.items()}}))
        else:
            gh.on("updatedAt", out='{"data":{"repository":{}}}')
        gh.on("issues?state=open", out=open_issues)
        git = Stub()
        git.on(("fetch",), out="")
        git.on(("merge-base", "--is-ancestor"), rc=0)
        git.on(("merge-base", "origin/main"), out=V)
        git.on(("diff", "--name-only"), out=kw.pop("files", "dev/programme/delivery/9.md"))
        git.on(("grep",), rc=0 if grep_rows else 1, out=grep_rows or "")
        git.on(f"origin/main:{PLAN}", out=plan_text)
        git.on(("show", "-s"), out=head_commit_at or iso(NOW - datetime.timedelta(hours=2)))
        git.on(("--format=%H %ct %s",),
               out=f"{policy_now or 'f' * 40} {int(NOW.timestamp())} the policy subject")
        git.on(("rev-list", "--count", f"{handover}..origin/main"),
               out=str(behind_handover))
        git.on(("rev-list", "--count", f"{H1}..origin/main"), out=str(behind))
        git.on(("rev-list",), out="0")
        git.on(f"origin/main:{CODEOWNERS}",
               out=codeowners_text or "/CLAUDE.md @tvofi\n")
        git.on(f"origin/main:{HANDOVER}", out=f"updated-for: {handover}\n")
        git.on(("--merges", "--since=24 hours ago"), out=merges24)
        git.on(("--merges", "--format=%H %s"), out=merges)
        git.on(("--merges",), out=rows)
        git.on(("grep",), rc=0 if grep_rows else 1, out=grep_rows or "")
        git.on(f"origin/main:{PLAN}", out=plan_text)
        git.on(("show", "-s"), out=head_commit_at or iso(NOW - datetime.timedelta(hours=2)))
        git.on(("--format=%H %ct %s",),
               out=f"{policy_now or 'f' * 40} {int(NOW.timestamp())} the policy subject")
        git.on(("rev-list", "--count", f"{handover}..origin/main"),
               out=str(behind_handover))
        git.on(("cat-file", "-e"), rc=1)  # rows missing unless a stub says otherwise
        t = Tick("o/r", str(kw.pop("checkout", ROOT)), queue=queue,
                 train_log=train_log, workers_file=workers, roster_file=roster,
                 gh=gh, git=git, proc=procs or (lambda pattern: []),
                 bus=(lambda: (bus_rc, bus_refs)) if bus_refs is not None
                 else (lambda: (0, [])), now=NOW, policy_state=policy_state,
                 **kw)
        return t

    def git_factory(files="dev/programme/delivery/9.md", show=None, behind="0"):
        show = {"origin/main:" + HANDOVER: f"updated-for: {H1}\n",
                "origin/main:" + CODEOWNERS: "/CLAUDE.md @tvofi\n",
                **(show or {})}

        def git(argv):
            if argv[:1] == ["fetch"]:
                return 0, ""
            if argv[:2] == ["merge-base", "--is-ancestor"]:
                return 1, ""  # every verdict is moved, in these arms
            if argv[:1] == ["merge-base"]:
                return 0, V
            if argv[:1] == ["diff"]:
                return 0, files
            if argv[:1] == ["show"]:
                return (0, show[argv[1]]) if argv[1] in show else (1, "no show")
            if argv[:1] == ["log"]:
                if "--format=%H %ct %s" in argv:
                    return 0, f"{'f' * 40} 0 the policy subject"
                return 0, ""
            if argv[:1] == ["cat-file"]:
                return 1, ""
            if argv[:2] == ["rev-list", "--count"]:
                return 0, behind if "origin/main" in argv[2] and \
                    argv[2].startswith(H1) else "0"
            return 1, f"NO STUB git {' '.join(argv[:3])}"

        return git

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        version = tmp / "checkout"
        version.mkdir()
        (version / "VERSION").write_text("7.0.0\n")
        (version / ".github" / "workflows").mkdir(parents=True)
        qfile, wfile, rfile, log = (tmp / "q.json", tmp / "workers.json",
                                    tmp / "roster.json", tmp / "train.log")

        # ---- TRAIN ----
        qfile.write_text(json.dumps([{"pr": 1, "verdict": V},
                                     {"pr": 2, "verdict": V}]))
        t = tick(prs=[pr_obj(2, H1)], states={1: ("merged", H2), 2: ("open", H1)},
                 queue=str(qfile))
        t.train()
        a, f = check("TRAIN", [
            ("dead train reported", any("train not alive" in l["text"]
                                        for l in t.sections["TRAIN"])),
            ("stale merged entry flagged", any("stale queue entries" in x["text"]
                                               and "#1" in x["text"]
                                               for x in t.findings)),
            ("unmerged entry counted", any("holds 1 unmerged" in l["text"]
                                           for l in t.sections["TRAIN"])),
        ])
        total, failed = total + a, failed + f
        t = tick(procs=lambda pattern: [(11, "python3 merge_train.py"),
                                        (12, "python3 merge_train.py")])
        t.train()
        a, f = check("TRAIN race", [
            ("two trains flagged as a race", any("merge race" in x["text"]
                                                 for x in t.findings)),
            ("one train not flagged",
             True),  # covered by the dead-train arm above (0 procs, no flag)
        ])
        total, failed = total + a, failed + f
        log.write_text("step lines\nTRAIN STOPPED ci: #9 red: x\n")
        (tmp / "train.rc").write_text("TRAIN_RC=1\n")
        t = tick(train_log=str(log))
        t.train()
        a, f = check("TRAIN stop", [
            ("TRAIN STOPPED flagged", any("last run stopped" in x["text"]
                                          for x in t.findings)),
            ("nonzero rc flagged", any("exited 1" in x["text"]
                                       for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- PRS ----
        q13 = tmp / "q13.json"
        q13.write_text(json.dumps([{"pr": 13, "verdict": V}]))
        t = tick(prs=[pr_obj(10, "d" * 40, ms="BLOCKED"), pr_obj(11, H2),
                      pr_obj(12, H2), pr_obj(13, H2), pr_obj(14, H1)],
                 runs_at={H2: [run_obj("tests", conclusion="failure"),
                               run_obj("briefs", conclusion="failure")],
                          "d" * 40: [], H1: [run_obj("tests")]},
                 bodies={11: "## Red checks\n\nbriefs: answered\n"},
                 states={13: ("open", H2)}, queue=str(q13),
                 required_names=("tests", "closures"))
        t.checkout = str(version)
        t.git = git_factory(files="custom_components/x.py")
        t.prs(["tests", "closures"])
        a, f = check("PRS", [
            ("red unanswered flagged (tests)", any("#11" in x["text"]
                                                   and "unanswered" in x["text"]
                                                   and "tests" in x["text"]
                                                   for x in t.findings)),
            ("answered red not flagged", not any(
                "#11" in x["text"] and "briefs" in x["text"]
                and "unanswered" in x["text"] for x in t.findings)),
            ("zero runs flagged", any("#10" in x["text"] and "ZERO check runs"
                                      in x["text"] for x in t.findings)),
            ("dirty/blocked flagged", any("#10" in x["text"] and "BLOCKED"
                                          in x["text"] for x in t.findings)),
            ("twins flagged", any("twin open PRs" in x["text"]
                                  and "#11" in x["text"] and "#12" in x["text"]
                                  for x in t.findings)),
            ("missing row flagged (13)", any("#13" in x["text"]
                                             and "no delivery row" in x["text"]
                                             for x in t.findings)),
            ("verdict moved no carry flagged (13)",
             any("#13" in x["text"] and "no carry" in x["text"]
                 for x in t.findings)),
            ("absent required flagged (14)", any("#14" in x["text"]
                                                 and "ABSENT" in x["text"]
                                                 for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # behind-main arm
        t = tick(prs=[pr_obj(15, H1)], runs_at={H1: [run_obj("tests")]},
                 behind=40, behind_max=25)
        t.checkout = str(version)
        t.git = git_factory(behind="40")
        t.prs(["tests"])
        a, f = check("PRS behind", [
            ("badly-behind flagged", any("#15" in x["text"]
                                         and "commits behind main" in x["text"]
                                         for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(prs=[pr_obj(16, H1)], runs_at={H1: [run_obj("tests")]},
                 behind=9)
        t.checkout = str(version)
        t.git = git_factory(behind="9")
        t.prs(["tests"])
        a, f = check("PRS behind default", [
            ("modestly-behind not flagged at the default 25",
             not any("commits behind main" in x["text"] for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # claims arms
        for stamp, want in (("6.9.9", True), ("7.0.0", False),
                            ("7.0.0-commented", False)):
            raw = f"claims-for: {stamp}\n" if not stamp.endswith("commented") \
                else f"# claims-for: {stamp.removesuffix('-commented')}\n"
            t = tick(prs=[pr_obj(14, H1)], runs_at={H1: [run_obj("tests")]})
            t.checkout = str(version)
            t.git = git_factory(
                files="dev/programme/delivery/1.md\ntests/golden/claimed_drift.txt",
                show={f"{H1}:tests/golden/claimed_drift.txt": raw})
            t.prs(["tests"])
            a, f = check("PRS claims", [
                (f"claims-for {stamp} {'flagged' if want else 'not flagged'}",
                 any("#14" in x["text"] and "claims-for" in x["text"]
                     for x in t.findings) == want),
            ])
            total, failed = total + a, failed + f

        # ---- WORKERS ----
        wfile.write_text(json.dumps([
            {"seat": "moved", "pr": 20, "head": H1,
             "dispatched_at": iso(NOW), "agent_kind": "fixer"},
            {"seat": "ciwait", "pr": 21, "head": H2,
             "dispatched_at": iso(NOW - datetime.timedelta(hours=1)),
             "agent_kind": "fixer"},
            {"seat": "fresh-nopr", "pr": None, "head": None,
             "dispatched_at": iso(NOW), "agent_kind": "fixer"},
            {"seat": "old-nopr", "pr": None, "head": None,
             "dispatched_at": iso(NOW - datetime.timedelta(hours=5)),
             "agent_kind": "fixer"},
        ]))
        t = tick(workers=str(wfile),
                 runs_at={H2: [run_obj("tests", started=NOW, done=NOW)]},
                 states={20: ("open", H2), 21: ("open", H2)})
        t.workers()
        txt = [l["text"] for l in t.sections["WORKERS"]]
        a, f = check("WORKERS", [
            ("DONE? on head move", any(x.startswith("moved: DONE?") for x in txt)),
            ("OK on new CI completion", any(x.startswith("ciwait: OK")
                                            for x in txt)),
            ("OK fresh no-pr", any(x.startswith("fresh-nopr: OK") for x in txt)),
            ("STALLED? old no-pr", any(x.startswith("old-nopr: STALLED?")
                                       for x in txt)),
        ])
        total, failed = total + a, failed + f
        t = tick(workers=str(wfile),
                 runs_at={H2: [run_obj("tests", started=NOW - datetime.timedelta(hours=2),
                                       done=NOW - datetime.timedelta(hours=2))]},
                 states={20: ("open", H1), 21: ("open", H2)})
        t.workers()
        txt = [l["text"] for l in t.sections["WORKERS"]]
        a, f = check("WORKERS stalled", [
            ("STALLED? on no new CI", any(x.startswith("ciwait: STALLED?")
                                          for x in txt)),
            ("head-move not re-flagged at same head",
                 not any(x.startswith("moved: DONE?") for x in txt)),
        ])
        total, failed = total + a, failed + f

        # ---- PLAN ----
        rfile.write_text(json.dumps({"groups": [
            {"group": "A", "resume": {"stage": "done"}},
            {"group": "B", "resume": {"stage": "not-started"}, "after": ["A"]},
            {"group": "C", "resume": {"stage": "not-started"}, "after": ["B"]},
            {"group": "D", "resume": {"stage": "fixing"}, "after": []},
            {"group": "E", "resume": {"stage": "deferred"}},
        ]}))
        t = tick(roster=str(rfile))
        t.plan()
        txt = [l["text"] for l in t.sections["PLAN"]]
        a, f = check("PLAN", [
            ("unblocked B flagged", any(x["text"].startswith("B: UNBLOCKED")
                                        for x in t.findings)),
            ("C blocked by B", any(x.startswith("C: blocked by B") for x in txt)),
            ("in-progress D not flagged", any(x.startswith("D: in progress")
                                              for x in txt)
             and not any(x["text"].startswith("D:") for x in t.findings)),
            ("deferred E stays deferred", any(x.startswith("E: deferred")
                                              for x in txt)
             and not any(x["text"].startswith("E:") for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- MAIN ----
        gh = Stub()
        gh.on("commits/main", out=H1)
        gh.on(".[] | select(.name", out="42")
        gh.on("rulesets/42", out="tests\nclosures\n")
        gh.on(f"commits/{H1}/check-runs",
              out=json.dumps(run_obj("tests", conclusion="failure")) + "\n"
              + json.dumps(run_obj("record-autofix", conclusion="failure")))
        gh.on("issues/201/comments", out=json.dumps([[MAN]]))
        t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(), now=NOW)
        t.main()
        a, f = check("MAIN", [
            ("red required on main flagged", any("REQUIRED not green" in x["text"]
                                                 and "tests" in x["text"]
                                                 for x in t.findings)),
            ("nightly-class red named", any("record-autofix" in x["text"]
                                            for x in t.findings)),
            ("mandate reported", any(l["text"].startswith("mandate:")
                                     for l in t.sections["MAIN"])),
        ])
        total, failed = total + a, failed + f

        # mandate in force / expired, through the gate's own reader
        if gate_ok:
            for label, body, want_flag in (
                    ("in force", MAN["body"], False),
                    ("expired", mandate_body(iso(NOW - datetime.timedelta(days=1)),
                                             iso(NOW - datetime.timedelta(hours=1))),
                     True)):
                gh = Stub()
                gh.on("issues/comments/", out=json.dumps(dict(
                    MAN, body=body, updated_at=MAN["created_at"])))
                gh.on("issues/201/comments", out=json.dumps([[MAN]]))
                t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=Stub(),
                         now=NOW, mandate_id=mid)
                t.mandate("MAIN")
                line = next((l for l in t.sections["MAIN"]
                             if l["text"].startswith("mandate:")), None)
                a, f = check("MAIN mandate", [
                    (f"mandate {label}: line flag == {want_flag}",
                     line is not None and line["flag"] == want_flag),
                ])
                total, failed = total + a, failed + f

        # pins drift
        wf = version / ".github" / "workflows"
        s1 = "1" * 40
        s2 = "2" * 40
        (wf / "a.yml").write_text(f"  - uses: actions/checkout@{s1}\n")
        (wf / "b.yml").write_text(f"  - uses: actions/checkout@{s2}\n")
        t = tick(checkout=str(version))
        t.pins("MAIN")
        arms = [("pin drift flagged", any("action-pin drift" in x["text"]
                                          and "actions/checkout" in x["text"]
                                          for x in t.findings))]
        (wf / "b.yml").write_text(f"  - uses: actions/checkout@{s1}\n")
        t = tick(checkout=str(version))
        t.pins("MAIN")
        arms.append(("matching pins not flagged",
                     not any("action-pin drift" in x["text"] for x in t.findings)))
        a, f = check("MAIN pins", arms)
        total, failed = total + a, failed + f

        # ---- read-back discipline ----
        t = tick(gh_extra=[(("pr", "list"), 1, "API exploded")], with_mandate=False)
        t.prs(["tests"])
        a, f = check("read-back", [
            ("unreadable PR list reported", any("UNREADABLE" in x["text"]
                                                and "open pull requests"
                                                in x["text"] for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- STATE stale vs all-clear ----
        old = "e" * 40
        t = tick(handover=old, behind_handover=3,
                 rows="Merge pull request #77 from tvofi/x",
                 merges=f"{'d' * 40} Merge pull request #78 from tvofi/y",
                 search_counts={"d" * 40: 0},
                 files="dev/programme/delivery/9.md")
        t.state()
        a, f = check("STATE stale", [
            ("updated-for behind flagged", any("updated-for" in x["text"]
                                               and "behind" in x["text"]
                                               for x in t.findings)),
            ("record beat owed named", any("record beat owed" in x["text"]
                                           for x in t.findings)),
            ("state_docs --push dispatch item", any("state_docs.py --push"
                                                    in x["text"]
                                                    for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(handover=H1, merges="")
        t.state()
        a, f = check("STATE all-clear", [
            ("current reported, nothing flagged",
             any("state docs current" in l["text"] for l in t.sections["STATE"])
             and not any(x["section"] == "STATE" for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- unrecorded-merge all-clear (search finds every sha) ----
        t = tick(handover=old, merges="{'d'*0}".replace("'", '"'),
                 search_counts={})
        t = tick(handover=old,
                 merges=f"{'d' * 40} Merge pull request #78 from tvofi/y",
                 search_counts={"d" * 40: 1})
        t.state()
        a, f = check("unrecorded all-clear", [
            ("recorded merge not flagged", not any("record beat owed"
                                                   in x["text"]
                                                   for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- closes mismatch vs all-clear ----
        gql = lambda nodes: nodes
        t = tick(handover=old, behind_handover=3,
                 merges24="Merge pull request #77 from tvofi/x",
                 bodies={77: "Closes #201\n\nproper sentence."},
                 graphql={77: [{"number": 201}, {"number": 202}]})
        t.state()
        a, f = check("closes mismatch", [
            ("declared-vs-closed mismatch flagged",
             any("closes mismatch" in x["text"] and "#202" in x["text"]
                 for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(handover=old, behind_handover=3,
                 merges24="Merge pull request #77 from tvofi/x",
                 bodies={77: "Closes #201\n\nproper sentence."},
                 graphql={77: [{"number": 201}]})
        t.state()
        a, f = check("closes all-clear", [
            ("matching closes not flagged", not any("closes mismatch"
                                                    in x["text"]
                                                    for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- stale owner review vs current ----
        rv_old = [{"user": {"login": "tvofi"}, "state": "APPROVED",
                   "commit_id": H2, "submitted_at": iso(NOW)}]
        rv_cur = [{"user": {"login": "tvofi"}, "state": "APPROVED",
                   "commit_id": H1, "submitted_at": iso(NOW)}]
        for rv, want in ((rv_old, True), (rv_cur, False)):
            t = tick(prs=[pr_obj(50, H1)], runs_at={H1: [run_obj("tests")]},
                     reviews={50: rv})
            t.checkout = str(version)
            t._files = {50: ["tools/audit/seat/x.py"]}
            t.git = git_factory(files="tools/audit/seat/x.py",
                                show={"origin/main:" + CODEOWNERS:
                                      "/tools/ @tvofi\n"})
            t.owner_reviews("PRS", [{"number": 50, "headRefOid": H1,
                                     "headRefName": "fix/50",
                                     "mergeStateStatus": "CLEAN",
                                     "title": "t", "createdAt": iso(NOW)}])
            a, f = check("owner review", [
                (f"stale owner review {'flagged' if want else 'not flagged'}",
                 any("owner review" in x["text"] or "tvofi review" in x["text"]
                     for x in t.findings) == want),
            ])
            total, failed = total + a, failed + f

        # ---- mandate expiry warning ----
        if gate_ok:
            man_soon = dict(MAN, body=mandate_body(
                iso(NOW - datetime.timedelta(days=1)),
                iso(NOW + datetime.timedelta(hours=1))))
            gh = Stub()
            gh.on("issues/201/comments", out=json.dumps([[man_soon]]))
            gh.on("rate_limit", out=json.dumps({"remaining": 4000, "limit": 5000}))
            t = Tick("o/r", str(version), gh=gh, git=Stub(), proc=lambda p: [],
                     now=NOW)
            t.mandate("MAIN")
            a, f = check("mandate expiry", [
                ("window under 2h flagged", any("renew" in x["text"]
                                                for x in t.findings)),
            ])
            total, failed = total + a, failed + f

        # ---- rate headroom ----
        for remaining, want in ((500, True), (4000, False)):
            t = tick(rate=(remaining, 5000), with_mandate=False)
            t.main()
            a, f = check("rate headroom", [
                (f"quota {'flagged' if want else 'not flagged'} at {remaining}",
                 any("API quota low" in x["text"] for x in t.findings) == want),
            ])
            total, failed = total + a, failed + f

        # ---- A. body staleness ----
        t = tick(prs=[pr_obj(60, H1)], runs_at={H1: [run_obj("tests")]},
                 body_upd={60: iso(NOW - datetime.timedelta(hours=3))})
        t.body_staleness("PRS", [pr_obj(60, H1)])
        a, f = check("body staleness", [
            ("stale body flagged", any("re-take the body" in x["text"]
                                       and "#60" in x["text"]
                                       for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(prs=[pr_obj(60, H1)], runs_at={H1: [run_obj("tests")]},
                 body_upd={60: iso(NOW - datetime.timedelta(hours=1))})
        t.body_staleness("PRS", [pr_obj(60, H1)])
        a, f = check("body all-clear", [
            ("fresh body not flagged", not any("re-take the body"
                                               in x["text"]
                                               for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- B. undispositioned issues ----
        t = tick(open_issues="777")
        t.dispositions("REPLAN")
        a, f = check("dispositions", [
            ("unaccounted issue flagged", any("disposition #777" in x["text"]
                                              for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(open_issues="201", grep_rows="x #201 y")
        t.dispositions("REPLAN")
        a, f = check("dispositions all-clear", [
            ("rowed issue not flagged", not any("disposition #" in x["text"]
                                                for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- C. handoff orphans ----
        t = tick(bus_refs=["handoff/r9-xyz"])
        t.orphans("REPLAN")
        a, f = check("orphans", [
            ("orphan ref flagged", any("orphaned handoff ref handoff/r9-xyz"
                                       in x["text"] for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(bus_refs=[])
        t.orphans("REPLAN")
        a, f = check("orphans all-clear", [
            ("no orphans, no flag", not any("orphaned handoff" in x["text"]
                                            for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- D. non-standard conclusions ----
        for concl, want in (("cancelled", True), ("failure", False)):
            t = tick(prs=[pr_obj(70, H1)],
                     runs_at={H1: [run_obj("budget-raise-gate",
                                           conclusion=concl)]},
                     bodies={70: "## Red checks\n\nbudget-raise-gate: answered\n"})
            t.one_pr("PRS", pr_obj(70, H1), None, ["tests"])
            a, f = check("nonstandard conclusions", [
                (f"{concl}: rerun item {'present' if want else 'absent'}",
                 any("rerun budget-raise-gate" in x["text"]
                     for x in t.findings) == want),
            ])
            total, failed = total + a, failed + f

        # ---- E. mandate-cite drift ----
        for body, want in (("Agent approval under mandate 999999.", True),
                           (f"Agent approval under mandate {mid}.", False)):
            t = tick(prs=[pr_obj(50, H1)], runs_at={H1: [run_obj("tests")]},
                     reviews={50: [{"user": {"login": "tvofi"},
                                    "state": "APPROVED", "commit_id": H1,
                                    "submitted_at": iso(NOW), "body": body}]})
            t.checkout = str(version)
            t._files = {50: ["tools/audit/seat/x.py"]}
            t.git = git_factory(files="tools/audit/seat/x.py",
                                show={"origin/main:" + CODEOWNERS:
                                      "/tools/ @tvofi\n"})
            t.mandate("MAIN")
            t.owner_reviews("PRS", [{"number": 50, "headRefOid": H1,
                                     "headRefName": "fix/50",
                                     "mergeStateStatus": "CLEAN", "title": "t",
                                     "createdAt": iso(NOW),
                                     "updatedAt": iso(NOW)}])
            a, f = check("mandate-cite drift", [
                (f"cite {body[-8:]}: {'flagged' if want else 'not flagged'}",
                 any("re-post the review citing the in-force mandate"
                     in x["text"] for x in t.findings) == want),
            ])
            total, failed = total + a, failed + f

        # ---- main-red dispatch briefs: required lane, bot lane ----
        gh = Stub()
        gh.on("commits/main", out=H1)
        gh.on(".[] | select(.name", out="42")
        gh.on("rulesets/42", out="tests\nclosures\n")
        gh.on(f"commits/{H1}/check-runs",
              out=json.dumps(run_obj("tests", conclusion="failure", cid=424242))
              + "\n" + json.dumps(run_obj("record-autofix",
                                           conclusion="failure", cid=424243)))
        # the stub answers what `gh api --jq .output` returns: the output
        # object itself, not the response body
        gh.on("check-runs/424242", out=json.dumps(
            {"summary": "closures scope drifted",
             "text": ">>> FAILED: tests/stress.py\n"
                     "error: UNDER-SCOPED closures.json"}))
        gh.on("check-runs/424243", out=json.dumps(
            {"summary": "skip-failed-recording: no bot commit is coming",
             "text": ""}))
        gh.on("issues/201/comments", out=json.dumps([[MAN]]))
        gh.on("rate_limit", out=json.dumps({"remaining": 4000, "limit": 5000}))
        t = Tick("o/r", str(version), gh=gh, git=Stub(),
                 proc=lambda p: [], now=NOW)
        t.main()
        briefs = [l["text"] for l in t.sections["MAIN"]
                  if l["text"].startswith("ci-autofix:")
                  or l["text"].startswith("main-red ")]
        tests_brief = next((b for b in briefs if "main-red tests" in b), "")
        bot_brief = next((b for b in briefs if "record-autofix" in b), "")
        a, f = check("main-red briefs", [
            ("required-lane brief has the four fields",
             all(k in tests_brief for k in
                 ("main-red tests", "job 424242", "error line:",
                  "suspected class: gate-file change",
                  "dispatch a fixer seat"))),
            ("bot-lane brief leads with the ci-autofix rule and quotes the "
             "summary",
             bot_brief.startswith("ci-autofix: read the bot's job summary")
             and "skip-failed-recording" in bot_brief),
        ])
        total, failed = total + a, failed + f

        # ---- ETA: beat age, lane median, orchestrator ETAS ----
        stale_log = tmp / "stale-train.log"
        stale_log.write_text("#2143 serial: grader\n")
        old = NOW.timestamp() - 3 * 3600
        import os as _os
        _os.utime(stale_log, (old, old))
        t = tick(procs=lambda pattern: [(21, "python3 -u merge_train.py run q")],
                 train_log=str(stale_log))
        t.eta()
        a, f = check("ETA beat", [
            ("stale beat flagged", any("train beat stale" in x["text"]
                                       for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        fresh_log = tmp / "fresh-train.log"
        fresh_log.write_text("#2143 serial: grader\n")
        t = tick(procs=lambda pattern: [(21, "python3 -u merge_train.py run q")],
                 train_log=str(fresh_log))
        t.eta()
        a, f = check("ETA beat fresh", [
            ("fresh beat silent", not any("train beat stale" in x["text"]
                                          for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        (version / "tests").mkdir(exist_ok=True)
        (version / "tests" / "ci_budgets.json").write_text(
            json.dumps({"critical_path_minutes": 61.0}))
        slow = NOW - datetime.timedelta(hours=3)
        t = tick(prs=[pr_obj(95, H1)], checkout=str(version),
                 runs_at={H1: [run_obj("composed-proof", status="in_progress",
                                       started=slow)]})
        t.prs(["tests"])
        t.eta()
        a, f = check("ETA lane", [
            ("over-median pending flagged", any("vs median 61.0" in x["text"]
                                                for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        quick = NOW - datetime.timedelta(minutes=30)
        t = tick(prs=[pr_obj(95, H1)], checkout=str(version),
                 runs_at={H1: [run_obj("composed-proof", status="in_progress",
                                       started=quick)]})
        t.prs(["tests"])
        t.eta()
        a, f = check("ETA lane within", [
            ("within-median pending silent", not any("vs median" in x["text"]
                                                     for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        etas = tmp / "etas.txt"
        etas.write_text("pr=2149 expected-by="
                        + iso(NOW - datetime.timedelta(hours=1))
                        + " note=review owed\n")
        qd = tmp / "qeta.json"
        qd.write_text(json.dumps([{"pr": 2149}]))
        t = tick(queue=str(qd))
        t.eta()
        a, f = check("ETA orchestrator", [
            ("missed ETA flagged", any("ETA missed for #2149" in x["text"]
                                       for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        (tmp / "noetas").mkdir()
        qd2 = tmp / "noetas" / "q.json"
        qd2.write_text(json.dumps([{"pr": 2149}]))
        t = tick(queue=str(qd2))
        t.eta()
        a, f = check("ETA absent file", [
            ("absent ETAS file silent", not any("ETA missed" in x["text"]
                                                for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- policy drift ----
        pstate = tmp / "policy-drift.state"
        pstate.write_text("1" * 40 + "\n")
        t = tick(policy_now="2" * 40, policy_state=str(pstate))
        t.policy_drift("MAIN")
        a, f = check("policy drift", [
            ("moved corpus flagged", any("policy corpus moved at 2222"
                                         in x["text"] for x in t.findings)),
            ("state file updated", pstate.read_text().strip() == "2" * 40),
        ])
        total, failed = total + a, failed + f
        t = tick(policy_now="2" * 40, policy_state=str(pstate))
        t.policy_drift("MAIN")
        a, f = check("policy all-clear", [
            ("unchanged corpus not flagged", not any("policy corpus moved"
                                                     in x["text"]
                                                     for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- production order: run() as the heartbeat calls it. The stale
        # review and the mandate-cite drift must both fire even though PRS
        # runs before MAIN: run() reads the mandate first. ----
        for cite, want in (("mandate 999999.", True),
                           (f"mandate {mid}.", False)):
            t = tick(prs=[pr_obj(90, H1)], runs_at={H1: [run_obj("tests")]},
                     reviews={90: [{"user": {"login": "tvofi"},
                                    "state": "APPROVED", "commit_id": H1,
                                    "submitted_at": iso(NOW),
                                    "body": "Agent approval under " + cite}]},
                     files="tools/audit/seat/x.py",
                     codeowners_text="/tools/ @tvofi\n")
            rep = t.run()
            a, f = check("production order", [
                (f"cite {cite}: mandate-cite drift {'fires' if want else 'silent'}",
                 any("re-post the review citing the in-force mandate"
                     in x["text"] for x in rep["findings"]) == want),
                ("mandate read before PRS (live id set)",
                 getattr(t, "_mandate_live", None) == mid),
            ])
            total, failed = total + a, failed + f

        # ---- search method: the GET stub answers; a POST-form call would
        # have hit the 404 stub and reported UNREADABLE instead ----
        t = tick(handover="e" * 40, behind_handover=3,
                 merges=f"{'d' * 40} Merge pull request #78 from tvofi/y",
                 search_counts={"d" * 40: 0})
        t.state()
        a, f = check("search GET", [
            ("record beat found via GET (no 404 unreadable)",
             any("record beat owed" in x["text"] for x in t.findings)
             and not any("UNREADABLE" in x["text"] and "#201 search"
                         in x["text"] for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- orphans: usage output is never data ----
        t = tick(bus_refs=["usage: bus.sh watch", "usage: bus.sh publish",
                           " 7 more usage lines"], bus_rc=1)
        t.orphans("REPLAN")
        a, f = check("orphans unavailable", [
            ("one unavailable finding, no usage parsed as refs",
             any("bus.sh orphans unavailable" in x["text"]
                 for x in t.findings)
             and not any("orphaned handoff ref" in x["text"]
                         for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- closes negation: "does not fix #N" is not a declared close ----
        t = tick(handover="e" * 40, behind_handover=3,
                 merges24="Merge pull request #81 from tvofi/x",
                 bodies={81: "Does `not fix #205` here.\n\nThis leaves #205 "
                             "open; closes #201.\n"},
                 graphql={81: [{"number": 201}]})
        t.state()
        a, f = check("closes negation", [
            ("negated and code-spanned numbers not declared",
             not any("closes mismatch" in x["text"] for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(handover="e" * 40, behind_handover=3,
                 merges24="Merge pull request #81 from tvofi/x",
                 bodies={81: "Closes #205."},
                 graphql={81: []})
        t.state()
        a, f = check("closes real mismatch", [
            ("a real declared-not-closed still flagged",
             any("closes mismatch" in x["text"] and "#205" in x["text"]
                 for x in t.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- the null control: an all-clear board, empty list, exit 0 ----
        rfile.write_text(json.dumps({"groups": [
            {"group": "A", "resume": {"stage": "done"}},
            {"group": "B", "resume": {"stage": "done"}},
        ]}))
        t = tick(prs=[pr_obj(30, H1)],
                 runs_at={H1: [run_obj("tests"), run_obj("closures")]},
                 queue=None, train_log=None, workers=None, roster=str(rfile),
                 checkout=str(version))
        t.git = git_factory()
        rep = t.run()
        text = render(rep)
        a, f = check("null control", [
            ("provenance line always prints",
             text.startswith("BOARD measured from origin/main at ")),
            ("zero findings", rep["findings"] == []),
            ("empty list line printed", "DISPATCH LIST: empty" in text),
            ("all eight sections measured",
             set(rep["sections"]) == {"TRAIN", "PRS", "ETA", "WORKERS",
                                      "PLAN", "MAIN", "STATE", "REPLAN"}),
        ])
        total, failed = total + a, failed + f

    print(f"orchestrator_tick self-test: {total} checks, {failed} failed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the heartbeat's dispatch list")
    ap.add_argument("--repo",
                    default=os.environ.get("HPO_REPO", "tvofi/heatpump_optimizer"))
    ap.add_argument("--checkout", default=str(ROOT))
    ap.add_argument("--queue", action="append")
    ap.add_argument("--train-log")
    ap.add_argument("--workers-file")
    ap.add_argument("--roster-file")
    ap.add_argument("--roster-ref", default="origin/handoff/audit-r9-fixplan")
    ap.add_argument("--mandate-id", type=int)
    ap.add_argument("--mandate-since-days", type=int, default=14)
    ap.add_argument("--policy-state",
                    help="one-line state file beside the queue (default: "
                         "<queue dir>/policy-drift.state)")
    ap.add_argument("--stall-hours", type=float, default=2.0)
    ap.add_argument("--grace-hours", type=float, default=0.5,
                    help="no new CI completion inside this window is not a stall")
    ap.add_argument("--behind-max", type=int, default=25)
    ap.add_argument("--only",
                    help="comma-separated: TRAIN,PRS,ETA,WORKERS,PLAN,MAIN,STATE,REPLAN")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.workers_file and a.queue:
        sib = Path(a.queue[0]).parent / "workers.json"
        if sib.exists():
            a.workers_file = str(sib)
    only = [s.strip() for s in a.only.split(",")] if a.only else None
    if not a.policy_state and a.queue:
        a.policy_state = str(Path(a.queue[0]).parent / "policy-drift.state")
    t = Tick(a.repo, a.checkout, queue=a.queue, policy_state=a.policy_state, train_log=a.train_log,
             workers_file=a.workers_file, roster_file=a.roster_file,
             roster_ref=a.roster_ref, mandate_id=a.mandate_id,
             mandate_since_days=a.mandate_since_days,
             stall_hours=a.stall_hours, behind_max=a.behind_max)
    rep = t.run(only)
    print(json.dumps(rep, indent=1) if a.json else render(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
