# R11-OUTSIDE-SELF-SETTING-PUMP (#3662): identifying a self-setting pump under flat asks (architect note, round 3)

Designer seat, answering `Fix review: blocked 1134fe3655` (ba984f3567) and the repair fixer's `BLOCKED.md` (handoff-wip/r11-outside-self-setting-pump at 8b05d67241). Code read at the partial repair `ab0960f62f` and at origin/main `6f422812d5`. This note replaces the probe of the approved note (`design.md` at b31718e618); its admission rule, restore target, clamp re-seed (A) and persistence stand. Figures marked (spike) come from the designer's spike: a standalone simulation (Python, seeded, 168 pairs per cell, z = 3) on the sweep harness's signal generators, not the coordinator. The fixer re-measures every one through the harness.

## 1. The identification problem

The probe regresses log drawn on log heat ask, `asked_kw × cop_scale`. Under flat asks the heat ask moves only when the scale moves, and the scale moves only by folds whose target is `scale × asked / drawn` (`flow_meter.cop_evidence`). So the regressor is a running sum of the outcome's own past: x(t) = const − α·Σ log(drawn/asked). Two worlds produce the same rows:

- heat-led: drawn = asked × scale / true. The draw answers the scale (elasticity 1).
- self-setting: drawn = d(t), its own process (elasticity 0). Any autocorrelation in d(t) correlates it with its own running sum.

In the measured trace the regressor's whole span is one release step at one moment (1.000 to 0.758 at tick 47), so the test is a before/after split in time, and any draw that changes across that moment reads as following. No statistic on these rows separates the two worlds, because the regressor carries no variation that is independent of the draw. The sweep shows it: levels latch 397 of 1830 self-setting rows, differences 122 of 1830 and lose heat-led rows (154 and 128 of 360 not latching). Thresholds only move the errors between slow and fast swings. Identification needs variation in the heat ask whose timing the draw cannot have caused.

## 2. Options

| | (a1) restore as the one instrument | (a2) randomized scale dither, folds held while pending | (b) hold folds, wait for evidence | (c1) dither the plan's ask | (c2) bounded walk (fold within ±13 % of configured until proven) |
|---|---|---|---|---|---|
| What the learner does | Folds as today, then treats the jump back to the configured scale as a second step (A-B-A) | While pending: folds nothing, sets the scale to base × 1.15^(±½) by a seeded coin per pair of admitted rows, estimates the elasticity from the pair contrasts, decides by a confidence bound. Follows: back to base, folds resume. Ignored: configured scale, `COP_REFUSED_OFF_ASK` | Folds nothing while pending | Planner varies the commanded level so the window's own evidence becomes obtainable | Folds as today, clipped to a band |
| Identifies? | No. Two steps reject a linear drift, not a swing near twice the block length; the walk before the restore is still draw-led | Yes, by design: the coin is independent of the draw. (spike, z = 3) 0 of 3120 self-setting rows latch follows, periods 2 to 240 cycles, ±0/15/30/40 %; 0 of 600 heat-led rows read does_not_follow; undecided rows stay pending | Never decides: with no folds the heat ask never moves. A heat-led pump of true 0.68 stays at 1.000 (the alternative the approved note already rejected) | Yes where the ask is free; not where it is pinned, which is the flat-ask case | No. It bounds the harm, the verdict is as confounded as today |
| User-visible | As the blocked head, plus one scale jump | `scale_response` pending for about a day (median 48 rows, spike), scale within ±7.2 % of base meanwhile; then as the approved note | Scale frozen; heat-led flat-ask installs stop learning | Plan visibly departs from the optimum | Self-setting installs sit at 0.87 instead of 0.500 |
| Comfort and cost risk | The walk to 0.500 remains in the open cells | Heat-led: delivered heat alternates ±7.2 %, zero mean inside every pair, runs of at most two cycles; on a pinned plan the price paid is unchanged. Self-setting: none. Learning for heat-led starts at least 48 rows later than base | None from the scale; heat-led COP error is never corrected | Deliberate off-optimum plan steps; comfort bounds apply | COP mispriced by up to 13 % indefinitely; D4 says fix, not bound |
| Harness and sweep | Existing rows; fails the swing cells | `cop_duty_floor.py` `flat_row`/`run` and `sweep.py` drive it unchanged: both read `c._cop_scale` each tick, so the dither reaches the heat-led draw. `run()` needs only the pending-band read | Existing rows; fails every `heatled_*` control | Needs a closed-loop harness that does not exist | Existing rows; `selfset_*` read 0.87, not 1.000 |
| Size, seam | S, in seam | M, one owner (`MeasuredCop`); the coordinator's restore statement becomes "apply the scale the probe owes" | S, in seam | L, two owners (planner and learner): a stop under the designer contract | S, in seam |

