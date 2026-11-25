# D3-s1, box D3-g10: the full gate for 16 D3.M3 full-net survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Walls and loads provisional; counts final.

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1104       13480          12        1801       14983
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.30GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.73
Sun Nov 22 21:38:51 UTC 2026

== re-fire Wed Nov 25 00:48:46 UTC 2026 (successor seat, new container)
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         765       14029          12        1564       15321
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.12
```

Null control (`fullgate.py null`, comment-only marker): gate_rc=1, failed_scripts=['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail_lines={'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 2964.6 s, load1 0.57..0.92. RED-AS-NULL = red, but no script beyond the null's (read as survived).

Procedure: gate_wave.sh run -> fullgate.py run --src complete --key <key> (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh), one at a time, 4 h cap. Probes apply each mutant in memory (the method recompiled from its own source, attached by mock.patch.object for the mutant arm) and ran from a separate baseline worktree, never the gate tree.

## Tally

- gated: 16 of 16 (with a verdict: 15)
- KILLED: 1 (python3 tests/structure.py 1)
- SURVIVED: 0
- RED-AS-NULL: 14
- TIMEOUT: 1
- candidates: 14
- equivalent-candidates: 0

| key | site | patch | verdict | killed_by | wall s | load1 | class |
|---|---|---|---|---|---|---|---|
| 205660ee362d1a07 | custom_components/heatpump_optimizer/coordinator.py:7861 GUARD_OFF | `if ctx._thermal_params.two_tank_modelled: -> if False:` | RED-AS-NULL | - | 2879.5 | 0.87..0.92 | candidate |
| 34c20aac32a34344 | custom_components/heatpump_optimizer/coordinator.py:9273 CMP_BOUND | `if margin <= 0.0 and self._curve_learner.bias < 0.0: -> if margin <= 0.0 and self._curve_learner.bias <= 0.0:` | RED-AS-NULL | - | 2789.6 | 0.93..0.92 | candidate |
| c7054b2e59c82141 | custom_components/heatpump_optimizer/coordinator.py:9273 CMP_BOUND | `if margin <= 0.0 and self._curve_learner.bias < 0.0: -> if margin < 0.0 and self._curve_learner.bias < 0.0:` | RED-AS-NULL | - | 2843.0 | 0.79..0.96 | candidate |
| ff56936f15fd4675 | custom_components/heatpump_optimizer/coordinator.py:9273 BOOLOP | `if margin <= 0.0 and self._curve_learner.bias < 0.0: -> if margin <= 0.0 or self._curve_learner.bias < 0.0:` | RED-AS-NULL | - | 2779.2 | 0.96..0.92 | candidate |
| 349b2e117d076731 | custom_components/heatpump_optimizer/coordinator.py:6747 GUARD_OFF | `if wood_mean is None and had: -> if False:` | RED-AS-NULL | - | 2761.4 | 0.72..1.01 | candidate |
| cdd17526ebbf2a93 | custom_components/heatpump_optimizer/coordinator.py:6747 BOOLOP | `if wood_mean is None and had: -> if wood_mean is None or had:` | RED-AS-NULL | - | 2753.5 | 0.86..0.93 | candidate |
| 8ab42c4ab9755537 | custom_components/heatpump_optimizer/coordinator.py:6752 BOOLOP | `elif wood_mean is not None and not had: -> elif wood_mean is not None or not had:` | RED-AS-NULL | - | 2694.4 | 0.79..0.93 | candidate |
| e689dc488b493c6b | custom_components/heatpump_optimizer/coordinator.py:6752 GUARD_OFF | `elif wood_mean is not None and not had: -> elif False:` | RED-AS-NULL | - | 2635.5 | 0.86..0.92 | candidate |
| f2a191b48718e088 | custom_components/heatpump_optimizer/coordinator.py:5234 GUARD_OFF | `if state.active: -> if False:` | RED-AS-NULL | - | 3495.1 | 0.4..1.0 | candidate |
| b871ff0486182e3e | custom_components/heatpump_optimizer/coordinator.py:7549 CLAMP_DROP | `self._snow_accum_cm += rate_now * min(dt_true, 6.0) -> self._snow_accum_cm += rate_now * (dt_true)` | RED-AS-NULL | - | 3190.3 | 0.85..1.01 | candidate |
| 813cb7aecbd78f98 | custom_components/heatpump_optimizer/coordinator.py:7551 CMP_BOUND | `if self._snow_accum_cm >= SNOW_HEAVY_CM: -> if self._snow_accum_cm > SNOW_HEAVY_CM:` | RED-AS-NULL | - | 3188.6 | 0.94..0.92 | candidate |
| aa6b718c979bf831 | custom_components/heatpump_optimizer/coordinator.py:7118 GUARD_OFF | `if not self._weather_outage_cycles: -> if False:` | RED-AS-NULL | - | 3119.5 | 0.79..1.0 | candidate |
| 18fe89552892dc4b | custom_components/heatpump_optimizer/coordinator.py:7130 GUARD_OFF | `if self._weather_outage_cycles: -> if False:` | RED-AS-NULL | - | 3043.3 | 0.85..0.93 | candidate |
| 65175bb211f70f26 | custom_components/heatpump_optimizer/coordinator.py:10678 GUARD_OFF | `if report is None: -> if False:` | RED-AS-NULL | - | 3015.9 | 0.86..0.79 | candidate |
| 3b6228b7d69c32bc | custom_components/heatpump_optimizer/coordinator.py:7693 CLAMP_DROP | `np.clip(displace_value, self._ecl110_displace_min, self._ecl110_displace_max) -> (displace_value)` | KILLED | python3 tests/structure.py | 3341.7 | 0.66..0.93 | killed |
| f68e6ba7e28b251a | custom_components/heatpump_optimizer/coordinator.py:6356 GUARD_OFF | `if self._optimization_running: -> if False:` | TIMEOUT | - | None | None..None | timeout |

## Survivors: the step-4 answer and the probe

### 205660ee362d1a07 custom_components/heatpump_optimizer/coordinator.py:7861 GUARD_OFF (candidate)

`if ctx._thermal_params.two_tank_modelled: -> if False:` in HeatPumpOptimizerCoordinator._thermal_view. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_205660ee362d1a07.py`: baseline 2 keys (wood 55.0), mutant 0 keys (wood None); inputs tried: two_tank True, wood 55.0; two_tank False (null).
Should have failed: tests/config_flow_steps.py, tests/entities.py, tests/env_drift.py, tests/features.py, tests/finite_boundary.py, tests/manual_plan.py execute the line (reach.tsv); tests/features.py drives two-tank topologies (_w2t_* ~15885-15930, the two-tank capture ~6402) and features.py:72533 reads coord._thermal_view() keys, but no check reads two_tank_modelled / wood_tank_temperature from the thermal view of a two_tank_modelled install; entities.py configures no two-tank topology.
Candidate: No check reads the thermal view's two-tank keys; dropping the two-tank block from the payload is unseen (severity claimed medium, class_guess new).

