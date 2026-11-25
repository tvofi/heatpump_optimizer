Fix review: merge b721469aa88c74eee0cdc2e1536ba108063221b9

bus-nonce: 36c8f8c0dfd748bbd36098e3ecdcdb38

## Summary

Round 2 review of #3875 (R11-SEAM-store Part 1 of 2). The scope is the delta `git diff 8dd2a9da51 b721469aa88c74eee0cdc2e1536ba108063221b9`: two checks added to `tests/finite_boundary.py` and nine `killed_by` mutation-ledger pins. The delta contains no `custom_components/` change, so the review is not widened (fix-review.md step 12). Each added check kills the mutants it was written for. The head passes its checks, merges cleanly with main, and CI classifies GREEN.

## Evidence

- RESULT head: I measured `b721469aa88c74eee0cdc2e1536ba108063221b9` (ev/HEAD.txt), which is the PR head and the head the body names. The delta commits are e2f34a09c8 (bot, `ci: pin killed mutants`), b503d2e8d1 (`test: kill the diff's surviving mutants and pin its killed sites`) and the merge b721469aa8. The diff stat lists `tests/finite_boundary.py` (+30) and 9 new files under `tests/mutation_ledger/killed_by/`, and nothing else. The `dev/governance/roles/` diff against origin/main only rewords `fix-review.md` and changes no step. I reviewed against main's text, rendered by role_pack.py.
- RESULT merge: `git merge-tree --write-tree origin/main b721469aa88c74eee0cdc2e1536ba108063221b9` gives rc=0 against origin/main 7f7e05118f (ev/merge_tree.txt).
- RESULT CI: `merge_train.py classify b721469aa88c74eee0cdc2e1536ba108063221b9 --pr 3875` prints `GREEN b721469aa88c74eee0cdc2e1536ba108063221b9 pending: none red: none` (ev/classify.log). In the packet digest, `tests / nightly-status` reads failure and `tests / replay` reads cancelled. Neither is in the `owed-reds` set (ev/owed_reds.txt), so neither owes an answer.
- RESULT unmutated: `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` in a detached worktree at the head prints `ALL 122 FINITE BOUNDARY CHECKS PASSED` (ev/fb_wt.txt). This equals the body's figure.
- RESULT mutants: each was applied with sed in its own worktree at the head, and `tests/finite_boundary.py` was run there (diffs in ev/fb_mut_m*.diff).
  - m1, `_learned_pair` `value > 0` changed to `>=` (the CMP_BOUND pin 26881a60): `1 of 122 FAILED`. The fold check fails with `((0.0, 5), 1): True, ((0.0, 0), 0): True` (ev/fb_m1.txt). This equals the body's 1 of 122.
  - m2, the `_learned_pair` guard set to `if False:` (the GUARD_OFF pin 26881a60): `2 of 122 FAILED`. The fold check fails, and so does the P1 off-domain sweep (`refused=8`) (ev/fb_m2.txt).
  - m3, the `store.py:610` declaration `and` changed to `or` (the BOOLOP pin fe113ff6): `1 of 122 FAILED`. The check "the debug row declares exactly the accuracy sample's own fields" fails (ev/fb_m3.txt). This equals the body's 1 of 122.
  - m4, my own: `count >= least` changed to `count >= 1`, which ignores the count-0 floor. It gives `4 of 122 FAILED`, including the fold check's `((5e-324, 0), 0): False` arm and the round-trip check (`changed=['thermal_learning']`) (ev/fb_m4.txt).
  - The fold check's null arm (the least positive value, 5e-324, kept at both count floors) reads True at the head. That means the check separates the fold's floor from the value check rather than refusing everything.
- RESULT step 14: the nine new pins match the sites the body lists under `## Unpinned sites`. Five were recorded by mutation-autofix, and four (the CMP_BOUND, the two GUARD_OFF, and the BOOLOP at store.py:610) were pinned on the branch. m1, m2 and m3 independently reproduce the three pins whose killer is `tests/finite_boundary.py` and whose site the delta added. Nothing in `structure_budgets.json`, `closures.json` or the claim files moved in the delta.
- RESULT step 5: VERSION, the manifest version and the RELEASE_NOTES heading are untouched in the delta.
- RESULT prior verdict's findings: the round-1 verdict at 8dd2a9da51 had one note, about the null-control figure (5 of 120 as stated, 6 of 120 re-derived with a signature shim). That note was dismissed as paperwork, and the body's null-control paragraph is unchanged. Nothing is owed on it.
- RESULT not re-run, cited from CI per step 11: the gate, the mutation table, `tests/structure.py`, and the features/entities runs.

## Findings

- Note: body: the `## Red checks` section ends in a stray fragment, `## Unpinned sites`. mutation-autofix ... one bot commit.`, left over from an earlier cut and placed ahead of the real `## Unpinned sites` heading. Paperwork only; no code is affected. Carry: dismissed: paperwork in the PR body, no code or test effect

## Friction

none
