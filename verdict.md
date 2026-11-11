Fix review: blocked 0aed6ccbc99c5a3210dcb1caf013ea0d7c5ceed5 null-control-leak: _dhw_write now rounds an off-step everyday set-point up on a cycle whose disinfection temperature is below it, everyday 57 disinfection 50 step 5 writes 60 where 49a45dd8 and the no-cycle row write 55, above dhw_hard_max_temp 57

bus-nonce: 9ead2e4daa822a7b8994a7ff1cf637fb

## Block

Round 2, a delta review. It covers 49a45dd8a8aad27f63b797bc747e79d9246e439a to 0aed6ccbc99c5a3210dcb1caf013ea0d7c5ceed5. `review_carry.py` answers FRESH-REVIEW because `8da43a2fe` changes `custom_components/heatpump_optimizer/pump_arbiter.py` `_dhw_write`. The widened scope is that function's cycle write.

`8da43a2fe` drops `or cycle <= everyday`, so every cycle write is now rounded up. The body justifies this for one case: everyday 60.4, disinfection 60.2, step 1. There the nearest step (60) falls below the disinfection target, which the guard's credit test needs. But `dhw_cycle_temp` is `max(dhw_setpoint, disinfection)`. So the change also rounds up every install whose everyday set-point is at or above the disinfection temperature and off the entity's step. On those installs, the nearest step already meets the disinfection target. This is the body's own null-control class ("an everyday set-point at (60) and above (62) the disinfection temperature ... Had the fix leaked into them the diff would print those lines"). The harness puts that class only on-step, so it cannot see the leak (its output is byte-identical at 49a45dd8 and at the head, `ev/harness_prev_49a45dd8.txt` and `ev/harness_head.txt`).

Measured with the PR's own `_dhw_snap` and `written` helpers inside `tests/block_duty.py`'s `disinfection_checks`. The probe is spliced in temporarily (`ev/probe2.py`) and output is in `ev/probe_overshoot.txt`. The install is everyday 57, disinfection 50, entity min 30, max 65, step 5.

- RESULT head 0aed6ccbc: held cycle write 60.0; booked cycle write 60.0; null (no cycle) write 55.0
- RESULT prior head 49a45dd8: held cycle write 55.0; booked cycle write 55.0; null (no cycle) write 55.0

The cycle's target here is 50, and 55 already meets it. The head instead writes 60. That is a full step above the everyday set-point and above `dhw_hard_max_temp`, which is `min(70, dhw_cycle_temp)` = 57, the ceiling the plan models the tank under. The pump heats the tank 3 °C past what the plan accounts for on every cycle step. Before this delta, the reviewed head did not do this. The overshoot equals the entity's step: 1 °C on a step-1 entity with a 0.5 °C everyday set-point (52.4 → 53 against 52), and 5 °C on a step-5 entity.

The defect `8da43a2fe` fixes is real (M11 reproduces it below). The repair needs to round up only where the nearest step falls below the disinfection temperature. Something like `max(nearest(everyday), up(disinfection))` through `_bounded`'s existing `lo` argument would do it. That `lo` already rounds a floor up, so it adds no second rounding rule, which was the reason the body gave for rejecting the quantised comparison. It also needs a `tests/block_duty.py` null-control check on an off-step everyday set-point above the disinfection temperature, which fails at this head.

## Evidence

- Head reviewed: 0aed6ccbc99c5a3210dcb1caf013ea0d7c5ceed5 (`ev/HEAD.txt`), from a detached worktree. The prior head 49a45dd8 was checked out in a second worktree.
- Delta (`ev/delta.diff`): `pump_arbiter.py` +6/-4 (docstring and the dropped comparison), one `tests/block_duty.py` check, the M11 mutant row, 10 `killed_by` records, and `dev/programme/delivery/3452.md`.
- Baselines at the head: `tests/block_duty.py` rc=0, 63 of 63 passed; `tests/guard_pins.py` rc=0, 61 of 61 passed (`ev/base_*.log`).
- All 10 added ledger sites, each mutated by hand and run against its named check (`ev/mutants.txt`, driver `ev/mut.py`, tree restored clean): all KILLED.
  - `_dhw_write` GUARD_OFF 90de19e4 → guard_pins rc=1. This kill is a crash (`TypeError: float() ... NoneType`), not a failed check; it is still a kill.
  - `_dhw_write` RETURN_DEL e7e1a636 → block_duty 10 of 63 failed.
  - `dhw_gated` RETURN_DEL 7523de18 → block_duty 1 of 63.
  - `_dhw_floor` CLAMP_DROP 645cbad5 → block_duty 2 of 63.
  - `_dhw_floor` RETURN_DEL 645cbad5 → block_duty 4 of 63.
  - `dhw_cycle_temp` CLAMP_DROP 25788b20 → guard_pins 1 of 61.
  - `dhw_cycle_temp` RETURN_DEL 25788b20 → guard_pins 1 of 61.
  - `dhw_disinfection_temp` RETURN_DEL aae31b25 → guard_pins 1 of 61.
  - `dhw_hard_max_temp` CLAMP_DROP b26a9d8f → block_duty 1 of 63.
  - `dhw_hard_max_temp` RETURN_DEL b26a9d8f → guard_pins rc=1, also by crash (TypeError).
  - The split of 5 guard_pins and 5 block_duty matches the body.
- The arbiter change is covered: restoring `or cycle <= everyday` (M11) makes block_duty report 1 of 63 failed. That matches the body's "failed at d2ab2743 (1 of 63)".
- The PR's driver `tools/audit/seat/r10_disinfection_setpoint_mutants.py` at the head exits 0: NULL survived and 11 named mutants were killed (`ev/pr_mutants_head.txt`).
- The finder's harness `dev/audit/harnesses/r10_disinfection_setpoint.py` at the head and at 49a45dd8: rc=0 at both, and the outputs are IDENTICAL. That flatness is expected, since the delta only moves off-step installs and the harness has none with everyday ≥ disinfection. The body's null_* figure (80 lines identical against main) was not re-taken in this delta round. The prior round covered it, and the delta leaves the harness output unchanged.
- `git merge-tree --write-tree origin/main 0aed6ccbc` rc=0, clean (`ev/merge_tree.txt`). The tests/closures.json conflict printed `LEDGER-MERGE: resolved`.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched against the merge base (empty diff).
- CI: `merge_train.py classify` printed `WAIT 0aed6ccbc99c5a3210dcb1caf013ea0d7c5ceed5 pending: gate red: none` (rc=3) at 13:27:39 and 13:29:12 UTC (`ev/classify.txt`). No required check had concluded red at this head when the verdict was written. The block does not depend on CI, so no pending-ci wait was run.
- The body's `## Red checks` answer for `tests / mutation` at d2ab2743 (state (b), detector `ci_predict.py`) and `tests / fast (3.14)` (inherited census) are present. The trigger is answered.
- Closing self-audit: `carry_audit.py check` rc=0, 0 finding items. It ran on this verdict with a body file holding only the PR body's `## Forward-carry` and `## Friction` sections, because this seat has no `gh` to dump the body. The review packet's `carry_audit at the head` over the full body printed 0 items.
