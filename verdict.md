Fix review: merge b7c376a3228f1c0b9a794c5f6cc5f71a29fdae4f

bus-nonce: ee630a54671681f5497b5fa631e33ff7

## Scope

Round 2, a delta review of PR #3015 (R10-HOTFIX-AWAY-LIVE) from round 1's merge verdict at a85aea80db2b5af603fe813658cc75800bc05daf to head b7c376a3228f1c0b9a794c5f6cc5f71a29fdae4f. `review_carry.py a85aea80 b7c376a3` prints FRESH-REVIEW: 4 branch-only commits (ba982d840 merge main, 438e7f373 budget record, 8697c91f5 and b7c376a32 merges). The production delta is the merge with #3013 alone. fix-review.md: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so my copy is current.

## Findings

none

## Evidence

- (1) Budget record. `git show 438e7f373` changes only `tests/structure_budgets.json`: `max_class_loc` 8063 -> 8061 and `recorded_at` cc930cdd -> 5d4e0bcf. No other row moves in that commit. Against the merge base 18b788ac2, the three-dot diff also lowers `class_excess_loc` from 17659 to 17657. That value comes from the ba982d840 merge resolution (branch 17670, main 5d4e0bcf 17659, resolved 17657), not from 438e7f373, and it is the same -2 coordinator shrink seen on the `class_excess` row. `python3 tests/structure.py` at the head prints `RESULT class_excess_loc=17657` and `RESULT max_class_loc=8061`, both `ok` at exactly their budgets. All 23 `ok` lines sit at their budgets, with no headroom and no FAIL, and the run ends `STRUCTURE RATCHET PASSED` with rc 0 (ev/structure_head.txt). Both moves are downward and measured, so the change earned them. `budget-raise-gate` is green.
- (2) Semantic overlap with #3013 in away.py. #3015 adds `published_under` (override fields only) and gates `_resolve_away` and `_async_first_refresh_light` on `boost.session_restored`. #3013 widens `_OPT_FIELDS` and `solve_bands` to the weekend and holiday pairs. The two touch disjoint state: `published_under` reads `away_override_active` and `away_override_return_time`, and `solve_bands` reads the bands. At the merged head, `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4630 FEATURE CHECKS PASSED` with rc 0 (ev/features_head.txt). The away rows all read `ok`, both #3015's four R10-HOTFIX-AWAY-LIVE checks and #3013's weekend/holiday setback check with its null control (ev/away_rows_head.txt).
- (2, mutation at the merged head) I planted my own mutants, each diff in ev/mutant_m*.diff:
  - m1, `published_under` -> `return True`: `1 of 4630 FEATURE CHECKS FAILED`, the R10-HOTFIX-AWAY-LIVE reload/handover check.
  - m2, #3013's four weekend/holiday fields dropped from `_OPT_FIELDS`: `1 of 4630`, `away sets back the weekend and holiday comfort pairs too: Saturday ...`.
  - m3, the `session_restored` await removed from `_resolve_away`: `1 of 4630`, the resolve-before-restore check.

  Each fix is still killed by its own check after the merge, so neither change masks the other.
- (3) CI at this head. `merge_train.py classify b7c376a3` returns `GREEN ... pending: none red: none`, rc 0. I read all 42 check runs (get_check_runs): every one is success or skipped, and none is red at this head. `tests / fast (3.14)` passed, which shows the structure record cured the round-2 red. `governance / instrument-self-tests` passed too, so the round-2 self-test failure did not recur here. The body's `## Red checks` answers both the structure red (structure.py is the detector, and prepr runs it) and the instrument-self-tests red (unreproduced flake, prepr --self-test 429/0). The trigger is answered. `pr-contract` and `gate` are green after every other run concluded.
- (4) The Forward-carry item now reads `Carry: dismissed: R10-HOTFIX-AWAY-SETBACK merged as #3013 (18b788ac2); merge-tree against main is clean; ...`. carry_audit in the packet reads `3 routed, 0 unrouted, 0 bad destination(s)`. The semantic check it leaves to the reviewer is done in (2) above.
- Merge with main. origin/main has moved to fbc73128371ba2daf9696b851528819c6bf5070e. `git merge-tree --write-tree origin/main b7c376a3` gives tree 7928ebe4, rc 0, no conflict (ev/merge_tree.txt).
- Head. The PR body's `## Head` names b7c376a3228f1c0b9a794c5f6cc5f71a29fdae4f. I re-read the branch head after measuring and it is still b7c376a3228f1c0b9a794c5f6cc5f71a29fdae4f (ev/head_recheck.txt).
- `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched three-dot from the merge base (ev/version_untouched.txt is empty).
- Not re-derived: the body's round-1 figures (base `2 of 4609`, the scoped-gate counts) were taken at earlier heads and verified in round 1. I did not re-run the gate or the mutation table, because CI's runs at this head are cited instead.
