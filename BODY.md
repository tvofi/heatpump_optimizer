A live v6.7.17 install (14 kW nameplate maximum, pump really drawing 1.9-2.55 kW) never produced a COP sample. The COP learner's duty floor was `max(0.3 x max_electrical_power, 0.2)` = 4.2 kW, above every draw, so `cop_samples` stayed 0, the observed-COP sensor stayed unavailable (and HA hid its `waiting_for`), and the flow-lift fold, which reads the same floor, was starved too. Synthetic numbers only below; the user's diagnostics file was not used.

What changes (decided under tvofi's mandate 5951564627; aligned with the live-fix design note, `hpo-seats/live-arch/DESIGN.md`, sections 1 S5, 3, 4 and 5):

1. `ThermalParameters.flow_lift_power_floor_kw` is `max(0.8 x min_electrical_power, 0.2)` when a modulation floor is configured, and the old nameplate third when it is 0 ("no floor"). Both readers, `_fold_measured_cop` and `_fold_flow_lift`, take the property, so they move together.
2. `accuracy.MeasuredCop` holds the learner's last COP, the curve it was judged against, and `refusal`, one of the `accuracy.COP_REFUSED_*` codes (one per guard, in order). `_fold_measured_cop` returns the code and `_learn_measured_cop` records it. `accuracy.diagnostics_view(record, params)` takes values only and publishes `last_refusal`, `measured_cop` and `duty_floor_kw`. It is registered as the `cop_learner` row of a per-module view loop in `diagnostics.py`, read through a new public `_view` (`measured_cop`). The diagnostics dump is available whether or not the sensor is.
3. The measurement half (`cop`, `curve_dhw`, `dhw_temp`) persists under the additive `thermal_learning` key `measured_cop`, declared in `store.DOMAINS`. Every store stays at version 1. An unreadable record loads as no measurement, as a whole, so a COP is never paired with an unreadable curve.

The three old paired attributes `_last_measured_cop`, `_last_cop_curve_dhw` and `_last_cop_dhw_temp` became one record, so the pairing invariant their comment asserted is now structural.

Not in this PR (design note section 2, item 2): the floor is not capped at the observed running draw. An overstated modulation floor still refuses a pump that draws less than 0.8 x it; at 3 kW options and 2.2 kW draw the diagnostics name `duty_floor` at 2.4 kW, and a check below pins that. 7a's `draw_range` S4 has not merged, so the consumer belongs to 7b, and no local statistic is kept.

## Head

`5b5a2daec14fa720ee1904e0ef3ab7f3d4460ff0` (code head). Everything below was measured on it, at merge base `af79f2114b5dcd2cf0fef6b06f939ff1f7c406ee`.

## Mutation proof

Each mutant is a deleted or weakened production line in its own worktree at the head. The test block is the new `features.py` section "COP learner duty floor keys on the modulation floor (live v6.7.17)", run as an extracted runner over the same block. Failing checks per mutant:

- M1, `thermal_model.py` min-keyed branch deleted: `a 14 kW nameplate pump drawing 1.9-2.55 kW teaches the COP learner`, `the duty floor is 0.8 x the modulation floor, never below 0.2 kW`, `the flow-lift fold takes the same floor: a 14 kW nameplate at 2.2 kW folds`, `a refused COP interval names its guard and the floor in the diagnostics`, `a folded COP interval clears the refusal`, `the last measured COP and its curve are restored on restart` (6 of 15).
- M2, `self._measured_cop.refusal = ...` reduced to the bare call: `a refused COP interval names its guard and the floor in the diagnostics`, `each guard has its own code: a freeze and a missing reading` (2 of 15).
- M3, the `MeasuredCop.from_dict(stored.get("measured_cop"))` load line deleted: `the last measured COP and its curve are restored on restart` (1 of 15).
- M4, `(dhw and temp is None)` dropped from `from_dict`: `an unreadable stored COP record loads as no measurement, whole` (1 of 15).
- M5, the `cop_learner` diagnostics row deleted: `a refused COP interval names its guard and the floor in the diagnostics`, `a folded COP interval clears the refusal` (2 of 15).

## Null control

- The same test block at the merge base fails 13 of 15. The two that pass there are `idle and standby draws under the modulation floor still teach nothing` and `with no modulation floor configured the nameplate floor still applies`. Both are the behaviour the fix must keep, so they pass on both trees.
- Harness `tools/audit/harnesses/cop_duty_floor.py` (sha1 `0875a62157f9588bef491a211ebedfd146d09573`), at the base and at the head. `liveness_folded=3/3` at both: a 4 kW nameplate, whose old 1.2 kW floor already admitted a 2.2 kW draw, folds on both trees. So a zero at the base is the floor, not a learner that cannot fold. Idle, standby and duty-cycled draws fold 0 at both ends.

## Figures

All rows come from `PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/harnesses/cop_duty_floor.py`, run from a worktree root at the base and at the head. Each count is the folded intervals out of 3 per draw.

- `duty_floor_kw`: base 4.200, head 0.800 (14 kW max, 1.0 kW min).
- `min1_running_folded` (1.0, 1.2, 1.9, 2.2, 2.55 kW): base 0/15, head 15/15.
- `min1_idle_folded` (0.02-0.1 kW) 0/9, `min1_standby_folded` (0.2-0.5 kW, at or under `on_threshold_kw` = 0.5) 0/9, and `min1_duty_cycled_folded` (1.0 kW at 50 % / 70 % duty over 0.05 kW idle) 0/6: the same at base and head.
- `min3_running_folded`: base 0/15, head 3/15 (only the 2.55 kW draw clears 2.4 kW). This is the deferred S4 gap.
- `liveness_folded`: 3/3 at both.
- The constant: the harness's `sweep` lines print, for a floor of k x p_min with k from 0.5 to 1.0, how many of the 5 standby and duty-cycled draws each k admits, and how many of the 5 running draws. k=0.5 admits 3/5 and k=0.6-0.7 admit 1/5 (the 0.715 kW 70 %-duty interval). k=0.8 is the smallest that admits 0/5 while every running draw still folds, and it leaves 0.2 kW (20 %) below the modulation floor for a meter that under-reads. This sweep is the formula on the synthetic classes, not a measurement of a real pump.
- `python3 tests/structure.py`: ratchet passes. Re-recorded rows (all improvements, the reason is in the commit): `coordinator_attrs` 153 -> 151, `coordinator_multiassigned_attrs` 120 -> 118, `max_class_loc` 9048 -> 9041, `seam_cut_total` 766 -> 764.
- `python3 tools/audit/archscore/score.py --diff af79f2114b5dcd2cf0fef6b06f939ff1f7c406ee`: `dS +0.0246 IMPROVES` (`coord_footprint` 2613 -> 2612, `coordinator_multiassigned_attrs` 120 -> 118).
- Floor readers, from `git grep -n flow_lift_power_floor_kw -- custom_components`: three sites. `coordinator.py` `_fold_flow_lift` (keyed by this diff), `coordinator.py` `_fold_measured_cop` (keyed by this diff), and `accuracy.diagnostics_view` (reports it). No reader is left on the nameplate third except the min = 0 branch.
- Scoped gate: `python3 tests/closure.py select --diff af79f2114b5dcd2cf0fef6b06f939ff1f7c406ee` prints `MODE: SCOPED`. Run locally and green: `finite_boundary`, `entities`, `typing_ruler`, `debug_collect`, `guard_pins`, `doc_claims`, `structure`, `validate`. Also run locally: `features`, 1 of 3875 failing, `R9-F2.1 P3`, which fails identically at the merge base on this macOS/Accelerate seat (the known container-only check); and `harness_headers`, 12 of 109 failing, all on `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` hitting its 900 s wall limit while ten scripts ran in parallel, a harness this diff does not reach; `harness_headers` at the merge base fails the same harness's `exits 0` check. Left to CI: `stress`, `optimality`, `backtest`, `golden` and the rest of the scope.

## Red checks

none

## Forward-carry

`tools/audit/harnesses/cop_duty_floor.py`: its `min3_running_folded` row reads the gap this PR leaves (3/15 at the head, an overstated 3 kW modulation floor against a 1.9-2.55 kW draw), so the seat that adds the observed-draw cap at the floor's two readers reruns it and reads the gap close. That cap is the power-clamp seat's `draw_range` consumer (design note S4, stage 7b, out of tree), and the note already names it, so nothing new propagates. The refusal codes a later learner fix adds extend `accuracy.COP_REFUSED_*`, the list's own comment says so. Not touched: `_fold_capacity_envelope` learns only at >= 0.95 x nameplate, so an overstated maximum still starves the envelope. The design note records the envelope as out of S3's scope.

## Unpinned sites

Each site `prepr.sh` step 6d lists, by key, with its disposition. "Value check" names the new `features.py` check its mutant fails (mutation proof above); the rest are left to `mutation-autofix`, which pins a killed mutant (`ci-autofix.md`).

- `custom_components/heatpump_optimizer/thermal_model.py:666 CMP_BOUND`: value check `the duty floor is 0.8 x the modulation floor, never below 0.2 kW` (min 0 must take the nameplate branch: `with no modulation floor configured the nameplate floor still applies`).
- `custom_components/heatpump_optimizer/thermal_model.py:666 GUARD_OFF`: value check `with no modulation floor configured the nameplate floor still applies`.
- `custom_components/heatpump_optimizer/thermal_model.py:667 CLAMP_DROP`: value check `the duty floor is 0.8 x the modulation floor, never below 0.2 kW` (min 0.1 gives 0.2).
- `custom_components/heatpump_optimizer/accuracy.py:665 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/accuracy.py:680 BOOLOP`: value check `an unreadable stored COP record loads as no measurement, whole` (mutant M4).
- `custom_components/heatpump_optimizer/accuracy.py:680 CMP_BOUND`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:680 GUARD_OFF`: value check `an unreadable stored COP record loads as no measurement, whole`.
- `custom_components/heatpump_optimizer/accuracy.py:682 BOOLOP`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:682 GUARD_OFF`: `mutation-autofix`.
- `custom_components/heatpump_optimizer/accuracy.py:684 RETURN_DEL`: value check `the last measured COP and its curve are restored on restart`.
- `custom_components/heatpump_optimizer/coordinator.py:4751 RETURN_DEL`: `mutation-autofix` (the tracking-gate return's code; the existing v4.0.5 tracking checks drive it).
- `custom_components/heatpump_optimizer/coordinator.py:6825 RETURN_DEL`: `mutation-autofix`. This is the existing `return None` after "No published prices cover the planning horizon", which this diff does not touch; the predictor lists it because the lines above it moved.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
