Fix review: merge 9c4e4516cf9cb0c1a35a6c57aaceaee940e13768

PR #1838, R9-F10.4, round 2. Round 1 blocked a980e165 on census-hole (the verdict is in F10.4-review-a980e165). Code head measured: 9c4e4516, which is the PR head at posting. Body: 90fba84c, whose Head section names 9c4e4516. Base 3bd6f122 = origin/main.

## Resolution delta (832e640c..9c4e4516, one commit)

`dead_members()` now treats a member's name as ambiguous when another class holds it as a field: a class-body assign or annotation, or a store on the method's first parameter. This changes classification only and leaves liveness alone. A planted self-check case and a matching mutant are added.

- My round-1 probe (probe_head.txt): RESULT field_collision_unprinted=0 count; RESULT name_kept_reported=113 count (it was 21 and 92).
- structure.py at head: rc=0, 41 counting rules hold, STRUCTURE RATCHET PASSED. Every RESULT equals round 1: dead_methods=3, coordinator_multiassigned_attrs=120, seam_cut_total=777. `solar_radiation` is now printed name-kept. See structure_head.txt.
- Base under the new definition (structure_base_newdef.txt): dead_methods=9, coordinator_multiassigned_attrs=120, 114 name-kept, `DefrostDerate.samples` among them. The body's 113 and 114 are re-derived.
- mutants.py: unmutated rc=0 []; 13 of 13 mutants red. The new one ("another class's field does not make a name ambiguous") fails "an untyped x.n of a name another class holds as a field is name-kept". See mutants_head.txt.

Round 1's other measurements stand unchanged at this head, because the delta touches only `tests/structure.py`'s census and self-check and `mutants.py`: the finders 10→4 and 11→3, doc_claims 112 PASS with the anchor perturbation named, the untouched VERSION/manifest/notes/golden, and the clean merge-tree.

## Red checks (step 11)

- `briefs`: the body's claim holds. tests.yml's `briefs` job restores `.claude/workflows/*.mjs` from the base sha before linting.
  - Measured: base 3bd6f122's brief_lint.mjs over this head's tree gives rc=1 with `FIXTURE VACUOUS: 931dffe acceptance pins missing: [W1-G8] metric: coordinator_loc` (brief_lint_base_on_head.txt).
  - The head's own brief_lint.mjs over the same tree gives rc=0 (brief_lint_head.txt), and the base linter on the base tree gives rc=0.
  - The red therefore comes from retiring the `coordinator_loc` key while the pinned linter is the base's. Nothing inside this PR can turn it green. Answered in the body with a cheaper detector named and costed.
  - Merging past it, or landing the pin change first, is the owner's call, since brief_lint.mjs is policy.
- `budget-raise-gate`: red by design until tvofi's approving review. Answered.
- Tests (gate, mutation) had not reported on 9c4e4516 at posting. This verdict does not cite them, and the merge rule's CI-green condition still applies.

## Still owed to tvofi (not this verdict's to grant)

- The budget re-baselines `dead_methods` 0→3 and `coordinator_multiassigned_attrs` 117→120. Both are redefinitions at measured values, and base measures 9 and 120 under the new definitions. Plan card B5 pre-allows them on tvofi's approving review.
- The `briefs` bootstrap decision above. The brief_lint.mjs edit is also policy, needing tvofi's approval before merge.
