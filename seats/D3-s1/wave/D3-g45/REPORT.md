# D3-s1 box D3-g45: full gate of 15 D3.M3 full-net survivors

## Machine and controls
```
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087         866       13956          12        1535       15220
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
0.82 0.36 0.13 1/140 804
```
Null control (fullgate.py null): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] with fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, wall 3461.6 s, load1 0.71..0.92 (provisional). The mutants' red sets are compared against it.

## Tally
gated 15/15; verdicts {'RED-AS-NULL': 13, 'KILLED': 2}; candidates 11; equivalent-candidates 2; KILLED 2 (by python3 tests/stress.py); TIMEOUT 0.

## Gated keys
| key | site | verdict | killed_by | class |
|---|---|---|---|---|
| b2faf84904db389e | custom_components/heatpump_optimizer/thermal_model.py:677 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| 1a9ac2bac45ef9e0 | custom_components/heatpump_optimizer/thermal_model.py:270 CMP_BOUND | RED-AS-NULL | [] | equivalent-candidate |
| e5f8fc2488caedf5 | custom_components/heatpump_optimizer/thermal_model.py:287 CMP_BOUND | RED-AS-NULL | [] | equivalent-candidate |
| 1b476993921016f9 | custom_components/heatpump_optimizer/thermal_model.py:852 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| ea888783bb621669 | custom_components/heatpump_optimizer/thermal_model.py:855 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| b098598faf0d87dc | custom_components/heatpump_optimizer/thermal_model.py:835 GUARD_OFF | RED-AS-NULL | [] | candidate |
| a2a1d3802ceff60d | custom_components/heatpump_optimizer/thermal_model.py:404 GUARD_OFF | KILLED | ['python3 tests/stress.py'] | killed |
| b9bbb3ac364893f7 | custom_components/heatpump_optimizer/thermal_model.py:698 GUARD_OFF | KILLED | ['python3 tests/stress.py'] | killed |
| dd40fdb4edae4d79 | custom_components/heatpump_optimizer/thermal_model.py:2270 GUARD_OFF | RED-AS-NULL | [] | candidate |
| 19404e3632806509 | custom_components/heatpump_optimizer/thermal_model.py:2554 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| beeb068352333132 | custom_components/heatpump_optimizer/thermal_model.py:2573 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| ea9c4705de428b28 | custom_components/heatpump_optimizer/thermal_model.py:2576 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| 98853a541b6b5d6a | custom_components/heatpump_optimizer/thermal_model.py:2581 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| fdf5872fd576c405 | custom_components/heatpump_optimizer/thermal_model.py:2581 CLAMP_DROP | RED-AS-NULL | [] | candidate |
| 39041ccf21eedba6 | custom_components/heatpump_optimizer/thermal_model.py:2583 GUARD_OFF | RED-AS-NULL | [] | candidate |

## Survivors that change behaviour (gate_survivors)

