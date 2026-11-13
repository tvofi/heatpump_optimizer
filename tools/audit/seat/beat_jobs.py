#!/usr/bin/env python3
"""beat_jobs.py -- the beat's job rows: each writes only actionable lines to one digest.

    python3 -I tools/audit/seat/beat_jobs.py ROW --state S [--repo DIR] [--overlay FILE] [--board FILE]
    python3 -I tools/audit/seat/beat_jobs.py fold --state S
    python3 -I tools/audit/seat/beat_jobs.py --self-test [--no-mutants]

WHY THIS EXISTS (R10-FLY-STANDING-CONTRACTS P1, design note on
design/r10-fly-standing-contracts 21210036). The standing tick and roster
seats, and the sweep runner's loops, ran as out-of-tree stand-ins whose output
lived in private logs. Each is a row of `beatd.jobs.json` here, run by
`beatd.py`, and every row writes into one digest the orchestrator's one wake
reads. This file owns every row's predicate; it calls the instruments it names
and edits none of them.

THE DIGEST, `S/digest/` (S is `--state`, the beat's `$HPO_STATE_DIR`). This
file is its only writer:
  jobs/<row>     the row's actionable lines, stamps and ages normalised,
                 written atomically and only when they changed;
  digest.txt     every jobs file, concatenated in row order;   written by fold()
  new.txt        the lines the last changing fold added (empty when it added none);  by fold()
  gone.txt       the lines the last changing fold dropped (empty when it dropped none); by fold()
  new.stamp      touched (the fold's UTC) only when that fold added a line;
  events.txt     `<utc> HEAD-MOVED #<n> <old12> <new12>` (head-watch) and
                 `<utc> STUCK ...` (opener) lines, appended once each;
  heads.tsv      head-watch's last-seen head per open pull request;
  state/         each row's own memory (tick passes, roster marks, holds).
fold() runs under `flock digest/.lock`. A null pass changes no byte; the wake
reads only `new.stamp` and `events.txt`. `S/events.tsv` is ledger.py's and no
row writes it. Outside `digest/` the one write is the pulse row's: pulse.py's
output into `S/beatd/pulse.txt`, the file `beatd.py status` reads.

THE SESSION'S PATHS come from the sweep overlay (`--overlay`, default
`S/sweep-overlay.json`), the same JSON `sweep_render.py` fills the sweep from,
so no second list exists. A row whose key it lacks writes
`<row>: UNREADABLE overlay lacks <key>`, never nothing. The board is
`--board`, else the overlay's `tick_log`, else `S/tick.txt` (`tick_loop.sh
--out`'s default).

ROWS (the job table's `interval_s` in brackets):
  tick-digest [240]  the board's flagged (`-> `) lines of the actionable family
                     (FAMILY); a `NOT REVIEWABLE` or `RED unanswered` line
                     counts only once a second board in a row carries it (a
                     read between open_pr's two pushes is transient). One pass
                     per board: an unchanged provenance line is no pass.
  owed-check [1800]  owed_unactioned.py once per sweep, never per tick pass:
                     `UNACTIONED <key> sweeps=<n>` on rc 1, `UNREADABLE` on 2.
  roster-drain [120] each pending op of `S/roster-drain.queue` through
                     roster_queue.py `run`, one at a time; every `roster:` line
                     it reports goes to the digest and the exact line (text and
                     occurrence) is marked done in `state/` as soon as it ran,
                     refused or not: a refusal is never retried, and a pass
                     killed mid-queue replays at most the op it was killed in.
                     No op starts past ROSTER_PASS_BUDGET_S into a pass; the
                     rest wait for the next. `hold <tree-path> <op...>` waits
                     until `origin/main:<tree-path>` exists, and is
                     `roster: HOLD-STALE` after HOLD_STALE_S. Done or refused is
                     read from the exact line roster_queue's `--mark` rewrites
                     (`#done <op>` / `#refused <op>`): an op it neither reported
                     nor marked is `roster: UNRUN` and stays pending; a refusal
                     because the worktree is on no origin ref (an earlier
                     refusal's leftover) stays pending under one `roster:
                     CASCADE` line. The lint clone is `S/roster-lint`, the
                     orchestrator's to provision.
  plan-beat [1800]   replan.py `--out`, then state_docs.py `--push --mirror
                     --plan`; `plan-beat: PLAN UNAVAILABLE` on a replan failure
                     or state_docs rc 1, `plan-beat: REFUSED` on its rc 2; on
                     success `plan-beat: PLAN MOVED` when the mirrored PLAN.html
                     differs from the last pass's (a republish is owed). A
                     pass whose state push landed (`pushed ` on rc 0 or 1)
                     dispatches `pages.yml` on main, which publishes the page
                     at plan_public.PLAN_URL; `plan-beat: PAGES NOT DISPATCHED`
                     when gh refuses.
  gantt [1800]       sweep_gantt.py against `plan_json`, its baseline in
                     `state/gantt/`, the `gantt_acks` file, the roster at
                     `gantt_roster` (`<branch>:<path>`), the open pull requests,
                     the handoff tips (fetched to `refs/gantt/`) and the
                     overlay's `fire_ledger`; its GANTT-SLIP and GANTT-BASELINE lines.
  verdict-audit [1800] verdict_audit.py `--repo` (+ `fire_ledger`, `train_glob`,
                     `unheld_skip`); its UNHELD lines.
  pulse [300]        pulse.py into `S/beatd/pulse.txt`; its STOPPED and
                     UNREADABLE lines to the digest.
  cancel-sweep [600] cancel_superseded.py `sweep --repo R`; failures only.
  disk [900]         worktree_gc.sh when `/` has under `disk_floor_gib` free;
                     a line only if still under afterwards.
  opener [300]       open_driver.py `--board` (one pass; its state stays in
                     `S/open-driver/`); its `OWED ... open-refused`,
                     `NEEDS-TITLE`, `STARVED` and `STUCK` lines, STUCK also
                     to events.txt.
  head-watch [120]   open pull-request heads from the API against heads.tsv.
  audit-dispatch [1800] review_strength.py `--fetch --guardrail`; each arm line
                     that reads `would-trip` gives one `DISPATCH: planted-defect-audit
                     arm=<arm> cut=<first..last verdict>` line, once per sustained trip of an arm
                     (owner ruling tvofi 2026-11-01: P0 0.28, ALPHA 0.05, never blocks).
                     An arm stays dispatched while it reads `would-trip` and is
                     dispatched again only after it reads `ok` or `insufficient`.
                     The guardrail's exit code is not read as a verdict; a failed run
                     is UNREADABLE until the next readable run clears it.
  outside-intake [1800] outside_intake.py `list --since <intake_since>
                     --cursor state/outside-cursor.json`: its `OUTSIDE` lines
                     (submissions by outside users owed a triage, an answer or
                     a reply this turn), `outside-intake: UNREADABLE` on rc 2.
  darwin-selftest [900] Darwin hosts only (any other host runs nothing, not even git).
                     At each new origin/main tip (one run per tip; the tip is
                     remembered in `state/darwin-selftest.json`, so an unchanged
                     tip is skipped), under a heavy slot of tests/gate_lock.py,
                     in a detached worktree this row makes under `state/` and
                     removes (it writes into no checkout it tests): `prepr.sh
                     --self-test`, then `--self-test` of each script under
                     tools/audit/seat that selftest_wiring.py reports as both
                     self-testing and wired in a workflow. One line per red,
                     `darwin-selftest: RED <instrument> <first FAIL line>`; the
                     digest has none when every one is green. WHY: CI runs the
                     self-tests on Linux only, so a Darwin-only read (mutant_run.py
                     listing /proc) was found only when an opener failed. It
                     detects after the merge; it does not prevent.
  bottleneck [1800]  bottleneck_check.py `--checkout <repo> --train-log
                     <train_log> --wip-cap <plan_slots> --memory
                     state/bottleneck.json`: its `BOTTLENECK:` and
                     `BOTTLENECK-UNREADABLE:` lines (the flow metrics past the
                     owner's thresholds, 2026-11-07); a held breach re-prints its
                     first line, so it is new once per trip. A line suggests; the
                     orchestrator decides. `bottleneck: UNREADABLE` on a non-zero rc.
  scorecard [86400]  scorecard.py `report --dir S/scorecard --train-log <train_log>
                     [--sweep-record <sweep_record>]` into `S/beatd/scorecard.txt`
                     (ten report-only lines, none a gate); the digest hears only
                     `scorecard: UNREADABLE rc=<n>` when the instrument fails.
No row runs `git checkout`, `reset`, `pull` or `merge`; main is read as
`git -C <repo> cat-file -e origin/main:<path>`. No row touches a seat's alive
file. Every row exits 0 once its lines are written: the digest is the signal,
and beatd's own outcome stays `ok` unless this file crashed.
"""
from __future__ import annotations

