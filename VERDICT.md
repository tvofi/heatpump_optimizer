Fix review: merge ed39d3ae193c209dfb5d9808d2b8dc07890c1e63

bus-nonce: c350071e41613ac6e57410129c11cb18

Carry re-review. The earlier draft is `Fix review: merge dc727c4d8fbf98a3fe9ef93feb16c428912eb78b` (ref probe/rev-3511-bcf93034, nonce bcf93034). It was never posted because an unrelated check was red; I re-issue it at this head.

## Evidence

- RESULT `review_carry.py dc727c4d8 ed39d3ae1` prints CARRY (`ev/carry.txt`). Two branch-only commits are new: a merge of origin/main and `85f677041 ci: pin killed mutants` (github-actions[bot]), which adds seven tests/mutation_ledger/killed_by/optimizer.py/*.json pins and nothing else.
- RESULT the branch's own patch is unchanged. The stable patch-id of the non-merge commits, excluding tests/mutation_ledger, is f6cf46c2ad51... at both dc727c4d8 and ed39d3ae193c209dfb5d9808d2b8dc07890c1e63. The file set differs only by those seven ledger pins.
- RESULT the merge of main resolved tests/closures.json only by the ledger merge driver: `git merge-tree --write-tree origin/main ed39d3ae193c209dfb5d9808d2b8dc07890c1e63` exits clean and prints `LEDGER-MERGE: resolved tests/closures.json`, so it merges with current main.
- RESULT CI at this head: `merge_train.py classify` prints `GREEN ed39d3ae193c209dfb5d9808d2b8dc07890c1e63 pending: none red: none`, rc 0 (`ev/classify.txt`).
- The draft's measurements (capacity seam closed, 560-case probe, census 1728/1728, mutation proof, harness figures) were taken at dc727c4d8 and are carried, not re-run; the delta touches no custom_components/ code.
- Red checks: none red, so none owed.

## Findings

- P7 (carried from the earlier draft): replacing the step-0 `humidity = None if weather.humidity is None else float(weather.humidity[0])` with `humidity = None` passes the group's block yet moves the held state with a learned humid defrost derate. The code at the head is right; the pin is missing. Owed: a capacity row with a learned humid derate and a humidity series, failing first against that mutant. Carry: R10-SAV-VALUATION-RESIDUE
- P8 (carried): the pump bound reading `need_kw` instead of `made` survives; measured effect is at most 0.03 kWh_th per step of charge, nothing drawn. Carry: dismissed: measured near-equivalent at default parameters, per the earlier draft
