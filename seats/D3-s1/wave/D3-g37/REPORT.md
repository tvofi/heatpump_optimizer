# D3-s1, box D3-g37: full gate for 16 D3.M3 full-net survivors (sysid.py)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine (provisional): nproc: 4 total used free shared buff/cache available Mem: 16087 749 14098 12 1510 15338 Swap: 0 0 0 model name : Intel(R) Xeon(R) Processor @ 2.10GHz Filesystem Size Used Avail Use% Mounted on /dev/vda 252G 12G 58G 17% / load1: 0.82 Wed Nov 25 00:53:20 UTC 2026

## Controls

Null control (`fullgate.py null`, comment-only marker): gate_rc=1, failed ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] with fail_lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 4025.7 s, load1 0.59..0.92. Red on artefact checks only: see gates/null-note.txt (includes this box's own probes/_mut.py helper-copy line, fixed after the null; later gates read at most 3 there).

## Box events

Box events: at ~13:48 UTC the session's container was restarted while key 845bf7a69b48b94b's first gate had just started (13:55); the long-running comms loop and gate driver kept the old proxy address, so their pushes failed and a failed push left box_comms.sh's mkdir lock behind. The comms loop was restarted under the current environment, the stale lock (this box's own) removed, and the gate driver stopped by PID (parents first, then SIGINT to fullgate.py, whose finally reset the tree to the baseline) 5 minutes into that gate, which wrote no record; gate_wave.sh run was restarted and re-gated 845bf7a69b48b94b from the start (14:00-15:09 UTC). No gate record was lost or overwritten; every key's gate is a single complete run. After all 16 gates, all 16 probes were re-run on the quiet box with the final helper code; every number matched the first run (outputs in probes/out/).

## Tally

- gated: 16 of 16; TIMEOUT: 0; not gated: 0
- verdicts: RED-AS-NULL 16
- KILLED by script: none
- classes: candidate 2, equivalent-candidate 14

