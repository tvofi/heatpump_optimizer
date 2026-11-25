# D3-s1 box D3-g39: full gate for 15 D3.M3 full-net survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Dimension D3, step D3.M3 (full gate) with each survivor's D3.M4 answer executed by a probe.

## Machine and controls

nproc 4, Intel(R) Xeon(R) Processor @ 2.30GHz; MACHINE.txt in this directory. Every wall, CPU and load number is provisional (the judge re-takes it).

Null control (`fullgate.py null`, comment-only marker): gate_rc 1, red scripts python3 tests/closure.py selftest, python3 tests/entities.py, python3 tests/harness_headers.py (fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}), wall 2698.3 s, load1 0.27 -> 1.01. All three are in the earlier boxes' null and are artefact checks of the stripped tree; none is machine-caused, so it was not re-taken. A key red on exactly these scripts with no more fail lines reads RED-AS-NULL (survived).

Procedure: gate_wave.sh run (out-of-tree driver) ran `fullgate.py run --src complete --key <key>` per key, one gate at a time, GATE_JOBS=1, 4 h cap. Probes ran from a second baseline worktree (never the gate's tree), loading the mutated module in memory via probes/_mutload.py.

## Tally

- gated: 15 of 15; verdicts: RED-AS-NULL 15
- KILLED: 0
- TIMEOUT: 0
- candidates (survived, probe moves): 11
- equivalent-candidates (survived, no input found that moves the probe): 4

Findings are returned as `findings: []`; candidates sit under `gate_survivors` for the orchestrator's id assignment.

## Per key

### 559484953b5cdd5d — sysid.py:610 CMP_BOUND — RED-AS-NULL — candidate

`if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9): -> if not (c_r > 1e-9 and c_s > 1e-9 and k_s >= 1e-9):` in `slab_mode_tau_fast`. Gate: gate_rc 1, killed_by [], wall 2732.4 s, load1 0.93 -> 0.96.

Step 4: should have failed tests/entities.py, tests/features.py (their traced baseline executes the line): no check calls slab_mode_tau_fast with k_s exactly 1e-9 and asserts 0.0 (the unset-plant answer).

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_559484953b5cdd5d.py`: cases moved 1, null cases moved 0. Inputs (baseline / mutant): boundary_k_s: 0.0 / 1200000000.0; just_above_k_s: 600000000.0 / 600000000.0; ordinary: 2.4 / 2.4; zero_k_s: 0.0 / 0.0.

Candidate (low, class_guess I1): slab_mode_tau_fast's k_s > 1e-9 guard is unpinned at its bound: k_s == 1e-9 returns 1.2e9 h instead of 0.0 and the full gate stays green. boundary_k_s: baseline 0.0, mutant 1200000000.0; null cases moved 0.

### cb38833c854f6257 — sysid.py:610 CMP_BOUND — RED-AS-NULL — candidate

`if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9): -> if not (c_r >= 1e-9 and c_s > 1e-9 and k_s > 1e-9):` in `slab_mode_tau_fast`. Gate: gate_rc 1, killed_by [], wall 2796.0 s, load1 0.81 -> 0.92.

Step 4: should have failed tests/entities.py, tests/features.py (their traced baseline executes the line): no check calls slab_mode_tau_fast with c_r exactly 1e-9 and asserts 0.0.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_cb38833c854f6257.py`: cases moved 1, null cases moved 0. Inputs (baseline / mutant): boundary_c_r: 0.0 / 1.999999999e-09; just_above_c_r: 3.999999996e-09 / 3.999999996e-09; ordinary: 2.4 / 2.4; zero_c_r: 0.0 / 0.0.

Candidate (low, class_guess I1): slab_mode_tau_fast's c_r > 1e-9 guard is unpinned at its bound: c_r == 1e-9 returns 2.0e-9 h instead of 0.0 and the full gate stays green. boundary_c_r: baseline 0.0, mutant 1.999999999e-09; null cases moved 0.

### fa6fdd76e6fa619d — sysid.py:610 CMP_BOUND — RED-AS-NULL — candidate

