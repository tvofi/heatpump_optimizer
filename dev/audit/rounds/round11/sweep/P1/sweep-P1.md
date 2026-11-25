# Round 11 class sweep: P1 (D14 steps 3–4)

Class P1 (`dev/audit/config/bugclasses.json`): a non-finite, malformed or
out-of-domain value crosses an input boundary (persisted store, live entity,
external feed, service call) with no guard. Ledger status: `barriered`. The
barrier is `QuarantiningStore._sanitize` plus `tests/finite_boundary.py` Arm 4,
and it covers non-finite, magnitude and naive store leaves only. None of the seven
judged findings is a shape that barrier refuses.

All commands below run from the register worktree (`origin/handoff/audit-r11-register`,
28b864af).

## Judged findings, one shape each

| finding | shape (family) | site | state at register head |
|---|---|---|---|
| D1-s2-01 (low) | store leaf predicate misses NaN (`store-leaf`) | `store._poisoned` | guarded: the float branch calls `math.isfinite`, and `nan_boundary.py` prints 0 |
| D1-s2-05 (low) | wrong-typed option read through bare `float()` (`opt-float`) | `thermal_model.ThermalParameters.from_config`, `_flow_curve_values`, `comfort_band.effective` | live: `config_fuzz.py --versions 1` build_fail |
| D1-s2-06 (low) | stored number into `timedelta` with no finite cap (`dyn-timedelta`) | `boost._restore_settle` | live: restarts_raising=8 (`0 <= hours < math.inf` lets 1e12 through) |
| D1-s2-51 (medium) | plausibility window checked on one side (`window`) | `inputs.plausible_c` | guarded: two-sided, and `plausible_upper.py` prints 0 |
| D1-s3-01 (medium) | flag from `float(x) != 0` with no finiteness test (`num-flag`) | `inputs.parse_bool` | live: 10 non-finite flags read True |
| D1-s3-02 (low) | `isinstance(x, (int, float))` admits a bool (`bool-number`) | `coordinator._parse_ecl110_state` | live |
| D1-s3-03 (low) | feed instant parsed with no range bound (`feed-instant`) | `open_meteo._parse_block` → `mean_over` | live: 3 failed solves |

## Enumerator and controls

`python3 dev/audit/rounds/round11/D14/sweep-P1/p1_seams.py` parses every module of
the package. For each family it lists every function carrying the judged shape (a
seam) and flags the seams where the guard that finding names is absent. Each
family's seam and flag rules are in the script's docstring. Output from the
register head: `seams_total=74`, `seams_flagged=47` (the full listing is in
`D14/sweep-P1/p1_seams.out`).

- **Positive control.** `--plant` copies the package and puts the two sites the
  register head already guards back in their pre-fix shape: `_poisoned` loses
  `isfinite`, and `plausible_c` becomes one-sided. Result:
  `judged_sites_flagged=7 of 7`. On the head itself, all 7 are listed and 5 are
  flagged; the 2 unflagged are the fixed sites.
- **Null control.** `--null` runs on a clean fixture with one guarded twin per
  family: `seams_flagged=0`.
- **Perturbation.** `--perturb <family>` makes a one-line edit to that fixture that
  puts the shape back. Each of the 7 families gives `seams_flagged=1`.

Probes for the seams beyond the judged sites:
`PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/D14/sweep-P1/p1_probes.py`
(output in `D14/sweep-P1/p1_probes.out`). Its `config-effective` arm has a null
(well-typed stored options raise 0 times) and a perturbation (`--perturb
config-effective`, the guarded twin, takes the count from 20 to 0).

## Dispositions (all 74 seams)

**store-leaf (1)**
| seam | disposition |
|---|---|
| `store._poisoned` | judged site (D1-s2-01); guarded at the register head |

**num-flag (1)**
| seam | disposition |
|---|---|
| `inputs.parse_bool` | **instance**, judged site (D1-s3-01) |

**dyn-timedelta (1)**
| seam | disposition |
|---|---|
| `boost._restore_settle` | **instance**, judged site (D1-s2-06) |

