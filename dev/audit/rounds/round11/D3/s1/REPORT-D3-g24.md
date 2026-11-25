# D3-s1 wave box D3-g24: full gate for 16 D3.M3 full-net survivors

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, round 11. Findings are returned as `gate_survivors` (ids assigned at consolidation).

## Machine and controls

```
date 2026-11-22T21:40:40Z
nproc 4
cpu Intel(R) Xeon(R) Processor @ 2.10GHz
load1 0.54
python3 /opt/hpo/venv-ci/bin/python3 Python 3.14.7
node v22.23.5

               total        used        free      shared  buff/cache   available
Mem:           16087        1109       13474          12        1801       14978
Swap:              0           0           0

Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /

# re-fire (resumed seat, gates 9..16 from here) 2026-11-25T00:51:41Z
nproc 4
cpu  Intel(R) Xeon(R) Processor @ 2.30GHz
load1 0.49
               total        used        free      shared  buff/cache   available
Mem:           16087        1042       13704          12        1614       15044
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
```

Null control (`python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`, comment-only marker): gate_rc=1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] with fail_lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, wall 3652.4 s (provisional). Every one of these is an artefact of the stripped detached worktree (gates/null-note.txt); a key is KILLED only by a script beyond these or more FAIL lines in one.

Wall, CPU and load numbers are provisional (nproc 4; load1 per gate in its record); counts are final.

## Tally

- gated: 16/16; verdicts: {'RED-AS-NULL': 16}
- KILLED: 0
- TIMEOUT: 0 
- candidates (gate survivors that change behaviour): 5
- equivalent-candidates: 11

| key | site | verdict | class | probe metric baseline -> mutant |
|---|---|---|---|---|
| 1dcb273b03f63a4e | optimizer.py:4943 CLAMP_DROP | RED-AS-NULL | equivalent-candidate | mutant_replay_moved 0 -> 0 |
| c679a9939ee7b3ee | optimizer.py:4943 CLAMP_DROP | RED-AS-NULL | equivalent-candidate | mutant_replay_moved 0 -> 0 |
| 41d866cef7ea4115 | optimizer.py:4696 CMP_BOUND | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 0 |
| fa3bb379b762e2a9 | optimizer.py:4700 CMP_BOUND | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 0 |
| ce5b92d704397d85 | optimizer.py:4717 BOOLOP | RED-AS-NULL | candidate | mutant_cases_moved 0 -> 1 |
| dd2b698bc1d5d4b8 | optimizer.py:4717 CMP_BOUND | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 0 |
| aab0b73e229ad900 | optimizer.py:4720 CMP_BOUND | RED-AS-NULL | candidate | mutant_cases_moved 0 -> 2 |
| 7cb1bac951ddeb9e | optimizer.py:3772 CMP_BOUND | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 0 |
| 9bfc2c6d1bfe66bd | optimizer.py:5120 GUARD_OFF | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 1 |
| 56de38e47369b2b7 | optimizer.py:5123 CMP_BOUND | RED-AS-NULL | candidate | mutant_cases_moved 0 -> 2 |
| df066a5f3f3d3e0f | optimizer.py:5139 CMP_BOUND | RED-AS-NULL | candidate | mutant_cases_moved 0 -> 1 |
| bbcded8a73c6a2f1 | optimizer.py:5145 CMP_BOUND | RED-AS-NULL | candidate | mutant_cases_moved 0 -> 1 |
| 0f03bb94bcab1682 | optimizer.py:4067 GUARD_OFF | RED-AS-NULL | equivalent-candidate | mutant_downstream_moved 0 -> 0 |
| f54d3d4c7351ac76 | optimizer.py:4069 CLAMP_DROP | RED-AS-NULL | equivalent-candidate | mutant_downstream_moved 0 -> 1 |
| 0270b5efaac478d2 | optimizer.py:6550 GUARD_OFF | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 3 |
| 68ee8d20663ac601 | optimizer.py:6559 CMP_BOUND | RED-AS-NULL | equivalent-candidate | mutant_cases_moved 0 -> 0 |

## Survivors, one paragraph each

### ce5b92d704397d85 (candidate)

