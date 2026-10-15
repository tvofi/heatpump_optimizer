# Class sweep: N-log-flood (round 10, D14 steps 3-4)

**Mechanism.** A condition that persists is logged at WARNING or ERROR on every cycle, when it should be logged once per transition. The judged finding is D1-s2-03 (`_weather_series`, 4 records over 4 cycles; a latch takes it to 1). In `dev/audit/config/bugclasses.json` the class has no entry yet, so its status is effectively `open` and new.

## Enumerators

- Static: `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer`. It reads every `_LOGGER.warning` and `_LOGGER.error` call through the AST. A call counts as latched when it sits under an `if` whose test names a latch flag, or under a `not in` test against a set the same function `.add`s to. Result: 85 sites, 6 latched, 79 unlatched seams.
- Runtime: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py [arm...] [--perturb]`. Each arm runs 4 real `_async_update_data` cycles under a condition that does not change, and counts every distinct package message. A message that appears 4 or more times is a flood.

## Controls

| control | result |
|---|---|
| positive (re-finds D1-s2-03) | `no_weather_entity` shows `No weather forecast available` 4 times; `weather_fetch_fails` shows it 4 times |
| null, runtime | `control` arm (48-row forecast, prices present): `floods=0` |
| null, static | a fixture with one latched warning gives `seams=0` |
| perturbation, runtime | `--perturb` replaces `_weather_fetch_failed`'s latch test with `if True:`. `No forecast data returned` goes from 1 to 4 times; control stays at 0 |
| perturbation, static | the same one-line change in the fixture moves `seams` from 0 to 1 |

## Dispositions

### Instance: a runtime probe fails on each

| file:symbol | probe arm | count over 4 cycles | beyond finding |
|---|---|---|---|
| coordinator.py `_weather_series` | no_weather_entity | 4 | no (D1-s2-03) |
| coordinator.py `_fetch_solar_forecast` | open_meteo_no_coord | 4 | yes |
| coordinator.py `_solar_location` | open_meteo_bad_coord | 4 | yes |
| coordinator.py `_price_series` (no price data) | no_prices | 4 | yes |
| coordinator.py `async_run_optimization` (not enough price data) | no_prices | 4 | yes |
| coordinator.py `_tariff_months` | bad_peak_months | 16 (`_capacity_tariff` is called 4 times per cycle) | yes |
| coordinator.py `_tariff_hours` | bad_peak_hours | 16 | yes |

There are 6 instances beyond the finding.

### Instance on static evidence only (not counted; a runtime probe is still owed)

Each of these is unlatched, is reached on every cycle or every actuation, and is triggered by a condition that persists, usually configuration. No arm has driven them yet:

- coordinator.py `_apply_action` (the stale-plan hold)
- coordinator.py `_command_valve_target` (lines 7286 and 7313: wrong zone kind, wrong entity domain)
- coordinator.py `_note_solve_failure` (an ERROR on every failed solve)
- pump_arbiter.py `_space_target` (an indoor set-point whose minimum is above the room target)
- inputs.py `_age_gate` (a future last-reported stamp, per read)

### Guarded: the static enumerator misses these, because the guard sits outside its pattern

| site | guard |
|---|---|
| coordinator.py `_tibber_fetch_failed` | `_tibber_outage_cycles` counter |
| coordinator.py `_weather_fetch_failed` | `_weather_outage_cycles` counter (the perturbation target) |
| open_meteo.py `async_refresh` | `_failures == 1` |
| coordinator.py `_check_pump_mode_expired` | `expired == _pump_mode_expired_notice` transition |
| legionella.py `check_mode_block` | `overdue_days == mode_block_notice` transition |
| coordinator.py `_update_current_state` (wood tank) | `wood_mean is None and had` transition |
| legionella.py `async_track_cycle` (5 sites) | once per attempt; `attempt` spaces retries by the interval |
| pump_arbiter.py `_not_held` | `misses > 1` and the `retry` spacing |
| curve_learning.py `record_miss` | an event per comfort miss; bias reset |
| coordinator.py `_detect_outage` | once per detected outage |
| coordinator.py `_note_worker_fallback` | per cycle by recorded design (docstring, #1755); the notice is latched per cause |
| the 6 latched sites the enumerator recognises | as printed |

### Not applicable: not reached per cycle

These run at load, restore, migration, setup, in the config flow, at frontend registration, from a service call, or at shutdown:

- `from_dict`, `_stored_rows`, `_in_domain`, `_bound_instants`, `_surface_version`, `best_restore`
- `async_migrate_entry`, `_async_load_*`, `async_restore_learned_snapshot`, `_async_setup_peak_guard`
- frontend.py, config_flow.py, grid_fee.py `from_config` and `apply_catalog`, thermal_model `from_config`
- `async_update_thermal_params`, `async_simulate`, `async_adopt_heat_loss_refit`, `async_shutdown`, `parse_day_overrides`

Each actuation exception handler (MQTT publish, `_async_set_pump`, `_command_frequency`, disinfection `_write` and `release`, `switch_supply`, climate displace) logs one record per failed call. Each such record is a separate event, not a repeat of a held condition, so it is a candidate only under a persistent outage. It is not counted here.

## Proposed barrier

Add a once-per-transition helper, such as `log_once(key, active)`, beside the existing outage counters, and route the 7 probed sites through it. Make `probe.py` a `tests/` script that asserts `floods == 0` on every arm. Its cost is about 8 arms of 4 cycles each, a few seconds of gate time.
