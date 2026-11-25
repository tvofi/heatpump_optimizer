# D3-s1 wave box D3-g12: full gate of 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Findings: none numbered here (ids are assigned at consolidation); candidates are under `gate_survivors`.

## Method

Each key's one-line mutant was applied, committed and run through the full gate (`GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=92d38ecb640bd462f2e19c0814d0f0b7df1ee692 GATE_JOBS=1 ./tests/run.sh`) by `dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>`, one gate at a time, driven down keys.tsv by `dev/audit/rounds/round11/D3/s1/wave/D3-g12/gate_wave.sh run` (4 h cap, resumable, tree reset to the baseline after each gate). Verdicts: KILLED (a script red beyond this box's null), SURVIVED (gate_rc 0), RED-AS-NULL (red only on the null's scripts: read as survived), TIMEOUT. Every survivor got the D3.md step-4 answer as an executed probe (`probes/probe_<key>.py`, baseline vs the mutant applied in memory). The box was resumed mid-run from a stalled predecessor's checkpoint; gates 1-6 and the null are the predecessor's, gates 7-16 this seat's, on the same machine class.

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1101       13481          12        1802       14985
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.86
Sun Nov 22 21:39:09 UTC 2026

## re-fire Wed Nov 25 00:47:12 UTC 2026 (new container)
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         792       14022          12        1544       15294
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.37
```

Null control (`fullgate.py null`, comment-only marker): gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}), wall 3895.6 s (provisional), load1 0.89..0.86. All three are artefact checks of the stripped tree and the in-tree wave dir (see NULL-NOTES.md); no card.mjs heap or stress/budget failure. Read as usable.

Every wall/CPU/load number is provisional (provisional: true; nproc 4, Intel Xeon @ 2.10GHz); counts and verdicts are final.

## Tally

- gated: 16 of 16
- KILLED: 0
- SURVIVED: 0
- RED-AS-NULL: 16
- TIMEOUT: 0
- candidates (probe moves the value): 15
- equivalent-candidates: 1

| key | site | verdict | gate_rc | wall_s | class |
|---|---|---|---|---|---|
| 7ffebcb567a4242e | custom_components/heatpump_optimizer/coordinator.py:2540 CMP_BOUND | RED-AS-NULL | 1 | 3804.6 | candidate |
| 845155d368e8b524 | custom_components/heatpump_optimizer/coordinator.py:900 CMP_BOUND | RED-AS-NULL | 1 | 3830.5 | candidate |
| 3e68dcd55f9567e5 | custom_components/heatpump_optimizer/coordinator.py:3013 CMP_BOUND | RED-AS-NULL | 1 | 3808.5 | candidate |
| 88ecd932bc81efec | custom_components/heatpump_optimizer/coordinator.py:3013 CMP_BOUND | RED-AS-NULL | 1 | 3668.5 | candidate |
| 4403a4c7bec83d8f | custom_components/heatpump_optimizer/coordinator.py:3417 GUARD_OFF | RED-AS-NULL | 1 | 3756.7 | candidate |
| 89bec0a0291b4756 | custom_components/heatpump_optimizer/coordinator.py:467 CMP_BOUND | RED-AS-NULL | 1 | 3941.0 | candidate |
| b028ad9d6c702965 | custom_components/heatpump_optimizer/coordinator.py:2360 GUARD_OFF | RED-AS-NULL | 1 | 3346.6 | candidate |
| 3b9eddc7ba9a7488 | custom_components/heatpump_optimizer/defrost.py:124 CONST | RED-AS-NULL | 1 | 3280.9 | candidate |
| fc4fe0f49de831a8 | custom_components/heatpump_optimizer/defrost.py:142 CONST | RED-AS-NULL | 1 | 3231.1 | equivalent-candidate |
| d1197dfed14a6927 | custom_components/heatpump_optimizer/defrost.py:313 CMP_BOUND | RED-AS-NULL | 1 | 3225.1 | candidate |
| 3e3fbb5fcbbe9bcc | custom_components/heatpump_optimizer/defrost.py:566 GUARD_OFF | RED-AS-NULL | 1 | 3221.5 | candidate |
| 1ba9abbe8e702464 | custom_components/heatpump_optimizer/defrost.py:537 CMP_BOUND | RED-AS-NULL | 1 | 3273.3 | candidate |
| 4aac8e694ddc5dfe | custom_components/heatpump_optimizer/defrost.py:537 CMP_BOUND | RED-AS-NULL | 1 | 3448.0 | candidate |
| 5366f1e6254f603c | custom_components/heatpump_optimizer/defrost.py:392 CMP_BOUND | RED-AS-NULL | 1 | 3427.3 | candidate |
| efb33eb6212be24e | custom_components/heatpump_optimizer/defrost.py:392 CMP_BOUND | RED-AS-NULL | 1 | 3466.4 | candidate |
| 0e3569fef6b39497 | custom_components/heatpump_optimizer/defrost.py:434 CMP_BOUND | RED-AS-NULL | 1 | 3480.1 | candidate |

## Survivors: step-4 answers with probe numbers

### 7ffebcb567a4242e: custom_components/heatpump_optimizer/coordinator.py:2540 CMP_BOUND (_open_loop_plan_value), candidate

Patch: `return float(trajectory[0]) if starts[0] - now_s <= 900.0 else None -> return float(trajectory[0]) if starts[0] - now_s < 900.0 else None`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `<=` -> `<` at coordinator.py:2540 the full gate stays green while _open_loop_plan_value returns None instead of 42.0 for a plan starting exactly 900 s ahead. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_7ffebcb567a4242e.py`: baseline seed_at_900s_baseline=42.0, mutant seed_at_900s_mutant=None; inputs tried: lead times 899, 900, 901, 0.5, 1800 s before the plan's first step. Should have failed: tests/features.py (traced baseline executes coordinator.py:2540): no check builds a plan whose first step starts exactly 900 s after now and asserts the open-loop seed is the plan's first value, not None. Severity claimed low, class_guess I1.

### 845155d368e8b524: custom_components/heatpump_optimizer/coordinator.py:900 CMP_BOUND (_outage_reading), candidate

Patch: `if gap_minutes <= OUTAGE_GAP_MINUTES: -> if gap_minutes < OUTAGE_GAP_MINUTES:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `<=` -> `<` at coordinator.py:900 the full gate stays green while a restart 90.0 min after the last heartbeat reads as 'Update gap of 90 minutes' instead of no outage. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_845155d368e8b524.py`: baseline gap_90.0min_baseline=None, mutant gap_90.0min_mutant='Update gap of 90 minutes'; inputs tried: gaps 89, 89.999, 90, 90.001, 91 min. Should have failed: tests/features.py (traced baseline executes coordinator.py:900): no check restarts with a heartbeat exactly OUTAGE_GAP_MINUTES old and asserts no outage is read. Severity claimed low, class_guess I1.

### 3e68dcd55f9567e5: custom_components/heatpump_optimizer/coordinator.py:3013 CMP_BOUND (_plausible_forecast_rows), candidate

Patch: `if not math.isfinite(value) or not lo <= value <= hi: -> if not math.isfinite(value) or not lo < value <= hi:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `lo <= value` -> `lo < value` at coordinator.py:3013 the full gate stays green while every forecast field sitting on its lower edge (a dry hour's 0.0 mm, a calm 0.0 m/s, night's 0 W/m2) is replaced by None: 6 of 6 fields moved. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3e68dcd55f9567e5.py`: baseline precipitation_lo_0_baseline=0.0, mutant precipitation_lo_0_mutant=None; inputs tried: every _FORECAST_FIELD_RANGE field at lo, hi and midpoint (18 inputs); 6 lo edges moved. Should have failed: tests/entities.py / tests/features.py (traced baselines execute coordinator.py:3013): no check feeds a forecast row with a field on its window's lower edge (0.0 mm rain, 0.0 m/s wind, 0 W/m2 solar, 0 % RH) and asserts the value survives _plausible_forecast_rows. Severity claimed medium, class_guess I1.

### 88ecd932bc81efec: custom_components/heatpump_optimizer/coordinator.py:3013 CMP_BOUND (_plausible_forecast_rows), candidate

Patch: `if not math.isfinite(value) or not lo <= value <= hi: -> if not math.isfinite(value) or not lo <= value < hi:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `value <= hi` -> `value < hi` at coordinator.py:3013 the full gate stays green while every forecast field on its upper edge, saturated 100 % humidity among them, is replaced by None: 6 of 6 fields moved. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_88ecd932bc81efec.py`: baseline humidity_hi_100_baseline=100.0, mutant humidity_hi_100_mutant=None; inputs tried: every _FORECAST_FIELD_RANGE field at lo, hi and midpoint (18 inputs); 6 hi edges moved. Should have failed: tests/entities.py / tests/features.py (traced baselines execute coordinator.py:3013): no check feeds a forecast row with a field on its window's upper edge (100 % humidity) and asserts the value survives _plausible_forecast_rows. Severity claimed medium, class_guess I1.

### 4403a4c7bec83d8f: custom_components/heatpump_optimizer/coordinator.py:3417 GUARD_OFF (_price_entity_state), candidate

Patch: `if not entity_id: -> if False:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `if not entity_id:` -> `if False:` at coordinator.py:3417 the full gate stays green while an install with no price entity makes 1 state lookup with a None id (0 at baseline), which raises under Home Assistant core's get-then-lower lookup (modelled: 0 -> 1 raises). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_4403a4c7bec83d8f.py`: baseline unset_falsy_lookups_baseline=0 count, mutant unset_falsy_lookups_mutant=1 count; inputs tried: price entity unset (None) and configured ('sensor.price'); FakeStates (dict.get) and Home Assistant core's get-then-lower shape (modelled). Should have failed: tests/features.py / tests/manual_plan.py (traced baselines execute coordinator.py:3417): every state store the suite uses is a dict.get, which answers None for a None id, so no check can see a lookup made with no entity id; a check asserting _price_entity_state makes no state lookup when the price entity is unset is what is missing. Severity claimed low, class_guess I1.

### 89bec0a0291b4756: custom_components/heatpump_optimizer/coordinator.py:467 CMP_BOUND (_storable_sample_count), candidate

Patch: `if not np.isfinite(count) or not 0 <= count <= 2**31: -> if not np.isfinite(count) or not 0 <= count < 2**31:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `count <= 2**31` -> `count < 2**31` at coordinator.py:467 the full gate stays green while a stored count of exactly 2**31 is rejected (accepted 1 -> 0) and its learned value discarded on load. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_89bec0a0291b4756.py`: baseline accepted_2^31_baseline=1 (value 2147483648), mutant accepted_2^31_mutant=0 (value None); inputs tried: 0, 2**31-1, 2**31, 2**31+1, float(2**31). Should have failed: tests/finite_boundary.py / tests/features.py (traced baselines execute coordinator.py:467): no check loads a stored sample count of exactly 2**31 and asserts it is kept. Severity claimed low, class_guess I1.

### b028ad9d6c702965: custom_components/heatpump_optimizer/coordinator.py:2360 GUARD_OFF (_warm_seeded), candidate

Patch: `if result is not None: -> if False:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `if result is not None:` -> `if False:` at coordinator.py:2360 the full gate stays green while the fresh per-solve optimizer never receives the previous plan: warm-start plan length 96 -> 0 on every cycle. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_b028ad9d6c702965.py`: baseline previous_plan_warm_plan_len_baseline=96 count, mutant previous_plan_warm_plan_len_mutant=0 count; inputs tried: a 96-step previous plan; a cold start (no previous plan). Should have failed: tests/features.py / tests/entities.py / tests/config_flow_steps.py (traced baselines execute coordinator.py:2360): no check asserts the per-solve optimizer receives the previous cycle's plan as _prev_shipped_plan (the #1295 MPC warm start). Severity claimed medium, class_guess I1.

### 3b9eddc7ba9a7488: custom_components/heatpump_optimizer/defrost.py:124 CONST (<module>), candidate

Patch: `DERATE_ALPHA = 0.05 -> DERATE_ALPHA = 0.1`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With DERATE_ALPHA 0.05 -> 0.1 at defrost.py:124 the full gate stays green while one observation at ratio 0.8 moves the bucket to 0.98 instead of 0.99, and the published factor after 12 is 0.8975 instead of 0.9343. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3b9eddc7ba9a7488.py`: baseline ratio0.8_factor_after_1_baseline=0.990000, mutant ratio0.8_factor_after_1_mutant=0.980000; inputs tried: delivered_ratio 0.8 and 1.0, 1 and 12 observations, the published factor after 12. Should have failed: tests/features.py / tests/boost_drift_replay.py (closure of defrost.py): no DefrostDerate check asserts the inferred factor's EWMA step after one observation (1 - DERATE_ALPHA * (1 - ratio)). Severity claimed medium, class_guess I1.

### d1197dfed14a6927: custom_components/heatpump_optimizer/defrost.py:313 CMP_BOUND (DefrostDerate._decide), candidate

Patch: `if inferred < measured: -> if inferred <= measured:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `inferred < measured` -> `<=` at defrost.py:313 the full gate stays green while a tied bucket's published summary row flips from ('measured', 3 samples) to ('inferred', 1 sample); the derate value is unchanged. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_d1197dfed14a6927.py`: baseline tie_diff_count_decide_baseline=('measured', 0.925, 3), mutant tie_diff_count_decide_mutant=('inferred', 0.925, 1); inputs tried: exact ties at equal counts (5/5) and different counts (searched: inferred 1 vs measured 3), inferred strictly lower, strictly higher. Should have failed: tests/features.py (closure of defrost.py): no _decide/summary check builds a bucket whose trust-blended inferred and measured derates tie below DERATE_CONFIDENCE_SAMPLES and asserts source 'measured' with the duty count. Severity claimed low, class_guess I1.

### 3e3fbb5fcbbe9bcc: custom_components/heatpump_optimizer/defrost.py:566 GUARD_OFF (DefrostDerate.from_dict), candidate

Patch: `if instance.migrated: -> if False:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `if instance.migrated:` -> `if False:` at defrost.py:566 the full gate stays green while a pre-v5.3.0 store upgrade logs 0 INFO records instead of 1; migrated flag and factors are unchanged. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3e3fbb5fcbbe9bcc.py`: baseline v1_store_upgrade_log_records_baseline=1 count, mutant v1_store_upgrade_log_records_mutant=0 count; inputs tried: a v1 store (factors/counts) and a v2 store. Should have failed: tests/features.py (traced baseline executes defrost.py:566): no check loads a v1 defrost store and asserts the upgrade INFO record. Severity claimed low, class_guess I1.

### 1ba9abbe8e702464: custom_components/heatpump_optimizer/defrost.py:537 CMP_BOUND (DefrostDerate.from_dict._unit), candidate

Patch: `return 0.0 <= v <= 1.0  # observe_duty's gate; NaN fails it -> return 0.0 <= v < 1.0  # observe_duty's gate; NaN fails it`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `v <= 1.0` -> `v < 1.0` at defrost.py:537 the full gate stays green while a bucket stored at duty 1.0 restarts unmeasured (duty count 12 -> 0; factor 0.6786 -> 1.0, or -> 0.8571 over an inferred derate). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_1ba9abbe8e702464.py`: baseline duty1.0_restored_duty_count_baseline=12 count, mutant duty1.0_restored_duty_count_mutant=0 count; inputs tried: stored duties 0.0, 0.25, 0.5, 1.0; a duty-1.0 bucket over an inferred 0.8 derate. Should have failed: tests/finite_boundary.py / tests/features.py (closure of defrost.py): no round-trip check stores a duty of exactly 1.0 and asserts the bucket survives from_dict. Severity claimed low, class_guess I1.

### 4aac8e694ddc5dfe: custom_components/heatpump_optimizer/defrost.py:537 CMP_BOUND (DefrostDerate.from_dict._unit), candidate

Patch: `return 0.0 <= v <= 1.0  # observe_duty's gate; NaN fails it -> return 0.0 < v <= 1.0  # observe_duty's gate; NaN fails it`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `0.0 <= v` -> `0.0 < v` at defrost.py:537 the full gate stays green while every measured bucket at duty 0.0 (no defrost observed) restarts unmeasured: duty count 12 -> 0, and over an inferred 0.8 derate the published factor falls 1.0 -> 0.8571. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_4aac8e694ddc5dfe.py`: baseline duty0.0_restored_duty_count_baseline=12 count, mutant duty0.0_restored_duty_count_mutant=0 count; inputs tried: stored duties 0.0, 0.25, 0.5, 1.0; a zero-duty bucket over an inferred 0.8 derate. Should have failed: tests/finite_boundary.py / tests/boost_drift_replay.py / tests/features.py (traced baselines execute defrost.py:537): no round-trip check stores a measured bucket at duty 0.0 and asserts its duty count survives from_dict. Severity claimed high, class_guess I1.

### 5366f1e6254f603c: custom_components/heatpump_optimizer/defrost.py:392 CMP_BOUND (DefrostDerate.observe), candidate

Patch: `if delivered_ratio <= 0 or delivered_ratio > 3.0: -> if delivered_ratio < 0 or delivered_ratio > 3.0:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `delivered_ratio <= 0` -> `< 0` at defrost.py:392 the full gate stays green while a 0.0 ratio is folded as the deepest derate (count 0 -> 1; factor 1.0 -> 0.9775; a learned bucket's published factor 0.9286 -> 0.9115). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_5366f1e6254f603c.py`: baseline ratio0.0_count_baseline=0 count, mutant ratio0.0_count_mutant=1 count; inputs tried: delivered_ratio 0.0, 1e-9, 1.0, 2.999999, 3.0, 3.000001; a bucket learned to 0.8 over 6 samples. Should have failed: tests/features.py / tests/boost_drift_replay.py (traced baselines execute defrost.py:392): no observe check folds delivered_ratio 0.0 and asserts the bucket is untouched. Severity claimed low, class_guess I1.

### efb33eb6212be24e: custom_components/heatpump_optimizer/defrost.py:392 CMP_BOUND (DefrostDerate.observe), candidate

Patch: `if delivered_ratio <= 0 or delivered_ratio > 3.0: -> if delivered_ratio <= 0 or delivered_ratio >= 3.0:`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `delivered_ratio > 3.0` -> `>= 3.0` at defrost.py:392 the full gate stays green while a ratio of exactly 3.0 is dropped (count 1 -> 0; a learned bucket's published factor 0.9208 -> 0.9286). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_efb33eb6212be24e.py`: baseline ratio3.0_count_baseline=1 count, mutant ratio3.0_count_mutant=0 count; inputs tried: delivered_ratio 0.0, 1e-9, 1.0, 2.999999, 3.0, 3.000001; a bucket learned to 0.8 over 6 samples. Should have failed: tests/features.py / tests/boost_drift_replay.py (closure of defrost.py): no observe check folds delivered_ratio exactly 3.0 and asserts it is counted. Severity claimed low, class_guess I1.

### 0e3569fef6b39497: custom_components/heatpump_optimizer/defrost.py:434 CMP_BOUND (DefrostDerate.observe_duty), candidate

Patch: `and self.counts[t][h] > 0 -> and self.counts[t][h] >= 0`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

With `counts > 0` -> `>= 0` at defrost.py:434 the full gate stays green while a bucket with no inferred estimate logs a handover 'from the inferred estimate 1.000' (0 -> 1 records); learned state is unchanged. Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_0e3569fef6b39497.py`: baseline no_inferred_handover_logs_baseline=0 count, mutant no_inferred_handover_logs_mutant=1 count; inputs tried: a bucket with no inferred samples and one with 3, each folded 12 duties. Should have failed: tests/features.py (closure of defrost.py): no observe_duty check reaches DERATE_CONFIDENCE_SAMPLES in a bucket with no inferred samples and asserts no handover record. Severity claimed low, class_guess I1.

### fc4fe0f49de831a8: custom_components/heatpump_optimizer/defrost.py:142 CONST (<module>), equivalent-candidate

Patch: `DEFROST_DUTY_MAX = 0.30 -> DEFROST_DUTY_MAX = 0.6`. Gate: RED-AS-NULL, gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (= the null's).

Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_fc4fe0f49de831a8.py`: baseline points_differ=0 count, mutant max_abs_diff=0.0; inputs tried: derate_from_duty over duties 0..1 step 0.01 plus 0.299999, 0.300001, 0.3666667, 2.0, -0.1 (106); a bucket trusted at duty 0.5 (factor and summary). Should have failed: none can: derate_from_duty clamps its output at DERATE_MIN = 0.55, which equals 1 - 1.5 * DEFROST_DUTY_MAX exactly, so the duty cap binds nowhere the floor does not.

## Non-findings

- key fc4fe0f49de831a8 (custom_components/heatpump_optimizer/defrost.py:142 CONST, `DEFROST_DUTY_MAX = 0.30 -> DEFROST_DUTY_MAX = 0.6`): full gate RED-AS-NULL (gate_rc 1, no script beyond the null), and the probe finds no input that moves the delivered value: equivalent-candidate: `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key fc4fe0f49de831a8; PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_fc4fe0f49de831a8.py` -> gate RED-AS-NULL failed_scripts=['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (null: ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py']); probe points_differ=0 count vs max_abs_diff=0.0; inputs tried: derate_from_duty over duties 0..1 step 0.01 plus 0.299999, 0.300001, 0.3666667, 2.0, -0.1 (106); a bucket trusted at duty 0.5 (factor and summary)

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/gate_wave.sh`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_0e3569fef6b39497.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_1ba9abbe8e702464.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3b9eddc7ba9a7488.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3e3fbb5fcbbe9bcc.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_3e68dcd55f9567e5.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_4403a4c7bec83d8f.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_4aac8e694ddc5dfe.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_5366f1e6254f603c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_7ffebcb567a4242e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_845155d368e8b524.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_88ecd932bc81efec.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_89bec0a0291b4756.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_b028ad9d6c702965.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_d1197dfed14a6927.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_efb33eb6212be24e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_fc4fe0f49de831a8.py`

## Coverage

D3.M3 (this wave): universe 742, examined 16 here; every other key named by its box in REPORT.json. D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json.

## Exposure

No docs/ or GitHub record read. This seat resumed box D3-g12 from a stalled predecessor's checkpoint (handoff-wip/finder-r11-D3-g12 @ 40ef33e7): the probes, meta and record builder under probes/_scripts/ and the first six records are the predecessor's, restored by gate_wave.sh restore and kept unchanged. This seat read the box's own dispatch/inbox/wip refs, keys.tsv on the 47 sibling dispatch refs (key lists only, to name every other key by box), COMMON.md, D3.md, dev/audit/README.md, finding.schema.json and REPORT-D3-u1b/top6/rem.json (coverage rows) through haiku extractors. Environment workaround, not pushed: $HOME/venv-ci is a symlink to /opt/hpo/venv-ci, where this container's venv-ci lives.
