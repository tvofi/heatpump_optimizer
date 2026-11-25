# D3-s1 box D3-g43: full gate for 15 D3.M3 full-net survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: 4 vCPU Intel Xeon @ 2.10GHz, 16 GB, alone on the box; every wall/load number is provisional (see MACHINE.txt).

Null control: `fullgate.py null`, gate_rc=1, red on ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] only (artefact checks of the stripped tree), wall 3676.0 s, load1 0.92->1.04. Kills are counted beyond it.

## Tally

gated 15/15: KILLED=5, RED-AS-NULL=10; candidates 2, equivalent-candidates 8, timeouts 0.

KILLED by: 97bd985754f1099b -> python3 tests/stress.py; cc34cacdd80553ed -> python3 tests/edge.py; a3f2b00cc4aa527e -> python3 tests/edge.py,python3 tests/stress.py; a486806b8f4ff4d7 -> python3 tests/stress.py; f2706cbdb16a8f66 -> python3 tests/edge.py

## Per key

| key | site | patch | verdict | class |
|---|---|---|---|---|
| f2ab25c56b407ef9 | custom_components/heatpump_optimizer/thermal_model.py:3389 CMP_BOUND | `if carnot_ref <= 1e-9: -> if carnot_ref < 1e-9:` | RED-AS-NULL  | equivalent-candidate |
| d9a65b3770e6860a | custom_components/heatpump_optimizer/thermal_model.py:4114 GUARD_OFF | `if n_sub == 1: -> if False:` | RED-AS-NULL  | equivalent-candidate |
| 97bd985754f1099b | custom_components/heatpump_optimizer/thermal_model.py:4140 GUARD_OFF | `if n_sub == 1: -> if False:` | KILLED ['python3 tests/stress.py'] | killed |
| cc34cacdd80553ed | custom_components/heatpump_optimizer/thermal_model.py:4553 GUARD_OFF | `if initial_state.wood_tank_temperature is not None: -> if False:` | KILLED ['python3 tests/edge.py'] | killed |
| 7b46514aedc0a8cf | custom_components/heatpump_optimizer/thermal_model.py:4571 BOOLOP | `start_hour is not None and p.internal_gains_profile is not None -> start_hour is not None or p.internal_gains_profile is not None` | RED-AS-NULL  | equivalent-candidate |
| 876be7bf2f538255 | custom_components/heatpump_optimizer/thermal_model.py:4578 BOOLOP | `if p.two_zone_enabled and throttled: -> if p.two_zone_enabled or throttled:` | RED-AS-NULL  | equivalent-candidate |
| a3f2b00cc4aa527e | custom_components/heatpump_optimizer/thermal_model.py:4668 CLAMP_DROP | `np.maximum(T_wood, T_buf) -> (T_wood)` | KILLED ['python3 tests/edge.py', 'python3 tests/stress.py'] | killed |
| a486806b8f4ff4d7 | custom_components/heatpump_optimizer/thermal_model.py:4679 CLAMP_DROP | `floor_temp = np.minimum(T_upper, T_slab) -> floor_temp = (T_upper)` | KILLED ['python3 tests/stress.py'] | killed |
| 806f3255b74936a9 | custom_components/heatpump_optimizer/thermal_model.py:4690 CLAMP_DROP | `) / max(dt, 1e-6) -> ) / (dt)` | RED-AS-NULL  | equivalent-candidate |
| f2706cbdb16a8f66 | custom_components/heatpump_optimizer/thermal_model.py:4695 CLAMP_DROP | `* np.maximum(0.0, T_buf - floor_temp) -> * (0.0)` | KILLED ['python3 tests/edge.py'] | killed |
| 1108e8140e06404e | custom_components/heatpump_optimizer/thermal_model.py:4696 CLAMP_DROP | `/ max(dt, 1e-6) -> / (dt)` | RED-AS-NULL  | equivalent-candidate |
| 7068e39e4608027f | custom_components/heatpump_optimizer/thermal_model.py:4699 CLAMP_DROP | `w * drawn, np.maximum(avail_wood, 0.0) -> w * drawn, (avail_wood)` | RED-AS-NULL  | candidate |
| 6462c28df2f973e0 | custom_components/heatpump_optimizer/thermal_model.py:4702 CLAMP_DROP | `drawn - wood_draw, np.maximum(avail_hp, 0.0) -> drawn - wood_draw, (avail_hp)` | RED-AS-NULL  | candidate |
| daf153fda85092ff | custom_components/heatpump_optimizer/thermal_model.py:4711 CLAMP_DROP | `/ max(dt, 1e-6) -> / (dt)` | RED-AS-NULL  | equivalent-candidate |
| e5a0d6a548f12244 | custom_components/heatpump_optimizer/thermal_model.py:4714 CLAMP_DROP | `drawn, np.maximum(available, 0.0) -> drawn, (available)` | RED-AS-NULL  | equivalent-candidate |

