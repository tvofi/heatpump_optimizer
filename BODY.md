Adopts outside pull request 3292 (contributor Bankaifan, fork head f20c98084b179c85d2c834adc4caf49dc05631d8): a configured input the cycle finds `missing_entity` or `unavailable` is re-read as soon as its entity reports a value, not one `optimization_interval` later. The contributor's four commits are kept with their authorship; their trailers naming an assistant session were dropped from the messages, and the contributor is credited by the Co-authored-by trailer below. The fork's `dev/programme/carries/carry-201.json` hunk is dropped (a programme record; the orchestrator rules it in or not). One added commit drops a stale mutation-ledger pin that the `has_value` helper made unreachable. Independent review: read from the merged tree; the design matches `away.watch_away_inputs` (debounced `async_request_refresh`), `inputs.py` imports no Home Assistant, the watch reads nothing itself so every guard applies, and release latches (#236).

Closes #3292 on merge (close it with thanks once this merges). Plan page link for the outside-intake ruling: owed on 3292 by the orchestrator.

Co-authored-by: Daniel <476059+Bankaifan@users.noreply.github.com>

## Head

c0cb5dcea9e242fbfd4e28f7316adb6f20067df3 (code head, cut from origin/main 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76; main had not moved at the last `tools/pr/prepr.sh` run, so no second run).

## Mutation proof

Mutant: the predicate line `self._input_returns.arm(reader.health)` in `_update_current_state` replaced by `pass`, `PYTHONPATH=tests/hastub python3 tests/features.py` run from a `git archive` copy. Red section checks: the read that found it absent watches exactly that entity; the entity reporting a value asks for one refresh; that refresh re-reads it; a return one second short of an interval; a return exactly one interval after; the in-flight precondition; the next report after a dropped request; a rejected returned value keeps learners frozen; an input read as unavailable is watched. (The `recorded_at` check also reads red in any archive copy: #1713, the runner's.) The fork's own mutant table (spacing guard, release latch, `has_value`, hold start) is the contributor's and was not re-run here.

## Null control

Unmutated head, same command, from the worktree: `ALL 4923 FEATURE CHECKS PASSED`. Mutant: `10 of 4923 FEATURE CHECKS FAILED`. Flat-price null control: not applicable (no cost figure).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, no budget re-recorded.
- `GATE_SCOPE=auto` gate: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`; its one failure was `tests/structure.py` on an uncommitted reformat of the constructor that was then reverted; structure passes at the head.
- `bash tools/pr/prepr.sh` at the head: `PRE-PR ... rc=0`.
- Unpinned sites listed by prepr step 6d (the mutation job pins the killed ones; a survivor is triaged by hand): the new sites in `InputReturnWatch`, `has_value` and `_track_states`.

## Red checks

none (the one predicted red, a stale ledger pin of the replaced `_begin` guard line, is repaired in this diff; cheaper detector already standing: `ci_predict` ledger arm).

## Forward-carry

none. (The fork's archscore-gap carry is dropped with the carry-201 hunk; the orchestrator decides whether to land it.)

## Friction

none
