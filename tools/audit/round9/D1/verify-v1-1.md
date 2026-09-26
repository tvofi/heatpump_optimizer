# Round 9 · D1 · verifier V1 (reproduce): unit D1-1

**Environment.** Evidence tree `6f51db2c` (baseline `1936d5ca`), worktree on branch handoff/audit-r9-verify-g1-v1. Python 3.14.0rc2, numpy 2.4.6, scipy 1.17.1. Machine: 4 vCPU cloud container, box G1-V1, shared with two other sub-seats. load1 during the runs was 0.84 to 3.45.

The finders' header path `/home/claude/venv-r9/bin/python` does not exist on this box, so the s1/s2 harnesses ran with `/home/claude/venv/bin/python` and the s3 harnesses with `/home/claude/venv314/bin/python`. Both are the same 3.14 interpreter.

Every command ran from the evidence-tree root with `PYTHONPATH=tests/hastub`. Every count below is contention-immune. The only timing numbers are D1-s2-02 and D1-s2-05, and each carries its load1 and thread_factor.

**Real-HA reference.** For the reach attacks I read Home Assistant core from the `homeassistant==2025.4.4` wheel, and from 2024.3.3 as well. Two facts matter:
- `hass.async_create_task` defaults to `eager_start=True` (2025.4.4 `core.py:797`).
- The core `weather.get_forecasts` service builds its own response: `{"forecast": weather._convert_forecast(native)}`, where `_convert_forecast` does `dict(_forecast_entry)` on every row (2025.4.4 `components/weather/__init__.py:703`, `:1027`).

**My harnesses** are under `tools/audit/round9/D1/verify-v1/u1/`: `arbiter_eager.py`, `pump_setpoint_types.py`, `forecast_wedge.py` and `forecast_core_shape.py`.

Tally: 14 verify, 0 weaken, 1 refute (D1-s2-01), 0 unresolved.

---

## D1-s1-01: a tz-naive persisted timestamp raises at three loader seams (medium) — VERIFY
- **Re-run** (`naive_ts.py`): snapshot_raises=21, snapshot_taken=0, curve_raises=19, comfort_override_raises=21, comfort_quiet_raises=21, sibling_raises=0. thread_factor 1.000, load1 0.84. Exact match.
- **Null control** (`--aware`): every count 0, snapshot_taken=3. **Perturbation** (`--fix`): every count 0, snapshot_taken=3. The number moves to zero as stated.
- **Attacks:** Reach: every production writer serialises an aware `now` (`snapshots.py:93`, `curve_learning.py:123`, `comfort_learning.py:205`), so a naive leaf comes only from a corrupt, hand-edited or foreign store, which is in the D1 store-corruption scope. Consequence: the failure is permanent and silent, because the heartbeat guard logs at DEBUG only (`coordinator.py:4679-4682`). Medium is earned.
- **Metric:** per seam, the number of consumer calls over 21 aware-clock days that raise after the leaf was loaded naive.

## D1-s1-02: a non-numeric snapshot temperature_bias breaks best_restore and the accuracy_drift issue (medium) — VERIFY
- **Re-run** (`snap_restore.py`): service_raises=4, missing_issue=4. **Null control** (`--control`): 0 and 0. **Perturbation** (`--fix`): 0 and 0. load1 1.01, thread_factor 1.000.
- **Attack (reach):** store corruption only, the same class as s1-01. Medium stands.
- **Metric:** of 4 non-numeric bias variants, the count where the restore service raises and the count where 10 out-of-band days raise no issue.

