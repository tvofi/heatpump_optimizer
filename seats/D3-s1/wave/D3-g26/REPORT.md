# Round 11 D3-s1, box D3-g26: full gate of 16 D3.M3 full-net survivors

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Every count below is final; every wall, CPU and load number is provisional (nproc 4; the judge re-takes it).

## Machine and controls

```
date 2026-11-22T21:43:17Z
nproc 4
model name	: Intel(R) Xeon(R) Processor @ 2.30GHz
               total        used        free      shared  buff/cache   available
Mem:           16087        1107       13476          12        1801       14980
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1 0.73
--- resumed container
date 2026-11-25T00:51:26Z
nproc 4
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087         789       14013          12        1557       15297
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.45
```

Null control (`fullgate.py null`, a comment-only marker, through `gate_wave.sh null`): gate_rc 1, wall 2899.6 s, load1 0.62..1.04, red scripts python3 tests/closure.py selftest, python3 tests/entities.py, python3 tests/harness_headers.py with fail lines {"python3 tests/closure.py selftest": 2, "python3 tests/entities.py": 1, "python3 tests/harness_headers.py": 3}. All three are artefact checks reading no production file (closure.py selftest merge-tool pins, entities.py branch environment, harness_headers.py on a round-4 D6 harness whose docs the finder-wall strip removes); the same three as D3-rem's usable null. Usable, not re-taken. A key is KILLED only on a red script beyond this null or more FAIL lines in one.

Procedure: `gate_wave.sh run` (the dispatch ref's driver) runs `fullgate.py run --src complete --key <key>` (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh) for each key of keys.tsv in order, one gate at a time, capped at 4 h. Probes run in a separate baseline worktree (never the gate's tree), each applying its one-line mutant in memory and printing `RESULT <metric>=<value>` for the baseline and the mutant.

This box was resumed: a predecessor seat on another container took the null and the first nine gates and wrote the probes; this seat restored them from the wip checkpoint, re-ran the nine probes (identical RESULT values) and took the remaining gates.

## Tally

- gated: 16/16
- KILLED: 1 (python3 tests/stress.py: 1)
- SURVIVED: 0
- RED-AS-NULL: 15
- TIMEOUT: 0
- candidates (gate survivors whose probe moves): 9
- equivalent-candidates: 6

| key | site | verdict | killed_by | class |
|---|---|---|---|---|
| 35d104f30f878131 | custom_components/heatpump_optimizer/optimizer.py:6661 GUARD_OFF | RED-AS-NULL | - | candidate |
| ec173cf0e67c0689 | custom_components/heatpump_optimizer/optimizer.py:4518 GUARD_OFF | KILLED | python3 tests/stress.py | killed |
| f56e3474baa75dc5 | custom_components/heatpump_optimizer/optimizer.py:4528 GUARD_OFF | RED-AS-NULL | - | candidate |
| 1721e50b7537a426 | custom_components/heatpump_optimizer/optimizer.py:4532 GUARD_OFF | RED-AS-NULL | - | candidate |
| 2693e4fc04518cbf | custom_components/heatpump_optimizer/optimizer.py:4560 BOOLOP | RED-AS-NULL | - | candidate |
| ee671fa6ecec9023 | custom_components/heatpump_optimizer/optimizer.py:4560 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| 9a06a1a7e515fa67 | custom_components/heatpump_optimizer/optimizer.py:4610 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| 977021e3b3964277 | custom_components/heatpump_optimizer/optimizer.py:2782 GUARD_OFF | RED-AS-NULL | - | candidate |
| 10de422e4e1024a7 | custom_components/heatpump_optimizer/optimizer.py:2786 GUARD_OFF | RED-AS-NULL | - | candidate |
| e4affa9b9b540588 | custom_components/heatpump_optimizer/optimizer.py:2788 RETURN_DEL | RED-AS-NULL | - | candidate |
| 0fcdd4bdabc205ea | custom_components/heatpump_optimizer/optimizer.py:2794 GUARD_OFF | RED-AS-NULL | - | candidate |
| 8365c2592bae9886 | custom_components/heatpump_optimizer/optimizer.py:2796 GUARD_OFF | RED-AS-NULL | - | candidate |
| 65b62179a34d3443 | custom_components/heatpump_optimizer/optimizer.py:2823 GUARD_OFF | RED-AS-NULL | - | equivalent-candidate |
| 67ac7292ac5ddd19 | custom_components/heatpump_optimizer/optimizer.py:2825 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| cfda6ca73c6951f1 | custom_components/heatpump_optimizer/optimizer.py:2825 GUARD_OFF | RED-AS-NULL | - | equivalent-candidate |
| c2896572788698c0 | custom_components/heatpump_optimizer/optimizer.py:2412 CLAMP_DROP | RED-AS-NULL | - | equivalent-candidate |

