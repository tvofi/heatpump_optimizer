# D3-s1 wave box D3-g19 -- full gate for 16 D3.M3 full-net survivors

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, round 11, seat D3-s1. findings: [] (ids assigned at consolidation); candidates under `gate_survivors`.

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1095       13487          12        1802       14992
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.60
taken: 2026-11-22T21:40:32Z

## re-fire (successor seat, new container) 2026-11-25T00:48:32Z
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         777       14038          12        1542       15310
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.48
note: null control restored from the predecessor's checkpoint (gate_wave.sh null keeps it once taken); gates 1-6 ran on the machine above, gates 7-16 on this one
```

Null control (`fullgate.py null`, comment-only marker): gate_rc 1, red on artefact checks only: {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}; wall 4063.2 s (provisional). Taken by the predecessor seat on this box before the hand-over; restored from its checkpoint (gate_wave.sh keeps a taken null). A mutant kills only by failing a script beyond these, or more FAIL lines in one.

Every wall, CPU and load number is provisional (nproc 4, Intel Xeon @ 2.10GHz); counts are final.

## Tally

- gated: 16 of 16
- verdicts: {'RED-AS-NULL': 16}
- classes: {'candidate': 13, 'equivalent-candidate': 3}
- KILLED: 0; TIMEOUT: 0; candidates: 13; equivalent-candidates: 3

| key | site | patch | verdict | class | probe baseline -> mutant |
|---|---|---|---|---|---|
| `911f3cf5172ffc44` | grid_fee.py:496 RETURN_DEL | `return None -> pass` | RED-AS-NULL | candidate | None -> dict |
| `b5f0a73275608684` | grid_fee.py:360 CMP_BOUND | `and abs(float(entity_value)) > worst -> and abs(float(entity_value)) >= worst` | RED-AS-NULL | candidate | fixed -> entity |
| `68cc141bf2c3493a` | grid_fee.py:388 CMP_BOUND | `and float(entity_value) < lowest -> and float(entity_value) <= lowest` | RED-AS-NULL | candidate | fixed -> entity |
| `2043855ef5cf151d` | grid_fee.py:219 GUARD_OFF | `if not spec: -> if False:` | RED-AS-NULL | candidate | [] -> GridFeeError |
| `eee37674711fa45f` | optimizer.py:2006 CONST | `PRICE_MEAN_GUESS_EPS = 1e-3 -> PRICE_MEAN_GUESS_EPS = 0.002e-3` | RED-AS-NULL | candidate | [1.0, 0.7333, 0.4667, 0.2] -> [1.0, 0.8344, 0.2, 0.2] |
| `23b144fb9583c5c7` | optimizer.py:2156 CONST | `_MIN_MODULATION_BAND_KW = 0.1 -> _MIN_MODULATION_BAND_KW = 0.2` | RED-AS-NULL | candidate | 0.6667 -> 0.9565 |
| `68ef00f470ecea8d` | optimizer.py:2385 CONST | `_SAFETY_REPAIR_ROUNDS = 3 -> _SAFETY_REPAIR_ROUNDS = 6` | RED-AS-NULL | candidate | 4 count -> 7 count |
| `be95c184bf4746ff` | optimizer.py:4211 GUARD_OFF | `if n == 0: -> if False:` | RED-AS-NULL | candidate | 0.5 -> 0.0 |
| `e53563e772b70dbc` | optimizer.py:4229 CMP_BOUND | `solar_peak_mask = solar_radiation > 200.0 -> solar_peak_mask = solar_radiation >= 200.0` | RED-AS-NULL | candidate | 0 count -> 1 count |
| `aebea2e6b76b2dc3` | optimizer.py:4234 CLAMP_DROP | `n_6h = min(int(6 / dt_hours), n) -> n_6h = (int(6 / dt_hours))` | RED-AS-NULL | equivalent-candidate |  ->  |
| `2ae9ff3138f9364d` | optimizer.py:4235 CLAMP_DROP | `n_12h = min(int(12 / dt_hours), n) -> n_12h = (int(12 / dt_hours))` | RED-AS-NULL | equivalent-candidate |  ->  |
| `24ef8e54dad20484` | optimizer.py:4249 CMP_BOUND | `if typical_heat_loss > 0: -> if typical_heat_loss >= 0:` | RED-AS-NULL | candidate | 1.0 -> 0.6 |
| `7f048d7823b17826` | optimizer.py:4250 CLAMP_DROP | `solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0) -> solar_fraction = min(future_solar_6_12h / (typical_heat_loss * 6), 1.0)` | RED-AS-NULL | candidate | 0.8824 -> 0.6000 |
| `4c7e296370fc452d` | optimizer.py:4271 CMP_BOUND | `if avg_future_precip > 0.1: -> if avg_future_precip >= 0.1:` | RED-AS-NULL | candidate | 1.0 -> 1.0075 |
| `9644a454ac8f288b` | optimizer.py:4272 CLAMP_DROP | `rain_intensity = min(avg_future_precip / 2.0, 1.0) -> rain_intensity = (avg_future_precip / 2.0)` | RED-AS-NULL | candidate | 1.1500 -> 1.3000 |
| `1b3cbaddab6e496f` | optimizer.py:3402 GUARD_OFF | `if end <= i: -> if False:` | RED-AS-NULL | equivalent-candidate |  ->  |

## Survivors (step-4 answers)

### `911f3cf5172ffc44` grid_fee.py:496 RETURN_DEL (candidate)

Patch `return None -> pass` in `apply_catalog`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3992.4 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_911f3cf5172ffc44.py`: stale_row_baseline=None; stale_row_mutant=dict; stale_row_mutant_rules_written='garbage'; moved=1 count; stale_inputs_moved=2 of 2 count; shipped_rows=2 count; shipped_rows_reaching_line=0 count; null_delta=0 count; wall=0.10 s (provisional); thread_factor=1.000; load1=0.93; swapins=0.