## D1-s1-03: one out-of-range DHW sample inflates the published p90 (medium) — VERIFY
- **Re-run** (`--day 4`): glitch −127: max_event 42.218 kWh, window p90 25.760 kWh. Control 1.073 / 1.073. Glitch 85: 8.747 / 5.677. Glitch 1e6: 231757.047 / 139054.657.
- **Other arms:** `--day 13` gives p90 1.073 for every glitch, so the exposure is the first ~10 days while max_event stays in the reservoir. `--guard` returns the −127 and 1e6 rows to 1.073, the stated downward move; the 85 row is unchanged. load1 1.53, thread_factor 1.000.
- **Attack (reach):** `coordinator.py:5526-5527` feeds `reader.read(CONF_DHW_TEMP_ENTITY).value` straight to `async_learn_dynamics`. The input reader's problems (`inputs.py:579-762`: not_configured, missing_entity, unavailable, stale, not_numeric, unknown_value, not_boolean, unknown_unit) include no range check, so a DS18B20 −127 reading reaches the learner.
- **Aggregate check:** three glitch values plus a control at two days; the −127 row alone carries the claim.
- **Metric:** after DAY+1 simulated days, the largest folded occurrence and the window p90 in kWh.

## D1-s1-04: a timestamp stored while the clock ran ahead stretches stale timeouts (low) — VERIFY
- **Re-run** (`--ahead 30`): 33 / 37 / 31. `--ahead 365`: 369 / 373 / 366. **Null control** (`--ahead 0`): 4 / 8 / 2. **Perturbation** (`--ahead 30 --clamp`): 4 / 8 / 2. load1 1.53. Exact match. Low is appropriate: the trigger is a large forward clock error later corrected.
- **Metric:** per seam, the first day index at which the production call acts.

## D1-s2-01: a malformed weather-forecast response wedges every later cycle (high) — REFUTE on reach
- **Re-run** (`parsers.py --n 200 --seed 9`): weather.wedged=35 of 200 (entry 27, shape 8, field 0). `--perturb row_filter`: 0. Seed 11: 30. load1 1.80–2.06. The harness prints a constant `thread_factor=1.000` rather than measuring it: a contract defect, harmless for a count.
- **Own measurement** (`forecast_wedge.py`): the mechanism is real inside the stub. For 6 non-dict or non-list shapes, 36 of 36 later healthy cycles raise. `--null` 0; `--perturb` (making `_current_humidity` skip non-dict rows) 0.
- **Reach attack** (`forecast_core_shape.py`): the finder's same 200 seeded payloads, shaped the way HA core's `get_forecasts` delivers them. Core builds each row with `dict(row)`, so an unbuildable row makes the service call itself raise; a missing or None forecast becomes `[]`. Result: **core_wedged=0 of 200**, against raw_wedged=35 in the same run; 27 payloads are rejected inside the service before they reach the integration. load1 2.87, thread_factor 1.000. Every one of the 35 wedging payloads has a non-dict row or a non-list forecast, which real HA core cannot deliver (2025.4.4 `weather/__init__.py:703`, `:1027`). The dict-row field mutations wedge 0.
- **Vote:** refute, executed number 0 of 200 under real-HA delivery. The store-before-validate / read-before-refetch ordering is real but stub-only. If the judge keeps it as defence in depth, severity low.
- **Metric:** of 200 seeded payloads after core-style shaping, the count whose second cycle (healthy forecast restored) still raises.

## D1-s2-02: finite-but-absurd forecast values reach the solve unbounded (medium) — VERIFY
- **Re-run** (`solve_poison.py --cap 60`): capped_cases=3 of 10 (wind 1e308, 1e12 and 1e20, each at 60.07 s, ratio 24.8). Healthy 2.42 s, optimal. temp −1e308 and +1e308: status "failed (no usable starting point)" while cycle_ok=True. load1 3.10, thread_factor 1.000 (solve in the worker process).
- **Perturbation** (`--perturb clip`): capped_cases=0 of 10, every case optimal, ratio 0.2–1.0, load1 2.66.
- **Attacks:** contention cannot explain 25× the healthy wall under the same load. The coordinator has no solve timeout (the only one is `worker.wait(timeout=2)`). Core `_convert_forecast` float-converts without bounding, so an absurd value from a buggy source passes through; the trigger is improbable, so medium.
- **Metric:** per poisoned case, whether the real cycle is still running at 60 s; count of capped cases (wall times provisional).

