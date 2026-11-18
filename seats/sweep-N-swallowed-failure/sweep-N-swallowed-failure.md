# Class sweep, round 11: N-swallowed-failure

Baseline: `origin/handoff/audit-r11-register` at 28b864af. `dev/audit/config/bugclasses.json` has no entry for
this class (new this round; nearest N-silent-zero, which returns a success-shaped value where this class
records nothing visible).

**Property.** A failing operation the integration catches and does not re-raise leaves a record at WARNING
or higher, or reaches the user some other way.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/swallowed_sweep.py`

The universe is every except handler of `tools/audit/enumerate.py d1-excepts`: 257 handlers.

A handler is a seam when its body does not re-raise and its highest record is below WARNING. Records counted:

- direct `_LOGGER` calls;
- `log_held` (a latched WARNING);
- one level of package helpers the handler calls by name (for example `_weather_fetch_failed`).

Each seam is joined to the finder's executed arms, which ran at 92d38ecb: the lifecycle injection
(`D1/s3/out/inj_*.jsonl`, WARNING+ records added over the fault-free control) and the local arm
(`m5_table.tsv`). The join key is (file, function, rank within the function), because line numbers moved
between the two trees.

`RESULT handlers=257 seams=206`.

- **Positive control**: every judged handler is a seam — all 17 `persist_seams.py` handlers (D1-s3-05) and
  all 7 `silent_broad.py` handlers (D1-s3-07).
- **Null control**: `--null` uses a fixture with four handlers:
  - a save logged at WARNING;
  - a re-raising save;
  - a narrow `float()` parse;
  - a call whose error is returned to the caller.

  Unexplained seams: 0.
- **Perturbation**: `--perturb` reads the ledger save's DEBUG as WARNING, a one-line change. Seams go
  206 → 205 and persist seams 18 → 17.

## Dispositions (206 seams)

| disposition | count |
|---|---|
| instance, judged (D1-s3-05: 17, D1-s3-07: 7) | 24 |
| instance, beyond the findings | 23 |
| guarded | 25 |
| not applicable | 134 |

### instance beyond the findings

| handler | function | probe | what goes unseen |
|---|---|---|---|
| `config_flow.py:781` | `_prefilled_values` | local | a raising default callable drops its prefill with no record |
| `coordinator.py:10712` | `HeatPumpOptimizerCoordinator._maybe_refresh_price_tile` | local | price tile refresh failing at DEBUG |
| `coordinator.py:1086` | `_replay_interval` | lifecycle | learning replay simulation failing at DEBUG on every interval |
| `coordinator.py:2210` | `_with_sensor_advisor` | lifecycle | sensor advisor ranking skipped at DEBUG on every pass |
| `coordinator.py:3055` | `_stored_fuse_advisor` | local | stored fuse advisor read returns None with no record |
| `coordinator.py:4174` | `HeatPumpOptimizerCoordinator._async_setup_ecl110_state_subscription` | static | ECL110 MQTT state subscription unavailable at DEBUG (no arm reaches it: static probe only) |
| `coordinator.py:4581` | `HeatPumpOptimizerCoordinator._async_load_thermal_learning` | lifecycle | load family: learned thermal parameters not loaded, DEBUG only; the learner restarts from defaults |
| `coordinator.py:8477` | `HeatPumpOptimizerCoordinator._async_load_manual_plan` | lifecycle | load family: stored manual plan not loaded, DEBUG only |
| `coordinator.py:9255` | `HeatPumpOptimizerCoordinator._track_curve_comfort` | local | heat-curve comfort tracking returns with no record |
| `dhw_learning.py:254` | `DhwProfileLearner.async_load_profile` | lifecycle | load family: learned DHW profile not loaded, DEBUG only |
| `dhw_planner.py:1604` | `DhwPlanner._plan_dhw_min_cost` | lifecycle | DHW cost LP raising falls back to the greedy planner at DEBUG on every plan |
| `diagnosis.py:151` | `diagnose_record` | static | interval diagnosis failing at DEBUG (no arm reaches it: static probe only) |
| `duty_switch.py:504` | `_load` | local | load family: duty-switch record not loaded, DEBUG only |
| `legionella.py:227` | `LegionellaGuard.async_load` | lifecycle | load family: legionella timestamp not loaded, DEBUG only |
| `off_restore.py:343` | `async_forget` | local | store removal failing at DEBUG: the off-restore store survives its forget |
| `open_meteo.py:400` | `OpenMeteoSolar._fenced` | local | Open-Meteo response unparseable at DEBUG |
| `open_meteo.py:421` | `OpenMeteoSolar._get_json` | local | Open-Meteo request failing at DEBUG |
| `optimizer.py:4000` | `HeatPumpOptimizer._co_optimize` | lifecycle | DHW/space co-optimization pass skipped at DEBUG on every solve |
| `optimizer.py:496` | `_avoid_priced_switches` | static | duty-switch candidate pass skipped at DEBUG (no arm reaches it: static probe only) |
| `optimizer.py:705` | `_commit_runs` | lifecycle | run commitment failing at DEBUG on every solve; the projection ships |
| `setpoint_check.py:88` | `evaluate` | lifecycle | set-point consistency check skipped at DEBUG on every pass |
| `store.py:690` | `load_mapping` | lifecycle | load family: every restore built on load_mapping (boost, away, pump arbiter) starts from nothing on a failing load, recorded at DEBUG |
| `whatif.py:213` | `steady_pair` | static | what-if steady pair failing at DEBUG (no arm reaches it: static probe only) |

Probe kinds:

- **lifecycle**: `excepts_inject.py --only <id at 92d38ecb>` fires the fault on every pass. Over the
  fault-free control, the armed phases add 0 WARNING+ records.
- **local**: the local arm enters the try and contains the fault, and the handler makes no WARNING+ record.
- **static**: no arm reaches the handler. The seam is listed by the enumerator only, and an executed probe is
  still owed.

Two families stand out:

- **Load family** (6). Every load handler in the store layer records at DEBUG: `store.load_mapping` (under
  boost, away and the pump arbiter), thermal learning, manual plan, DHW profile, duty switch and legionella.
  A persistently failing load restarts the learner or the state from defaults with no visible record. This is
  the load-side twin of D1-s3-05's saves.
- **Feature passes** (13). A solver or advisor pass that fails on every cycle and falls back at DEBUG: the
  DHW LP's greedy fallback, co-optimization, run commitment, the set-point check, the sensor advisor, learning
  replay and the Open-Meteo fetch.

### guarded and not applicable

- **guarded** (25).
  - The injected fault adds WARNING+ records downstream (lifecycle arm, 11).
  - The fault escapes its phase.
  - The handler hands the error to a caller that reports it: the debug collection's outcome, the
    `cannot_connect` form error, the process worker's pickled error raised by its parent, or
    `off_restore._restore_baseline`'s error logged by `async_restore`.
  - The executor fallback computes the same plan, and the worker failure is surfaced at WARNING.
- **not applicable** (134).
  - 118 narrow catches around a parse or coercion with no awaited operation: bad input becomes a default, a
    success-shaped value, which is N-silent-zero's mechanism.
  - Teardown of a worker being discarded, or cleanup inside a path that re-raises.
  - A notice or repair issue that fails to clear and stays visible.
  - Cosmetic labels.
  - `_raise_cop_issue`'s success-shaped 0.0 (N-silent-zero).

Each seam's row is in the JSON's `other_seams`.

## Barrier (proposed; `barriered: false`)

Add a `tests/entities.py` AST rule over `d1-excepts`: a broad handler, or one whose try body awaits, that does
not re-raise must record at WARNING or higher, either once and latched through `log_latch.log_held` or through
a named helper. Exemptions are listed with a reason, the way the not-applicable rows above are. This is a
static pass over 257 handlers and costs well under a second. The executed arm stays `excepts_inject.py`.
