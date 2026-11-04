R10-FLY-STANDING-CONTRACTS, part P1 (code), as the approved design orders it (design/r10-fly-standing-contracts 21210036, `Design review: approve` on design-verdict/r10-fly-standing-contracts 2d0ac2c0). P2 to P5 follow after this merges under the same group; they are not in this diff.

What lands:
- `tools/audit/seat/beat_jobs.py`, the one owner of the beat's job predicates and the only writer of `$HPO_STATE_DIR/digest/`. Nine rows: tick-digest, owed-check, roster-drain, plan-beat, pulse, cancel-sweep, disk, opener, head-watch. Each writes only actionable lines to `digest/jobs/<row>`; `fold()` under `flock digest/.lock` builds `digest.txt`, `new.txt`, `gone.txt` and touches `new.stamp` only on a new line. A null pass changes no byte. head-watch and the opener's STUCK lines go to `digest/events.txt`; `events.tsv` stays ledger.py's.
- `tools/audit/seat/beatd.jobs.json`, beatd's default table (beatd.py `--jobs` default), one row per job, loaded clean by `beatd.load_table`.
- `tools/audit/seat/beat_jobs_selftest.py`, the self-test's cases and mutants; `tools/audit/seat/fixtures/beat_jobs/` (a board in the tick's printed shapes and its actionable set); `instruments/beat_jobs.py.md` and its `INSTRUMENTS.md` row; the governance workflow step that runs the self-test (selftest_wiring `--check`: 0 unwired).
- `tools/audit/seat/pulse.py` (carry 5, design item 6): the verdict arm names every owed verdict, one PULSE line each, and both seats when merge and non-merge verdicts are owed.
- `tools/audit/seat/sweep_template.md`: steps (2), (4b), (4e), (5) and (8) read the digest; step (2) runs `git -C {{orch_checkout}} ls-remote` (carry 6); step (5) reads the digest whole and prints both board counts, and `tick_log` is documented as the board `tick_loop.sh --out` writes (carry 7). (1b), the tick restart and the `tick_alive`/`tick_brief` placeholders stay for P2 (design item 21).
- `tools/audit/seat/sweep_render.py`: a new `git-cwd` refusal (a rendered `` `git `` that does not open `git -C`), and self-test rows for steps (2) and (5).

Design choices, stated:
- Session paths come from the sweep overlay (`$HPO_STATE_DIR/sweep-overlay.json` by default), the JSON `sweep_render.py` already reads, so no second list of session paths exists; a row whose key the overlay lacks writes `<row>: UNREADABLE overlay lacks <key>`, never nothing. Alternatives: env_pass names per path (lost: a second list, silent when unset); a new session config file (lost: duplicates the overlay).
- roster-drain marks done in its own memory (`digest/state/roster-done.json`, keyed by exact line text and occurrence) rather than rewriting the orchestrator's queue file, which the orchestrator appends to unlocked; a rewrite could lose an append. Design item 13 says roster-drain deletes its own marker once exact-line marking lands in roster_queue.py. The queue is `$HPO_STATE_DIR/roster-drain.queue`, separate from the roster seat's queue, so the job can run beside the seat for the scratch-branch acceptance without double-applying; its lint clone is `$HPO_STATE_DIR/roster-lint`, the orchestrator's to provision (roster_queue.py refuses it by name until then, and the line reaches the digest). `roster_queue.py` has no hold form; `hold <tree-path> <op ...>` is this row's grammar, released when `git cat-file -e origin/main:<tree-path>` succeeds, `HOLD-STALE` after 24 h (gap 6).
- The pulse row writes pulse.py's stdout to `S/beatd/pulse.txt` (pulse.py has no `--out`): the one write outside `digest/`, the file the design names (beatd.py `status` reads it).
- An idle roster-drain pass keeps the last drain's lines, so a refusal stays in `digest.txt` until the next op instead of vanishing after one 120 s pass.
- Design item 22 (plan-beat beside postmerge's `state_docs.py --push`): not measured live here. state_docs.py exits 2 on a failed push, which this row prints as `plan-beat: REFUSED`, and the next 30-min pass republishes; no lock added. Recorded as unmeasured; design item 22 already binds P2.
- Setup the beat needs before P2's gate can read every row ok: the lint clone roster-drain uses, in the state directory, and a copy of the sweep overlay there; both are stated in `tools/audit/seat/beat_jobs.py`'s docstring.

## Head

34624b407949a164cb6e55a3a616dd60e6317789, merge base 8e90d81443317f76f22602a89651f7ca17c633f9 = origin/main at the measurement (`git rev-parse origin/main`, 2026-11-04T11:17Z). origin/main moved twice during the work; it was merged (not rebased), every check below re-run on the merged tree, and `prepr.sh` re-run on it.

## Mutation proof

- `beat_jobs.py`: the self-test plants 16 mutants, one per row predicate and two on the fold, each in a temp copy, and every one is killed by its named case (`python3 -I tools/audit/seat/beat_jobs.py --self-test`, lines `ok   mutant <name> killed by: <case>`): family_drops_owed, no_age_norm, transient_counts_at_once, same_board_two_passes, unflagged_lines_read, owed_rc1_dropped, roster_no_mark, roster_hold_ignored, plan_rc1_silent, pulse_stopped_dropped, cancel_failure_dropped, disk_no_recheck, opener_no_event, head_no_compare, fold_stamp_always, null_pass_writes.
- `pulse.py` carry 5: restoring `seat_of`'s oldest-only rule turns `FAIL two owed verdicts name both PRs on two lines and both seats`; separately, returning only the head line from `judge_verdict` turns the same check red. Restored after each.
- `sweep_render.py`: deleting the `git-cwd` raise (`if bare:` to `if False:`) turns `FAIL null control: step (2) without its -C is refused as git-cwd`. Restored.

## Null control

- beat_jobs self-test nulls, each asserting no byte written: a board with nothing owed (no job file, no digest, no stamp); owed_unactioned rc 0; no roster queue; both plan steps rc 0; a pulse with nothing stopped (only `pulse.txt`); a clean cancel sweep; disk above the floor (no collection run); an opener pass that only starts; head-watch's first pass (records heads, no event) and an unchanged second pass (byte-identical files). Each planted case first asserts its expected line is absent from the empty digest.
- pulse.py: one owed verdict still prints one line (`one owed verdict prints one line`).
- sweep_render.py: the tracked template renders (every placeholder filled); the old step (2) text is refused as `git-cwd`, and the old step (5) text fails the digest-read check.
- At the merge base, the two-verdict snapshot (blocked 9 h, merge 5 h, both at their open heads) gives `seat_of` = `dispatch` and one detail line naming only #2527; at the head, `merge and dispatch` and a second line `#2526 merge aaaaaaaa 5.0 h`.

## Figures

- beat_jobs self-test: `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `beat_jobs self-test: 52 checks, 0 failed` (36 cases, 16 mutants).
- pulse self-test: `python3 -I tools/audit/seat/pulse.py --self-test` prints `pulse self-test: 58 checks, 0 failed`.
- sweep_render self-test: `python3 -I tools/audit/seat/sweep_render.py --self-test` prints `sweep_render self-test: 34 checks, 0 failed`.
- self-test wiring: `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 112 self-testing, 112 wired, 0 unwired` and `0 index gap(s)`.
- job table: `beatd.load_table(Path("tools/audit/seat/beatd.jobs.json"))` returns 9 jobs, no refusal.
- carry 5, base against head: the driver applies `seat_of("verdict", snap, now, 2 h)` and `judge_verdict` to one two-verdict snapshot, loaded from `git show origin/main:tools/audit/seat/pulse.py` and from the head file; outputs as quoted under Null control.
- the fixture board's actionable set: the rule is FAMILY over the board's `-> ` lines, transients only on a second board; the self-test compares the digest of `fixtures/beat_jobs/board.txt`, read at two board stamps, to `fixtures/beat_jobs/digest.txt` byte for byte; the four non-family flagged lines (`train beat stale`, `re-take the body`, `DONE?`, `API quota low`) and every unflagged line are absent. The family literals are pinned: each must appear in `orchestrator_tick.py` or `ledger.py` source (`every family literal is one the board's printers print`).
- class seams (step 8), rule `git grep -n "git " tools/audit/seat/sweep_template.md | grep -v -- "-C {{"` at the merge base returns step (2) only; at the head it returns nothing, and `sweep_render.py`'s `git-cwd` refusal now enforces the class at every render rather than this one instance.
- no row moves the checkout: every git argv the nine rows issue in the self-test is recorded, and none names `checkout`, `switch`, `reset`, `pull`, `merge`, `rebase`, `stash`, `clean` or `restore` (`no row runs a git command that moves HEAD or the tree`); the only git the rows run is `git -C <repo> cat-file -e origin/main:<path>`.
- scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`; `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`; `tests/entities.py` result below.
- structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget file is touched.
- architecture score: `tests/arch_score.py` and `tests/arch_score_head.py` are scoped out (no changed file in their measured closures); no file under the scored tree changes.

## Live-usage review

STEP 1 needs the orchestrator's out-of-tree stand-in logs (the tick-digest stand-in, the sweep runner and roster drain, the opener driver's log, the rendered sweep and overlay, cloud_relay's level file, the tick board). A cloud fixer cannot read them, and the dispatch ruling says to record that as a gap and go on. So each row below is the gap the brief names, its evidence the brief's own 2026-10-31 field record, and its disposition in this diff; no figure is re-measured from a log.

| gap (brief, 2026-10-31) | disposition in P1 |
|---|---|
| 1. owed_unactioned.py counts every run as a sweep | the owed-check row runs it at 1800 s, once per sweep, and step (5) no longer runs it by hand |
| 2. a NOT REVIEWABLE or RED line read between open_pr's two pushes is transient | tick-digest counts those lines only once a second board carries them (planted case and null) |
| 3. a blind touch loop on a seat's alive file defeats liveness | no row touches an alive file; the Wait term is P2's standing.md (design items 1, 27) |
| 4. a sweep step that fast-forwards the checkout the loops run from corrupts them | no row runs a git command that moves HEAD or the tree (self-test case); P3's pre-bash.sh guard covers sessions |
| 5. during a recycle, work sent to both seats minted three nonces at one head | not P1: the Recycle term is P2's, the generation token P5's |
| 6. hold-file lines never expire | roster-drain's `hold` lines are `HOLD-STALE` after 24 h and release once main carries their path (planted case) |
| 7. stated gap: no live log read | the orchestrator's review of the stand-ins against this table is owed before P2's retirement gate (design §6: every P1 row `ok` from main for one cycle beside the live seats) |

## Red checks

none

## Forward-carry

none

## Friction

none
