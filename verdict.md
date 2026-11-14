Fix review: merge cc335482ae7c3cc9878f4fffdd59250b688325ff

bus-nonce: 821440c6983c8c43161cb026ae5a2c30

## Scope

Round 2, a delta round over reviewed head b3384f6f075e5896e7661c004769eea09393a149, whose verdict blocked on `store-roundtrip`: a one-row map record with an unread cell read back empty. Reviewed: `git diff b3384f6f07 cc335482ae` (`ev/delta.diff`: `draw_range._stored_map`, `draw_range._map_cell`, two checks in `tests/features.py`) and whether that finding is resolved. Nothing was widened. `_map_cell` has one caller, `_stored_map:267`, and `_stored_map` has one, `DrawRange.from_dict:551`. `as_dict:535` writes `map_rows` only when there are rows, and `_segment_row:188` always fills `start_min` and `steady_min` with ints. So no code reviewed earlier gets a new input it did not get before.

## Findings

None.

## Evidence

- Head: cc335482ae7c3cc9878f4fffdd59250b688325ff, measured in a detached worktree at that SHA, which is also the head the body's `## Head` names. No pull request exists yet, so there is no review packet, no CI run and no live check to read. The `## Red checks` answer cannot be checked against runs yet: no red exists. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs` among the required set.
- Prior finding resolved: the part A block at the head reads `ALL 31 FEATURES BLOCK PASSED` (`features_block.py` with a prelude emitted at the head, 41 statements). b3384f6f07's `draw_range.py` with the head's tests reads `2 of 31 FEATURES BLOCK FAILED`: "an unread cell is a stored value ..." and "an unread start or steady minute is a bad cell ...". That re-derives the body's round-2 figure.
- Hand mutants, all run through the same block command:
  - The NULL mutant survived (`ALL 31`).
  - KILLED: the round-1 reader restored (`if c else []`), which fails the one-row reload (`[]`).
  - KILLED: the empty-minute guard dropped, which is the GUARD_OFF equivalent.
  - KILLED: `MAP_COLUMNS[:3]`, which is the driver's CONST_SWAP and makes `written_c` required.
  - KILLED: `MAP_COLUMNS[:1]` (start only) and `MAP_COLUMNS[1:2]` (steady only).
  - KILLED: `if False:`.
  - KILLED: making `outdoor_c`, `drawn_spread_kw` or `band_high_kw` required (2 of 31 each).
  - KILLED: the STMT_DEL of the `split` line (rc 1).
  
  Together these cover every sibling of the rule. An empty cell reads as unread in every numeric column, because the round-trip fixture's `hold` row has all 13 such columns empty and the no-inlet runs cover `inlet_*`. An empty cell is a bad cell, dropping only its own row, in exactly `start_min` and `steady_min`. Each direction of breaking the rule fails a check.
- My diff-mode `mutant_run.py --diff b3384f6f07...HEAD --path custom_components --list` lists the same 3 mutants the body names (`:279 GUARD_OFF`, `:279 CONST_SWAP`, `:262 STMT_DEL`). My run of that driver printed nothing, so the hand mutants above stand in for it: they are the same three edits plus more.
- Merge with main: `git merge-tree --write-tree origin/main cc335482ae` at origin/main d7004eaa77 exits 0, with `LEDGER-MERGE: resolved tests/structure_budgets.json` (`ev/merge-tree.txt`).
- `VERSION`, the manifest version and the notes heading are untouched: the delta touches only `draw_range.py` and `tests/features.py`.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/ dev/governance/rules/ CLAUDE.md` prints nothing, so the contract I read is current.
- Not re-derived, because they are round-1 figures outside this delta and their review stands: the body's harness, structure, archscore and scoped-gate figures, which it marks as round 1.
