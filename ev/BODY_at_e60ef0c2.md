R10-SEAT-IDENTITY-P5 (part 1 of 1: carries 0-4, 8). One writer per standing seat (generation token) and per orchestrator session (session lock), the `loop-cwd` beat row, and the mutant harness made runnable again. Functions touched in the shared seams: `beat_jobs.py` `loop_cwd` (new) and the `ROWS`/`RUN` tables; `beatd.jobs.json` one entry; `sweep_template.md` the Placeholders row `loop_cwd_patterns`, one sentence in (5b) and one in step (0); `roster_queue.py` `run_queue`; `merge_train.py` `train_add`; `bus.sh` `dispatch`; `handover_prompt.py` Resume steps. No edit to `beatd.py`.

## Head

7572aa0aa878e55d8480264d8f0bcd927c6280aa

## Merge of origin/main (repair)
Conflict: origin/main 402b0e7636 (#3484) and this branch both edited `PLANTS` in `dev/audit/harnesses/r10_open_driver_mutants.py` (main added M-livetip and M-moved-gone; this branch retargeted M-exact and M-body at `topic_grammar.py`). Resolution: both sides kept, every plant of each present, nothing else changed. Harness run at the merged head: 24 mutants, 0 survived. `tools/pr/prepr.sh` at the merged head: rc=0, every step ok (closures, diff mutants and body skipped), no red predicted. Carry: dismissed: no finding.

## Closures repair (edited classification lines)
Under the coordinator's ruling the owner's mandate covers, the minimal classification edit only:
- `tests/closure.py` `INERT_EXCEPT`: added `tools/audit/seat/seat_gen.py` and `tools/audit/seat/seat_gen_selftest.py` (plus a comment), because `tests/entities.py` reads both and the INERT `tools/audit/seat/` prefix declared them unread; the refusal text named "remove from INERT or except them", and the prefix stays INERT as for `orchestrator_tick.py`.
- `tests/closures.json`: the two files recorded into the `tests/entities.py` closure by `derive_closures.sh --single tests/entities.py --record-only` then `closure.py merge --partial --allow-failures` (the recording's only FAILs were the orphan check this edit clears and the harness's own null-control fixtures); `orphan_files()` now prints `[]`. The stray earlier entry under another key is removed by the merge.
- `BLOCKED.md` removed. Nothing else changed.
`tools/pr/prepr.sh` at this head: rc=0 (MODE: FULL, since `tests/closure.py` is a gate file).

## Mutation proof

Each plant is one site in `seat_gen.py` or `beat_jobs.py`; the named check goes red, the unmutated control is green.
- `seat_gen.py --self-test`: `held > gen` to `>=` reddens "check null: the current generation passes"; to `<` reddens "check: a lower generation is SUPERSEDED, exit 1"; dropping the command match reddens "lock null: a reused pid naming another command is taken over"; dropping `held != mine` reddens "lock null: the session's own pid is not a duplicate"; dropping the ancestor command test reddens "session_pid: the first ancestor running the session binary, never the shell". 5 of 5 killed.
- `beat_jobs.py --self-test`: comparing only that the path resolves (`if now is None`) reddens "loop-cwd: a directory recreated at the same path writes DEAD"; treating an empty `lsof` as DEAD reddens "loop-cwd: an lsof that returns nothing is UNREADABLE, never DEAD".
- `dev/audit/harnesses/r10_open_driver_mutants.py`: mutants=22, `survived=0` (carry 8 retarget of M-exact, M-body, M-triageB to `topic_grammar.py` and M-crit).

## Repair round 4 (items by number)
- Item 3: built, see Forward-carry. Self-test: `pulse.py` 69 checks 0 failed, with 3 new (SUPERSEDED, null control bump before launch, null control no token). Mutation: `launched < gen_t` to `>` reddens "a gen bump after the newest launch ... is SUPERSEDED" and "null control: a gen bump before the newest launch is ok" (2 failed), restored green.
- Item 4: `lock` now records the process start time (`ps -o etimes=` back from now, 0 if ps cannot say) and takes a flock around read-decide-write as `bump` does; docstring states it. `seat_gen.py` 23 checks 0 failed. Mutation: writing `int(now)` again reddens "lock: a free lock is taken" and "lock: a live other holder ... refuses" (2 failed), restored green.
- Item 5: restated in Figures (9 lines in 5 files, three wired writers).
- Item 6: residual conflict with #3484 (carry R10-HOTFIX-OPENER-UNBLOCK): only `dev/audit/harnesses/r10_open_driver_mutants.py`, two adjacent PLANTS edits; whichever PR lands second keeps both hunks and sets EXPECTED to mutants=24 (measured 24 survived=0 by the reviewer).
- Main moved: merged origin/main (6e100ef69802) and reran `tools/pr/prepr.sh` at this head: rc=0.

## Null control

- Generation: the current generation, a generation ahead of the file and a seat with no file all exit 0; unset `HPO_SEAT_GEN` leaves each wired writer (`run_queue`, `dispatch`, `train_add`) writing as before (self-test cases in `roster_queue.py`, `bus.sh`, `merge_train.py`: superseded writes nothing, generation 2 writes).
- Lock: a dead holder pid and a reused pid naming another command are both taken over; the session's own pid is not a duplicate.
- `loop-cwd`: a live directory writes nothing (real child process); a process absent from `pgrep` is no line; a lacking overlay key prints UNREADABLE.
- Harness null: the unmutated copy prints `failed=0`.

## Figures

- `python3 -I tools/audit/seat/seat_gen.py --self-test`: instrument `seat_gen.py`, prints its check count and `0 failed`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: 0 failed.
- `python3 -I tools/audit/seat/open_driver.py --self-test`: 0 failed.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: `survived=0`; at the merge base it aborted `ABORT M-exact: pattern occurs 0 times` (carry 8).
- `python3 tools/pr/ci_predict.py --base ba544faa2dd25b75b0129879112d6409affe9662`: no red predicted at the head.
- Writers wired, measured at the merge base by `git grep -n -E "def (run_queue|train_add)|dispatch\(\)" -- tools/audit/seat`: re-measured at merge base 6e100ef69802 (main, merged): 9 lines in 5 files -- `bus.sh` `dispatch()` (1), `cloud_dispatch.py` `dispatch()` call sites (5), `merge_train.py` `train_add`, `queue_pre_flight.py` `run_queue`, `roster_queue.py` `run_queue`. The conclusion holds: three wired writers (`bus.sh dispatch`, `merge_train.train_add`, `roster_queue.run_queue`); the `cloud_dispatch.py` sites are callers and `queue_pre_flight.py`'s `run_queue` is an unrelated function.

## Red checks
- `tests / closures`: red at the earlier head because `seat_gen.py` and `seat_gen_selftest.py` sat on the INERT `tools/audit/seat/` prefix while `tests/entities.py` read them. Repaired at this head (see Closures repair; `orphan_files()` empty, prepr rc=0). Cheaper detector: `closure.py orphan_files()` / `tests/entities.py` locally, about 20 minutes under strace, and `ci_predict` self-test-reads, which prepr runs in seconds but only predicted it once the files were classified; standing cost is the recording itself, so no new detector is warranted. Carry: dismissed

- `tests / fast (3.14)`: red on this branch's ancestry (main), not on a file this diff touches; this diff changes no production code and its own self-tests pass at head (prepr rc=0). Cheaper detector: none found for a main-side red, the scoped gate already runs only this diff's closure. Carry: dismissed: inherited from main, outside this diff

## Forward-carry

- Carry 0, Carry 1 and Carry 2 (generation token, session lock, their fold): built here; the `lock` step is named in `handover_prompt.py` Resume steps and `sweep_template.md` step (0). The tick flag is now built (item 3): `pulse.py` `read_alive` reads the `<seat>.gen` epoch (`gen_t`, from `$HPO_STATE_DIR`) and `judge_alive`, given the launch ledger, prints `SUPERSEDED <seat>: <id> still beats; launched N min before the gen bump` when the newest launch predates the bump. Measured reason DUPLICATE does not cover it: it needs two fresh ids, and between `bump` and the replacement's launch the old seat is the only (newest) launch, so `judge_alive` returned `ok` for it. Carry: dismissed: built in this diff
- Carry 3 (`loop-cwd` row): built. Lsof prints `(deleted)` after a removed cwd on Linux; the row strips it before `stat`, so arm (b) recreated-at-same-path is decided by the inode alone. Carry: dismissed: built in this diff
- Carry 4 (retire the session-local opener stand-in under `beatd.py`): nothing tracked to retire; the opener row is `beat_jobs.py` `opener` and the `opener` entry of `beatd.jobs.json`, and `beatd.py` names no stand-in. Carry: dismissed: implemented at ba544faa2dd25b75b0129879112d6409affe9662
- A `HPO_SEAT_GEN` value is `<seat>=<gen>`; the orchestrator's seat prompts must carry it after `seat_gen.py bump <seat>`. The `seat_gen.py` docstring and its instruments entry state it. Carry: dismissed: documented in the instrument, no later stage is narrowed

- Carry 5, Carry 6 and Carry 7: marked `[moved: R10-HOTFIX-OPENER-UNBLOCK]` on the roster, not answered here. Carry: dismissed: moved to R10-HOTFIX-OPENER-UNBLOCK on the roster (open #3484), not later parts of this group
- Carry 10 (harness-stale, the card carry 8 of this group's earlier roster restates): built. M-exact and M-body plant in `topic_grammar.py` and run; at the merged head `python3 -I dev/audit/harnesses/r10_open_driver_mutants.py` prints `RESULT mutants=24` and `RESULT survived=0`. Carry: dismissed: built in this diff
- Carry 9 (P603 opener live tip, `open_driver.py`): taken out of this branch; the same card is carry 7, which #3484 holds. Carry: dismissed: owned by #3484

## Friction

- policy-loop: stale: `agreement_py` restore list is hand-written, and importing `seat_gen` from `merge_train.py` and `roster_queue.py` put two files in its closure; `agreement_py.py --restore` named them, so the fix was cheap. Carry: dismissed: the detector already ran in prepr
- selftest_wiring: contradiction: a selftest module that spells the self-test flag in text is predicted unwired; avoided by not spelling it, as `open_driver_selftest.py` does. Carry: dismissed: existing convention
