# D7-s3, round 11: this year's train (M5), dead code (M6), duplicated shapes (M8)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, the export `plant-export/audit-r11-baseline`. Box: Apple M1 (8 cores), Darwin 27.2.0 arm64, Python 3.14.7 (venv-ci), shared, load1 150-300 throughout; every number below is a count.

## Method

- **M5.** The universe is the 29 modules `git diff --diff-filter=A 1936d5ca..92d38ecb -- 'custom_components/*.py'` lists on the round's checkout. `fn_trace.sh` ran 20 suite scripts once each under a `sys.monitoring` function-entry sentinel; `m5_train.py` then raised `RuntimeError` on entry to one function at a time (in memory, no file edited) and re-ran the scripts that enter it, cheapest first, stopping at the first new failing check. `pins` adds each module's docstring, docs paragraphs and importers.
- **M6.** Three static censuses over all 95 package modules: `m6_dead.py` (name reachability from the Home Assistant contract, with the M5 trace as the runtime sentinel), `m6_inner.py` (parameters, locals, attribute stores, dataclass fields), `m6_stmt.py` (statements dead by the AST, and `else` arms no member of the tested enumeration reaches). Each has a planted positive control and a reader perturbation; `m6_two_zone_auto.py` drives the one dead arm found.
- **M8.** `m8_enum.py` enumerates families of one rule written twice six ways (token-stream clones, one name in two modules, near-equal literals, seam expressions, scalar/batch twins, inverse pairs); `m8_families.tsv` holds each family's disposition; `m8_agree.py` drives 22 agreement families' implementations with shared probes and applies each disagreeing family's one-line fix in memory.

## Coverage

| step | universe | examined | not reached |
|---|---|---|---|
| D7.M5 | 29 | 29 | 0 |
| D7.M6 | 25888 | 25888 | 0 |
| D7.M8 | 114 | 114 | 0 |

Redispatched: **C1** examined (the step has a denominator: 29 modules, 480 functions). **C2** examined for the seven groups in this seat's cells (131 functions); the test-instrument and card groups are leads. Function-level remainder: see *Unfinished*.

## Findings

### D7-s3-01 (D7.M8, high, bug) temperature_from_c is not the inverse of normalize_temperature_c: every Fahrenheit set-point write is wrong

inputs.temperature_from_c(c, unit) multiplies by the unit's to-Celsius factor instead of dividing by it, so for the three Fahrenheit spellings a value written and read back through normalize_temperature_c is not the value written: 21.5 degC is written as 43.94 degF (6.6 degC) instead of 70.7 degF.

