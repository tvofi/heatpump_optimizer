# Round 9, D8 seat s3 — ordering and naming (M3), enabled by default (M4), the matrix graduates (M5)

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), export `/home/claude/audit-r9-baseline`,
box B4 (cloud container, linux), `/home/claude/venv-r9/bin/python`, `PYTHONPATH=tests/hastub`.
Cells (`check_scopes.py --seat D8-s3`): steps M3+M4+M5 over binary_sensor.py, button.py, climate.py,
entity.py, sensor.py, switch.py.

Exposure: none. I did not read `docs/`, GitHub, or any earlier-round evidence under
`tools/audit/round3..round8` (the coordinator's notice arrived after the work; nothing to name).
The `tests/entities.py` checks citing earlier D8 ids were read as tree context only (collect/display_name
helpers and what the gate already pins).

## Method

`roster.py` (shared builder, not a harness) builds a real `HeatPumpOptimizerCoordinator` the way
`tests/golden.py:_capture_coordinator` does (frozen clock at `golden.START`, injected prices and
forecasts, `_build_data_dict`), or after real `_update_current_state` input cycles
(`build_honest`, `tests/entities.py:_honest_coordinator`'s shape), and drives every platform's real
`async_setup_entry` (sensor, binary_sensor, button, climate, switch, datetime): 75 entities, 74
translation keys (the climate entity takes the device name).

- M3: families defined by production symbols (mixin, class, input slot, card literal), never by name;
  contiguous runs counted in the entity_id, English-name and Swedish-name sort of the whole roster.
  A member that also belongs to a second family is transparent (a trade-off between two families is
  not counted). English/Swedish concept-token parity and key-set parity strings/en/sv.
- M4: README's disabled list and "first hour" entities against the registry default in all five
  golden topologies; a sweep of every entity slot the setup flow can write
  (`config_flow._user_sensors_fields` plus `modbus_prefill._NAMED`, the setup-time device pre-fill)
  for entities lit by the slot but left disabled; a byte-duplicate detector over enabled sensors.
- M5: `m5_matrix.py` runs the four harnesses twice each with `socket.connect` refused and counted.

## Findings

### D8-s3-01 (M3, low, hygiene) — two families split in both name sorts

`m3_families.py`: `families_split_unexplained_name_en=2`, `_name_sv=2`, `_entity_id=1`.
- accuracy (`PredictionAccuracySensor` + `DiagnoseIntervalButton`, whose press publishes onto that
  sensor): "Diagnose Last Interval" / "Prediction Accuracy", "Diagnostisera senaste intervallet" /
  "Prognosnoggrannhet" — 2 runs in each language (the button is not led by its sensor's token the
  way #1227 led the Learning buttons).
- energy meters (`_AccumulatingSensor`, the six Energy-dashboard meters), DHW members set aside:
  "Cost Total Heating (lifetime)", "Space Heating Cost/Energy (lifetime)", "Total Energy (lifetime)"
  — 3 runs en, 3 sv, 3 entity_id; the total-cost meter alone is `Cost `-led while its two siblings
  are subject-led, and Thermal Battery sorts between Space Heating and Total.
Perturbation: the button's en/sv names take the sensor's lead token → en 2→1, sv 2→1.
Null control: ecl110, tariff, card_headline, learning families read 1 run in every ordering.

### D8-s3-02 (M3, low, hygiene) — Swedish name of the Sensor-Gap Advisor says something else

`m3_translation.py`: `concept_mismatch=1` over 74 names: sv `sensor_gap_advisor` = "Sensorlucka i
valutan" ("sensor gap in the currency"), en "Sensor-Gap Advisor": the advisor role is gone and a
currency qualifier the English dropped remains. Other 17 concept tokens: 0 mismatches; key sets
strings/en/sv: 0 differences. Perturbation: sv name "Sensorlucka, rådgivare" → 0.

### D8-s3-03 (M4, low, hygiene) — Upper Floor Temperature, a byte duplicate of the indoor reading, is on by default everywhere

`m4_duplicates.py`: `duplicate_enabled_pairs=1` over 5 topologies × 3 input cycles —
`upper_floor_temperature == indoor_temperature_optimizer` in every cycle (its own docstring says so),
enabled by default on single-zone installs too, where there is no upper floor; README lists it as
"The radiator zone" with no default note. Disabling it by default on new installs needs no registry
migration (the docstring's argument is against removal, not against a default). Perturbation:
`UpperFloorTempSensor._attr_entity_registry_enabled_default=False` → 0; the any-default count stays
1 (control: the move is the default, not the value).

## Non-findings

- Setup-time inputs: 16 setup-writable entity slots swept, `lit_and_on=6`, `lit_but_off=0`
  (`m4_setup_inputs.py`); sensitivity: a static-off DHW Temperature default → 1. The Compressor
  Frequency Advisor's slot is setup-writable through the device pre-fill, but it does not light
  without measured power (options-page), so its static off is honest.
- README's disabled-by-default list (19 names) equals the production disabled set on DHW installs
  (coord_dhw, coord_all_features: 0 either way); on no-DHW installs the 7 extra off entities are the
  DHW-gated ones.
- Quick-start "first hour" entities (Prediction Accuracy, Input Problem, Learning Run System
  Identification, the card's plan_* sensors) are all enabled by default in all 5 topologies.
- Brief-named families ECL110, tariff, learning, card headline: 1 run in every ordering; PV has one member.
- strings.json and translations/en.json entity blocks are identical; no duplicate display name in en or sv.
- Matrix determinism and isolation: `nondeterministic_results=0`, `network_connects=0`.

## Harnesses

All under `tools/audit/round9/D8/s3/`, each runnable by the command in its header:
`m3_families.py`, `m3_translation.py`, `m4_setup_inputs.py`, `m4_duplicates.py`, `m5_matrix.py`
(and the builder `roster.py`). Root rule: relative (`Path("custom_components/...")`, `tests`),
so they measure the working directory; run from the export root.

## Unfinished

None of my steps. M5's graduate is written as a runner here; moving it into `tests/` (top level,
classified in a closure or on INERT) is the fixer's job.
