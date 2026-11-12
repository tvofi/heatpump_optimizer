R10-SEAT-IDENTITY-P5 (part 1 of 1: carries 0-4, 8, 9). One writer per standing seat (generation token) and per orchestrator session (session lock), the `loop-cwd` beat row, the opener's live-tip rule, and the mutant harness made runnable again. Functions touched in the shared seams: `beat_jobs.py` `loop_cwd` (new) and the `ROWS`/`RUN` tables; `beatd.jobs.json` one entry; `sweep_template.md` the Placeholders row `loop_cwd_patterns`, one sentence in (5b) and one in step (0); `roster_queue.py` `run_queue`; `merge_train.py` `train_add`; `bus.sh` `dispatch`; `handover_prompt.py` Resume steps. No edit to `beatd.py`.

## Head

b18d78b5070ca6fc27f8a865240e295a544c18c2

## Mutation proof

Each plant is one site in `seat_gen.py` or `beat_jobs.py` or `open_driver.py`; the named check goes red, the unmutated control is green.
- `seat_gen.py --self-test`: `held > gen` to `>=` reddens "check null: the current generation passes"; to `<` reddens "check: a lower generation is SUPERSEDED, exit 1"; dropping the command match reddens "lock null: a reused pid naming another command is taken over"; dropping `held != mine` reddens "lock null: the session's own pid is not a duplicate"; dropping the ancestor command test reddens "session_pid: the first ancestor running the session binary, never the shell". 5 of 5 killed.
- `beat_jobs.py --self-test`: comparing only that the path resolves (`if now is None`) reddens "loop-cwd: a directory recreated at the same path writes DEAD"; treating an empty `lsof` as DEAD reddens "loop-cwd: an lsof that returns nothing is UNREADABLE, never DEAD".
- `dev/audit/harnesses/r10_open_driver_mutants.py`: M-livetip (no rebind to the live tip) and M-gone-tip (no `SKIP moved` for a gone ref) are killed; `survived=0`.

## Null control

- Generation: the current generation, a generation ahead of the file and a seat with no file all exit 0; unset `HPO_SEAT_GEN` leaves each wired writer (`run_queue`, `dispatch`, `train_add`) writing as before (self-test cases in `roster_queue.py`, `bus.sh`, `merge_train.py`: superseded writes nothing, generation 2 writes).
- Lock: a dead holder pid and a reused pid naming another command are both taken over; the session's own pid is not a duplicate.
- `loop-cwd`: a live directory writes nothing (real child process); a process absent from `pgrep` is no line; a lacking overlay key prints UNREADABLE.
- Opener: a board line at A with a clean live tip B opens at B; a line whose handoff ref is gone still prints `SKIP moved`; a live tip already on main is `SKIP landed`.
- Harness null: the unmutated copy prints `failed=0`.

## Figures

- `python3 -I tools/audit/seat/seat_gen.py --self-test`: instrument `seat_gen.py`, prints its check count and `0 failed`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: 0 failed.
- `python3 -I tools/audit/seat/open_driver.py --self-test`: 0 failed.
- `python3 dev/audit/harnesses/r10_open_driver_mutants.py`: `survived=0`; at the merge base it aborted `ABORT M-exact: pattern occurs 0 times` (carry 8).
- `python3 tools/pr/ci_predict.py --base ba544faa2dd25b75b0129879112d6409affe9662`: no red predicted at the head.
- Writers wired, measured at the merge base by `git grep -n -E "def (run_queue|train_add)|dispatch\(\)" -- tools/audit/seat`: exactly `run_queue`, `train_add`, `dispatch`; `queue_pre_flight.py`'s `run_queue` is an unrelated function and is not wired.

## Red checks

none

## Forward-carry

- Carries 0, 1 and 2 (generation token, session lock, their fold): built here; the `lock` step is named in `handover_prompt.py` Resume steps and `sweep_template.md` step (0). The planted `DUPLICATE seat` case already exists in `pulse.py` (two fresh ids), so no code was added there. Carry: dismissed: built in this diff
- Carry 3 (`loop-cwd` row): built. Lsof prints `(deleted)` after a removed cwd on Linux; the row strips it before `stat`, so arm (b) recreated-at-same-path is decided by the inode alone. Carry: dismissed: built in this diff
- Carry 4 (retire the session-local opener stand-in under `beatd.py`): nothing tracked to retire; the opener row is `beat_jobs.py` `opener` and the `opener` entry of `beatd.jobs.json`, and `beatd.py` names no stand-in. Carry: dismissed: implemented at ba544faa2dd25b75b0129879112d6409affe9662
- A `HPO_SEAT_GEN` value is `<seat>=<gen>`; the orchestrator's seat prompts must carry it after `seat_gen.py bump <seat>`. The `seat_gen.py` docstring and its instruments entry state it. Carry: dismissed: documented in the instrument, no later stage is narrowed

## Friction

- policy-loop: stale: `agreement_py` restore list is hand-written, and importing `seat_gen` from `merge_train.py` and `roster_queue.py` put two files in its closure; `agreement_py.py --restore` named them, so the fix was cheap. Carry: dismissed: the detector already ran in prepr
- selftest_wiring: contradiction: a selftest module that spells the self-test flag in text is predicted unwired; avoided by not spelling it, as `open_driver_selftest.py` does. Carry: dismissed: existing convention
