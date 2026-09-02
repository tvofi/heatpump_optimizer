# D8 — Sensor verification and ordering (round 2)

- baseline: c398fc84eec25fc44b60d74aae05b9a2da205884
- export: /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline
- harness: `tools/audit/round2/D8/matrix.py` (one command in its header)
- machine: MacBookAir10,1 (Apple M1, 8 GB), numpy on OpenBLAS, thread-pinned; every
  number below is a count and is contention-immune (`load1` 2.2–6.0 during the
  runs, `thread_factor` 1.000).
- exposure: none (no `docs/` read; `README.md` read for the first-hour list, as
  the D8 brief requires).

## Method

The matrix is 5 topologies × 17 feature toggles = 85 cells, every cell run for
two cycles with changed inputs, every entity of every platform constructed
through the real `async_setup_entry` against a real
`HeatPumpOptimizerCoordinator` (not `FakeCoordinator`):

- topologies: `tests/golden.py:coordinator_scenarios()` — `coord_minimal`,
  `coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`;
- features (config + entity states overlaid on the topology): `none`,
  `weather_only` (no indoor/outdoor thermometer), `dhw`, `two_zone`,
  `valve_storage`, `two_tank`, `coil`, `wood`, `ecl110`, `pv`,
  `capacity_tariff`, `grid_fee`, `tuya` (the four pump-signal entities),
  `away`, `measured_power`, `probes` (tank, buffer, lower-floor, floor-return
  and irradiance sensors), `frequency`;
- per cycle, as `_capture_coordinator` does: golden-shaped prices and forecasts
  injected, the clock frozen (tz-aware, 2026-01-15T00:00Z then +30 min),
  `_update_current_state()` reads the states; then — beyond
  `_capture_coordinator` — `async_run_optimization()` solves (inline through
  `FakeHass.async_add_executor_job`) and `_build_data_dict()` publishes. Cycle 2
  moves the indoor/outdoor/tank/power/frequency states, the price level (+0.2)
  and the forecast (−2 K). All 85 cells solve `optimal` in both cycles.
- per (cell, cycle, entity): state, availability, attributes, device class,
  state class, unit, entity category, enabled-by-default, translation key,
  entity id, icon. 11 050 snapshots.

Checks, one `RESULT` line each (expected values in the harness header):

| check | definition |
|---|---|
| `unknown_where_data_exists` | available, state `None`, every mapped source key present and non-empty in the payload (map: `matrix.py:SOURCES`, written from each `native_value`) |
| `type_violations` | numeric where MEASUREMENT/TOTAL/TOTAL_INCREASING, tz-aware datetime where TIMESTAMP, listed option where `_attr_options` |
| `metadata_violations` | device class × state class per `DEVICE_CLASS_STATE_CLASSES`; unit per device class; MONETARY unit == `coordinator.currency` |
| `unserialisable_attributes` / `numpy_attribute_sites` | orjson's rules walked over every attribute dict: numpy scalars/arrays counted per value and per (entity, attribute, leaf) site |
| `nonfinite_attributes` | NaN/inf reaching an attribute (orjson writes `null`) |
| `stale_entities` | an entity constructed on cycle 1 reads differently from a fresh entity on the cycle-2 payload |
| `follows_payload_mismatch` | 41 direct numeric readers: state within 0.051 of the source key on cycle 2 |
| `default_temperature_leaks` | a temperature (or a number derived from one) published on an *available* entity whose `reading_ok` flag for that field is False — a `ThermalState` constructor default or a seed, never a reading |
| `outdoor_default_published` | Outdoor Temperature (Optimizer) available while no outdoor entity read OK |
| `schedule_truncated` | `optimization_schedule.schedule` shorter than `space_plan.forecast` |
| `family_splits_*` | for ten hand-listed families, contiguous runs − 1 in the sorted entity-id / English-name / Swedish-name order |
| `first_hour_disabled` | README quick-start + card entities that are disabled by default |
| `enabled_unavailable_minimal` | enabled-by-default entities unavailable in `coord_minimal+none` after a solve |

Two full runs on 2026-09-02 produced identical counts, identical per-entity
values and identical violation lists.

## Findings

### D8-01 — `ThermalState` constructor defaults are published as temperatures through five ungated paths (severity: high, class: bug)

