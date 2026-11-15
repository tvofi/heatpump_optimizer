# R11-OUTSIDE-ROOMS-P2: rooms as one pure module feeding the solver's existing floor-margin array (phases 1, 2, 3a; 3b re-cut out)

Round 2, answering `Design review: revise be728d3e72eb8673d58e53bedf5562ba21bbbf0e architecture-unsound` (design-verdict/R11-OUTSIDE-ROOMS-P2 6e83652f28) point by point; each section names the points it answers. Base: origin/main 5825e1346c14eecace5c87c046558774145a94dc. Predecessor R11-OUTSIDE-ROOMS-P1 has no handoff head (it is built to this note), so the code was read at the base only; every line below is at the base. Paths are under `custom_components/heatpump_optimizer/` unless they start with `tests/`, `docs/`, `dev/` or `README.md`. Names without backticks do not exist yet.

## Finding (owner report, #3616)

No finder harness: owner report. The reporter has about 20 `climate` room thermostats (current temperature, target, heating or idle; each opens its own underfloor loop; no per-loop flow). Quoted from the issue: "Average indoor temperature: 19.6°C ... Planned space heating over the next 24 hours: 0 kWh" and "I would expect the heating plan to account for rooms that remain below their individual target temperatures." The 0 kWh was the slab seed (R11-OUTSIDE-SLAB-SEED-GUARD); what remains is the owner's three steps: a room list with average and spread (1), comfort from each room's own target (2), loop state as a delivery limit plus per-room history and an identifiability report (3). The tree has no room concept: one indoor read at `coordinator.py:6647`, targets from configuration only, and "zone" means the two floors.

## Owning seam

One new pure module, rooms (no `homeassistant` import, beside `comfort_band.py`), owns "what the room list says now": the reading record, the summary, the floor lift, and one per-coordinator side table (module state, by `fixer.md` step 17: the last readings and the lift the last solve was given; `boost.py:310` is the pattern). A second new pure module, room history, owns the ring and the identifiability report (phase 3a) and its store. Callers only: `inputs.py` (the entity read), `coordinator.py` (passes readings and gate signals in, adds one array), `config_flow.py`, `entry_config.py`, `sensor.py`, `payload.py`, `diagnostics.py`, `store.py` (a `DOMAINS` entry). `optimizer.py` and `thermal_model.py` are not edited in phases 1, 2 or 3a. One owner per concern holds; no stop.

## Shape

```
options (room list key) -> EntryConfig tuple -> InputReader room read (per entity, attributes)
   -> rooms side table: readings -> summary ---------------> payload -> 2 sensors          (P1)
                        -> gates -> lift (held, ramped, clipped per step to the band)
                           -> + _confidence_margins -> SolveLimits.min_temp_margins        (P2)
                        -> room history ring -> own store; report -> diagnostics, 1 sensor (P3a)
```

### Phase 1 (P1). Answers points 1, 2, 3

**Options.** One new key holding a list of entity ids (`climate`, or `sensor` with device class temperature), at most 32, on its own new options page with a multiple entity selector (`_entity_of`, `config_flow.py:1111`, is single-valued and the tree has no multiple selector today). `EntryConfig` gains its first list parser: absent, None and empty all parse to the empty tuple. The key is an entity assignment, so it joins `_WIRING` (`entry_config.py:297`) and survives a factory reset: `FACTORY_KEPT` (`entry_config.py:328`) keeps only names ending in `_entity`, which a list key does not.

**The read (point 1).** `InputReader.read` (`inputs.py:1094`) parses `float(state.state)`, which for a `climate` is its HVAC mode, so the room read is a new method beside it, not a call of it:

