# D3-s1 box D3-g11: full gate for 16 D3.M3 full-net survivors (round 11, baseline 92d38ecb640b)

## Machine and controls

```
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1087       13497          12        1800       15000
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1 0.69
Sun Nov 22 21:38:58 UTC 2026
```

Null control (`fullgate.py null`, comment-only marker): gate_rc 1, wall 3288.9 s (provisional), red scripts python3 tests/closure.py selftest, python3 tests/entities.py, python3 tests/harness_headers.py -- artefact checks only (dev/audit/rounds/round11/D3/s1/wave/D3-g11/gates/null-note.txt). A key is KILLED only on a script red beyond these or more FAIL lines in one.

Procedure: `gate_wave.sh run` (one gate at a time, GATE_JOBS=1, 4 h cap) -> `fullgate.py run --src <src> --key <key>`; each recorded gate -> `probes/box-tools/build_result.py <key>` runs the key's probe in a clean baseline checkout and writes results/<key>.json. This seat resumed a stalled predecessor at 4/16 gated; nothing was re-gated.

## Tally

- gated: 16 keys; verdicts {'TIMEOUT': 1, 'RED-AS-NULL': 14, 'KILLED': 1}
- KILLED: dc6c13eca2ca1737 by python3 tests/boost_drift_replay.py, python3 tests/features.py
- classes: {'timeout': 1, 'equivalent-candidate': 4, 'candidate': 10, 'killed': 1}
- candidates (gate_survivors): 10; equivalent-candidates: 4; timeouts: 1

Wall, CPU and load numbers are provisional (nproc 4, Intel Xeon @ 2.10GHz; the judge re-takes them); counts are final.

| key | site | patch | verdict | class | probe baseline -> mutant |
|---|---|---|---|---|---|
| 9efe002b48e1827d | coordinator.py:6360 RETURN_DEL | `return None -> pass` | TIMEOUT | timeout | - -> - |
| a7488872387d5ca7 | coordinator.py:6379 CMP_BOUND | `if len(prices) < 4: -> if len(prices) <= 4:` | RED-AS-NULL | equivalent-candidate | - -> - |
| 61e748f094f2daa8 | coordinator.py:6454 CMP_BOUND | `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT: -> if self._solve_failures > SOLVE_FAILURE_ISSUE_COUNT:` | RED-AS-NULL | candidate | 0 -> 1 |
| a33188790c5affad | coordinator.py:6454 GUARD_OFF | `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT: -> if False:` | RED-AS-NULL | candidate | 0 -> 1 |
| 94285425a1bc856a | coordinator.py:6615 GUARD_OFF | `if pending: -> if False:` | RED-AS-NULL | candidate | True -> False |
| 69b933a6a720006b | coordinator.py:6620 GUARD_OFF | `if still_pending: -> if False:` | RED-AS-NULL | candidate | 1 -> 0 |
| ede3dd3467ffc6e5 | coordinator.py:11214 CMP_BOUND | `if len(horizon.prices) < 4: -> if len(horizon.prices) <= 4:` | RED-AS-NULL | equivalent-candidate | - -> - |
| 9dcd374ac007dfc9 | coordinator.py:11271 BOOLOP | `if "power_cap_kw" in overrides and simulated.predictive_info -> if "power_cap_kw" in overrides or simulated.predictive_info` | RED-AS-NULL | candidate | 0 -> 1 |
| d4b32336085935df | coordinator.py:8457 GUARD_OFF | `if not entry: -> if False:` | RED-AS-NULL | equivalent-candidate | - -> - |
| 4fd094e9727818b3 | coordinator.py:2907 CMP_BOUND | `age > timedelta(minutes=DHW_INLET_MAX_AGE_MINUTES) -> age >= timedelta(minutes=DHW_INLET_MAX_AGE_MINUTES)` | RED-AS-NULL | candidate | 12.0 -> None |
| e2b030e0716d126c | coordinator.py:2910 CMP_BOUND | `-5.0 <= value <= 35.0 -> -5.0 <= value < 35.0` | RED-AS-NULL | candidate | 35.0 -> None |
| dc6c13eca2ca1737 | coordinator.py:1864 GUARD_OFF | `if worker is not None and worker.poll() is None: -> if False:` | KILLED | killed | - -> - |
| 738102c9ed0f89af | coordinator.py:984 GUARD_OFF | `if curve is None: -> if False:` | RED-AS-NULL | candidate | ok -> TypeError |
| 372a4f4fcc8de86f | coordinator.py:490 CMP_BOUND | `value > 0 and -> value >= 0 and` | RED-AS-NULL | candidate | 0 -> 1 |
| 6f5898d327366799 | coordinator.py:3101 CMP_BOUND | `precip > 1e-9, -> precip >= 1e-9,` | RED-AS-NULL | candidate | 1.0 -> 0.0 |
| b247841f5466162d | coordinator.py:2539 CMP_BOUND | `if now_s < starts[0]: -> if now_s <= starts[0]:` | RED-AS-NULL | equivalent-candidate | - -> - |

