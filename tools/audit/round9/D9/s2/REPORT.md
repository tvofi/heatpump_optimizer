# Round 9 — D9-s2 (D9)

Rendered by the box B5 thread from the JSON the seat returned (`tools/audit/round9/reports-B5.json`), because the seat's own write of this file was refused by its harness. The content is the seat's; nothing was added, verified or judged.

- baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`
- exposure: none recorded

## Method and coverage

### D9.M1 — deep

The real coordinator cycle (_async_update_data) was replayed through tests/replay.py:run_fixture over tests/replay/synthetic-dhw-only.json: 48 cycles per day, 75 entities, solve via _await_optimize and process_worker in-process. The rig repeats the day N times. Five metrics were hooked on production symbols. (1) Full solves per cycle: solves_per_cycle.py gives 1.0 (48/48 main); with price tiles on it gives 2.0. (2) Loop-thread work per cycle: loop_work.py gives 26.7 ms CPU per real cycle, 0.617 reference solves, 22.8 % of the cycle, with the sensor_advisor split out. (3) Retained bytes: retained.py over 4 days / 192 cycles, slope per attribute, ru_maxrss. (4) Payload: payload.py gives data dict 75.8 KB/cycle, recorded 8.3 KB vs unrecorded 79.1 KB attributes per cycle, 247 KB/day of recorder attribute rows. (5) DHW planning loops: they live in optimizer.py and thermal_model.py (D9-s1 cells) and went to a lead. The rest-file part, dhw_schedule.overlap_fraction, was profiled at 114,360 calls per day of solves. Findings: D9-s2-01.

### D9.M2 — deep

m2_nonkernel_2x.py runs the gate's own sweep (51 scenarios, Calibration, build_case) and evaluates every tests/stress.py rule with the gate's own functions (live_solve_budget_ratio, scenario_budget, SWEEP_BUDGET_RATIO, work_drift_compare against a PLAIN arm of the same process). Arms: plain; uniform non-kernel 2x; null plain2; confined non-kernel 2x at scale 1/2.19/4; a positive control that runs one scenario's whole solve twice; and a six-victim leave-one-out arm. m2_loop_blind.py runs tests/replay.py:cost_offenders (the only budget over the cycle) under a loop-only 2x, replay's own whole-cycle 2x and a loop x5 perturbation, and traces stress.build_case's reach into cycle code. Findings: D9-s2-02, D9-s2-03.

## Findings

### D9-s2-01 — sensor_advisor ranking re-simulated on the event loop at every plan-sensor state write: 1152 simulate steps, ~32% of loop CPU per cycle

- step: D9.M1; severity: low; class: bug; class_guess: new
- instrumented symbol: `heatpump_optimizer.topology:rank_sensor_advisor (called from sensor:_sensor_advisor_attribute in _PlanSensorBase.extra_state_attributes); heatpump_optimizer.thermal_model:ThermalModel.simulate_step counted outside executor jobs`
- metric: ThermalModel.simulate_step calls made on the loop thread (outside hass.async_add_executor_job jobs) during one read of every published entity, on the replayed real cycle.

Every state write of the two plan sensors (_PlanSensorBase.extra_state_attributes) calls topology.rank_sensor_advisor on the event loop. Each read of all entities makes 2 calls and 384 ThermalModel.simulate_step calls; with 3 writes per cycle that is 1152 loop-thread simulate steps and 31.6% of the cycle's loop-thread CPU, for a result that depends only on the config entry and the once-per-cycle heat_pump_power_series.

```json
{
  "id": "D9-s2-01",
  "scope": "D9-s2",
  "step": "D9.M1",
  "title": "sensor_advisor ranking re-simulated on the event loop at every plan-sensor state write: 1152 simulate steps, ~32% of loop CPU per cycle",
  "severity": "low",
  "claim": "Every state write of the two plan sensors (_PlanSensorBase.extra_state_attributes) calls topology.rank_sensor_advisor on the event loop. Each read of all entities makes 2 calls and 384 ThermalModel.simulate_step calls; with 3 writes per cycle that is 1152 loop-thread simulate steps and 31.6% of the cycle's loop-thread CPU, for a result that depends only on the config entry and the once-per-cycle heat_pump_power_series.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/loop_work.py",
    "harness_path": "tools/audit/round9/D9/s2/loop_work.py",
    "value": 384,
    "unit": "ThermalModel.simulate_step calls on the loop thread per read of every entity (loop_simulate_steps_per_read); advisor_calls_per_read=2, entity_writes_per_cycle=3, advisor_share_of_loop=0.3164, advisor_cpu_per_read_ms=2.816, loop_cpu_per_real_cycle_ms=26.698",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "round-9 box B5: Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, Python 3.14.0rc2, numpy 2.4.6, scipy 1.17.1",
    "cpu_or_wall": "count",
    "contention_note": "Fan-out: up to two other D9-s2 processes (its own M2 sweep) on the box. The count is contention-immune. The CPU share (0.316) is provisional.",
    "tolerance": "exact for counts; +-25 % for the CPU share",
    "load1": 1.33,
    "thread_factor": 1.0004
  },
  "instrumented_symbol": "heatpump_optimizer.topology:rank_sensor_advisor (called from sensor:_sensor_advisor_attribute in _PlanSensorBase.extra_state_attributes); heatpump_optimizer.thermal_model:ThermalModel.simulate_step counted outside executor jobs",
  "perturbation": {
    "change": "--advisor-steps 1 (in memory: topology._ADVISOR_REPLAY_STEPS 48 -> 1); and, config, --options '{\"lower_floor_temp_entity\": \"sensor.x\", \"floor_return_temp_entity\": \"sensor.y\", \"buffer_tank_temp_entity\": \"sensor.z\"}' (every advisor candidate configured)",
    "expected_direction": "down",
    "observed_value": "8 steps per read with --advisor-steps 1 (advisor_share_of_loop 0.086); 0 steps per read with all candidates configured (advisor_share_of_loop 0.0011)"
  },
  "metric_definition": "ThermalModel.simulate_step calls made on the loop thread (outside hass.async_add_executor_job jobs) during one read of every published entity, on the replayed real cycle.",
  "phenomenon_property": "No entity property evaluated at state-write time runs a thermal-model simulation. A value derived from configuration and per-cycle data is computed at most once per cycle, off the per-write path.",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/loop_work.py  (RESULT loop_simulate_steps_per_read must be 0; the hook counts every simulate_step on the loop thread during entity reads, whichever property makes it)",
  "stop_rule_class": "bug",
  "class_guess": "new",
  "files": [
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/topology.py",
    "custom_components/heatpump_optimizer/coordinator.py"
  ],
  "proposed_fix_scope": "Compute the #1269 ranking once per cycle in the coordinator (e.g. in _build_data_dict, or memoised on the config plus the power-series tuple) and have both plan sensors read the cached value. The per-read ThermalParameters.from_config plus ThermalModel construction (0.54 ms per read even at 1 step) goes with it. Pi extrapolation: 8.4 ms/cycle here x ASSUMED 4-6x (Pi 4 Cortex-A72 vs this Xeon core, not measured) = 34-51 ms of event-loop CPU per 30-min cycle, plus more on every extra listener update (peak-guard transitions, snapshot restore).",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/loop_work.py --options '{\"lower_floor_temp_entity\": \"sensor.x\", \"floor_return_temp_entity\": \"sensor.y\", \"buffer_tank_temp_entity\": \"sensor.z\"}'",
    "value": "loop_simulate_steps_per_read=0, advisor_share_of_loop=0.0011",
    "note": "The arm where the ranking returns None. The effect vanishes, so the 0.316 share is the advisor's and not the rig's."
  },
  "reproduction_steps": [
    "From /home/claude/audit-r9-D9-s2: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/loop_work.py",
    "Read RESULT loop_simulate_steps_per_read (384) and advisor_share_of_loop (~0.32)",
    "Re-run with --advisor-steps 1 (8) and with all candidates configured (0)"
  ]
}
```

### D9-s2-02 — No budgeted check can see a 2x of the coordinator's loop-thread work; nightly replay needs ~x5, stress.py reaches none of it

- step: D9.M2; severity: medium; class: bug; class_guess: new
- instrumented symbol: `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data (injection and executor-CPU split via harness:FakeHass.async_add_executor_job), tests/replay.py:cost_figures/cost_offenders/COST_BUDGETS (the gate's own check), tests/stress.py:build_case (reach trace)`
- metric: Offenders returned by tests/replay.py:cost_offenders on the committed fixture when only the cycle's loop-thread CPU (update minus executor jobs, plus entity read) is doubled exactly.

An exact 2x of the coordinator cycle's loop-thread CPU (update work outside the executor plus the entity read) leaves tests/replay.py:cost_offenders empty: cycle_cpu_ratio goes 2.42 -> 2.82 against a 3.576 budget. tests/stress.py, the only per-PR CPU gate, executes 0 functions of coordinator.py/sensor.py/topology.py. Only a x5 of the loop work turns the nightly budget red.

```json
{
  "id": "D9-s2-02",
  "scope": "D9-s2",
  "step": "D9.M2",
  "title": "No budgeted check can see a 2x of the coordinator's loop-thread work; nightly replay needs ~x5, stress.py reaches none of it",
  "severity": "medium",
  "claim": "An exact 2x of the coordinator cycle's loop-thread CPU (update work outside the executor plus the entity read) leaves tests/replay.py:cost_offenders empty: cycle_cpu_ratio goes 2.42 -> 2.82 against a 3.576 budget. tests/stress.py, the only per-PR CPU gate, executes 0 functions of coordinator.py/sensor.py/topology.py. Only a x5 of the loop work turns the nightly budget red.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_loop_blind.py",
    "harness_path": "tools/audit/round9/D9/s2/m2_loop_blind.py",
    "value": 0,
    "unit": "cost_offenders entries for the loop2x arm (loop2x.offenders); none.offenders=0, cpu.offenders=1, loop_over_none=1.1644, none.loop_share_of_budgeted_cycle=0.1413, stress_cycle_functions=0 of 139 solve functions",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "round-9 box B5: Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, Python 3.14.0rc2, numpy 2.4.6, scipy 1.17.1",
    "cpu_or_wall": "count",
    "contention_note": "Fan-out: this seat's own stress sweep ran concurrently (load1 2.15). The offender counts depend on ref-normalised CPU ratios, so the ratios are provisional; the offender counts were identical on the re-run (load1 2.50).",
    "tolerance": "exact for offender counts; +-10 % for cycle_cpu_ratio",
    "load1": 2.15,
    "thread_factor": 1.0004
  },
  "instrumented_symbol": "heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data (injection and executor-CPU split via harness:FakeHass.async_add_executor_job), tests/replay.py:cost_figures/cost_offenders/COST_BUDGETS (the gate's own check), tests/stress.py:build_case (reach trace)",
  "perturbation": {
    "change": "--scale 4: spin 4x the loop-thread CPU after each update and each entity read, i.e. loop work x5",
    "expected_direction": "up",
    "observed_value": "loop5x.offenders=1 ('cpu_ratio 3.796 over its budget 3.576'), loop_over_none=1.5493"
  },
  "metric_definition": "Offenders returned by tests/replay.py:cost_offenders on the committed fixture when only the cycle's loop-thread CPU (update minus executor jobs, plus entity read) is doubled exactly.",
  "phenomenon_property": "Every budgeted cost check that covers the coordinator cycle must turn red on a 2x of the loop-thread share of the cycle alone. The part that blocks Home Assistant's event loop must not be diluted by the executor-side solve it is averaged with.",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_loop_blind.py  (loop2x.offenders must be >= 1; stress_cycle_functions names what the per-PR gate reaches)",
  "stop_rule_class": "bug",
  "class_guess": "new",
  "files": [
    "tests/replay.py",
    "tests/stress.py",
    "custom_components/heatpump_optimizer/coordinator.py"
  ],
  "proposed_fix_scope": "tests/replay.py: budget loop-thread CPU as its own figure: cycle CPU minus executor-job CPU, plus writes-per-cycle x one entity read. HA writes every entity 3 times per cycle (2 listener updates in async_run_optimization plus the refresh's own), while replay times 1 read: loop_work.py measures 26.7 ms per real cycle against the ~14.9 ms replay budgets. Give it the same sqrt(2) band and a perturbation arm that doubles only that share. Optionally move the cheap controls-plus-loop figure into the per-PR lane, which today reaches no cycle code.",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_loop_blind.py",
    "value": "none.offenders=0 (null); cpu.offenders=1 with cycle_cpu_ratio 4.592 > 3.576 (replay's own whole-cycle 2x, positive control)",
    "note": "The check is live and can fire. It fires for the whole cycle, not for the loop share, which is 14% of what it budgets."
  },
  "reproduction_steps": [
    "From /home/claude/audit-r9-D9-s2: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_loop_blind.py",
    "Read loop2x.offenders=0 beside cpu.offenders=1 and stress_cycle_functions=0",
    "Re-run with --scale 4: loop5x.offenders=1"
  ]
}
```

### D9-s2-03 — stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams

- step: D9.M2; severity: medium; class: bug; class_guess: new
- instrumented symbol: `heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (injection: after the real solve, spin CPU equal to solve CPU minus kernel CPU metered by the live tests/stress.py:SolverWork, times scale); tests/stress.py:build_case, Calibration, scenario_budget, live_solve_budget_ratio, SWEEP_BUDGET_RATIO, work_drift_compare (the gate's own rules)`
- metric: Number of tests/stress.py rules, evaluated with the gate's own functions over its own 51-scenario sweep, that trip when one scenario's non-kernel solve work is scaled up.

When one scenario's solve CPU is doubled (winter/2z/dhw at 2.014x) with all the extra work outside the three metered simulate seams, 0 of tests/stress.py's rules trip (ceiling, per-scenario, sweep, evaluations, simulate steps, kernel cost). The same holds for six victims across families at 1.92x-2.21x. This contradicts the file's own claim at SCENARIO_WORK_FACTOR that a 2x regression confined to one scenario is still seen. Non-kernel code is 44.6%-80.6% of every scenario's solve CPU.

```json
{
  "id": "D9-s2-03",
  "scope": "D9-s2",
  "step": "D9.M2",
  "title": "stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams",
  "severity": "medium",
  "claim": "When one scenario's solve CPU is doubled (winter/2z/dhw at 2.014x) with all the extra work outside the three metered simulate seams, 0 of tests/stress.py's rules trip (ceiling, per-scenario, sweep, evaluations, simulate steps, kernel cost). The same holds for six victims across families at 1.92x-2.21x. This contradicts the file's own claim at SCENARIO_WORK_FACTOR that a 2x regression confined to one scenario is still seen. Non-kernel code is 44.6%-80.6% of every scenario's solve CPU.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/gate_lock.py auto-lease --label d9s2-m2 -- /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_nonkernel_2x.py --arms plain,nonkernel2x_one@2.19,nonkernel2x_one@4 --victim winter/2z/dhw",
    "harness_path": "tools/audit/round9/D9/s2/m2_nonkernel_2x.py",
    "value": 0,
    "unit": "stress.py rules tripped (nonkernel2x_one@2.19.tripped_total); victim_cpu_x=2.0144, victim_evals_x=1, victim_sim_x=1, victim_kernel_x=0.967, victim_budget_x=2.630 (the per-scenario budget over this run's own ratio)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "round-9 box B5: Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, Python 3.14.0rc2, numpy 2.4.6, scipy 1.17.1",
    "cpu_or_wall": "count",
    "contention_note": "Fan-out. The gate lease was held by this run; up to 2 other seats' processes may have shared the box (load1 1.0-1.8). The rule counts were identical in all four sweeps that ran the confined injection. The CPU ratios are provisional.",
    "tolerance": "exact for rule counts; +-10 % for victim_cpu_x",
    "load1": 1.42,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (injection: after the real solve, spin CPU equal to solve CPU minus kernel CPU metered by the live tests/stress.py:SolverWork, times scale); tests/stress.py:build_case, Calibration, scenario_budget, live_solve_budget_ratio, SWEEP_BUDGET_RATIO, work_drift_compare (the gate's own rules)",
  "perturbation": {
    "change": "--arms plain,nonkernel2x_one@4 --victim winter/2z/dhw (non-kernel work x5 on the one scenario, solve x2.83)",
    "expected_direction": "up",
    "observed_value": "nonkernel2x_one@4.tripped_total=1 (tripped_cpu_per_scenario=1, victim_cpu_x=2.831 > budget 2.630); every count/kernel channel still 0"
  },
  "metric_definition": "Number of tests/stress.py rules, evaluated with the gate's own functions over its own 51-scenario sweep, that trip when one scenario's non-kernel solve work is scaled up.",
  "phenomenon_property": "A 2x of any single scenario's solve CPU trips at least one stress.py rule, whether the added work is inside the simulate seams (counts, kernel cost) or outside them (objective assembly, DHW planning Python, candidate scoring, result building).",
  "seam_rule": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/gate_lock.py auto-lease --label d9s2 -- /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_nonkernel_2x.py --arms plain,solvecpu2x_set  (every victim must be caught; add victims with --victims)",
  "stop_rule_class": "bug",
  "class_guess": "new",
  "files": [
    "tests/stress.py"
  ],
  "proposed_fix_scope": "tests/stress.py: add a per-scenario non-kernel channel judged against the baseline captured beside the run (capture_baseline_work already solves the same scenarios on the same machine). Candidate: (solve CPU - kernel CPU) per counted evaluation, with the KERNEL_DOUBT re-solve median that kernel_cost_over_verdict uses. Or judge per-scenario solve CPU against that same-machine baseline instead of the recorded table at 3.0x. Also correct the SCENARIO_WORK_FACTOR comment's claim. Pi relevance: the non-kernel share (median 0.487) is interpreter-bound Python, the part a Pi-class core slows most.",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/gate_lock.py auto-lease --label d9s2-m2 -- /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_nonkernel_2x.py --arms plain,nonkernel2x,plain2,twice",
    "value": "plain2.tripped_total=0 (sweep_ratio_over_plain 0.9986). Positive control from the --arms plain,nonkernel2x_one,twice_one --victim winter/2z/dhw run: twice_one.tripped_total=2 (evals and simulate channels at 2.000x, victim_cpu_x 2.073).",
    "note": "A clean re-sweep trips nothing. The same-size 2x through optimize() twice trips two rules. Only the location of the extra work differs."
  },
  "leave_one_out": {
    "cells": 6,
    "min": 1.92112,
    "max": 2.21356,
    "drop_most_favourable": 1.96907
  },
  "reproduction_steps": [
    "From /home/claude/audit-r9-D9-s2, holding the lease: ... m2_nonkernel_2x.py --arms plain,nonkernel2x_one@2.19,nonkernel2x_one@4 --victim winter/2z/dhw",
    "Read nonkernel2x_one@2.19.tripped_total=0 with victim_cpu_x ~2.01, and nonkernel2x_one@4.tripped_total=1",
    "Leave-one-out: ... m2_nonkernel_2x.py --arms plain,solvecpu2x_set -> solvecpu2x_set.tripped_total=0 with six victims at 1.92x-2.21x solve CPU (drop the most favourable, winter/1z/dhw at 1.92x: min 1.97x), every victim evals_x=sim_x=1, over_per_scenario_budget=0"
  ]
}
```

## Non-findings

- A coordinator cycle runs exactly one full solve by default (main path). Enabling price tiles adds exactly one what-if solve per scheduled cycle, as documented ("at most one extra solve per interval"). No diagnose, simulate or other path runs a solve inside a scheduled cycle. — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/solves_per_cycle.py [--options '{"price_tiles_enabled": true, "main_fuse_amperes": 25}']` → solves_per_cycle_mean=1.0000, max=1, path_main=48/48. With tiles: 2.0000 (main 48, price_tile 48). The fuse advisor made 0 solves in the one-day replay (weekly rate limit).
- A UNIFORM 2x of the solver's non-kernel work across all 51 scenarios is caught by stress.py, but only by the sweep rule. All per-scenario rules and the three count/kernel channels stay at 0. — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/gate_lock.py auto-lease --label d9s2-m2 -- /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_nonkernel_2x.py --arms plain,nonkernel2x,plain2` → nonkernel2x.tripped_total=1 (tripped_sweep=1, sweep_ratio 192.1 vs 134.32; per-scenario x1.32-x1.78). Non-kernel share of sweep CPU is 0.626 (per scenario min 0.446, median 0.487, max 0.806). plain2.tripped_total=0.
- The sweep budget holds on this box but with little headroom. Plain sweep ratio is 119.3-121.6 against SWEEP_BUDGET_RATIO 134.32 (derived at 94.98 on the M1), so here the sweep rule sees a uniform +10-12 % rather than +41 %. The detection check still passes (budget < 2x observed). Recorded as portability context, not a defect. — `same as above, RESULT plain.sweep_ratio` → 119.417 / 119.254 / 121.56 / (set run) plain; budget 134.32
- Coordinator collections grow over 4 replayed days only where a bounded structure is still filling. _accuracy.samples is deque(maxlen=672) = 14 days at 30 min, and data['heat_pump_power_series'] is a copy of it. _price_days_seen is an untrimmed in-memory set (the store keeps the last 90) but grows by about one short string per day (9 B/cycle, 983 B after 4 days, ~25 KB/year). That is negligible, so it is not filed. — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/retained.py --days 4 --top 20` → total_bytes_end=496540, total slope 422 B/cycle (20 KB/day), dominated by _accuracy 404 B/cycle (92 KB at 192 cycles, cap 672 samples). data 30 B/cycle (heat_pump_power_series). _prices 24 B/cycle. _price_days_seen 9 B/cycle. ru_maxrss 177.7 MB for the whole harness process (HA stubs, numpy, scipy, replay).
- Published payload versus the recorder exclusion set: the bulky attributes are excluded. No single recorded key exceeds 11.3 KB/day. — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/payload.py --top 15` → data_dict 75,816 B/cycle. Entity attributes 8,261 B recorded vs 79,130 B unrecorded per cycle. 893 recorded attribute rows and 247,172 B/day (upper bound: component-level exclusions not subtracted). Top entity climate.heat_pump_optimizer 17.2 %. Top keys: plan_narrative.items 11.2 KB/day, plan_narrative.lines 9.2 KB/day, savings_months 6.9 KB/day.
- The only budget over the real coordinator cycle is live and can fire: replay's own whole-cycle 2x turns it red, and a clean replay is green. — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/m2_loop_blind.py` → none.offenders=0 (cycle_cpu_ratio 2.4226); cpu.offenders=1 (4.5922 > 3.576)
- A 2x of one scenario's WHOLE solve (optimize() run twice) is caught by stress.py's count channels. This confirms #346/#1229 on this tree. — `... m2_nonkernel_2x.py --arms plain,nonkernel2x_one,twice_one --victim winter/2z/dhw` → twice_one.tripped_total=2 (work evals and simulate at 2.000x, victim_cpu_x 2.073). nonkernel2x_one (scale 1, victim x1.458) tripped 0.
- The loop-thread work of a default cycle, outside the sensor advisor, is bounded and holds no simulate step in the update path. — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/s2/loop_work.py` → loop_update_simulate_steps_per_cycle=0.00. loop_update_cpu_ms=9.03, entity_read_cpu_ms=5.89 per read, executor (solve) 90.6 ms. loop_cpu_per_real_cycle_ratio=0.617 reference solves. Pi at ASSUMED 4-6x: 107-160 ms loop CPU per 30-min cycle.

## Harnesses

- `tools/audit/round9/D9/s2/_rig.py`
- `tools/audit/round9/D9/s2/solves_per_cycle.py`
- `tools/audit/round9/D9/s2/loop_work.py`
- `tools/audit/round9/D9/s2/retained.py`
- `tools/audit/round9/D9/s2/payload.py`
- `tools/audit/round9/D9/s2/m2_loop_blind.py`
- `tools/audit/round9/D9/s2/m2_nonkernel_2x.py`

## Unfinished

- D9.M1: Longest contiguous event-loop stretch per cycle on a real asyncio loop was not measured: replay's FakeHass runs executor jobs inline, so only the loop-thread CPU total per cycle is reported (loop_work.py). Measuring the stretch needs a real loop plus ThreadPoolExecutor rig driving _async_update_data. Only one recorded fixture exists (DHW-only, single zone), so the loop share and advisor share are from one topology. A two-zone or space-heating replay would need a new fixture.
- D9.M1: REPORT.md was not written: this session's harness refuses report-file writes from a subagent. The report content is this JSON; the harness headers carry method, command, perturbation and expected values.
- D9.M2: The wall/CPU-ratio numbers were taken during the fan-out and are provisional. The quiet window should re-take m2_nonkernel_2x.py (plain,nonkernel2x_one@2.19,nonkernel2x_one@4 --victim winter/2z/dhw; plain,solvecpu2x_set) and m2_loop_blind.py. Counts of tripped rules were stable across all runs. On this Xeon box the plain sweep ratio already sits at 119-122 against the 134.32 budget (0.89-0.91). That was not pursued as a finding (portable-budget variance, recorded as a non-finding).

## Leads

- owner D9-s1: `custom_components/heatpump_optimizer/optimizer.py` `HeatPumpOptimizer._build_dhw_requirements / _apply_dhw_min_run / _plan_dhw_min_cost` — DHW planning loops dominate the DHW-only replay's solve. Under cProfile over 48 real cycles, _build_dhw_requirements was 9.64 s of 16.5 s solve time (58 %), with thermal_model.extend_dhw_temps called 1383 times and simulate_dhw_step 106,595 times (~2,220 per solve). A candidate for the brief's DHW planning loop metric (simulate-step-equivalents per DHW loop).
- owner D9-s1: `custom_components/heatpump_optimizer/thermal_model.py` `ThermalModel.effective_dhw_draw_pattern / dhw_tank_heat_loss_coefficient / dhw_inlet_reference` — Per-step helpers called ~100k-320k times per day of solves: effective_dhw_draw_pattern 4,704 calls driving dhw_schedule.overlap_fraction 114,360 times (24 per call) for a window set that is constant within a solve; dhw_inlet_reference 321,602 calls; dhw_tank_heat_loss_coefficient 107,572 calls. These look cacheable per solve and are not metered by any stress.py count channel (see D9-s2-03).
- owner unknown: `custom_components/heatpump_optimizer/entity.py` `HeatPumpOptimizerSensorBase.__init_subclass__ scrub (_finite)` — The non-finite scrub walks every attribute of every entity at every write, including the unrecorded bulk series: 233,594 recursive _finite calls per 48 entity reads (~4.9k per read). Its CPU share of the 5.9 ms entity read was not isolated. A loop-thread cost that grows with payload size.
