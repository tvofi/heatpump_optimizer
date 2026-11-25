# D3-s1 round 11, box D3-g16: the full gate for 16 D3.M3 full-net survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Box D3-g16: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython, alone on the box. Counts are final; every wall, CPU and load number is provisional.

## Machine and controls

```
taken_utc: 2026-11-22T21:39:33Z
nproc: 4
cpu_model: Intel(R) Xeon(R) Processor @ 2.10GHz
load1: 0.84
free -m:
               total        used        free      shared  buff/cache   available
Mem:           16087        1056       13527          12        1802       15031
Swap:              0           0           0
df -h $HOME:
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
python3: /opt/hpo/venv-ci/bin/python3 (/root/venv-ci -> /opt/hpo/venv-ci symlink, out of tree)
provisional: true

## re-fire container
taken_utc: 2026-11-25T00:48:39Z
nproc: 4
cpu_model: Intel(R) Xeon(R) Processor @ 2.10GHz
load1: 0.33
free -m:
               total        used        free      shared  buff/cache   available
Mem:           16087         734       14066          12        1558       15352
Swap:              0           0           0
df -h $HOME:
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
python3: /opt/hpo/venv-ci/bin/python3 (/root/venv-ci -> /opt/hpo/venv-ci symlink, out of tree)
provisional: true
```

Full-gate null control (`fullgate.py null`, comment-only marker): gate_rc=1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], summary ['3 TEST SCRIPT(S) FAILED'], wall 3297.9 s (provisional), load1 0.87..0.92. A mutant is KILLED only when run.sh is red with a script (or more FAIL lines in one) beyond this null; red with nothing beyond it is RED-AS-NULL, read as survived.

Procedure: gate_wave.sh (dispatch ref tip, out of tree): `gate_wave.sh null` once, then `gate_wave.sh run` gating each key of keys.tsv in order, one gate at a time, 4 h cap (TIMEOUT, never KILLED), tree reset to the baseline after each, checkpoint after each. Probes were authored and run from a separate baseline worktree ($HOME/probe-tree) and kept out of the gate's tree until the last gate finished, so no untracked .py joined harness_headers.py's scan mid-wave.

## Tally

- keys 16, gated 16, TIMEOUT 0, not gated 0
- verdicts: RED-AS-NULL 16
- KILLED by script: none
- classes: candidate 10, equivalent-candidate 6

## Gate table