Inputs tried: one injected row with rules "garbage" (no '='), one with "Mon = abc"; every shipped product id; None; "none"; unknown id.

**apply_catalog's stale-row refusal (grid_fee.py:496) is unreachable from the shipped catalog and pinned by no check.** Replacing grid_fee.py:496 `return None` with `pass` survives the full gate; with a stale catalog row injected apply_catalog then returns the unparseable rules for writing (probe stale_row_mutant=dict, baseline None), and no shipped row reaches the line (0 of 2)

Reach: the probe reaches line 496 only with an injected stale catalog row (mock.patch.dict on SWEDEN_CATALOG); with the shipped catalog the line is unreachable: an unreachable finding, not a test gap

Should have failed: none can, through production: no traced baseline executes grid_fee.py:496 and every shipped SWEDEN_CATALOG row parses (probe: shipped_rows_reaching_line=0). The checks that call apply_catalog are tests/entities.py:8221-8237 (a shipped id, an unknown id, DSO_PRODUCT_NONE) and tests/features.py:18104-18110 (dropped ids resolve to None); none injects a row whose grid_fee_rules fail parse_rules, the only input that reaches the line

### `b5f0a73275608684` grid_fee.py:360 CMP_BOUND (candidate)

Patch `and abs(float(entity_value)) > worst -> and abs(float(entity_value)) >= worst` in `max_abs_component`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3781.4 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_b5f0a73275608684.py`: label_baseline=fixed; label_mutant=entity; label_changed=1 count; value_delta=0.0; negative_tie_label=fixed->entity; zero_tie_label=fixed->entity; null_label_delta=0 count; wall=0.07 s (provisional); thread_factor=1.000; load1=0.93; swapins=0.

Inputs tried: ties +0.30/-0.30 against fixed 0.30; fixed 0.0 / entity 0.0 (tie at zero); the three null inputs.

**No check pins max_abs_component's source label on a fixed/entity |rate| tie (grid_fee.py:360 > -> >=).** Changing grid_fee.py:360 `> worst` to `>= worst` survives the full gate and moves max_abs_component's source label on a fixed/entity tie from 'fixed' to 'entity' (value unchanged)

Reach: executed on the traced baseline (tests/features.py); the tie is reachable from a config with grid_fee_fixed equal to |fee entity state|

Should have failed: tests/features.py (traced baseline executes grid_fee.py:360): its max_abs_component checks at tests/features.py:28737-28745 use rules mode and MODE_NONE only; it lacks an entity-mode tie, e.g. max_abs_component(GridFeeSchedule(mode='entity', fixed=0.30), 0.30) == (0.30, 'fixed')

### `68cc141bf2c3493a` grid_fee.py:388 CMP_BOUND (candidate)

Patch `and float(entity_value) < lowest -> and float(entity_value) <= lowest` in `min_component`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3741.2 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68cc141bf2c3493a.py`: label_baseline=fixed; label_mutant=entity; label_changed=1 count; value_delta=0.0; zero_tie_label=fixed->entity; null_label_delta=0 count; wall=0.07 s (provisional); thread_factor=1.000; load1=0.74; swapins=0.

