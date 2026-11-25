# D3-s1 box D3-g17 — full gate for 16 u1 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, box D3-g17. findings: [] (ids assigned at consolidation); candidates under `gate_survivors`.

## Machine and controls

```
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087        1067       13516          12        1801       15019
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.83
date: 2026-11-22T21:40:09Z
python3: /opt/hpo/venv-ci/bin/python3 (symlinked at $HOME/venv-ci)
re-fire 2026-11-25T00:48:50Z (resumed seat)
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087         738       14070          12        1549       15348
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.44
re-fire seat 2026-11-25: all 16 probes re-run in a fresh baseline worktree ~/probe-tree on this machine; every RESULT line except load1/thread_factor/swapins identical to the predecessor's .out.txt
re-fire seat: gate b1a8d3056bf42597 was interrupted twice before recording (monitor teardown at 00:49Z, container restart ~01:14Z); each time the stale lease was released, the tree reset to the baseline, the partial log set aside, and the gate re-taken from scratch at 01:15:29Z
```

Null control: `fullgate.py null` (comment-only marker), record `dev/audit/rounds/round11/D3/s1/wave/D3-g17/gates/null.json`: gate_rc 1, failed scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], wall 3358.4 s (provisional).
Box note: Box D3-g17 null control (fullgate.py null, comment-only marker), 2026-11-22T21:41Z..22:36Z, wall 3358.4 s (provisional), load1 0.85..0.93, nproc 4.
gate_rc=1, red on artefact checks only, read as the box's floor (a mutant is KILLED only beyond these counts):
- python3 tests/closure.py selftest: 2 of 118 FAILED (merge-reason pins: status 'skip-not-under-scoped' in this detached, stripped worktree)
- python3 tests/entities.py: 1 of 2723 FAILED ('and is accepted when it does' [the scoped path records only what the diff can reach]: the scoped-recording rig in this checkout)
- python3 tests/harness_headers.py: 3 of 115 FAILED (round4/D6/claims.py header 123/0 vs printed 122/1 and its committed output rewritten: the finder-wall strip removed what claims.py reads)
No script is red because of the machine (card.mjs passed at the default heap), so the null was not re-taken.

The null was taken by the predecessor seat on this box before a stall; the re-fire seat restored it from the checkpoint (gate_wave.sh null: once, restored on a re-fire) and re-ran all 16 probes in a fresh baseline worktree with identical RESULT lines. All walls/loads are provisional (nproc 4, Intel Xeon @ 2.10GHz).

## Tally

- gated: 16 of 16
- verdicts: {'RED-AS-NULL': 16}
- KILLED by: none
- classes: {'equivalent-candidate': 6, 'candidate': 10}
- candidates: 10; equivalent-candidates: 6

