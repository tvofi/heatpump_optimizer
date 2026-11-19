Fix review: merge aa98d2b6fbb55ba4a79a7fcd428d2b11ab0e8e30

bus-nonce: a9213b23973f80e6c4e5e8c5ed4dea26

Round 2, a delta review: `git diff 478e2ab92c36b309c73e8cc29903671434f73375 aa98d2b6fbb55ba4a79a7fcd428d2b11ab0e8e30` (`ev/delta.diff`). It touches `coordinator.py` (one line), `tests/features.py` (+153) and four `killed_by` pins.

## Prior findings

- All twelve survivors from the blocked verdict at 478e2ab9 are killed at this head. I used that verdict's own driver (`ev/mut_driver.py`). The outdoor anchor was moved to the new production text, and I added one mutant that restores the cycle-start `ctx`. Results: 23 mutants, 23 KILLED, 0 SURVIVED, 0 NOAPPLY (`ev/mutants.txt`). Each one is killed by a FAIL line from the check written for it. That includes the coordinator mutants (step deleted, outdoor->return, space/dhw swap, cycle-start ctx), which fail on the new check that drives `_async_update_data`, and the unload-flush deletion, which fails on the check that drives `async_unload_entry`.
- Null control: the driver run with a no-op mutant leaves the block passing (`ev/null.txt`, rc 0). Baseline is `ALL 47 FEATURES BLOCK PASSED`, rc 0 (`ev/block_baseline.txt`).
- The block's new checks use fixtures defined elsewhere in `tests/features.py`, so I ran it standalone with a prelude (`ev/prelude.py`). I checked that every line of that prelude appears verbatim in `tests/features.py` at the head. Without the prelude, the baseline fails with a NameError (`ev/*_noprelude.txt`). That failure comes from the extraction instrument, not from the PR: CI runs the whole file.

## Production delta (widened to exactly this line)

- `coordinator.py:6123` now reads the room history's outdoor value through `_ctx_of(self)` instead of the `ctx` bound when the cycle started. `CoordinatorContext` is replaced on each state update (`coord._ctx = replace(self, _current_state=new)`, `ev/ctx_rebinds.txt`). That means the old `ctx` held the outdoor reading from before `_update_current_state`, one cycle stale. The change is correct, it matches the file's existing `_ctx_of(self)._current_state` reads, and a mutant that reverts it is killed.

## Notes

- Note: none.

## Evidence

- Head: `aa98d2b6fbb55ba4a79a7fcd428d2b11ab0e8e30` (`ev/HEAD.txt`), re-read before posting.
- `git merge-tree --write-tree origin/main <head>`: rc 0 (`ev/merge_tree.txt`).
- CI at the head: `gate` SUCCESS, `pr-contract` SUCCESS (05:13Z re-run after the body edit), `tests / mutation` SUCCESS (`ev/checks.txt`). `tests / nightly-status` is not required and is inherited from main; the body answers it.
- The four new `killed_by` pins are bot-recorded `--pin-killed` rows on `room_history.py` sites.
- Finder's harness: none (#3616 is an outside report). The mutants are the reviewer's instrument from round 1.

## Friction

- `features_block.py` cannot run a block that uses fixtures from earlier blocks unless it is given a hand-built prelude.