## Survivors: step-4 answers

### 9efe002b48e1827d HeatPumpOptimizerCoordinator.async_run_optimization (coordinator.py:6360 RETURN_DEL, `return None -> pass`) -- TIMEOUT, timeout

Full gate TIMEOUT (unfinished). Pre-gate probe numbers below.

``

    RESULT reentrant_solves_baseline=0 mutant=2
    RESULT inflight_flag_after_baseline=True mutant=False
    RESULT null_moved=0 count  (no solve in flight: baseline (1, False, None), mutant (1, False, None))
    RESULT thread_factor=1.000
    RESULT load1=0.00
    RESULT swapins=0 count

### a7488872387d5ca7 HeatPumpOptimizerCoordinator.async_run_optimization (coordinator.py:6379 CMP_BOUND, `if len(prices) < 4: -> if len(prices) <= 4:`) -- RED-AS-NULL, equivalent-candidate

No input moved the number. tests/config_flow_steps.py, tests/entities.py, tests/features.py execute line 6379; none can fail: the horizon is 0 or opt_config.n_steps (96) steps long, and no config path sets horizon_hours

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_a7488872.py`

    RESULT no_prices_len=0 baseline='no_prices' mutant='no_prices'
    RESULT one_hour_from_now_len=96 baseline=None mutant=None
    RESULT two_hours_from_now_len=96 baseline=None mutant=None
    RESULT past_only_len=0 baseline='no_prices' mutant='no_prices'
    RESULT head_2h_past_len=96 baseline=None mutant=None
    RESULT tail_23h_len=0 baseline='no_prices' mutant='no_prices'
    RESULT day_and_half_len=96 baseline=None mutant=None
    RESULT lengths_seen=[0, 96]
    RESULT moved_production=0 count
    RESULT sensitivity_1h_horizon_len=4 baseline=None mutant='no_prices'  (not a production horizon)
    RESULT null_moved=0 count  (len=5)
    RESULT thread_factor=1.000
    RESULT load1=1.08
    RESULT swapins=0 count

### 61e748f094f2daa8 HeatPumpOptimizerCoordinator.async_run_optimization (coordinator.py:6454 CMP_BOUND, `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT: -> if self._solve_failures > SOLVE_FAILURE_ISSUE_COUNT:`) -- RED-AS-NULL, candidate

After exactly SOLVE_FAILURE_ISSUE_COUNT (3) failed cycles and one successful cycle, the baseline deletes the solve_failures repair issue (0 left); with `>=` -> `>` the persistent issue stays open (1 left). Should have failed: tests/features.py's 'three consecutive failed solves raise exactly one repair issue' (features.py ~28248) raises the issue at 3 failures but never runs the recovering solve and asserts the issue is gone. Title: No check recovers after exactly three failed solves; the solve_failures repair issue's deletion boundary is unpinned (class_guess I1, severity medium).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_61e748f0.py`

    RESULT issues_left_after_recovery_3_failures_baseline=0 mutant=1  (raised 1 / 1)
    RESULT null_moved=0 count  (4 failures: baseline (1, 0), mutant (1, 0))
    RESULT thread_factor=1.000
    RESULT load1=0.88
    RESULT swapins=0 count

### a33188790c5affad HeatPumpOptimizerCoordinator.async_run_optimization (coordinator.py:6454 GUARD_OFF, `if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT: -> if False:`) -- RED-AS-NULL, candidate

After 3 failed cycles and one successful cycle the baseline deletes the solve_failures repair issue (0 left); with the deletion guard forced off the persistent issue stays open after recovery (1 left). Should have failed: tests/features.py's 'three consecutive failed solves raise exactly one repair issue' (features.py ~28248) never runs a recovering solve and asserts the issue is deleted. Title: No check asserts a successful solve deletes the solve_failures repair issue; removing the deletion is unseen (class_guess I1, severity medium).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_a3318879.py`

    RESULT issues_left_after_recovery_3_failures_baseline=0 mutant=1  (raised 1 / 1)
    RESULT null_moved=0 count  (1 failures: baseline (0, 0), mutant (0, 0))
    RESULT thread_factor=1.000
    RESULT load1=1.02
    RESULT swapins=0 count

