# D1 — Robustness and stability (round 4)

Baseline `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`, export at
`/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline`.
Machine: 8-core Apple M1, 8 GB, macOS 25.6.0, CPython 3.11, OpenBLAS pinned to
one thread. Ten finders shared the box; `load1` was 4.1–7.8 throughout. Every
number below is a **count**, so none of them is contention-sensitive; the two
`wall_s` figures are provisional and load-bearing for nothing.

Exposure: none. No `docs/audit-*`, no `docs/backlog.md`, no GitHub, no `gh`.
Two code comments in `coordinator.py` cite earlier `D1-nn` ids; they were read
as context, not as a to-do list, and nothing here was steered by them.

## Method

Four harnesses under `tools/audit/round4/D1/`, all runnable from the export
root with `PYTHONPATH=tests/hastub` and the five-variable thread pin.

1. `real_loop.py` — the real-loop lifecycle harness D1.md step 1 asks for.
   `RealHass` subclasses `tests/harness.py:FakeHass` and replaces the two
   methods that make the stub useless for this dimension:
   `async_add_executor_job` runs on a `ThreadPoolExecutor` on the running
   loop, `async_create_task` schedules instead of `coro.close()`. Every
   lifecycle transition goes through `tests/harness.py:ha_setup_entry` /
   `ha_unload_entry`, one at a time per entry, which is how Home Assistant's
   entry manager serialises them; nothing calls a lifecycle method directly
   or concurrently with a refresh, because a race that needs that is a stub
   artefact and was refuted on this project before.
2. `store_fuzz.py` — 200 seeded mutants for each of the 12 persisted stores
   (2400 total), 17 mutation operators, each mutant loaded through the real
   loader and followed by two ordinary cycles.
3. `price_prior_zero.py` — the targeted harness for finding D1-01.
4. `accuracy_wipe.py` — the targeted harness for finding D1-02.

Mutants are split into **strict-JSON** and **loose**. Real Home Assistant
round-trips `.storage` through orjson, which has no `NaN`/`Infinity` literal,
so a bare non-finite float describes in-memory corruption rather than a file
on disk. Both findings below are reproduced by a **strict-JSON** payload — a
plain JSON string and a plain JSON number — so neither depends on the test
stub's more permissive `json` module.

## Findings

### D1-01 — one corrupt bin in the persisted price shape prices a planning hour at 0.00 SEK/kWh (high)

`price_model.py:PriceShapeModel.from_dict` coerces every hourly shape bin with
`float(v)` inside `try/except (TypeError, ValueError, OverflowError)` and
performs **no finiteness check** — while `PriceShapeModel.observe_day`, the
writer of the same field, rejects a non-finite day at line 137 and clips the
rest. A shape bin holding the JSON string `"nan"` therefore loads as NaN, and
`price_model.py:extend_price_series` fills the horizon past the published
prices with `prices.append(max(0.0, model.predict(when, level)))`. In CPython
`max(0.0, nan)` is `0.0`, so instead of failing the integration quietly
prices that hour as **free electricity**.

```
PYTHONPATH=tests/hastub python3 tools/audit/round4/D1/price_prior_zero.py
RESULT zero_priced_steps=4              # of 96 planning steps
RESULT control_zero_priced_steps=0      # same store, finite bin
RESULT null_control_zero_priced_steps=0 # whole horizon published, prior unused
RESULT bins_reaching_zero=14            # of 24 hourly bins
RESULT zero_steps_per_bin_min=4  RESULT zero_steps_per_bin_max=4
```

The four affected steps are priced `0.0000` against `0.6018` in the matched
control. There is no log line, `last_update_success` is untouched, and
`store_fuzz.py` shows the corrupt value being written back
(`corrupt_persisted_mutants=91` over the corpus, 58 of them `price_model`),
so a restart does not clear it.

* metric: planning steps in `_forecast_arrays()[0]` whose price is exactly 0.
* null control: publish the whole 48 h horizon so `extend_price_series` never
  consults the prior — 0 zero-priced steps.
* leave-one-out: 24 cells (one per hourly bin), 14 reach the guessed tail in
  a 24 h horizon, every one of them produces exactly 4 zero-priced steps;
  range 4–4, total 56, 52 with the most favourable cell dropped.
* perturbation: add an `np.isfinite` filter to `from_dict`'s shape branch —
  `zero_priced_steps` must go to 0 while `control_zero_priced_steps` stays 0.

### D1-02 — one corrupt scalar in the accuracy store silently destroys the whole store (high)

