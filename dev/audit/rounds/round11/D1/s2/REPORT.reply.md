# D1-s2 report: audit round 11, D1 (robustness and stability), steps D1.M2 and D1.M3

**Result:** both steps are complete: 41 of 41 store lines and 51 of 51 input slots examined, with nothing left unreached. There are 6 findings and nothing unfinished.

- **Seat and tree:** D1-s2 on box B4, run against the export of baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`.
- **Where the files are:** everything is in `dev/audit/rounds/round11/D1/s2/` inside the export at `<HOME>/hpo-orch/r10s6/r11/plant-export/audit-r11-baseline`.
  - `REPORT.json`, built to `finding.schema.json` and checked against its rules by a local checker (no `jsonschema` module was available).
  - The six finding files under `findings/`.
  - The 17 harnesses listed below.
- **Exposure:** none. I did not read `docs/`, GitHub or the twin seat's directory.

## Method
- **Shared rig (`d1s2_lib.py`):**
  - It subclasses `FakeHass` so `async_create_task` schedules on a real asyncio loop. The constructor's store loads and every task a cycle spawns actually run, and their exceptions are collected.
  - It hooks `_best_effort_cycle_step` to count fenced failures, because repeats of those only log at DEBUG.
  - `_await_optimize` is memoised: the first solve is real and later cycles reuse it. `--real-solve K` re-runs K mutants per store with a real in-process solve.
  - Price patches sit below the real `_fetch_tibber_prices`, so its own error handling runs.
- **D1.M2 (stores and upgrades):**
  - `store_fuzz.py` runs 200 seeded structural mutants on each of the 17 stores (18 operators). Each mutant goes through the real loaders and two real cycles.
  - It is classified against that store's healthy-restart control, so warnings a healthy restart already logs are subtracted.
  - Extra arms:
    - `nan_boundary.py`: every numeric leaf of every store.
    - `config_fuzz.py`: config entry versions v1 to v6, 200 mutants each.
    - `upgrade_fuzz.py`: ledger v1→2 and defrost v1→2.
    - `clock_save.py`: a writer clock 48 h ahead across a restart, and a save during the load.
    - `hold_restore.py`: a hold from the previous run carried to the first actuator write.
    - `off_restore_race.py` and `boost_settle.py`.
- **D1.M3 (inputs):**
  - `staleness.py` drives all 51 slots through healthy, unavailable, back within one interval, unknown, future-stamped, clock back 2 h and silent for 7 h.
  - 24 slots reach the coordinator's watchdog. The other 27 go through their own readers: `consumers.py` names those readers and `staleness_unread.py` drives them.
  - Feed and edge-case arms:
    - `pv_stale.py` and `weather_stuck.py`: the PV meter and the weather forecast going stale.
    - `price_weather.py`: a price fetch that raises while prices still cover now, a price list that stops updating, and an empty forecast.
    - `presence_dst.py`: presence changing between updates, DST spring and autumn, and host clock jumps.
    - `booked.py`: the published and booked values while the meters are unavailable.

## Carried over from round 10
- **C1 (D1.M2) – examined.**
  - manual_plan, DHW profile and draws, boost, pump arbiter, notifier and debug are all fuzzed with populated payloads. Boost, manual_plan and away each carry a running hold.
  - A positive control exists: `store_fuzz.py --control` reports `cycle_fail,repeat_fence`.
  - The one-log-line check now subtracts the warnings a healthy restart already logs.
- **C2 (D1.M3) – examined.**
  - DST: freezing the clock in Europe/Stockholm across both 2026 changes gave 0 wrong cells of 6.
  - A backward host-clock jump on the watchdog (24 slots) and on the age readings published no negative age.

## Findings
| id | step | severity | claim | harness, then null control / perturbation |
|---|---|---|---|---|
| D1-s2-01 | M2 | high | `store._poisoned` misses NaN, because `abs(nan) >= ABSURD` is False. In 3 of 515 single-leaf "NaN" substitutions (comfort learned_weight and evidence, dhw cooling_rate) the NaN reaches live or published state. The next save then writes a bare NaN token, and the following restart drops the whole accuracy and snapshots documents. `tests/finite_boundary.py`'s own nan and str-nan checks print FAIL on this tree. | `nan_boundary.py`, 3 → `--sub Infinity` 0 / `--fix` 0 |
| D1-s2-02 | M3 | high | `_pv_measured_production` bypasses `InputReader`, so the declared 30-minute limit never applies. 6 of 6 ages past the limit, and a report stamped 90 min in the future, are still published as `pv.measured_production_kw` and seed step 0 of the PV forecast. | `pv_stale.py`, 6 → `--fresh` 0 / `--fix` 0 |
| D1-s2-03 | M3 | high | A non-empty forecast that has stopped advancing counts as a recovered fetch. In 5 of 5 cells where every row is in the past, `weather_forecast_stale_hours` is published as None (fresh), and the plan holds the last row's 0.7 °C flat against a live -3 °C. | `weather_stuck.py`, 5 → `--advancing` 0 / `--fix` 0 |
| D1-s2-04 | M2 | medium | `off_restore._armed_record` sets `loaded = True` before its read lands and takes no lock. A concurrent `async_restore` therefore sends no restore write and saves `{"armed": {}}` over the persisted baseline (2 of 2 consequences). | `off_restore_race.py`, 2 → `--serial` 0 / `--fix` 0 |
| D1-s2-05 | M2 | medium | Raw numeric config reads (`_tabled_values`, `from_config`, `comfort_band.effective`) plus a migration that only stamps the version mean one wrong-typed option fails setup or every cycle. That happened in 142 of 1200 v1–v6 mutants (21 to 26 per version). | `config_fuzz.py`, 142 → healthy controls 0 / `--fix` 0 |
| D1-s2-06 | M2 | medium | A stored `boosted_h` that is finite and below `ABSURD` but outside `timedelta`'s range raises `OverflowError` in the boost restore task on every restart (8 of 10). The space overlay's start is lost and the boosted time becomes 0 instead of unknown. | `boost_settle.py`, 8 → control 0 / `--fix` 0 |

Every finding's number is a count, so none is provisional. `load1` was quoted at 18 to 300.

## Checks that held
- **Store fuzz:** 3400 mutants gave 0 loader raises, cycle failures, repeated fences or live non-finite values. The only task raises are D1-s2-06.
- **Two log lines for one bad leaf:** this happens only when a far-future ISO string is planted in a field that is not an instant. `_bound_instants` and the loader's quarantine each log once.
- **Old-version records:** ledger v1→2 and defrost v1→2 load cleanly, both healthy and under 200 mutants each.
- **Clock 48 h ahead across a restart:** no cycle failed and no extra future instants were published.
- **Save during the load:** the coordinator's savers wait for their read. Turning that wait off raises the clobbered set from 5 to 7, so the wait matters.
  - Of the 5 that differ even with the wait, only `off_restore` is a real loss (D1-s2-04).
  - `dhw_legionella` differs only in the `+00:00` suffix.
  - `duty_switch` and `pump_duty` differ only because the harness called their private `_persist` before their lazy `_load`, which production never does.
  - `dhw_draws` writes a pre-read payload, but no production path reaches that before the first interval has passed.
- **Holds from the previous run:** a hold that expired during the downtime is released, and a running hold survives. The first actuator write was `switch.turn_on`.
- **Watchdog:** unavailable, unknown, future-stamped, past-max-age and returning inputs are all handled correctly for every slot.
- **Price feed:** a fetch failure while prices still cover now is bridged. A price entity that stops updating publishes `current_price` None and `plan_stale` True.
- **Presence:** a change between updates requests one refresh per change (0 missed of 3).
- **Meters unavailable:** no measured value is published. The energy totals keep integrating the modelled draw, which is close to the meter's own delta over the outage.

## Leads
- **D1-s3, `coordinator.py:_spawn`:** an exception in a spawned load or restore task is never awaited or logged by the integration.
- **D1-s3, `store.py:_bound_instants`:** it rewrites ISO-looking strings in fields that are not instants, and logs a misleading "stored instant ... ahead of the clock" warning.

## Harnesses
`d1s2_lib.py`, `store_fuzz.py`, `nan_boundary.py`, `config_fuzz.py`, `upgrade_fuzz.py`, `clock_save.py`, `hold_restore.py`, `off_restore_race.py`, `boost_settle.py`, `staleness.py`, `consumers.py`, `staleness_unread.py`, `pv_stale.py`, `price_weather.py`, `weather_stuck.py`, `presence_dst.py`, `booked.py`.

Each runs as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/<file>` from the export root. Probes, edit scripts and logs are in `scratch/` inside that directory and are not harnesses.