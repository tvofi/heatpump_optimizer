# D3-s1 wave box D3-g07: full gate of 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Every wall, CPU and load number is provisional: true (the judge re-takes it).

## Machine and controls

```
date: 2026-11-22T21:38:54Z
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1057       13526          12        1800       15029
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.66
python3: /opt/hpo/venv-ci/bin/python3 (symlinked at $HOME/venv-ci)
--- re-fire 2026-11-25T00:46:59Z
4
               total        used        free      shared  buff/cache   available
Mem:           16087         738       14079          12        1540       15348
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
0.62
```

Null control (`fullgate.py null`, comment-only marker in tariff.py): gate_rc 1, red scripts python3 tests/closure.py selftest, python3 tests/entities.py, python3 tests/harness_headers.py, fail lines {"python3 tests/closure.py selftest": 2, "python3 tests/entities.py": 1, "python3 tests/harness_headers.py": 3}, wall 4006.9 s. All three are artefact checks that read no production cell file (gates/null-note.txt); a mutant is KILLED only by a script beyond the null or more failing checks in one.

## Tally

Gated 16 of 16: RED-AS-NULL 16. Candidates 12, equivalent-candidates 4, timeouts 0. findings: [] (ids are assigned by the orchestrator's consolidation step).

| key | site | verdict | killed_by | class |
|---|---|---|---|---|
| d3cad40ffce9b765 | custom_components/heatpump_optimizer/coordinator.py:9402 CMP_BOUND | RED-AS-NULL | - | candidate |
| e163f6fbc359cd4c | custom_components/heatpump_optimizer/coordinator.py:9402 CMP_BOUND | RED-AS-NULL | - | candidate |
| 67495f7b404053fc | custom_components/heatpump_optimizer/coordinator.py:7477 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| f0146f6f4901ec82 | custom_components/heatpump_optimizer/coordinator.py:7491 GUARD_OFF | RED-AS-NULL | - | candidate |
| 5f950692fab8eb1b | custom_components/heatpump_optimizer/coordinator.py:7492 CLAMP_DROP | RED-AS-NULL | - | equivalent-candidate |
| 4410da4e8eb84cb8 | custom_components/heatpump_optimizer/coordinator.py:8838 BOOLOP | RED-AS-NULL | - | candidate |
| 7ec91efc2c6deffd | custom_components/heatpump_optimizer/coordinator.py:8838 CMP_BOUND | RED-AS-NULL | - | candidate |
| f11665aaedbf2550 | custom_components/heatpump_optimizer/coordinator.py:8838 GUARD_OFF | RED-AS-NULL | - | candidate |
| 9b72b944ac12fa25 | custom_components/heatpump_optimizer/coordinator.py:8842 GUARD_OFF | RED-AS-NULL | - | candidate |
| fd1cc23d380739ba | custom_components/heatpump_optimizer/coordinator.py:8847 CMP_BOUND | RED-AS-NULL | - | candidate |
| c20f346300d7efc1 | custom_components/heatpump_optimizer/coordinator.py:9292 BOOLOP | RED-AS-NULL | - | candidate |
| 60f673da42f9d671 | custom_components/heatpump_optimizer/coordinator.py:9294 CMP_BOUND | RED-AS-NULL | - | candidate |
| 661116d11d6faa49 | custom_components/heatpump_optimizer/coordinator.py:9170 GUARD_OFF | RED-AS-NULL | - | equivalent-candidate |
| b6ac2d53028d45a3 | custom_components/heatpump_optimizer/coordinator.py:5049 GUARD_OFF | RED-AS-NULL | - | candidate |
| 7f2768bd0a78b4bf | custom_components/heatpump_optimizer/coordinator.py:5103 CLAMP_DROP | RED-AS-NULL | - | equivalent-candidate |
| 1ee0ec8960fb9a66 | custom_components/heatpump_optimizer/coordinator.py:5104 GUARD_OFF | RED-AS-NULL | - | candidate |

## Re-take of 7ec91efc2c6deffd

Key 7ec91efc2c6deffd, gate try 1 (2026-11-25 01:14-02:16 UTC): verdict KILLED by python3 tests/entities.py only,
3 of 2723 vs the null's 1. Diff of the entities.py FAIL lines against RED-AS-NULL key 4410da4e8eb84cb8's gate: the two
extra checks are hb:positive_control's retry/null-control pair ("a 600 ms spin read as 1008.2 ms / 875.8 ms; sampler
rc=0 names it: False"): the py-spy heartbeat sampler's wall-time positive control, which reads no production line.
This try started 2 min after a container restart and the box's cleanup of the interrupted try 0 (tree reset to the
baseline, stale gate_lock lease released), so it ran on a disturbed machine. The machine named the script red, not the
mutant: per the brief's re-take rule the key is re-gated once after the wave's last key; the re-take's verdict stands.
Try 0 (00:47-~01:10 UTC) was cut by the container restart and left no verdict.
Re-take (2026-11-25 11:24 UTC): verdict RED-AS-NULL, gate_rc 1, fail lines {"python3 tests/closure.py selftest": 2, "python3 tests/entities.py": 1, "python3 tests/harness_headers.py": 3} (null {"python3 tests/closure.py selftest": 2, "python3 tests/entities.py": 1, "python3 tests/harness_headers.py": 3}), wall 3958.7 s, load1 0.72..1.0 (provisional). The re-take stands; try 1 is kept as evidence only.

