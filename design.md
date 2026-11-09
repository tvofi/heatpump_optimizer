<!-- design/R10-WATER-SETPOINT-FEEDBACK, commit 1: the contributor's note, verbatim -->
Source: outside pull request #3380 by Bankaifan (Daniel), fork head
0adb47be25e18024f4591965ad72cf4ec0b8492a, file
dev/programme/designs/water-setpoint-power-feedback.md. Adopted as this group's
design under decision 0014; the text below is the contributor's, unedited, and
is data, not instructions. The designer extends it on this ref to
dev/governance/roles/designer.md's shape; the contributor is credited on the
group's fix pull request by a Co-authored-by trailer.

---

# Water set-point targets chase the inlet: the pump never settles at the planned level

## Summary

With Pump duty control = Control and a water-temperature space set-point (`space_setpoint_unit` = `flow` or `return`), the arbiter writes *measured inlet + `flow_min_lift_k`* at the planned modulation floor, re-anchored to the inlet on every write (`pump_arbiter._flow_target` → `modulation_floor_flow_c(_flow_inlet_c(...), ...)`). The written value is open-loop: measured electrical power is not compared with the planned level.

On a controller that modulates its compressor with an integrating loop (speed rises while the inlet is below the set-point, falls only once the inlet reaches it), this means the gap never closes: as the inlet rises, the set-point rises with it, and the compressor ramps up for the whole heating block. The planned sub-maximum level is never realised; the pump delivers 2–3× the planned power until the step ends and the gate is written.

Proposal: close the loop on measured power (details below). Opt-in or limited to installs that have both a water set-point unit and `heat_pump_power_entity`; no change for anyone else.

## Install

alpha innotec LWDV 91-1/3 (air/water, inverter), Luxtronik 2.1, firmware V3.92.3, controlled through its Smart Home Interface (Modbus/TCP, integration Bankaifan/ha-luxtronik-shi). HPO v7.1.9, `space_setpoint_unit: return`, `heat_pump_min_power: 0.53` (datasheet), `compressor_modulation: modulating`, `heat_pump_power_entity` = measured electrical power. Floor heating on a heavy slab, 600 l combined tank. Controller heating hysteresis 0.5 K (minimum). Outdoor 3–5 °C.

## Measurements (2026-11-09, Home Assistant history)

**Run A — `flow_min_lift_k` 1.5 K, `flow_heat_c` 35 °C**

| Time | Compressor | Electrical | Written return set-point | Measured return |
|---|---|---|---|---|
| 18:41 | 52 Hz | ~1.2 kW | 28.5 °C | 25.1 °C |
| 18:50 | ~69 Hz | ~1.6 kW | 29.0 °C | 25.2 °C |
| 19:00 | 80 Hz | 1.95 kW | 30.0 °C | 26.4 °C |

Planned level during the run: 0.23–1.3 kW. Ramp ≈ 1.4 Hz/min.

**Run B — `flow_min_lift_k` 0.5 K, `flow_heat_c` 32 °C, manual plan pinning space heating, planned level constant 0.53 kW**

| Time | Compressor | Electrical (5-min mean) | Written return set-point | Measured return |
|---|---|---|---|---|
| 19:35 | ~50.7 Hz | 1.13 kW | 26.5–27.0 °C | 26.0 °C |
| 19:45 | ~53.8 Hz | 1.22 kW | 27.0 °C | 26.4 °C |
| 19:55 | ~57.7 Hz | 1.33 kW | 27.5 °C | 27.0 °C |
| 20:10 | 62.7 Hz | 1.47 kW | 28.5 °C | 27.7 °C |

Ramp ≈ 0.4 Hz/min. One compressor start, no cycling; the controller's start programme holds 52 Hz for ~3 min before it regulates. The set-point entity still had a 0.5 K step here, so +0.5 K was written as +0.4 … +1.0 K.

**Run C — as Run B, set-point entity now with a 0.1 K step (ha-luxtronik-shi update, same running cycle)**

