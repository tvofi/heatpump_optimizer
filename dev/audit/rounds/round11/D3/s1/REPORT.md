# D3-s1 wave box D3-g20: full gate for 16 D3.M3 full-net survivors

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Dimension D3, seat D3-s1, step D3.M3/D3.M4. findings: [] (ids assigned at consolidation).

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1094       13489          12        1801       14993
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.63
Sun Nov 22 21:40:15 UTC 2026
--- re-fire 2026-11-25T00:48:35Z (successor seat)
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087         755       14056          12        1547       15331
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.30GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.44
```

Null control `fullgate.py null` (dev/audit/rounds/round11/D3/s1/wave/D3-g20/gates/null.json): gate_rc 1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] (fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}), wall 3785.5 s (provisional). These are the stripped-tree artefact checks; a mutant counts as KILLED only with a script, or more FAIL lines in one, beyond them.
Gates 1-7 ran on the first seat's machine (Xeon @ 2.10GHz, where the null was taken); gates 8-16 on the successor's (Xeon @ 2.30GHz, nproc 4), the null restored from the checkpoint as gate_wave.sh does, not re-taken. Every wall/CPU/load number is provisional.

## Tally

gated 16/16: KILLED 2, RED-AS-NULL 14; KILLED by: aa338654e7801916 ['python3 tests/stress.py']; 0275af9776ae709e ['python3 tests/features.py']. Classes: candidates 8, equivalent-candidates 6, killed 2, timeout 0.

| key | site | verdict | class |
|---|---|---|---|
| a0722b8c635d2d93 | custom_components/heatpump_optimizer/optimizer.py:3402 CMP_BOUND | RED-AS-NULL | equivalent-candidate |
| d800d2857a698d22 | custom_components/heatpump_optimizer/optimizer.py:3405 CMP_BOUND | RED-AS-NULL | candidate |
| 176e4dd6d5aec097 | custom_components/heatpump_optimizer/optimizer.py:3408 CMP_BOUND | RED-AS-NULL | candidate |
| c40e66fc9831672f | custom_components/heatpump_optimizer/optimizer.py:6069 CLAMP_DROP | RED-AS-NULL | candidate |
| 7452dcf280ce931f | custom_components/heatpump_optimizer/optimizer.py:6070 CMP_BOUND | RED-AS-NULL | equivalent-candidate |
| aa338654e7801916 | custom_components/heatpump_optimizer/optimizer.py:6070 GUARD_OFF | KILLED | killed |
| 7add4cd79387ec24 | custom_components/heatpump_optimizer/optimizer.py:6091 CMP_BOUND | RED-AS-NULL | candidate |
| 72d1e72dd0acdfc1 | custom_components/heatpump_optimizer/optimizer.py:6093 GUARD_OFF | RED-AS-NULL | equivalent-candidate |
| bdb9a95deedcc8fe | custom_components/heatpump_optimizer/optimizer.py:6093 CMP_BOUND | RED-AS-NULL | equivalent-candidate |
| bf2229e3f179f4b6 | custom_components/heatpump_optimizer/optimizer.py:6097 CMP_BOUND | RED-AS-NULL | candidate |
| 19141bef62ecb4a6 | custom_components/heatpump_optimizer/optimizer.py:4766 CMP_BOUND | RED-AS-NULL | equivalent-candidate |
| 47430bf93e309e76 | custom_components/heatpump_optimizer/optimizer.py:4766 GUARD_OFF | RED-AS-NULL | candidate |
| 0275af9776ae709e | custom_components/heatpump_optimizer/optimizer.py:4802 GUARD_OFF | KILLED | killed |
| 9e71bd23e996ec6a | custom_components/heatpump_optimizer/optimizer.py:4828 CMP_BOUND | RED-AS-NULL | equivalent-candidate |
| 3652dbb5880d62c8 | custom_components/heatpump_optimizer/optimizer.py:3969 CMP_BOUND | RED-AS-NULL | candidate |
| b1926550efd8eac4 | custom_components/heatpump_optimizer/optimizer.py:3969 CMP_BOUND | RED-AS-NULL | candidate |

## Per key

### a0722b8c635d2d93 custom_components/heatpump_optimizer/optimizer.py:3402 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if end <= i: -> if end < i:` in `HeatPumpOptimizer._anticipatory_weights`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_a0722b8c635d2d93.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_a0722b8c635d2d93.py`), rc 0. Baseline: weights all 1.0 at dt>8 h. Mutant: weights all 1.0 (np.mean([])=nan, nan>0.5/1.1 False). Inputs tried: 450: dt {0.25,0.5,1,8,9,24} h x n {1,4,96} x solar {0,0.5,next(0.5),2,nan} x loss {1,1.1,next(1.1),2,nan}; moved 0.
Probe output: `RESULT inputs_tried=450 count`; `RESULT inputs_moved=0 count`; `RESULT tie_baseline_weight0=1.0`; `RESULT tie_mutant_weight0=1.0`; `RESULT null_delta=0`; `RESULT thread_factor=1.000`; `RESULT load1=0.85`; `RESULT swapins=0 count`
Should fail: none: no input separates the arms at the returned weights (executed by tests/block_duty, boost_drift_replay, config_flow_steps, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate.py).
Equivalent-candidate: a0722b8c635d2d93 (custom_components/heatpump_optimizer/optimizer.py:3402 CMP_BOUND) is an equivalent-candidate: end == i only when int(8/dt) == 0 (dt > 8 h); the empty window's mean is nan and both comparisons are False, so the weight is unchanged.

### d800d2857a698d22 custom_components/heatpump_optimizer/optimizer.py:3405 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if future_solar > 0.5:  # > 0.5 kW solar gain is significant -> if future_solar >= 0.5:  # > 0.5 kW solar gain is significant` in `HeatPumpOptimizer._anticipatory_weights`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_d800d2857a698d22.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_d800d2857a698d22.py`), rc 0. Baseline: weight[0]=1.0 at mean solar exactly 0.5 kW. Mutant: weight[0]=0.85. Inputs tried: 450-input grid (as a0722b8c); moved 60, every one at solar == 0.5.
Probe output: `RESULT inputs_tried=450 count`; `RESULT inputs_moved=60 count`; `RESULT tie_baseline_weight0=1.0`; `RESULT tie_mutant_weight0=0.85`; `RESULT first_moved_input='dt=0.25 n=1 solar=0.5 loss=1.0' baseline=1.0 mutant=0.85`; `RESULT null_delta=0`; `RESULT thread_factor=1.000`; `RESULT load1=0.75`; `RESULT swapins=0 count`
Should fail: tests/features.py (or any of tests/block_duty, boost_drift_replay, config_flow_steps, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate.py that executes line 3405) lacks an _anticipatory_weights check at solar gain exactly 0.5 kW asserting the weight is unchanged (1.0).
Candidate: **Anticipatory warm-start weight at exactly 0.5 kW solar is unpinned (> vs >=)**. HeatPumpOptimizer._anticipatory_weights returns weight 1.0 for a constant 0.5 kW solar window, and the full gate stays green when the comparison is made >=, which returns 0.85. class_guess I1, severity low; metric: weight[0] of _anticipatory_weights(n=4, dt=0.25, solar=0.5 const, loss=1.0 const); perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': '1.0 -> 0.85 (down) under the mutant'}; null control solar = loss = 2.0 constant: null_delta 0.

### 176e4dd6d5aec097 custom_components/heatpump_optimizer/optimizer.py:3408 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if future_loss > 1.1: -> if future_loss >= 1.1:` in `HeatPumpOptimizer._anticipatory_weights`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_176e4dd6d5aec097.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_176e4dd6d5aec097.py`), rc 0. Baseline: weight[0]=1.0 at mean loss factor exactly 1.1. Mutant: weight[0]=1.1. Inputs tried: 450-input grid (as a0722b8c); moved 70, every one at loss == 1.1.
Probe output: `RESULT inputs_tried=450 count`; `RESULT inputs_moved=70 count`; `RESULT tie_baseline_weight0=1.0`; `RESULT tie_mutant_weight0=1.1`; `RESULT first_moved_input='dt=0.25 n=1 solar=0.0 loss=1.1' baseline=1.0 mutant=1.1`; `RESULT null_delta=0`; `RESULT thread_factor=1.000`; `RESULT load1=0.86`; `RESULT swapins=0 count`
Should fail: tests/features.py (or any of tests/block_duty, boost_drift_replay, config_flow_steps, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate.py) lacks an _anticipatory_weights check at heat-loss factor exactly 1.1 asserting weight 1.0.
Candidate: **Anticipatory warm-start weight at a heat-loss factor of exactly 1.1 is unpinned (> vs >=)**. HeatPumpOptimizer._anticipatory_weights returns weight 1.0 for a constant 1.1 heat-loss factor window, and the full gate stays green when the comparison is made >=, which returns 1.1. class_guess I1, severity low; metric: weight[0] of _anticipatory_weights(n=4, dt=0.25, solar=0 const, loss=1.1 const); perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': '1.0 -> 1.1 (up) under the mutant'}; null control solar = loss = 2.0 constant: null_delta 0.

### c40e66fc9831672f custom_components/heatpump_optimizer/optimizer.py:6069 CLAMP_DROP (RED-AS-NULL, candidate)

Patch `lo = max(20.0, float(p.cop_flow_reference_temp)) -> lo = (20.0)` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_c40e66fc9831672f.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_c40e66fc9831672f.py`), rc 0. Baseline: ceiling 35.0 C (buffer_max 70, out_mean -20 C, defaults). Mutant: ceiling 20.0 C. Inputs tried: 117: buffer_max {30,35,40,55,70,90} x out_mean {15,0,-10,-15,-20,-30} x buffer_cooling_rate {default,0,2.0} + 9 constructed exact ties net(hi|lo|mid)==0; moved 45 (every cold case where net(35 C) <= 0); max |delta| 15 C.
Probe output: `RESULT inputs_tried=117 count (ties constructed: 9)`; `RESULT inputs_moved=45 count`; `RESULT moved hi=30.0 out=-20.0 ua=None: baseline=30.0 mutant=20.0`; `RESULT moved hi=30.0 out=-20.0 ua=0.0: baseline=30.0 mutant=20.0`; `RESULT moved hi=30.0 out=-20.0 ua=2.0: baseline=30.0 mutant=20.0`; `RESULT moved hi=30.0 out=-30.0 ua=None: baseline=30.0 mutant=20.0`; `RESULT max_abs_delta_c=15.0`; `RESULT focus hi=70.0 out=-20.0 ua=None: baseline=35.0 mutant=20.0`; `RESULT null_delta=0 C`; `RESULT from_config_buffer_max_30=30.0`; `RESULT thread_factor=1.000`; `RESULT load1=0.96`; `RESULT swapins=0 count`
Should fail: tests/features.py (its traced baseline reaches line 6093's `return lo`, the only script that does) lacks an assertion that a cold-weather _buffer_charge_ceiling never falls below the 35 C flow reference (cop_flow_reference_temp): heat below the reference is always chargeable.
Candidate: **Buffer charge ceiling's floor at the COP flow reference is unpinned: dropping it lowers the cold-weather ceiling 35 -> 20 C**. With max(20, cop_flow_reference_temp) replaced by 20, HeatPumpOptimizer._buffer_charge_ceiling at out_mean -20 C returns 20.0 C instead of 35.0 C (45 of 117 probe inputs move), and the GATE_SCOPE=full GOLDEN_MODE=drift gate stays green. class_guess I1, severity medium; metric: the value _buffer_charge_ceiling(out_mean) returns, C, default parameters, buffer_max_temp 70 C, out_mean -20 C; perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': '35.0 -> 20.0 C (down) under the mutant'}; null control out_mean 15 C (net(hi) > 0, returns buffer_max_temp on both arms): null_delta 0 C.

