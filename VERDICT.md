Fix review: merge c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822

bus-nonce: 7995f8f34278a29487ff2a3eef3efdfa

Delta round (owner ruling 2026-11-09): reviewed 06a3478fd..c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822 only. The previous verdict at 06a3478fd was `merge` with no findings, so nothing from it is open. The delta is one main merge (c9ba955f3). The PR's own three-dot diff against 2f6d699e5 is the same 8 files as before (`ev/threedot.txt`) and holds no custom_components, VERSION or RELEASE_NOTES line (`ev/version-untouched.txt`: 0). The custom_components changes in the raw delta come from main, so no already-reviewed production code is put at risk and no wider review was done.

## Findings

- Defect, non-required: the PR's new step in `.github/workflows/governance.yml` ("Show the survivor-list check ...", `instrument-self-tests`) carries `if: ${{ !cancelled() }}` and no step id, so main's new `tools/ci/selftest_scope.py static` refuses it: `UNGATED step 'Show the survivor-list check ...': its if: does not read steps.scope.outputs.<its own id>`, 1 problem at this head against 0 on origin/main (`ev/selftest-scope-static-head.txt`, `ev/selftest-scope-static-main.txt`). That is the red `governance / instrument-self-tests` (`FAIL the live job parses (116 steps) and its gating is consistent`, selftest_scope 90 checks, 1 failed). The check came in with the main merge, so the fault is this PR's step against a rule that landed after it. The context is not in `merge_train.py owed-reds` (`ev/owed-reds.txt`), so by the red-check ruling it does not block this verdict, but a push of this head to main would leave the job red there. Repair before or at the merge: give the step an id and a scope-output gate, and record it in `tools/ci/selftest_closures.json` as the sibling steps are. Carry: R10-REVIEW-ENUMERATE

## Evidence

- Head measured: c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822 (`ev/HEAD.txt`).
- CI: `merge_train.py classify c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822 --pr 3341` printed `RED ... pending: none red: gate`. The `gate` log reads `FAIL tests / fast (3.14): failure` and nothing else. The `fast` red is inherited from main, not this PR's: its log shows `3 of 112 HARNESS HEADER CHECKS FAILED` (D6 claims.json and claims.md drift) and `2 TEST SCRIPT(S) FAILED`; I ran `tests/harness_headers.py` on a worktree of origin/main (2f6d699e5) and it fails the same three checks (`ev/harness_headers-main.txt`, rc=1). This matches the dispatch's note that main is red on the same unit, fixed by #3378. The PR's diff touches none of those files. The other `fast` failure is the entities lane; I did not re-run it (336 s) and rely on the dispatch's statement for it. The PR is behind that red, not the cause.
- Merge: `git merge-tree --write-tree origin/main c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822` rc 0 (`ev/merge-tree.txt`).
- `survivor_list.py --self-test`: 20 checks, 0 failed at the head (`ev/survivor-selftest.txt`), as at the previously reviewed head. The instrument's code is byte-identical in the PR diff to the head already judged.
- Review packet refusals (`red-unanswered` for `gate` and `tests / fast (3.14)`, `required-red` for `gate`) are the inherited main red above. Not re-derived: mutation and gate runs (CI's heavy runs cited), `bus.sh --self-test` (unchanged since the previous verdict's 162 checks).
- Policy: the diff edits dev/governance/roles/fix-review.md, so it merges only on tvofi's approving review.
- This is a later round of an already-reviewed PR; round count not exceeded.