### b2faf84904db389e: No check pins the lower clamp of buffer_tank_heat_loss_coefficient: a near-zero buffer_cooling_rate yields a ~zero standby loss unseen
Dropping max(rate, low) at thermal_model.py:677 survives the full gate (no script fails beyond the null); with buffer_cooling_rate=1e-6 C/h on a 200 L buffer the UA falls from 4.11e-4 to 9.28e-9 kW/K (x2.3e-5).
Mechanism: The lower bound from buffer_cooling_rate_bounds keeps a learned or stored implausibly small rate from modelling a lossless tank; no suite check feeds a rate below the bound, so removal of the floor is invisible.
Step 4: should fail: tests/features.py (executes buffer_tank_heat_loss_coefficient per the ledger) lacks an assertion that a below-lower-bound buffer_cooling_rate is lifted to buffer_cooling_rate_bounds(volume)[0]; also optimality.py/validate.py named by the M4 answer.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_b2faf84904db389e.py`: baseline ua(rate=1e-6, 200 L)=0.00041098 kW/K; mutant 9.28e-09 kW/K (ratio 2.26e-05); inputs buffer_cooling_rate=1e-6 (moves), 0.0 (null: default branch, identical).
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3431.9 s (provisional).

### 1b476993921016f9: No check pins the greywater_recovery clip [0, 0.9] of dhw_draw_power
Dropping np.clip(greywater_recovery,0,0.9) at thermal_model.py:852 survives the full gate; with greywater_recovery=1.5 dhw_draw_power falls from 0.0326 kW to -0.163 kW, and with -0.5 it rises from 0.326 to 0.489 kW.
Mechanism: No gate script feeds an out-of-range recovery directly to the property, so the clip is unpinned and a service or store write of an out-of-range value would give a negative draw power unseen.
Step 4: should fail: tests/features.py or tests/optimality.py (the closures that execute dhw_draw_power) lack an assertion that an out-of-range greywater_recovery is clipped into [0, 0.9].
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_1b476993921016f9.py`: baseline 0.032625 kW (recovery 1.5, clipped to 0.9); mutant -0.163125 kW; recovery -0.5: 0.326250 -> 0.489375; inputs -0.5, 0.0, 0.5, 0.9, 1.5, nan (identical).
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3417.4 s (provisional).

### ea888783bb621669: No check pins the max(delta_t, 0) floor of dhw_draw_power
Dropping max(delta_t,0.0) at thermal_model.py:855 survives the full gate; with the DHW set-point 40 below the inlet reference 50 the draw power falls from 0.0 to -0.0725 kW.
Mechanism: A set-point below the cold-water inlet is not rejected before this property, and no check drives it; the floor is the only thing keeping a negative energy draw (a tank cooled by consumption) out of the DHW balance.
Step 4: should fail: tests/features.py or tests/optimality.py lack an assertion that dhw_draw_power is 0.0 when the set-point is not above the inlet reference.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_ea888783bb621669.py`: baseline 0.0 kW; mutant -0.0725 kW (sp=10/ref=10: 0.0 both; sp=55/ref=10: 0.32625 both); inputs sp40/ref50 (moves), sp10/ref10, sp55/ref10 (null).
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3296.5 s (provisional).

### b098598faf0d87dc: No check pins the amplitude <= 0 early return of seasonal_inlet_temp for negative amplitudes
Removing the `swing <= 0.0` guard at thermal_model.py:835 survives the full gate; with dhw_inlet_seasonal_amplitude=-3 the day-60 inlet moves from 10.0 to 13.0 degC and day 240 from 10.0 to 7.0028. Amplitude 0 and positive values are identical (the guard is only distinguishable for negative amplitudes).
Mechanism: The guard documents that amplitude <= 0 yields the constant mean; no check drives a negative amplitude, so an inverted seasonal swing would pass unseen. Reachability of a negative amplitude through config/service validation is not established here (lead for the verifier).
Step 4: should fail: tests/features.py or tests/optimality.py (closures executing seasonal_inlet_temp) lack an assertion that a negative amplitude returns the annual mean.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_b098598faf0d87dc.py`: baseline 10.0; mutant 13.0 (day 240: 10.0 -> 7.0028); inputs 0.0 (identical), -3.0 (moves), 4.0 (identical), nan (identical), days 60 and 240.
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3259.5 s (provisional).