### 34c20aac32a34344 custom_components/heatpump_optimizer/coordinator.py:9273 CMP_BOUND (candidate)

`if margin <= 0.0 and self._curve_learner.bias < 0.0: -> if margin <= 0.0 and self._curve_learner.bias <= 0.0:` in HeatPumpOptimizerCoordinator._track_curve_comfort. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_34c20aac32a34344.py`: baseline (0.0, 5, 0), mutant (0.0, 0, 0); inputs tried: margin -0.3, bias 0.0; margin -0.3, bias -1.0 (null); margin +0.5, bias 0.0 (null).
Should have failed: tests/config_flow_steps.py, tests/features.py execute the line (reach.tsv); tests/features.py ~23686-23704 (_c2c) checks the worst margin and 'touching the floor with the bias applied resets it immediately' only at bias -1.0; no case dips under the floor with bias 0 and asserts comfortable_days is kept.
Candidate: No check dips a zone under the floor with zero curve bias; bias<0 -> <=0 (comfortable-day streak wiped) is unseen (severity claimed low, class_guess new).

### c7054b2e59c82141 custom_components/heatpump_optimizer/coordinator.py:9273 CMP_BOUND (candidate)

`if margin <= 0.0 and self._curve_learner.bias < 0.0: -> if margin < 0.0 and self._curve_learner.bias < 0.0:` in HeatPumpOptimizerCoordinator._track_curve_comfort. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_c7054b2e59c82141.py`: baseline (0.0, 0, 1), mutant (-1.0, 5, 0); inputs tried: margin 0.0, bias -1.0; margin -0.3, bias -1.0 (null); margin 0.0, bias 0.0 (null); margin +0.5, bias -1.0 (null).
Should have failed: tests/config_flow_steps.py, tests/features.py execute the line (reach.tsv); tests/features.py ~23697-23704 (_c2c) sets the room to floor - 0.1 (margin -0.1); no case lands exactly on the floor (margin 0.0) and asserts the bias reset.
Candidate: No check lands a zone exactly on the comfort floor with a curve bias; margin<=0 -> <0 is unseen (severity claimed low, class_guess new).

