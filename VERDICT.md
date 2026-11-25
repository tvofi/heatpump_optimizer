Fix review: blocked 392fe0b7eb427ab84c9d4971256defe611b9a839 metric-gamed: structure: module_excess_loc 21756 is met only by ec6be8dbdf's re-wrap of optimizer._leg_rule's call

bus-nonce: 5e1012c3a47b5bc870dc9f56b6b7740b

## Summary

This is round 3, a delta review: `git diff 1d3b7925 392fe0b7`. My round-2 verdict at 1d3b7925 was `merge` with `pending-ci: gate`. Since then the fixer has merged two mains, 02fc3cde92 (clean) and c0a750fa6e (three production content conflicts, resolved by hand). The fixer has also made three repair commits: ec6be8dbdf, a production and test repair; 180da49d41 and 54a8c81c15, pin drops; and b736a6addc, pins. The rest of the range is main's own history, plus `mutation-autofix`'s f4ec7bf618.

I read the merge resolution of `duty_legs.leg_rule`, `duty_switch._fields` and `optimizer._leg_rule` / `OptimizationConfig`. It is the union both sides intend: main's `unlatched` mask goes third, and this PR's `heat_min`, `dhw_min` and `before` come after it. Main's `both_step_legs` stays deleted. Eight mutants on the resolved lines test it: six are killed in the two blocks, R4 is killed by the full suite, and R6 survives the full suite (see Block).

## Block

1. **metric-gamed: structure: module_excess_loc** (step 14).
   - The merged ledger sets `module_excess_loc` to 21756 (`LEDGER-MERGE: ... 21775 + both deltas = 21756`). That figure assumes the conflict resolution adds no line, but the union of the two `_leg_rule` calls adds one.
   - ec6be8dbdf pays that line by re-wrapping the call's arguments onto fewer lines ("_leg_rule pays the ratchet's line"). Nothing else in the code changes.
   - Removing the mechanism the commit names: with only that re-wrap reverted at the head, `tests/structure.py` prints `FAIL module_excess_loc 21757 > 21756 (+1)` (`ev/structure_rewrap.txt`). So the re-wrap alone is what meets the recorded budget.
   - `module_excess` (tests/structure.py:3022) counts physical lines, `tree.body[-1].end_lineno`. So re-wrapping any call in a module over the limit makes the same move with nothing improved, and the diff's change is exactly that shape.
   - Owed: revert the re-wrap, or pay the line with a change that improves code. Otherwise record `module_excess_loc` at the measured 21757 with the reason in the commit message. That is still 6 below the merge base's 21763 (d3d66c40), so it is not a raise. The body's "pays the merged tree's `module_excess_loc` +1" line must then say which one was done.
2. **Surviving mutant on a line the merge resolution wrote, which CI's mutation lane cannot draw** (step 1, widened per step 12).
   - The site is `custom_components/heatpump_optimizer/duty_legs.py`, `leg_rule`'s return line, which c0a750fa6e rewrote. The mutant is `leg_minimum(heat_min), leg_minimum(dhw_min), before)` -> `... IDLE)`. It survives the whole `tests/features.py`. The only FAIL is `_bootstrap`, which the body records as failing outside `run.sh`'s interpreter, and it fails identically under R4 (`ev/full_suite_R6.txt`).
   - The mutant is not equivalent (`ev/R6_equivalence.txt`). Take minimums 10/10, a both step whose hot-water share is 6 min, and the pump in a hot-water leg as the solve starts. `plan_legs` serves `(('dhw', 6.0), ('space', 9.0))` with `before=DHW` and `(('dhw', 10.0), ('space', 5.0))` with `before=IDLE`.
   - The arbiter reads `before` from `rec.solve_before` (`duty_switch.leg_rule`). The planner reads it only through this argument and `optimizer._leg_rule`'s `opt.config.duty_leg_before`. With this argument dropped, the planner prices a lengthened hot-water leg that the arbiter does not serve. That breaks the body's "planner and arbiter read one rule", and no check notices.
   - Its operator (an argument replaced by a constant) is not one of the mutation lane's operators, so `tests / mutation` cannot report it.
   - Owed: a check that drives `optimizer._leg_rule` (or a solve) with `duty_leg_before` set to the pump's hot-water leg, failing with the argument dropped, plus its null control.

## Findings

none

## Evidence

