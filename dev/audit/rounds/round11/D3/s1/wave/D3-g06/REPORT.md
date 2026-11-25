# D3-s1 round 11, box D3-g06: the full gate for 16 u1 full-net survivors (D3.M3) and their D3.M4 answers

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Seat D3-s1. Counts are final; every wall and load number is provisional.

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1110       13473          12        1801       14976
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.62
Sun Nov 22 21:38:19 UTC 2026
--- re-fire Wed Nov 25 00:46:04 UTC 2026 (resumed from handoff-wip 66fd370c6b; null kept)
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         748       14061          12        1548       15338
Swap:              0           0           0
Model name:                              Intel(R) Xeon(R) Processor @ 2.10GHz
/dev/vda        252G   12G   58G  17% /
load1: 0.47
```

Full-gate null control (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`, comment-only marker): gate_rc=1, failed_scripts=['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail_lines={'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, summary=['3 TEST SCRIPT(S) FAILED'], wall 3471.9 s (provisional), load1 0.63..1.0.

Procedure: gate_wave.sh (shipped on dispatch/finder-r11-D3-g06): null once, then `fullgate.py run --src complete --key <key>` per keys.tsv row, one gate at a time, 4 h cap, checkpoint after each; each survivor's probe ran from a separate baseline worktree, never the gate tree.

## Tally

- keys: 16; gated: 16; KILLED 2, RED-AS-NULL 14
- KILLED by script: {'node tests/card.mjs': 2, 'python3 tests/stress.py': 1}
- candidates (full-gate survivors whose probe moves): 14; equivalent-candidates: 0; TIMEOUT: 0

## Gate table

| key | site | verdict | killed_by | class | gate wall s (prov.) | load1 |
|---|---|---|---|---|---|---|
| d915157ffe509e58 | coordinator.py:10231 CMP_BOUND | RED-AS-NULL | - | candidate | 3427.1 | 0.56..0.93 |
| dff127b334682936 | coordinator.py:9327 CMP_BOUND | RED-AS-NULL | - | candidate | 3362.1 | 0.86..0.92 |
| 6b306521ae03824d | coordinator.py:5382 CMP_BOUND | KILLED | node tests/card.mjs | killed | 3421.4 | 0.72..0.96 |
| b546d5e705722bb5 | coordinator.py:5382 GUARD_OFF | KILLED | node tests/card.mjs, python3 tests/stress.py | killed | 3252.1 | 0.89..0.92 |
| 59337f7f63497f21 | coordinator.py:9437 CMP_BOUND | RED-AS-NULL | - | candidate | 3196.0 | 0.78..0.92 |
| 4542deee22df985f | coordinator.py:9440 GUARD_OFF | RED-AS-NULL | - | candidate | 3168.0 | 0.85..0.92 |
| 8e729260c34e2e3b | coordinator.py:9440 CMP_BOUND | RED-AS-NULL | - | candidate | 3163.5 | 0.85..0.92 |
| e347b6890486dd0d | coordinator.py:9447 GUARD_OFF | RED-AS-NULL | - | candidate | 3133.3 | 0.34..0.92 |
| 72fbe692d30d275e | coordinator.py:9452 CLAMP_DROP | RED-AS-NULL | - | candidate | 3153.9 | 0.8..1.01 |
| 2e4d4a89570a1b24 | coordinator.py:9383 CMP_BOUND | RED-AS-NULL | - | candidate | 3152.0 | 0.85..0.92 |
| 30fcf9ba50130ea2 | coordinator.py:9386 CMP_BOUND | RED-AS-NULL | - | candidate | 3162.9 | 0.78..0.92 |
| 89a3d25e2425b8e0 | coordinator.py:9386 GUARD_OFF | RED-AS-NULL | - | candidate | 3155.3 | 1.08..0.92 |
| efa2c19c51831a68 | coordinator.py:9386 CMP_BOUND | RED-AS-NULL | - | candidate | 3139.7 | 0.78..0.93 |
| 205d200980d58e9e | coordinator.py:9390 CMP_BOUND | RED-AS-NULL | - | candidate | 3322.5 | 0.79..0.93 |
| 96fe4cecaa16f997 | coordinator.py:9390 GUARD_OFF | RED-AS-NULL | - | candidate | 3328.4 | 0.79..0.92 |
| 1a24365a55bfb2c7 | coordinator.py:9402 BOOLOP | RED-AS-NULL | - | candidate | 3511.8 | 0.79..0.93 |

## Survivors: the D3.M4 answer and the probe numbers

**d915157ffe509e58** coordinator.py:10231 CMP_BOUND `if 0 < idx < len(trajectory): -> if 0 < idx <= len(trajectory):` (HeatPumpOptimizerCoordinator._file_lead_predictions), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_d915157ffe509e58.py`: len4 baseline [] mutant raisesIndexError; len12 baseline [(1.0,20.04)] mutant raisesIndexError; len24 baseline [(1.0,20.04),(3.0,20.12)] mutant raisesIndexError; len48 baseline [(1.0,20.04),(3.0,20.12),(6.0,20.24)] mutant raisesIndexError; len96 baseline [(1.0,20.04),(3.0,20.12),(6.0,20.24),(12.0,20.48)] mutant raisesIndexError; cases_moved=5, null_moved=0 (len5=[(1.0,20.04)], len97=[(1.0,20.04),(3.0,20.12),(6.0,20.24),(12.0,20.48),(24.0,20.96)]). Reach: the plan's room trajectory (OptimizationResult.sensor_trajectory) is exactly lead/dt_h points long: a horizon of 3, 11, 23, 47 or 95 steps at 15 min; the caller is _solve_record at coordinator.py:6461. Should have failed: tests/features.py 'each solve files one promise per lead bucket within the horizon' (the _c16 block) drives only a 97-point trajectory; no check files from a trajectory exactly lead/dt_h points long and asserts that lead is skipped without a raise. Candidate title: No check files lead predictions from a trajectory exactly lead/dt_h points long; idx<=len is unseen (severity claimed low).

**dff127b334682936** coordinator.py:9327 CMP_BOUND `if not np.isfinite(thermal_kw) or thermal_kw <= 0.0: -> if not np.isfinite(thermal_kw) or thermal_kw < 0.0:` (HeatPumpOptimizerCoordinator._fold_capacity_envelope), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_dff127b334682936.py`: cop0 baseline {} mutant {-4:[0.0,1]}; heat0 baseline {} mutant {-4:[0.0,1]}; draw0 baseline {} mutant {-4:[0.0,1]}; cases_moved=3, null_moved=0 (cop_neg={}, cop2={-4:[8.0,1]}). Reach: thermal_kw = observed_cop * measured_power or a measured heat_kw; through _fold_cop_evidence (coordinator.py:5422) observed_cop > 0.1 and heat 0 is refused as observed_cop, so 0 kW needs a 0 kW measured draw with a passing observed COP or a direct call; tests/features.py calls the symbol directly (#17, round-5 D3-06 block). Should have failed: tests/features.py 'a non-positive thermal figure never enters the learned envelope' (_c14_neg, round-5 D3-06 block) feeds observed_cop -1.0 only; no check feeds a thermal figure of exactly 0 kW. Candidate title: No check folds a thermal figure of exactly 0 kW into the capacity envelope; <= 0 -> < 0 is unseen (severity claimed low).

**59337f7f63497f21** coordinator.py:9437 CMP_BOUND `if previous_time is None or dt_h <= 1e-6: -> if previous_time is None or dt_h < 1e-6:` (HeatPumpOptimizerCoordinator._fold_internal_gains), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_59337f7f63497f21.py`: dt1e-6 baseline None mutant 0.9; cases_moved=1, null_moved=0 (dt0p5=0.4, dt0=None). Reach: dt_h is the interval since the last learning sample (coordinator.py ~5831); exactly 1e-6 h (3.6 ms) is the boundary. Should have failed: tests/features.py #53 internal-gains block (_c53, _nf_edge) folds only dt_h 0.5; no check folds at dt_h 1e-6 and asserts no profile forms. Candidate title: No check folds internal gains at dt_h exactly 1e-6 h; the dt guard boundary is unpinned (severity claimed low).

**4542deee22df985f** coordinator.py:9440 GUARD_OFF `if capacity <= 1e-6: -> if False:` (HeatPumpOptimizerCoordinator._fold_internal_gains), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_4542deee22df985f.py`: cap0 baseline None mutant 0.3; cap0_prior0p8 baseline 0.8 mutant 0.79; capneg baseline None mutant 0.29; cases_moved=3, null_moved=0 (cap10=0.4, cap10_prior0p8=0.89). Reach: capacity is _zone_capacity(params), the zone's thermal mass from _house_loss_terms; zero or negative needs a degenerate room/zone mass. Should have failed: tests/features.py #53 internal-gains block folds only the default zone mass; no check folds with a zero thermal mass and asserts the profile untouched. Candidate title: No check folds internal gains with a zero zone mass; dropping the capacity guard is unseen (severity claimed low).

**8e729260c34e2e3b** coordinator.py:9440 CMP_BOUND `if capacity <= 1e-6: -> if capacity < 1e-6:` (HeatPumpOptimizerCoordinator._fold_internal_gains), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_8e729260c34e2e3b.py`: cap1e-6 baseline None mutant 0.3; cap1e-6_prior0p8 baseline 0.8 mutant 0.79; cases_moved=2, null_moved=0 (cap10=0.4, cap0=None). Reach: capacity is _zone_capacity(params); exactly 1e-6 is the boundary. Should have failed: tests/features.py #53 internal-gains block; no check folds at capacity exactly 1e-6. Candidate title: No check folds internal gains at a zone mass of exactly 1e-6; the capacity boundary is unpinned (severity claimed low).

**e347b6890486dd0d** coordinator.py:9447 GUARD_OFF `if not np.isfinite(y): -> if False:` (HeatPumpOptimizerCoordinator._fold_internal_gains), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_e347b6890486dd0d.py`: res_nan baseline 0.3 mutant nan; res_inf baseline 0.3 mutant 0.9; cases_moved=2, null_moved=0 (res0p1=0.4, res0=0.3). Reach: the production caller drops a non-finite residual first (coordinator.py:5805 `if not np.isfinite(residual): return clean`) and capacity/dt_h are finite, so a non-finite y needs a direct call or an overflow. Should have failed: tests/features.py #53 internal-gains block; no check feeds a non-finite residual and asserts the profile stays finite. Candidate title: No check feeds _fold_internal_gains a non-finite residual; dropping the isfinite guard is unseen (severity claimed low).

**72fbe692d30d275e** coordinator.py:9452 CLAMP_DROP `np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05)) -> np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * (g0))` (HeatPumpOptimizerCoordinator._fold_internal_gains), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_72fbe692d30d275e.py`: g0_0 baseline 0.1 mutant 0.0; g0_0p01 baseline 0.11 mutant 0.03; g0_0p04 baseline 0.14 mutant 0.12; cases_moved=3, null_moved=0 (g0_default=0.4, g0_0p05=0.15). Reach: g0 is ThermalParameters.internal_gains: not a config key (ThermalParameters._tabled_values has none), so every production coordinator carries the 0.3 default and max(g0, 0.05) == g0; only a params object built with gains < 0.05 separates the arms. Should have failed: tests/features.py 'a warm evening hour learns extra gains, tethered under the cap' asserts <= 3*g0 at g0 0.3 only; no check runs a g0 below 0.05 where the 0.05 floor binds. Candidate title: No check runs the internal-gains cap with g0 below 0.05; the 0.05 floor of the cap is unpinned (severity claimed low).

**2e4d4a89570a1b24** coordinator.py:9383 CMP_BOUND `if irradiance < SOLAR_APERTURE_MIN_IRRADIANCE: -> if irradiance <= SOLAR_APERTURE_MIN_IRRADIANCE:` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_2e4d4a89570a1b24.py`: irr150 baseline (1.0,1.0,0.0147,0.16) mutant (0.0,1.0,0.0,0.0); cases_moved=1, null_moved=0 (irr149=(0.0,1.0,0.0,0.0), irr400=(1.0,1.0,0.0392,0.16)). Reach: irradiance is the interval's measured solar_radiation (W/m2); exactly 150.0 is the boundary SOLAR_APERTURE_MIN_IRRADIANCE. Should have failed: tests/features.py 'dim steps carry no aperture information and never move the scale' (_c37) folds at 50 W/m2 only; no check folds at exactly SOLAR_APERTURE_MIN_IRRADIANCE. Candidate title: No check folds the solar aperture at exactly 150 W/m2; the irradiance threshold boundary is unpinned (severity claimed low).

**30fcf9ba50130ea2** coordinator.py:9386 CMP_BOUND `if capacity <= 1e-6 or dt_h <= 1e-6: -> if capacity <= 1e-6 or dt_h < 1e-6:` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_30fcf9ba50130ea2.py`: dt1e-6 baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0392,80000.0); cases_moved=1, null_moved=0 (dt0p5=(1.0,1.0,0.0392,0.16), dt0=(0.0,1.0,0.0,0.0)). Reach: dt_h is the interval since the last learning sample; exactly 1e-6 h is the boundary. Should have failed: tests/features.py #36 aperture block folds only dt_h 0.5; no check at dt_h 1e-6. Candidate title: No check folds the solar aperture at dt_h exactly 1e-6 h; the dt guard boundary is unpinned (severity claimed low).

**89a3d25e2425b8e0** coordinator.py:9386 GUARD_OFF `if capacity <= 1e-6 or dt_h <= 1e-6: -> if False:` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_89a3d25e2425b8e0.py`: cap0 baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0392,0.0); dt0 baseline (0.0,1.0,0.0,0.0) mutant raisesZeroDivisionError; dt_neg baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0392,-0.16); cases_moved=3, null_moved=0 (cap10_dt0p5=(1.0,1.0,0.0392,0.16), default=(1.0,1.0,0.0392,0.16)). Reach: capacity = _zone_capacity(params) and dt_h from the learning cycle; zero or negative needs a degenerate mass or a clock step. Should have failed: tests/features.py #36 aperture block folds only the default mass and dt_h 0.5; no check with a zero mass or zero dt_h. Candidate title: No check folds the solar aperture with zero mass or zero dt_h; dropping the guard is unseen (severity claimed low).

