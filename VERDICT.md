Fix review: merge 4f0f2a8cc648f63395e36c795f11f8c9b63efbb4

bus-nonce: b5bfb3a930729b2e5f3010bb9d5b6d1f
pending-ci: gate

Round 3, a delta review over reviewed-head 0f9fc88ff36dd0326fa7f862e38d909b95133138 (round-2 draft 190a25208d9a, merge, not posted). Scope: `git diff 0f9fc88f 4f0f2a8c` and the round-2 items.

## Evidence

- What moved the head: two first-parent commits, `baf1450505 ci: pin killed mutants` (github-actions bot, four `killed_by` pins: early_cutoff `_exempt`, pump_arbiter `desired` and `supply_tick`, supply_hold `note_cooling`) and `4f0f2a8cc6 ci: merge main` (origin/main b18edd593c). There is no fixer change.
- The PR's own diff against its merge base is line-identical at both heads for custom_components, tests/features.py, tests/entities.py, docs and README.md (ev/pr_diff_compare.log). So round 2's production and test findings and its mutation proof carry unchanged.
- tests/structure_budgets.json moves only downward (class_excess_loc, max_class_loc, module_excess_loc), so this is no raise (ev/budgets.diff). `git merge-tree --write-tree origin/main 4f0f2a8c`: rc 0.
- CI at the head: `merge_train.py classify --pr 3864` prints `WAIT ... pending: gate red: none` (rc 3). governance / instrument-self-tests is completed success. `tests / mutation` is completed failure: `MUTATION TABLE REFUSED -- 1928 unpinned against 1919, 9 added by this diff` (ev/mutation_4f0f2a8c.log). These are unpinned sites in the PR's own code, the class ci-autofix's mutation-autofix repairs, and round 2 already proved the delta's mutants killed. It is still red, and the relay refuses over it until the bot pins.
- Prior items 1-3 resolved in round 2 stay resolved, since the diff is unchanged.
Carry: dismissed: evidence, not a finding