**Claim.** With no thermometer behind a field, the integration publishes the
`ThermalState()` constructor default (55.0 °C tank, 40.0 °C buffer, 22.0 °C
slab seed, 21.0 °C room, 5.0 °C outdoor) — or a number derived from it — as an
available state or attribute, on paths that `_MeasuredTemperatureMixin` does not
cover.

**Evidence.** `RESULT default_temperature_leaks=1132` over 80 of 85 cells (min
10, max 24 per cell; the five `probes` cells, where every field has a reading,
count 0), plus `RESULT outdoor_default_published=10` (the five `weather_only`
cells × 2 cycles). Sites, with occurrences over the 170 (cell, cycle) pairs:

| site | occurrences | what is published |
|---|---|---|
| `climate.heat_pump_optimizer` attr `dhw_temperature` | 160 | 55.0 in every cell without a tank sensor — including `coord_minimal`, where hot water is not configured at all |
| `climate.heat_pump_optimizer` attr `slab_temperature` | 160 | the one-off `room + 1.0` seed (22.4) |
| `climate.heat_pump_optimizer` attr `lower_floor_temperature` | 160 | the indoor reading under a downstairs label (the stand-in the sensor platform refuses to publish) |
| `sensor…thermal_battery_charge` attrs `components.slab` / `components.buffer_tank` | 160 + 160 | 22.4 / 40.0; the *state* (SOC %) is computed over these components too |
| `sensor…thermal_battery_charge` attr `components.dhw_tank` | 76 | 55.0 |
| `sensor…mixed_hot_water` **state** and attr `tank_temperature` | 76 + 76 | 300 L of 40 °C water and 37.5 shower minutes from a 55.0 °C tank nobody measures (38 cells: every DHW cell without a tank sensor); README: "Unavailable without mixed-water data" |
| `sensor…thermal_battery_charge` attr `components.lower_floor` | 64 | the room temperature |
| `sensor…indoor_temperature_optimizer` **state**, `climate` `current_temperature` | 10 + 10 | 21.0 in the `weather_only` cells |
| `sensor…outdoor_temperature_optimizer` **state** | 10 | 5.0 in the `weather_only` cells while the plan is solved on a −5 °C forecast; `Estimated COP` follows it: 3.32 at the 5.0 default vs 2.62 / 2.19 at the real −3 / −8 °C |

The DHW Temperature, Buffer, Slab, Lower Floor and Floor Return *sensors* are
correctly unavailable in the same cells (`_MeasuredTemperatureMixin`); the same
numbers leave through the climate entity, the thermal-battery view, Mixed Hot
Water, and the un-gated Indoor/Outdoor sensors.

**Instrumented symbol.** `heatpump_optimizer.thermal_model:ThermalState`
(defaults), read through
`heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict`
(`_thermal_view`, `_dhw_mixed_water`, `_battery_view`) and published by
`heatpump_optimizer.climate:HeatPumpOptimizerClimate.extra_state_attributes`,
`heatpump_optimizer.sensor:MixedHotWaterSensor`, `ThermalBatterySensor`,
`IndoorTempSensor`, `OutdoorTempSensor`.

**Perturbation.** (a) Config: add the `probes` sensors — the count is 0 in all
five `probes` cells (to_zero). (b) One-line production edit:
`ThermalState.dhw_temperature: float = 50.0` — Mixed Hot Water in
`coord_dhw+none` moves 300.0 → 266.7 L, shower minutes 37.5 → 33.3, the climate
`dhw_temperature` attribute 55.0 → 50.0 (down; observed with the scratch
procedure described under "Harnesses").

**Metric definition.** Count of (cell, cycle, entity, attribute-or-state)
publications of a temperature, or a value derived from one, on an available
entity whose `reading_ok[field]` is False.

**Leave-one-out.** 85 cells, min 0, max 24; dropping the most favourable cell
(a 24) leaves 1108; dropping a `probes` cell (0) leaves 1132.

**Severity.** `high`: a wrong published value, on the climate entity every
install has and on two states (Mixed Hot Water, Outdoor Temperature) that read
as measurements with `VOLUME_STORAGE`/`TEMPERATURE` device classes. Not
`critical`: no money or comfort is decided on these publications (the solve
uses the forecast and the plan, not the published outdoor state).

