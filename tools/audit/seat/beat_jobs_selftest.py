"""The cases and mutants of beat_jobs.py's self-test, kept beside it.

Run through `beat_jobs.py`'s own flag, which CI's governance workflow names.
Every case runs in-process against a throwaway state directory, with the
instruments replaced by a recording fake runner: no network, no subprocess, no
git. Each planted case first asserts that its expected line is absent from an
empty digest, so it cannot pass vacuously; each null asserts no byte written.
MUTANTS plants one edit per row predicate (and the fold) in a temp copy of
beat_jobs.py and expects the named case to fail; a mutant that crashes the
cases is reported failed, never killed.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "beat_jobs"
SHA = {k: (c * 40) for k, c in (("a", "a"), ("b", "b"), ("c", "c"))}
MOVES = ("checkout", "switch", "reset", "pull", "merge", "rebase", "stash", "clean", "restore")


def load(path: Path, name: str = "beat_jobs_under_test"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Fake:
    """A runner answering per tool basename; records every argv."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, argv, cwd, env):
        self.calls.append(list(argv))
        tool = next((Path(a).name for a in argv if a.endswith((".py", ".sh"))), argv[0])
        if argv[0] == "git":
            tool = "git"
        ans = self.answers.get(tool, (0, "", ""))
        return ans(argv) if callable(ans) else ans

    def ran(self, tool):
        return sum(any(Path(a).name == tool for a in c) for c in self.calls)


def arg(argv, flag):
    """The word after `flag` in an argv, or None: a dropped flag fails a case, never crashes it."""
    return argv[argv.index(flag) + 1] if flag in argv[:-1] else None


def board(stamp: str, *flagged: str, plain: tuple[str, ...] = ()) -> str:
    return "\n".join([f"BOARD measured from origin/main at 0123456789ab, {stamp}", "== PRS ==",
                      *("   " + p for p in plain), *("-> " + f for f in flagged), "DISPATCH LIST: x"]) + "\n"


