# D1 verify-v3, unit D1-1 (lens V3: reach and class)

Real HA: homeassistant 2026.2.3 (/root/venvha, Python 3.14.0rc2), no hastub on the path; shim `typing.ByteString = bytes` for mashumaro only. The production target may be newer. Harnesses: `tools/audit/round9/D1/verify-v3/D1-s*_realha.py` plus the bootstrap `D1-1_realha.py` (real HomeAssistant, frame and loader set up, real ConfigEntry); each runs as `/root/venvha/bin/python tools/audit/round9/D1/verify-v3/<file> [arm]`. Every perturbation is in memory. Step 1 re-runs used `PYTHONPATH=tests/hastub /root/venv314/bin/python`, load1 0.59–2.87, thread_factor 1.000; all 15 reproduced exactly. Real-HA runs: load1 1.1–3.3, thread_factor 1.001–1.043 (count metrics).

## D1-s1-01: verify, medium, P1
- Step 1: 21/0/19/21/21, sibling 0; --aware and --fix give 0 raises and 3 snapshots taken.
- Own measurement (D1-s1-01_realha.py), metric = raising consumer calls over 21 real-clock days after a real-Store load: consumer_raises=63/63; --aware 0/63.
- Reach: the real Store keeps a naive leaf unchanged (store_keeps_naive=1). The 3 production producers write 0/3 naive stamps under real dt_util, so reach is a hand-edited or corrupt store only. Medium stands on consequence (snapshot insurance, curve and comfort learning stop permanently; set_temperature raises).
- Seam rule: partial. coordinator._update_snow_memory with a naive stored snow_accum_last raises 21/21 and is not in the rule's module list; also missing are fuse_advisor_at, away, boost, pump_arbiter and legionella.

## D1-s1-02: verify, medium, P1
- Step 1: 4/4; control 0; --fix 0.
- Own measurement, metric = best_restore raises after a QuarantiningStore round trip: 4/4, control 0/1.
- Reach: corrupt store only (AccuracyTracker emits float or None).
- Seam rule: partial. It misses snapshots.py:194 (the bias read) and coordinator.py:8840/8881 (snap.get("learners")).

## D1-s1-03: verify, medium, class new (live sample with no plausibility bound; shared with s2-02)
- Step 1: p90 25.760 vs 1.073 kWh; 1e6 gives 139054.657; --guard 1.073.
- Own measurement: a real HA State "-127" read by InputReader.read is delivered ok=1. Window p90 25.760 vs 1.073 kWh; 85 C gives 5.677; a reader-side guard gives 1.073.
- Reach: real (sensor sentinel values). The plan path is gated by DHW quantile targets (default False), but the p90 always feeds the dhw_advisor sweep (coordinator.py:2694) and the published dhw_draw_stats.
- Seam rule: partial. It misses async_learn_cooling, the unbounded reader, and legionella.async_track, which credits a cycle on one hot sample under the default instant-credit rule.

## D1-s1-04: verify, low, class new (future instant trusted; shared with s3-05)
- Step 1: 33/37/31; 0 ahead 4/8/2; --clamp 4/8/2.
- Own measurement: producers write the stamps on a clock 30 days fast, then a real Store round trip. First action on days 31/37/31 vs 1/7/2 at 0 ahead; 365 ahead gives 366/372/366.
- Constant attack: the finder's harness uses max_gap 72 h; production VENT_CUSUM_STARVE_HOURS is 6 h. The stretch equals the clock error either way.
- Seam rule: partial. It misses boost, legionella last_cycle, pump_arbiter written-at and the coordinator snow stamps.

## D1-s2-01: refute, severity low if kept, class new
- Step 1: wedged 35/200 (entry 27, shape 8); row_filter 0.
- Own measurement (D1-s2-01_realha.py): the same 200 payloads, generator copied verbatim, returned as a real WeatherEntity's native forecast through real `weather.async_get_forecasts_service` into the real coordinator. wedged=0/200, ha_service_raised=34, malformed_responses=0. Bypassing HA's service gives 35/200.
- Why it refutes: real HA rebuilds every row with dict(row). A non-dict row raises inside HA, and the coordinator then records a failed fetch and stores nothing. The wedge is reachable only if something replaces the weather.get_forecasts service.
- Seam rule: all (11 sites).

## D1-s2-02: verify, medium, class new (shared with s1-03)
- Step 1: 3/10 cases capped at 60 s (wind 1e308, 1e12, 1e20); temp ±1e308 gives status failed; healthy 2.54 s; clip gives 0/10. Walls provisional, load1 2.33.
- Own measurement: reaches_solve_arrays=2/2 through real HA's conversion (wind goes to km/h and back); --clip 0/2.
- Consequence: `_await_optimize` has no timeout, so a runaway solve blocks the worker and `_PROCESS_LOCK`.
- Seam rule: partial. It counts the weather-entity parser only; the same harness's ecl110 arm shows 55/200.