- Evidence: `dev/audit/rounds/round11/D7/s3/m8_agree.py --only temperature_roundtrip` -> **12** probes of 35 on which write-then-read differs (4 temperatures x 3 Fahrenheit spellings; 0 degC and the 4 Celsius/Kelvin spellings agree)
- Symbol: `custom_components.heatpump_optimizer.inputs:temperature_from_c`
- Perturbation: attribute swap of inputs.temperature_from_c for `value_c / factor - offset` (m8_agree.py --only temperature_roundtrip --perturb) -> to_zero (observed 0)
- Control: the other forward/backward pair of the package (DhwStore.store_temp_for_tap / tap_temp_for_store) round-trips on 24 of 24 probes; the Celsius and Kelvin rows of the same table round-trip on 20 of 20
- Mechanism: const.TEMPERATURE_UNIT_TO_C holds (offset, factor) with degC = (value + offset) * factor. The forward rule (inputs.py:normalize_temperature_c) applies it; the backward rule (inputs.py:temperature_from_c) returns value_c * factor - offset where the inverse is value_c / factor - offset. Factor is 1.0 for degC and K, so only the 5/9 rows disagree. Callers: SetpointGrid.quantise (inputs.py:643-647), write_setpoint_c (inputs.py:770) and setpoint_check's Fix value (setpoint_check.py:183): every set-point the integration writes to an entity whose unit is degF.
- Fix scope: inputs.py:temperature_from_c divides by the factor; a round-trip check over every row of TEMPERATURE_UNIT_TO_C in the suite. One owner: inputs.py (the table's only reader pair).

### D7-s3-02 (D7.M6, high, bug) project_window_mean never reads `remaining`: the peak guard weights the live draw by elapsed time

power_guard.project_window_mean stores `remaining = window_minutes - elapsed` and returns (mean * elapsed + current_kw * elapsed) / window_minutes, so a constant 4 kW draw projects 0.0 kW at the window's start, 0.67 kW at minute 5 and 8.0 kW at minute 60 instead of 4.0 kW throughout.

- Evidence: `dev/audit/rounds/round11/D7/s3/m8_agree.py --only window_mean` -> **7** probes of 8 on which a constant 4 kW draw does not project 4 kW (minutes 0, 5, 15, 45, 55, 60 and the no-samples case; minute 30 agrees because elapsed and remaining are equal there)
- Symbol: `custom_components.heatpump_optimizer.power_guard:project_window_mean`
- Perturbation: attribute swap of power_guard.project_window_mean for the same body with `current_kw * (window_minutes - elapsed)` (m8_agree.py --only window_mean --perturb); the static twin: m6_inner.py's unread_local row power_guard.py:64 leaves the census -> to_zero (observed 0)
- Control: the probe at minute 30 (elapsed and remaining are both 30) agrees in the same run: the one point of the window where the dropped term cannot show; the other seven unread locals of the census (coordinator.py:3121 i, coordinator.py:6619 done, optimizer.py:1212 solar, sysid.py:1977 rank1, sysid.py:2109 residuals, sysid.py:2322 outdoors and powers) are unpacking targets with no dropped term
- Mechanism: The dead local is the term the formula needs: the remainder of the window is assumed to continue at current_kw, i.e. current_kw * remaining. With `elapsed` in its place the projection under-reads for the first half of every metering window (the guard cannot suppress electric DHW before the peak is booked) and over-reads in the second half (it suppresses on a draw that is under the threshold). The docstring's own two limits fail: 'at the window's start this is the current draw' reads 0, 'at its end it converges on the realised average' reads mean + current. Caller: coordinator.py:8794, whose result is GuardState.update's projection_kw against the capacity-tariff threshold.
- Fix scope: power_guard.py:project_window_mean reads `remaining`; the structure ratchet could carry an unread-local count (tests/structure.py has none).

### D7-s3-03 (D7.M8, low, hygiene) `The plan step covering now` is written four times; two copies have no end rule and hold the last step forever

coordinator._covering_index and pump_arbiter._step_index answer `no step` once now is past the plan's last step, while pump_arbiter._planned_room and early_cutoff._planned_room keep returning the last step's value at any later instant (4 of 8 shared probes disagree, from the last step's end edge to a day past it).

- Evidence: `dev/audit/rounds/round11/D7/s3/m8_agree.py --only step_covering_now` -> **4** probes of 8 on which the four implementations do not agree whether a step covers now
- Symbol: `custom_components.heatpump_optimizer.early_cutoff:_planned_room`
- Perturbation: attribute swap of pump_arbiter._planned_room and early_cutoff._planned_room for bodies that take their index from pump_arbiter._step_index (m8_agree.py --only step_covering_now --perturb) -> to_zero (observed 0)
- Control: the four probes inside the plan (before, first, mid, last) agree in the same run
- Mechanism: All four start from bisect_right(timestamps, now) - 1. _covering_index (coordinator.py:591) and _step_index (pump_arbiter.py:543) add the half-open end of the last step (R10 N-no-expiry, #2229); the two _planned_room copies bound the index only by the series' length. Their callers are gated on plan_stale (age over three solve cycles) at pump_arbiter.py:1421 and early_cutoff.py:224, and ungated at pump_arbiter.py:632, 654, 1454 and 1646; a plan's horizon outlasts the stale limit on every shipped configuration, so no wrong write was produced here -- the copies disagree, and the class's barrier does not cover them.
- Fix scope: pump_arbiter._planned_room and early_cutoff._planned_room index through pump_arbiter._step_index (or coordinator._covering_index moved to a leaf both import); pump_arbiter.py:1942's bare bisect with them. One owner: the step-index function.

### D7-s3-04 (D7.M8, low, hygiene) Three small rules have copies that disagree: water's heat capacity, a naive instant's zone, a finite number

Driven with the same probes, the package's copies of three small rules disagree on 12 of 21 probes: the heat that warms a litre of water by 1 K has three values (0.0011600, 0.0011605 and 0.0011631 kWh, spread 0.26 %); a naive datetime is read as UTC by drift._as_utc and manual_plan._instant and as the host's local zone by open_meteo._ensure_utc (9 h apart under TZ=Asia/Tokyo); and `is this a finite number` is answered four ways (finite_float refuses NaN and inf, entity.payload_number and sensor._as_float pass them, replay_doc.numeric passes True, 'nan' and 'inf').

- Evidence: `dev/audit/rounds/round11/D7/s3/m8_agree.py --quiet` -> **12** probes of 21 on which the copies disagree, over the families water_heat (1 of 1), naive_instant (2 of 3) and finite_number (9 of 17)
- Symbol: `custom_components.heatpump_optimizer.sensor:_gap_probe_terms`
- Perturbation: m8_agree.py --perturb: const.WATER_CP_KJ_PER_KG_K set from WATER_SPECIFIC_HEAT and sensor._gap_probe_terms re-executed with the literal replaced by it; open_meteo._ensure_utc swapped for drift._as_utc; entity.payload_number, sensor.payload_number and replay_doc.numeric swapped for finite_float -> to_zero (observed 0)
- Control: six families of the same run agree on every probe (dhw_store_tap 24, stored_number 13, soc 5, buffer_prior_in_bounds 8, effective 4, ua_from_rate 3), and naive_instant's aware-datetime probe agrees across all four implementations
- Mechanism: Each rule has no single owner. Water: const.WATER_SPECIFIC_HEAT = 0.00116 kWh/(L K) (thermal_model's tank masses, external_heat), const.WATER_CP_KJ_PER_KG_K = 4.186 with WATER_KG_PER_L = 0.998 (flow_meter.thermal_output_kw), and the literal 4.187 / 3600 in sensor._gap_probe_terms. Naive instants: drift._as_utc (`replace(tzinfo=utc)`), open_meteo._ensure_utc (`astimezone(utc)`, the host zone), manual_plan._instant (UTC), and Home Assistant's dt_util.as_utc at coordinator._utc_age_seconds; debugger._aware keeps a naive stored stamp as UTC text where price_tiles._aware drops it. Numbers: four predicates with four domains. No wrong published value was produced from any of the three here -- the sensor base scrubs a non-finite native value, the 0.26 % sits inside the learners' noise -- so this is the structure, not a defect in an output.
- Fix scope: sensor._gap_probe_terms and flow_meter read one water constant from const.py; open_meteo._ensure_utc and drift._as_utc become one function in drift.py with the zone an argument; payload_number is named for what it admits (or refuses NaN). The seven `unknown`/`unavailable` literals (m8_agree.py --seams) join one tuple in inputs.py in the same change.

### D7-s3-05 (D7.M6, low, hygiene) Dead state inside live code: 50 constants, parameters, locals, attributes and fields nothing in production reads

No definition of the package is unreachable by name (dead = 0 of 6969), but 50 pieces of state are stored by production and read by no production code: 6 config-key constants named only by tests, 4 unused imports, 16 parameters their function never loads, 7 locals stored and never loaded (beside the one in D7-s3-02), 8 instance attributes and 8 dataclass fields only tests read, and 1 dataclass field nothing reads.

- Evidence: `dev/audit/rounds/round11/D7/s3/m6_inner.py && python3 dev/audit/rounds/round11/D7/s3/m6_dead.py --trace <trace dir>` -> **50** definitions (m6_dead.py: test_only constants 6, unused imports 4; m6_inner.py: unread_params 16, unread_locals 8 less the one of D7-s3-02, test_read_only attributes 8 and fields 8, unread_fields 1)
- Symbol: `custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._power_to_setpoints`
- Perturbation: m6_inner.py --perturb and m6_dead.py --perturb: a reader of every reported name appended to an in-memory copy of its module takes write_only and dead to 0; one planted unreferenced definition raises each census by exactly 1 (planted_delta=1) -> to_zero (observed 0)
- Control: the statement census over the same 2678 function bodies finds 0 dead stores, 0 no-effect statements, 0 constant conditions, 0 duplicate dict keys, 0 repeated tests and 0 identical arms; its two self_operand rows are the `x != x` NaN test, and its one exhausted_else row is D7-s3-09
- Mechanism: Each is what a refactor left behind: const.py keeps CONF_BUFFER_TANK_LOSS, CONF_SOLAR_UPPER_FRACTION, CONF_HOUSE_HEAT_LOSS_SCALE and CONF_LOWER_FLOOR_LOSS_RATIO though production reads those keys by their string or through ThermalParameters; PVConfig.export_price_entity is set at coordinator.py:9796 while the coordinator reads the entity straight from the entry config (9802); optimizer._power_to_setpoints takes outdoor_temps and zips room_temps it never uses; tariff.window_factors takes dt_hours, optimizer._solve_space n_steps, sysid.slab_mode_identifiability config, dhw_planner._baseline_dhw_economics initial_state, coordinator._observe_frequency and CurveLearner.record_miss a `now` -- callers compute and pass each. The attributes (_last_manual_setpoint, _slab_fit_used, _step_dhw_draw_kw, _step_dhw_floor_injected, _step_dhw_refused, draws_dirty, last_return_c, manual_pins_active) are production writes whose only readers are tests: test hooks living as coordinator, model and optimizer state.
- Fix scope: Delete the four constants and four imports; drop the eight dead parameters at their call sites; move the test-only attributes behind the tests' own seams or delete them with the checks that read them. No behaviour changes; structure.py could ratchet the two counts.

### D7-s3-06 (D7.M5, medium, hygiene) This year's 29 modules: 93 of 480 functions can be deleted with no behaviour script failing

Of the 480 non-trivial functions in the 29 modules added since the previous baseline, 89 are entered by no script of the behaviour suite and 4 more are entered but raise on every call with every script that enters them still green; 285 are pinned (a script reports a failing check it did not report unmutated) and 102 could not be driven through their long scripts in the window.

- Evidence: `dev/audit/rounds/round11/D7/s3/m5_train.py report --trace <trace dir> --out dev/audit/rounds/round11/D7/s3/m5_mutants.json` -> **93** functions of 480 (unentered 89, swallowed 4; pinned 285, not_reached 102)
- Symbol: `custom_components.heatpump_optimizer.early_cutoff:diagnostics_view`
- Perturbation: a check that calls the function: m5_pin_demo.py reports 0 failing unmutated and 1 failing under HPO_FN_MUTATE=early_cutoff.py:329, where every suite script entering it stays green -- one such check per function takes `swallowed` down by one; the deletion mutant itself is the perturbation for the pinned rows (new failing checks 0 -> >=1) -> down (observed 1)
- Control: the hook armed on a line no function starts at kills nothing in the three scripts driven; a pinned mutant's kill is a new failing check against the same script's unmutated log
- Mechanism: Every module has a module docstring, a docs paragraph and at least one importer, and 27 of the 28 that hold functions have a script that pins some of them (whatif.py's six are entered only by scripts this seat could not drive; payload.py holds types only); what is missing is per function. The unentered ones cluster (heat_curve 18, duty_switch 15, draw_range 14, duty_legs 9, heat_energy 9, runs 6): code paths a module ships that nothing in tests/ calls. The swallowed ones sit behind the coordinator's best-effort wrappers and diagnostics' never-breaks view, which turn a raise into a logged line no check reads. In this tree tests/entities.py also stops at line 9634 of 42669 on KeyError 'house_heat_loss_coefficient', so every check after it pins nothing (lead). Not counted: the golden differential (tests/golden.py, tests/env_drift.py) cannot run in an export without .git, so a function whose deletion only moves a golden reads unpinned here -- each row is a candidate for D3's gate, not a verdict on it.
- Fix scope: Tests, by module: a check per unentered function (or its deletion where m6 agrees nothing reaches it), and a value check behind each swallowing wrapper. D3 owns the gate-level verdict; the structure is this dimension's.

### D7-s3-07 (D7.M8, high, bug) tariff._exact_topk_sum sums the k smallest excesses: the scalar capacity charge and its batch twin disagree

tariff._exact_topk_sum returns sum(sort(excess)[:k]), the k smallest values, where its docstring and its batch twin (`np.sort(x, axis=1)[:, -k:]`) take the k largest; for every k above 1 with more than k windows the scalar _plateau_aware_topk_sum differs from _plateau_aware_topk_sum_batch (4 of 12 probes), peak_cost_smooth from peak_cost_batch (1 of 4), and the solve's scalar objective from objective_batch under a per-window capacity tariff (2 of 8, relative difference 1.4).

- Evidence: `dev/audit/rounds/round11/D7/s3/m8_agree.py --only twin_topk` -> **4** probes of 24 on which a row of the batch is not the scalar's value to the bit (plateau_aware at k = 2 and 3 on the random and one-spike matrices; the 12 smooth probes and every k = 1 probe agree); twin_peak_cost 1 of 4, twin_objective 2 of 8
- Symbol: `custom_components.heatpump_optimizer.tariff:_exact_topk_sum`
- Perturbation: attribute swap of tariff._exact_topk_sum for `float(np.sum(np.sort(excess)[-k:]))` (m8_agree.py --only twin_topk --perturb; the same swap under --only twin_peak_cost and --only twin_objective) -> to_zero (observed 0)
- Control: the other twins agree to the bit in the same harness: simulate_trajectory 9 of 9, wood_share 24 of 24, _day_peaks 4 of 4, switch_weight 3 of 3, _smooth_topk_sum 12 of 12, and the objective pair on all five no-tariff cases and on the distinct-days tariff case
- Mechanism: The rule `the billed top-k` is written twice: once as tariff._exact_topk_sum (tariff.py:916), which the exact published charge peak_cost (tariff.py:1038) and the solver's scalar term _plateau_aware_topk_sum (tariff.py:958) call, and once inline in _plateau_aware_topk_sum_batch (tariff.py:943), which the batched objective calls for the finite-difference gradient. The scalar copy slices the wrong end of the sort. With [1, 5, 3, 4, 2, 0.5] and k = 2 the scalar returns 1.5 and the twin 9.0. It bites whenever more than k excesses are compared with k above 1: `Peaks on different days` off (peak_tariff_distinct_days False, the per-window rule the option's own text names), or a horizon spanning more plan days than peak_count. There the published projected_peak_cost bills the smallest excesses (often 0), and the solver's line search reads a capacity term its gradient was not taken from. On the default (distinct days, 3 peaks, a horizon of at most 3 days) k equals the number of day peaks and the two ends of the sort are the same sum, which is why the objective pair agrees there.
- Fix scope: tariff.py: _exact_topk_sum takes the sorted tail, and _plateau_aware_topk_sum_batch's exact arm calls the same rule (one owner: tariff.py). The row-parity grid the batch docstring cites gains a k > 1, more-than-k-windows row for the exact arm.

### D7-s3-08 (D7.M8, high, bug) emitter_delivery lost its never-negative clamp: behind a valve the scalar model and its batch twin diverge

mixing_valve.emitter_delivery returns ua * (mix_temp - zone_temp) with no floor at zero, against its own docstring (`Never negative: a valve can shut, but it cannot cool a house`) and against the inline np.maximum(0.0, ...) of simulate_trajectory_batch; under every throttling valve mode simulate_trajectory and simulate_trajectory_batch then diverge once the tank falls to the zone it feeds (18 of 42 probes, buffer temperature up to 2.4 K apart within 24 h), where they are bitwise equal on all 24 probes without a valve.

- Evidence: `dev/audit/rounds/round11/D7/s3/m8_agree.py --only twin_trajectory` -> **18** probes of 42 (a model variant x a weather, 4 schedules and 6 or 7 series each) on which a row of simulate_trajectory_batch is not simulate_trajectory to the bit: all 18 are the six valve variants (manual, smart_read, smart_write x one- and two-zone config) x 3 weathers; the 8 no-valve variants agree on 24 of 24
- Symbol: `custom_components.heatpump_optimizer.mixing_valve:emitter_delivery`
- Perturbation: attribute swap of mixing_valve.emitter_delivery for `max(0.0, ua * (mix_temp - zone_temp))` (m8_agree.py --only twin_trajectory --perturb) -> to_zero (observed 0)
- Control: the eight variants with no throttling valve (single- and two-zone config, big buffer, flow-Carnot COP, flow-curve COP, wood tank, wood coil) agree to the bit on 24 of 24 probes in the same run; within the valve variants the full-power schedule agrees and only the schedules that let the tank fall to the slab diverge
- Mechanism: The rule `what an emitter circuit takes from the mixed flow` is written twice: mixing_valve.emitter_delivery (mixing_valve.py:133), which the scalar two-zone step calls through thermal_model._valve_two_zone_delivery (thermal_model.py:2526, 2536), and inline in the batched trajectory (thermal_model.py:4673-4678). The scalar copy has no clamp, so with the pump off and the tank drained to the slab's temperature the scalar step moves heat from the slab back into the tank (slab 23.01 against the twin's 23.06 after one hour, tank 22.11 against 21.34): a mixing valve run in reverse. simulate_step is the model the coordinator predicts with and the solver's scalar objective integrates; the batch is what its finite-difference gradient is taken on, and the batch docstring states `bitwise parity is the contract`. On a valve install the objective and its gradient are therefore two different plants over every coast.
- Fix scope: mixing_valve.py:emitter_delivery floors at zero; the batch twin's two inline expressions call or mirror it under a parity row with the tank below the slab (the regime tests/features.py's equivalence grid does not hold today, or the suite would be red on it).

### D7-s3-09 (D7.M6, high, bug) The presence rule for two zones is dead code: `auto`, the default mode, is resolved as `on`

ThermalParameters.from_config tests the two-zone mode with `in (TWO_ZONE_MODE_ON, DEFAULT_TWO_ZONE_MODE)`, and DEFAULT_TWO_ZONE_MODE is `auto`, so every entry with no mode key or with `auto` is modelled two-zone whatever keys it holds; the `else` arm that infers the mode from the zone keys is reached only by an unknown mode string. On 4 of 6 configs the default mode and an unknown mode -- which the function's own comment declares the same rule -- give different answers.

- Evidence: `dev/audit/rounds/round11/D7/s3/m6_two_zone_auto.py` -> **4** configs of 6 on which `no mode key` or `auto` answers two_zone_enabled differently from an unknown mode on the same config (no zone keys, and a stored single-zone house: True against False; with zone keys both say True)
- Symbol: `custom_components.heatpump_optimizer.thermal_model:ThermalParameters.from_config`
- Perturbation: the classmethod re-executed in memory with `(const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE)` replaced by `(const.TWO_ZONE_MODE_ON,)` (m6_two_zone_auto.py --perturb); the static twin: m6_stmt.py's exhausted_else row for thermal_model.py leaves the census -> to_zero (observed 0)
- Control: the explicit modes are untouched on all three configs (on -> True, off -> False), and with zone keys present the default mode and the unknown mode agree (2 of 2)
- Mechanism: thermal_model.py:1122-1134: `if two_zone_mode in (ON, DEFAULT): True / elif == OFF: False / else: any(zone key in config)`. The three arms take all three values of const.TWO_ZONE_MODES between them, so the presence rule above them in the comment (`auto ... is the presence rule unchanged; an unknown value is treated as auto`) cannot run for a valid entry. An install that never chose a mode and stores no zone keys -- every single-zone house set up before the mode key, and tests/profiles.py's `house(two_zone=False)` -- is simulated, planned and identified as two zones with the default zone parameters. config_flow._single_zone takes its answer from the same call, so the options flow hides the whole-house loss field on those entries too.
- Fix scope: thermal_model.py: `auto` falls through to the presence rule (the membership test names ON alone). Every golden and scenario built on a config with no zone keys moves back to one zone.

## M5 table

| module | functions | pinned | swallowed | unentered | not driven | pinned by |
|---|---|---|---|---|---|---|
| batchmath | 1 | 1 | 0 | 0 | 0 | plan_view |
| debugger | 49 | 49 | 0 | 0 | 0 | debug_collect |
| dhw_planner | 41 | 36 | 0 | 3 | 2 | block_duty, edge, plan_view |
| draw_range | 37 | 8 | 0 | 14 | 15 | config_flow_steps, debug_collect, entities, solar_alignment |
| driving_grade | 9 | 2 | 0 | 0 | 7 | config_flow_steps |
| duty_legs | 12 | 3 | 0 | 9 | 0 | plan_view |
| duty_switch | 37 | 16 | 0 | 15 | 6 | block_duty, config_flow_steps, entities, guard_pins |
| early_cutoff | 16 | 2 | 1 | 2 | 11 | block_duty, config_flow_steps |
| entry_config | 26 | 17 | 0 | 1 | 8 | config_flow_steps, entities, solar_alignment, wood_advisor |
| flow_meter | 6 | 3 | 1 | 0 | 2 | solar_alignment |
| heat_curve | 28 | 8 | 1 | 18 | 1 | config_flow_steps, debug_collect |
| heat_energy | 33 | 21 | 1 | 9 | 2 | entities, solar_alignment |
| issues | 4 | 4 | 0 | 0 | 0 | entities, solar_alignment |
| learner_progress | 9 | 7 | 0 | 1 | 1 | config_flow_steps, solar_alignment |
| log_latch | 2 | 2 | 0 | 0 | 0 | config_flow_steps, solar_alignment |
| notifier | 15 | 3 | 0 | 1 | 11 | config_flow_steps |
| off_restore | 16 | 9 | 0 | 5 | 2 | config_flow_steps, debug_collect, guard_pins, wood_advisor |
| plan_slots | 2 | 2 | 0 | 0 | 0 | plan_view |
| plan_step | 1 | 1 | 0 | 0 | 0 | block_duty |
| price_tiles | 17 | 2 | 0 | 0 | 15 | config_flow_steps |
| quiet_windows | 25 | 18 | 0 | 0 | 7 | block_duty, config_flow_steps, guard_pins |
| replay_doc | 42 | 42 | 0 | 0 | 0 | debug_collect |
| running_signal | 15 | 13 | 0 | 2 | 0 | block_duty, config_flow_steps, solar_alignment |
| runs | 11 | 1 | 0 | 6 | 4 | plan_view |
| slab_seed | 5 | 5 | 0 | 0 | 0 | entities, solar_alignment |
| slot_drivers | 7 | 7 | 0 | 0 | 0 | entities, plan_view |
| supply_hold | 8 | 3 | 0 | 3 | 2 | block_duty, config_flow_steps |
| whatif | 6 | 0 | 0 | 0 | 6 |  |

C2 groups:

| group | functions | pinned | swallowed | unentered | not driven | pinned by |
|---|---|---|---|---|---|---|
| batched_gradient_and_bounds_gate | 16 | 10 | 0 | 1 | 5 | entities, plan_view |
| weekly_windows | 8 | 6 | 0 | 0 | 2 | config_flow_steps, guard_pins, solar_alignment |
| topology_catalogue | 21 | 19 | 0 | 0 | 2 | config_flow_steps, entities, guard_pins, solar_alignment, wood_advisor |
| wood_and_coil | 38 | 28 | 0 | 3 | 7 | guard_pins, plan_view, solar_alignment, wood_advisor |
| dhw_confidence | 2 | 2 | 0 | 0 | 0 | config_flow_steps, plan_view |
| tuya_signals_and_prefill | 44 | 35 | 0 | 8 | 1 | config_flow_steps, entities, guard_pins, solar_alignment |
| re_anchor_law | 2 | 0 | 0 | 0 | 2 |  |

Swallowed (entered, deletion leaves every entering script green): early_cutoff.py:329:diagnostics_view; flow_meter.py:27:thermal_output_kw; heat_curve.py:351:write_displace; heat_energy.py:105:CounterDelta.rebase

Unentered: dhw_planner.py:379:_DhwPlanContext.c_dhw; dhw_planner.py:384:_DhwPlanContext.tank_decay; dhw_planner.py:1634:DhwPlanner._apply_dhw_pins; draw_range.py:188:DrawRange._ceiling_median; draw_range.py:191:DrawRange.takes_ceiling; draw_range.py:201:DrawRange.observe_ceiling; draw_range.py:249:DrawRange.observed; draw_range.py:264:DrawRange._metered_range; draw_range.py:316:DrawRange.observe_idle; draw_range.py:320:DrawRange.planned; draw_range.py:331:DrawRange.summary; draw_range.py:359:DrawRange.from_dict; draw_range.py:440:_stored_idle; draw_range.py:469:_command_cells; draw_range.py:514:follows_ask; draw_range.py:633:planned_range; draw_range.py:661:diagnostics_view; duty_legs.py:67:both_step_legs; duty_legs.py:95:_runs; duty_legs.py:101:leg_ends; duty_legs.py:152:switch_weights_batch; duty_legs.py:192:switch_weight; duty_legs.py:209:lost_share; duty_legs.py:222:availability; duty_legs.py:263:delivered_space; duty_legs.py:278:switch_ban; duty_switch.py:137:SwitchContext.void_cause; duty_switch.py:148:_heated; duty_switch.py:174:Direction.n; duty_switch.py:178:Direction.p; duty_switch.py:182:Direction.span_days; duty_switch.py:186:Direction.median_off_s; duty_switch.py:190:Direction.weights; duty_switch.py:246:Direction.from_row; duty_switch.py:315:DutySwitchLearner.edge; duty_switch.py:362:DutySwitchLearner._void; duty_switch.py:367:DutySwitchLearner._close; duty_switch.py:401:DutySwitchLearner.split; duty_switch.py:415:DutySwitchLearner.from_record; duty_switch.py:449:_Record.feed; duty_switch.py:526:both_step_duty; early_cutoff.py:119:CutoffState.interval_cut; early_cutoff.py:181:arm._changed; entry_config.py:245:EntryConfig.from_mapping; heat_curve.py:105:state_for; heat_curve.py:112:_restorer; heat_curve.py:123:_restore_recorded; heat_curve.py:135:_baseline_reading; heat_curve.py:141:_persistent_restored; heat_curve.py:308:offset_target; heat_curve.py:332:_decide; heat_curve.py:393:_send; heat_curve.py:404:_age_s; heat_curve.py:414:_record_write; heat_curve.py:424:_local_day; heat_curve.py:428:writes_today; heat_curve.py:433:classify; heat_curve.py:448:persistent_target; heat_curve.py:462:_within_range; heat_curve.py:480:_persistent_refusal; heat_curve.py:495:write_persistent; heat_curve.py:536:_write_persistent_target; heat_energy.py:98:CounterDelta.delta_over; heat_energy.py:130:close_after_h; heat_energy.py:135:resolution_refusal; heat_energy.py:310:span_heat; heat_energy.py:455:HeatEnergyMeter._close; heat_energy.py:517:HeatEnergyMeter.earns_basis; heat_energy.py:522:HeatEnergyMeter.earn_basis; heat_energy.py:543:HeatEnergyMeter.spans_own_scale; heat_energy.py:580:log_close; learner_progress.py:175:FreezeRecord.last; notifier.py:110:_comfort_cause; off_restore.py:199:_restore_baseline; off_restore.py:287:async_rebaseline; off_restore.py:304:async_consumer_state; off_restore.py:314:consumer_state; off_restore.py:320:async_save_state; running_signal.py:109:attach._changed; running_signal.py:189:_arm_timer._due; runs.py:64:steps_at_least; runs.py:102:realizable; runs.py:108:commit; runs.py:165:candidates; runs.py:191:_moves; runs.py:210:_advance; supply_hold.py:96:_freeze_span; supply_hold.py:142:_passes; supply_hold.py:149:_ends_soon; optimizer.py:3732:HeatPumpOptimizer._terminal_cost_batch; wood_fuel.py:279:_iso; wood_fuel.py:352:_wood_override_fuel; thermal_model.py:359:ThermalParameters.dhw_coil_active; pump_signals.py:179:PumpElectricHeat.resistive_heat; pump_signals.py:188:PumpElectricHeat.compressor_draw_distorted; pump_signals.py:318:PumpSignals.mode_live; pump_signals.py:323:PumpSignals.space_heat; pump_signals.py:328:PumpSignals.dhw; pump_signals.py:333:PumpSignals.space_blocked; pump_signals.py:343:PumpSignals.dhw_blocked; device_prefill.py:101:EntityRecord.domain

## Non-findings

- No definition of the package is dead by name: every function, method, class and module constant is named by other package code, by the Home Assistant contract or by a class the framework calls. `dev/audit/rounds/round11/D7/s3/m6_dead.py --trace <trace dir> --perturb` -> dead=0 of 6969; planted_delta=1; dead_after_readers=0
- No function body holds a statement dead by the AST alone: no store overwritten before a load, no effect-free expression statement, no constant condition, no duplicate dict key, no repeated if/elif test, no identical arms. `dev/audit/rounds/round11/D7/s3/m6_stmt.py --perturb` -> 0 in each of six kinds over 2678 bodies; self_operand=2 (both the `x != x` NaN test); exhausted_else=1 (finding D7-s3-09); every planted kind reads delta 1
- No instance attribute is written by production and read by nothing at all. `dev/audit/rounds/round11/D7/s3/m6_inner.py --perturb` -> write_only_attributes=0 (8 more are read only by tests: finding D7-s3-05); planted_delta=1
- The eight module-level functions whose every naming is an attribute read (async_setup_debugger, async_setup_notifier, async_register_services and five more) are reached through the lazy module loader, not masked by a same-named method. `dev/audit/rounds/round11/D7/s3/m6_inner.py | grep '^ROW masked'` -> masked_functions=8, each entered in the trace or loaded through __init__._lazy
- DhwStore.store_temp_for_tap and tap_temp_for_store are exact inverses, combi and not. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only dhw_store_tap` -> 0 of 24 probes disagree
- duty_switch._stored_number and store._number admit the same stored numbers. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only stored_number` -> 0 of 13 probes disagree
- StorageComponent.soc and VirtualBattery.soc are one rule. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only soc` -> 0 of 5 probes disagree
- The buffer cooling-rate prior lies inside its own clamp at every volume, and the wood and hot-water tank UA both invert to their cooling rate. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only buffer_prior_in_bounds; dev/audit/rounds/round11/D7/s3/m8_agree.py --only ua_from_rate` -> 0 of 8 and 0 of 3 probes disagree
- Without a throttling valve simulate_trajectory_batch is simulate_trajectory row for row, to the bit: eight model variants (one- and two-zone config, big buffer, flow-Carnot and flow-curve COP, wood tank, wood coil) under three weathers and four schedules each. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only twin_trajectory` -> 24 of 24 no-valve probes agree on every series; the 18 valve probes are finding D7-s3-08
- The solve's objective_batch is its scalar objective row for row, to the bit, wherever no per-window capacity term is priced: five no-tariff cases and the distinct-days tariff. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only twin_objective` -> 6 of 8 cases agree at relative difference 0; the two that do not are finding D7-s3-07
- wood_share/_wood_share_vec, _smooth_topk_sum/_batch, _day_peaks/_batch and switch_weight/switch_weights_batch agree to the bit. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only twin_wood_share (and twin_topk, twin_day_peaks, twin_switch_weight)` -> 0 of 24, 0 of 12 (smooth rows of twin_topk), 0 of 4, 0 of 3
- dhw_schedule's formatters and parsers are inverses: every one of the 127 weekday sets, 9 clock times, 6 window specs and 4 weekly specs survives format-then-parse. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only parse_format` -> 0 of 146 probes disagree
- Every class with both as_dict and from_dict reads back what it wrote (15 classes; a default instance, and one moved off its defaults after one admission). `dev/audit/rounds/round11/D7/s3/m8_agree.py --only as_from_dict` -> 0 of 29 probes disagree; AccuracySample has no default instance and was not driven
- comfort_band.effective and config_flow._effective return the same value. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only effective` -> 0 of 4 probes disagree
- Every one of the 29 added modules has a module docstring, at least one docs/ or README paragraph naming it, and at least one production importer. `dev/audit/rounds/round11/D7/s3/m5_train.py pins --trace <trace dir>` -> 29 of 29 on each of the three; fewest: issues.py 6 docstring lines; 25 modules have exactly 1 docs paragraph; 7 have exactly one importer
- The seven literals of `a state that holds no value` differ in membership ('none', '' and None are each missing somewhere), but no pair of production predicates was found to return different answers for a state Home Assistant can deliver; a static comparison of literals, reported and not raised. `dev/audit/rounds/round11/D7/s3/m8_agree.py --only no_value_state` -> 3 of 5 members differ across 7 sites (inputs.py:69, inputs.py:447, away.py:180, away.py:626, coordinator.py:8723, price_model.py:824, supply_hold.py:65)
- The deletion hook kills nothing when armed on a line no function starts at. `dev/audit/rounds/round11/D7/s3/m5_train.py null --trace <trace dir>` -> null_new_failing=0

## Harnesses

- `dev/audit/rounds/round11/D7/s3/fn_trace.sh`
- `dev/audit/rounds/round11/D7/s3/trace_site/sitecustomize.py`
- `dev/audit/rounds/round11/D7/s3/m5_train.py`
- `dev/audit/rounds/round11/D7/s3/m5_pin_demo.py`
- `dev/audit/rounds/round11/D7/s3/m6_dead.py`
- `dev/audit/rounds/round11/D7/s3/m6_inner.py`
- `dev/audit/rounds/round11/D7/s3/m6_stmt.py`
- `dev/audit/rounds/round11/D7/s3/m6_two_zone_auto.py`
- `dev/audit/rounds/round11/D7/s3/m8_enum.py`
- `dev/audit/rounds/round11/D7/s3/m8_agree.py`
- `dev/audit/rounds/round11/D7/s3/m8_families.tsv`
- `dev/audit/rounds/round11/D7/s3/m5_mutants.json`
- `dev/audit/rounds/round11/D7/s3/m5_c2_mutants.json`

## Unfinished

- D7.M5: Function-level deletion mutants not driven through every entering script: 102 of the 29 modules' functions (dhw_planner.py 2, draw_range.py 15, driving_grade.py 7, duty_switch.py 6, early_cutoff.py 11, entry_config.py 8, flow_meter.py 2, heat_curve.py 1, heat_energy.py 2, learner_progress.py 1, notifier.py 11, off_restore.py 2, price_tiles.py 15, quiet_windows.py 7, runs.py 4, supply_hold.py 2, whatif.py 6) and 18 of the C2 groups' (coordinator.py 1, dhw_schedule.py 2, optimizer.py 1, tariff.py 5, thermal_model.py 5, topology.py 2, wood_fuel.py 2). Each stayed green under the scripts driven so far; what is left is the 70-96 s tier where the second pass was cut (config_flow_steps.py, validate.py, edge.py, entities.py) and the long scripts never driven (tests/features.py at 6073 s here, finite_boundary.py, backtest.py, optimality.py, boost_drift_replay.py, manual_plan.py, dst_checks.py; load1 150-300); resume with `m5_train.py mutate --retry --max-script-seconds 4000 --out m5_mutants.json` (and `--c2 --out m5_c2_mutants.json`), which re-drives only the scripts not yet run. The golden differential (env_drift.py --all) was not run for any mutant: the export has no .git.

## Leads

- D3-s3, `tests/entities.py`, line 9634 `_low, _high = _NOMINAL[_key]`: In this tree the script stops with KeyError 'house_heat_loss_coefficient' at line 9634 of 42669 (after 676 passing checks and 12 failing ones), so every later check is never evaluated; the same key is the `declared but not rendered {'thermal_model': ['house_heat_loss_coefficient']}` failure in tests/config_flow_steps.py.
- D3-s3, `tests/`, the behaviour scripts' own verdicts in this tree: Unmutated, on this box: block_duty 1 of 153 failing, config_flow_steps 5 of 585, debug_collect 1 of 163, guard_pins 1 of 91 (#1913 GCHV hold), manual_plan 5 of 132, optimality 5 of 84, finite_boundary 6 of 114, dst_checks 8 of 137, boost_drift_replay 5 of 46, plan_view `space slot energy 46.246 kWh != schedule 46.310 kWh`; deployment_shape and golden cannot run without .git. Logged per script by fn_trace.sh; this seat used them only as each mutant's baseline.
- D3-s3, `tests/features.py`, the project_window_mean block (about line 19066): The check `project_window_mean(2.0, 30.0, 6.0, 60.0) == 4.0` sits at the one minute where D7-s3-02's dropped term cannot show (elapsed equals remaining); its neighbours at 45 and 60 minutes do see it.
- unknown, `custom_components/heatpump_optimizer/boost.py`, persist (and six sibling save wrappers: m8_enum.py --show A014, A028): Nine persist wrappers share one try/await-save/except shape; two (coordinator._async_save_thermal_learning, _async_save_energy_totals) await the store's async_wait_for_read first and seven do not. Whether a save can overtake a pending load on the seven is a lifecycle question for D1; not measured here.
- unknown, `custom_components/heatpump_optimizer/config_flow.py`, HeatPumpOptimizerOptionsFlow._disinfection_errors: The disinfection mode is compared with FREQ_MODE_CONTROL (the frequency feature's constant, 'control'); no disinfection-mode constant exists. One word serving two vocabularies: right while both spell it the same.
- D3-s3, `tests/env_drift.py`, C2: drift gate, scoped gate (tests/closure.py), stress budgets (tests/stress.py, tests/stress_budgets.json): Three of the additions round 10 handed over as C2 are test instruments, outside this seat's cells (custom_components/heatpump_optimizer/*.py): each still owes its fails-on-deletion check, doc paragraph and owner.
- unknown, `custom_components/heatpump_optimizer/www/`, C2: card collaborators: The card's collaborator modules are JavaScript, outside this seat's cells; the same three questions are owed there.

## Exposure

m5_train.py greps docs/*.md and README.md for `<module>.py` and counts the paragraphs; the seat read no docs text. No earlier round's findings were read: the previous baseline SHA was taken from the `baseline_sha` field of the round-10 report files left in the export (grep for the field only), as D7.M5's enumerator requires.
