# Round 9, D1 unit D1-2 — verifier V2 (independent lens)

Box G1-V2 (4 vCPU Linux, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1), evidence tree at baseline
`1936d5ca72a06556eeed4e8e5bf3dea520e517e1`, `PYTHONPATH=tests/hastub`, BLAS pinned to 1 thread.
Every number below is a count (contention-immune); every run printed `thread_factor` 1.000-1.002,
`swapins` 0, `load1` 0.45-3.37 (two other verifier seats running).
Own harnesses: `tools/audit/round9/D1/verify-v2/u2_*.py`, each with the contract header.
No finding here is a test-gap claim, so step 4 (single-line production mutation the suite misses)
does not apply to any of them.

| id | step 1 (finder harness) | step 2 (own harness) | vote | severity |
|---|---|---|---|---|
| D1-s4-01 | reproduced exactly | boundary arm refutes the non-finite half | weaken | low |
| D1-s4-02 | reproduced exactly | reproduced at a second fault site, 3 configs; non-finite trigger fenced | weaken | low |
| D1-s4-03 | reproduced exactly | larger through the real boundary (72/156) | verify | low |
| D1-s5-01 | reproduced exactly | timeline: live RH held 8 h -> 24/32 samples None | verify | medium |
| D1-s5-02 | reproduced exactly | 15/34 price, 9 peak corruptions admitted through the boundary | weaken | low |
| D1-s5-03 | reproduced exactly | 0 rows for every digit count >= 309 and every position, via json.loads text | verify | low |
| D1-s5-04 | reproduced exactly | 44/59 hourly offsets, 14/14 15-min offsets blank >= half | verify | low |

## D1-s4-01 — DefrostDerate duty grid not bounded on load

Step 1: `s4/store_fuzz.py`: duty_targeted_stuck=53, pinned 42, silent 53, nan_bucket_factor_after_200=0.5500;
`--perturb` -> 0 / 1.0000. Matches.

Step 2: `u2_defrost_boundary.py`. Metric: of 156 exhaustive single-cell duty corruptions (12 cells x 13
scalars), each saved through the stub Store (json round-trip) and loaded through
`store.QuarantiningStore.async_load` (the production boundary behind both `DefrostDerate.from_dict` call
sites, `coordinator.py` `_async_load_accuracy` and the snapshot restore), count whose delivered
`factor()` at the bucket centre differs from the healthy twin's by > 0.01 after 200 zero-duty folds.
Finder's metric keys on the loaded grid cell after 24 folds, without the store boundary.

- boundary arm: wrong_after_200=36, all 36 pinned at DERATE_MIN; nonfinite_cells_loaded=0. Every
  non-finite corruption ("nan", "inf", float nan/inf) is scrubbed to None by QuarantiningStore, the
  duty grid then fails the cast and the load takes the migrated path (D1-s4-03): 0 of 48 stay wrong at 200 folds.
- bypass arm (from_dict on the raw payload, the finder's route): wrong_after_200=84, nonfinite_cells_loaded=48.
- Finite out-of-range survives the boundary: "1e308", 1e300, 2**70 pin the bucket at 0.55; folds to
  recover 6779, 6604, 509; 50.0 recovers in 85. A negative -1e300 shows derate 1.0 (no frost) under a real
  0.2 duty for 6604 folds; -0.5 for 45.

Attacks: contention n/a (counts). Gate mode n/a. Grid artefact: exhaustive grid, per-scalar split
printed; the result is decided by scalar class, not cell. Null: healthy payload 0 in both arms.
Reach: the claim's headline mechanism ("non-finite ... pins for the life of the process", nan bucket
0.5500) does not reach through the production load path — refuted by boundary.nonfinite_cells_loaded=0.
What remains is a finite out-of-range cell, which no writer produces (`observe_duty` refuses duty outside
[0,1]); only a hand-edited or corrupted store holds one, and it recovers in 85-6779 folds of that bucket.
Severity: the finite remainder is a corruption-only trigger with a bounded, conservative-direction effect
for the positive case -> low.

## D1-s4-02 — a guarded solve failure is adopted as a successful plan