import argparse
import collections
import fcntl
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
        "cancel-sweep", "disk", "opener", "head-watch", "audit-dispatch", "outside-intake", "bottleneck", "scorecard",
        "darwin-selftest")
HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
#: roster-drain starts no op past this many seconds into a pass; the rest wait for the next pass. At
#: most half the row's timeout_s in beatd.jobs.json (the self-test pins it), so an op started just
#: before it has as long again (the orchestrator saw ~45 s an op through roster_queue's lint gate).
ROSTER_PASS_BUDGET_S = 450
#: The board's actionable family (carry 20's list), keyed on the texts
#: orchestrator_tick.py and ledger.py print; the self-test pins each literal there.
FAMILY = re.compile(
    r"^(?:OWED\b|DISPATCH:|OWNER FLAG:|BLOCKED-UNFIXED:|DESIGN-BUILD:|UNREADABLE:|DESIGN OWED:"
    r"|REVIEW OWED:|RECORD-OWED:|REVIEW STALLED:|UNLEVELLED:|APPROVAL-OWED:|MERGE-READY:|main-red "
    r"|main \S+: REQUIRED not green"
    r"|#\d+: (?:RAISE APPROVAL OWED|NOT REVIEWABLE|mergeable state DIRTY|RED unanswered"
    r"|code-owned with no \S+ review))")