## D1-s2-03: a sample count past 2**64 in the thermal-learning store fails every cycle (medium) — VERIFY
- **Re-run** (`store_fuzz.py --sweep-huge`): thermal_learning huge_leaf_wedges=6 of 58; every other store 0. load1 2.41. **Perturbation** (`--perturb learning_view_float`): 0. **Null control** (`--n 200 --seed 9`): 0 raises across 7 stores (1400 mutants).
- **Independent check:** `orjson.loads(b'[1e20]')` gives a float; `np.isfinite(int(1e20))` raises TypeError; `orjson.dumps(int(1e20))` raises "Integer exceeds 64-bit range", so the corrupt store is never re-saved.
- **Metric:** of (leaf, huge value) pairs loaded through orjson and the real loader, the count whose second cycle raises.

## D1-s2-04: five cycle-path guards swallow persistent failures at DEBUG (medium) — VERIFY
- **Re-run** (`guards.py`): silent_sites=5 of 5; each site reached=3, cycles_ok=3/3, debug_only=3. **Perturbation** (`--perturb debug_to_warning`): 0 of 5. load1 2.93.
- **Attacks:** the five `except Exception: _LOGGER.debug` sites are at `coordinator.py:4659-4666`, `:4679-4682` and `:5084-5094`. The perturbation is near-tautological and the finder has no null control. The harm is demonstrated independently: in D1-s1-01 a reachable persistent TypeError goes through the heartbeat guard every cycle, invisible at the default log level. Medium stands.
- **Metric:** per guarded callee, WARNING-or-above records plus repair issues over 3 raising cycles.

## D1-s2-05: HA stop waits out an in-flight solve before reaping the worker (medium) — VERIFY
- **Re-run** (`worker_stop.py --reps 5`): stop_latency_ratio **0.931** (min 0.856, max 1.008), inside the claimed 0.928 ± 0.1. Solve 1.873 s, in-flight stop 1.782 s, idle stop 0.008 s. concurrent_stress_processes=0, load1 2.70, thread_factor 1.000.
- **Perturbation** (`--perturb unlocked_reap`): ratio 0.005 (0.004–0.007), load1 3.17.
- **Attack (code):** the `_stop` listener (`coordinator.py:1083-1084`) awaits `_shutdown_process_pool`, which takes `_PROCESS_LOCK` (`:1047`), held by `_run_in_process` for the whole round trip (`:1094`). The ratio is load-robust; absolute times are provisional.
- **Metric:** stop-listener wall time fired 0.1 s into a real solve, divided by that solve's duration.

## D1-s3-01: a tz-less return_time wedges every cycle (high) — VERIFY
- **Re-run** (`away_naive_return.py`): failed cycles 6 of 6 in both orders; service raised 1 and 1; solves_failed 2 of 2. **Null control** (`--aware-input`): all 0. **Perturbation** (`--perturb`): all 0. load1 3.2–3.3.
- **Reach: reachable from the product's own UI.** The card sends the `datetime-local` value verbatim (`www/heatpump-optimizer-card.js:4331-4333`: `return_time: ret.value`). The service schema is `cv.string` (`services.py:133`) and the `services.yaml` example is tz-less. `coordinator.async_set_away` calls `away.expire_override` (`coordinator.py:9063`) before `away._apply_return` normalises naive values (`away.py:462`). High is earned.
- **Metric:** of 6 cycles after `set_away` with a tz-less return_time, cycles where `_resolve_away` raises, plus failed solves out of 2.

## D1-s3-02: the pump-duty arbiter re-registers its timer and listener on an unloaded coordinator (high) — VERIFY, with a caveat on the perturbation
- **Re-run** (`arbiter_unload.py`): live_registrations_after_unload=2, writes_after_unload=2. **Null control** (`--null`): 0 and 0. **Perturbation** (`--perturb`): 0 and 0. load1 3.33.
- **Reach attack** (`arbiter_eager.py`). The finder's harness schedules `hass.async_create_task` lazily; real HA starts the task eagerly (2025.4.4 `core.py:797`).