| key | site | patch | verdict | killed_by | wall s (prov.) | load1 | class |
|---|---|---|---|---|---|---|---|
| 35d61c87783ebe66 | dhw_planner.py:680 GUARD_OFF | `if known is not None: -> if False:` | RED-AS-NULL | - | 3192.9 | 0.85..0.92 | candidate |
| 01acd6cc2431d71d | dhw_planner.py:692 CLAMP_DROP | `known_mask[: min(reach_step, n_steps)] = False -> known_mask[: (reach_step)] = False` | RED-AS-NULL | - | 3237.6 | 0.78..0.98 | equivalent-candidate |
| 8fc6a207d6600867 | dhw_planner.py:470 CMP_BOUND | `if surplus is None or not np.any(surplus[: len(prices)] > 1e-6): -> if surplus is None or not np.any(surplus[: len(prices)] >= 1e-6):` | RED-AS-NULL | - | 3288.7 | 0.76..1.0 | candidate |
| 72882f2ac25c19b1 | dhw_planner.py:474 CLAMP_DROP | `surplus = np.clip(surplus - space_demand[: len(prices)], 0.0, None) -> surplus = (surplus - space_demand[: len(prices)])` | RED-AS-NULL | - | 3320.5 | 0.92..1.0 | candidate |
| ea6dfc5a3c85cce3 | dhw_planner.py:2133 CMP_BOUND | `while pos < size: -> while pos <= size:` | RED-AS-NULL | - | 3138.9 | 0.93..0.92 | equivalent-candidate |
| a21e5757eab163a7 | dhw_planner.py:2140 CMP_BOUND | `if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)): -> if not bool(np.all(candidate[pos + 1: end + 1] < limit + 1e-9)):` | RED-AS-NULL | - | 3218.4 | 0.94..1.01 | candidate |
| b16740061447ef70 | dhw_planner.py:1018 CLAMP_DROP | `window_hours = max((end_idx - start_idx) * dt, dt) -> window_hours = ((end_idx - start_idx) * dt)` | RED-AS-NULL | - | 3191.2 | 0.94..1.0 | equivalent-candidate |
| e19cdb6bf198d1e7 | dhw_planner.py:1034 CMP_BOUND | `if p90 is not None and np.isfinite(p90) and count > 0: -> if p90 is not None and np.isfinite(p90) and count >= 0:` | RED-AS-NULL | - | 3204.9 | 0.85..0.92 | equivalent-candidate |
| 41000bf52dbaa1ad | dhw_planner.py:547 CLAMP_DROP | `threshold = max(1.0, float(np.percentile(pattern, 60))) -> threshold = (1.0)` | RED-AS-NULL | - | 3363.2 | 0.14..0.92 | candidate |
| 88d911d796fdd71d | dhw_planner.py:548 CMP_BOUND | `busy_hours = [h for h in range(24) if pattern[h] >= threshold] -> busy_hours = [h for h in range(24) if pattern[h] > threshold]` | RED-AS-NULL | - | 3303.7 | 0.87..0.92 | candidate |
| 3ec31b99309ca722 | dhw_planner.py:549 GUARD_OFF | `if not busy_hours: -> if False:` | RED-AS-NULL | - | 3352.0 | 0.78..0.92 | candidate |
| 9b890e4f1fdfcd41 | dhw_planner.py:556 GUARD_OFF | `if hour == prev + 1: -> if False:` | RED-AS-NULL | - | 3316.7 | 0.86..0.92 | equivalent-candidate |
| 84eb14f49ff66736 | dhw_planner.py:2232 CLAMP_DROP | `j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j) -> j for j in range((0), k + 1) if usable(j)` | RED-AS-NULL | - | 3210.1 | 0.86..0.85 | candidate |
| 7da9151a6a79c43e | dhw_planner.py:2234 GUARD_OFF | `if not candidates: -> if False:` | RED-AS-NULL | - | 3473.9 | 0.66..1.01 | candidate |
| 88a992e9013ee436 | dhw_planner.py:2236 GUARD_OFF | `if not candidates: -> if False:` | RED-AS-NULL | - | 3584.4 | 0.93..0.92 | equivalent-candidate |
| 50ae25437a296deb | dhw_planner.py:2280 CMP_BOUND | `if take <= 1e-6: -> if take < 1e-6:` | RED-AS-NULL | - | 3559.1 | 0.93..0.92 | candidate |

## Survivors: the D3.M4 answer and the probe

**35d61c87783ebe66** dhw_planner.py:680 GUARD_OFF, `if known is not None: -> if False:` (DhwPlanner._dhw_legionella_due), full gate RED-AS-NULL: **candidate**, severity claimed medium. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_35d61c87783ebe66.py`: baseline 0 count, mutant 1 count (cycle_placed_baseline=0 count; cycle_placed_mutant=1 count; mutant_step_price_known=0; null_inputs_moved=0 of 3 (-); thread_factor=1.000; load1=0.84; swapins=0). Inputs: partial known mask (12 published, 12 prior) with the one sub-ceiling price estimated; null: all-known, None (fresh optimizer), cheap step published. Reach: production: optimizer.py passes the per-step price_known mask to DhwPlanner (optimizer.py:4373) whenever the horizon runs past the published day-ahead prices. Should have failed: tests/features.py: the elastic-legionella block (_el_solve, ~20046-20100, 'a generous ceiling runs the cycle early on a known cheap hour') runs on a flat, fully published price profile; it lacks the twin where the only price under the ceiling is prior-estimated, asserting the cycle is not placed ('Prior-guessed steps never qualify').

**01acd6cc2431d71d** dhw_planner.py:692 CLAMP_DROP, `known_mask[: min(reach_step, n_steps)] = False -> known_mask[: (reach_step)] = False` (DhwPlanner._dhw_legionella_due), full gate RED-AS-NULL: **equivalent-candidate**. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_01acd6cc2431d71d.py`: inputs_tried=864 count; baseline_cycles_placed=178 count; outputs_differing=0 count; thread_factor=1.000; load1=0.84; swapins=0. Inputs: 864: tank 10/30/45/55/59.9/65 C x (200 L, 3 kW)/(3000 L, 0.5 kW)/(50 L, 6 kW) x known None/all/first-12/short-5 x cheap step 0/11/23 x ceiling 1.0/1e-6 x Off window none/steps 0-3. Why: reach_step is int(hot[0]) with hot indexing ramp[1:] (length n_steps), or n_steps itself, so min(reach_step, n_steps) == reach_step; numpy slicing past the end clamps besides.

