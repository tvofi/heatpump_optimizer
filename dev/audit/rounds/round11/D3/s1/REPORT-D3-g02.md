# D3-s1 wave box D3-g02 — full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Findings: none numbered here (the consolidation step assigns ids); candidates under `gate_survivors`.

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1160       13423          12        1801       14926
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.79

## re-fire machine 2026-11-25T00:47:13Z (seat resumed from wip 041a3863; null and 6 gates were taken on the machine above)
nproc 4
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087         754       14055          12        1550       15333
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.28
```

Null control: `fullgate.py null`, gate_rc 1, red only on artefact checks {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 3680.2 s, load1 0.69..0.92. Every wall/CPU/load number is provisional (4 vCPU Intel Xeon @ 2.10GHz, nproc 4, GATE_JOBS=1; the judge re-takes it).
Procedure: gate_wave.sh (out of tree) — null once, then `fullgate.py run --src complete --key <key>` per key of keys.tsv, one at a time, 4 h cap; a predecessor seat took the null and the first 6 gates, this seat the rest after a re-fire.

## Tally

- gated: 16 of 16
- RED-AS-NULL: 16
- KILLED by script: none
- candidates: 10
- equivalent-candidates: 6
- timeouts: 0

| key | site | verdict | class | wall s | load1 |
|---|---|---|---|---|---|
| cd1d099ef87f3ab9 | custom_components/heatpump_optimizer/coordinator.py:4525 GUARD_OFF | RED-AS-NULL | candidate | 3512.3 | 1.01..1.0 |
| 473508040d23cc21 | custom_components/heatpump_optimizer/coordinator.py:4528 CLAMP_DROP | RED-AS-NULL | candidate | 3408.9 | 0.93..0.93 |
| ad8a02e5c07428ab | custom_components/heatpump_optimizer/coordinator.py:4538 GUARD_OFF | RED-AS-NULL | candidate | 3451.5 | 0.86..0.96 |
| b3a8cff2e5c0a8cc | custom_components/heatpump_optimizer/coordinator.py:5654 CMP_BOUND | RED-AS-NULL | candidate | 3538.3 | 0.89..0.92 |
| 59027d3bdf2e7a0c | custom_components/heatpump_optimizer/coordinator.py:5656 CMP_BOUND | RED-AS-NULL | candidate | 3528.2 | 0.85..0.92 |
| 7d276b43052dbeb9 | custom_components/heatpump_optimizer/coordinator.py:5658 CMP_BOUND | RED-AS-NULL | equivalent-candidate | 3428.3 | 0.78..0.92 |
| 953a106a1aa39cee | custom_components/heatpump_optimizer/coordinator.py:5658 GUARD_OFF | RED-AS-NULL | equivalent-candidate | 3311.8 | 0.41..0.92 |
| 4b296fec48fc594f | custom_components/heatpump_optimizer/coordinator.py:5663 CMP_BOUND | RED-AS-NULL | equivalent-candidate | 3265.4 | 0.93..0.96 |
| 58fe17a0726473a6 | custom_components/heatpump_optimizer/coordinator.py:5663 GUARD_OFF | RED-AS-NULL | equivalent-candidate | 3302.7 | 0.89..0.92 |
| 2700e28d79c64bd8 | custom_components/heatpump_optimizer/coordinator.py:5665 CMP_BOUND | RED-AS-NULL | candidate | 3314.6 | 0.71..0.93 |
| 223ac303af04edde | custom_components/heatpump_optimizer/coordinator.py:5671 GUARD_OFF | RED-AS-NULL | equivalent-candidate | 3349.3 | 0.79..0.92 |
| 9d324a1dc7a6aa82 | custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND | RED-AS-NULL | candidate | 3458.6 | 0.78..0.92 |
| bb1abbfc58114a17 | custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND | RED-AS-NULL | candidate | 3432.6 | 0.87..0.92 |
| 74dbcc2eae2c24f5 | custom_components/heatpump_optimizer/coordinator.py:5679 CMP_BOUND | RED-AS-NULL | candidate | 3517.7 | 0.86..0.92 |
| 355c3d7dd36a1b90 | custom_components/heatpump_optimizer/coordinator.py:5782 CMP_BOUND | RED-AS-NULL | candidate | 3621.7 | 0.85..0.92 |
| 206a570d8cc784e3 | custom_components/heatpump_optimizer/coordinator.py:5800 GUARD_OFF | RED-AS-NULL | equivalent-candidate | 3537.4 | 0.86..0.92 |

## Survivors (step-4 answers)

### cd1d099ef87f3ab9 — custom_components/heatpump_optimizer/coordinator.py:4525 GUARD_OFF (candidate)

Patch `if result.timestamps: -> if False:` in `HeatPumpOptimizerCoordinator._async_drive_pumps`. Gate RED-AS-NULL (rc 1, wall 3512.3 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_cd1d099ef87f3ab9.py`: baseline turn_on (step 5 and step 6 of a plan heating only in steps 4-7); turn_off (step 10 of a plan heating only in step 0); mutant turn_off; turn_off; turn_on. Inputs tried: step5_heat_only_4_7, step6_heat_only_4_7, step10_heat_only_step0, step0_null, all_off_null, cold_rail_null. Candidate: No check fails when the space pump stops walking the plan: its step index can stay at step 0 (coordinator.py:4525). With coordinator.py:4525 `if result.timestamps:` disabled, _async_drive_pumps commands the space circulation pump from the plan's first step instead of the current one -- turn_off at 1.25 h into a plan that heats in steps 4-7 (baseline turn_on) -- and the full GATE_SCOPE=full gate stays green beyond its null. Severity claimed high, class_guess new. Should have failed: tests/dst_checks.py and tests/features.py — a space-pump tick with `now` inside a plan step whose heat differs from step 0 (e.g. heat only in steps 4-7, tick at 1.25 h) asserting turn_on (and the mirror: heat only in step 0, tick at 2.5 h, asserting turn_off)