def cases(bj) -> dict[str, bool]:
    res: dict[str, bool] = {}
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    n = [0]

    def fresh(overlay=None, answers=None, free=None, now=1_800_000_000.0):
        n[0] += 1
        s = root / f"s{n[0]}"
        (s / "beatd").mkdir(parents=True)
        ov = {"repo": "o/r", "seat_ledger": str(s / "ledger"), "plan_json": str(s / "p.json"),
              "plan_slots": 10, "plan_seats": 99, "state_mirror": str(s / "mirror"),
              "disk_floor_gib": 20, "seat_queues": "--seat-queue merge=" + str(s / "q")}
        if overlay is not None:
            ov = overlay
        (s / "sweep-overlay.json").write_text(json.dumps(ov))
        fake = Fake(answers)
        return bj.Ctx(s, root, run=fake, free_gib=free, now=now), fake

    def files(ctx):
        d = ctx.digest
        return {p.relative_to(d).as_posix(): p.read_bytes() for p in d.rglob("*") if p.is_file()} \
            if d.exists() else {}

    def digest(ctx):
        return bj.read(ctx.digest / "digest.txt")

    owed = "OWED handoff: refs/heads/handoff/r10-x -- no PR head carries it: open_pr.sh (opener)"

    # tick-digest
    c, _ = fresh()
    c.board.write_text(board("2026-11-01T09:00:00+00:00", "train beat stale 75m", plain=("#1 [h] GREEN",)))
    bj.tick_digest(c)
    res["tick-digest null: a board with nothing owed writes no job, no digest, no stamp"] = (
        not (c.digest / "jobs" / "tick-digest").exists() and not digest(c)
        and not (c.digest / "new.stamp").exists())
    c, _ = fresh()
    pre = owed not in digest(c)
    c.board.write_text(board("2026-11-01T09:00:00+00:00", owed, "train beat stale 75m"))
    bj.tick_digest(c)
    res["tick-digest: one OWED line gives exactly that line, and a stamp"] = (
        pre and digest(c) == owed + "\n" and bj.read(c.digest / "new.txt") == owed + "\n"
        and (c.digest / "new.stamp").exists())
    before = files(c)
    c.board.write_text(board("2026-11-01T09:04:00+00:00", owed, "train beat stale 79m"))
    bj.tick_digest(c)
    c.now += 240
    st = c.digest / "state" / "tick.json"
    res["tick-digest: a timestamp-only change writes nothing but the pass mark"] = (
        {k: v for k, v in files(c).items() if k != "state/tick.json"}
        == {k: v for k, v in before.items() if k != "state/tick.json"} and st.exists())
    stalled = "REVIEW STALLED: #7 8796a5b4 47m"
    c, _ = fresh()
    c.board.write_text(board("2026-11-01T09:00:00+00:00", stalled))
    bj.tick_digest(c)
    c.board.write_text(board("2026-11-01T09:04:00+00:00", stalled.replace("47m", "51m")))
    stamp = files(c).get("new.stamp")
    bj.tick_digest(c)
    res["tick-digest: an age-only change is no new line"] = (
        digest(c) == "REVIEW STALLED: #7 8796a5b4 <age>\n" and files(c).get("new.stamp") == stamp)
    red = "#3102: RED unanswered in ## Red checks: tests"
    c, _ = fresh()
    pre = red not in digest(c)
    c.board.write_text(board("2026-11-01T09:00:00+00:00", red))
    bj.tick_digest(c)
    once = red not in digest(c)
    c.board.write_text(board("2026-11-01T09:00:00+00:00", red))
    bj.tick_digest(c)
    same = red not in digest(c)
    c.board.write_text(board("2026-11-01T09:04:00+00:00", red))
    bj.tick_digest(c)
    res["tick-digest: a transient RED gives nothing; on a second board it appears"] = (
        pre and once and same and digest(c) == red + "\n")
    c, _ = fresh()
    c.board.write_text(board("2026-11-01T09:00:00+00:00", red))
    bj.tick_digest(c)
    c.board.write_text(board("2026-11-01T09:04:00+00:00", "MERGE-READY: #9 9a8b7c6d"))
    bj.tick_digest(c)
    res["null: a RED that cleared on the next board never appears"] = (
        digest(c) == "MERGE-READY: #9 9a8b7c6d\n")
    c, _ = fresh()
    bj.tick_digest(c)
    res["tick-digest: an absent board is UNREADABLE, never clean"] = "UNREADABLE board" in digest(c)

    c, _ = fresh()
    c.board.write_text("-> OWED x\nnot a provenance line\n")
    bj.tick_digest(c)
    res["tick-digest: a board without its provenance line is UNREADABLE, never clean"] = (
        digest(c) == f"tick-digest: UNREADABLE board {c.board.name} has no provenance line\n")

    c, _ = fresh()
    b = board("2026-11-01T09:00:00+00:00", "MERGE-READY: #9 9a8b7c6d")
    c.board.write_text(b)
    bj.tick_digest(c)
    c.board.write_text("")
    bj.tick_digest(c)
    c.board.write_text(b)
    bj.tick_digest(c)
    res["tick-digest: the same board returning after an outage clears the UNREADABLE line"] = (
        digest(c) == "MERGE-READY: #9 9a8b7c6d\n")

    # the recorded-shape board: the actionable set at a persistent board
    c, _ = fresh()
    text = (FIXTURE / "board.txt").read_text()
    c.board.write_text(text)
    bj.tick_digest(c)
    c.board.write_text(text.replace("09:12:44", "09:16:44"))
    bj.tick_digest(c)
    res["the fixture board's digest is exactly its recorded actionable set"] = (
        digest(c) == (FIXTURE / "digest.txt").read_text())
    src = "".join((HERE / f).read_text() for f in ("orchestrator_tick.py", "ledger.py"))
    lits = ["OWED", "DISPATCH:", "OWNER FLAG:", "BLOCKED-UNFIXED:", "DESIGN-BUILD:", "UNREADABLE:",
            "DESIGN OWED:", "REVIEW OWED:", "REVIEW STALLED:", "UNLEVELLED:", "APPROVAL-OWED:",
            "MERGE-READY:", "main-red ", "REQUIRED not green", "RAISE APPROVAL OWED", "NOT REVIEWABLE",
            "mergeable state DIRTY", "RED unanswered", "code-owned with no ",
            "BOARD measured from origin/main at"]
    gone = [x for x in lits if x not in src or x not in bj.FAMILY.pattern + bj.PROVENANCE.pattern]
    if gone:
        print("    literals not in the board's printers or the family: " + ", ".join(gone))
    res["every family literal is one the board's printers print"] = not gone

    # owed-check
    un = "UNACTIONED\n  pr#41  sweeps=3 first=2026-11-01T08:00Z (1.2h)\n      -> OWED x\n"
    c, f = fresh(answers={"owed_unactioned.py": (0, "owed: 0 key(s)\n", "")})
    bj.owed_check(c)
    res["owed-check null: rc 0 writes nothing"] = not files(c) and f.ran("owed_unactioned.py") == 1
    c, _ = fresh(answers={"owed_unactioned.py": (1, "owed: 1\n" + un, "")})
    pre = "UNACTIONED pr#41" not in digest(c)
    bj.owed_check(c)
    res["owed-check: an UNACTIONED exit lands in new.txt"] = (
        pre and bj.read(c.digest / "new.txt") == "UNACTIONED pr#41 sweeps=3\n")
    c, _ = fresh(answers={"owed_unactioned.py": (2, "UNREADABLE: board 31 min old\n", "")})
    bj.owed_check(c)
    res["owed-check: rc 2 is UNREADABLE"] = "owed-check: UNREADABLE UNREADABLE: board" in digest(c)
    c, f = fresh(answers={"owed_unactioned.py": (0, "owed: 0 key(s)\n", "")})
    bj.owed_check(c)
    a = f.calls[0]
    res["owed-check: the instrument is handed the board and the ledger"] = (
        arg(a, "--tick") == str(c.board) and arg(a, "--acks") == str(c.state / "ledger")
        and arg(a, "--state").endswith("owed-unactioned.json"))
    c, f = fresh(overlay={"repo": "o/r"})
    bj.owed_check(c)
    res["a row whose overlay key is missing says so, and runs nothing"] = (
        digest(c) == "owed-check: UNREADABLE overlay lacks seat_ledger\n" and not f.calls)

    # roster-drain
    def roster(word):
        def ans(argv):
            rep = Path(argv[argv.index("--report") + 1])
            op = Path(argv[argv.index("--queue") + 1]).read_text().split()
            rep.write_text(f"roster: {op[0]} {op[1]} {word}\n")
            return 0, "", ""
        return ans

    c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde")})
    bj.roster_drain(c)
    res["roster-drain null: no queue writes nothing"] = not files(c) and not f.calls
    pre = "roster: set-stage G1 pushed" not in digest(c)
    (c.state / "roster-drain.queue").write_text("# head\n\nset-stage G1 done\n")
    bj.roster_drain(c)
    first = digest(c)
    bj.roster_drain(c)
    res["roster-drain: a queue line drains once, is marked, and is not re-run"] = (
        pre and first == "roster: set-stage G1 pushed 0123abcde\n" and f.ran("roster_queue.py") == 1)
    (c.state / "roster-drain.queue").write_text("# head\n\nset-stage G1 done\nset-stage G1 done\n")
    bj.roster_drain(c)
    res["roster-drain: an identical second line is its own line"] = f.ran("roster_queue.py") == 2
    c, f = fresh(answers={"roster_queue.py": roster("refused rc=1 lint gate: TOTAL: 1")})
    (c.state / "roster-drain.queue").write_text("append-carry G2 @x\n")
    bj.roster_drain(c)
    bj.roster_drain(c)
    res["roster-drain: a REFUSE line arrives in the digest and is never retried"] = (
        "roster: append-carry G2 refused" in digest(c) and f.ran("roster_queue.py") == 1)
    on = {"v": 1}
    c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde"), "git": lambda a: (on["v"], "", "")})
    (c.state / "roster-drain.queue").write_text("hold dev/programme/triage/s9-batch1.md set-stage G3 x\n")
    bj.roster_drain(c)
    held = f.ran("roster_queue.py") == 0 and not digest(c)
    c.now += bj.HOLD_STALE_S + 1
    bj.roster_drain(c)
    stale = "roster: HOLD-STALE set-stage G3 x waits on dev/programme/triage/s9-batch1.md" in digest(c)
    on["v"] = 0
    bj.roster_drain(c)
    res["roster-drain: a hold waits for main, is HOLD-STALE past 24 h, then releases"] = (
        held and stale and f.ran("roster_queue.py") == 1 and "pushed" in digest(c))

    c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde")})
    q = c.state / "roster-drain.queue"
    q.write_text("append-carry G2 note text that is lo")
    bj.roster_drain(c)
    waits = f.ran("roster_queue.py") == 0 and not digest(c)
    q.write_text("append-carry G2 note text that is long\n")
    bj.roster_drain(c)
    res["roster-drain: an unterminated last line waits for its newline and runs once, whole"] = (
        waits and f.ran("roster_queue.py") == 1
        and digest(c) == "roster: append-carry G2 pushed 0123abcde\n")
    c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde")})
    q = c.state / "roster-drain.queue"
    q.write_text("set-stage G1 done\n")
    bj.roster_drain(c)
    q.write_text("")
    bj.roster_drain(c)
    shrank = "roster: QUEUE-SHRANK 0 terminated line(s) now, 1 drained before" in digest(c)
    q.write_text("set-stage G1 done\nset-stage G2 done\n")  # re-queued past the old length: still refused
    bj.roster_drain(c)
    res["roster-drain: a cleared queue is refused as QUEUE-SHRANK, stays refused, and nothing runs"] = (
        shrank and f.ran("roster_queue.py") == 1 and "QUEUE-SHRANK" in digest(c))
    c, f = fresh(answers={"roster_queue.py": roster("no op attempted: lint clone not provisioned")})
    (c.state / "roster-drain.queue").write_text("set-stage G1 done\n")
    bj.roster_drain(c)
    bj.roster_drain(c)
    res["roster-drain: a no-op-attempted report is retried on the next pass"] = f.ran("roster_queue.py") == 2

    # plan-beat
    c, f = fresh()
    bj.plan_beat(c)
    res["plan-beat null: both succeed, nothing written"] = not files(c) and f.ran("state_docs.py") == 1
    c, _ = fresh(answers={"state_docs.py": (1, "", "state_docs: PLAN.html UNAVAILABLE: stale plan\n")})
    bj.plan_beat(c)
    res["plan-beat: state_docs rc 1 is PLAN UNAVAILABLE"] = digest(c).startswith("plan-beat: PLAN UNAVAILABLE rc=1")
    c, f = fresh(answers={"replan.py": (2, "", "refused: no round\n")})
    bj.plan_beat(c)
    res["plan-beat: a replan failure is PLAN UNAVAILABLE and publishes nothing"] = (
        "PLAN UNAVAILABLE replan rc=2" in digest(c) and f.ran("state_docs.py") == 0)

    c, f = fresh(answers={"state_docs.py": (2, "", "state_docs: refused: dirty mirror REFUSED\n")})
    bj.plan_beat(c)
    res["plan-beat: state_docs rc 2 is REFUSED, not PLAN UNAVAILABLE"] = digest(c).startswith("plan-beat: REFUSED rc=2")
    a = f.calls[0]
    res["plan-beat: replan is handed the plan, slots and seats"] = (
        arg(a, "--out") == str(c.state.parent / "p.json") or arg(a, "--out").endswith("p.json")) and (
        arg(a, "--slots") == "10" and arg(a, "--seats") == "99")

    # pulse
    ok = "PULSE opener ok fine\npulse: 1 arms, 0 stopped, 0 unreadable at 2026-11-01T09:00:00Z\n"
    c, f = fresh(answers={"pulse.py": (0, ok, "")})
    bj.pulse(c)
    res["pulse null: nothing stopped writes no digest, but the pulse file"] = (
        set(files(c)) == set() and (c.state / "beatd" / "pulse.txt").read_text() == ok
        and "--seat-queue" in f.calls[0])
    stop = "PULSE verdict STOPPED seat merge: 1 verdict(s)\n" + ok
    c, _ = fresh(answers={"pulse.py": (1, stop, "")})
    bj.pulse(c)
    res["pulse: a STOPPED line reaches the digest"] = digest(c) == "PULSE verdict STOPPED seat merge: 1 verdict(s)\n"

    c, f = fresh(answers={"pulse.py": (3, ok, "")})
    bj.pulse(c)
    res["pulse: an rc outside 0-2 is UNREADABLE, whatever it printed"] = digest(c).startswith("pulse: UNREADABLE rc=3")
    c, f = fresh(overlay={"repo": "o/r", "seat_alives": ["merge=/x/alive"]}, answers={"pulse.py": (0, ok, "")})
    bj.pulse(c)
    a = f.calls[0]
    res["pulse: each seat_alives entry is a --seat-alive argument"] = arg(a, "--seat-alive") == "merge=/x/alive"

    # cancel-sweep
    summ = "CANCEL-SWEEP: cancelled 1, kept 2 (live head), skipped 0 (bot head / not a PR), ghosts 0\n"
    c, _ = fresh(answers={"cancel_superseded.py": (0, "cancel_superseded: cancelled 9\n" + summ, "")})
    bj.cancel_sweep(c)
    res["cancel-sweep null: a clean sweep writes nothing"] = not files(c)
    c, _ = fresh(answers={"cancel_superseded.py": (0, "cancel_superseded: could not cancel 9\n" + summ, "")})
    bj.cancel_sweep(c)
    res["cancel-sweep: a failure reaches the digest"] = digest(c) == "cancel_superseded: could not cancel 9\n"

    c, f = fresh(answers={"cancel_superseded.py": (1, "", "boom\n")})
    bj.cancel_sweep(c)
    a = f.calls[0]
    res["cancel-sweep: a non-zero exit is a line, never silence, and gets --repo"] = (
        digest(c) == "cancel-sweep: rc=1: boom\n" and arg(a, "--repo") == "o/r")

    # disk
    c, f = fresh(free=lambda: 50.0)
    bj.disk(c)
    res["disk null: above the floor runs no collection"] = not files(c) and not f.calls
    frees = iter([5.0, 30.0])
    c, f = fresh(free=lambda: next(frees))
    bj.disk(c)
    res["disk: a collection that frees enough writes nothing"] = not files(c) and f.ran("worktree_gc.sh") == 1
    c, _ = fresh(free=lambda: 5.0)
    bj.disk(c)
    res["disk: still under the floor after collection is a line"] = digest(c).startswith("disk: 5 GiB free")

    # opener
    out = ("START r10-a 0123abcd R10-A pid=4\nSKIP r10-b 0123abcd seen\n"
           "OWED 2026-11-01T09:00:00Z open-refused r10-c 0123abcd rc=1 REFUSE title\n"
           "STUCK r10-d 0123abcd 3 tries\n")
    c, f = fresh(answers={"open_driver.py": (0, out, "")})
    pre = "open-refused" not in digest(c)
    bj.opener(c)
    jobs = bj.read(c.digest / "jobs" / "opener")
    ev = bj.read(c.digest / "events.txt")
    res["opener: an open-refused line lands in jobs/opener, a STUCK line in events.txt too"] = (
        pre and jobs == "OWED <t> open-refused r10-c 0123abcd rc=1 REFUSE title\nSTUCK r10-d 0123abcd 3 tries\n"
        and ev.endswith(" STUCK r10-d 0123abcd 3 tries\n") and ev.count("\n") == 1
        and "--board" in f.calls[0])
    bj.opener(c)
    res["opener: a STUCK line re-printed is not a second event"] = bj.read(c.digest / "events.txt") == ev
    c, _ = fresh(answers={"open_driver.py": (0, "START r10-a 0123abcd R10-A pid=4\n", "")})
    bj.opener(c)
    res["opener null: a pass that only starts writes nothing"] = not files(c)

    c, _ = fresh(answers={"open_driver.py": (1, "", "kaboom\n")})
    bj.opener(c)
    res["opener: a non-zero exit is a line, never silence"] = digest(c) == "opener: open_driver rc=1: kaboom\n"
    a = fresh(answers={"open_driver.py": (0, "", "")})
    bj.opener(a[0])
    b = a[1].calls[0]
    res["opener: open_driver is handed the board"] = arg(b, "--board") == str(a[0].board)

    # head-watch
    heads = {"v": f"12 {SHA['a']}\n13 {SHA['b']}\n"}
    c, _ = fresh(answers={"gh": lambda a: (0, heads["v"], "")})
    bj.head_watch(c)
    first = not (c.digest / "events.txt").exists() and (c.digest / "heads.tsv").exists()
    before = files(c)
    bj.head_watch(c)
    still = files(c) == before
    heads["v"] = f"12 {SHA['c']}\n13 {SHA['b']}\n"
    bj.head_watch(c)
    ev = bj.read(c.digest / "events.txt").splitlines()
    res["head-watch: a head move writes one line to events.txt and events.tsv stays absent"] = (
        first and still and len(ev) == 1 and ev[0].endswith(f"HEAD-MOVED #12 {SHA['a'][:12]} {SHA['c'][:12]}")
        and not (c.state / "events.tsv").exists())
    c, _ = fresh(answers={"gh": lambda a: (0, heads["v"], "")})
    for h in "abab":
        heads["v"] = f"12 {SHA[h]}\n" if h in SHA else ""
        bj.head_watch(c)
        c.now += 120
    res["head-watch: a head returning to an old sha is still a move (A->B->A->B is three events)"] = (
        len(bj.read(c.digest / "events.txt").splitlines()) == 3)
    c, _ = fresh(answers={"gh": (1, "", "boom")})
    bj.head_watch(c)
    res["head-watch: an unreadable API is UNREADABLE"] = digest(c) == "head-watch: UNREADABLE gh rc=1\n"

    # fold
    c, _ = fresh()
    bj.write_job(c, "pulse", ["PULSE a STOPPED x"])
    s1 = files(c)["new.stamp"]
    c.now += 60
    bj.write_job(c, "pulse", [])
    res["fold: a gone line is gone.txt and no new stamp"] = (
        bj.read(c.digest / "gone.txt") == "PULSE a STOPPED x\n" and files(c)["new.stamp"] == s1
        and digest(c) == "")
    c.now += 60
    bj.write_job(c, "disk", ["disk: 1 GiB"])
    bj.write_job(c, "pulse", ["PULSE a STOPPED x"])
    res["fold: the digest is in row order"] = digest(c) == "PULSE a STOPPED x\ndisk: 1 GiB\n"

    # no row moves the checkout
    calls = []
    for row in bj.ROWS:
        c, f = fresh(answers={"gh": (0, "", "")}, free=lambda: 1.0)
        (c.state / "roster-drain.queue").write_text("hold a/b x G\n")
        c.board.write_text(board("2026-11-01T09:00:00+00:00", owed))
        bj.RUN[row](c)
        calls += f.calls
    git = [c for c in calls if c[0] == "git"]
    res["no row runs a git command that moves HEAD or the tree"] = (
        bool(git) and not any(set(c) & set(MOVES) for c in git))
    tmp.cleanup()
    return res


