Fix review: blocked d713ca529a8803eae031184d7f34f49ea5085fa3 equivalence-refuted: the survivor_triage row's `above_c >= target` to `>` mutant is not equivalent; set_thermal_parameters admits a 71-75 disinfection temperature, where the head raises an off-step notice reading "below 75, above 75" for a 70 C hard-cap shortfall and the mutant raises none

bus-nonce: 71da675d8fa743db8b13fbf27b145482

## Block

Scope: delta `git diff 12a6617f07eee3a0b909de458020fac4df611858 d713ca529a8803eae031184d7f34f49ea5085fa3`, one file: `tests/mutation_ledger/survivor_triage/legionella.py/OffStepNotice.check.CMP_BOUND.03f00051.json`, verdict `equivalent`. The dispatch names the prior verdict `Fix review: merge 12a6617f07` (on probe/rev-3581-ce1f9506). The packet's scope line reads `full` only because verdict/3581 does not carry that verdict yet. The merge d713ca52 merges 4328fc4245 into its own parent 12a6617f07, so main contributes nothing.

The row's argument assumes `dhw_legionella_temp <= 70`, taken from config_flow's 55-70 slider. That bound is not the domain. `services.py:502-503` (`set_thermal_parameters`) accepts `dhw_legionella_temperature` in `vol.Range(min=55, max=75)`. `coordinator._THERMAL_PARAM_CONVERSIONS` passes it to `ThermalParameters.dhw_legionella_temp` as a `float` and clamps nothing.

For any target T in (70, 75]:
- `dhw_hard_max_temp` = min(70, cycle) = 70 < T, so `written_c` = 70.
- On an entity whose range reaches T and whose step holds T, `above_c == T`.
- So `written_c < T - margin` holds, and `above_c >= T` holds while `above_c > T` does not. The arms differ on reachable input.

Probe: `ev/probe_75.py`, using guard_pins' own `_step_notice` driver; entity min 30, max 80, steps 1, 5 and 0.5.
- Head (`ev/probe_75_head.txt`) raises `dhw_legionella_off_step` on, for example, everyday 55, disinfection 75, step 5: `{'legionella_temp': '75', 'written': '70', 'step': '5', 'below': '75', 'above': '75'}`.
- Mutant (`ev/probe_75_mutant.txt`) raises nothing there. The two differ on 10 of 18 rows (`ev/probe_75_diff.txt`).
- `tests/guard_pins.py` under the mutant: `ALL 84 GUARD PIN CHECKS PASSED`, rc=0 (`ev/guard_pins_mutant.txt`). Nothing pins the gap.

The head's behaviour on these rows is also the PR's own defect class. The `OffStepNotice` docstring says "where ... no step is the remedy ... the unreachable notice's advice stands". Here the shortfall is the 70 C hard cap, not a rounding gap. Yet the head raises the off-step notice, which clears `dhw_legionella_unreachable` and tells the user to pick 75 from two on-step choices that are both 75, the temperature they already chose. This is the 70 C counterpart of the range-cap block at a07c37b273 (verdict/3581, 65d48606).

A sound repair would do one of these, then pin a row with a target above 70 so the gate kills this mutant:
- make the gate also require that the step above is at or below the hard maximum, e.g. `above_c <= params.dhw_hard_max_temp`; or
- bring the service range into line with the 70 C hard maximum (`services.py` max 75 to 70), as a separately justified change.

The PR body's `## Unpinned sites` and `## Mutation proof` repeat the same `<= 70` premise. They need re-wording with the repair, along with the `range_gate_above_minus_margin` survivor's equivalence argument, which rests on the same bound.

## Evidence

- RESULT: the mutant is distinguishable on service-reachable input. Head and mutant differ on 10 of 18 probe rows, and guard_pins passes 84 of 84 under both (head: `ev/guard_pins_head.txt`).
- `git merge-tree --write-tree origin/main d713ca52`: rc=0, no conflict (`ev/merge_tree.txt`).
- `merge_train.py classify d713ca52 --pr 3581`: `WAIT d713ca529a8803eae031184d7f34f49ea5085fa3 pending: gate red: none` (`ev/classify.txt`). CI was not waited out because the block does not depend on it.
- The red `tests / mutation` at 12a6617f07 is in the owed-reds set (`ev/owed_reds.txt`), and the body's `## Red checks` answers it: it names the check and a cheaper detector (prepr ci_predict / step 6d) with its standing cost. That paragraph contains two "The cheaper detector is ..." sentences, which is redundant but not contradictory. The answer is only as sound as the equivalence claim it relies on, which is refuted above.
- Body `## Head`: 4328fc4245 is ledger only; `git diff --stat 12a6617f d713ca52` lists exactly the one row.
- Ingress and cap: `ev/service_range.txt` (services.py 500-504) and `ev/hard_max.txt` (thermal_model.py 885-894).

## Findings

none

## Friction

- The review packet rendered `Review scope: full` because the prior merge verdict at 12a6617f07 exists only on probe/rev-3581-ce1f9506 and not on verdict/3581. I followed the dispatch's delta scope.
