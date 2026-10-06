Fix review: blocked ec401ab3a7aa25c17f04c15acaa8c49a6c1fae7a conflict: README.md, custom_components/heatpump_optimizer/strings.json, translations/en.json, translations/sv.json, docs/architecture.md, tests/deployment_shape.py, tools/audit/round4/D6/claims.md and claims.py conflict with origin/main 00da22db537a688efe6a7a9518a9fc91767c3a5a

bus-nonce: 890e31b4531ef263d24f085fb3d5d499

Round 3. Measured detached at ec401ab3a7aa25c17f04c15acaa8c49a6c1fae7a. Parents 33f6e8edfbee922929a61d7bbd3f665e52f624d8 and bab72287a6460a6f4246a7c5857792f248dc9d9f. The body names this head. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/` is empty. The three-dot diff does not touch `VERSION`, the manifest version, or the `RELEASE_NOTES.md` heading. Claim files are unchanged from 50a36f792eb32913607bc003408c4b6661e41a73.

## Closures

`tests/derive_closures.sh` records `tests/debug_collect.py` at line 174, after `tests/guard_pins.py` at line 169 and before `tests/finite_boundary.py` at line 182. `tests/run.sh` runs it in that same order, lines 484, 488 and 493. `tests/closure.py` does not name the script in `NOT_A_TEST`, `DRIVEN_BY_OTHERS` or `SLOW_GATED`.

`tests/closures.json` records it: 81 files, the same list and order as at 50a36f792eb32913607bc003408c4b6661e41a73 and at 33f6e8edfbee922929a61d7bbd3f665e52f624d8, `rc` 0. The recorded `seconds` are 2.2 here and 0.6 at 50a36f79. bab72287 and origin/main 00da22db have no entry (31 scripts; this head has 32).

`git merge-tree --write-tree 33f6e8edfbee922929a61d7bbd3f665e52f624d8 bab72287a6460a6f4246a7c5857792f248dc9d9f` exits 0. Its tree `8188575b7da54750a0ee7a9e4eee2c5d57aabc7d` equals this commit's tree. stderr: `LEDGER-MERGE: resolved tests/closures.json`, `closures.tests/doc_claims.py: merged as a set (141 entries)`.

RESULT derive_lane=debug_collect.py after guard_pins.py count
RESULT closure_files=81 count
RESULT closure_rc=0 count
RESULT closure_list_equal_50a3=1 count

## Conflict

`git merge-tree --write-tree origin/main ec401ab3a7aa25c17f04c15acaa8c49a6c1fae7a` exits 1. Content conflicts: `README.md`, `custom_components/heatpump_optimizer/strings.json`, `custom_components/heatpump_optimizer/translations/en.json`, `custom_components/heatpump_optimizer/translations/sv.json`, `docs/architecture.md`, `tests/deployment_shape.py`, `tools/audit/round4/D6/claims.md`, `tools/audit/round4/D6/claims.py`. stderr resolves `tests/structure_budgets.json` and `tests/closures.json` (`LEDGER-MERGE: resolved`) and has no `MERGE-CLAIM` line. The commit's check-runs total is 0 and the combined status is pending. The pull request head at measurement was this SHA.

evidence: /Users/timmalmstrom/hpo-seats/r9-dbg-1-review-ec40/evidence