**8fc6a207d6600867** dhw_planner.py:470 CMP_BOUND, `if surplus is None or not np.any(surplus[: len(prices)] > 1e-6): -> if surplus is None or not np.any(surplus[: len(prices)] >= 1e-6):` (DhwPlanner._dhw_planning_prices), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_8fc6a207d6600867.py`: baseline 2.000000000 per-kWh, mutant 1.999999333 per-kWh (step0_price_baseline=2.000000000 per-kWh; step0_price_mutant=1.999999333 per-kWh; max_abs_delta=6.667e-07 per-kWh; rank_changed=0; inputs_moved=1 of 6 (all_steps_1e-6); thread_factor=1.000; load1=1.02; swapins=0). Inputs: surplus exactly 1e-6 at its maximum (moves); None, zeros, 2e-6, 1 kW, nextafter(1e-6, 0) (do not move). Reach: exact float tie only: a forecast surplus equal to 1e-6 kW at its maximum; any other surplus gives identical prices. Should have failed: tests/features.py: 'hot-water planning ranks a fully covered step at the export price' (~4508-4512) feeds a 4 kW surplus; no check feeds a surplus whose maximum is exactly 1e-6 kW.

**72882f2ac25c19b1** dhw_planner.py:474 CLAMP_DROP, `surplus = np.clip(surplus - space_demand[: len(prices)], 0.0, None) -> surplus = (surplus - space_demand[: len(prices)])` (DhwPlanner._dhw_planning_prices), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_72882f2ac25c19b1.py`: baseline 2.000000 per-kWh, mutant 3.333333 per-kWh (step0_price_baseline=2.000000 per-kWh; step0_price_mutant=3.333333 per-kWh; cheapest_step_baseline=0; cheapest_step_mutant=1; null_inputs_moved=0 of 4 (-); thread_factor=1.000; load1=0.93; swapins=0). Inputs: surplus [1,0,0,0] kW against space demand [3,0,0,0] kW (moves: 2.0 -> 3.333 per kWh, cheapest step 0 -> 1); space demand 0.5, 1.0 (equal), None, zeros (do not move). Reach: production: the co-optimization replan passes the space profile (optimizer.py:2065 and 3986 -> DhwPlanner._build_dhw_requirements -> dhw_planner.py:1147); space demand above the PV surplus is the ordinary case on a cold sunny morning. Should have failed: tests/features.py: 'on the replan, space heating takes its surplus share first' (~4514-4521) feeds space demand 2 kW under a 4 kW surplus; it lacks the case where space demand exceeds the surplus, asserting the step stays at the import price.

**ea6dfc5a3c85cce3** dhw_planner.py:2133 CMP_BOUND, `while pos < size: -> while pos <= size:` (DhwPlanner._dhw_raise_fits), full gate RED-AS-NULL: **equivalent-candidate**. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_ea6dfc5a3c85cce3.py`: inputs_tried=116 count; baseline_refusals=44 count  (liveness: both verdicts occur); inputs_with_extra_pass=60 count; outputs_differing=0 count  (verdict, the candidate array after the call, any exception); thread_factor=1.000; load1=0.95; swapins=0. Inputs: 116: sizes 1/7/8/9/16/24/96 x slots 0/1/n-8/n-1/n x idle, flat-out with a high ceiling, flat-out with a tight ceiling, a ceiling breached only at the last step (60 land a pass at pos == size; 44 refused). Why: the extra pass at pos == size reads candidate[size] (it exists: n + 1 temperatures), runs extend_dhw_temps' step loop over an empty range and tests empty slices, so the verdict and the candidate are unchanged.

**a21e5757eab163a7** dhw_planner.py:2140 CMP_BOUND, `if not bool(np.all(candidate[pos + 1: end + 1] <= limit + 1e-9)): -> if not bool(np.all(candidate[pos + 1: end + 1] < limit + 1e-9)):` (DhwPlanner._dhw_raise_fits), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_a21e5757eab163a7.py`: baseline 1, mutant 0 (raise_fits_baseline=1; raise_fits_mutant=0; non_tie_inputs_moved=0 of 4 (-); thread_factor=1.000; load1=0.86; swapins=0). Inputs: a ceiling whose value + 1e-9 equals the simulated temperature to the last bit (moves); a rounded 64 C ceiling, the ceiling at the temperature, 2e-9 and 0.1 K below (do not move). Reach: exact float tie only: a candidate temperature equal to max(ceiling + 0.5, base) + 1e-9 to the last bit. Should have failed: tests/features.py: the F22 raise-fits block (~69314-69330) compares the chunked check with a reference decision on ordinary inputs; no check builds a temperature exactly on limit + 1e-9.

