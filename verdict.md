Design review: approve 1abf062b2d41ce2fdd7ef89791d801f14e43ebab

Reviewed design/R11-VALVE-REFERENCE at 1abf062b2d41ce2fdd7ef89791d801f14e43ebab (round 2), judged against e352724335c136b65562cd3e71f728549ad04a82, which the note now names as its base. Round 2 changes only design.md (diff from 3c4c236375).

Round-1 revise point 1 (product-tradeoff-regression), closed:
- The single-zone branch of `flow_target_for_indoor` is now gated on `not p.two_zone_enabled and mixing_valve.is_throttling(p.mixing_valve_mode)`. Checked at the base: `THROTTLING_MODES` (mixing_valve.py:58) is manual, smart_read and smart_write, so every `none` install takes the unchanged expression. `from_config` sets `cop_flow_carnot = is_throttling(mode)` (thermal_model.py:1074) and `_flow_curve_values` turns `flow_curve_cop` off when it is set (thermal_model.py:193). So the priced curve (`compute_cop` -> `curve_flow_temp` -> `curve_supply_temp`, and the batch at thermal_model.py:4487) only reads the gated-off path on a configured install. `direct_flow_carnot` (tests/golden.py:700, `two_zone=False`, no valve) runs the gated-off path too.
- The remaining readers of the gated branch at the base are `sysid.py:249` `_valve_regulates`, which returns early unless `is_throttling` holds and is meant to read the plant's curve (invariant d); the bias learner (coordinator.py:973), carried as r1; and the flow write (coordinator.py:7746), which `valve_flow_needs_two_zone` refuses on a single-zone house before it reads the curve. This matches the note.
- The new invariant (c′), `==` against base literals on the `direct_flow_carnot` configuration, passes at both ends and fails if the gate is dropped. Dropping the gate is also in the mutation list. The arithmetic is scalar Python with no BLAS path, so exact literals are sound.
- Round-1 note r2 (wind) is answered: (d) is now pinned at wind 0 and precipitation 0.

Checked with no point raised:
- Sibling sites: at the base, `_valve_flow_set` (thermal_model.py:2263) has callers at 2314, 2343 and 2348. The direct `mixing_valve.flow_setpoint` calls at 2508 and 4661 are the two-zone ones, which stay out of scope as the finding's control. `flow_target_for_indoor` (3489) has the three readers listed above plus flow_lift.py:116. No missed site.
- Sibling designs in flight: no other open design/* note names `flow_target_for_indoor`, `_valve_flow_set`, `flow_setpoint`, `_compute_baseline_power`, `_thermostat_held_state` or `REFERENCE_BASIS`. R10-START-COUNTER-EDGES and R11-OUTSIDE-HONEST-METERED-FLOOR touch thermal_model.py, but at other functions (`on_threshold_kw`, `levels_clamped`). The two designs do not claim the same seam.
- Cost: unchanged from round 1 (three production files, tests/features.py, the harness), which fits the group.
- Dispatch precondition (carry 1's diagnostics-bundle reproduction): still routed as decision: owner, pending owner confirmation. It is not a revise point.

Notes for the fixer (non-blocking):
- The gate keys on `mixing_valve_mode`, but the price path keys on `cop_flow_carnot` and `flow_curve_cop`. Only `from_config` ties the two (thermal_model.py:1074). A `ThermalParameters` built directly with a throttling mode and `flow_curve_cop=True`, `cop_flow_carnot=False` would price the new curve. Assert the coupling in the (c′) section, or key both on one predicate. Carry: R11-VALVE-REFERENCE (item r3)

Seat token count: not reported by this harness.
