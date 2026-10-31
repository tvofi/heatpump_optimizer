Fix review: merge 979797ad1dcfb0d8ba80f3c131d5076e4b7b2782

bus-nonce: c1347e9d1fc869fc0d35783023a2b0b9

## Scope

PR #3006 (R10-COP-PARTLOAD part 2), round 5 delta review at head 979797ad1dcfb0d8ba80f3c131d5076e4b7b2782, from detached worktrees at that SHA. The last merge verdict was at a6be5baa55e41507a7dec1ffec7b88a660167e15. `review_carry.py a6be5baa5 979797ad1dcfb0d8ba80f3c131d5076e4b7b2782` prints FRESH-REVIEW (1 of 6 branch-only commits carries code: 1ba5e7ef3, the structure re-record). The roles diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- budget-raise-gate is red at this head and keeps `gate` red: the D2 policy-cap raise (`dev/governance/config/policy_budgets.json`, unchanged since round 1) still needs the owner's approving review at this head, or the orchestrator's approval under mandate 6329234399. The body answers it under Red checks as the approval mechanism by design. This review does not settle the approval. Carry: dismissed: owner-approval precondition, already answered in the body and owed to the orchestrator/owner at merge time, not a defect in the authored work

## Evidence

- Delta: `git merge-tree --write-tree origin/main a6be5baa5` gives tree 9b6944031f84 (the claimnotes/ledger driver resolved structure_budgets.json and closures.json). Diffed against the head, the only change is `tests/structure_budgets.json` (2+/2-), `max_class_loc` 8060 -> 8059 and `recorded_at` (ev/delta-vs-A-merged-main.txt). The three-dot code diff (custom_components, tests/features.py, tests/mutation_ledger) at the head matches the one at a6be5baa5 except for blob ids and hunk offsets (ev/code-diff-A-vs-H.txt).
- Budgets, three-dot against main: `class_excess_loc` 17655 -> 17653, `max_class_loc` 8060 -> 8059, `recorded_at` moved. No key in tests/structure_budgets.json rises.
- RESULT structure.py at head: `STRUCTURE RATCHET PASSED`; RESULT class_excess_loc=17653, RESULT max_class_loc=8059, both at their budgets (ev/structure.txt). At origin/main 7539d1675: RESULT class_excess_loc=17655, RESULT max_class_loc=8060 (ev/structure-main.txt). So the measured values justify the lowering. The branch's own coordinator line saving (has_hum/hum pair) gives the -1 on main's tree, and nothing raises a budget.
- Mutation proof, re-run at this head with tests/features.py (PYTHONPATH=tests/hastub):
  - base: `ALL 4673 FEATURE CHECKS PASSED`.
  - A0 (the derate branch of `added_power_for_heat_per_cop_kw` deleted): `4 of 4673 FEATURE CHECKS FAILED`. They are the increment round trip, cheapest-first, floor repair and buffer-cap tightening, as the body states (4 of 13).
  - C1 (`_capacity_caps` back to `float(entry[0]) / cop_i`): `1 of 4673 FAILED`, the capacity-caps check, cap 4.0 against nameplate 5.0, as the body states.
  - Mutant diffs and logs: ev/mutant_*.diff.txt, ev/features_*.txt.
  - The count 4673 differs from the body's round-2 4618 because main added checks since then.
- Null control, zero-derate arms: each mutant's failing checks carry their own d=0 null arms, and the base run passes them. The finder's harness was not re-run. The production code is identical to the verdicted head's (above), so the earlier verdict's harness figures carry over.
- Claim files: tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to origin/main (ev/claims.txt). The three-dot diff touches no file under tests/golden/, VERSION, RELEASE_NOTES.md or the manifest (ev/claims-version-diff.txt is empty). I could not run `env_drift.py --all` locally (a baseline worktree add exited 129). With no golden fixture in the diff, CI's `tests / fast (3.14)` green covers it.
- Merge: `git merge-tree --write-tree origin/main 979797ad1dcfb0d8ba80f3c131d5076e4b7b2782` exits 0, tree 5c361eb7ed1a (ev/merge-tree.txt).
- Scoped gate mode line: `python3 tests/closure.py select --diff 7539d1675` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (ev/mode.txt).
- CI, this head only:
  - `merge_train.py classify` exited 1: `RED ... pending: none red: gate` (ev/classify.txt).
  - Both `gate` runs (124621652043 kind code, 124622205678 kind edit) print exactly one FAIL, `budget-raise-gate / budget-raise-gate: failure`.
  - Every other lane concluded success or skipped: tests/fast (3.14), closures, coverage, mutation, typing, browser, replay, instrument-self-tests, arch-score, policy-docs, wave-script, codeql, hassfest, validate-hacs.
  - `pr-contract` 124621997526 started 18:33:23Z, after budget-raise-gate concluded red at 18:32:30Z, and is green. So the body's answer to that red was checked (step 11).
- The body's Head section names 979797ad1dcfb0d8ba80f3c131d5076e4b7b2782. The branch head re-read at post time is 979797ad1dcfb0d8ba80f3c131d5076e4b7b2782 (ev/head-at-post.txt).
- Round: this is round 5's delta review of a carried code head. The code was last re-cut in round 2; rounds 3-5 are main merges and budget re-records only.
