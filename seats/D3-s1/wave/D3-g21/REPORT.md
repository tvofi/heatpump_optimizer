# D3-s1 wave box D3-g21: full gate for 16 D3.M3 full-net survivors

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, round 11. Procedure: `gate_wave.sh` (dispatch tip of dispatch/finder-r11-D3-g21) runs `dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` per key of keys.tsv, one gate at a time (`GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh`), capped at 14400 s.

## Machine and controls

First machine (null and gates 1-8): nproc 4, Intel Xeon @ 2.10GHz, 16 GB. Re-fire machine (gates 9-16): nproc 4, Intel Xeon @ 2.30GHz, 16 GB. See `dev/audit/rounds/round11/D3/s1/wave/D3-g21/MACHINE.txt`. All wall, CPU and load numbers are provisional: true (the judge re-takes them).

Null control `dev/audit/rounds/round11/D3/s1/wave/D3-g21/gates/null.json`: gate_rc 1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 3461.9 s. All three are artefact checks (see `gates/null-note.txt`); usable, not re-taken.

## Tally

- gated: 16 of 16; KILLED 1, RED-AS-NULL 15
- KILLED: 1; 39a6d2e97fd44ed5 by python3 tests/stress.py
- candidates (survive, probe moves): 11: fd57e13959b23a4c, ad01ae06d7ea84ec, cb58757b91fa48c4, 00298af0aa9d1903, a4f4c88e7480a514, be3a3a75280c7b7e, deb281264473bdd6, a66e107749d0ae11, 4e5a67b907d13871, ed5e3ec5b879ed90, 6309f3e4a0a6c45f
- equivalent-candidates: 4: 905a40b5ecea024f, 8ac9888c3d5fed52, 904118eef67fced3, 6b6eb0c1091c3c5c
- TIMEOUT: 0

Findings: [] by the brief; candidates are under `gate_survivors` for the orchestrator's id assignment.

## Per key

### fd57e13959b23a4c — custom_components/heatpump_optimizer/optimizer.py:3997 CMP_BOUND (candidate)

`if score < best_score - 1e-9: -> if score <= best_score - 1e-9:` in `HeatPumpOptimizer._co_optimize`. Gate: RED-AS-NULL (gate_rc 1, wall 3302.1 s, load1 0.45..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_fd57e13959b23a4c.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_fd57e13959b23a4c.py`), metric: which DHW plan _co_optimize returns when the re-planned candidate scores exactly best_score - 1e-9. Baseline tie_baseline=original, mutant tie_mutant=replanned. All RESULT lines: tie_baseline=original; tie_mutant=replanned; moved=1 count; null_delta=0 count; below_tie=replanned|replanned; above_tie=original|original; thread_factor=1.000; load1=1.42; swapins=0.

Inputs tried: score == best_score - 1e-9 (the tie) | score one ulp below the tie | score one ulp above the tie.

Should fail: tests/features.py (traced baseline executes optimizer.py:3997; tests/edge.py and tests/stress.py also execute it): no co-optimize check feeds a replan scoring exactly best_score - 1e-9 and asserts the original plan is kept.

Candidate: No check pins _co_optimize's strict adoption rule at a score exactly 1e-9 better; < -> <= is unseen. Severity claimed low; the plan returned at the tie moves from original to replanned.

### 905a40b5ecea024f — custom_components/heatpump_optimizer/optimizer.py:5044 GUARD_OFF (equivalent-candidate)

`if n == 0 or len(prices) != n: -> if False:` in `HeatPumpOptimizer._derive_hold_schedule`. Gate: RED-AS-NULL (gate_rc 1, wall 3219.8 s, load1 0.86..1.0, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_905a40b5ecea024f.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_905a40b5ecea024f.py`), metric: _derive_hold_schedule's outcome on length-mismatched / empty inputs, and the count of production calls that pass such inputs. Baseline mismatch_baseline=None, mutant mismatch_mutant=raise:ValueError. All RESULT lines: mismatch_baseline=None; mismatch_mutant=raise:ValueError; empty_baseline=None; empty_mutant=raise:IndexError; null_delta=0 count; reach_calls_mismatched=0 count; reach_calls_total=2 count; thread_factor=1.000; load1=1.47; swapins=0.