`coordinator.py:_async_load_accuracy` wraps only `async_load()` in
`try/except`. Its first statement after the `isinstance` guard is
`AccuracyTracker.from_dict(stored.get("accuracy"))`, and
`accuracy.py:AccuracyTracker.from_dict:363` iterates
`data.get("samples", []) or []` — whatever is there. A JSON number or `true`
in that key raises `TypeError`, which escapes the loader. The loader is
`_spawn`ed from `_init_*` (`coordinator.py:1425`), so under real Home
Assistant it becomes an unretrieved background-task exception: setup
succeeds, no entity goes unavailable, nothing sets `last_update_success`
False. The next ordinary cycle then runs `_async_save_accuracy`, which writes
the in-memory **defaults** over the store.

```
PYTHONPATH=tests/hastub python3 tools/audit/round4/D1/accuracy_wipe.py
RESULT fields_lost=3  RESULT fields_checked=3
RESULT control_fields_lost=0
RESULT bool_variant_fields_lost=3
RESULT warning_log_lines=0  RESULT log_lines=0
RESULT last_update_success_after=1
```

What is lost, permanently, after one cycle: the month's realised
capacity-tariff peaks `[7.4, 6.8, 5.9] → []` (the quantity the capacity
tariff is billed on), the learned defrost derate table `0.80/0.90 → 1.0/1.0`,
and the user's operation mode `economy → auto`. Zero log lines at any level.

Every sibling loader guards its decode — the ledger even has an explicit
"same corruption barrier as the other riders" comment around its day-book
decode. `_async_load_accuracy` is the one that does not.

* metric: of three money- or physics-bearing fields in the accuracy store,
  how many differ from the healthy payload after load + one cycle.
* null control: the identical store with a well-formed `samples` list — 0.
* perturbation: wrap the decode in `try/except Exception` with one
  `_LOGGER.warning`, or make `from_dict` skip a non-list `samples`;
  `fields_lost` must go to 0 and `warning_log_lines` to 1.

## Non-findings

Each with the command and the executed number.

1. **Lifecycle leaks nothing across five setup/unload cycles on a real loop
   with a real executor.**
   `python3 tools/audit/round4/D1/real_loop.py --cycles 5 --inflight` →
   `leaked_tasks=0 leaked_listeners=0 leaked_futures=0
   surviving_coordinators=0 referrers_max=0 escaped_exceptions=0
   first_cycle_ok=5`. The harness is demonstrably sensitive: with
   `--break release` (which neuters `_release_registrations`) the same run
   reports `leaked_listeners=6, surviving_coordinators=3`. The config enables
   both hass-level state subscriptions (peak guard, defrost watch)
   deliberately — with them off the leak metric cannot move and a zero means
   nothing.
2. **A solve in flight when the entry is unloaded is discarded, not landed on
   the torn-down instance.** Same command →
   `inflight_unloads=5, inflight_solves_discarded=5,
   inflight_plan_landed_after_unload=0`. All five solves return `"shutdown"`,
   which is the `#237` guard at `coordinator.py:4630` firing.
3. **2400 seeded store mutants: no exception escapes a loader, and no failure
   repeats on the next cycle.**
   `python3 tools/audit/round4/D1/store_fuzz.py --mutants 200` →
   `exception_escaped_mutants=0, repeat_failure_mutants=0,
   multi_log_mutants=0` across 12 stores.
4. **Nine of the twelve stores publish nothing non-finite under any of their
   200 mutants.** Same command, per-store table: `thermal_learning`,
   `ledger`, `accuracy`, `energy`, `snapshots`, `manual_plan`, `dhw_draws`,
   `dhw_legionella`, `away`, `boost` all report `nan_pub=0`. Only
   `price_model` (6) and `dhw_profile` (10) leak a non-finite into the
   published payload.
5. **The price-shape learner cannot itself produce the NaN D1-01 needs.**
   `price_model.py:observe_day:137` rejects a non-finite day and `:143`
   rejects a daily mean at or below 1e-6, so the writer is strictly stronger
   than the reader. Read against `store_fuzz.py`'s `thermal_learning` column
   (`nan_pub=0` over 200 mutants) for the analogous clamped path.
6. **`async_run_optimization` cannot latch `_optimization_running`.** The
   reset is in a `finally` (`coordinator.py:4722`); the 2400-mutant run never
   wedged a second cycle (`repeat_failure_mutants=0`).