## Survivors: the step-4 answer per key

### d3cad40ffce9b765 custom_components/heatpump_optimizer/coordinator.py:9402 CMP_BOUND (candidate)

Patch `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6: -> if m["n"] > SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:` in HeatPumpOptimizerCoordinator._fold_solar_aperture. Gate RED-AS-NULL (wall 3794.3 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_d3cad40ffce9b765.py`: scale_baseline_at_min=2.000000 on the baseline, scale_mutant_at_min=1.000000 under the mutant. Inputs: 30 sunny folds, irradiance 200..780 W/m2 in 20 W/m2 steps, residual = 1.5x modelled solar gain; null 29 folds; 31 folds (both arms move). Traced reach: tests/features.py. Should fail: tests/features.py (the only closure script whose traced baseline executes coordinator.py:9402) has no check that the solar-aperture scale moves off 1.0 on exactly the SOLAR_APERTURE_MIN_SAMPLES-th varying sunny fold Finding candidate: No check pins the solar-aperture learner's first correction at exactly SOLAR_APERTURE_MIN_SAMPLES folds (severity low, class I1).

### e163f6fbc359cd4c custom_components/heatpump_optimizer/coordinator.py:9402 CMP_BOUND (candidate)

Patch `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6: -> if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] >= 1e-6:` in HeatPumpOptimizerCoordinator._fold_solar_aperture. Gate RED-AS-NULL (wall 3807.4 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_e163f6fbc359cd4c.py`: scale_baseline_tie=1.000000 on the baseline, scale_mutant_tie=2.000000 under the mutant. Inputs: moment state n=100, cov=2e-6, x == mx, start variance searched over representable floats until v - a*v == 1e-6 exactly (found); null: variance one float above the tie; 36 realistic fold sequences (31/60/200 folds x irradiance ramps 150/300/600 W/m2 x 5/20 W/m2 steps x residual ratio 0.6/1.5): 0 differ. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:9402) has no check of the `var > 1e-6` guard at its exact tie; the tie is a float-equality event the probe could only reach by constructing the moment state, never by a realistic fold sequence (0 of 36 differ) Finding candidate: No check pins the solar-aperture variance guard at its exact 1e-6 tie (severity low, class I1).

### f0146f6f4901ec82 custom_components/heatpump_optimizer/coordinator.py:7491 GUARD_OFF (candidate)

