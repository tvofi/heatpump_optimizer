# Round 9 verify, lens V1 (reproduce): D1, unit D1-2 (D1-s4-01..03, D1-s5-01..04)

Environment: evidence tree SHA 6f51db2c (baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1), 4 vCPU cloud container (box G1-V1, shared with two other sub-seats). CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1. PYTHONPATH=tests/hastub. Every metric here is a count, so contention does not affect it. Harness runs: load1 0.44–3.39, thread_factor 1.000–1.005, swapins 0.

My own harnesses:
- `tools/audit/round9/D1/verify-v1/u2/indep_d1_2.py`: an independent measurement for every finding.
- `tools/audit/round9/D1/verify-v1/u2/store_fuzz_via_boundary.py`: the finder's store_fuzz.py, unchanged, with every payload first passed through the production store boundary `store._sanitize`.

I created no private worktrees and made no production edits. Every perturbation was applied in memory.

**Cross-cutting attack (D1-s4-01, D1-s4-03, D1-s5-02).** Every production `Store` is a `QuarantiningStore`. Its `async_load` runs `store._sanitize`, which turns any non-finite float, and any string that parses to a non-finite value ("nan", "inf", "NaN"), into `None` before a loader sees it. The finders' store fuzzers call `from_dict` directly, which skips that boundary. I re-ran them with the boundary put back in.

---

## D1-s4-01: defrost duty cell non-finite or out of range pins the bucket at DERATE_MIN
- **Re-run (exact header command):** duty_targeted_stuck=53, pinned=42, silent=53; nan_bucket_factor_after_200_zero_folds=0.5500; sibling_factors_stuck=0; healthy_null_control_stuck=0. This matches the finder.
- **Perturbation (--perturb):** every stuck count is 0 and the nan bucket reads 1.0000. The number moves to zero in the stated direction.
- **Null control:** 0. Reproduced.
- **Reach attack, the finder's harness through the production store boundary** (`store_fuzz_via_boundary.py`):
  - duty_targeted_stuck falls from 53 to 30 and pinned from 42 to 23.
  - **nan_bucket_factor_after_200_zero_folds = 1.0000, not 0.5500.**
  - The quarantine turns the "nan"/"inf" cell into None, `_grid_of` fails, and the whole duty grid resets. That is D1-s4-03's path, not a pin.
  - The 30 includes negative cells (-5.0, -1e300). Those derate to 1.0, the same as a healthy bucket.
- **Own measurement** (`indep_d1_2.py` s4_01): 12 scalars × 12 buckets, one bad duty cell, duty_counts 50, zero-duty folds.
  - Direct: 120/144 below healthy after 24 folds, 96/144 pinned.
  - Through the boundary: 72/144 below healthy, 48/144 pinned.
  - Folds needed to recover, through the boundary: nan/inf (string or float) 0; 1.01 → 201; 2.0 → 208; 50.0 → 238; 2**70 → 662; 1e300 → 6757; 1e308 → 6932.
  - No finite value "never recovers". Only a non-finite one does, and in real Home Assistant non-finite never reaches the loader.
- **Outcome:** the loader defect is real. Finite out-of-range duty (1e300, 50, 2.0) is loaded silently and is not clamped, while `factors` is clamped. A very large value holds the bucket at 0.55 for thousands of hourly folds. But the headline mechanism, non-finite strings pinning the bucket for the life of the process at 0.5500 after 200 folds, cannot happen through `QuarantiningStore`. Reach needs a hand-edited or corrupted file that holds a finite value greater than 1.
- **Vote: weaken, to low.** Metric: count of mutants (or bucket cells) whose loaded duty still derates the bucket below a healthy one after N zero-duty folds, with and without `store._sanitize` before `from_dict`.

## D1-s4-02: a failed solve is returned as a plan, and the coordinator counts it a success
- **Re-run:** both coord_minimal and coord_dhw give solve_failures=0, issues=0, failed_plans_published=3. Null control (fault in `_forecast_arrays`): 3 and 1. Non-finite grid: returned_failed_plan=9 of 15, raised=2. Matches the finder.
- **Perturbation:** solve_failures goes from 0 to 3, issues from 0 to 1, failed plans published from 3 to 0, and non-finite returned plans from 9 to 0. The direction is as stated.
- **Own measurement** (`indep_d1_2.py` s4_02): I injected the fault one level lower, at scipy's `minimize` as the optimizer module imports it, instead of `_scoped_minimize`.
  - `optimize` does not raise, in both the space-only and the DHW path, and returns status `failed (...)`.
  - Coordinator after 4 cycles: `_solve_failures`=0, issues=0, 4 of 4 published plans carry the failed status.
  - Control run with no fault: 0 failed.
- **Attacks:**
  - `_multi_start_minimize` tolerates one bad start and raises only when all starts fail. The guard then swallows that raise, which is the claimed mechanism, confirmed by reading the code.
  - The fallback plan is the heuristic initial power, not a harmful plan, and an ERROR line is logged each cycle. Only the repair issue and the failure counter are lost.
  - I kept medium: the counter and the repair issue exist precisely to surface this condition.
- **Vote: verify, medium.** Metric: the coordinator's `_solve_failures` and number of solve_failures issues after k cycles in which every L-BFGS-B call raises.

