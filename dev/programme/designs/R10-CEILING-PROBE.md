# R10-CEILING-PROBE — architect note (design)

Read at `origin/main` 3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f; predecessors R10-SETPOINT-BOOST, R10-CI-LAYOUT and R10-NIGHT-FOLDS are merged there, so no handoff head differs. Issues #2498, #2808, #2465 (carry). Fixer-seat harnesses: probe_duty.py (sha1 0d3fbd4541c8a1b7aa0a4ed6304ba55c1828dff5), probe_draw.py (sha1 f4a4344c30aadf764929ec473d1ada2b11eb1e5f); the fixer commits both under `dev/audit/harnesses/` in step 2.

## Owning seam

`custom_components/heatpump_optimizer/sysid.py` owns *when* the experiment runs and what it commands; `custom_components/heatpump_optimizer/draw_range.py` owns what a sample teaches the band. `custom_components/heatpump_optimizer/pump_arbiter.py` only translates an action into a set-point and `custom_components/heatpump_optimizer/coordinator.py` only wires. One owner per concern, no split.

## Decisions

**(a) Actuation through a flow set-point.** Today `pump_arbiter._planned_duty` returns `None` for a system-identification action, so the baseline hold (curve or `FLOW_HOLD_C`) is written and the fit books `step_power x COP` that was never commanded (probe_duty.py: step 5.0 kW gives duty None). Change, at two arbiter sites: `_planned_duty` yields duty `space` while the action's power is above the on-threshold and `idle` otherwise (relax writes the gate); and `_flow_target` (`pump_arbiter.py:613-623`) gains a system-identification branch ahead of the `flow_setpoint_for_level` call that writes the **configured ceiling** (`configured_flow_heat_c`) through the same `_bounded` clamp. That branch is the ceiling-write site; without it duty `space` follows `_band_kw`'s p_max and self-censors once the top is learned. Intermediate levels are **not** calibrated here: the probe measures one point (ceiling); the gain below it stays #2465 carry 1's residual.

*Pre-step comfort bound.* A ceiling step delivers at most configured p_max x COP. Before the step, `_begin_step_phase` (`sysid.py:1547-1570`) runs the existing sizer/rollout (`_size_step_power` over `_predict_step_excursion_plant`) with the step fixed at configured p_max x COP and `step_hours`; where the predicted peak passes `max_excursion_c` it shortens the step to the longest duration in whole cycles that stays inside it, and below one full hour (2 samples) refuses with the published reason "ceiling step exceeds the comfort bound". The probe kind (b) runs the same bound against the room temperature at its start (it has no settle phase). The post-hoc excursion abort stays as the second control.

*Booking on set-point installs* (`coordinator.py:10984-10991`). The override's `power` and `power_normalized` into `boost.adopt_plan` become configured p_max and 1.0 for a step (what the ceiling commands, the same booking a full-level plan step makes), 0.0 in relax. The fit's delivered heat per step sample is the metered draw x COP (`_measured_power`), replacing `sysid.py:1694`'s sized-step booking; a set-point install with no meter refuses to arm with a published reason. Both kinds publish under `REASON_SYSTEM_IDENTIFICATION` (`payload.py:115`); the probe is distinguished in the sysid view's result reason, not by a new payload reason.