Step 1: `s4/solve_guard.py`: guarded solve_failures=0, issues=0, failed_plans_published=3 (both configs);
null 3/1/0; nonfinite_input returned_failed_plan=9 of 15. `--perturb` -> 3/1/0 and 0 of 15. Matches.

Step 2: `u2_solve_fail.py`. Metric: 3 consecutive `async_run_optimization` cycles with the fault at
`optimizer:_multi_start_minimize` (the production's own ValueError "no usable starting point"; the
finder injected at `_scoped_minimize`), per config: `_solve_failures`, solve_failures issues, cycles adopting
a status starting "failed", cycles advancing `last_optimization`.
- coord_minimal, coord_two_zone, coord_all_features: 0 / 0 / 3 / 3 each. The failed plan is adopted and
  also stamped as the last successful optimization.
- Reachability arm (no injection): one NaN price total, one NaN forecast temperature, one inf solar value
  placed in the coordinator's own inputs: failed_adopted 0, 0, 0 (each cycle adopted a normal plan). The
  finder's second trigger (a non-finite horizon input) is fenced before the optimizer on the coordinator path.
- Null: no fault, failed_adopted=0.

Attacks: contention n/a. Transport: both harnesses replace `_await_optimize` with an inline
`optimize_in_process` — the coordinator's own #511 fallback, so the adoption logic measured is production.
FakeHass executor seriality does not bear on a counter. Reach: only an exception raised inside the solve
reaches the guard from the coordinator; that is a solver or code fault. Severity: when it fires, each
cycle still logs ERROR and publishes `optimization_status` "failed (...)"; what is lost is the repair notice and
an honest last-success stamp -> low.

## D1-s4-03 — one bad cell in a v2 store voids all measured buckets, labelled a v1 upgrade

Step 1: `s4/store_fuzz.py`: v2_one_bad_cell_flagged_migrated=226/250, discarded 2712; `--perturb-label` -> 0. Matches.

Step 2: same `u2_defrost_boundary.py`, metric: of 156 single-cell duty corruptions through QuarantiningStore,
count loaded `migrated=True` and measured buckets reset. boundary: migrated=72 (every non-finite and
unparseable scalar class, 6 x 12), buckets discarded 864 = 72 x 12; bypass: migrated=24. The production
boundary routes more corruptions onto this path, not fewer: the realistic corruption (a non-finite leaf)
lands here every time.

Attacks: counts; exhaustive grid; null 0. Reach: corruption-only (no writer emits a bad cell), but through
the real boundary. Consequence: all 12 buckets' measured duty lost and a false "pre-v5.3.0 upgrade" log/label;
inferred factors kept. Low, as filed.

## D1-s5-01 — inputs.age_of ignores last_reported and accepts future stamps

Step 1: `s5/age_of_divergence.py`: reported_divergent=7/12, future_divergent=6/6, control 0/12; `--perturb` -> 0/0/0. Matches.

Step 2: `u2_age_timeline.py`. Metric: a live sensor holding one value for H hours while re-reporting every
5 min, sampled every 15 min through `coordinator:_dhw_inlet_c` and
`HeatPumpOptimizerCoordinator._indoor_humidity_value`; count samples delivered None although the sensor
reported <= 5 min ago. Finder's metric: disagreement cells against `InputReader._age_minutes` on a static grid.
- humidity (limit 120 min): hold 1 h 0/4, 2 h 0/8, 3 h 4/12, 4 h 8/16, 8 h 24/32, 12 h 40/48.
- dhw_inlet (limit 1440 min): hold 24 h 0/96, 30 h 24/120, 48 h 96/192.
- null (value changes on every write): 0/48 and 0/192.
- future arm: clock stepped back 60 min just after the sensor died: dead sensor served 13 samples (humidity)
  vs 9 under the reader's rule; 101 vs 97 (inlet). The extra is the length of the clock step, bounded.

Attacks: counts; the stub `FakeState` carries `last_reported` the way real HA (2024.3+) writes it, so the
reach is real HA's. Severity: a live integer-%RH sensor steady for > 2 h (overnight) loses the mold floor for
the rest of the steady spell, silently; the inlet case needs a > 24 h unchanged value. Medium, as filed.

