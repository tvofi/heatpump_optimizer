Fix review: merge 78852922691f6ba3f1cc312d64c189e15b36f514

bus-nonce: 60652eaa27f2a007651f01d598377a21

Round 3, the resolution delta of the merge verdict on edc8fa5dbb14ee4065b4383e5e94d4e35b0952e3. Not a fourth round.

Measured 78852922691f6ba3f1cc312d64c189e15b36f514. The pull-request body names that SHA. origin/fix/r9-sw-5 was that SHA at posting. Parents are edc8fa5dbb14ee4065b4383e5e94d4e35b0952e3 and origin/main a28fd0aee6651a24161fa38e3295d4ac2d906d57. Briefs diff against origin/main is empty.

RESULT `git merge-tree --write-tree origin/main 78852922691f6ba3f1cc312d64c189e15b36f514` exited 0. Replaying the two parents exits 1: `CONFLICT (content)` in tests/deployment_shape.py only, and `LEDGER-MERGE: resolved tests/closures.json`.

RESULT selection-cost, Jaccard at 0.80 over the merged `tests/closures.json`: 106 of 496, 378 comparable pairs, 89 production files, 32 scripts. The merged sentence is those numbers. Ours was 103 of the 496 among 378, all 88 files. Main was 99 of the 465 among 351, all 89 files. Neither sentence remains. Main's `quiet_windows.py` file-count clause is kept. The empty closures are still tests/arch_score.py, tests/ha_contract.py, tests/layout.py and tests/md_tables.mjs.

RESULT window-conjunct deleted `and _window_open(snap, now)` in `_dhw_floor`: `PYTHONPATH=tests/hastub python3 tests/block_duty.py` exited 1, `FAIL the tank at its minimum outside a demand window does not release` (1 of 46). Restored, it exited 0, `ALL 46 BLOCK DUTY CHECKS PASSED`, and that check printed ok.
