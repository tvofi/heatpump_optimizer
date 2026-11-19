Fix review: merge 143c3767f9178089b7d56b6b1ca002118046a97c

bus-nonce: 475eaf0cc0f651ecbd106589ad72a865

Round 3, a delta review: `git diff aa98d2b6fbb55ba4a79a7fcd428d2b11ab0e8e30 143c3767f9178089b7d56b6b1ca002118046a97c`. The delta is one merge of origin/main (99436a082c) into the branch. It had two hand-resolved conflicts, in `docs/configuration.md` and `tests/features.py`. Everything else in the delta is main's own content, auto-merged.

## Prior findings

- The verdict at aa98d2b6 was `merge` with no open findings. I re-ran its 23 mutants with that verdict's own driver, re-pointed to this head (`ev/mut_driver.py`). Result: 23 KILLED, 0 SURVIVED, 0 NOAPPLY (`ev/mutants.txt`). `pairs keep null call` is killed by the same LinAlgError as in round 2.
- Null control: the no-op mutant leaves the block passing, rc 0 (`ev/null.txt`).

## Merge resolution

- **No production line was hand-edited.** `git show --remerge-diff HEAD` (`ev/remerge_diff.txt`) differs from the automatic merge only in the two conflicted files. `tests/closures.json` was resolved by the LEDGER-MERGE driver. The `custom_components/` changes in the delta are main's commits, merged without conflict.
- **`docs/configuration.md`.** At the merge base, the Room thermometers row is identical to main's, so only the PR changed it. The Let-a-cold-room row is identical to the PR's, so only main changed it. The head carries the PR's thermometers row and main's lift row, byte-identical to each side (row hashes in `ev/doc_rows.txt`). That keeps both sides with nothing lost.
- **`tests/features.py`.** Main's plan-peak block and the PR's room-history block both appear verbatim at the head (`ev/features_sides.txt`). The plan-peak block comes first, the room-history block follows, and `sys.exit(R.close(...))` closes the file once. The file parses.

## Room-history block

- `features_block.py` run with the round-2 prelude: `ALL 47 FEATURES BLOCK PASSED`, rc 0 (`ev/block_baseline.txt`). Every prelude line is still verbatim in `tests/features.py` at the head.

## Notes

- Note: when this was written, CI at the head was still queued (`ev/checks.txt`). The verdict covers the code. The required checks still have to conclude before the merge.

## Evidence

- Head: `143c3767f9178089b7d56b6b1ca002118046a97c` (`ev/HEAD.txt`).
- `git merge-tree --write-tree origin/main <head>`: rc 0 (`ev/merge_tree.txt`).
- Finder's harness: none (#3616 is an outside report). The mutants are the reviewer's instrument from round 1.
