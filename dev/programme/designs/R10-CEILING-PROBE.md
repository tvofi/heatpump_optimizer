# R10-CEILING-PROBE — architect note (design)

Read at `origin/main` 3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f; predecessors R10-SETPOINT-BOOST, R10-CI-LAYOUT and R10-NIGHT-FOLDS are merged there, so no handoff head differs. Issues #2498, #2808, #2465 (carry). Fixer-seat harnesses: probe_duty.py (sha1 0d3fbd4541c8a1b7aa0a4ed6304ba55c1828dff5), probe_draw.py (sha1 f4a4344c30aadf764929ec473d1ada2b11eb1e5f); the fixer commits both under `dev/audit/harnesses/` in step 2.

## Owning seam

`custom_components/heatpump_optimizer/sysid.py` owns *when* the experiment runs and what it commands; `custom_components/heatpump_optimizer/draw_range.py` owns what a sample teaches the band. `custom_components/heatpump_optimizer/pump_arbiter.py` only translates an action into a set-point and `custom_components/heatpump_optimizer/coordinator.py` only wires. One owner per concern, no split.

## Decisions

**(a) Actuation through a flow set-point.** Today `pump_arbiter._planned_duty` returns `None` for a system-identification action, so the baseline hold (curve or `FLOW_HOLD_C`) is written and the fit books `step_power x COP` that was never commanded (probe_duty.py: step 5.0 kW gives duty None). Change: a system-identification action yields duty `space` while its power is above the on-threshold and `idle` otherwise, so the relax phase writes the gate. The step writes the **configured ceiling** (`configured_flow_heat_c`) directly — not `flow_setpoint_for_level`, whose output depends on `_band_kw`'s p_max and would follow a learned top (see (c)). On a set-point install the experiment's step power therefore *is* the ceiling: `SystemIdentification.step` sizes the step as today, but where the arbiter actuates by set-point the delivered heat recorded per step sample is the metered draw x COP (`_measured_power`), not the sized step; with no meter configured on a set-point install the experiment refuses to arm with a published reason, because nothing measures what the ceiling delivered. Intermediate levels are **not** calibrated here: the probe measures one point (ceiling), and the gain between set-point and draw below it stays the residual #2465 carry 1 names.

**(b) Probe-only run on converged houses (#2808).** `conditions_met` keeps refusing the *fit* at `learner_samples >= converged_samples`; that guard is right for the heat-loss experiment. A second experiment kind, the ceiling probe, runs where the fit is refused: same night window, outdoor band, price percentile and comfort-excursion abort; no settle phase, a step at the ceiling for `step_hours`, relax at the gate, no fit and no adoption. It is eligible only on an install whose arbiter commands by flow set-point (`pump_arbiter.flow_command` non-`None`) and whose band top is unlearned or due for re-test (c). Cadence: armed automatically, at most one probe per 7 days while the top is unlearned, then one per 30 days (the existing `min_days_between_runs`). The Run System Identification button arms the fit where the house is not converged and the probe where it is; the published outcome (#2808) is one of: probe completed with its sample count and drawn median, probe refused with the gate's reason, or aborted with the freeze's reason — the result's reason string, so the existing sysid view and diagnostics carry it. A learning freeze aborts a probe as it aborts the fit (unchanged #1523 behaviour), but the abort is now visible.

**(c) Minimum probe samples and re-test.** probe_draw.py: one run gives 4 ceiling samples (2 h at the 30 min cadence) against `MIN_SAMPLES` 48; `observed()` gives `(1.5, None)` and the clamp stays unengaged even at 48 (48/336 below `DISAGREE_SHARE`). So probe samples do not enter the rolling window's percentile; they go to a separate probe store on `DrawRange` (persisted beside idle draws), and the top is set from it when it holds **12 samples from at least 3 distinct runs** whose per-run medians agree within `AGREE_TOLERANCE`; the top is their median, and it replaces the configured max under the existing `_metered_range` rule (only when more than `AGREE_TOLERANCE` below). A probe-learned top bypasses the disagreement latch: it is a direct measurement, not a disagreement statistic. **Re-test, so it cannot self-censor:** the probe writes the configured ceiling, never one derived from the learned top, so every probe is uncensored by construction; any non-probe sample commanded at the ceiling (`_evidence`'s full flag) drawing more than `AGREE_TOLERANCE` above the learned top drops the probe store and reverts to configured; and a probe top lapses 45 days after its newest run, so a cold snap after a mild-weather probe re-tests rather than under-books.

**Cross-impact on sysid results.** Every result adopted on a set-point install before this fix rests on an uncommanded step (the D15 ventilation-detector lead citing #2808). The fixer adds an adoption refusal for a stored result whose step was not actuated, keyed on the install kind, and states in the body that past adoptions are not rewound (the learned scale has since moved under passive learning).

## Alternatives rejected

- Map the step through `flow_setpoint_for_level`: one call site fewer, but its p_max is `_band_kw`'s, so once the top is learned the probe writes a sub-ceiling set-point and censors itself.
- Feed probe samples into the rolling window and lower `MIN_SAMPLES`: changes the clamp for every install, including duty-cycling ones the brief requires unchanged.
- Lift the converged guard for the whole experiment: re-runs the heat-loss fit on 482-sample houses and lets a single night overwrite a converged scale through `adoption_decision`.

## Sibling sites

`rg -n '"system_identification"' custom_components/heatpump_optimizer` — the arbiter's `_planned_duty`, `boost.py`'s action check, the coordinator's override. Each reads the action's mode; the fixer covers the arbiter and confirms the boost check stays a pass-through.

## Evidence plan

- Failing tests first, in test scripts the fixer names: sysid step on a set-point install writes the ceiling and relax writes the gate (probe_duty.py control inverted); converged house arms a probe, not a fit, and publishes its outcome; 11 probe samples or 2 runs leave the top configured, 12 from 3 runs set it; a ceiling-commanded overdraw drops it; lapse at 45 days.
- Synthetic pump with known maximum 3.0 kW recovered within `AGREE_TOLERANCE`; duty-cycling install byte-identical (null); flat price: probe never starts (price gate null); gate-held idle draw 1.4 kW above idle as a control (#2465 carry 3).
- Mutation targets: the duty branch in `_planned_duty`, the 12/3 threshold, the overdraw drop, the lapse.
- Goldens: none expected to move; any that does is claimed, not re-recorded.

## Hot files and serial position

`custom_components/heatpump_optimizer/sysid.py`, `custom_components/heatpump_optimizer/draw_range.py`, plus `custom_components/heatpump_optimizer/pump_arbiter.py` (not in the roster's hot list; the roster owes that edit). All `after` predecessors are merged; R10-COP-PARTLOAD and R10-BUFFER-STORE also touch the band and queue behind this group if dispatched together.

## Notes for the fixer

- Carry: R10-CEILING-PROBE (item 1) — a learned top clamps `_band_kw`'s p_max; assert the full-level step still writes `heat_c`, so plan-driven ceiling samples keep accruing.
- Carry: #2465 (item 2) — set-point-to-draw gain at intermediate levels stays uncalibrated; the probe measures the ceiling point only.
- Carry: R10-CEILING-PROBE (item 3) — no-meter set-point installs refuse to arm; publish the reason.
