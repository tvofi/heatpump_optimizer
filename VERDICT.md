Fix review: blocked a07c37b273744ade8cc2c48d07d4a79c58365196 class-open: OffStepNotice's predicate reads an entity range cap as a step gap: max 60 under a 65 disinfection temperature raises the off-step notice and suppresses the unreachable notice's correct hardware advice

bus-nonce: 591f84c2ebf5735b319c586e140c7663

## Block

`OffStepNotice.check` raises when `cycle_write(...).written_c < target - margin`. That predicate does not test what the notice says it tests, the step. `written_c` is `dhw_step_target_c`, and `SetpointGrid.bounded` also clamps it to the entity's own maximum (`high_c`). `below_c` and `above_c` are clamped the same way. So on a hot-water set-point entity whose `max` is under the disinfection temperature, the notice fires on any step, including 1 and 0.5. This setup is common: many pumps cap the hot-water set-point at 55-60 °C and leave the last degrees to an immersion heater. The notice then tells the user the temperature is "between the hot water set-point's steps", that "no immersion heater is needed", and to pick 60 °C "to keep disinfecting at least as hot as you chose" (above = below = 60, under the chosen 65). It also clears `dhw_legionella_unreachable` and keeps it down. That notice's immersion-heater advice is the correct remedy here.

Measured with `tests/guard_pins.py`'s own `_step_notice` and stub hass (ev/probe.py, ev/probe2.py, output in ev/probe_entity_max.txt):
- head: entity `{"min":30,"max":60,"step":1}`, everyday 55, disinfection 65, both credit rules: notice raised, `written 60, step 1, below 60, above 60`. The same happens at step 5 and at step 0.5 (everyday 50).
- head, after one observe pass and then `raise_unreachable_issue(60, 65)`: standing = `dhw_legionella_above_setpoint`, `dhw_legionella_off_step`. The unreachable notice is suppressed.
- base 50373173d4, same probe: standing = `dhw_legionella_above_setpoint`, `dhw_legionella_unreachable`.
- control: the same config with entity `max` 80, step 1: no notice under either rule. The trigger is the range cap alone.

This is a regression from base on a realistic configuration. The slider and harness grids never reach it, because every row uses a 30-80 °C entity. The body names no enumeration over the entity's range (fixer.md step 8). The notice's domain should be the step gap only. One way to do that: raise only when the on-step value above the target is itself writable (`above_c >= target`, or the `hi` clamp did not bind). That would leave a range-capped write to the unreachable notice. Pin it with an entity-max row and its null.

## Findings

- Surviving mutant, already disclosed in the body: in `pump_arbiter.cycle_write`, dropping `rounding="down"` from `below_c` (nearest) leaves `ALL 79 GUARD PIN CHECKS PASSED` (ev/mutants.txt). The `{below}` placeholder for a target nearer the upper step, such as 63 on step 5 (would read 65 rather than 60), has no pin. Pin it with a row whose nearest step is above the target, alongside the range-cap repair. Carry: R10-DISINFECTION-STEP-NOTICE

## Evidence

- Round: first, full review, of the handoff before its pull request. There is no review packet, no PR and no CI to read. `merge_train.py owed-reds` prints the required set (ev/owed_reds.txt), but no check has run on this head, so no red is owed an answer. The body's `tests / closures` note about the weekend clock (PR 3578) is not this branch's red and is not judged here.
- Head: a07c37b273744ade8cc2c48d07d4a79c58365196, measured in a detached worktree (ev/HEAD.txt). It matches the body's `## Head`.
- `git diff $(merge-base)...origin/main -- dev/governance/roles/`: empty. The contract is current.
- `git merge-tree --write-tree origin/main a07c37b273`: rc 0, tree 0713a5ffba. It merges cleanly with origin/main 8af37bdf44.
- RESULT `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` at head: ALL 79 GUARD PIN CHECKS PASSED (ev/guard_pins_head.txt). This re-derives the body's 201/436 of 1750, 34/71 of 330, the 1314 and 169 on-step nulls and the other nulls, since each count is asserted by a passing check.
- RESULT `python3 tests/structure.py`: class_excess_loc 17502 <= 17502, STRUCTURE RATCHET PASSED (ev/structure.txt).
- Mutants (ev/mutants.txt), one at a time, each restored. Killed: margins swapped in `check`; cycle predicate set to True; unreachable raised under off-step; unreachable not cleared; memo set to `if False`; `<` changed to `<=`; `above_c` rounding dropped; hard maximum dropped. Survived: `below_c` rounding dropped (see Findings).
- Merge resolution read: `cycle_write` is re-expressed on main's `setpoint_grid`, `dhw_step_target_c` and `SetpointGrid.bounded`. Main's `_bounded`, `_grid`, `_dhw_write` and `_dhw_target` are untouched in the three-dot diff.
- VERSION, manifest, RELEASE_NOTES.md and tests/golden: untouched (ev/version_untouched.txt is empty).
- Not re-derived: the 1509-key translation parity; `Architecture score: dS +0.0000`; the base-vs-5c961851a2 harness `cmp`; the failing-test-first `8 of 79` at base. The block does not depend on any of them.
