# D1 — Robustness and stability (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`.
All numbers below are counts and are contention-immune; `load1` and
`thread_factor` are recorded per harness for form (the executor harnesses put
their CPU on worker threads, so their `thread_factor` is meaningless and no
timing number is claimed). Box: Apple M1 8-core 8 GB, Darwin 25.6.0, CPython
3.13.1, numpy 2.5.2, ten other auditors running.

Every harness runs from the export root with
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python tools/audit/round2/D1/<harness>.py`
and its captured output sits next to it as `<harness>.out`.

## Method

The test stub (`tests/harness.py:FakeHass`) closes every created coroutine
and runs the executor inline, so none of the five questions in the brief can
be answered on it. Five harnesses were built:

1. `lifecycle_realloop.py` — a real asyncio loop, a `ThreadPoolExecutor`, and
   a model of Home Assistant's `DataUpdateCoordinator` (2024.x: `_async_refresh`,
   a `Debouncer`, interval scheduling only while listeners exist,
   `async_shutdown` that cancels the timer and the debouncer but not an
   in-flight refresh, `async_config_entry_first_refresh` raising
   `ConfigEntryNotReady`) plus the config-entry state machine
   (`async_setup` → `SETUP_RETRY` + `_async_process_on_unload` on NotReady;
   `async_unload` → component unload then `_async_process_on_unload`, which
   cancels entry background tasks; `async_reload` = both under `setup_lock`).
   The model is bound in place of the stub's `DataUpdateCoordinator` before
   the integration imports it, so `HeatPumpOptimizerCoordinator` inherits it.
   Platforms are modelled as five coordinator listeners added on forward and
   removed on unload. `HeatPumpOptimizer.optimize` is gated by a
   `threading.Event` so "during an in-flight solve" is a deterministic point,
   not a race against the clock. Tibber is a fake aiohttp session; the weather
   service is registered on the stub's real service registry; MQTT subscribe
   records a real unsubscribe. Every task, executor future, listener, MQTT
   subscription and timer is tracked; exceptions are collected from a loop
   exception handler and task done-callbacks. Both eager (HA ≥ 2024.3) and
   lazy task start are run; the numbers are identical.
2. `store_fuzz.py` — ten `Store` payloads, healthy payloads produced by the
   coordinator's own savers after one real cycle plus explicit seeding of the
   stores a cycle leaves empty, 200 seeded mutants each (type swaps, missing
   keys, NaN/±inf, negative, huge, zero, wrong nesting, truncated lists,
   strings where dicts go, whole-document replacements). Each mutant is loaded
   through the real fire-and-forget loader on a real loop, followed by two
   update cycles (6 h horizon, real solve) and a fresh-coordinator restart on
   the disk those cycles left behind. Null control: the identity mutant.
3. `staleness.py` — the price feed that stops covering the horizon, the
   fabricated first forecast, clock steps forward and back, `last_reported`
   in the future, `unknown`/`unavailable`, three failed solves and recovery.
4. `executor_race.py` — the solve held inside the executor while every
   loop-side writer is exercised; the plan is compared field by field with an
   unmutated run (deterministic: repeat runs are identical) and with a
   pre-mutation positive control.
5. `guards.py` — an exception injected at each swallowing site on the update
   path, plus a `Store.async_save` that raises `OSError`.

## Findings

### D1-01 — ConfigEntryNotReady from the first refresh leaks the coordinator's listeners and MQTT subscription per retry

*Severity medium, class bug.*

**Claim.** When `async_config_entry_first_refresh` raises `ConfigEntryNotReady`
(the first Tibber fetch fails), the coordinator built by that setup keeps its
`async_track_state_change_event` registrations (peak guard, defrost watch)
and its ECL110 MQTT subscription, none of which is ever unsubscribed, and each
retry of the setup leaks another coordinator.

**Mechanism.** `HeatPumpOptimizerCoordinator.__init__` (coordinator.py 676–691)
spawns `_async_setup_peak_guard`, `_async_setup_defrost_watch` and
`_async_setup_ecl110_state_subscription` before `async_setup_entry`
(`__init__.py` 389–408) awaits the first refresh. They register directly on
`hass` (7727, 7680, 1273), not through `entry.async_on_unload`. On
`ConfigEntryNotReady` Home Assistant runs only the entry's `async_on_unload`
callbacks and cancels the entry's background tasks; `async_unload_entry` and
`coordinator.async_shutdown` never run. The bound methods on the bus keep the
whole coordinator alive (thermal model, optimizer, stores, arrays), and every
subsequent meter event runs the dead coordinators' `_on_power_event`. The
ECL110 state topic defaults on (`DEFAULT_ECL110_STATE_TOPIC`), so on an MQTT
install the subscription leaks even with both guards off.

**Real-HA path.** Tibber unreachable when Home Assistant boots (the usual
after a power cut: the Pi is up before the router). HA retries setup with
backoff (5, 10, 20, 40, 80 s, then ~80 s + jitter) for the length of the
outage.

**Evidence.** `lifecycle_realloop.py`, scenario `notready_eager` (5 retries,
then Tibber recovers and the entry loads):

| RESULT | value |
|---|---|
| `notready_leaked_listeners` | **10** (5 retries × peak guard + defrost) |
| `notready_leaked_mqtt_subs` | **5** |
| `notready_zombie_coordinators` (alive after `gc.collect()`, weakrefs taken at construction) | **5** |
| `notready_zombie_handler_runs` (dead handlers run for ONE power event after the entry loaded) | **5** |
| `notready_eager.live_listeners` | 2 (the loaded instance's own) |
| `notready_eager.escaped_exceptions` | 0 |
| lazy-start arm | identical: 10 / 5 / 5 / 5 |

Null control (feature-off arm, `notready_guards_off_eager`):
`peak_guard_enabled=False`, no defrost entity, `ecl110_state_topic=""` →
`leaked_listeners=0`, `leaked_mqtt_subs=0`, `zombie_coordinators=0`.

**Metric.** Registrations on the bus (and MQTT subscriptions) whose callback
is bound to a coordinator from a setup that raised `ConfigEntryNotReady`,
after 5 retries and one successful setup.

**Perturbation.** Config: the guards-off arm above → to_zero (observed 0).
Code: register the three subscriptions after the first refresh succeeds (or
through `entry.async_on_unload`, or wrap the first refresh in
`async_setup_entry` with `except ConfigEntryNotReady: await coordinator.async_shutdown(); raise`) → to_zero.

**Consequence on a Pi.** Memory and per-event CPU grow linearly with the
number of retries for the life of the process; the zombies hold no plan, so
they do not actuate (`_async_peak_guard_transition` returns on an empty
`_current_action`). Workaround: restart HA once the network is back. Hence
medium.

**Files.** `custom_components/heatpump_optimizer/coordinator.py` (676–691,
1265–1283, 7671–7686, 7714–7733), `custom_components/heatpump_optimizer/__init__.py`
(389–408). Fix scope: one place in `async_setup_entry` or the three
registrations.

### D1-02 — A reload while a scheduled solve is in the executor lets the torn-down coordinator actuate the pump and write stores after its own shutdown

*Severity medium, class bug.*

**Claim.** If an options save reloads the entry while the coordinator's
scheduled refresh is inside `async_add_executor_job`, `async_shutdown`
returns, the new coordinator sets up, and the old refresh then completes the
rest of `_async_update_data` on the dead instance: it commands the switch and
publishes two MQTT commands from the pre-reload plan, and writes two stores.

**Mechanism.** `async_shutdown` (coordinator.py 4989–5025) documents that the
base class "stops the refresh debouncer and any in-flight refresh". Home
Assistant's `DataUpdateCoordinator.async_shutdown` cancels the scheduled
timer and the debouncer; it does not cancel a running `_async_refresh`, and a
scheduled refresh is a hass-level task that the entry's unload does not
cancel (only entry background tasks are — which is why the *first* solve,
scheduled through `entry.async_create_background_task`, is clean, see
non-findings). Nothing after the executor await in `async_run_optimization`
or in `_async_update_data` checks `_shutdown_requested`.

**Real-HA path.** Any options page save while the 30-minute cycle is solving.
On Pi-class hardware a solve is tens of seconds, so the window is a few
percent of the time; the reload itself is the trigger the skip-solve flag
was built to soften.

**Evidence.** `lifecycle_realloop.py`, scenario `midsolve_eager`, phase C
(scheduled refresh held in the executor, options changed, reload through the
state machine, then released):

| RESULT | value |
|---|---|
| `sched_shutdown_returned_before_release` | 1 |
| `sched_midsolve_zombie_actuations` (`_apply_action` with a plan after shutdown) | **1** |
| `sched_zombie_service_calls` (attributed to the dead instance, after shutdown) | **3** = `switch.turn_on + mqtt.publish + mqtt.publish` |
| `sched_midsolve_zombie_saves` (store writes by the dead instance after shutdown) | **2** |
| `sched_newest_first_cycle_ok` | 1 |
| `sched_escaped_exceptions` | 0 |

Null control: the same reload during the *first* solve (an entry background
task, cancelled by the state machine): `old_post_shutdown_actuations=0`,
`old_post_shutdown_saves=0`, `old_tasks_alive=0`, `old_instance_alive_after_gc=0`.

**Metric.** Service calls to `switch.*`/`mqtt.*` and store writes issued by a
coordinator after its own `async_shutdown()` returned, for one reload with a
scheduled refresh held in the executor.

**Perturbation.** One line after `result = await self.hass.async_add_executor_job(...)`
in `async_run_optimization` (and before `_apply_action` in
`_async_update_data`): `if getattr(self, "_shutdown_requested", False): return`
→ to_zero. Alternatively cancel the in-flight refresh task in `async_shutdown`.

**Consequence.** One actuation from the old configuration lands within a
solve's duration of the reload, concurrent with the new instance's setup, and
the old instance's post-solve saves race the new instance's loads; the new
instance's first solve supersedes both within one cycle. Bounded, so medium.

**Files.** `coordinator.py` (4733–4760 executor call and the post-solve tail,
4344–4430 `_async_update_data`, 4989–5025 `async_shutdown`).

### D1-03 — Store loaders crash on corrupt payloads; three stores are never reset so the loss repeats on every restart

*Severity medium, class bug.*

**Claim.** Of 2000 seeded mutants (200 per store) 152 end the store's loader
task with an unhandled exception; for `dhw_profile` (64/200),
`thermal_learning` (9/200) and `dhw_draws` (1/200) the corrupt file is never
rewritten, so a restart raises again — the learned state is lost for good and
`thermal_learning` is left half-applied.

**Mechanism.** The loaders guard only `store.async_load()`; the parsing after
it trusts the shape. `_async_load_dhw_profile` → `_normalize_dhw_profile`
applies `np.clip` to whatever the 24-element list holds (`None`, a string, a
nested list); `_async_load_thermal_learning` catches
`(TypeError, ValueError)` but `int(float("inf"))` raises `OverflowError`, a
wrapped `freq_map` raises `KeyError`, and a top-level list raises
`AttributeError` on `.get`; `PriceShapeModel.from_dict` does `float(v)` over
`shapes`/`quarter_factors` without a guard; `DefrostDerate.from_dict`,
`StartCounter.from_dict` and `AccuracyTracker.from_dict` hit the same
`OverflowError`/`KeyError` paths. In HA the task's exception is logged once
by the loop handler ("Error doing job"), the rest of that loader is skipped,
nothing is quarantined. `accuracy`, `energy_totals`, `ledger` and
`price_model` happen to be rewritten by the next cycle or the next learned day
(so `repeat_on_restart=0`, at the cost of the history they held); the three
above are written only on learning events. The update loop itself never
fails: `cycle1_failed=0` and `cycle2_failed=0` for all 2000 mutants.

**Evidence.** `store_fuzz.py` (seed 20260901, exact):

| store | loader_raised /200 | repeat_on_restart | exception kinds |
|---|---|---|---|
| snapshots | 0 | 0 | — |
| dhw_profile | **64** | **64** | TypeError 38, UFuncTypeError 24, AttributeError 2 |
| dhw_legionella | 0 | 0 | — |
| dhw_draws | 1 | 1 | TypeError |
| thermal_learning | **9** | **9** | OverflowError 6, AttributeError 2, KeyError 1 |
| price_model | **57** | 0 | TypeError 41, ValueError 14, AttributeError 2 |
| ledger | 3 | 0 | AttributeError 2, OverflowError 1 |
| accuracy | 11 | 0 | OverflowError 8, AttributeError 2, KeyError 1 |
| energy_totals | 7 | 0 | TypeError 5, AttributeError 2 |
| manual_plan | 0 | 0 | — |
| **total** | **152 / 2000** | **74** | |

Leave-one-out over the 10 cells: range 0–64; dropping the most favourable
(largest) cell leaves 88/1800. Null control: `identity_failures=0` in every
store. `silent_load=0` everywhere (no corruption is swallowed at load only to
fail a later cycle). Concrete mutants are in `store_fuzz_failures.json`, e.g.
`none@hourly_profile/1` → `TypeError('>=' not supported between 'NoneType' and 'float')`,
`inf@buffer_cooling_samples` → `OverflowError('cannot convert float infinity to integer')`,
`top:wrapped_list` → `AttributeError("'list' object has no attribute 'get'")`.

**Metric.** Loader tasks ending with an unhandled exception over 200 seeded
mutants per store, and the subset whose fresh-coordinator load raises again on
the disk left after two update cycles.

**Perturbation.** Wrap each loader body after `async_load()` in
`try/except Exception` that logs one WARNING and saves `{}` (the pattern
`_async_load_manual_plan` already uses) → `loader_raised` and
`repeat_on_restart` to_zero for that store; `manual_plan` and `snapshots`,
which validate their shape, are the 0/200 reference.

**Consequence.** No wrong money and the loop survives, but the learned
parameters (weeks of DHW profile, the house heat-loss scale, COP scale, the
detectors' memory) silently fall back to defaults with a traceback per boot;
`thermal_learning` applies the buffer cooling rate and then stops, so the plan
runs on a mixed learned/default model. Workaround: delete the `.storage`
file. Medium.

**Files.** `coordinator.py` 1401–1476 (`_async_load_dhw_profile`,
`_normalize_dhw_profile` ~1520), 1489–1497, 1843–2030, 7133–7149, 7164–7211,
7230–7257, 7302–7322; `price_model.py:PriceShapeModel.from_dict`,
`defrost.py:DefrostDerate.from_dict`, `wear.py:StartCounter.from_dict`,
`curve_learning.py:CurveLearner.from_dict`, `freq_control.py:FrequencyMap.from_dict`,
`dhw_draws.py:DrawStats.from_dict`.

### D1-04 — A price list no longer covering the horizon is planned and actuated on a flat 0.5 price while the cycle stays green

*Severity medium, class bug.*

**Claim.** When `_prices` is non-empty but no entry covers any step of the
horizon, `extend_price_series` prices every step at its `fallback=0.5`
constant, the solve runs, publishes a plan with `savings_percentage` and
`predicted_cost`, actuates the switch, and `_async_update_data` succeeds.

**Mechanism.** `_price_series` (coordinator.py 5711–5765) returns `None` —
"skip the run" — only when `self._prices` is empty; `_known_prices_for`
returns an empty leading run for a stale list, and
`price_model.extend_price_series` (`if known_count == 0: return np.full(n_steps, fallback)`)
invents exactly the flat curve the `_price_series` docstring says was removed.
The only disclosure is `price_known_steps=0` in the payload and the per-slot
`price_known` flags; no sensor or the card reads `price_known_steps`.

**Reach.** Needs a successful fetch with stale content (the fetch failing is
handled honestly: `UpdateFailed`, red) or a clock more than a day off from
the list; narrow, stated as such.

**Evidence.** `staleness.py`, arms `covering` (list starts at today's
midnight) and `stuck` (list ends two days ago), 24 h horizon, 96 steps:

| RESULT | covering | stuck |
|---|---|---|
| `*_prices_known_steps` | 96 | **0** |
| `*_prices_fallback_steps` (== 0.5) | 0 | **96** |
| `*_prices_solved` | 1 | **1** |
| `*_prices_update_success` | 1 | **1** |
| `*_prices_switch_calls` | 1 | **1** |
| `*_prices_savings_pct` (published) | 27.92 | **13.4** |
| `*_prices_plan_stale` | 0 | 0 |
| `*_prices_forecast_min_max` | 0.600/1.058 | 0.500/0.500 |

**Metric.** Steps of the solve horizon priced at `extend_price_series`'s
fallback constant when no published entry covers any step, and whether the
cycle still solves, actuates and returns a payload.

**Perturbation.** Shift the list to cover `now` (the `covering` arm) →
`fallback_steps` to_zero (observed 0); or in `_price_series`, after
`_known_prices_for`, `if not known: return None` → `stuck_prices_solved`
to_zero.

**Files.** `coordinator.py` 5711–5765, `price_model.py:extend_price_series`.
Fix scope: one condition in `_price_series`.

### D1-05 — The what-if solve shares learner containers with the loop by reference; a mid-solve write tears its answer

*Severity low, class bug.*

**Claim.** `async_simulate` builds `scratch_params = replace(self._thermal_params)`
(shallow), so `defrost_derate` (the live `DefrostDerate` object),
`internal_gains_profile` and `dhw_windows` are shared with the event loop
while the what-if runs in the executor; an in-place write on them mid-solve
changes the what-if's answer.

**Evidence.** `executor_race.py` (deterministic: `whatif_repeat_identical=1`,
`live_repeat_identical=1`):

| RESULT | value |
|---|---|
| `whatif_torn_fields` (all shared containers mutated mid-solve) | **10** of 10 changed by the pre-mutation control |
| `whatif_torn_defrost_learner` (80 × `observe` mid-solve) | **9** |
| `whatif_torn_gains_profile` | 7 |
| `whatif_torn_dhw_windows` | 9 |
| `whatif_torn_draw_pattern` | 0 |
| `whatif_scalar_torn_fields` (scalar writes on `_thermal_params`/`_current_state`/`_opt_config`) | 0 |
| `whatif_exceptions` | 0 |
| null control, the live solve (`_solve_snapshot` deep-copies): `live_torn_fields` | **0** of `live_control_changed=26` |

**Metric.** What-if payload fields that differ between a run whose shared
containers were mutated in place while the solve thread was held in the
executor and an unmutated run with identical inputs.

**Perturbation.** `copy.deepcopy(self._thermal_params)` in `async_simulate`
(the idiom `_solve_snapshot` uses) → to_zero.

**Reach and consequence.** The only in-place production writer is
`_defrost.observe`/`observe_duty` in `_record_accuracy` at the end of every
cycle (`dhw_hourly_draw_pattern`, `internal_gains_profile` and `dhw_windows`
are reassigned, never mutated in place); one EWMA step lands mid-solve only
when a card drag overlaps the cycle's tail, and the what-if never actuates.
Low.

**Files.** `coordinator.py` 10687–10800 (`async_simulate`).

## Non-findings (checked and held)

| claim | command | value |
|---|---|---|
| Reload during the *first* solve (entry background task) leaks nothing: HA cancels the task | `lifecycle_realloop.py` | `reload_midsolve_old_tasks_alive=0`, `old_listeners=0`, `old_mqtt_subs=0`, `old_timers=0`, `old_exec_futures_pending=0`, `old_instance_alive_after_gc=0`, `new_first_cycle_ok=1` |
| Unload during a solve, then setup again: nothing left, handover republished, new first cycle solves | `lifecycle_realloop.py` | `unload_midsolve_listeners=0`, `unload_midsolve_mqtt_subs=0`, `unload_midsolve_tasks_alive=0`, `resetup_first_cycle_ok=1`, `handover_republished=1` |
| No exception escapes any lifecycle scenario (loop handler + task results, eager and lazy start) | `lifecycle_realloop.py` | `total_escaped_exceptions=0` (all arms) |
| Tibber down at boot fails the setup honestly (NotReady) and the entry loads on recovery | `lifecycle_realloop.py` | `notready_eager.first_cycle_ok=1` after 5 retries |
| The live solve reads only copies: every loop-side writer mutated mid-solve changes nothing | `executor_race.py` | `live_torn_fields=0`, `live_control_changed=26`, `live_repeat_identical=1`, `live_exceptions=0` |
| A 4 h forward clock step marks the plan stale and stops actuation; a backward step clamps the age | `staleness.py` | `clock_fwd_plan_stale=1`, `clock_fwd_actuations=0`, `clock_fwd_plan_age_minutes=240.0`, `clock_back_plan_age_minutes=0.0` |
| `unknown`, `unavailable` and a 3 h-old reading are rejected; a future `last_reported` is accepted (the entity's claim, not fabricated) | `staleness.py` | `unknown_ok=0`, `unavailable_ok=0`, `three_hours_old_ok=0`, `future_last_reported_ok=1` |
| Three failed solves raise the repair issue, the plan is stale after 100 min and not actuated, recovery clears both | `staleness.py` | `solve_fail_counter=3`, `solve_fail_issue_raised=1`, `solve_fail_plan_stale_after_100min=1`, `solve_fail_actuations_when_stale=0`, `solve_recover_counter=0`, `solve_recover_issue_cleared=1` |
| A failed first weather fetch is marked stale from the start and the 48 h constant series is built only then | `staleness.py` | `fabricated_forecast_steps=48`, `fabricated_forecast_all_equal_current=1`, `fabricated_forecast_published_stale_hours=0.0` |
| No corrupt store ever takes the update loop down | `store_fuzz.py` | `cycle1_failed=0`, `cycle2_failed=0` in 2000/2000 |
| Snapshot ring, legionella timestamp and manual plan validate their shape | `store_fuzz.py` | `loader_raised=0/200` each |
| Healthy payloads load cleanly (null control) | `store_fuzz.py` | `identity_failures=0` × 10 |
| The five DEBUG-swallowed sites (`_command_frequency`, `_async_drive_pumps`, `_async_watch_learning_drift`, `_maybe_run_fuse_advisor`, `_maybe_refresh_price_tile`) keep the cycle alive and recover | `guards.py` | `cycle_completed=1`, `update_failed=0`, `recovered=1` each |
| A store that refuses to write (`OSError`) never breaks the cycle and saves resume | `guards.py` | `store_save_oserror.cycle_completed=1`, `recovered=1`, `saves_after_recovery=16` |
| Faults in `_update_current_state`, `_async_learn_price_shape`, `_apply_action`, `_record_accuracy` surface as `UpdateFailed` (red) and recover | `guards.py` | `update_failed=1`, `recovered=1` each |

Hygiene observations with numbers (not filed as findings):

- `weather_forecast_stale_hours` goes negative after a backward clock step
  (`clock_back_weather_stale_hours=-2.0`) and reads `0.0` at the instant of
  the fabricated forecast; no sensor, binary sensor or the card reads the key
  (0 occurrences in `www/heatpump-optimizer-card.js`), so M2's disclosure
  never reaches a user.
- A failure in `_command_valve_target` or `_file_lead_predictions` logs
  "Optimization failed" at ERROR on every cycle although the solve succeeded
  and the plan was stored (`guards.py`: `logged_2nd_cycle=1`, `cycle_completed=1`);
  the failure counter is reset before it is incremented, so the repair issue
  cannot trip.
- The DEBUG-swallowed sites never escalate on a persistent fault
  (`logged_warn_plus=0` on the second cycle too).

## Harnesses

- `tools/audit/round2/D1/lifecycle_realloop.py` (+ `.out`)
- `tools/audit/round2/D1/store_fuzz.py` (+ `.out`, `store_fuzz_failures.json`)
- `tools/audit/round2/D1/staleness.py` (+ `.out`)
- `tools/audit/round2/D1/executor_race.py` (+ `.out`)
- `tools/audit/round2/D1/guards.py` (+ `.out`)

## Not finished

- DST transitions were not re-driven for the age sensors (`tests/dst_checks.py`
  covers the quarter grid under `HASTUB_TZ`; a per-sensor age check under the
  zone needs a separate subprocess and was cut for time).
- The ECL110 MQTT state payload was not fuzzed (its handler swallows
  everything with a bare `except Exception`; a fuzz would show 0 escapes by
  construction).
- The wall-clock size of D1-02's window on a Pi (a solve's duration) is not
  measured here; it is provisional and quiet-window material.
- The HA core semantics in `lifecycle_realloop.py` were written from the core
  sources as remembered, not re-read (GitHub is off limits under COMMON.md);
  the header states each assumption so the judge can check them.

## Exposure

None: no `docs/` audit material was read; code comments citing `D<k>-nn`
ids were treated as context only.
