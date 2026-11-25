# D3-s1 wave box D3-g40: full gate for 15 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, step D3.M3/D3.M4, box D3-g40. Findings: none numbered here; candidates go under `gate_survivors` for the orchestrator's consolidation.

## Machine and controls

```
date: 2026-11-25T00:53:31Z
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         768       14077          12        1512       15319
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 1.20
python3: /opt/hpo/python/cpython-3.14.7-linux-x86_64-gnu/bin/python3.14 ($HOME/venv-ci is a symlink to /opt/hpo/venv-ci, created by this box)
```

Null control: `fullgate.py null` (comment-only marker), gate_rc 1, red only on `python3 tests/closure.py selftest`, `python3 tests/entities.py`, `python3 tests/harness_headers.py` (stripped-tree artefacts: closure shrink pins, one entity check, round4/D6 claims.py header drift) -- the profile of D3-rem's accepted null; wall 3969.4 s, load1 0.93..1.0. Not re-taken. Wall, CPU and load numbers are provisional (nproc 4, Intel Xeon @ 2.10GHz); counts are final.

Procedure: gate_wave.sh `null` then `run`: for each key, `fullgate.py run --src complete --key <key>` applies the one-line mutant, commits, runs `GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh`, records, resets to the baseline; one gate at a time, 4 h cap.

