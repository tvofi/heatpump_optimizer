# Round 11 D3 late findings -- verifier report (seat D3-vlate, box VD3L)

Baseline tree 92d38ecb64 with e3cb5c019b's D3 evidence copied over; at-head readings in the evidence tree e3cb5c019b. All three lenses on every finding. Machine: cloud container, 4 vCPU; thread_factor 1.0 throughout; load1 quoted per number. This seat resumed a stalled predecessor's wip ref (aae12cc390): its probe, V2 and at-head outputs were kept, and the full gates it had not checkpointed were re-run.

Null full gate: gate_rc 0, failed_scripts 0, wall 3767 s, load1 1.0.

At-head method: the mutant applied in the evidence tree, then `tests/guard_pins.py` and `tests/features.py` only (seats/D3-vlate/athead.sh); the full gate was not re-run at head. A not-killed reading there is therefore 'not killed by those two scripts', not 'survives the full gate at head'.

**Gates still pending:** D3-s1-66, D3-s1-67, D3-s1-68, D3-s1-69, D3-s1-70, D3-s1-71

| id | vote | severity | full gate | at head |
|---|---|---|---|---|
| D3-s1-02 | weaken | nit | SURVIVED | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-52 | verify | low | n/a | not re-run |
| D3-s1-62 | verify | low | SURVIVED | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-63 | weaken | nit | SURVIVED | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-64 | weaken | nit | SURVIVED | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-65 | verify | low | SURVIVED | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-66 | verify | low | pending | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-67 | verify | low | pending | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-68 | weaken | nit | pending | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-69 | weaken | nit | pending | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-70 | verify | low | pending | not killed; the full gate was not re-run at head (about an hour per mutant) |
| D3-s1-71 | weaken | nit | pending | KILLED at head; the full gate was not re-run at head (about an hour per mutant) |

## D3-s1-02

- vote: **weaken**, severity nit
- value: _smooth_topk_sum(x,0) 0.0 -> 1.473806 under the mutant, batch stays 0.0 (mismatch 0 -> 1)
- metric: scalar _smooth_topk_sum(x,0) minus batch _smooth_topk_sum_batch(x[None],0), base vs whole-module mutant; reach = production calls with k<=0
- V1 reproduced: base_d931.out (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): scalar_k0 0.000000 -> 1.473806, batch_k0 0.000000 both arms, mismatch 0 -> 1; m31 harness topk_k0 0.0 -> 19.9986 kW, null_delta 0.0; load1 0.73 thread_factor 1.0; full gate (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence), `fullgate.py run --key d931ab195b940b0c`): SURVIVED, gate_rc 0, failed_scripts 0, killed 0, wall 3666 s, load1 1.88, thread_factor 1.0; null gate: gate_rc 0, failed 0
- V2 independent: v2_simple.py (own input, whole-module mutant): 02_scalar_k0 0.0 -> 3.999998, batch [0.0]; nulls k=2 and k<0 delta 0.0
- V3 reachable: no: reach_calls_k_le_0 = 0 of 111 production calls; both callers clamp k with max(1, ...) (tariff.py 982, 1204); hastub not involved
- V3 class: I1 (guard whose mutation leaves the gate green); class_guess 'new' corrected
- V3 seam_rule: enumerates: the grep names both sibling guards (744 scalar, 798 batch), the phenomenon's two seams
- attacks: contention (load1 < 2, thread_factor 1.0: none); null control k=2/k<0 (0.0); reachability (0 of 111 calls, so severity cut to nit: the divergence is unreachable today)
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at tariff.py:744, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-52

