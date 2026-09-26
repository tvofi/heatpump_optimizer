# Round 9 — D1 (robustness and stability), finder seat D1-s2

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), export
`/home/claude/audit-r9-baseline`, box B4 (light seat). Interpreter
`/home/claude/venv-r9/bin/python`, `PYTHONPATH=tests/hastub`, every harness run
from the export root.

Cells: D1.M1–M6 over `__init__`, `coordinator`, `services`, `repairs`,
`frontend`, `narrative`, `diagnosis`, `comfort_band`, `const` (all deep steps).

Exposure: none. No `docs/`, no GitHub, no earlier-round evidence opened (none of
tools/audit/round3..round8 was read). `tools/audit/bugclasses.json` was read
for class ids only.

## Real-HA semantics every harness uses

* `HASTUB_TZ=Europe/Stockholm`, so `dt_util.now()` is tz-aware as in Home
  Assistant (the stub's default clock is naive).
* Store bytes are parsed as Home Assistant parses them, with **orjson**, not
  the stub's stdlib `json`. orjson refuses a `NaN`/`Infinity` token and an
  integer beyond 64 bits (the real Store then quarantines the whole file and
  the loader gets `None`), and turns a u64 overflow into a float. Two stub-only
  failures (non-findings below) were voided by this.
* Lifecycle runs through `tests/harness.py:ha_setup_entry`/`ha_unload_entry`,
  one at a time, never concurrently (the brief's trap).
* A real `ThreadPoolExecutor` on a real loop wherever a boundary is measured
  (`lifecycle.py`, `worker_stop.py`); solves go through the real process worker.

## Findings

### D1-s2-01 (M6, high): one malformed weather-forecast response wedges every later cycle until restart

`_fetch_weather_forecast` stores the response's `forecast` value
(`self._weather_forecast = _forecast_in_model_units(...)`) before anything
checks that it is a list of dict rows. For a degC/m-s/mm entity,
`_forecast_in_model_units` returns it untouched. A non-dict row (`"x"`, `None`,
`[...]`) or a non-list `forecast` (a string) is then iterated with `.get` by the
eleven `self._weather_forecast` readers. `_update_current_state` calls
`_current_humidity` **before** the next fetch, so every later cycle raises
`UpdateFailed` before it reaches the fetch that would replace the bad forecast.
That holds even once the weather entity answers correctly again. Entities go
unavailable, with no plan and no actuation, until Home Assistant restarts.

`parsers.py --n 200 --seed 9`: `weather.cycle_raised=35` and
`weather.wedged=35` of 200 hostile payloads (27 non-dict rows, 8 non-list
shapes). `wedged` counts cycles that still raise after a HEALTHY forecast is
served again. With `--perturb row_filter` (keep only the dict rows of a list,
where the forecast is stored), `wedged` and `cycle_raised` both drop to 0.

### D1-s2-02 (M6, medium): finite but absurd forecast values reach the solve unbounded

No physical-range bound sits between a `weather.get_forecasts` row and the
horizon arrays. In `parsers.py`, 8 of 200 payloads (`weather.poisoned_series=8`)
put |T| > 100 degC, wind < 0 or > 100 m/s, or negative rain into the series the
solve receives.

The consequence, from `solve_poison.py` (real process-worker solve, fresh
interpreter per case, healthy cycle 3.45 s in the same session):
- One row at `temperature=-1e308`, or eight rows at `+1e308`, gives a
  `failed (no usable starting point)` plan while the cycle reports success.
- One row at `wind_speed` of 1e12, 1e20 or 1e308 runs the solve past the 60 s
  cap (`capped=1`). In an earlier probe the 1e308 worker had burned over 3 min
  of CPU when it was killed. 1e6 and 500 finish in about 1–2 s.

On a Pi the runaway solve pegs a core. Every solve serialises on
`_PROCESS_LOCK`, so it also blocks every later solve and the stop reap
(D1-s2-05). With `--perturb clip` (clip temperature, wind and rain where the
forecast is stored), `capped_cases=0` and every status is `optimal`. The
healthy case in the same session is the null control.

### D1-s2-03 (M2, medium): a sample count past 2**64 in the thermal-learning store fails every cycle

`_async_load_thermal_learning` parses `cop_baseline[*][1]` and
`capacity_envelope[*][1]` with `int(entry[1])` and no bound. The real (orjson)
Store accepts a JSON number such as `1e20` or `1e308`, and `int()` turns it
into a Python int that numpy cannot hold. `_learning_view` then raises
`TypeError` at `np.isfinite(entry[1])` inside `_build_data_dict`, on every
cycle. The re-save cannot repair it, because orjson refuses the >64-bit int on
save, so the failure survives restarts.

`store_fuzz.py --sweep-huge`: `thermal_learning.huge_leaf_wedges=6` of 58
leaf-values (3 leaves × {1e20, 1e308}), and 0 in every other store. The seeded
fuzz at 1000 mutants per store (seed 10) hit the same seam once. With
`--perturb learning_view_float` the count is 0.

### D1-s2-04 (M5, medium): the five cycle-path guards swallow a persistent failure at DEBUG

`_async_update_data` and `async_run_optimization` fence five callees with
`except Exception: _LOGGER.debug(...)`: `_command_frequency`,
`_async_drive_pumps`, `_async_watch_learning_drift`, `_maybe_run_fuse_advisor`
and `_maybe_refresh_price_tile`. `guards.py` injects a persistent `TypeError`
into each:
- every site was reached in 3 of 3 cycles;
- every cycle reported `last_update_success=True`;
- the user-visible record count (WARNING+ logs plus repair issues) is 0 for
  all five (`silent_sites=5 of 5`).

Two of the five are actuation (frequency command and pump drive), so a
programming error there silently stops commanding the hardware.
`grep -n -A2 "except Exception" coordinator.py | grep _LOGGER.debug` lists 24
guards of this kind. With `--perturb debug_to_warning`, `silent_sites=0`.

### D1-s2-05 (M1/M4, medium): Home Assistant stop waits out an in-flight solve

The stop listener registered by `async_register_worker_shutdown` runs
`_shutdown_process_pool` on the executor. That function takes `_PROCESS_LOCK`,
which `_run_in_process` holds for the whole solve (from the dump to
`pickle.load`). Fired 0.1 s into a real solve, the listener returns only when
the solve does.

`worker_stop.py --reps 5`:
- `stop_latency_ratio=0.928` of the solve's own duration (min 0.843, max
  1.017);
- `stop_latency_inflight_s=1.171`, against `stop_latency_idle_s=0.008` with no
  solve in flight (null control).

The repository itself puts a Pi solve at 30–70 s, so a restart during a solve
waits that long, and indefinitely behind D1-s2-02's runaway. With
`--perturb unlocked_reap` (the reap does not queue behind the transport lock),
the ratio is 0.010.

## Non-findings (checked and held)

* **M2 store fuzz over the 7 coordinator stores** (`thermal_learning`,
  `price_model`, `accuracy`, `energy`, `ledger`, `snapshots`, `manual_plan`),
  with orjson disk semantics:
  - `store_fuzz.py --n 200 --seed 9`: 0 loader raises, 0 cycle raises and 0
    collateral (a healthy sibling key lost) in 1400 mutants.
  - `--n 1000 --seed 10`: 0 loader raises and 0 collateral in 7000 mutants;
    1 cycle wedge, at the D1-s2-03 seam.
* **Stub-only store failures, voided.** Under the stub's stdlib json
  (`--stdlib-json`) the fuzz gives `energy.loader_raised=1`
  (`np.float64(10**400)` OverflowError, all totals reset) and
  `accuracy.cycle_raised=1` (`defrost.duty_counts=10**400`). orjson refuses
  both files outright, so no loader ever sees them. Harness gap: the hastub
  `Store` accepts bytes that Home Assistant's Store refuses.
* **M1 lifecycle** (`lifecycle.py`): setup → light first refresh → reload
  mid-solve → unload mid-solve → setup gives `leaked_coordinators=0`,
  `tasks_holding_old=0`, `escaped_exceptions=0`, `error_logs=0` and
  `final_first_solve_ok=1`. Instrument checks: `--perturb leak` gives
  `leaked_coordinators=2`, and `--perturb no_cancel_any` gives
  `discarded_solves=4`.
* **M4 executor boundary** (`executor_share.py`): at submission, the objects
  shared between the live coordinator and a job are 2 for the solve, 1 for
  simulate and 5 for diagnose. They are only `coord._pv_surplus` (an ndarray)
  and `coord._last_interval_record` (dicts). Both are rebound, never written in
  place (a grep for in-place writes finds 0). `--perturb no_snapshot_copy`
  gives `shared_solve=16`.
* **M3 plan age** (`staleness.py --part age`): the DST fold and gap both read
  60.0 min for 60 real minutes. Clock jumps read wall time:
  - forward 6 h reads 390 min and marks the plan stale, so actuation is held
    (fails safe);
  - backward 6 h is clamped to 0 and not marked stale.

  The wall clock is the only clock this seam has, and the backward case
  matters only across consecutive solve failures. Recorded, not claimed.
* **M3 stuck price entity** (`staleness.py --part prices`): known steps fall
  96 → 48 → 8 → 2 → 0. With none left the cycle publishes no plan
  (`blind_plans=0`), and `price_known_steps` and `plan_price_known` disclose it.
* **M6 ECL110 handler** (`parsers.py`): `handler_raised=0` of 200 hostile
  payloads. 55 of them land a finite but absurd displace (1e308) on the live
  state. That had no effect on the plan in the harness's non-ECL configuration,
  so this check is partial.

## Harnesses

All are under `tools/audit/round9/D1/s2/`: `store_fuzz.py`, `lifecycle.py`,
`worker_stop.py`, `executor_share.py`, `guards.py`, `staleness.py`,
`parsers.py` and `solve_poison.py`. Each header carries its metric, command,
expectation, baseline and perturbations. Root rule: paths resolve relative to
the cwd (the export root), as in `tests/harness.py`.

## Unfinished

* M1: two config entries sharing the worker lock (two entries, one reload)
  were not driven.
* M6: an ECL110 absurd but finite displace was not driven through an
  ECL-configured cycle.
* M5: 5 of the 24 debug-only guards were driven. The other 19 are enumerated by
  the seam rule but were not injected.

## Leads (outside the cells)

See `leads` in report.json.