`custom_components/heatpump_optimizer/optimizer.py:4717 BOOLOP` `if price_sigma is not None and self.config.price_risk_lambda > 0.0: -> if price_sigma is not None or self.config.price_risk_lambda > 0.0:` in `HeatPumpOptimizer._stash_price_horizon`; full gate RED-AS-NULL (gate_rc 1, wall 3505.2 s, load1 0.78..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_ce5b92d704397d85.py`: mutant_cases_moved baseline 0 -> mutant 1 (reach_mutant_moved=1, reach_null_moved=0). Inputs tried: the 25 _stash_cases.CASES plus a whole HeatPumpOptimizer.optimize (6 h, price_risk_lambda 0.5, ForecastSeries without price_sigma). Step-4 answer: Mutant ce5b92d704397d85 (optimizer.py:4717 `and` -> `or`) survives the full gate, yet HeatPumpOptimizer.optimize with price_risk_lambda=0.5 and a ForecastSeries carrying no price_sigma (its default None) returns an optimal plan on the baseline and raises IndexError under the mutant. Severity claimed low: optimize() raises for a caller using the dataclass default price_sigma=None with risk pricing on; the coordinator always passes an array (coordinator.py:1599, 7258), so no Home Assistant user path reaches it. Should have failed: tests/features.py executes line 4717 on its traced baseline but has no case with price_risk_lambda > 0 and price_sigma None asserting the prices pass through untouched (and optimize does not raise). Moving case: `CASE lam_pos_sigma_none: baseline=('ok', 'prices', '<f8', [1.0, 2.0, 3.0, 4.0]) mutant=('raise', 'IndexError') moved=1`.

### aab0b73e229ad900 (candidate)

`custom_components/heatpump_optimizer/optimizer.py:4720 CMP_BOUND` `if np.any(risk > 0.0): -> if np.any(risk >= 0.0):` in `HeatPumpOptimizer._stash_price_horizon`; full gate RED-AS-NULL (gate_rc 1, wall 3362.2 s, load1 0.78..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_aab0b73e229ad900.py`: mutant_cases_moved baseline 0 -> mutant 2 (reach_mutant_moved=1, reach_null_moved=0). Inputs tried: the 25 _stash_cases.CASES plus a whole optimize (6 h, lambda 0.5, price_sigma zero except NaN on one unpublished step). Step-4 answer: Mutant aab0b73e229ad900 (optimizer.py:4720 `risk > 0.0` -> `>= 0.0`) survives the full gate, yet with price_risk_lambda=0.5 and price_sigma zero except NaN on one unpublished step, optimize returns an optimal plan on the baseline and 'failed (no usable starting point)' under the mutant (a NaN added into the solve's prices). Severity claimed low: a NaN sigma reaching the solve turns the plan failed; the coordinator's sigma comes from price_model.extend_price_series (zero on known steps, PriceShapeModel.sigma elsewhere) and no NaN source was shown. Should have failed: tests/features.py (the only closure script whose traced baseline executes line 4720) has no case with an all-zero or non-finite risk asserting the price array is returned untouched. Moving case: `CASE lam_pos_sigma_nan_unknown: baseline=('ok', 'prices', '<f8', [1.0, 2.0, 3.0, 4.0]) mutant=('ok', 'prices', '<f8', [1.0, 2.0, nan, 4.0]) moved=1`.

### 56de38e47369b2b7 (candidate)

`custom_components/heatpump_optimizer/optimizer.py:5123 CMP_BOUND` `for i in np.nonzero(refused > 1e-9)[0]: -> for i in np.nonzero(refused >= 1e-9)[0]:` in `HeatPumpOptimizer._tighten_buffer_caps`; full gate RED-AS-NULL (gate_rc 1, wall 2764.1 s, load1 0.78..1.04). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_56de38e47369b2b7.py`: mutant_cases_moved baseline 0 -> mutant 2. Inputs tried: the 12 _tighten_core cases. Step-4 answer: Mutant 56de38e47369b2b7 (optimizer.py:5123 `refused > 1e-9` -> `>= 1e-9`) survives the full gate, yet with a step refusing exactly 1e-9 kW _tighten_buffer_caps leaves the caps and returns False on the baseline and tightens that step's cap 3.0 -> 1.998 kW and returns True (one more re-solve) under the mutant. Severity claimed low: at the exact 1e-9 kW tie a step's buffer cap is tightened and a repair re-solve spent; a refusal of exactly 1e-9 kW is a float tie. Should have failed: tests/features.py and tests/validate.py execute line 5123 on their traced baselines; neither feeds a refused value at the 1e-9 boundary. Moving case: `CASE refused_tie_1e-9_alone: baseline=('ok', False, [3.0, 3.0, 3.0, 3.0], []) mutant=('ok', True, [1.9979999995922448, 3.0, 3.0, 3.0], [0]) moved=1`.

### df066a5f3f3d3e0f (candidate)

`custom_components/heatpump_optimizer/optimizer.py:5139 CMP_BOUND` `if new_cap < float(power_caps[i]) - 1e-9: -> if new_cap <= float(power_caps[i]) - 1e-9:` in `HeatPumpOptimizer._tighten_buffer_caps`; full gate RED-AS-NULL (gate_rc 1, wall 2777.3 s, load1 0.81..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_df066a5f3f3d3e0f.py`: mutant_cases_moved baseline 0 -> mutant 1. Inputs tried: the 12 _tighten_core cases, incl. a cap c with float(c) - 1e-9 == new_cap exactly (found by nextafter search). Step-4 answer: Mutant df066a5f3f3d3e0f (optimizer.py:5139 `<` -> `<=`) survives the full gate, yet at a cap c with c - 1e-9 == new_cap exactly _tighten_buffer_caps returns False on the baseline and True (cap lowered by 1e-9 kW, one more re-solve) under the mutant. Severity claimed low: at the float tie a repair round is spent re-solving for a 1e-9 kW cap change, the cost the line's own comment says the margin avoids. Should have failed: tests/features.py (the only closure script whose traced baseline executes line 5139) has no tie case asserting changed False. Moving case: `CASE refused_real_cap_tie(new_cap==cap-1e-9): baseline=('ok', False, [1.7941224499795918, 3.0, 3.0, 3.0], []) mutant=('ok', True, [1.7941224489795917, 3.0, 3.0, 3.0], [1]) moved=1`.

### bbcded8a73c6a2f1 (candidate)

`custom_components/heatpump_optimizer/optimizer.py:5145 CMP_BOUND` `int(np.count_nonzero(refused > 1e-9)), -> int(np.count_nonzero(refused >= 1e-9)),` in `HeatPumpOptimizer._tighten_buffer_caps`; full gate RED-AS-NULL (gate_rc 1, wall 2696.1 s, load1 0.77..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_bbcded8a73c6a2f1.py`: mutant_cases_moved baseline 0 -> mutant 1. Inputs tried: the 12 _tighten_core cases. Step-4 answer: Mutant bbcded8a73c6a2f1 (optimizer.py:5145 `refused > 1e-9` -> `>= 1e-9` in the debug count) survives the full gate, yet with one step refusing exactly 1e-9 kW beside one refusing 0.5 kW the logged count is 1 on the baseline and 2 under the mutant. Severity claimed low: a DEBUG log line over-counts tightened steps at the 1e-9 kW tie; no plan or published value moves. Should have failed: tests/features.py executes line 5145 but no check reads the debug count. Moving case: `CASE refused_tie_1e-9_plus_real: baseline=('ok', True, [3.0, 1.7941224489795917, 3.0, 3.0], [1]) mutant=('ok', True, [3.0, 1.7941224489795917, 3.0, 3.0], [2]) moved=1`.

### 1dcb273b03f63a4e (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4943 CLAMP_DROP` `guess = np.minimum(np.clip(guess, 0.0, p_max), headroom) -> guess = np.minimum((guess), headroom)` in `HeatPumpOptimizer._solve_space`; full gate RED-AS-NULL (gate_rc 1, wall 3308.6 s, load1 0.78..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_1dcb273b03f63a4e.py`: mutant_replay_moved baseline 0 -> mutant 0 (mutant_guess_outside_bounds_mutant=6, mutant_whole_moved=0). Inputs tried: 3 DHW scenarios (power_caps_extra 3/2/1 kW, 12 h/15 min): the captured _solve_space call replayed with warm_start None, init_base x2-0.5, warm = init_base x1.5, init_base + p_max, init_base - p_max/2, all -1 kW (18 replays), plus the whole optimize() per scenario. Step-4 answer: the mutated guess leaves its bounds (guess_outside_bounds_mutant > 0) yet no returned plan, status or score moves: the starts are projected/re-scoped downstream before anything is shipped. A check that would distinguish it: a _solve_space case seeded with a warm start outside [0, p_max] asserting the returned plan/status equal the clipped-start solve (would not fail: equivalent).

### c679a9939ee7b3ee (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4943 CLAMP_DROP` `guess = np.minimum(np.clip(guess, 0.0, p_max), headroom) -> guess = (np.clip(guess, 0.0, p_max))` in `HeatPumpOptimizer._solve_space`; full gate RED-AS-NULL (gate_rc 1, wall 3242.9 s, load1 0.72..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_c679a9939ee7b3ee.py`: mutant_replay_moved baseline 0 -> mutant 0 (mutant_guess_outside_bounds_mutant=15, mutant_whole_moved=0). Inputs tried: as 1dcb273b03f63a4e (18 replays incl. warm starts above the cap-limited headroom, 3 whole solves). Step-4 answer: the guess exceeds the headroom bound on 15 replays yet the returned plan, status and score never move. A check that would distinguish it: a warm start above the power_caps_extra headroom asserting the solve's result (would not fail: equivalent).

### 41d866cef7ea4115 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4696 CMP_BOUND` `if price_known.size < n_steps: -> if price_known.size <= n_steps:` in `HeatPumpOptimizer._stash_price_horizon`; full gate RED-AS-NULL (gate_rc 1, wall 3240.0 s, load1 0.94..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_41d866cef7ea4115.py`: mutant_cases_moved baseline 0 -> mutant 0. Inputs tried: 25 _stash_cases.CASES: price_known of size n-1, n, n+1, 0; pv_surplus n-1, n, n+1, 0, int; lambda 0/neg/pos x sigma None/empty/pos/zero/neg/inf/NaN; int and -0.0 prices; denormal lambda*sigma. Step-4 answer: at size == n the pad is np.zeros(0) and the concatenation equals the input (values and dtype). A check that would distinguish it: none can fail: equivalent.

### fa3bb379b762e2a9 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4700 CMP_BOUND` `if pv_surplus.size < n_steps: -> if pv_surplus.size <= n_steps:` in `HeatPumpOptimizer._stash_price_horizon`; full gate RED-AS-NULL (gate_rc 1, wall 3287.6 s, load1 0.78..1.0). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_fa3bb379b762e2a9.py`: mutant_cases_moved baseline 0 -> mutant 0. Inputs tried: the 25 _stash_cases.CASES (see 41d866cef7ea4115). Step-4 answer: at size == n the pad is np.zeros(0); the float concatenation equals the input. A check that would distinguish it: none can fail: equivalent.

### dd2b698bc1d5d4b8 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4717 CMP_BOUND` `if price_sigma is not None and self.config.price_risk_lambda > 0.0: -> if price_sigma is not None and self.config.price_risk_lambda >= 0.0:` in `HeatPumpOptimizer._stash_price_horizon`; full gate RED-AS-NULL (gate_rc 1, wall 3669.9 s, load1 0.79..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_dd2b698bc1d5d4b8.py`: mutant_cases_moved baseline 0 -> mutant 0. Inputs tried: the 25 _stash_cases.CASES (lambda 0 with sigma pos/inf/NaN/None, negative lambda included). Step-4 answer: at lambda == 0 the risk term is 0*sigma (0, or NaN for inf sigma, which np.any(risk > 0) skips), so prices are returned untouched in both arms. A check that would distinguish it: none can fail: equivalent.

### 7cb1bac951ddeb9e (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:3772 CMP_BOUND` `(d := cap - traj[name][:, -1]) > 0.0, d, 0.0 -> (d := cap - traj[name][:, -1]) >= 0.0, d, 0.0` in `HeatPumpOptimizer._terminal_cost_batch.cost_batch`; full gate RED-AS-NULL (gate_rc 1, wall 3500.2 s, load1 0.93..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_7cb1bac951ddeb9e.py`: mutant_cases_moved baseline 0 -> mutant 0 (mutant_parity_breaks=0). Inputs tried: 81 cases: 3 row_cost variants (same COP, split COP, refill derate) x coef +/-/0 x 9 end temperatures (end == cap, cap=-0/end=+0, +/-1 ulp, NaN, +/-inf, far below/above), compared bit for bit. Step-4 answer: np.where(d >= 0, d, 0) differs from the > form only at d == +/-0.0, where it returns a signed zero that the row's builtin sum absorbs bit for bit. A check that would distinguish it: none can fail: equivalent.

### 9bfc2c6d1bfe66bd (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:5120 GUARD_OFF` `if refused is None: -> if False:` in `HeatPumpOptimizer._tighten_buffer_caps`; full gate RED-AS-NULL (gate_rc 1, wall 2790.4 s, load1 0.44..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_9bfc2c6d1bfe66bd.py`: mutant_cases_moved baseline 0 -> mutant 1 (reach_refused_is_none=0). Inputs tried: 12 refused vectors (None, zeros, the 1e-9 tie, 1 ulp either side, NaN, negative, cap ties) via a stubbed simulate_trajectory, plus the real ThermalModel.simulate_trajectory's refused slot. Step-4 answer: moves only for refused None (TypeError), which ThermalModel.simulate_trajectory never returns (np.zeros(n_steps) at thermal_model.py:4370; reach_refused_is_none=0): unreachable through production. A check that would distinguish it: a stubbed refused=None case would fail, but no production caller can produce one: the guard is dead code.

### 0f03bb94bcab1682 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4067 GUARD_OFF` `if phase == 0: -> if False:` in `HeatPumpOptimizer._window_offset_steps`; full gate RED-AS-NULL (gate_rc 1, wall 2671.9 s, load1 0.78..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_0f03bb94bcab1682.py`: mutant_downstream_moved baseline 0 -> mutant 0 (mutant_return_moved=57). Inputs tried: 127 cases: window 15/60 min x dt 0.25/0.5/1.0/0.75/1 min x starts 00:00, 07:00, 12:00, 12:15, 12:45, 23:30 x masks off/on; dt 1e-9/0/-0.25; start None. Step-4 answer: the return moves (0 -> one whole window of steps) on every aligned start, but every consumer partitions by offset % per_window (tariff._window_partition), so PeakBilling, the capacity penalty and _grid_report never move. A check that would distinguish it: an _window_offset_steps unit asserting 0 at an aligned start would fail; no check through _peak_billing can (equivalent at the observable output).

### f54d3d4c7351ac76 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:4069 CLAMP_DROP` `return max(0, int(round((window - phase) / max(dt * 60.0, 1e-6)))) -> return max(0, int(round((window - phase) / (dt * 60.0))))` in `HeatPumpOptimizer._window_offset_steps`; full gate RED-AS-NULL (gate_rc 1, wall 2638.5 s, load1 0.72..0.93). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_f54d3d4c7351ac76.py`: mutant_downstream_moved baseline 0 -> mutant 1 (mutant_return_moved=3, reach_optimize_dt0_raises_before=1, reach_offset_calls_at_dt0=0). Inputs tried: the 127 _window_core cases (dt 1e-9, 0, -0.25 included) plus optimize(time_step_minutes=0). Step-4 answer: moves only at dt == 0 (ZeroDivisionError), and optimize with time_step_minutes=0 already raises on the baseline before any offset is computed: unreachable through production. A check that would distinguish it: none through production; a direct _window_offset_steps(dt=0) call separates.

### 0270b5efaac478d2 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:6550 GUARD_OFF` `if not result.timestamps: -> if False:` in `HeatPumpOptimizer.get_current_action`; full gate RED-AS-NULL (gate_rc 1, wall 2750.7 s, load1 0.78..0.92). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_0270b5efaac478d2.py`: mutant_cases_moved baseline 0 -> mutant 3 (reach_optimize_empty_results=0). Inputs tried: 21 cases: a real 6 h plan, its first step alone and the plan emptied x clocks at/1 us/half a step/one step/one step + 1 s before the first start, step 1, mid step 3, last start, past the end; plus 3 degenerate optimize() calls. Step-4 answer: moves only on an empty result (IndexError instead of the idle action); the one production caller (coordinator.py:6464) passes the result optimize() just returned, and optimize raises on every degenerate input tried instead of returning an empty plan (reach_optimize_empty_results=0). A check that would distinguish it: none through production; a direct call with an empty OptimizationResult separates.

### 68ee8d20663ac601 (equivalent-candidate)

`custom_components/heatpump_optimizer/optimizer.py:6559 CMP_BOUND` `if now_s < starts[0]: -> if now_s <= starts[0]:` in `HeatPumpOptimizer.get_current_action`; full gate RED-AS-NULL (gate_rc 1, wall 2857.5 s, load1 0.93..1.0). Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/probes/probe_68ee8d20663ac601.py`: mutant_cases_moved baseline 0 -> mutant 0. Inputs tried: the 21 _action_core cases, incl. now == starts[0] on a multi-step and a one-step plan. Step-4 answer: at now == starts[0] the pre-horizon branch picks i = 0 (gap 0 <= one step), which is the step the loop picks too. A check that would distinguish it: none can fail: equivalent.

## Coverage

D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched items are carried verbatim from REPORT-D3-u1b.json. D3.M3 is this wave's row: universe 742 (the wave list), examined 16 (this box's gated keys), the other 726 keys named under not_reached by their box.