- Signature: room read `(entity_id: str) -> room reading`, a frozen record of `entity_id`, temperature in degC or None, target in degC or None, calling (bool or None), HVAC mode (str or None), `age_minutes`, `problem` (one of `PROBLEM_WORDS`, or None).
- Entity, availability and age stages reuse `_begin` (`inputs.py:1006`) with an explicit `entity_id` and an explicit age limit, `QUIET_STORE_MAX_AGE_MINUTES` (`const.py:297`, the indoor sensor's limit: a thermostat reports on change) times the reader's scale.
- `climate`: temperature is `temperature_c(attributes["current_temperature"], _instance_unit(hass))` and target is `temperature_c(attributes["temperature"], _instance_unit(hass))`, the conversion `setpoint_and_unit` applies at `inputs.py:485-505` (climate attributes are in the instance's unit system); calling is `attributes["hvac_action"] == "heating"`, None when the attribute is absent; HVAC mode is `state.state`. A missing or non-finite `current_temperature` is `not_numeric`.
- `sensor`: temperature is `temperature_c(state.state, state_unit(state))` (`inputs.py:423`, `inputs.py:387`); target, calling and mode are None.
- Range: `ROOM_AIR_RANGE_C` (`const.py:1876`) tested directly; outside it the reading is `implausible`. No new problem word.

**Health (point 2).** The room read does not call `InputHealth.record` (`inputs.py:153`, keyed by `reading.key`, last write wins) and registers no key in `INPUT_MAX_AGE_MINUTES` or `INPUT_PLAUSIBLE_RANGE_C` (the note's earlier claim that the range registers in the age table was wrong). Room readings live only in the rooms side table. Consequence, stated as an invariant: a dead, stale or implausible room never reaches `input_problems` or `stale_inputs`, so the Input problem sensor (`binary_sensor.py:100`) and the stale-input event (`notifier.py:145`) do not move for one unavailable thermostat among twenty, nor for all of them. What the user sees instead: the valid count, and a dropped-rooms attribute (entity id to problem word) on the room average sensor; under the quorum both sensors read unknown. A list that fails its quorum for longer than the age limit is the one case worth a repair notice; that is routed below, not designed in.

**The HVAC-mode rule (point 3): new behaviour, not inherited.** `inputs.py:455-505` states only the unit rule; nothing in the tree reads an HVAC mode of a foreign entity. New rule: a room's target counts only while its HVAC mode is `heat` or `auto`. A room in `off`, `cool`, `heat_cool`, `dry` or `fan_only` keeps its temperature in the summary and contributes no shortfall. It has its own failing test and mutation target (Evidence).

**Summary and entities.** Mean, spread (warmest less coldest), coldest entity, valid count; None under a quorum (fewer than half the list, minimum one). Two sensors (room average, room spread), created in `sensor.py` `async_setup_entry` (`sensor.py:190`) only when the list is non-empty: the first conditionally created sensors in a list that is a static literal today. The options listener reloads the entry, so the set is fixed for the entry's lifetime. Per-room values are attributes keyed by entity id; no per-room entity, no room name stored. The summary does not replace `state.room_temperature`.

### Phase 2 (this group). Answers points 4, 5, 6, 7

**Raw lift.** For each fresh room whose target counts, the shortfall is its target less its temperature; the house's is the live comfort target less `state.room_temperature`. Raw lift is the largest room shortfall less the house shortfall, clipped to [0, cap].

**Gates (point 4), each returning the base array object untouched.** Enumerated by `git grep -n -E "min_temp|floor_drop|WIDENING|RELAX" -- custom_components/heatpump_optimizer/coordinator.py custom_components/heatpump_optimizer/away.py custom_components/heatpump_optimizer/optimizer.py`; the floor-lowering sites it returns, and the rule for each:

| site | signal the coordinator reads | rule |
|---|---|---|
| Economy widening, `_floor_widening` (`coordinator.py:6260`), `ECONOMY_MIN_TEMP_WIDENING` | `self._mode == MODE_ECONOMY` | no lift: the user chose the wider floor |
| open-window relax, same function, `OPEN_WINDOW_RELAX_C` | `self._vent_cusum.tripped`, whether or not `open_window_relax_enabled` | no lift: the coldest room is the one with the window open |
| away setback, `solve_bands` (`away.py:372`) | `AwayState.active` (`away.py:82`) | no lift |
| away recovery (`floor_drop_c`, `away.py:365`, is None here) | `AwayState.active` with `recovery_active` (`away.py:87`); the one flag `active` covers both | no lift: the spread during recovery is the setback's, not a standing deficit |
| night floor, `get_temp_bounds` (`optimizer.py:2599`), and the holiday profile through the same two methods | none needed | lift kept, clipped per step (below): the night floor rises by at most the night band, so the setback depth is never inverted |
| mold floor, `min_temp_floors` | none | raises, never lowers; composes by maximum after the margin, unchanged |

Also gated: feature flag off, empty list, quorum failed, no room with a counting target, a manual space pin present, the two-zone model (both below).

**Clip to the band (point 6): the lifted floor never exceeds the comfort target.** The lift is a per-step array: lift at step k is the smaller of the held lift and `target_k - floor_k - confidence_k`, floored at zero, where `target_k` and `floor_k` are `get_comfort_temp` (`optimizer.py:2590`) and `get_temp_bounds` (`optimizer.py:2599`) of the solve's own configuration at the horizon's step times (the calls `_build_comfort_bounds` makes at `optimizer.py:4525`; `slot_drivers.py:42` is the precedent for calling them outside the solver) and `confidence_k` is the base array. So the sum of both margins never crosses the target because of the lift, the penalty and the pull never oppose, and `comfort_band` (`optimizer.py:5137`) never needs its 1.0 minimum because of the lift. Why not allow floor above target: measured below, the plan then holds the house above the user's target at a cost the user did not choose. Consequence, stated plainly: phase 2 can hold the house at its target while a room is short, and cannot plan the house above its target; that is phases 4 and 5 (a per-zone target), or the user raising the target. The gates make the un-banded configuration equal to the banded one whenever the lift is non-zero.

**Ramp (point 7).** The floor penalty has no grace for a state below it (`_COMFORT_FLOOR_L1`, `optimizer.py:1125`; the tree has no rising-floor helper), so the lift itself ramps from the house's present margin over the floor at a fixed rate, measured below.

**Hold and the what-if (point 7, carry r4).** No plan-level hysteresis exists in the tree and a solve runs every `DEFAULT_OPTIMIZATION_INTERVAL`. The held lift lives in the side table and moves only when the raw lift differs from it by at least a deadband (recommended 0.2 K) or a gate fires (to zero at once). The what-if (`coordinator.py:11348`) reads the held lift the baseline was solved with, never a recomputed one, so no lift drift lands in `coordinator.py:11252`'s delta.

**Two-zone (point 7).** `min_temp_margins` is one house-wide array applied to both floors (`optimizer.py:3268`), `state.room_temperature` is the upper floor (`optimizer.py:2421`), and the list does not say which floor a room is on. Phase 2 gives no lift on a two-zone install (`two_zone_enabled`) and says so in the lift attribute; mapping rooms to zones is phase 4's key, and a per-zone margin is that phase's solver change.

**What the lifted floor moves inside `optimizer.py` (point 5).** Every consumer reads `temp_min_bounds` with the margin; confidence margins (off by default) already move all five.

| consumer | verdict |
|---|---|
| `_safety_release_steps` (`optimizer.py:5001`) | must not move: no lift while `space_pins` is not None, so a lift never releases a manual forced-off pin |
| `_derive_hold_schedule` (`optimizer.py:4899`, smart-write only) | moves: the hold target is by definition the floor the plan holds, the candidate is adopted only on a better objective, and the clip bounds it at the comfort target |
| `power_cap_breach_c` (`optimizer.py:4678-4686`) | moves, by at most the lift and only where a cap, block or off step applies: the shortfall is against the floor the plan was asked to hold |
| `classify_space_steps` (`optimizer.py:2047`) | moves: more steps read as comfort floor, which is true of the lifted minimum; the driver row names the room (carry) |
| `comfort_band` (`optimizer.py:5137`) | moves: narrows toward its 1.0 minimum, never past it, so the pull stiffens by at most the ratio of band before to band after |

Stateless across restarts: no store, no migration. One attribute on the spread sensor names the room that set the lift, its size, and the gate that zeroed it.

### Phase 3a (P3): recording only

Room history keeps, per room, a ring sized in time (a fortnight at the entry's interval; `HISTORY_LENGTH`, `accuracy.py:51`, is a fortnight only at 30 minutes) of time, temperature, target and calling, in its own `QuarantiningStore` (`store.py:696`) at version 1 with a `DOMAINS` entry (`store.py:328`); a room removed from the list drops its ring. The identifiability report is a pure function of the rings: per room, separable or one reason code (no action reported, short history, never or always calling, no temperature response to calling, calling collinear with a named room). Published in diagnostics and as one sensor. This is the evidence phases 3b, 4 and 5 gate on.

### Phase 3b: re-cut out of this note (point 8)

Not designed here; it gets its own note once 3a's history exists from a live install. What that note must settle, so nothing above paints it into a corner: `power_caps_extra` is a total-draw cap (`optimizer.py:4750` subtracts the hot-water plan from it; `optimizer.py:331` takes its horizon minimum as hot-water run power), so a loop limit needs a channel that bounds space heat only, and the only one, the horizon's `power_caps`, is set inside the optimizer; that is an `optimizer.py` seam and a group of its own. It must name the envelope's owning module and store (not coordinator code, at zero headroom), and compose at both sites: `_solve_record` before `compose_with_silent` (`coordinator.py:6298`) and `_whatif_solve` (`coordinator.py:11306`), which composes no capacity cap today. Phases 1 to 3a add nothing it must undo: it reads the same reading record and rings.

**Invariants.** (i) No room list: plan, entity set, stored options, Input problem sensor and notifier events byte-identical, in every phase. (ii) The lift raises the planned floor and everything derived from it (table above), never above the comfort target, and never changes the target, the ceiling, the measured state or a manual pin's fate. (iii) A missing, stale or implausible room is dropped, never guessed, and never raises an input problem. (iv) No `entry.options` read below the glue; the coordinator composes, rooms computes.

**Migration.** None. `CONFIG_ENTRY_VERSION` stays; every new key reads with a default; the new store starts at version 1. Phases 4 and 5 stay reachable: zone groups add a key mapping entity id to group, thermostat writes go through `pump_arbiter.py`, both read the same record and rings.

## Solve cost and plan effect (production solver, measured at the base). Answers point 7

No decision variable, constraint or objective term is added. Instrument: `HeatPumpOptimizer.optimize` through `tests/profiles.py` `solve_inputs`, 24 h at 15 min, hot water on, floor 19.5, target 20.0 day and night, ceiling 23.0, room start 19.6 (the reporter's figure; slab one kelvin above), single-threaded BLAS, seat's Linux container (ratios carry to a Raspberry Pi, milliseconds do not). Null control in every set: a zero array reproduces None's plan byte for byte (sha1 of the power schedule), every non-zero lift changes it. Run-to-run wall time varies up to twofold on one row, so only energy and temperature are signal.

Mild day, where the unlifted plan is off the power bound (`weather("shoulder")`, `prices("winter_typical")`, start 12:00 so the day floor and target hold from step 0, three runs). "Bound" counts the first twelve steps with space power at nameplate less the hot-water step; min and mean are the planned sensor temperature over hours 3 to 24.

| lift | model | median ms | kWh total / space | space kWh, first 3 h | steps at bound | min / mean degC |
|---|---|---|---|---|---|---|
| None (zeros identical) | single | 695 | 10.5 / 6.2 | 0.00 | 0 | 19.58 / 19.90 |
| 0.5 K held | single | 1065 | 13.4 / 9.1 | 3.00 | 2 | 20.00 / 20.26 |
| 0.5 K, ramped from zero over 2 h | single | 1572 | 12.5 / 8.2 | 0.68 | 0 | 19.74 / 20.08 |
| 0.5 K held, start 19.9 | single | 1294 | 11.2 / 7.0 | 0.00 | 0 | 19.80 / 20.15 |
| 1.0 K held (floor above target; outside the design) | single | 1022 | 16.4 / 12.2 | 7.31 | 4 | 20.50 / 20.85 |
| None (zeros identical) | two-zone | 2751 | 16.3 / 12.0 | 0.07 | 0 | 19.08 / 19.80 |
| 0.5 K held | two-zone | 3192 | 19.1 / 14.8 | 2.36 | 1 | 19.70 / 20.21 |
| 0.5 K, ramped from zero over 2 h | two-zone | 3415 | 18.8 / 14.5 | 1.95 | 0 | 19.78 / 20.19 |
| 1.0 K held (outside the design) | two-zone | 2776 | 21.8 / 17.5 | 5.05 | 3 | 20.00 / 20.55 |

What it establishes. (a) A held lift that starts above the house does drive the first steps to the bound where the unlifted plan has none; a start 0.1 K under the lifted floor does not. So the lift is ramped: at step k it is at most the house's present margin over the floor plus a rate times the step's lead time (recommended 0.25 K per hour, the measured ramp), then held. Anchoring on the present temperature, not on zero, is what lets a receding horizon converge: each solve starts the ramp where the house is. The clip to the band applies after the ramp. (b) Floor above target (the 1.0 K rows) plans a house 0.5 to 0.85 K above the user's target for 56 % more electricity on this day, which is the case the clip removes. (c) The designed maximum on this fixture, 0.5 K, costs 19 % (ramped) to 28 % (held) more electricity on a mild day; on `weather("winter_cold")` from a 00:00 start it costs 8.5 % single-zone (77.5 to 84.1 kWh) and 4.8 % two-zone (101.7 to 106.6), and there every row including None runs all twelve first steps at the bound, so that day cannot show (a). On the cold day the 1.0 K single-zone plan averages 20.38 over hours 6 to 24, under its own 20.5 day floor: capacity-bound, holding neither floor nor target. (d) Solve time moves inside the run-to-run spread; `tests/stress_budgets.json` is not raised and the fixer re-measures with `tests/stress.py`. The two-zone rows are cost evidence only: phase 2 gives a two-zone install no lift.

## Alternatives

- **Feed the coldest room as `state.room_temperature`.** Lost: that state also drives the RC dynamics, the heat-loss learner and the accuracy record; two concerns in one field.
- **A per-step target array or per-room states in `optimizer.py`.** Lost: a new `SolveInputs` field and a third comfort term, and room parameters not identifiable from one heat input. It is what planning above the house target needs, so it is phase 4's, behind 3a's report.
- **Record room reads in `InputHealth` under per-room keys.** Lost: `details()` (`inputs.py:177`) lists every not-ok reading under any key and the problem sensor is on for any of them; there is no advisory class, so one dead thermostat is a standing problem, and each key would owe both age tables and `tests/features.py`'s `_r10st_same` census.
- **Clamp to the target inside `_build_comfort_bounds`.** Lost: it would also clamp confidence margins and the mold floor for installs with no room list, breaking invariant (i).
- **Use `min_temp_floors`, or `replace(config, min_temp=...)` as away does.** Lost as before: the first is ranked and reported as the mold floor; the second hides the lift from the why-now drivers, which read `comfort_floors`.

## Sibling sites

`git grep -n "min_temp_margins=" -- custom_components/heatpump_optimizer/coordinator.py` returns the two builds (`coordinator.py:6325`, `coordinator.py:11348`); both take the lift, the second the held one. Inside the optimizer: the five consumers tabled above. Out of scope, with reason: the coordinator's own floor checks judge model zones against the configured floor as safety and read no margin; they do not move.

## Evidence, by file

- `tests/features.py` (modules driven directly, production symbols imported). P1: the room read for a `climate` in Celsius and in a Fahrenheit instance, for a `sensor`, for a `climate` with no `current_temperature`; summary, quorum, stale and implausible rooms dropped; with twenty rooms and one unavailable, `input_problems` and `stale_inputs` equal the no-list run's (null control: the same entity under `CONF_INDOOR_TEMP_ENTITY` does raise both). P2 failing test (symbol absent, then the assertion): rooms A 18.0 target 21.0 `heat`, B 20.4 target 20.0, C 20.4 target 16.0, D 17.0 target 22.0 `off`; model temperature 19.6, target 20.0, floor 19.5; expected lift 0.5 at every day step (the band), and D contributes nothing. Null controls, each returning the base array object: A at 21.0; D switched to `cool`; empty list; flag off; Economy; `_vent_cusum` tripped with the relax option off and on; away active; away recovering; a space pin; two-zone. Clip: with a 0.3 K confidence margin the lift is 0.2; at a night step it is the night band. Ramp: with the house 0.4 K under the lifted floor, step 0's lift is the house's margin over the floor, not the held lift; with the house at or above the lifted floor the array is flat. Hold: raw moving by less than the deadband leaves the array equal; the what-if's margins equal the baseline's after the readings change.
- `tests/validate.py` or `tests/edge.py`: one production solve with and without the fixture's lift, on the mild-day set above; lowest planned temperature and space energy both higher, and the planned temperature never above target plus the pull's own overshoot in the unlifted plan. With a forced-off pin present, the released-pin set equals the no-list run's. With a binding cap, `power_cap_breach_c` rises by no more than the lift.
- `tests/config_flow_steps.py`: the new page saves a list; an emptied submit clears it (`_clear_absent`, `config_flow.py:2537`, is written for scalar rows); an install that never opens it stores no key; a factory reset keeps it.
- `tests/golden.py`: `tests/golden/config_flow.json` is re-recorded, because `capture_config_flow` (`tests/golden.py:1210`) fingerprints the menu and every page; it is not value-bearing, so neither claim file is touched. Every other fixture is the null control for invariant (i) and must not move.
- `tests/entities.py`: `README.md`'s "menu of N pages" figure and the new page's label (`tests/entities.py:668-681`, pinned to `_OPTION_PAGES`); the two sensors need a `collect()` call (`tests/entities.py:264`) with a `data` or `coordinator` whose list is non-empty, or they are never exercised, plus one with the default `DATA` showing the count unchanged; `docs/configuration.md`, `strings.json` and the three translations in parity. `tests/finite_boundary.py`: the P3a store's `DOMAINS` entry.
- P3a: a synthetic two-room history from `simulate_step` with independent calling reads separable; B's calling copied from A reads collinear; the calling column shuffled in time reads no response; too few rows reads short history.
- Mutation targets: the clip at zero, at the cap and at the band; the ramp's anchor and its rate; the house-shortfall subtraction; the confidence subtraction in the clip; the quorum predicate; the HVAC-mode predicate; each gate's predicate (seven); the deadband comparison; the what-if's read of the held lift; each verdict threshold in the report.

## Hot files, position, carries

Serial: R11-OUTSIDE-SLAB-SEED-GUARD, then P1, P2, P3a; 3b after its own note. Hot: `coordinator.py` (the two `SolveLimits` builds, `_update_current_state`, `_build_data_dict`), `const.py`, `config_flow.py`, `entry_config.py`, `inputs.py`, `sensor.py`, `payload.py`, `strings.json`, the translations, `README.md`. Shared files, not a shared seam, with design/R11-OUTSIDE-HONEST-METERED-FLOOR (`store.DOMAINS`, `coordinator.py`), R11-OWNER-GENERIC-CONTROL-TEXT (`config_flow.py`, `strings.json`, translations) and design/R11-OUTSIDE-SELF-SETTING-PUMP (`_fold_capacity_envelope`, which this note no longer touches). No pinned grader is added, so no p1/p2 split. Carries owed: the notes below; received: the verdict's r1 to r6, kept below.

## Decisions routed

- decision: owner. The lift yields to Economy and to a detected open window (designed so; the verdict's recommendation).
- decision: owner. The lift never releases a manual pin (designed so) and does move the smart-write hold target, bounded at the comfort target (designed so; the alternative is one more gate on smart-write).
- decision: owner. The lift stops at the house's comfort target (designed so). Allowing more needs a per-zone target, phase 4.
- decision: owner. The cap, now a second bound under the band: recommended 1.0 K. And phase 2 as its own opt-in flag, default off: recommended yes.
- decision: owner. Two-zone installs get phases 1 and 3a and no lift until phase 4 (designed so).
- decision: owner. Whether a room list under quorum for longer than the age limit raises a repair notice; not designed, recommended as a later item.
- decision: orchestrator. Size and split: P1 is L (about ten production files, three translations, `README.md`, `docs/configuration.md`, one re-recorded fixture); P2 without `optimizer.py` is M; P3 is 3a only; 3b is a new group behind its own design.

## Notes for the fixer

- Re-anchor every coordinator cite at the branch's merge base; the builds are `coordinator.py:6320-6340` and `coordinator.py:11342-11360` at this base. Carry: R11-OUTSIDE-ROOMS-P1 (item r1)
- The emptied multi-entity submit and the factory reset are both decided above (cleared; kept through `_WIRING`); test both. Carry: R11-OUTSIDE-ROOMS-P1 (item r2)
- No input key is registered, so `_r10st_same` and `_r9f41_temp_keys` in `tests/features.py` owe nothing; the side table is picked up by `_src_snapshot` (`tests/features.py:15552`) automatically and must hold plain data only and read the same whether the store load lands before or after the setup refresh. Carry: R11-OUTSIDE-ROOMS-P1 (item r3)
- The what-if takes the held lift, by design above; pin it. Carry: R11-OUTSIDE-ROOMS-P2 (item r4)
- Rooms has module state (the side table); say so in the body, never "stateless module". Carry: R11-OUTSIDE-ROOMS-P1 (item r5)
- Size the ring in time, not rows. Carry: R11-OUTSIDE-ROOMS-P3 (item r6)
- `_begin` may record into health on its early exits; the room read must leave `reader.health.readings` untouched on every path, and the twenty-room test is the control. Carry: R11-OUTSIDE-ROOMS-P1 (item s1)
- Do not re-implement the day and night rule for the clip: call the configuration's two methods at the horizon's step times. Carry: R11-OUTSIDE-ROOMS-P2 (item s2)
- Every key of `tests/structure_budgets.json` sits at zero headroom (`python3 tests/structure.py`): no new coordinator attribute, one call each in `_solve_record` and `_build_data_dict`, gate signals passed as arguments to a rooms function, and every symbol phase 1 adds needs a reader in phase 1. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e01)
- A new coordinator method needs a `tests/seam_map.json` entry; prefer module functions in rooms. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e02)
- A new module must sit in a measured closure: the single-script form of `tests/derive_closures.sh`, on Linux only. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e03)
- The why-now drivers read `comfort_floors`, so the lift shows in the comfort-floor row unnamed; name the room lift there and in the narrative. Carry: R11-OUTSIDE-ROOMS-P2 (item 5a1c0e06)
- Worst-case store size is 32 rooms by a fortnight of rows by four values; store centi-degrees as integers, measure file and resident memory under `tests/stress.py`, save on the accuracy store's cadence. Carry: R11-OUTSIDE-ROOMS-P3 (item 5a1c0e07)
- Entity ids are exported unredacted in diagnostics, as the indoor sensor is; store no free-text room name, or add its key to `TO_REDACT`. Carry: R11-OUTSIDE-ROOMS-P3 (item 5a1c0e08)

Seat tokens: three scouts (two read-only, one measuring), 96807, 111840 and 89697 (harness figures); the harness reports none for the main loop.