Other candidates that lost: an AR-prewhitened or lagged regression is still observational (scale innovations are functions of the draw's past); the room's thermal response belongs to the heat-loss learners (two owners, as in the approved note).

## 3. Recommendation: (a2), which is (a) and (b) together

Hold folds while the verdict is pending, and let the only scale movement be a dither the learner randomizes. Reasons, in the code's terms:

- It removes the endogeneity at its source. With folds held, the draw can no longer move the regressor, so the "walk to the clamp unproven" path does not exist; with a seeded coin, no swing of any period can align with the regressor except by chance, and the confidence bound prices that chance.
- Undecided is safe. A row that reaches neither bound stays pending inside ±7.2 % of base. In the spike only 2 to 4 cycle swings of ±30 to 40 % (and one 8-cycle cell) end pending after `WINDOW` rows; none latches wrong.
- It keeps one owner and adds one constant (the bound's z; step size is `FOLLOW_ASK_SPAN`, minimum rows `MIN_SAMPLES`, threshold `FOLLOW_SLOPE_MIN`, cap `WINDOW`). `draw_range.step_response` and the levels probe go; `draw_range.py` returns to main's shape plus the merge's `_verdict`.
- The product already runs an active experiment (the ceiling store's system-identification intervals, `draw_range.py`), so a bounded, self-ending probe is not a new kind of behaviour.

Shape: `MeasuredCop` keeps the probe base scale, the pair's coin and the pair contrasts `coin × Δlog drawn / log FOLLOW_ASK_SPAN`; after `MIN_SAMPLES` rows it latches follows when mean − z·se ≥ `FOLLOW_SLOPE_MIN`, ignored when mean + z·se ≤ it. One method tells the coordinator the scale owed this cycle (dither level, base, or configured), applied at the existing restore site past the freeze gate. Each row carries the scale its draw was read under (the fixer's priced-scale alignment). At `WINDOW` rows undecided: stop dithering, return to base, stay pending and hold; re-arm after `COP_HOLD_HORIZON_S`.

Owner decisions this needs: (i) the learner may dither the scale ±7.2 % for about a day per probe; (ii) "while pending, an admitted row keeps base's outcome" (approved note) becomes "folds nothing"; (iii) the re-arm policy above.

Open risk, not measured here: the harness is open loop. Where a live plan is not pinned it re-prices the electrical ask against the dithered scale, the heat ask stays flat and the probe gains nothing; the asks may then span and hand the judgement back to the window's evidence. That ends in pending or a reset, never a walk, but it is unmeasured. It is the follow-up's first item.

## 4. Acceptance

All through `dev/audit/harnesses/cop_duty_floor.py` and `blocked-evidence/sweep.py` (to be committed under `dev/audit/harnesses/`), at base 367c3b9cac, PR head 1134fe3655 and the new head.

- Self-setting, all 1830 sweep rows plus periods 2, 3 and 4 cycles: **0 latch follows**. Every latched row reads does_not_follow and ends at the configured scale (1.000; from scale0 0.5 and 0.7 too). A pending row's scale never leaves base × 1.15^(±½). The harness's "off by more than 5 %" column counts dither cycles, so it is read against that band.
- The reviewer's seven rows (`ev/attack_drift_rows.py`), seeds 1 to 5: does_not_follow, 1.000.
- Heat-led, all 360 sweep rows: **0 read does_not_follow**; pending is allowed only in cells the body names with their counts (spike: 8-cycle ±30 % swing with ±20 % meter noise). `heatled_true_0.68` and `0.8` end at 0.679 and 0.799; the `held_*_heatled_true_0.8` twins keep 0.807 and 0.806.
- Null controls: (1) dither amplitude forced to zero: no row of either kind latches follows (spike: 600 of 600 heat-led read does_not_follow), which shows the verdict comes from the instrument; (2) `selfset_2.2_swing0_control`: does_not_follow, 1.000; (3) the full harness output differs from the PR head's only in the flat, swing and `held_*` rows; (4) any state but unobtainable, a measured-heat install, and no window are bit-identical to base (invariants k and l).
- Failing tests first in `tests/features.py`: a 64-cycle ±15 % swing ends at 1.000 (fails at 1134fe3655); no fold lands while pending; the dither never passes a clamp; a reload mid-probe returns to base. Mutation targets: the coin's sign in the contrast, both bound comparisons, the hold while pending, the return to base, the cap.

## 5. This PR, and the follow-up

This PR: the (a2) probe in `accuracy.py`, the one coordinator statement, the priced-scale alignment, the stored base key in `store.py`, the harness rows and the committed sweep. The PR cannot merge without it: the block is class-open on D4. If the owner wants #3662 merged before a redesign lands, the only safe cut is (b) alone, with the stated cost that heat-led flat-ask installs stop learning until the follow-up.

Follow-up group: a closed-loop harness mode and the re-pricing row above; the defrost carry's control (R11-INTAKE-R10-RESIDUE item 0116e1a6 must cite the swing rows reading does_not_follow); tuning the dither size against measured time-to-decision.

## Notes for the fixer

- Sibling sites: `git grep -n -e "step_response(" -e "draw_response(" -e "take_restore(" -e "_admit(" -e "scale_response" -e "_apply_cop_scale(" -- custom_components`; every `_admit` caller (`_judge_ratio`, `release`) must hold, not fold, while pending. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- `max_class_loc` and `class_excess_loc` have zero headroom: replace the `take_restore` statement, do not add a second one. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- Persist the probe base beside `scale_response` and apply it on load while pending, or a restart mid-probe keeps a dithered scale as its base. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- A pair is two consecutive admitted rows; a refused or frozen cycle between them voids the pair instead of stretching it. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- Near a clamp the two levels are base and base × or ÷ `FOLLOW_ASK_SPAN` on the open side; at a clamp the re-seed (A) applies first. Carry: R11-OUTSIDE-SELF-SETTING-PUMP


## Owner decisions (tvofi, 2026-11-16 ~16:40Z)
1. Active dither approved: the learner may move the scale +/-7.2% for about a day per probe.
2. While pending, an admitted row folds nothing (replaces the approved note's keep-base-outcome).
3. Undecided at the window cap: stop dithering, return to base, stay pending, re-arm after COP_HOLD_HORIZON_S.
