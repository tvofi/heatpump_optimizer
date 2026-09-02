# Quiet-window re-takes and D3 full-gate confirmations (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884` throughout. Interpreter
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python`,
`PYTHONPATH=tests/hastub`, the five thread-pin variables exported before any numpy
import, every harness run from the worktree or export it was written in. The gate
lock `/tmp/hpo-gate.lock` was held for the whole window.

## Conditions, and one caveat about `load1` on this box

The box was idle: no other auditor's process ran during the window (`ps` showed no
Python or Node but my own; `top` reported **92-96 % idle CPU** before every run).
But **`load1` never fell below 1.38**: this Mac carries a standing load average of
roughly 1.4-2.0 from system daemons that are not CPU-bound, so the contract's
`load1 <= 1.5` gate is not reachable here even on a completely idle machine. Each
run was therefore started at a `load1` trough *and* at >85 % idle CPU, and both
numbers are recorded in every log (`QUIET_LOAD_BEFORE`, `QUIET_CPU_BEFORE`,
`QUIET_LOAD_AFTER`, `QUIET_CPU_AFTER`) alongside the harness's own closing
`RESULT load1`. `thread_factor` was 1.000 on every numpy harness.

Two runs were redone because they were taken while the box was busy:

- `D9-h4.log` (load1 3.54) -> **`D9-h4-redo.log`** (load1 2.20 -> 1.93). The redo is canonical.
- `D9-h3-run2/run3` were caught by a load spike (load1 15.8 and 8.0 at start, though
  CPU was 95 % idle). **`D9-h3-run4.log`** (load1 1.47 -> 1.42, the only sample inside
  the contract's gate at both ends) is canonical for D9-05; all four samples agree.

## Part 1 - re-takes (106 numbers, 90 reproduced, 16 not)

`reproduced` applies the tolerance the finder's report states (timing +-25 % unless
the report is tighter). Full machine-readable detail in `quiet.json`.

### D9-01 - `tools/audit/round2/D9/h1_grad_equivalents.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h1_grad_equivalents.py`  
Log: `tools/audit/round2/quiet/D9-h1.log` - load1 2.19238, thread_factor 1, swapins 11628422

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `pin_zero_range_two_zone_dhw.equivalents_per_gradient` | 9221.55 | 9221.55 | exact | yes | count: contention-immune |
| `two_zone_dhw.equivalents_per_gradient` | 297.32 | 297.32 | exact | yes | count: contention-immune |
| `pin_zero_range.equivalents_per_gradient` | 9294.55 | 9294.55 | exact | yes | count: contention-immune |
| `dhw_cap_zero_range.equivalents_per_gradient` | 9221.85 | 9221.85 | exact | yes | count: contention-immune |
| `dhw_cap_one_step_zero_range.equivalents_per_gradient` | 294 | 294 | exact | yes | count: contention-immune |
| `pin_zero_range_two_zone_dhw.simulate_step_calls` | 1595328 | 1595328 | exact | yes | count: contention-immune |
| `dhw_cap_zero_range.simulate_step_calls` | 1512384 | 1512384 | exact | yes | count: contention-immune |
| `two_zone_dhw.simulate_step_calls` | 20736 | 20736 | exact | yes | count: contention-immune |
| `two_zone_dhw.solve_over_reference` | 38.5 | 37.5528 | +-25% | yes | CPU ratio against reference_solve |
| `pin_zero_range_two_zone_dhw.solve_over_reference` | 751 | 721.079 | +-25% | yes | CPU ratio against reference_solve |
| `dhw_cap_zero_range.solve_over_reference` | 711-750 | 685.779 | +-25% | yes | CPU ratio against reference_solve |
| `dhw_cap_one_step_zero_range.solve_over_reference` | 54.7 | 53.7409 | +-25% | yes | CPU ratio against reference_solve |
| `pin_zero_range.solve_over_reference` | 39.1 | 33.1686 | +-25% | yes | CPU ratio against reference_solve |
| `two_zone_dhw.solve_cpu` | 908 | 668.703 | +-25% | **NO** | absolute CPU ms: the fan-out figure was inflated by contention |
| `pin_zero_range_two_zone_dhw.solve_cpu` | 25046 | 12840.3 | +-25% | **NO** | absolute CPU ms: the fan-out figure was inflated by contention |
| `dhw_cap_zero_range.solve_cpu` | 17700-23700 | 12211.7 | +-25% | **NO** | absolute CPU ms: the fan-out figure was inflated by contention |
| `dhw_cap_one_step_zero_range.solve_cpu` | 1824 | 956.965 | +-25% | **NO** | absolute CPU ms: the fan-out figure was inflated by contention |
| `pin_zero_range.solve_cpu` | 923 | 590.633 | +-25% | **NO** | absolute CPU ms: the fan-out figure was inflated by contention |
| `reference_solve_cpu` | 18-33 | 17.807 | +-25% | yes | the ruler itself; fan-out 18-33 ms |

### D9-03 - `tools/audit/round2/D9/h1_grad_equivalents.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h1_grad_equivalents.py`  
Log: `tools/audit/round2/quiet/D9-h1.log` - load1 2.19238, thread_factor 1, swapins 11628422

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `two_zone_dhw.scalar_steps_per_gradient` | 201.32 | 201.32 | exact | yes | count |
| `perturb_memo_two_zone_dhw.scalar_steps_per_gradient` | 100.66 | 100.66 | exact | yes | count |
| `perturb_memo_two_zone_dhw.batch_rows_per_gradient` | 96 | 96 | exact | yes | count |
| `two_zone_dhw.nfev` | 103 | 103 | exact | yes | count |
| `two_zone_dhw.njev` | 103 | 103 | exact | yes | count |
| `perturb_memo_two_zone_dhw.solve_cpu` | 789 | 565.387 | +-25% | **NO** | absolute CPU ms |

### D9-NF-solve-ratios - `tools/audit/round2/D9/h1_grad_equivalents.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h1_grad_equivalents.py`  
Log: `tools/audit/round2/quiet/D9-h1.log` - load1 2.19238, thread_factor 1, swapins 11628422

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `single_zone_nodhw.solve_over_reference` | 2.72 | 2.5727 | +-25% | yes |  |
| `single_zone_dhw.solve_over_reference` | 6.1 | 6.16291 | +-25% | yes |  |

### D9-04 - `tools/audit/round2/D9/h1b_dhw_loops.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h1b_dhw_loops.py`  
Log: `tools/audit/round2/quiet/D9-h1b.log` - load1 1.52002, thread_factor 1, swapins 11628547

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `two_zone_dhw.simulate_dhw_only_per_planning_call` | 64 | 64 | exact | yes | count |
| `two_zone_dhw.tank_steps_per_planning_call` | 6144 | 6144 | exact | yes | count |
| `two_zone_dhw.compute_cop_dhw_calls` | 14168 | 14168 | exact | yes | count |
| `perturb_h48_two_zone_dhw.simulate_dhw_only_per_planning_call` | 118 | 118 | exact | yes | count |
| `perturb_h48_two_zone_dhw.tank_steps_per_planning_call` | 22656 | 22656 | exact | yes | count |
| `single_zone_dhw.planner_share_of_solve` | 0.6296 | 0.621334 | +-15% | yes | share, report tolerance +-15 % |
| `two_zone_dhw.minrun_share_of_planner` | 0.48 | 0.465988 | +-15% | yes | share |
| `two_zone_dhw.planner_over_reference` | 3.4-3.8 | 4.07907 | +-15% | yes | ratio to reference_solve |
| `two_zone_dhw.planner_cpu` | 70-76 | 71.2532 | +-25% | yes | absolute CPU ms |
| `perturb_h48_two_zone_dhw.planner_over_reference` | 13.5 | 13.7981 | +-25% | yes | perturbation 24->48 h |
| `perturb_h48_two_zone_dhw.planner_cpu` | 266 | 241.025 | +-25% | yes | absolute CPU ms |

### D9-05 - `tools/audit/round2/D9/h3_gil_hold.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h3_gil_hold.py`  
Log: `tools/audit/round2/quiet/D9-h3-run4.log` - load1 1.42432, thread_factor 1, swapins 11851227

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `two_zone_dhw.starvation_share` | 0.967 | 0.950134 | +-5% | yes | the finding's headline; report tolerance +-5 % |
| `dhw_cap_zero_range.starvation_share` | 0.998 | 0.997563 | +-5% | yes |  |
| `single_zone_dhw.starvation_share` | 0.748 | 0.741276 | +-5% | yes |  |
| `idle_control.starvation_share` | 0 | 0 | +-5% | yes | null control |
| `two_zone_dhw.wall` | 795 | 674.411 | +-25% | yes | wall ms |
| `dhw_cap_zero_range.wall` | 14700 | 11398.2 | +-25% | yes | wall ms |
| `idle_control.ticks_per_second` | 779 | 758.467 | +-25% | yes | null control |
| `two_zone_dhw.ticks_per_second` | 74 | 44.4833 | +-25% | **NO** | loop turn rate under the solve |
| `two_zone_dhw.gap_p50` | 13.3 | 2.3596 | +-25% | **NO** | median loop gap |
| `two_zone_dhw.gap_p99` | 35.8 | 304.11 | +-25% | **NO** |  |
| `two_zone_dhw.longest_gil_hold` | 39.4 | 376.307 | +-25% | **NO** | report range 39-75 ms; four quiet samples give 265/313/376/412 ms - the defect is LARGER than reported |
| `perturb_switch50ms_two_zone_dhw.starvation_share` | 0.961 | 0.949365 | +-5% | yes | perturbation arm |

### D9-05 - `tools/audit/round2/D9/h3_gil_hold.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h3_gil_hold.py`  
Log: `tools/audit/round2/quiet/D9-h3.log` - load1 1.78564, thread_factor 1, swapins 11628559

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `perturb_switch50ms_two_zone_dhw.longest_gil_hold` | 82.9 | 404.181 | +-25% | **NO** | perturbation arm; only sampled in run 1 |

### D9-NF-loop-work - `tools/audit/round2/D9/h4_loop_thread_work.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h4_loop_thread_work.py`  
Log: `tools/audit/round2/quiet/D9-h4-redo.log` - load1 1.92822, thread_factor 1, swapins 11628775

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `two_zone_dhw.cycle3.loop_thread_cpu` | 3.08 | 2.40592 | +-25% | yes |  |
| `two_zone_dhw.cycle3.executor_cpu` | 712.6 | 525.779 | +-25% | **NO** | absolute CPU ms |
| `two_zone_dhw.cycle3.stage._build_data_dict` | 1.31 | 1.06013 | +-25% | yes |  |
| `perturb_h48_two_zone_dhw.cycle3.loop_thread_cpu` | 4.36 | 3.37417 | +-25% | yes |  |
| `perturb_price_tiles.cycle3.loop_thread_cpu` | 3.73 | 2.95783 | +-25% | yes |  |
| `two_zone_dhw.cycle3.loop_over_executor` | 0.0043 | 0.00457591 | +-25% | yes | the ratio the non-finding rests on |

### D9-NF-retained-bytes - `tools/audit/round2/D9/h5_retained_bytes.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h5_retained_bytes.py`  
Log: `tools/audit/round2/quiet/D9-h5.log` - load1 1.81152, thread_factor 1.00008, swapins 11628908

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `ru_maxrss_after_12_cycles` | 99991552 | 97976320 | +-25% | yes | RSS |
| `ru_maxrss_after_48_cycles` | 101924864 | 100794368 | +-25% | yes | RSS |
| `deep_after_cycle1` | 361805 | 361805 | exact | yes | deterministic byte count |
| `deep_after_cycle16` | 381989 | 381989 | exact | yes | deterministic byte count |
| `deep_slope_second_half` | 521-773 | 773.036 | +-25% | yes | B/cycle |
| `traced_slope_second_half` | 4385 | 4733.61 | +-25% | yes | B/cycle |
| `growth_total_traced_excl_harness` | 3354 | 3445.38 | +-25% | yes | B/cycle |
| `growth_own_total` | 1681 | 1541 | +-25% | yes | B/cycle |
| `store_saves_per_cycle.total` | 2.125 | 2.125 | exact | yes |  |
| `store_bytes_per_cycle.total` | 7041-9605 | 7040.94 | +-25% | yes |  |

### D9-02 - `tools/audit/round2/D9/h7_stress_gate.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D9/h7_stress_gate.py`  
Log: `tools/audit/round2/quiet/D9-h7.log` - load1 1.78418, thread_factor 1.0002, swapins 11628892

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `smallest_detectable_uniform_regression` | 4.685 | 4.76301 | +-20% | yes | report tolerance +-20 % on the ratios |
| `plain.worst_ratio` | 298.8 | 293.932 | +-20% | yes | report tolerance +-20 % on the ratios |
| `plain.sweep_ratio` | 50.7 | 53.3809 | +-20% | yes | report tolerance +-20 % on the ratios |
| `plain.median_ratio` | 33.9 | 35.6426 | +-20% | yes | report tolerance +-20 % on the ratios |
| `injected_2x.worst_ratio` | 590.5 | 588.661 | +-20% | yes | report tolerance +-20 % on the ratios |
| `injected_2x.sweep_ratio` | 105.2 | 106.545 | +-20% | yes | report tolerance +-20 % on the ratios |
| `plain.per_scenario_tripped` | 0 | 0 | exact | yes | report tolerance +-20 % on the ratios |
| `plain.sweep_tripped` | 0 | 0 | exact | yes | report tolerance +-20 % on the ratios |
| `injected_2x.per_scenario_tripped` | 0 | 0 | exact | yes | report tolerance +-20 % on the ratios |
| `injected_2x.sweep_tripped` | 0 | 0 | exact | yes | report tolerance +-20 % on the ratios |
| `ci_sets_stress_ratio` | 0 | 0 | exact | yes | report tolerance +-20 % on the ratios |
| `tests_memory_instrumentation` | 0 | 0 | exact | yes | report tolerance +-20 % on the ratios |

### D0-02 - `tools/audit/round2/D0/race_grid.py --quiet`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D0/race_grid.py --quiet`  
Log: `tools/audit/round2/quiet/D0-race_grid.log` - load1 1.77, thread_factor 1, swapins 0

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `production_cpu_total` | 111.8 | 80.34 | +-25% | **NO** | the one provisional number in D0; the quiet box is FASTER, which is the expected direction |
| `wall_total` | 780 | 556.6 | +-25% | **NO** | report: about 13 min under load |
| `restart_improves_tz` | 15 | 15 | exact | yes | count: contention-immune |
| `pg_above_pgtol_tz` | 64 | 64 | exact | yes | count: contention-immune |
| `cells_with_gap_tz` | 49 | 49 | exact | yes | count: contention-immune |
| `step0_differs_among_gap_cells` | 28 | 28 | exact | yes | count: contention-immune |
| `mean_restart_gap_sek_tz` | 0.0519 | 0.0519 | exact | yes | SEK gap, report tolerance +-1e-3: bit-identical |
| `mean_gap_sek_tz` | 0.1088 | 0.1088 | exact | yes | SEK gap, report tolerance +-1e-3: bit-identical |
| `max_gap_sek_tz` | 2.5099 | 2.5099 | exact | yes | SEK gap, report tolerance +-1e-3: bit-identical |
| `null_flat_mean_gap_sek_tz` | 0.1553 | 0.1553 | exact | yes | SEK gap, report tolerance +-1e-3: bit-identical |
| `nonflat_mean_gap_sek_tz` | 0.1022 | 0.1022 | exact | yes | SEK gap, report tolerance +-1e-3: bit-identical |
| `loo_mean_gap_pct_tz` | 0.232 | 0.232 | exact | yes | SEK gap, report tolerance +-1e-3: bit-identical |