### 7452dcf280ce931f custom_components/heatpump_optimizer/optimizer.py:6070 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if hi <= lo: -> if hi < lo:` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_7452dcf280ce931f.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_7452dcf280ce931f.py`), rc 0. Baseline: ceiling == buffer_max_temp when hi == lo (35 C). Mutant: same value via net(hi)>0 -> hi, else net(lo)<=0 -> lo == hi. Inputs tried: 117 (grid incl. buffer_max 35 C at every out_mean, + 9 exact ties); moved 0.
Probe output: `RESULT inputs_tried=117 count (ties constructed: 9)`; `RESULT inputs_moved=0 count`; `RESULT focus hi=35.0 out=-30.0 ua=None: baseline=35.0 mutant=35.0`; `RESULT null_delta=0 C`; `RESULT from_config_buffer_max_30=30.0`; `RESULT thread_factor=1.000`; `RESULT load1=0.84`; `RESULT swapins=0 count`
Should fail: none (executed by tests/env_drift, features, validate.py).
Equivalent-candidate: 7452dcf280ce931f (custom_components/heatpump_optimizer/optimizer.py:6070 CMP_BOUND) is an equivalent-candidate: at hi == lo every remaining return path yields hi (== lo).

### aa338654e7801916 custom_components/heatpump_optimizer/optimizer.py:6070 GUARD_OFF (KILLED, killed)

