R10-FLY-STANDING-CONTRACTS, part P1 (code), as the approved design orders it (design/r10-fly-standing-contracts 21210036, `Design review: approve` on design-verdict/r10-fly-standing-contracts 2d0ac2c0). P2 to P5 follow after this merges under the same group; they are not in this diff.

Rounds 2 and 3 after verdict/3197 (round 1 blocked, three items; round 2 blocked on seven row mutants that survived the self-test, and four low ones). Round 2 below. Each is fixed at its root in `beat_jobs.py` and killed in its self-test:

1. roster-drain ran a half-written queue line. It now runs only newline-terminated lines; an unterminated tail waits for its newline and then runs once, whole.
2. The done-marker lost a re-queued op after the queue was cleared. The queue is now stated append-only: roster-drain remembers how many terminated lines it has drained (`roster-queue-lines.json`) and, on a queue with fewer, reports `roster: QUEUE-SHRANK ...`, runs nothing and stays refused (`roster-shrank.json`) until the operator deletes the four roster memories, which the line names.
3. The nine surviving reviewer mutants each have a planted case, and an argv assertion where the arm is wiring (tick-digest provenance line, owed-check `--tick`/`--acks`/`--state`, roster-drain no-op-attempted retried, plan-beat rc 2 REFUSED and replan `--out/--slots/--seats`, pulse rc outside 0-2 UNREADABLE and `--seat-alive`, cancel-sweep rc != 0 and `--repo`, opener rc != 0 and `--board`).

Both Follow-ups were free in the same lines and are taken: head-watch's HEAD-MOVED dedupes only against that PR's last move (A->B->A->B is three events; STUCK lines keep the whole-file dedupe), and tick-digest forgets its remembered pass on UNREADABLE, so the same board returning clears the line.

What lands overall:
- `tools/audit/seat/beat_jobs.py`, the one owner of the beat's job predicates and the only writer of `$HPO_STATE_DIR/digest/`. Nine rows: tick-digest, owed-check, roster-drain, plan-beat, pulse, cancel-sweep, disk, opener, head-watch. Each writes only actionable lines to `digest/jobs/<row>`; `fold()` under `flock digest/.lock` builds `digest.txt`, `new.txt`, `gone.txt` and touches `new.stamp` only on a new line. A null pass changes no byte. head-watch and the opener's STUCK lines go to `digest/events.txt`; `events.tsv` stays ledger.py's.
- `tools/audit/seat/beatd.jobs.json`, beatd's default table, one row per job.
- `tools/audit/seat/beat_jobs_selftest.py` (cases and mutants), `tools/audit/seat/fixtures/beat_jobs/`, `instruments/beat_jobs.py.md` and its `INSTRUMENTS.md` row, the governance workflow step that runs the self-test.
- `tools/audit/seat/pulse.py` (carry 5): the verdict arm names every owed verdict, one PULSE line each, and both seats when merge and non-merge verdicts are owed.
- `tools/audit/seat/sweep_template.md` steps (2), (4b), (4e), (5), (8) read the digest; step (2) runs `git -C {{orch_checkout}} ls-remote` (carry 6); step (5) prints both board counts (carry 7). `tools/audit/seat/sweep_render.py` gains a `git-cwd` refusal.

Design choices, stated:
- Session paths come from the sweep overlay; a row whose key the overlay lacks writes `<row>: UNREADABLE overlay lacks <key>`, never nothing.
- roster-drain marks done in its own memory (`digest/state/roster-done.json`, keyed by occurrence and exact text) rather than rewriting the orchestrator's unlocked queue. Alternative considered for item 2: key on something that survives truncation (lost: no such key exists in an append-only line list, and silently re-running a cleared queue could apply an op twice); refusing a shrink visibly was taken. The refusal is sticky because a re-queued op appended past the old length would otherwise run while its predecessors are skipped.
- The pulse row writes pulse.py's stdout to `S/beatd/pulse.txt` (pulse.py has no `--out`), the one write outside `digest/`.
- An idle roster-drain pass keeps the last drain's lines.
- Design item 22 (plan-beat beside postmerge's `state_docs.py --push`) is not measured live here; design item 22 binds P2.
- Setup the beat needs before P2's gate: the lint clone roster-drain uses in the state directory and a copy of the sweep overlay there (stated in `beat_jobs.py`'s docstring).

Round 3 (this head) pins what the round-2 delta review planted, each in `beat_jobs_selftest.py`:

- The seven blocking survivors: tick-digest's NOT REVIEWABLE half of the transient rule; roster-drain's hold release handing roster_queue the held op rather than `hold <path> <op>`; plan-beat's `--mirror` argv; pulse's `--launch-ledger` argv; cancel-sweep's `truncated` failure text; the opener's `NEEDS-TITLE ` and `STARVED ` prefixes.
- The four low ones: head-watch drops closed PRs from heads.tsv; fold counts a duplicated line; `Ctx.need` refuses an empty string; a malformed hold line is refused once and marked.
- The follow-up: a changing fold that added nothing empties `new.txt`, and one that dropped nothing empties `gone.txt`; `new.stamp` is still touched only on a new line.

Opener STUCK arm: the opener row's STUCK arm has no producer at this head; `open_driver.py` prints no `STUCK ` line, and the design lands STUCK as an `open_driver.py` edit owned by R10-HANDOFF-PATH. The arm is forward-wired as designed; the stage that lands STUCK must keep the `STUCK ` prefix the OPENER regex reads.
Carry: R10-HANDOFF-PATH

## Head

3e0fc2c03f31f2e91574242402d81fd9e3979f26 (the code head at handoff/r10-fly-standing-contracts-p1; it is origin/main 783d8dc72811 merged into the fix branch). The prepr run on this head was rc=0; this body was rebuilt after that run and changes no code.

## Mutation proof

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `beat_jobs self-test: 107 checks, 0 failed`; each planted mutant is killed by its named case (`ok   mutant <name> killed by: <case>`), including `fold_new_kept_stale`, killed by `fold: a fold that added nothing empties new.txt, and leaves the stamp`.
- The reviewer's harness at both ends. Fetched with `git fetch origin refs/heads/probe/rev-3197-774a490e`, its `ev/own_mutants2.py` was run from this head's worktree: at the reviewed head 344feb6c it printed 24 planted, 11 survived; at this head it prints `own_mutants2: 24 planted, 0 survived`. One line reads `SITE 0x  fold: gone.txt never written`: that mutant's source site no longer exists verbatim in `beat_jobs.py`, so it plants nothing here and is counted in the 24; the behaviour it stood for is the `fold` case that empties `gone.txt`.
- Carried from rounds 1 and 2: the round-1 harness results stand (`ev/own_mutants.py` at the reviewed head showed nine `SURVIVED`, at this head none), as do the pulse.py `seat_of` and `judge_verdict` mutations and sweep_render's `git-cwd` raise deleted.

## Null control

- Every new case passes on the unmutated tree (`beat_jobs self-test: 107 checks, 0 failed`), and each asserts its expected line absent before the plant. A fold that changes nothing writes no byte; a fold that adds nothing empties new.txt and leaves the stamp, a null pass leaves both alone.
- The unterminated-line, shrunk-queue and untouched-queue nulls of round 2 stand, as do round 1's: nothing-owed board, owed rc 0, both plan steps rc 0, pulse nothing stopped, clean cancel sweep, disk above floor, opener only starting, head-watch first and unchanged pass.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `beat_jobs self-test: 107 checks, 0 failed`.
- `python3 -I tools/audit/seat/pulse.py --self-test` prints `pulse self-test: 58 checks, 0 failed`; `python3 -I tools/audit/seat/sweep_render.py --self-test` prints `sweep_render self-test: 34 checks, 0 failed`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 112 self-testing, 112 wired, 0 unwired` and `selftest_wiring: 0 index gap(s)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget file is touched.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2611 ENTITY CHECKS PASSED`.
- Toolchain: `python3 -c 'import numpy,scipy'` prints 2.5.4 1.18.1, equal to the pins in tests/requirements-ci.txt; this diff records no golden, and CI remains the authority for any.

## Live-usage review

No out-of-tree stand-in log is readable from a cloud fixer; recorded as a gap, as before. Dispositions unchanged: gap 1 owed-check runs at 1800 s; gap 2 transient RED or NOT REVIEWABLE needs a second board (now pinned for both texts); gap 3 and 5 are P2/P5; gap 4 no row moves the checkout (self-test case); gap 6 holds are HOLD-STALE after 24 h; gap 7 owed before P2's retirement gate.

## Red checks

`tests / nightly-status` was red at the last head and is inherited from main: it reports main's scheduled Nightly run (the cycle_cost cpu_ratio budget); this diff reaches neither `nightly.yml` nor `tests/nightly_status.py`; it is not a required check, and no cheaper detector in this diff's reach exists for a budget measured on a schedule. CI for this head had not concluded when this body was written.

## Forward-carry

- The opener row's STUCK arm has no producer until `open_driver.py` prints a `STUCK ` line (see above). Carry: R10-HANDOFF-PATH

## Friction

none
