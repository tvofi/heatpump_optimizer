# D3-s1 round 11, box D3-g22: the full gate for 16 D3.M3 full-net survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Tree: a `prepare_baseline.sh --strip` worktree plus the D3-s1 evidence from e3cb5c0. Each gate: `fullgate.py run --src complete --key <key>` (one-line mutant committed, gate_lock lease, `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=92d38ecb640bd462f2e19c0814d0f0b7df1ee692 GATE_JOBS=1 ./tests/run.sh`, reset), driven one at a time by the dispatch's `gate_wave.sh run` (4 h cap, TIMEOUT never read as KILLED). Probes ran from a separate clean baseline worktree, never in the gate's tree, each mutant applied in memory.

## Machine and controls

```
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087        1077       13506          12        1801       15010
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 1.27
Sun Nov 22 21:40:44 UTC 2026

## re-fire 2026-11-25T00:51:53Z (resumed from wip 99e9528e62; gate 6ab21fd9f9fe4953 was running at the stall and is re-taken)
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087         727       14085          12        1545       15359
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.42
python3: /opt/hpo/venv-ci/bin/python3 (symlinked at $HOME/venv-ci, out of tree)
```

Null control (`fullgate.py null`, comment-only marker): gate_rc 1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], FAIL counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 4325.5 s (load1 0.91 -> 0.98). Walls and loads are provisional.

Reach census: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/reach_scan.py` (7 real solves of features.py's v5.3.0 January scenario: plain, space-blocked, DHW-blocked, 3.6 kW cap, 0.05 kW cap, PV surplus, forced-off pins) records the shapes each instrumented method receives.

## Tally

gated 16 of 16; RED-AS-NULL 16; candidates 2; equivalent-candidates 14; TIMEOUT 0.

| key | site | verdict | gate_rc | wall s | class |
|---|---|---|---|---|---|
| ea0b9abd134c33cd | custom_components/heatpump_optimizer/optimizer.py:6497 CMP_BOUND | RED-AS-NULL | 1 | 3826.9 | equivalent-candidate |
| fa67e0922f51edda | custom_components/heatpump_optimizer/optimizer.py:6498 CMP_BOUND | RED-AS-NULL | 1 | 3852.4 | equivalent-candidate |
| ef9a378b671791ca | custom_components/heatpump_optimizer/optimizer.py:6504 CLAMP_DROP | RED-AS-NULL | 1 | 3829.4 | candidate |
| 1897b1e8f0e09c02 | custom_components/heatpump_optimizer/optimizer.py:6509 CLAMP_DROP | RED-AS-NULL | 1 | 3843.4 | equivalent-candidate |
| c859178ad2524ff8 | custom_components/heatpump_optimizer/optimizer.py:4876 CMP_BOUND | RED-AS-NULL | 1 | 3847.0 | equivalent-candidate |
| e658b77d3e5ca8f6 | custom_components/heatpump_optimizer/optimizer.py:4879 CMP_BOUND | RED-AS-NULL | 1 | 3883.1 | equivalent-candidate |
| 6ab21fd9f9fe4953 | custom_components/heatpump_optimizer/optimizer.py:4908 BOOLOP | RED-AS-NULL | 1 | 3678.7 | equivalent-candidate |
| 1d0c70b3b63230eb | custom_components/heatpump_optimizer/optimizer.py:4913 CMP_BOUND | RED-AS-NULL | 1 | 3599.2 | equivalent-candidate |
| d600d4886444a718 | custom_components/heatpump_optimizer/optimizer.py:4914 CLAMP_DROP | RED-AS-NULL | 1 | 3640.2 | equivalent-candidate |
| 6e420d1efdf4895b | custom_components/heatpump_optimizer/optimizer.py:4915 CMP_BOUND | RED-AS-NULL | 1 | 3664.0 | equivalent-candidate |
| 7da20bf51cc217e6 | custom_components/heatpump_optimizer/optimizer.py:4917 CLAMP_DROP | RED-AS-NULL | 1 | 3613.1 | candidate |
| 1f1dc504455f17da | custom_components/heatpump_optimizer/optimizer.py:5699 CMP_BOUND | RED-AS-NULL | 1 | 3724.4 | equivalent-candidate |
| 9fe0782a9839475e | custom_components/heatpump_optimizer/optimizer.py:5701 CLAMP_DROP | RED-AS-NULL | 1 | 3930.9 | equivalent-candidate |
| 7c2ae6b70ec6acb7 | custom_components/heatpump_optimizer/optimizer.py:5693 CMP_BOUND | RED-AS-NULL | 1 | 4159.8 | equivalent-candidate |
| 97da0984453a53bb | custom_components/heatpump_optimizer/optimizer.py:5222 CMP_BOUND | RED-AS-NULL | 1 | 3993.9 | equivalent-candidate |
| af94ce8be7140e87 | custom_components/heatpump_optimizer/optimizer.py:5225 CMP_BOUND | RED-AS-NULL | 1 | 3882.1 | equivalent-candidate |

## Survivors (step-4 answers with probe numbers)

### ea0b9abd134c33cd — custom_components/heatpump_optimizer/optimizer.py:6497 CMP_BOUND (equivalent-candidate)

Patch `out_t = outdoor_temps[i] if i < len(outdoor_temps) else outdoor_temps[-1] -> out_t = outdoor_temps[i] if i <= len(outdoor_temps) else outdoor_temps[-1]` in `HeatPumpOptimizer._power_to_displace_schedule`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_ea0b9abd.py`: baseline short_outdoor (power 4, outdoor 3): 4 values (pads with outdoor[-1]); mutant IndexError. Inputs tried: power 4 / outdoor 3 (moves: 4 -> IndexError); power 48 / outdoor 48 linspace (equal_len_delta=0); 7 real solves (reach_scan.py: disp_outdoor_shorter_than_power=0). Answer: unreachable through production: the one caller (optimizer.py:3881) passes h.outdoor_temps and space_power, both n_steps long, so the padding branch never runs (reach 0 of 7 real solves). Check that should have failed: tests/features.py (R9-F2.1 P3 block, ~68727) calls _power_to_displace_schedule only with equal-length series; no check passes an outdoor series shorter than the power schedule.