Inputs tried: tie -0.20/-0.20; tie at 0.0/0.0 (fixed 0, entity 0); the three null inputs.

**No check pins min_component's source label on a fixed/entity rate tie (grid_fee.py:388 < -> <=).** Changing grid_fee.py:388 `< lowest` to `<= lowest` survives the full gate and moves min_component's source label on a fixed/entity tie from 'fixed' to 'entity' (value unchanged)

Reach: executed on the traced baseline (tests/features.py); the tie is reachable from a negative fixed component equal to the fee entity's state

Should have failed: tests/features.py (traced baseline executes grid_fee.py:388): its min_component checks at tests/features.py:17749-17766 cover rules mode, a positive fixed and MODE_NONE; it lacks an entity-mode tie, e.g. min_component(GridFeeSchedule(mode='entity', fixed=-0.20), -0.20) == (-0.20, 'fixed')

### `2043855ef5cf151d` grid_fee.py:219 GUARD_OFF (candidate)

Patch `if not spec: -> if False:` in `parse_rules`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3769.5 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_2043855ef5cf151d.py`: parse_none_baseline=[]; parse_none_mutant=GridFeeError; spec_problem_none_baseline=None; spec_problem_none_mutant=invalid_grid_fee_rules; moved=1 count; empty_string_delta=0 count; from_config_rules_delta=0 count; from_config_warnings_baseline=0 count; from_config_warnings_mutant=1 count; wall=0.07 s (provisional); thread_factor=1.000; load1=0.75; swapins=0.

Inputs tried: None, '', ' ', '\n', ';', ',', 'Mon = 0.5'; from_config with grid_fee_rules=None in rules mode.

**No check feeds parse_rules None; disabling its empty-spec guard turns None into a GridFeeError unseen.** Changing grid_fee.py:219 `if not spec:` to `if False:` survives the full gate; parse_rules(None) then raises GridFeeError instead of returning [], spec_problem(None) returns invalid_grid_fee_rules instead of None, and from_config logs a WARNING it did not before

Reach: executed on the traced baseline; for every str input the split loop already drops empty lines (empty_string_delta=0), so the guard is load-bearing only for None

Should have failed: tests/features.py (traced baseline executes grid_fee.py:219 through from_config/spec_problem): no check calls parse_rules(None) or spec_problem(None); it lacks `parse_rules(None) == []` and `spec_problem(None) is None` (the signature is `str | None` and the docstring says empty input is an empty list)

### `eee37674711fa45f` optimizer.py:2006 CONST (candidate)

Patch `PRICE_MEAN_GUESS_EPS = 1e-3 -> PRICE_MEAN_GUESS_EPS = 0.002e-3` in `<module>`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3934.9 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_eee37674711fa45f.py`: weights_baseline=[1.0, 0.7333, 0.4667, 0.2]; weights_mutant=[1.0, 0.8344, 0.2, 0.2]; max_abs_delta=0.2667; max_abs_delta_24step=0.2783; null_max_abs_delta=0.0; wall=0.36 s (provisional); thread_factor=1.000; load1=0.85; swapins=0.

Inputs tried: the 4-step ramp above; a 24-step ramp 0..0.0012; the two null horizons.

**No check pins PRICE_MEAN_GUESS_EPS; a 500x smaller threshold sends near-zero-mean horizons down the saturating guess.** Changing optimizer.py:2006 PRICE_MEAN_GUESS_EPS from 1e-3 to 2e-6 survives the full gate and moves _price_guess_weights on a mean-6e-4 horizon by up to 0.267 (rank fill -> clipped smooth weights)

Reach: executed on every solve; the moving input (horizon mean price between 2e-6 and 1e-3 per kWh) is a near-zero-price horizon