### dd40fdb4edae4d79: No check pins the per-step valve_target override of _valve_flow_set
Replacing `if valve_target is not None:` at thermal_model.py:2270 with False survives the full gate; a per-step valve_target of 45 gives flow set-point 51.75 baseline vs 40.25 mutant (configured target 35), 25 gives 28.75 vs 40.25.
Mechanism: The per-step target is how a commanded valve holds its charge; no gate script asserts that the plan's lowered/raised valve target changes the simulated flow temperature, so the plan's valve target could be ignored without any check failing.
Step 4: should fail: tests/optimality.py / features.py (valved-tank closures) lack an assertion that a per-step valve_target changes the delivered flow set-point.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_dd40fdb4edae4d79.py`: baseline 51.75; mutant 40.25; inputs 45.0 (moves), 25.0 (moves), None (null, identical).
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3317.4 s (provisional).

### 19404e3632806509: No check pins min(T_upper, T_slab) as the floor of the valved-tank energy bound
Using T_upper alone as the floor temperature at thermal_model.py:2554 survives the full gate; on 3936 of 17496 ordinary-dt grid inputs _valve_two_zone_delivery changes (e.g. q_rad 0.5167 -> 0.3617 kW).
Mechanism: The energy bound must use the coldest store the tank feeds; with the slab colder than the upper floor the mutant understates the available heat. No check places the slab below the upper floor with a throttled valve.
Step 4: should fail: tests/optimality.py / features.py throttled-valve closures lack an assertion with T_slab < T_upper that the bound uses the coldest store.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_19404e3632806509.py`: baseline q_rad=0.5167 kW at (T_up 18, T_slab 15, T_buf 25); mutant q_rad=0.3617 kW; inputs 3x3x3x3x3x3x3x2x4x2 grid; null baseline-vs-baseline 0.
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3225.9 s (provisional).

### beeb068352333132: No check pins the dt floor (1e-6) of the wood-tank energy bound
Dropping max(dt_hours,1e-6) at thermal_model.py:2573 survives the full gate; with dt_hours=0 the step raises ZeroDivisionError and with 1e-7 the bound changes (4374 of 34992 grid inputs, all with dt < 1e-6; none moves at dt >= 0.25).
Mechanism: The floor guards a zero or sub-microsecond step; no check drives a degenerate dt through the two-tank throttled path. Whether production can reach dt < 1e-6 is a lead for the verifier.
Step 4: should fail: tests/features.py (two-tank closure) lacks an assertion that a zero dt_hours is finite.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_beeb068352333132.py`: baseline finite tuple at dt=0; mutant ZeroDivisionError at dt=0; inputs dt 0.0, 1e-7, 0.25, 1.0 (only the first two move).
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3138.7 s (provisional).

### ea9c4705de428b28: No check pins the dt floor (1e-6) of the heat-pump-tank energy bound
Dropping max(dt_hours,1e-6) at thermal_model.py:2576 survives the full gate; dt_hours=0 raises ZeroDivisionError, 1e-7 changes the bound (4374 of 34992 grid inputs; none at dt >= 0.25).
Mechanism: Same floor as the wood-tank twin one line above; no check drives a degenerate dt through the two-tank throttled path.
Step 4: should fail: tests/features.py (two-tank closure) lacks an assertion that a zero dt_hours is finite.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_ea9c4705de428b28.py`: baseline finite tuple at dt=0; mutant ZeroDivisionError at dt=0; inputs dt 0.0, 1e-7, 0.25, 1.0 (only the first two move).
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3067.5 s (provisional).

### 98853a541b6b5d6a: No check pins the max(avail_hp, 0) floor of the two-tank heat-pump-tank draw
Removing the zero floor of avail_hp at thermal_model.py:2581 survives the full gate; 1275 of 17496 ordinary-dt grid inputs change the delivery (max abs diff 2.72 kW).
Mechanism: With a negative availability (heat-pump input below standing loss and the tank at the floor), the floor keeps the draw non-negative; unpinned, a negative hp_draw makes the tank gain heat from the emitters.
Step 4: should fail: tests/optimality.py / features.py two-tank closures lack an assertion with thermal_power < standing loss that the heat-pump draw is not negative.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_98853a541b6b5d6a.py`: baseline non-negative draws; mutant max abs diff 2.7158 kW; inputs grid of 34992 (two-tank True/False), null 0.
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3251.2 s (provisional).

### fdf5872fd576c405: No check pins the availability cap on the two-tank heat-pump-tank draw
Replacing the min(drawn - wood_draw, max(avail_hp,0)) cap at thermal_model.py:2581 by drawn - wood_draw survives the full gate; 1280 of 17496 ordinary-dt grid inputs change the delivery (max abs diff 17.5 kW).
Mechanism: The energy bound that keeps the tank from delivering heat it does not hold is the only thing capping hp_draw; no check starves the heat-pump tank while the wood tank is also short.
Step 4: should fail: tests/optimality.py / features.py two-tank closures lack an assertion that a starved heat-pump tank cannot deliver more than it holds.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_fdf5872fd576c405.py`: baseline draw capped by availability; mutant max abs diff 17.5 kW; inputs grid of 34992, null 0.
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3148.1 s (provisional).

