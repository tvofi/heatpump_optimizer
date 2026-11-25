Fix review: merge f5744c8cf9d6607b195f45f012132bffec5d43d8

bus-nonce: 9796121a705c12e87eb0e8dd18403253

## Scope

The packet's `## Review scope` line reads `full`: no verdict on the verdict refs names the reviewed head fa76fdc4b0dd857aabf359118d5f0f84cea8d352, so this is a full review of R11-OUTSIDE-3849 at f5744c8c, not a delta-only round. f5744c8c is a merge of fa76fdc4 into ef0cd459, and its tree equals fa76fdc4's (`89ecf0b2da57aa89c0b44d51e0f6029a759ad8d7` for both, `ev/trees.txt`). The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Evidence

- RESULT CI: `merge_train.py classify f5744c8cf9d6607b195f45f012132bffec5d43d8 --pr 3877` printed `GREEN f5744c8cf9d6607b195f45f012132bffec5d43d8 pending: none red: none`, rc 0 (`ev/classify.txt`). The packet digest's only failure, `tests / nightly-status`, is not in `merge_train.py owed-reds`.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0 (`ev/merge-tree.txt`).
- RESULT version: the three-dot diff from 24e3f37620f8 moves none of `VERSION`, `manifest.json` or `RELEASE_NOTES.md`.
- RESULT goldens: the diff touches nothing under `tests/golden/` and neither claim file, so step 4 has no moved fixture to compare.
- RESULT mutation proof (step 1): I re-ran it at this head in fresh worktrees through the body's block command, `features_block.py "from types import SimpleNamespace as _DspNS" "# R11-OUTSIDE-HONEST-STARTS-RUNS, the descents"`:
  - Unmutated: `ALL 105 FEATURES BLOCK PASSED`.
  - M1 (`Direction.priced` returns `self.p if self.usable else 0.0`): `6 of 105 FEATURES BLOCK FAILED`. The failing checks are the shrink, issue-3849, grid, order/merge, 16-state census and full-optimize checks.
  - M2 (`leg_rule` stops `[p > 0 for p in stop_probability]`): `5 of 105 FEATURES BLOCK FAILED`. The failing checks are order/merge, per-direction mask, census, arbiter 3849 step and full optimize.
  - Both counts match the body (`ev/mutant-M0.txt`, `ev/mutant-M1.txt`, `ev/mutant-M2.txt`). I did not re-run M3-M8; CI's `tests / mutation` is green at this head.
- RESULT harness (steps 2, 3): no finder's harness is named. The fixer's harness `dev/audit/harnesses/r11_outside_3849_unlatched_price.py` was run at this head and from a 24e3f37620f8 checkout with the head's harness file:
  - At this head: `read ((0.2857142857142857, 0.0), (0.0, 0.0)) mask (True, True) leg rule ('dhw', None)`, split excess 0.2857.
  - At the base: `read ((0.0, 0.0), (0.0, 0.0)) mask absent`, split excess 0.0000.
  - Empty learner (null control): 0.0000 with `('dhw', None)` on both trees.
  - These are the body's figures; the body measured them at e6e83c39 and at e3cb5c01 (`ev/harness-head.txt`, `ev/harness-base.txt`).
- RESULT seams (step 6): every reader of `duty_switch_stop_probability`, `duty_switch_off_seconds` and `duty_switch_unlatched` in `custom_components/` is listed by `grep -n` over the package. They are `optimizer._priced_stops`, `_leg_rule`, `_stop_availability` (line 283), `_avoid_priced_switches` (248), lines 361, 448 and 5094, and `duty_switch.config_fields`.
  - The off-time readers get 0 for an unlatched direction from `planner_pairs`, as the body states.
  - `_leg_rule` swaps `priced_pair(stops, 1.0)` for `_priced_stops(opt) or (0.0, 0.0)`. Both read the same `priced_pair(..., 1.0)`, and `None` only where the max is 0, so the result is the same.
  - The arbiter (`DutySwitchLearner.split`) and the planner read one `leg_rule` with the same mask.
- RESULT budgets (step 14): `class_excess_loc` 17301 -> 17300 and `module_excess_loc` 21775 -> 21774, both down, with no raise. The line paid is the shortened history comment above `_step_clock` in `optimizer.py`.
- RESULT forward-carry (step 10): the body's carry to R11-OUTSIDE-HONEST-DHW-RUNS is in `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r11-roster`. It is stated with its control: split excess 0.0000 at e3cb5c01 and 0.2857 at the head.
- RESULT actuator (step 16): no new refusal on an actuator write.
- RESULT head (steps 7, 12): the body's `## Head` names f5744c8c and fa76fdc4, which is what I measured. The PR head was f5744c8c when I read it.

## Findings

none

## Friction

none