Patch `if hi <= lo: -> if False:` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Killed by ['python3 tests/stress.py']:   FAIL a refused merge surfaces merge()'s reason, not just skip-merge-failed  [status='skip-not-under-scoped' log=''];   FAIL and a merge that succeeds carries no merge reason (null control)  [status='skip-not-under-scoped' log='']; >>> FAILED: python3 tests/closure.py selftest;   FAIL a3:roster  [1 registered, 82 in the committed collect() roster; missing=['binary_sensor.heat_pump_optimizer_away_mode', 'binary_sensor.heat_pump_optimizer_external_heat_source', 'binary_sensor.heat_pump_optimizer_input_problem', 'binary_sensor.heat_pump_optimizer_mold_floor_breach', 'binary_s;   FAIL a3:orjson  [1 failed HA json_bytes; first: ['sensor.x:ValueError:orjson rejects non-finite floats']]

Note: The only check beyond the null is tests/stress.py's timing-ratio check 'the per-call-cost arm reaches the rule ...': its unchanged-solve arm read x0.80 (31 ms vs 39 ms plain). The mutant changes _buffer_charge_ceiling only when buffer_max_temp < 35 C (probe below), a rating no stress.py building uses at the 40..90 C flow range, so the kill is provisional and timing-suspect: wall 3798.3 s, load1 0.85->0.85, nproc 4. Recorded KILLED as fullgate.py decides; the judge's quiet re-take settles it.