### 473508040d23cc21 — custom_components/heatpump_optimizer/coordinator.py:4528 CLAMP_DROP (candidate)

Patch `idx = int(max(0.0, since0 / 3600.0 / dt_hours)) -> idx = int((0.0))` in `HeatPumpOptimizerCoordinator._async_drive_pumps`. Gate RED-AS-NULL (rc 1, wall 3408.9 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_473508040d23cc21.py`: baseline turn_on (step 5 and step 6 of a plan heating only in steps 4-7); turn_off (step 10 of a plan heating only in step 0); mutant turn_off; turn_off; turn_on. Inputs tried: step5_heat_only_4_7, step6_heat_only_4_7, step10_heat_only_step0, step0_null, plan_in_future_clamp, all_off_null, cold_rail_null. Candidate: No check fails when the space pump's plan-step index is pinned to 0 (coordinator.py:4528). With coordinator.py:4528 `idx = int(max(0.0, since0 / 3600.0 / dt_hours))` replaced by `idx = int((0.0))`, _async_drive_pumps follows the plan's first step at every tick (turn_off at 1.25 h into a plan heating in steps 4-7, baseline turn_on) and the full gate stays green beyond its null. Severity claimed high, class_guess new. Should have failed: tests/dst_checks.py and tests/features.py — a space-pump tick with `now` inside a plan step whose heat differs from step 0 (e.g. heat only in steps 4-7, tick at 1.25 h) asserting turn_on (and the mirror: heat only in step 0, tick at 2.5 h, asserting turn_off)

### ad8a02e5c07428ab — custom_components/heatpump_optimizer/coordinator.py:4538 GUARD_OFF (candidate)

Patch `if params.two_zone_enabled: -> if False:` in `HeatPumpOptimizerCoordinator._async_drive_pumps`. Gate RED-AS-NULL (rc 1, wall 3451.5 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_ad8a02e5c07428ab.py`: baseline turn_on (two-zone, plan off now/next, room average 21.4 C, upper floor 15 C; likewise lower floor 15 C); mutant turn_off; turn_off. Inputs tried: upper_cold_room_warm, lower_cold_room_warm, zones_warm_null, single_zone_upper_cold_null, room_cold_null. Candidate: No check fails when the space pump ignores a cold floor in a two-zone house (coordinator.py:4538). With coordinator.py:4538 `if params.two_zone_enabled:` disabled, _async_drive_pumps turns the space pump OFF while a floor sits at 15 C under a 21.4 C room average (baseline turn_on via the comfort-floor rail), and the full gate stays green beyond its null. Severity claimed high, class_guess new. Should have failed: tests/features.py — a two-zone coordinator with a warm room average and one floor below the comfort floor + SPACE_PUMP_FLOOR_MARGIN_C, plan off now and next, asserting turn_on

### b3a8cff2e5c0a8cc — custom_components/heatpump_optimizer/coordinator.py:5654 CMP_BOUND (candidate)

Patch `if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS: -> if dt_h <= BUFFER_COOLING_MIN_SAMPLE_HOURS:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3538.3 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_b3a8cff2e5c0a8cc.py`: baseline samples=1 rate=0.4327056338738068 saves=1; mutant samples=0 rate=0.39587982935374616 saves=0. Inputs tried: dt_exact_0p15h, dt_0p14h_null, dt_0p16h_null, dt_1h_null. Candidate: No check pins the 0.15 h minimum buffer-cooling interval at its bound (coordinator.py:5654). With `dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS` -> `<=`, an interval of exactly 0.15 h (540 s, 50.0 -> 49.6 C) is rejected (samples 1 -> 0, rate 0.4327 -> 0.3959 C/h unchanged) and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — an interval of exactly 0.15 h asserting the sample is accepted

### 59027d3bdf2e7a0c — custom_components/heatpump_optimizer/coordinator.py:5656 CMP_BOUND (candidate)

Patch `if dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS: -> if dt_h >= BUFFER_COOLING_MAX_SAMPLE_HOURS:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3528.2 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_59027d3bdf2e7a0c.py`: baseline samples=1 rate=0.39946104468116317 saves=1; mutant samples=0 rate=0.39587982935374616 saves=0. Inputs tried: dt_exact_3h, dt_2p9h_null, dt_3p5h_null, dt_1h_null. Candidate: No check pins the 3 h maximum buffer-cooling interval at its bound (coordinator.py:5656). With `dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS` -> `>=`, an interval of exactly 3.0 h (50.0 -> 48.0 C) is rejected (samples 1 -> 0) and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — an interval of exactly 3.0 h asserting the sample is accepted

### 2700e28d79c64bd8 — custom_components/heatpump_optimizer/coordinator.py:5665 CMP_BOUND (candidate)

Patch `if end_delta < BUFFER_COOLING_MIN_DELTA: -> if end_delta <= BUFFER_COOLING_MIN_DELTA:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3314.6 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_2700e28d79c64bd8.py`: baseline samples=1 rate=0.4075927387094018 saves=1; mutant samples=0 rate=0.39587982935374616 saves=0. Inputs tried: end4_exact_3h, end4_exact_1h, end3p9_null, end4p1_null, cool_null. Candidate: No check pins the 4 K end-delta buffer-cooling guard at its bound (coordinator.py:5665). With `end_delta < BUFFER_COOLING_MIN_DELTA` -> `<=`, an interval ending exactly 4.0 K above ambient (24.5 -> 24.0 C over 3 h, 0.98 C/h inside the bounds) is rejected (samples 1 -> 0) and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — an interval ending exactly 4 K above ambient with an in-bounds implied rate asserting acceptance

### 9d324a1dc7a6aa82 — custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND (candidate)

Patch `if observed < low or observed > high: -> if observed < low or observed >= high:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3458.6 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_9d324a1dc7a6aa82.py`: baseline samples=1 rate=0.4513030054632706 saves=1 (two tie inputs); mutant samples=0 rate=0.39587982935374616 saves=0. Inputs tried: observed_eq_high_1h, observed_eq_high_0p5h, above_high_null, cool_null. Candidate: No check pins the buffer-cooling ceiling as inclusive (coordinator.py:5674 `> high`). With `observed > high` -> `>=`, an interval whose implied rate equals the 35 L tank's ceiling bit-for-bit (3.167038634829969 C/h) is discarded (samples 1 -> 0, rate 0.4513 -> 0.3959) and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — an interval implying exactly the ceiling asserting it is folded (or a documented exclusive bound asserted)

### bb1abbfc58114a17 — custom_components/heatpump_optimizer/coordinator.py:5674 CMP_BOUND (candidate)

Patch `if observed < low or observed > high: -> if observed <= low or observed > high:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3432.6 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_bb1abbfc58114a17.py`: baseline samples=1 rate=0.3167038634829969 saves=1; mutant samples=0 rate=0.39587982935374616 saves=0. Inputs tried: observed_eq_low_3h, observed_eq_low_2h, below_low_null, cool_null. Candidate: No check pins the buffer-cooling floor as inclusive (coordinator.py:5674 `< low`). With `observed < low` -> `<=`, an interval whose implied rate equals the 35 L tank's floor bit-for-bit (0.07917596587074922 C/h, 2 h) is discarded (samples 1 -> 0) and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — an interval implying exactly the floor asserting it is folded

### 74dbcc2eae2c24f5 — custom_components/heatpump_optimizer/coordinator.py:5679 CMP_BOUND (candidate)

Patch `if observed < self._buffer_cooling_rate -> if observed <= self._buffer_cooling_rate` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3517.7 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_74dbcc2eae2c24f5.py`: baseline rate 1.6564106040767905 / 0.932824908459742 / 1.9062583357611946; mutant rate 1.6564106040767907 / 0.9328249084597421 / 1.9062583357611949. Inputs tried: observed_eq_rate1_set, observed_eq_rate2_set, observed_eq_rate0p3_set, observed_eq_rate_1p6564106040767907_set, observed_eq_rate_0p9328249084597421_set, observed_eq_rate_1p9062583357611949_set, below_rate_null, above_rate_null. Candidate: Buffer-cooling alpha choice on an exact tie moves the rate by 1-2 ulp only; no check can see it (coordinator.py:5679). With `observed < self._buffer_cooling_rate` -> `<=`, an observation equal to the current rate blends with ALPHA_DOWN instead of ALPHA_UP, moving the written rate by one or two ulp (1.6564106040767905 -> ...907) on 3 of 6 tie rates tried, and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — none worth adding: the observable difference is float rounding; a check would pin arithmetic, not behaviour

### 355c3d7dd36a1b90 — custom_components/heatpump_optimizer/coordinator.py:5782 CMP_BOUND (candidate)

Patch `if delta_t < HOUSE_LOSS_MIN_DELTA: -> if delta_t <= HOUSE_LOSS_MIN_DELTA:` in `HeatPumpOptimizerCoordinator._async_learn_house_heat_loss`. Gate RED-AS-NULL (rc 1, wall 3621.7 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_355c3d7dd36a1b90.py`: baseline samples=1, scale 1.01 (cooling/flat/two-zone) or 0.99 (warming) at indoor-outdoor exactly 6.0 K; mutant samples=0, scale 1.0. Inputs tried: delta6_exact_cool, delta6_exact_warm, delta6_exact_flat, delta6_exact_two_zone, delta5p9_null, delta26_null. Candidate: No check pins the 6 K minimum indoor-outdoor delta of the house heat-loss learner at its bound (coordinator.py:5782). With `delta_t < HOUSE_LOSS_MIN_DELTA` -> `<=`, a dark 0.5 h interval at exactly 6.0 K indoor-outdoor is skipped (samples 1 -> 0, scale 1.01 -> 1.0) and the full gate stays green beyond its null. Severity claimed low, class_guess new. Should have failed: tests/features.py — an interval at exactly HOUSE_LOSS_MIN_DELTA asserting it is learned (and one just under asserting it is skipped)

### 7d276b43052dbeb9 — custom_components/heatpump_optimizer/coordinator.py:5658 CMP_BOUND (equivalent-candidate)

Patch `if buffer_temp > previous_temp: -> if buffer_temp >= previous_temp:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3428.3 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_7d276b43052dbeb9.py`: baseline inputs_moved=0 of 9; mutant identical on all 9. Inputs tried: equal_50_1h, equal_24_3h, equal_50_0p15h, equal_50_vol0, equal_50_vol1e6, equal_inf, equal_nan, warm_null, cool_null. Equivalent-candidate: `>` and `>=` differ only on an equal pair; equal temperatures imply observed 0.0 C/h, which the volume-derived floor (positive at every volume, 0.0001 L .. 1e6 L tried) rejects; inf/nan pairs are rejected in both arms

### 953a106a1aa39cee — custom_components/heatpump_optimizer/coordinator.py:5658 GUARD_OFF (equivalent-candidate)

Patch `if buffer_temp > previous_temp: -> if False:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3311.8 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_953a106a1aa39cee.py`: baseline inputs_moved=0 of 9; mutant identical on all 9. Inputs tried: warm_48_50_1h, warm_ulp, warm_24_90_0p15h, warm_vol0, warm_vol1e6, warm_to_inf, warm_from_minus_inf, warm_rate_at_floor, cool_null. Equivalent-candidate: a warming interval implies a negative (or non-finite) rate, rejected by the positive floor or the isfinite guard without this line; features.py records the same at 'a tank that got warmer'

### 4b296fec48fc594f — custom_components/heatpump_optimizer/coordinator.py:5663 CMP_BOUND (equivalent-candidate)

Patch `if start_delta < BUFFER_COOLING_MIN_DELTA: -> if start_delta <= BUFFER_COOLING_MIN_DELTA:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3265.4 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_4b296fec48fc594f.py`: baseline inputs_moved=0 of 6; mutant identical on all 6. Inputs tried: start4_equal_1h, start4_cool_3h, start4_end_ulp_below, start4_vol0, start4p5_null, cool_null. Equivalent-candidate: start_delta == 4.0 differs only there; a non-warming interval then has end_delta <= 4.0: < 4 is rejected by the end guard, == 4 implies 0 C/h, below the positive floor

### 58fe17a0726473a6 — custom_components/heatpump_optimizer/coordinator.py:5663 GUARD_OFF (equivalent-candidate)

Patch `if start_delta < BUFFER_COOLING_MIN_DELTA: -> if False:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3302.7 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_58fe17a0726473a6.py`: baseline inputs_moved=0 of 8; mutant identical on all 8. Inputs tried: start3p9_3h, start_ulp_below4_equal, start0_equal, start_neg, start_nan, start_minus_inf, start3p9_vol0, cool_null. Equivalent-candidate: subsumed: a non-warming interval has end_delta <= start_delta < 4, so the end guard rejects every interval this one would; nan/-inf starts are rejected identically; features.py records the same at 'starting within 4 K'

### 223ac303af04edde — custom_components/heatpump_optimizer/coordinator.py:5671 GUARD_OFF (equivalent-candidate)

Patch `if not np.isfinite(observed): -> if False:` in `HeatPumpOptimizerCoordinator._async_learn_buffer_cooling`. Gate RED-AS-NULL (rc 1, wall 3349.3 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_223ac303af04edde.py`: baseline direct call: samples 0 (both inf, both nan, prev nan, end nan); reach_nonfinite_delivered=0 of 4; mutant direct call: samples 1 and 1 save on those 4; unreachable through InputReader. Inputs tried: prev_inf_end50, both_inf, both_nan, prev_huge, prev_huge_end_huge, prev_nan_end50, end_nan, cool_null. Equivalent-candidate: moves only on non-finite temperatures passed by a direct call (4 of 8: samples 0 -> 1 and one save, rate held by @_refuses_non_finite); the sole production caller (coordinator.py:6829-6830) passes only an ok InputReader value, and InputReader refuses nan/inf/-inf (not_numeric) and 1e308 (implausible): reach 0 of 4, so no reachable input distinguishes the arms

### 206a570d8cc784e3 — custom_components/heatpump_optimizer/coordinator.py:5800 GUARD_OFF (equivalent-candidate)

Patch `if not np.isfinite(residual): -> if False:` in `HeatPumpOptimizerCoordinator._async_learn_house_heat_loss`. Gate RED-AS-NULL (rc 1, wall 3537.4 s). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g02/probes/probe_206a570d8cc784e3.py`: baseline inputs_moved=0 of 9; mutant identical on all 9; nonfinite_residuals_past_guard=6. Inputs tried: observed_nan, observed_inf, observed_minus_inf, observed_nan_two_zone, observed_nan_sustained_power0, outdoor_nan_predicted_nan, power_nan, room0_nan, finite_null. Equivalent-candidate: the mutant lets 6 non-finite residuals past the line, but drift.Cusum.update refuses non-finite residuals and _loss_residual_rejected rejects nan/inf (abs(nan) <= bound is False), so no learner state, save or return value moves

## Unfinished

- none

## Coverage

D3.M3: universe 742, examined 16 by this box; 726 not reached (every other key assigned to its box D3-g01..D3-g47, listed in REPORT.json). D3.M1, D3.M2, D3.M4, D3.M5 rows and the redispatched C-items carried verbatim from REPORT-D3-u1b.json.