**opt-float (12)**
| seam | disposition |
|---|---|
| `thermal_model.ThermalParameters.from_config`, `thermal_model._flow_curve_values`, `comfort_band.effective` | **instance**, judged sites (D1-s2-05) |
| `config_flow._effective` | **instance, beyond the finding.** `_power_errors` and `_partload_errors` raise on a wrong-typed stored heat-pump power or derate option, so the options page fails instead of showing a form error: 20 of 20 raise; null 0; perturbation 0 |
| `topology.describe_setup` | **instance, beyond the finding.** A wrong-typed stored `wood_tank_volume` raises (3 of 3). This read is reached from the coordinator (`describe_setup`, every sensor publish) and from the config flow |
| `topology._slot_extras` | **instance, beyond the finding.** A wrong-typed stored `mixing_valve_target` raises (3 of 3) |
| `quiet_windows.measured_ceiling_kw` | **instance, beyond the finding.** A wrong-typed stored compressor min/max Hz raises (3 of 3). Its caller, `silent_cap_kw`, guards only its own fraction read, not this call |
| `quiet_windows.silent_cap_kw` | guarded: its own `float(config.get(...))` is inside `try/except (TypeError, ValueError)` |
| `grid_fee.GridFeeSchedule.from_config`, `price_model.pull_prices`, `wood_fuel.wood_fuel_ready`, `wood_fuel._wood_override_fuel` | guarded: each read is inside `try/except (TypeError, ValueError)` |

The four beyond-finding opt-float instances share D1-s2-05's root:
`async_migrate_entry` (`__init__.py`) stamps the version and never coerces an
option's type. They need the same population D1-s2-05 needs (a wrong-typed option
in an older entry), so they are low severity like the finding.

**window (5)**
| seam | disposition |
|---|---|
| `inputs.plausible_c` | judged site (D1-s2-51); guarded at the register head (`window[0] <= value_c <= window[1]`) |
| `open_meteo._parse_block` | guarded: `value < 0.0 or value > max_value`, after `math.isfinite` |
| `grid_fee.spec_problem` | guarded: `rule.rate < 0.0` (line 245) and `rule.rate > fee_bound(currency)` (line 248). The rule did not credit these because the subject is an attribute |
| `grid_fee.fee_bound` | not applicable: it computes the ceiling and compares nothing |
| `slab_seed.judge` | not applicable: `ISSUE_FLOOR_RETURN_IMPLAUSIBLE` is a repair-issue id, not a window |

**feed-instant (21)**
| seam | disposition |
|---|---|
| `open_meteo._parse_block` | **instance**, judged site (D1-s3-03) |
| `price_model._raw_start`, `price_model._entries_by_day`, `price_model._noon` | not applicable to the overflow shape: the parsed stamp only keys a day and is never shifted by a timedelta. Probe: Tibber and entity rows stamped 0001-01-01 and 9999-12-31 through `prices_from_*` → `hourly_/quarters_from_entries` give `price_extreme_stamp_raised=0` |
| `coordinator._comparable_ts` | guarded structurally: its only `+` is `_covering_index`'s `starts[i] + span`, and `i` indexes the last start at or before now, so a 9999 stamp never reaches the addition. A year-1 start plus one span does not underflow |
| `manual_plan._parse_dt`, `services.handle_apply_manual_plan` | guarded: `build_override` refuses an expiry in the past and clamps to `MANUAL_PLAN_WINDOW_HOURS` (manual_plan.py:297, 306). Probe: slot stamps at both ends of the datetime range give `manual_extreme_stamp_raised=0` |
| `wood_fuel._as_dt` | guarded: the parsed instant is only compared and subtracted (`utc_elapsed_seconds`); the `+ step` is on grid stamps |
| `drift.stored_instant`, `accuracy.AccuracyTracker.replay`, `accuracy._stored_promise`, `coordinator._outage_reading`, `coordinator._stored_isoformat`, `manual_plan.ManualOverride.from_dict`, `price_tiles._aware` | guarded: store reads behind `store._bound_instants` (at `QuarantiningStore.async_load`), which caps every stored instant at load time plus the store's declared lead. Downstream they only subtract from now or add to a year-1 instant, and neither overflows |
| `heat_curve._age_s` | not applicable: the integration's own `written_at` (`_record_write`, `now.isoformat()`), subtracted from now only |
| `accuracy.AccuracyTracker.from_dict`, `binary_sensor.MoldFloorBreachBinarySensor._plan_outdoor_now`, `coordinator.HeatPumpOptimizerCoordinator._immersion_dhw_margin`, `duty_switch.Direction.from_row`, `store._bound_instants` | guarded: the enumerator saw the parsed instant compared against a bound (`_bound_instants` is the bound itself) |