### 94285425a1bc856a HeatPumpOptimizerCoordinator.async_shutdown (coordinator.py:6615 GUARD_OFF, `if pending: -> if False:`) -- RED-AS-NULL, candidate

A 0.3 s background task pending at unload has finished when the baseline's async_shutdown returns (True); with the `if pending:` guard forced off shutdown returns with it still running (False). Should have failed: tests/features.py, tests/entities.py, tests/config_flow_steps.py execute line 6615 on their traced baselines; none registers a still-running task in coord._background_tasks before async_shutdown and asserts it is done afterwards. Title: No check asserts async_shutdown awaits pending background tasks; skipping the capped wait is unseen (class_guess I1, severity medium).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_94285425.py`

    RESULT pending_task_baseline=task_done:True warnings:0 mutant=task_done:False warnings:0
    RESULT task_done_baseline=True mutant=False
    RESULT null_moved=0 count  (already-done task: baseline (True, 0), mutant (True, 0))
    RESULT thread_factor=1.000
    RESULT load1=0.87
    RESULT swapins=0 count

### 69b933a6a720006b HeatPumpOptimizerCoordinator.async_shutdown (coordinator.py:6620 GUARD_OFF, `if still_pending: -> if False:`) -- RED-AS-NULL, candidate

A background task that outlives async_shutdown's 5 s capped wait is reported by one warning on the baseline; with the `if still_pending:` guard forced off no warning is logged (0). Should have failed: tests/features.py executes line 6620 on its traced baseline; no check wedges a background task past the 5 s cap and asserts the warning. Title: No check asserts the 5 s shutdown-cap warning for a wedged background task; dropping it is unseen (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_69b933a6.py`

    RESULT wedged_task_baseline=task_done:False warnings:1 mutant=task_done:False warnings:0
    RESULT warnings_baseline=1 mutant=0
    RESULT null_moved=0 count  (0.3 s task: baseline (True, 0), mutant (True, 0))
    RESULT thread_factor=1.000
    RESULT load1=0.78
    RESULT swapins=0 count

### ede3dd3467ffc6e5 HeatPumpOptimizerCoordinator.async_simulate (coordinator.py:11214 CMP_BOUND, `if len(horizon.prices) < 4: -> if len(horizon.prices) <= 4:`) -- RED-AS-NULL, equivalent-candidate

No input moved the number. tests/config_flow_steps.py, tests/features.py execute line 11214; none can fail: the horizon is 0 or opt_config.n_steps (96) steps long, and no config path sets horizon_hours

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_ede3dd34.py`

    RESULT no_prices_len=0 baseline=no_prices mutant=no_prices
    RESULT one_hour_from_now_len=96 baseline=priced mutant=priced
    RESULT two_hours_from_now_len=96 baseline=priced mutant=priced
    RESULT past_only_len=0 baseline=no_prices mutant=no_prices
    RESULT head_2h_past_len=96 baseline=priced mutant=priced
    RESULT tail_23h_len=0 baseline=no_prices mutant=no_prices
    RESULT day_and_half_len=96 baseline=priced mutant=priced
    RESULT lengths_seen=[0, 96]
    RESULT moved_production=0 count
    RESULT sensitivity_1h_horizon_len=4 baseline=priced mutant=no_prices  (not a production horizon)
    RESULT null_moved=0 count  (len=5)
    RESULT thread_factor=1.000
    RESULT load1=0.82
    RESULT swapins=0 count

### 9dcd374ac007dfc9 HeatPumpOptimizerCoordinator.async_simulate (coordinator.py:11271 BOOLOP, `if "power_cap_kw" in overrides and simulated.predictive_info -> if "power_cap_kw" in overrides or simulated.predictive_info`) -- RED-AS-NULL, candidate

The what-if payload async_simulate returns for {"target_temperature": 22.0} carries no power_cap_breach_c on the baseline (0); with `and` -> `or` it carries power_cap_breach_c=0.0 though no power cap was asked (1). Should have failed: tests/features.py and tests/config_flow_steps.py execute line 11271; the T2 power-cap what-if checks assert the key when capped but no check asserts its absence for an uncapped what-if. Title: No check asserts an uncapped what-if omits power_cap_breach_c; and -> or adds it to every simulate answer (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_9dcd374a.py`

    RESULT no_cap_breach_key_baseline=0 mutant=1 (mutant value 0.0)
    RESULT no_cap_empty_breach_key_baseline=0 mutant=1 (mutant value 0.0)
    RESULT null_moved=0 count  (capped: (1, 0.0))
    RESULT thread_factor=1.000
    RESULT load1=0.87
    RESULT swapins=0 count