| key | site | patch | verdict | wall s | load1 | class |
|---|---|---|---|---|---|---|
| ba25d4dc58c7fecc | custom_components/heatpump_optimizer/sysid.py:846 CMP_BOUND | `if np.isfinite(next_cost) and next_cost < cost: -> if np.isfinite(next_cost) and next_cost <= cost:` | RED-AS-NULL | 3274.8 | 0.72..1.05 | equivalent-candidate |
| 67f17d97399379c0 | custom_components/heatpump_optimizer/sysid.py:848 CLAMP_DROP | `damping = max(damping * 0.3, 1e-12) -> damping = (damping * 0.3)` | RED-AS-NULL | 3254.5 | 0.9..1.0 | equivalent-candidate |
| 99866c2ffc704413 | custom_components/heatpump_optimizer/sysid.py:852 CMP_BOUND | `if not accepted or float(np.max(np.abs(delta))) < 1e-10: -> if not accepted or float(np.max(np.abs(delta))) <= 1e-10:` | RED-AS-NULL | 3234.5 | 0.99..0.92 | equivalent-candidate |
| b4f7503c6959449d | custom_components/heatpump_optimizer/sysid.py:1073 CMP_BOUND | `if solution.shape[0] >= 4: -> if solution.shape[0] > 4:` | RED-AS-NULL | 3362.7 | 0.78..0.92 | candidate |
| f6016f6adb9683a8 | custom_components/heatpump_optimizer/sysid.py:1073 GUARD_OFF | `if solution.shape[0] >= 4: -> if False:` | RED-AS-NULL | 3636.9 | 0.78..0.92 | candidate |
| 0c0a6bcb94a3ba3a | custom_components/heatpump_optimizer/sysid.py:129 CMP_BOUND | `if ua <= 1e-9 or capacity <= 1e-9: -> if ua < 1e-9 or capacity <= 1e-9:` | RED-AS-NULL | 3561.5 | 0.79..0.92 | equivalent-candidate |
| 2b5a8949055ecd4c | custom_components/heatpump_optimizer/sysid.py:129 CMP_BOUND | `if ua <= 1e-9 or capacity <= 1e-9: -> if ua <= 1e-9 or capacity < 1e-9:` | RED-AS-NULL | 3562.8 | 0.94..1.0 | equivalent-candidate |
| e3ea72b8dc57884a | custom_components/heatpump_optimizer/sysid.py:139 CLAMP_DROP | `peak = max(abs(after_step - baseline), abs(after_relax - baseline)) -> peak = (abs(after_step - baseline))` | RED-AS-NULL | 3874.8 | 0.85..0.92 | equivalent-candidate |
| 6db5003950426ce8 | custom_components/heatpump_optimizer/sysid.py:328 CMP_BOUND | `while remaining > 1e-12: -> while remaining >= 1e-12:` | RED-AS-NULL | 3695.7 | 0.78..1.0 | equivalent-candidate |
| 1e9d97a860146a80 | custom_components/heatpump_optimizer/sysid.py:890 CMP_BOUND | `if ua <= 1e-6 or room_cap <= 1e-6: -> if ua <= 1e-6 or room_cap < 1e-6:` | RED-AS-NULL | 3742.4 | 0.92..0.94 | equivalent-candidate |
| 51b2c8ce3dadae0c | custom_components/heatpump_optimizer/sysid.py:890 CMP_BOUND | `if ua <= 1e-6 or room_cap <= 1e-6: -> if ua < 1e-6 or room_cap <= 1e-6:` | RED-AS-NULL | 3711.3 | 0.73..0.92 | equivalent-candidate |
| 62a1f4d0c1be5960 | custom_components/heatpump_optimizer/sysid.py:892 CMP_BOUND | `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 < gains_kw <= 2.0):` | RED-AS-NULL | 3794.7 | 0.78..0.92 | equivalent-candidate |
| 845bf7a69b48b94b | custom_components/heatpump_optimizer/sysid.py:892 CMP_BOUND | `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 <= gains_kw < 2.0):` | RED-AS-NULL | 4123.9 | 0.86..0.92 | equivalent-candidate |
| ab65584805229d1c | custom_components/heatpump_optimizer/sysid.py:892 GUARD_OFF | `if not (-0.5 <= gains_kw <= 2.0): -> if False:` | RED-AS-NULL | 3753.2 | 0.86..1.08 | equivalent-candidate |
| 186b3076dcce442c | custom_components/heatpump_optimizer/sysid.py:897 CMP_BOUND | `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau <= 200.0) or not (0.01 <= ua < 5.0):` | RED-AS-NULL | 3599.7 | 0.99..1.0 | equivalent-candidate |
| 66e79426a66d3362 | custom_components/heatpump_optimizer/sysid.py:897 CMP_BOUND | `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):` | RED-AS-NULL | 3464.0 | 0.85..0.92 | equivalent-candidate |

## Survivors: the step-4 answer and the probe numbers

### ba25d4dc58c7fecc custom_components/heatpump_optimizer/sysid.py:846 CMP_BOUND (_lm_solve) -- equivalent-candidate

Patch `if np.isfinite(next_cost) and next_cost < cost: -> if np.isfinite(next_cost) and next_cost <= cost:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_ba25d4dc58c7fecc.py`.

_lm_solve accepts an equal-cost step. Unit: moves on a plateau residual (x 1.0 -> 0.99999901) and at a clip bound (x[1] 1.33e-8 -> 0.0), 51 of 200 random problems. Production: 22 of 168 runs publish a different SysIdResult, all at float-noise level: the largest relative change of any published float is 4.0e-6 (ua_told_halfwidth 0.0013256945 -> 0.0013256998), heat_loss_kw_per_c agrees to 1e-15, 6 adoption decisions differ only in weight (<= 4.6e-9 absolute) or scale (1 ulp), admitted 10 vs 10. Equivalent at every decision the integration publishes; the residual movement is below what a check can pin portably (solver floats do not reproduce across BLAS builds).

Should have failed: tests/features.py (the two-state ridge drives, _ridge_drive ~54300) executes line 846 but pins no solver output to 1e-6 relative; a check that would kill this must pin float noise, so none should.

