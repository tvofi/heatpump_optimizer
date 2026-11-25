Fix review: merge c6a3da6510a6fc5c01e573672699ee9f00c7b621

bus-nonce: 88ba6ef6e1ff600ff5beafdb3468aa13
pending-ci: gate

Round: later, a resolution delta over the reviewed head fe6676d8e461569d5924aaea4b26f3f86af85c1c (verdict `merge`). Scope: the packet's `## Review scope: delta`. The delta is `9673fea60b` (ci: pin killed mutants, 3 ledger files), `581a69edc9` (merges `ea88e99baa`, the merge of main `f52e700df1` that was resolved by hand), `615c5eccb5` (update_pr merges main `bb6377b4da`) and `c6a3da6510` (update_pr merges main `d3d66c4040`). The review widens to one already-reviewed production line, `boost.py` `_restore_settle`, because the resolution rewrote it. That line is the only place the PR's own production diff changed.

## Evidence

- Recomputing each merge settles what was resolved by hand. `git merge-tree --write-tree` with the repository's merge drivers gives a tree equal to the committed one for each of `581a69edc9`, `615c5eccb5` and `c6a3da6510` (an empty diff in all three). `git show --remerge-diff ea88e99baa` shows exactly two hand resolutions (`ev/remerge-ea88e99b.txt`):
  - In `boost.py` `_restore_settle`, the conflict was between the branch's `... and 0.0 <= hours < math.inf` followed by `and held.space_boosted is not None else None)` and main's `and admitted("boost", {"space_settle": {"boosted_h": hours}}) else None)`. The resolution keeps both: main's `admitted(...)` gate, then the branch's `and held.space_boosted is not None`. This matches the orchestrator's description.
  - The branch had renamed pin `_restore_settle.CMP_BOUND.81c29603` to `d165bc24`, and main deleted it (rename/delete). The resolution takes the deletion. That is correct: the pin's `old` line (`0.0 <= hours < math.inf`) no longer exists at the head, so the pin would be stale.
- The PR's own production diff, compared on its +/- lines (`git diff 9276ddf6b1 fe6676d -- custom_components` against `git diff d3d66c4040 c6a3da6 -- custom_components`), has 48 lines at each head. It differs in exactly one line pair, the `_restore_settle` line above, now rebased onto main's `admitted(...)` line (`ev/prod-diff-fe6676d-vs-head.txt`). `boost.py` still uses `math` (`settle_tail`'s `math.log`), so the import is not orphaned.
- Both sides' rules are pinned at the head. Each mutant ran in its own worktree under `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - head: `ALL 6172 FEATURE CHECKS PASSED` (`ev/features_head.tail.txt`). This includes `a persisted tail restored after the boost mode keeps its boosted sum unknown` and main's `D1-s2-06` boosted-sum check.
  - M1 drops the branch rule `and held.space_boosted is not None`. It FAILs `a persisted tail restored after the boost mode keeps its boosted sum unknown` with `'boost': (NOW, timedelta(seconds=1800))`, and prints `1 of 6172 FEATURE CHECKS FAILED` (`ev/M1.diff`, `ev/features_M1.tail.txt`). This is the check and reading the body names for this line.
  - M2 drops main's `admitted("boost", ...)` gate. The run raises `ValueError: cannot convert float NaN to integer` in `_restore_settle` from the boosted-hours sweep `(-1.0, nan, inf, True, 0.0, 0.5)` at `tests/features.py:87202`, rc=1 (`ev/M2.diff`, `ev/features_M2.tail.txt`).
- The `tests/structure_budgets.json` ledger merges were re-derived by hand.
  - `615c5eccb5`: driver line `17298 + both deltas = 17295`.
  - `c6a3da6510`: from base `bb6377b4da` (17297, 7841), the branch side `615c5ecc` (17295, 7839) and main `d3d66c4040` (17290, 7834):
    - `class_excess_loc` 17297 - 2 - 7 = 17288
    - `max_class_loc` 7841 - 2 - 7 = 7832
  - `python3 tests/structure.py` at the head measures `class_excess_loc=17288` and `max_class_loc=7832`, each at its cap, and prints `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
  - Both values are below main's (17290, 7834), so this is no budget raise.
- REKEY: the `c6a3da6510` merge equals the automatic merge with the repository's drivers. The ledger files it carries against `d3d66c4040` are the PR's pins:
  - `BoostState.note_mode.GUARD_OFF.0133a292`
  - `_mode_live.RETURN_DEL.166875c9` (renamed)
  - `_effective_cycling_cost.GUARD_OFF.048e8dfd`
  - `_floor_widening.BOOLOP.62655886`
  - `diagnostics_state.RETURN_DEL.5978d02d`

  The `tests / mutation` job is CI's check of them.
- `9673fea60b` adds three `killed_by` ledger files. These are `mutation-autofix`'s pins for the three ADDED UNPINNED sites named in the previous verdict's evidence (`boost.py` `_mode_live` RETURN_DEL, `coordinator.py` `diagnostics_state` RETURN_DEL, `_effective_cycling_cost` GUARD_OFF).
- Merge with main: `git merge-tree --write-tree origin/main c6a3da6` exits 0 against origin/main `0e1eba2b4a` (`ev/merge-tree.txt`).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files: untouched by the delta's own commit `9673fea60b`, and the merges are automatic except as described above.
- The previous verdict's one finding, the `## Head` body paperwork, is resolved: the section now names one code head (`ea88e99baa`) and one main merge.
- CI: `merge_train.py classify c6a3da6 --pr 3873` printed `WAIT ... pending: gate red: none` from 14:17Z through 14:50Z. A single exit 2 at 14:39Z (`REFUSE ci: the check runs at c6a3da6510a6 could not be read`) was transient; the next poll read WAIT again (`ev/classify.log`). No red was seen at this head. The verdict is returned with `pending-ci: gate` for the relay.

## Findings

- The body's `## Unpinned sites` bullet for `boost.py:627 CMP_BOUND*2` describes `0.0 <= hours < math.inf` as "unchanged and only reflowed". At this head, main's `admitted("boost", ...)` replaces that condition and pin `81c29603`/`d165bc24` is deleted. The `## Head` section also says the resolution inside the code head "is described below", but the body does not describe the `boost.py` resolution. This is paperwork, not a block: both rules are pinned (M1, M2 above). Carry: dismissed: body paperwork; the next body render at a moved head rewrites these sections