- Head reviewed: 392fe0b7eb427ab84c9d4971256defe611b9a839 (`ev/HEAD.txt`), the PR head at read time, as the body's `## Head` names. Merge base d3d66c40. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. This is round 3. My round-1 block at 8ca95413 and round-2 merge at 1d3b7925 came before it.
- Step 13: `git merge-tree --write-tree origin/main 392fe0b7` at origin/main 91f6e91bea exits 0. The output reads `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt` and `LEDGER-MERGE: resolved` for structure_budgets.json and closures.json (`ev/merge_tree.txt`).
- Merge-resolution mutants (`ev/mutant_driver.py`, run over the R11-OWNER-MODE-LEGS block, whose baseline is ALL 19 PASSED, and the R10-DUTY-SWITCH-PLANNER-PRICE / issue-3849 block, whose baseline is rc 0). Results are in `ev/mutants_merge_resolution_{ml,dsp}_block.txt`:
  - R1, `leg_rule`'s off time read from the unmasked stop (the branch's pre-merge side): KILLED, 4 checks.
  - R2, `leg_rule` ignores `unlatched`: KILLED, 5.
  - R3, the planner's `_leg_rule` mask -> `(False, False)`: KILLED, 2.
  - R5, `heat_min` dropped: KILLED in both blocks.
  - R7, `split()` ignores `unlatched`: KILLED, 3, including ec6be8dbdf's rewritten issue-3849 arbiter check (`[['space', 'space', 'dhw', 'dhw']`). That shows the `both_step_duty` -> `served_leg` rewrite still separates.
  - R8, the planner's stops -> `(0.0, 0.0)`: KILLED, 7.
  - R4, `_fields` drops the learner's `**fields`: survives both blocks, but the full `tests/features.py` kills it with 2 coordinator checks ("the coordinator passes the learner's read ...", "the coordinator passes the unlatched mask with the pairs ..."), `ev/full_suite_R4.txt`.
  - R6: see Block 2.
- Previous finding (M17, `duty_switch.py:592` `current == wanted`): dismissed as equivalent in round 2. The delta does not touch it.
- Step 5: three-dot `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. `tests/golden/claimed_drift.txt` keeps the branch's `config_flow` claim, and `claims-for: 10.1.3` equals `VERSION`. The card claim file's two-dot delta is main's (R11-OWNER-CARD-EXTERNAL-HEAT).
- Pin repairs: 180da49d41 drops main's two pins on returns the merge replaced, b736a6addc adds 5 pins, f244a4b7b5 merges the bot's f4ec7bf618, and 54a8c81c15 drops the bot's stale `leg_rule` CMP_BOUND pin. This is consistent with the head's `tests / mutation` log, which reads `MUTATION TABLE REFUSED -- 1862 unpinned site(s) against 1851 ..., 12 of them added by this diff`. That count equals the body's Unpinned sites (9 lines, 12 mutants).
- Step 11, owed reds (`merge_train.py owed-reds`). The body's `## Red checks` names and answers `tests / mutation`, through the `mutation-autofix` path that pins new sites, which is in `ci-autofix.md`. It also names and answers `tests / fast (3.14)` at 1aa635d275 and `codeql / Analyze (python)` at f4ec7bf618, and I checked that each was answered. `gate` reads failure in the packet digest, but `merge_train.py classify` reads `WAIT 392fe0b7... pending: gate red: none` on every poll from 21:37Z to 22:22Z (`ev/classify_poll.log`). `nightly-ha` and `nightly-status` are not in the owed set.
- Step 14 controls: `tests/structure.py` at the head prints `ok module_excess_loc 21756 <= 21756` and `STRUCTURE RATCHET PASSED`. With ec6be8dbdf's optimizer hunk reverted it prints `FAIL ... 21757 > 21756 (+1)` (`ev/structure_rewrap.txt`).
- Step 2: there is no finder's harness, because the issue is an owner feature. The delta does not touch `dev/audit/harnesses/mode_legs.py`.
- Step 10: the carries to R11-OWNER-FAULT-HOLD and R11-OWNER-FROST-HOLD are unchanged since round 2. The packet's carry_audit reads `3 routed, 0 unrouted`.
- The body's figures in `## Gate at head` (`ALL 2763 ENTITY CHECKS PASSED` at b736a6addc, `ALL 6190 FEATURE CHECKS PASSED` at 180da49d41) were not re-run as such. My two full `tests/features.py` runs at the head were mutant runs.

## Friction

none
