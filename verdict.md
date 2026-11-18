Fix review: blocked 478e2ab92c36b309c73e8cc29903671434f73375 mutation-vacuous: coordinator.py room-history cycle step (deleted; outdoor argument swapped for floor return; space/dhw kW swapped), __init__.py unload flush deleted, room_history.py _accumulate problem-reading guard, dhw exclusion, target last-reading, _close_period power mean, _step_pairs/_room_verdict null-call filter, _times grid check, _house_line space filter, room_record.report_of cache key

bus-nonce: f9d2cfe3ea61b6cba7a183ae91ab9081

Round 1 (first review of #3711; no earlier reviewed head).

## Block

The new feature's production behaviour is not pinned at the points a reader of this report depends on most. Mutants applied one at a time at the head (driver `ev/mut_driver.py`, output `ev/mutants.txt`); every one below leaves the PR's block `ALL 40 FEATURES BLOCK PASSED` (rc 0):

- `coordinator.py` cycle step: the call to `room_record.async_note_cycle` made a no-op; `ctx._current_state.outdoor_temperature` replaced by `self._floor_return_temp` (the fit's regressor fed the wrong sensor); `power` and `dhw_power` swapped. The outdoor swap also survives the full `tests/features.py` (`ALL 5940 FEATURE CHECKS PASSED`, rc 0, 957 s) and `tests/entities.py` (rc 0, 603 s): `ev/mut_coord_swap*.txt`. Step deleted together with the unload flush: `tests/features.py` rc 0; `tests/entities.py` rc 1 only on `main() passes the committed table at its own recorded count (the null control)`, the CI-ratchet's recorded-count line, not a room-history check (`ev/mut_unload_step*`). The extractor read of the block confirms no check runs `_async_update_data` or `async_unload_entry`: the block drives `room_record.async_note_cycle` directly, so the coordinator's arguments are never exercised.
- `__init__.py` unload flush deleted (the design's verdict item v3a): survives, as above.
- `room_history._accumulate`: `reading.problem is None and` dropped (a reading with a problem counts toward the calling share); `and house.dhw_kw <= 0.0` dropped (hot-water cycles count as space heating); target kept from the first reading instead of the last. No block check feeds a problem reading or a non-zero `dhw_kw`.
- `room_history._close_period`: power as the period's last sample instead of its mean: no check asserts the mean.
- `room_history._room_verdict`: the `columns["call"][i] is not None` pair filter dropped (a NaN share then reaches `lstsq`).
- `room_history._times`: the `b % PERIOD_MIN` off-grid refusal dropped.
- `room_history._house_line`: the `s >= CALLING_SHARE` space-heating filter dropped.
- `room_record.report_of`: cache key reduced to the row count (the report goes stale once the ring is full at `HISTORY_LENGTH` rows).

These are not the ratchet's generated operators, so the CI pin runs and the body's `## Mutation proof` could not have shown them; the body's own `## Unpinned sites` already concedes the cycle step and unload flush are "wiring the features block does not drive". Owed: checks that drive the coordinator's cycle with a room list and assert the house columns it writes (outdoor, return, power mean, space share with a hot-water step), the unload flush through `async_unload_entry`, a problem reading and a reading without `calling`, an off-grid stored time, and a full-ring report refresh; each shown failing on its mutant above.

Killed by the block (the null control for the driver): first->last temperature reading, the note floor's `+ 1`, the pair gap, the per-hour rate, the ring length, a bad house cell emptying the ring, no load before note, flush ignoring `unsaved`, persist never resetting `unsaved`, the diagnostics key published unconditionally (`ev/mutants.txt`).

## Notes

- Note: body-figure: `## Unpinned sites` lists `coordinator.py:6124 STMT_DEL`, `:6125 CONST_SWAP` and `__init__.py:429 STMT_DEL` as "SURVIVED ... pinned by mutation-autofix"; the autofix pins killed mutants only, and the review measured these survive the block and the full `tests/features.py`. Carry: dismissed: settled by the re-cut this block requires on this pull request

## Evidence

- Head reviewed: `478e2ab92c36b309c73e8cc29903671434f73375` (`ev/HEAD.txt`), the head the body names.
- `git merge-tree --write-tree origin/main <head>`: rc 0, no conflict (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and `tests/structure_budgets.json`: no change in the three-dot diff.
- Block baseline at the head: `ALL 40 FEATURES BLOCK PASSED` (`ev/block_baseline_tail.txt`), as the body states.
- `tests/entities.py` `ALL 2731 ENTITY CHECKS PASSED` (613 s) and `tests/finite_boundary.py` `ALL 115 FINITE BOUNDARY CHECKS PASSED` (103 s) at the head, as the body states (`ev/baseline_entities_finite.txt`).
- CI: `merge_train.py classify` still `WAIT ... pending: gate red: none` at the last read (`ev/classify_last.txt`, rc 3); not awaited further because this verdict blocks on tests, which CI cannot change. Gate scope, golden drift, structure, archscore and the mutation lane are not re-run here (CI's heavy runs are cited, not repeated).
- Finder's harness: none, as the body states (#3616 is an outside report); the mutants here are the reviewer's own instrument.
- Coordinator wiring read by a `frugal:extractor` subagent over `tests/features.py`'s block (lines 96884-97347): no `_async_update_data`, `async_refresh` or `async_unload_entry`; every `House` has `dhw_kw = 0.0`; no `RoomReading` has `problem` set.

## Friction

none
