# D8-s1, round 10: sensor verification (D8.M1, D8.M2)

Baseline 17f1c55fad1b. Machine: macOS arm64, a shared B4 box (load1 21-117 while this ran). Every number below is a count, so box load does not affect it.

## Method

`matrix.py` (D8.M1) builds 19 cells. Five come from `coordinator_scenarios()`, and 14 are coord_minimal plus one feature overlay each:

- dhw
- two_zone
- valve_storage
- two_tank
- coil
- wood
- ecl110
- pv
- capacity
- grid_fee
- tuya_dhw_only: a select reading "DHW (Hot Water)", which blocks space heating
- tuya_dhw_only_min
- min_modulation: 12 kW max power, 1 kW min power
- away

Each cell runs the production `_async_update_data` with the four network fetches stubbed:

1. Cycle A.
2. Change the inputs: prices, forecast, indoor, outdoor and tank readings.
3. Cycle B.

Five cells also walk the frozen clock 16 quarter-hours forward. In every snapshot, every entity of the sensor, binary_sensor, button, climate and switch platforms is built through the real `async_setup_entry`.

D8.M2 then checks each entity:

- whether it raises
- MEASUREMENT values are numeric
- TIMESTAMP values are tz-aware
- ENUM values are among the options
- the unit matches the device_class
- no monetary value is a MEASUREMENT
- translation_key is present in strings.json
- state and attributes are orjson- and JSON-clean (no numpy types, no non-finite numbers)
- no entity is enabled, available and None
- which entities stay static between A and B

The operating-state oracle compares each entity against the plan's own `current_action` (`power` + `dhw_power`, `heat_pump_on`). The entities checked are the climate `hvac_action`, `recommended_power`, `plan_space_heating`, `plan_dhw_heating` and `heat_pump_action`.

## Findings

### D8-s1-01: Plan sensors say "heating now" on a step the plan has switched off (low, bug)

`SpaceHeatingPlanSensor` and `DHWHeatingPlanSensor` publish "heating now" from the plan's `active_now`. `active_now` is set in `coordinator._build_plan_views` as `raw[0] > 0.05`. The plan's own on decision is `thermal_model.planned_draws_run` with `MIN_RUNNING_DRAW_KW = 0.1`.

So on a step drawing 0.05-0.1 kW, the entities disagree:

| Entity | Published value |
|---|---|
| Space Heating Plan | "heating now" |
| Heat Pump Action | "off" |
| Climate hvac_action | idle |
| Recommended Power | 0 |

The plan's slot list uses the same 0.05 kW literal (`_plan_slots`, and the `DHWScheduleSensor` fallback). Its "N slots planned" count therefore includes steps the plan declares off.

- **Harness:** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D8/s1/f1_active_now.py`
- **Result:** `heating_now_while_off` = 1 of 36 snapshots (coord_all_features at step 17: space 0.07 kW, `heat_pump_on` False, mode off). `slot_steps_declared_off` = 4 of 192 steps.
- **Perturbation:** `--perturb` gates `active_now` on `result.heat_pump_on_schedule[0]`. `heating_now_while_off` goes from 1 to 0. The secondary count stays at 4, because the slot literal is separate.
- **Seams:** `grep -n "0\.05" custom_components/heatpump_optimizer/coordinator.py custom_components/heatpump_optimizer/sensor.py`, narrowed to `_plan_slots`, `active_now` and `DHWScheduleSensor`.
- **Fix scope:** the plan views and the plan sensors take the plan's running rule (`planned_draws_run` / `heat_pump_on_schedule`), not a literal 0.05.
- **Note for the judge:** `MIN_RUNNING_DRAW_KW` cannot be perturbed in memory. The solve runs in `process_worker.py`'s subprocess.

## Non-findings

`matrix.py`, 19 cells, cycles A and B (5 cells over 18 snapshots). Each class below counted 0:

- raises
- measurement not numeric
- timestamp not tz-aware
- enum value not in options
- unit vs device_class mismatch
- monetary value as MEASUREMENT
- untranslated translation_key
- not serialisable
- enabled, available and None

The other oracle classes also counted 0:

- climate action vs plan
- recommended_power vs plan
- heat_pump_action idle while drawing
- dhw-plan disagreement

The only oracle hit is the space-plan disagreement in D8-s1-01.

Two harness gaps came up and are now closed:

1. `next_optimization` was None in 17 cells while the harness bypassed `_async_update_data`. It came from the gap, not from production: driving the real cycle sets it.
2. A plain `sensor.*` mode entity reading "DHW" is ambiguous by design (`pump_mode._STATUS_AMBIGUOUS`). The DHW-only cell needs a select entity with options.

## Leads (outside my cells)

- **D2-s1, optimizer.py:_build_actions (p_norm/mode):** in min_modulation (min power 1.0 kW), the plan's step 0 runs at 0.3 kW, mode "eco", `power_normalized` 0.0 and `heat_pump_on` True. That is below nameplate minimum modulation, and the normalized power reads 0 while the pump is on.
- **D2-s1, coordinator.py current_action:** carries `np.float64` (`solar_reduction_factor`, `pre_heat_urgency`). No entity publishes them today (0 not_serialisable), but the payload is not plain.

## Unfinished

- Within M2, "value follows the payload": `matrix.py` prints the 54 entity keys whose state was identical in A and B (STATIC lines). Each one was not resolved against its source key. Most are accumulators with no meter, frozen-clock timestamps or night-time solar, but each needs a per-key oracle.
- `MonthlySavingsSensor` is available but None when settled months exist and the open month has no booking yet. This was found by reading the code and not measured.

## Exposure

None. No docs/ and no GitHub were read.