**efa2c19c51831a68** coordinator.py:9386 CMP_BOUND `if capacity <= 1e-6 or dt_h <= 1e-6: -> if capacity < 1e-6 or dt_h <= 1e-6:` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_efa2c19c51831a68.py`: cap1e-6 baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0392,0.0); cases_moved=1, null_moved=0 (cap10=(1.0,1.0,0.0392,0.16), cap0=(0.0,1.0,0.0,0.0)). Reach: capacity = _zone_capacity(params); exactly 1e-6 is the boundary. Should have failed: tests/features.py #36 aperture block; no check at capacity exactly 1e-6. Candidate title: No check folds the solar aperture at a zone mass of exactly 1e-6; the capacity boundary is unpinned (severity claimed low).

**205d200980d58e9e** coordinator.py:9390 CMP_BOUND `if x <= 1e-6 or not np.isfinite(y): -> if x < 1e-6 or not np.isfinite(y):` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_205d200980d58e9e.py`: x1e-6 baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,2e-08,0.16); cases_moved=1, null_moved=0 (x0=(0.0,1.0,0.0,0.0), x_real=(1.0,1.0,0.0392,0.16)). Reach: x = ThermalModel.compute_solar_gain(irradiance), 0.735 kW at 150 W/m2 with the default aperture; exactly 1e-6 kW needs a near-zero aperture configuration. Should have failed: tests/features.py #36 aperture block; no check with a modelled solar gain of exactly 1e-6 kW. Candidate title: No check folds the solar aperture at a modelled gain of exactly 1e-6 kW; the x boundary is unpinned (severity claimed low).

