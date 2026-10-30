Design review: revise ce5ca88b harness

Reviewed: round-2 design note at handoff-body/r10-cop-gate-vent 6eb360d0 (BODY.md byte-identical to handoff-body/r10-cop-gate-vent-r2 a91f1811), with its Appendix A harness. Run against the payload head eec56f24 (detached worktree, clean); custom_components/ has no diff from 1afdef88, the note's measured SHA, so line numbers carry. Round 2 of 3. The verdict line names ce5ca88b because the brief fixes that string. The design under review is 6eb360d0.

## Reproduction

Appendix A, extracted verbatim, run with `PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py` under venv-ci at eec56f24 (33 s). Every line of the note's measured block appears verbatim in the output:
- the cop-under-a-window arm: inferred 0.500 clamp against a null of 1.056 [0.989-1.120]; flow and span 1.000 at null and both k;
- draw-range: slope 0.996/1.003/1.009, observed0 max 2.453/2.576/2.698;
- buffer: g=0 at 1.0000 both; g=0.0005 1.2946→1.3058; g=0.002 2.1781→2.2233.

The cusum table, including its null rows (0/0/0/1.12 [0-3]; front-only 0), the learners arm and the latch arm are unchanged from round 1.

## Round-1 revise points

1. COP split on heat evidence: **answered.** I read `_fold_measured_cop` (`coordinator.py:4999-5062`). The freeze at :5017 precedes the counter exit at :5040 and the hoisted `heat_kw` read at :5048. `judge_ratio` is skipped when `heat_kw` is set. The proposed `room_air=not measured_heat` gates the same evidence the fold uses on the same cycle. The arm shows the measured-heat folds hold at 1.000 under both windows while the inferred tail, fed the same draws, walks to the clamp, which is a valid positive control. Coupling checked: the flow bias reaches modelled COP only through `compute_cop` → `curve_flow_temp` (`thermal_model.py:2621-2641`), and only on the no-measured-heat branch. `space_reference_cop` (`flow_meter.py:127-143`) uses measured `last_supply_c` when heat is measured. So the lifted folds do not inherit a window through the flow bias.
2. draw-range `power_frozen` (:9760) stays frozen: **answered**, measured (max +5 %/+10 %) and argued (no consumer judges draw against measured heat; the defrost settlement at :9850 is unchanged).
3. Output arms per lifted learner: **answered for COP; open for `_fold_flow_lift`** (the revise point below).

Carried notes: the site count is corrected (13 call sites plus the DHW callable, :9780 named). The buffer is settled from the topology and kept frozen (`mixing_valve.py:57-59`, `pump_schedule.py`; the arm moves at g > 0). The counter refusal code is asserted in failing test 1. All answered.

## Revise point

1. `coordinator.py:878` (`_fold_flow_lift`), the site table's "room_air=False (accepted round 1)" row, and "Unchanged from round 1", which says "none of their inputs is room air: … supply against the curve" — harness. The brief for this round requires each lifted learner to show its output movement against a no-window null. This learner is lifted on argument alone, and the argument does not hold.

   The residual is measured supply minus `curve_supply_temp(model, outdoor, target)` (`coordinator.py:886-893`). The curve side is room-independent, but the supply side is not. At a fixed delivered heat (the plant runs a commanded power), emitter water temperature is room temperature plus Q/UA_em. So a window that cools the room by ΔT lowers supply by about ΔT. On a pump with room compensation it moves supply the other way. In both cases the room air enters through the emitter.

   The learned quantity matters. `bias_k` is a persisted EWMA (`flow_lift.py:180-200`, clamp ±15 K) and it prices every plan step through `flow_lift_factor` (`thermal_model.py:3871`, via `flow_curve_bias` pushed at `coordinator.py:3931`).

   The note's own window model fixes the flow temperature, so an arm built on it would read flat by construction. That cannot settle it.

   Fix wanted: add an arm that runs the production `FlowCurveBias.observe` (or `_fold_flow_lift`) on 30 days of the existing window scenario, with two plant laws:
   - (a) commanded heat, with supply = room + Q/UA_em + ΔT_design/2;
   - (b) the curve held, the note's model, as the by-construction null.

   Report `bias_k` at k = 0.00 / 0.15 / 0.30 over 8 seeds. If (a) moves `bias_k` beyond its no-window null, :878 keeps the default freeze (the note's own rule from point 3). Otherwise the lift is measured.

Not revise points: DHW (`async_learn_dynamics` takes only `dhw_temp`, and its ambient term is the constant `TANK_ROOM_AMBIENT_TEMP`, `dhw_learning.py:42,417`) and `_dhw_probe_temperature` (a tank probe) read no room air, so a window arm would be identity by construction. Their lift stands on inspection.

## Notes for the fixer (carried, not revise points)

- `coordinator.py:1152`: `_freq_fold_blocked` already ignores the vent latch. It returns `bool(frozen and ":" in frozen)` (:1153), and `"ventilation"` carries no colon (`coordinator.py:6642`), so boost and the tail reasons pass too. The note's `room_air=False` there is a no-op, and its mutation target ":1152 back to default fails its row" is an equivalent mutant no test can kill. Drop the edit and that mutant, and record in the PR body that the site already lifts. Carry: R10-COP-GATE (item E)
- The flow-heat COP lift fails closed only if `heat_output_kw` is None whenever the reading is stale. `observe_temps` (`flow_lift.py:154-178`) stores what `read_heat_output_kw` returns each cycle. The failing test should include a stale thermal-power entity, with the latch set, and assert `COP_REFUSED_FROZEN`. Carry: R10-COP-GATE (item E)
- Carry: dismissed: freeze reason resets each cycle (item 9)

Seat tokens: subagent locator 37108; main-loop count not reported by the harness.