**b16740061447ef70** dhw_planner.py:1018 CLAMP_DROP, `window_hours = max((end_idx - start_idx) * dt, dt) -> window_hours = ((end_idx - start_idx) * dt)` (DhwPlanner._dhw_window_floors), full gate RED-AS-NULL: **equivalent-candidate**. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_b16740061447ef70.py`: inputs_tried=600 count; stats_branch_live=1  (count 8 at p90 0 moves the ready temps against no stats: the blend is reached); outputs_differing=0 count; thread_factor=1.000; load1=0.83; swapins=0. Inputs: 600: specs '06:00-08:30, 17:00-22:00', '00:00-24:00', '23:00-23:15', '05:45-06:00', '21:00-03:00' x (dt, n) (0.25, 96), (1, 24), (0.25, 1), (1, 3) x start 0/5.75/22 h x learned stats none/count 0/negative/3/8 at p90 0/0 at p90 0/negative p90/1e300/NaN-inf/unparseable. Why: a window start has in_window[start_idx] True, so end_idx >= start_idx + 1 and (end_idx - start_idx) * dt >= dt already.

**e19cdb6bf198d1e7** dhw_planner.py:1034 CMP_BOUND, `if p90 is not None and np.isfinite(p90) and count > 0: -> if p90 is not None and np.isfinite(p90) and count >= 0:` (DhwPlanner._dhw_window_floors), full gate RED-AS-NULL: **equivalent-candidate**. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_e19cdb6bf198d1e7.py`: inputs_tried=600 count; stats_branch_live=1  (count 8 at p90 0 moves the ready temps against no stats: the blend is reached); outputs_differing=0 count; thread_factor=1.000; load1=0.44; swapins=0. Inputs: the same 600 inputs as b16740061447ef70, every stats set keyed by the planner's own window labels; liveness: count 8 at p90 0 moves the ready temps. Why: at count 0 the blend weight w = min(1, 0/8) = 0 and (1 - 0) * e + 0 * max(0, p90) == e exactly for every finite p90; a negative count fails both comparisons.

**41000bf52dbaa1ad** dhw_planner.py:547 CLAMP_DROP, `threshold = max(1.0, float(np.percentile(pattern, 60))) -> threshold = (1.0)` (DhwPlanner._effective_dhw_windows), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_41000bf52dbaa1ad.py`: baseline 10.0 h, mutant 13.0 h (window_hours_baseline=10.0 h; window_hours_mutant=13.0 h; mutant_raises=0; null_delta_hours=0.0 h; inputs_moved=1 of 10 (mean1_shoulder_1.1); thread_factor=1.000; load1=0.88; swapins=0). Inputs: 10 learned patterns: shipped default, flat 1.0, flat 0.5, mean-1 with 3 shoulder hours at 1.1 under p60 1.42 (moves: 10 h -> 13 h), plateau 1.0/2.0, alternating 2.0/0.2, single peak, all 1 - 1e-12, plateau 0.5/1.25, wrap past midnight. Reach: production: a learned profile is normalised to mean 1 (DhwUsageLearner.normalize_profile), and any profile with 40 % of its hours above 1 has p60 > 1. Should have failed: tests/features.py: the window/floor block (~38020-38033, _wf_params from the house profile) and the _r7d203 window-capacity cases (~63133) derive learned windows only from the shipped profile, whose p60 is 0.83 < 1; no check derives them from a mean-1 profile whose p60 is above 1.

**88d911d796fdd71d** dhw_planner.py:548 CMP_BOUND, `busy_hours = [h for h in range(24) if pattern[h] >= threshold] -> busy_hours = [h for h in range(24) if pattern[h] > threshold]` (DhwPlanner._effective_dhw_windows), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_88d911d796fdd71d.py`: baseline 16.0 h, mutant 24.0 h (window_hours_baseline=16.0 h; window_hours_mutant=24.0 h; mutant_raises=0; null_delta_hours=0.0 h; inputs_moved=3 of 10 (plateau_1.0_peak_2.0,alternating_2.0_0.2,mean1_plateau_1.25); thread_factor=1.000; load1=0.78; swapins=0). Inputs: the same 10 patterns; plateau 0.5/1.25 (16 h -> 24 h), plateau 1.0/2.0 and alternating 2.0/0.2 move. Reach: production: a plateau at the 60th percentile (clipped or flat learned profiles) puts the threshold exactly on pattern values. Should have failed: tests/features.py: the same window/floor block (~38020-38033) and ~63133 use only the shipped profile; no check feeds a pattern with hours exactly at the threshold.

