Fix review: merge e3d8f5c660f77417d2fcde114620a387a62f5a66

bus-nonce: 1e8e440d82b4d377635d35948934bd17

## Scope

Round: delta review over the merge verdict at 5f8e2cdb5fe2d236f71c62f8d41b31836df88107 (fix-review.md step 12). The delta is four merges of origin/main (up to 7194ff84) plus one branch commit, a268a50d (dev/audit/config/scopes.json). The three earlier blocked verdicts (9f133225 lifecycle-leak, ef876fec ci-red, 61e49d1d test-red) were already resolved by the merge verdicts at 2c1ab822, 1a0d1351 and 5f8e2cdb. The previous verdict had no open block. The only widening is the hand-resolved production hunk in diagnostics.py, named below.

## Evidence

- RESULT merges: f2fc22c3, a9c10725 and e3d8f5c6 have the same tree as `git merge-tree --write-tree` of their parents. ea0c7f82 and 6cc9ae92 differ only in files that the repository's ledger and claim merge drivers resolve. dce9bda8 was hand-resolved in custom_components/heatpump_optimizer/diagnostics.py only (ev/merges.txt).
- RESULT diagnostics.py: the resolution unions both sides. The import line carries both `boost` (main, #3862) and `fault_log` (this PR). `_VIEWS` keeps this PR's `fault_log` view and main's `external_heat_block_ignore` view, and no conflict marker is left. The fault_log view is byte-identical to the reviewed one. Risk named: losing the fault_log view or import in the resolution. It is not lost.
- RESULT net PR diff: comparing 8f22a3b2..5f8e2cdb with 7194ff84..e3d8f5c6 file by file, nine files' +/- lines differ (ev/netdiff.txt). The rest of the PR's own diff, including all other production files, is unchanged.
  - diagnostics.py: the union above.
  - scopes.json: a268a50d, below.
  - option_doc_coverage.py, claims.py, deployment_shape.py, docs/architecture.md, claims.md/json: main's FG-1 change (#3911) removed the text counts the branch had moved. At the head these files equal main's, or carry only the branch's non-count rows. Nothing the branch must carry is lost.
  - structure_budgets.json: the branch still lowers module_excess_loc by 8 (21646 to 21638).
- RESULT counts at the head: `claims.py` rc=0, claims_false=0, arch_modules_on_disk=107, arch_map_listed=107, ha_module_level_importers=37. `tests/structure.py` rc=0.
- RESULT scopes.json (a268a50d): `check_scopes.py --repo .` rc=0 at the head. Null control: with main 7194ff84's scopes.json at the same head it is rc=1, `FAIL D5 ... over ledger.max_units 4500: s7 holds 4509 units`. Narrowing s7 to tests/features.py is what clears it. The coverage line reads unclassified=0, so the rest of tests/f* stays covered (ev/check_scopes.txt).
- RESULT merge: `git merge-tree --write-tree origin/main e3d8f5c6` rc=0 against origin/main b4ebe3dc (ev/merge_tree.txt).
- RESULT CI, live: gate 140337653398 (CI code run 45936122730) succeeded at this head. Every required check is green except one: the CI edit run 45936123844's gate 140307136103 is red. Its log reads `FAIL run(s) [45936122730] at this head are still being judged; their gate decides`, so that red is a deferral to the code run's green gate, not a code or test red. `merge_train.py classify` prints `WAIT ... pending: gate red: none` (ev/classify.txt). nightly-ha (2025.2.0, stable) and nightly-status are red and not required.

Note: ci-state: the edit run's deferring gate 140307136103 is still listed red beside the code run's green gate, and classify reads WAIT. A gate re-run of 45936123844 should clear it. No code, test or harness in this PR causes it.