### fa67e0922f51edda — custom_components/heatpump_optimizer/optimizer.py:6498 CMP_BOUND (equivalent-candidate)

Patch `if out_t < 0: -> if out_t <= 0:` in `HeatPumpOptimizer._power_to_displace_schedule`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_fa67e092.py`: baseline max_abs_delta=0.0 displace; mutant identical. Inputs tried: out_t 0.0, -0.0, 1e-300, -1e-300, 5e-324, nan, -10, 5 x power zeros / 3 kW / ramp (24 cells). Answer: equivalent mutant: at out_t == 0 the branch adds min(2, |0|*0.08) = 0.0. Check that should have failed: none: no check can distinguish (equivalent).

### ef9a378b671791ca — custom_components/heatpump_optimizer/optimizer.py:6504 CLAMP_DROP (candidate)

Patch `alpha = float(np.clip(self.config.dt_hours / tau, 0.0, 1.0)) -> alpha = float((self.config.dt_hours / tau))` in `HeatPumpOptimizer._power_to_displace_schedule`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_ef9a378b.py`: baseline tau 0.01 h (alpha 2.5 unclipped): [-19.6 x4, 20.0 x8, -19.6 x12]; mutant alternating -20.0 / 20.0 every step; max_abs_delta=40.0 displace, steps_moved=20 of 24. Inputs tried: tau 0.01/0.1 h (alpha 2.5): delta 40.0, 20 steps; tau 0.2 h (alpha 1.25): delta 2.5, 10 steps; tau 0.25 h (config-flow floor, alpha 1.0): delta 0.0; tau 1.5 h (default): delta 0.0. Answer: moves on a set_thermal_parameters input the service admits (ecl110_pid_time_constant_hours >= 0.01 h, services.py:516, mapped at coordinator.py:2739, floored to 0.1 h at thermal_model.py:725; the step is a fixed 15 min), and the schedule is the ECL110 displace command get_current_action reads (optimizer.py:6581-6585). Check that should have failed: tests/features.py: no check drives _power_to_displace_schedule with ecl110_pid_tau_hours below dt_hours (features.py:50928 sets 0.6 h, alpha 0.42; the R9-F2.1 block ~68727 uses the default 1.5 h); the assertion it lacks: with tau < dt the filtered schedule equals the clipped raw command (alpha clamped to 1), i.e. no step-to-step overshoot.

Candidate: **No check runs the ECL110 displace filter with a PID time constant below the 15-min step; dropping the alpha clamp is unseen** (severity claimed medium, class_guess I1). Metric: max |baseline - mutant| of the published displace schedule (displace units) for a 0 -> max -> 0 power step at -5 C with ecl110_pid_time_constant_hours = 0.01 h (alpha 2.5). Null: tau 1.5 h (default) and 0.25 h (config-flow floor): 0.0 displace. Id left to consolidation.