Numbers: unit_plateau_baseline=(array([1.]), 1.0); unit_plateau_mutant=(array([0.99999901]), 1.0); unit_plateau_moved=1 count; unit_rosenbrock_baseline=(array([1., 1.]), 1.836566794967668e-30); unit_rosenbrock_mutant=(array([1., 1.]), 1.836566794967668e-30); unit_rosenbrock_moved=0 count; unit_bound_baseline=(array([1.00000000e+01, 1.33143747e-08]), 100.0); unit_bound_mutant=(array([10.,  0.]), 100.0); unit_bound_moved=1 count; unit_rankdef_baseline=(array([0.6, 0.4]), 0.0); unit_rankdef_mutant=(array([0.6, 0.4]), 0.0); unit_rankdef_moved=0 count; unit_random_moved=51 count (over 200 random nonlinear least-squares problems); unit_moved=2 count; null_linear_baseline=(array([ 3., -1.]), 4.388038785291878e-30); null_linear_mutant=(array([ 3., -1.]), 4.388038785291878e-30); null_linear_moved=0 count; null_moved=0 count; reach_runs=168 count; reach_calls=714 count; reach_calls_separating=185 count; reach_outcomes_differ=22 count; adoption_admitted_baseline=10 count; adoption_admitted_mutant=10 count; adoption_decisions_differ=6 count; max_rel_field_deviation=4.009e-06 (heavy_old,decl=True,truth={'house_heat_loss_scale': 3.0},noise=0.02,seed=0,cad=0.5:ua_told_halfwidth 0.0013256944583941584->0.0013256997732507124)

### 67f17d97399379c0 custom_components/heatpump_optimizer/sysid.py:848 CLAMP_DROP (_lm_solve) -- equivalent-candidate