### d4b32336085935df HeatPumpOptimizerCoordinator.month_channel_totals (coordinator.py:8457 GUARD_OFF, `if not entry: -> if False:`) -- RED-AS-NULL, equivalent-candidate

No input moved the number. none can fail through production: ledger.py:MonthlyLedger.line returns {'kwh': 0.0, 'sek': 0.0} (truthy) for an empty month or line, so the guard never fires on the baseline either (see the lead on the docstring's None contract)

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_d4b32336.py`

    RESULT fresh_ledger_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT other_month_only_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT other_line_only_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT restored_non_dict_entry_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT moved_production=0 count
    RESULT stub_empty_dict_baseline=None mutant=(0.0, 0.0)  (not a production ledger)
    RESULT stub_none_baseline=None mutant=AttributeError  (not a production ledger)
    RESULT null_moved=0 count
    RESULT thread_factor=1.002
    RESULT load1=0.77
    RESULT swapins=0 count

### 4fd094e9727818b3 _dhw_inlet_c (coordinator.py:2907 CMP_BOUND, `age > timedelta(minutes=DHW_INLET_MAX_AGE_MINUTES) -> age >= timedelta(minutes=DHW_INLET_MAX_AGE_MINUTES)`) -- RED-AS-NULL, candidate

A 12.0 degC DHW inlet reading exactly DHW_INLET_MAX_AGE_MINUTES (24 h) old is used on the baseline (12.0); with `>` -> `>=` it is rejected (None) and the seasonal model is used instead. Should have failed: tests/block_duty.py, tests/boost_drift_replay.py, tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/finite_boundary.py, tests/manual_plan.py, tests/solar_alignment.py execute line 2907; none feeds an inlet reading aged exactly 24 h. Title: No check pins _dhw_inlet_c's staleness boundary at exactly 24 h; > -> >= is unseen (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_4fd094e9.py`

    RESULT age_at_limit_baseline=12.0
    RESULT age_at_limit_mutant=None
    RESULT null_moved=0 count
    RESULT thread_factor=1.002
    RESULT load1=0.80
    RESULT swapins=0 count

### e2b030e0716d126c _dhw_inlet_c (coordinator.py:2910 CMP_BOUND, `-5.0 <= value <= 35.0 -> -5.0 <= value < 35.0`) -- RED-AS-NULL, candidate

A fresh DHW inlet reading of exactly 35.0 degC is used on the baseline (35.0); with `<= 35.0` -> `< 35.0` it is rejected (None) and the seasonal model is used. Should have failed: tests/features.py and the other traced closure scripts execute line 2910; none feeds an inlet reading at the 35.0 degC bound. Title: No check pins _dhw_inlet_c's 35 degC plausibility bound; <= -> < is unseen (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_e2b030e0.py`

    RESULT inlet_35_baseline=35.0
    RESULT inlet_35_mutant=None
    RESULT null_moved=0 count
    RESULT thread_factor=1.004
    RESULT load1=0.78
    RESULT swapins=0 count

### 738102c9ed0f89af _fold_flow_lift (coordinator.py:984 GUARD_OFF, `if curve is None: -> if False:`) -- RED-AS-NULL, candidate

With a fresh supply reading and a non-finite outdoor temperature (curve_supply_temp returns None) _fold_flow_lift returns without folding on the baseline; with `if curve is None:` forced off it raises TypeError into _record_accuracy (coordinator.py:10011). Should have failed: tests/features.py executes line 984 on its traced baseline; no check drives _fold_flow_lift with curve_supply_temp returning None and asserts no fold and no raise. Title: No check folds a flow-curve residual with an unusable curve; dropping _fold_flow_lift's None guard is unseen (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_738102c9.py`

    RESULT outdoor_nan_baseline=ok samples=0 mutant=TypeError
    RESULT outdoor_inf_baseline=ok samples=0 mutant=TypeError
    RESULT null_moved=0 count  (finite outdoor: ok samples=1)
    RESULT thread_factor=1.007
    RESULT load1=0.78
    RESULT swapins=0 count

### 372a4f4fcc8de86f _learned_pair (coordinator.py:490 CMP_BOUND, `value > 0 and -> value >= 0 and`) -- RED-AS-NULL, candidate

A stored fold [0.0, 3] is refused by _learned_pair on the baseline (ValueError, dropped: accepted 0); with `value > 0` -> `value >= 0` it is installed (accepted 1). Should have failed: tests/features.py / tests/entities.py store-restore checks execute line 490; none restores a learned pair whose value is exactly 0.0 and asserts it is dropped. Title: No check restores a stored learned pair with value 0.0; _learned_pair's > 0 bound is unpinned (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_372a4f4f.py`

    RESULT zero_value_baseline=0
    RESULT zero_value_mutant=1
    RESULT neg_zero_value_baseline=0
    RESULT neg_zero_value_mutant=1
    RESULT null_moved=0 count
    RESULT thread_factor=1.000
    RESULT load1=0.85
    RESULT swapins=0 count

### 6f5898d327366799 _liquid_fraction (coordinator.py:3101 CMP_BOUND, `precip > 1e-9, -> precip >= 1e-9,`) -- RED-AS-NULL, candidate

For one step with precipitation exactly 1e-9 mm/h and a snowfall of at least that water equivalent, _liquid_fraction returns 1.0 on the baseline and 0.0 with `>` -> `>=`; the step's wetting contribution is ~1e-9 either way. Should have failed: tests/entities.py and tests/features.py execute line 3101; none feeds precipitation exactly at the 1e-9 threshold. Title: No check pins _liquid_fraction's dry threshold at precip == 1e-9; > -> >= is unseen (class_guess I1, severity low).

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_6f5898d3.py`

    RESULT precip_1e-9_snow_baseline=1.0 mutant=0.0
    RESULT null_moved=0 count
    RESULT thread_factor=1.004
    RESULT load1=0.86
    RESULT swapins=0 count

### b247841f5466162d _open_loop_plan_value (coordinator.py:2539 CMP_BOUND, `if now_s < starts[0]: -> if now_s <= starts[0]:`) -- RED-AS-NULL, equivalent-candidate

No input moved the number. tests/entities.py and tests/features.py execute line 2539; none can fail on a valid plan: at the tie both arms return trajectory[0]; only a malformed plan with a duplicated head timestamp separates them

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_b247841f.py`

    RESULT tie_96_steps_baseline=50.0 mutant=50.0
    RESULT tie_1_step_baseline=50.0 mutant=50.0
    RESULT tie_2_steps_baseline=50.0 mutant=50.0
    RESULT tie_plus_1us_baseline=50.0 mutant=50.0
    RESULT tie_minus_1us_baseline=50.0 mutant=50.0
    RESULT before_600s_baseline=50.0 mutant=50.0
    RESULT before_901s_baseline=None mutant=None
    RESULT mid_baseline=62.0 mutant=62.0
    RESULT past_end_baseline=None mutant=None
    RESULT moved_valid=0 count
    RESULT dup_head_baseline=51.0 mutant=50.0  (malformed plan, not a production state)
    RESULT thread_factor=1.004
    RESULT load1=0.78
    RESULT swapins=0 count

## Killed

- dc6c13eca2ca1737 custom_components/heatpump_optimizer/coordinator.py:1864 GUARD_OFF `if worker is not None and worker.poll() is None: -> if False:`: killed by python3 tests/boost_drift_replay.py, python3 tests/features.py (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src pre --key dc6c13eca2ca1737`), gate_rc 1.

## Coverage

D3.M1, D3.M2, D3.M4, D3.M5 and their C-items are carried verbatim from REPORT-D3-u1b.json. D3.M3 is this wave's row: universe 742, examined 15, the rest named by box in REPORT.json's not_reached.

## Unfinished

- 9efe002b48e1827d custom_components/heatpump_optimizer/coordinator.py:6360 RETURN_DEL (return None -> pass): full gate TIMEOUT past the 14400 s cap; last script running: python3 tests/features.py; capped at 14400 s (gate_wave.sh GATE_CAP) while python3 tests/features.py sat idle (load1 0.00 at 2.5 h) after printing the section '#1754 -- a refresh during an in-flight solve is honoured' (tests/features.py:31448): with the re-run branch's return deleted, the second run request enters the rig's gated executor (_solve_coord's hass.entered/release events) and waits on a release the check never gives, so the suite deadlocks instead of failing an assertion. Neither a finding nor a non-finding (unit (c)); the pre-gate probe (probes/9efe002b48e1827d/probe.out) moves 0 -> 2 solves.; neither finding nor non-finding (pre-gate probe: RESULT reentrant_solves_baseline=0 mutant=2; RESULT inflight_flag_after_baseline=True mutant=False; RESULT null_moved=0 count  (no solve in flight: baseline (1, False, None), mutant (1, False, None)); RESULT thread_factor=1.000; RESULT load1=0.00; RESULT swapins=0 count)