| arm | live registrations | notes |
|---|---|---|
| `lazy` (the finder's scheduling) | 2 | leaked tick writes 2 |
| `eager`, same interleaving | 0 | apply reaches `_listen` before the release, so the finder's exact sequence does not leak under real HA |
| `eager_lock`: a tick's apply holds the arbiter lock mid-write (pump reset by the user) when the state event arrives | **2** | the leak survives real-HA scheduling |
| `null`: `eager_lock` without the event | 0 | control |

- **The finder's proposed perturbation does not fix `eager_lock`:** `eager_lock --perturb` still leaves **2**, because the queued apply passed the `_entry_released` check before the release and then blocked on the lock. The fix needs a released check after the lock is acquired, or inside `_listen`.
- In `eager_lock` the leaked tick's writes read 0 at +30 min only because the stub pump "did not hold" the writes (misses=2 put every slot on retry backoff). The timer and listener are live, so a later tick past the retry writes, and the dead instance also warns and raises the repair issue.
- The leak is real under real-HA scheduling, in a narrower window than the claim implies. The consequence (actuation after unload) keeps the severity at high.
- **Metric:** arbiter timers plus state listeners that close over the coordinator and are still live after `async_shutdown` and a drain.

## D1-s3-03: pump_arbiter._load installs non-numeric set-points that raise on every apply (medium) — VERIFY
- **Re-run** (`store_fuzz.py --naive-clock`): pump_duty_repeat_fail=8, loader_raise=34. The default aware arm gives 25: the 8 plus 17 naive_dt mutants, which belong to D1-s3-01's class. `--perturb` gives 0 on both clocks; healthy_repeat is 0 everywhere.
- **Own per-cell measurement** (`pump_setpoint_types.py`, aware clock): repeat_raise_nonnumeric=8 of 18, repeat_raise_numeric=0 of 6. Raising cells: "abc", the numeric string "40", [40] and {"v":40}, on both the space and DHW set-point slots. Not raising: the mode slot, None and true. `--perturb` (drop non-numeric set-points and non-str modes after the real `_load`): 0 of 18.
- **Attack (consequence):** `coordinator._apply_action` calls `pump_arbiter.apply` unguarded as its first line (`coordinator.py:6676`), so the raise also stops the heat_pump_on/displace actuation. Corruption-only trigger; medium stands.
- **Metric:** mutants whose second `pump_arbiter.apply` after the real loader still raises.

## D1-s3-04: the climate entity publishes the away setback as the user's target during the solve (medium) — VERIFY
- **Re-run** (`climate_midsolve.py`): max_published_deviation=5.00 C, after_solve_deviation=0.00. **Null control** (`--null`): 0.00. **Perturbation** (`--perturb`): 0.00. load1 3.1.
- **Method attack:** the harness injects the mid-solve write by calling `_async_peak_guard_transition()` inside a wrapped `_await_optimize`; it did not reproduce the write end to end from a real state event. In real HA the solve's executor await lasts seconds to over a minute, and any event-driven `async_update_listeners` in that window publishes the value, so it is reachable. The wrong value is transient, so medium rather than high.
- **Metric:** the maximum difference between the climate `target_temperature` and the configured target over listener writes made during the solve await.

## D1-s3-05: boost's "two-hour maximum" is an absolute instant (medium) — VERIFY
- **Re-run** (`boost_unbounded.py`): jump0 2.00 h, jump1 3.00, jump6 8.00, jump24 26.00, restore_2099 72.00 h (the cap). **Perturbation** (`--perturb`): 2.00 / 0 / 0 / 0 / 0. load1 3.19.
- **Attack (reach):** the triggers are a backward clock step or a corrupt store; the user can switch boost off by hand, so medium rather than high.
- **Metric:** hours, sampled every 15 min up to 72 h, during which `boost.apply` sets `boost_space`.

## D1-s3-06: FrequencyMap.from_dict admits unbounded ratios and out-of-range deciles (medium) — VERIFY
- **Re-run** (`freq_map_store.py`, seed 9): stuck_after_day=10 of 200 (huge_ratio 3, neg_key 7). healthy_stuck=0; the healthy map recommends 80.0 Hz. **Perturbation** (`--perturb`): 0.
- **Leave-one-out on the seed:** seed 3 gives 9 (neg_key 6, huge_ratio 3); with `--perturb`, 0. load1 3.19. Store corruption only; medium stands.
- **Metric:** mutants whose clipped `recommend(3 kW)` after 96 truthful folds delivers under 50 % of the target.