Should have failed: tests/features.py / tests/optimality.py (traced baselines execute optimizer.py:2082 through _price_guess_weights): no check calls _price_guess_weights on a horizon whose mean lies in (2e-6, 1e-3]; it lacks e.g. _price_guess_weights([0, 4e-4, 8e-4, 1.2e-3]) == rank weights [1.0, 0.733, 0.467, 0.2]

### `23b144fb9583c5c7` optimizer.py:2156 CONST (candidate)

Patch `_MIN_MODULATION_BAND_KW = 0.1 -> _MIN_MODULATION_BAND_KW = 0.2` in `<module>`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3975.0 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_23b144fb9583c5c7.py`: fraction_baseline=0.6667; fraction_mutant=0.9565; abs_delta=0.2899; bands_moved=3 of 3 count; null_abs_delta=0.0; wall=0.33 s (provisional); thread_factor=1.000; load1=0.78; swapins=0.

Inputs tried: bands 0.10, 0.15, 0.19 kW at mid-band power; the two null bands.

**No check pins _MIN_MODULATION_BAND_KW; doubling it grades a 0.15 kW-band pump as fixed-speed unseen.** Changing optimizer.py:2156 _MIN_MODULATION_BAND_KW from 0.1 to 0.2 survives the full gate and moves _power_fraction(1.10 kW) on a 1.00-1.15 kW pump from 0.667 to 0.957

Reach: executed on every plan (setpoint, displace and action sites share _power_fraction); the moving input is a pump whose modulation band is 0.1-0.2 kW

Should have failed: tests/features.py (traced baseline executes _power_fraction, optimizer.py:2170): its pumps have bands of 0 (fixed speed) or well above 0.2 kW; it lacks a _power_fraction check on a band in [0.1, 0.2) kW, e.g. min 1.00 / max 1.15 kW at 1.10 kW == 0.667

### `68ef00f470ecea8d` optimizer.py:2385 CONST (candidate)

Patch `_SAFETY_REPAIR_ROUNDS = 3 -> _SAFETY_REPAIR_ROUNDS = 6` in `<module>`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3805.0 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68ef00f470ecea8d.py`: release_calls_baseline=4 count; release_calls_mutant=7 count; moved=1 count; released_baseline=24 count; released_mutant=24 count; real_release_calls_baseline=2 count; real_release_calls_mutant=2 count; real_released_baseline=24 count; real_released_mutant=24 count; null_release_calls=0/0 count; wall=1.72 s (provisional); thread_factor=1.000; load1=0.85; swapins=0.

Inputs tried: the never-converging stub; the real release rule on an all-off 24 h winter plan; no pins.

**No check pins the manual-plan repair bound _SAFETY_REPAIR_ROUNDS; 3 -> 6 adds three full solves unseen.** Changing optimizer.py:2385 _SAFETY_REPAIR_ROUNDS from 3 to 6 survives the full gate; on a never-converging manual plan optimize consults _safety_release_steps 7 times instead of 4 (three extra full solves) with the same 24 released slots

Reach: executed on the traced baseline; the round count is observable only on a plan that needs more than 3 repair rounds, which the probe builds with the suite's own stub (the real rule converged in 1 round on the all-off winter plan)

Should have failed: tests/manual_plan.py:test_release_always_resolves (traced baseline executes the loop at optimizer.py:4514 with the never-converging stub): it asserts `len(calls) > 0` and that every slot is released, but lacks `len(calls) == _SAFETY_REPAIR_ROUNDS + 1` (4); with the real release rule the all-off plan converges after 1 round in both arms

### `be95c184bf4746ff` optimizer.py:4211 GUARD_OFF (candidate)