Inputs tried: power 8 / prices 9 (mismatch) | power 0 / prices 0 (empty) | matched length 8 (null) | optimize() smart-write store reach: 24-step horizon with 24 and 30 prices.

Should fail: none through production: tests/features.py and tests/stress.py execute line 5044 but no production caller passes a length mismatch or an empty horizon.

Equivalent-candidate: The direct call moves (None -> ValueError / IndexError), but the one production caller (optimizer.py:4601) passes result.power_schedule and prices both n_steps long: reach_calls_mismatched=0 of 2. Equivalent at every production-reachable input; a non-finding unless a later seat finds a caller that delivers a mismatch.

### ad01ae06d7ea84ec — custom_components/heatpump_optimizer/optimizer.py:5054 GUARD_OFF (candidate)

`if p85 <= p25 * 1.05: -> if False:` in `HeatPumpOptimizer._derive_hold_schedule`. Gate: RED-AS-NULL (gate_rc 1, wall 3229.9 s, load1 0.92..1.0, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ad01ae06d7ea84ec.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ad01ae06d7ea84ec.py`), metric: whether _derive_hold_schedule proposes a valve-hold schedule at a sub-5 % price spread; through optimize() the proposals (each one a full re-solve) and solve CPU. Baseline nearflat_baseline=None, mutant nearflat_mutant=array:23,23,19,19,19,19,23,23. All RESULT lines: nearflat_baseline=None; nearflat_mutant=array:23,23,19,19,19,19,23,23; moved=1 count; null_delta=0 count; reach_proposed_baseline=0 count; reach_proposed_mutant=1 count; reach_plan_maxabs_diff_kw=0.0000 kW; reach_objective_delta=0.000000; reach_cpu_baseline_s=1.15 s (provisional); reach_cpu_mutant_s=1.73 s (provisional); thread_factor=1.000; load1=1.47; swapins=0.

Inputs tried: 8-step direct call at p85/p25 = 1.03 | exactly flat prices (null) | optimize() smart-write 500 L store, -15 C, profile 1.0x6/1.02x12/1.04x6.

Should fail: tests/features.py (traced baseline executes optimizer.py:5054; tests/stress.py too): no check drives _derive_hold_schedule or a smart-write solve at a near-flat (<5 %) spread and asserts None / a single solve.

Candidate: No check pins the flat-price refusal of _derive_hold_schedule; dropping it re-solves every near-flat plan. Severity claimed low; up: proposals 0 -> 1 per near-flat plan; solve CPU about +70 % (provisional); plan unchanged.

### cb58757b91fa48c4 — custom_components/heatpump_optimizer/optimizer.py:5054 CMP_BOUND (candidate)

`if p85 <= p25 * 1.05: -> if p85 < p25 * 1.05:` in `HeatPumpOptimizer._derive_hold_schedule`. Gate: RED-AS-NULL (gate_rc 1, wall 3223.6 s, load1 0.85..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_cb58757b91fa48c4.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_cb58757b91fa48c4.py`), metric: whether _derive_hold_schedule proposes a schedule when p85 == 1.05 * p25 exactly; through optimize() the proposals and solve CPU. Baseline tie_baseline=None, mutant tie_mutant=array:23,23,19,19,19,23,23,23. All RESULT lines: tie_p85_equals_1p05_p25=1 count; tie_baseline=None; tie_mutant=array:23,23,19,19,19,23,23,23; moved=1 count; null_delta=0 count; reach_two_level_16_8_proposed_baseline=0 count; reach_two_level_16_8_proposed_mutant=0 count; reach_two_level_16_8_plan_maxabs_diff_kw=0.0000 kW; reach_two_level_16_8_objective_delta=0.000000; reach_two_level_16_8_cpu_baseline_s=0.91 s (provisional); reach_two_level_16_8_cpu_mutant_s=0.93 s (provisional); reach_three_level_10_8_6_proposed_baseline=0 count; reach_three_level_10_8_6_proposed_mutant=1 count; reach_three_level_10_8_6_plan_maxabs_diff_kw=0.0000 kW; reach_three_level_10_8_6_objective_delta=0.000000; reach_three_level_10_8_6_cpu_baseline_s=0.75 s (provisional); reach_three_level_10_8_6_cpu_mutant_s=1.58 s (provisional); thread_factor=1.000; load1=1.60; swapins=0.

