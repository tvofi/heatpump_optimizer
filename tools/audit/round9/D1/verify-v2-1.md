# Round 9, D1 unit D1-1: verifier V2 (independent)

Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, evidence tree 6f51db2c. Machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2, numpy 2.4.6, BLAS pinned to 1 thread, one worker process at a time; two other verifier sub-seats shared the box (load1 0.4-3.7 across runs, quoted per number). Every number below is a count or a ratio unless marked provisional.

Harnesses written by this seat: `tools/audit/round9/D1/verify-v2/u1_*.py` (15 files), each run from the repository root with `PYTHONPATH=tests/hastub`; each header carries metric, command, expected value, baseline and machine. Real-HA reach checks read the `homeassistant-2026.2.3` wheel's source (`components/weather/__init__.py`, `core.py`, `helpers/update_coordinator.py`), downloaded to a temp directory; Home Assistant was not executed.

No finding in this unit is a test-gap claim, so verifier.md step 4 applies to none.

| id | vote | severity | V2 number |
|---|---|---|---|
| D1-s1-01 | verify | medium | naive arm: snapshot_due 21/21, curve_record_day 19/21, comfort_decay 21/21 raise; aware arm 0; Cusum control 0; writer_naive_stamps 0 of 7 |
| D1-s1-02 | verify | medium | raise_manual 5 of 8 and raise_alarm 5 of 8 bias variants ("0.3", "garbage", [0.3], {"v":0.3}, "nan"); 0 for 0.3, null, true; latch_changes_after 0 of 15 days |
| D1-s1-03 | verify | medium | 30 of 240 glitch-day x day-end cells show published p90 >10% above control (G0 10 d, G2 8, G4 6, G6 4, G8 2, G>=10 0; peak 40.53 vs 0.80 kWh); impossible (> 23.2 kWh tank ceiling) occurrence stored on 9-29 of 30 days per cell; --guard 0 |
| D1-s1-04 | verify | low | extra delay = 24*A hours at every seam: A=1 -> 24 h, A=7 -> 168 h, A=30 -> 720 h (cusum/snapshot/curve); --clamp 0 |
| D1-s2-01 | refute | low | ha_wedged 0 of 200 (ha_first_cycle_raised 0) vs raw_wedged 35 of 200 on the same seeded payloads |
| D1-s2-02 | verify | medium | sub-steps per 0.25 h step: 1 up to 500 m/s, 76 at 1e6, 75000001 at 1e12, 7.5e15 at 1e20; --clip 1 everywhere |
| D1-s2-03 | verify | medium | 6 of 14 (seam, literal) pairs raise in _learning_view: 1.9e19, 1e20, 1e308 at both cop_baseline['4'][1] and capacity_envelope['0'][1]; 1000, 2**63-1, 2**64-1, 1e19 give 0; resave refused by orjson for the same 6 |
| D1-s2-04 | verify | medium | 5 of 5 injected sites add 0 WARNING+ records and 0 repair issues over 3 cycles (control baseline 4 records), cycles_ok 3/3; real trigger (naive snapshot stamp, no injection): heartbeat raised 3 of 3, extra visible records 0 |
| D1-s2-05 | verify | medium | stop latency / job duration = 0.851 (D=2 s) and 0.940 (D=5 s), i.e. (D-0.3)/D; idle 0.001 s; --unlocked 0.001/0.000 |
| D1-s3-01 | verify | high | card datetime-local string through SERVICE_SCHEMA_SET_AWAY + async_set_away: set_away raised 1 of 2, _resolve_away raised 6 of 6; aware string 0/0; away inactive 0/0; as_local fix 0/0 |
| D1-s3-02 | weaken | medium | leaking unload offsets 1 of 31 (only k=0: the state event dispatched in the same loop step as the unload's non-yielding segment); --guard 0 of 31 |
| D1-s3-03 | verify | medium | 4 of 8 set-point variants raise on 5 of 5 apply() calls ("40", "abc", [40], {"v":40}) and the record persists; 40.0, 40, true, null 0; extra: an unknown slot key ('dhw') with 40.0 raises KeyError 5 of 5 |
| D1-s3-04 | verify | medium | climate.target_temperature read at the solve await: away 16.0 vs configured 21.0 (5.00 C), after solve 0.00; away off 0.00/0.00 |
| D1-s3-05 | weaken | low | overrun beyond BOOST_HOURS = the backward clock step exactly: J 0/1/10/60/1440 min -> 0/1/10/60/1440 min; restore keeps an until 3 h or 365 d ahead past the 2 h cap (2 of 4), 0 for <= 2 h |
| D1-s3-06 | verify | medium | stuck_at_96 = 7 of 15 phantom cells; a negative decile key never recovers (10000 of 10000 folds for every ratio incl. 0.2 kW/Hz); key 0 recovers in 7/24/46/155/6755 folds for ratios 0.2/1/10/1e6/1e308; key 5 recovers at 0 |

## D1-s1-01: verify, medium

- **V2 metric:** Per learner seam, of 21 daily consumer calls (aware Europe/Stockholm clock across DST) on an object built by production from_dict from a tz-naive stamp, the count that raise; plus tz-naive stamps emitted by the production writers under an aware clock after an as_dict/json/from_dict round trip.
- **Method:** Step 1: naive_ts.py = snapshot_raises 21, taken 0, curve 19, comfort 21/21, sibling 0 (load1 0.42, tf 1.000); --aware and --fix all 0, taken 3. Step 2: tools/audit/round9/D1/verify-v2/u1_naive_ts.py drives SnapshotRing.due / CurveLearner.record_day / ComfortLearner._decay directly (no coordinator) = 21/19/21, aware 0, --fix 0 (load1 2.26, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: count metric, n/a. gate mode: n/a. grid: n/a. null control: aware arm 0 and Cusum.load (naive->UTC) 0 in the same run. reach: production writers emit 0 naive stamps of 7 and git log -G'datetime.now()|utcnow()' finds no naive writer in snapshots/curve_learning/comfort_learning, so the input is a hand-edited or foreign store; drift.py's own comment treats a naive legacy payload as in scope, and u1_guards.py shows the heartbeat raises 3/3 cycles with 0 WARNING records in production cycles. severity: silent permanent loss of #42 snapshots plus raising comfort paths, recoverable by deleting the store: medium holds.
- **V2 number:** naive arm: snapshot_due 21/21, curve_record_day 19/21, comfort_decay 21/21 raise; aware arm 0; Cusum control 0; writer_naive_stamps 0 of 7

## D1-s1-02: verify, medium

- **V2 metric:** Of 8 JSON-legal temperature_bias leaves in one healthy snapshot loaded by production SnapshotRing.from_dict, the count for which best_restore raises (manual path; alarm path); plus observe_bias change reports over the days after the alarm-day raise.
- **Method:** Step 1: snap_restore.py = service_raises 4, missing_issue 4; --control 0/0; --fix 0/0 (load1 0.54, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_snap_bias.py = 5/8 both paths, --fix (float() under guard) 0/8, latch reports 0 changes in 15 days after trip (load1 2.71, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a (counts). null control: numeric 0.3 gives 0 in both harnesses. reach: production writes accuracy.summary() floats only, so a hand-edited store; best_restore's own docstring (#D1-05) names a hand-edited store as the case it must survive. consequence: restore service raises and the accuracy_drift issue never appears for the latched alarm; medium holds.
- **V2 number:** raise_manual 5 of 8 and raise_alarm 5 of 8 bias variants ("0.3", "garbage", [0.3], {"v":0.3}, "nan"); 0 for 0.3, null, true; latch_changes_after 0 of 15 days

## D1-s1-03: verify, medium

- **V2 metric:** Over 30 simulated days of 5-min tank samples with one -127 C sample on glitch day G in {0,2,4,6,8,10,12,20}, the number of day-ends at which production DrawStats.quantile(0.9) exceeds the glitch-free control by >10%; plus day-ends holding an occurrence above thermal mass x 100 C.
- **Method:** Step 1: dhw_glitch.py --day 4 = -127 max_event 42.218, p90 25.760 vs 1.073; --day 13 p90 1.073; --guard -127/1e6 back to 1.073, 85 C spike unchanged 8.747/5.677 (load1 1.10-1.25, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_dhw_sweep.py (evening shower series, different tank profile) as in value (load1 2.22, tf 1.000); --guard 0 of 240.
- **Attacks (verifier.md step 3 order):** contention: n/a. grid: 8 cells, range 0-10 days, dropping the most favourable cell (G0) leaves 20 day-cells over 7 cells; p90 inflation exists only while the window holds <= 10 occurrences (first ~10 days of a window's life), the stored impossible occurrence persists 40 occurrences. null control: glitch-free series in the same run. reach: InputReader.read applies no range bound to the DHW temperature (inputs.py read -> _value_in_model_units), -127/85 are real DS18B20 fault values. severity: bounded wrong readiness energy for <= ~10 days with DHW quantile targets on: medium, not higher.
- **V2 number:** 30 of 240 glitch-day x day-end cells show published p90 >10% above control (G0 10 d, G2 8, G4 6, G6 4, G8 2, G>=10 0; peak 40.53 vs 0.80 kWh); impossible (> 23.2 kWh tank ceiling) occurrence stored on 9-29 of 30 days per cell; --guard 0

## D1-s1-04: verify, low

- **V2 metric:** Per seam, extra hours (hourly ticks, UTC aware clock) before the production call first acts when its persisted stamp lies A days in the future, relative to A=0, for A in {1,7,30}.
- **Method:** Step 1: clock_jump.py --ahead 0/30/365 = 4/8/2, 33/37/31, 369/373/366; --ahead 30 --clamp 4/8/2 (load1 1.25, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_future_stamp.py via Cusum.load/release_if_starved, SnapshotRing.from_dict/due, CurveLearner.from_dict/_step_down = value (load1 2.11, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: A=0 base 6 h / 168 h / 1 h. reach: needs a clock that ran ahead and was then corrected; a Pi without RTC boots behind (fake-hwclock) and steps forward, so the ahead case is a misconfigured or manually set clock. severity low, as filed.
- **V2 number:** extra delay = 24*A hours at every seam: A=1 -> 24 h, A=7 -> 168 h, A=30 -> 720 h (cusum/snapshot/curve); --clamp 0

## D1-s2-01: refute, low

- **V2 metric:** Of the finder's 200 seeded get_forecasts payloads (seed 9), the count after which 3 further healthy-forecast cycles all raise, with the service response shaped as Home Assistant 2026.2.3's weather.get_forecasts can return it ({"forecast": [dict(row) for row in native]}, a service exception when dict(row) or iteration fails).
- **Method:** Step 1: parsers.py --n 200 --seed 9 = cycle_raised 35, wedged 35 (all 'entry'/'shape' kinds); --perturb row_filter 0 (load1 1.78-1.97, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_forecast_ha.py reuses the finder's generator: raw arm 35/35 (reproduces), ha arm 0/0 (load1 2.37, tf 1.000).
- **Attacks (verifier.md step 3 order):** reach (decisive): homeassistant/components/weather/__init__.py (2026.2.3 wheel) async_get_forecasts_service returns {'forecast': weather._convert_forecast(native)} and _convert_forecast does forecast_entry = dict(_forecast_entry) per row, so a str/None/int/list row raises inside HA's service (the coordinator's except marks the fetch failed and stores nothing) and the forecast is always a list of dicts; every wedging payload is a non-dict row or non-list forecast that real HA cannot deliver. The finder's harness serves the payload through the hastub service registry, which skips that normalisation. Dict rows with hostile values (field/dt/order/oversize kinds) wedge 0 in both arms. The in-tree fragility (_current_humidity reading a stored forecast before revalidation) is real code but unreachable through Home Assistant; at most hygiene.
- **V2 number:** ha_wedged 0 of 200 (ha_first_cycle_raised 0) vs raw_wedged 35 of 200 on the same seeded payloads

## D1-s2-02: verify, medium

- **V2 metric:** Euler sub-steps per model step returned by production ThermalModel._stability_substeps(wind, 0, 0.25 h) for default single-zone parameters, per forecast wind speed.
- **Method:** Step 1: solve_poison.py --cap 60 = capped_cases 3 of 10 (wind 1e308, 1e12, 1e20 capped at 60 s; healthy 3.06 s optimal; temp -1e308 status failed 'no usable starting point' with cycle_ok True) (load1 3.74, tf 1.000, provisional walls); --perturb clip capped 0 of 10, all optimal (load1 3.26). Step 2: tools/audit/round9/D1/verify-v2/u1_wind_substeps.py = value (count, contention-immune; load1 2.26, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: capped flag and sub-step count are load-robust; walls provisional. null control: healthy forecast and wind 500 in the same session finish. reach: HA's _convert_forecast converts wind with float() and unit conversion and bounds nothing, so a finite absurd wind from a weather integration reaches the solve. The sub-step count is linear in wind (wind_factor = 1 + wind_sensitivity*wind in effective_heat_loss_coefficient), which is the unbounded-loop mechanism. severity medium: requires an integration emitting an absurd value; consequence is a runaway worker and failed plans.
- **V2 number:** sub-steps per 0.25 h step: 1 up to 500 m/s, 76 at 1e6, 75000001 at 1e12, 7.5e15 at 1e20; --clip 1 everywhere

## D1-s2-03: verify, medium

- **V2 metric:** Per stored sample-count JSON literal at cop_baseline['4'][1] and capacity_envelope['0'][1], parsed by orjson and loaded by production _async_load_thermal_learning, whether HeatPumpOptimizerCoordinator._learning_view() raises; plus whether orjson can re-serialise the loaded counts.
- **Method:** Step 1: store_fuzz.py --sweep-huge = thermal_learning 6 of 58, other stores 0; --perturb learning_view_float 0; --n 200 --seed 9 ordinary corruption 0 cycle raises (load1 2.20-2.68, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_huge_count.py = value (load1 1.79, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: 1000 and every literal < 2**64 give 0. threshold: the raise is at int(literal) >= 2**64, not at 2**63. reach: production increments counts by 1, so only a hand-edited or foreign store; the stuck-store half holds (orjson refuses the >64-bit int, so the corrupt file is never overwritten). The claim's capacity_envelope seam also raises (view line with np.isfinite(v[1])). medium holds.
- **V2 number:** 6 of 14 (seam, literal) pairs raise in _learning_view: 1.9e19, 1e20, 1e308 at both cop_baseline['4'][1] and capacity_envelope['0'][1]; 1000, 2**63-1, 2**64-1, 1e19 give 0; resave refused by orjson for the same 6

## D1-s2-04: verify, medium

- **V2 metric:** Per cycle-path callee raising every call, over 3 async_refresh cycles, WARNING+ records from ANY logger (not keyed on message text) plus repair issues, minus a no-fault control; and the same for a production-reached failure of _async_watch_learning_drift.
- **Method:** Step 1: guards.py = silent_sites 5 of 5 (reached 3 each, debug_only 3); --perturb debug_to_warning 0 of 5 (load1 2.71-2.73, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_guards.py = value (load1 1.52, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: no-fault run gives the baseline 4 records the subtraction removes. reach: the real-trigger arm shows a store-reachable persistent failure (D1-s1-01's naive stamp) is swallowed with no visible record, so the silence is not only an injection artefact. severity: the harm is invisibility of another defect; with a demonstrated real trigger and actuation sites (_command_frequency, _async_drive_pumps) among the five, medium holds.
- **V2 number:** 5 of 5 injected sites add 0 WARNING+ records and 0 repair issues over 3 cycles (control baseline 4 records), cycles_ok 3/3; real trigger (naive snapshot stamp, no injection): heartbeat raised 3 of 3, extra visible records 0

## D1-s2-05: verify, medium

- **V2 metric:** Wall seconds for production _shutdown_process_pool (the EVENT_HOMEASSISTANT_STOP listener body) to return when called 0.3 s into a known-duration job (child runs time.sleep(D)) through production _run_in_process, divided by D.
- **Method:** Step 1: worker_stop.py --reps 5 = stop_latency_ratio 0.988 (min 0.909, max 1.029), idle 0.008 s, solve 2.696 s (load1 2.76, tf 1.000, 0 concurrent stress.py); --perturb unlocked_reap 0.004 (load1 2.91). Step 2: tools/audit/round9/D1/verify-v2/u1_stop_reap.py = value (load1 1.55, tf 1.005).
- **Attacks (verifier.md step 3 order):** contention: ratio metric; my job duration is fixed by time.sleep in the child, so the ratio is independent of solver speed and box load, and matches (D-0.3)/D exactly. null control: idle 0.001 s. reach: real HA 2026.2.3 core.py waits STOP_STAGE_SHUTDOWN_TIMEOUT = 100 s for stop listeners, so the stall is min(remaining solve, 100 s) per restart on a Pi. medium holds.
- **V2 number:** stop latency / job duration = 0.851 (D=2 s) and 0.940 (D=5 s), i.e. (D-0.3)/D; idle 0.001 s; --unlocked 0.001/0.000

## D1-s3-01: verify, high

- **V2 metric:** For the card's YYYY-MM-DDTHH:MM string passed through the production set_away schema and HeatPumpOptimizerCoordinator.async_set_away, the number of the next 6 _resolve_away() calls that raise, per arm (naive+active, aware+active, naive+inactive, naive+active with as_local fix).
- **Method:** Step 1: away_naive_return.py = solves_failed 2 of 2, failed cycles 6 of 6 (both orders), service raised 1; --aware-input and --perturb 0 (load1 2.11-2.13, tf 1.000); store_fuzz.py (aware clock) away 13, legionella 10, pump_duty 25 (17 naive_dt) of 200, --perturb 0 (load1 3.61). Step 2: tools/audit/round9/D1/verify-v2/u1_away_card.py = value (load1 1.98, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: aware string and inactive away 0. reach: the card's own away strip calls set_away with input[type=datetime-local].value (heatpump-optimizer-card.js away handler), which has no offset; the schema is cv.string; real HA's dt_util.now() is aware; so the ordinary UI path wedges every solve until away is switched off. severity high earned (wrong comfort/plan through the primary UI).
- **V2 number:** card datetime-local string through SERVICE_SCHEMA_SET_AWAY + async_set_away: set_away raised 1 of 2, _resolve_away raised 6 of 6; aware string 0/0; away inactive 0/0; as_local fix 0/0

## D1-s3-02: weaken, medium

- **V2 metric:** Of 31 unload offsets k (async_shutdown starts k loop yields after a pump-mode state change is dispatched to the arbiter's production listener; pump services yield, write state and dispatch state_changed like HA), the count leaving a pump_arbiter timer or listener closed over the released coordinator after all tasks drain.
- **Method:** Step 1: arbiter_unload.py = live 2, writes_after_unload 2; --null 0/0; --perturb 0/0 (load1 2.02-2.11, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_arbiter_window.py = value (load1 2.93, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. mechanism holds: apply() has no _entry_released check and _listen re-arms on empty unsubs. reach/window: real HA's DataUpdateCoordinator.async_shutdown (2026.2.3) does not yield and async_unload_entry awaits async_unload_platforms first, so an apply task created by an event or the 1-min tick runs after release only when it is queued in the loop iteration in which the unload coroutine resumes; my sweep leaks at k=0 only and at none of k=1..30. When it happens the consequence is high (a released coordinator writes the pump every minute until restart), but the trigger is a sub-iteration race per unload, so the expected consequence is medium.
- **V2 number:** leaking unload offsets 1 of 31 (only k=0: the state event dispatched in the same loop step as the unload's non-yielding segment); --guard 0 of 31

## D1-s3-03: verify, medium

- **V2 metric:** Per stored dhw_setpoint value variant in the pump_duty store, loaded by production pump_arbiter._load, the number of 5 consecutive production pump_arbiter.apply() calls that raise.
- **Method:** Step 1: store_fuzz.py --naive-clock = pump_duty_repeat_fail 8 of 200 (type_swap_str 4, wrap_list 3, wrap_dict 1), loader_raise 34; --perturb 0 (load1 3.61, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_pump_duty_load.py = value (load1 2.53, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: 40.0 and 40 give 0 and the record is rewritten to 55.0. reach: production persists float set-points, so a hand-edited or foreign store; the unknown-slot-key arm is a second seam of the same _load property (it validates neither slot names nor values). medium holds.
- **V2 number:** 4 of 8 set-point variants raise on 5 of 5 apply() calls ("40", "abc", [40], {"v":40}) and the record persists; 40.0, 40, true, null 0; extra: an unknown slot key ('dhw') with 40.0 raises KeyError 5 of 5

## D1-s3-04: verify, medium

- **V2 metric:** |HeatPumpOptimizerClimate.target_temperature - configured target| read from the production property inside a pass-through wrapper of _await_optimize (no write forced), away active vs off, and right after async_run_optimization returns.
- **Method:** Step 1: climate_midsolve.py = max_published_deviation 5.00 C, after 0.00; --null 0.00; --perturb 0.00 (load1 3.47-3.56, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_climate_window.py = value (load1 2.18, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: away off 0.00. reach: publication needs a loop-side state write during the executor await; coordinator.py has 5 async_update_listeners call sites and the finder's is the event-driven peak-guard transition; on a Pi the await lasts the whole solve (tens of seconds), so a write in the window is plausible when peak guard is configured. Transient wrong published value in state history: medium as filed.
- **V2 number:** climate.target_temperature read at the solve await: away 16.0 vs configured 21.0 (5.00 C), after solve 0.00; away off 0.00/0.00

## D1-s3-05: weaken, low

- **V2 metric:** Minutes a boost channel set by production BoostState.set stays active (BoostState.active, 1-min sampling) beyond BOOST_HOURS after the wall clock steps back J; and whether production boost.restore keeps a stored until X ahead past now + BOOST_HOURS.
- **Method:** Step 1: boost_unbounded.py = jump0 2.00, jump1 3.00, jump6 8.00, jump24 26.00, restore_2099 72.00 (cap) h; --perturb 2.00/0/0/0/0 (load1 2.16-2.23, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_boost_overrun.py = value (load1 2.14, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. grid: finder's 5 cells, 26 h rests on a 24 h backward step. reach: overrun equals the step size exactly, and the clock steps a Raspberry Pi actually takes (fake-hwclock boot, NTP) are forward or seconds-to-minutes; a 2099 until needs a hand-edited store. The boost is user-toggled and visible, so the user can switch it off. Mechanism verified; consequence low.
- **V2 number:** overrun beyond BOOST_HOURS = the backward clock step exactly: J 0/1/10/60/1440 min -> 0/1/10/60/1440 min; restore keeps an until 3 h or 365 d ahead past the 2 h cap (2 of 4), 0 for <= 2 h

## D1-s3-06: verify, medium

- **V2 metric:** Per phantom stored bucket (key in {-1,0,5} x ratio in {0.2,1,10,1e6,1e308}, count 50) added to a healthy map loaded by production FrequencyMap.from_dict, truthful folds (0.04 kW/Hz, at the clipped recommend(3 kW) answer) until the plant delivers >= 50% of 3 kW, cap 10000.
- **Method:** Step 1: freq_map_store.py = stuck_after_day 10 of 200, healthy 0; --perturb 0 (load1 2.23, tf 1.000). Step 2: tools/audit/round9/D1/verify-v2/u1_freq_phantom.py = value (load1 2.12, tf 1.000).
- **Attacks (verifier.md step 3 order):** contention: n/a. null control: healthy map recommends 80 Hz, 0 folds. grid: 15 cells, range 0-10000 folds; the negative-key cells are permanent because observe() clips folds to deciles 0-9 and so can never decay the phantom. reach: from_dict is the only path to a negative key (hand-edited store); in-range keys with an inflated ratio decay at EWMA 0.1. Under-delivery pinned at hz_min: medium holds.
- **V2 number:** stuck_at_96 = 7 of 15 phantom cells; a negative decile key never recovers (10000 of 10000 folds for every ratio incl. 0.2 kW/Hz); key 0 recovers in 7/24/46/155/6755 folds for ratios 0.2/1/10/1e6/1e308; key 5 recovers at 0

## Unfinished

None.