Patch `if n == 0: -> if False:` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3680.8 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_be95c184bf4746ff.py`: pre_heat_urgency_baseline=0.5; pre_heat_urgency_mutant=0.0; moved=1 count; extra_keys_mutant=3 count; null_delta=0 count; reach_optimize_horizon_0=IndexError n_seen=0; reach_optimize_horizon_0.1=IndexError n_seen=0; reach_optimize_empty=1 count; wall=0.47 s (provisional); thread_factor=1.000; load1=0.86; swapins=0.

Inputs tried: n=0 (all six summary keys compared); the 24-step null; optimize() with horizon_hours=0 and 0.1 for reach.

**No check calls _analyze_forecast_trajectory on an empty forecast; dropping its n == 0 guard moves pre_heat_urgency 0.5 -> 0.0.** Changing optimizer.py:4211 `if n == 0:` to `if False:` survives the full gate; on an empty forecast the method returns pre_heat_urgency 0.0 instead of 0.5 and three extra keys, and optimize() raises IndexError on an empty horizon in both arms

Reach: line 4211 is executed every solve; the moving input (n = 0) reaches it only from an optimize() that then fails regardless of the arm

Should have failed: none through production: optimize() reaches the method with n = 0 at horizon_hours 0 or 0.1 but raises IndexError later in both arms; a direct check `_analyze_forecast_trajectory(empty...)['pre_heat_urgency'] == 0.5` is what separates. The traced baselines (tests/block_duty.py, tests/features.py, ...) execute line 4211 with n > 0 only; tests/features.py:13058 builds the empty-forecast dict by hand rather than calling the method

### `e53563e772b70dbc` optimizer.py:4229 CMP_BOUND (candidate)

Patch `solar_peak_mask = solar_radiation > 200.0 -> solar_peak_mask = solar_radiation >= 200.0` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3637.3 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_e53563e772b70dbc.py`: peaks_baseline=0 count; peaks_mutant=1 count; moved=1 count; other_keys_delta=0 count; null_delta=0 count; wall=0.34 s (provisional); thread_factor=1.000; load1=1.06; swapins=0.

Inputs tried: 200.0 at one step; 199.9; 200.1.

**No check pins the 200 W/m2 solar-peak boundary; > -> >= at optimizer.py:4229 is unseen.** Changing optimizer.py:4229 `> 200.0` to `>= 200.0` survives the full gate and moves solar_peak_indices on a forecast with 200.0 W/m2 at one step from [] to [3]

Reach: executed every solve; the moving input is a radiation value of exactly 200.0 W/m2

Should have failed: tests/features.py / tests/block_duty.py (traced baselines execute optimizer.py:4229): no forecast with exactly 200.0 W/m2; they lack a check that a 200.0 W/m2 step is absent from solar_peak_indices

### `aebea2e6b76b2dc3` optimizer.py:4234 CLAMP_DROP (equivalent-candidate)

Patch `n_6h = min(int(6 / dt_hours), n) -> n_6h = (int(6 / dt_hours))` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3639.7 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_aebea2e6b76b2dc3.py`: grids_tried=35 count; grids_moved=0 count; wall=0.33 s (provisional); thread_factor=1.000; load1=0.87; swapins=0.

Inputs tried: n in (1,3,5,6,7,12,24) x dt in (0.25,1.0,3.0,7.0,13.0) h, sun 500 W/m2, cold outdoor.

Equivalence: equivalent: int(6/dt) > n only when 6/dt > n, and then solar_gains_kw[n_6h:n_12h] is empty in both arms because n_12h = min(int(12/dt), n) <= n; 0 of 35 (n, dt) grids moved

### `2ae9ff3138f9364d` optimizer.py:4235 CLAMP_DROP (equivalent-candidate)

Patch `n_12h = min(int(12 / dt_hours), n) -> n_12h = (int(12 / dt_hours))` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3525.6 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_2ae9ff3138f9364d.py`: grids_tried=35 count; grids_moved=0 count; wall=0.46 s (provisional); thread_factor=1.000; load1=0.83; swapins=0.

Inputs tried: n in (1,3,6,11,12,13,24) x dt in (0.25,1.0,3.0,7.0,13.0) h, sun 500 W/m2, cold outdoor.

Equivalence: equivalent: numpy clamps a slice end past len(solar_gains_kw) to n, so solar_gains_kw[n_6h:int(12/dt)] == solar_gains_kw[n_6h:n]; 0 of 35 (n, dt) grids moved

### `24ef8e54dad20484` optimizer.py:4249 CMP_BOUND (candidate)

