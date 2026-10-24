ARCH2-s2 P1 (round 10, D7): the four standing configuration notices (grid fee magnitude, grid fee sign, lower-floor modelled, comfort-band contradiction) had four coordinator flags and four hand-copied create/clear blocks. `setpoint_check.ConfigNotices` now owns the rule once: raise once per offending value, clear unconditionally. Touches only the config-notice fields in `coordinator.py`; `issues.set_issue` gains a `persistent` option. No issue closed here; Part of the ARCH2-s2 group.

## Head

5b067738bd38010b0af9e54e78224b55234476e2, on base 50af6174f53c0f9bec3f705c3a4bb99615f71acc.

## Mutation proof

In `ConfigNotices.report`, `if offending is None:` replaced by `if offending is None and issue_id in self._raised:` (the reload-leak defect: clear gated on instance memory). `tests/features.py` then fails: "ConfigNotices: a fresh instance (entry reload) still clears the notice". Restored, it passes.

## Null control

Unmodified tree at the base: `python3 tests/entities.py` and the existing features checks for the four notices (once-per-value, unconditional clear after reload) pass both before and after; the new two ConfigNotices checks pass on the head and the clear check fails under the mutant above.

## Figures

- Structure rows improved and recorded (`python3 tests/structure.py --record`): class_excess_loc 18217->18118, coordinator_attrs 146->143, coordinator_multiassigned_attrs 114->110, max_class_loc 8457->8358, seam_cut_total 710->703.
- Scoped run at head with PYTHONPATH=tests/hastub: tests/features.py, entities.py, structure.py, guard_pins.py, golden.py, doc_claims.py, typing_ruler.py, harness_headers.py, deployment_shape.py, config_flow_steps.py all rc=0. Left to CI: the remaining scope.run scripts (arch_score_head, block_duty, boost_drift_replay, debug_collect, env_drift, finite_boundary, manual_plan, plan_view, card*, solar_alignment, wood_advisor).
- Finder's harness (`dev/audit/rounds/round10/D7/arch2-s2/` at fabaf4664) was not re-executed: archscore was not run here; the finder reported coord_footprint 2580->2563 and coordinator_multiassigned_attrs 118->114 at its base.

## Architecture score

Not run locally; the structure ratchet above moved down on five rows.

## Red checks

none

## Forward-carry

none. Note: the patch's `setpoint_check` hunk did not apply to main, and an `ir` import there broke architecture.md's HA-boundary counts, so the owner goes through `issues.set_issue`/`clear_issue` instead. `clear_issue` is best-effort (logs a failed delete), a small change from the bare delete.

## Friction

none

## Unpinned sites

- coordinator.py CMP_BOUND on the grid_fee_magnitude and grid_fee_sign `notices.report` lines: pinned by `mutation-autofix` after the PR opens (ci-autofix.md); the threshold comparisons were unchanged in meaning from the replaced `if worst > fee_bound(...)` / `if lowest < 0.0` and the existing fee-notice checks in tests/features.py cover them.
- issues.py `if persistent:` and setpoint_check.py `if offending is None:`: pinned by `mutation-autofix`; the latter is killed by the new "fresh instance still clears" check (mutation proof above).
- setpoint_check.py `if self._raised.get(issue_id) == offending:`: pinned by `mutation-autofix`; killed by the "same offending value raised once" check where the stub registry records each create.