### ff56936f15fd4675 custom_components/heatpump_optimizer/coordinator.py:9273 BOOLOP (candidate)

`if margin <= 0.0 and self._curve_learner.bias < 0.0: -> if margin <= 0.0 or self._curve_learner.bias < 0.0:` in HeatPumpOptimizerCoordinator._track_curve_comfort. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_ff56936f15fd4675.py`: baseline (-1.0, 5, 0), mutant (0.0, 0, 1); inputs tried: margin +0.5, bias -1.0; margin -0.3, bias -1.0 (null); margin +0.5, bias 0.0 (null).
Should have failed: tests/config_flow_steps.py, tests/features.py execute the line (reach.tsv); tests/features.py ~23686-23704 (_c2c) calls _track_curve_comfort with a comfortable room only while bias is 0, and sets bias -1.0 only for the floor-touch case; no case keeps a learned bias through a comfortable update.
Candidate: No check keeps a learned curve bias through a comfortable update; and->or (every update resets the bias) is unseen (severity claimed medium, class_guess new).

### 349b2e117d076731 custom_components/heatpump_optimizer/coordinator.py:6747 GUARD_OFF (candidate)

`if wood_mean is None and had: -> if False:` in HeatPumpOptimizerCoordinator._update_current_state. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_349b2e117d076731.py`: baseline (warnings,infos,format_errors)=(1, 2, 0), temps (60.0, 60.0, None, None, 58.0), mutant (0, 2, 0), temps identical; inputs tried: healthy,healthy,unavailable,unavailable,healthy; single healthy read (null).
Should have failed: tests/features.py execute the line (reach.tsv); tests/features.py drives _update_current_state with wood_tank_top/bottom entities (~2055-2109) but never makes the wood probe go stale after a good read, and no check reads the coordinator log.
Candidate: No check reads the stale-wood-probe WARNING; disabling it is unseen (published temperature unaffected) (severity claimed low, class_guess new).

### cdd17526ebbf2a93 custom_components/heatpump_optimizer/coordinator.py:6747 BOOLOP (candidate)

`if wood_mean is None and had: -> if wood_mean is None or had:` in HeatPumpOptimizerCoordinator._update_current_state. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_cdd17526ebbf2a93.py`: baseline (1, 2, 0), temps (60.0, 60.0, None, None, 58.0), mutant (3, 2, 0), temps identical; inputs tried: healthy,healthy,unavailable,unavailable,healthy; single healthy read (null).
Should have failed: tests/features.py execute the line (reach.tsv); tests/features.py drives _update_current_state with wood entities (~2055-2109) but no check reads the log: a healthy held wood probe logging the stale WARNING every cycle is not asserted absent.
Candidate: No check bounds the stale-wood-probe WARNING to transitions; and->or (WARNING every held cycle) is unseen (severity claimed low, class_guess N-log-flood).

### 8ab42c4ab9755537 custom_components/heatpump_optimizer/coordinator.py:6752 BOOLOP (candidate)

`elif wood_mean is not None and not had: -> elif wood_mean is not None or not had:` in HeatPumpOptimizerCoordinator._update_current_state. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_8ab42c4ab9755537.py`: baseline (1, 2, 0), temps (60.0, 60.0, None, None, 58.0), mutant (1, 4, 1), temps identical; inputs tried: healthy,healthy,unavailable,unavailable,healthy; single healthy read (null).
Should have failed: tests/features.py execute the line (reach.tsv); tests/features.py drives _update_current_state with wood entities (~2055-2109) but no check reads the log, so the activation INFO repeating on a held healthy cycle and '%.1f' formatted with None on a second stale cycle go unasserted.
Candidate: No check bounds the two-tank activation INFO to transitions; and->or (repeat INFO, %.1f of None) is unseen (severity claimed low, class_guess N-log-flood).

### e689dc488b493c6b custom_components/heatpump_optimizer/coordinator.py:6752 GUARD_OFF (candidate)

