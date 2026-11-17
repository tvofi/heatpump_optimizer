# D1-s3 round 11 report: robustness steps M5 (exception handlers) and M6 (external-input parsers)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Interpreter: venv-ci python 3.14.7 with `PYTHONPATH=tests/hastub`. Measured in the export tree only; no GitHub calls; no `.md` file written.

**Seven findings (two in M6's parsers, five in M5's handlers).** M5 examined 227 of its 257 handlers, so its coverage is incomplete: the other 30 were not reached. M6 examined all 31 of its parser lines. Every count is exact and contention-immune. No timing figure is a result; the shared box ran at load1 75–290 throughout.

## Coverage
| step | enumerator | universe | examined | not reached | redispatched |
|---|---|---|---|---|---|
| D1.M5 | `python3 tools/audit/enumerate.py d1-excepts` | 257 | 227 | 30 | C1 and C2 examined |
| D1.M6 | `python3 tools/audit/enumerate.py d1-parsers` | 31 | 31 | 0 | C3 examined |

- **C1:** round 10 left M5 without a denominator; it now has one (above).
- **C2:** every reachable handler had an exception injected; 30 remain not reached and are listed below.
- **C3:** examined in full: the ECL110 handler and parser plus the subscribe site, pump-signal state parsing, the weather forecast through `_fetch_weather_forecast`, and the Open-Meteo `async_refresh` JSON path.

**M5 not reached (30), also listed in REPORT.json under `unfinished`:**
- climate.py:300
- coordinator.py: 10876, 11230, 11237, 1919, 2107, 4173, 5992, 7113
- diagnosis.py: 93, 103, 114, 151
- disinfection.py:225
- draw_range.py: 388, 456
- heat_curve.py:397
- off_restore.py: 218, 252
- optimizer.py:496
- repairs.py:54
- services.py: 657, 991, 1144, 1265
- whatif.py: 127, 213
- wood_fuel.py: 129, 369, 501

## Method
- **How the fault is injected.** `d1s3hook.py` rewrites the integration's own modules at import. It compiles a raise of the handler's own caught type (RuntimeError for a broad handler) at the top of each try body, one guard per listed handler, and adds entry/exit probes inside each handler. My first design raised from a trace function; it is unusable because CPython switches tracing off after the first raise.
- **Lifecycle arm** (`excepts_inject.py`, 107 handlers). Each handler gets a fault on every pass across setup, refresh, refresh, diagnostics, unload, restart, setup, refresh. It runs on a real asyncio loop with a thread pool and scheduled tasks, in both process-worker and in-process solve modes. A fault-free refresh (or setup retry) at the end checks recovery. Log records are counted over a fault-free control run.
- **Local arm** (`local_inject.py`, 120 more handlers). One injection each, the first time a call reaches the handler. The calls come from 11 test scripts plus `drivers_misc.py`.
- **Tables:** `classify.py` sorts the lifecycle results; `m5_table.py` writes the per-handler verdicts to `out/m5_table.tsv`.
- **Peer waits:** `dev/audit/harnesses/silent_peer_waits.py` and `peer_wait.py`.
- **M6:** `parsers_fuzz.py` makes 914 direct parser calls plus full refresh cycles for weather, Tibber, Open-Meteo, ECL110 and the pump signals.