| key | site | verdict | wall_s | load1 | class |
|---|---|---|---|---|---|
| 0aa6eaace756da92 | custom_components/heatpump_optimizer/dhw_planner.py:2285 CMP_BOUND | RED-AS-NULL | 3286.1 | 0.87..0.97 | equivalent-candidate |
| eae8cfee2ddbd16d | custom_components/heatpump_optimizer/dhw_planner.py:2285 CMP_BOUND | RED-AS-NULL | 3252.4 | 0.82..0.92 | equivalent-candidate |
| fd9b39c806b43b56 | custom_components/heatpump_optimizer/dhw_planner.py:2303 CMP_BOUND | RED-AS-NULL | 3262.5 | 0.78..0.92 | equivalent-candidate |
| 61862d35b6b2885d | custom_components/heatpump_optimizer/dhw_planner.py:2307 CLAMP_DROP | RED-AS-NULL | 3197.3 | 0.78..0.94 | candidate |
| 5b123e9e5b76ebc3 | custom_components/heatpump_optimizer/dhw_planner.py:2227 CMP_BOUND | RED-AS-NULL | 3219.7 | 0.8..0.92 | candidate |
| 4f1f941124291aeb | custom_components/heatpump_optimizer/dhw_planner.py:2228 CMP_BOUND | RED-AS-NULL | 3249.6 | 0.78..0.92 | candidate |
| c1d6f40c74ee74ad | custom_components/heatpump_optimizer/dhw_planner.py:1510 CLAMP_DROP | RED-AS-NULL | 3281.1 | 0.86..1.03 | candidate |
| b1a8d3056bf42597 | custom_components/heatpump_optimizer/dhw_planner.py:1527 CLAMP_DROP | RED-AS-NULL | 3324.2 | 0.47..0.92 | candidate |
| 8db7b149f5f9eda5 | custom_components/heatpump_optimizer/dhw_planner.py:1528 CLAMP_DROP | RED-AS-NULL | 3207.4 | 0.87..1.06 | equivalent-candidate |
| ddf4602569b157b1 | custom_components/heatpump_optimizer/dhw_planner.py:1529 CMP_BOUND | RED-AS-NULL | 3183.4 | 1.22..0.92 | candidate |
| 247372989ae65baa | custom_components/heatpump_optimizer/dhw_planner.py:1535 CLAMP_DROP | RED-AS-NULL | 3226.3 | 0.78..0.92 | candidate |
| b1074e70396100d8 | custom_components/heatpump_optimizer/dhw_planner.py:1538 CLAMP_DROP | RED-AS-NULL | 3131.2 | 0.71..0.97 | candidate |
| 539e5aeaccf156f3 | custom_components/heatpump_optimizer/dhw_planner.py:1546 GUARD_OFF | RED-AS-NULL | 3134.2 | 0.89..0.92 | equivalent-candidate |
| 6e1174561ae9297c | custom_components/heatpump_optimizer/dhw_planner.py:1546 CMP_BOUND | RED-AS-NULL | 3215.2 | 1.01..0.92 | equivalent-candidate |
| b7a6f145165338bf | custom_components/heatpump_optimizer/dhw_planner.py:1606 RETURN_DEL | RED-AS-NULL | 3338.9 | 0.72..1.0 | candidate |
| 2074f3eefe8521aa | custom_components/heatpump_optimizer/dhw_planner.py:1608 GUARD_OFF | RED-AS-NULL | 3512.5 | 0.85..0.96 | candidate |

## Survivors: step-4 answers and probe numbers

**0aa6eaace756da92** `custom_components/heatpump_optimizer/dhw_planner.py:2285 CMP_BOUND` (`if 0.0 < plan[j] < min_run_power: -> if 0.0 < plan[j] <= min_run_power:`), gate RED-AS-NULL -> **equivalent-candidate**. Reach: executed. Check that should fail: none: at plan[j] == min_run_power the mutant assigns plan[j] the value it already holds; no check can fail. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_0aa6eaace756da92.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_0aa6eaace756da92.py`): tie_min_run_power=1.67716250482; tie_plan_baseline=[0,0,0,0,0,0,0,0,1.6771625,0,0,0]; tie_plan_mutant=[0,0,0,0,0,0,0,0,1.6771625,0,0,0]; tie_delta_kw=0; sweep_inputs=160; differing_inputs=0; sweep_max_delta_kw=0; null_delta_kw=0. Inputs tried: tie(min_run_power==landed power);160 random (derate 0/0.2, min_run_power 0.1/0.5/1.5/3.0, initial plans with 0/0.5/3.0, integer-price ties).

**eae8cfee2ddbd16d** `custom_components/heatpump_optimizer/dhw_planner.py:2285 CMP_BOUND` (`if 0.0 < plan[j] < min_run_power: -> if 0.0 <= plan[j] < min_run_power:`), gate RED-AS-NULL -> **equivalent-candidate**. Reach: executed. Check that should fail: none: the line runs only after a take > 1e-6 was added, so plan[j] > 0 and 0.0 < / 0.0 <= agree. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_eae8cfee2ddbd16d.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_eae8cfee2ddbd16d.py`): edge_inputs=9; edge_delta_kw=0; sweep_inputs=160; differing_inputs=0; sweep_max_delta_kw=0; null_delta_kw=0. Inputs tried: derate 0/0.2/0.9 x prices (falling, all-zero, one NaN) at min_run_power 1.5; 160 random.

