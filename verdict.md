Fix review: merge f476a8ab5cb1229da5d78c622fa984ac7324c86c

bus-nonce: 38e58eb754140b96e6108b62ae04d954

## Scope

Delta from the previous merge verdict at a00b84084857e2c39a93f67b30443975d096c740 (fix-review.md step 12). The packet printed `Review scope: full` because verdict/<pr> names no verdict at this head. `review_carry.py a00b8408 f476a8ab` printed FRESH-REVIEW, because 7ddff620 is not the automatic merge of its parents. The delta is a main merge (8f22a3b2: #3838, #3906) and its hand resolution. It changes no production line, so nothing widens the scope.

## Evidence

- Resolution: `git merge-tree --write-tree a00b8408 8f22a3b2` conflicts in `dev/audit/rounds/round4/D6/claims.py` and `tests/deployment_shape.py` only. Diffed against that automatic tree (ev/resolution-vs-automerge.diff), the head changes those two files plus the regenerated `docs/architecture.md` and D6 `claims.md`/`claims.json`. Each conflict keeps both histories: R11-OUTSIDE-ROOMS-3B's comfort_floor.py and #3848's dhw_start.py are both named in the arch_modules_on_disk, arch_map_listed and #1218 package-file notes. The pair note keeps both branches' history lines.
- The reviewed fix is unchanged. `git diff <base>...<head> -- custom_components/` is line-identical at a00b8408 (base 3ee06864) and at f476a8ab (base 8f22a3b2): PROD-DIFF-IDENTICAL. Across all 39 files, the PR's own diff changed only in claims.py, claims.json, claims.md, architecture.md, deployment_shape.py and structure_budgets.json (ev/pr-diff-delta.txt). The PR's own closures.json, features.py, block_duty.py and mutation-ledger diffs are unchanged.
- Counts were re-derived at this head, not carried over:
  - 124 tracked files under the package (`git ls-tree`), 105 `.py` modules.
  - claims.py printed `RESULT arch_modules_on_disk=105`, `arch_map_listed=105` and `claims_false=0` (rc 0). `git status --short` was empty afterwards, so the committed claims.md/json and architecture.md are byte-identical to a fresh regeneration (ev/claims.txt).
  - 36 module-level importers + 1 in-function + 68 others = 105.
- Closure pairs, my own independent computation from tests/closures.json (production-file Jaccard >= 0.80, ev/pairs.txt):
  - main 8f22a3b2: 34 scripts, 561 pairs, 435 comparable, 184 at or above 0.80;
  - a00b8408: 184;
  - f476a8ab: 190.
  These match the note and the body.
- `python3 tests/structure.py` at the head: rc 0, `module_excess_loc 21650 <= 21650`. Measured, it equals the ledger driver's value (21762 + both deltas = 21650), and it is 103 below main's 21753, the same payment as before (ev/structure.txt).
- `PYTHONPATH=tests/hastub python3 tests/deployment_shape.py`: `ALL DEPLOYMENT SHAPE CHECKS PASSED` rc 0.
- Mutation re-proof at the head. In `pump_signals.with_dhw_under_way`, `dhw_charge_under_way=True` replaced the running/mode expression: `tests/block_duty.py` printed `1 of 161 BLOCK DUTY CHECKS FAILED`, rc 1, KILLED (ev/mutant_M1.txt). Unmutated null: `ALL 161 BLOCK DUTY CHECKS PASSED`, rc 0.
- `git merge-tree --write-tree origin/main(dbdc71fa) f476a8ab`: no conflict, tree 95b819a5 (closures.json via the ledger driver).
- CI: `merge_train.py classify f476a8ab --pr 3863` printed `GREEN f476a8ab5cb1229da5d78c622fa984ac7324c86c pending: none red: none`, rc 0, twice (ev/classify.txt). No owed reds.
- Head re-read before return: `refs/heads/fix/r11-outside-3848` = f476a8ab5cb1229da5d78c622fa984ac7324c86c.
- Body `## Head`: the figures for 7ddff620 were each re-derived and match: 124 files, 190 of 561, 435 comparable, main 184, 105 modules, 36 importers, other 68. The opening `dhw_start.py` bullet still quotes an earlier round's "21672 against main's 21775". That is a dated history line; the payment it describes (103) is unchanged at 21650 against 21753.
- I did not rerun doc_claims.py or the full entities.py locally. CI is green on both at this head.
