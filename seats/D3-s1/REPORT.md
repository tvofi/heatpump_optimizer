# D3-s1, box D3-g30: full gate for 16 D3.M3 full-net survivors (price_model.py)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Seat D3-s1, round 11, wave box D3-g30. Walls, CPU and load are provisional; counts and probe values are final.

## Machine and controls

```
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087        1016       13567          12        1802       15071
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.87
taken: 2026-11-22T21:43:44Z
note: venv-ci lives at /opt/hpo/venv-ci; $HOME/venv-ci is a symlink to it (box-local, not pushed)

## re-fire 2026-11-25T00:52:54Z (new container, successor seat)
nproc: 4
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087         742       14057          12        1559       15345
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.41
note: venv-ci at /opt/hpo/venv-ci; $HOME/venv-ci symlink (box-local)
```

Null control (`python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`, comment-only marker): gate_rc=1, failed_scripts=['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], summary=['3 TEST SCRIPT(S) FAILED'], wall 3777.3 s, load1 0.83..1.05. Record `dev/audit/rounds/round11/D3/s1/wave/D3-g30/gates/null.json`.

Procedure: gate_wave.sh (dispatch tool) ran `fullgate.py run --src complete --key <key>` for each key of keys.tsv in order, one gate at a time (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh with the one-line mutant committed, 4 h cap). Each survivor's step-4 answer was executed by a probe that re-executes price_model.py from its own source with the one line replaced, in memory, run from a separate clean baseline worktree (never the gate's tree), driving the production caller PriceShapeLearner.fold / from_dict / summary / predict / expected_daily_min where one exists.

## Tally

- gated: 16 of 16
- verdicts: RED-AS-NULL 16
- KILLED by: none
- TIMEOUT: none
- candidates (full-gate survivors whose probe moves): 14
- equivalent-candidates: 2

## Gated

