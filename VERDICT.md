Fix review: merge ed39d3ae193c209dfb5d9808d2b8dc07890c1e63

bus-nonce: c350071e41613ac6e57410129c11cb18
pending-ci: gate

Carry re-review of the earlier merge draft at dc727c4d8fbf98a3fe9ef93feb16c428912eb78b (probe/rev-3511-bcf93034, "Fix review: merge dc727c4d...", itself pending-ci: gate). That draft stands in full at this head, including its Evidence and its P7 finding with its Carry.

## Evidence

- RESULT `review_carry.py dc727c4d8fbf98a3fe9ef93feb16c428912eb78b ed39d3ae193c209dfb5d9808d2b8dc07890c1e63` prints CARRY (`ev/carry.txt`). Two branch-only commits since the draft: 85f677041 "ci: pin killed mutants" and the merge ed39d3ae1 of origin/main.
- RESULT 85f677041 touches only tests/mutation_ledger/killed_by/optimizer.py/ pin files (`ev/pin_commit_paths.txt`); no production, test-script or policy file. It pins killed mutants for _held_unreachable and _thermostat_held_state, which the draft's mutation proof showed killed.
- RESULT the branch's own patch is otherwise unchanged: every file in the delta dc727c4d8fbf98a3fe9ef93feb16c428912eb78b..ed39d3ae193c209dfb5d9808d2b8dc07890c1e63 that main did not also change is a mutation-ledger pin.
- RESULT the merge of main equals `git merge-tree --write-tree 85f677041 4aa9868946` byte for byte (empty tree diff, `ev/tree_vs_driver_merge.txt`); that merge reports "LEDGER-MERGE: resolved tests/closures.json", so closures.json was resolved only by the ledger merge driver, with no hand edit.
- RESULT `git merge-tree --write-tree origin/main ed39d3ae193c209dfb5d9808d2b8dc07890c1e63` exits 0 (`ev/merge_tree.txt`).
- CI at this head: `merge_train.py classify` prints "WAIT ed39d3ae193c209dfb5d9808d2b8dc07890c1e63 pending: gate red: none" (`ev/classify.txt`); nothing at this head is red. Per the brief CI was not waited on, so this returns pending-ci: gate.
- Not re-derived: the draft's figures (census, harness residuals, mutation proof, structure and entities runs) were measured at dc727c4d and are carried, not re-run; the delta adds no production code of the branch's own.

## Findings

- P7, carried unchanged from the earlier draft: replacing the step-0 humidity read with `humidity = None` passes the group's block yet moves the held state under a learned humid defrost derate; the defrost bound is unpinned. Owed: a capacity row with a learned humid derate and a humidity series, run failing-first against this mutant. Carry: R10-SAV-VALUATION-RESIDUE