## D1-s4-03: one bad cell in a v2 store voids all 12 buckets and is labelled a pre-v5.3.0 upgrade
- **Re-run:** v2_one_bad_cell_flagged_migrated=226, measured buckets discarded=2712. Matches.
- **Perturbation (--perturb-label):** 226 goes to 0. The direction is as stated. The discard count stays 2712, as the perturbation's scope implies.
- **Own measurement** (`indep_d1_2.py` s4_03): 4 corruptions (NaN float, "abc", None, []) × duty/duty_counts × 12 buckets = 96 payloads, all passed through `store._sanitize`. migrated=True in 96/96; the pre-v5.3.0 INFO line was logged in 96/96; 1152/1152 measured buckets were discarded. Controls: a healthy v2 payload gives migrated=0; a true v1 payload gives migrated=1.
- **Attack:** the store boundary makes this path *more* reachable, because every non-finite duty leaf now lands here. The consequence is a misleading label, the loss of measured duty, and a fallback to inferred factors, so low severity is earned.
- **Vote: verify, low.** Metric: of v2 payloads with one malformed duty or duty_counts cell, the count loaded with migrated=True and the upgrade log line.

## D1-s5-01: `inputs.age_of` ignores last_reported and accepts future stamps
- **Re-run:** reported_divergent=7/12, future_divergent=6/6, control_divergent=0/12. Matches.
- **Perturbation:** 0/0/0. The number moves to zero as stated.
- **Own measurement** (`indep_d1_2.py` s5_01): I drove the real consumers `coordinator._dhw_inlet_c` and `_indoor_humidity_value` at their own limits (1440 and 120 min) and compared each against `InputReader._age_minutes` on the same State. Divergent cells: dhw_inlet 4/10, indoor_humidity 5/10. Every case with last_reported == last_updated agrees. A future stamp (-5 min and -120 min) is delivered as fresh while the reader returns None.
- **Reach:** `hacs.json` sets the minimum Home Assistant version to 2025.2.0, so `last_reported` always exists in real Home Assistant.
- **Consequence attack:** a live-but-steady sensor degrades to the no-sensor behaviour: the seasonal inlet model, or no mould floor. The code itself calls that the fail-safe direction. The future-stamp case keeps a frozen value alive until the clock catches up. Both are real, but the consequence is a degrade to the configured fallback, not a wrong control action.
- **Vote: weaken, to low.** Metric: cells in which the value delivered through `age_of` (None or a number) disagrees with the reader's verdict on the same State.

## D1-s5-02: learner-store loaders check finiteness but not domain (price shape, peak tracker)
- **Re-run** (`--n 300 --seed 9`): price_model_silent_invalid=11 (next_still_invalid=9), peak_tracker_silent_invalid=8 (next_still_invalid=2), crash=0. Controls 0 and 0. Matches.
- **Perturbation:** 0 and 0. The direction is as stated.
- **Leave-one-out over seeds 1, 2, 3, 4, 5, 9:** price_model 8, 10, 8, 9, 13, 11 (min 8), which reproduces the finder's block. peak_tracker 2, 5, 3, 0, 5, 8: seed 4 gives **0**, so the peak arm is seed-sensitive and 8 is its most favourable cell. next_still_invalid for the peak arm is 0–2, so it mostly heals within one cycle.
- **Own measurement** (`indep_d1_2.py` s5_02, hand-built, through `store._sanitize`): a shape bin of 0.0 gives 1/24 bad tail steps with 0 warnings, and a bin of -2.0 does the same. A stored peak of -2.0 among [5, 4, -2] gives threshold_kw=-2.000 with 0 warnings. A stored peak list of [-1] gives threshold -1.000 and billed -1.000. Healthy control: threshold 3.500, 0 bad steps. Finite out-of-domain values pass the quarantine untouched, so the boundary attack does not reduce this finding.
- **Vote: verify, medium.** The price arm is robust across seeds; the peak arm is weaker, ranging from 0 to 8 across seeds. Metric: mutants whose loaded state makes the next cycle produce a price ≤0, non-finite or more than 1000× the mean, or a negative threshold or billed peak, with no WARNING logged.

## D1-s5-03: one huge JSON integer drops a whole price fetch or Open-Meteo refresh
- **Re-run:** entity, tibber and open_meteo huge_int rows are 0, 0, 0. Controls are 24, 24, 72. Matches.
- **Perturbation:** 24, 24, 72. The number moves up as stated.
- **Own measurement:** `price_model._raw_value` over 24 rows plus one 10**400 row delivers 0/24 because it raises OverflowError. `open_meteo._parse_block` over 24 samples plus one 10**400 delivers 0/24 because it raises. The "1e999" string control keeps 24/24 on both.
- **Consequence:** the sibling `tariff._stored_peaks` already catches OverflowError. Reach needs an upstream to emit a 309+ digit integer, which is implausible, so low severity is correct.
- **Vote: verify, low.** Metric: rows delivered for valid rows plus one huge-integer row, with a raise counted as 0.

## D1-s5-04: one off-grid timestamp collapses Open-Meteo's inferred resolution
- **Re-run:** healthy 0; stray 1 min 192; stray 5 min 192; stray 30 min 94. The finder's leave-one-out cells are flat at 192. Matches.
- **Perturbation (median gap):** 0 in every arm. The number moves to zero as stated.
- **Own measurement** at different offsets (48 h hourly series, one stray stamp): 1 min 192/192; 7 min 192/192; 20 min 143/192; 45 min 143/192, with the resolution inferred as 15 min; healthy 0/192.
- **Consequence:** the phenomenon holds at any sub-hourly off-grid offset. Reach needs an irregular stamp from the API, and the result is a loss of solar data rather than a wrong value, so low severity is correct.
- **Vote: verify, low.** Metric: quarter-hour steps over 48 h for which `irradiance_for` returns None after one stray stamp.