TRANSIENT = re.compile(r"^#\d+: (?:NOT REVIEWABLE|RED unanswered)")
PROVENANCE = re.compile(r"^BOARD measured from origin/main at \S+, \S+")
OPENER = re.compile(r"^(?:OWED \S+ open-refused |NEEDS-TITLE |STARVED |STUCK )")
STAMP = re.compile(r"\b\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|[+-]\d\d:\d\d)?")
AGE = re.compile(r"(?<![\w#.])\d+(?:\.\d+)?\s?(?:h|m|min|s)\b(?: ago)?")


def utc(t: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() if t is None else t))


def norm(line: str) -> str:
    """A line with its stamps and ages replaced, so a re-print is no change."""
    return AGE.sub("<age>", STAMP.sub("<t>", line.rstrip()))


def sh(argv: list[str], cwd: Path, env: dict) -> tuple[int, str, str]:
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=3000)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", f"{e.__class__.__name__}: {e}"
    return p.returncode, p.stdout, p.stderr


def atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}")
    tmp.write_text(text)
    os.replace(tmp, path)


def read(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        return ""


class Ctx:
    """One row's inputs; `run` and `free_gib` are the edges the self-test replaces."""

    def __init__(self, state: Path, repo: Path, overlay: Path | None = None, board: Path | None = None,
                 run=sh, free_gib=None, now: float | None = None, platform: str | None = None):
        self.state, self.repo, self.run, self.clock = state, repo, run, time.monotonic
        self.platform = sys.platform if platform is None else platform
        self.digest = state / "digest"
        self.now = time.time() if now is None else now
        self.free_gib = free_gib or (lambda: shutil.disk_usage("/").free / 2 ** 30)
        try:
            self.overlay = json.loads((overlay or state / "sweep-overlay.json").read_text())
        except (OSError, ValueError):
            self.overlay = {}
        tick = self.overlay.get("tick_log")
        self.board = board or (Path(tick) if isinstance(tick, str) and tick else state / "tick.txt")
        self.env = dict(os.environ, HPO_STATE_DIR=str(state))

    def py(self, tool: str, *args: str) -> tuple[int, str, str]:
        return self.run([sys.executable, "-I", str(self.repo / tool), *args], self.repo, self.env)

    def need(self, row: str, *keys: str) -> list[str] | None:
        """The overlay's values for keys, or None after writing the row's UNREADABLE line."""
        missing = [k for k in keys if self.overlay.get(k) in (None, "")]
        if missing:
            write_job(self, row, [f"{row}: UNREADABLE overlay lacks {', '.join(missing)}"])
            return None
        return [str(self.overlay[k]) for k in keys]

    def memory(self, name: str, default):
        try:
            return json.loads((self.digest / "state" / name).read_text())
        except (OSError, ValueError):
            return default

    def remember(self, name: str, value, default=None) -> None:
        """Write a row's memory when it changed; an empty memory is never created."""
        text, path = json.dumps(value, sort_keys=True), self.digest / "state" / name
        if value == default and not path.exists():
            return
        if read(path) != text:
            atomic(self.digest / "state" / name, text)


# ---------------------------------------------------------------- the digest

class Locked:
    def __init__(self, ctx: Ctx):
        self.path = ctx.digest / ".lock"

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(self.fd, fcntl.LOCK_EX)

    def __exit__(self, *_):
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)


def write_job(ctx: Ctx, row: str, lines: list[str]) -> None:
    """The row's lines, normalised; nothing is written when they did not change."""
    text = "".join(norm(ln) + "\n" for ln in lines if ln.strip())
    path = ctx.digest / "jobs" / row
    if read(path) == text:
        return
    with Locked(ctx):
        atomic(path, text)
        fold_locked(ctx)


def fold_locked(ctx: Ctx) -> None:
    jobs = ctx.digest / "jobs"
    text = "".join(norm(ln) + "\n" for row in ROWS for ln in read(jobs / row).splitlines() if ln.strip())
    old = read(ctx.digest / "digest.txt")
    if text == old:
        return
    was, now = collections.Counter(old.splitlines()), collections.Counter(text.splitlines())
    new, gone = list((now - was).elements()), list((was - now).elements())
    atomic(ctx.digest / "digest.txt", text)
    atomic(ctx.digest / "new.txt", "".join(ln + "\n" for ln in new))  # empty when the fold added nothing
    atomic(ctx.digest / "gone.txt", "".join(ln + "\n" for ln in gone))
    if new:
        atomic(ctx.digest / "new.stamp", utc(ctx.now) + "\n")


def fold(ctx: Ctx) -> None:
    with Locked(ctx):
        fold_locked(ctx)


def event(ctx: Ctx, line: str) -> None:
    """Append `<utc> line` to events.txt unless that line is already there (HEAD-MOVED: unless it is that PR's last)."""
    with Locked(ctx):
        path = ctx.digest / "events.txt"
        kept = [ln.split(" ", 1)[-1] for ln in read(path).splitlines()]
        if line.startswith("HEAD-MOVED "):  # a head may return to an old sha: dedupe on the PR's last move only
            same = [e for e in kept if e.startswith(" ".join(line.split()[:2]) + " ")]
            if same and same[-1] == line:
                return
        elif line in kept:
            return
        with path.open("a") as f:
            f.write(f"{utc(ctx.now)} {line}\n")


