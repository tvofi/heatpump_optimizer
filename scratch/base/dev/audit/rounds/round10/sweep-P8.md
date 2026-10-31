# Sweep P8 — round 10 (class sweep, D14 method steps 3–4)

Class P8 (`dev/audit/config/bugclasses.json`, status `open`, detector `null`,
barrier `null`): a currency or unit resolved by divergent precedence on
different surfaces. Findings swept: D12-s3-01 (climate set-point written in
degC on a degF instance), D14-s3-01 (plan narrative labelled in the instance
currency over feed money). Tree: `handoff/audit-r10-register` at `9355f107d`.

## Enumerator

`python3 dev/audit/rounds/round10/D14/sweep-P8/p8_enumerate.py [PKG_DIR]` —
an AST scan of the whole package, widened from both findings' `seam_rule`s
to every seam of the two surfaces the class lives on:

- **C seams:** every `resolve_currency(...)` call outside `currency.py`. That
  resolver gives the instance label; feed-denominated money must be labelled
  with `coordinator.currency` (feed first, #1657). A call is flagged unless it
  is the setup fallback, the `price_currency` guard, or an options-dialog field.
- **T seams:** every outbound temperature write: `async_call` `set_temperature`/`set_value`
  and `_write_setpoint`. A seam is flagged unless its value is converted
  with `temperature_from_c` using the `_setpoint_and_unit` unit, or was
  converted upstream. `_setpoint_and_unit` is the read rule that falls back to
  `hass.config.units.temperature_unit`.

Base: `RESULT flagged=4 seams=15` (`D14/sweep-P8/base.out`).

| control | result | evidence |
|---|---|---|
| positive (base) | flags `coordinator.py:10456 _narrative_view` (D14-s3-01) and `pump_arbiter.py:845 _write` (D12-s3-01), so both findings are re-found | `base.out` |
| positive (pre-fix `82667c41a^`) | flagged=7, including `_narrative_view`, `_write` and the three config-flow labels that #1657 later moved behind the guard | `prefix.out` |
| null (clean fixture: write via `_setpoint_and_unit`, narrative via `self.currency`) | flagged=0 | `null.out` |
| perturbation (one line: `sensor.py:475` `coordinator.currency` → `resolve_currency(coordinator.hass)`) | flagged 4 → 5, new `sensor.py:475 FLAG` | `perturb.out` |

## Dispositions (all 15 seams)

| seam | disposition |
|---|---|
| `coordinator.py:10456 _narrative_view` | **instance**: finding D14-s3-01; probe `D14/s3/p8_replay_currency.py` (1 of 14) |
| `pump_arbiter.py:845 _write` | **instance**: finding D12-s3-01; probe `D12/s3/surface_units.py` (2 of 6, degF) |
| `coordinator.py:7299 _command_valve_target` (climate) | **instance, beyond the findings**: a 45 degC valve target is written raw to `climate.set_temperature`. On a degF instance it reads back as 7.2 degC |
| `coordinator.py:7306 _command_valve_target` (number/input_number) | **instance, beyond the findings**: the value is written raw to a degF number entity and reads back as 7.2 degC |
| `coordinator.py:10730 _command_frequency` | not applicable: Hz, not a temperature |
| `repairs.py:53 async_step_confirm` | guarded: `value` is computed in `setpoint_check._dhw` via `temperature_from_c(floor, unit)` with the `_setpoint_and_unit` unit |
| `coordinator.py:1979, 1992 _audit_price_units` | not applicable: this is the guard, the `price_currency_mismatch` repair comparing feed and instance |
| `coordinator.py:2596 __init__` | not applicable: the canonical resolver, `_feed_currency(...) or resolve_currency(hass)` |
| `config_flow.py:553 _money`, `3736/3737 async_step_grid`, `3777/3795/3796 async_step_grid_fees` | guarded: the options dialog is labelled in the instance currency by #1657's decision, and the `price_currency_mismatch` repair (`coordinator._audit_price_units`) names any disagreement |

The scan also covers these seams, which the AST rule does not count. All are guarded or not applicable:

- `sensor.py`: 12 `coordinator.currency` label sites. Guarded, because they share the one feed-first source.
- The card's `currency()` (`www/heatpump-optimizer-card.js:5567`). Guarded, because it prefers the integration's published `currency` attribute.
- `pump_arbiter._bounded`/`_space_target` reads of `min`/`max`. Not applicable: a climate state has no `min`/`max` attribute, so it is not clamped, and a number entity declares its unit.
- `inputs.read_flow_kg_s`. Not applicable: flow units do not depend on the instance.

## Probe for the new seam

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P8/p8_valve_probe.py`
runs the real method with a fake self on `FakeHass`. It reads the captured payload back through
`setpoint_check._read_setpoint`.

- degF arm: `RESULT misdelivered=2`
- null degC arm: `0`
- `--perturb` (convert with `temperature_from_c` and the `_setpoint_and_unit` unit): `0`

Outputs: `valve.out`, `valve.perturb.out`.

## Count and barrier

Of the 4 instances, 2 are the findings' own sites and 2 lie beyond them, on one
symbol: the mixing-valve smart-write. That second temperature-write path bypasses the
`_write_setpoint` conversion entirely, so a fix scoped to `pump_arbiter._write`
alone leaves the class open. Proposed barrier: route
`_command_valve_target` through one write helper that resolves the unit like
`_setpoint_and_unit`. Then run `p8_enumerate.py` as a `tests/` structural check
(sub-second, AST only), plus the D14-s3-01 replay currency invariant with its
reintroduce arm. Class status stays `open`, with `barriered: false`.
