Fix review: blocked 8c3f64114f6eb60679562cbd6e0f6a1fdab4b588 introduced-red: the tests/features.py freeze refuses this PR's two new spans (tests / fast (3.14, 1/4), tests/entities.py)

bus-nonce: 3f921e39b026ff6eaa67d741a3b8df38

## Block

At this head, `tests / fast (3.14, 1/4)` (job 141060416123) reads `5 of 2800 ENTITY CHECKS FAILED` in `tests/entities.py`, section `The tests/features.py freeze (R11-OWNER-FEATURES-SPLIT)`. The required `gate` is red on it. `tests / fast (3.14)` is in the owed-reds set (`ev/owed_reds.txt`).

The freeze reached this branch through the main merge into this head. Main froze `tests/features.py` in 62d50e9990 and re-recorded the manifest in 94d05d861c. Neither commit is an ancestor of the previous reviewed head 6ade1643e2. This is precondition state (d): the branch's tests were written before the rule existed.

Reproduced locally with the harness's own live check, `features_freeze.tree_refusals` (`dev/audit/harnesses/features_freeze.py`; `ev/freeze_tree_refusals.txt`):
- At the head it returns 3 refusals:
  - `span: tests/features.py has span "R11-OUTSIDE-START-APPROACH: a run's first steps draw what the pump draws (Bankaifan, comment 6944433306 on #3670)", which tests/features_frozen_budgets.json does not list`. This is this group's block.
  - The same refusal for `"R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed on the planner's own store"`. That block comes from the stacked predecessor #3805 and is in this PR's three-dot diff.
  - `lines: tests/features.py has 106539 lines, above the 104695` recorded.
- At origin/main a59a1b0d9a it returns 1 refusal, `lines` only (104990 > 104695). Main is over its own line cap, so the lines refusal is not this PR's alone. The two span refusals are absent at main, so this PR introduces them.

The freeze sends new tests to a seam script. `features_freeze.py --seam tests/features.py` names the homes (`ev/seam_homes.txt`): `plan` for this group's block and `surface` for #3805's. Repair, for the fixer to carry out:
- Move both sections, with their helpers, into `tests/features_plan.py` and `tests/features_surface.py`. The harness docstring lists what that move owes: the `run` line in `tests/run.sh`, the closure, and no import of `tests/features.py`.
- Bring the line count to the manifest's cap.
- Never re-record the manifest to admit the spans. `spans` is FROZEN under budget-raise-gate.
- Re-drive the mutation table's hand mutants against the moved block, the case-8 pair included.

## Findings

- Note: freeze-on-main: origin/main a59a1b0d9a already reads the freeze's `lines` refusal (104990 > 104695) with no PR applied, so `tests / fast (3.14, 1/4)` stays red for any branch on that main until main re-records or nets out its own growth (#3934's merge, ac9045c223, is the latest touch of `tests/features.py` on main). This PR's repair cannot clear that refusal alone. Carry: dismissed: main's own check, owned by the orchestrator, who repairs main's lane (defect-root-cause.md); recorded here so this PR's fixer does not chase it
- Note: stacked-predecessor span: the second refused span is #3805's (R11-OUTSIDE-HONEST-DHW-RUNS), still open. #3805 needs the same move before it can merge. Carry: dismissed: #3805 is its own open PR, and the merge train re-proves it against the freeze on current main; this verdict asks the fixer of this branch, which carries the span, to move it or take #3805's move

## Evidence

- Head measured: 8c3f64114f6eb60679562cbd6e0f6a1fdab4b588 (`ev/HEAD.txt`), the body's `## Head` SHA. Round: third review, a later round over 6ade1643e20a9518e7600703c348abe46feba4a1 (verdict `mutation-vacuous`). Scope: delta (fix-review.md step 12). The packet printed `full (first round: no --reviewed-head)` because no reviewed head was passed to it.
- Roles drift: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merge with main: `git merge-tree --write-tree origin/main 8c3f64114f` exits 0 (origin/main a59a1b0d9a, the head's merge base). The ledger driver printed `LEDGER-MERGE: resolved` for `tests/structure_budgets.json` and `tests/closures.json` (`ev/merge_tree.txt`).
- Delta isolated: `git merge-tree --write-tree a59a1b0d9a 6ade1643e2` (tree ccfdcd43f9) diffed against the head shows `tests/features.py` +39 and nothing else (`ev/delta_stat.txt`). That is the case-8 check of e50d72615a plus 2b0a25318f's comment re-wording. There is no production delta, so step 12 does not widen.
- Prior block (mutation-vacuous, case 8) resolved at this head. The block was run by `features_block.py` with its `--emit-prelude` prelude:
  - Control: `ALL 24 FEATURES BLOCK PASSED`, rc 0.
  - `coordinator.py:6312` `_solve_record` `approach=...` replaced by `approach=None`: `1 of 24 FEATURES BLOCK FAILED`, rc 1 (`record None want Approach(...)`).
  - `coordinator.py:11238` `_whatif_solve` `approach=...` replaced by `approach=None`: `1 of 24 FEATURES BLOCK FAILED`, rc 1.
  - Each mutant was restored and the tree left clean. Logs: `ev/mut_case8.log`, `ev/mut_control.txt`, `ev/mut_case8a.txt`, `ev/mut_case8b.txt`.
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched in the three-dot diff.
- CI at this head:
  - `merge_train.py classify 8c3f64114f --pr 3907` read `WAIT ... pending: gate red: none` from 18:46Z to the last run (`ev/classify_poll.txt`). `tests / mutation-pins` shards were still running.
  - The block above rests on the failed `tests / fast (3.14, 1/4)` job and the local reproduction, not on classify.
  - Other reds in the digest (`ev/review-packet.md`):
    - `tests / mutation` is the ADDED UNPINNED red that `mutation-autofix` repairs (ci-autofix.md).
    - `budget-raise-gate` is the inherited #3805 raise answered in the body's `## Raise justification`.
    - `tests / nightly-status` grades main and is not in the owed set.
- Not re-derived by this seat: the harness-arm figures, the axis grep counts, the closures counts and the architecture-score dS. A delta round has no production change that would reopen them.