`elif wood_mean is not None and not had: -> elif False:` in HeatPumpOptimizerCoordinator._update_current_state. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_e689dc488b493c6b.py`: baseline (1, 2, 0), temps (60.0, 60.0, None, None, 58.0), mutant (1, 0, 0), temps identical; inputs tried: healthy,healthy,unavailable,unavailable,healthy; single stale read (null).
Should have failed: tests/features.py execute the line (reach.tsv); tests/features.py drives _update_current_state with wood entities (~2055-2109) but no check reads the 'Two-tank model active' INFO.
Candidate: No check reads the two-tank activation INFO; disabling it is unseen (published temperature unaffected) (severity claimed low, class_guess new).

### f2a191b48718e088 custom_components/heatpump_optimizer/coordinator.py:5234 GUARD_OFF (candidate)

`if state.active: -> if False:` in HeatPumpOptimizerCoordinator._update_external_heat_detection. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_f2a191b48718e088.py`: baseline (1, False), mutant (0, False); inputs tried: detector active; detector inactive (null).
Should have failed: tests/block_duty.py, tests/boost_drift_replay.py, tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/finite_boundary.py, tests/manual_plan.py, tests/solar_alignment.py execute the line (reach.tsv); none of the eight executing scripts reads the coordinator's DEBUG log; the line only chooses whether a debug record is emitted.
Candidate: No check reads the external-heat DEBUG record; disabling it is unseen (detector state unaffected) (severity claimed low, class_guess new).

### b871ff0486182e3e custom_components/heatpump_optimizer/coordinator.py:7549 CLAMP_DROP (candidate)

`self._snow_accum_cm += rate_now * min(dt_true, 6.0) -> self._snow_accum_cm += rate_now * (dt_true)` in HeatPumpOptimizerCoordinator._update_snow_memory. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_b871ff0486182e3e.py`: baseline (1.2, False), mutant (2.4, True); inputs tried: gap 12 h, rate 0.2; gap 3 h (null); gap 6 h (null, the boundary).
Should have failed: tests/features.py execute the line (reach.tsv); tests/features.py ~23067-23083 (_c31) seeds the clock then calls again 3 h later, inside the 6 h bound; no case leaves a gap past 6 h and asserts the new fall is credited for 6 h only.
Candidate: No check leaves a snow-memory gap past 6 h; dropping the new-fall bound (an outage books a blizzard) is unseen (severity claimed medium, class_guess new).

### 813cb7aecbd78f98 custom_components/heatpump_optimizer/coordinator.py:7551 CMP_BOUND (candidate)

`if self._snow_accum_cm >= SNOW_HEAVY_CM: -> if self._snow_accum_cm > SNOW_HEAVY_CM:` in HeatPumpOptimizerCoordinator._update_snow_memory. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_813cb7aecbd78f98.py`: baseline (2.0, True), mutant (2.0, False); inputs tried: accum 2.0 (tie); accum 1.5 (null); accum 2.5 (null).
Should have failed: tests/config_flow_steps.py, tests/features.py execute the line (reach.tsv); tests/features.py ~23067-23077 asserts 'three hours of heavy snowfall cross the trip line' at 3 cm (> 2.0) only; no case sits exactly on SNOW_HEAVY_CM.
Candidate: No check sits the snow accumulator exactly on SNOW_HEAVY_CM; >= -> > is unseen (severity claimed low, class_guess new).

### aa6b718c979bf831 custom_components/heatpump_optimizer/coordinator.py:7118 GUARD_OFF (candidate)

`if not self._weather_outage_cycles: -> if False:` in HeatPumpOptimizerCoordinator._weather_fetch_failed. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_aa6b718c979bf831.py`: baseline (1, 1, 1, 0, False), mutant (0, 1, 2, 0, False); inputs tried: fail,fail,recover; recover alone (null).
Should have failed: tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/manual_plan.py execute the line (reach.tsv); no executing script reads the coordinator log; entities.py:42245 only counts the call site; the first failure's WARNING ('Plans continue on the last forecast, marked stale') is unasserted.
Candidate: No check reads the first weather-failure WARNING; demoting it to DEBUG is unseen (outage state unaffected) (severity claimed low, class_guess new).

### 18fe89552892dc4b custom_components/heatpump_optimizer/coordinator.py:7130 GUARD_OFF (candidate)

`if self._weather_outage_cycles: -> if False:` in HeatPumpOptimizerCoordinator._weather_fetch_recovered. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_18fe89552892dc4b.py`: baseline (1, 1, 1, 0, False), mutant (1, 0, 1, 0, False); inputs tried: fail,fail,recover; recover alone (null).
Should have failed: tests/entities.py, tests/features.py execute the line (reach.tsv); tests/features.py ~56179-56195 checks that recovery clears the outage count and the staleness (both arms do: the carried M4 claim that the counter is not cleared does not hold, the reset sits outside the guard) but not the recovery INFO.
Candidate: No check reads the weather-recovery INFO; disabling it is unseen (outage reset unaffected) (severity claimed low, class_guess new).

