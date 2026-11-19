Fix review: merge de84aa9bf9cc7a08b57436a8e952f7cafa73d657
Note: stale-body: the `## Head` section still lists three superseded heads (4050847db5, 8f34cd23e0, ef7d2e4038) under the current one; the first line names de84aa9bf9, which is the head measured
bus-nonce: 4c8f8154f2f2648609ab3f66887e361e
pending-ci: gate

## Evidence

Delta review (round 3 for this PR: full round 1 merged at e0769b570e; round 2 blocked at f50a75b4f7 on `module_excess_loc 21633 > 21571` after main's merge). The packet reads `Review scope: full` because no ref verdict names f50a75b4; I scoped it by the 2026-11-09 delta rule instead, and the PR's own diff justifies that: the three-dot diff at de84aa9bf9 equals the three-dot diff at the merge-verdicted e0769b570e on every path except `tests/structure_budgets.json` (`ev/delta.diff`). The diff is the one row `module_excess_loc` 21571 -> 21633 plus `recorded_at` -> b36742b17b, which is an ancestor of the head and is its merge base with main. The roles diff from the merge base to origin/main is empty.

- Prior finding resolved: `python3 tests/structure.py` at de84aa9bf9 prints `ok module_excess_loc 21633 <= 21633` and `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure-de84aa9bf9....txt`).
- Number re-derived (step 8), with my own definition: AST last-statement end line minus 2000, summed over the package's top-level `.py` modules at the head. It reads TOTAL 21633 (`ev/module-excess-rederive-....txt`; thermal_model.py 3069 is the largest term). It matches the recorded figure.
- Earned (step 14): the +62 is main's own module growth, which came in through the merge base b36742b17b. The PR's code is unchanged since the merge verdict. The row is new in this PR and absent on main, so recording it as measured is the only value it can take. The 2000 limit is the owner's 2026-11-18 ruling (RULINGS.md, "the module-span limit to 2000, both yes"). origin/main e83a2c919f has no `custom_components/` change against the head (`git diff --stat` is empty), so the row holds after the merge as well.
- Merge with main (step 13): `git merge-tree --write-tree origin/main de84aa9bf9` exits 0. No conflict.
- VERSION, the manifest and the notes heading are untouched; both claim files are byte-identical to the merge base (steps 4, 5).
- Body (step 7): `## Head` names de84aa9bf9cc7a08b57436a8e952f7cafa73d657 as the head (Note above).
- Live checks (step 11), read 16:13Z and again at render: `gate` failure. Its one red input is `budget-raise-gate / budget-raise-gate`, the owner-approval gate on this raise; that is APPROVAL-OWED and left to the orchestrator. Every other concluded check is success. `tests / arch-instrument`, `tests / closures`, `tests / coverage` and `tests / fast (3.14)` are still in flight. The carry audit at the head reads 0 items.

RESULT structure_ratchet=PASSED module_excess_loc=21633 budget=21633
RESULT module_excess_rederived=21633
RESULT own_diff_vs_merge_verdict=tests/structure_budgets.json only
RESULT merge_tree_rc=0
