Fix review: merge 129cc1217e8cae19b4c43d821e535d3018727d34

bus-nonce: 0ca7375151740a80e4419dd4be9eeb6b

Round 2 (delta review): `git diff d554d42e9a645841ccf87da65d24fb1b6660f9a9 129cc1217e8cae19b4c43d821e535d3018727d34`, against the round-1 block on `verdict/3925` (cac388888b).

## Prior block: resolved

- The round-1 block was mutant F: delete `const.CONF_RADIATOR_POWER_FRACTION,` from `TWO_ZONE_FIELDS`. The delta pins the four keys literally in `_zg_values`, independent of the constant, and adds a check that the presence rule's output equals that literal set. The refusal loop and the "wrote nothing" check now drive the literal set, not the rule's output.
- Re-run at the head: full `tests/features.py`, in a `git archive` export of 129cc121 with mutant F applied (`ev/mut_F.patch`), gives `4 of 6285 FEATURE CHECKS FAILED` rc=1 (`ev/mut_F_features_full.txt`). Three of the four are this block: `the presence rule turns an auto config two-zone on each of the four zone keys` [rule=3 keys, pinned=4], `set_thermal_parameters refuses radiator_power_fraction on a single-zone entry` [returned None instead of raising], and `the refused calls wrote nothing` [options include radiator_power_fraction]. This matches the body's round-2 answer.
- Null control: the unmutated head export gives `1 of 6285 FEATURE CHECKS FAILED` (`ev/features_head.txt`). That one is `#363 ... stamps a resolvable recorded_at` [recorded_at = 'unknown']. It fails the same way in both exports and comes from the export having no `.git`, not from this PR. All 13 ZONE-GATE checks pass at the head.

## Delta otherwise

- `services.py`: docstring only. One sentence over 40 words is split, and the meaning is unchanged.
- `tests/features.py`: the literal pin above, plus a comment that states the design choice. The comment is accurate.
- `tests/mutation_ledger/killed_by/`: two pins from `mutation-autofix` (github-actions[bot] commit 206656165f), `services.py` BOOLOP killed by entities.py and `thermal_model.py` RETURN_DEL killed by stress.py. Both are records the lane wrote, and neither needs judgement.
- No production behaviour changed in the delta.

## Findings

none

## Evidence

- RESULT head reviewed: 129cc1217e8cae19b4c43d821e535d3018727d34 (`ev/HEAD.txt`), the head the packet was rendered at. The PR head has since moved to d50ab75eebbf, which the coordinator reports as a bot commit. This verdict is for 129cc121 only; the carry to the new head is the coordinator's `review_carry` step.
- RESULT ancestry: d554d42e9a is an ancestor of the head. The delta is 5 commits: test, merge, bot pin, comment split, merge. `git merge-tree --write-tree origin/main 129cc121` exits 0. `dev/governance/roles/` is unchanged on main since the merge base.
- RESULT CI at 129cc121, read live:
  - `tests / mutation` is red with `MUTATION TABLE REFUSED`: `services.py:663` and `:666` GUARD_OFF are ADDED UNPINNED. That is the class `mutation-autofix` repairs (in progress at read time), and the body predicts it under `## Red checks`. The body names both sites as killed.
  - `gate` reads `FAIL run(s) [45935233265] at this head are still being judged`. It waits on the run above and is not an independent red.
  - `tests / nightly-status` is red on nightly-ha/slow lanes from run 45911887743. That check is not required and is unrelated to this PR.
- RESULT not re-run: the finder's harness `probes_p2.py` and mutants A to E. The production tree is unchanged since round 1, where both were verified. The body reports A to E re-run at 56ced7a0a9, still failing.