Patch `damping = max(damping * 0.3, 1e-12) -> damping = (damping * 0.3)`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_67f17d97399379c0.py`.

Dropping the 1e-12 damping floor. Unit: 16 of 200 random nonlinear problems end at a different x; the plateau, Rosenbrock, bound, rank-deficient and linear inputs do not move. Production: 1 of 714 _lm_solve calls returns a different x, and 0 of 168 runs publish a different outcome (every SysIdResult field, the override sequence, every sysid log line).

Should have failed: none at the published outcome; tests/features.py and tests/entities.py execute line 848 (M4 carried) but nothing published moves over the 168-run sweep.

Numbers: unit_plateau_baseline=(array([1.]), 1.0); unit_plateau_mutant=(array([1.]), 1.0); unit_plateau_moved=0 count; unit_rosenbrock_baseline=(array([1., 1.]), 1.836566794967668e-30); unit_rosenbrock_mutant=(array([1., 1.]), 1.836566794967668e-30); unit_rosenbrock_moved=0 count; unit_bound_baseline=(array([1.00000000e+01, 1.33143747e-08]), 100.0); unit_bound_mutant=(array([1.00000000e+01, 1.33143747e-08]), 100.0); unit_bound_moved=0 count; unit_rankdef_baseline=(array([0.6, 0.4]), 0.0); unit_rankdef_mutant=(array([0.6, 0.4]), 0.0); unit_rankdef_moved=0 count; unit_random_moved=16 count (over 200 random nonlinear least-squares problems); unit_moved=0 count; null_linear_baseline=(array([ 3., -1.]), 4.388038785291878e-30); null_linear_mutant=(array([ 3., -1.]), 4.388038785291878e-30); null_linear_moved=0 count; null_moved=0 count; reach_runs=168 count; reach_calls=714 count; reach_calls_separating=1 count; reach_outcomes_differ=0 count

### 99866c2ffc704413 custom_components/heatpump_optimizer/sysid.py:852 CMP_BOUND (_lm_solve) -- equivalent-candidate

Patch `if not accepted or float(np.max(np.abs(delta))) < 1e-10: -> if not accepted or float(np.max(np.abs(delta))) <= 1e-10:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_99866c2ffc704413.py`.

Stopping when max|delta| equals 1e-10 exactly. Unit: 0 of 200 random problems and 0 of the 5 shaped inputs move; production: 0 of 714 calls separate, 0 of 168 outcomes differ. An exact 1e-10 step is never produced.

Should have failed: none: no input found that makes max|delta| exactly 1e-10.

Numbers: unit_plateau_baseline=(array([1.]), 1.0); unit_plateau_mutant=(array([1.]), 1.0); unit_plateau_moved=0 count; unit_rosenbrock_baseline=(array([1., 1.]), 1.836566794967668e-30); unit_rosenbrock_mutant=(array([1., 1.]), 1.836566794967668e-30); unit_rosenbrock_moved=0 count; unit_bound_baseline=(array([1.00000000e+01, 1.33143747e-08]), 100.0); unit_bound_mutant=(array([1.00000000e+01, 1.33143747e-08]), 100.0); unit_bound_moved=0 count; unit_rankdef_baseline=(array([0.6, 0.4]), 0.0); unit_rankdef_mutant=(array([0.6, 0.4]), 0.0); unit_rankdef_moved=0 count; unit_random_moved=0 count (over 200 random nonlinear least-squares problems); unit_moved=0 count; null_linear_baseline=(array([ 3., -1.]), 4.388038785291878e-30); null_linear_mutant=(array([ 3., -1.]), 4.388038785291878e-30); null_linear_moved=0 count; null_moved=0 count; reach_runs=168 count; reach_calls=714 count; reach_calls_separating=0 count; reach_outcomes_differ=0 count

### b4f7503c6959449d custom_components/heatpump_optimizer/sysid.py:1073 CMP_BOUND (_one_state_ua_halfwidth) -- candidate

Patch `if solution.shape[0] >= 4: -> if solution.shape[0] > 4:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_b4f7503c6959449d.py`.

**Candidate: No check reads the one-state fit's UA interval: dropping its main-path covariance branch is unseen.** The one-state fit's published UA 95 % half-width (SysIdResult.ua_profile_halfwidth, the adoption gate's input) is computed by sysid.py:_one_state_ua_halfwidth, whose main-path branch (line 1073, a four-column solution with the drift column) no check pins: replacing it by the two-column fallback covariance (`if solution.shape[0] >= 4:` -> `if solution.shape[0] > 4:`) passes the full GATE_SCOPE=full GOLDEN_MODE=drift gate while the published half-width shrinks by 36-79 % on every completed one-state fit and adoption_decision flips a refused fit (+-50 % interval) to adopted.

Severity claimed medium: a mutant that narrows the interval adopts a fit the +-10 % bar exists to refuse (wrong heat-loss scale learned, wrong comfort/money downstream); the defect is the missing check, with a workaround (the bar still refuses most fits).

Should have failed: tests/features.py: the one-state drives (_drift_drive, tests/features.py:54735, which executes sysid.py:1073 through SystemIdentification.identify) read only completed/confidence/heat_loss_kw_per_c; no check reads a one-state result's ua_profile_halfwidth or its adoption_decision. The assertion it lacks: a completed one-state fit's ua_profile_halfwidth equals the delta-method width from the full normal-equation inverse (seed 1000: 0.3196), or adoption_decision refuses a fit whose interval is wider than the +-10 % bar.

Numbers: unit_solution_size=4 count; unit_halfwidth_seed1000_baseline=0.31963411254337787; unit_halfwidth_seed1000_mutant=0.14199610074430277; unit_halfwidth_seed1000_moved=1 count; null_fallback_size2_baseline=0.14199610074430277; null_fallback_size2_mutant=0.14199610074430277; null_fallback_size2_moved=0 count; unit_moved=1 count; null_moved=0 count; reach_runs=168 count; reach_calls=61 count; reach_calls_separating=61 count; reach_outcomes_differ=8 count; adoption_admitted_baseline=10 count; adoption_admitted_mutant=11 count; adoption_decisions_differ=8 count

### f6016f6adb9683a8 custom_components/heatpump_optimizer/sysid.py:1073 GUARD_OFF (_one_state_ua_halfwidth) -- candidate

Patch `if solution.shape[0] >= 4: -> if False:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_f6016f6adb9683a8.py`.

**Candidate: No check reads the one-state fit's UA interval: dropping its main-path covariance branch is unseen.** The one-state fit's published UA 95 % half-width (SysIdResult.ua_profile_halfwidth, the adoption gate's input) is computed by sysid.py:_one_state_ua_halfwidth, whose main-path branch (line 1073, a four-column solution with the drift column) no check pins: replacing it by the two-column fallback covariance (`if solution.shape[0] >= 4:` -> `if False:`) passes the full GATE_SCOPE=full GOLDEN_MODE=drift gate while the published half-width shrinks by 36-79 % on every completed one-state fit and adoption_decision flips a refused fit (+-50 % interval) to adopted.

Severity claimed medium: a mutant that narrows the interval adopts a fit the +-10 % bar exists to refuse (wrong heat-loss scale learned, wrong comfort/money downstream); the defect is the missing check, with a workaround (the bar still refuses most fits).

Should have failed: same as b4f7503c6959449d: tests/features.py _drift_drive (54735) reaches line 1073 but no check reads the one-state ua_profile_halfwidth or adoption_decision on it.

Numbers: unit_solution_size=4 count; unit_halfwidth_seed1000_baseline=0.31963411254337787; unit_halfwidth_seed1000_mutant=0.14199610074430277; unit_halfwidth_seed1000_moved=1 count; null_fallback_size2_baseline=0.14199610074430277; null_fallback_size2_mutant=0.14199610074430277; null_fallback_size2_moved=0 count; unit_moved=1 count; null_moved=0 count; reach_runs=168 count; reach_calls=61 count; reach_calls_separating=61 count; reach_outcomes_differ=8 count; adoption_admitted_baseline=10 count; adoption_admitted_mutant=11 count; adoption_decisions_differ=8 count

### 0c0a6bcb94a3ba3a custom_components/heatpump_optimizer/sysid.py:129 CMP_BOUND (_predict_step_excursion) -- equivalent-candidate

Patch `if ua <= 1e-9 or capacity <= 1e-9: -> if ua < 1e-9 or capacity <= 1e-9:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_0c0a6bcb94a3ba3a.py`.

Unit: ua exactly 1e-9 returns (0.92, 0.92) instead of (inf, inf); 5e-10 and 2e-9 do not move. Production: the only caller (sysid.py:1627) logs a debug line and is reached only after _predict_step_excursion_plant found a fitting step, which its own guard (sysid.py:315-316, ua <= 1e-9) refuses first; 40 calls over the sweep, 0 separating, 0 outcomes differ.

Should have failed: none through production; tests/features.py:29790/29796/29811/59718 call it directly with ua 0.20.

Numbers: unit_ua_1e-9_baseline=(inf, inf); unit_ua_1e-9_mutant=(0.9199996590614319, 0.9199996590614319); unit_ua_1e-9_moved=1 count; null_ua_5e-10_baseline=(inf, inf); null_ua_5e-10_mutant=(inf, inf); null_ua_5e-10_moved=0 count; null_ua_2e-9_baseline=(0.9200001358985901, 0.9200001358985901); null_ua_2e-9_mutant=(0.9200001358985901, 0.9200001358985901); null_ua_2e-9_moved=0 count; unit_moved=1 count; null_moved=0 count; reach_runs=168 count; reach_calls=40 count; reach_calls_separating=0 count; reach_outcomes_differ=0 count

### 2b5a8949055ecd4c custom_components/heatpump_optimizer/sysid.py:129 CMP_BOUND (_predict_step_excursion) -- equivalent-candidate

Patch `if ua <= 1e-9 or capacity <= 1e-9: -> if ua <= 1e-9 or capacity < 1e-9:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_2b5a8949055ecd4c.py`.

Unit: capacity exactly 1e-9 returns (17.5, 17.5) instead of (inf, inf); 5e-10 and 2e-9 do not move. Production: unreachable as for 0c0a6bcb94a3ba3a (the plant sizer's capacity <= 1e-9 guard at sysid.py:316 refuses first); 40 calls, 0 separating, 0 outcomes differ.

Should have failed: none through production; tests/features.py calls it directly with capacity 8.0/10.0.

Numbers: unit_cap_1e-9_baseline=(inf, inf); unit_cap_1e-9_mutant=(17.5, 17.5); unit_cap_1e-9_moved=1 count; null_cap_5e-10_baseline=(inf, inf); null_cap_5e-10_mutant=(inf, inf); null_cap_5e-10_moved=0 count; null_cap_2e-9_baseline=(17.5, 17.5); null_cap_2e-9_mutant=(17.5, 17.5); null_cap_2e-9_moved=0 count; unit_moved=1 count; null_moved=0 count; reach_runs=168 count; reach_calls=40 count; reach_calls_separating=0 count; reach_outcomes_differ=0 count

### e3ea72b8dc57884a custom_components/heatpump_optimizer/sysid.py:139 CLAMP_DROP (_predict_step_excursion) -- equivalent-candidate

Patch `peak = max(abs(after_step - baseline), abs(after_relax - baseline)) -> peak = (abs(after_step - baseline))`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_e3ea72b8dc57884a.py`.

