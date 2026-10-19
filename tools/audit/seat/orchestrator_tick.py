#!/usr/bin/env python3
"""The heartbeat's dispatch list: one command, read-only, everything needing a decision.

    python3 tools/audit/seat/orchestrator_tick.py [--repo OWNER/REPO] [--checkout DIR]
        [--queue FILE] [--train-log FILE] [--workers-file FILE]
        [--roster-file PATH | --roster-ref GITREF [--roster-path PATH]]
        [--mandate-id N]
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
          origin/main's tip, and merged PRs since it with no delivery row
          (both merge-subject templates, through delivery_status's collect)
          -- each nonzero names the owed action (`state_docs.py --push`), the
          write itself stays in the per-merge beat.
  REPLAN  detection only, the item names the owed action: queued-stale
          (pinned verdict vs live head), merged entries to prune, repeated
          TRAIN STOPPED at one pr+step, roster groups contested by an open
          PR's files, done resumes whose commit is not in main, owner-gated
          age, and the throughput stall (verdicted green entry, no train,
          main idle) -- "fire the train"; and OWED handoffs, every pass:
          `bus.sh orphans --min-age-h 0`'s STRANDED refs, a PR behind its own
          newer handoff included.
  CARRY   opt-in (`--only CARRY`, weekly and at closure; never in the default
          pass): `carry_audit.py sweep --last N --issues` over origin/main and
          the tick's roster ref; exit 1 is one dispatch line and the sweep's
          unowned lines, anything else without its summary is UNREADABLE.
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
#: OWED-handoff lines printed per pass (the earlier list's cap, kept).
CAP_ORPHANS = 20
#: The OWED-handoff read. DESIGN CHOICE: no age window. bus.sh's default
#: (--min-age-h 2) spares a ref pushed moments ago as a lane's in-flight push,
#: but a handoff whose body ref exists is complete, and a level line that
#: waits two hours is how #2411's handoff sat unapplied from 19:49Z.
BUS_ORPHANS_ARGV = ("orphans", "--min-age-h", "0")
#: The carry sweep's tool and window (CARRY, finding-propagation.md's sweep).
CARRY_AUDIT = "tools/audit/carry_audit.py"
CARRY_LAST = 20
#: Unowned-finding lines printed per sweep.
CAP_CARRY = 20
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
                 roster_ref: str | None = None,
                 roster_path: str | None = None,
                 mandate_id: int | None = None, stall_hours: float = 2.0,
                 grace_hours: float = 0.5, behind_max: int = 25,
                 mandate_since_days: int = 14,
                 relay_log: str | None = None,
                 now: datetime.datetime | None = None,
                 gh=None, git=None, proc=None, bus=None, carry=None,
                 carry_last: int = CARRY_LAST) -> None:
        self.repo, self.checkout = repo, checkout
        self.queues = ([queue] if isinstance(queue, str) else list(queue or []))
        self.policy_state = policy_state
        self.train_log = train_log
        self.workers_file = workers_file
        self.roster_file, self.roster_ref = roster_file, roster_ref
        self.roster_path = roster_path
        self.mandate_id, self.mandate_since_days = mandate_id, mandate_since_days
        self.stall_hours, self.grace_hours = stall_hours, grace_hours
        self.behind_max = behind_max
        # cloud_relay.sh's own default log (#2419): POSTED/OWED lines.
        self.relay_log = relay_log or os.path.join(
            os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo"),
            "cloud-relay.log")
        self.now = now or datetime.datetime.now(datetime.timezone.utc)
        self._gh, self._git, self._proc, self._bus = gh, git, proc, bus
        self._carry, self.carry_last = carry, carry_last
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
        bus.sh does not know (it lands with a PR) prints usage there. The
        argv is BUS_ORPHANS_ARGV, which the stub receives too."""
        if self._bus is not None:
            return self._bus(list(BUS_ORPHANS_ARGV))
        r = subprocess.run(["bash", str(SEAT / "bus.sh"), *BUS_ORPHANS_ARGV],
                           cwd=self.checkout, capture_output=True, text=True)
        return r.returncode, [l.strip() for l in r.stdout.splitlines()
                              if l.strip()]

    def carry_run(self, argv: list[str]) -> "tuple[int, list[str]]":
        """`carry_audit.py <argv>`, a subprocess over the tree's own tool, never
        a copy: (rc, stdout lines). The stub receives the same argv."""
        if self._carry is not None:
            return self._carry(list(argv))
        r = subprocess.run([sys.executable, "-I", str(ROOT / CARRY_AUDIT), *argv],
                           cwd=self.checkout, capture_output=True, text=True)
        return r.returncode, [l.rstrip() for l in (r.stdout + r.stderr).splitlines()
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

    def critical_median(self) -> "float | None":
        """The recorded critical-path median in minutes (tests/ci_budgets.json,
        the one measured baseline), or None when unreadable. One reader for the
        ETA lane check and for the WAITING bound below."""
        try:
            return json.loads((Path(self.checkout) / CI_BUDGETS).read_text()
                              ).get("critical_path_minutes") or None
        except (OSError, ValueError):
            return None

    def stuck(self, started, med) -> bool:
        """A lane pending past 2x the median: the ETA check's own threshold."""
        try:
            st = datetime.datetime.fromisoformat(str(started).replace("Z", "+00:00"))
        except ValueError:
            return False
        return (self.now - st).total_seconds() / 60 > 2 * med

    def split_absent(self, absent: list[str], latest: dict) -> "tuple[list[str], list[str]]":
        """(waiting, absent): a required job with no check run yet is only
        ABSENT once nothing at the sha is still in flight. While a run is in
        flight the job may be gated on its `needs` (closures waits on coverage
        in the Tests workflow), and "absent" would send a re-dispatch for work
        that is queued behind a sibling. The wait is bounded by the ETA check's
        threshold: a run in flight past 2x the critical-path median is stuck
        and no longer explains the missing job, and an unreadable median cannot
        bound it, so both read ABSENT."""
        med = self.critical_median()
        live = med is not None and any(
            c.get("status") != "completed"
            and not self.stuck(c.get("started_at"), med)
            for c in latest.values())
        return (list(absent), []) if live else ([], list(absent))

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

    def _open_numbers(self) -> "set[int] | None":
        """The open pull requests' numbers: one `gh pr list` per tick, shared by
        TRAIN and REPLAN. A queue entry is unmerged only when its PR is in this
        set -- never from a `pulls/<n>` `.state`, which reads `closed` for a
        merged PR and never `merged` (2026-10-18: three merged entries, one
        merged outside the train, were reported as a dead train's queue).
        None: the read failed, and is reported."""
        if getattr(self, "_open_set", False) is not False:
            return self._open_set
        code, o = self.gh(["pr", "list", "--repo", self.repo, "--state", "open",
                           "--limit", "200", "--json", "number"])
        try:
            got = {int(p["number"]) for p in json.loads(o)} if code == 0 else None
        except (ValueError, TypeError, KeyError):
            got = None
        if got is None or len(got) >= 200:
            self.unreadable("TRAIN", "the open pull requests",
                            "200 or more, may be truncated" if got else o.strip()[-100:])
            got = None
        self._open_set = got
        return got

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
        preprs = self._seat_procs(self.proc("prepr.sh"), "prepr.sh",
                                  python_only=False)
        self.line(S, f"prepr slots: {len(preprs)} running (cap 4)"
                  + ("" if len(preprs) < 4 else " -- do not start a fifth"),
                  flag=len(preprs) >= 4)
        queue, open_ = self._queue(), 0
        if queue is not None:
            if not queue:
                self.line(S, "queue empty" if self.queues else "no --queue given")
            # An entry is unmerged only when its PR is OPEN; a set it cannot
            # read counts every entry unmerged, so a dead train is never hidden.
            ok = self._open_numbers() if queue else set()
            stale = [i.get("pr") for i in queue if ok is not None and i.get("pr") not in ok]
            open_ = len(queue) - len(stale)
            if stale:
                self.line(S, "stale queue entries (not OPEN: merged or closed, "
                          "drop them): " + ", ".join("#" + str(p) for p in stale),
                          flag=True)
            if open_:
                self.line(S, f"queue holds {open_} unmerged entr(y/ies)"
                          + ("" if live
                             else " -- train not alive: a dead train; load one or merge"),
                          flag=not live)
        if not live and queue is not None and not open_:
            self.line(S, "no train running (the queue holds no OPEN entry)")
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
                           "mergeStateStatus,title,createdAt,updatedAt,author"])
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
        self.open_pr_cap(S, prs)
        self.verdict_levels(S, prs)
        self.relay_owed(S)
        for head, ns in sorted(by_head.items()):
            if len(ns) > 1:
                self.line(S, "twin open PRs at one head "
                          f"{head[:12]}: {', '.join('#' + str(x) for x in ns)}"
                          " (duplicate CI, ambiguous red)", flag=True)

    def open_pr_cap(self, S: str, prs: list) -> None:
        """Two level lines every pass (tvofi, 2026-10-18): the open-PR soft cap
        open_pr.sh enforces, counted by pr_cap.py's own rule, and the counted
        PRs whose three-dot diff touches the coordinator, against its cap of 2.
        A diff one_pr could not read leaves the second count a floor: flagged."""
        cap_mod = _module("pr_cap_tick", "tools/audit/seat/pr_cap.py")
        if cap_mod is None:
            self.unreadable(S, "open-PR cap", "tools/audit/seat/pr_cap.py absent")
            return
        counted, cap = cap_mod.counted(prs), cap_mod.cap_from_env()
        if cap is None:
            self.unreadable(S, "open-PR cap", f"{cap_mod.CAP_ENV} is not a positive integer")
        else:
            n = len(counted)
            self.line(S, f"OPEN-PR CAP: {n}/{cap}" + (" (at the cap: open_pr.sh refuses; drain first)"
                                                     if n >= cap else ""), flag=n >= cap)
        files = getattr(self, "_files", {}) or {}
        hit, unread = cap_mod.coordinator_prs({p["number"]: files.get(p["number"]) for p in counted})
        k, kcap = len(hit), cap_mod.COORDINATOR_CAP
        text = f"coordinator.py PRs: {k}/{kcap}" + (f" ({', '.join('#' + str(x) for x in hit)})" if hit else "")
        if unread:
            text += f"; diff UNREADABLE at {', '.join('#' + str(x) for x in unread)}, so at least {k}"
        self.line(S, text, flag=k > kcap or bool(unread))

    #: The verdict grammar, bus.sh's verdict_sha (app_comment.sh's two patterns).
    VERDICT_MERGE = re.compile(r"^Fix review: merge ([0-9a-f]{40})$")
    VERDICT_BLOCKED = re.compile(r"^Fix review: blocked ([0-9a-f]{40}) [a-z-]+: .+$")

    def _verdict_authors(self) -> "tuple[set, int] | None":
        """The approver App's identity off app_approve.sh, through
        proof_watch.verdict_allowlist, its one reader; None when unreadable."""
        pw = _module("proof_watch_tick", "tools/audit/seat/proof_watch.py")
        if pw is None or not hasattr(pw, "verdict_allowlist"):
            return None
        for rel in ("tools/pr/app_approve.sh", "tools/audit/app_approve.sh"):
            got = pw.verdict_allowlist(ROOT / rel)
            if got is not None:
                return got
        return None

    def _handoff_newer(self, branch: str, at: str) -> "bool | None":
        """Is there a handoff/<topic> tip committed after `at`? The topic is the
        branch less `fix/`, then less `-pr` (open_pr.sh's two spellings).
        None: a read failed."""
        t = branch[4:] if branch.startswith("fix/") else branch
        for topic in dict.fromkeys([t, t[:-3] if t.endswith("-pr") else t]):
            code, o = self.git(["ls-remote", "origin", f"refs/heads/handoff/{topic}"])
            if code:
                return None
            sha = o.split()[0] if o.split() else ""
            if not sha:
                continue
            if self.git(["fetch", "-q", "origin", f"refs/heads/handoff/{topic}"])[0]:
                return None
            code, ct = self.git(["log", "-1", "--format=%ct", sha])
            try:
                when = datetime.datetime.fromtimestamp(int(ct.strip()), datetime.timezone.utc)
                return code == 0 and when > datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
            except ValueError:
                return None
        return False

    def verdict_levels(self, S: str, prs: list) -> None:
        """Level lines every pass, state not events (the round-10 orchestrator,
        2026-10-18: #2401 sat merge-ready and #2399 sat blocked, unacted, because
        only events reached it). From the approver App's newest `Fix review:`:
          MERGE-READY: #N <head8>      merge at the current head, CLEAN or UNSTABLE;
          BLOCKED-UNFIXED: #N <head8>  blocked at the current head, and no
                                       handoff/<topic> tip committed after it.
        A verdict at an older head prints neither line."""
        allow = self._verdict_authors()
        if allow is None:
            self.unreadable(S, "verdict levels", "no VERDICT_AUTHORS in app_approve.sh")
            return
        authors, vid = allow
        for pr in sorted(prs, key=lambda p: p["number"]):
            n, head = pr["number"], pr.get("headRefOid") or ""
            code, o = self.gh(["api", "--paginate", "--slurp",
                               f"repos/{self.repo}/issues/{n}/comments?per_page=100"])
            try:
                cs = [c for page in json.loads(o) for c in page] if code == 0 else None
            except (ValueError, TypeError):
                cs = None
            if cs is None:
                self.unreadable(S, f"verdicts on #{n}", o.strip()[-100:])
                continue
            vs = [c for c in cs if (c.get("user") or {}).get("login") in authors
                  and (c.get("user") or {}).get("id") == vid
                  and (c.get("body") or "").startswith("Fix review:")]
            if not vs:
                continue
            v = max(vs, key=lambda c: (c.get("created_at") or "", c.get("id") or 0))
            first = (v.get("body") or "").split("\n", 1)[0].rstrip("\r")
            m, b = self.VERDICT_MERGE.match(first), self.VERDICT_BLOCKED.match(first)
            ms = (pr.get("mergeStateStatus") or "").upper()
            if m and m.group(1) == head and ms in ("CLEAN", "UNSTABLE"):
                self.line(S, f"MERGE-READY: #{n} {head[:8]}", flag=True)
            elif b and b.group(1) == head:
                newer = self._handoff_newer(pr.get("headRefName") or "", v.get("created_at") or "")
                if newer is None:
                    self.unreadable(S, f"handoff ref for blocked #{n}", "git read failed")
                elif not newer:
                    self.line(S, f"BLOCKED-UNFIXED: #{n} {head[:8]}", flag=True)

    def relay_owed(self, S: str) -> None:
        """`OWED: <line>`, a level line every pass, for each OWED entry in
        cloud_relay.sh's log with no later POSTED for the same PR (the round-10
        orchestrator, 2026-10-18: a relayed verdict left unposted). The log's
        lines are `POSTED <utc> <pr> <sha>` and `OWED <utc> <pr> <sha|-> <why>`.
        No log is no relay yet, not a failure; an unreadable one is UNREADABLE."""
        try:
            with open(self.relay_log, encoding="utf-8", errors="replace") as fh:
                rows = fh.read().splitlines()
        except FileNotFoundError:
            self.line(S, "cloud-relay log: none yet (no OWED to report)")
            return
        except OSError as e:
            self.unreadable(S, "cloud-relay log", str(e)[:100])
            return
        owed: dict[str, list[str]] = {}
        for row in rows:
            f = row.split()
            if len(f) >= 3 and f[0] == "OWED":
                owed.setdefault(f[2], []).append(row.strip())
            elif len(f) >= 3 and f[0] == "POSTED":
                owed.pop(f[2], None)
        for pr in sorted(owed, key=lambda x: (len(x), x)):
            for row in owed[pr]:
                self.line(S, f"OWED: {row}", flag=True)

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
                waiting, absent = self.split_absent(absent, latest)
                if waiting:
                    self.line(S, f"#{n}: required contexts not started yet "
                                 f"(WAITING on needs; a run is in flight): "
                                 f"{', '.join(waiting)}")
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
            # WHICH roster is roster_lib's answer (newest_roster over the
            # ref's tree, or --roster-path); only the git reads are the
            # tick's, so the self-test drives them through the stub. A fixed
            # round-9 path read round 9's groups at a round-10 ref, whose
            # tree carries both rosters (R10-TICK b).
            ref = self.roster_ref or rl.DEFAULT_ROSTER_REF
            path = self.roster_path
            if not path:
                code, o = self.git(["ls-tree", "--name-only", ref,
                                    rl.ROSTERS_DIR + "/"])
                path = None if code else rl.newest_roster(o.split())
                if path is None:
                    self.unreadable(S, f"roster at {ref}",
                                    o.strip()[-120:] if code else
                                    f"no {rl.ROSTERS_DIR}/wave-r<N>-groups.json")
                    return None, None
            code, o = self.git(["show", f"{ref}:{path}"])
            if code:
                self.unreadable(S, f"roster at {ref}:{path}", o.strip()[-120:])
                return None, None
            try:
                roster = json.loads(o)
            except ValueError as e:
                self.unreadable(S, f"roster at {ref}:{path}", str(e)[:120])
                return None, None
            self.line(S, f"roster {ref}:{path}")
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
                waiting, absent = self.split_absent(absent, latest)
                if waiting:
                    self.line(S, f"main {tip[:12]}: required contexts not "
                                 "started yet (WAITING on needs; a run is in "
                                 f"flight): {', '.join(waiting)}")
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
        missing: list[str] = []
        for pr in self.merged_prs(S, "merges since updated-for",
                                  [f"{sha}..origin/main"]) or []:
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

    def merged_prs(self, S: str, what: str, rng: list[str]) -> "list[str] | None":
        """The pull requests merged on main's first-parent line over `rng`,
        newest first, as `tests/delivery_status.py` reads them -- its own
        `parse_log` and `collect`, never a copy of the subject grammar. That
        reads both GitHub templates: `Merge pull request #N from ...` and the
        title form `<title> (#N)`, a single-parent squash such as the
        record-autofix merges #2413, #2412 and #2407, which `git log --merges`
        and a merge-only pattern never saw. None, and UNREADABLE, when the
        log or the module cannot be read -- never an empty list."""
        ds = _module("delivery_status_tick", "tests/delivery_status.py")
        if ds is None:
            self.unreadable(S, what, "tests/delivery_status.py absent")
            return None
        code, o = self.git(["log", "--first-parent",
                            f"--format={ds.LOG_FORMAT}", *rng])
        if code:
            self.unreadable(S, what, o.strip()[-80:])
            return None
        merges, _ = ds.collect(ds.parse_log(o))
        return [str(m["number"]) for m in merges]

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
        merged = self.merged_prs(S, "merges of the last 24h",
                                 ["--since=24 hours ago", "origin/main"])
        if merged is None:
            return
        # git log is newest-first; "oldest first" is the tail of that list
        prs = merged[-CAP_CLOSES:]
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
            open_set = self._open_numbers()
            if open_set is not None and pr not in open_set:
                self.line(S, f"#{pr} not OPEN (merged or closed) -- prune it "
                             "from the queue", flag=True)
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
        code, o = self.git(["grep", "-oh", r"#[0-9]\+", "origin/main", "--",
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
        """OWED handoffs, a level line every pass: `bus.sh orphans`' STRANDED
        refs -- a complete handoff (code and body refs) that no `fix/*` head
        and no main carries, which includes a pull request whose head is not
        a descendant of its own newer handoff (#2411, 2026-10-18).

        The run's own summary line (`orphans: N stranded, ...`, stdout, on
        every completed run) is what makes its output data. bus.sh exits 1
        both for "a ref is stranded" and for a refusal (`die`), so the exit
        code alone cannot tell them apart: rc 1 with ORPHAN lines and a
        summary is the finding, and any output without a summary is the
        instrument unavailable -- ONE finding, never usage text parsed as
        refs. Each ORPHAN line is printed whole: it carries the topic, tip,
        age and the repair word (`opener`, `update`, `review`)."""
        try:
            rc, out = self.bus()
        except OSError as e:
            self.unreadable(S, "bus.sh orphans", str(e)[:80])
            return
        summary = [l for l in out if l.startswith("orphans: ")]
        stranded = [l for l in out if l.startswith("ORPHAN ")]
        if not summary or rc not in (0, 1) or (rc == 1) != bool(stranded):
            self.line(S, f"bus.sh orphans unavailable (exit {rc}, "
                         f"{'a summary' if summary else 'no summary'} line, "
                         f"{len(stranded)} ORPHAN line(s)): OWED handoffs "
                         "UNCHECKED this pass, not confirmed empty", flag=True)
            return
        for l in stranded[:CAP_ORPHANS]:
            self.line(S, f"OWED handoff: {l[len('ORPHAN '):]} -- no PR head "
                         "carries it: open_pr.sh (opener), update_pr.sh "
                         "(update) or a human decision (review)", flag=True)
        if len(stranded) > CAP_ORPHANS:
            self.line(S, f"OWED handoffs capped at {CAP_ORPHANS} of "
                         f"{len(stranded)}; the rest print next pass once "
                         "these are discharged", flag=True)
        for l in out:
            if l.startswith("SUPERSEDED "):
                self.line(S, f"superseded handoff ref {l[len('SUPERSEDED '):]}"
                             " -- main carries its change: prune")
        self.line(S, summary[0])

    # --------------------------------------------------------------- CARRY
    def carry_sweep(self) -> None:
        """The weekly and closure carry sweep (finding-propagation.md; #2404's
        carry_audit.py): `sweep --last N --issues` over both roster refs --
        origin/main, then the roster ref this tick reads -- so a carry main
        holds that the roster ref lacks prints ROSTER-DRIFT. Exit 1 is the
        finding: one dispatch line, then the sweep's unowned lines. Any other
        exit, or no `CARRY-SWEEP:` summary, is UNREADABLE, never a clean zero.

        OPT-IN, never in the default pass: the sweep reads every one of N
        merged pull requests' body and comments, so a four-minute tick cannot
        carry it. The orchestrator runs `--only CARRY` weekly and at closure."""
        S = "CARRY"
        if not (ROOT / CARRY_AUDIT).is_file() and self._carry is None:
            self.unreadable(S, "carry sweep", f"{CARRY_AUDIT} absent (it lands with #2404)")
            return
        rl = _module("roster_lib_tick", "tools/audit/seat/roster_lib.py")
        default = rl.DEFAULT_ROSTER_REF if rl is not None else "origin/main"
        refs = list(dict.fromkeys(["origin/main", self.roster_ref or default]))
        argv = [a for r in refs for a in ("--roster-ref", r)] + [
            "sweep", "--last", str(self.carry_last), "--issues"]
        try:
            rc, out = self.carry_run(argv)
        except OSError as e:
            self.unreadable(S, "carry sweep", str(e)[:80])
            return
        summary = [l for l in out if l.startswith("CARRY-SWEEP:")]
        if rc not in (0, 1) or not summary:
            self.unreadable(S, "carry sweep", f"exit {rc}, "
                            + (out[-1][:100] if out else "no output"))
            return
        if rc == 1:
            self.line(S, f"carry sweep found unowned findings ({summary[0]}; refs "
                         f"{', '.join(refs)}): dispatch a carry seat to route each "
                         f"(`python3 -I {CARRY_AUDIT} {' '.join(argv)}`)", flag=True)
            rows = [l for l in out if not l.startswith(("CARRY-SWEEP:", "CARRY-AUDIT:"))]
            for l in rows[:CAP_CARRY]:
                self.line(S, f"  {l.strip()[:160]}", flag=True)
            if len(rows) > CAP_CARRY:
                self.line(S, f"  ... {len(rows) - CAP_CARRY} more; run the command above", flag=True)
        self.line(S, f"carry sweep: {summary[0]} (refs {', '.join(refs)}, last {self.carry_last})")

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
            med = self.critical_median()
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
        if only and "CARRY" in only:  # opt-in: never in the default pass
            todo.append("CARRY")
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
            elif s == "CARRY":
                self.carry_sweep()
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

    def fp_log(subjects: str) -> str:
        """Subject lines as `git log --first-parent --format=LOG_FORMAT`
        prints them: a `Merge pull request` subject has two parents, any
        other (the squash `<title> (#N)` form) one."""
        recs = []
        for i, subj in enumerate(l for l in subjects.splitlines() if l.strip()):
            par = f"{'1' * 40} {'2' * 40}" if subj.startswith("Merge ") else "1" * 40
            recs.append(f"{i:040x}\x1f{par}\x1f{subj}\x1f\x1e")
        return "\n".join(recs)

    bus_calls: list = []  # every argv the bus stub received
    BUS_CLEAR = ("orphans: 0 stranded, 0 superseded; skipped no-body=0 named=0 "
                 "ancestor=0 young=0; origin main b87e8f1")

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
        # A pull request's own comments (verdict_levels): none, unless an arm says.
        gh.on(lambda argv: any(x.endswith("/comments?per_page=100") for x in argv), out="[]")
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
        git.on(("--first-parent", "--since=24 hours ago"), out=fp_log(merges24))
        git.on(("--merges", "--format=%H %s"), out=merges)
        git.on(("--first-parent",), out=fp_log(rows))
        git.on(("grep",), rc=0 if grep_rows else 1, out=grep_rows or "")
        git.on(f"origin/main:{PLAN}", out=plan_text)
        git.on(("show", "-s"), out=head_commit_at or iso(NOW - datetime.timedelta(hours=2)))
        git.on(("--format=%H %ct %s",),
               out=f"{policy_now or 'f' * 40} {int(NOW.timestamp())} the policy subject")
        git.on(("rev-list", "--count", f"{handover}..origin/main"),
               out=str(behind_handover))
        git.on(("cat-file", "-e"), rc=1)  # rows missing unless a stub says otherwise
        kw.setdefault("relay_log", os.devnull)  # hermetic: never the host's relay log
        t = Tick("o/r", str(kw.pop("checkout", ROOT)), queue=queue,
                 train_log=train_log, workers_file=workers, roster_file=roster,
                 gh=gh, git=git, proc=procs or (lambda pattern: []),
                 bus=(lambda argv: bus_calls.append(argv) or (bus_rc, bus_refs))
                 if bus_refs is not None
                 else (lambda argv: (0, [BUS_CLEAR])), now=NOW, policy_state=policy_state,
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
        # The t16 shape (2026-10-18): every queued PR merged, one outside the
        # train. REST reads `closed` for a merged PR, so the stub says so; the
        # open set (one `gh pr list`) holds only PRs the queue does not name.
        q16 = tmp / "q16.json"
        q16.write_text(json.dumps([{"pr": p, "verdict": V} for p in (2379, 2394, 2416)]))
        t = tick(prs=[pr_obj(2420, H1)], queue=str(q16),
                 states={p: ("closed", H2) for p in (2379, 2394, 2416)})
        t.train()
        tl = [l["text"] for l in t.sections["TRAIN"]]
        t_bad = tick(prs=[], queue=str(q16), gh_extra=[(("pr", "list"), 1, "HTTP 502")])
        t_bad.train()
        t_rp = tick(prs=[pr_obj(2394, H1)], queue=str(q16),
                    states={p: ("closed", H2) for p in (2379, 2394, 2416)})
        t_rp.replan()
        a, f = check("TRAIN queue: OPEN is the only unmerged", [
            ("null control: a queue whose entries are all merged prints no train-not-alive line",
             not any("train not alive" in x or "unmerged" in x for x in tl)),
            ("and says no train runs with no OPEN entry, unflagged",
             "no train running (the queue holds no OPEN entry)" in tl),
            ("and flags the three entries to drop",
             any("stale queue entries" in x["text"] and "#2379, #2394, #2416" in x["text"]
                 for x in t.findings)),
            ("an open set it cannot read counts every entry unmerged, and says so",
             any("holds 3 unmerged" in l["text"] and "train not alive" in l["text"] and l["flag"]
                 for l in t_bad.sections["TRAIN"])
             and any("UNREADABLE: the open pull requests" in x["text"] for x in t_bad.findings)),
            ("REPLAN: a queued PR not OPEN is to prune; an OPEN one is not",
             any("#2379 not OPEN" in x["text"] for x in t_rp.findings)
             and not any("#2394 not OPEN" in x["text"] for x in t_rp.findings)),
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

        # R10-TICK a: a required job gated on its `needs` has no check run
        # yet; with a sibling in flight (not stuck) it is WAITING, not ABSENT,
        # on the PRS arm and on the MAIN arm. A run in flight past 2x the
        # critical-path median is stuck and explains nothing: ABSENT again.
        (version / "tests").mkdir(exist_ok=True)
        (version / "tests" / "ci_budgets.json").write_text(
            json.dumps({"critical_path_minutes": 61.0}))
        fresh_run = NOW - datetime.timedelta(minutes=10)
        stuck_run = NOW - datetime.timedelta(hours=10)

        def lines(t, section):
            return [x["text"] for x in t.sections.get(section, [])]

        def gated(started, arm):
            runs = [run_obj("coverage", status="in_progress", conclusion=None,
                            started=started), run_obj("tests")]
            t = tick(prs=[pr_obj(17, H1)], runs_at={H1: runs},
                     required_names=("tests", "closures"),
                     checkout=str(version))
            t.git = git_factory(files="custom_components/x.py")
            if arm == "PRS":
                t.prs(["tests", "closures"])
            else:
                t.main()
            return t, lines(t, arm)

        for arm in ("PRS", "MAIN"):
            t, ls = gated(fresh_run, arm)
            a, f = check(f"{arm} needs-gated job", [
                ("waiting named, unflagged", any(
                    "WAITING" in l and "closures" in l for l in ls)
                    and not any("ABSENT" in x["text"] for x in t.findings)),
            ])
            total, failed = total + a, failed + f
            t, ls = gated(stuck_run, arm)
            a, f = check(f"{arm} stuck sibling", [
                ("ABSENT flagged under a stuck run", any(
                    "ABSENT" in x["text"] and "closures" in x["text"]
                    for x in t.findings)),
                ("no WAITING under a stuck run", not any(
                    "WAITING" in l for l in ls)),
            ])
            total, failed = total + a, failed + f
        t = tick(prs=[], runs_at={H1: [run_obj("tests")]},
                 required_names=("tests", "closures"), checkout=str(version))
        t.git = git_factory()
        t.main()
        a, f = check("MAIN settled null control", [
            ("settled + missing -> ABSENT flagged", any(
                "ABSENT" in x["text"] and "closures" in x["text"]
                for x in t.findings)),
        ])
        total, failed = total + a, failed + f
        t = tick(checkout=str(version))
        inflight = {"c": {"status": "queued", "started_at": iso(fresh_run)}}
        stuck_f = {"c": {"status": "queued", "started_at": iso(stuck_run)}}
        done = {"c": {"status": "completed"}}
        a, f = check("split_absent", [
            ("in flight -> waiting",
             t.split_absent(["closures"], inflight) == (["closures"], [])),
            ("settled -> absent (null control)",
             t.split_absent(["closures"], done) == ([], ["closures"])),
            ("stuck -> absent",
             t.split_absent(["closures"], stuck_f) == ([], ["closures"])),
        ])
        total, failed = total + a, failed + f
        t.checkout = str(tmp / "no-budgets")
        a, f = check("split_absent unbounded", [
            ("unreadable median -> absent",
             t.split_absent(["closures"], inflight) == ([], ["closures"])),
        ])
        total, failed = total + a, failed + f

        # R10-TICK c: no invalid-escape SyntaxWarning when this file compiles
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
        a, f = check("compile clean", [
            ("no SyntaxWarning on compile", not any(
                issubclass(w_.category, (SyntaxWarning, DeprecationWarning))
                for w_ in caught)),
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

        # ---- PLAN: which roster at a ref (R10-TICK b) ----
        # A round-10 tree carries round 9's roster too. The tick reads the
        # newest round unless --roster-path names one; no roster at all is
        # UNREADABLE, never a silent read of another round's groups.
        r9p = "dev/programme/rosters/wave-r9-groups.json"
        r10p = "dev/programme/rosters/wave-r10-groups.json"
        r9g = json.dumps({"groups": [
            {"group": "R9-X", "resume": {"stage": "not-started"}}]})
        r10g = json.dumps({"groups": [
            {"group": "R10-A", "resume": {"stage": "done"}},
            {"group": "R10-B", "resume": {"stage": "not-started"},
             "after": ["R10-A"]}]})

        def ref_tick(listing, **kw2):
            t2 = tick(roster_ref="origin/r10", **kw2)
            t2._git.on(("ls-tree", "origin/r10"), out=listing)
            t2._git.on(f"origin/r10:{r9p}", out=r9g)
            t2._git.on(f"origin/r10:{r10p}", out=r10g)
            t2.plan()
            return t2, [l["text"] for l in t2.sections["PLAN"]]

        t, txt = ref_tick(f"{r9p}\n{r10p}\n")
        t9, txt9 = ref_tick(f"{r9p}\n{r10p}\n", roster_path=r9p)
        t0, txt0 = ref_tick("dev/programme/rosters/README.md\n")
        a, f = check("PLAN roster", [
            ("two rosters: the newest round's group is unblocked",
             any(x["text"].startswith("R10-B: UNBLOCKED") for x in t.findings)),
            ("two rosters: no round-9 group is read",
             not any("R9-X" in x for x in txt)),
            ("the roster read is named", f"roster origin/r10:{r10p}" in txt),
            ("--roster-path wins over the newest",
             any(x["text"].startswith("R9-X: UNBLOCKED") for x in t9.findings)
             and not any("R10-" in x for x in txt9)),
            ("no roster at the ref is UNREADABLE, loudly",
             any("UNREADABLE: roster at origin/r10" in x["text"]
                 for x in t0.findings) and not any("R9-X" in x for x in txt0)),
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

        # ---- STATE missing rows: both GitHub subject templates ----
        # The tick's own merge pattern read `Merge pull request #N` only, over
        # `git log --merges`, so a single-parent `<title> (#N)` merge -- the
        # record-autofix merges #2413/#2412/#2407 -- was never checked.
        both = ("Merge pull request #77 from tvofi/x\n"
                "record: delivery rows for #2397 (autofix) (#2413)\n"
                "ci: record nightly kills\n"
                "Merge remote-tracking branch 'origin/main' into x")
        t = tick(handover=old, behind_handover=3, rows=both)
        t._git.h.insert(0, (("cat-file", "-e", f"{ROW_DIR}77.md"), 0, ""))
        t.state()
        missing = [x["text"] for x in t.findings
                   if x["text"].startswith("merged PRs without a delivery row")]
        t2 = tick(handover=old, behind_handover=3, rows=both)
        t2._git.h.insert(0, (("cat-file", "-e"), 0, ""))
        t2.state()
        t3 = tick(handover=old, behind_handover=3, rows=both)
        t3._git.h.insert(0, (("--first-parent",), 128, "fatal: bad revision"))
        t3.state()
        a, f = check("STATE missing rows", [
            ("a squash `<title> (#N)` merge with no row is named; a rowed merge, "
             "a direct push and a numberless merge are not",
             missing == ["merged PRs without a delivery row at origin/main: #2413"]),
            ("null control: every merge rowed names none",
             not any(x["text"].startswith("merged PRs without")
                     for x in t2.findings)),
            ("a log it cannot read is UNREADABLE, never a clean zero",
             any("UNREADABLE: merges since updated-for" in x["text"]
                 for x in t3.findings)),
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

        # ---- closes over a squash `<title> (#N)` merge ----
        t = tick(handover=old, behind_handover=3,
                 merges24="record: delivery rows (autofix) (#83)",
                 bodies={83: "Closes #301\n\nproper sentence."},
                 graphql={83: [{"number": 301}, {"number": 302}]})
        t.state()
        a, f = check("closes squash", [
            ("a squash merge's declared-vs-closed mismatch is flagged",
             any("closes mismatch" in x["text"] and "#302" in x["text"]
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

        # ---- C. OWED handoffs (bus.sh orphans, its real output shape) ----
        # bus.sh exits 1 when a ref is stranded and prints its summary line on
        # every completed run; the old stub (rc 0, bare ref names, no summary)
        # encoded the reading that turned every live finding into "unavailable".
        orph = (f"ORPHAN r10-sav-baseline {'f2' * 20} 3.1h uncovered=2 "
                "repair=update")
        t = tick(bus_refs=[orph, f"SUPERSEDED r9-old {'5' * 40} 30.0h",
                           "orphans: 1 stranded, 1 superseded; skipped no-body=0 "
                           "named=0 ancestor=0 young=0; origin main b87e8f1"], bus_rc=1)
        t.orphans("REPLAN")
        a, f = check("OWED handoffs", [
            ("a stranded ref at bus.sh's rc 1 is OWED, flagged, never 'unavailable'",
             any(x["text"].startswith("OWED handoff: r10-sav-baseline ")
                 and "repair=update" in x["text"] for x in t.findings)
             and not any("unavailable" in x["text"] for x in t.findings)),
            ("a superseded ref is a prune line, unflagged",
             any(l["text"].startswith("superseded handoff ref r9-old")
                 and not l["flag"] for l in t.sections["REPLAN"])),
            ("the read carries no age window (a complete handoff is owed now)",
             bus_calls[-1] == ["orphans", "--min-age-h", "0"]),
        ])
        total, failed = total + a, failed + f
        t = tick(bus_refs=[BUS_CLEAR])
        t.orphans("REPLAN")
        a, f = check("OWED handoffs all-clear", [
            ("null control: 0 stranded prints the summary and flags nothing",
             not any(x["section"] == "REPLAN" for x in t.findings)
             and any(l["text"] == BUS_CLEAR for l in t.sections["REPLAN"])),
        ])
        total, failed = total + a, failed + f
        t = tick(bus_refs=["bus: REFUSE: orphans: could not fetch"], bus_rc=1)
        t.orphans("REPLAN")
        t2 = tick(bus_refs=[orph, BUS_CLEAR], bus_rc=0)
        t2.orphans("REPLAN")
        a, f = check("OWED handoffs refused", [
            ("a refusal (rc 1, no summary) is unavailable, not a clean zero",
             any("bus.sh orphans unavailable" in x["text"] for x in t.findings)
             and not any(x["text"].startswith("OWED handoff") for x in t.findings)),
            ("an exit that contradicts its lines (rc 0 beside an ORPHAN) is unavailable",
             any("bus.sh orphans unavailable" in x["text"] for x in t2.findings)),
        ])
        total, failed = total + a, failed + f

        # ---- CARRY: the weekly and closure carry sweep (#2404's carry_audit.py) ----
        calls: list = []

        def sweep(rc, lines):
            return lambda argv: calls.append(argv) or (rc, lines)
        summ = "CARRY-SWEEP: 20 pull request(s), 2 other unowned finding(s)"
        t = tick(roster_ref="origin/r10", carry=sweep(1, [
            "ISSUE-UNOWNED #2409 'an issue no group lists'",
            "ROSTER-DRIFT R10-X: a carry on origin/main is missing on origin/r10: 'c'",
            summ]))
        t.carry_sweep()
        fl = [x["text"] for x in t.findings if x["section"] == "CARRY"]
        t0 = tick(carry=sweep(0, ["CARRY-SWEEP: 20 pull request(s), 0 other unowned finding(s)"]))
        t0.carry_sweep()
        t2 = tick(carry=sweep(2, ["carry_audit: REFUSED no roster at origin/main"]))
        t2.carry_sweep()
        n_before = len(calls)
        t3 = tick(carry=sweep(0, ["CARRY-SWEEP: 0 pull request(s), 0 other unowned finding(s)"]))
        t3.run()
        default_pass_swept = len(calls) != n_before
        t3.run(["CARRY"])
        a, f = check("CARRY sweep", [
            ("exit 1 prints one dispatch line, then each unowned line, flagged",
             len(fl) == 3 and fl[0].startswith("carry sweep found unowned findings")
             and "ISSUE-UNOWNED #2409" in fl[1] and "ROSTER-DRIFT R10-X" in fl[2]),
            ("the sweep runs --last N --issues over origin/main, then the tick's roster ref",
             calls[:1] == [["--roster-ref", "origin/main", "--roster-ref", "origin/r10",
                            "sweep", "--last", str(CARRY_LAST), "--issues"]]),
            ("null control: exit 0 prints the summary and flags nothing",
             not any(x["section"] == "CARRY" for x in t0.findings)
             and any(l["text"].startswith("carry sweep: CARRY-SWEEP:")
                     for l in t0.sections["CARRY"])),
            ("one roster ref is passed once, not twice",
             calls[1:2] == [["--roster-ref", "origin/main", "sweep", "--last",
                            str(CARRY_LAST), "--issues"]]),
            ("a refusal (exit 2) is UNREADABLE, never a clean zero",
             any("UNREADABLE: carry sweep" in x["text"] for x in t2.findings)),
            ("opt-in: the default pass never sweeps; --only CARRY does",
             not default_pass_swept and len(calls) == n_before + 1),
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
             and not any(x["text"].startswith("OWED handoff")
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

        # ---- the open-PR cap and the coordinator count (tvofi, 2026-10-18) ----
        coord, row = "custom_components/heatpump_optimizer/coordinator.py", "dev/programme/delivery/1.md"
        app, dep = {"login": "app/hpo-author", "is_bot": True}, {"login": "app/dependabot", "is_bot": True}

        def cap_board(specs):  # [(n, title, author, files | None)] -> the PRS lines
            heads = {n: f"{n:040x}" for n, *_ in specs}
            t = tick(prs=[{**pr_obj(n, heads[n]), "title": ti, "author": au} for n, ti, au, _ in specs])
            t.checkout = str(version)
            base, fs = git_factory(), {heads[n]: f for n, _, _, f in specs}

            def git(argv):
                if argv[:1] == ["diff"]:
                    f = fs.get(argv[-1])
                    return (0, f) if f is not None else (1, "unreadable")
                return base(argv)
            t.git = git
            t.prs(["tests"])
            return t.sections["PRS"]

        def one(lines, prefix):
            hits = [l for l in lines if l["text"].startswith(prefix)]
            return hits[0] if len(hits) == 1 else {"flag": None, "text": f"{len(hits)} lines"}

        at = cap_board([(n, "t", app, f"{row} {coord}" if n < 3 else row) for n in range(6)])
        below = cap_board([(n, "t", app, f"{row} {coord}" if n < 2 else row) for n in range(5)]
                          + [(7, "record: rows", app, coord), (8, "bump", dep, coord)])
        unread = cap_board([(1, "t", app, row), (2, "t", app, None)])
        old_cap = os.environ.get("HPO_OPEN_PR_CAP")
        os.environ["HPO_OPEN_PR_CAP"] = "x"
        try:
            badcap = cap_board([(1, "t", app, row)])
        finally:
            if old_cap is None:
                os.environ.pop("HPO_OPEN_PR_CAP", None)
            else:
                os.environ["HPO_OPEN_PR_CAP"] = old_cap
        a, f = check("open-PR cap", [
            ("six counted: OPEN-PR CAP: 6/6, flagged",
             one(at, "OPEN-PR CAP: ")["flag"] is True and one(at, "OPEN-PR CAP: ")["text"].startswith("OPEN-PR CAP: 6/6")),
            ("five counted beside a record: and a bot PR: 5/6, not flagged",
             one(below, "OPEN-PR CAP: ") == {"flag": False, "text": "OPEN-PR CAP: 5/6"}),
            ("three counted PRs touch the coordinator: 3/2, flagged",
             one(at, "coordinator.py PRs: ") == {"flag": True, "text": "coordinator.py PRs: 3/2 (#0, #1, #2)"}),
            ("two counted touch it (the record and bot ones uncounted): 2/2, not flagged",
             one(below, "coordinator.py PRs: ") == {"flag": False, "text": "coordinator.py PRs: 2/2 (#0, #1)"}),
            ("a diff it cannot read flags the coordinator count as a floor",
             one(unread, "coordinator.py PRs: ")["flag"] is True
             and "UNREADABLE at #2, so at least 0" in one(unread, "coordinator.py PRs: ")["text"]),
            ("an invalid HPO_OPEN_PR_CAP is UNREADABLE, never a count",
             any(l["flag"] and "UNREADABLE: open-PR cap" in l["text"] for l in badcap)
             and one(badcap, "OPEN-PR CAP: ")["flag"] is None),
        ])
        total, failed = total + a, failed + f

        # ---- verdict levels: MERGE-READY / BLOCKED-UNFIXED (2026-10-18) ----
        apr = {"login": "hpo-approver[bot]", "id": 330097732, "type": "Bot"}
        old_h, vt = "9" * 40, iso(NOW - datetime.timedelta(hours=1))

        def vc(cid, body, at=vt, user=apr):
            return {"id": cid, "user": user, "created_at": at, "body": body}

        def vboard(specs, handoffs=None, fail=()):  # [(n, ms, [comments])], {topic: commit-epoch}
            heads = {n: f"{n:040x}" for n, *_ in specs}
            extra = [((f"issues/{n}/comments?per_page=100",), 1 if n in fail else 0,
                      "HTTP 502" if n in fail else json.dumps([cs])) for n, _, cs in specs]
            board = [pr_obj(n, heads[n], ms=ms) for n, ms, _ in specs]
            t = tick(prs=board, gh_extra=extra)
            for topic, ct in (handoffs or {}).items():
                t._git.on(("ls-remote", f"refs/heads/handoff/{topic}"), out=f"{'7' * 40}\trefs/heads/handoff/{topic}\n")
            t._git.on(("ls-remote",), out="")
            t._git.on(("log", "-1", "--format=%ct"), out=str(int(min((handoffs or {"_": 0}).values()))))
            t.verdict_levels("PRS", board)
            return t.sections.get("PRS", []), heads

        h = lambda n: f"{n:040x}"
        lines, heads = vboard([
            (40, "CLEAN", [vc(1, f"Fix review: merge {h(40)}\n\nRESULT ok")]),
            (41, "CLEAN", [vc(2, f"Fix review: merge {old_h}")]),
            (42, "DIRTY", [vc(3, f"Fix review: merge {h(42)}")]),
            (43, "UNSTABLE", [vc(4, f"Fix review: blocked {h(43)} harness: x", at=iso(NOW - datetime.timedelta(hours=3))),
                              vc(5, f"Fix review: merge {h(43)}")]),
            (44, "BLOCKED", [vc(6, f"Fix review: blocked {h(44)} harness: class open")]),
            (45, "CLEAN", [vc(7, f"Fix review: merge {h(45)}", user={"login": "tvofi", "id": 1, "type": "User"})]),
            (46, "BLOCKED", [vc(8, f"Fix review: blocked {old_h} harness: x")]),
        ])
        txt = [l["text"] for l in lines]
        fixed, _ = vboard([(47, "BLOCKED", [vc(9, f"Fix review: blocked {h(47)} harness: x")])],
                          handoffs={"47": int((NOW - datetime.timedelta(minutes=10)).timestamp())})
        stale_fix, _ = vboard([(48, "BLOCKED", [vc(10, f"Fix review: blocked {h(48)} harness: x")])],
                              handoffs={"48": int((NOW - datetime.timedelta(hours=2)).timestamp())})
        unread, _ = vboard([(49, "CLEAN", [])], fail=(49,))
        a, f = check("verdict levels", [
            ("a merge verdict at the current head, CLEAN: MERGE-READY, flagged",
             any(l["flag"] and l["text"] == f"MERGE-READY: #40 {h(40)[:8]}" for l in lines)),
            ("null control: a merge verdict at a stale head prints no MERGE-READY",
             not any(x.startswith("MERGE-READY: #41") for x in txt)),
            ("a merge verdict at the head while DIRTY prints none",
             not any(x.startswith("MERGE-READY: #42") for x in txt)),
            ("the newest verdict wins, and UNSTABLE is merge-ready",
             f"MERGE-READY: #43 {h(43)[:8]}" in txt and not any(x.startswith("BLOCKED-UNFIXED: #43") for x in txt)),
            ("blocked at the head with no handoff ref: BLOCKED-UNFIXED, flagged",
             any(l["flag"] and l["text"] == f"BLOCKED-UNFIXED: #44 {h(44)[:8]}" for l in lines)),
            ("a verdict not from the approver App is ignored",
             not any("#45" in x for x in txt)),
            ("null control: blocked at a stale head prints no BLOCKED-UNFIXED",
             not any("#46" in x for x in txt)),
            ("a handoff tip committed after the blocked verdict: no BLOCKED-UNFIXED",
             not any(l["text"].startswith("BLOCKED-UNFIXED") for l in fixed)),
            ("a handoff tip committed before it still prints BLOCKED-UNFIXED",
             any(l["text"] == f"BLOCKED-UNFIXED: #48 {h(48)[:8]}" for l in stale_fix)),
            ("comments it cannot read are UNREADABLE, never silence",
             any(l["flag"] and "UNREADABLE: verdicts on #49" in l["text"] for l in unread)),
        ])
        total, failed = total + a, failed + f

        # ---- OWED from cloud_relay.sh's log (2026-10-18) ----
        def owed_lines(text):
            lg = tmp / "relay.log"
            if text is None:
                lg.unlink(missing_ok=True)
            else:
                lg.write_text(text)
            t = tick(relay_log=str(lg))
            t.relay_owed("PRS")
            return t.sections.get("PRS", [])

        o1 = f"OWED 2026-10-18T19:00:00Z 7 {'a' * 40} bus.sh confirm failed; run it by hand"
        o2 = "OWED 2026-10-18T19:05:00Z 8 - push-verdict printed no 40-hex review commit"
        p1 = f"POSTED 2026-10-18T19:10:00Z 7 {'a' * 40}"
        o3 = f"OWED 2026-10-18T19:20:00Z 7 {'b' * 40} confirm failed"
        both = owed_lines("\n".join([o1, o2]) + "\n")
        healed = owed_lines("\n".join([o1, p1]) + "\n")
        again = owed_lines("\n".join([o1, p1, o3]) + "\n")
        none = owed_lines(None)
        twice = owed_lines("\n".join([o1, o3]) + "\n")
        a, f = check("relay OWED", [
            ("each OWED with no later POSTED prints OWED: <line>, flagged",
             [l["text"] for l in both if l["flag"]] == [f"OWED: {o1}", f"OWED: {o2}"]),
            ("null control: an OWED followed by a POSTED prints nothing",
             not any(l["text"].startswith("OWED:") for l in healed)),
            ("an OWED after that POSTED prints again, alone",
             [l["text"] for l in again if l["text"].startswith("OWED:")] == [f"OWED: {o3}"]),
            ("two OWED for one PR with no POSTED print both, each entry",
             [l["text"] for l in twice if l["flag"]] == [f"OWED: {o1}", f"OWED: {o3}"]),
            ("no log yet is no OWED and no flag",
             not any(l["flag"] for l in none) and any("cloud-relay log: none yet" in l["text"] for l in none)),
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
    ap.add_argument("--roster-ref", default=None,
                    help="default origin/main (roster_lib.DEFAULT_ROSTER_REF)")
    ap.add_argument("--roster-path", default=None,
                    help="the roster at --roster-ref (default: the newest "
                         "dev/programme/rosters/wave-r<N>-groups.json there)")
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
                    help="comma-separated: TRAIN,PRS,ETA,WORKERS,PLAN,MAIN,STATE,REPLAN; "
                         "CARRY (opt-in, weekly and at closure) runs only when named")
    ap.add_argument("--carry-last", type=int, default=CARRY_LAST,
                    help="CARRY: the merged pull requests the sweep reads")
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
             roster_ref=a.roster_ref, roster_path=a.roster_path,
             mandate_id=a.mandate_id,
             mandate_since_days=a.mandate_since_days,
             stall_hours=a.stall_hours, behind_max=a.behind_max,
             carry_last=a.carry_last)
    rep = t.run(only)
    print(json.dumps(rep, indent=1) if a.json else render(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