**(b) Probe-only run on converged houses (#2808).** `conditions_met` keeps refusing the *fit* at `learner_samples >= converged_samples`. A second experiment kind, the ceiling probe, shares the night window, outdoor band, price percentile, freeze abort (#1523) and comfort bound (a); no settle, a ceiling step of `step_hours` (or the shortened one), relax at the gate, no fit, no adoption. Eligible only where `pump_arbiter.flow_command` is non-`None` and a meter is configured, and the band top is unlearned or due (c). Gate wiring: `coordinator.py:10970-10975` passes the experiment kind beside `learner_samples`; `conditions_met` skips only the converged check for the probe kind.

*Cadence state.* The probe owns its own last-run and interval on `SystemIdentification`, persisted beside `last_run` in its view (`sysid.py:2345`): interval 7 days while the top is unlearned, 30 days once learned. `arm()`'s `min_days_between_runs` check (`sysid.py:1365-1374`) reads only the fit's `last_run`; neither kind's run moves the other's clock. On a house still eligible for the fit, the button and auto-arm choose the fit when its clock allows (a fit's ceiling step is also a probe run), else the probe; never both in one night (one experiment active, as today).

*Fit steps feed the probe store.* After (a) every set-point fit step is a ceiling step, so its step samples enter the probe store and stamp the probe's last-run. Outcome published (#2808) as the result reason: completed with sample count and drawn median, refused with the gate's reason, or aborted with the freeze's reason.

**(c) Minimum probe samples and re-test.** probe_draw.py: one run gives 4 ceiling samples (2 h at the 30 min cadence) against `MIN_SAMPLES` 48; `observed()` gives `(1.5, None)` and the clamp stays unengaged even at 48 (48/336 below `DISAGREE_SHARE`). So probe samples do not enter the rolling window's percentile; they go to a separate probe store on `DrawRange` (persisted beside idle draws), and the top is set from it when it holds **12 samples from at least 3 distinct runs**, each run contributing at least 2 step samples (a run aborted or shortened below 2 contributes none; one aborted after 2 contributes the samples it took), whose per-run medians agree within `AGREE_TOLERANCE`; the top is their median, and it replaces the configured max under the existing `_metered_range` rule (only when more than `AGREE_TOLERANCE` below). A probe-learned top bypasses the disagreement latch: it is a direct measurement, not a disagreement statistic. **Re-test, so it cannot self-censor:** the probe writes the configured ceiling, never one derived from the learned top, so every probe is uncensored by construction; non-probe samples commanded at the ceiling (`_evidence`'s full flag) drawing more than `AGREE_TOLERANCE` above the learned top drop the probe store only on a count (fixer note item 4); and a probe top lapses 45 days after its newest run.

**Mild-band top (owner decision, orchestrator ruling under mandate scope all; tvofi may override).** A pump's capacity falls with outdoor temperature, so a top learned in the -5..10 °C band over-states cold-weather capacity; it does not under-book. Accepted: the mild-band top with the 45-day lapse; the planner clamps to min(learned, configured); the configured p_max stays the owner's override.

**Cross-impact on sysid results.** Results adopted on set-point installs before this fix rest on an uncommanded step (the D15 ventilation-detector lead citing #2808). No refusal is added: `_adopt_system_identification` (`coordinator.py:10998-11011`) runs every cycle right after `_run_system_identification` (`coordinator.py:6217-6218`) and replaces the result with `completed=False` on admit and refuse alike, so no completed-but-unadopted result survives to refuse, and past adoptions are already applied. An experiment in flight across the upgrade finishes under new code, which actuates its remaining step. The body states past adoptions are not rewound.

## Alternatives rejected

- Map the step through `flow_setpoint_for_level`: one call site fewer, but its p_max is `_band_kw`'s, so once the top is learned the probe writes a sub-ceiling set-point and censors itself.
- Feed probe samples into the rolling window and lower `MIN_SAMPLES`: changes the clamp for every install, including duty-cycling ones the brief requires unchanged.
- Lift the converged guard for the whole experiment: re-runs the heat-loss fit on 482-sample houses and lets a single night overwrite a converged scale through `adoption_decision`.

## Sibling sites

`rg -n '"system_identification"|_sysid_step_off_loop|learner_samples=' custom_components/heatpump_optimizer` — `_planned_duty` and `_flow_target` (arbiter, both changed), the coordinator's override booking (`coordinator.py:10984-10991`, changed) and gate call (`coordinator.py:10970-10975`, changed), `boost.py`'s action check (pass-through, confirmed by test), `sysid.py:1694` (changed).

## Evidence plan

- Failing tests first, in test scripts the fixer names: sysid step on a set-point install writes the ceiling and relax writes the gate (probe_duty.py control inverted); converged house arms a probe, not a fit, and publishes its outcome; 11 probe samples or 2 runs leave the top configured, 12 from 3 runs set it; a ceiling-commanded overdraw drops it; lapse at 45 days.
- Comfort bound: a plant whose ceiling rollout passes the allowance shortens, then refuses under one hour; probe vs fit clocks independent; fit ceiling step feeds the probe store.
- Synthetic pump with known maximum 3.0 kW recovered within `AGREE_TOLERANCE`; duty-cycling install byte-identical (null); flat price: probe never starts (price gate null); gate-held idle draw 1.4 kW above idle as a control (#2465 carry 3).
- Mutation targets: the duty branch in `_planned_duty`, the sysid branch in `_flow_target`, the metered-draw booking at `sysid.py:1694`, the 12/3 threshold, the overdraw drop, the lapse.
- Goldens: none expected to move; any that does is claimed, not re-recorded.

## Hot files and serial position

`custom_components/heatpump_optimizer/sysid.py`, `custom_components/heatpump_optimizer/draw_range.py`, plus `custom_components/heatpump_optimizer/pump_arbiter.py` and `custom_components/heatpump_optimizer/coordinator.py` (not in the roster's hot list; the roster owes that edit; order against design/r10-livestate, which touches both). All `after` predecessors are merged; R10-COP-PARTLOAD and R10-BUFFER-STORE also touch the band and queue behind this group if dispatched together.

## Notes for the fixer

- Carry: R10-CEILING-PROBE (item 1) — a learned top clamps `_band_kw`'s p_max; assert the full-level step still writes `heat_c`, so plan-driven ceiling samples keep accruing.
- Carry: #2465 (item 2) — set-point-to-draw gain at intermediate levels stays uncalibrated; the probe measures the ceiling point only.
- Carry: R10-CEILING-PROBE (item 3) — no-meter set-point installs refuse to arm; publish the reason.
- Carry: R10-CEILING-PROBE (item 4) — the overdraw drop needs at least 2 samples over the learned top (or a median over a window), and DHW-active samples are excluded, as `coordinator.py:4754-4781` subtracts a DHW share; a single defrost spike or immersion step must not drop the store.
- Carry: R10-CEILING-PROBE (item 5) — test a synthetic 3.0 kW pump with a 3 kW immersion step during the probe: the learned top must not inflate (exclude samples where an auxiliary heater is reported on, or refuse the run).
- Carry: R10-CEILING-PROBE (item 6) — `sysid.py:1694` books `self._step_power * thermal_cop`; on set-point installs it books metered draw x COP, pinned by a mutant that restores the sized step.