# ---------------------------------------------------------------- the rows

def actionable(board: str) -> list[str]:
    return [ln[3:] for ln in board.splitlines() if ln.startswith("-> ") and FAMILY.match(ln[3:])]


def tick_digest(ctx: Ctx) -> None:
    text = read(ctx.board)
    first = text.splitlines()[0] if text else ""
    seen_before = ctx.memory("tick.json", {"pass": "", "transient": []})
    if not PROVENANCE.match(first):
        why = "absent" if not text else "has no provenance line"
        # forget the pass: the same board returning after an outage is a fresh read, not "already seen"
        ctx.remember("tick.json", {"pass": "", "transient": seen_before["transient"]}, {"pass": "", "transient": []})
        return write_job(ctx, "tick-digest", [f"tick-digest: UNREADABLE board {ctx.board.name} {why}"])
    seen = ctx.memory("tick.json", {"pass": "", "transient": []})
    if seen["pass"] == first:
        return  # the same board read twice is one pass
    keep, transient = [], []
    for ln in actionable(text):
        if TRANSIENT.match(ln):
            transient.append(norm(ln))
            if norm(ln) not in seen["transient"]:
                continue
        keep.append(ln)
    ctx.remember("tick.json", {"pass": first, "transient": transient})
    write_job(ctx, "tick-digest", keep)


def owed_check(ctx: Ctx) -> None:
    got = ctx.need("owed-check", "seat_ledger")
    if got is None:
        return
    rc, out, err = ctx.py("tools/audit/seat/owed_unactioned.py", "--tick", str(ctx.board),
                          "--state", str(ctx.digest / "state" / "owed-unactioned.json"), "--acks", got[0])
    if rc == 0:
        return write_job(ctx, "owed-check", [])
    if rc == 1:
        keys = re.findall(r"^  (\S+)  sweeps=(\d+)", out, re.M)
        if keys:
            return write_job(ctx, "owed-check", [f"UNACTIONED {k} sweeps={n}" for k, n in keys])
    why = next((ln for ln in (out + err).splitlines() if ln.startswith("UNREADABLE")), f"rc={rc}")
    write_job(ctx, "owed-check", [f"owed-check: UNREADABLE {why}"])


def on_main(ctx: Ctx, path: str) -> bool:
    return ctx.run(["git", "-C", str(ctx.repo), "cat-file", "-e", f"origin/main:{path}"],
                   ctx.repo, ctx.env)[0] == 0


def roster_drain(ctx: Ctx) -> None:
    done = set(ctx.memory("roster-done.json", []))
    holds = ctx.memory("roster-hold.json", {})
    lines, count, ran, cascade = [], collections.Counter(), False, 0
    # The queue is append-only. Only newline-terminated lines run: a last segment read mid-append waits
    # for its newline. A queue with fewer terminated lines than a past pass drained was cleared or
    # rotated, which would silently skip a re-queued op under its occurrence key: refuse it visibly.
    whole = read(ctx.state / "roster-drain.queue").split("\n")[:-1]
    seen = int(ctx.memory("roster-queue-lines.json", 0))

    def save() -> None:  # after every op, not only at the pass's end: a killed pass keeps what it applied
        ctx.remember("roster-queue-lines.json", len(whole), 0)
        ctx.remember("roster-done.json", sorted(done), [])
        ctx.remember("roster-hold.json", holds, {})
    if len(whole) < seen or ctx.memory("roster-shrank.json", False):
        ctx.remember("roster-shrank.json", True, False)  # sticky: the op queued after the clear must not vanish
        return write_job(ctx, "roster-drain", [
            f"roster: QUEUE-SHRANK {len(whole)} terminated line(s) now, {seen} drained before; the queue is "
            "append-only; nothing ran. Rebaseline by deleting roster-done.json, roster-hold.json, "
            "roster-queue-lines.json and roster-shrank.json under the digest state"])
    start = ctx.clock()
    for raw in whole:
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        count[text] += 1
        key = f"{count[text]}\t{text}"
        if key in done:
            continue
        op = text
        if text.startswith("hold "):
            parts = text.split(None, 2)
            if len(parts) < 3:
                lines.append(f"roster: refused malformed hold line: {text}")
                done.add(key)
                continue
            first = holds.setdefault(key, ctx.now)
            if not on_main(ctx, parts[1]):
                if ctx.now - first > HOLD_STALE_S:
                    lines.append(f"roster: HOLD-STALE {parts[2]} waits on {parts[1]}")
                continue
            op = parts[2]
        if ctx.clock() - start >= ROSTER_PASS_BUDGET_S:
            break  # beatd kills the pass at timeout_s; this op and the rest run next pass
        one, report = ctx.digest / "state" / "roster-one.queue", ctx.digest / "state" / "roster-report.txt"
        atomic(one, op + "\n")
        report.unlink(missing_ok=True)
        ran = True
        rc, out, err = ctx.py("tools/audit/seat/roster_queue.py", "run", "1", "1", "--mark", "--queue", str(one),
                              "--report", str(report), "--edit-checkout", str(ctx.repo),
                              "--worktree", str(ctx.digest / "state" / "roster-wt"),
                              "--lint-clone", str(ctx.state / "roster-lint"))
        said = [ln for ln in read(report).splitlines() if ln.startswith("roster: ")]
        mark = read(one).split("\n", 1)[0]  # `--mark` rewrites the exact line `#done <op>` or `#refused <op>`
        if not said and mark == op:  # no report line and no mark: roster_queue attempted nothing
            lines.append(f"roster: UNRUN {op} rc={rc} no report line; stays pending")
            continue
        if mark == f"#refused {op}" and any("is on no origin ref" in ln for ln in said):
            cascade += 1  # the worktree an earlier refusal left detached refused it, not the lint gate
            continue
        lines += said or [f"roster: {op} {mark.split()[0]} rc={rc} no report line"]
        if mark != op or not any("no op attempted" in ln for ln in said):
            done.add(key)  # applied or refused: never retried past the lint gate
            holds.pop(key, None)
            save()
    if cascade:
        lines.append(f"roster: CASCADE {cascade} op(s) stay pending: the worktree "
                     f"{ctx.digest / 'state' / 'roster-wt'} is on no origin ref after an earlier refusal; "
                     "remove it to release them")
    save()
    if lines or ran or "HOLD-STALE" in read(ctx.digest / "jobs" / "roster-drain"):
        write_job(ctx, "roster-drain", lines)  # an idle pass keeps the last drain's lines


