# R10-CEILING-PROBE — architect note (third note: the minimal re-cut)

Base `origin/main` 6fe5170cd7ce01e60ffebfc93e598c216e628fa3. Issues #2498, #2808; carry #2465. Note 2 `9ef332566` drew `revise class-open`, so this third note is `design-review.md`'s minimal shape, the rest carried — seven items stay here, one goes to R10-COP-GATE; all `after` predecessors are merged at the base. The finder's duty/level and draw-window harnesses are committed by the fixer in step 2 under `dev/audit/harnesses/`.

## Owning seam

`sysid.py` owns when the experiment runs and what it commands, `draw_range.py` what a sample teaches the band, `pump_arbiter.py` how an action becomes a set-point, `coordinator.py` the wiring. One path: `arm(kind)` sizes the step, `boost.adopt_plan` carries it as the action, the arbiter turns the action's power into a level, the metered draw and written set-point reach `observe`, the probe store and the top.

## 1. One sized variable per kind (revise 1)

- **The fit keeps the sizer.** `_begin_step_phase` sets `_step_power` from `_size_step_power` (`sysid.py:1547`, `sysid.py:1564`); that sizer returns `max_power_kw` when the full step fits and bisects below otherwise (`sysid.py:1469-1470`). Its answer is the house's, not a constant (F1).
- **The probe's bound is a duration search.** At q = p_max × COP, `_predict_step_excursion_plant` runs over candidate durations, longest first, in whole cycles (`DEFAULT_OPTIMIZATION_INTERVAL`, `const.py:1423`), against the sizer's own test; below two cycles the arm refuses. `_unadoptable` (`sysid.py:1564-1566`, where the step power is fixed) is the fit's alone: a probe adopts nothing (F2).
- **The arbiter reads the action's power, not the plan's.** `_planned_duty` returns `space` while that power exceeds 0.05 kW and `idle` otherwise — the threshold `heat_pump_on` already uses (`coordinator.py:10989`). The space path of `_flow_target` (`pump_arbiter.py:613-623`) maps it through a level function in place of the plan's `step_duty` (`pump_arbiter.py:325-359`); the mapping sends p_max to the heat level, so the ceiling is not a branch (F3).
- **Invariant.** The action's `power` equals what the step phase returns (`sysid.py:1698`, `_step_power`), the level the arbiter maps, and the power the bound was computed at; duty is `space` exactly when the heat pump is on. The booking already writes that power and its normalized form (`coordinator.py:10985-10991`).
- **Each kind has its own clock.** `arm` tests that kind's interval: the fit keeps `min_days_between_runs` (`sysid.py:1365-1374`); the probe owns 7 days unlearned, 30 once learned. One helper, `armable(...) -> (kind, refusal)`, serves `arm` and the button predicate. Probe eligibility is install-level: a meter configured and a flow set-point driven (the conditions `_flow_command` tests, `pump_arbiter.py:563-581`, less the written record), because the command is unset before the first pass.

## 2. #2808's surfaces (revise 2)

- **The dead fit.** A converged house no longer arms the fit in silence: `armable` returns the probe when eligible and otherwise a refusal published in `result` (`sysid.py:1340`). The converged denial (`sysid.py:1401`, "house already converged") is skipped for the probe kind only; the fit's guard is untouched (F4).
- **The freeze holds an armed experiment.** `_run_system_identification` keeps its abort for a started experiment and holds one that has not started, republishing the `_learning_frozen` reason (`coordinator.py:10956-10963`). A started run still aborts because its samples are the evidence and a freeze says the interval's heat cannot be attributed; a held arm injects nothing.
- **The outcome is recorded.** The bulky view stays out of `_unrecorded_attributes` (`sensor.py:1995-1997`), and the result's `reason` lives only inside it, so no history shows why an arm was refused; the status sensor publishes a recorded outcome attribute from it, and the view gains a kind, a held reason and a timestamped last attempt (`payload.py:530-535`). A probe completes uncompleted, its outcome in `reason`, so `_adopt_system_identification` adopts nothing (`coordinator.py:11004-11009`). The reason cannot ride the button — Home Assistant drops an unavailable entity's attributes — and availability widens to an armable kind (`button.py:146-152`).
- **Refused by name.** No new model-status state, no new payload reason, no change to `icons.json`, `strings.json`, `translations/` or the card: the probe is a kind inside `REASON_SYSTEM_IDENTIFICATION` (`payload.py:115`).