## Findings
| id | step | severity | class | finding | value (perturbed) | null control |
|---|---|---|---|---|---|---|
| D1-s3-01 | M6 | medium | P1 | `inputs.parse_bool` reads "nan"/"inf"/"1e309" as True, so the published state shows fault=True and defrosting=True and learning freezes as `pump_fault` | 10 (0 with `--perturb parse_bool_finite`) | state "0" → 0 |
| D1-s3-02 | M6 | low | P1 | `_parse_ecl110_state` takes a JSON bool as a displacement (`true`→1.0, `false`→0.0) | 3 (0 with `--perturb ecl110_refuse_bool`) | numeric payloads still accepted, 2 of 2 |
| D1-s3-03 | M6 | medium | P1 | An Open-Meteo sample stamped 0001-01-01 makes `IrradianceSeries.mean_over` overflow outside the fetch fence, so every solve fails while the update still reports success | 3 failed solves (0 with `--perturb openmeteo_overflow_guard`) | healthy body → 0 |
| D1-s3-04 | M5 | medium | P2 | In `_run_in_process`, the transport-failure path calls `worker.wait()` with no timeout while holding `_PROCESS_LOCK`; the timeout path beside it bounds the same wait | lock held after the 8 s cap = 1 (0 with `--perturb`) | timeout path returns and frees the lock |
| D1-s3-05 | M5 | medium | new | All 17 persist handlers log a failing save only at DEBUG (`persist_seams.py`) | 10 of 10 reached (9 with `--perturb`) | control run; the weather handler warns once |
| D1-s3-06 | M5 | low | N-log-flood | `_async_update_data`'s generic arm logs ERROR with a traceback on every cycle of a persisting failure | 3 (0 with `--perturb`) | recovery refresh adds no such record |
| D1-s3-07 | M5 | low (hygiene) | new | Seven broad handlers swallow a fault with no record at any level | 7 of 11 reached (6 with `--perturb`) | 4 helper-logging handlers counted as recorded |

Commands, measured symbols, property statements and seam rules are in `findings/D1-s3-0N.json`.

## Checks that held
- **Weather forecast:** 10 hostile variants × 3 cycles gave 0 failed updates, no non-finite values, and at most one warning per outage.
- **Tibber:** 14 hostile bodies never failed an update while the last prices still covered now. No warning was added after the first cycle.
- **Open-Meteo:** the 7 other hostile bodies caused 0 failed solves and one warning each.
- **ECL110:** 0 of 16 payloads raised, a refused subscription was contained, and the next cycle completed.
- **Unit calls that raised an unexpected error type (121 of 914), and why none is a finding:**
  - Most are non-text input to config-text tokenizers whose callers always pass validated text.
  - `pull_prices` raises AttributeError on hostile Tibber JSON, but `_fetch_tibber_prices`' broad handler contains it.
  - `debugger._read_stores` and `_parsed` raise RecursionError on 100k-deep JSON. Those files are the integration's own stores, outside M6's scope.
- **Silent process worker:** times out at `PROCESS_REPLY_TIMEOUT_S` (1800 s), and the stop path frees it at once.
- **Recovery:** every lifecycle-injected handler recovered on the fault-free refresh or setup retry (no-recovery = 0).
- **Per-cycle worker-fallback warning** (coordinator.py 2069/2093/2097/2328): documented deliberate design in `_note_worker_fallback`.
- **Pass-through re-raisers** (6141/6189/6976) work as designed.
- **Setup-retry warnings** (6976/6978/6980, const:1491, price_model:749) are one record per Home Assistant setup retry, and the retry recovers.

## Harnesses
All under `dev/audit/rounds/round11/D1/s3/`:
- Shared code: `wl.py` (workload), `d1s3hook.py` (injection rewrite)
- M5: `excepts_inject.py`, `local_inject.py`, `run_local.sh`, `run_features.sh`, `drivers_misc.py`, `classify.py`, `m5_table.py`, `persist_seams.py`, `persist_family.py`, `silent_broad.py`, `log_flood.py`, `peer_wait.py`
- M6: `parsers_fuzz.py`
- Raw outputs: `out/`

## Leads (not findings; no harness)
- **D1-s2:** a weather forecast whose rows carry garbage, year-1 or year-9999 datetimes is accepted as fresh and aligned by position; its own timestamps are never used to judge staleness.
- **D1-s2:** the store-loader field fallbacks reset a corrupt field with no log line at any level (accuracy, comfort, curve and DHW learners). M2 requires "one log line".
- **Unknown seat:** at this baseline, `tests/entities.py` exits with KeyError `'house_heat_loss_coefficient'` at line 9634 and prints 32 FAIL lines, with no injection. This also limited how far the local arm could reach.

**Exposure:** none.

Report written to <HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D1/s3/REPORT.json. It passed my own field, enum and coverage check; the jsonschema package is not installed in venv-ci, so it was not validated against the full schema. Findings are in <HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline/dev/audit/rounds/round11/D1/s3/findings/.