## Survivors: step-4 answers

### 35d104f30f878131 (candidate) — custom_components/heatpump_optimizer/optimizer.py:6661 GUARD_OFF

`if result.predictive_info: -> if False:` in `HeatPumpOptimizer.get_current_action`. Gate RED-AS-NULL (gate_rc 1, wall 2775.1 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_35d104f30f878131.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_35d104f30f878131.py`): predictive_keys (predictive keys in the current action (of 3)) baseline 3 count  {'solar_reduction_factor': np.float64(0.99), 'wind_anticipation_factor': 1.06, 'pre_heat_urgency': np.float64(0.16)}, mutant 0 count  {'solar_reduction_factor': None, 'wind_anticipation_factor': None, 'pre_heat_urgency': None}. Inputs tried: winter_typical/winter_cold solved plan, step 0 (25 predictive_info keys): 3 -> 0 keys; ECL110 context pre_heat_urgency 0.16 -> None; null: same plan with predictive_info emptied (0 -> 0). Should fail: tests/features.py (also tests/entities.py, tests/config_flow_steps.py execute the line): no check asserts get_current_action carries solar_reduction_factor / wind_anticipation_factor / pre_heat_urgency for a plan with predictive_info, nor that the ECL110 legacy command context carries pre_heat_urgency. Candidate: No check reads the predictive keys of the current action; dropping the block that adds them is unseen.

### f56e3474baa75dc5 (candidate) — custom_components/heatpump_optimizer/optimizer.py:4528 GUARD_OFF

`if space_pins is not None: -> if False:` in `HeatPumpOptimizer.optimize`. Gate RED-AS-NULL (gate_rc 1, wall 2769.2 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_f56e3474baa75dc5.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_f56e3474baa75dc5.py`): released_space (space steps reported released) baseline 4 count, mutant 28 count. Inputs tried: cold winter house, space pins off at 0-23 (safe) and 80-83 (breaching): released 4 -> 28, solves 2 -> 5; null: summer house, space pins all off: released delta 0. Should fail: tests/manual_plan.py (also tests/features.py executes the line): test_safety_release forces EVERY space step off (np.zeros(N)), so per-block release and wholesale abandonment release the same set; no case has a non-breaching off-block beside a breaching one asserting only the breaching block is released. Candidate: No check pins that only the breaching space off-block is released; the per-round space pin release is unseen.

### 1721e50b7537a426 (candidate) — custom_components/heatpump_optimizer/optimizer.py:4532 GUARD_OFF

