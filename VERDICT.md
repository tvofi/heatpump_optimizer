Fix review: merge 1fd2d7a67e522d49798b5a04e49f615767454b21

bus-nonce: 58706691c8247c76ac263b913f77b689

## Scope

Round: delta review over the merge verdict at e3d8f5c660f77417d2fcde114620a387a62f5a66 (fix-review.md step 12). The delta is merges only: 29219502 and 1908a835 merge origin/main, and 7ea71069 and 1fd2d7a6 merge those into the branch. There is no new branch commit. The previous verdict had no block. Its one note, ci-state, is resolved: classify now reads GREEN. The delta writes no production code of this PR's own, so the review is not widened.

## Evidence

- RESULT merges: 7ea71069 and 1fd2d7a6 have the same tree as `git merge-tree --write-tree` of their parents. 1908a835 differs only in tests/structure_budgets.json, which the ledger driver resolved (`LEDGER-MERGE: resolved`). 29219502 was hand-resolved in dev/audit/config/scopes.json only. It takes main's s7 `tests/fe*` (7df39f34) over the branch's `tests/features.py` (ev/merges.txt).
- RESULT net PR diff: comparing 7194ff84..e3d8f5c6 with e8485652..1fd2d7a6 file by file, every production file and test file is byte-identical in its +/- lines. Only two files differ. scopes.json has left the PR's diff (it is main's at the head). structure_budgets.json still lowers module_excess_loc by 8, now 21627 to 21619 (ev/netdiff.txt).
- RESULT scopes.json: `tools/audit/check_scopes.py --repo .` rc=0 at the head, unclassified=0. Main's re-cut clears the ledger cap that a268a50d had worked around (ev/check_scopes.txt).
- RESULT structure: `PYTHONPATH=tests/hastub python3 tests/structure.py` rc=0, `module_excess_loc 21619 <= 21619` (ev/structure.txt).
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` rc=0 against origin/main 9ffb388f. closures.json is resolved by its driver (ev/merge_tree.txt).
- RESULT CI, live: gate 140527192776 succeeded at this head. `merge_train.py classify --pr 3870` prints `GREEN ... pending: none red: none` (ev/classify.txt). nightly-ha (stable, 2025.2.0) and nightly-status are red. They are not required checks.