**Proposed fix scope.** Gate the derived publications on the same
`reading_ok` map the sensors already use: Mixed Hot Water unavailable without
a tank reading; climate attributes `None` where the field has no reading;
thermal-battery components carry `measured: false` or are dropped; Indoor /
Outdoor sensors gated on their input like the other temperatures (the outdoor
one could fall back to the forecast's first step, which is what the plan uses).
Files: `custom_components/heatpump_optimizer/climate.py`, `sensor.py`
(MixedHotWaterSensor, ThermalBatterySensor, IndoorTempSensor,
OutdoorTempSensor), `coordinator.py` (`_dhw_mixed_water`, `_battery_view`).
Golden drift: `coord_*` fixtures only if the coordinator changes what it
publishes (entity-side gating alone drifts nothing).

### D8-02 — numpy scalars reach entity attributes and one state at three sites (severity: low, class: hygiene)

**Claim.** `_build_data_dict` copies `OptimizationResult` scalars and the
solar-gain trajectory into the payload without `_plain_types`, so `np.float64`
values reach `extra_state_attributes` (and, in valve-storage topologies, the
Predicted Savings state), against the integration's own stated policy
("Numpy scalars are converted to plain Python types because these values end
up in entity attributes, which Home Assistant must serialize", coordinator.py,
applied to `predictive_info` only).

**Evidence.** `RESULT numpy_attribute_sites=3`, `RESULT unserialisable_attributes=3630`
(per value), `RESULT numpy_state=30`:

| site | cells | origin |
|---|---|---|
| `sensor…optimization_schedule` attr `schedule[i].solar_gain` | 85 / 85 (every non-zero entry: 3570 values) | `optimizer.py:1534` `solar_gain_trajectory=[compute_solar_gain(sr) for sr in h.solar_radiation]` — `sr` is an ndarray element; `compute_solar_gain` returns a Python 0.0 only for `sr <= 0` |
| `sensor…savings_percentage` attr `deferred_energy_cost`, `climate` attr `predicted_savings`, `sensor…predicted_savings` **state** | 15 / 85 (`valve_storage`, `two_tank`, `coil` on every topology) | `result.deferred_energy_cost` / `predicted_savings` are numpy in the buffer-store solve path; `round(np.float64, 2)` stays `np.float64` |
| `sensor…heat_pump_action` attr `solar_gain_kw` | daylight only (the matrix cycles are at 00:00/00:30; verified at 12:00 with the scratch procedure) | `optimizer.py:5697` `round(result.solar_gain_trajectory[i], 3)` |

**Instrumented symbol.**
`heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict`
(the `schedule` comprehension and the `result` block), fed by
`heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize`.

**Perturbation.** Wrap the `schedule` list and the `result` scalars in
`_plain_types(...)` in `_build_data_dict` (or `.tolist()`/`float()` at the two
optimizer sites): `numpy_attribute_sites` → 0, `numpy_state` → 0 (to_zero).

**Metric definition.** Distinct (entity, attribute root, leaf) sites at which
an `np.generic`/`np.ndarray` is found in `extra_state_attributes`, over all
snapshots; plus the count of snapshots whose state is a numpy scalar.

**Severity.** `low`: orjson does not serialise float subclasses natively and
hands them to the `default` hook; Home Assistant's `json_encoder_default`
converts float subclasses, so current cores write the state (at a callback per
value on a 24-entry list every cycle); an `np.int64` on the same path would not
be converted. The judge should confirm the installed core's hook before raising
this. Class `hygiene`: a stated policy bypassed at three sites.

**Proposed fix scope.** `coordinator.py:_build_data_dict` (two `_plain_types`
wraps) or `optimizer.py` lines 1534 and 5697. No golden drift expected
(`golden.py:r()` rounds through `float`; verify with `GOLDEN_MODE=drift`).

### D8-03 — the two legacy schedule sensors describe 6 of the plan's 24 hours (severity: low, class: hygiene)

**Claim.** `Optimization Schedule` and `DHW Heating Schedule` are built from
`result.*[:24]` — 24 steps at the 15-minute step is 6 hours — while the README
says "The whole 24 h schedule, in attributes" and the plan sensors carry 96
steps; the states say "24 steps" and "*N* heating periods" where *N* counts
15-minute steps inside those 6 hours (and "1 heating periods", "1 slots planned"
are not grammatical).

**Evidence.** `RESULT schedule_truncated=170` — every solved (cell, cycle):
`len(schedule)=24` against `len(space_plan.forecast)=96` in all 85 cells.
`Optimization Schedule` is one of the six entities whose source moved between
cycles while the state did not (`"24 steps"` both cycles, 85/85).

**Instrumented symbol.**
`heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict`
(the `[:24]`/`[1:25]` slices), `heatpump_optimizer.sensor:ScheduleSensor`,
`DHWScheduleSensor`.

**Perturbation.** Replace the `[:24]` slices with the horizon length (or read
the plan views): `schedule_truncated` → 0 (to_zero). Alternatively fix the
README row; the metric then stays and the claim vanishes.

**Metric definition.** Count of (cell, cycle) in which
`len(optimization_schedule.attrs.schedule) < len(space_plan.forecast)`.

**Severity.** `low`: the plan sensors carry the full horizon and the card reads
those; the legacy sensors are documented as such in code, not in the README.

**Proposed fix scope.** `coordinator.py:_build_data_dict` slices, or
`README.md` (Optimization Schedule / DHW Heating Schedule rows), and the two
state strings' grammar in `sensor.py`. Golden drift: every `coord_*` fixture's
`schedule`/`dhw_schedule` length if the slice changes.

### D8-04 — alphabetical order splits the hot-water family (and four others) (severity: low, class: hygiene)

**Claim.** Sorting the 55 sensors by entity id or by English name breaks the
DHW family into three runs because three members are named `hot_water_*` /
`mixed_hot_water` while six are `dhw_*`; the tariff, learning, card-headline,
lifetime and two-zone families are split as well.

**Evidence.** `RESULT family_splits_entity_id=15`, `family_splits_name_en=15`,
`family_splits_name_sv=16` (per family, id order: dhw 2, tariff 2, learning 2,
accuracy 1, card_headline 3, lifetime 2, two_zone 3; ecl110, pv and
thermal_battery 0). Sorted id order around the DHW family:
`dhw_heating_cost … dhw_temperature | ecl110_* | … | hot_water_cost hot_water_energy
| … | mixed_hot_water`. In Swedish the DHW family is split the same way
(`Varmvatten…` vs `Blandat varmvatten`, `Schema för varmvatten`), and the
lifetime accumulators split three ways (`Total …`, `Uppvärmnings…`,
`Varmvatten…`).

**Instrumented symbol.** `heatpump_optimizer.sensor:async_setup_entry` (the
roster and each entity's `translation_key`), `strings.json`,
`translations/en.json`, `translations/sv.json`.

**Perturbation.** Rename the three keys into the family (`dhw_energy`,
`dhw_cost_lifetime`, `dhw_mixed_water`) with matching translations: dhw splits
2 → 0 and the totals 15 → 13 / 13 (down). The suggested object id follows the
translation key, so this is a naming release, not a patch.

**Metric definition.** For each family (translation-key sets in
`matrix.py:FAMILIES`), the number of contiguous runs the family forms in the
sorted order, minus one; summed over families.

**Severity.** `low`, class `hygiene`: cosmetic in the entity list; no value is
wrong. The brief asks for the count; the judge may fold it into a naming
release or void it.

**Proposed fix scope.** `sensor.py` translation keys + `strings.json` +
`translations/*.json` (+ README tables). The card's id-suffix contract covers
the headline stats only and is unaffected.

## Non-findings (checked and held)

| claim | command | value |
|---|---|---|
| No entity is unknown where its data exists (60 entities mapped to source keys) | `PYTHONPATH=tests/hastub python tools/audit/round2/D8/matrix.py` | `unknown_where_data_exists=0` over 11 050 snapshots |
| Every MEASUREMENT/TOTAL/TOTAL_INCREASING state is numeric and finite; both TIMESTAMP sensors are tz-aware; no ENUM sensors | same | `type_violations=0` |
| Device class × state class pairs and units are consistent; MONETARY units equal `coordinator.currency` (SEK) | same | `metadata_violations=0` |
| No NaN/inf reaches any attribute on any platform (sensor scrub + the unscrubbed binary_sensor/climate/switch paths) | same | `nonfinite_attributes=0`, `set_attributes=0`, `nonstr_keys=0` |
| No entity caches state: entities built on cycle 1 read exactly what fresh entities read on cycle 2 | same | `stale_entities=0` |
| 41 direct numeric readers follow their payload key within rounding on cycle 2 | same | `follows_payload_mismatch=0` |
| No entity raises from `available`, `native_value`/`is_on` or `extra_state_attributes` in any cell | same | `exceptions=0` |
| Every non-climate entity pre-assigns `<platform>.heat_pump_optimizer_<translation_key>`; unique ids are unique; every entity has an icon | same | `bad_entity_ids=0`, `duplicate_unique_ids=0`, `no_icon=0` |
| `strings.json`, `en.json`, `sv.json` carry identical entity key sets, equal to the entity roster; every Swedish name differs from the English | same | `translation_key_mismatch=0`, `en_differs_from_strings=0`, `sv_untranslated=0` |
| The disabled-by-default set is the six niche sensors the README lists; nothing the quick start or the card needs is disabled | same | `disabled_by_default=6`, `first_hour_disabled=0` |
| Feature gating works as documented: MonthlyPeak/PVSurplus/DHW/measured/frequency/contract entities are unavailable without their feature and available with it | same (per-cell availability in `matrix_results.json`) | `coord_minimal+none` 18 enabled-but-unavailable; `coord_all_features+probes` 0 |
| Every cell solves, both cycles | same | 85/85 `optimal` |

Observations that are not findings (no wrong value, or transient):

- `enabled_unavailable_minimal=18`: on the minimal install 18 enabled-by-default
  sensors sit unavailable (all DHW, two-zone, measured-power, tariff and PV
  entities). The README states this design ("the entity exists but reports
  itself unavailable, so nothing appears and disappears"); it is the design
  question the brief's item 4 raises, not a defect.
- `enabled_none_minimal=1`: `Prediction Accuracy` is available with state
  Unknown until the first accuracy pair lands (one interval); the
  `_WaitsForEvidenceMixin` pattern is not applied here. Transient.
- `Valve Target Recommendation` (disabled by default) is available with state
  Unknown in the 70 cells without a mixing valve; the other five niche sensors
  gate availability instead. Cosmetic once enabled without a valve.
- `unitless_numeric=5` sensors (Estimated COP, Observed COP, Comfort Weight,
  Optimization Score, Compressor Starts) carry a state class and no unit —
  allowed by Home Assistant.
- Entities whose source moved between cycles while the state string did not
  (`optimization_schedule` 85, `predictive_optimization_insight` 85,
  `dhw_heating_plan` 62, `space_heating_plan` 55, `dhw_heating_schedule` 43,
  `plan_narrative` 32 cells): string summaries; their attributes moved. Checked
  by hand, not a staleness.

Harness gaps named (leads that vanished):

- The base-class non-finite scrub means no sensor can publish NaN/inf; the
  matrix therefore checks the *unscrubbed* platforms too, and found none. The
  `peak_threshold_kw=+inf` attribute on Monthly Peak Power is scrubbed to
  `None`, as designed.
- `NextOptimizationSensor` reads `_next_optimization`, which only
  `_async_update_data` (the Tibber/network path) sets; the harness mirrors that
  assignment after each solve. Not a finding.
- With the stub's naive clock `last_optimization` would be naive; the harness
  freezes a tz-aware clock, as Home Assistant's `dt_util.now()` is. Not a
  finding.
- orjson is not installed in the venv; serialisability is a walk applying its
  rules (numpy, NaN/inf, key types) rather than a real `orjson.dumps`.

## Harnesses

- `tools/audit/round2/D8/matrix.py` — the matrix; writes
  `matrix_results.json` (per-cell availability/values, violation lists) next to
  itself; `matrix_full.out` is the first full run's stdout.
- Scratch procedures (not committed; two dozen lines each on top of
  `matrix.py`'s `cell_config`/`_cycle`/`collect`): the D8-01 perturbation
  rebuilt `ThermalState` with `dhw_temperature=50.0` via
  `dataclasses.make_dataclass`, rebound it in `heatpump_optimizer.coordinator`,
  ran the `coord_dhw+none` cell unsolved and read Mixed Hot Water
  (300.0 → 266.7 L); the D8-02 daylight site set `matrix.START_AWARE += 12 h`,
  ran `coord_minimal+none` solved and walked the Heat Pump Action attributes
  (`solar_gain_kw` is `np.float64`, value 0.98).

## Not finished

- Attributes were checked for type and finiteness, not for meaning; a
  per-attribute source map (as `SOURCES` does for states) would let the
  "follows the payload" check cover attributes.
- The two cycles are 30 minutes apart at midnight; learners that need hours
  (COP baseline, draw statistics, contract settlement) stay at their
  first-sample gates, so `Observed COP`, `Contract Comparison` and `DHW Heavy
  Day Demand` were verified only as "unavailable with `waiting_for` set", not
  with data.
- Ordering families are hand-listed (`FAMILIES`); a different grouping gives a
  different split count.