`if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9): -> if not (c_r > 1e-9 and c_s >= 1e-9 and k_s > 1e-9):` in `slab_mode_tau_fast`. Gate: gate_rc 1, killed_by [], wall 2696.6 s, load1 0.78 -> 0.92.

Step 4: should have failed tests/entities.py, tests/features.py (their traced baseline executes the line): no check calls slab_mode_tau_fast with c_s exactly 1e-9 and asserts 0.0.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_fa6fdd76e6fa619d.py`: cases moved 1, null cases moved 0. Inputs (baseline / mutant): boundary_c_s: 0.0 / 1.999999999e-09; just_above_c_s: 3.999999996e-09 / 3.999999996e-09; ordinary: 2.4 / 2.4; zero_c_s: 0.0 / 0.0.

Candidate (low, class_guess I1): slab_mode_tau_fast's c_s > 1e-9 guard is unpinned at its bound: c_s == 1e-9 returns 2.0e-9 h instead of 0.0 and the full gate stays green. boundary_c_s: baseline 0.0, mutant 1.999999999e-09; null cases moved 0.

### 246043395831f540 — tariff.py:128 CMP_BOUND — RED-AS-NULL — candidate

`if not self.enabled or self.peaks_averaged <= 0: -> if not self.enabled or self.peaks_averaged < 0:` in `CapacityTariff.marginal_price_per_kw`. Gate: gate_rc 1, killed_by [], wall 2735.0 s, load1 0.72 -> 0.92.

Step 4: should have failed tests/config_flow_steps.py, tests/entities.py, tests/features.py (their traced baseline executes the line): no check builds an enabled CapacityTariff with peaks_averaged 0 and asserts marginal_price_per_kw == 0.0.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_246043395831f540.py`: cases moved 1, null cases moved 0. Inputs (baseline / mutant): disabled0: 0.0 / 0.0; peaks0: 0.0 / raises ZeroDivisionError; peaks3: 16.666666666666668 / 16.666666666666668; peaksneg1: 0.0 / 0.0.

Candidate (low, class_guess I1): CapacityTariff.marginal_price_per_kw's peaks_averaged <= 0 guard is unpinned at 0: an enabled tariff with peaks_averaged 0 raises ZeroDivisionError and the full gate stays green. peaks0: baseline 0.0, mutant raises ZeroDivisionError; null cases moved 0.

### de935c38786265e7 — tariff.py:437 GUARD_OFF — RED-AS-NULL — candidate

`if not math.isfinite(tracker._window_factor): -> if False:` in `PeakTracker.from_dict`. Gate: gate_rc 1, killed_by [], wall 2715.6 s, load1 0.78 -> 0.93.

Step 4: should have failed tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): no check restores a PeakTracker from a payload with window_factor 'nan' or 'inf' and a non-empty window and asserts the factor is 1.0 with the window kept (or the closed peak).

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_de935c38786265e7.py`: cases moved 4, null cases moved 0. Inputs (baseline / mutant): f05_peaks: (1.0, 1.0) / (1.0, 1.0); f1_state: ('2026-01-10T07:00:00|60', 2.0, 1, 1.0) / ('2026-01-10T07:00:00|60', 2.0, 1, 1.0); inf_peaks: (2.0, 1.0) / (1.0,); inf_state: ('2026-01-10T07:00:00|60', 2.0, 1, 1.0) / ('', 0.0, 0, 1.0); nan_peaks: (2.0, 1.0) / (1.0,); nan_state: ('2026-01-10T07:00:00|60', 2.0, 1, 1.0) / ('', 0.0, 0, 1.0).

Candidate (medium, class_guess I1): PeakTracker.from_dict's non-finite window_factor reset is unpinned: with it off a restored 'nan'/'inf' factor discards the open window and its 2 kW peak, and the full gate stays green. nan_peaks: baseline (2.0, 1.0), mutant (1.0,); null cases moved 0.

### 4ad3dc13bfdb70a8 — tariff.py:465 CMP_BOUND — RED-AS-NULL — candidate

`or not 0.0 <= tracker._window_factor <= 1.0 -> or not 0.0 < tracker._window_factor <= 1.0` in `PeakTracker.from_dict`. Gate: gate_rc 1, killed_by [], wall 2807.2 s, load1 0.86 -> 0.97.

Step 4: should have failed tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): no check restores a PeakTracker whose window_factor is 0.0 and asserts the window is kept (key, sum, samples, factor 0.0) with no warning.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_4ad3dc13bfdb70a8.py`: cases moved 1, null cases moved 0. Inputs (baseline / mutant): f05_state: ('2026-01-10T07:00:00|60', 2.0, 1, 0.5) / ('2026-01-10T07:00:00|60', 2.0, 1, 0.5); f0_peaks: (1.0,) / (1.0,); f0_state: ('2026-01-10T07:00:00|60', 2.0, 1, 0.0) / ('', 0.0, 0, 1.0); f1_state: ('2026-01-10T07:00:00|60', 2.0, 1, 1.0) / ('2026-01-10T07:00:00|60', 2.0, 1, 1.0); fneg_state: ('', 0.0, 0, 1.0) / ('', 0.0, 0, 1.0).