| key | site | patch | verdict | killed_by | wall s | load1 | class |
|---|---|---|---|---|---|---|---|
| b10967dd4ea185fd | price_model.py:72 CONST | `SHAPE_MIN = 0.2 -> SHAPE_MIN = 0.4` | RED-AS-NULL | - | 3634.9 | 0.97..0.93 | candidate |
| 7e5493bcbddd6c18 | price_model.py:80 CONST | `QUARTER_ALPHA = 0.12 -> QUARTER_ALPHA = 0.24` | RED-AS-NULL | - | 3478.5 | 0.94..0.92 | candidate |
| 66686e3bc3bac9b9 | price_model.py:81 CONST | `QUARTER_CONFIDENCE_DAYS = 5 -> QUARTER_CONFIDENCE_DAYS = 10` | RED-AS-NULL | - | 3502.6 | 0.3..1.18 | candidate |
| 5bf50f5d986f927d | price_model.py:84 CONST | `QUARTER_FACTOR_MIN = 0.25 -> QUARTER_FACTOR_MIN = 0.5` | RED-AS-NULL | - | 3468.2 | 1.0..0.92 | candidate |
| cc96ce9e391ca6f2 | price_model.py:85 CONST | `QUARTER_FACTOR_MAX = 4.0 -> QUARTER_FACTOR_MAX = 8.0` | RED-AS-NULL | - | 3550.2 | 0.72..0.92 | candidate |
| b5aef00760fd5ea8 | price_model.py:90 CONST | `VAR_ALPHA = 0.15 -> VAR_ALPHA = 0.3` | RED-AS-NULL | - | 3555.8 | 0.79..0.92 | candidate |
| b9b6cf1d15a84248 | price_model.py:337 GUARD_OFF | `if not day_types or not np.isfinite(level) or level <= 0.0: -> if False:` | RED-AS-NULL | - | 3147.4 | 0.29..0.92 | candidate |
| a5c9796d35117839 | price_model.py:342 CMP_BOUND | `if self.days[idx] < SHAPE_CONFIDENCE_DAYS: -> if self.days[idx] <= SHAPE_CONFIDENCE_DAYS:` | RED-AS-NULL | - | 3137.3 | 0.78..1.0 | candidate |
| 13cadf1ab9a2de61 | price_model.py:400 CMP_BOUND | `if var is not None and max(max(s) for s in var) <= RESIDUAL_VAR_MAX: -> if var is not None and max(max(s) for s in var) < RESIDUAL_VAR_MAX:` | RED-AS-NULL | - | 3156.6 | 0.85..0.92 | candidate |
| b5a482468c783209 | price_model.py:207 CMP_BOUND | `if mean <= 1e-6: -> if mean < 1e-6:` | RED-AS-NULL | - | 3295.8 | 0.78..0.93 | candidate |
| 0b10a7c76e2514d2 | price_model.py:219 GUARD_OFF | `if self.days[idx] == 0: -> if False:` | RED-AS-NULL | - | 3186.7 | 0.86..0.92 | candidate |
| c4697335da324182 | price_model.py:226 GUARD_OFF | `if self.days[idx] == 0: -> if False:` | RED-AS-NULL | - | 3301.1 | 0.8..0.92 | candidate |
| 79c65c4903e72ee2 | price_model.py:232 CLAMP_DROP | `updated = updated / max(float(np.mean(updated)), 1e-6) -> updated = updated / (float(np.mean(updated)))` | RED-AS-NULL | - | 3396.2 | 0.86..0.92 | equivalent-candidate |
| 4e79ba6ea642d086 | price_model.py:258 CMP_BOUND | `usable = hour_means > 1e-6 -> usable = hour_means >= 1e-6` | RED-AS-NULL | - | 3405.2 | 0.86..1.12 | candidate |
| 12cd6ddd79fb36fc | price_model.py:269 GUARD_OFF | `if self.quarter_days[idx] == 0: -> if False:` | RED-AS-NULL | - | 3536.6 | 1.01..0.92 | candidate |
| cee6857510fbe69e | price_model.py:275 CLAMP_DROP | `updated = updated / np.maximum(updated.mean(axis=1, keepdims=True), 1e-6) -> updated = updated / (updated.mean(axis=1, keepdims=True))` | RED-AS-NULL | - | 3411.9 | 0.85..0.92 | equivalent-candidate |

## Survivors: step-4 answers and probe numbers

### b10967dd4ea185fd price_model.py:72 CONST (candidate, gate RED-AS-NULL)

Patch `SHAPE_MIN = 0.2 -> SHAPE_MIN = 0.4`. Doubling the shape floor raises the cheapest learned hour of an ordinary winter weekday from 0.2914 to 0.3945 of the daily mean (and a 0.01 SEK hour from 0.1985 to 0.3903) through PriceShapeLearner.fold, and quarters RESIDUAL_VAR_MAX (225 -> 56.25), yet no gated script fails: the guessed price tail's night trough is flattened silently.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b10967dd4ea185fd.py`: shape_min_winter_day: baseline 0.291439 -> mutant 0.394538; shape_min_one_hour_0p01: baseline 0.198468 -> mutant 0.390283; null_delta 0 count; inputs tried: winter_day,one_hour_0p01,one_hour_negative,mild_day_ratios_0p8_1p2,flat.

