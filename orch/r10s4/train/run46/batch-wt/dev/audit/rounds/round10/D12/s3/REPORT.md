# D12-s3 report (round 10, baseline 17f1c55fad1b)

Cells: D12.M3 (heat-pump axes, control surfaces), D12.M5 (null control), files `**`.

## Method
Drove the production set-point write `pump_arbiter:_write` for both set-point slots
(space, DHW) across the three control-surface domains the options page accepts for them
(`climate`, `number`, `input_number`, config_flow.py:1588/1663) under the two Home Assistant
unit systems, captured the service-call payload, and read the delivered value back with
production's own reader `setpoint_check._read_setpoint`.

## Findings
### D12-s3-01 (high, bug): climate set-point surface is written in degC on a Fahrenheit instance
`pump_arbiter._write` converts with `temperature_from_c(value, state_unit(state))`; a climate
state has no `unit_of_measurement`, so the conversion is the identity and `climate.set_temperature`
receives the degC number, which Home Assistant interprets in the instance unit system. The read
path (`setpoint_check._setpoint_and_unit`) already falls back to `hass.config.units.temperature_unit`;
the write path does not. Space 21 degC is delivered as 21 degF (-6.1 degC), DHW 50 degC as 50 degF (10 degC).
- Harness: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D12/s3/surface_units.py`
- RESULT misdelivered_cells=2 (of 6, degF arm); null control degC arm 0 of 6; number/input_number 0 in both.
- Perturbation `--perturb` (state_unit falls back to the instance unit for a unit-less state): 2 -> 0.
- Property/seam rule: every set-point write whose target entity has no `unit_of_measurement`
  must convert with the instance unit; seams: `grep -n "temperature_from_c(" custom_components/heatpump_optimizer/*.py`.

## Non-findings
- number / input_number surfaces deliver correctly under degC and degF (4+4 cells, same harness).
- Celsius-instance climate surface delivers correctly (null control, 2 cells).

## Unfinished
- M3: switch, ECL110 MQTT, Tuya and frequency (on/off vs modulating) surfaces not driven through a coordinator cycle.
- M3: `_bounded` reads `min`/`max`, not climate's `min_temp`/`max_temp` -- not measured.

## Exposure
none (no docs/ or GitHub read).
