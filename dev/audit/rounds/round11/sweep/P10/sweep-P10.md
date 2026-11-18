# Round 11 class sweep: P10 (CPU work on the event loop)

Class P10 (`dev/audit/config/bugclasses.json`): CPU work (a model kernel, a fit, a
batch simulation) runs outside the process worker, on the event loop or on a
GIL-holding executor thread, and starves the loop. Ledger status: `open`,
`detector: null`, `barrier: null`.

The judged finding is **D9-s1-04** (verified, low). `coordinator.async_simulate`
calls `whatif.schedule_days(...)` inline when `steady=True`. That function
evaluates `o.reference_day(i)` for both optimizers on the loop thread, and through
`HeatPumpOptimizer._compute_baseline_power` this runs 384 `ThermalModel.simulate_step`
calls per steady what-if (960 on the weekend arm).

All commands below run from the register worktree (`origin/handoff/audit-r11-register`,
28b864af).

## Why round 10's enumerator missed it

`dev/audit/rounds/round10/D14/sweep-P10/p10_loop_reach.py`, run at the register head,
prints `loop_reachable_seams=2`, and the D9-s1-04 site is not among them
(`D14/sweep-P10/r10_enumerator_at_head.out`). There are two reasons:

- It leaves a call on any receiver other than `self` or a module unresolved, and
  `schedule_days` reaches the kernel through `o.reference_day(i)`, where `o` is an
  optimizer it was handed.
- It counts a callable parameter named `solve` (`whatif.steady_pair`, which is
  `_held_solve`, an off-loop hop) as a `numpy.linalg` kernel.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-P10/p10_loop_reach.py` keeps round 10's
rules: every `async def` is a root, and a function handed to `_await_process`,
`_await_off_loop` or `async_add_executor_job` is an argument, not an edge. It changes
four things:

- A call on any other receiver resolves to every package function of that name, when
  the package defines that name at most three times (`--fanout`); a logger receiver is
  excluded.
- A bare name resolves through `from .mod import f`. A bare name defined nowhere is a
  callable parameter and stays unresolved.
- linalg and optimize names count as kernels only on a `linalg`/`optimize` receiver
  or when imported from numpy/scipy.
- `--through-hops` follows the hops as well and marks them, so every seam's chain
  names the hop that guards it.

Output: `kernel_seams=31`, `loop_reachable_seams=4` (`D14/sweep-P10/p10_loop_reach.out`).
With `--through-hops`, 27 seams are reached
(`p10_loop_reach_through_hops.out`).

| control | command | result |
|---|---|---|
| positive (re-finds D9-s1-04) | `--seam optimizer.py:_compute_baseline_power` | `FAIL on the loop`, exit 1. Chain: `async_simulate / whatif.schedule_days / optimizer.reference_day / _compute_baseline_power` |
| positive, dynamic | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D9/s1/h_whatif_loop_block.py` | `loop_simulate_step_calls=384` (960 weekend); loop CPU 10.9–22.6 ms per what-if |
| null, clean fixture | `--null` (two files; the kernel is reached only through `_await_off_loop`) | `loop_reachable_seams=0` |
| null, dynamic | the same harness, `null_steady_false` | 0 |
| perturbation, static | `--perturb` (one line: the hop is replaced by a direct call) | 0 → 1 |
| perturbation, dynamic | the same harness, `perturbed_offloop` (`reference_day` through the worker) | 384 → 0 |

The 12 generic method names defined more than three times stay unresolved; the
count is printed on stderr. That blind spot belongs to the dynamic detector
(`D14/s3/p10_routes.py`, `tests/replay.py:kernel_routes`).

## Dispositions (all 31 seams)

**Instance (the judged site; none beyond it)**
- `optimizer.py:_compute_baseline_power:simulate_step`, the D9-s1-04 site. On the
  same route, without a hop, `thermal_model.py:valve_top_equilibrium:solve` is reached
  via `_thermostat_held_state → _held_at_valve_top`. It is the same missing hop at
  `whatif.schedule_days`, and the finding's fix removes both, so it is not counted
  separately.

**Not applicable**
- `coordinator.py:_whatif_solve:simulate_wood_slots`. `wood_fuel.simulate_wood_slots`
  parses override slots into a kW series and runs no model kernel; only its name
  matched (as in round 10).
- `drift.py:_positive_definite:cholesky`, reached through
  `_async_load_thermal_learning`. It is one validity check of a stored k×k
  covariance at restore, measured at 25–30 µs for k = 2…8. That is not a model
  kernel, fit or batch simulation, and it cannot starve the loop.

**Guarded** (the hop `--through-hops` names)
- `optimizer.py` (`_combi_dhw_exo`, `_combi_flux_exchange`, `_optimize_with_dhw`,
  `_replay_end_state`, `_scoped_minimize`, `_solve_objectives._space_traj`,
  `_tighten_buffer_caps`), `dhw_planner.py` (`_clamp_dhw_to_capacity`,
  `_dhw_coil_wood_forecast`, `_dhw_plan_temps`, `_plan_dhw_min_cost` linprog), and
  `thermal_model.py:extend_dhw_temps`: all reached from
  `_await_optimize → [_await_process] optimizer.optimize_in_process`.
  `thermal_model.py:valve_top_equilibrium` is reached by this route too, besides the
  instance route above.
- `sysid.py` (`identify` lstsq/solve, `_lm_solve`, `_held_state`,
  `_one_state_ua_halfwidth`, `_slab_ua_profile_halfwidth`, `_valve_drive`):
  `_sysid_step_off_loop → [_await_off_loop] sysid.step_detached`.
- `topology.py:_advisor_replay`: `_with_sensor_advisor → [_await_off_loop] rank_sensor_advisor`.
- `diagnosis.py:_room_after`: `async_diagnose_interval → [_await_process] diagnose_record`.
- `away.py:estimate_recovery_hours`, round 10's D14-s1-01:
  `_recovery_off_loop → [_await_off_loop]`. Fixed since round 10.
- `coordinator.py:_replay_step`, round 10's `_replay_interval` instance:
  `_replay_interval → [_await_off_loop] _replay_step`. Fixed since round 10.
- `thermal_model.py:simulate_trajectory` and `simulate_trajectory_with_dhw` (×2), and
  `optimizer.py:_solve_objectives.objective_batch:simulate_trajectory_batch`: these
  are the kernels' own bodies, reached only from the guarded callers above.

## Count and barrier

There is 1 instance seam, the judged site, and 0 beyond it. Both round-10 instances
are now guarded. The class still has no barrier. Proposed barrier: gate on
`p10_loop_reach.py` exiting with `loop_reachable_seams` equal to an allow-list
(today `_whatif_solve:simulate_wood_slots` and `drift._positive_definite`, both
not applicable). Its cost is one AST pass over the package (1.3 s wall here). Alongside it, add a
steady what-if arm to `tests/replay.py:KERNEL_ARMS` so the dynamic route count covers
`async_simulate`. The arms `D14/s1/p10_kernels.py` lists (base, fallback, sysid,
away, learner) include no what-if.
