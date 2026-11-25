# D3-s1 box D3-g04: full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1, wave box D3-g04. Counts are final; wall, CPU and load numbers are provisional (the judge re-takes them).

## Machine and controls

```
date: 2026-11-22T21:38:04Z
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
free -m:
               total        used        free      shared  buff/cache   available
Mem:           16087        1061       13522          12        1801       15026
Swap:              0           0           0
df -h $HOME:
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1: 0.79
python3: /opt/hpo/venv-ci/bin/python3

re-fire (resume seat): 2026-11-25T00:46:04Z
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
               total        used        free      shared  buff/cache   available
Mem:           16087         765       14035          12        1559       15322
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.67
```

box D3-g04 full-gate null control (fullgate.py null via gate_wave.sh null), 2026-11-22 21:38-22:42Z, nproc 4 Intel Xeon Processor @ 2.10GHz, 16 GB, load1 0.69..0.92, wall 3845.1 s, child CPU 6361.4 s (provisional).
gate_rc=1, 3 scripts red, all artefact checks; none reads a production cell file:
- tests/closure.py selftest (2 lines): "a refused merge surfaces merge()'s reason, not just skip-merge-failed" and "and a merge that succeeds carries no merge reason (null control)" [status='skip-not-under-scoped']: branch/merge-tool pins in a detached worktree.
- tests/entities.py (1 line): "and is accepted when it does [the scoped path records only what the diff can reach]": scoped-gate pin, branch-environment artefact (identical to box D3-rem's null).
- tests/harness_headers.py (3 lines): round4/D6/claims.py RESULT claims_true/claims_false vs its header (122/1 printed vs 123/0) and "the executed harnesses leave their committed output byte-identical" (claims.json/claims.md rewritten): an earlier round's register harness re-run on the finder-stripped tree.
The a3:/a4: FAIL lines in entities.py's section are its positive controls (printed under ok-checks), not red checks; fail_lines counts entities.py at 1.
Not re-taken: red on artefact checks only and no machine-caused script (no card.mjs heap failure). fullgate.py counts KILLED only on a script beyond these or more FAIL lines in one of them.

Procedure: `gate_wave.sh run` (the dispatch tip's driver) runs `python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key <key>` per key, one gate at a time: the one-line mutant is applied and committed, the gate_lock lease taken, `GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh` run, the verdict recorded against this box's null, and the tree reset to the baseline. Probes run from a separate clean baseline worktree, never the gate's tree.

## Tally

- gated: 16 of 16
- RED-AS-NULL: 16
- KILLED by script: none
- candidates (full-gate survivors whose probe moves): 9
- equivalent-candidates: 7
- TIMEOUT / unfinished: 0

| key | site | verdict | class | probe baseline -> mutant |
|---|---|---|---|---|
| 466c95cb8978ea1d | custom_components/heatpump_optimizer/coordinator.py:7733 GUARD_OFF | RED-AS-NULL | candidate | warnings_baseline=0 count -> warnings_mutant=1 count |
| a7dd3153718e531b | custom_components/heatpump_optimizer/coordinator.py:9153 GUARD_OFF | RED-AS-NULL | candidate | outcome_baseline=None -> outcome_mutant=array[4] max=2e-09 |
| b6b6e82fb4a33703 | custom_components/heatpump_optimizer/coordinator.py:9153 CMP_BOUND | RED-AS-NULL | equivalent-candidate | exact_tie_reachable=0 count -> differing_inputs=0 count |
| 10ba5036744c9a99 | custom_components/heatpump_optimizer/coordinator.py:9155 CLAMP_DROP | RED-AS-NULL | equivalent-candidate | max_abs_delta_production=0.0 C -> max_abs_delta_subminute=0.15 C |
| 7457d714cd44306c | custom_components/heatpump_optimizer/coordinator.py:9166 CMP_BOUND | RED-AS-NULL | candidate | outcome_baseline=None -> outcome_mutant=array[4] max=1e-09 |
| 6aeb83e5435c9cac | custom_components/heatpump_optimizer/coordinator.py:10428 GUARD_OFF | RED-AS-NULL | candidate | grid_fee_sek_baseline=3.0 -> grid_fee_sek_mutant=absent |
| d06a2d8e53342785 | custom_components/heatpump_optimizer/coordinator.py:10433 GUARD_OFF | RED-AS-NULL | candidate | monthly_avg_spot_sek_baseline=15.0 -> monthly_avg_spot_sek_mutant=absent |
| 9789e0e7faa1b53a | custom_components/heatpump_optimizer/coordinator.py:10445 CMP_BOUND | RED-AS-NULL | equivalent-candidate | differing_inputs=0 count -> null_delta=0 count |
| 8b4f4adbf55981bc | custom_components/heatpump_optimizer/coordinator.py:9931 GUARD_OFF | RED-AS-NULL | equivalent-candidate | differing_reachable=0 count -> differing_unreachable=1 count |
| c555c1a38da31dde | custom_components/heatpump_optimizer/coordinator.py:4391 CMP_BOUND | RED-AS-NULL | equivalent-candidate | litres_baseline=3200.0 at inlet 39.0 -> litres_mutant=absent |
| ff67ca31aba14e7f | custom_components/heatpump_optimizer/coordinator.py:4391 GUARD_OFF | RED-AS-NULL | equivalent-candidate | litres_baseline=absent at inlet 39.5 -> litres_mutant=6200.0 at inlet 39.5; at 40.0: raises ZeroDivisionError |
| 201955bf671ce8aa | custom_components/heatpump_optimizer/coordinator.py:4396 CMP_BOUND | RED-AS-NULL | equivalent-candidate | outcome_baseline=no shower_minutes -> outcome_mutant=raises ZeroDivisionError |
| faf822994582adfc | custom_components/heatpump_optimizer/coordinator.py:4463 CLAMP_DROP | RED-AS-NULL | candidate | recommended_baseline=48 -> recommended_mutant=56 |
| feed2751f4116bd1 | custom_components/heatpump_optimizer/coordinator.py:4464 CMP_BOUND | RED-AS-NULL | candidate | recommended_baseline=48 -> recommended_mutant=50 |
| 29bad645ca2c2438 | custom_components/heatpump_optimizer/coordinator.py:4471 CMP_BOUND | RED-AS-NULL | candidate | recommended_baseline=48 -> recommended_mutant=50 |
| 640a1a68b6c1eb23 | custom_components/heatpump_optimizer/coordinator.py:9846 GUARD_OFF | RED-AS-NULL | candidate | ha_contract_baseline=(None, {}) for None -> ha_contract_mutant=raises AttributeError for None |

## Survivors: step-4 answers

### 466c95cb8978ea1d — custom_components/heatpump_optimizer/coordinator.py:7733 GUARD_OFF (candidate)

`if not entity_id: -> if False:` in `HeatPumpOptimizerCoordinator._command_valve_target`. Gate: RED-AS-NULL (gate_rc 1, wall 3511.2 s, load1 1.03..0.84). With mixing_valve_mode=smart_write and no mixing_valve_write_entity (an accepted, optional option), _command_valve_target's `if not entity_id:` guard returns with a DEBUG line. With the guard removed the write is attempted on None/'' inside _valve_write_problem, fails, and log_held latches a WARNING 'Valve write entity None could not be commanded' each time the condition starts. The full GATE_SCOPE=full GOLDEN_MODE=drift gate does not notice. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_466c95cb8978ea1d.py`: baseline `warnings_baseline=0 count`, mutant `warnings_mutant=1 count`; inputs tried: mixing_valve_write_entity unset (None); mixing_valve_write_entity ''; null: number.valve present. Should have failed: tests/features.py: the _command_valve_target block (~13340-13410) drives smart_write with a write entity, a climate entity, a flow kind and a None current action, but no case with smart_write and NO write entity; it lacks an assertion that this case returns before _valve_write_problem (no WARNING latched, no write attempted). tests/config_flow_steps.py also executes the line and asserts nothing about it.

### a7dd3153718e531b — custom_components/heatpump_optimizer/coordinator.py:9153 GUARD_OFF (candidate)

`if damp <= 1e-9: -> if False:` in `HeatPumpOptimizerCoordinator._confidence_margins`. Gate: RED-AS-NULL (gate_rc 1, wall 3075.7 s, load1 0.7..0.92). _confidence_margins returns None (the byte-inert no-margin answer) when 1 - trust() <= 1e-9. With that guard removed, a temperature MAE a hair above 0.25 C (damp ~1e-9) and a lead sigma above 1 C yield an array of ~2e-9 C margins instead of None. The full gate does not notice; the consequence is a non-None min_temp_margins handed to the solver with nanokelvin values. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_a7dd3153718e531b.py`: baseline `outcome_baseline=None`, mutant `outcome_mutant=array[4] max=2e-09`; inputs tried: mae 0.25+1.75e-9 (damp 9.9999997e-10) x sigma 2, 5, 0.5, 1.0 C; null: mae 0.25, 0.1 (damp 0), mae 1.125 (damp 0.5). Should have failed: tests/features.py: the _confidence_margins block (~23988-24030) checks the fresh-install None, the cap and the trust damping, but never a damp inside (0, 1e-9] with sigma > 1 C; it lacks an assertion that a near-perfect trust returns None. tests/config_flow_steps.py executes the line without asserting on it.

### b6b6e82fb4a33703 — custom_components/heatpump_optimizer/coordinator.py:9153 CMP_BOUND (equivalent-candidate)

`if damp <= 1e-9: -> if damp < 1e-9:` in `HeatPumpOptimizerCoordinator._confidence_margins`. Gate: RED-AS-NULL (gate_rc 1, wall 3096.1 s, load1 0.79..0.92). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_b6b6e82fb4a33703.py`: baseline `exact_tie_reachable=0 count`, mutant `differing_inputs=0 count`; inputs tried: 2001 trust values within 1000 ulps of 1-1e-9, sigma 2 and 5 C; 401 MAE values within 200 ulps of 0.25+1.75e-9; exact damp==1e-9: not representable as 1 - t (nearest 9.9999997e-10 / 1.00000008e-9). Should have failed: none reachable: the arms differ only at damp == 1e-9 exactly, which 1.0 - trust() cannot produce (granularity 2**-53 near 1).

### 10ba5036744c9a99 — custom_components/heatpump_optimizer/coordinator.py:9155 CLAMP_DROP (equivalent-candidate)

`dt_h = max(ctx._opt_config.time_step_minutes, 1.0) / 60.0 -> dt_h = (ctx._opt_config.time_step_minutes) / 60.0` in `HeatPumpOptimizerCoordinator._confidence_margins`. Gate: RED-AS-NULL (gate_rc 1, wall 3124.4 s, load1 0.99..0.92). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_10ba5036744c9a99.py`: baseline `max_abs_delta_production=0.0 C`, mutant `max_abs_delta_subminute=0.15 C`; inputs tried: time_step_minutes 15.0 (the only production value); 5, 15, 60 (null); 0.0, 0.25, 0.5, 0.999 fed directly (separates by 0.15 C at <1 min). Should have failed: none reachable: OptimizationConfig.time_step_minutes is never assigned outside its 15.0 default (optimizer.py:2667), so max(step, 1.0) is the identity on every production input.

### 7457d714cd44306c — custom_components/heatpump_optimizer/coordinator.py:9166 CMP_BOUND (candidate)

`return margins if bool(np.any(margins > 1e-9)) else None -> return margins if bool(np.any(margins >= 1e-9)) else None` in `HeatPumpOptimizerCoordinator._confidence_margins`. Gate: RED-AS-NULL (gate_rc 1, wall 3225.4 s, load1 0.79..0.92). _confidence_margins returns None unless some margin exceeds 1e-9. With `>` -> `>=`, a lead sigma of 2e-9 C at damp 0.5 (sigma*damp == 1e-9 exactly) returns an array of 1e-9 C instead of None. The full gate does not notice; the consequence is a non-None, nanokelvin min_temp_margins. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_7457d714cd44306c.py`: baseline `outcome_baseline=None`, mutant `outcome_mutant=array[4] max=1e-09`; inputs tried: sigma 2e-9 at damp 0.5 (mae 1.125); sigma 4e-9 at damp 0.25 (mae 0.6875); null: sigma 1e-8 and 1e-10. Should have failed: tests/features.py: the _confidence_margins block (~23988-24030) never constructs a margin of exactly 1e-9; it lacks the tie case asserting None.

### 6aeb83e5435c9cac — custom_components/heatpump_optimizer/coordinator.py:10428 GUARD_OFF (candidate)

`if fee_line["sek"]: -> if False:` in `HeatPumpOptimizerCoordinator._contract_comparison`. Gate: RED-AS-NULL (gate_rc 1, wall 3230.0 s, load1 0.85..0.93). _contract_comparison publishes the month's grid-fee cost as grid_fee_sek when the ledger holds a grid_fee line. With the `if fee_line["sek"]:` branch disabled the key is never published (3.0 SEK -> absent), and the full gate does not notice: no check books a grid_fee line and reads the comparison. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_6aeb83e5435c9cac.py`: baseline `grid_fee_sek_baseline=3.0`, mutant `grid_fee_sek_mutant=absent`; inputs tried: 10 kWh, 12 SEK spot, 3 SEK grid fee, mean 1.5; null: no grid-fee line. Should have failed: tests/features.py: the _contract_comparison block (~56964-57000, `_t6_contract`) books only a spot line, never a grid_fee line; it lacks an assertion that grid_fee_sek equals the month's grid-fee line. tests/entities.py publishes the contract_comparison sensor without a grid-fee ledger line either.

### d06a2d8e53342785 — custom_components/heatpump_optimizer/coordinator.py:10433 GUARD_OFF (candidate)

`if kwh > 0 and mean_spot is not None: -> if False:` in `HeatPumpOptimizerCoordinator._contract_comparison`. Gate: RED-AS-NULL (gate_rc 1, wall 3045.0 s, load1 0.33..0.92). _contract_comparison settles the month under monthly-average spot (månadsspot) when kWh > 0 and a spot mean exists, publishing monthly_avg_spot_sek and load_profile_value_per_kwh and entering it in `cheapest`. With that branch disabled the three keys disappear and, where monthly average is the cheapest contract, `cheapest` names hourly_spot instead. The full gate does not notice. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_d06a2d8e53342785.py`: baseline `monthly_avg_spot_sek_baseline=15.0`, mutant `monthly_avg_spot_sek_mutant=absent`; inputs tried: 10 kWh, 12 SEK spot, mean 1.5; 10 kWh, 12 SEK, mean 1.0, fixed 1.4 (monthly average cheapest); null: no spot mean. Should have failed: tests/features.py: `_t6_contract` (~56964-57000) never records a spot-price mean (observe_meta_mean), so the monthly-average arm is never present; it lacks an assertion on monthly_avg_spot_sek == kwh * mean and on cheapest == 'monthly_avg_spot' when that arm wins.

### 9789e0e7faa1b53a — custom_components/heatpump_optimizer/coordinator.py:10445 CMP_BOUND (equivalent-candidate)

`if kwh > 0 and len(costs) > 1: -> if kwh >= 0 and len(costs) > 1:` in `HeatPumpOptimizerCoordinator._contract_comparison`. Gate: RED-AS-NULL (gate_rc 1, wall 2881.0 s, load1 1.01..0.85). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_9789e0e7faa1b53a.py`: baseline `differing_inputs=0 count`, mutant `null_delta=0 count`; inputs tried: kwh 0 with spot 0/5/-3 SEK, mean 1.0/0.5/None, fixed 1.0/2.0/0.7, fee 0/3; kwh -1; kwh nan; kwh 1e-12. Should have failed: none: at kwh == 0 both other contracts are gated on kwh > 0, so costs holds hourly_spot alone and len(costs) > 1 is false on both arms.

### 8b4f4adbf55981bc — custom_components/heatpump_optimizer/coordinator.py:9931 GUARD_OFF (equivalent-candidate)

`if not self._weather_forecast: -> if False:` in `HeatPumpOptimizerCoordinator._current_humidity`. Gate: RED-AS-NULL (gate_rc 1, wall 2908.0 s, load1 0.72..0.94). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_8b4f4adbf55981bc.py`: baseline `differing_reachable=0 count`, mutant `differing_unreachable=1 count`; inputs tried: []; [{}]; [{'humidity': None}]; [{'humidity': 80}]; timestamped two-entry list; None (unreachable: raises TypeError under the mutant). Should have failed: none reachable: _weather_forecast is a list from __init__ (coordinator.py:3725) and only ever assigned a non-empty list (7076) or a fabricated one (7111); on [] the loop runs zero times and returns None on both arms.

### c555c1a38da31dde — custom_components/heatpump_optimizer/coordinator.py:4391 CMP_BOUND (equivalent-candidate)

`if 40.0 - inlet < 1.0: -> if 40.0 - inlet <= 1.0:` in `HeatPumpOptimizerCoordinator._dhw_mixed_water`. Gate: RED-AS-NULL (gate_rc 1, wall 2739.4 s, load1 0.8..0.95). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_c555c1a38da31dde.py`: baseline `litres_baseline=3200.0 at inlet 39.0`, mutant `litres_mutant=absent`; inputs tried: inlet 39.0 (separates: 3200 L -> {}); inlets -5.0..35.0 step 0.5 (81 values); live inlet 30, 35 accepted; 35.5, 39 refused by _dhw_inlet_c; null: inlet 10. Should have failed: none reachable: the inlet production resolves is at most 35 C (options 25 + 8 seasonal; a live probe above 35 C is refused by _dhw_inlet_c), so 40 - inlet >= 5 and the boundary at 1.0 is never met.

### ff67ca31aba14e7f — custom_components/heatpump_optimizer/coordinator.py:4391 GUARD_OFF (equivalent-candidate)

`if 40.0 - inlet < 1.0: -> if False:` in `HeatPumpOptimizerCoordinator._dhw_mixed_water`. Gate: RED-AS-NULL (gate_rc 1, wall 2674.0 s, load1 0.89..0.92). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_ff67ca31aba14e7f.py`: baseline `litres_baseline=absent at inlet 39.5`, mutant `litres_mutant=6200.0 at inlet 39.5; at 40.0: raises ZeroDivisionError`; inputs tried: inlet 39.5 (separates: {} -> 6200 L); inlet 40.0 (mutant ZeroDivisionError); inlets -5.0..35.0 step 0.5 (81 values); null: inlet 10. Should have failed: none reachable: as for c555c1a38da31dde, the resolved inlet never exceeds 35 C, so the guard is never taken in production.

### 201955bf671ce8aa — custom_components/heatpump_optimizer/coordinator.py:4396 CMP_BOUND (equivalent-candidate)

`if flow > 0: -> if flow >= 0:` in `HeatPumpOptimizerCoordinator._dhw_mixed_water`. Gate: RED-AS-NULL (gate_rc 1, wall 2854.7 s, load1 0.35..0.93). Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_201955bf671ce8aa.py`: baseline `outcome_baseline=no shower_minutes`, mutant `outcome_mutant=raises ZeroDivisionError`; inputs tried: flow 0 (separates: mutant ZeroDivisionError); flow 4..20 step 0.5 (33 values); 0, -1, 3.9 through the option's NumberSelector: refused; null: flow 8. Should have failed: none through the options flow: shower_flow_lpm's selector bounds it to 4..20 (config_flow.py:1811). EntryConfig itself (entry_config.py:193) parses it with finite_float alone, so a stored 0 from outside the flow would raise; recorded as a lead, not a finding.

### faf822994582adfc — custom_components/heatpump_optimizer/coordinator.py:4463 CLAMP_DROP (candidate)

`usable_kwh = c_dhw * max(t - params.dhw_min_temp, 0.0) -> usable_kwh = c_dhw * (t - params.dhw_min_temp)` in `HeatPumpOptimizerCoordinator._dhw_setpoint_sweep`. Gate: RED-AS-NULL (gate_rc 1, wall 2881.3 s, load1 0.72..0.92). _dhw_setpoint_sweep clamps a candidate's usable band at zero (max(t - dhw_min_temp, 0)). With the clamp dropped, a candidate below dhw_min_temperature gets negative usable energy; when every demand window has learned a zero-kWh heaviest draw (twenty empty occurrences), those candidates stop meeting it and the recommendation moves 48 -> 56 at a 55 C minimum. The full gate does not notice. (The baseline itself recommends 48 C below a 55 C minimum in that state: a lead.) Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_faf822994582adfc.py`: baseline `recommended_baseline=48`, mutant `recommended_mutant=56`; inputs tried: dhw_min_temperature None/48/50/55 x learned zero-kWh windows on/off (8 cells; 2 differ); null: profile-fallback heaviest 4.97 kWh. Should have failed: tests/features.py: the _dhw_setpoint_sweep block (~20133-20230) drives the default minimum (45 C, below every candidate) and a learned 8 kWh draw, never a minimum above the 48 C candidate with a zero-kWh heaviest window; it lacks an assertion on meets_heaviest_window for a candidate below dhw_min_temp.

### feed2751f4116bd1 — custom_components/heatpump_optimizer/coordinator.py:4464 CMP_BOUND (candidate)

`meets = usable_kwh >= heaviest -> meets = usable_kwh > heaviest` in `HeatPumpOptimizerCoordinator._dhw_setpoint_sweep`. Gate: RED-AS-NULL (gate_rc 1, wall 2929.9 s, load1 0.72..0.92). _dhw_setpoint_sweep marks a candidate as meeting the heaviest window when usable_kwh >= heaviest. With `>`, a candidate whose usable energy equals the heaviest window (a zero-kWh learned heaviest at a minimum equal to a candidate) stops meeting it, and the recommendation moves 48 -> 50 at a 48 C minimum. The full gate does not notice. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_feed2751f4116bd1.py`: baseline `recommended_baseline=48`, mutant `recommended_mutant=50`; inputs tried: dhw_min_temperature None/48/50/55 x learned zero-kWh windows on/off (8 cells; 3 differ); null: profile-fallback heaviest. Should have failed: tests/features.py: the _dhw_setpoint_sweep block (~20133-20230) never makes a candidate's usable energy equal the heaviest window; it lacks the tie case asserting meets_heaviest_window is True.

### 29bad645ca2c2438 — custom_components/heatpump_optimizer/coordinator.py:4471 CMP_BOUND (candidate)

`if meets and (best is None or cost_day < best["cost_per_day"]): -> if meets and (best is None or cost_day <= best["cost_per_day"]):` in `HeatPumpOptimizerCoordinator._dhw_setpoint_sweep`. Gate: RED-AS-NULL (gate_rc 1, wall 3042.0 s, load1 0.72..0.93). _dhw_setpoint_sweep keeps the first (cooler) candidate on a cost tie. The comparison reads the unrounded cost against the best's rounded cost_per_day, so a tie is reachable on a continuous input: at a recent kWh price of 0.012022669199125837 SEK candidate 50's cost equals candidate 48's stored 0.05. With `<=` the recommendation moves 48 -> 50. The full gate does not notice. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_29bad645ca2c2438.py`: baseline `recommended_baseline=48`, mutant `recommended_mutant=50`; inputs tried: kwh price scanned ulp by ulp from 0.05/K50 (tie found at 0.012022669199125837); null: kwh price 1.0. Should have failed: tests/features.py: the _dhw_setpoint_sweep block (~20133-20260) compares recommendations at ordinary prices only; it lacks a tie case (a candidate whose unrounded cost equals the stored rounded best) asserting the lower setpoint is kept.

### 640a1a68b6c1eb23 — custom_components/heatpump_optimizer/coordinator.py:9846 GUARD_OFF (candidate)

`if not entity_id: -> if False:` in `HeatPumpOptimizerCoordinator._entity_state`. Gate: RED-AS-NULL (gate_rc 1, wall 2982.1 s, load1 0.86..0.85). _entity_state returns (None, {}) for an unset entity id before calling hass.states.get. features.py pins that outcome, and its title claims 'before any lookup', but it runs on FakeStates.get, a dict lookup that answers None for None. Removing the guard therefore passes the full gate. Under a registry following Home Assistant's StateMachine.get (which lower()s the id), the mutant raises AttributeError for None, the EntryConfig default of away_presence_entity that _resolve_away reads every cycle. Home Assistant is not installed in venv-ci; the contract is written out in the probe. Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_640a1a68b6c1eb23.py`: baseline `ha_contract_baseline=(None, {}) for None`, mutant `ha_contract_mutant=raises AttributeError for None`; inputs tried: None and '' under the suite's FakeStates (no difference); None and '' under a registry following HA's StateMachine.get (None: mutant raises AttributeError); null: binary_sensor.home present. Should have failed: tests/features.py: the check 'no entity and an empty entity id both read as absent, before any lookup' (~53757) runs on FakeStates, whose get(None) answers None, so it cannot see that the lookup happened; it lacks a states registry that records or refuses the lookup (or honours Home Assistant's entity_id.lower()).

## Seat notes

# D3-g04 preliminary per-key notes (probe class if the gate SURVIVES; KILLED/TIMEOUT override)

- 466c95cb8978ea1d: candidate -- No check drives smart_write with no valve write entity; dropping the guard turns a DEBUG skip into a WARNING
- a7dd3153718e531b: candidate -- No check feeds _confidence_margins a damping in (0, 1e-9]; removing its early None is unseen
- b6b6e82fb4a33703: equivalent-candidate -- none reachable: the arms differ only at damp == 1e-9 exactly, which 1.0 - trust() cannot produce (granularity 2**-53 near 1).
- 10ba5036744c9a99: equivalent-candidate -- none reachable: OptimizationConfig.time_step_minutes is never assigned outside its 15.0 default (optimizer.py:2667), so max(step, 1.0) is the identity on every production input.
- 7457d714cd44306c: candidate -- No check makes a confidence margin exactly 1e-9; the `>` -> `>=` swap in its None test is unseen
- 6aeb83e5435c9cac: candidate -- No check books a grid-fee line before reading the contract comparison; dropping grid_fee_sek is unseen
- d06a2d8e53342785: candidate -- No check records a spot mean before the contract comparison; the monthly-average contract can vanish unseen
- 9789e0e7faa1b53a: equivalent-candidate -- none: at kwh == 0 both other contracts are gated on kwh > 0, so costs holds hourly_spot alone and len(costs) > 1 is false on both arms.
- 8b4f4adbf55981bc: equivalent-candidate -- none reachable: _weather_forecast is a list from __init__ (coordinator.py:3725) and only ever assigned a non-empty list (7076) or a fabricated one (7111); on [] the loop runs zero times and returns No
- c555c1a38da31dde: equivalent-candidate -- none reachable: the inlet production resolves is at most 35 C (options 25 + 8 seasonal; a live probe above 35 C is refused by _dhw_inlet_c), so 40 - inlet >= 5 and the boundary at 1.0 is never met.
- ff67ca31aba14e7f: equivalent-candidate -- none reachable: as for c555c1a38da31dde, the resolved inlet never exceeds 35 C, so the guard is never taken in production.
- 201955bf671ce8aa: equivalent-candidate -- none through the options flow: shower_flow_lpm's selector bounds it to 4..20 (config_flow.py:1811). EntryConfig itself (entry_config.py:193) parses it with finite_float alone, so a stored 0 from outsi
- faf822994582adfc: candidate -- No check sets the DHW minimum above the lowest sweep candidate; dropping the usable-energy clamp moves the advice unseen
- feed2751f4116bd1: candidate -- No check ties a sweep candidate's usable energy to the heaviest window; `>=` -> `>` moves the advice unseen
- 29bad645ca2c2438: candidate -- No check pins the sweep's tie-break; `<` -> `<=` hands a cost tie to the hotter setpoint unseen
- 640a1a68b6c1eb23: candidate -- The _entity_state 'before any lookup' check cannot see a lookup; removing the guard is unseen and raises under HA's states contract

## resume seat (fire 2)
- 2026-11-25 00:46Z resumed from wip 31bc0f0c (6/16 gated, d06a2d8e53342785 had been running when the predecessor stalled; no record, re-run).
- 01:32Z container restart killed gate d06a2d8e53342785 at 46 min (no record). Stale gate_lock lease D3-s1-r11 and slot run.sh-1224 released (owner pids gone); partial state/gates log removed; re-started 01:33Z. The gate counts only the completed run.
- probe toolchain (_tools) restored to $HOME/pgen; probes run from a clean baseline worktree $HOME/probe-tree, never the gate tree.
- 05:5xZ second container restart killed gate 201955bf671ce8aa (started 05:31Z, ~20 min in; no record). Lease and slot run.sh-29876 released, partial state removed, re-run.
- 2026-11-25T10:04:34Z all 16 gates recorded (GATES-DONE gated 16/16 RED-AS-NULL=16); REPORT built by probes/_tools/build_wave_report.py.

