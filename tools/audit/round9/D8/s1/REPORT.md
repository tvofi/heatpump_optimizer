# D8-s1 report (round 9, baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1)

Rendered by the B6 box host from the seat's returned JSON report, verbatim in content: the seat's own write of this file was refused by its tool environment. The JSON is authoritative and is carried in tools/audit/round9/reports-B6.json.

## Coverage

- **D8.M1** (deep): matrix.py: 6 topologies (5 coordinator_scenarios + coord_minimal_bare) x 15 feature toggles = 90 cells, each 2 real _async_update_data cycles 15 min apart with every input moved, all 64 sensor+binary_sensor entities through the real async_setup_entry; light.py adds the setup-time light refresh over all 90 cells. No earlier-round evidence (tools/audit/round3..round8) was read.
- **D8.M2** (deep): matrix.py per entity per cycle: raise, orjson, non-finite, numeric-under-state-class, tz-aware TIMESTAMP, ENUM option, unit vs device class, available-unknown, value-follows-payload, operating-state oracle vs current_action power+dhw_power/heat_pump_on incl. DHW-only (Tuya select mode=DHW, space blocked) and minimum-modulation cells; price15.py, minpower.py, mold.py targeted.

## Unfinished

- none

## Findings

### D8-s1-01 (high, bug, class_guess P2): Current Electricity Price publishes an earlier quarter's price when prices are quarter-hourly

