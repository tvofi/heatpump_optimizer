Fix review: merge 36417ab5fab69c3932eda49da9d79ecd956e621b

bus-nonce: 398952f51b396d1a3adf5ab9489cd72d
pending-ci: gate

## Scope

Delta round over the previous verdict `merge 3da16553914c71017ee25fd98486f2125083016c`, which had no findings. Scope: `git diff 3da1655391 36417ab5fa`. In that range the PR-side work is one commit, `361cc26c97` (changes only `dev/audit/config/scopes.json`). The rest is three main merges (`9e0a095d51`, `9dfa722747`, `2643502f38`) and the merge of `361cc26c97` itself (`36417ab5fa`). The delta changes no production code on the PR side, so the scope is not widened.

## Evidence

- RESULT resolutions: `git show --remerge-diff` on `9e0a095d51`, `9dfa722747` and `2643502f38` prints no diff. The only conflicts were in `tests/structure_budgets.json` and `tests/closures.json`, and the ledger driver resolved both (`LEDGER-MERGE: resolved`). There is no hand resolution (ev/remerge-*.txt).
- RESULT merge-tree: `git merge-tree --write-tree origin/main 36417ab5fa` (origin/main `0238a79886`) exits 0, tree 17605524df (ev/merge-tree.txt).
- RESULT scopes repair: with `python3 -I tools/audit/check_scopes.py --repo .` at the head, the run prints `ok D5 mode=cells seats=10 universe=945` with `s7:1f/4329u` and `s8:49f/3999u`, RC=0 (ev/check_scopes-head.log). Null control: I put `scopes.json` back to its `2643502f38` content in the head worktree and re-ran it. It prints `FAIL D5 ... over ledger.max_units 4500: s7 holds 4513 units`, RC=1 (ev/check_scopes-without-commit.log). So the red was caused by the diff and the commit removes that cause. The movement is earned (step 14). `tests/f*` holds `features.py`, `finite_boundary.py`, `fixtures/` and `frontend.py`. After the re-cut, `s7` takes `features.py` and `s8`'s new `tests/f{i,r}*` takes the other three, so nothing goes unowned. check_scopes confirms this with universe 945, unchanged.
- RESULT budgets: `git diff origin/main 36417ab5fa -- '*budgets*.json'` moves only tests/structure_budgets.json, and every changed row goes down: class_excess_loc 17220 -> 17216, max_class_loc 7762 -> 7754, module_excess_loc 21646 -> 21634 (ev/budgets-vs-main.diff). No budget rises, so no raise is owed.
- RESULT version: the three-dot diff does not touch VERSION or RELEASE_NOTES.md.
- RESULT CI, read live at 36417ab5fa: `gate` reads failure, and its log says `FAIL run(s) [45930781927] at this head are still being judged; their gate decides`. That is a deferral: `pr-contract / pr-contract` was still queued. Hence `pending-ci: gate`. `governance / instrument-self-tests`, the lane the repair targets, reads success. The only other red is `tests / nightly-status`, which is not required. Every owed-reds lane (coverage-ratchet, fast (3.14) 1-4/4, mutation, typing, validate-hacs) reads success.
- RESULT head re-read: `gh pr view 3845` headRefOid is 36417ab5fab69c3932eda49da9d79ecd956e621b.

## Findings

none

## Friction

none
