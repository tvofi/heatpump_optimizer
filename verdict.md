Fix review: merge 12a6617f07eee3a0b909de458020fac4df611858

bus-nonce: ce1f9506d28e9647e8c4fdca26a8dd92
pending-ci: gate

## Summary

Delta round over the blocked head a07c37b273744ade8cc2c48d07d4a79c58365196 (second round). Both items of that verdict are resolved at 12a6617f07eee3a0b909de458020fac4df611858.

1. Class-open, range cap read as a step gap: resolved. `OffStepNotice.check` now also requires `write.above_c >= target` (legionella.py:100). Previous verdict's own probe re-run at this head: entity `{"min":30,"max":60,"step":1}`, disinfection 65, after one observe pass and `raise_unreachable_issue(60, 65)`: standing = `dhw_legionella_above_setpoint`, `dhw_legionella_unreachable` (ev/probe_entity_max_head.txt). This matches the base. New pins cover the capped row under both credit rules, the unreachable notice standing, a null on a max-80 step-5 entity, and an entity-range census (min 30/60, max 55-80, steps 0.5/1/5, disinfection 55-70, both rules). The census uses an independent oracle written with math.floor/ceil.
2. The `below_c` rounding survivor: resolved. Dropping `rounding="down"` from `below_c` in `pump_arbiter.cycle_write` now fails two checks: "63 on step 5 is named below 60 and above 65" and the census (ev/mutants_delta.txt).

## Evidence

- Round: second, delta (`git diff a07c37b2 12a6617f`). Production delta: legionella.py only (one predicate clause and its docstring). The rest of the delta is main's merge (VERSION, notes, manifest, card, claim files, features.py, all reached through merge-base c987209cc7), tests/guard_pins.py, ledger pins and an instrument (check-wave-script.mjs). Scope is not widened. The added clause can only suppress the notice, never raise it, so the one already-reviewed code it affects is the unreachable notice's yield. The capped-row pin and the probe show that yield is restored, not newly at risk.
- Head: 12a6617f07eee3a0b909de458020fac4df611858, measured in a detached worktree (ev/HEAD.txt).
- RESULT `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` at head: ALL 84 GUARD PIN CHECKS PASSED (ev/guard_pins_head.txt). The census figures 1632 rows and 154 raised are asserted by a passing check, so they are re-derived by it.
- Mutants, one at a time, each restored (ev/mutants_delta.txt):
  - `below_c` rounding dropped: killed, 2 fail.
  - range gate clause deleted: killed, 3 fail (census reads 683 of 1632).
  - gate re-read on `below_c >= target`: killed, 6 fail.
  - `>=` changed to `>`: survives, ALL 84 PASSED. Judged equivalent (next item).
- Equivalence of the `>=` -> `>` survivor, judged on the full entity-range domain with my own instrument (ev/equiv_probe.py, ev/equiv_probe.txt).
  - Domain: every Celsius entity with min in {5,20,30,40,55,58,60,62,65,66,70} (min-capped rows included), max in {50..90} (off-step maxima 57, 63, 67 included), step in {0.1,0.5,1,2,2.5,3,5,10}; Fahrenheit entities with min/max in °F and steps 0.5-10; disinfection 55-70 by 0.5; everyday set-point 40-70; both credit margins.
  - RESULT rows=650628 head_raised=60340 rows_with_above_eq_target=130986 head_vs_gt_mutant_differ=0 head_vs_alternative_differ=0.
  - The `above_c == target` boundary is reached 130986 times, and the mutant never changes the outcome. The fixer's alternative predicate (`below_c < above_c`) also agrees with the head on every row.
  - Why it holds: `above_c == target` means the target is on the step and inside the entity's range. `written_c` is the cycle temperature (>= target) rounded down under `dhw_hard_max_temp = min(70, cycle) >= target`, so it lands at or above that same on-step target, and the short-of-credit clause is false. The argument needs the target to be at most 70, which the config schema enforces (`_number(55, 70, 1)`, config_flow.py:1794).
  - The survivor is acceptable. The alternative predicate is not required.
- Outside the schema (disinfection > 70, ev/equiv_probe_over70.txt): RESULT rows=83952 head_raised=15759 head_vs_gt_mutant_differ=10539 head_vs_alternative_differ=10539. There the 70 °C hard maximum binds and the head raises an off-step notice naming below = above = target. This is unreachable under the 55-70 slider, it was not introduced by this delta (the a07c37b2 predicate fired there too), and the alternative predicate would close it as well. See Findings.
- PR body `## Head` names 12a6617f07eee3a0b909de458020fac4df611858, the head measured here. Its `## Forward-carry` and `## Friction` read none. carry_audit check ran on an excerpt of the body holding those sections plus this verdict: rc 0, 1 routed.
- The body's equivalence argument for `>=` -> `>` matches the one I re-derived, and so does its reliance on the 55-70 slider. Its own probe-only second survivor (`above_c >= target - margin`) is not on the ledger and not in the brief, and I did not re-measure it. The body's "Not measured: Fahrenheit" is covered for this predicate by the °F rows of ev/equiv_probe.py.
- `git diff $(merge-base)...origin/main -- dev/governance/roles/`: empty. The contract is current.
- `git merge-tree --write-tree origin/main 12a6617f`: clean, tree 4ebf9a56e0, against origin/main 513a07dfdc.
- VERSION, manifest, RELEASE_NOTES.md and tests/golden: untouched three-dot from merge-base c987209cc7 (ev/version_untouched.txt).
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt). structure_budgets.json is not in this delta.
- CI: `merge_train.py classify` printed `WAIT 12a6617f07eee3a0b909de458020fac4df611858 pending: gate red: none` on every poll from 03:37 to 04:06 UTC (ev/classify_log.txt), so this verdict carries `pending-ci: gate`. No red, so no `## Red checks` answer is owed. `merge_train.py owed-reds` is in ev/owed_reds.txt.
- Not re-derived: `Architecture score: dS` and the translation parity count. Neither is in the delta.

## Findings

- Follow-up: on a disinfection temperature above 70 °C (outside the config schema's 55-70 range), `OffStepNotice.check` reads the 70 °C hard-maximum cap as a step gap and names below = above = target. The fixer's alternative `below_c < above_c` (or the `>` form) would make that domain correct and every CMP mutant killable. Carry: dismissed: unreachable under the 55-70 validated slider (config_flow.py:1794) and pre-existing at the reviewed head, not introduced by this delta