def plan_beat(ctx: Ctx) -> None:
    got = ctx.need("plan-beat", "plan_json", "plan_slots", "plan_seats", "state_mirror", "repo")
    if got is None:
        return
    plan, slots, seats, mirror, repo = got
    # the overlay's plan_coordinator_cap rides to replan.py; absent, replan's own default stands
    cap = ["--coordinator-cap", str(ctx.overlay["plan_coordinator_cap"])] if ctx.overlay.get("plan_coordinator_cap") else []
    rc, _, err = ctx.py("tools/plan/replan.py", "--out", plan, "--slots", slots, "--seats", seats, *cap)
    if rc != 0:
        last = (err.strip().splitlines() or [""])[-1]
        return write_job(ctx, "plan-beat", [f"plan-beat: PLAN UNAVAILABLE replan rc={rc}: {last}"])
    # the train log feeds the page's skip-share and train-skips table (UNAVAILABLE without it)
    train = ["--train-log", str(ctx.overlay["train_log"])] if ctx.overlay.get("train_log") else []
    rc, out, err = ctx.py("tools/audit/seat/state_docs.py", "--push", "--mirror", mirror, "--plan", plan, *train)
    lines = []
    if rc != 0:
        said = [ln for ln in err.splitlines() if "UNAVAILABLE" in ln or "REFUSED" in ln]
        word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"
        lines.append(f"plan-beat: {word} rc={rc}: {(said or [''])[-1]}")
    if rc == 0:
        page = read(Path(mirror) / "PLAN.html")
        sha = hashlib.sha256(page.encode()).hexdigest() if page else ""
        moved = sha and sha != ctx.memory("plan-page.json", "")
        ctx.remember("plan-page.json", sha, "")
        # owner ruling (tvofi 2026-11-06): every sweep updates the plan artifact; a changed page owes a republish
        if moved:
            lines.append(f"plan-beat: PLAN MOVED {Path(mirror) / 'PLAN.html'} re-rendered; republish owed")
    if rc in (0, 1) and re.search(r"^pushed ", out, re.M):  # the state ref moved: publish its page
        drc, _, derr = ctx.run(["gh", "workflow", "run", "pages.yml", "--repo", repo, "--ref", "main"],
                               ctx.repo, ctx.env)
        if drc != 0:
            lines.append(f"plan-beat: PAGES NOT DISPATCHED rc={drc}: {(derr.strip().splitlines() or [''])[-1]}")
    write_job(ctx, "plan-beat", lines)


