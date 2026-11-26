Fix review: merge a00b84084857e2c39a93f67b30443975d096c740

bus-nonce: 2d7522b4e81b70dcf786f5fd1771808b
pending-ci: gate

## Scope

Delta re-review. The previous verdict was `merge` at 498708251b6d122add9aae8ae8542afe27bef5ba (probe/rev-3863-a0f438d8). This review covers `git diff 498708251b a00b8408`, which contains only main merges and their resolutions. The packet's `## Review scope` line reads `full` because the dispatch renders it with `--reviewed-head` set to this head. The brief scopes this review to the delta. No production delta widens it.

## Evidence

- Production lines are unchanged. The PR's own diff against its merge base was taken at each head: `git diff $(merge-base origin/main 498708251b) 498708251b -- custom_components/` (base d3d66c4040) and the same for a00b8408 (base 3ee06864da). Their `+`/`-` lines are identical (`PROD_PM_IDENTICAL`; ev/prod_old.diff and ev/prod_new.diff, 351 lines each). Both heads touch the same 39 files (ev/old_files, ev/new_files). The production files that 537e45b787's combined diff names (coordinator.py, dhw_planner.py, thermal_model.py) are therefore resolved to the PR's own patch.
- The resolution in tests/deployment_shape.py is the union. Against main 3ee06864da it keeps main's history clauses: R11-SEAM-entity-service's services.yaml, 184 and 180 before it landed, and 182 before flow_limit.py. It also keeps the branch's clauses: dhw_start.py and 122 until #3848's dhw_start.py (ev/ds_vs_main.diff).
- Every count was re-derived independently (ev/derive.py, a Jaccard predicate written from entities.py's `_d308_pairs` description, not imported). ev/derive.txt holds the results:
  - Merged head a00b8408: 184 of 561 pairs at >= 0.80, 435 comparable, 123 package files, 104 modules, 36 at module level plus one in a function. That gives 67 HA-free modules.
  - Branch side 99511c75f8 reads 186 and main side dbdc520e86 reads 182, as the note states. 537e45b787 reads 184. The previous head 498708251b reads 184 (103 modules, 66 HA-free).
- docs/architecture.md at the head reads "104 modules" and "The other 67 modules", which matches the derivation.
- Local runs at the head: `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py` gives `ALL DEPLOYMENT SHAPE CHECKS PASSED` (ev/deployment_shape.txt). `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- The body's `## Head` figures were checked at this head and agree with the tree: 184 of 561, 435 comparable, 123 files, 104 modules, 67 HA-free.
- `git merge-tree --write-tree origin/main a00b8408` reports no conflict (ev/mergetree.txt).
- No mutation run is owed. The delta moves no production line, so the earlier proof (M1, M9 killed; M8 equivalent and removed) carries.
- Merge-order note: #3838 and #3835 also claim module count 67. Whichever lands second must re-derive the count in docs/architecture.md and the #1218 pair note on its main merge. entities.py and doc_claims.py derive both from the tree, so a stale count goes red on that PR's own CI and cannot merge silently.
- CI: `merge_train.py classify a00b84084857e2c39a93f67b30443975d096c740 --pr 3863` printed `WAIT a00b84084857e2c39a93f67b30443975d096c740 pending: gate red: none` (rc=3) on every run from 02:56 to about 03:30 UTC, more than 30 minutes, with no red. The relay posts this verdict once gate is green at this head (ev/classify.txt).
- seat_comms: the heartbeat loop was stopped at the 30-minute background limit. It was restarted and stopped again at exit. The inbox carried no command.

## Findings

- Note: stale-body: the body's intro bullets and the earlier "Merge of main" paragraph still read 103 modules, 66 HA-free, 122 package files and "102 modules less the 37". `## Head` reads the current 104, 67, 123 and 184 of 561, and those agree with the tree. The stale lines are paperwork, not a block. Carry: dismissed: PR-body paperwork, settled by editing the body before the merge, nothing owed after it
