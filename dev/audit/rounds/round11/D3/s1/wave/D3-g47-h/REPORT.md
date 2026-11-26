# D3-s1 wave box D3-g47-h (helper half of box D3-g47)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Gated the last 6 keys of D3-g47 (rows 10-15 of 15); the main box gates rows 1-9.

## Machine and controls
```
4
               total        used        free      shared  buff/cache   available
Mem:           16087         786       14009          12        1563       15301
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
1.01 0.39 0.14 1/137 677

```
Null control (`fullgate.py null`): gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], wall 3358.4 s, load1 0.87->0.92 (provisional). The three failures are artefact checks of the stripped tree (and a subset of the earlier null in gates-prior); every key below is read against them.

## Tally
gated 6; KILLED 0; SURVIVED 0; RED-AS-NULL 6 (read as survived); TIMEOUT 0; candidates 5; equivalent-candidates 1.

| key | site | verdict | class |
|---|---|---|---|
| 5b6489f7860d73b1 | custom_components/heatpump_optimizer/thermal_model.py:2852 CLAMP_DROP | RED-AS-NULL | candidate |
| 1111a3e5d9c44e3f | custom_components/heatpump_optimizer/thermal_model.py:2854 CMP_BOUND | RED-AS-NULL | candidate |
| 67a0550ee998a213 | custom_components/heatpump_optimizer/thermal_model.py:2854 GUARD_OFF | RED-AS-NULL | candidate |
| 75b300b2bc47485f | custom_components/heatpump_optimizer/thermal_model.py:2856 CLAMP_DROP | RED-AS-NULL | candidate |
| 92c063e90dafcc35 | custom_components/heatpump_optimizer/thermal_model.py:2903 CMP_BOUND | RED-AS-NULL | equivalent-candidate |
| 6fa8436f09ad7e06 | custom_components/heatpump_optimizer/thermal_model.py:2906 CLAMP_DROP | RED-AS-NULL | candidate |

## Survivors

### 5b6489f7860d73b1 (custom_components/heatpump_optimizer/thermal_model.py:2852 CLAMP_DROP) -- candidate
Patch: `rh = min(max(indoor_rh_percent, 0.0), 100.0) / 100.0 -> rh = (max(indoor_rh_percent, 0.0)) / 100.0`. Should fail: tests/features.py and tests/entities.py execute line 2852 on the traced baseline (carried M4 answer); neither asserts mold_safe_room_floor for indoor_rh_percent > 100 (33.79 vs 43.67 at rh 150)
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_5b6489f7860d73b1.py`:
```
INPUT (20.0, 100.0, 0.0, 0.7) base 33.794921985364404 mut 33.794921985364404
INPUT (20.0, 100.0001, 0.0, 0.7) base 33.794921985364404 mut 33.7949457193209
INPUT (20.0, 120.0, 0.0, 0.7) base 33.794921985364404 mut 38.17183236314228
INPUT (20.0, 150.0, 0.0, 0.7) base 33.794921985364404 mut 43.667507680809926
INPUT (20.0, 1000000.0, 0.0, 0.7) base 33.794921985364404 mut 546.4342305108123
RESULT floor_at_rh150_base=33.794921985364404 mutant=43.667507680809926
```

### 1111a3e5d9c44e3f (custom_components/heatpump_optimizer/thermal_model.py:2854 CMP_BOUND) -- candidate
Patch: `if e <= 1e-9: -> if e < 1e-9:`. Should fail: tests/features.py/entities.py execute line 2854; no check pins mold_safe_room_floor at e == 1e-9 exactly (room -20C, rh 7.94e-08: -100.0 vs -194.06); single-point boundary, low consequence
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_1111a3e5d9c44e3f.py`:
```
INPUTS tried 720 exactly-1e-9 hits (-20.0, 7.93870519098195e-08)
RESULT floor_e_eq_1e-9_base=-100.0 mutant=-194.0555820506525
```