`if dhw_pins is not None: -> if False:` in `HeatPumpOptimizer.optimize`. Gate RED-AS-NULL (gate_rc 1, wall 2796.4 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_1721e50b7537a426.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_1721e50b7537a426.py`): released_dhw (DHW steps reported released) baseline 48 count, mutant 56 count. Inputs tried: low tank 40 C, DHW pins off at 0-47 (breaching) and 88-95 (safe): released 48 -> 56, solves 2 -> 5; DHW pins all off: released 88 -> 96; null: summer house tank 54 C, DHW off at 88-95: released delta 0. Should fail: tests/manual_plan.py (also tests/features.py executes the line): test_safety_release's low-tank case forces every DHW step off and asserts only len(manual_released_dhw) > 0; no case asserts which DHW steps are released (a non-breaching off-block must stay pinned). Candidate: No check pins which DHW off-steps the safety release frees; the per-round DHW pin release is unseen.

### 2693e4fc04518cbf (candidate) — custom_components/heatpump_optimizer/optimizer.py:4560 BOOLOP

`if not _pin_is_free(value) and value < 0.5: -> if not _pin_is_free(value) or value < 0.5:` in `HeatPumpOptimizer.optimize`. Gate RED-AS-NULL (gate_rc 1, wall 2862.6 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_2693e4fc04518cbf.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_2693e4fc04518cbf.py`): released (space steps reported released) baseline 88 count, mutant 96 count. Inputs tried: out-of-rounds abandonment (manual_plan.py's own never_satisfied stub), space pins ON at 0-7, OFF at 8-95: released 88 -> 96; pins all off as in test_release_always_resolves: 96 -> 96 (no move); free NaN pins: never released in either arm; reach: build_override/channel_pins/_normalise_pins emit pins {0.0, 1.0}: forced-on pins are production input. Should fail: tests/manual_plan.py (the only script whose traced baseline executes line 4560): test_release_always_resolves abandons a plan of ALL-off pins (np.zeros(N)) and asserts len(manual_released_space) == N; no case mixes forced-on pins and asserts they stay pinned (released count == forced-off count). Candidate: No check abandons a plan holding forced-on pins; and->or in the wholesale release is unseen.

### 977021e3b3964277 (candidate) — custom_components/heatpump_optimizer/optimizer.py:2782 GUARD_OFF

`if self.holiday_comfort_night is not None: -> if False:` in `OptimizationConfig._comfort_pair`. Gate RED-AS-NULL (gate_rc 1, wall 3852.4 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_977021e3b3964277.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_977021e3b3964277.py`): hours_moved_total (hourly comfort targets moved over two holiday days) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 24 count. Inputs tried: holiday Wednesday and holiday Saturday with holiday_comfort_night 17.0 (weekday night 19.5): night 17.0 -> 19.5, 12 hours each, 24 moved; plain Saturday (weekend overrides): 0; null plain Wednesday: 0. Should fail: tests/features.py (also tests/entities.py executes the line): no check configures holiday_comfort_night and asserts _comfort_pair / get_comfort_temp returns it at a night hour of a holiday date. Gate takes: first take KILLED by a stress.py wall-time self-test line on a scenario that never reaches the line; re-taken once alone: RED-AS-NULL. The recorded verdict is the re-take's; both takes are kept. take 1: KILLED (gate_rc 1, wall 2741.1 s, load1 0.79..0.85) -- timing artefact: the one extra FAIL line is stress.py's own per-call-cost self-test ('the per-call-cost arm reaches the rule the sweep applies ... (round-5 D9-07)', winter/1z/space: 41 ms plain vs 23 ms plain again, x0.56; evaluations 42 vs 42, simulate 131232 vs 131232) -- its two plain arms disagree, its count channels are flat, and its scenario sets no holiday date, so it never takes the mutated branch | take 2: RED-AS-NULL (gate_rc 1, wall 3852.4 s, load1 0.35..1.0) -- re-taken once, alone on the machine, after every other gate finished: red only on the null's three scripts. Candidate: No check reads the holiday night comfort override; ignoring holiday_comfort_night is unseen.

### 10de422e4e1024a7 (candidate) — custom_components/heatpump_optimizer/optimizer.py:2786 GUARD_OFF

`if self.holiday_day_end_hour is not None: -> if False:` in `OptimizationConfig._comfort_pair`. Gate RED-AS-NULL (gate_rc 1, wall 2795.3 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_10de422e4e1024a7.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_10de422e4e1024a7.py`): hours_moved_total (hourly comfort targets moved over two holiday days) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 4 count. Inputs tried: holiday Wednesday and Saturday with holiday_day_end_hour 20 (weekday 22): end 20 -> 22, hours 20-21 read day 20.0 instead of night 17.0: 4 moved; plain Saturday: 0; null plain Wednesday: 0. Should fail: tests/features.py (also tests/entities.py executes the line): no check configures holiday_day_end_hour and asserts the holiday comfort band ends at it. Candidate: No check reads the holiday day-end-hour override; ignoring holiday_day_end_hour is unseen.

### e4affa9b9b540588 (candidate) — custom_components/heatpump_optimizer/optimizer.py:2788 RETURN_DEL

`return day, night, start, end -> pass` in `OptimizationConfig._comfort_pair`. Gate RED-AS-NULL (gate_rc 1, wall 3474.1 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_e4affa9b9b540588.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_e4affa9b9b540588.py`): hours_moved_total (hourly comfort targets moved on a weekend holiday) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 23 count. Inputs tried: holiday on a Saturday with both holiday (20/17 08-20) and weekend (22/20 09-23) overrides: (20.0,17.0,8,20) -> (22.0,20.0,9,23), 23 hours moved; holiday on a Wednesday: 0 (the weekend branch does not apply); null plain Wednesday: 0. Should fail: tests/features.py (also tests/entities.py executes the line): no check puts a holiday on a weekend day with weekend overrides configured and asserts the holiday values win. Candidate: No check puts a holiday on a weekend; deleting the holiday branch's return is unseen.

### 0fcdd4bdabc205ea (candidate) — custom_components/heatpump_optimizer/optimizer.py:2794 GUARD_OFF

`if self.day_start_hour_weekend is not None: -> if False:` in `OptimizationConfig._comfort_pair`. Gate RED-AS-NULL (gate_rc 1, wall 3510.0 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_0fcdd4bdabc205ea.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_0fcdd4bdabc205ea.py`): hours_moved_total (hourly comfort targets moved on a Saturday) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 2 count. Inputs tried: plain Saturday with day_start_hour_weekend 9 (weekday 7): start 9 -> 7, hours 7-8 read day 22.0 instead of night 20.0: 2 moved; holidays: 0 (holiday branch returns first); null plain Wednesday: 0. Should fail: tests/features.py (also tests/entities.py, tests/boost_drift_replay.py execute the line): no check configures day_start_hour_weekend and asserts the weekend comfort band starts at it. Candidate: No check reads the weekend day-start-hour override; ignoring day_start_hour_weekend is unseen.

### 8365c2592bae9886 (candidate) — custom_components/heatpump_optimizer/optimizer.py:2796 GUARD_OFF

`if self.day_end_hour_weekend is not None: -> if False:` in `OptimizationConfig._comfort_pair`. Gate RED-AS-NULL (gate_rc 1, wall 3437.6 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_8365c2592bae9886.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_8365c2592bae9886.py`): hours_moved_total (hourly comfort targets moved on a Saturday) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 1 count. Inputs tried: plain Saturday with day_end_hour_weekend 23 (weekday 22): end 23 -> 22, hour 22 reads night 20.0 instead of day 22.0: 1 moved; holidays: 0; null plain Wednesday: 0. Should fail: tests/features.py (also tests/entities.py, tests/boost_drift_replay.py execute the line): no check configures day_end_hour_weekend and asserts the weekend comfort band ends at it. Candidate: No check reads the weekend day-end-hour override; ignoring day_end_hour_weekend is unseen.

### ee671fa6ecec9023 (equivalent-candidate) — custom_components/heatpump_optimizer/optimizer.py:4560 CMP_BOUND

`if not _pin_is_free(value) and value < 0.5: -> if not _pin_is_free(value) and value <= 0.5:` in `HeatPumpOptimizer.optimize`. Gate RED-AS-NULL (gate_rc 1, wall 2776.8 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_ee671fa6ecec9023.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_ee671fa6ecec9023.py`): released (space steps reported released) baseline 88 count, mutant 96 count. Inputs tried: direct optimize() input with pins = 0.5 at 0-7, abandonment stub: released 88 -> 96 (moves only on a 0.5 pin); pins 1.0 / 0.0: no move; reach: build_override over 5 slot layouts x 2 channels, through channel_pins and _normalise_pins, emits only {0.0, 1.0}; reach_half_pins=0. Should fail: tests/manual_plan.py (the only script executing line 4560): none through production: a 0.5 pin never reaches optimize(); only a direct optimize() call with a 0.5 pin separates the arms. Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production.

### 9a06a1a7e515fa67 (equivalent-candidate) — custom_components/heatpump_optimizer/optimizer.py:4610 CMP_BOUND

`and candidate.objective_value < fixed_objective - 1e-9 -> and candidate.objective_value <= fixed_objective - 1e-9` in `HeatPumpOptimizer.optimize`. Gate RED-AS-NULL (gate_rc 1, wall 2834.8 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_9a06a1a7e515fa67.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_9a06a1a7e515fa67.py`): natural_cells_moved (cells whose (adopted, objective) differ) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 0 count. Inputs tried: golden valve_storage_smart_write and wood_two_tank_smart_write, winter_typical and flat prices, 24 h and 48 h (8 cells): 0 cells move (hold adopted at winter 24 h in both arms, never elsewhere); forced exact tie (candidate objective overwritten to fixed_objective - 1e-9): adopted 0 -> 1 -- the boundary itself, which no honest solve lands on. Should fail: tests/features.py, tests/env_drift.py execute line 4610: none: only a candidate objective exactly equal to fixed_objective - 1e-9 separates < from <=, a measure-zero float tie. Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production.

### 65b62179a34d3443 (equivalent-candidate) — custom_components/heatpump_optimizer/optimizer.py:2823 GUARD_OFF

`if values.size == 0: -> if False:` in `OptimizationConfig.baseline_load_array`. Gate RED-AS-NULL (gate_rc 1, wall 3434.7 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_65b62179a34d3443.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_65b62179a34d3443.py`): cells_moved (grid cells whose outcome differs) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 1 count  ['empty:values->IndexError']. Inputs tried: 13-cell grid: None, [], [] at n=0, list/ndarray of size n-1, n, n+1 at n=96 and n=0: 1 cell moves (empty profile at n=96: zeros -> IndexError); reach: 4 real coordinator refresh cycles (house power entity absent/present x manual plan off/on): pairs [(96, 96)], 0 distinguishing calls (coordinator._baseline_house_load always returns n_steps values). Should fail: tests/config_flow_steps.py, tests/entities.py, tests/env_drift.py, tests/features.py execute line 2823: none through production: only an empty stored profile at n_steps > 0 separates the arms, and the only producer (coordinator._baseline_house_load) never builds one. Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production.

### 67ac7292ac5ddd19 (equivalent-candidate) — custom_components/heatpump_optimizer/optimizer.py:2825 CMP_BOUND

`if values.size >= n_steps: -> if values.size > n_steps:` in `OptimizationConfig.baseline_load_array`. Gate RED-AS-NULL (gate_rc 1, wall 3491.6 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_67ac7292ac5ddd19.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_67ac7292ac5ddd19.py`): cells_moved (grid cells whose outcome differs) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 0 count  []. Inputs tried: 13-cell grid (None, [], size n-1/n/n+1 lists and ndarrays at n=96 and n=0): 0 cells move -- at size == n the pad branch appends np.full(0) and returns the same float64 values; reach: production pairs [(96, 96)]; the returned array is only read (_grid_report, _peak_billing callers), never mutated, so view-vs-copy is unobservable. Should fail: tests/config_flow_steps.py, tests/entities.py, tests/env_drift.py, tests/features.py execute line 2825: none: the mutant is equivalent at the returned values. Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production.

### cfda6ca73c6951f1 (equivalent-candidate) — custom_components/heatpump_optimizer/optimizer.py:2825 GUARD_OFF

`if values.size >= n_steps: -> if False:` in `OptimizationConfig.baseline_load_array`. Gate RED-AS-NULL (gate_rc 1, wall 3496.1 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_cfda6ca73c6951f1.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_cfda6ca73c6951f1.py`): cells_moved (grid cells whose outcome differs) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 4 count  ['list97_n96:values->ValueError', 'arr97_n96:values->ValueError', 'list1_n0:values->ValueError', 'arr1_n0:values->ValueError']. Inputs tried: 13-cell grid: 4 cells move, every profile longer than n_steps (size 97 at n=96, size 1 at n=0): values -> ValueError (np.full negative count); size == n equal; reach: 4 coordinator refresh cycles: pairs [(96, 96)], 0 distinguishing calls. Should fail: tests/config_flow_steps.py, tests/entities.py, tests/env_drift.py, tests/features.py execute line 2825: none through production: only a stored profile longer than the horizon separates the arms, and the coordinator builds it at exactly n_steps. Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production.

### c2896572788698c0 (equivalent-candidate) — custom_components/heatpump_optimizer/optimizer.py:2412 CLAMP_DROP

`for i in range(min(len(out), len(pins))): -> for i in range((len(out))):` in `_apply_pins_to_bounds`. Gate RED-AS-NULL (gate_rc 1, wall 3599.0 s provisional). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_c2896572788698c0.py` (`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_c2896572788698c0.py`): cells_moved (grid cells whose outcome differs) baseline 0 (the metric is a baseline-vs-mutant delta), mutant 4 count  ['len0:IndexError', 'len1:IndexError', 'len2:IndexError', 'len3:IndexError']. Inputs tried: 4 bounds x pin vectors of length 0..6: 4 cells move (pins shorter than bounds: IndexError); equal and longer pins identical; reach: 4 coordinator refresh cycles, manual plan on and off: pairs [(96, 96), (96, None)], 0 distinguishing calls; _normalise_pins pads/truncates pins to the horizon, and the candidate-levels caller (_run_bounds, optimizer.py:565) builds its mask from the same plan as its bounds. Should fail: tests/manual_plan.py, tests/features.py, tests/optimality.py, tests/env_drift.py execute line 2412: none through production: only a pin vector shorter than the bounds separates the arms, and every caller hands equal lengths. Equivalent-candidate: a non-finding unless a later seat finds a distinguishing input reachable through production.

## Killed

- ec173cf0e67c0689 custom_components/heatpump_optimizer/optimizer.py:4518 GUARD_OFF: KILLED by python3 tests/stress.py (gate_rc 1); fail lines {"python3 tests/closure.py selftest": 2, "python3 tests/entities.py": 1, "python3 tests/stress.py": 3, "python3 tests/harness_headers.py": 3}

## Coverage

D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json. D3.M3 is this wave's: universe 742, examined 16 here; the other keys are assigned by box (D3-g01..D3-g47) under not_reached.

## Unfinished

- none

findings: [] — the wave's candidates go under `gate_survivors` for the orchestrator's cross-box id assignment.