**bool-number (33)**
| seam | disposition |
|---|---|
| `coordinator._parse_ecl110_state` | **instance**, judged site (D1-s3-02) |
| `dhw_draws.DrawStats.from_dict`, `tariff._stored_peaks`, `off_restore._entry_of`, `coordinator._async_load_energy_totals`, `coordinator._async_load_ledger`, `legionella.LegionellaGuard.async_load` | **instance, beyond the finding.** A JSON `true` in the store loads as the number 1.0: a 1.0 kWh draw, a 1.0 kW billed peak, a 1.0 baseline, 1.0 kWh on a total, an operation score of 1.0, or a 1.0 °C attempt peak. Probe arm `store-bool` gives 6 of 7. The store barrier does not see it: `_poisoned` returns False for a bool by design, and Arm 4's `WRONG_TYPE` (`tests/finite_boundary.py:113`) substitutes no bool. These are low severity, like D1-s2-01: no saver writes a bool to these fields, so the store has to be corrupted first |
| `comfort_learning.ComfortLearner.from_dict` | guarded: the stored configured weight must equal the configured one, and the learned weight is clipped to `[COMFORT_WEIGHT_MIN, COMFORT_WEIGHT_MAX]`. The probe arm's seventh loader is not admitted |
| `config_flow._same_setting` | not applicable: `posted` comes from the options form's number selectors; the only possible bool is a boolean field compared with its own stored value |
| `replay_doc.numeric` | not applicable: it reads recorder state rows, whose `state` is a string |
| `thermal_model.ThermalParameters.dhw_inlet_reference` | not applicable: `dhw_inlet_current` is set from the coordinator's resolved float (an InputReader reading or the seasonal model), not from an untyped source |
| `coordinator._fold_away`, `coordinator._with_sensor_advisor`, `topology.rank_sensor_advisor`, `diagnostics._inputs_at.aged`, `diagnostics._over_age`, `ledger.MonthlyLedger.observe_spot_and_settle_savings`, `notifier._comfort`, `pump_arbiter._flow_command` | not applicable: each tests a value the integration computed itself (the publish payload, power windows, diagnostics problem dicts, the pending ledger snapshot, the plan rows, the arbiter's own written value), not an input boundary |
| `boost._restore_settle`, `coordinator.plan_stale_limit_minutes`, `defrost.DefrostWindow._elapsed`, `draw_range._stored_idle`, `drift._finite_floats`, `duty_switch._stored_number`, `learner_progress._snapshot_count`, `pump_arbiter._writable`, `replay_doc._collect_strings`, `replay_doc._number`, `replay_doc._scan_leaf`, `replay_doc.clean_value`, `replay_doc.json_decimal_places`, `store._number` | guarded: each excludes `isinstance(x, bool)` beside the number test |

## Count and barrier

There are 19 instance seams. Nine are judged sites; two of those (D1-s2-01 and
D1-s2-51) are guarded at the register head. **Ten are beyond the findings**, under
two roots:

1. **Wrong-typed options, 4 seams** (`config_flow._effective`,
   `topology.describe_setup`, `topology._slot_extras`,
   `quiet_windows.measured_ceiling_kw`), with D1-s2-05's root. Proposed barrier:
   quarantine wrong-typed numeric options once, in `async_migrate_entry` (D1-s2-05's
   `--fix` shape). Then add an options arm to `tests/finite_boundary.py`: seed every
   numeric option with the `WRONG_TYPE` spellings and require that setup, one cycle
   and every options-flow validator raise nothing. The `opt-float` family of
   `p1_seams.py` is its seam list.
2. **A bool in a numeric store leaf, 6 seams.** Proposed barrier: add a bool
   (`true`/`false`) to Arm 4's `WRONG_TYPE` and have the scan reject a numeric leaf
   whose loaded value differs from its seed by exactly the bool coercion. A loader
   then either refuses the bool or is listed. Alternatively, `_sanitize` could null a
   bool at a leaf the store's schema declares numeric, though no such schema exists
   today.

The remaining live judged shapes (`parse_bool`, `_parse_ecl110_state`,
`_restore_settle`, `_parse_block`) have no beyond-finding twin: every other seam in
their families is guarded or not applicable. A per-family runtime barrier for them
would protect only the judged site, so their fixes are per-instance. `barriered` is
`false`: the class's existing store barrier does not reach either root above.