Should have failed: tests/features.py 'Unknown price horizon (item 7)' block (~3660-3700, traced executing price_model.py:72 via observe_day's clip): it checks only that a trough exists (predict(03:00) < predict(12:00)); it lacks an assertion that a learned hour below SHAPE_MIN x mean is stored at exactly SHAPE_MIN, i.e. shapes[idx] min after a day with a 0.01 hour.

Finding fields: title "price_model.py:72 SHAPE_MIN 0.2 -> 0.4 survives the full gate: the learned price shape's floor is unpinned"; class_guess I1; severity_claimed low; perturbation the one-line mutant b10967dd4ea185fd: `SHAPE_MIN = 0.2` -> `SHAPE_MIN = 0.4`; direction shape_min_winter_day: 0.291439 -> 0.394538; shape_min_one_hour_0p01: 0.198468 -> 0.390283.

### 7e5493bcbddd6c18 price_model.py:80 CONST (candidate, gate RED-AS-NULL)

Patch `QUARTER_ALPHA = 0.12 -> QUARTER_ALPHA = 0.24`. Doubling the quarter EWMA rate moves the learned 07:00 quarter factor after two opposite-ramp days from 0.924 to 0.948 through PriceShapeLearner.fold; no gated script reads a quarter factor after a second, different day.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_7e5493bcbddd6c18.py`: qf_h7q0_two_days_up_down: baseline 0.924 -> mutant 0.948; null_delta 0 count; inputs tried: two_days_up_down,three_days_up_down_up,one_day_seed_only,two_identical_days.

Should have failed: tests/features.py quarter block (~18722-18800, traced executing observe_day_quarters' EWMA): it folds identical days only (6x the same _q_days day; 3x _spiked), where alpha cancels; it lacks an assertion of quarter_factors after two different days equal to (1-QUARTER_ALPHA)*day1 + QUARTER_ALPHA*day2 renormalised.

Finding fields: title "price_model.py:80 QUARTER_ALPHA 0.12 -> 0.24 survives the full gate: the quarter-factor learning rate is unpinned"; class_guess I1; severity_claimed low; perturbation the one-line mutant 7e5493bcbddd6c18: `QUARTER_ALPHA = 0.12` -> `QUARTER_ALPHA = 0.24`; direction qf_h7q0_two_days_up_down: 0.924 -> 0.948.

### 66686e3bc3bac9b9 price_model.py:81 CONST (candidate, gate RED-AS-NULL)

Patch `QUARTER_CONFIDENCE_DAYS = 5 -> QUARTER_CONFIDENCE_DAYS = 10`. Doubling the quarter confidence ramp changes predict(weekday 07:00, level 1.0) after 5 learned quarter days from 1.57377 to 1.661202 (trust 1.0 -> 0.5) through PriceShapeLearner.fold; the gate's only quarter_confidence check (features.py ~18780) folds QUARTER_CONFIDENCE_DAYS days and reads the constant back, so it moves with the mutant.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_66686e3bc3bac9b9.py`: predict_0700_5_days: baseline 1.57377 -> mutant 1.661202; predict_0700_7_days: baseline 1.57377 -> mutant 1.62623; null_delta 0 count; inputs tried: 5_days,7_days,1_day,0_days,10_days.

Should have failed: tests/features.py ~18772-18800 (traced executing quarter_confidence): it derives its day count from QUARTER_CONFIDENCE_DAYS itself; it lacks a literal pin, e.g. quarter_confidence == 1.0 after exactly 5 quarter days (or 0.6 after 3).

Finding fields: title "price_model.py:81 QUARTER_CONFIDENCE_DAYS 5 -> 10 survives the full gate: the quarter-confidence ramp length is unpinned"; class_guess I1; severity_claimed low; perturbation the one-line mutant 66686e3bc3bac9b9: `QUARTER_CONFIDENCE_DAYS = 5` -> `QUARTER_CONFIDENCE_DAYS = 10`; direction predict_0700_5_days: 1.57377 -> 1.661202; predict_0700_7_days: 1.57377 -> 1.62623.

### 5bf50f5d986f927d price_model.py:84 CONST (candidate, gate RED-AS-NULL)

Patch `QUARTER_FACTOR_MIN = 0.25 -> QUARTER_FACTOR_MIN = 0.5`. Doubling the lower quarter clip raises a learned 06:00 quarter that sat at 0.2x its hour mean from 0.246914 to 0.465116 through PriceShapeLearner.fold, and a stored factor row with ratio 9 loads as 0.465116 instead of 0.2 through from_dict; no gated script feeds a quarter below 0.5x its hour.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_5bf50f5d986f927d.py`: qf_h6q0_quarter_at_0p2_of_hour: baseline 0.246914 -> mutant 0.465116; stored_q0_stored_ratio_9: baseline 0.2 -> mutant 0.465116; null_delta 0 count; inputs tried: stored_ratio_9,stored_ratio_2.

Should have failed: tests/features.py quarter clip check 'a clipped quarter still leaves its hour's factors at mean 1.0' (~18748-18760, traced executing the np.clip): its _spiked hour [0.2,0.2,0.2,20] puts the low quarters at 0.034x, clipped by either bound, and it asserts only the hour mean and max < 4.5; it lacks min(_h6) == QUARTER_FACTOR_MIN / renormaliser as a literal (0.25-based) value.

Finding fields: title "price_model.py:84 QUARTER_FACTOR_MIN 0.25 -> 0.5 survives the full gate: the lower quarter clip is unpinned"; class_guess I1; severity_claimed low; perturbation the one-line mutant 5bf50f5d986f927d: `QUARTER_FACTOR_MIN = 0.25` -> `QUARTER_FACTOR_MIN = 0.5`; direction qf_h6q0_quarter_at_0p2_of_hour: 0.246914 -> 0.465116; stored_q0_stored_ratio_9: 0.2 -> 0.465116.

### cc96ce9e391ca6f2 price_model.py:85 CONST (candidate, gate RED-AS-NULL)

Patch `QUARTER_FACTOR_MAX = 4.0 -> QUARTER_FACTOR_MAX = 8.0`. With negative spot quarters (hour [3.0,-1.0,-1.0,-0.6], mean 0.1) the learned 03:00 quarter factor is 3.368421 at the baseline and 3.657143 under the mutant through PriceShapeLearner.fold, and a stored ratio-20 row loads as 3.2 instead of 3.129584; the gate's 'max(_h6) < 4.5' tolerates the mutant's clip because a non-negative hour can never exceed 4x its mean.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cc96ce9e391ca6f2.py`: qf_h3q0_negative_quarters_q0_30x: baseline 3.368421 -> mutant 3.657143; stored_q0_stored_ratio_20: baseline 3.129584 -> mutant 3.2; null_delta 0 count; inputs tried: stored_ratio_20,stored_ratio_2.

Should have failed: tests/features.py ~18748-18800 (traced executing the np.clip and 'max(_h6) < 4.5'): its spiked hour is non-negative, where 4x is the arithmetic ceiling, so the upper clip never binds differently; it lacks a negative-quarter hour (e.g. [3.0,-1.0,-1.0,-0.6]) asserting the raw factor is clipped at exactly QUARTER_FACTOR_MAX = 4.0.

Finding fields: title "price_model.py:85 QUARTER_FACTOR_MAX 4.0 -> 8.0 survives the full gate: the upper quarter clip is pinned only by a loose bound"; class_guess I1; severity_claimed low; perturbation the one-line mutant cc96ce9e391ca6f2: `QUARTER_FACTOR_MAX = 4.0` -> `QUARTER_FACTOR_MAX = 8.0`; direction qf_h3q0_negative_quarters_q0_30x: 3.368421 -> 3.657143; stored_q0_stored_ratio_20: 3.129584 -> 3.2.

### b5aef00760fd5ea8 price_model.py:90 CONST (candidate, gate RED-AS-NULL)

Patch `VAR_ALPHA = 0.15 -> VAR_ALPHA = 0.3`. Doubling the residual-variance EWMA rate moves the published price_prior weekday_sigma[17] after two different days from 1.0936 to 0.9929 through PriceShapeLearner.fold and PriceShapeModel.summary; no gated script reads residual_var or sigma after a second day.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5aef00760fd5ea8.py`: weekday_sigma_17_two_days_day_reversed: baseline 1.0936 -> mutant 0.9929; null_delta 0 count; inputs tried: two_days_day_reversed,three_days,one_day_seed_only.

Should have failed: tests/features.py ~18820 (_vol block, traced executing observe_day's variance EWMA) and tests/finite_boundary.py's residual_var reads: they assert finiteness/positivity of sigma, not its value; they lack residual_var after two days == (1-VAR_ALPHA)*r1^2 + VAR_ALPHA*r2^2.

Finding fields: title "price_model.py:90 VAR_ALPHA 0.15 -> 0.3 survives the full gate: the published price-prior sigma's learning rate is unpinned"; class_guess I1; severity_claimed low; perturbation the one-line mutant b5aef00760fd5ea8: `VAR_ALPHA = 0.15` -> `VAR_ALPHA = 0.3`; direction weekday_sigma_17_two_days_day_reversed: 1.0936 -> 0.9929.

### b9b6cf1d15a84248 price_model.py:337 GUARD_OFF (candidate, gate RED-AS-NULL)

Patch `if not day_types or not np.isfinite(level) or level <= 0.0: -> if False:`. With the guard off, expected_daily_min([], 0.8) on a trained model raises ValueError (min() of an empty list) where the baseline returns None, and level nan/0/-0.4/inf return nan/0.0/-0.117/inf instead of None. The coordinator's #47 caller (coordinator.py:4355-4375) builds day_types from the days strictly after today up to the legionella deadline and guards only level > 1e-6, so an overdue or due-today cycle hands it []; no gated script calls it with an empty span.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b9b6cf1d15a84248.py`: edm_empty_day_types_level_0p8: baseline None -> mutant 'raises ValueError'; edm_level_nan: baseline None -> mutant nan; null_delta 0 count; inputs tried: empty_day_types_level_0p8,level_nan,level_zero,level_negative,level_inf,normal_level_0p8.

Should have failed: tests/features.py '#47 the elastic legionella gate' block (~20012-20044, traced executing expected_daily_min): its four checks pass non-empty day types and level 1.0; it lacks expected_daily_min([], level) is None (the overdue-deadline span) and expected_daily_min([0], nan/0.0) is None.

Finding fields: title "price_model.py:337 expected_daily_min's input guard deleted survives the full gate: an empty day-type span raises ValueError"; class_guess I1; severity_claimed medium; perturbation the one-line mutant b9b6cf1d15a84248: `if not day_types or not np.isfinite(level) or level <= 0.0:` -> `if False:`; direction edm_empty_day_types_level_0p8: None -> 'raises ValueError'; edm_level_nan: None -> nan.

### a5c9796d35117839 price_model.py:342 CMP_BOUND (candidate, gate RED-AS-NULL)

Patch `if self.days[idx] < SHAPE_CONFIDENCE_DAYS: -> if self.days[idx] <= SHAPE_CONFIDENCE_DAYS:`. After exactly SHAPE_CONFIDENCE_DAYS = 5 folded weekdays the baseline answers expected_daily_min([0], 0.8) = 0.233151 and the mutant None (one more day of 'defer to the deadline' for the #47 legionella gate); the gate's checks use 0, 3, 10 and 30 days, never the boundary.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_a5c9796d35117839.py`: edm_5_days_exactly_confident: baseline 0.233151 -> mutant None; null_delta 0 count; inputs tried: 5_days_exactly_confident,4_days,6_days.

Should have failed: tests/features.py #47 block (~20012-20044, traced executing line 342): 'a partially trained prior still defers' uses days=3 and the trained arms 10 and 30; it lacks expected_daily_min([0], 1.0) is not None at days[0] == SHAPE_CONFIDENCE_DAYS exactly.

Finding fields: title "price_model.py:342 expected_daily_min's confidence boundary < -> <= survives the full gate"; class_guess I1; severity_claimed low; perturbation the one-line mutant a5c9796d35117839: `if self.days[idx] < SHAPE_CONFIDENCE_DAYS:` -> `if self.days[idx] <= SHAPE_CONFIDENCE_DAYS:`; direction edm_5_days_exactly_confident: 0.233151 -> None.

### 13cadf1ab9a2de61 price_model.py:400 CMP_BOUND (candidate, gate RED-AS-NULL)

Patch `if var is not None and max(max(s) for s in var) <= RESIDUAL_VAR_MAX: -> if var is not None and max(max(s) for s in var) < RESIDUAL_VAR_MAX:`. A stored residual_var bin exactly at RESIDUAL_VAR_MAX (225.0) loads as 225.0 at the baseline and restarts at 0.0 under the mutant through PriceShapeModel.from_dict (the restore path); 224.9 and 225.1 load alike in both arms. The learner itself wrote at most 18.8 on an adversarial sequence, so only a hand-edited or foreign store reaches the boundary.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_13cadf1ab9a2de61.py`: var_loaded_exactly_cap_225: baseline 225.0 -> mutant 0.0; null_delta 0 count; inputs tried: exactly_cap_225,below_cap_224p9,above_cap_225p1,typical_0p3.

Should have failed: tests/features.py D1-s5-02 check (~66815-66862, traced executing line 400): it plants 300.0 (above the cap), where both arms reset; it lacks a stored bin of exactly RESIDUAL_VAR_MAX asserting it loads as written.

Finding fields: title "price_model.py:400 from_dict's variance load gate <= -> < survives the full gate (boundary only)"; class_guess I1; severity_claimed low; perturbation the one-line mutant 13cadf1ab9a2de61: `if var is not None and max(max(s) for s in var) <= RESIDUAL_VAR_MAX:` -> `if var is not None and max(max(s) for s in var) < RESIDUAL_VAR_MAX:`; direction var_loaded_exactly_cap_225: 225.0 -> 0.0.

### b5a482468c783209 price_model.py:207 CMP_BOUND (candidate, gate RED-AS-NULL)

Patch `if mean <= 1e-6: -> if mean < 1e-6:`. A 24-hour day of 12 x 0.0 and 12 x 2e-6 (np.mean exactly 1e-6) is rejected at the baseline (days 0) and learned under the mutant (days 1) through PriceShapeLearner.fold; mean 0, 2e-6 and a winter day behave alike in both arms. Sibling of D3-s1-71 (line 252).

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5a482468c783209.py`: days_learned_mean_exactly_1e-6: baseline 0 -> mutant 1; null_delta 0 count; inputs tried: mean_exactly_1e-6,mean_zero,winter_day,mean_2e-6.

Should have failed: tests/features.py 'Unknown price horizon (item 7)' block (~3660-3700) and tests/guard_pins.py observe_day calls (traced executing line 207): they test a partial day and a NaN hour; they lack a day whose mean is exactly 1e-6 asserting observe_day returns False.

Finding fields: title "price_model.py:207 observe_day's mean guard <= -> < survives the full gate (float-exact boundary)"; class_guess I1; severity_claimed low; perturbation the one-line mutant b5a482468c783209: `if mean <= 1e-6:` -> `if mean < 1e-6:`; direction days_learned_mean_exactly_1e-6: 0 -> 1.

### 0b10a7c76e2514d2 price_model.py:219 GUARD_OFF (candidate, gate RED-AS-NULL)

Patch `if self.days[idx] == 0: -> if False:`. With the seed branch off the first observed day blends into the zero prior: the published price_prior weekday_sigma[17] after one winter day falls from 1.1858 to 0.4593 (sqrt(0.15) of it) through PriceShapeLearner.fold and summary(); a flat day gives 0.0 in both arms.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_0b10a7c76e2514d2.py`: weekday_sigma_17_one_winter_day: baseline 1.1858 -> mutant 0.4593; null_delta 0 count; inputs tried: one_winter_day,one_reversed_day,one_flat_day.

Should have failed: tests/features.py ~18820 (_vol block, traced executing line 219) and tests/finite_boundary.py residual_var reads: they assert sigma is finite/positive, not its value; they lack residual_var after one day == residuals**2 (or summary()['weekday_sigma'] after one day equal to |normalised - 1|).

Finding fields: title "price_model.py:219 observe_day's first-day variance seed deleted survives the full gate"; class_guess I1; severity_claimed low; perturbation the one-line mutant 0b10a7c76e2514d2: `if self.days[idx] == 0:` -> `if False:`; direction weekday_sigma_17_one_winter_day: 1.1858 -> 0.4593.

### c4697335da324182 price_model.py:226 GUARD_OFF (candidate, gate RED-AS-NULL)

Patch `if self.days[idx] == 0: -> if False:`. With the seed branch off the first day is EWMA-blended into the flat prior instead of replacing it: the published price_prior weekday_shape[17] after one winter day is 1.142 instead of 2.186, and still 1.56 instead of 2.186 after five identical days (when the shape is fully trusted), through PriceShapeLearner.fold and summary(). The fully trusted guessed tail's evening peak is underpriced by 29% at day 5.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_c4697335da324182.py`: weekday_shape_17_one_winter_day: baseline 2.186 -> mutant 1.142; weekday_shape_17_five_winter_days: baseline 2.186 -> mutant 1.56; null_delta 0 count; inputs tried: one_winter_day,five_winter_days,one_flat_day.

Should have failed: tests/features.py item-7 block (~3660-3700, traced executing line 226): 'the learned shape has a trough at night' and 'one day's evidence is heavily damped' hold in both arms; it lacks shapes[idx] after one observed day == the clipped normalised day exactly.

Finding fields: title "price_model.py:226 observe_day's first-day shape seed deleted survives the full gate"; class_guess I1; severity_claimed medium; perturbation the one-line mutant c4697335da324182: `if self.days[idx] == 0:` -> `if False:`; direction weekday_shape_17_one_winter_day: 2.186 -> 1.142; weekday_shape_17_five_winter_days: 2.186 -> 1.56.

### 4e79ba6ea642d086 price_model.py:258 CMP_BOUND (candidate, gate RED-AS-NULL)

Patch `usable = hour_means > 1e-6 -> usable = hour_means >= 1e-6`. An hour of quarters [0, 0, 0, 4e-6] (mean exactly 1e-6) keeps factor 1.0 at the baseline and learns 3.368421 for its :45 quarter under the mutant through PriceShapeLearner.fold; an all-zero hour and an ordinary ramp behave alike in both arms.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_4e79ba6ea642d086.py`: qf_h3q3_hour_mean_exactly_1e-6: baseline 1.0 -> mutant 3.368421; null_delta 0 count; inputs tried: hour_mean_exactly_1e-6,hour_all_zero,ramp.

Should have failed: tests/features.py G8 observe_day_quarters arms (~58809-58820) and tests/finite_boundary.py (traced executing line 258): they test a short, non-finite and all-zero day; they lack an hour whose mean is exactly 1e-6 asserting its factors stay 1.0.

Finding fields: title "price_model.py:258 observe_day_quarters' usable-hour guard > -> >= survives the full gate (float-exact boundary)"; class_guess I1; severity_claimed low; perturbation the one-line mutant 4e79ba6ea642d086: `usable = hour_means > 1e-6` -> `usable = hour_means >= 1e-6`; direction qf_h3q3_hour_mean_exactly_1e-6: 1.0 -> 3.368421.

### 12cd6ddd79fb36fc price_model.py:269 GUARD_OFF (candidate, gate RED-AS-NULL)

Patch `if self.quarter_days[idx] == 0: -> if False:`. With the seed branch off the first quarter day blends into the flat prior: the learned 07:00 quarter factor after one day is 0.988 instead of 0.9, and predict(weekday 07:00, 1.0) after five days (full quarter trust) is 1.666051 instead of 1.57377, through PriceShapeLearner.fold; a flat quarter day gives 1.0 in both arms.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_12cd6ddd79fb36fc.py`: qf_h7q0_1_day: baseline 0.9 -> mutant 0.988; predict_0700_5_days: baseline 1.57377 -> mutant 1.666051; null_delta 0 count; inputs tried: 1_flat_day.

Should have failed: tests/features.py quarter block (~18722-18770, traced executing line 269): it folds 6 or 3 identical days and checks only ordering (:45 above siblings) and the hour mean; it lacks quarter_factors after one observed day == the clipped per-hour ratios exactly.

Finding fields: title "price_model.py:269 observe_day_quarters' first-day quarter seed deleted survives the full gate"; class_guess I1; severity_claimed low; perturbation the one-line mutant 12cd6ddd79fb36fc: `if self.quarter_days[idx] == 0:` -> `if False:`; direction qf_h7q0_1_day: 0.9 -> 0.988; predict_0700_5_days: 1.57377 -> 1.666051.

### 79c65c4903e72ee2 price_model.py:232 CLAMP_DROP (equivalent-candidate, gate RED-AS-NULL)

Patch `updated = updated / max(float(np.mean(updated)), 1e-6) -> updated = updated / (float(np.mean(updated)))`. Every production path leaves the EWMA'd shape's mean >= 0.12 x SHAPE_MIN > 1e-6 (observe_day clips the day to [0.2, 3] and from_dict's _in_domain keeps stored bins positive), so the floor never binds: one day, two days, spiky days and from_dict-restored negative/zero/tiny rows give identical shapes in both arms. Only a model hand-built with a negative stored shape (bypassing from_dict) separates them.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_79c65c4903e72ee2.py`: shape17_production_one_day: baseline 2.185792349726776 -> mutant 2.185792349726776; shape17_handbuilt_negative_row_bypassing_from_dict: baseline -617704.9180327869 -> mutant 0.812769628990509; null_delta 0 count; inputs tried: negative_row_bypassing_from_dict.

Should have failed: none through production; a direct construction PriceShapeModel(shapes=[[-1.0]*24, ...]) separates (baseline -617704.9, mutant 0.8128).

### cee6857510fbe69e price_model.py:275 CLAMP_DROP (equivalent-candidate, gate RED-AS-NULL)

Patch `updated = updated / np.maximum(updated.mean(axis=1, keepdims=True), 1e-6) -> updated = updated / (updated.mean(axis=1, keepdims=True))`. Every production path keeps each hour's EWMA'd factors positive (an hour with mean <= 1e-6 gets factor 1.0, others are clipped to [0.25, 4]; from_dict's _in_domain repairs stored rows), so the hour mean never drops below 0.25 x 0.12 and the floor never binds: a zero-price hour, a negative hour after a normal day, spike/zero sequences and from_dict-restored negative/zero rows give identical factors in both arms. The carried M4 answer ('an hour whose quarter factors average 0') is not reachable: the usable mask sets such an hour to 1.0. Only a hand-built model with negative stored factors separates.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cee6857510fbe69e.py`: qf12_production_zero_price_hour: baseline 1.0 -> mutant 1.0; qf12_handbuilt_negative_bypassing_from_dict: baseline -760000.0 -> mutant 1.0; null_delta 0 count; inputs tried: negative_bypassing_from_dict.

Should have failed: none through production; a direct construction PriceShapeModel(quarter_factors=[...negative...]) separates (baseline -760000.0, mutant 1.0).

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b10967dd4ea185fd.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_7e5493bcbddd6c18.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_66686e3bc3bac9b9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_5bf50f5d986f927d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cc96ce9e391ca6f2.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5aef00760fd5ea8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b9b6cf1d15a84248.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_a5c9796d35117839.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_13cadf1ab9a2de61.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5a482468c783209.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_0b10a7c76e2514d2.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_c4697335da324182.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_79c65c4903e72ee2.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_4e79ba6ea642d086.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_12cd6ddd79fb36fc.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cee6857510fbe69e.py`
- gate_wave.sh (the dispatch's out-of-tree driver; procedure above)

## Findings

None numbered here: every candidate is under `gate_survivors` in REPORT.json for the orchestrator's consolidation to assign ids across the wave.