7. **Staleness: an `unavailable`, `unknown`, stale or future-stamped input is
   never published as measured.** `/tmp` probe driving
   `_update_current_state` + `_build_data_dict` across six input states:
   a 10 h-old stamp gives `stale_inputs=['indoor_temp_entity']` and
   `input_ages_minutes` 600.0; a stamp 6 h in the future is *also* flagged
   stale with one log line ("ahead of the host clock; treating as stale
   rather than age 0"); `unavailable` and `unknown` give
   `input_health='1 missing'` and one `input_problems` entry, and
   `binary_sensor.py:96` ORs `stale_inputs` with `input_problems`, so the
   problem binary sensor fires for all four. `indoor_temperature` falls back
   to the `ThermalState()` default rather than to a remembered reading, which
   is the documented behaviour, not a silent measurement.
8. **The reload plan handover is bounded at one payload per entry.**
   `real_loop.py --cycles 5` → `handover_keys_retained=2` (one payload plus
   one stamp, for one entry) and `hass_data_keys=4` regardless of cycle
   count; `_take_fresh_handover` pops unconditionally and drops a record
   older than one update interval.
9. **Executor boundary: the solve gets frozen copies.**
   `coordinator.py:_solve_snapshot` deep-copies `_current_state`,
   `_thermal_params` and `_opt_config` and builds a fresh
   `HeatPumpOptimizer` over its own `ThermalModel`, so no `self._*` the loop
   writes is shared with the worker. Driven 5× with an unload landing inside
   the executor await (non-finding 2) with `escaped_exceptions=0`.

### Disproved leads and harness gaps named

* **`tests/hastub/homeassistant/helpers/update_coordinator.py`'s
  `async_refresh`, `async_config_entry_first_refresh` and
  `async_request_refresh` only increment a counter — they never call
  `_async_update_data`.** So no test in this tree runs an update cycle
  through the coordinator base class, and `_skip_solve_once`, which
  `__init__.py` sets and comments as consumed "on the next refresh", is never
  consumed in the suite. `real_loop.py` drives `_async_update_data` twice per
  cycle explicitly for this reason, which is stated in the file. This is a
  harness gap, not a tree defect, and it is recorded here so the next auditor
  does not spend the same hour on it. It plausibly belongs to D3.
* **`FakeHass.async_add_executor_job` runs inline and `async_create_task`
  closes the coroutine.** Confirmed at `tests/harness.py:146-156`. Every
  lifecycle number in this report comes from `RealHass`, not `FakeHass`.
* **A bare `NaN` written back to a store is a stub artefact, not a real-HA
  one.** The `homeassistant.helpers.storage` stub round-trips through
  Python's `json`, which emits and re-reads the non-standard `NaN` literal;
  orjson, which real Home Assistant uses, does not. That is why
  `corrupt_persisted_mutants=91` is quoted as corpus context rather than as a
  finding, and why both findings above are reproduced from strict JSON.

## Harnesses

| file | what it produces |
|---|---|
| `tools/audit/round4/D1/real_loop.py` | real-loop, real-executor lifecycle; `--inflight` unloads mid-solve; `--break release\|tasks` is the in-process perturbation |
| `tools/audit/round4/D1/store_fuzz.py` | 200 seeded mutants × 12 stores, three properties per mutant |
| `tools/audit/round4/D1/price_prior_zero.py` | D1-01, with its matched control, null control and 24-cell sweep |
| `tools/audit/round4/D1/accuracy_wipe.py` | D1-02, with its null control and a second mutant shape |

## What I could not finish

* **DST and frozen-clock staleness.** D1.md step 3 asks for `dt.freeze` jumps
  forward and back and the `tests/dst_checks.py` transitions against every
  "age" sensor. I drove six input states (non-finding 7) but no clock jump
  and no DST fold. Untested.
* **A price list that stops updating and a weather entity returning an empty
  forecast.** Not driven.
* **The guard audit (D1.md step 5) was not exhaustive.** `coordinator.py`
  alone is 10 451 lines; I injected exceptions only through the store loaders
  (2400 mutants) and read the two guards the findings sit on. The other
  `except Exception` sites were not each driven with an injected exception.
* **The executor-boundary race (D1.md step 4) was not enumerated.** I
  verified the snapshot is a deep copy and that an unload inside the executor
  await is handled, but I did not list every `self._*` the solve thread reads
  against every loop-side writer, nor mutate each writer mid-solve.
* **`dhw_profile` publishes a NaN under 10 of 200 mutants** (`cooling_rate`
  and `hourly_profile` bins reaching `data.dhw_hold_hours` and
  `data.dhw_usage_profile`). Only one of those ten is strict-JSON reachable
  and all ten carry two log lines, so I did not build the targeted harness
  that would turn it into a finding. It is the most likely third finding and
  the next hour should go there.