### 7add4cd79387ec24 custom_components/heatpump_optimizer/optimizer.py:6091 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if net(hi) > 0.0: -> if net(hi) >= 0.0:` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_7add4cd79387ec24.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_7add4cd79387ec24.py`), rc 0. Baseline: ceiling 54.99999999534339 C at a constructed exact tie net(55 C) == 0.0. Mutant: ceiling 55.0 C. Inputs tried: 117 (as c40e66fc); moved 3, exactly the 3 constructed net(hi)==0.0 ties (buffer_max 55/70/90 C, out_mean ~-19.7 C, internal_gains and buffer_cooling_rate walked by ulps); max |delta| 1.28e-8 C.
Probe output: `RESULT inputs_tried=117 count (ties constructed: 9)`; `RESULT inputs_moved=3 count`; `RESULT moved tie net(hi)==0 hi=55.0 out=-19.685103302977925: baseline=54.99999999534339 mutant=55.0`; `RESULT moved tie net(hi)==0 hi=70.0 out=-19.668688609117403: baseline=69.99999999185093 mutant=70.0`; `RESULT moved tie net(hi)==0 hi=90.0 out=-19.646802350636705: baseline=89.99999998719431 mutant=90.0`; `RESULT max_abs_delta_c=1.280568540096283e-08`; `RESULT focus tie net(hi)==0 hi=55.0 out=-19.685103302977925: baseline=54.99999999534339 mutant=55.0`; `RESULT null_delta=0 C`; `RESULT from_config_buffer_max_30=30.0`; `RESULT thread_factor=1.000`; `RESULT load1=0.82`; `RESULT swapins=1 count`
Should fail: tests/features.py / tests/validate.py (execute line 6091) have no input with net(hi) exactly 0.0; a pin would need a constructed float tie.
Candidate: **Buffer charge ceiling's net(hi) > 0 boundary is unpinned (moves 1e-8 C at an exact float tie)**. At a constructed exact tie net(buffer_max_temp) == 0.0, HeatPumpOptimizer._buffer_charge_ceiling returns hi - 4.7e-9 C, and returns exactly hi under the >= mutant, which the full gate does not detect. class_guess I1, severity low; metric: the value _buffer_charge_ceiling returns at the constructed net(hi)==0.0 tie, C; perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': 'up by (hi-lo)/2**32 (~1e-8 C) under the mutant'}; null control out_mean 15 C: null_delta 0 C.

### 72d1e72dd0acdfc1 custom_components/heatpump_optimizer/optimizer.py:6093 GUARD_OFF (RED-AS-NULL, equivalent-candidate)