- step: D8.M2
- claim: With 15-minute price entries, sensor.heat_pump_optimizer_cost_current_electricity_price publishes the price of the earliest quarter within the last hour instead of the quarter covering now at 95 of 96 quarter instants of a day.
- mechanism: CurrentPriceSensor.native_value reads data['current_price'] = coordinator._get_current_price() -> _current_spot_price(), which returns the first entry with starts_at <= now < starts_at + 1 h. That test assumes hourly entries. The coordinator ingests 15-minute days (quarters_from_entries, #19), and there the first match is up to 45 min old. get_current_action picks the step covering now, so Heat Pump Action's price attribute and the price sensor disagree.
- evidence: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/price15.py` -> 95 wrong quarter instants of 96 (harness tools/audit/round9/D8/s1/price15.py; load1 6.21, thread_factor 1.0; other D8/finder seats running on the box; count is contention-immune)
- instrumented symbol: heatpump_optimizer.sensor:CurrentPriceSensor.native_value (over coordinator:HeatPumpOptimizerCoordinator._current_spot_price via _build_data_dict)
- perturbation: price15.py --fix: _current_spot_price treats an entry as covering [its start, the next entry's start) (expected to_zero; observed 0)
- metric: Of 96 instants (7 min into each quarter of 2026-01-15, Europe/Stockholm), count where the sensor's native_value differs from the price entry whose quarter covers now.
- phenomenon property: Every published or booked 'price of now' equals the price entry whose interval [start, next start) contains now, at any price resolution.
- seam rule: `grep -n 'timedelta(hours=1)' custom_components/heatpump_optimizer/coordinator.py  (every price-covering-now search with a fixed 1 h window)`
- null control: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/price15.py --hourly` -> 0 (same day at hourly resolution: 0 wrong, so the effect is the resolution assumption)
- proposed fix scope: coordinator._current_spot_price: cover [start, next start) (fall back to +1 h only for the last entry); the settlement and comfort learner share _get_current_price, so they are fixed together.
- files: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/sensor.py

### D8-s1-02 (low, bug, class_guess P2): DHW Heating Schedule counts 15-minute steps as 'heating periods', disagreeing with DHW Heating Plan's slot count

- step: D8.M2
- claim: In every DHW-enabled matrix cycle (92 of 92), sensor.heat_pump_optimizer_dhw_heating_schedule publishes a 'heating periods' count different from the DHW Heating Plan's slot_count for the same schedule.
- mechanism: DHWScheduleSensor.native_value counts dhw_schedule steps with dhw_power > 0.1 and labels them periods. _plan_slots merges consecutive steps above 0.05 into slots. A multi-step slot is counted once by the plan and once per step by the schedule sensor.
- evidence: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/matrix.py` -> 92 cycles (of 92 DHW cycles) (harness tools/audit/round9/D8/s1/matrix.py; load1 4.17, thread_factor 1.0; other seats running; count is contention-immune)
- instrumented symbol: heatpump_optimizer.sensor:DHWScheduleSensor.native_value (against sensor:DHWHeatingPlanSensor.extra_state_attributes['slot_count'])
- perturbation: matrix.py --perturb-dhw-runs: native_value counts contiguous runs of dhw_power > 0.05 (run on --only +dhw, 6 cells, baseline 12) (expected to_zero; observed 0)
- metric: Count of (cell, cycle) where the integer leading DHW Heating Schedule's state differs from DHW Heating Plan's slot_count, both available.
- phenomenon property: Two entities summarising one plan state the same count of heating periods: a period is a contiguous run at the plan's own threshold.
- seam rule: `grep -n 'dhw_power", 0) >\|threshold: float = 0.05' custom_components/heatpump_optimizer/sensor.py custom_components/heatpump_optimizer/coordinator.py`
- leave-one-out: {"cells": 46, "min": 2, "max": 2, "drop_most_favourable": 90}
- proposed fix scope: DHWScheduleSensor.native_value counts contiguous runs at the _plan_slots threshold (or reads dhw_plan slot_count).
- files: custom_components/heatpump_optimizer/sensor.py

### D8-s1-03 (low, bug, class_guess P2): Recommended Power publishes a sub-threshold draw at steps Heat Pump Action reports 'off'

- step: D8.M2
- claim: At plan steps whose space power lies between 0.05 kW and the on-threshold max(0.1, 0.5*min_power), Recommended Power (and Heat Pump Action power_kw) publish that power while the same action has heat_pump_on=False and Heat Pump Action reads 'off'.
- mechanism: entity.commanded_power_kw returns power + dhw_power and never reads heat_pump_on. get_current_action classifies such a step as off (below on-threshold) but keeps the continuous power.
- evidence: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/minpower.py` -> 4 horizon steps (5 topologies x 96 steps at min_power 1.0 kW); worst 0.41 kW (harness tools/audit/round9/D8/s1/minpower.py; load1 5.78, thread_factor 1.0; other seats running; count is contention-immune)
- instrumented symbol: heatpump_optimizer.sensor:CurrentPowerSensor.native_value and sensor:HeatPumpActionSensor.native_value, each step made current via optimizer:HeatPumpOptimizer.get_current_action + coordinator._build_data_dict
- perturbation: minpower.py --perturb: commanded_power_kw returns 0.0 when the action's heat_pump_on is False (expected to_zero; observed 0)
- metric: Count of horizon steps at which Recommended Power > 0.05 kW while Heat Pump Action's state is 'off'.
- phenomenon property: No entity attributes a power draw to the pump at a step the same action declares off (heat_pump_on False).
- seam rule: `grep -rn 'commanded_power_kw(' custom_components/heatpump_optimizer/`
- null control: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/minpower.py (min_power 0.2 arm)` -> 0 (on-threshold 0.1: no sub-threshold band, so 0; matrix.py independently shows 2 of 180 real cycles (coord_all_features+valve#1 0.36 kW, +grid_fee#0 0.29 kW))
- leave-one-out: {"cells": 5, "min": 0, "max": 4, "drop_most_favourable": 0}
- proposed fix scope: entity.commanded_power_kw gates on heat_pump_on (shared with climate's recommended_power_kw), or get_current_action zeroes power below the on-threshold.
- files: custom_components/heatpump_optimizer/entity.py, custom_components/heatpump_optimizer/sensor.py

## Non-findings

- No cycle and no entity property raises across 90 cells x 2 real cycles x 64 entities: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/matrix.py` -> cycle_raises=0, property_raises=0
- Every published state and attribute is orjson-serialisable and finite: `matrix.py` -> not_serialisable=0, nonfinite=0
- State-classed entities publish numbers, TIMESTAMPs are tz-aware, ENUM states are listed options, units match device class: `matrix.py` -> measurement_nonnumeric=0, timestamp_not_aware=0, enum_not_option=0, unit_vs_device_class=0
- Heat Pump Action agrees with the plan's heat_pump_on and its power_kw / Recommended Power equal plan power + dhw_power in every cell incl. DHW-only (hot_water, space 0, DHW 3.4-4.0 kW): `matrix.py; matrix.py --only tuya_dhw_only --show` -> action_off_while_on=0, action_running_while_off=0, power_disagrees=0
- The only available-but-unknown entity after a solve is Valve Target Recommendation without a mixing valve (disabled by default): `matrix.py` -> available_unknown=156 = 78 non-valve cells x 2
- Setup-time light refresh publishes nothing invalid beyond plan-less unknowns: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/light.py` -> only light_available_unknown=908
- Mold Floor Breach publishes floor/shortfall/space_blocked in DHW-only mode and stays off inside the margin: `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/mold.py` -> room 21.4: floor 21.0 shortfall -0.1; room 15.7: floor 16.02 shortfall 0.32; mold_on=0 both
- Values unmoved between cycles have an explanation, so none is stale: dark-hour solar, hourly forecast step in bare cells, lifetime accumulators with no settled interval, whole-degree DHW advisor: `matrix.py (unmoved listing)` -> solar 90/90 cells at 06:10 Jan; outdoor/COP 15 bare cells

## Harnesses

- tools/audit/round9/D8/s1/matrix.py
- tools/audit/round9/D8/s1/light.py
- tools/audit/round9/D8/s1/mold.py
- tools/audit/round9/D8/s1/price15.py
- tools/audit/round9/D8/s1/minpower.py

## Leads

- owner D1-s2: custom_components/heatpump_optimizer/coordinator.py `_get_current_price / _current_spot_price`: The same 1 h window prices the settlement's pending dict and the comfort learner's relative price. With quarter-hour prices, booked costs (lifetime cost accumulators, ledger) would use a quarter up to 45 min old.
- owner D8-s2: custom_components/heatpump_optimizer/entity.py `commanded_power_kw (climate recommended_power_kw)`: The climate entity's recommended_power_kw shares commanded_power_kw, which ignores heat_pump_on (D8-s1-03). It likely publishes a power at steps its hvac_action calls off.
- owner D8-s3: custom_components/heatpump_optimizer/sensor.py `ValveTargetRecommendationSensor`: Static enabled_default False even when a mixing valve is configured. Without a valve it is available and permanently unknown instead of unavailable.
- owner D2-s1: custom_components/heatpump_optimizer/coordinator.py `_dhw_setpoint_sweep`: It prices candidate setpoints at ctx._current_state.outdoor_temperature, which is the 5.0 C ThermalState default without an outdoor thermometer. _effective_outdoor / forecast_outdoor_now exist for exactly this case.
- owner D2-s1: custom_components/heatpump_optimizer/battery.py `VirtualBattery / label_measured`: On a DHW install without a tank probe, Thermal Battery charge/energy include the dhw_tank at the constant 55.0 C constructor default across cycles. It is disclosed as 'modelled' but not modelled.

## Exposure

none