Driver note: 2026-11-25T15:54:46Z driver restarted (session restart moved the git proxy port; old driver's pushes failed and left the comms lock held); gate 13 1894e6dcd2251a30 attempt 1 interrupted at ~10 min by SIGINT, tree reset, re-run from start The interrupted attempt left no record; the key's only gate record is the complete re-run.

## Tally

Gated 15 of 15: KILLED 1, RED-AS-NULL 14; KILLED by `python3 tests/structure.py` (1). TIMEOUT 0. Candidates 4, equivalent-candidates 10, killed 1.

| key | site | patch | verdict | class | probe metric baseline -> mutant |
|---|---|---|---|---|---|
| 5f094dbca9a593e9 | custom_components/heatpump_optimizer/tariff.py:750 CLAMP_DROP | `scale = max(tau * peak, 1e-9) -> scale = (tau * peak)` | RED-AS-NULL | candidate | max_delta_reachable_caller 0.0 -> 5.6932e-10 kW |
| 7b4d6225353952ed | custom_components/heatpump_optimizer/tariff.py:763 CLAMP_DROP | `z = np.clip((x - mid) / scale, -60.0, 60.0) -> z = ((x - mid) / scale)` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| e6bcd13be86202b8 | custom_components/heatpump_optimizer/tariff.py:766 CMP_BOUND | `if abs(count - k) < 1e-6: -> if abs(count - k) <= 1e-6:` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| e01cc20e67f1f720 | custom_components/heatpump_optimizer/tariff.py:768 CMP_BOUND | `if count > k: -> if count >= k:` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| f8eec0888776e8ff | custom_components/heatpump_optimizer/tariff.py:773 CLAMP_DROP | `z = np.clip((x - mid) / scale, -60.0, 60.0) -> z = ((x - mid) / scale)` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| 968c552b8acd9df9 | custom_components/heatpump_optimizer/tariff.py:801 CMP_BOUND | `positive = np.flatnonzero(np.any(values > 0, axis=1)) -> positive = np.flatnonzero(np.any(values >= 0, axis=1))` | KILLED | killed | differing_all_direct 0 -> 20 count |
| 996dce5148e02763 | custom_components/heatpump_optimizer/tariff.py:806 CLAMP_DROP | `scale = np.maximum(tau * peak, 1e-9) -> scale = (tau * peak)` | RED-AS-NULL | candidate | max_delta_reachable_caller 0.0 -> 5.6932e-10 kW |
| 754e4cb5fa60e129 | custom_components/heatpump_optimizer/tariff.py:821 CLAMP_DROP | `z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0) -> z = ((x - mid[:, None]) / scale[:, None])` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| a074fb25836c2bc6 | custom_components/heatpump_optimizer/tariff.py:824 CMP_BOUND | `close = np.abs(count - k) < 1e-6 -> close = np.abs(count - k) <= 1e-6` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| 22dd975583db1b89 | custom_components/heatpump_optimizer/tariff.py:828 CMP_BOUND | `over = count > k -> over = count >= k` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| 134d9411b323ef8a | custom_components/heatpump_optimizer/tariff.py:832 CLAMP_DROP | `z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0) -> z = ((x - mid[:, None]) / scale[:, None])` | RED-AS-NULL | equivalent-candidate | differing_all_direct 0 -> 0 count |
| 3e9a439baa86a074 | custom_components/heatpump_optimizer/tariff.py:528 CMP_BOUND | `if not math.isfinite(value) or value < 0.0: -> if not math.isfinite(value) or value <= 0.0:` | RED-AS-NULL | candidate | billed_peak_kw 1.333333 -> 4.0 kW |
| 1894e6dcd2251a30 | custom_components/heatpump_optimizer/tariff.py:570 GUARD_OFF | `if house.size == 0: -> if False:` | RED-AS-NULL | candidate | n_peak_windows_differing 0 -> 10 count |
| 0e94685aa803560d | custom_components/heatpump_optimizer/tariff.py:573 CMP_BOUND | `if per_window <= 1: -> if per_window < 1:` | RED-AS-NULL | equivalent-candidate | differing_value_or_length 0 -> 0 count |
| 64a2ed644109fda3 | custom_components/heatpump_optimizer/tariff.py:573 GUARD_OFF | `if per_window <= 1: -> if False:` | RED-AS-NULL | equivalent-candidate | differing_value_or_length 0 -> 0 count |

## Survivors: step-4 answers

**5f094dbca9a593e9** `custom_components/heatpump_optimizer/tariff.py:750 CLAMP_DROP` `scale = max(tau * peak, 1e-9) -> scale = (tau * peak)` (_smooth_topk_sum) -- gate RED-AS-NULL, class **candidate**. Under the mutant at tariff.py:750 the scalar smooth top-k (through its only caller _plateau_aware_topk_sum) returns a different value on 45 of 60 tiny-peak plateau excess vectors (peak < 2e-8 kW), max |delta| 5.7e-10 kW, and raises 906 RuntimeWarnings; plateaus at ordinary magnitudes are bit-identical. The full gate stays green: no check feeds a plateau below tau*peak = 1e-9. Severity claimed low, class_guess I1. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_5f094dbca9a593e9.py`: differing 0 -> 45 of 60 tiny inputs; max delta 5.69e-10 kW; RuntimeWarnings 0 -> 906. Inputs tried: 2322 inputs: plateau 600, tieband 300, uniform 300, spread 30, tiny 60 (peaks 1e-7..5e-324), zero 24, negative 8, exacttie 1000. Should have failed: tests/features.py (the carried M4's line-executing scripts) -- lacking: a _smooth_topk_sum / _plateau_aware_topk_sum unit on a tied plateau with peak below 2e-8 kW asserting the k*tie_level value and no RuntimeWarning.

**7b4d6225353952ed** `custom_components/heatpump_optimizer/tariff.py:763 CLAMP_DROP` `z = np.clip((x - mid) / scale, -60.0, 60.0) -> z = ((x - mid) / scale)` (_smooth_topk_sum) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_7b4d6225353952ed.py`: 0 values differ; RuntimeWarnings 0 -> 2620 (exp overflow inside the bisection when the bracket is far from the plateau). Inputs tried: same 2322-input corpus (scalar mode). Should have failed: tests/features.py (the carried M4's line-executing scripts) -- lacking: only a warnings-as-errors run of a tiny-peak plateau would fail; no value-level assertion can.

**e6bcd13be86202b8** `custom_components/heatpump_optimizer/tariff.py:766 CMP_BOUND` `if abs(count - k) < 1e-6: -> if abs(count - k) <= 1e-6:` (_smooth_topk_sum) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_e6bcd13be86202b8.py`: 0 differ, 0 warnings; no input hit |count - k| == 1e-6 exactly. Inputs tried: same corpus incl. exacttie family: 1000 one-lower-window plateaus n=2..6 at 200 offsets. Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: none at value level: the two arms differ only on a float-exact 1e-6 residual.

**e01cc20e67f1f720** `custom_components/heatpump_optimizer/tariff.py:768 CMP_BOUND` `if count > k: -> if count >= k:` (_smooth_topk_sum) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_e01cc20e67f1f720.py`: 0 differ; count == k exactly already breaks at line 766 (|0| < 1e-6), and nan compares False under both > and >=: unreachable difference. Inputs tried: same corpus. Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: none: provably equivalent.

**f8eec0888776e8ff** `custom_components/heatpump_optimizer/tariff.py:773 CLAMP_DROP` `z = np.clip((x - mid) / scale, -60.0, 60.0) -> z = ((x - mid) / scale)` (_smooth_topk_sum) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_f8eec0888776e8ff.py`: 0 differ, 0 warnings: after the bisection mid <= peak + 5.25*scale and excess >= 0, so the final |z| <= ~26 < 60 and the clip never binds. Inputs tried: same corpus incl. spread up to 1e9 and tiny to 5e-324. Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: none for non-negative excess (the only caller's domain).

**968c552b8acd9df9** `custom_components/heatpump_optimizer/tariff.py:801 CMP_BOUND` `positive = np.flatnonzero(np.any(values > 0, axis=1)) -> positive = np.flatnonzero(np.any(values >= 0, axis=1))` (_smooth_topk_sum_batch) -- gate KILLED, class **killed**. Killed by python3 tests/structure.py; failing lines: `########## ratchet vs structure_budgets.json (recorded_at a39627da59ac) ##########`; `gain duplication_copies 7 (budget 8, -1; not yet recorded -- see below)`; `metric                                 budget     measured      delta`; `a budget and a better tree the gate is not loose, it is ABSENT, and`. killed by tests/structure.py's ratchet alone: duplication_copies measured 7 against budget 8 (a gain the ratchet refuses), i.e. the mutated text breaks one duplicated block -- a structural count, not a behavioural assertion. The probe's reading stands beside it: 0 caller-reachable values move; 20 direct-call inputs (rows with max 0 and negative entries) do. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_968c552b8acd9df9.py`: direct differing 0 -> 20; [0,-1,-2,-3] k=4: 0.0 -> -6.0; caller-reachable differing 0. Inputs tried: same corpus (batch mode, single rows and 3x3 stacked matrices). Should have failed: tests/env_drift.py, tests/features.py (the carried M4's line-executing scripts) -- lacking: a batch-vs-scalar parity unit over rows whose max is <= 0 (the docstring's 'Rows with nothing positive return 0.0, as the scalar guard does').

**996dce5148e02763** `custom_components/heatpump_optimizer/tariff.py:806 CLAMP_DROP` `scale = np.maximum(tau * peak, 1e-9) -> scale = (tau * peak)` (_smooth_topk_sum_batch) -- gate RED-AS-NULL, class **candidate**. Under the mutant at tariff.py:806 the batch smooth top-k (through _plateau_aware_topk_sum_batch) differs on 67 caller-reachable rows (45 tiny single rows, 22 stacked), max |delta| 5.7e-10 kW, with 1356 RuntimeWarnings; ordinary plateaus are bit-identical. The scalar twin keeps its floor, so the batch/scalar bit-parity the docstring promises breaks on these rows. Severity claimed low, class_guess I1. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_996dce5148e02763.py`: reachable differing 0 -> 67; max delta 5.69e-10 kW; RuntimeWarnings 0 -> 1356. Inputs tried: same corpus (batch mode). Should have failed: tests/env_drift.py, tests/features.py (the carried M4's line-executing scripts) -- lacking: a batch-vs-scalar bit-parity unit on a tied plateau row with peak below 2e-8 kW.

**754e4cb5fa60e129** `custom_components/heatpump_optimizer/tariff.py:821 CLAMP_DROP` `z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0) -> z = ((x - mid[:, None]) / scale[:, None])` (_smooth_topk_sum_batch) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_754e4cb5fa60e129.py`: 0 values differ; RuntimeWarnings 0 -> 2708 (exp overflow in the bisection loop). Inputs tried: same corpus (batch mode). Should have failed: tests/features.py (the carried M4's line-executing scripts) -- lacking: only a warnings-as-errors run; no value-level assertion.

**a074fb25836c2bc6** `custom_components/heatpump_optimizer/tariff.py:824 CMP_BOUND` `close = np.abs(count - k) < 1e-6 -> close = np.abs(count - k) <= 1e-6` (_smooth_topk_sum_batch) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_a074fb25836c2bc6.py`: 0 differ, 0 warnings; no row hit |count - k| == 1e-6 exactly. Inputs tried: same corpus (batch mode) incl. exacttie 1000. Should have failed: tests/env_drift.py, tests/features.py (the carried M4's line-executing scripts) -- lacking: none at value level.

**22dd975583db1b89** `custom_components/heatpump_optimizer/tariff.py:828 CMP_BOUND` `over = count > k -> over = count >= k` (_smooth_topk_sum_batch) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_22dd975583db1b89.py`: 0 differ: count == k exactly is already `close` at line 824, and a done row's lo/hi/mid are frozen by np.where; provably equivalent. (The carried M4 states the patch as `>=` -> `>`; the mutant record and this probe use `>` -> `>=`.). Inputs tried: same corpus (batch mode). Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: none: provably equivalent.

**134d9411b323ef8a** `custom_components/heatpump_optimizer/tariff.py:832 CLAMP_DROP` `z = np.clip((x - mid[:, None]) / scale[:, None], -60.0, 60.0) -> z = ((x - mid[:, None]) / scale[:, None])` (_smooth_topk_sum_batch) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_134d9411b323ef8a.py`: 0 differ, 0 warnings: final |z| <= ~26 for non-negative rows. Inputs tried: same corpus (batch mode). Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: none for non-negative excess.

**3e9a439baa86a074** `custom_components/heatpump_optimizer/tariff.py:528 CMP_BOUND` `if not math.isfinite(value) or value < 0.0: -> if not math.isfinite(value) or value <= 0.0:` (_stored_peaks) -- gate RED-AS-NULL, class **candidate**. Under the mutant at tariff.py:528 a PeakTracker reloaded from its own as_dict loses each peak stored as 0.0 (any peak under 0.0005 kW rounds there), so billed_peak_kw rises 1.333 -> 4.0 kW and threshold_kw 0.0 -> 4.0 kW for peaks [4.0, 0.0004, 0.0003]; the full gate stays green, so no test pins the zero-peak round trip. Severity claimed medium, class_guess I1. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_3e9a439baa86a074.py`: billed_peak_kw 1.333333 -> 4.0 kW; threshold_kw 0.0 -> 4.0 kW; peaks reloaded 3 -> 1; closed-month billed 1.333 -> 4.0 kW; null delta 0. Inputs tried: PeakTracker peaks [4.0, 0.0004, 0.0003] (as_dict rounds to [4.0, 0.0, 0.0]), peaks_averaged 3, one as_dict->from_dict restart; null [4,3,2]. Should have failed: tests/features.py, tests/finite_boundary.py (the carried M4's line-executing scripts) -- lacking: a PeakTracker.from_dict(t.as_dict()) round-trip assertion with a 0.0 (or sub-0.0005 kW) peak: len(peaks) and billed_peak_kw/threshold_kw preserved.

**1894e6dcd2251a30** `custom_components/heatpump_optimizer/tariff.py:570 GUARD_OFF` `if house.size == 0: -> if False:` (metering_windows) -- gate RED-AS-NULL, class **candidate**. Under the mutant at tariff.py:570 metering_windows on a zero-length series with more than one step per window returns [nan] (with RuntimeWarnings) instead of an empty array, so Optimizer._n_peak_windows' expression counts 1 window for a 0-step plan instead of 0 (10 of 315 inputs: every length-0 input with per_window > 1). _peak_charge and the tariff.py:1227 helper guard size 0 before calling and topology._window_peak guards an empty series, so the reachable consequence is the window count fed to window_factors/peak-day sizing for an empty plan. Severity claimed low, class_guess I1. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_1894e6dcd2251a30.py`: length 0 -> 1 ([nan]); n_peak_windows 0 -> 1 on 10/315; RuntimeWarnings 0 -> 40. Inputs tried: 315: lengths 0,1,2,3,4,5,7,12,96 x (15,.25) (60,.25) (60,1) (30,.5) (60,.5) (15,1) (5,.25) x offsets 0,1,2,3,5. Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: a metering_windows(np.zeros(0), 60, 0.25) unit asserting size 0 (and _n_peak_windows(0, ...) == 0).

**0e94685aa803560d** `custom_components/heatpump_optimizer/tariff.py:573 CMP_BOUND` `if per_window <= 1: -> if per_window < 1:` (metering_windows) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_0e94685aa803560d.py`: 0 values or lengths differ; at per_window == 1 the partition is the identity (head empty, reshape(n,1).mean). Only the result's identity differs (a copy instead of the input array, 200 inputs), which no caller observes: every caller passes a fresh array and none writes into the result. Inputs tried: same 315-input corpus. Should have failed: not named by the carried M4 answer (the carried M4's line-executing scripts) -- lacking: none at value level.

**64a2ed644109fda3** `custom_components/heatpump_optimizer/tariff.py:573 GUARD_OFF` `if per_window <= 1: -> if False:` (metering_windows) -- gate RED-AS-NULL, class **equivalent-candidate**. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_64a2ed644109fda3.py`: 0 values or lengths differ; per_window = max(1, ...) so the disabled branch is the per_window == 1 identity again; only result aliasing differs (200 inputs). Inputs tried: same 315-input corpus. Should have failed: tests/block_duty.py, tests/boost_drift_replay.py, tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/manual_plan.py, tests/optimality.py, tests/plan_view.py, tests/validate.py (the carried M4's line-executing scripts) -- lacking: none at value level.

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `gate_wave.sh (out-of-tree driver on dispatch/finder-r11-D3-g40: null, then run over keys.tsv one gate at a time, cap 14400 s, checkpoint per gate)`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/build_record.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/build_report.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_lib.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/topk_search.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/metering_search.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_5f094dbca9a593e9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_7b4d6225353952ed.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_e6bcd13be86202b8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_e01cc20e67f1f720.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_f8eec0888776e8ff.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_968c552b8acd9df9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_996dce5148e02763.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_754e4cb5fa60e129.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_a074fb25836c2bc6.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_22dd975583db1b89.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_134d9411b323ef8a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_3e9a439baa86a074.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_1894e6dcd2251a30.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_0e94685aa803560d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_64a2ed644109fda3.py`