Inputs tried: 8-step two-level tie 1.00/1.05 | 6 % spread (null) | optimize() two-level 1.0x16/1.05x8 (no hold step: both 0) | optimize() three-level 1.0x10/1.02x8/1.05x6 (tie, proposed 0 -> 1).

Should fail: tests/features.py (traced baseline executes optimizer.py:5054; tests/stress.py too): no hold-schedule check on a profile with p85 == 1.05 * p25 exactly asserting None.

Candidate: No check feeds _derive_hold_schedule a spread of exactly 5 %; <= -> < at the flat-price refusal is unseen. Severity claimed low; up: proposals 0 -> 1 at the tie (one extra re-solve); plan unchanged.

### 8ac9888c3d5fed52 — custom_components/heatpump_optimizer/optimizer.py:5059 GUARD_OFF (equivalent-candidate)

`if not bool(expensive.any()) or not bool(charging.any()): -> if False:` in `HeatPumpOptimizer._derive_hold_schedule`. Gate: RED-AS-NULL (gate_rc 1, wall 3340.2 s, load1 0.78..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_8ac9888c3d5fed52.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_8ac9888c3d5fed52.py`), metric: count of inputs whose _derive_hold_schedule outcome differs between arms. Baseline edge_differ=0 count, mutant fuzz_differ=0 count. All RESULT lines: edge_differ=0 count; edge_no_charging=None|None; edge_nan_prices_no_expensive=None|None; edge_all_nan_prices=None|None; edge_zero_power=None|None; edge_max_power_cheap_only_after_peak=None|None; edge_length_one=None|None; fuzz_differ=0 count; fuzz_guard_true=1113 count; reach_plan_maxabs_diff_kw=0.0000 kW; thread_factor=1.000; load1=1.55; swapins=0.

Inputs tried: no charging step | NaN price (no expensive step) | all-NaN prices | all-zero power | maximum power with cheap steps only after the peak | length 1 | 3000 seeded random (power, prices) pairs, 1113 of them with the removed guard firing | optimize() smart-write store reach.

Should fail: none: the guard is redundant with line 5074's.

Equivalent-candidate: Equivalent: with no charging step after_charge is all False, with no expensive step before_peak is all False, so hold is empty and line 5074 returns the same None. 0 differing outcomes of 6 edge + 3000 fuzz inputs.

### 00298af0aa9d1903 — custom_components/heatpump_optimizer/optimizer.py:5074 GUARD_OFF (candidate)

`if not bool(hold.any()): -> if False:` in `HeatPumpOptimizer._derive_hold_schedule`. Gate: RED-AS-NULL (gate_rc 1, wall 3317.0 s, load1 0.78..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_00298af0aa9d1903.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_00298af0aa9d1903.py`), metric: whether _derive_hold_schedule returns None when charging adjoins the peak (no hold step); through optimize() the proposals (each a full re-solve) and solve CPU. Baseline nohold_baseline=None, mutant nohold_mutant=array:23,23,23,23,23,23,23,23. All RESULT lines: nohold_baseline=None; nohold_mutant=array:23,23,23,23,23,23,23,23; moved=1 count; null_delta=0 count; reach_two_level_16_8_proposed_baseline=0 count; reach_two_level_16_8_proposed_mutant=1 count; reach_two_level_16_8_plan_maxabs_diff_kw=0.0000 kW; reach_two_level_16_8_objective_delta=0.000000; reach_two_level_16_8_cpu_baseline_s=0.96 s (provisional); reach_two_level_16_8_cpu_mutant_s=2.07 s (provisional); reach_cheap_then_peak_12_12_proposed_baseline=0 count; reach_cheap_then_peak_12_12_proposed_mutant=1 count; reach_cheap_then_peak_12_12_plan_maxabs_diff_kw=0.0000 kW; reach_cheap_then_peak_12_12_objective_delta=0.000000; reach_cheap_then_peak_12_12_cpu_baseline_s=0.89 s (provisional); reach_cheap_then_peak_12_12_cpu_mutant_s=1.91 s (provisional); thread_factor=1.000; load1=1.62; swapins=0.

Inputs tried: 8-step direct call, charging right up to the peak | input with hold steps (null) | optimize() two-level 1.0x16/1.2x8 | optimize() 0.5x12/3.0x12.