Unit: where the relax endpoint is farther from the baseline the peak drops (q 3.6 kW: 0.667 -> 0.0196 K; q 0: 1.345 -> 0.686 K); the features.py:29790 input does not move. Production: the function's only consumer is the debug log at sysid.py:1627-1633, called with the sized step, where the step endpoint dominates: 40 calls over the sweep, 0 separating, 0 log lines or outcomes differ.

Should have failed: tests/features.py:29790 (`_peak, _final = _predict_step_excursion(21.0, 2.0, 0.20, 8.0, 0.3, 9.0, 2.0, 2.0)`) executes line 139 on a step-dominated input; the assertion it lacks is a relax-dominated case (e.g. q at hold + 0.1 kW) pinning peak == |after_relax - baseline|; no production behaviour depends on it.

Numbers: unit_relax_dominates_q3p6_baseline=(0.6673482684515015, 0.6673482684515015); unit_relax_dominates_q3p6_mutant=(0.019605280423839133, 0.6673482684515015); unit_relax_dominates_q3p6_moved=1 count; unit_relax_dominates_q0_baseline=(1.3454639382338769, 1.3454639382338769); unit_relax_dominates_q0_mutant=(0.6861848148343448, 1.3454639382338769); unit_relax_dominates_q0_moved=1 count; null_step_dominates_q9_baseline=(1.3411908262303633, 0.42229510654324187); null_step_dominates_q9_mutant=(1.3411908262303633, 0.42229510654324187); null_step_dominates_q9_moved=0 count; unit_moved=2 count; null_moved=0 count; reach_runs=168 count; reach_calls=40 count; reach_calls_separating=0 count; reach_outcomes_differ=0 count