#: (old, new, the case that must fail). Each old string appears once in beat_jobs.py.
MUTANTS = {
    "family_drops_owed": (r'r"^(?:OWED\b|', r'r"^(?:OWEDX\b|', "tick-digest: one OWED line gives exactly that line, and a stamp"),
    "no_age_norm": ('return AGE.sub("<age>", STAMP.sub("<t>", line.rstrip()))', 'return STAMP.sub("<t>", line.rstrip())',
                    "tick-digest: an age-only change is no new line"),
    "transient_counts_at_once": ("            if norm(ln) not in seen[\"transient\"]:\n                continue\n", "",
                                 "tick-digest: a transient RED gives nothing; on a second board it appears"),
    "same_board_two_passes": ('    if seen["pass"] == first:\n        return', '    if False:\n        return',
                              "tick-digest: a transient RED gives nothing; on a second board it appears"),
    "unflagged_lines_read": ('if ln.startswith("-> ") and FAMILY', 'if FAMILY',
                             "the fixture board's digest is exactly its recorded actionable set"),
    "owed_rc1_dropped": ("    if rc == 1:\n", "    if rc == 9:\n", "owed-check: an UNACTIONED exit lands in new.txt"),
    "roster_no_mark": ("            done.add(key)  # applied", "            pass  # applied",
                       "roster-drain: a queue line drains once, is marked, and is not re-run"),
    "roster_hold_ignored": ("            if not on_main(ctx, parts[1]):", "            if False:",
                            "roster-drain: a hold waits for main, is HOLD-STALE past 24 h, then releases"),
    "plan_rc1_silent": ('    if rc == 0:\n        return write_job(ctx, "plan-beat", [])',
                        '    if rc in (0, 1):\n        return write_job(ctx, "plan-beat", [])',
                        "plan-beat: state_docs rc 1 is PLAN UNAVAILABLE"),
    "pulse_stopped_dropped": ('(?:STOPPED|UNREADABLE) ', '(?:UNREADABLE) ', "pulse: a STOPPED line reaches the digest"),
    "cancel_failure_dropped": ('r"could not cancel| rc=', 'r"could not cancelX| rc=',
                               "cancel-sweep: a failure reaches the digest"),
    "disk_no_recheck": ("    free = ctx.free_gib()\n", "    free = floor - 1\n",
                        "disk: a collection that frees enough writes nothing"),
    "opener_no_event": ('        if ln.startswith("STUCK "):', '        if ln.startswith("STUCKX "):',
                        "opener: an open-refused line lands in jobs/opener, a STUCK line in events.txt too"),
    "head_no_compare": ("        if n in old and old[n] != heads[n]:", "        if False:",
                        "head-watch: a head move writes one line to events.txt and events.tsv stays absent"),
    "fold_stamp_always": ("    if new:\n        atomic(ctx.digest / \"new.txt\"", "    if True:\n        atomic(ctx.digest / \"new.txt\"",
                          "fold: a gone line is gone.txt and no new stamp"),
    "null_pass_writes": ("    if read(path) == text:\n        return\n    with Locked(ctx):",
                         "    with Locked(ctx):",
                         "tick-digest null: a board with nothing owed writes no job, no digest, no stamp"),
    "tick_provenance_any_text": ("    if not PROVENANCE.match(first):\n", "    if not text:\n",
                                 "tick-digest: a board without its provenance line is UNREADABLE, never clean"),
    "owed_tick_wrong": ('"--tick", str(ctx.board)', '"--tick", str(ctx.state)',
                        "owed-check: the instrument is handed the board and the ledger"),
    "roster_partial_runs": ('.split("\\n")[:-1]', '.split("\\n")',
                            "roster-drain: an unterminated last line waits for its newline and runs once, whole"),
    "roster_shrank_not_sticky": (' or ctx.memory("roster-shrank.json", False):', ':',
                                "roster-drain: a cleared queue is refused as QUEUE-SHRANK, stays refused, and nothing runs"),
    "roster_shrink_ignored": ("    if len(whole) < seen or ", "    if False and ",
                              "roster-drain: a cleared queue is refused as QUEUE-SHRANK, stays refused, and nothing runs"),
    "roster_noop_marked": ('        if not any("no op attempted" in ln for ln in said):', '        if True:',
                           "roster-drain: a no-op-attempted report is retried on the next pass"),
    "plan_rc2_unavailable": ('word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"', 'word = "PLAN UNAVAILABLE"',
                             "plan-beat: state_docs rc 2 is REFUSED, not PLAN UNAVAILABLE"),
    "plan_replan_args_dropped": ('"--out", plan, "--slots", slots, "--seats", seats)', '"--out", plan)',
                                 "plan-beat: replan is handed the plan, slots and seats"),
    "pulse_unreadable_ignored": ("    if rc not in (0, 1, 2) or not out:", "    if not out:",
                                 "pulse: an rc outside 0-2 is UNREADABLE, whatever it printed"),
    "pulse_alive_dropped": ('        args += ["--seat-alive", e]', '        pass',
                            "pulse: each seat_alives entry is a --seat-alive argument"),
    "cancel_rc_ignored": ("    if rc != 0:\n        bad.append(f\"cancel-sweep", "    if False:\n        bad.append(f\"cancel-sweep",
                          "cancel-sweep: a non-zero exit is a line, never silence, and gets --repo"),
    "opener_rc_ignored": ("    if rc != 0:\n        lines.append(f\"opener", "    if False:\n        lines.append(f\"opener",
                          "opener: a non-zero exit is a line, never silence"),
    "opener_board_dropped": ('"tools/audit/seat/open_driver.py", "--board", str(ctx.board))', '"tools/audit/seat/open_driver.py")',
                             "opener: open_driver is handed the board"),
    "head_dedupe_whole_file": ('            if same and same[-1] == line:', '            if line in kept:',
                              "head-watch: a head returning to an old sha is still a move (A->B->A->B is three events)"),
    "tick_unreadable_sticks": ('        ctx.remember("tick.json", {"pass": "", "transient": seen_before["transient"]}, {"pass": "", "transient": []})\n', "",
                               "tick-digest: the same board returning after an outage clears the UNREADABLE line"),
    "event_dedupe_dropped": ("        elif line in kept:\n            return\n", "",
                             "opener: a STUCK line re-printed is not a second event"),
}


def run(target: Path, mutants: bool = True) -> int:
    bj = load(target)
    res = cases(bj)
    failed = 0
    for name, ok in res.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        failed += not ok
    total = len(res)
    if mutants:
        src = target.read_text()
        with tempfile.TemporaryDirectory() as d:
            for i, (mname, (old, new, case)) in enumerate(MUTANTS.items()):
                total += 1
                if src.count(old) != 1:
                    print(f"  FAIL mutant {mname}: its site appears {src.count(old)} times")
                    failed += 1
                    continue
                p = Path(d) / f"m{i}.py"
                p.write_text(src.replace(old, new))
                try:
                    killed = cases(load(p, f"beat_jobs_m{i}")).get(case) is False
                except Exception as e:  # a crash is no kill
                    print(f"    mutant {mname} crashed: {e.__class__.__name__}: {e}")
                    killed = False
                print(f"  {'ok  ' if killed else 'FAIL'} mutant {mname} killed by: {case}")
                failed += not killed
    print(f"beat_jobs self-test: {total} checks, {failed} failed")
    return 1 if failed else 0