Should fail: tests/features.py (the only traced script executing optimizer.py:5074): no check asserts None (or one solve) for a smart-write plan whose charging adjoins its peak.

Candidate: No check pins _derive_hold_schedule's None when no hold step exists; dropping it doubles smart-write solve CPU. Severity claimed medium; up: proposals 0 -> 1 on both common two-level profiles; solve CPU about 2x (provisional); plan unchanged.

### a4f4c88e7480a514 — custom_components/heatpump_optimizer/optimizer.py:4033 CMP_BOUND (candidate)

`if surplus is None or not np.any(surplus[: len(prices)] > 1e-6): -> if surplus is None or not np.any(surplus[: len(prices)] >= 1e-6):` in `HeatPumpOptimizer._energy_cost_fn`. Gate: RED-AS-NULL (gate_rc 1, wall 3252.5 s, load1 0.79..0.99, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a4f4c88e7480a514.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a4f4c88e7480a514.py`), metric: energy cost _energy_cost_fn prices for a fixed schedule when the PV-surplus forecast peaks at exactly 1e-6 kW. Baseline tie_cost_baseline=29.00000000, mutant tie_cost_mutant=28.99999600. All RESULT lines: tie_cost_baseline=29.00000000; tie_cost_mutant=28.99999600; moved=1 count; null_delta=0 count; plan_predicted_cost_baseline=10.72234229; plan_predicted_cost_mutant=10.72234229; plan_maxabs_diff_kw=0.000000 kW; thread_factor=1.000; load1=1.62; swapins=0.

Inputs tried: surplus 1e-6 kW on 4 steps (the tie) | surplus 0 and 2e-6 kW (null) | optimize() with the 1e-6 surplus forecast (predicted cost and plan unchanged).

Should fail: tests/features.py (traced baseline executes optimizer.py:4033, as do 14 other closure scripts): no pricing check sits on a surplus of exactly 1e-6 kW.

Candidate: No check feeds _energy_cost_fn a PV surplus of exactly 1e-6 kW; > -> >= at the grid-only shortcut is unseen. Severity claimed low; down: the priced cost falls by margin * 1e-6 kW * dt per tie step (4e-6 here); the optimize() plan and predicted cost do not move.

### 904118eef67fced3 — custom_components/heatpump_optimizer/optimizer.py:5271 CMP_BOUND (equivalent-candidate)

`while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5: -> while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) <= 0.5:` in `HeatPumpOptimizer._expand_off_blocks`. Gate: RED-AS-NULL (gate_rc 1, wall 3205.9 s, load1 0.91..0.93, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_904118eef67fced3.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_904118eef67fced3.py`), metric: the step list _expand_off_blocks returns, and the count of differing outputs over pins drawn from the production pin domain. Baseline tie_baseline=[2], mutant tie_mutant=[0,1,2]. All RESULT lines: tie_baseline=[2]; tie_mutant=[0,1,2]; production_domain_differ=0 count; null_delta=0 count; thread_factor=1.000; load1=1.62; swapins=0.

Inputs tried: pin of exactly 0.5 (moves: [2] -> [0,1,2]) | 5000 seeded random pin arrays over {PIN_OFF 0.0, PIN_ON 1.0, PIN_FREE NaN} | 0.0/1.0 only (null).

Should fail: none through production: tests/features.py and tests/manual_plan.py execute line 5271 with pins in {0, 1, NaN} only.

Equivalent-candidate: The direct call moves only on a 0.5 pin; manual_plan.channel_pins writes only PIN_OFF, PIN_ON and PIN_FREE, so 0 of 5000 production-domain inputs differ. Equivalent at every production-reachable input.

### be3a3a75280c7b7e — custom_components/heatpump_optimizer/optimizer.py:5016 CLAMP_DROP (candidate)