def gantt(ctx: Ctx) -> None:
    """sweep_gantt.py against the plan plan-beat wrote; its GANTT-SLIP and GANTT-BASELINE lines."""
    got = ctx.need("gantt", "repo", "plan_json", "gantt_roster", "gantt_acks")
    if got is None:
        return
    repo, plan, roster, acks = got
    branch, _, path = roster.partition(":")
    d, git = ctx.digest / "state" / "gantt", ["git", "-C", str(ctx.repo)]
    d.mkdir(parents=True, exist_ok=True)
    # tips land under refs/gantt/, never refs/heads/ or refs/remotes/: no branch and no tree moves
    rc, _, err = ctx.run([*git, "fetch", "-q", "origin", f"+refs/heads/{branch}:refs/gantt/roster",
                          "+refs/heads/handoff/*:refs/gantt/handoff/*", "+refs/heads/handoff-wip/*:refs/gantt/handoff-wip/*"],
                         ctx.repo, ctx.env)
    if rc != 0:  # refs/gantt/ would still hold the last pass's roster and tips: never read them as current
        return write_job(ctx, "gantt", [f"gantt: UNREADABLE fetch rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    rc, out, _ = ctx.run([*git, "show", f"refs/gantt/roster:{path}"], ctx.repo, ctx.env)
    if rc != 0 or not path:
        return write_job(ctx, "gantt", [f"gantt: UNREADABLE roster {roster} rc={rc}"])
    atomic(d / "roster.json", out)
    _, out, _ = ctx.run([*git, "for-each-ref", "--format=%(objectname)%09%(refname)%09%(committerdate:unix)",
                         "refs/gantt/handoff/", "refs/gantt/handoff-wip/"], ctx.repo, ctx.env)
    atomic(d / "handoff-rows.tsv", out.replace("\trefs/gantt/", "\trefs/heads/"))
    rc, out, _ = ctx.run(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "100",
                          "--json", "number,title"], ctx.repo, ctx.env)
    if rc != 0:
        return write_job(ctx, "gantt", [f"gantt: UNREADABLE gh pr list rc={rc}"])
    atomic(d / "prs.json", out)
    ledger = ctx.overlay.get("fire_ledger")
    atomic(d / "fired.txt", read(Path(str(ledger))) if ledger else "")
    rc, out, err = ctx.py("tools/audit/seat/sweep_gantt.py", "--plan", plan, "--baseline", str(d / "baseline.json"),
                          "--acks", acks, "--roster", str(d / "roster.json"), "--open-prs", str(d / "prs.json"),
                          "--handoff-rows", str(d / "handoff-rows.tsv"), "--fired", str(d / "fired.txt"))
    if rc != 0:
        return write_job(ctx, "gantt", [f"gantt: UNREADABLE sweep_gantt rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    write_job(ctx, "gantt", [ln for ln in out.splitlines() if re.match(r"^GANTT-(?:SLIP|BASELINE) ", ln)])


def verdict_audit(ctx: Ctx) -> None:
    """verdict_audit.py: one UNHELD line per open pull request whose next step nobody holds."""
    got = ctx.need("verdict-audit", "repo")
    if got is None:
        return
    args = ["--repo", got[0]]
    for key, flag in (("fire_ledger", "--fired"), ("train_glob", "--train-glob"), ("unheld_skip", "--skip")):
        if ctx.overlay.get(key):
            args += [flag, str(ctx.overlay[key])]
    rc, out, err = ctx.py("tools/audit/seat/verdict_audit.py", *args)
    if rc != 0:
        return write_job(ctx, "verdict-audit",
                         [f"verdict-audit: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    write_job(ctx, "verdict-audit", [ln for ln in out.splitlines() if ln.startswith("UNHELD ")])


def pulse(ctx: Ctx) -> None:
    o = ctx.overlay
    args = ["--repo", str(o["repo"])] if o.get("repo") else []
    args += shlex.split(str(o.get("seat_queues") or ""))
    alives = o.get("seat_alives") or []
    for e in (alives if isinstance(alives, list) else str(alives).split()):
        args += ["--seat-alive", e]
    if o.get("launch_ledger"):
        args += ["--launch-ledger", str(o["launch_ledger"])]
    rc, out, err = ctx.py("tools/audit/seat/pulse.py", *args)
    if rc not in (0, 1, 2) or not out:
        return write_job(ctx, "pulse", [f"pulse: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    atomic(ctx.state / "beatd" / "pulse.txt", out)
    write_job(ctx, "pulse", [ln for ln in out.splitlines()
                             if re.match(r"^PULSE \S+ (?:STOPPED|UNREADABLE) ", ln)])


def cancel_sweep(ctx: Ctx) -> None:
    got = ctx.need("cancel-sweep", "repo")
    if got is None:
        return
    rc, out, err = ctx.py("tools/pr/cancel_superseded.py", "sweep", "--repo", got[0])
    bad = [ln for ln in out.splitlines()
           if re.search(r"could not cancel| rc=-?\d+|unreadable|truncated", ln)]
    if rc != 0:
        bad.append(f"cancel-sweep: rc={rc}: {(err.strip().splitlines() or [''])[-1]}")
    write_job(ctx, "cancel-sweep", bad)


def disk(ctx: Ctx) -> None:
    got = ctx.need("disk", "repo", "disk_floor_gib")
    if got is None:
        return
    floor = float(got[1])
    if ctx.free_gib() >= floor:
        return write_job(ctx, "disk", [])
    rc, _, _ = ctx.run(["bash", str(ctx.repo / "tools/audit/worktree_gc.sh"), got[0]], ctx.repo, ctx.env)
    free = ctx.free_gib()
    write_job(ctx, "disk", [] if free >= floor else
              [f"disk: {int(free)} GiB free on / under the {got[1]} GiB floor after worktree_gc (rc={rc})"])


def opener(ctx: Ctx) -> None:
    rc, out, err = ctx.py("tools/audit/seat/open_driver.py", "--board", str(ctx.board))
    lines = [ln for ln in out.splitlines() if OPENER.match(ln)]
    if rc != 0:
        lines.append(f"opener: open_driver rc={rc}: {(err.strip().splitlines() or [''])[-1]}")
    for ln in lines:
        if ln.startswith("STUCK "):
            event(ctx, norm(ln))
    write_job(ctx, "opener", lines)


def head_watch(ctx: Ctx) -> None:
    got = ctx.need("head-watch", "repo")
    if got is None:
        return
    rc, out, _ = ctx.run(["gh", "api", "--paginate", f"repos/{got[0]}/pulls?state=open&per_page=100",
                          "--jq", '.[] | "\\(.number) \\(.head.sha)"'], ctx.repo, ctx.env)
    heads = dict(ln.split() for ln in out.splitlines() if re.fullmatch(r"\d+ [0-9a-f]{40}", ln))
    if rc != 0:
        return write_job(ctx, "head-watch", [f"head-watch: UNREADABLE gh rc={rc}"])
    path = ctx.digest / "heads.tsv"
    old = dict(ln.split("\t") for ln in read(path).splitlines() if "\t" in ln)
    for n in sorted(heads, key=int):
        if n in old and old[n] != heads[n]:
            event(ctx, f"HEAD-MOVED #{n} {old[n][:12]} {heads[n][:12]}")
    text = "".join(f"{n}\t{heads[n]}\n" for n in sorted(heads, key=int))
    if read(path) != text:
        atomic(path, text)
    write_job(ctx, "head-watch", [])


GUARD_WINDOW_S = 60 * 24 * 3600  # the bus window handed to --guardrail; the arms cut on the last N PRs, not on this
TRIP = re.compile(r"^GUARDRAIL (\S+) last \d+ PRs \(first verdict (\S+\.\.\S+)\):.* -> would-trip\b")


def audit_dispatch(ctx: Ctx) -> None:
    """One audit DISPATCH line per sustained trip of an arm; the sliding cut of a still-tripped arm gives none."""
    fmt = "%Y-%m-%dT%H:%MZ"
    until = time.strftime(fmt, time.gmtime(ctx.now))
    since = time.strftime(fmt, time.gmtime(ctx.now - GUARD_WINDOW_S))
    rc, out, err = ctx.py("tools/audit/seat/review_strength.py", "--repo", str(ctx.repo), "--fetch",
                          "--window", f"X={since}..{until}", "--guardrail")
    arms = [ln for ln in out.splitlines() if ln.startswith("GUARDRAIL ") and " unclassified " not in ln]
    if rc != 0 or not arms:
        why = (err.strip().splitlines() or [f"rc={rc}, no arm line"])[-1]
        kept = [ln for ln in read(ctx.digest / "jobs" / "audit-dispatch").splitlines() if ln.startswith("DISPATCH:")]
        return write_job(ctx, "audit-dispatch", kept + [f"audit-dispatch: UNREADABLE review_strength {why}"])
    tripped = ctx.memory("audit-dispatch.json", [])  # arms inside a trip already dispatched; the cut slides, the trip does not
    kept = [ln for ln in read(ctx.digest / "jobs" / "audit-dispatch").splitlines() if ln.startswith("DISPATCH:")]
    new = []
    for ln in arms:
        m = TRIP.match(ln)
        arm = ln.split()[1]
        if m and arm not in tripped:
            tripped.append(arm)
            new.append(f"DISPATCH: planted-defect-audit arm={arm} cut={m[2]}")
        elif not m and arm in tripped:  # the arm reads ok or insufficient: the trip is over, the next one dispatches again
            tripped.remove(arm)
    ctx.remember("audit-dispatch.json", tripped, [])
    # a readable pass clears a stale UNREADABLE and keeps the DISPATCH lines, as roster-drain keeps HOLD-STALE until idle
    write_job(ctx, "audit-dispatch", kept + new)


def outside_intake(ctx: Ctx) -> None:
    got = ctx.need("outside-intake", "repo", "intake_since")
    if got is None:
        return
    rc, out, err = ctx.py("tools/audit/seat/outside_intake.py", "list", "--repo", got[0], "--since", got[1],
                          "--cursor", str(ctx.digest / "state" / "outside-cursor.json"))
    if rc in (0, 1):
        return write_job(ctx, "outside-intake", [ln for ln in out.splitlines() if ln.startswith("OUTSIDE ")])
    why = next((ln for ln in out.splitlines() if ln.startswith("outside-intake: UNREADABLE")), None)
    write_job(ctx, "outside-intake", [why or f"outside-intake: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])


def bottleneck(ctx: Ctx) -> None:
    """bottleneck_check.py: one line per flow metric past its threshold, held once per trip by its memory."""
    got = ctx.need("bottleneck", "train_log", "plan_slots")
    if got is None:
        return
    rc, out, err = ctx.py("tools/audit/seat/bottleneck_check.py", "--checkout", str(ctx.repo),
                          "--train-log", got[0], "--wip-cap", got[1],
                          "--memory", str(ctx.digest / "state" / "bottleneck.json"))
    if rc != 0:
        return write_job(ctx, "bottleneck", [f"bottleneck: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    write_job(ctx, "bottleneck", [ln for ln in out.splitlines() if ln.startswith(("BOTTLENECK: ", "BOTTLENECK-UNREADABLE: "))])


def scorecard(ctx: Ctx) -> None:
    """scorecard.py report into S/beatd/scorecard.txt; report-only, so the digest hears only of a failed run."""
    got = ctx.need("scorecard", "train_log")
    if got is None:
        return
    args = ["report", "--dir", str(ctx.state / "scorecard"), "--train-log", got[0], "--repo", str(ctx.repo)]
    if ctx.overlay.get("sweep_record"):
        args += ["--sweep-record", str(ctx.overlay["sweep_record"])]
    rc, out, err = ctx.py("tools/audit/seat/scorecard.py", *args)
    if rc != 0 or not out.strip():
        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    atomic(ctx.state / "beatd" / "scorecard.txt", out)
    write_job(ctx, "scorecard", [])


DARWIN_SEAT = "audit/seat/"
DARWIN_LEASE_LABEL = "darwin-selftest"


def first_fail(out: str, err: str, rc: int) -> str:
    """The first line naming FAIL in the run's output, else its last non-empty line, else the exit code."""
    lines = [ln.strip() for ln in (out + "\n" + err).splitlines() if ln.strip()]
    return next((ln for ln in lines if "FAIL" in ln), lines[-1] if lines else f"rc={rc} with no output")


def darwin_instruments(wt: Path) -> list[str]:
    """Paths under tools/ of the seat scripts that self-test and are wired in a workflow, in the worktree under test."""
    import selftest_wiring
    wired = selftest_wiring.wired(wt)
    return [p for p in selftest_wiring.self_testing(wt)
            if p.startswith(DARWIN_SEAT) and p.endswith((".py", ".sh")) and p in wired]


def darwin_selftest(ctx: Ctx) -> None:
    if ctx.platform != "darwin":
        return
    rc, tip, err = ctx.run(["git", "-C", str(ctx.repo), "rev-parse", "origin/main"], ctx.repo, ctx.env)
    tip = tip.strip()
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", tip):
        return write_job(ctx, "darwin-selftest",
                         [f"darwin-selftest: UNREADABLE origin/main rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
    if ctx.memory("darwin-selftest.json", {}).get("tip") == tip:
        return
    gate = [sys.executable, "-I", str(ctx.repo / "tests" / "gate_lock.py")]
    wt = ctx.digest / "state" / "darwin-selftest-wt"
    env = {k: v for k, v in ctx.env.items() if k != "HPO_STATE_DIR"}  # a self-test never reaches this digest
    env["HPO_SLOT_LABEL"] = DARWIN_LEASE_LABEL
    lines: list[str] = []
    ctx.run([*gate, "slot-take", "--label", DARWIN_LEASE_LABEL, "--owner-pid", str(os.getpid())], ctx.repo, env)
    try:
        ctx.run(["git", "-C", str(ctx.repo), "worktree", "remove", "--force", str(wt)], ctx.repo, env)  # a killed pass's
        rc, _, err = ctx.run(["git", "-C", str(ctx.repo), "worktree", "add", "--detach", str(wt), tip], ctx.repo, env)
        if rc != 0:
            return write_job(ctx, "darwin-selftest",
                             [f"darwin-selftest: UNREADABLE worktree rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
        runs = [("tools/pr/prepr.sh", ["bash", "tools/pr/prepr.sh", "--self-test"])]
        runs += [(f"tools/{p}", ["python3" if p.endswith(".py") else "bash", *(["-I"] if p.endswith(".py") else []),
                                 f"tools/{p}", "--self-test"]) for p in darwin_instruments(wt)]
        for name, argv in runs:
            rc, out, err = ctx.run(argv, wt, env)
            if rc != 0:
                lines.append(f"darwin-selftest: RED {name} {first_fail(out, err, rc)}")
    finally:
        ctx.run(["git", "-C", str(ctx.repo), "worktree", "remove", "--force", str(wt)], ctx.repo, env)
        ctx.run([*gate, "slot-release", "--label", DARWIN_LEASE_LABEL], ctx.repo, env)
    ctx.remember("darwin-selftest.json", {"tip": tip})
    write_job(ctx, "darwin-selftest", lines)


RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": roster_drain,
       "plan-beat": plan_beat, "gantt": gantt, "verdict-audit": verdict_audit, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
       "opener": opener, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
       "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard,
       "darwin-selftest": darwin_selftest}


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        import beat_jobs_selftest  # the cases and mutants live beside this file
        return beat_jobs_selftest.run(Path(__file__), mutants="--no-mutants" not in argv)
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("row", choices=(*ROWS, "fold"))
    ap.add_argument("--state", required=True, type=Path)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--overlay", type=Path)
    ap.add_argument("--board", type=Path)
    a = ap.parse_args(argv)
    ctx = Ctx(a.state, a.repo.resolve(), a.overlay, a.board)
    (fold if a.row == "fold" else RUN[a.row])(ctx)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv[1:]))