**3ec31b99309ca722** dhw_planner.py:549 GUARD_OFF, `if not busy_hours: -> if False:` (DhwPlanner._effective_dhw_windows), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_3ec31b99309ca722.py`: baseline 24.0 h, mutant 1 (window_hours_baseline=24.0 h; window_hours_mutant=nan h; mutant_raises=1; null_delta_hours=0.0 h; inputs_moved=2 of 10 (flat_0.5_unnormalised,all_just_below_1); thread_factor=1.000; load1=0.94; swapins=0). Inputs: flat 0.5 (not mean-1) and all 1 - 1e-12 raise IndexError under the mutant; the 8 other patterns do not move. Reach: direct call; through production only at a learned profile whose every hour sits below 1.0, which normalize_profile's mean-1 rescale admits only within its 1e-12 tolerance (all_just_below_1). Should have failed: tests/features.py: the window/floor block (~38020-38033) never feeds a pattern with every hour below 1.0, asserting the [FULL_DAY] fallback.

**9b890e4f1fdfcd41** dhw_planner.py:556 GUARD_OFF, `if hour == prev + 1: -> if False:` (DhwPlanner._effective_dhw_windows), full gate RED-AS-NULL: **equivalent-candidate**. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_9b890e4f1fdfcd41.py`: window_hours_baseline=12.0 h; window_hours_mutant=12.0 h; mutant_raises=0; null_delta_hours=0.0 h; inputs_moved=0 of 10 (-); thread_factor=1.000; load1=0.81; swapins=0. Inputs: 10 learned patterns: contiguous runs, a wrap past midnight (22-02), alternating single hours, plateaus, a single peak, flat and non-normalised. Why: each hour then opens its own one-hour window, and dhw_schedule._normalize (applied through parse_windows(format_windows(...))) merges touching windows back (start <= last_end), so the returned windows are identical.

**84eb14f49ff66736** dhw_planner.py:2232 CLAMP_DROP, `j for j in range(max(0, k - max_lead_steps), k + 1) if usable(j) -> j for j in range((0), k + 1) if usable(j)` (DhwPlanner._plan_dhw_cheapest_first), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_84eb14f49ff66736.py`: baseline 10, mutant 0 (first_charge_step_baseline=10; first_charge_step_mutant=0; charge_steps_outside_lead_window_mutant=1 count; null_inputs_moved=0 of 3 (-); thread_factor=1.000; load1=0.69; swapins=0). Inputs: 12 h horizon, need 55 C at step 10, cheapest price at step 0, max_lead_steps 2 (moves: step 10 -> 0); lead 24, flat prices, the cheapest step inside the lead window (do not move). Reach: production: ctx.max_lead_steps is ceil(ThermalModel.dhw_hold_hours() / dt) (dhw_planner.py:1173, 1214), the hours the tank holds heat, under the horizon whenever the tank's standby loss is material. Should have failed: tests/features.py: the cheapest-first cases (~63622 with max_lead_steps=6, ~82539 _pli_greedy) never put the cheapest step outside the lead window; none asserts that no charge lands before k - max_lead_steps when a usable step exists inside it.

**7da9151a6a79c43e** dhw_planner.py:2234 GUARD_OFF, `if not candidates: -> if False:` (DhwPlanner._plan_dhw_cheapest_first), full gate RED-AS-NULL: **candidate**, severity claimed medium. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_7da9151a6a79c43e.py`: baseline 55.451 C  (requirement 55), mutant 41.891 C (dhw_kw_sum_baseline=1.9870 kW; dhw_kw_sum_mutant=0.0000 kW; tank_at_need_baseline=55.451 C  (requirement 55); tank_at_need_mutant=41.891 C; null_inputs_moved=0 of 2 (-); thread_factor=1.000; load1=0.86; swapins=0). Inputs: a forced-off pin over the whole lead window (steps 8-10) (moves: 1.987 kW bought at step 0 -> nothing; tank 55.45 -> 41.89 C at the need); no pin, a pin outside the lead window (do not move). Reach: production: forced_off carries manual pins and the quiet Off window. Should have failed: tests/features.py: the cheapest-first cases (~63622, ~82539) pass no forced_off; no check pins the whole lead window off and asserts the shortfall is bought earlier.