## 3. Learning, its consumer, the probe window (revise 3, 4)

- **The store.** Ceiling-commanded running samples go beside the rolling window on the same `DrawRange`. The top is the median of at least twelve, adopted only through `_metered_range`'s rule (`draw_range.py:162-172`: more than `AGREE_TOLERANCE` below the configured maximum), lapsing 45 days after the newest sample; twelve is three probe runs (F5). Control: twelve written below the ceiling fail the `CEILING_TOLERANCE_K` test (`draw_range.py:138`) and set nothing.
- **The window sentence, corrected.** The high of `observed` does take probe samples (`draw_range.py:159`, `MIN_SAMPLES`), so a 336-sample window holding 48 full-ceiling samples reads `((1.5, 3.0), False, None)` (F6). What it cannot do is release the top: `planned` only returns `_metered_range`'s answer while engaged (`draw_range.py:217-226`), and 48/336 = 0.143 is below `DISAGREE_SHARE` 0.25 **on a full window**. At 192 running samples or fewer the same 48 reach 0.25, and a probe sample is the latch's exact shape — asked the booked p_max, drawn the pump's real 3 kW — so the latch would cap the plan from an experiment. A ceiling sample cannot inform the low either, which is `LOW_PERCENTILE` of all running draws (`draw_range.py:158`). F7.
- **Learning only.** Nothing in the solve reads the learned range: `planned_range` is called only by `diagnostics_view` (`draw_range.py:438`, `draw_range.py:469`), and no code assigns `max_electrical_power`. This group's consumer is the diagnostics value; routing the top into the solve is R10-COP-GATE's draw evidence (COP-GATE item 1), where R10-HEAT-METER's note assigns it. The test asserts that value, never a plan change.
- **Why not the plan path; the mild band.** Mapping through the plan's step would write the plan's level, not the experiment's, since `_step_kw` reads `power_schedule` (`pump_arbiter.py:462-466`). The ruling stands (mild-band top, 45-day lapse, configured p_max) with the 15 % rule as its only gate, its rationale corrected: the store learns *electrical* draw, and a cold inverter draws at least as much, so a mild-band top under-states the cold maximum — books less heat, never fictional heat.

## Cross-impact

No adoption refusal is added: `_adopt_system_identification` consumes and replaces the result every cycle (`coordinator.py:11009`). Past adoptions on a flow install rest on a step never commanded; the body says they are not rewound. The rev-2 claim that an experiment in flight across the upgrade finishes under new code is false — a reload constructs it afresh (`coordinator.py:3599`) — and is dropped (item 9).

## Alternatives rejected