**fd9b39c806b43b56** `custom_components/heatpump_optimizer/dhw_planner.py:2303 CMP_BOUND` (`if added <= 1e-9: -> if added < 1e-9:`), gate RED-AS-NULL -> **equivalent-candidate**. Reach: executed. Check that should fail: none: added is 0.0 or a take > 1e-6 (the take <= 1e-6 skip), never exactly 1e-9. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_fd9b39c806b43b56.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_fd9b39c806b43b56.py`): tiny_gap_delta_kw=0; sweep_inputs=160; differing_inputs=0; sweep_max_delta_kw=0; null_delta_kw=0. Inputs tried: initial temp 54.99/54.999999/54.9999999999/55.0 against a 55 C floor (shortfall at the take threshold); 160 random.

**61862d35b6b2885d** `custom_components/heatpump_optimizer/dhw_planner.py:2307 CLAMP_DROP` (`return np.clip(plan, 0.0, p_dhw_max) -> return (plan)`), gate RED-AS-NULL -> **candidate**. Reach: method-level only: DhwPlanner.optimize sets min_run_power <= p_dhw_run (dhw_planner.py:1141), and its _ctx_clamp re-clamps later. Check that should fail: tests/features.py _plan_dhw_cheapest_first callers (_r7d203_greedy_steps at features.py:63168, the derate check at features.py:82539, the min-cost/greedy comparison at features.py:63622): none passes min_run_power > p_dhw_max and asserts the returned plan stays <= ctx.p_dhw_max. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_61862d35b6b2885d.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_61862d35b6b2885d.py`): plan_baseline=[0,0,0,0,0,0,0,0,3,0,0,0]; plan_mutant=[0,0,0,0,0,0,0,0,3.5,0,0,0]; plan_max_baseline=3; plan_max_mutant=3.5; plan_max_null_delta=0; sweep_inputs=160; sweep_differing_inputs=0; sweep_max_delta_kw=0. Inputs tried: min_run_power 3.5/p_dhw_max 3.0; null 0.1/3.0; 160 random (derate 0/0.2/0.9, initial plans) for a float overshoot. Finding candidate: No check pins cheapest-first's final clip to p_dhw_max; dropping it is unseen.

**5b123e9e5b76ebc3** `custom_components/heatpump_optimizer/dhw_planner.py:2227 CMP_BOUND` (`plan[j] < p_dhw_max - 1e-6 -> plan[j] <= p_dhw_max - 1e-6`), gate RED-AS-NULL -> **candidate**. Reach: boundary only: an initial plan step exactly at p_dhw_max - 1e-6. Check that should fail: tests/features.py _plan_dhw_cheapest_first callers (_r7d203_greedy_steps at features.py:63168, the derate check at features.py:82539, the min-cost/greedy comparison at features.py:63622): none seeds an initial_plan step at exactly p_dhw_max - 1e-6. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_5b123e9e5b76ebc3.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_5b123e9e5b76ebc3.py`): plan_baseline=[0,0,0,0,0,0,0,2.999999,0,0,0.202506121,0]; plan_mutant=[0,0,0,0,0,0,0,3,0,0,0.202506121,0]; step7_baseline=2.999999; step7_mutant=3; delta_kw=1e-06; cost_baseline=0.907518264; cost_mutant=0.907518364; null_delta_kw=0; sweep_inputs=120; sweep_differing_inputs=0. Inputs tried: initial plan step 7 at p_dhw_max-1e-6 (tie), at p_dhw_max-2e-6 (null); 120 random (no tie: 0 differ). Finding candidate: No check seeds cheapest-first at p_dhw_max-1e-6; the candidate bound's < -> <= is unseen.

**4f1f941124291aeb** `custom_components/heatpump_optimizer/dhw_planner.py:2228 CMP_BOUND` (`and temps[j + 1] < ceiling[j] - 0.1 -> and temps[j + 1] <= ceiling[j] - 0.1`), gate RED-AS-NULL -> **candidate**. Reach: boundary only: a tank temperature exactly 0.1 C under the step's ceiling. Check that should fail: tests/features.py _plan_dhw_cheapest_first callers (_r7d203_greedy_steps at features.py:63168, the derate check at features.py:82539, the min-cost/greedy comparison at features.py:63622): none places a step's simulated temperature exactly at ceiling - 0.1. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_4f1f941124291aeb.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_4f1f941124291aeb.py`): tie_temp=60.01999856691201; max_temp_step3=61.11999856691201; plan_baseline=[0,0,0,0,0,0,0,0,1.13391471,2.03671589,0,0]; plan_mutant=[0,0,0,0.1,0,0,0,0,1.07658536,2.03677205,0,0]; step3_baseline=0; step3_mutant=0.1; delta_kw=0.1; null_delta_kw=0; sweep_inputs=120; sweep_differing_inputs=0. Inputs tried: exact tie temps[4]==ceiling[3]-0.1 (max_temp searched by nextafter); ceiling 2 ulp up (null); 120 random (0 differ). Finding candidate: No check ties a tank temperature to ceiling-0.1 in cheapest-first; < -> <= is unseen.