## Candidates (gate survivors that change behaviour)

### 7068e39e4608027f - Batch two-tank wood draw clamp max(avail_wood, 0) is unpinned
Replacing `np.maximum(avail_wood, 0.0)` by `avail_wood` moves the batch trajectories by 0.0041 K (2 scenarios: two-tank, wood tank just below the floor temperature at zero power) and breaks parity with the scalar path, yet the full gate stays as red as the null.

- Production line: custom_components/heatpump_optimizer/thermal_model.py:4699 CLAMP_DROP, `w * drawn, np.maximum(avail_wood, 0.0) -> w * drawn, (avail_wood)`
- Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_7068e39e4608027f.py`: baseline_vs_mutant max abs diff = 0.00408045 K, batch-vs-scalar parity mutant 0.00408045 (baseline 0), null control 0.
- Step 4, the check that should have failed: tests/features.py `_grad_parity`: a two-tank cell where the wood tank is at or below the floor temperature so avail_wood < 0.
- Severity claimed: low; class_guess N-structure-blind.

### 6462c28df2f973e0 - Batch two-tank hp draw clamp max(avail_hp, 0) is unpinned
Replacing `np.maximum(avail_hp, 0.0)` by `avail_hp` moves the batch trajectories by 0.0166 K (4 scenarios: two-tank, buffer just below the floor temperature at zero power) and breaks parity with the scalar path, yet the full gate stays as red as the null.

- Production line: custom_components/heatpump_optimizer/thermal_model.py:4702 CLAMP_DROP, `drawn - wood_draw, np.maximum(avail_hp, 0.0) -> drawn - wood_draw, (avail_hp)`
- Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_6462c28df2f973e0.py`: baseline_vs_mutant max abs diff = 0.0166438 K, batch-vs-scalar parity mutant 0.0166438 (baseline 0), null control 0.
- Step 4, the check that should have failed: tests/features.py `_grad_parity`: a two-tank cell at zero power with the buffer at or below the floor temperature so avail_hp < 0.
- Severity claimed: low; class_guess N-structure-blind.

## Equivalent-candidates