### 1897b1e8f0e09c02 — custom_components/heatpump_optimizer/optimizer.py:6509 CLAMP_DROP (equivalent-candidate)

Patch `filtered.append(round(float(np.clip(effective, d_min, d_max)), 1)) -> filtered.append(round(float((effective)), 1))` in `HeatPumpOptimizer._power_to_displace_schedule`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1897b1e8.py`: baseline admitted windows: max_abs_delta=0.0 over 576 cells; mutant refused windows (d_min 2 / d_max -2): max_abs_delta=2.0. Inputs tried: windows (-20,20) (-30,0) (0,30) (0,0) (-0.5,0.5) (-30,30) x tau 0.01/0.25/1.5/24 h x 4 power x 3 outdoor x 2 forecast factors: delta 0.0; windows (2,10) and (-10,-2), refused by config flow and service: delta 2.0. Answer: equivalent on every window the config flow (config_flow.py:1888, [-30,0] / [0,30]) and the service (services.py:517-522) admit: alpha is clipped to [0,1] at line 6504 and the EWMA starts at 0, which every admitted window contains, so it never leaves the window; it moves only for a window excluding 0. Check that should have failed: none reachable: a check would need a displace window excluding 0, which no input surface admits.

### c859178ad2524ff8 — custom_components/heatpump_optimizer/optimizer.py:4876 CMP_BOUND (equivalent-candidate)

Patch `planned = trajectory[1:] if trajectory.size > n_steps else trajectory -> planned = trajectory[1:] if trajectory.size >= n_steps else trajectory` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_c859178a.py`: baseline n-long trajectory breaching at step 0: power_cap_breach_c=1.0; mutant 0.0. Inputs tried: trajectory n long (moves 1.0 -> 0.0); trajectory n+1 long (null_delta=0); 7 real solves (reach_scan.py: breach_traj_eq_n=0). Answer: unreachable through production: result.sensor_trajectory carries n+1 entries in every solve (traj 49 for n 48). Check that should have failed: none reachable: the n-long trajectory is never produced.

### e658b77d3e5ca8f6 — custom_components/heatpump_optimizer/optimizer.py:4879 CMP_BOUND (equivalent-candidate)

Patch `if steps > 0: -> if steps >= 0:` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_e658b77d.py`: baseline empty temp_min_bounds: power_cap_breach_c=0.0; mutant ValueError (np.max of an empty array). Inputs tried: temp_min_bounds [] with n 0 (moves); 4-step plan with bounds (null_delta=0); 7 real solves (reach_scan.py: tmin 48, traj 49). Answer: unreachable through production: steps = min(n, n) >= 1 in every solve. Check that should have failed: none reachable: steps == 0 needs an empty horizon.

### 6ab21fd9f9fe4953 — custom_components/heatpump_optimizer/optimizer.py:4908 BOOLOP (equivalent-candidate)

Patch `if requirement is not None and dhw_trajectory: -> if requirement is not None or dhw_trajectory:` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_6ab21fd9.py`: baseline requirement None + DHW trajectory set: dhw_floor_breach_c=0.0; mutant IndexError. Inputs tried: 4 cells requirement None/set x trajectory []/set (cells_moved=1: requirement None with a trajectory); real solve, DHW-disabled install with dhw_blocked=True (requirement None, trajectory []): 0.0 both arms. Answer: unreachable through production: a DHW trajectory comes only from the DHW solve, which sets _dhw_requirement in the same pass (optimizer.py:5747); the reachable requirement-None case (DHW off, mode blocks hot water) has an empty trajectory and publishes 0.0 under both arms (reach_scan.py: breach_dhw_req_none_with_traj=0). Check that should have failed: none reachable.

### 1d0c70b3b63230eb — custom_components/heatpump_optimizer/optimizer.py:4913 CMP_BOUND (equivalent-candidate)

