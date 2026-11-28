Fix review: merge b3762bb01f8b348a6792b0954473a61ab7b529e3

bus-nonce: 36874108253edb95b45f910f7139d442

## Scope

This is the third round: a delta review over the previous verdict `merge 36417ab5fab69c3932eda49da9d79ecd956e621b`, which had no findings. The scope is `git diff 36417ab5fa b3762bb01f`. That range has eight branch-side commits, and every one is a merge. `review_carry.py 36417ab5f b3762bb01` prints `FRESH-REVIEW` because `4800bc04e2` is not the automatic merge of its parents, so I reviewed each merge's resolution with `git show --remerge-diff`.

Only one resolution touches production code: `custom_components/heatpump_optimizer/dhw_learning.py` `DhwProfileLearner.async_save_draws`, in `4800bc04e2`. Main's #3931 (`f99ae8a4ef`) deleted the dead `draws_dirty` attribute. This branch had moved the same save into `store.save_held`. The resolution keeps `save_held` and drops the `self.draws_dirty = False` line.

That is a production delta, so I widened the review to exactly that method. The risk I checked is one CI would not show directly: the resolution could have quietly brought back the swallow-under-broad-handler shape (main's side) and lost this PR's failure reporting. It could also have left a reference to an attribute main deleted.

## Evidence

- RESULT resolutions (ev/remerge-*.txt):
  - `f7b44e69ec`: `dev/audit/config/scopes.json` is taken whole from main's D5 s7/s8 re-cut, which puts the same files in each seat as the PR's own cut. `structure_budgets.json` and `closures.json` were resolved by the ledger driver (`LEDGER-MERGE: resolved`).
  - `de356461aa`: ledger-driver resolutions only.
  - `4800bc04e2`: the `dhw_learning.py` hunk above.
  - `bf1ca4c8a9`, `625226630d`, `82a183714d`, `8c0a3b2302` and `b3762bb01f`: the remerge diff is empty.
- RESULT dhw_learning resolution: `git grep -nE '_last_manual_setpoint|draws_dirty|last_return_c\b'` over custom_components, tests and tools at the head prints nothing. No reference remains to any attribute #3931 deleted.
- RESULT targeted mutant on the resolution (ev/mutant.diff): I put back main's `try: ... except Exception: _LOGGER.debug(...)` form of `async_save_draws`, in place of `save_held`.
  - The `D1-s3-05` census in `tests/features.py` (`_cr_save_sites`, run standalone by my own wrapper `census.py`, which runs the test file's function verbatim) goes from `CENSUS PASS` with 18 held (ev/census-head.log) to `CENSUS FAIL` with `swallowed [('dhw_learning.py', 385, 'swallowed')]` (ev/census-mutant.log). The mutant is killed.
  - `tests/finite_boundary.py` passes both with and without the mutant: `ALL 122 FINITE BOUNDARY CHECKS PASSED`, rc 0 (ev/finite_boundary-*.log). That is expected, because it checks finiteness, not failure reporting.
  - The wrapper is mine and is disclosed as mine. I did not re-run the full features.py; that belongs to CI's gate.
- RESULT scopes: `python3 -I tools/audit/check_scopes.py --repo .` at the head prints `ok D5 mode=cells seats=10 universe=949`, with `s7:1f/0loc/4347u` and `s8:49f/0loc/4072u`, both under 4500, rc 0 (ev/check_scopes-head.log). The universe is 949, not the body's 945 at `f7b44e69ec`, because later main merges added files. The body figure was measured at that merge, so it is not a defect at this head.
- RESULT budgets: three-dot `tests/structure_budgets.json` moves only downward: class_excess_loc 17204 -> 17200, max_class_loc 7759 -> 7751, module_excess_loc 21607 -> 21595. The body's figures (max_class_loc 7751, module_excess_loc 21595, methods_over_200 7) match the head file. No raise is owed.
- RESULT version: neither `VERSION` (10.1.7 at the base and at the head) nor `RELEASE_NOTES.md` is in the three-dot diff. The manifest's only three-dot change is `quality_scale` platinum -> gold. That change was already in the PR at both earlier reviewed heads, and it is not the version field.
- RESULT merge-tree: `git merge-tree --write-tree origin/main b3762bb01f` with origin/main at `cb2026c3b5` exits 0, tree `9d2884a8a0`, and the ledger driver resolved budgets and closures (ev/merge-tree.txt). GitHub's `dirty` is the claim-driver case, not a conflict.
- RESULT head: the PR's head.sha reads b3762bb01f8b348a6792b0954473a61ab7b529e3, and the body's `## Head` names it.
- RESULT CI: `merge_train.py classify b3762bb01f --pr 3845` exits 0 with `GREEN b3762bb01f8b348a6792b0954473a61ab7b529e3 pending: none red: none` (ev/classify.txt). It printed WAIT while a re-queued `gate` run (140920656347) ran. The only red check is `tests / nightly-status`, which is not in `owed-reds` (coverage-ratchet, fast (3.14), mutation, typing, validate-hacs), so it is owed no answer.

## Findings

none

## Friction

none