Patch `if net(lo) <= 0.0: -> if False:` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_72d1e72dd0acdfc1.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_72d1e72dd0acdfc1.py`), rc 0. Baseline: ceiling == lo (35 C) when net(lo) <= 0. Mutant: bisection moves only hi; returns lo == 35 C. Inputs tried: 117 (as c40e66fc); moved 0.
Probe output: `RESULT inputs_tried=117 count (ties constructed: 9)`; `RESULT inputs_moved=0 count`; `RESULT focus hi=70.0 out=-30.0 ua=None: baseline=35.0 mutant=35.0`; `RESULT null_delta=0 C`; `RESULT from_config_buffer_max_30=30.0`; `RESULT thread_factor=1.000`; `RESULT load1=0.94`; `RESULT swapins=0 count`
Should fail: none (executed by tests/features.py).
Equivalent-candidate: 72d1e72dd0acdfc1 (custom_components/heatpump_optimizer/optimizer.py:6093 GUARD_OFF) is an equivalent-candidate: with net(lo) <= 0 and net decreasing every net(mid) <= 0, so only hi moves and the loop returns lo unchanged.

### bdb9a95deedcc8fe custom_components/heatpump_optimizer/optimizer.py:6093 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if net(lo) <= 0.0: -> if net(lo) < 0.0:` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bdb9a95deedcc8fe.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bdb9a95deedcc8fe.py`), rc 0. Baseline: ceiling 35.0 C at a constructed exact tie net(35 C) == 0.0. Mutant: 35.0 C. Inputs tried: 117 (as c40e66fc, incl. 3 exact net(lo)==0.0 ties); moved 0.
Probe output: `RESULT inputs_tried=117 count (ties constructed: 9)`; `RESULT inputs_moved=0 count`; `RESULT focus tie net(lo)==0 hi=55.0 out=-19.70698956145862: baseline=35.0 mutant=35.0`; `RESULT null_delta=0 C`; `RESULT from_config_buffer_max_30=30.0`; `RESULT thread_factor=1.000`; `RESULT load1=0.90`; `RESULT swapins=0 count`
Should fail: none (executed by tests/features.py).
Equivalent-candidate: bdb9a95deedcc8fe (custom_components/heatpump_optimizer/optimizer.py:6093 CMP_BOUND) is an equivalent-candidate: at net(lo) == 0.0 the mutant bisects, every net(mid) < 0, and the loop returns lo unchanged.

### bf2229e3f179f4b6 custom_components/heatpump_optimizer/optimizer.py:6097 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if net(mid) > 0.0: -> if net(mid) >= 0.0:` in `HeatPumpOptimizer._buffer_charge_ceiling`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bf2229e3f179f4b6.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bf2229e3f179f4b6.py`), rc 0. Baseline: ceiling 44.99999999534339 C at a constructed exact tie net(45 C) == 0.0 (first midpoint, buffer_max 55). Mutant: 45.0 C. Inputs tried: 117 (as c40e66fc); moved 3, exactly the 3 constructed net(mid)==0.0 ties; max |delta| 1.28e-8 C.
Probe output: `RESULT inputs_tried=117 count (ties constructed: 9)`; `RESULT inputs_moved=3 count`; `RESULT moved tie net(mid)==0 hi=55.0 out=-19.696046432218274: baseline=44.99999999534339 mutant=45.0`; `RESULT moved tie net(mid)==0 hi=70.0 out=-19.68783908528801: baseline=52.49999999185093 mutant=52.5`; `RESULT moved tie net(mid)==0 hi=90.0 out=-19.676895956047666: baseline=62.499999987194315 mutant=62.5`; `RESULT max_abs_delta_c=1.280568540096283e-08`; `RESULT focus tie net(mid)==0 hi=55.0 out=-19.696046432218274: baseline=44.99999999534339 mutant=45.0`; `RESULT null_delta=0 C`; `RESULT from_config_buffer_max_30=30.0`; `RESULT thread_factor=1.000`; `RESULT load1=0.78`; `RESULT swapins=0 count`
Should fail: tests/features.py (the only script reaching line 6097) has no input whose bisection midpoint is an exact root.
Candidate: **Buffer charge ceiling's bisection comparison net(mid) > 0 is unpinned (moves 1e-8 C at an exact float tie)**. At a constructed exact root at the first bisection midpoint, HeatPumpOptimizer._buffer_charge_ceiling returns mid - 4.7e-9 C, and exactly mid under the >= mutant, which the full gate does not detect. class_guess I1, severity low; metric: the value _buffer_charge_ceiling returns at the constructed net(mid)==0.0 tie, C; perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': 'up by ~1e-8 C under the mutant'}; null control out_mean 15 C: null_delta 0 C.

### 19141bef62ecb4a6 custom_components/heatpump_optimizer/optimizer.py:4766 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if f.size < n_steps: -> if f.size <= n_steps:` in `HeatPumpOptimizer._build_comfort_bounds`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_19141bef62ecb4a6.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_19141bef62ecb4a6.py`), rc 0. Baseline: identical bounds for every array input. Mutant: identical; a 0-d floor raises on both arms (IndexError vs ValueError). Inputs tried: 66: n {1,4,96} x floors.size {0,1,n-1,n,n+1,2n} x fill {18,25,nan,-inf} + 0-d floor + short list with margins; moved 1, beyond exception type 0.
Probe output: `RESULT inputs_tried=66 count`; `RESULT inputs_moved=1 count`; `RESULT inputs_moved_beyond_exception_type=0 count (rows where both arms raise, differing only in the exception type: 1)`; `RESULT moved n=1 floors=0-d 18.0: baseline=raises IndexError mutant=raises ValueError`; `RESULT null_delta=0 count (n=96 floors=None margins=None)`; `RESULT thread_factor=1.000`; `RESULT load1=0.86`; `RESULT swapins=0 count`
Should fail: none (executed by tests/entities, env_drift, features.py).
Equivalent-candidate: 19141bef62ecb4a6 (custom_components/heatpump_optimizer/optimizer.py:4766 CMP_BOUND) is an equivalent-candidate: at f.size == n_steps the mutant concatenates an empty pad (a no-op); the only other moved input raises on both arms.

### 47430bf93e309e76 custom_components/heatpump_optimizer/optimizer.py:4766 GUARD_OFF (RED-AS-NULL, candidate)

Patch `if f.size < n_steps: -> if False:` in `HeatPumpOptimizer._build_comfort_bounds`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_47430bf93e309e76.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_47430bf93e309e76.py`), rc 0. Baseline: min bounds shape (n,) with the short mold-floor series padded by -inf. Mutant: min bounds shape (0,) for an empty series (silent), ValueError for 2..n-1 floors, the one floor broadcast over all n steps for a single floor. Inputs tried: 66 (as 19141bef); moved 33.
Probe output: `RESULT inputs_tried=66 count`; `RESULT inputs_moved=33 count`; `RESULT inputs_moved_beyond_exception_type=31 count (rows where both arms raise, differing only in the exception type: 2)`; `RESULT moved n=1 floors.size=0 fill=18.0: baseline=(shape(1,) first=[19.5], shape(1,) first=[16.5], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(1,) first=[-inf])) mutant=(shape(1,) first=[19.5], shape(0,) first=[], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(0,) first=[]))`; `RESULT moved n=1 floors.size=0 fill=25.0: baseline=(shape(1,) first=[19.5], shape(1,) first=[16.5], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(1,) first=[-inf])) mutant=(shape(1,) first=[19.5], shape(0,) first=[], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(0,) first=[]))`; `RESULT moved n=1 floors.size=0 fill=nan: baseline=(shape(1,) first=[19.5], shape(1,) first=[16.5], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(1,) first=[-inf])) mutant=(shape(1,) first=[19.5], shape(0,) first=[], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(0,) first=[]))`; `RESULT moved n=1 floors.size=0 fill=-inf: baseline=(shape(1,) first=[19.5], shape(1,) first=[16.5], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(1,) first=[-inf])) mutant=(shape(1,) first=[19.5], shape(0,) first=[], shape(1,) first=[23.0], (shape(1,) first=[16.5], shape(0,) first=[]))`; `RESULT moved n=1 floors=list[18.0]*0 margins=0.5: baseline=(shape(1,) first=[19.5], shape(1,) first=[17.0], shape(1,) first=[23.0], (shape(1,) first=[17.0], shape(1,) first=[-inf])) mutant=(shape(1,) first=[19.5], shape(0,) first=[], shape(1,) first=[23.0], (shape(1,) first=[17.0], shape(0,) first=[]))`; `RESULT null_delta=0 count (n=96 floors=None margins=None)`; `RESULT thread_factor=1.000`; `RESULT load1=1.02`; `RESULT swapins=0 count`
Should fail: tests/features.py / tests/entities.py / tests/env_drift.py (execute line 4766) never pass min_temp_floors shorter than n_steps; lacks a padding assertion (short floors -> trailing -inf, bounds shape (n,)).
Candidate: **Mold-floor padding in _build_comfort_bounds is unpinned: without it a short floor series silently empties or mis-broadcasts the comfort band**. With the `f.size < n_steps` padding disabled, HeatPumpOptimizer._build_comfort_bounds returns a (0,)-shaped minimum-bound array for an empty mold-floor series and raises ValueError for a series of 2..n-1 floors (33 of 66 probe inputs move), and the full gate stays green. class_guess I1, severity low; metric: the (targets, min, max, (comfort floors, mold floors)) tuple _build_comfort_bounds returns, compared by shape and value; perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': 'shape (n,) -> (0,) / ValueError under the mutant'}; null control min_temp_floors None (branch not entered): null_delta 0.