### 6db5003950426ce8 custom_components/heatpump_optimizer/sysid.py:328 CMP_BOUND (_predict_step_excursion_plant) -- equivalent-candidate

Patch `while remaining > 1e-12: -> while remaining >= 1e-12:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_6db5003950426ce8.py`.

Unit: a phase of exactly 1e-12 h takes one extra 1e-12 h substep, moving (peak, final) by ~6e-14 K; the quarter-hour grid and 2e-12 h do not move. Production: phase lengths are configured hours on the dt grid, so remaining reaches 0.0 or a value far from 1e-12: 560 calls over the sweep, 0 separating, 0 outcomes differ.

Should have failed: none: a 6e-14 K difference at an exact 1e-12 h phase is below any meaningful tolerance.

Numbers: unit_step_1e-12_baseline=(0.08246082627876561, 0.08246082627876561); unit_step_1e-12_mutant=(0.08246082627870521, 0.08246082627870521); unit_step_1e-12_moved=1 count; unit_relax_1e-12_baseline=(0.06645262975512267, 0.06645262975512267); unit_relax_1e-12_mutant=(0.06645262975518662, 0.06645262975518662); unit_relax_1e-12_moved=1 count; unit_both_1e-12_baseline=(0.0, 0.0); unit_both_1e-12_mutant=(0.0, 0.0); unit_both_1e-12_moved=0 count; unit_dt_leaves_1e-12_baseline=(0.06610848689436111, 0.06610848689436111); unit_dt_leaves_1e-12_mutant=(0.06610848689436111, 0.06610848689436111); unit_dt_leaves_1e-12_moved=0 count; null_quarter_grid_baseline=(0.10226561017985958, 0.07598617410885922); null_quarter_grid_mutant=(0.10226561017985958, 0.07598617410885922); null_quarter_grid_moved=0 count; null_step_2e-12_baseline=(0.08246082627864126, 0.08246082627864126); null_step_2e-12_mutant=(0.08246082627864126, 0.08246082627864126); null_step_2e-12_moved=0 count; unit_moved=2 count; null_moved=0 count; reach_runs=168 count; reach_calls=560 count; reach_calls_separating=0 count; reach_outcomes_differ=0 count