1. **Every step at p_max, the bisection replaced by a duration search** (the review's option (i)): agrees the four by construction but runs the fit at the ceiling on every house (F1).
2. **Probe samples into the rolling window, `MIN_SAMPLES` lowered**: moves the clamp for every install, including the duty-cycling ones the brief holds unchanged, and the probe latches itself at 192 samples (F7).
3. **The converged guard lifted for the whole experiment**: lets one night overwrite a converged house's learned scale.
4. **The outcome at log level only**: #2808 asks for history and a timestamp; a log line is neither.

## Sibling sites

The command `git grep -n '_sysid_step_off_loop\|learner_samples=' custom_components/heatpump_optimizer/` lists every site. Beyond those changed above: the view's publication (`coordinator.py:7769`, fields change), the bulky attribute (`sensor.py:2042`, stays unrecorded), the entity key (`button.py:143`), the state list (`const.py:1492`), and the config, translation and card files, unchanged because no state name is added. One live behaviour goes in the body: `boost.py:647` returns `RELEASE_SYSID`, so an active experiment **releases a live block** rather than passing through (item 13; rev 2 said pass-through and was wrong).

## Figures, instruments, controls

Each value re-derived at the base by the seat probe named, run as `python3 -I <probe> <worktree>`.

| # | figure | instrument | control |
|---|---|---|---|
| F1 | step power 5.0 kW (ua 0.35, C 12) vs 2.2583 kW (ua 0.12, C 4); p_max 5.0, COP 3.0. | `sysid.py:1423-1512`; sysid probe. | the house moves it. |
| F2 | 15 kW: 0.447 K peak at 2.0 h (leaky), 0.769 K at 1.0 h (tight), 0.903 K at 0.5 h (ua 0.05, C 1.2: every whole-cycle arm refuses). | `sysid.py:1457-1462`; sysid probe. | leaky keeps 2.0 h. |
| F3 | 5.0/1.5/0.0 kW -> 55.0/37.5/55.0 °C (band 1.0–5.0); duty `space`, experiment `None`. | `thermal_model.py:1517`; level, arbiter probes. | the level moves it. |
| F4 | 199 ready, 482 converged, arm already granted. | `sysid.py:1316-1378`; sysid probe. | 150 ready. |
| F5 | 4 step samples per 2.0 h run at 30 minutes; 12 = 3 runs. | `sysid.py:1609-1705`; sysid probe. | a 6.0 h step gives 12 per run. |
| F6 | 48 full in 336 -> high 3.0; 48 full in 48 -> the same high. | `draw_range.py:147-160`; range probe. | 47 leave it unset. |
| F7 | 48/336 = 0.143; 48/192 = 0.25; 48/193 = 0.2487. | `draw_range.py:51`, `draw_range.py:60`; range probe. | 192 latches, 193 not. |
| F8 | every budget metric at its budget. | `tests/structure.py`. | an added coordinator attribute exceeds it. |

## Evidence plan

- Tests first, in `tests/features.py`, the button pin in `tests/entities.py`: duty and level for both kinds and the fit's sized level (the finder's duty harness inverted); a converged house arms a probe and publishes its kind; no meter refuses with a reason; the freeze holds an armed experiment and aborts a started one; the outcome carries a timestamp; eleven stored samples set no top, twelve do; the lapse; the duration search's three arms.
- Controls beside their arms: the moving control is a plan of `power_schedule=[5.0]` on a 1.0–5.0 band, printing `space` and 55.0 °C at 5.0 kW against 37.5 °C at 1.5 kW — two outcomes for two levels, which the defect cannot produce, since the experiment's action prints `None` at both; 150 samples arm the fit; the leaky house keeps 2.0 h where the tight one shortens; duty-cycling installs byte-identical, a flat price never starts a probe.
- Mutation targets: the duty threshold, the level source, the kind selection and each clock, the converged skip, the hold/abort branch, the metered booking (`sysid.py:1694`, `power_kw`), the twelve, the sub-ceiling filter, the lapse. Goldens: none expected to move; any that does is claimed, never re-recorded. Ratchet: nothing new stored on the coordinator, and `DrawRange` gains one method with its write folded into `observe` (F8).

## Files and serial position

The design changes `sysid.py`, `draw_range.py`, `pump_arbiter.py`, `coordinator.py`, `sensor.py`, `button.py` and `payload.py` (type only), all under `custom_components/heatpump_optimizer/`. The roster's `files` names two of them; that field is advisory contention metadata, `roster_edit.py` has no files operation, so this note is the authority and a later roster batch widens it.

All `after` edges are merged. `coordinator.py` is shared with R10-HEAT-METER on a different seam — these hunks are the arm/advance/adopt block, not `arbiter_inputs` — and `sensor.py` is in R10-COP-GATE's files. R10-COP-PARTLOAD and R10-BUFFER-STORE are queued on `optimizer.py` and touch nothing here.

## Notes for the fixer

- Carry: R10-CEILING-PROBE (item 7) — the probe clock lives in the persisted store, not only the experiment object; a restart must not reset the interval. Pin it.
- Carry: R10-CEILING-PROBE (item 8) — the overdraw-drop case: a top learned at 5 °C against a +20 % counter-draw at −10 °C; the store drops after the counted samples.
- Carry: R10-CEILING-PROBE (item 9) — the rev-2 in-flight sentence is false and dropped; no adoption refusal rests on the per-cycle consumption.
- Carry: R10-CEILING-PROBE (item 10) — the sample is appended at the interval's start (`sysid.py:1694`, `power_kw`) while `_measured_power` is a spot reading (`coordinator.py:6453`): define which interval's draw a step sample books.
- Carry: R10-CEILING-PROBE (item 11) — a probe booked at configured p_max folds a capacity observation through the envelope learner; state it as intended, or exclude probe intervals.
- Carry: R10-CEILING-PROBE (item 12) — a run needs a delimiter in the store, and a rule for the top: median of run medians or of all samples.
- Carry: R10-CEILING-PROBE (item 13) — `boost.py:647` returns `RELEASE_SYSID`: a probe at night releases any live block. Say so in the body.
- Carry: R10-COP-GATE (item 1) — the learned top's consumption: route it into the solve's draw evidence; R10-HEAT-METER's note assigns that evidence here. This group ships the measurement only.