**c1d6f40c74ee74ad** `custom_components/heatpump_optimizer/dhw_planner.py:1510 CLAMP_DROP` (`influence = np.where(lag >= 0, np.power(decay, np.maximum(lag, 0)) / c_dhw, 0.0) -> influence = np.where(lag >= 0, np.power(decay, (lag)) / c_dhw, 0.0)`), gate RED-AS-NULL -> **candidate**. Reach: decay 0 only (standby loss over one step >= the stored heat); a realistic tank decays ~0.988/h; plan output unchanged. Check that should fail: none in the suite: no check runs _plan_dhw_min_cost with tank decay 0 under warnings-as-errors or counts its RuntimeWarnings. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_c1d6f40c74ee74ad.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_c1d6f40c74ee74ad.py`): null_decay=0.988; null_warnings_baseline=0; null_warnings_mutant=0; null_plan_delta_kw=0; decay0_decay=0; decay0_warnings_baseline=0; decay0_warnings_mutant=1; decay0_plan_delta_kw=0; sweep_inputs=80; differing_inputs=0; sweep_max_delta_kw=0. Inputs tried: decay 0.988 (null) and 0.0, 24 steps; 80 random scenarios at decay 0.988 for plan deltas. Finding candidate: No check sees the DHW LP's 0**negative RuntimeWarning at tank decay 0 once the lag clamp is dropped.

**b1a8d3056bf42597** `custom_components/heatpump_optimizer/dhw_planner.py:1527 CLAMP_DROP` (`demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None) -> demand = (np.asarray(space_demand, dtype=float))`), gate RED-AS-NULL -> **candidate**. Reach: p_total_max <= 0 only (DhwPlanner.optimize passes the configured p_max); with p_total_max > 0, 0/120 inputs separate. Check that should fail: tests/features.py check 'the DHW cost program plans under space-heating contention' (features.py:63744), the suite's only _plan_dhw_min_cost call with space_demand/p_total_max: it feeds demand >= 0 with p_total_max 5, never a negative space demand. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1a8d3056bf42597.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1a8d3056bf42597.py`): differing_pmax_pos=0/120; max_delta_kw=0; differing_pmax_nonpos=120/120; null_differing=0/60. Inputs tried: 120 random at p_total_max 1/3 with demand -3..4; 120 random at p_total_max -0.5/0 with demand -3..4; 60 at p_total_max 0 with demand 0..4 (null). Finding candidate: No check feeds the DHW LP a negative space demand; dropping its clip is unseen.