Patch `if rh is not None: -> if False:` in HeatPumpOptimizerCoordinator._forecast_arrays. Gate RED-AS-NULL (wall 3813.1 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_f0146f6f4901ec82.py`: humidity_mean_baseline=95.0 on the baseline, humidity_mean_mutant=85.0 under the mutant. Inputs: weather entity 85 % for 48 h, Open-Meteo hourly relative_humidity_2m 95 % for 72 h built by the production _parse_block, clock frozen at golden.START in UTC; null: Open-Meteo 85 %. Traced reach: tests/entities.py, tests/solar_alignment.py. Should fail: tests/entities.py and tests/solar_alignment.py execute coordinator.py:7491 on the traced baseline, yet neither asserts that ForecastArrays.humidity carries Open-Meteo's humidity where the client has it Finding candidate: No check pins Open-Meteo's humidity overlay onto the forecast horizon (severity medium, class I1).

### 4410da4e8eb84cb8 custom_components/heatpump_optimizer/coordinator.py:8838 BOOLOP (candidate)

Patch `if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp: -> if params.dhw_enabled or state.dhw_temperature < params.dhw_min_temp:` in HeatPumpOptimizerCoordinator._guard_floor_hold. Gate RED-AS-NULL (wall 3867.5 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_4410da4e8eb84cb8.py`: hold_baseline=None on the baseline, hold_mutant=None under the mutant. Inputs: dhw_enabled False, dhw_temperature 40 C < dhw_min_temp 45 C, room 21 C, floor 17 C; null: dhw 55 C. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:8838) has no _guard_floor_hold check with hot water disabled and a low tank reading asserting False Finding candidate: No check pins _guard_floor_hold's hot-water arm to installs with hot water enabled (severity low, class I1).

### 7ec91efc2c6deffd custom_components/heatpump_optimizer/coordinator.py:8838 CMP_BOUND (candidate)

Patch `if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp: -> if params.dhw_enabled and state.dhw_temperature <= params.dhw_min_temp:` in HeatPumpOptimizerCoordinator._guard_floor_hold. Gate RED-AS-NULL (wall 3958.7 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_7ec91efc2c6deffd.py`: hold_baseline=0 on the baseline, hold_mutant=1 under the mutant. Inputs: dhw_enabled True, dhw_temperature == dhw_min_temp == 45.0 C (the tie); null 44.9 C. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:8838) has no _guard_floor_hold check at dhw_temperature == dhw_min_temp asserting False Finding candidate: No check pins _guard_floor_hold's hot-water comparison at its tie (severity low, class I1).

### f11665aaedbf2550 custom_components/heatpump_optimizer/coordinator.py:8838 GUARD_OFF (candidate)

Patch `if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp: -> if False:` in HeatPumpOptimizerCoordinator._guard_floor_hold. Gate RED-AS-NULL (wall 3363.5 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_f11665aaedbf2550.py`: hold_baseline=1 on the baseline, hold_mutant=0 under the mutant. Inputs: dhw_enabled True, dhw_temperature 40 C < dhw_min_temp 45 C, room 21 C; null: room 16 C under the 17 C floor. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:8838) has no _guard_floor_hold check with hot water enabled and the tank under dhw_min_temp asserting True Finding candidate: No check pins that a cold hot-water tank overrides the peak/price guard (severity medium, class I1).

### 9b72b944ac12fa25 custom_components/heatpump_optimizer/coordinator.py:8842 GUARD_OFF (candidate)

Patch `if params.two_zone_enabled: -> if False:` in HeatPumpOptimizerCoordinator._guard_floor_hold. Gate RED-AS-NULL (wall 3654.6 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_9b72b944ac12fa25.py`: hold_baseline=1 on the baseline, hold_mutant=0 under the mutant. Inputs: two_zone_enabled True, upper floor 16 C under the 17 C floor, room 21 C; null: room 16 C as well. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:8842) has no two-zone _guard_floor_hold check with a zone under min_temp asserting True Finding candidate: No check pins that a breached zone floor overrides the peak/price guard (severity medium, class I1).

### fd1cc23d380739ba custom_components/heatpump_optimizer/coordinator.py:8847 CMP_BOUND (candidate)

Patch `return any(t is not None and float(t) < floor for t in temps) -> return any(t is not None and float(t) <= floor for t in temps)` in HeatPumpOptimizerCoordinator._guard_floor_hold. Gate RED-AS-NULL (wall 3379.6 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_fd1cc23d380739ba.py`: hold_baseline=0 on the baseline, hold_mutant=1 under the mutant. Inputs: room == min_temp == 17.0 C (the tie), hot water off; null 17.1 C. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:8847) has no _guard_floor_hold check at a temperature exactly on the floor asserting False Finding candidate: No check pins _guard_floor_hold's comfort-floor comparison at its tie (severity low, class I1).

### c20f346300d7efc1 custom_components/heatpump_optimizer/coordinator.py:9292 BOOLOP (candidate)

