# Class sweep, round 11: N-step-grid

Baseline: `origin/handoff/audit-r11-register` at 28b864af (package as 92d38ecb). Class status in
`dev/audit/config/bugclasses.json`: `open`, no detector, no barrier (R9 D4-s2-05).

**Property.** Every number the integration declares on a step grid (a selector, a card input) admits its own
max and every value its backend stores as reachable, and every number it writes to an entity lies on that
entity's step.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/sweep_step_grid.py`

Four surfaces, the whole package:

| surface | how | seams |
|---|---|---|
| A config_flow selectors, `_widen_to_fit` | the finder's `D14/s1/step_grid.py` (delivered configs) | 1 site (`_widen_to_fit`, 28 widened slider defaults) |
| B services.yaml number selectors (47) | step_grid.py | 6 fields of `set_thermal_parameters` |
| C card `<input type=number\|range>` (5) | Chromium: each input rendered with a value its backend validator admits | 4 |
| D `hass.services.async_call` (8 sites) | AST: numeric write whose data does not flow from `_on_step`/`quantise_setpoint_c` | 2 |

`RESULT seams_total=13`.

- **Positive control**: re-finds both judged findings — D14-s1-01 (`_widen_to_fit`, the six
  `set_thermal_parameters` fields) and D16-s1-01 (`_command_frequency`).
- **Null control**: `--null` (a snapped number write, a turn_off, on-grid range and number inputs) reads 0;
  the selector surface's null is step_grid.py's own (options surface 0, 49 box fields with step `any`).
- **Perturbation**: `--perturb-write` removes `inputs.write_setpoint`'s `_on_step` (one line) and
  `seams_writes` moves 2 → 3; `--perturb-freq` applies the D16-s1-01 fix and it moves 2 → 1.

Runs: `run_baseline.txt`, `run--null.txt`, `run--perturb-write.txt`, `run--perturb-freq.txt` in the report
directory.

## Dispositions

### instance (12; 4 beyond the findings)

| seam | finding | probe |
|---|---|---|
| `config_flow._widen_to_fit` | D14-s1-01 | step_grid.py: 28 `SEAM widen` lines; `--perturb-widen` → 0 |
| `services.yaml` `set_thermal_parameters.{slab_thermal_mass, slab_heat_transfer, upper_floor_thermal_mass, lower_floor_thermal_mass, inter_zone_heat_transfer, window_area}` | D14-s1-01 | step_grid.py: max and example off min+k*step; `--perturb-svc` → 0 |
| `coordinator._command_frequency` | D16-s1-01 | `D16/s1/cells.py --no-gates`: clause_grid 50; sweep `--perturb-freq` → seam gone |
| card `input.wi-temp` (:12761) | **beyond** | range 16..24 step 0.5 bound to `comfort_temp_day`, stored by `apply_schedule` as any float in 5..30: a stored 21.3 renders as 21.5 |
| card `input.wi-dhw-min` (:12771) | **beyond** | max is the published `round(dhw_setpoint - 5.0, 1)` of a setpoint `apply_schedule` stores as any float: setpoint 55.3 → max 50.3, unreachable (reads 50); stored min 45.3 renders as 45.5 |
| card `input.wi-quiet-frac` (:13025) | **beyond** | range 0.6..1 step 0.05 bound to `silent_mode_power_fraction`, admitted as any float in 0..1: 0.62 renders as 0.6 |
| card `input.sp-setpoint` (:13618) | **beyond** | number 0..30 step 0.5 bound to `manual_setpoint`, admitted by `assign_entity` as any float: 21.3 is `stepMismatch` |

The four card seams are the selector-side mechanism on the card's own inputs: the backend validators
(`services._float_range`) admit any float in range, the input's grid admits a subset, so a legal stored value
is shown or submitted as its nearest grid point. Severity low (display and drag start, not a write to the pump),
as the judged D14-s1-01.

### guarded

- `config_flow._number` box fields (49 `_OPTION_FIELDS` rows, `_questionnaire_fields` heated_area): step `"any"`
  (#1679); `tests/config_flow_steps.py:7592` refuses a box field with a step.
- `inputs.write_setpoint` (with `write_setpoint_c`; reached by the pump arbiter's set-point slots,
  `coordinator._valve_write_problem`, `heat_curve._send`, `repairs`): `_on_step(value, setpoint_step(...))`
  before the call; pinned at `tests/features.py:77755`; the sweep's `--perturb-write` shows the enumerator sees
  its removal.
- `pump_arbiter._write` via `_service` (night start/end hour/minute `set_value`): `int()` of
  `quiet_windows.wall_clock()` (hours 0..23, minutes 0..59). The enumerator lists it, because nothing on the path
  reads the entity's step; it is on the grid of an integer register and would not be on one whose step is > 1.

### not applicable

- `_OPTION_FIELDS` slider rows (45) as declared: on their grid (step_grid `seams_options=0`), but no `tests/`
  script checks it — `step_grid.py --perturb-min` re-introduces 2 seams and nothing fails.
- 41 other services.yaml number selectors: max and example on the grid.
- `heat_curve.publish_ecl110_topics`: an MQTT payload, not an entity with a step.
- `_async_set_pump`, `pump_arbiter.switch_supply`, `weather.get_forecasts`: not numeric writes.
- card `input.wi-wood-liters`: its value is only its own input's value or the constant 50.

## Barrier (proposed; `barriered: false`)

One `tests/config_flow_steps.py` check over the three declaration surfaces (delivered `_OPTION_FIELDS`
configs, `_widen_to_fit` of every slider, services.yaml selectors), plus the card inputs in `tests/card.mjs`
against their bound settings' validators, and one AST rule in `tests/entities.py`: every numeric
`services.async_call` in the package takes data that flows from `_on_step`/`quantise_setpoint_c` (two sites
today: `_command_frequency`, `pump_arbiter._write`'s night keys). Cost: the AST scan and the selector walk are
sub-second; the card check rides the existing card run.
