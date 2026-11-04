R10-FLY-STANDING-CONTRACTS, part P1 (code), as the approved design orders it (design/r10-fly-standing-contracts 21210036, `Design review: approve` on design-verdict/r10-fly-standing-contracts 2d0ac2c0). P2 to P5 follow after this merges under the same group; they are not in this diff.

Round 2 after verdict/3197 (round 1, blocked, three items). Each is fixed at its root in `beat_jobs.py` and killed in its self-test:

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

## Head

bb3bcda5d73975cc62458092ddb7df3871f20855 (merged with origin/main 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e; origin/main moved since the first `prepr.sh` run, so it was rerun on this head with this body).

## Mutation proof

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` plants 32 mutants, each in a temp copy and each killed by its named case (`ok   mutant <name> killed by: <case>`). The 16 from round 1 plus the 16 of this round: tick_provenance_any_text, owed_tick_wrong, roster_partial_runs, roster_shrank_not_sticky, roster_shrink_ignored, roster_noop_marked, plan_rc2_unavailable, plan_replan_args_dropped, pulse_unreadable_ignored, pulse_alive_dropped, cancel_rc_ignored, opener_rc_ignored, opener_board_dropped, head_dedupe_whole_file, tick_unreadable_sticks, event_dedupe_dropped.
- The reviewer's harness at both ends: `ev/own_mutants.py` at the reviewed head printed nine `SURVIVED`; at this head it prints none (its `event: dedupe removed` site no longer exists verbatim because the dedupe was split, and is replaced by `event_dedupe_dropped`, which is killed). `ev/probes.py` P1 at the reviewed head ran the truncated op and the whole op; at this head it runs only the whole op. P2 at this head runs the op once and the digest carries `roster: QUEUE-SHRANK`. P3 prints three events. P4's same board returning prints `MERGE-READY: #9 9a8b7c6d`.
- Carried from round 1: pulse.py `seat_of` and `judge_verdict` mutations turn `two owed verdicts name both PRs on two lines and both seats` red; sweep_render's `git-cwd` raise deleted turns `null control: step (2) without its -C is refused as git-cwd` red.

## Null control

- Every new case passes on the unmutated tree (`beat_jobs self-test: 82 checks, 0 failed`), and each asserts its expected line absent before the plant. The shrink case's null: an untouched queue drains once and is not re-run (`a queue line drains once, is marked, and is not re-run`); a first pass with no queue writes no byte (`roster-drain null: no queue writes nothing`, memory `roster-queue-lines.json` is never created at 0).
- Round 1's nulls stand: nothing-owed board, owed rc 0, both plan steps rc 0, pulse nothing stopped, clean cancel sweep, disk above floor, opener only starting, head-watch first and unchanged pass.
- pulse.py: one owed verdict still prints one line; sweep_render: the tracked template renders.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `beat_jobs self-test: 82 checks, 0 failed`.
- `python3 -I tools/audit/seat/pulse.py --self-test` and `python3 -I tools/audit/seat/sweep_render.py --self-test` are unchanged from round 1 (58 and 34 checks, 0 failed); neither file is touched this round.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 112 self-testing, 112 wired, 0 unwired` and `0 index gap(s)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget file is touched; claim files are byte-identical to origin/main.
- `tools/pr/prepr.sh` rc=0 before the final merge of origin/main; rerun on this head with this body (see Head).

## Live-usage review

No out-of-tree stand-in log is readable from a cloud fixer; recorded as a gap, as in round 1. Dispositions unchanged: gap 1 owed-check runs at 1800 s; gap 2 transient RED needs a second board; gap 3 and 5 are P2/P5; gap 4 no row moves the checkout (self-test case); gap 6 holds are HOLD-STALE after 24 h; gap 7 owed before P2's retirement gate.

## Red checks

`tests / nightly-status` is red at this head and inherited from main, not from this diff: it reports main's scheduled Nightly run (the cycle_cost cpu_ratio budget), and this diff reaches neither `nightly.yml` nor `tests/nightly_status.py`; it is not a required check, and no cheaper detector in this diff's reach exists for a budget measured on a schedule. No other check has concluded red at the time of writing; CI for this head had not run when this body was written.

## Forward-carry

none

## Friction

none