## D1-s5-02 — price-model and peak-tracker loaders admit finite out-of-domain state

Step 1: `s5/store_domain_fuzz.py --n 300 --seed 9`: price 11 (next 9), peak 8 (next 2), crash 0; `--perturb` -> 0/0. Matches.

Step 2: `u2_store_domain.py`. Metric P: of 34 enumerated single-field corruptions of a 28-day-trained
PriceShapeModel, routed through QuarantiningStore, count whose `extend_price_series` tail differs from the
healthy twin by > 2x at any guessed step (or is <= 0 / non-finite), no WARNING: 15 on load, 15 silent,
15 after 1 more observed day, 9 after 14 days (shape bins -1, 50, 1e300 and quarter factors -1 persist 14 days;
0-valued bins wash out). Null 0.
Metric K: PeakTracker, published `threshold_kw`/`billed_peak_kw` negative or > 1000 kW. 3-day base, 18
corruptions: 9 at load (every negative and huge peak), 5 after the next cycle, 5 after 3 real windows
(1e300 peak, 1e300 window_factor, 1e300 window_wsum). A negative peak is displaced by the next same-day window
under `distinct_days` in my arrangement (0 after the next cycle), where the finder's draws kept 2.
1-day base: 3 at load, 3 persisting. Null 0.

Attacks: counts; enumerated grid split per field. Reach: QuarantiningStore scrubs only non-finite leaves, so
every finite value here reaches the loaders in real HA; but no in-tree writer produces any of them (observe_day
clips and renormalises, observe refuses negative power), so the trigger is a hand-edited or corrupted store
holding finite garbage. Severity: consequence is real (a wrong priced tail, a wrong published peak) but
the trigger is corruption-only and the realistic corruption (non-finite) is already quarantined -> low.

## D1-s5-03 — one huge JSON integer drops the whole price or Open-Meteo payload

Step 1: `s5/price_huge_int.py`: entity/tibber/open_meteo huge rows 0/0/0, controls 24/24/72; `--perturb` -> 24/24/72. Matches.

Step 2: `u2_huge_int.py`. Metric: rows delivered when the payload arrives as JSON text decoded by
`json.loads` (aiohttp's default decoder, which `_get_json` and the Tibber fetch use), hostile literal swept over
digit count and position. Tibber and Open-Meteo: 0 rows for 309, 400 and 4000 digits in first, middle and last
position (18 of 18 cells); json.loads accepts all of them. Controls: 308 digits keeps the payload (Tibber 25,
the 1e308 row itself admitted as a price; Open-Meteo 72); string '1e999' keeps 24.

Attacks: counts; reach is real (json.loads, not a stub) but needs an upstream API to emit a > 308-digit
integer. Consequence: one fetch lost, retried next cycle. Low, as filed.
Side observation (not a vote): a finite 1e308 price row is admitted by `prices_from_tibber_payload` (25 rows).

## D1-s5-04 — one off-grid Open-Meteo stamp collapses the inferred resolution

Step 1: `s5/open_meteo_resolution.py`: stray 1/5/30 min -> 192/192/94 None steps, healthy 0; `--perturb` -> 0. Matches.

Step 2: `u2_om_stray.py`. Metric: stray offset swept over every minute 1..59 in the hourly block and 1..14 in
the minutely_15 block; count offsets blanking >= 96 of 192 quarter-hour steps via `irradiance_for`
(and `humidity_for`). Hourly: 44 of 59 offsets (range 94-192) for irradiance, 44 of 59 for humidity;
minutely_15: 14 of 14 (range 191-192). Controls: clean 0, missing hour 4, duplicate stamp 0.
Next clean refresh restores 0 (192 -> 0).

Attacks: counts; the sweep removes the grid-cell choice (finder's three offsets). Reach: the request fixes
`timezone=UTC`, so DST cannot create an off-grid stamp; the trigger is a malformed API response, and the
damage lasts one refresh. Low, as filed.