### 1e9d97a860146a80 custom_components/heatpump_optimizer/sysid.py:890 CMP_BOUND (_slab_refusal) -- equivalent-candidate

Patch `if ua <= 1e-6 or room_cap <= 1e-6: -> if ua <= 1e-6 or room_cap < 1e-6:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_1e9d97a860146a80.py`.

Unit: room_cap exactly 1e-6: refused ('fit gave implausible signs') -> accepted; null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(0.2, 1e-06, 0.3, 10.0); unit0_baseline='fit gave implausible signs'; unit0_mutant='accept'; unit_moved=1 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

### 51b2c8ce3dadae0c custom_components/heatpump_optimizer/sysid.py:890 CMP_BOUND (_slab_refusal) -- equivalent-candidate

Patch `if ua <= 1e-6 or room_cap <= 1e-6: -> if ua < 1e-6 or room_cap <= 1e-6:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_51b2c8ce3dadae0c.py`.

Unit: ua exactly 1e-6: reason 'fit gave implausible signs' -> 'fitted parameters outside plausible bounds' (refused either way); null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(1e-06, 5.0, 0.3, 10.0); unit0_baseline='fit gave implausible signs'; unit0_mutant='fitted parameters outside plausible bounds'; unit1_args=(1e-06, 0.0001, 0.3, 0.0001); unit1_baseline='fit gave implausible signs'; unit1_mutant='fitted parameters outside plausible bounds'; unit_moved=2 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

### 62a1f4d0c1be5960 custom_components/heatpump_optimizer/sysid.py:892 CMP_BOUND (_slab_refusal) -- equivalent-candidate

Patch `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 < gains_kw <= 2.0):`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_62a1f4d0c1be5960.py`.

Unit: gains exactly -0.5: accepted -> refused ('fitted gains outside plausible bounds'); null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(0.2, 5.0, -0.5, 10.0); unit0_baseline='accept'; unit0_mutant='fitted gains outside plausible bounds'; unit_moved=1 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

### 845bf7a69b48b94b custom_components/heatpump_optimizer/sysid.py:892 CMP_BOUND (_slab_refusal) -- equivalent-candidate

Patch `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 <= gains_kw < 2.0):`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_845bf7a69b48b94b.py`.

Unit: gains exactly 2.0: accepted -> refused; null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(0.2, 5.0, 2.0, 10.0); unit0_baseline='accept'; unit0_mutant='fitted gains outside plausible bounds'; unit_moved=1 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

### ab65584805229d1c custom_components/heatpump_optimizer/sysid.py:892 GUARD_OFF (_slab_refusal) -- equivalent-candidate