### 65175bb211f70f26 custom_components/heatpump_optimizer/coordinator.py:10678 GUARD_OFF (candidate)

`if report is None: -> if False:` in HeatPumpOptimizerCoordinator.async_diagnose_interval. Gate: RED-AS-NULL (gate_rc 1).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_65175bb211f70f26.py`: baseline (1, None, 1), mutant (0, None, 1); inputs tried: worker returns None; worker returns a report (null).
Should have failed: tests/features.py execute the line (reach.tsv); tests/features.py ~26057-26060 asserts 'no settled interval means no diagnosis, not a crash' (return None) but not the INFO that tells the user why.
Candidate: No check reads the no-settled-interval INFO; disabling it is unseen (return value unaffected) (severity claimed low, class_guess new).

## KILLED (non-findings)

- full gate KILLED 3b6228b7d69c32bc custom_components/heatpump_optimizer/coordinator.py:7693 CLAMP_DROP (np.clip(displace_value, self._ecl110_displace_min, self._ecl110_displace_max) -> (displace_value)): the suite fails on it: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 3b6228b7d69c32bc` -> killed_by=python3 tests/structure.py; gate_rc=1; wall 3341.7 s, load1 0.66..0.93 (provisional)

## Leads

- 3b6228b7d69c32bc custom_components/heatpump_optimizer/coordinator.py:7693 CLAMP_DROP: killed by a size/seam metric, not by a check of the clamp: an equivalent behaviour change that kept the two attribute reads (e.g. clipping against a wrong bound) would pass the gate. Should-fail check absent: a coordinator check that publishes an ECL110 command at displace_min + negative bias and asserts the sent value stays within [displace_min, displace_max].

## KILLED: nature of each kill

- 3b6228b7d69c32bc: structural ratchet only: tests/structure.py refuses an unrecorded improvement (seam_cut_total 415 -> 413, the two self._ecl110_displace_min/max reads leave the coordinator); no behavioural assertion in any script failed beyond the null's three (closure.py selftest, entities.py, harness_headers.py)

## Unfinished

- TIMEOUT key f68e6ba7e28b251a custom_components/heatpump_optimizer/coordinator.py:6356 GUARD_OFF (if self._optimization_running: -> if False:): the full gate passed the 14400 s cap; last script the log shows: tests/features.py; neither KILLED nor SURVIVED

## Harnesses

- dev/audit/rounds/round11/D3/s1/fullgate.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_205660ee362d1a07.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_34c20aac32a34344.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_c7054b2e59c82141.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_ff56936f15fd4675.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_349b2e117d076731.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_cdd17526ebbf2a93.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_8ab42c4ab9755537.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_e689dc488b493c6b.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_f2a191b48718e088.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_b871ff0486182e3e.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_813cb7aecbd78f98.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_aa6b718c979bf831.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_18fe89552892dc4b.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_65175bb211f70f26.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_3b6228b7d69c32bc.py
- gate_wave.sh procedure: gate_wave.sh (dispatch/finder-r11-D3-g10 tip): null once, then fullgate.py run per key in keys.tsv order, one gate at a time, 4 h cap (TIMEOUT), checkpoint after each

## Exposure

Re-fire: the first seat's container stalled after 8 gates (null, 205660ee..e689dc48); a successor seat on a new container restored the checkpoint and ran gates 9-16 (f2a191b4..f68e6ba7) on a 4-core Intel Xeon @ 2.10GHz, 16 GB, alone (MACHINE.txt holds both machines). The null control is the first container's (2.30GHz), kept as gate_wave.sh restores it; every post-re-fire gate's red set equals the null's three scripts except 3b6228b7 (tests/structure.py), so no machine-driven difference is visible. All probes ran on the first container from a separate baseline worktree; their values are deterministic.

No docs/ or GitHub API read. Read per the brief: COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports, REPORT-D3-top6.md / REPORT-D3-rem.md (method pattern), the carried M4 answers for this box's keys, and state/reach.tsv (traced baseline: which closure scripts execute each line). The other boxes' keys.tsv were read from their dispatch/finder-r11-D3-gNN refs only to name not_reached by box; none of their gates was run. $HOME/venv-ci does not exist on this box: gate_wave.sh's PATH entry is inert and python3 resolves to /opt/hpo/venv-ci (the session-start toolchain line: OK).
