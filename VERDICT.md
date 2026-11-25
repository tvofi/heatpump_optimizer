Fix review: merge 2c1ab82218a2859fde885beb590db3a279651756

bus-nonce: eef32938f2c3f2e138147c17d89f083c
pending-ci: gate

## Scope

Delta re-review over the reviewed head 61e49d1d83ef45aa083f50a054493fa64227f615: `git diff 61e49d1d83 0e99fbe628` (tests/deployment_shape.py, docstring only; 2c1ab822 is that tree merged, with no other change). No production delta, so the review is not widened.

## Prior findings

- The block at 61e49d1d83 ("note says 180 of the 561 but the merged closures derive 182") is resolved. The note now reads `182 of the 561` and `all 182 among the 435`. The #1218 note predicate re-derived on tests/closures.json passes at 2c1ab822 and fails at 61e49d1d83 (`ev/d308_pairs.txt`).

## Findings

- None.

## Evidence

- Pair count, by `_d308_pairs`' predicate re-run (`ev/d308.py`, `ev/d308_pairs.txt`): 182 of 561 at >= 0.80, 435 comparable, 122 production files, at each of:
  - the PR head 2c1ab822;
  - the current PR head 106578f8;
  - 2c1ab822 merged with origin/main d3d66c4040 (merge-tree tree b1930789, whose tests/closures.json blob is the head's, 4bb6df85; main has not touched closures.json since base bb6377b4da).
- origin/main alone also derives 182, from 121 production files. Head and head+main agree, so there is no merge-time carry. The post-merge re-record on main, after #3864's production change, may still move the count. That cannot be measured here, and main's own gate checks it.
- Mutation: both of these fail the docstring check (`missing ['182 of the 561']`):
  - the prior note on the head's closures;
  - `182 -> 181`.
- The delta's added history is true (`ev/d308_pairs.txt`, `ev/jac.py`):
  - f0a1881e9d^1 (d7324bbc58) derives 180 and has no solve_gate.py.
  - f0a1881e9d^2 (main bb6377b4da) and the merge both derive 182; solve_gate.py is in 23 closures, among them env_drift.py's, golden.py's and manual_plan.py's.
  - env_drift.py/manual_plan.py and golden.py/manual_plan.py move from 95/119 = 0.798 to 96/120 = 0.800.
- Note: the clause "182 before ... fault_log.py ... from 0.800 to 0.792" is branch history that predates this delta and was not changed by it. At the head the two config_flow_steps.py pairs sit at 85/107 = 0.794, against main's 85/106 = 0.802. The clause is narrative only, and no test reads that figure.
- `git merge-tree --write-tree origin/main 2c1ab822` exits 0. The ledger driver resolves tests/structure_budgets.json (`ev/merge_tree.txt`).
- The PR head moved to 106578f8f0673be13407656476c7bba1b243db69 ("ci: merge main") after dispatch. `review_carry.py 2c1ab822 106578f8` prints `CARRY` (`ev/review_carry.txt`), so this verdict carries to that head.
- CI: `merge_train.py classify 2c1ab822 --pr 3870` printed `WAIT ... pending: gate red: none` on every poll from 12:57 to 13:10 UTC (`ev/classify.log`). No CI run exists for head_sha 2c1ab822, only a skipped Dependabot run. The CI runs for PR 3870 (CI code 45618102773, CI edit 45619591862) are on 106578f8 and queued. So no gate can complete at 2c1ab822, and green has to be read at 106578f8.
- tests/entities.py at the head did not finish within my 230 s cap (`ev/entities_timeout_tail.txt`). The #1218 check was re-derived standalone instead, and CI's run is the one to cite.