**8db7b149f5f9eda5** `custom_components/heatpump_optimizer/dhw_planner.py:1528 CLAMP_DROP` (`headroom = np.clip(p_total_max - demand, 0.0, None) -> headroom = (p_total_max - demand)`), gate RED-AS-NULL -> **equivalent-candidate**. Reach: executed. Check that should fail: none: a negative headroom forces a constant displacement at E=0; the marginal DHW price, hence the plan, is unchanged. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_8db7b149f5f9eda5.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_8db7b149f5f9eda5.py`): edge_inputs=9; edge_delta_kw=0; sweep_inputs=120; differing_inputs=0; sweep_max_delta_kw=0. Inputs tried: 3 price shapes (flat, alternating, one cheap) x 3 demand shapes (all over, alternating, one 50 kW) at p_total_max 3; 120 random with demand 0..8.

**ddf4602569b157b1** `custom_components/heatpump_optimizer/dhw_planner.py:1529 CMP_BOUND` (`spare = demand < p_total_max - 1e-6 -> spare = demand <= p_total_max - 1e-6`), gate RED-AS-NULL -> **candidate**. Reach: boundary only: a step's space demand exactly p_total_max - 1e-6. Check that should fail: tests/features.py check 'the DHW cost program plans under space-heating contention' (features.py:63744), the suite's only _plan_dhw_min_cost call with space_demand/p_total_max: it never places a step's demand exactly at p_total_max - 1e-6. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_ddf4602569b157b1.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_ddf4602569b157b1.py`): plan_baseline=[1e-06,0,0,1.31032673,0,0]; plan_mutant=[1.37938921,0,0,0,0,0]; step0_delta_kw=1.379; cost_baseline=3.93098; cost_mutant=1.37939; null_delta_kw=0; sweep_inputs=80; differing_inputs=0; sweep_max_delta_kw=0. Inputs tried: step-0 demand exactly p_total_max-1e-6 (tie); p_total_max-2e-6 (null); 80 random (no tie: 0 differ). Finding candidate: No check places space demand at p_total_max-1e-6; the DHW LP's spare test < -> <= is unseen.

**247372989ae65baa** `custom_components/heatpump_optimizer/dhw_planner.py:1535 CLAMP_DROP` (`window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / max(dt, 1e-6)))) -> window = max(1, int(round(_DHW_REFILL_WINDOW_HOURS / (dt))))`), gate RED-AS-NULL -> **candidate**. Reach: dt <= 0 only (ctx.dt is the configured positive step length); dt 1, 0.25, 1e-7 do not separate. Check that should fail: none in the suite: no check calls _plan_dhw_min_cost with a zero step length. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_247372989ae65baa.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_247372989ae65baa.py`): positive_dt_differing=0; dt0_baseline=None; dt0_mutant=ZeroDivisionError; dtneg_baseline=None; dtneg_mutant=None. Inputs tried: dt 1.0, 0.25, 1e-7 (window >= horizon in both), 0.0, -1.0. Finding candidate: No check calls the DHW LP at dt 0; dropping the window's max(dt, 1e-6) floor is unseen.

**b1074e70396100d8** `custom_components/heatpump_optimizer/dhw_planner.py:1538 CLAMP_DROP` (`lo = max(0, j - window) -> lo = (0)`), gate RED-AS-NULL -> **candidate**. Reach: realistic: any horizon longer than the 6 h refill window (a 24 h horizon) with a cheap spare step more than 6 h before a full one. Check that should fail: tests/features.py check 'the DHW cost program plans under space-heating contention' (features.py:63744), the suite's only _plan_dhw_min_cost call with space_demand/p_total_max: its 8-step 1 h horizon never puts a spare step more than the 6 h window before a full one, so the window's lower bound is never exercised. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1074e70396100d8.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1074e70396100d8.py`): plan_baseline=[1.75073672,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]; plan_mutant=[0,0,0,0,0,0,0,0,0,0,1.47660443,0,0,0,0,0]; cost_baseline=1.5757; cost_mutant=0.14766; delta_kw=1.751; null_flat_delta_kw=0; sweep_inputs=120; differing_inputs=7; sweep_max_delta_kw=1.88. Inputs tried: 16 steps dt 1 h: spare cheap step 0, full steps 1-13 and 15, step 10 cheapest, spare step 14 at 4.0; flat prices (null); 120 random at dt 1. Finding candidate: No check bounds the DHW LP's refill search window backwards; lo = 0 is unseen.