**88a992e9013ee436** dhw_planner.py:2236 GUARD_OFF, `if not candidates: -> if False:` (DhwPlanner._plan_dhw_cheapest_first), full gate RED-AS-NULL: **equivalent-candidate**. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_88a992e9013ee436.py`: inputs_tried=21 count; baseline_plans_with_nothing_bought=6 count  (the no-candidate path is reached); outputs_differing=0 count (-); thread_factor=1.000; load1=0.92; swapins=0. Inputs: 21: all steps forced off, a ceiling below the tank, a ceiling 0.05 K over it, the lead window pinned, two requirements, big draws, an ordinary case, each at max_lead_steps 0/2/24 (6 plans buy nothing: the no-candidate path is reached). Why: with no candidate the fall-through sorts an empty list, buys nothing, and `if added <= 1e-9: unreachable.add(k)` does exactly what the guard's `unreachable.add(k); continue` does.

**50ae25437a296deb** dhw_planner.py:2280 CMP_BOUND, `if take <= 1e-6: -> if take < 1e-6:` (DhwPlanner._plan_dhw_cheapest_first), full gate RED-AS-NULL: **candidate**, severity claimed low. Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_50ae25437a296deb.py`: baseline 0.0000 kW, mutant 0.1000 kW (step0_kw_baseline=0.0000 kW; step0_kw_mutant=0.1000 kW; off_tie_inputs_moved=0 of 4 (-); thread_factor=1.000; load1=0.79; swapins=0). Inputs: a 6-step horizon with only step 0 runnable and c_dhw tuned to 0.2319999999922984 so the binding headroom d * c_dhw == 1e-6 exactly (moves: 0 -> 0.1 kW); headroom 1e-9 K either side, c_dhw 0.232 and a loose ceiling (do not move). Reach: exact float tie only: needed, spare and headroom never land on 1e-6 kWh to the last bit except by construction (here c_dhw is tuned to 0.2319999999922984). Should have failed: tests/features.py: the cheapest-first cases (~63622, ~82539) never land take on exactly 1e-6 kWh; no check pins the boundary as a skip.

## Findings

None numbered here: candidates are returned under `gate_survivors` for the orchestrator's consolidation to number (finding ids D3-s1-01..71 are taken).

## Unfinished

- none

## Coverage

D3.M1, D3.M2, D3.M4, D3.M5 and the C-items are carried verbatim from REPORT-D3-u1b.json. D3.M3 (this wave): box D3-g16 full-gated 16 of its 16 keys (keys.tsv; dev/audit/rounds/round11/D3/s1/wave/D3-g16/keys.tsv) one at a time with `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh) driven by gate_wave.sh run; records dev/audit/rounds/round11/D3/s1/wave/D3-g16/gates/<key>.json, null control dev/audit/rounds/round11/D3/s1/wave/D3-g16/gates/null.json (gate_rc=1, failed ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py']). The wave list (742 keys over boxes D3-g01..D3-g47) was read from each dispatch/finder-r11-D3-gNN ref's keys.tsv: 742 keys; the 726 keys of the other 46 boxes are not_reached here, by box. Earlier boxes' D3.M3 rows (REPORT-D3-u1a..d, -top6, -rem) cover the fast net, the full net and the 35 gated pre-wave survivors, none of them in this wave list. redispatched C3/C5 carried verbatim from REPORT-D3-u1b.json's D3.M3 row.

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_35d61c87783ebe66.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_01acd6cc2431d71d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_8fc6a207d6600867.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_72882f2ac25c19b1.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_ea6dfc5a3c85cce3.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_a21e5757eab163a7.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_b16740061447ef70.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_e19cdb6bf198d1e7.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_41000bf52dbaa1ad.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_88d911d796fdd71d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_3ec31b99309ca722.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_9b890e4f1fdfcd41.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_84eb14f49ff66736.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_7da9151a6a79c43e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_88a992e9013ee436.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_50ae25437a296deb.py`

## Exposure

No docs/ or GitHub records read. Read: COMMON.md, D3.md, dev/audit/README.md, finding.schema.json, the u1 slice reports and REPORT-D3-top6/-rem with their probes (the pattern), the carried M4 answers for this box's keys, the production lines and the tests/features.py checks named under should_fail. To enumerate the wave list for not_reached the seat read keys.tsv (and nothing else) from each sibling dispatch/finder-r11-D3-gNN ref.