### 39041ccf21eedba6: No check pins the proportional starvation scale of the two-tank draw
Removing the `drawn > delivered > 0.0` scaling branch at thermal_model.py:2583 survives the full gate; 1223 of 17496 ordinary-dt grid inputs change the emitter deliveries (max abs diff 16.9 kW).
Mechanism: The branch scales emitter deliveries down when the tanks can back only part of the draw; unpinned, the emitters are credited heat that no tank gave.
Step 4: should fail: tests/optimality.py / features.py two-tank closures lack an assertion that a partly starved step scales the emitter draw to delivered/drawn.
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_39041ccf21eedba6.py`: baseline emitter draw scaled to what the tanks deliver; mutant max abs diff 16.92 kW; inputs grid of 34992, null 0.
Gate: RED-AS-NULL, gate_rc 1, red set identical to the null, wall 3032.5 s (provisional).

## Equivalent-candidates

- 1a9ac2bac45ef9e0 custom_components/heatpump_optimizer/thermal_model.py:270 CMP_BOUND `if not np.isfinite(value) or value < THERMAL_MASS_FLOOR: -> if not np.isfinite(value) or value <= THERMAL_MASS_FLOOR:`: max_abs_diff=0.0, inputs_moved=0 of 48; probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_1a9ac2bac45ef9e0.py`; inputs floor exactly, nextafter(floor,0), nextafter(floor,1), floor/2, 0.0, -1.0, nan, inf, 'x', None, floor*(1+1e-10), 1.0.
- e5f8fc2488caedf5 custom_components/heatpump_optimizer/thermal_model.py:287 CMP_BOUND `if not np.isfinite(value) or value < POSITIVE_PARAM_FLOOR: -> if not np.isfinite(value) or value <= POSITIVE_PARAM_FLOOR:`: max_abs_diff=0.0, inputs_moved=0 of 24; probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_e5f8fc2488caedf5.py`; inputs floor 0.01 exactly, nextafter(floor,0), nextafter(floor,1), floor/2, 0.0, -1.0, nan, inf, 'x', None, floor*(1+1e-10), 1.0.

## KILLED (non-findings)

- a2a1d3802ceff60d custom_components/heatpump_optimizer/thermal_model.py:404 GUARD_OFF (ThermalParameters.topology_layout): killed_by ['python3 tests/stress.py']; fail lines ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/stress.py'].
- b9bbb3ac364893f7 custom_components/heatpump_optimizer/thermal_model.py:698 GUARD_OFF (ThermalParameters.wood_tank_heat_loss_coefficient): killed_by ['python3 tests/stress.py']; fail lines ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py', 'python3 tests/stress.py'].

## Unfinished

none

## Leads / instrument notes

- Both KILLED keys (the topology_layout and wood_tank memo guards) are killed only by tests/stress.py, one failing check beyond the null; stress.py reads wall time (a performance budget), so the kill is a timing kill that the judge should re-take on a quiet machine before counting it as a pin.
- box_comms.sh left its mkdir lock stale three times (after the container restart at 22:18 and at a gate-start heartbeat 23:11); `comms: lock stuck`, cleared by rmdir of the lock dir. Instrument fault, not pushed.
- Probes read a pristine git-archive export of the baseline (~/probe-tree), never the gate's tree, because the tree carries a committed mutant while a gate runs.