Patch `planned = planned[1:] if planned.size > req.size else planned -> planned = planned[1:] if planned.size >= req.size else planned` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1d0c70b3.py`: baseline DHW trajectory as long as the requirement, short at step 0: dhw_floor_breach_c=5.0; mutant 0.0. Inputs tried: trajectory n / requirement n (moves 5.0 -> 0.0); trajectory n+1 / requirement n (null_delta=0); 7 real solves (reach_scan.py: breach_dhw_traj_eq_req=0). Answer: unreachable through production: the DHW trajectory carries n+1 entries against an n-entry requirement. Check that should have failed: none reachable.

### d600d4886444a718 — custom_components/heatpump_optimizer/optimizer.py:4914 CLAMP_DROP (equivalent-candidate)

Patch `steps = min(planned.size, req.size) -> steps = (planned.size)` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_d600d488.py`: baseline trajectory n+2 / requirement n: dhw_floor_breach_c=2.0; mutant ValueError (broadcast). Inputs tried: trajectory n+2 (moves); trajectory n+1 (null_delta=0); trajectory shorter than requirement (delta 0); 7 real solves (reach_scan.py: breach_dhw_planned_longer_than_req_after_trim=0). Answer: unreachable through production: after the index-0 trim the trajectory and requirement are both n long. Check that should have failed: none reachable.

### 6e420d1efdf4895b — custom_components/heatpump_optimizer/optimizer.py:4915 CMP_BOUND (equivalent-candidate)

Patch `if steps > 0: -> if steps >= 0:` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_6e420d1e.py`: baseline empty requirement: dhw_floor_breach_c=0.0; mutant ValueError. Inputs tried: requirement [] (moves); one-entry trajectory (trimmed? no: size 1 not > 4; steps 1; delta 0); production shape (null_delta=0). Answer: unreachable through production: the requirement carries n_steps >= 1 entries (reach_scan.py req 48). Check that should have failed: none reachable.

### 7da20bf51cc217e6 — custom_components/heatpump_optimizer/optimizer.py:4917 CLAMP_DROP (candidate)

Patch `np.max(np.clip(req[:steps] - planned[:steps], 0.0, None)) -> np.max((req[:steps] - planned[:steps]))` in `HeatPumpOptimizer._publish_breach_reports`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_7da20bf5.py`: baseline real DHW-blocked solve, tank 60 C: dhw_floor_breach_c=0.0 (tank 65 C: 0.0); mutant tank 60 C: -1.394; tank 65 C: -5.908. Inputs tried: tank 45 C: 11.739 both arms (null); tank 55 C: 3.121 both arms; tank 60 C: 0.0 -> -1.394; tank 65 C: 0.0 -> -5.908. Answer: moves in a real HeatPumpOptimizer.optimize with SolveLimits.dhw_blocked=True (a pump-mode entity in a heating-only mode) whenever the tank coasts above its requirement; the method's own comment documents "zero when the tank coasted through anyway". Check that should have failed: tests/features.py v5.3.0 mode-block section (_mb_dhw = _mb_run(dhw_blocked=True), ~36841): its checks read dhw_power_schedule, power_schedule, dhw_reasons and mode_blocked_* but never predictive_info['dhw_floor_breach_c']; no script in the closure reads the key (grep dhw_floor_breach tests/ is empty). The assertion it lacks: a DHW-blocked plan whose tank stays above its requirement publishes dhw_floor_breach_c == 0.0 (and >= 0 always).

Candidate: **No check reads dhw_floor_breach_c; a DHW-blocked plan could publish a negative tank shortfall unseen** (severity claimed low, class_guess I1). Metric: dhw_floor_breach_c (C) published by a real DHW-blocked solve (features.py v5.3.0 January scenario) with the tank starting at 60 C. Null: tank 45 C (a real shortfall, 11.739 C both arms): 0.0 C. Id left to consolidation.

### 1f1dc504455f17da — custom_components/heatpump_optimizer/optimizer.py:5699 CMP_BOUND (equivalent-candidate)

Patch `if self._pv_surplus is None or not np.any(self._pv_surplus > 1e-6): -> if self._pv_surplus is None or not np.any(self._pv_surplus >= 1e-6):` in `HeatPumpOptimizer._pv_self_consumed`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1f1dc504.py`: baseline max_abs_delta=0.0 kWh; mutant identical at the published 3 dp. Inputs tried: surplus exactly 1e-6 everywhere / at one step, 0, 9.99e-7, 1.01e-6, 3 kW x power 0 / 6 kW / ramp x dt 0.25 / 1.0 (36 cells). Answer: equivalent at the published value: only a surplus of exactly 1e-6 kW differs and its served energy, at most n*1e-6*dt kWh, rounds to 0.000. Check that should have failed: none: no published value distinguishes.

### 9fe0782a9839475e — custom_components/heatpump_optimizer/optimizer.py:5701 CLAMP_DROP (equivalent-candidate)

Patch `n = min(len(power), len(self._pv_surplus)) -> n = (len(power))` in `HeatPumpOptimizer._pv_self_consumed`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_9fe0782a.py`: baseline power 10 / surplus 8: 1.5 kWh; mutant ValueError (broadcast). Inputs tried: power longer than surplus (moves); power shorter (delta 0); 48/48 (null_delta=0.0); 7 real solves (reach_scan.py: pvsc_power_longer_than_surplus=0). Answer: unreachable through production: _prepare_series slices/pads the surplus to exactly n_steps (optimizer.py:4695-4707) and every caller passes an n_steps power schedule. Check that should have failed: none reachable.