### D1-02 - `tools/audit/round2/D1/lifecycle_realloop.py`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D1/lifecycle_realloop.py`  
Log: `tools/audit/round2/quiet/D1-lifecycle.log` - load1 2.26, thread_factor 32.582, swapins 0

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `midsolve_eager.sched_zombie_service_calls` | 3 | 3 | exact | yes | the finding's headline value |
| `sched_midsolve_zombie_actuations` | 1 | 1 | exact | yes |  |
| `sched_midsolve_zombie_saves` | 2 | 2 | exact | yes |  |
| `notready_leaked_listeners` | 10 | 10 | exact | yes |  |
| `notready_leaked_mqtt_subs` | 5 | 5 | exact | yes |  |
| `notready_zombie_coordinators` | 5 | 5 | exact | yes |  |
| `total_escaped_exceptions` | 0 | 0 | exact | yes |  |
| `midsolve_lazy.sched_zombie_service_calls` | 6 | 3 | exact | **NO** | DID NOT REPRODUCE: 3, not 6. The lazy arm issued one zombie cycle here, not two; the eager arm (the finding's headline) reproduced exactly |

### D10-14 - `tools/audit/round2/D10/coverage_suite.sh`

Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub <interp> tools/audit/round2/D10/coverage_suite.sh`  
Log: `tools/audit/round2/quiet/D10-coverage.log` - load1 1.65, thread_factor 1, swapins 11647165

| metric | original (fan-out) | quiet | tol | reproduced | note |
|---|---|---|---|---|---|
| `coverage_total_pct` | 88.4 | 88.4 | +-1% | yes | report tolerance +-1.0 pt |
| `coverage_config_flow_pct` | 86.4 | 86.4 | +-1% | yes | +-1.0 pt |
| `coverage_statements` | 12877 | 12877 | exact | yes |  |
| `coverage_modules_ge95` | 20 | 20 | exact | yes |  |
| `coverage_missing` | 1493 | 1491 | +-1% | yes |  |
| `scripts_nonzero_exit` | 2 | 2 | exact | yes | entities.py and golden.py, both export artefacts |
| `wall_s` | 1818 | 982 | +-25% | **NO** | the provisional number; quiet box is 46 % faster |

### What did not reproduce, and what it means

Four classes, none of which weakens the finding it belongs to:

1. **Absolute CPU/wall figures are 26-49 % lower on the quiet box** (D9-01's five
   `solve_cpu` values, D9-03's memo arm, D9's `executor_cpu`, D0-02's
   `production_cpu_total` 111.8 -> 80.3 s, D10-14's `wall_s` 1818 -> 982 s). Every one
   moves in the expected direction - the fan-out numbers were inflated by ten
   auditors sharing the box - and every *ratio* against `reference_solve` reproduced
   inside tolerance. This is exactly the split the harness contract predicts, and it
   is why the ratios, not the milliseconds, carry the findings.

2. **D9-05's gap distribution is worse than reported, not better.** The starvation
   share - the number the finding rests on - reproduced (0.967 -> 0.942-0.950 across
   four samples, inside the report's +-5 %). But the *longest GIL hold* came out
   **265 / 313 / 376 / 412 ms** against a reported 39.4 ms (report range 39-75 ms),
   with `gap_p99` 232-338 ms against 35.8 ms, and `gap_p50` *lower* (1.6-2.4 ms vs
   13.3 ms). The stage attribution also differs: the longest hold landed in
   `dhw_lp_build` in three samples and `batch_sim` in the fourth, where the report
   names `simulate_trajectory_batch`. Under contention the loop was being scheduled
   often enough to break long holds into many medium ones; on an idle box the
   executor thread keeps the GIL for a quarter to two-fifths of a second at a
   stretch. **D9-05 understates its own defect** and should be re-stated from these
   numbers, with the LP build named alongside the batch simulation.

3. **D1-02's lazy arm halved: 6 -> 3 zombie service calls**, and the actuation flipped
   from `switch.turn_on` to `switch.turn_off` in both arms. The finding's headline
   (the eager arm: 3 calls, 1 actuation, 2 store writes) reproduced exactly, as did
   every `notready_*` count. The lazy arm ran one zombie cycle here rather than two;
   the direction of the switch command follows the plan the frozen clock lands on,
   and neither is load-related. The claim stands; the `6` in the report's tolerance
   line does not.

4. **D0-02's wall/CPU only.** All 160 cells were compared field by field against the
   fan-out run's `out/race_grid_24h_baseline.json`: **every one of 22 numeric fields
   in all 160 cells was bit-identical** (max |delta| 0.0), including every SEK gap,
   projected gradient and iteration count. The solver is deterministic on this build.

5. **D10-14's coverage percentage is stable; only its wall time moved.**
   `coverage_total_pct` came back at exactly 88.4 %, `config_flow.py` at 86.4 %,
   12877 statements and 20 of 45 modules at 95 % - all identical. `coverage_missing`
   moved 1493 -> 1491, and a diff of the per-module tables shows the whole difference
   is `sysid.py` (90.4 % -> 91.4 %, two lines): a fixture-dependent branch, which is
   the caveat the finder already stated. The same two scripts exited non-zero
   (`entities.py` on the export's missing RELEASE_NOTES.md, `golden.py` on the
   strict comparison this box cannot reproduce), so the measured set is unchanged.

## Part 2 - D3 full-gate confirmations

Each mutant, in order, in `/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D3`:

```
git checkout -q -b quiet-<id> c398fc84eec25fc44b60d74aae05b9a2da205884
git apply tools/audit/round2/D3/mutants/<id>.patch
git commit -qam 'quiet-window mutant <id>'      # env_drift refuses HEAD == baseline
PYTHON=<interp> GATE_SCOPE=full GOLDEN_MODE=drift \
  GOLDEN_REF=c398fc84eec25fc44b60d74aae05b9a2da205884 GATE_JOBS=1 ./tests/run.sh
git checkout -q --detach c398fc84eec25fc44b60d74aae05b9a2da205884 && git branch -D quiet-<id>
```

Driver: `tools/audit/round2/quiet/d3_gate.sh <id>` (asserts the preconditions, runs
the gate, restores the worktree, prints the verdict).

| mutant | finding | patch | verdict | killed by | scripts run | wall | log |
|---|---|---|---|---|---|---|---|
| M31 | D3-01 | `tools/audit/round2/D3/mutants/M31.patch` | **SURVIVED** | - | 16 | 201 s | `tools/audit/round2/quiet/D3-M31.gate.log` |
| M19 | D3-02 | `tools/audit/round2/D3/mutants/M19.patch` | **SURVIVED** | - | 16 | 201 s | `tools/audit/round2/quiet/D3-M19.gate.log` |
| M13 | D3-03 | `tools/audit/round2/D3/mutants/M13.patch` | **SURVIVED** | - | 16 | 202 s | `tools/audit/round2/quiet/D3-M13.gate.log` |
| M32 | D3-04 | `tools/audit/round2/D3/mutants/M32.patch` | **SURVIVED** | - | 16 | 201 s | `tools/audit/round2/quiet/D3-M32.gate.log` |
| M21 | D3-05 | `tools/audit/round2/D3/mutants/M21.patch` | **SURVIVED** | - | 16 | 200 s | `tools/audit/round2/quiet/D3-M21.gate.log` |
| M30 | D3-06 | `tools/audit/round2/D3/mutants/M30.patch` | **SURVIVED** | - | 16 | 205 s | `tools/audit/round2/quiet/D3-M30.gate.log` |

**All six survive the full gate: six confirmed suite gaps.** Each run ended in
`ALL TEST SCRIPTS PASSED` with 16 scripts executed, nothing scoped out, and the
mutant provably in the tree (`git diff --stat` against the baseline is recorded as
`D3_HEAD` in each log).

This closes the gap D3's own prescreen left open: the prescreen could not run
`stress.py`, `edge.py` or `backtest.py`, and skipped `golden.py` because its strict
comparison does not reproduce on this box. All three now ran, plus `env_drift.py
--all` against the baseline (the drift-mode replacement for `golden.py`) and
`card_drift.mjs`. The survivors survived those too.

Scope caveat, stated once: this is the gate CI runs on **every push and PR**, which
skips `tests/rolling.py` (`SLOW=1`, the closed-loop simulation) - the same skip CI's
fast lane takes. CI's nightly/dispatch job sets `SLOW=1`
(`.github/workflows/tests.yml:293`), so a mutant only `rolling.py` could catch would
still show as a survivor here. `golden.py` is skipped in drift mode by design.

## Worktree hygiene

`audit-r2-D3` ends at `c398fc84eec25fc44b60d74aae05b9a2da205884` detached, no
`quiet-*` branch, `git status` showing only `?? tools/audit/`, and `git diff
--stat baseline HEAD` empty. `audit-r2-D0`'s `out/race_grid_24h_baseline.json` was
overwritten by the re-take and has been restored to the fan-out original; the quiet
copy is kept beside the logs as `D0-race_grid_24h_baseline.quiet.json`. Production
and tests were never modified outside D3's apply/revert cycle.

## Files

- `tools/audit/round2/quiet.json` - machine-readable, both parts
- `tools/audit/round2/quiet/*.log` - one log per run, each carrying its own conditions
- `tools/audit/round2/quiet/run_quiet.sh`, `d3_gate.sh` - the two drivers
- `tools/audit/round2/quiet/emit.py`, `emit_md.py` - build `quiet.json` and this file from the logs
