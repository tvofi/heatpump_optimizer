Fix review: merge 2e4f3ebe0811a3b1a079c41ec269233ac5395871

bus-nonce: a36650a8a9fd67ec0af91159b00d839a

## Scope

Round 3, a delta review of e536706f45cb07d32b3f76847366d0a868670030..2e4f3ebe0811a3b1a079c41ec269233ac5395871 (one github-actions commit, `ci: pin killed mutants`). Round 2's merge verdict stands for e536706f; its code was not re-reviewed. `review_carry.py e536706f 2e4f3ebe` prints FRESH-REVIEW (1 of 1 branch-only commit carries code), hence this delta. Roles diff merge-base...origin/main under dev/governance/roles/ is empty: the contract read is current.

## Findings

none

## Evidence

- (1) The delta touches only 7 new files under `tests/mutation_ledger/killed_by/` (42 lines added, ev/delta-stat.txt). No path under `custom_components/`, no test logic, no `*budget*` file. Author github-actions[bot] (ev/bot-commit.txt). VERSION, RELEASE_NOTES.md, the manifest and both claim files are unchanged merge-base...head.
- (2) All 7 pinned `old` lines are added lines in merge-base 861f949ae...e536706f under custom_components/ (each `+` line counted 1), and none of them occurs anywhere under custom_components/ at the merge base. Each pin's reason records a `mutation_table.py --pin-killed` run (a measured kill, not a prediction). CI's own `tests / mutation` at this head prints `PIN RE-VERIFICATION: 7 reproduced, 0 not reproduced, 0 not re-verified`, `0 survivor(s) of 7 evaluated`, `MUTATION TABLE PASSED` (ev/mutation-ci-log.txt).
- My own targeted mutants at this head, `PYTHONPATH=tests/hastub python3 tests/features.py`: thermal_model BOOLOP (`and` -> `or` in `heat_loss_entity_voids`) rc=1, `KeyError: 'lower_floor_temp_entity'` after 14 FAIL lines (ev/mutant-a-features.txt); coordinator `if HEAT_LOSS_LEARNERS[1] in learners:` -> `if False:` rc=1, `11 of 4644 FEATURE CHECKS FAILED` (ev/mutant-b-features.txt); the unmutated head rc=0, `ALL 4644 FEATURE CHECKS PASSED` (ev/mutant-c-features.txt). Figure not re-derived: the pin file records failed=12 for the GUARD_OFF 11a66faf site where my run counts 11; the kill itself reproduces, and the count is the pin's own recording at its own run.
- (3) The body's `## Head` section names the bot commit and states the `tests / mutation` red at e536706f is the unpinned-site refusal this pin answers (ci-autofix.md); its `## Red checks` mutation line already names the 7 sites and the pin as the resolution. The trigger is answered.
- (4) `merge_train.py classify 2e4f3ebe0811a3b1a079c41ec269233ac5395871` exited 0: `GREEN ... pending: none red: none` (ev/classify-last.txt; ev/classify-1.txt is the first WAIT). Check runs at this head show no failure conclusion.
- `git merge-tree --write-tree origin/main 2e4f3ebe0811a3b1a079c41ec269233ac5395871` exit 0, tree 48a3d0b090e7fdde6f697624c0d6e3e4029df692, no conflict (ev/merge-tree.txt).
- Review packet rendered at this head: refusals none, advisories none, carry_audit 3 routed 0 unrouted (ev/packet-render.txt).
- Head re-read before publishing: origin/fix/r10-hotfix-learner-inputs is 2e4f3ebe0811a3b1a079c41ec269233ac5395871, the head measured (ev/HEAD.txt).