### 0275af9776ae709e custom_components/heatpump_optimizer/optimizer.py:4802 GUARD_OFF (KILLED, killed)

Patch `if space_blocked: -> if False:` in `HeatPumpOptimizer._build_space_power_caps`.
Killed by ['python3 tests/features.py']:   FAIL a refused merge surfaces merge()'s reason, not just skip-merge-failed  [status='skip-not-under-scoped' log=''];   FAIL and a merge that succeeds carries no merge reason (null control)  [status='skip-not-under-scoped' log='']; >>> FAILED: python3 tests/closure.py selftest;   FAIL a mode that cannot heat rooms plans no space heating at all;   FAIL every empty space slot says WHY, instead of reading as 'idle'  [['cheap_price', 'pump_mode']]

### 9e71bd23e996ec6a custom_components/heatpump_optimizer/optimizer.py:4828 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if extra.size < n_steps: -> if extra.size <= n_steps:` in `HeatPumpOptimizer._build_space_power_caps`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_9e71bd23e996ec6a.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_9e71bd23e996ec6a.py`), rc 0. Baseline: identical caps for every array input. Mutant: identical; a 0-d extra cap raises on both arms (IndexError vs ValueError). Inputs tried: 264 (as 0275af97); moved 4, beyond exception type 0.
Probe output: `RESULT inputs_tried=264 count`; `RESULT inputs_moved=4 count`; `RESULT inputs_moved_beyond_exception_type=0 count (rows where both arms raise, differing only in the exception type: 4)`; `RESULT moved n=1 extra=0-d 2.5 blocked=False: baseline=raises IndexError mutant=raises ValueError`; `RESULT moved n=1 extra=0-d 2.5 blocked=False: baseline=raises IndexError mutant=raises ValueError`; `RESULT moved n=1 extra=0-d 2.5 blocked=True: baseline=raises IndexError mutant=raises ValueError`; `RESULT moved n=1 extra=0-d 2.5 blocked=True: baseline=raises IndexError mutant=raises ValueError`; `RESULT null_delta=0 count (n=96 extra=None blocked=False off=None)`; `RESULT thread_factor=1.000`; `RESULT load1=0.87`; `RESULT swapins=0 count`
Should fail: none (executed by tests/env_drift, features.py).
Equivalent-candidate: 9e71bd23e996ec6a (custom_components/heatpump_optimizer/optimizer.py:4828 CMP_BOUND) is an equivalent-candidate: at extra.size == n_steps the mutant concatenates an empty pad (a no-op).