| Time | Compressor | Electrical (5-min mean) | Written return set-point | Controller readback (input 10101) | Measured return |
|---|---|---|---|---|---|
| 20:18 | 64.0 Hz | 1.48 kW | 28.5 °C | 28.5 °C | 28.0 °C |
| 20:23 | ~64.8 Hz | 1.51 kW | 28.8 °C | 28.8 °C | 28.3 °C |
| 20:30 | ~65.7 Hz | 1.57 kW | 29.1 °C | 29.1 °C | 28.6 °C |
| 20:35 | 66.8 Hz | 1.58 kW | 29.1 °C | 29.1 °C | 28.7 °C |

The gap is now exactly 0.5 K at each write (shrinking to ~0.3–0.4 K until the next write as the inlet rises). The ramp drops to ≈ 0.16 Hz/min (steps of ~1 Hz every ~5 min) but does not stop: any persistent positive gap keeps the controller's integrator rising. Planned level throughout: 0.53 kW.

Earlier observation on the same install (separate review): the compressor can hold 26–31 Hz / 500–600 W, but only while the gap set-point − inlet stays at or below ~0.5 K, i.e. when the inlet actually reaches the set-point. Ramp rate there was roughly 0.9 Hz/min per kelvin of gap.

## Why the current design cannot settle

- Floor value = inlet + lift, recomputed from the live inlet ⇒ gap ≥ lift for as long as the step heats.
- An integrating controller only reduces speed when gap ≤ 0 ⇒ it never does, short of the ceiling (`flow_heat_c`) or the gate.
- At low planned levels the ceiling is never reached, so speed rises monotonically until the step ends.
- Side effect: measured power is consistently above the planned level, so learners that read measured power (capacity curve, COP, power range) see a level the plan never asked for.

## Proposal: power feedback on the water set-point

While a step heats and the pump is running (measured power above a small running threshold, not defrosting):

1. Error `e = P_measured − P_planned` (electrical, kW), filtered (e.g. 2–3 min mean; the meter updates every few seconds).
2. Adjust the written set-point around the inlet instead of always above it:
   - `e > +deadband` (pump above plan): write `inlet + lift_adj`, with `lift_adj` decreasing towards `−lift_max_down` (e.g. −1 K). A target at or below the inlet makes the controller's integrator wind down.
   - `e < −deadband` (pump below plan): increase `lift_adj` towards the configured `flow_min_lift_k` and above, up to the existing level interpolation and the ceiling.
   - Inside the deadband: hold the last written value (do not re-anchor to the rising inlet).
3. Step size and rate limit per write (e.g. 0.2 K per minute) so the controller's own loop is not fought.
4. Start of a run: keep today's behaviour (inlet + lift, or more, so a stopped compressor starts past the controller hysteresis); feedback begins after a start-hold time (e.g. 5 min, covers the start programme).
5. Never write above the ceiling, never below the gate floor; the gate still ends the step.
6. Only with a water set-point unit and a configured `heat_pump_power_entity`; otherwise unchanged. Optionally behind an option (default off for one release) if you prefer.

The house-side planning is untouched: the plan still decides kW per step; the water temperature becomes the result of delivering that power into the slab, which is what the planner assumes anyway.

## Acceptance (what we can verify on this install)

- With a pinned space slot at the modulation floor, compressor frequency settles (no monotonic rise over 30 min); mean electrical power within ±20 % of the planned level after the start-hold.
- With a higher planned level, power follows the level within the same tolerance.
- No additional compressor starts compared with today.
- No behaviour change for `space_setpoint_unit: indoor` or without a power entity.

We can run the acceptance test on this install and report the same history tables.

---

<!-- commit 2: designer's extension under dev/governance/roles/designer.md steps 2-7; the text above is unchanged -->

# Design note (designer seat)

**Base.** Code read at `origin/main` 1cabb845d61754d333005b64d3df14d55827d0c6. The predecessor
R10-WATER-SETPOINT-LIFT merged as #3372 (b944521a2fa01e737372ea7dd81bd3ed3ab00d30), which is an ancestor of the base, so
there is no separate predecessor handoff head. **No finder harness: contributor report** (outside PR #3380, Runs A–C
above). The step 6 simulation below is the reproduction. The claim was re-read at the base: `pump_arbiter.py:756`
recomputes `modulation_floor_flow_c` (`thermal_model.py:1667`) from `_flow_inlet_c` on every pass.
`ArbiterInputs.measured_power_kw` has one reader, the ledger's run/idle test in `_observe` (`pump_arbiter.py:1196`).
It is never compared with `_step_kw`.