`take = min(n_steps, src.size) -> take = (n_steps)` in `HeatPumpOptimizer._normalise_pins`. Gate: RED-AS-NULL (gate_rc 1, wall 2716.9 s, load1 0.12..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_be3a3a75280c7b7e.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_be3a3a75280c7b7e.py`), metric: what _normalise_pins returns for a pin array shorter than the horizon; the same through optimize(SolveLimits(space_pins=short)). Baseline short_baseline=array:1,0,nan,nan, mutant short_mutant=raise:ValueError. All RESULT lines: short_baseline=array:1,0,nan,nan; short_mutant=raise:ValueError; null_delta=0 count; optimize_short_pins_baseline=ok; optimize_short_pins_mutant=raise:ValueError; reach_plan_maxabs_diff_kw=0.0000 kW; thread_factor=1.000; load1=1.62; swapins=0.

Inputs tried: 2 pins on a 4-step horizon | exact-length and longer pins (null) | optimize() with 3 pins on 24 steps | optimize() with 24 pins and a 20-step weather series (coordinator sizing: equal plans).

Should fail: tests/manual_plan.py (traced baseline executes optimizer.py:5016; tests/block_duty.py, features.py, optimality.py, stress.py too): no check passes a short pin array and asserts the NaN padding.

Candidate: No check feeds _normalise_pins a pin array shorter than the horizon; dropping min() makes optimize() raise. Severity claimed low; the outcome moves from a padded array to ValueError, and optimize() from a plan to ValueError; the coordinator sizes pins to len(prices) >= n_steps, so its live path does not reach it.

### 39a6d2e97fd44ed5 — custom_components/heatpump_optimizer/optimizer.py:5478 CLAMP_DROP (killed)

`initial_power = np.clip(initial_power, p_min, p_max) -> initial_power = (initial_power)` in `HeatPumpOptimizer._optimize_space_only`. Gate: KILLED (gate_rc 1, wall 2487.9 s, load1 0.94..0.93, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/stress.py'] = the null's; more fails than null: [].

### deb281264473bdd6 — custom_components/heatpump_optimizer/optimizer.py:5902 CMP_BOUND (candidate)

`dhw_active_steps = int(np.sum(optimal_dhw > 0.1)) -> dhw_active_steps = int(np.sum(optimal_dhw >= 0.1))` in `HeatPumpOptimizer._optimize_with_dhw`. Gate: RED-AS-NULL (gate_rc 1, wall 2490.0 s, load1 1.01..1.0, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_deb281264473bdd6.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_deb281264473bdd6.py`), metric: the DHW active-step count in the 'DHW+Space optimization completed' INFO log line under a 0.1 kW fuse cap. Baseline dhw_active_steps_logged_baseline=0, mutant dhw_active_steps_logged_mutant=22. All RESULT lines: dhw_steps_at_0p1=22 count; dhw_active_steps_logged_baseline=0; dhw_active_steps_logged_mutant=22; null_delta=0 count; plan_dhw_maxabs_diff_kw=0.0000 kW; thread_factor=1.021; load1=1.65; swapins=0.

Inputs tried: fuse cap min 0.1 kW (22 DHW steps at exactly 0.1 kW) | no fuse cap (null: steps >= 0.6 kW).

Should fail: tests/features.py (traced baseline executes optimizer.py:5902): no caplog check on the completion line under a fuse cap that puts DHW steps at exactly 0.1 kW.

Candidate: No check reads the DHW active-step count at the 0.1 kW floor; > -> >= in the completion log is unseen. Severity claimed low; up: logged count 0 -> 22 (log only).

### a66e107749d0ae11 — custom_components/heatpump_optimizer/optimizer.py:5945 CLAMP_DROP (candidate)