Patch `if not (-0.5 <= gains_kw <= 2.0): -> if False:`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_ab65584805229d1c.py`.

Unit: gains 3.0, -1.0, 2.0000001: refused -> accepted (then clipped to [0, 2] at sysid.py:2411); null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(0.2, 5.0, 3.0, 10.0); unit0_baseline='fitted gains outside plausible bounds'; unit0_mutant='accept'; unit1_args=(0.2, 5.0, -1.0, 10.0); unit1_baseline='fitted gains outside plausible bounds'; unit1_mutant='accept'; unit2_args=(0.2, 5.0, 2.0000001, 10.0); unit2_baseline='fitted gains outside plausible bounds'; unit2_mutant='accept'; unit_moved=3 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

### 186b3076dcce442c custom_components/heatpump_optimizer/sysid.py:897 CMP_BOUND (_slab_refusal) -- equivalent-candidate

Patch `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau <= 200.0) or not (0.01 <= ua < 5.0):`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_186b3076dcce442c.py`.

Unit: ua exactly 5.0: accepted -> refused ('fitted parameters outside plausible bounds'); null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(5.0, 10.0, 0.3, 40.0); unit0_baseline='accept'; unit0_mutant='fitted parameters outside plausible bounds'; unit_moved=1 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

### 66e79426a66d3362 custom_components/heatpump_optimizer/sysid.py:897 CMP_BOUND (_slab_refusal) -- equivalent-candidate

Patch `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):`. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_66e79426a66d3362.py`.

Unit: tau exactly 200 h: accepted -> refused; null rows do not move. unreachable through production: _slab_refusal's only caller is _slab_outcome (sysid.py:2408), fed ua=exp(x[0]) and room_cap=exp(x[1]) from _lm_solve, whose seeds are floored at log(1e-3)/log(1e-2) (sysid.py:2375-2376) and whose accepted candidates are clipped to [1e-4, 1e2] / [1e-3, 1e3] (sysid.py:836-839), so ua and room_cap never come near 1e-6; gains_kw=x[2] sits on the ridge prior gains_prior_kw = night_gains_prior_kw over ThermalParameters.internal_gains, which no config key, preset or coordinator write moves off 0.3 (the learned profile is clipped to [0, 0.9] at coordinator.py:9452 and is not published into the plant); measured: 360 production fits, 108 _slab_refusal calls, 0 separating, 0 published results differ, delivered gains in [-2.2e-6, 0.9], ua in [0.057, 0.97], room_cap in [4.07, 14.6].

Should have failed: none through production; a direct unit call separates. tests/features.py:53988 calls _slab_refusal directly only at (0.0, 400.0, 0.0, 200.0) (the sign guard, decided identically by this mutant); the assertion it lacks is a direct call at the mutated boundary value.

Numbers: unit0_args=(0.5, 50.0, 0.3, 50.0); unit0_baseline='accept'; unit0_mutant='fitted parameters outside plausible bounds'; unit_moved=1 count; null_moved=0 count (over 3 null rows); reach_runs=360 count; reach_slab_refusal_calls=108 count; reach_calls_separating=0 count; reach_results_differ=0 count; reach_ua_range=[0.0568477, 0.965586]; reach_room_cap_range=[4.06749, 14.5566]; reach_gains_kw_range=[-2.24402e-06, 0.9]; reach_slab_mass_range=[16.5, 23]

## Unfinished

- the coverage row's enumerator reads SURVIVORS.tsv, the orchestrator's wave list, which is not in this box's tree; its universe 742 is the brief's count, not re-derived here

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`: the full gate per mutant (apply, commit, gate_lock lease, full drift gate, record, reset)
- `gate_wave.sh (dispatch ref, out of tree)`: the box driver: fullgate.py null once, then fullgate.py run per keys.tsv key in order, one gate at a time, 4 h cap, checkpoint after each
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_ba25d4dc58c7fecc.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_67f17d97399379c0.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_99866c2ffc704413.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_b4f7503c6959449d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_f6016f6adb9683a8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_0c0a6bcb94a3ba3a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_2b5a8949055ecd4c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_e3ea72b8dc57884a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_6db5003950426ce8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_1e9d97a860146a80.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_51b2c8ce3dadae0c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_62a1f4d0c1be5960.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_845bf7a69b48b94b.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_ab65584805229d1c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_186b3076dcce442c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_66e79426a66d3362.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/_mut.py`: in-memory one-line mutant of a production function
- `dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/_drive.py`: production SystemIdentification sweep (two-state presets + first-order plant)