## 2. Owning seam

- **Owner:** `pump_arbiter.py`. `_flow_target` computes the target. `ArbiterState` (`pump_arbiter.py:256`) holds the
  loop's state, because it already owns the written record (`written`) and the step ledger (`step`).
- **Callers only:**
  - `desired` → `_space_target` → `_flow_target`. `state_for(coord)` is threaded from `desired`, which already holds `coord`.
  - `coordinator.arbiter_inputs` publishes the snapshot.
- **Unchanged:** `thermal_model.py`. `flow_setpoint_for_level` and `modulation_floor_flow_c` stay the open-loop
  feed-forward. One exception: the docstring sentence "The set-point is a power command" at `thermal_model.py:1675`
  is false for an integrating controller and is corrected.
- `tests/seam_map.json` maps coordinator methods only (`arbiter_inputs` is `views`), so it names no arbiter seam.
- **One owner**, so this is not a stop.
- **Design finding, files list.** Defrost reaches the arbiter only through the coordinator. The arbiter has zero
  defrost reads; the one predicate is `freq_control.defrost_interval`. So the snapshot needs one field, and
  `custom_components/heatpump_optimizer/coordinator.py` must be added to the group's `files`.
  - Fallback, if the coordinator line budget has no headroom: the arbiter reads the defrost entity through its own
    InputReader, as `live_power_kw` reads power, and passes it to `defrost_interval`.
  - The orchestrator edits the roster; this seat does not.

## 3. Shape

**Qualifying pass.** The loop runs only when all of these hold:
- the unit is `flow` or `return` (`_flow_unit`);
- `heat_pump_power_entity` is configured;
- the duty is exactly `space`;
- no system-identification action (`_experiment_kw` is None);
- the planned level is below the band top;
- not defrosting;
- if the owner chooses the option, the option is on.

Any other pass writes today's value and **resets** the loop record.

**State.** A new, unpersisted record on `ArbiterState`:
- run start;
- the unrounded set-point W, in °C;
- a deque of (time, measured kW) covering the filter window;
- the last adjustment time.

It is unpersisted because `_persist` stores only `written`. A restart re-enters the start-hold, which is today's
behaviour. W is kept unrounded so that sub-step increments accumulate. With the entity's 0.5 K step in Run B, a
0.2 K/min nudge would otherwise round away.

**Per qualifying pass**, with `now` the pass time and `base` today's open-loop target from `flow_setpoint_for_level`:

```
P_plan  = _step_kw(plan, now)                       # electrical kW, same unit as heat_pump_min_power
P_meas  = mean of deque over WINDOW (3 min); None when the deque is empty or measured_power_kw is None
running = P_meas is not None and P_meas >= _ran_kw(inp)
if not running or record empty:      W = base; run start = now            # today's write: start past hysteresis
elif now - run start < START_HOLD (5 min): W = base                       # start programme
elif |P_meas - P_plan| <= DEADBAND (max(0.1*P_plan, 0.05 kW)): W unchanged (no re-anchor to the rising inlet)
else: W += -sign(P_meas - P_plan) * RATE (0.2 K/min) * minutes since last adjustment
W = clamp(W, lo = max(inlet - DOWN_K (1 K), gate value + one entity step), hi = flow_heat_c ceiling)
write _bounded(W) as today
```

The rate is measured in time, not per pass. Passes come from the cycle, the one-minute tick and the entity-change
listener (`coordinator.arbiter_inputs` docstring), so their count per minute is not fixed. The constants live in
`pump_arbiter.py` beside `RUN_SETTLE`, and the fixer may tune them only within the acceptance tolerance.

**Interfaces that change:**
- `_flow_target` and `_space_target` gain the ArbiterState argument.
- `ArbiterInputs` gains a defrost boolean.
- Persisted payload keys: none.
- Entity attributes: none.
- Under the owner's option answer, one options-flow key.

**Invariants:**
- **I1.** An `indoor` unit, or no `heat_pump_power_entity`, leaves every slot's write byte-identical to today, for
  every duty.