`float(max(dhw_floor_temps[0], dhw_ready_temps[0])) -> float((dhw_floor_temps[0]))` in `HeatPumpOptimizer._optimize_with_dhw`. Gate: RED-AS-NULL (gate_rc 1, wall 2442.5 s, load1 0.85..0.93, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a66e107749d0ae11.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a66e107749d0ae11.py`), metric: predictive_info.dhw_required_temperature_now (published as the DHW sensor's dhw_required_temperature attribute, sensor.py:1191) per start hour. Baseline required_now_baseline=55.0 C, mutant required_now_mutant=20.0 C. All RESULT lines: first_differing_hour=5; required_now_baseline=55.0 C; required_now_mutant=20.0 C; hours_differ=4 count; differing_hours=5,6,16,17; null_delta=0 count; thread_factor=1.001; load1=1.71; swapins=0.

Inputs tried: all 24 start hours of a hot-water solve (4 differ: 5, 6, 16, 17) | the 20 other hours (null).

Should fail: tests/entities.py (traced baseline executes optimizer.py:5945; block_duty, features, manual_plan, optimality, plan_view, validate, card.mjs and card_drift.mjs too; every golden's solve starts outside a window): no check or golden starts a hot-water solve inside a demand window and pins dhw_required_temperature.

Candidate: No check reads dhw_required_temperature_now inside a demand window; dropping max(floor, ready) publishes the floor. Severity claimed high; down: 55.0 -> 20.0 C at the first in-window hour; 4 of 24 start hours move.

### 4e5a67b907d13871 — custom_components/heatpump_optimizer/optimizer.py:5956 CMP_BOUND (candidate)

`for idx in np.where(optimal_dhw > 0.1)[0][:48].tolist() -> for idx in np.where(optimal_dhw >= 0.1)[0][:48].tolist()` in `HeatPumpOptimizer._optimize_with_dhw`. Gate: RED-AS-NULL (gate_rc 1, wall 2434.7 s, load1 0.8..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_4e5a67b907d13871.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_4e5a67b907d13871.py`), metric: count of hours in predictive_info.dhw_planned_heating_hours (sensor.py:1248/1350) under a 0.1 kW fuse cap. Baseline dhw_planned_heating_hours_baseline=0, mutant dhw_planned_heating_hours_mutant=22. All RESULT lines: dhw_steps_at_0p1=22 count; dhw_planned_heating_hours_baseline=0; dhw_planned_heating_hours_mutant=22; null_delta=0 count; plan_dhw_maxabs_diff_kw=0.0000 kW; thread_factor=1.023; load1=1.71; swapins=0.

Inputs tried: fuse cap min 0.1 kW (22 DHW steps at exactly 0.1 kW) | no fuse cap (null).

Should fail: tests/entities.py (traced baseline executes optimizer.py:5956; block_duty, features, manual_plan, optimality, plan_view, validate too): no check publishes a plan whose DHW steps sit at exactly the 0.1 kW floor (a fuse cap <= 0.1 kW, dhw_planner.py:1138-1141).

Candidate: No check reads dhw_planned_heating_hours at the 0.1 kW DHW floor; > -> >= is unseen. Severity claimed low; up: 0 -> 22 listed hours.

### ed5e3ec5b879ed90 — custom_components/heatpump_optimizer/optimizer.py:5962 CMP_BOUND (candidate)

`float(np.sum((optimal_dhw > 0.1) & ~in_demand_window) * dt), 2 -> float(np.sum((optimal_dhw >= 0.1) & ~in_demand_window) * dt), 2` in `HeatPumpOptimizer._optimize_with_dhw`. Gate: RED-AS-NULL (gate_rc 1, wall 2436.0 s, load1 0.87..0.93, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ed5e3ec5b879ed90.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ed5e3ec5b879ed90.py`), metric: predictive_info.dhw_preheat_hours (sensor.py:1249) under a 0.1 kW fuse cap. Baseline dhw_preheat_hours_baseline=0.0, mutant dhw_preheat_hours_mutant=13.0. All RESULT lines: dhw_steps_at_0p1=22 count; dhw_preheat_hours_baseline=0.0; dhw_preheat_hours_mutant=13.0; null_delta=0 count; plan_dhw_maxabs_diff_kw=0.0000 kW; thread_factor=1.041; load1=1.71; swapins=0.

Inputs tried: fuse cap min 0.1 kW (22 DHW steps at exactly 0.1 kW, 13 outside a window) | no fuse cap (null).

Should fail: tests/entities.py (traced baseline executes optimizer.py:5962, as do 11 other closure scripts): no check publishes a plan whose DHW steps sit at exactly the 0.1 kW floor.

Candidate: No check reads dhw_preheat_hours at the 0.1 kW DHW floor; > -> >= is unseen. Severity claimed low; up: 0.0 -> 13.0 h.

### 6309f3e4a0a6c45f — custom_components/heatpump_optimizer/optimizer.py:5283 CLAMP_DROP (candidate)

`floor = max(float(self.model.params.min_electrical_power), 0.1) -> floor = (float(self.model.params.min_electrical_power))` in `HeatPumpOptimizer._pin_on_power`. Gate: RED-AS-NULL (gate_rc 1, wall 2463.7 s, load1 0.8..1.0, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6309f3e4a0a6c45f.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6309f3e4a0a6c45f.py`), metric: lowest planned space power on manually pinned-ON steps with the pump's minimum power configured at 0 kW. Baseline pinned_on_min_kw_baseline=0.1000 kW, mutant pinned_on_min_kw_mutant=0.0000 kW. All RESULT lines: configured_min_kw=0.0; pin_on_power_min0_baseline=0.1 kW; pin_on_power_min0_mutant=0.0 kW; pin_on_power_min005_baseline=0.1 kW; pin_on_power_min005_mutant=0.05 kW; pinned_on_min_kw_baseline=0.1000 kW; pinned_on_min_kw_mutant=0.0000 kW; null_delta_kw=0.0000 kW; thread_factor=1.000; load1=1.71; swapins=0.