### 7c2ae6b70ec6acb7 — custom_components/heatpump_optimizer/optimizer.py:5693 CMP_BOUND (equivalent-candidate)

Patch `if not np.any(self._pv_surplus > 1e-6): -> if not np.any(self._pv_surplus >= 1e-6):` in `HeatPumpOptimizer._pv_surplus_list`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_7c2ae6b7.py`: baseline surplus max exactly 1e-6 kW: pv_surplus [] (each forecast step's pv_surplus null); mutant [0.0] * 48. Inputs tried: exactly 1e-6 everywhere (moves: [] -> 48 x 0.0); zeros, 9.99e-7, 1.01e-6, 3 kW block (null_delta=0). Answer: moves only when the surplus maximum is exactly 1e-6 kW (1 mW), a measure-zero value of clip(production - load, 0) (pv.py:80-91); its consequence is a published 0.0 instead of null per step; recorded as equivalent-candidate with the moving input disclosed so a later seat may promote it. Check that should have failed: none practical: a check would pin the threshold's tie at 1e-6.

### 97da0984453a53bb — custom_components/heatpump_optimizer/optimizer.py:5222 CMP_BOUND (equivalent-candidate)

Patch `temp = room[i + 1] if i + 1 < len(room) else room[-1] -> temp = room[i + 1] if i + 1 <= len(room) else room[-1]` in `HeatPumpOptimizer._safety_release_steps`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_97da0984.py`: baseline room trajectory n long, forced-off pins at the floor: space releases [0, 1, 2]; mutant IndexError. Inputs tried: room n long (moves); room n+1 long (null_delta=0); real pinned solve (reach_scan.py pins_off arm: rel_room_not_n_plus_1=0). Answer: unreachable through production: the loop runs i < n and the room trajectory has n+1 entries, so i + 1 <= n < len(room) and the else-branch never runs. Check that should have failed: none reachable.

### af94ce8be7140e87 — custom_components/heatpump_optimizer/optimizer.py:5225 CMP_BOUND (equivalent-candidate)

Patch `if i < len(temp_min_bounds) -> if i <= len(temp_min_bounds)` in `HeatPumpOptimizer._safety_release_steps`. Gate RED-AS-NULL (gate_rc 1). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_af94ce8b.py`: baseline temp_min_bounds n-1 long: space releases [0, 1, 2]; mutant IndexError. Inputs tried: bounds n-1 long (moves); bounds n long (null_delta=0); real pinned solve (reach_scan.py: rel_bounds_shorter_than_power=0). Answer: unreachable through production: temp_min_bounds carries n_steps entries for an n-step power schedule. Check that should have failed: none reachable.


## Coverage

D3.M3: enumerator `awk -F'\t' '$6=="gate"' SURVIVORS.tsv` (742 keys), examined 16 here; not reached: the other 46 boxes' keys (assigned to boxes D3-g01..D3-g47 but this one). D3.M1, D3.M2, D3.M4, D3.M5 carried verbatim from REPORT-D3-u1b.json.

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/breach_rig.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/g22_rig.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1897b1e8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1d0c70b3.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_1f1dc504.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_6ab21fd9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_6e420d1e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_7c2ae6b7.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_7da20bf5.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_97da0984.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_9fe0782a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_af94ce8b.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_c859178a.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_d600d488.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_e658b77d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_ea0b9abd.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_ef9a378b.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/probe_fa67e092.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/reach_scan.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/build_results.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g22/build_report.py`
- the dispatch's `gate_wave.sh` (out of tree): null, then `run` over keys.tsv, one gate at a time, ckpt after each

## Unfinished

- none

## Exposure

none (no docs/, GitHub or register read).