**96fe4cecaa16f997** coordinator.py:9390 GUARD_OFF `if x <= 1e-6 or not np.isfinite(y): -> if False:` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_96fe4cecaa16f997.py`: x0 baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0,0.16); res_nan baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0392,nan); res_inf baseline (0.0,1.0,0.0,0.0) mutant (1.0,1.0,0.0392,inf); cases_moved=3, null_moved=0 (default=(1.0,1.0,0.0392,0.16), res0=(1.0,1.0,0.0392,0.0)). Reach: x is the modelled solar gain (0 with a zero aperture); a non-finite residual is dropped upstream at coordinator.py:5805, so y non-finite needs a direct call. Should have failed: tests/features.py #36 aperture block; no check with a zero modelled gain or a non-finite residual. Candidate title: No check feeds _fold_solar_aperture a zero modelled gain or a non-finite residual; dropping the guard is unseen (severity claimed low).

**1a24365a55bfb2c7** coordinator.py:9402 BOOLOP `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6: -> if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES or m["var"] > 1e-6:` (HeatPumpOptimizerCoordinator._fold_solar_aperture), full gate RED-AS-NULL, class candidate. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_1a24365a55bfb2c7.py`: n1 baseline (1.0,1.0,0.0392,0.16) mutant (1.0,2.0,0.0392,0.16); n10_varied baseline (10.0,1.0,0.458124495,2.784389) mutant (10.0,2.0,0.458124495,2.784389); n40_var0 baseline (41.0,1.0,1.96,0.65) mutant (41.0,0.3,1.96,0.65); cases_moved=3, null_moved=0 (preset_n29_var0p5=(30.0,1.087994,1.9992,0.65), preset_n40_var0p5=(41.0,1.087994,1.9992,0.65)). Reach: every installation's first sunny samples: n < SOLAR_APERTURE_MIN_SAMPLES (30) with a non-zero EWMA variance after the first fold. Should have failed: tests/features.py 'the aperture regression converges on the true scale' (_c36) runs 180 samples and reads only the end; no check asserts the scale stays 1.0 before SOLAR_APERTURE_MIN_SAMPLES. Candidate title: No check holds the aperture scale at 1.0 before 30 samples; and->or adopts it from the first sample (severity claimed medium).

