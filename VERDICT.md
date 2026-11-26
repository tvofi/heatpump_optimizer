Fix review: merge 5f8e2cdb5fe2d236f71c62f8d41b31836df88107

bus-nonce: 6ed37cc85a15221671c27fc56354813a

## Scope

Round: delta review after the merge verdict at 1a0d13512588f35397993818aad8d566bf96afbc (fix-review.md step 12). review_carry.py prints FRESH-REVIEW because 4d865cb7 is a hand-resolved merge, so this round reviews that delta: the resolution of origin/main 8f22a3b2 into the branch. The packet's `## Review scope: full` line comes from rendering with --reviewed-head equal to the head; the dispatch names this as a delta review over 1a0d1351, and step 12 governs. The production delta is unchanged (below), so the scope stays at the delta.

## Evidence

- RESULT production-unchanged: `git diff <merge-base> 1a0d1351 -- custom_components/` and `git diff 8f22a3b2 5f8e2cdb -- custom_components/` carry identical +/- lines (13 files, +526/-70). The reviewed fix is unchanged.
- RESULT hand-resolution: the tree at 5f8e2cdb differs from `git merge-tree --write-tree 1a0d1351 8f22a3b2` only in the six files the body names (claims.json, claims.md, claims.py, docs/architecture.md, tests/deployment_shape.py, tests/features.py). 4d865cb7 and 5f8e2cdb have the same tree. Diff in ev/hand_resolution.diff.
- RESULT features.py-union: the branch's added lines (merge-base..1a0d1351) equal 8f22a3b2..5f8e2cdb's, and main's added and removed lines (merge-base..8f22a3b2, +259/-17) equal 1a0d1351..5f8e2cdb's (+258/-17). The only difference on each side is one blank separator line, which the two sides now share. The R11-OWNER-FAULT-TEXT section and the #3616 R11-OUTSIDE-ROOMS-3B section are both complete, each closing its own `R.check(`. The file parses. No conflict markers are left in any of the six files.
- RESULT counts re-derived at 5f8e2cdb:
  - 124 tracked files under custom_components/heatpump_optimizer/ and 105 .py modules.
  - `claims.py` prints arch_modules_on_disk=105, arch_map_listed=105 and claims_false=0, rc=0. Its regeneration leaves claims.md and claims.json byte-identical.
  - 37 HA importers: main's 36 plus fault_log.py. comfort_floor.py is not one.
  - 182 of 561 script pairs at Jaccard >= 0.80 over the production closures in closures.json, among 435 non-empty pairs. Main 8f22a3b2 gives 184 and 1a0d1351 gives 181 under the same rule, matching the history sentence (ev/pairs.txt, script in the review directory).
  - structure_budgets module_excess_loc: 21762 (merge-base) - 8 (branch, 21754) - 9 (main, 21753) = 21745, the committed value.
  - tests/structure.py: rc=0.
- RESULT mutation: CMP_BOUND on config_flow.py:2675 (`>` to `>=` FAULT_TEXT_ENTITIES_MAX) makes tests/config_flow_steps.py go rc=0 to rc=1, failing "five fault-text entities are refused..." (ev/mutant.txt). Source restored.
- RESULT claims: tests/golden/ is unchanged from 1a0d1351. The single config_flow claim line is the reviewed one. VERSION, manifest and RELEASE_NOTES are untouched in the three-dot diff. `env_drift.py --all` was not completed locally (killed at the 200 s cap), so CI's green gate is cited.
- RESULT merge: `git merge-tree --write-tree origin/main 5f8e2cdb` rc=0 against origin/main dbdc71fa, so it merges cleanly.
- RESULT CI: `merge_train.py classify 5f8e2cdb... --pr 3870` prints `GREEN 5f8e2cdb5fe2d236f71c62f8d41b31836df88107 pending: none red: none` (ev/classify.txt). The packet's red nightly-ha (2025.2.0, stable) and nightly-status are not in the `owed-reds` set, so no answer is owed.
- RESULT prior findings: the previous merge verdict carried no open block. carry_audit at the head reads 3 finding items, 3 routed, 0 unrouted.
