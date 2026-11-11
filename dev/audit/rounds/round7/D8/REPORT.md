# D8 — Sensor verification and ordering (round 7)

Baseline: `f9d6f78243fa65f6fa128d2357752a2ae7f60648`. Machine: 8-core Apple M1,
8 GB, darwin 25.6.0, Python 3.11.5, numpy 2.4.6. All numbers are counts or
ratios against a fixed series — contention-immune — except where marked
provisional (none here). Exposure: none (no `docs/`, no GitHub read).

## Method

`matrix.py` builds the coordinator the way `_capture_coordinator` does
(inject 48 h of prices and forecasts, freeze the clock, run two cycles through
`_update_current_state` + `async_run_optimization` + `_build_data_dict`), then
constructs every entity of all five platforms (`sensor`, `binary_sensor`,
`climate`, `switch`, `datetime`) through the real `async_setup_entry`, over
9 configurations (the 5 `coordinator_scenarios()` topologies plus DHW / PV /
peak / away toggles on the minimal base). For each entity it checks every
per-entity rule the brief names and emits one `RESULT` line per violation
class.

## Findings

### D8-01 — the sensor-gap advisor ranks over power series the coordinator never publishes

The `SensorGapAdvisorSensor` (`heatpump_optimizer/sensor.py:2818`) reads
`coordinator.data["house_power_series"]` and `["heat_pump_power_series"]` to
price the missing house-power meter (`topology.rank_sensor_gaps` ->
`peak_miss_sek`). The coordinator's `_build_data_dict` never writes those two
keys — the only places they appear in production are those two reads — so on a
real install the advisor always sees an empty series and `_window_peak` returns
0.0, making the house-power slot's "estimated extra cost per month" a silent
0.00. The docstring of `_gap_probe_terms` names this exact case ("the advisor
against a series-less payload ranks nothing") but treats it as the no-data
fallback, when it is in fact the steady state of every install. The tests pass
because `tests/entities.py` feeds the advisor a fake coordinator whose data
carries `_gap_load_data` (which does include the series), so the production
wiring of the series is never exercised.

- Instrumented: `heatpump_optimizer.sensor:SensorGapAdvisorSensor._gaps`
- Metric: the house-power slot's `sek_per_month` with the house-power entity
  unconfigured, on a real post-solve payload.
- Measured: `0.0` SEK/month with the coordinator's own payload (162 keys,
  neither series present); `30.0` SEK/month once the two series are published.
- Perturbation (the fix, one line in `_build_data_dict`): publish
  `house_power_series` and `heat_pump_power_series`. Direction: up.

Harness: `tools/audit/round7/D8/gap_series.py`.

### D8-02 — `dhw_setpoint_advisor` ships enabled-by-default on a no-DHW install

`DHWSetpointAdvisorSensor` (`sensor.py:2361`) is the one hot-water sensor not
wrapped in `_DHWEntityMixin`. Every other DHW-gated entity (dhw_cost,
dhw_energy, dhw_heating_cost, dhw_heating_schedule, plan_dhw_heating) follows
the mixin's rule — "a fresh install with no hot water must not ship enabled
entities that are unavailable on every refresh" — and ships disabled by default
when DHW is off. `dhw_setpoint_advisor` declares no registry default and no DHW
gate, so a no-DHW install ships it enabled, and its `available` (which needs
`dhw_advisor.recommended_setpoint`) is False forever, since `_build_data_dict`
emits `dhw_advisor` only when DHW is on.

- Instrumented: `heatpump_optimizer.sensor:DHWSetpointAdvisorSensor.entity_registry_enabled_default`
- Metric: count of sensor entities enabled-by-default that are unavailable on
  a no-DHW config and available on a DHW config.
- Measured: `1` (dhw_setpoint_advisor), against `5` DHW entities that correctly
  ship off without DHW. Wrapping the sensor in `_DHWEntityMixin` flips its
  registry default to `False` on the no-DHW coordinator (count -> 0).

Harness: `tools/audit/round7/D8/dhw_advisor_default.py`.

## Non-findings (checked and held)

- **JSON/orjson-serialisability of every published leaf** across all five
  platforms x 9 configs x 2 cycles: `RESULT json_bad=0` (no numpy scalar,
  numpy array, NaN/inf, or non-JSON type in any `native_value` / `is_on` /
  climate temperature / attribute leaf). The `HeatPumpOptimizerSensorBase`
  `_finite` scrub and the climate/binary platforms hold.
- **ENUM state in options**: `RESULT enum_bad=0`.
- **MEASUREMENT/TOTAL/TOTAL_INCREASING numeric**: `RESULT numeric_bad=0`.
- **TIMESTAMP is a datetime**: `RESULT timestamp_bad=0`.
- **unit matches device_class** (canonical unit table): `RESULT unit_bad=0`.
- **state_class/device_class pair against HA `DEVICE_CLASS_STATE_CLASSES`**:
  `RESULT state_class_bad=0`; no unit on a `NON_NUMERIC_DEVICE_CLASS`:
  `RESULT unit_on_non_numeric_bad=0`.
- **translation coverage** (strings.json == en.json == sv.json, all five
  platforms): `RESULT translation_bad=0`; also by hand: all 59 sensor keys
  present in both languages.
- **entity_id format and uniqueness**: `RESULT entity_id_bad=0`,
  `dup_entity_id=0` (every entity is
  `{domain}.heat_pump_optimizer_{translation_key}`).
- **naming/ordering**: the `plan_*` prefix that "splits" the DHW and space
  families is the deliberate #1333 grouping (card-comment + `PLAN_ID_SUFFIXES`),
  not a defect; no family split is an accident.

Command: `PYTHONPATH=tests/hastub
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
tools/audit/round7/D8/matrix.py`.

## Harnesses

- `tools/audit/round7/D8/matrix.py` — the full per-entity matrix.
- `tools/audit/round7/D8/gap_series.py` — D8-01.
- `tools/audit/round7/D8/dhw_advisor_default.py` — D8-02.

## Not finished

- The "enabled-by-default vs first-hour list" comparison against the README and
  the card is only partly done: the card's four headline stats and both plan
  sensors are all enabled by default (verified), but I did not enumerate the
  README's full first-hour list against the enabled set.
- `next_optimization` is enabled-by-default, DIAGNOSTIC, TIMESTAMP and
  `available` but `native_value=None` after a solve — left unexamined as a
  possible third finding (wall-clock scheduling, likely legitimate).