## D1-s2-03: verify, medium, P1
- Step 1: 6/58 leaf values; perturb 0.
- Own measurement: view_raises=3/3 at 1e20 and 0/3 at 1e18. The real Store logs ERROR "Bad data at $.data.cop_baseline.4[1]" and keeps the corrupt file (file_still_corrupt=1), so the wedge survives restarts.
- Reach: corrupt store only.
- Seam rule: partial. It covers 7 of 13 QuarantiningStore sites.

## D1-s2-04: verify, medium, class new
- Step 1: 5/5 silent; perturb 0.
- Own measurement, with HA's own async_enable_logging and empty logger/system_log config: 0 records emitted and 0 system_log entries per site, 3/3 cycles ok, debug_enabled=0. --debug-to-warning gives 3 records and 1 entry per site.
- Seam rule: partial. It finds 24 guards in coordinator.py; the pattern totals 52 package-wide.

## D1-s2-05: verify, medium, class new
- Step 1: ratio 0.937; unlocked 0.006; idle 0.007 s.
- Own measurement: a real hass.async_stop takes 5.501 s against a 6 s job started 0.5 s earlier (ratio 0.917, load1 3.24, walls provisional). Idle 0.002 s; unlocked reap 0.003 s.
- Bound: real HA caps the stop stage at 100 s.
- Seam rule: all (3 _PROCESS_LOCK sites).

## D1-s3-01: verify, high, P2
- Step 1: 6/6 cycles, 2/2 solves failed; aware input 0; perturb 0.
- Own measurement: the card's datetime-local value and the services.yaml shape both pass real cv. async_set_away raises 2/2 and _resolve_away raises 12/12; the offset control gives 0; the perturbation gives 0.
- Reach: the card's own input (heatpump-optimizer-card.js:4331). The stub's naive default clock hides it.
- Seam rule: partial.

## D1-s3-02: verify, high, class corrected new -> P2
- Step 1: 2 registrations and 2 writes after unload; null and perturb 0.
- Own measurement:
  - The finder's literal order (event, then unload, lock free) gives 0/0 in real HA. Real `async_create_task` is eager and state_changed dispatch is deferred.
  - An unload 0.45 s into a writing pass (pump services take 0.3 s, one write already landed) gives 2 registrations and 1 write after unload. The lock-held arm gives the same 2/1.
- Constraint on the fixer: test the mid-pass interleaving, not the finder's order.
- Class: the coordinator latches on _entry_released at _async_setup_peak_guard; apply lacks that guard, which makes it P2.
- Seam rule: partial.

## D1-s3-03: verify, medium, P1
- Step 1: pump_duty_repeat_fail=8/200 on the naive clock (25 including naive_dt on the aware clock); perturb 0.
- Own measurement: apply raises 9/9 and 3/3 files stay corrupt; control 0.
- Reach: corrupt store only.
- Seam rule: all.

## D1-s3-04: weaken to low, class new
- Step 1: 5.00 C; null and perturb 0. The mid-solve write in that harness is synthesised at the await.
- Own measurement:
  - A concurrent refresh gives 0.00 C. Real async_refresh holds `_debounced_refresh.async_lock` (the stub's does not), so solves serialise (2 solves, 0 mid-solve writes).
  - The peak-guard path gives 5.00 C: peak guard on (default off), 16 A fuse, 30 kW readings 10.2 s apart, solve held 25 s. Null and perturb give 0.
- Why low: the wrong value lasts at most until the refresh-end write and needs away plus a transition inside the solve.
- Seam rule: all.

## D1-s3-05: verify, medium, class new (shared with s1-04)
- Step 1 and own measurement are identical: 2/3/8/26/72 h; perturb 2/0/0/0/0.
- Reach: a backward clock step, or a corrupt store for the 2099 case.
- Seam rule: all within boost.

## D1-s3-06: verify, medium, P1
- Step 1: 10/200; perturb 0.
- Own measurement: store_stuck=2/2 via QuarantiningStore; healthy 0.
- Live seam: one 500 kW reading delivered by a real State through InputReader at 22 Hz leaves the map under 50 % of target for 32 folds.
- Seam rule: partial. from_dict is the only loader, but FrequencyMap.observe is an unbounded live seam of the same phenomenon.

## For the judge
- Same-mechanism pairs: s1-04 with s3-05; s1-03 with s2-02 and the live seam of s3-06.
- Stub divergences measured (leads for the owner of tests/hastub; not filed), each moving a D1 verdict:
  - `DataUpdateCoordinator.async_refresh` takes no lock in the stub; real HA holds `_debounced_refresh.async_lock` (s3-04: 0 vs 5.00 C).
  - `FakeHass`/`LoopHass` create tasks lazily; real `hass.async_create_task` has `eager_start=True` (s3-02: 0 vs 2 in the finder's order).
  - The stub serves raw get_forecasts payloads; real HA normalises rows through `_convert_forecast` (s2-01: 0 vs 35).
- Side observation (not a vote): `_async_load_thermal_learning` saves the thermal-learning store at coordinator.py:2909 when it has no `house_heat_loss_anchor`, before `cop_baseline` and later fields are parsed, so the file is rewritten with `cop_baseline={}`; in-memory state is complete and the next save restores the file.