### 67a0550ee998a213 (custom_components/heatpump_optimizer/thermal_model.py:2854 GUARD_OFF) -- candidate
Patch: `if e <= 1e-9: -> if False:`. Should fail: tests/features.py/entities.py execute line 2854; no check asserts mold_safe_room_floor(.., indoor_rh=0, ..) == -100.0 (mutant gives -194.9)
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_67a0550ee998a213.py`:
```
INPUT (20.0, 0.0, 0.0, 0.7) base -100.0 mut -194.90728051942975
INPUT (20.0, -5.0, 0.0, 0.7) base -100.0 mut -194.90728051942975
INPUT (20.0, 1e-12, 0.0, 0.7) base -100.0 mut -194.90728051942975
RESULT floor_at_rh0_base=-100.0 mutant=-194.90728051942975
```

### 75b300b2bc47485f (custom_components/heatpump_optimizer/thermal_model.py:2856 CLAMP_DROP) -- candidate
Patch: `t_surface_min = dew_point_for_pressure(e / max(surface_rh_limit, 0.05)) -> t_surface_min = dew_point_for_pressure(e / (surface_rh_limit))`. Should fail: tests/features.py/entities.py execute line 2856; no check asserts the 0.05 floor on surface_rh_limit (limit 0.01: 90.49 vs 147.46; limit 0: ZeroDivisionError)
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_75b300b2bc47485f.py`:
```
INPUT (20.0, 50.0, 0.0, 0.7, 0.8) base 18.02454114208337 mut 18.02454114208337
INPUT (20.0, 50.0, 0.0, 0.7, 0.05) base 90.49033855922843 mut 90.49033855922843
INPUT (20.0, 50.0, 0.0, 0.7, 0.04) base 90.49033855922843 mut 97.59274302524308
INPUT (20.0, 50.0, 0.0, 0.7, 0.01) base 90.49033855922843 mut 147.45844384031514
INPUT (20.0, 50.0, 0.0, 0.7, 0.0) base 90.49033855922843 mut EXC ZeroDivisionError
INPUT (20.0, 50.0, 0.0, 0.7, -0.5) base 90.49033855922843 mut -194.90728051942975
RESULT floor_at_limit0.01_base=90.49033855922843 mutant=147.45844384031514
```

### 92c063e90dafcc35 (custom_components/heatpump_optimizer/thermal_model.py:2903 CMP_BOUND) -- equivalent-candidate
Patch: `if hp_temp > flow_set: -> if hp_temp >= flow_set:`. Should fail: n/a: at hp_temp == flow_set both branches return 0.0 (region 2 f_w=0; region 3 hp_deficiency=0 and wood<flow=hp so hotter=0); 960 inputs tried (flow x wood x floor x margin), no difference
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_92c063e90dafcc35.py`:
```
INPUTS tried 960 first difference None
RESULT wood_share_hp_eq_flow_base=0.0 mutant=0.0 ndiff=0
```

### 6fa8436f09ad7e06 (custom_components/heatpump_optimizer/thermal_model.py:2906 CLAMP_DROP) -- candidate
Patch: `span = max(flow_set - floor_temp, 1e-6) -> span = (flow_set - floor_temp)`. Should fail: tests/features.py executes line 2906; no check asserts wood_share when flow_set == floor_temp and hp_temp>flow_set (0.0 vs ZeroDivisionError)
Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_6fa8436f09ad7e06.py`:
```
INPUT (30.0, 50.0, 40.0, 40.0) base 0.0 mut EXC ZeroDivisionError
INPUT (50.0, 50.0, 40.0, 40.0) base 1.0 mut 1.0
INPUT (30.0, 50.0, 40.0, 45.0) base 0.0 mut 0.0
INPUT (30.0, 50.0, 40.0, 20.0) base 0.25 mut 0.25
INPUT (39.0, 50.0, 40.0, 40.0) base 0.0 mut EXC ZeroDivisionError
RESULT wood_share_floor_eq_flow_base=0.0 mutant=EXC ZeroDivisionError
```

## Unfinished
none.

Findings are returned under `gate_survivors`, no ids assigned (the orchestrator numbers them).