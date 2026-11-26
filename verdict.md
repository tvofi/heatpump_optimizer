Fix review: merge 8ec4351288a069c784e7cfa6996b8e1c56c417f6

bus-nonce: 23372d03c20a033cf3f591023196a5ed

Round: delta review over the merge verdict at 2003bbb48cc1b0d70edf0a39b2264aa4c9a533b4 (`git diff 2003bbb4 8ec43512`, a merge of origin/main 8f22a3b2, #3838 ROOMS-3B and #3906). `review_carry.py` prints FRESH-REVIEW, because 42c278fe is a hand resolution and not the automatic merge of its parents.

## Evidence

- RESULT fix_unchanged=yes: I compared the PR's net contribution before and after the merge, from merge-base d9100de7 to 2003bbb4 and from merge-base 8f22a3b2 to 8ec43512. Both touch the same 124 files. Only six differ in their contribution, all of them count-bearing: dev/audit/rounds/round4/D6/claims.{py,json,md}, docs/architecture.md, tests/deployment_shape.py and tests/structure_budgets.json. No file under custom_components/ and no test or harness the fix added differs, and the PR's own contribution to tests/closures.json is identical (ev/delta.txt).
- RESULT resolutions: c20643b8 and 8ec43512 each equal the automatic merge of their parents. 42c278fe differs from the automatic merge only in those five count files, where the automatic merge had conflicts in claims.py and deployment_shape.py. Each resolution keeps both sides: the provenance chains name both R11-OUTSIDE-ROOMS-3B's comfort_floor.py and R11-OUTSIDE-HONEST-DHW-RUNS's dhw_charges.py, and the architecture map lists dhw_charges.py beside main's entries (ev/count-files-vs-main.diff).
- RESULT closures_set_merge: every entry that main (8f22a3b2) or the PR side (2003bbb4) added to tests/closures.json over the shared base is still present at the head (0 lost).
- RESULT counts_rederived: I counted 105 modules in custom_components/heatpump_optimizer/*.py and 105 entries in the docs/architecture.md map, and 124 tracked package files, matching the lane closure size of 124. Re-deriving from closures.json at the head with entities.py's predicate gives 190 of 561 script pairs at Jaccard >= 0.80 (435 comparable), matching tests/deployment_shape.py. That script passes at the head: ALL DEPLOYMENT SHAPE CHECKS PASSED.
- RESULT budgets_rederived_down: tests/structure.py at the head prints STRUCTURE RATCHET PASSED, with every metric equal to its budget, so the budgets were re-measured, not carried (ev/structure.txt). Compared with main (8f22a3b2 and dbdc71fa), only methods_over_200 (7 to 6) and module_excess_loc (21753 to 21706) move, both downward. The drop of 47 equals the PR's drop before the merge (21763 to 21716). No key is raised.
- RESULT merges_with_main: `git merge-tree --write-tree origin/main 8ec43512` is clean against origin/main dbdc71fa; the ledger driver resolved tests/closures.json.
- RESULT ci: `merge_train.py classify 8ec43512 --pr 3805` printed `GREEN 8ec4351288a069c784e7cfa6996b8e1c56c417f6 pending: none red: none` (ev/classify.txt). There are no reds, so no `## Red checks` answer is owed.
- Prior findings: the verdict at 2003bbb4 was merge and carried no blocking finding. This delta reopens none and adds none.
- Not re-run locally: claims.py and tests/entities.py import homeassistant, which is not in this seat's venv-ci. CI's GREEN at this head covers them. The figures they assert (105 / 124 / 190) I re-derived independently above.

## Friction

- review_packet.py render refused with `UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r11-roster`. b2ce461c is a body-item hash in dev/programme/rosters/wave-r11-groups.json, not a commit, so the packet treats an item id as a SHA. I did the delta review by hand from `git diff 2003bbb4 8ec43512`.