Candidate (low, class_guess I1): PeakTracker.from_dict's 0.0 <= window_factor bound is unpinned at 0.0: a legitimately persisted factor-0 (masked-month) window is restarted empty with a warning, and the full gate stays green. f0_state: baseline ('2026-01-10T07:00:00|60', 2.0, 1, 0.0), mutant ('', 0.0, 0, 1.0); null cases moved 0.

### 7fcaf91cced5ce41 — tariff.py:235 GUARD_OFF — RED-AS-NULL — candidate

`if not np.isfinite(house_power_kw) or house_power_kw < 0: -> if False:` in `PeakTracker.observe`. Gate: gate_rc 1, killed_by [], wall 2749.3 s, load1 0.82 -> 1.01.

Step 4: should have failed tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): no check folds a nan, inf or negative house_power_kw into PeakTracker.observe and asserts the closed window's peak is unchanged.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_7fcaf91cced5ce41.py`: cases moved 3, null cases moved 0. Inputs (baseline / mutant): inf_peaks: ((2.0,), 1) / (('inf',), 1); nan_peaks: ((2.0,), 1) / (('nan',), 1); neg_peaks: ((2.0,), 1) / ((0.5,), 1); ok_peaks: ((1.5,), 1) / ((1.5,), 1).

Candidate (medium, class_guess I1): PeakTracker.observe's non-finite/negative sample guard is unpinned: with it off a nan sample makes the month's peak nan and a negative one lowers it 2.0 -> 0.5 kW, and the full gate stays green. nan_peaks: baseline ((2.0,), 1), mutant (('nan',), 1); null cases moved 0.

### 81557beca8f0a974 — tariff.py:279 CMP_BOUND — RED-AS-NULL — equivalent-candidate

`if dt_hours is not None and np.isfinite(dt_hours) and dt_hours > 0: -> if dt_hours is not None and np.isfinite(dt_hours) and dt_hours >= 0:` in `PeakTracker.observe`. Gate: gate_rc 1, killed_by [], wall 2741.8 s, load1 0.85 -> 0.92.