- **I2.** A heating step never writes at or below the gate value (R10-SETPOINT-BOOST), and never above the ceiling.
- **I3.** The first write of a run equals today's value.
- **I4.** DHW, both, idle, experiment, defrost, release and full-level passes write today's value.
- **I5.** The planner and the plan are unchanged, so a flat-price plan is byte-identical.

## 4. Alternatives

- **A1. Anchor the floor once per plan step and hold it.** This is #3372's forward-carry: the fork's start-then-hold
  sequence.
  - It stops the re-anchor. It still never reads power, so an integrating controller ramps for as long as the
    inlet sits below the held value, and the level reached is set by step length rather than by the plan.
  - It lost: no power reference, so it cannot meet acceptance.
  - Its useful half, holding instead of re-anchoring, is the deadband branch above.
- **A2. Reuse the frequency loop in `freq_control.py`.**
  - That loop owns the compressor-frequency slot, `FrequencyMap` and the watchdog, for installs whose plan writes
    frequency.
  - Driving the set-point slot from it would give that slot's state two owners, and its kW-per-Hz map learns
    nothing about a set-point.
  - It lost on state ownership.
- **A3. Run the loop in the coordinator, which already holds `_measured_power`.**
  - Two modules would then decide one write. The coordinator is the ratcheted core, and the arbiter already
    receives measured power in its snapshot.
  - It lost on coupling.
- **A4. Make `flow_setpoint_for_level` closed-loop.**
  - That function is pure and is also the pricing-side mapping. Feedback needs state across passes, which would
    have to be passed in from the arbiter anyway.
  - It lost on state ownership.

## 5. Sibling sites

Enumerated by
`git grep -n -E '_flow_target|_flow_inlet_c|modulation_floor_flow_c|_experiment_kw|flow_setpoint_for_level' -- 'custom_components/*.py'`:

| site | covered how |
|---|---|
| `flow` unit (`_flow_unit`, `pump_arbiter.py:343`) | Covered by the same path. Today a flow target settles where the condenser ΔT equals the lift: steady, but at a level set by the lift rather than the plan. The loop moves it onto the plan. The simulation covers both units. |
| `return` unit (`_return_unit`, `_as_target`, `_full_draw_c` `pump_arbiter.py:729`) | Covered. `_full_draw_c` is untouched: the loop never writes above the ceiling, and it is off at full level, so ceiling evidence is unchanged. |
| `_experiment_kw` (`pump_arbiter.py:548`, used in `_flow_target` and `_band_kw`) | **Out of scope; loop off.** System identification fits the response to a commanded set-point, and the ceiling probe needs the ceiling. A feedback-moved W would corrupt both. |
| defrost | **Loop frozen and reset.** A reversing cycle's draw is not a response to W (`defrost_interval` docstring). |
| DHW and `both` (`desired`, `pump_arbiter.py:861`; disinfection promotes space to both) | **Loop off.** The meter then includes the DHW draw. The space slot writes the gate or the share as today. |
| baseline and `release` (`_flow_target`'s fallback hold) | Unchanged. The loop record is reset. |

## Learners that read measured power

The plan is unchanged. What changes is that measured power moves toward the asked level, so evidence that
`COP_TRACKING_ERROR_GATE` and `draw_range._disagrees` reject today starts to fold.

- **`coordinator._interval_space_power`.** The gate is \|measured − commanded\| / commanded > `COP_TRACKING_ERROR_GATE`.
  More intervals will pass.
- **`_fold_measured_cop`.** Its `judge_floor` and `judge_ratio` compare against `_commanded_power`.
- **`draw_range.fold`, `observe`, `follows_ask`.** `observe` is asked against drawn. `_flow_command` passes the written
  value as `FlowCommand.written`, which is the draw_range censoring input.
- **`_fold_capacity_envelope`.** Only at commanded ≥ 0.95·p_max. The loop is off at full level, so this is unchanged.
- **Read-only consumers:** accuracy, `_track_realised_peak`, external-heat and immersion detection.

**What the fixer shows** for this set (each in step 6):
- The draw_range verdicts at full level are unchanged.
- Its censoring still classifies only ceiling writes as ceiling evidence.
- `draw_range` learns no set-point-to-power map from a W the loop chose.

## 6. Evidence plan

All checks live in `tests/features.py`, as new check sections beside the R10-SETPOINT-POWER and return-unit sections
that already exercise `_flow_target`.

1. **Failing test.** A simulated integrating controller:
   - speed += k·(W − T_in)·dt, clamped;
   - P = f(speed);
   - T_in follows a slab first-order lag driven by P.

   It is driven through the real `desired` path, with:
   - return unit;
   - plan pinned at 0.53 kW;
   - `flow_min_lift_k` 0.5;
   - entity step 0.1 K;
   - 60 simulated minutes at one-minute ticks, plus random listener passes.

   Asserts:
   - after the start-hold, the mean P is within ±20 % of plan;
   - no monotone rise in speed over the last 30 minutes;
   - one start.

   At the base it fails: P rises past 2× plan, which matches Run B/C. It passes with the fix.
2. **Repeats of the simulation:**
   - with a 0.5 K entity step (the quantization case);
   - for the `flow` unit (today: steady but off-plan; fixed: on-plan);
   - at a higher planned level (tracks the level).
3. **Invariant I1 with a null control.** For a matrix of units × duties × levels, replay a pass sequence twice: once
   with arbitrary measured power, once with power None. The writes must be identical for `indoor`, and for no power
   entity. The null control is the same replay for `return` with the power entity, which **must differ**; that
   proves the harness moves.
4. **I2–I4.** Pins for:
   - the gate clamp on a tank at or below the gate;
   - defrost, experiment, DHW, both, full level and release equal to the open-loop value;
   - a first-of-run write equal to today's.
5. **Null control for the loop.** With measured power equal to plan, W stays within one entity step of its first
   post-hold value for 30 minutes. A perturbation that restores the re-anchor makes test 1 fail again.
6. **Goldens.** No plan golden moves. The fixer runs `GOLDEN_MODE=drift` against the merge base, and it must show
   none. Under the option answer, `tests/golden/config_flow.json` moves with a `tests/golden/claimed_drift.txt`
   row, and `tests/config_flow_steps.py` gains the step. These also join the `files` list.
7. **Mutation proof targets**, all in `pump_arbiter.py`:
   - the qualifying-pass predicate (each conjunct);
   - the deadband hold branch (mutated to re-anchor);
   - the time-based rate;
   - the start-hold comparison;
   - the lower clamp's gate term;
   - the unrounded accumulation (mutated to round W).
8. **Field acceptance.** The contributor's own history tables on the install above, after merge. This is not a gate.

## 7. Hot files, serial position, carries

- **Hot files:** `pump_arbiter.py` and `const.py`, plus, under the option answer, `config_flow.py`, `strings.json`,
  translations and `docs/configuration.md`.
- **Serial position:** after R10-WATER-SETPOINT-LIFT, which is merged. The roster's note admits overlap on
  `pump_arbiter.py` with R10-ARBITER-OFF-RESTORE (off/unload restore). This group touches the heating-step target
  and its held state only, so whichever merges second rebases onto `release` and `desired`.

## Decision: owner

`decision: owner`: is the loop on by default for every qualifying install (water unit + power entity), or behind an
option that is off for one release?

- **Designer's lean: option, off for one release.** The evidence is one controller family (Luxtronik 2.1), measured
  on one install.
  - A controller that is proportional rather than integrating may already settle. The loop is harmless there,
    because it holds inside the deadband, but that is unmeasured.
  - The option costs one key, the docs and the config_flow golden row listed in step 6.
- **Default-on** needs no option. Every qualifying install would get the I1-gated behaviour in one release.

## Notes for the fixer

- `Carry: R10-WATER-SETPOINT-FEEDBACK (item 0)` — The fix pull request carries the contributor's Co-authored-by
  trailer, as the roster's carry states.
- `Carry: R10-WATER-SETPOINT-FEEDBACK (item 1)` — #3372's start-then-hold and anchor-once-per-step are answered by
  the start-hold and the deadband hold. A1 above records why neither alone is the fix.
- `Carry: R10-WATER-SETPOINT-FEEDBACK (item 2)` — Confirm that `power_schedule` is electrical kW, which
  `heat_pump_min_power` 0.53 against a 0.53 kW plan suggests, before comparing it with the meter. Test 1 pins the
  unit.
