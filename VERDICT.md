Fix review: merge 50a36f792eb32913607bc003408c4b6661e41a73

bus-nonce: 7f39b476f83be1470b617cb86e72ed28

Round 2, the resolution delta of the conflict block at 058a5f8018e87cb7861477c8e7382ba9c7daada8. Parents: 058a5f8018e87cb7861477c8e7382ba9c7daada8 and origin/main 1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872. The body names this head. Contract copy matches origin/main.

`git merge-tree --write-tree origin/main 50a36f792eb32913607bc003408c4b6661e41a73` exits 0. GitHub `mergeStateStatus` is BLOCKED; that is not DIRTY, and the merge-tree has no conflict and no `MERGE-CLAIM` line.

## Architecture and the D6 census

Read against both parents, not the diff. The first parent says 76 entities, 59 sensors, 5 buttons. origin/main says 76 entities, 60 sensors, 4 buttons. The merged mermaid says 77 entities, 60 sensors, 5 buttons. Main's sensor and this branch's finalize button are both present, as are `debugger.py`, 13 services, 71 modules and 27 module-level `homeassistant` imports.

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` exits 0.

RESULT claims_false=0 count
RESULT entities=77 count
RESULT sensors=60 count
RESULT buttons=5 count

## Claims

The bare claim list is `config_flow` only, byte-identical to the first parent. origin/main's five `coord_*` claims are not in it. The three-dot diff against origin/main does not touch those fixtures; it moves `tests/golden/config_flow.json`. `# may-drift:` lines: 19 on both parents and on this head.

RESULT claim_list=config_flow count
RESULT may_drift_lines=19 count

## Structure

`python3 tests/structure.py` exits 0. `max_class_loc` is 9048, one below origin/main's 9049 and the ledger sum of the two parents' deltas from 9068 (main 9049, the reviewed head 9067). `seam_cut_total` is 765, equal to origin/main. The cap is not raised.

RESULT max_class_loc=9048 count
RESULT seam_cut_total=765 count

## Checks

`pr-contract` is success on this head. `delivery-status` and `nightly-status` are failure, the same two the previous body answers; this diff does not change what `nightly-status` reads. `fast (3.14)`, `closures`, `coverage`, `mutation` and `Analyze (python)` were still in progress. The mutation table was not re-run.

evidence: /Users/timmalmstrom/hpo-seats/r9-dbg-1-review-50a3/evidence