- vote: **verify**, severity low
- value: 0 of 45 card_drift states move under two payload-changing production edits; 44 move under a one-token card edit; card_drift selected on 11 of 12 cell-file diffs
- metric: states card_drift.mjs reports changed (of 45) per arm, with sha256 of the plan payload changed or not; plus closure.select hits
- V1 reproduced: m5_card_drift_payload.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): base moved 0; prod_small moved 0 payload_changed 1; prod_large moved 0 payload_changed 1; card moved 44 rc 1; closure edges 11, cell diffs selecting 11; load1 1.51 thread_factor 1.00; no full-gate claim
- V2 independent: own runs of tests/card_drift.mjs over a doubled payload (v2_card_drift_plan-x2): 'identical in all 45 states'; same over the plain payload: identical in all 45
- V3 reachable: CI-only (gate scheduling), not a Home Assistant path; the cost is gate time on every cell-file diff, no product consequence
- V3 class: I2 (measured closure diverges from the real dependency graph); class_guess 'new' corrected
- V3 seam_rule: demonstrated seam only: --select-only enumerates the 12 D3-s1 cell files (11 select card_drift), not every closure _widen unions
- attacks: null (no edit: moved 0); positive control (card edit: 44 moved, so the harness can move); payload doubled (still 0): the finder's claim holds
- at head: in the evidence tree e3cb5c019b: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_card_drift_payload.py --select-only` -> card_drift_cell_closure_edges 11, cell_diffs_selecting_card_drift 11 (load1 2.22, thread_factor 1.00): the over-selection stands at head; the full harness refuses at head (rc 1, AssertionError: its card-edit anchor `ha-card { padding: 12px 12px 8px 12px; }` has moved in heatpump-optimizer-card.js), so the 0-of-45 half was not re-measured at head

## D3-s1-62

- vote: **verify**, severity low
- value: rule text '0.5': rules -1 (GridFeeError) -> 1 parsed; verdict invalid_grid_fee_rules -> None
- metric: _parse_rule/from_config outcome on a rule with no '=': error (-1) or parsed rule count; config_flow spec_problem verdict
- V1 reproduced: probe_121362d4.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): rules -1 -> 1, delta 2; verdict invalid_grid_fee_rules -> None; null_delta 0; reach_calls_without_eq 2; full gate (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence), `fullgate.py run --key 121362d48b408236`): SURVIVED, gate_rc 0, failed_scripts 0, killed 0, wall 3731 s, load1 1.83, thread_factor 1.0; null gate: gate_rc 0, failed 0
- V2 independent: v2_simple.py: bare rate '0.5' -1 -> 1 and problem invalid_grid_fee_rules -> None; bare tokens 'a b' stay -1 in both arms (the mutant only opens the numeric case); null 0
- V3 reachable: yes: config_flow.spec_problem (config_flow.py:3927) and GridFeeSchedule.from_config (grid_fee.py:287) take user option text; no divergent hastub symbol on the path
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide: the tabulate --tsv | grep SURVIVED rule lists all 992 surviving mutants of the round, a superset including this one
- attacks: null (0); malformed-but-non-numeric input (no move: narrows the gap to bare numerics); reachability through config flow (yes)
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at grid_fee.py:173, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-63

- vote: **weaken**, severity nit
- value: max_abs_component label fixed -> rules on a |rate| tie; value delta 0.0
- metric: (value, source label) returned by max_abs_component on a fixed/rule |rate| tie
- V1 reproduced: probe_95779f9d.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): label fixed -> rules, label_changed 1, value_delta 0.0, rules-only tie delta 0, null 0, reach_from_config_tie 1; full gate (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence), `fullgate.py run --key 95779f9d6d71c50d`): SURVIVED, gate_rc 0, failed_scripts 0, killed 0, wall 3398 s, load1 1.0, thread_factor 1.0; null gate: gate_rc 0, failed 0
- V2 independent: v2_simple.py own tie: (0.4,'fixed') -> (0.4,'rules'); null 0
- V3 reachable: yes via from_config, but only the repair-issue placeholder text (coordinator.py:7623) reads the label; the number is equal in both arms
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: consequence: value_delta 0.0 on a tie, so only a message label changes -> severity cut to nit
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at grid_fee.py:355, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-64

- vote: **weaken**, severity nit
- value: min_component label fixed -> rules on a rate tie; value delta 0.0
- metric: (value, source label) returned by min_component on a fixed/rule rate tie
- V1 reproduced: probe_5cc84148.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): label fixed -> rules, label_changed 1, value_delta 0.0, null 0, reach_from_config_tie 1; full gate (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence), `fullgate.py run --key 5cc84148fa68bda1`): SURVIVED, gate_rc 0, failed_scripts 0, killed 0, wall 3403 s, load1 0.85, thread_factor 1.0; null gate: gate_rc 0, failed 0
- V2 independent: v2_simple.py own tie: (0.1,'fixed') -> (0.1,'rules'); null 0
- V3 reachable: yes via from_config; the label is read only when the value is < 0 (coordinator.py:7628), so a message label at most
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: consequence: equal value, label read only on a negative minimum -> nit; the finder's gate status was RED-AS-NULL, so the gate re-run decides survival
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at grid_fee.py:383, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-65

- vote: **verify**, severity low
- value: learned flow bias 3.638040 K -> 4.689280 K (delta 1.051240 K)
- metric: FlowBias learned bias after the probe's sample sequence, FLOW_BIAS_ALPHA 0.1 vs 0.2
- V1 reproduced: probe_0c3e91a6.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): 3.638040 -> 4.689280 K, null_delta 0.0; full gate (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence), `fullgate.py run --key 0c3e91a6a349409a`): SURVIVED, gate_rc 0, failed_scripts 0, killed 0, wall 3631 s, load1 0.92, thread_factor 1.0; null gate: gate_rc 0, failed 0
- V2 independent: v2_simple.py own one-fold input: 1.0 -> 2.0; null 0.0
- V3 reachable: yes: every fold after the warm-up (coordinator.py:986) on any plant with flow sensing
- V3 class: I1 (an unpinned behaviour constant); class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: null (0.0); a doc check reads the constant rather than pinning 0.1, so it follows the mutant (confirmed by the survivor)
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at flow_lift.py:47, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-66

- vote: **verify**, severity low
- value: bias 3.000000 K -> 3.666667 K at the sample one past FLOW_BIAS_MIN_SAMPLES
- metric: FlowBias learned bias after MIN_SAMPLES+1 folds, '<' vs '<=' warm-up guard
- V1 reproduced: probe_a0b3b288.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): 3.000000 -> 3.666667 K, delta 0.666667, null 0.0, reach_samples_eq_min 1; full gate PENDING
- V2 independent: v2_simple.py: 1.0 -> 1.666667; null 0.0; a 7-sample input moves 0.6 (the boundary is crossed on every plant)
- V3 reachable: yes: every plant passes samples == FLOW_BIAS_MIN_SAMPLES once
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: null 0.0; leave-one-out not applicable (single-number claim)
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at flow_lift.py:188, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-67

- vote: **verify**, severity low
- value: unset holiday-DHW-windows option parses to [] instead of None in 3 of 3 unset forms; consequence: a holiday day has 0 DHW windows instead of 2
- metric: _holiday_dhw_windows(config) for absent/''/None; consequence = len(windows_for_day(..., holiday=True)) with the parser's value
- V1 reproduced: probe_050fdc4a.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): None -> [] for absent, '' and None; unset_forms_moved 3; null 0; reach_unset_calls 3; full gate PENDING
- V2 independent: v2_67_consequence.py (own, dhw_schedule.windows_for_day): holiday day windows in force 2 -> 0; null (not a holiday day) 2 -> 2, delta 0
- V3 reachable: yes: the default install leaves the option unset and the holiday overlay is consulted whenever holiday mode is on (dhw_schedule.py:413 'holiday_windows is not None')
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: consequence measured beyond the parser: holiday mode loses every DHW window (2 -> 0); the judge may weigh a raise above low
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at thermal_model.py:169, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-68

- vote: **weaken**, severity nit
- value: direct call at dt=0.25 h: delivered 0.278400 -> 2.800000 kW; through simulate_step: 0 of 287299 calls differ
- metric: (q_rad+q_floor) of _valve_two_zone_delivery, base vs whole-module mutant on the same arguments, over every call simulate_step makes in a plant sweep
- V1 reproduced: probe_22b5ec87.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): 0.278400 -> 2.800000 kW, delta 2.521600, null 0.0, reach_valve_calls 64 (single-tank 64); full gate PENDING
- V2 independent: v2_valve_calls.py (own spy over simulate_step): 287299 calls, 0 differ, max delta 0.000000 kW, dt_hours seen 0.00198..0.5; v2_valve_dt.py direct: dt 0.25/0.1/0.05 h differ (2.52/2.10/1.41 kW), dt <= 0.02 h equal; the finder's plant substeps at dt 0.01923 h
- V3 reachable: the function is reached in real HA, but the public path's substepping keeps the tank bound from binding in every swept call, so the mutant is behaviour-equivalent there
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: reachability on the public path (0 of 287299 calls separate): the moving number exists only on a direct call with a coarse dt; severity cut to nit
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at thermal_model.py:2618 (moved from 2593), then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-69

- vote: **weaken**, severity nit
- value: dhw_kwh 2.5056 -> 1.9948 at prices x1000; realistic profiles delta 0.0; separation needs >= 8000 per kWh
- metric: solved DHW energy (kWh) from HeatPumpOptimizer.optimize, base vs mutant shortfall price, per price-profile cell
- V1 reproduced: probe_0911281e.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): 2.5056 -> 1.9948 kWh (delta -0.5108), null 0, realistic_delta 0.0, min_price_for_separation 8000; full gate PENDING
- V2 independent: v2_dhw.py (own, tests/profiles.py profiles x1000): 32 cells, 0 moved, max |delta| 0.0000; positive control (shortfall price 0.0) moves 1 of 1 cell by 1.0849 kWh, so the harness can move
- V3 reachable: only with a price spread of >= 8000 per kWh, which no real tariff carries; the shortfall penalty does not bind on any realistic input
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: grid artefact: 0 of 32 cells move at x1000 prices (positive control moves); consequence only at absurd prices -> nit
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at dhw_planner.py:1559, then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-70

- vote: **verify**, severity low
- value: tariff disabled with peaks held: threshold (5.0,10.0) -> (5.0,3.0), suppressing False -> True
- metric: (projection, threshold) handed to GuardState.update and guard.suppressing after _on_power_event, base vs and->or
- V1 reproduced: probe_5e8d48ef.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): enabled,factor0 (5.0,10.0) -> (0.0,3.0); disabled,factor1 (5.0,10.0) -> (5.0,3.0) suppressing False -> True; null_moved 0; full gate PENDING
- V2 independent: v2_power.py (own, real PeakTracker/GuardState): disabled+fuse 8 ((6,8),False) -> ((6,4),True); enabled factor0 no fuse ((6,inf),False) -> ((0,4),False); enabled factor0 fuse 8 unmoved; 2 of 3 cells moved; null 0
- V3 reachable: yes: a tariff switched off while the tracker holds peaks restored by from_dict (coordinator.py:8378) suppresses heating against a stale peak
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: null 0; one of three cells does not move (fuse caps the enabled-factor0 case); the disabled case alone carries the user-visible suppression
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at coordinator.py:8774 (moved from 8806), then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=0: not killed; the full gate was not re-run at head (about an hour per mutant)

## D3-s1-71

- vote: **weaken**, severity nit
- value: a day whose mean is exactly 1e-6: accepted 0 -> 1
- metric: observe_day_quarters acceptance (0/1) of a hand-built day at mean == 1e-6
- V1 reproduced: probe_c38d53ab.py (baseline tree 92d38ecb64 (+ e3cb5c019b's D3 evidence)): accepted 0 -> 1, quarter_days_delta 1, null 0, reach_real_price_days_at_boundary 0; full gate PENDING
- V2 independent: v2_head71.py (own): observe_day_quarters base 0 mut 1; sibling observe_day (sharing _usable_day at head) base 0 mut 1
- V3 reachable: only with a day whose mean price is exactly 1e-6; no real price day sits on that boundary (reach 0)
- V3 class: I1; class_guess 'new' corrected
- V3 seam_rule: phenomenon-wide (SURVIVED listing, 992 rows)
- attacks: reachability: exact-boundary input only -> nit; the finder's own gate status was RED-AS-NULL, so the re-run gate decides survival; main has since pinned it
- at head: targeted at head: mutant applied in evidence tree e3cb5c019b at price_model.py:163 (moved from 252, now in _usable_day), then tests/guard_pins.py and tests/features.py (PYTHONPATH=tests/hastub, seats/D3-vlate/athead.sh): guard_pins rc=0, features rc=1 '1 of 6034 FEATURE CHECKS FAILED' (null at head: features rc=0): KILLED at head; the full gate was not re-run at head (about an hour per mutant)