Step 4: should have failed tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): none can: adding house_power_kw * 0.0 to _window_wsum and 0.0 to _window_weight is the identity for every finite kW the line-235 guard admits.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_81557beca8f0a974.py`: cases moved 0, null cases moved 0. Inputs (baseline / mutant): dt025_acc: ('0.75', '0.5', '1.5') / ('0.75', '0.5', '1.5'); dt0_acc: ('0.0', '0.0', '1.5') / ('0.0', '0.0', '1.5'); dt0_bigkw_acc: ('0.0', '0.0', '5e+307') / ('0.0', '0.0', '5e+307'); dt0_mixed_acc: ('0.5', '0.25', '2.0') / ('0.5', '0.25', '2.0'); dt0_peaks: ((1.5,), 1) / ((1.5,), 1); dtneg0_acc: ('0.0', '0.0', '1.5') / ('0.0', '0.0', '1.5').

Equivalent-candidate: no input tried moves the number; a non-finding unless a later seat finds one.

### 8611ebe645da9f19 — tariff.py:391 CMP_BOUND — RED-AS-NULL — equivalent-candidate

`if len(self.peaks) < n: -> if len(self.peaks) <= n:` in `PeakTracker.threshold_kw`. Gate: gate_rc 1, killed_by [], wall 2796.0 s, load1 0.78 -> 1.0.

Step 4: should have failed tests/entities.py, tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): none can: at len(peaks) == n the mutant returns peaks[-1], which is peaks[n-1].

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_8611ebe645da9f19.py`: cases moved 0, null cases moved 0. Inputs (baseline / mutant): len_eq_n0: 3.0 / 3.0; len_eq_n1: 3.0 / 3.0; len_eq_n3: 1.0 / 1.0; len_eq_nan: nan / nan; len_eq_unsorted: 2.0 / 2.0; len_gt: 2.0 / 2.0; len_lt: 2.0 / 2.0.

Equivalent-candidate: no input tried moves the number; a non-finding unless a later seat finds one.

### 37b3c9a03326d207 — tariff.py:489 GUARD_OFF — RED-AS-NULL — candidate

`if not day: -> if False:` in `_one_per_day`. Gate: gate_rc 1, killed_by [], wall 2771.6 s, load1 0.85 -> 0.92.

Step 4: should have failed tests/entities.py, tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): no check passes _one_per_day (or a distinct-days PeakTracker restored from a payload without peak_days) two undated peaks and asserts both are kept.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_37b3c9a03326d207.py`: cases moved 2, null cases moved 0. Inputs (baseline / mutant): distinct_days: [(3.0, '2026-01-04'), (2.0, '2026-01-05')] / [(3.0, '2026-01-04'), (2.0, '2026-01-05')]; two_undated: [(3.0, ''), (2.0, '')] / [(3.0, '')]; undated_plus_dated: [(3.0, ''), (2.0, ''), (1.0, '2026-01-05')] / [(3.0, ''), (1.0, '2026-01-05')].

Candidate (low, class_guess I1): _one_per_day's undated-entry branch is unpinned: with it off two undated peaks collapse into one '' day and the lower is dropped, and the full gate stays green. two_undated: baseline [(3.0, ''), (2.0, '')], mutant [(3.0, '')]; null cases moved 0.

### 7f9297e43c9449d8 — tariff.py:491 CMP_BOUND — RED-AS-NULL — equivalent-candidate

`elif day not in best or kw > best[day][0]: -> elif day not in best or kw >= best[day][0]:` in `_one_per_day`. Gate: gate_rc 1, killed_by [], wall 2765.6 s, load1 0.78 -> 0.93.

Step 4: should have failed tests/entities.py, tests/features.py, tests/finite_boundary.py (their traced baseline executes the line): none can by value: a same-day tie replaces (kw, day) by an equal (kw, day); the only difference is the sign bit of a 0.0/-0.0 tie, which no tracker path produces (window sums start at 0.0).

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_7f9297e43c9449d8.py`: cases moved 0, null cases moved 0. Inputs (baseline / mutant): ordered: [('3.0', 'd')] / [('3.0', 'd')]; signbit_tie_info: [False] / [True]; tie: [('2.0', '2026-01-05')] / [('2.0', '2026-01-05')]; tie_billed: 1.5 / 1.5; tie_nan: [('nan', '2026-01-05')] / [('nan', '2026-01-05')]; tie_signed_zero: [('0.0', '2026-01-05')] / [('0.0', '2026-01-05')]; tie_then_lower: [('2.0', 'd')] / [('2.0', 'd')].

Equivalent-candidate: no input tried moves the number; a non-finding unless a later seat finds one.

### 9d16dbc0d3aba164 — tariff.py:904 GUARD_OFF — RED-AS-NULL — equivalent-candidate

`if house.size == 0: -> if False:` in `_peak_excess`. Gate: gate_rc 1, killed_by [], wall 2847.0 s, load1 0.78 -> 0.93.