## Findings

None numbered here: every candidate is under `gate_survivors` in REPORT.json; the orchestrator's consolidation assigns ids across the boxes.

## Non-findings

- Full-gate null control on box D3-g06 (comment-only marker): a usable null (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`): gate_rc=1, failed_scripts=['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail_lines={'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, summary=['3 TEST SCRIPT(S) FAILED'], wall 3471.9 s (provisional), load1 0.63..1.0
- coordinator.py:5382 CMP_BOUND (if modelled_cop <= 0.1: -> if modelled_cop < 0.1:) is pinned by the full gate: KILLED by node tests/card.mjs (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 6b306521ae03824d`): gate_rc=1, killed_by=['node tests/card.mjs'], wall 3421.4 s (provisional), record dev/audit/rounds/round11/D3/s1/wave/D3-g06/gates/6b306521ae03824d.json
- coordinator.py:5382 GUARD_OFF (if modelled_cop <= 0.1: -> if False:) is pinned by the full gate: KILLED by node tests/card.mjs, python3 tests/stress.py (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key b546d5e705722bb5`): gate_rc=1, killed_by=['node tests/card.mjs', 'python3 tests/stress.py'], wall 3252.1 s (provisional), record dev/audit/rounds/round11/D3/s1/wave/D3-g06/gates/b546d5e705722bb5.json

## Unfinished

- none

## Harnesses

- dev/audit/rounds/round11/D3/s1/fullgate.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_1a24365a55bfb2c7.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_205d200980d58e9e.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_2e4d4a89570a1b24.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_30fcf9ba50130ea2.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_4542deee22df985f.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_59337f7f63497f21.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_72fbe692d30d275e.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_89a3d25e2425b8e0.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_8e729260c34e2e3b.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_96fe4cecaa16f997.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_d915157ffe509e58.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_dff127b334682936.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_e347b6890486dd0d.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g06/probes/probe_efa2c19c51831a68.py

## Exposure

none