Inputs tried: min power 0 kW, 4 steps pinned ON in the dearest hours | min power 0.05 kW (direct: 0.1 -> 0.05) | min power 1.0 kW (null).

Should fail: tests/manual_plan.py (traced baseline executes optimizer.py:5283; features, guard_pins, block_duty and 12 more too): no check solves a forced-ON pin with heat_pump_min_power 0 and asserts the step runs (>= 0.1 kW).

Candidate: No check pins a forced-ON step above 0 kW when the minimum power is 0; dropping the 0.1 kW floor is unseen. Severity claimed medium; down: 0.1 -> 0.0 kW on the pinned steps (a step pinned ON is planned off).

### 6b6eb0c1091c3c5c — custom_components/heatpump_optimizer/optimizer.py:5284 CLAMP_DROP (equivalent-candidate)

`return min(floor, upper) -> return (floor)` in `HeatPumpOptimizer._pin_on_power`. Gate: RED-AS-NULL (gate_rc 1, wall 2435.3 s, load1 1.0..0.92, provisional), red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] = the null's; more fails than null: [].

Step 4: probe `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6b6eb0c1091c3c5c.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6b6eb0c1091c3c5c.py`), metric: _pin_on_power(upper < floor) direct, and the solver bounds _apply_pins_to_bounds builds plus the plan through optimize(). Baseline direct_baseline=0.5 kW, mutant direct_mutant=1.0 kW. All RESULT lines: direct_baseline=0.5 kW; direct_mutant=1.0 kW; bounds_differ=0 count; plan_maxabs_diff_kw=0.0000 kW; bounds_calls=4 count; thread_factor=1.000; load1=1.71; swapins=0.

Inputs tried: direct upper 0.5 < floor 1.0 (moves 0.5 -> 1.0) | fuse caps 0.5 kW under min 1.0 kW with pins | min 6 kW above max 5 kW with pins | min below ceiling (null).

Should fail: none: the clamp is re-applied downstream.

Equivalent-candidate: Every production caller passes upper=p_max and _apply_pins_to_bounds (optimizer.py:2418) re-clamps min(min_on_power, high) with high <= p_max: 0 of 4 bounds lists differ and the plans are identical. Equivalent at every production-reachable input.

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_00298af0aa9d1903.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_39a6d2e97fd44ed5.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_4e5a67b907d13871.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6309f3e4a0a6c45f.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_6b6eb0c1091c3c5c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_8ac9888c3d5fed52.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_904118eef67fced3.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_905a40b5ecea024f.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a4f4c88e7480a514.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_a66e107749d0ae11.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ad01ae06d7ea84ec.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_be3a3a75280c7b7e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_cb58757b91fa48c4.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_deb281264473bdd6.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_ed5e3ec5b879ed90.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_fd57e13959b23a4c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/_tools/DHWCAP.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/_tools/HOLD_REACH.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/_tools/PRE.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/_tools/make_result.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/_tools/build_report.py`
- `gate_wave.sh` (out of tree, dispatch tip): the per-key driver named above

## Unfinished

- none

## Exposure

No docs/ or GitHub read. Read COMMON.md, D3.md, dev/audit/README.md, finding.schema.json and the carried slice reports and probes in the stripped worktree, this box's dispatch/inbox/wip refs, and the other 46 wave boxes' dispatch keys.tsv only to name their keys under not_reached. Re-fire: resumed from handoff-wip/finder-r11-D3-g21 @ d9d4e225 (8 of 16 gated, the null control and all 16 probes executed on the first machine); gates 9-16 ran on a second machine (nproc 4, Intel Xeon @ 2.30GHz) against the restored null.