Patch `if when.tzinfo is None and now.tzinfo is not None: -> if when.tzinfo is None or now.tzinfo is not None:` in HeatPumpOptimizerCoordinator._immersion_dhw_margin. Gate RED-AS-NULL (wall 3487.5 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_c20f346300d7efc1.py`: margin_baseline=2.0 on the baseline, margin_mutant=0.0 under the mutant. Inputs: now 2026-01-15T12:00Z; events now-1 d, now-2 d and one stamped -05:00 whose instant is 1 h inside the 14-day cutoff; null: that event stamped +00:00. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:9292) has no _immersion_dhw_margin check with an aware event stamped in another offset than now's, asserting it is counted by its true instant Finding candidate: No check pins _immersion_dhw_margin to an event's true instant across UTC offsets (severity low, class I1).

### 60f673da42f9d671 custom_components/heatpump_optimizer/coordinator.py:9294 CMP_BOUND (candidate)

Patch `if when >= cutoff: -> if when > cutoff:` in HeatPumpOptimizerCoordinator._immersion_dhw_margin. Gate RED-AS-NULL (wall 3467.8 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_60f673da42f9d671.py`: margin_baseline=2.0 on the baseline, margin_mutant=0.0 under the mutant. Inputs: now 2026-01-15T12:00Z; events now-1 d, now-2 d and one exactly at now-14 d (the tie); null: 1 s inside. Traced reach: tests/features.py. Should fail: tests/features.py (traced reach of coordinator.py:9294) has no _immersion_dhw_margin check with an event exactly at the 14-day cutoff asserting it counts Finding candidate: No check pins _immersion_dhw_margin's 14-day window at its boundary (severity low, class I1).

### b6ac2d53028d45a3 custom_components/heatpump_optimizer/coordinator.py:5049 GUARD_OFF (candidate)

Patch `if self._pump_signals.mode_observed and not self._pump_signals.space_heat: -> if False:` in HeatPumpOptimizerCoordinator._interval_space_power. Gate RED-AS-NULL (wall 3867.2 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_b6ac2d53028d45a3.py`: space_kw_baseline=-1 on the baseline, space_kw_mutant=0 under the mutant. Inputs: power entity configured; observed mode hot-water-only (space_heat False, dhw True), plan 0 kW space / 1.5 kW hot water, meter 1.5 kW; also mode off, meter 0 kW (None -> 0.0 as well); null: space-heat mode 2 kW / 2 kW. Traced reach: tests/boost_drift_replay.py, tests/entities.py, tests/features.py. Should fail: tests/boost_drift_replay.py, tests/entities.py and tests/features.py execute coordinator.py:5049 on the traced baseline, yet none asserts _interval_space_power() is None while the observed mode heats no rooms Finding candidate: No check pins that a mode heating no rooms yields no space-power sample (severity medium, class I1).

### 1ee0ec8960fb9a66 custom_components/heatpump_optimizer/coordinator.py:5104 GUARD_OFF (candidate)

Patch `if tank == "dhw": -> if False:` in HeatPumpOptimizerCoordinator._max_pump_rise. Gate RED-AS-NULL (wall 4114.5 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_1ee0ec8960fb9a66.py`: rise_dhw_baseline=71.659 on the baseline, rise_dhw_mutant=409.483 under the mutant. Inputs: default parameters with a 200 L DHW tank (0.232 kWh/K) and the default buffer (0.0406 kWh/K), 5 kW electrical, outdoor 5 C, tank 'dhw'; null: tank 'buffer'. Traced reach: tests/block_duty.py, tests/boost_drift_replay.py, tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/finite_boundary.py, tests/manual_plan.py, tests/solar_alignment.py. Should fail: eight closure scripts execute coordinator.py:5104 on the traced baseline (block_duty, boost_drift_replay, config_flow_steps, entities, features, finite_boundary, manual_plan, solar_alignment), yet none asserts _max_pump_rise('dhw') == thermal_kw / dhw_store.capacity_kwh_per_c Finding candidate: No check pins _max_pump_rise('dhw') to the hot-water tank's own capacity (severity medium, class I1).

### 67495f7b404053fc custom_components/heatpump_optimizer/coordinator.py:7477 CMP_BOUND (equivalent-candidate)

Patch `while len(series) < n_steps: -> while len(series) <= n_steps:` in HeatPumpOptimizerCoordinator._forecast_arrays. Gate RED-AS-NULL (wall 3803.3 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_67495f7b404053fc.py`: fields_differing=0 on the baseline, fields_differing=0 under the mutant. Inputs: weather forecast 0/1/10/48 h x solar series 0/48 h x Open-Meteo off/on = 16 cases, each on a first and a second call of one coordinator, all 10 ForecastArrays fields compared NaN-aware: 0 differ; positive arm: the outdoor list after the padding loop is 96 long on the baseline and 97 under the mutant (the mutant runs, its extra element is sliced off by [:n_steps] before any array is built, and the lists are rebuilt per call). Traced reach: tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/solar_alignment.py. Should fail: none: no observable output of _forecast_arrays changes (every series is sliced [:n_steps]); a check could only read the internal list length

### 5f950692fab8eb1b custom_components/heatpump_optimizer/coordinator.py:7492 CLAMP_DROP (equivalent-candidate)

Patch `humidity[i] = float(np.clip(rh, 0.0, 100.0)) -> humidity[i] = float((rh))` in HeatPumpOptimizerCoordinator._forecast_arrays. Gate RED-AS-NULL (wall 3804.1 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_5f950692fab8eb1b.py`: production_inputs_differing=0 on the baseline, production_inputs_differing=0 under the mutant. Inputs: Open-Meteo hourly humidity 150 / 95 / -5 / NaN through the production _parse_block (max_value=100): 0 of 4 differ (out-of-range and non-finite samples are dropped before humidity_for, whose mean of in-range samples stays in [0, 100]); reach: line 7492 executes 96 times per call in the probe; positive arm: a 150 % series injected past the parser gives 100 vs 150, an input no production path builds. Traced reach: none. Should fail: none: the clamp is the identity on every value the only producer (open_meteo._parse_block, max_value=100) can deliver. No traced baseline executes coordinator.py:7492 (the closure scripts never drive an available Open-Meteo client with humidity); the probe reaches it, so the line is reachable, not dead

### 661116d11d6faa49 custom_components/heatpump_optimizer/coordinator.py:9170 GUARD_OFF (equivalent-candidate)

Patch `if not entity_id: -> if False:` in HeatPumpOptimizerCoordinator._indoor_humidity_value. Gate RED-AS-NULL (wall 3643.5 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_661116d11d6faa49.py`: inputs_differing=0 on the baseline, inputs_differing=0 under the mutant. Inputs: indoor_humidity_entity unset / None / '' x bus empty / live 55 % sensor / unavailable sensor / 150 % sensor = 12 inputs, comparing the value and the count of log records at every level: 0 differ (InputReader(hass, {}) with no entity id returns ok=False and its InputHealth is local to the call); positive arm: a configured entity reads 55.0 in both. Traced reach: tests/config_flow_steps.py, tests/entities.py, tests/features.py. Should fail: none: with no entity id, the fall-through read returns ok=False, so the function returns None as the early exit does

### 7f2768bd0a78b4bf custom_components/heatpump_optimizer/coordinator.py:5103 CLAMP_DROP (equivalent-candidate)

Patch `thermal_kw = params.max_electrical_power * max(cop, 1.0) -> thermal_kw = params.max_electrical_power * (cop)` in HeatPumpOptimizerCoordinator._max_pump_rise. Gate RED-AS-NULL (wall 3792.3 s). Probe `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_7f2768bd0a78b4bf.py`: inputs_differing=294 on the baseline, inputs_differing=294 under the mutant. Inputs: outdoor -60..+34 C in 1 K steps plus NaN, +inf, -inf (98 values) x cop_scale 0.5 / 1.0 / 1.5 x tank dhw / buffer = 588 inputs: 0 differ, min COP seen 1.0 (ThermalModel.compute_cop's only return is _cop_law's max(cop, 1.0); max(nan, 1.0) is nan in both arms); positive arm: compute_cop forced to 0.5 gives 123.153 vs 61.576 degC/h, so the probe sees the clamp when it acts. Traced reach: tests/block_duty.py, tests/boost_drift_replay.py, tests/config_flow_steps.py, tests/entities.py, tests/features.py, tests/finite_boundary.py, tests/manual_plan.py, tests/solar_alignment.py. Should fail: none: the clamp duplicates the floor compute_cop already applies; no input reaches cop < 1

