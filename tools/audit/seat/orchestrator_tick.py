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
  MAIN    main's tip sha; any non-green required context (the ruleset re-read
          every tick -- nudge.md step 4: never a remembered list); non-required
          autofix/record/nightly reds at the tip (the nightly bot class); the
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

API cost: one full tick is roughly 2 + 5x(open PRs) calls (list, bodies,
check-runs per head, ruleset, comments) -- at 20 open PRs about a hundred;
run it at the orchestrator's five-minute cadence, never in a poll loop.
--only limits which sections run (MAIN before PRS shares the required read).

Output: one line per fact, flagged lines prefixed `-> ` (the orchestrator
acts top-down); `--json` for machine use. Exit 0 unless --self-test fails:
the list is a report, not a gate. The null control (an all-clear board)
prints the empty dispatch list and exits 0.
"""

from __future__ import annotations

import argparse
import datetime
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
USES = re.compile(r"^\s*-?\s*uses:\s*([\w.-]+/[\w.-]+)@(\S+)", re.M)
NIGHTLY_CLASS = re.compile(r"autofix|record|nightly|closures", re.I)
DEFERRED_STAGES = ("deferred", "refused")
UNBLOCKABLE_STAGES = (None, "", "not-started")
#: The shared actions whose pin the whole lane rides; a pin drift on one of
#: these is the class that reddened a composed proof on a twin SHA.
STATE_ACTIONS = ("actions/checkout", "actions/setup-node", "actions/cache",
                 "actions/upload-artifact", "actions/download-artifact",
                 "github/codeql-action/init", "github/codeql-action/analyze")


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

    def __init__(self, repo: str, checkout: str, queue: str | None = None,
                 train_log: str | None = None, workers_file: str | None = None,
                 roster_file: str | None = None,
                 roster_ref: str | None = "origin/handoff/audit-r9-fixplan",
                 mandate_id: int | None = None, stall_hours: float = 2.0,
                 grace_hours: float = 0.5, behind_max: int = 25,
                 mandate_since_days: int = 14,
                 now: datetime.datetime | None = None,
                 gh=None, git=None, proc=None) -> None:
        self.repo, self.checkout = repo, checkout
        self.queue, self.train_log = queue, train_log
        self.workers_file = workers_file
        self.roster_file, self.roster_ref = roster_file, roster_ref
        self.mandate_id, self.mandate_since_days = mandate_id, mandate_since_days
        self.stall_hours, self.grace_hours = stall_hours, grace_hours
        self.behind_max = behind_max
        self.now = now or datetime.datetime.now(datetime.timezone.utc)
        self._gh, self._git, self._proc = gh, git, proc
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
        if not self.queue:
            return []
        try:
            with open(self.queue, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError) as e:
            self.unreadable("TRAIN", f"queue {self.queue}", str(e)[:120])
            return None

    # -------------------------------------------------------------- TRAIN
    def train(self) -> None:
        S = "TRAIN"
        live = [p for p in self.proc("merge_train.py")
                if "orchestrator_tick" not in p[1]]
        if live:
            self.line(S, f"train alive: pid {live[0][0]} ({len(live)} process(es)); "
                         "it holds every merge -- load nothing else")
        else:
            self.line(S, "train not alive")
        preprs = self.proc("prepr.sh")
        self.line(S, f"prepr slots: {len(preprs)} running (cap 4)"
                  + ("" if len(preprs) < 4 else " -- do not start a fifth"),
                  flag=len(preprs) >= 4)
        queue = self._queue()
        if queue is not None:
            if not queue:
                self.line(S, "queue empty" if self.queue else "no --queue given")
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
                           "mergeStateStatus,title,createdAt"])
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
        for pr in sorted(prs, key=lambda p: p["number"]):
            n, head = pr["number"], pr.get("headRefOid") or ""
            if head:
                by_head.setdefault(head, []).append(n)
            self.one_pr(S, pr, verdicts.get(n), required)
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
                  if (c.get("completed_at") or "") > str(w.get("dispatched_at", ""))]
        if new_ci:
            self.line(S, f"{seat}: OK (CI completed at #{pr}'s head since "
                         f"dispatch: {len(new_ci)} run(s)) {tail}")
        elif hours <= self.grace_hours:
            self.line(S, f"{seat}: OK (recently dispatched, inside the "
                         f"{self.grace_hours}h CI grace) {tail}")
        else:
            self.line(S, f"{seat}: STALLED? head unchanged and no new CI "
                         f"completion since dispatch {tail}", flag=True)

    # ---------------------------------------------------------------- PLAN
    def plan(self) -> None:
        S = "PLAN"
        rl = _module("roster_lib_tick", "tools/audit/seat/roster_lib.py")
        if rl is None:
            self.unreadable(S, "roster", "roster_lib.py not found in the tree")
            return
        if self.roster_file:
            try:
                roster = rl.load_roster_file(self.roster_file)
            except (OSError, ValueError) as e:
                self.unreadable(S, f"roster file {self.roster_file}", str(e)[:120])
                return
        else:
            code, o = self.git(["show", f"{self.roster_ref or 'origin/main'}:"
                                f"{rl.ROSTER_PATH}"])
            if code:
                self.unreadable(S, f"roster at {self.roster_ref}", o.strip()[-120:])
                return
            try:
                roster = json.loads(o)
            except ValueError as e:
                self.unreadable(S, f"roster at {self.roster_ref}", str(e)[:120])
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
        self.mandate(S)
        self.pins(S)
        code, o = self.git(["rev-list", "--count", "HEAD..origin/main"])
        if code == 0 and o.strip().isdigit() and int(o) > 0:
            self.line(S, f"checkout is {o.strip()} commit(s) behind origin/main "
                         "(an ancestor checkout is not current)", flag=True)
        elif code != 0:
            self.unreadable(S, "checkout staleness", o.strip()[-80:])

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

    def mandate(self, S: str) -> None:
        """The one mandate reading: budget_raise_gate's mandate_state over the
        tracking issue's comments -- the newest grammar-matching owner comment
        within --mandate-since-days, or exactly --mandate-id. The search
        window is stated in the output so a quiet window is never mistaken
        for an all-clear."""
        g = _module("budget_raise_gate_tick", "tools/policy/budget_raise_gate.py",
                    ".claude/workflows/budget_raise_gate.py")
        if g is None or not hasattr(g, "mandate_state"):
            self.unreadable(S, "mandate", "budget_raise_gate.py not importable")
            return
        if self.mandate_id:
            code, o = self.gh(["api",
                               f"repos/{self.repo}/issues/comments/{self.mandate_id}"])
            if code:
                self.unreadable(S, f"mandate comment {self.mandate_id}",
                                o.strip()[-100:])
                return
            try:
                cands, since = [json.loads(o)], None
            except ValueError as e:
                self.unreadable(S, f"mandate comment {self.mandate_id}",
                                str(e)[:100])
                return
        else:
            start = (self.now - datetime.timedelta(
                days=self.mandate_since_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            cands = self._thread(start)
            if cands is None:
                return
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
            return
        m = cands[-1]
        thread = self._thread(m.get("created_at") or "", exclude=m.get("id"))
        ok, why = g.mandate_state(m.get("id"), m, thread or [], self.now,
                                  self.now.isoformat(), when="tick",
                                  covers=g.MANDATE_COVERS_POLICY,
                                  what="policy merging")
        self.line(S, f"mandate: {'in force' if ok else 'NOT in force'}: {why}",
                  flag=not ok)

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

    # ----------------------------------------------------------------- run
    def run(self, only: "list[str] | None" = None) -> dict:
        order = ["TRAIN", "PRS", "WORKERS", "PLAN", "MAIN"]
        todo = [s for s in order if not only or s in only]
        for s in todo:  # stable section order in the report
            self.sections.setdefault(s, [])
        req = None
        if "MAIN" in todo and "PRS" in todo:
            code, o = self.gh(["api", f"repos/{self.repo}/commits/main",
                               "--jq", ".sha"])
            if code == 0 and o.strip():
                req = self.required("MAIN")
        for s in todo:
            if s == "TRAIN":
                self.train()
            elif s == "PRS":
                self.prs(req)
            elif s == "WORKERS":
                self.workers()
            elif s == "PLAN":
                self.plan()
            elif s == "MAIN":
                self.main()
        return self.report()

    def report(self) -> dict:
        return {"repo": self.repo, "generated_at": self.now.isoformat(),
                "api_calls": self.api_calls, "findings": self.findings,
                "sections": self.sections}


def render(report: dict) -> str:
    """The compact text form: one line per fact, `-> ` on a flagged finding."""
    out = []
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
            started=NOW, done=NOW) -> dict:
    return {"name": name, "status": status, "conclusion": conclusion,
            "started_at": iso(started),
            "completed_at": iso(done) if status == "completed" else None}


def pr_obj(n, head, ms="CLEAN", branch=None) -> dict:
    return {"number": n, "headRefOid": head, "headRefName": branch or f"fix/{n}",
            "mergeStateStatus": ms, "title": "t", "createdAt": iso(NOW)}


def check(label: str, arms: list[tuple[str, bool]]) -> tuple[int, int]:
    for name, ok in arms:
        if not ok:
            print(f"  FAIL {label}: {name}")
    return len(arms), sum(1 for _, ok in arms if not ok)


def self_test() -> int:
    total = failed = 0
    g = _module("budget_raise_gate_tick", "tools/policy/budget_raise_gate.py",
                ".claude/workflows/budget_raise_gate.py")
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
             with_mandate=True, **kw) -> Tick:
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
        git = Stub()
        git.on(("fetch",), out="")
        git.on(("merge-base", "--is-ancestor"), rc=0)
        git.on(("merge-base", "origin/main"), out=V)
        git.on(("diff", "--name-only"), out=kw.pop("files", "dev/programme/delivery/9.md"))
        git.on(("rev-list", "--count", f"{H1}..origin/main"), out=str(behind))
        git.on(("rev-list",), out="0")
        t = Tick("o/r", str(kw.pop("checkout", ROOT)), queue=queue,
                 train_log=train_log, workers_file=workers, roster_file=roster,
                 gh=gh, git=git, proc=lambda pattern: [], now=NOW, **kw)
        return t

    def git_factory(files="dev/programme/delivery/9.md", show=None, behind="0"):
        show = show or {}

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
            ("zero findings", rep["findings"] == []),
            ("empty list line printed", "DISPATCH LIST: empty" in text),
            ("all five sections measured",
             set(rep["sections"]) == {"TRAIN", "PRS", "WORKERS", "PLAN", "MAIN"}),
        ])
        total, failed = total + a, failed + f

    print(f"orchestrator_tick self-test: {total} checks, {failed} failed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="the heartbeat's dispatch list")
    ap.add_argument("--repo",
                    default=os.environ.get("HPO_REPO", "tvofi/heatpump_optimizer"))
    ap.add_argument("--checkout", default=str(ROOT))
    ap.add_argument("--queue")
    ap.add_argument("--train-log")
    ap.add_argument("--workers-file")
    ap.add_argument("--roster-file")
    ap.add_argument("--roster-ref", default="origin/handoff/audit-r9-fixplan")
    ap.add_argument("--mandate-id", type=int)
    ap.add_argument("--mandate-since-days", type=int, default=14)
    ap.add_argument("--stall-hours", type=float, default=2.0)
    ap.add_argument("--grace-hours", type=float, default=0.5,
                    help="no new CI completion inside this window is not a stall")
    ap.add_argument("--behind-max", type=int, default=25)
    ap.add_argument("--only", help="comma-separated: TRAIN,PRS,WORKERS,PLAN,MAIN")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.workers_file and a.queue:
        sib = Path(a.queue).parent / "workers.json"
        if sib.exists():
            a.workers_file = str(sib)
    only = [s.strip() for s in a.only.split(",")] if a.only else None
    t = Tick(a.repo, a.checkout, queue=a.queue, train_log=a.train_log,
             workers_file=a.workers_file, roster_file=a.roster_file,
             roster_ref=a.roster_ref, mandate_id=a.mandate_id,
             mandate_since_days=a.mandate_since_days,
             stall_hours=a.stall_hours, behind_max=a.behind_max)
    rep = t.run(only)
    print(json.dumps(rep, indent=1) if a.json else render(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