### 3652dbb5880d62c8 custom_components/heatpump_optimizer/optimizer.py:3969 CMP_BOUND (RED-AS-NULL, candidate)

Patch `pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3) -> pinned = (dhw_power > 1e-6) & (space_power > headroom - 1e-3)` in `HeatPumpOptimizer._co_optimize`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_3652dbb5880d62c8.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_3652dbb5880d62c8.py`), rc 0. Baseline: (replanned, 1 pinned step) at space == headroom - 1e-3 exactly, dhw 1.0 kW. Mutant: (ok, 0): the DHW re-plan is skipped. Inputs tried: 42: dhw {0,1e-6,next/prev(1e-6),1,4,5} kW x space {head-2e-3, head-1e-3 (tie), prev/next of the tie, head, 0}; moved 4, exactly the tie rows with dhw > 1e-6.
Probe output: `RESULT inputs_tried=42 count`; `RESULT inputs_moved=4 count`; `RESULT moved dhw=1.0000000000000002e-06 space=tie head-1e-3 (4.9989989999999995): baseline(status,pinned)=('replanned', 1) mutant=('ok', 0)`; `RESULT moved dhw=1.0 space=tie head-1e-3 (3.999): baseline(status,pinned)=('replanned', 1) mutant=('ok', 0)`; `RESULT moved dhw=4.0 space=tie head-1e-3 (0.999): baseline(status,pinned)=('replanned', 1) mutant=('ok', 0)`; `RESULT moved dhw=5.0 space=tie head-1e-3 (-0.001): baseline(status,pinned)=('replanned', 1) mutant=('ok', 0)`; `RESULT focus dhw=1.0 space=tie head-1e-3 (3.999): baseline(status,pinned)=('replanned', 1) mutant=('ok', 0)`; `RESULT null_delta=0 count (dhw=1.0 space=1.0: far from both edges)`; `RESULT thread_factor=1.000`; `RESULT load1=0.87`; `RESULT swapins=0 count`
Should fail: tests/features.py (one of tests/block_duty, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate.py) has no co-optimize case with space power at exactly headroom - 1e-3.
Candidate: **DHW co-optimize pin test `space >= headroom - 1e-3` is unpinned at its tolerance edge**. With >= made >, HeatPumpOptimizer._co_optimize no longer pins a step whose space power is exactly headroom - 1e-3 and skips the DHW re-plan (status replanned -> ok), and the full gate stays green. class_guess I1, severity low; metric: (status, pinned steps handed to the DHW re-plan) from _co_optimize on a one-step input, recording planner stand-in; perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': '(replanned, 1) -> (ok, 0) under the mutant'}; null control dhw 1.0, space 1.0: null_delta 0.

### b1926550efd8eac4 custom_components/heatpump_optimizer/optimizer.py:3969 CMP_BOUND (RED-AS-NULL, candidate)

Patch `pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3) -> pinned = (dhw_power >= 1e-6) & (space_power >= headroom - 1e-3)` in `HeatPumpOptimizer._co_optimize`.
Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_b1926550efd8eac4.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_b1926550efd8eac4.py`), rc 0. Baseline: (ok, 0) at dhw exactly 1e-6 kW with space at its headroom. Mutant: (replanned, 1): the step is pinned and the DHW re-plan runs. Inputs tried: 42 (as 3652dbb5); moved 3, exactly the dhw == 1e-6 rows with space >= headroom - 1e-3.
Probe output: `RESULT inputs_tried=42 count`; `RESULT inputs_moved=3 count`; `RESULT moved dhw=1e-06 space=tie head-1e-3 (4.9989989999999995): baseline(status,pinned)=('ok', 0) mutant=('replanned', 1)`; `RESULT moved dhw=1e-06 space=above tie (4.998999): baseline(status,pinned)=('ok', 0) mutant=('replanned', 1)`; `RESULT moved dhw=1e-06 space=head (4.999999): baseline(status,pinned)=('ok', 0) mutant=('replanned', 1)`; `RESULT focus dhw=1e-06 space=head (4.999999): baseline(status,pinned)=('ok', 0) mutant=('replanned', 1)`; `RESULT null_delta=0 count (dhw=1.0 space=1.0: far from both edges)`; `RESULT thread_factor=1.000`; `RESULT load1=0.80`; `RESULT swapins=0 count`
Should fail: tests/features.py (one of tests/block_duty, doc_claims, entities, env_drift, features, manual_plan, optimality, plan_view, validate.py) has no co-optimize case with hot-water power exactly 1e-6 kW.
Candidate: **DHW co-optimize pin test `dhw > 1e-6` is unpinned at its threshold**. With > made >=, HeatPumpOptimizer._co_optimize pins a step with hot-water power exactly 1e-6 kW and runs the DHW re-plan (status ok -> replanned), and the full gate stays green. class_guess I1, severity low; metric: (status, pinned steps handed to the DHW re-plan) from _co_optimize on a one-step input, recording planner stand-in; perturbation {'change': "the key's one-line mutant, applied in memory by the probe", 'expected_direction': '(ok, 0) -> (replanned, 1) under the mutant'}; null control dhw 1.0, space 1.0: null_delta 0.