Patch `if typical_heat_loss > 0: -> if typical_heat_loss >= 0:` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3561.8 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_24ef8e54dad20484.py`: solar_reduction_baseline=1.0; solar_reduction_mutant=0.6; abs_delta=0.4000; no_sun_delta=0 count; null_delta=0 count; wall=0.32 s (provisional); thread_factor=1.000; load1=0.85; swapins=0.

Inputs tried: outdoor == target 21.0 C (sun 500, sun 0); outdoor 20.0 and 22.0 C.

**No check pins solar_reduction at zero typical heat loss; > 0 -> >= 0 at optimizer.py:4249 moves it 1.0 -> 0.6.** Changing optimizer.py:4249 `typical_heat_loss > 0` to `>= 0` survives the full gate and, with outdoor == target and 500 W/m2 sun, moves the published solar_reduction_factor from 1.0 to 0.6

Reach: executed every solve; the moving input is mean(outdoor) == target_temp exactly

Should have failed: tests/features.py / tests/block_duty.py (traced baselines execute optimizer.py:4249): no forecast whose mean outdoor equals the target; they lack a check that solar_reduction_factor == 1.0 at zero typical heat loss

### `7f048d7823b17826` optimizer.py:4250 CLAMP_DROP (candidate)

Patch `solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0) -> solar_fraction = min(future_solar_6_12h / (typical_heat_loss * 6), 1.0)` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3637.3 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_7f048d7823b17826.py`: solar_reduction_baseline=0.8824; solar_reduction_mutant=0.6000; abs_delta=0.2824; inputs_moved=4 of 4 count; null_delta=0 count; wall=0.36 s (provisional); thread_factor=1.000; load1=0.85; swapins=0.

Inputs tried: outdoor 20.9 and 20.99 C x sun 1.0 and 0.1 W/m2; null outdoor 15.0 C.

**No check makes the 0.1 floor in solar_fraction bind; dropping max(..., 0.1) at optimizer.py:4250 is unseen.** Changing optimizer.py:4250 to drop the max(typical_heat_loss * 6, 0.1) floor survives the full gate and moves solar_reduction_factor from 0.882 to 0.600 at outdoor 20.99 C, target 21.0 C, sun 1 W/m2

Reach: executed every solve; the floor binds only when 0 < 6 x typical heat loss < 0.1 (mean outdoor within about 0.11 K of the target at 0.15 kW/K)

Should have failed: tests/features.py / tests/block_duty.py (traced baselines execute optimizer.py:4250): every fixture's 6 x typical heat loss is far above 0.1; they lack a near-balance-point case where the 0.1 floor binds, e.g. outdoor 20.99 C vs target 21.0 with 1 W/m2 sun, solar_reduction_factor == 0.882

### `4c7e296370fc452d` optimizer.py:4271 CMP_BOUND (candidate)

Patch `if avg_future_precip > 0.1: -> if avg_future_precip >= 0.1:` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3593.1 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_4c7e296370fc452d.py`: rain_anticipation_baseline=1.0; rain_anticipation_mutant=1.0075; moved=1 count; lengths_moved=2 of 4 count; null_delta=0 count; wall=0.34 s (provisional); thread_factor=1.000; load1=0.85; swapins=0.

Inputs tried: 0.1 mm/h at n=1, 2, 4, 24 (n>=4 sums to 0.10000000000000002 and both arms fire); 0.09; 0.2.

**No check pins the 0.1 mm/h rain threshold; > -> >= at optimizer.py:4271 is unseen.** Changing optimizer.py:4271 `> 0.1` to `>= 0.1` survives the full gate and moves rain_anticipation_factor from 1.0 to 1.0075 on a 1-step forecast of exactly 0.1 mm/h

Reach: executed every solve; the moving input needs the decay-weighted mean to be exactly 0.1 (n = 1 or 2 at 0.1 mm/h; at n >= 4 rounding makes it 0.10000000000000002 and both arms fire)

Should have failed: tests/features.py / tests/block_duty.py (traced baselines execute optimizer.py:4271): no forecast whose weighted mean precipitation is exactly 0.1 mm/h; they lack a boundary check rain_anticipation_factor == 1.0 at 0.1 mm/h (n = 1)

### `9644a454ac8f288b` optimizer.py:4272 CLAMP_DROP (candidate)

Patch `rain_intensity = min(avg_future_precip / 2.0, 1.0) -> rain_intensity = (avg_future_precip / 2.0)` in `HeatPumpOptimizer._analyze_forecast_trajectory`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3624.9 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_9644a454ac8f288b.py`: rain_anticipation_baseline=1.1500; rain_anticipation_mutant=1.3000; abs_delta=0.1500; pre_heat_urgency=0.7500->1.0000; pre_heat_urgency_moved=1 count; at_cap_delta=0 count; null_delta=0 count; wall=0.31 s (provisional); thread_factor=1.000; load1=0.84; swapins=0.

