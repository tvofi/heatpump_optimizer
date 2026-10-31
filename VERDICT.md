Fix review: merge f91733b769b297847e7c143dbdc96d437a44c4b1

bus-nonce: f39671d9ca92a69cb2ba01a66ad21556

## Round

Round 2 of PR #3005 (R10-COP-GATE part 5). Reviewed head f91733b769b297847e7c143dbdc96d437a44c4b1 (code head eaa942dfd47f14b333c3b54f43d91419f1e1e029 plus an automatic merge of origin/main 5d4e0bcfb). Delta reviewed: 0e03b035..eaa942df, two commits touching tests only: fc03874db adds the fixtures and eaa942dfd adds the ledger entry. No production or golden file changed since round 1. coordinator.py is code-owned, so tvofi's approving review is still owed before the merge. This is flagged and does not block.

## Findings

- #2262 is still open, and the group's roster `fixes` list is empty, so this PR carries no closing keyword. The body hands the closure to the orchestrator after the merge: either add 2262 to R10-COP-GATE's `fixes` list, or close the issue by hand. Items B and D stay in the group's brief as carries 6, 7, 14, 17 and 12. Carry: R10-COP-GATE
- Forward-carry lead: `_interval_space_power` splits draw by the commanded split instead of the observed dwell. It is honestly labelled unmeasured, and its destination is a new carry in R10-COP-GATE's roster list. Carry: R10-COP-GATE
- Forward-carry lead: `_record_accuracy` passes the commanded `split` into `draw_range.fold`. It is honestly labelled unmeasured, with the same destination. Carry: R10-COP-GATE

## Evidence

- Mutation proof, at this head in three git worktrees, `PYTHONPATH=tests/hastub python3 tests/features.py` (ev/features_*.txt, ev/mutants.diff):
  - RESULT head: ALL 4627 FEATURE CHECKS PASSED, rc=0. Both new checks print `ok`.
  - RESULT mutant coordinator.py:884 `<=` to `<` (no-weight bound): 1 of 4627 FEATURE CHECKS FAILED, rc=1. The only failure is "the flow-lift gate's no-weight bound is inclusive ...". The curve-share check still prints `ok`.
  - RESULT mutant coordinator.py:884 `>` to `>=` (curve share): 1 of 4627 FEATURE CHECKS FAILED, rc=1. The only failure is "a hot-water share exactly at the curve share still folds ...". The no-weight check still prints `ok`.
  - Each mutant goes red on its own fixture only. In a git worktree the #363 recorded_at check passes, so I saw 1 failure per mutant, not the body's 2 from its copy without `.git`. The count rose from the body's 4608 to 4627 because of checks added on main.
- Null controls hold. Under the `<` mutant the 2e-6 h window still folds one sample (`2e-6 h (..., 1)`). Under the `>=` mutant the 0.16 share still folds none (`0.16 (..., 0)`). So only the equality decides, and each fixture asserts that its edge value is exact.
- Ledger: the diff adds exactly one killed_by entry, `_fold_flow_lift.CMP_BOUND.2f3e2f1a.json`, which records the 2 sites under one anchor. Its `old` text matches the gate line at this head. The GUARD_OFF entry under the same anchor comes from the bot's commit 0e03b035. I did not re-run `--pin-killed`, because CI's heavy runs are cited rather than re-run. The CI `tests / mutation` lane concluded success at this head. I read only that lane's job-output tail (count=1 shard), not its table.
- Body carry numbers checked against R10-COP-GATE's `carry` list at 4d2f32b2e: it holds 18 entries, and every citation fits its entry. 6 and 7 are the hover codes and plain words, 12 the learned top, 13 and 16 the flow-lift commanded split, 14 and 17 `envelope_drivers`, and 18 UX-HEALTH point A.
- #2262's state, read live: open, with no closing PRs. This matches the body.
- `git merge-tree --write-tree origin/main f91733b769b297847e7c143dbdc96d437a44c4b1` exits 0 against origin/main 5d4e0bcfb, which is already this head's base (ev/merge_tree.txt).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched on a three-dot diff.
- CI: `merge_train.py classify f91733b769b297847e7c143dbdc96d437a44c4b1` printed GREEN with pending none and red none (ev/ci_classify.txt). The Linux lanes `tests / fast (3.14)`, `tests / closures`, `tests / browser` and `tests / coverage` concluded success. This covers entities.py and card.mjs, which the fixer could not run on macOS.
- The `prelude` job in run 41145094001 was still in_progress at my read. It is not a required check and does not block. The `prelude` job in run 41145093420 concluded success.
- Red checks at this head: none, so no root-cause trigger is owed. The body answers round 1's two reds: mutation unpinned sites, and prelude HTTP 502.
- Head re-read before return: `fix/r10-cop-gate-p5-pr` is at f91733b769b297847e7c143dbdc96d437a44c4b1, and main is at 5d4e0bcfb.
- Not re-derived: the body's figures taken at eaa942df on the fixer's macOS host (4608 checks, the closure scope of 22 scripts, prepr output). I re-took the mutation and null figures at this head myself, as listed above.