- **f2ab25c56b407ef9** (custom_components/heatpump_optimizer/thermal_model.py:3389 CMP_BOUND, `if carnot_ref <= 1e-9: -> if carnot_ref < 1e-9:`): carnot_ref = (ref+273.15)/max(ref+273.15-t_out, 1.0) is >0 for any physical ref, so `<= 1e-9` and `< 1e-9` differ only at carnot_ref == 1e-9 bit-exactly. 576-point grid (ref 25..55, cop_reference_temp -7..12, outdoor -30..30, flow ref-1..60 and NaN): 0 moved; a scan of 4001 floats around ref=-273.15+1e-9 found none with ref+273.15 == 1e-9 exactly. (max diff 0)
- **d9a65b3770e6860a** (custom_components/heatpump_optimizer/thermal_model.py:4114 GUARD_OFF, `if n_sub == 1: -> if False:`): two-zone fast path `if n_sub == 1` -> `if False`: the loop path with n_sub == 1 does one _simulate_step_two_zone at dt/1 and divides the refused sums by 1; bit-identical. 108 step scenarios (n_sub histogram 1:38, 2:62, 7:4, 25:4) x six configs: 0 moved. (max diff 0)
- **7b46514aedc0a8cf** (custom_components/heatpump_optimizer/thermal_model.py:4571 BOOLOP, `start_hour is not None and p.internal_gains_profile is not None -> start_hour is not None or p.internal_gains_profile is not None`): `start_hour is not None and gains_profile is not None` -> `or`: hour_i then also exists when no profile is set, but it only reaches internal_gains_at, which returns the constant when profile is None (thermal_model.py:3535-3537). battery of 144 scenarios x 4 schedules: configs novalve/single-tank valve/two-tank 4-way (+wood)/valve_upper_direct_slab/smart_read two-tank/single-zone valve; states hot/cold/mid buffer, hot/cold wood, slab colder than upper floor, buffer just below the floor temperature, hot floors with cold buffer at zero power, ext heat, pmax 0/6/9, mild weather, dt 1 h/0.25/1e-4/1e-6/1e-7/0/-0.25, start_hour None/7/18, a 24-entry gains profile, valve targets: 0 moved. (max diff 0)
- **876be7bf2f538255** (custom_components/heatpump_optimizer/thermal_model.py:4578 BOOLOP, `if p.two_zone_enabled and throttled: -> if p.two_zone_enabled or throttled:`): `if p.two_zone_enabled and throttled` -> `or`: the extra branch only computes ua_rad/ua_floor, which are read only under the two-zone throttled branch. battery of 144 scenarios x 4 schedules: configs novalve/single-tank valve/two-tank 4-way (+wood)/valve_upper_direct_slab/smart_read two-tank/single-zone valve; states hot/cold/mid buffer, hot/cold wood, slab colder than upper floor, buffer just below the floor temperature, hot floors with cold buffer at zero power, ext heat, pmax 0/6/9, mild weather, dt 1 h/0.25/1e-4/1e-6/1e-7/0/-0.25, start_hour None/7/18, a 24-entry gains profile, valve targets: 0 moved. (max diff 0)
- **806f3255b74936a9** (custom_components/heatpump_optimizer/thermal_model.py:4690 CLAMP_DROP, `) / max(dt, 1e-6) -> ) / (dt)`): `/ max(dt, 1e-6)` -> `/ dt` in avail_wood: moves only at dt=0 (NaN from 0/0 or inf), 4 scenarios; every dt >= 1e-6 gives 0 moved. dt is the positive plan step in every production caller. (max diff inf)
- **1108e8140e06404e** (custom_components/heatpump_optimizer/thermal_model.py:4696 CLAMP_DROP, `/ max(dt, 1e-6) -> / (dt)`): `/ max(dt, 1e-6)` -> `/ dt` in avail_hp (wood branch): differs only for dt <= 1e-6. battery of 144 scenarios x 4 schedules: configs novalve/single-tank valve/two-tank 4-way (+wood)/valve_upper_direct_slab/smart_read two-tank/single-zone valve; states hot/cold/mid buffer, hot/cold wood, slab colder than upper floor, buffer just below the floor temperature, hot floors with cold buffer at zero power, ext heat, pmax 0/6/9, mild weather, dt 1 h/0.25/1e-4/1e-6/1e-7/0/-0.25, start_hour None/7/18, a 24-entry gains profile, valve targets: 0 moved, dt=0 and dt=1e-7 included; production dt_hours is the plan step (>0). (max diff 0)
- **daf153fda85092ff** (custom_components/heatpump_optimizer/thermal_model.py:4711 CLAMP_DROP, `/ max(dt, 1e-6) -> / (dt)`): `/ max(dt, 1e-6)` -> `/ dt` in avail (non-wood): moves only at dt=0 (2 scenarios, max abs diff 2.55e8 = inf/NaN propagation); every dt >= 1e-6 gives 0 moved. dt is the positive plan step in every production caller. (max diff 2.55385e+08)
- **e5a0d6a548f12244** (custom_components/heatpump_optimizer/thermal_model.py:4714 CLAMP_DROP, `drawn, np.maximum(available, 0.0) -> drawn, (available)`): `min(drawn, max(available, 0))` -> `min(drawn, available)` in the non-wood branch: battery of 144 scenarios x 4 schedules: configs novalve/single-tank valve/two-tank 4-way (+wood)/valve_upper_direct_slab/smart_read two-tank/single-zone valve; states hot/cold/mid buffer, hot/cold wood, slab colder than upper floor, buffer just below the floor temperature, hot floors with cold buffer at zero power, ext heat, pmax 0/6/9, mild weather, dt 1 h/0.25/1e-4/1e-6/1e-7/0/-0.25, start_hour None/7/18, a 24-entry gains profile, valve targets: 0 moved, including hot floors (45 C) over a 40 C buffer at zero power, where available < 0 and drawn == 0. (max diff 0)