## Unfinished

- none

## Harnesses

- dev/audit/rounds/round11/D3/s1/fullgate.py
- gate_wave.sh (out-of-tree driver on ref dispatch/finder-r11-D3-g20 tip c1223708: null/run/ckpt/restore; one gate at a time, 4 h cap)
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/tools/mkresult.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/tools/mkres.sh
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/tools/mkreport.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_arrays.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_bounds_cases.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_caps_cases.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_ceiling.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_coopt.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_mutant.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/_weights.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_0275af9776ae709e.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_176e4dd6d5aec097.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_19141bef62ecb4a6.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_3652dbb5880d62c8.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_47430bf93e309e76.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_72d1e72dd0acdfc1.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_7452dcf280ce931f.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_7add4cd79387ec24.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_9e71bd23e996ec6a.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_a0722b8c635d2d93.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_aa338654e7801916.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_b1926550efd8eac4.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bdb9a95deedcc8fe.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_bf2229e3f179f4b6.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_c40e66fc9831672f.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g20/probes/probe_d800d2857a698d22.py

## Exposure

Box D3-g20 (two seats: the first stalled after 7 gates, this successor resumed from its checkpoint on ref handoff-wip/finder-r11-D3-g20 @ 855a9a2f). Read COMMON.md, D3.md, dev/audit/README.md, the u1 slice reports and m4 answers, REPORT-D3-top6/rem, finding.schema.json, the carried harnesses and state in dev/audit/rounds/round11/D3/s1/, the 16 production lines of keys.tsv, and the other wave boxes' keys.tsv on their dispatch refs (to name not_reached). No docs/, register, round11/J/, verifier report or GitHub record was read.