Inputs tried: 4.0 mm/h; 2.0 mm/h (at the cap: identical); null 1.0 mm/h.

**No check caps rain_anticipation at heavy rain; dropping min(..., 1.0) at optimizer.py:4272 is unseen.** Changing optimizer.py:4272 to drop the min(avg/2, 1.0) cap survives the full gate and, at 4 mm/h all day, moves the published rain_anticipation_factor from 1.15 to 1.30 and pre_heat_urgency from 0.75 to 1.0

Reach: executed every solve with rain; the cap binds when the weighted mean precipitation exceeds 2 mm/h

Should have failed: tests/features.py / tests/block_duty.py / tests/env_drift.py (traced baselines execute optimizer.py:4272): no fixture's weighted mean precipitation exceeds 2 mm/h; they lack a heavy-rain check rain_anticipation_factor <= rain_heat_loss_multiplier (1.15) at 4 mm/h

### `1b3cbaddab6e496f` optimizer.py:3402 GUARD_OFF (equivalent-candidate)

Patch `if end <= i: -> if False:` in `HeatPumpOptimizer._anticipatory_weights`. Gate RED-AS-NULL (gate_rc 1, failing scripts identical to the null; wall 3650.8 s provisional).

Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_1b3cbaddab6e496f.py`: signature=['self', 'n_steps', 'dt', 'solar_gains', 'heat_loss_factors']; guard_hits_baseline=252 count; max_abs_delta=0.0; mutant_runtime_warnings=1008 count; null_max_abs_delta=0.0; wall=0.38 s (provisional); thread_factor=1.000; load1=0.69; swapins=0.

Inputs tried: dt in (0.25, 1, 4, 8, 8.5, 9, 24) h x signals (sun 2 kW / loss 1.3, sun 0 / loss 1.0, sun nan / loss nan,

Equivalence: equivalent: end <= i only when lookahead = int(8/dt) = 0 (dt > 8 h); the mutant then takes np.mean of an empty slice = nan, and nan > 0.5 / nan > 1.1 are False, so weights[i] stays 1.0 as `continue` leaves it; max_abs_delta 0.0 over 168 (dt, signal, n) inputs, only RuntimeWarnings differ

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_1b3cbaddab6e496f.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_2043855ef5cf151d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_23b144fb9583c5c7.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_24ef8e54dad20484.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_2ae9ff3138f9364d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_4c7e296370fc452d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68cc141bf2c3493a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68ef00f470ecea8d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_7f048d7823b17826.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_911f3cf5172ffc44.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_9644a454ac8f288b.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_aebea2e6b76b2dc3.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_b5f0a73275608684.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_be95c184bf4746ff.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_e53563e772b70dbc.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_eee37674711fa45f.py`

Procedure: gate_wave.sh (out-of-tree driver shipped on dispatch/finder-r11-D3-g19): `gate_wave.sh null` once, then `gate_wave.sh run` = fullgate.py run per key of keys.tsv, one gate at a time, 4 h cap, checkpoint after each; probes run in a separate baseline worktree, never in the gate tree.

## Exposure

Read COMMON.md, D3.md, dev/audit/README.md and finding.schema.json (through a haiku extractor), this seat's carried slice reports and m4 answers, the box's own dispatch/inbox/wip refs and the keys.tsv of the 47 dispatch/finder-r11-D3-g<NN> refs (key lists only); no register, J/ or verifier report, no docs/ or GitHub read. The box was resumed twice: a predecessor seat on another account stalled after 6 gates (resumed from its checkpoint 4d3f1ed7), and this seat's container restarted twice mid-gate (68ef00f470ecea8d, 2ae9ff3138f9364d): each aborted gate's partial log is kept as gates/<key>-restart-aborted*.log and the gate was re-run from the baseline after releasing the stale gate_lock lease. The first gate of 1b3cbaddab6e496f ran the whole suite (3495 s) but ended without a record: a stale index.lock in the gate worktree (created mid-gate at 11:10Z, no git process alive) made fullgate.py's reset fail, and gate_wave.sh wrote it as TIMEOUT; that record and log are kept as gates/1b3cbaddab6e496f-indexlock-norecord.{json,log}, the lock was removed, the tree reset to the baseline and the key re-gated (the record under gates/1b3cbaddab6e496f.json).