## Killed (non-findings)

- **97bd985754f1099b** (custom_components/heatpump_optimizer/thermal_model.py:4140 GUARD_OFF): killed_by ['python3 tests/stress.py'], wall 3725.7 s
- **cc34cacdd80553ed** (custom_components/heatpump_optimizer/thermal_model.py:4553 GUARD_OFF): killed_by ['python3 tests/edge.py'], wall 3724.5 s
- **a3f2b00cc4aa527e** (custom_components/heatpump_optimizer/thermal_model.py:4668 CLAMP_DROP): killed_by ['python3 tests/edge.py', 'python3 tests/stress.py'], wall 3791.4 s
- **a486806b8f4ff4d7** (custom_components/heatpump_optimizer/thermal_model.py:4679 CLAMP_DROP): killed_by ['python3 tests/stress.py'], wall 3637.0 s
- **f2706cbdb16a8f66** (custom_components/heatpump_optimizer/thermal_model.py:4695 CLAMP_DROP): killed_by ['python3 tests/edge.py'], wall 3598.9 s

## Incidents and caveats

- tools/audit/seat/gate_lock / fullgate.py: a stale zero-byte worktree index.lock (created 13:48Z, 15 min into the gate of a3f2b00cc4aa527e, source unknown: no git process of this seat held it) made fullgate's finally `git reset` fail; gate_wave.sh then recorded keys a3f2b00cc4aa527e, a486806b8f4ff4d7 and 806f3255b74936a9 as TIMEOUT without running them (REFUSE: HEAD is not the baseline). The lock was removed, the three bogus records discarded (kept under $HOME/aborted on the box, not in this report) and the three keys re-gated in full; the reported verdicts are the re-runs.
- Probes ran concurrently with gate 1 (`f2ab25c56b407ef9`; load1 peaked about 4.4); its recorded load1 end was 0.95 and its verdict is the same RED-AS-NULL as the null's failing set, but treat its timing as provisional. No probe ran during any other gate.
- The batch probes' scenario batteries and every input tried are in `probes/_blib.py` (default_battery, 144 scenarios); simulate_step keys use a 108-scenario step battery (n_sub 1, 2, 7, 25).
- findings is empty by the wave's rule: the orchestrator assigns ids across boxes; candidates are under gate_survivors.

Harnesses: dev/audit/rounds/round11/D3/s1/fullgate.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/_blib.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/gate_wave.sh, dev/audit/rounds/round11/D3/s1/wave/D3-g43/write_results.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/runprobes.sh, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_f2ab25c56b407ef9.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_d9a65b3770e6860a.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_97bd985754f1099b.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_cc34cacdd80553ed.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_7b46514aedc0a8cf.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_876be7bf2f538255.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_a3f2b00cc4aa527e.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_a486806b8f4ff4d7.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_806f3255b74936a9.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_f2706cbdb16a8f66.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_1108e8140e06404e.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_7068e39e4608027f.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_6462c28df2f973e0.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_daf153fda85092ff.py, dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_e5a0d6a548f12244.py