**539e5aeaccf156f3** `custom_components/heatpump_optimizer/dhw_planner.py:1546 GUARD_OFF` (`if not np.any(premium > 1e-9): -> if False:`), gate RED-AS-NULL -> **equivalent-candidate**. Reach: executed. Check that should fail: none: with every premium 0 the kept displacement columns cost nothing and the headroom rows never bind. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_539e5aeaccf156f3.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_539e5aeaccf156f3.py`): edge_inputs=9; edge_delta_kw=0; sweep_inputs=120; differing_inputs=0; sweep_max_delta_kw=0. Inputs tried: 3 price shapes (flat, falling, zero) x 3 demand shapes (all full, all spare, alternating); 120 random.

**6e1174561ae9297c** `custom_components/heatpump_optimizer/dhw_planner.py:1546 CMP_BOUND` (`if not np.any(premium > 1e-9): -> if not np.any(premium >= 1e-9):`), gate RED-AS-NULL -> **equivalent-candidate**. Reach: executed. Check that should fail: none observable: at a premium of exactly 1e-9 the mutant keeps a 1e-9 premium below HiGHS's tolerance; the plan is unchanged. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_6e1174561ae9297c.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_6e1174561ae9297c.py`): tie_premium=1e-09; tie_inputs=3; tie_delta_kw=0; sweep_inputs=80; differing_inputs=0; sweep_max_delta_kw=0. Inputs tried: 3 tie layouts (full step at price 0 beside spare steps at 1e-9); 80 random.

**b7a6f145165338bf** `custom_components/heatpump_optimizer/dhw_planner.py:1606 RETURN_DEL` (`return best -> pass`), gate RED-AS-NULL -> **candidate**. Reach: the probe reaches line 1606 by a direct call with one NaN price (linprog raises ValueError); no traced closure baseline executes it, and whether DhwPlanner.optimize can pass a NaN price is not established: the line is reachable at the method, not shown reachable end to end. Check that should fail: none in the suite executes line 1606: a direct check that _plan_dhw_min_cost returns None (greedy fallback) when linprog raises. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b7a6f145165338bf.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b7a6f145165338bf.py`): nan_price_linprog_raised=ValueError; nan_price_baseline=None; nan_price_mutant=UnboundLocalError; finite_differing=0. Inputs tried: one NaN price at step 3; all-finite prices (null). Finding candidate: No check makes the DHW LP's solver raise; deleting the fallback return is unseen.

**2074f3eefe8521aa** `custom_components/heatpump_optimizer/dhw_planner.py:1608 GUARD_OFF` (`if not result.success: -> if False:`), gate RED-AS-NULL -> **candidate**. Reach: solver failure only: the LP is feasible and bounded on every input tried (priced shortfall slack); the probe stubs a status-1 result with an x. Check that should fail: none in the suite: no check makes linprog report success=False with an x and asserts the greedy fallback (None). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_2074f3eefe8521aa.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_2074f3eefe8521aa.py`): status1_baseline=None; status1_mutant=plan; status1_mutant_plan=[0,0,0,0,0,0,0,0,0,0,1.47660443,0,0,0,0,0]; status2_baseline=None; status2_mutant=None; real_differing=0; success=False. Inputs tried: stubbed status 1 with x; stubbed status 2 without x; unmocked (null). Finding candidate: No check feeds the DHW LP an unsuccessful solve; dropping the success guard is unseen.

## Unfinished

- none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_0aa6eaace756da92.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_2074f3eefe8521aa.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_247372989ae65baa.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_4f1f941124291aeb.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_539e5aeaccf156f3.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_5b123e9e5b76ebc3.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_61862d35b6b2885d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_6e1174561ae9297c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_8db7b149f5f9eda5.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1074e70396100d8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1a8d3056bf42597.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b7a6f145165338bf.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_c1d6f40c74ee74ad.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_ddf4602569b157b1.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_eae8cfee2ddbd16d.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_fd9b39c806b43b56.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/_g17.py`
- gate_wave.sh procedure (dispatch ref tool, out of tree)
