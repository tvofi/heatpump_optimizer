# Round 11 class sweep: P1 (non-finite, malformed or out-of-domain value at an input boundary)

Baseline: `handoff/audit-r11-register` at 28b864af6d. Class status in `dev/audit/config/bugclasses.json`: `barriered` (detector `tests/finite_boundary.py`, barrier `QuarantiningStore._sanitize`). That barrier covers store loads. It does not cover option reads or live-entity parsers, and those are the families where this sweep's instances sit.

## Enumerator (D14 step 3)

`python3 dev/audit/rounds/round11/D14/sweep-P1/enumerate_p1.py . --controls`

Families are the union of the seven findings' `seam_rule`s, widened from their own files to the whole package:
`parser` (every `_parse*`/`parse_*`), `optfloat` (bare `float(config|candidate|options.get(`), `tdelta` (`timedelta(<unit>=<name>)`), `poison` (`store._poisoned` without an isfinite test), `window` (`inputs.plausible_c`), `tablerow` (thermal_model option tables).

- Seams returned: 51 (21 parser, 10 optfloat, 16 tdelta, 3 tablerow, 1 window).
- Positive control: it re-finds 6 of 7 finding sites at this tree. The seventh, `store._poisoned` (D1-s2-01), is already guarded here: `return not math.isfinite(value) or abs(value) >= ABSURD`. The finder's harness `nan_boundary.py --stores accuracy,dhw_profile` measures `leaves_reaching_live=0` here. In a planted copy with that guard reverted, the `poison` family re-finds it (52 seams).
- Null control: a clean fixture with one `finite_float(config.get(...))` reader gives 0 seams.
- Perturbation: adding the one line `return float(config.get('x'))` to that fixture gives 1 seam.

Blind spot: the `optfloat` family is a line grep. It misses an option read through a local alias, and it cannot see `.attributes` reads. The P1 barrier text already names that second gap.

## Dispositions (D14 step 4)

### Instances beyond the findings (4)

| file | symbol | probe | measured |
|---|---|---|---|
| quiet_windows.py | measured_ceiling_kw line 388 (freq min Hz) | `probe_option_floats.py` | stored `"abc"` raises ValueError; null 0 of 3 |
| quiet_windows.py | measured_ceiling_kw line 390 (freq max Hz) | same | raises ValueError |
| topology.py | _slot_extras (`manual_setpoint`) | same | raises ValueError |
| early_cutoff.py | arm, `timedelta(minutes=cfg.optimization_interval)` | `probe_interval_domain.py` | `EntryConfig.from_mapping` refuses `abc`/`nan` but passes 1e12, 1e10, -5 and 0. 1e12 and 1e10 overflow; -5 and 0 put the cycle end at or before now: 4 of 4. Null (15/30/60): 0 of 3 |

Probes run with `PYTHONPATH=tests/hastub:custom_components`. Reach is the same as D1-s2-05: the option selectors bound new entries, so the bad value arrives from an earlier-version entry or a hand-edited entry. Severity is therefore low. `probe_interval_domain.py` restates line 172 of `arm` inline. It does not drive `arm` through its wiring.

### Finding sites (beyond_finding false)

These are `thermal_model._tabled_values`/`_flow_curve_values`/`from_config` and `comfort_band.effective` (D1-s2-05), `boost._restore_settle` (D1-s2-06), `inputs.parse_bool` (D1-s3-01), `coordinator._parse_ecl110_state` (D1-s3-02), `open_meteo._parse_block` (D1-s3-03) and `inputs.plausible_c` via `InputReader.read` (D1-s2-51). `store._poisoned` (D1-s2-01) is guarded at this tree, as described above.

### Guarded

- `config_flow._effective`: a form-validation path. The selector types the value, and a `float()` failure there is a form error, not a live input.
- `price_model.pull_prices` line 858 and `wood_fuel.wood_fuel_ready` lines 127-128: each is wrapped in `try/except (TypeError, ValueError)`, and `wood_fuel_ready` also range-checks its result.
- `wood_fuel.lighting_window`: its argument comes from `finite_float(...)` with a default, bounded below by `max(0.0, ...)`. A finite option of 1e12 would still overflow here. That is the same reach as the `early_cutoff` instance, and it is the fixer's to cover in the same coercion fix.
- Parser family other than the finding sites (`away._parse_return_time`, `boost._parse_until`, the `dhw_schedule` and `grid_fee` parsers, `manual_plan._parse_dt`/`parse_channel`, `quiet_windows._parse_spec_pair`, `debugger._parsed`, `store._parses`): these parse service or option text into windows and instants, and each returns None or raises a handled validation error. No probe here moved them, so this is a disposition by reading, not by a probe.

### Not applicable (tdelta seams whose argument is internal)

- Loop index or offset: `coordinator._fabricated_forecast`, `quiet_windows.next_gchv_window`, `optimizer.reference_day`.
- Default parameter: `coordinator._solar_forecast_view`.
- Constant lead tables: `coordinator._file_lead_predictions` and `_file_dhw_lead_predictions`.
- Module constants: `pump_arbiter._leased` (LEASE_MINUTES), `tariff._window_slot` (floored by `max(1, int(...))`).
- Solver step `dt_hours`, drawn from the optimizer config: the remaining `optimizer`, `rooms`, `silent_mode`, `plan_slots` and `quiet_windows.step_actions` seams.

## Recommendation for the class

Route optimization_interval and the raw option `float()` reads through one coercer at `EntryConfig`/option load, with a domain window and not only a finiteness check. Add an `optfloat` arm to `tests/finite_boundary.py` so the barrier covers option reads as well as store loads.
