Builds R10-WATER-SETPOINT-FEEDBACK from the approved design note (design/R10-WATER-SETPOINT-FEEDBACK at 1442f9067ab3592ef5ed7c3389809539324c4ad1, `Design review: approve` at d3623f5b35777e4461fe62359e03ba84997fefc6), adopted from outside pull request 3380 (contributor Bankaifan, fork head 0adb47be25e18024f4591965ad72cf4ec0b8492a, a design note only). With Pump duty control at Control and a water space set-point (`space_setpoint_unit` flow or return), `pump_arbiter._flow_target` wrote the live inlet plus `flow_min_lift_k`, re-anchored every pass, and never compared `ArbiterInputs.measured_power_kw` with the planned level, so a controller that integrates on set-point minus return ramped for the whole heating block (the contributor's Luxtronik 2.1 runs: planned 0.53 kW, measured 1.13-1.58 kW). The arbiter now closes that target on measured power: `pump_arbiter._feedback`, its run record `FeedbackRun` on `ArbiterState` (unpersisted), the qualifying predicate `_feedback_on`, and the controller-clamp adoption `_clamp_cut` in `hold`. Gated by the new option `space_setpoint_power_feedback` on the advanced Sensors and entities page, default on (tvofi 2026-11-09, Carry 4), shown for a water unit and acting only with `heat_pump_power_entity` configured; every other install writes as before (I1, pinned below). No issue: roster group R10-WATER-SETPOINT-FEEDBACK, issues `[3380]`. Close 3380 with thanks once this merges.

Contributor ask (design note's fixer item 6, not waited on): @Bankaifan, please run the note's §Acceptance on the install and report the same history tables, with the controller preconditions now in `docs/configuration.md` (heating hysteresis at most the lift; parameter 979 below the heating-season return; the integration polling within 600 s and restoring heating mode after a controller restart; no second writer of 10000/10001). The simulation below says the wind-down from the 52 Hz start programme to a 0.53 kW plan takes about two hours on a 0.5 K hysteresis; read acceptance's "±20 % after the start-hold" against the last 30 minutes of a long block, not the first.

Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>

## Design items answered in code

- Shape (§3): per qualifying pass, after `FEEDBACK_START_HOLD` (5 min) of today's target, the target moves `FEEDBACK_RATE_K_PER_MIN` (0.2 K/min, time-based, from the run's last pass) against the error of the `FEEDBACK_WINDOW` (3 min) mean draw, is held inside the deadband, and stays in `_feedback_bounds`: at most `FEEDBACK_DOWN_K` (0.3 K) below the inlet, past no stop bound or controller cut, one entity step above the gate, at most the ceiling. Unrounded `w_c` accumulates.
- Seam: `pump_arbiter.py` only computes; `coordinator.arbiter_inputs` publishes one field, `ArbiterInputs.defrosting`, the raw `PumpSignals.defrosting` (§2 design finding: `coordinator.py` joins the group's files). The arbiter asks `freq_control.defrost_interval` itself, the P2 registry's owner of that decision (`tests/entities.py` `defrost_standoff`); no new read path.
- Departure, named: the feedback is applied in `desired` around `_space_target`'s value, not threaded into `_flow_target`/`_space_target` as the note's interface section says. `_flow_target` stays the pure open-loop feed-forward that `_flow_command`, `draw_range` and the existing checks read; the loop's state is touched in one caller.
- R1 (anti-windup): `_clamp_cut`, called in `hold`'s held branch for the space slot. A reading inside `[record the loop write replaced, the write] ± SETPOINT_TOLERANCE` is adopted as the record and as a one-sided cut bound for the run; `hold` reads it as held (no rewrite, miss or `ISSUE_IGNORED`). A cut of today's write keeps today's miss and repair. Design note 10: both sides pinned in one check (0.2 K under: held, no cut; 0.4 K under: cut adopted; 35.0 °C: dropped, run reset).
- R2: option (a), today's start write kept; docs line on hysteresis. Self-caused stop: `_note_stop` records the inlet-to-write gap at a running-to-stopped edge under a loop write below today's target, and `_feedback_bounds` holds the target `FEEDBACK_STOP_MARGIN_K` closer to the inlet than that gap for the life of the `ArbiterState`.
- Design note 7 (the loop's write quantum): taken as the reviewer offered, "force a write". `_note_sent` drops the space record when the loop's target differs from it at all, so `_write`'s `SETPOINT_TOLERANCE` skip cannot leave the controller 0.3 K from the loop's value; an equal value is still not sent, so a held target stays silent (design note 5's purpose kept; `_write` and `hold`'s echo grace unchanged). Without it, the main repeat stalls (mutant "sub-tolerance resend removed", below). With it, the design's 0.3 K margin holds: one 0.1 K step plus a 0.1 K inlet rise between passes, under the 0.5 K minimum hysteresis.
- R3: the integration's polling is a docs precondition; no HPO re-write. A revert to 35.0 °C falls outside the bracket, so `hold` drops the record and `_clamp_cut` resets the run (start hold re-entered). A heating-mode revert is a docs-recorded limitation.
- R4/R5, F1-F6: the fixture below models start at return <= register - hysteresis (0.5 K and 2 K), stop at return >= register + stop hysteresis (0.5 K and 0.1 K), the [979, return limit] clamp with readback, the 35.0 °C revert, and k = 0.9 Hz/min per K cited to #3372's comment of 2026-11-09T20:39:05Z as an install measurement, not firmware. F3: the main run uses 0.1 K steps and no deadband is in kelvin. F5: docs line on a second writer; the rate limit is per loop. F6: the 5 min start hold covers the 3 min start programme.
- Deadband: `FEEDBACK_DEADBAND_SHARE` (10 %) of the planned level, or of the band floor where the plan asks less. The note's absolute 0.05 kW floor was a second module-level 0.05 kW line constant, which `tests/entities.py`'s P2 `channel_active_kw` rule refuses; the band floor is scale-free and gives 0.053 kW on the reporting install.
- Qualifying predicate: duty exactly `space`, water unit, power entity, option on, no defrost, no experiment, no space boost, planned level below the band top. The note's conjuncts for mode, plan staleness and a positive level are implied by `duty == "space"` (`_planned_duty` returns space only from a fresh Auto/Economy plan step that runs, an experiment or a boost), so each would be an unkillable mutant; they are not written.
- Design note's fixer item 2: `power_schedule` is electrical kW: `_band_kw` maps it on `min/max_electrical_power`, and `thermal_model.planned_draw_runs` reads it against the electrical floor; `_nudged` compares it with the meter directly.
- Design review note item 9: `tests/golden/config_flow.json` does not move (the seeded unit is indoor, so the `when=_water_space_setpoint` field does not render, as `flow_min_lift_k` does not), so both claim files stay byte-identical.
- Files outside the roster's `files` list, each owed by the note or the option: `coordinator.py` (§2), `entry_config.py` (the option's typed read), `translations/de.json` (Carry 4's parity), `dev/audit/harnesses/r10_water_setpoint_feedback.py` (fixer.md step 18).

## Recorded limitations, measured by the fixture

- The wind-down is bounded by k x the 0.3 K the target may sit under the inlet: from the 52 Hz start programme (1.2 kW, 2.3x a 0.53 kW plan) the main repeat reaches every-minute-within-20 % only in the block's last 30 minutes of three hours.
- At a higher level the start hold writes the level map's value (31.9 °C at 1.2 kW on a 40 °C ceiling), which drives the compressor to 90 Hz before the loop starts; that repeat needs a four-and-a-half-hour block. Changing the start write is I3, the approved design's; not changed here.
- A 0.5 K entity step: the loop stops the ramp and the speed falls, but the coarse grid rounds the 0.3 K margin away, so the draw does not reach ±20 % of plan in three hours.
- A controller that stops at register + 0.1 K: one extra start, then the learned stop bound holds the target above the inlet, where an integrating controller ramps as today. Bounded, not fixed.

## Carries

- Carry 1 (the contributor's trailer): the `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>` line above, for the squash commit; no commit on the branch carries it, as the seat's dispatch forbids trailers in its own commits.
- Carry 2 (#3372's start-then-hold and anchor-once-per-step): closed here. The start hold (`FEEDBACK_START_HOLD`) writes today's start value, and the deadband branch of `_nudged` holds the target instead of re-anchoring it to the rising inlet; pinned by `R10-WATER-SETPOINT-FEEDBACK: a draw on plan holds the target ...` and the start-hold mutant. Design §4 A1 records why neither alone is the fix.
- Carry 3 (F1-F6, the SHI facts): answered under `## Design items answered in code` (R1-R5 and the F lines) and in `docs/configuration.md`'s preconditions; each fixture condition (start and stop hysteresis, [979, return limit] clamp with readback, 35.0 °C revert, k cited as an install measurement) is a repeat in `tests/features.py`.
- Carry 4 (owner decision: an advanced option, on by default for qualifying installs): `const.CONF_SPACE_SETPOINT_POWER_FEEDBACK`, default `True`, `EntryConfig.space_setpoint_power_feedback`, the `entities` page row with `when=_water_space_setpoint`; `strings.json`, `en`, `de` and `sv` translations; `docs/configuration.md`. A non-qualifying install keeps I1 whatever the option says (I1 check, option-off arm and no-power-entity arms). The config_flow golden does not move (indoor seed), so no claim.
- Carry 5 (design round 2 and the reviewer's notes for the fixer): R1-R5 answered as the approved note says; review note 7 (write quantum) by `_note_sent`'s sub-tolerance send, note 8 (stop model at W + 0.1 K) as its own repeat beside the W + hysteresis model, note 9 (golden claim) as above, note 10 (both sides of the bracket) in one check. The orchestrator's GENERIC-HEAT-CURVE assumption (config_flow refuses a heat-curve displacement entity with a water unit) is not built here: it is the orchestrator's routing, and this branch adds no such refusal.
- Carry 6 (r10-arbiter-off-restore's ordering note, item 0b0152d5: this group goes first on `pump_arbiter.py`, and a record it adds for the space write extends `ArbiterState.written["space_setpoint"]` and `ArbiterState.space_before` rather than adding a second): satisfied at this head. `space_before`, `_arm_space` and `_edited` are that group's and exist on neither side here (`git grep space_before` over `custom_components`: 0 files at origin/main and at 5a03cadb3, measured 2026-11-10T03:12Z; they are on `handoff/r10-arbiter-off-restore`). Every space write this branch sends, the loop's included, lands in the one persisted record `ArbiterState.written["space_setpoint"]` (`_write`, and `_clamp_cut` on a controller cut); `_persist` stores `held.written` and nothing this branch adds. What it adds beside that record is run-scoped and in memory only: `FeedbackRun.sent_c`/`prev_c` (the loop's last target and the record it replaced, read by `_clamp_cut` and `_note_stop` alone) and `ArbiterState.feedback`/`stop_gap_k`. None is an own-write refusal or an edit-adoption record, so that group's two readers stay on `written["space_setpoint"]` plus `space_before` and do not move. The one interaction they must survive, `_note_sent` dropping the record when the loop's target moves, is under `## Forward-carry`, destination that group's brief; its controls M03 and M04/M16 run on that group's branch, after this one merges.
- Carry 7 (the same ordering note, restated on the roster without its carry line): answered by Carry 6's line; it asks nothing further of this head.

## Head

5a03cadb3 (full SHA in the handoff ref), branch `handoff/r10-water-setpoint-feedback`, cut from origin/main b8f67a775137a8032d5c71b34ea64165c1d4613a (merge base; measured 2026-11-10T01:49Z).

## Mutation proof

Failing test first: the R10-WATER-SETPOINT-FEEDBACK block's main check, run against the base's production code (`git archive b8f67a775 custom_components tests/hastub tests/harness.py`, the block extracted with the base-absent `defrosting` field dropped, scratch runner sha1 32ce6fbefa6a2c670e615f25129cb443ffcf0153): `FAIL ... [mean 2.222 kW, every minute within False, starts 1, last speed 90.0 Hz]`, `1 of 1 FB-BASE FAILED`.

Each mutant applied alone to `pump_arbiter.py` in a copy of this head's `custom_components/`, then the R10-WATER-SETPOINT-FEEDBACK block of `tests/features.py` run against it (the block alone; the rest of features.py does not read these lines). Every mutant is killed; failing checks by name:

- `duty conjunct`: 2 failing — `R10-WATER-SETPOINT-FEEDBACK I1 null control: a return unit with a power entity moves on the same replay, and o…`; `R10-WATER-SETPOINT-FEEDBACK: a hot-water pass inside a step resets the run; the next space pass writes today's…`
- `option conjunct`: 3 failing — `R10-WATER-SETPOINT-FEEDBACK null control: the same block with the option off (today's inlet + lift) ramps mono…`; `R10-WATER-SETPOINT-FEEDBACK repeat, 0.5 K entity step: one start, the speed falls over the last 30 minutes, an…`; `R10-WATER-SETPOINT-FEEDBACK I1: an indoor unit, no power entity or the option off writes the same with any mea…`
- `power-entity conjunct`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK I1: an indoor unit, no power entity or the option off writes the same with any mea…`
- `defrost conjunct`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, defrost at minutes 150-154: the loop stands down (today's inlet + lift) an…`
- `experiment conjunct`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK I4: a system-identification step writes the same with any measured draw as with no…`
- `boost conjunct`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK I4: a space boost writes the same with any measured draw as with none…`
- `water-unit guard`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK I1: an indoor unit, no power entity or the option off writes the same with any mea…`
- `band-top conjunct`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK I4: a step at the band top (2.2 kW) writes the same with a draw above it as with n…`
- `deadband floor dropped`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK: below the band floor the deadband is 10 % of the floor, so a sub-minimum plan hol…`
- `deadband hold -> move`: 2 failing — `R10-WATER-SETPOINT-FEEDBACK: a draw on plan holds the target within one 0.1 K step of its first post-hold valu…`; `R10-WATER-SETPOINT-FEEDBACK: below the band floor the deadband is 10 % of the floor, so a sub-minimum plan hol…`
- `deadband hold -> re-anchor`: 2 failing — `R10-WATER-SETPOINT-FEEDBACK: a draw on plan holds the target within one 0.1 K step of its first post-hold valu…`; `R10-WATER-SETPOINT-FEEDBACK: below the band floor the deadband is 10 % of the floor, so a sub-minimum plan hol…`
- `rate per pass, not per minute`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, return limit 27.6 degC under a loop write: no miss and no repair, the cut…`
- `start hold removed`: 3 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, 0.5 K entity step: one start, the speed falls over the last 30 minutes, an…`; `R10-WATER-SETPOINT-FEEDBACK repeat, register reverted to 35.0 degC at minute 150: the next pass restarts the r…`; `R10-WATER-SETPOINT-FEEDBACK repeat, defrost at minutes 150-154: the loop stands down (today's inlet + lift) an…`
- `gate bound removed`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK I2: winding down over a return below the gate never writes the gate (20 degC) or b…`
- `W rounded to 0.5 K`: 6 failing — `R10-WATER-SETPOINT-FEEDBACK: a return target on an integrating controller, plan pinned at 0.53 kW, lift 0.5 K,…`; `R10-WATER-SETPOINT-FEEDBACK repeat, flow unit: every minute of the last 30 within 20 % of plan, one start…`; `R10-WATER-SETPOINT-FEEDBACK repeat, plan 1.2 kW, four-and-a-half-hour block: every minute of the last 30 withi…`; `R10-WATER-SETPOINT-FEEDBACK repeat, return limit 27.6 degC under a loop write: no miss and no repair, the cut…`; `R10-WATER-SETPOINT-FEEDBACK repeat, register reverted to 35.0 degC at minute 150: the next pass restarts the r…`; `R10-WATER-SETPOINT-FEEDBACK I2: winding down over a return below the gate never writes the gate (20 degC) or b…`
- `inlet-down bound removed`: 6 failing — `R10-WATER-SETPOINT-FEEDBACK: a return target on an integrating controller, plan pinned at 0.53 kW, lift 0.5 K,…`; `R10-WATER-SETPOINT-FEEDBACK repeat, flow unit: every minute of the last 30 within 20 % of plan, one start…`; `R10-WATER-SETPOINT-FEEDBACK repeat, plan 1.2 kW, four-and-a-half-hour block: every minute of the last 30 withi…`; `R10-WATER-SETPOINT-FEEDBACK repeat, 0.5 K entity step: one start, the speed falls over the last 30 minutes, an…`; `R10-WATER-SETPOINT-FEEDBACK repeat, register reverted to 35.0 degC at minute 150: the next pass restarts the r…`; `R10-WATER-SETPOINT-FEEDBACK repeat, defrost at minutes 150-154: the loop stands down (today's inlet + lift) an…`
- `R1 bracket -> drop and rewrite`: 2 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, return limit 27.6 degC under a loop write: no miss and no repair, the cut…`; `R10-WATER-SETPOINT-FEEDBACK R1 bracket: a reading 0.2 K under an upward loop write is held (record kept, no cu…`
- `clamp-cut slot test removed`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK: a hot-water set-point read differing from its record is dropped for a rewrite and…`
- `cut bound not set`: 2 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, return limit 27.6 degC under a loop write: no miss and no repair, the cut…`; `R10-WATER-SETPOINT-FEEDBACK R1 bracket: a reading 0.2 K under an upward loop write is held (record kept, no cu…`
- `stop bound removed`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, stop at register + 0.1 K: one extra start at most, and the stop bound is l…`
- `self-caused test never`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, stop at register + 0.1 K: one extra start at most, and the stop bound is l…`
- `revert reset removed`: 2 failing — `R10-WATER-SETPOINT-FEEDBACK repeat, register reverted to 35.0 degC at minute 150: the next pass restarts the r…`; `R10-WATER-SETPOINT-FEEDBACK R1 bracket: a reading 0.2 K under an upward loop write is held (record kept, no cu…`
- `sub-tolerance resend removed`: 4 failing — `R10-WATER-SETPOINT-FEEDBACK: a return target on an integrating controller, plan pinned at 0.53 kW, lift 0.5 K,…`; `R10-WATER-SETPOINT-FEEDBACK repeat, flow unit: every minute of the last 30 within 20 % of plan, one start…`; `R10-WATER-SETPOINT-FEEDBACK repeat, plan 1.2 kW, four-and-a-half-hour block: every minute of the last 30 withi…`; `R10-WATER-SETPOINT-FEEDBACK repeat, stop at register + 0.1 K: one extra start at most, and the stop bound is l…`
- `stale-run reset removed`: 1 failing — `R10-WATER-SETPOINT-FEEDBACK: a run not seen for longer than its averaging window starts over with today's targ…`

## Null control

- Fixture: the same three-hour block with the option off is today's open loop, and must ramp: `R10-WATER-SETPOINT-FEEDBACK null control: the same block with the option off (today's inlet + lift) ramps monotonically past twice the plan, as runs A-C did` passes. The harness reads both ends identically (`## Figures`).
- I1: indoor unit, return without power entity, flow without power entity, return with the option off: each replays 40 passes x 5 duties x 3 levels with a random measured draw and with none, byte-identical (`R10-WATER-SETPOINT-FEEDBACK I1: ...`). Its own null control: the same replay on return with a power entity moves, exactly at `[(0.53, "space"), (1.2, "space")]`.
- The R10-WATER-SETPOINT-LIFT default-options grid (`_NC_AT_MAIN`, 2688 cells through a real coordinator) is unchanged: `null control: with default options every set-point an indoor or flow unit writes, and every held FlowCommand, is main's, cell for cell` passes at this head.
- Flat-price null control: not applicable (no cost figure; I5, the plan is untouched).

## Figures

- `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at c540ff524 (5a03cadb3 adds only `tests/closures.json` and deletes one ledger pin; a closures change scopes the gate `MODE: FULL`, which is CI's to run, `fixer.md` step 5): `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`, `32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT AND NOT RUN` (`tests/arch_score.py`, `tests/ha_contract.py`: no changed file in their measured closures); among them `ALL 5063 FEATURE CHECKS PASSED`, `ALL 2707 ENTITY CHECKS PASSED`, `ALL 9 typing-ruler checks PASSED`, and `tests/env_drift.py --all origin/main` ok (56 scenarios, no plan golden moved, I5).
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py` (sha1 874afca01e6a5928020471983c5d81273f77a816), at this head: `return 0.53 kW option default mean 0.526 kW every-minute-within-20% True starts 1 speed 47.2 -> 28.4 Hz`; `option off mean 2.222 kW ... False starts 1 speed 62.9 -> 90.0 Hz`; `flow 0.53 kW option default mean 0.526 kW ... True starts 1`. The same file run on `git archive b8f67a775 custom_components tests/hastub tests/harness.py`: all three arms `mean 2.222 kW every-minute-within-20% False starts 1 speed 62.9 -> 90.0 Hz` (the base has no loop, so the option is inert there). Rule: mean measured draw over minutes 150-179 of a 180-minute block at plan 0.53 kW; within means every one of those minutes within 20 % of plan.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget re-recorded; `max_class_loc` flat (the coordinator's `arbiter_inputs` gains `defrosting=` and loses a docstring sentence that restated `ArbiterInputs`' own).
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS -0.0012 WORSENS (inadmissible: coord_footprint 2491->2493)`; answered under `## Architecture score`.
- `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/`: empty (config_flow golden and both claim files untouched; design review note item 9).
- Seam census (fixer.md step 8), the design's own enumerator: `git grep -n -E '_flow_target|_flow_inlet_c|modulation_floor_flow_c|_experiment_kw|flow_setpoint_for_level' -- 'custom_components/*.py'`. Every returned site is the design's §5 table, each dispositioned in code: the flow and return units share `_feedback` (both repeats pinned); `_experiment_kw` is a `_feedback_on` conjunct (I4 pin); defrost, DHW and both reset the run (`_feedback_on`'s duty and defrost conjuncts, pins); the baseline and `release` reach `desired` with duty `None` (I1 pin, every duty); `_full_draw_c` and `_flow_command` are untouched and the loop is off at the band top (I4 pin), so `draw_range`'s ceiling evidence is unchanged.

## Architecture score

- `coord_footprint` 2491 -> 2493: the two statements `desired` gains, a water-unit guard and the assignment applying the loop to the space target; `desired` is the arbiter function the coordinator is handed and the one place holding both the space target and the coordinator's arbiter state. The guard keeps an indoor pass from touching arbiter state at all (`tests/features.py`'s L2 range check calls `desired(None, ...)` on an indoor install). Paid down from +10 before handoff: `_feedback_on` takes the boost record instead of the coordinator, and an adopted clamp cut joins `hold`'s existing held branch instead of two new branches.

## Unpinned sites

Each site below is a line this diff adds, as `tools/pr/ci_predict.py` lists them at 5a03cadb3; disposition for every one: pinned by `mutation-autofix` on the pull request (`pump_arbiter.py` is under `custom_components/`, its lane), unmeasured here as a `killed_by` pin. This seat's own mutants of the same lines (`## Mutation proof`) are each killed by the R10-WATER-SETPOINT-FEEDBACK block of `tests/features.py`; a site `mutation-autofix` leaves alive is a survivor for triage, not pinned by this body.

- `custom_components/heatpump_optimizer/pump_arbiter.py:260 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:265 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:272 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:276 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:279 CONST`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:891 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:891 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:897 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:915 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:917 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:920 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:920 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:920 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:922 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:922 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:923 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:923 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:926 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:927 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:930 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:932 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:934 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:934 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:936 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:938 CLAMP_DROP*2`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:941 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:953 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:953 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:953 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:955 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:966 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:969 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:983 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:983 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:997 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:997 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1000 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1013 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1016 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1019 CMP_BOUND*2`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1019 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1022 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1022 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1028 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1115 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/pump_arbiter.py:1287 GUARD_OFF`: pinned by `mutation-autofix`

## Red checks

- `mutation` (predicted, not yet run: no pull request exists): `tests / mutation` refuses the 46 sites under `## Unpinned sites` until `mutation-autofix` pins them (`ci-autofix.md`). Root-cause question: the cheaper detector is `tools/pr/prepr.sh` step 6d (`ci_predict.py`), which already predicted it here at no CI cost; nothing cheaper exists, and the repair is the bot's by rule. A survivor it names is triaged, not pinned.
- `ledger` (predicted, repaired before handoff): STALE PIN `pump_arbiter.py:hold GUARD_OFF 360fba48`, the line `if not _differs(slot, observed, value):` this diff rewrote; the pin file is deleted at 5a03cadb3 and the rewritten line is listed above. Cheaper detector: the same step 6d, which caught it; none cheaper.
- `tests / closures` (predicted, repaired before handoff): INERT READS for the new `dev/audit/harnesses/r10_water_setpoint_feedback.py`, repaired by `python3 tools/pr/ci_predict.py --apply-inert` (5a03cadb3, `tests/closures.json`). Cheaper detector: step 6d; none cheaper.

## Forward-carry

- R10-ARBITER-OFF-RESTORE reuses this group's write record (roster ordering note). At this head the space slot's record is dropped by `pump_arbiter._note_sent` whenever the loop's target moves by less than `SETPOINT_TOLERANCE`, and re-created by `_write` in the same pass (absent after a failed write until the next pass); between those two lines it is absent. A restore that reads `ArbiterState.written` at MODE_OFF or unload reads it after the pass, so it sees the record, but it must not take the space record's absence as "never written" without checking `ArbiterState.feedback`. Precondition, not opportunity; re-measure on that group's merge base. Lands in that group's brief, `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`. Carry: R10-ARBITER-OFF-RESTORE
- The start hold's level-mapped write over-commands an integrating controller at a level above the floor (90 Hz within 15 minutes at 1.2 kW in the fixture, recorded limitations above). Whether the start write should be the floor's inlet-plus-lift on a qualifying install is I3, the approved design's, and is the orchestrator's to route, in `dev/programme/carries/carry-201.json`. Carry: #201

## Friction

none