Step 4: should have failed tests/features.py, tests/stress.py (their traced baseline executes the line): none can: on an empty plan metering_windows returns the empty array, billed_windows keeps it empty, and np.any(excess > 0) is False, so the result is None either way.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_9d16dbc0d3aba164.py`: cases moved 0, null cases moved 0. Inputs (baseline / mutant): empty_15: None / None; empty_60: None / None; empty_factors: None / None; empty_factors1: None / None; empty_off2: None / None; four_steps: (np.float64(2.0),) / (np.float64(2.0),).

Equivalent-candidate: no input tried moves the number; a non-finding unless a later seat finds one.

### 6536ff6b094f971d — tariff.py:744 GUARD_OFF — RED-AS-NULL — candidate

`if x.size == 0 or k <= 0: -> if False:` in `_smooth_topk_sum`. Gate: gate_rc 1, killed_by [], wall 2701.7 s, load1 0.79 -> 0.97.

Step 4: should have failed tests/features.py, tests/stress.py (their traced baseline executes the line): no check calls _smooth_topk_sum (or _plateau_aware_topk_sum / the smooth capacity charge) with k <= 0 and asserts 0.0.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_6536ff6b094f971d.py`: cases moved 2, null cases moved 0. Inputs (baseline / mutant): empty_k0: 0.0 / 0.0; empty_k3: 0.0 / 0.0; k0: 0.0 / 2.9654859789671595; k2: 4.9654872077726875 / 4.9654872077726875; kneg: 0.0 / 2.9654859789671595.

Candidate (low, class_guess I1): _smooth_topk_sum's k <= 0 guard is unpinned: with it off k = 0 returns the smooth top-1 (2.97) instead of 0.0, and the full gate stays green. k0: baseline 0.0, mutant 2.9654859789671595; null cases moved 0.

### 2d64a114647f1551 — tariff.py:747 CMP_BOUND — RED-AS-NULL — candidate

`if not np.any(x > 0): -> if not np.any(x >= 0):` in `_smooth_topk_sum`. Gate: gate_rc 1, killed_by [], wall 2660.0 s, load1 0.82 -> 0.93.

Step 4: should have failed tests/features.py, tests/stress.py (their traced baseline executes the line): no check calls _smooth_topk_sum on a non-positive series containing 0.0 and asserts exactly 0.0.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_2d64a114647f1551.py`: cases moved 3, null cases moved 0. Inputs (baseline / mutant): all_zero: 0.0 / 0.0; positive: 1.9933063882612345 / 1.9933063882612345; zero_and_neg_k2: 0.0 / -6.665187755269336e-13; zero_and_negative: 0.0 / -2.6269532288089563e-26; zero_and_tiny_neg: 0.0 / -4.875026045493982e-11.

Candidate (low, class_guess I1): _smooth_topk_sum's np.any(x > 0) guard is unpinned at zero: a series of zeros and negatives returns a small negative sum (-4.9e-11) instead of 0.0, and the full gate stays green. zero_and_tiny_neg: baseline 0.0, mutant -4.875026045493982e-11; null cases moved 0.

### 5371ee2b5e897750 — tariff.py:747 GUARD_OFF — RED-AS-NULL — candidate

`if not np.any(x > 0): -> if False:` in `_smooth_topk_sum`. Gate: gate_rc 1, killed_by [], wall 2787.0 s, load1 0.87 -> 0.93.

Step 4: should have failed tests/features.py, tests/stress.py (their traced baseline executes the line): no check calls _smooth_topk_sum on an all-negative or nan-only series and asserts 0.0.

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/probes/probe_5371ee2b5e897750.py`: cases moved 2, null cases moved 0. Inputs (baseline / mutant): all_negative: 0.0 / -1.0; all_zero: 0.0 / 0.0; nan_only: 0.0 / nan; positive: 1.9933063882612345 / 1.9933063882612345.

Candidate (low, class_guess I1): _smooth_topk_sum's no-positive-entry guard is unpinned: with it off an all-negative series returns -1.0 and a nan-only series nan instead of 0.0, and the full gate stays green. all_negative: baseline 0.0, mutant -1.0; null cases moved 0.

