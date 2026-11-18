# D1-s2 — round 10, D1 (robustness), steps M2 (store fuzz) and M3 (staleness)

Baseline 17f1c55fad1b. Box B4, shared (load1 26–45 throughout; every number
below is a count, contention-immune). Interpreter: hpo-seats/r9fix-lanerunner
python 3.14, `PYTHONPATH=tests/hastub`, run from the export root. Real loop:
`store_fuzz.py:RealHass` subclasses `tests/harness.py:FakeHass` so
`async_create_task` schedules on asyncio and executor jobs run on a
ThreadPoolExecutor (the FakeHass trap). Exposure: none.

## Method

M2: two healthy real cycles (`_async_update_data`, prices injected through a
replaced `_fetch_tibber_prices`) plus `_async_save_ledger` populate the stub
disk with 8 stores (accuracy, away, dhw_legionella, energy, ledger,
price_model, snapshots, thermal_learning). Per store, 200 seeded mutants
(type swap, delete, huge, negative, wrong nesting, string, truncation, null,
dict-for-list, bool) are written, a fresh coordinator is built, its spawned
loads drained, and one cycle run (a second when anything failed). Clock-ahead
arm (`CLOCK_AHEAD=1`): every ISO instant in each store rewritten 30 days ahead,
then restart.
M3: future `last_reported` stamps, a price list that stops updating, an empty /
absent weather forecast, unknown indoor via stale stamp; frozen clock via
`dt.freeze`.

## Findings

### D1-s2-01 (M2, low) — a healthy snapshot store is rewritten on every restart
`snapshot_bound.py`: after two healthy cycles and a plain restart, the
snapshots store's `_bound_instants` rewrites 5 legitimate future `lead_pending`
due-instants (`snapshots/0/learners/accuracy/lead_pending/*/0`) to now and logs
5 WARNINGs "ahead of the clock". The snapshot store is built with `lead=0`
while it embeds the accuracy learner, whose store carries
`lead=max(LEAD_BUCKETS)` (control: accuracy store rewrites 0). A rollback to
that snapshot restores promises due "now", scored against the wrong
measurement. Perturbation `--perturb` (snapshot store lead = 24 h): 5 → 0.
Property: a store whose payload embeds another store's payload must bound
instants with at least the embedded store's lead. Seam rule:
`grep -n "QuarantiningStore(" custom_components/heatpump_optimizer/*.py` and
compare each store's `lead` with the leads of the payloads it embeds.

### D1-s2-02 (M3, high) — a price list that stops updating publishes and books its last entry forever
`stale_price.py`: last hourly entry starts at T0+3 h; at T0+5, 8, 30, 50 h,
4/4 cycles publish `current_price=1.3` and book `_pending_prediction["price"]=1.3`
(what the settlement charges), with no failed cycle. `_current_spot_price`
treats the last entry as covering [start, ∞). Control: covered cycles 2/2
publish their own price. Perturbation (last entry covers one slot): 4 → 0.
Trigger in production: a source that answers `ok` with a non-advancing list
(e.g. a price entity whose integration stalled; `pull_prices` has no coverage
check). Property: a price whose slot has ended is never "current". Seam rule:
`grep -n "_get_current_price()\|_current_spot_price()" custom_components/heatpump_optimizer/coordinator.py`.

### D1-s2-03 (M3, low) — the no-forecast WARNING fires every cycle
`weather_warn.py`: `_weather_series` logs "No weather forecast available" at
WARNING once per cycle: 4/4 cycles both with no weather entity and with an
entity returning an empty forecast (control, 48 rows: 0). The fetch-failure
path itself is latched (log once per outage); this sibling line is not —
288/day. Perturbation (latch): 4 → 1.

## Non-findings

- Store fuzz: 8 stores × 200 mutants = 1600; load exceptions 0, cycle-1
  failures 0, repeated failures 0 (`store_fuzz.py 200 <store>`; fuzz_[abc].out).
  Limitation: the `log_gt3` column is confounded by D1-s2-01 and D1-s2-03
  (a healthy restart already logs > 3 WARNINGs), so "one log line" was not
  separable; no positive control proves the harness counts a cycle failure.
- Clock-ahead across a restart: 8/8 stores restart and cycle cleanly
  (`CLOCK_AHEAD=1 ... store_fuzz.py 1`; clock_ahead.out).
- Future `last_reported`: 0 failed cycles at +0.05 s, +1 s, +60 s; the input
  goes stale and the indoor sensor is gated by `_reading_ok`
  (`future_stamp.py`). The warning repeats per cycle (2/cycle) by design of
  #775 while the stamp is ahead; not raised as a finding.
- Stale indoor publishes `indoor_temperature=21.0` (the model default) in the
  payload, but `IndoorTempSensor`, climate and the mold binary sensor all gate
  on `reading_ok`.

## Unfinished
- M2: manual_plan, dhw profile/draws, boost, pump_arbiter, notifier and debug
  stores were not populated by two cycles and were not fuzzed.
- M3: DST transitions and the watchdog/age sensors under a backward clock jump
  were not driven.

## Harnesses
store_fuzz.py, snapshot_bound.py, stale_price.py, weather_warn.py, future_stamp.py
