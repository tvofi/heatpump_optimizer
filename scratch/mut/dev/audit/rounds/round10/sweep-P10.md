# Round 10 class sweep: P10 (model-kernel CPU work on the event loop)

Base: `handoff/audit-r10-register` at `9355f107d`. Class status in `dev/audit/config/bugclasses.json`:
`open`, `detector: null`, `barrier: null` (7 prior instances, R1–R9). The judged finding is D14-s1-01.

## Enumerator

`python3 dev/audit/rounds/round10/D14/sweep-P10/p10_loop_reach.py`, run from the repo root.
It starts from the 35 kernel call sites that `D14/s1/p10_seams.py` lists (`simulate_*`, `numpy.linalg`,
`scipy.optimize`). It walks a static call graph from every `async def` in the package. A function that is
passed to `_await_process`, `_await_off_loop` or `async_add_executor_job` is an argument, not a call,
so every hop off the loop cuts the edge. A call resolves by its receiver: `mod.f` (import aliases
included) goes to that module, and `self.f` or a bare `f` stays in the same file. A call on any other
receiver is left unresolved, which is a known blind spot that the dynamic harness covers.
`--seam FILE:FUNC` turns it into a probe: exit 1 when that seam can be reached from the loop.

Output at base: `RESULT loop_reachable_seams=3`:
- `away.py:estimate_recovery_hours:simulate_step`, reached through `async_run_optimization → _resolve_away → away.resolve → _apply_return`
- `coordinator.py:_replay_interval:simulate_step`, reached from `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss`
- `coordinator.py:async_simulate:simulate_wood_slots`

## Controls

| control | command | result |
|---|---|---|
| positive (re-finds D14-s1-01) | `p10_loop_reach.py --seam away.py:estimate_recovery_hours` | listed, exit 1 |
| positive, dynamic | `p10_seams.py --away` | `loop_kernels_away_seam=183` over 6 cycles |
| null, dynamic | `p10_seams.py --away --deficit 0` | 0 |
| null, clean fixture | a two-file package where the only kernel is reached through `_await_off_loop(hass, work, 1)` | `loop_reachable_seams=0` |
| perturbation, static | copy of the package with one change: `_with_sensor_advisor` calls `topology.rank_sensor_advisor(...)` directly instead of through `_await_off_loop` | 3 → 4: `topology.py:_advisor_replay` appears |
| perturbation, dynamic | `p10_seams.py --perturb` | `loop_kernels_all` 0 → 6967 |

## Dispositions (all 35 seams)

**Instance**
- `away.py:estimate_recovery_hours`: this is the finding site of D14-s1-01. Probes: the two positive controls above.
- `coordinator.py:_replay_interval`: **beyond the finding.** It runs one `ThermalModel.simulate_step` per learner
  per cycle, called synchronously from `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss`,
  with no off-loop hop. Probe: `p10_loop_reach.py --seam coordinator.py:_replay_interval` exits 1.
  `tests/replay.py:kernel_checks` (`KERNEL_ARMS` base/fallback/sysid) cannot see it, because its fixture is
  DHW-only and never reaches the space-heating learners. D14-s1-01's report listed this seam as
  "on the loop, not driven". The sweep counts it as an instance because the loop route is established
  statically. Its cost is bounded: 2 steps per cycle.

**Guarded**
- `optimizer.py` (10 seams) and `dhw_planner.py` (9 seams, `linprog` included): these run inside
  `optimize_in_process` through `_await_process` (coordinator.py:1615). The dynamic harness counts
  `worker_kernels=70` and `loop_kernels=0`. Barrier: `kernel_checks` base/fallback arms.
- `sysid.py` (7 seams): guarded by `_sysid_step_off_loop` → `_await_off_loop`. Barrier: the `sysid` arm of `KERNEL_ARMS`.
- `topology.py:_advisor_replay`: guarded by `_with_sensor_advisor` → `_await_off_loop` (D9-s2-01). The
  static perturbation shows the enumerator would see it if that guard were removed.
- `diagnosis.py:_room_after`: guarded by `async_diagnose_interval` → `_await_process(diagnosis.diagnose_record)`.
- `thermal_model.py` (4 internal seams: `simulate_trajectory`, `simulate_trajectory_with_dhw` ×2,
  `extend_dhw_temps`): these are the kernels' own bodies. They are reached only through the callers above,
  all of which are guarded except the two instances. `extend_dhw_temps` is called only from `dhw_planner`, which runs in the worker.

**Not applicable**
- `coordinator.py:async_simulate:simulate_wood_slots`: `wood_fuel.simulate_wood_slots` parses override slots
  into a kW series and runs no model kernel. The `simulate_` prefix matched its name only.

## Barrier status

No barrier. Proposed barrier, carried from D14-s1-01: add an `away` arm and a space-heating learner arm
to `KERNEL_ARMS` in `tests/replay.py`, or gate on `p10_loop_reach.py` exiting 0. That gate would need an
allow-list until both instances are fixed.
