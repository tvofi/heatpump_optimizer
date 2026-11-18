# Class sweep: N-solve-recompute (round 11, PLAN phase D, box SW2)

Class mechanism (`dev/audit/config/bugclasses.json`): the solve recomputes
interpreter-bound work that is invariant or vectorisable. Ledger status:
`barriered`. The barrier is `tests/stress.py`'s production-call channel
(`SCENARIO_CALLS_GROWTH`). It counts calls inside a scenario solve
(`production_calls(lambda: stress.build_case(...))`), so it sees work added
per iterate. It does not see a solve that a trigger runs again on inputs that
have not changed. The judged finding is that second kind: D9-s1-01, where a
diagnose press runs a full cycle and re-solves the plan to publish an analysis
that needs no solve. This sweep therefore covers that seam family: every call
site in the package that makes the planner solve run.

Worktree: `origin/handoff/audit-r11-register` (92d38ecb6 lineage), with the
judge files from 5806e17d7.

## Enumerator (D14 method step 3)

`python3 dev/audit/rounds/round11/D14/sweep-N-solve-recompute/enumerate.py`
reads the package by AST. It lists every call to `async_request_refresh`,
`async_refresh`, `async_refresh_now`, `async_run_optimization`,
`_await_optimize` or `optimize_in_process`, including one passed as an
argument. Calls inside `_async_update_data` are excluded, because that cycle
is the solve itself. Output: `D14/sweep-N-solve-recompute/enumerate.out`,
**28 seams**.

Controls (`--controls`, output in `controls.out`):

- **positive**: lists the D9-s1-01 site
  (`async_diagnose_interval -> async_request_refresh`), found=1.
- **null**: a clean fixture whose diagnose publishes through
  `_build_data_dict` + `async_update_listeners` gives seams=0.
- **perturbation**: one added line `await self.async_request_refresh()` moves
  the count 0 -> 1.

### Probe

`probe.py TRIGGER` runs a coordinator on the D9-s1 rig (two-zone + DHW house).
It runs three warm cycles, then a reference cycle at a frozen instant, then
the trigger. It hooks `optimizer._multi_start_minimize` and records every
result vector.

- The trigger is a **recompute** (rc=1) when it enters the solver and every
  solve it buys reproduces a solve whose result is already in hand, within
  `TOL = 1e-2` on a vector of scale 6.
- `TOL` was set from measurement. Two solves of identical inputs differ by at
  most 6.04e-4 (warm start). An input change (the away switch) moves the
  vector by 6.
- The stub's debouncer, under a frozen clock, would hold a second request
  forever. The probe therefore runs each request as one cycle, which is what
  Home Assistant's debouncer does at the end of its cooldown.

Probe output (`probe.out`):

| arm | solves | reproduced | rc |
|---|---|---|---|
| refresh (comparator self-check: same inputs) | 2 | 2 | 1 |
| away (input change, power control) | 1 | 0 | 0 |
| diagnose (D9-s1-01) | 2 | 2 | **1** |
| diagnose `--perturb` (publish without cycle) | 0 | 0 | 0 |
| force_button (refresh vs the press's own solve) | 2+2 | 2 | **1** |
| boost_dhw | 2 | 2 | **1** |
| block_space | 2 | 2 | **1** |
| boost_dhw `--perturb` | 0 | 0 | 0 |

## Disposition of every seam (method step 4)

| seam | disposition |
|---|---|
| coordinator.py:10686 `async_diagnose_interval` | **instance**, the D9-s1-01 site; probe `diagnose` rc=1. Reached from button.py:217 and services.py:1272. |
| button.py:110 `ForceOptimizationButton.async_press` | **instance**, beyond the finding. :109 already runs `async_run_optimization`; the trailing `async_request_refresh` runs the cycle again, and its solve reproduces the press's own solve (2 of 2). One press costs twice the solves it needs. Probe `force_button` rc=1. |
| entity.py:339 `publish_then_refresh._refresh`, as reached from switch.py:188 `TimedDutySwitch._press` (Boost DHW/Space, Block DHW/Space) | **instance**, beyond the finding. The boost/block hold is read only after the solve (`boost.apply` overlay, actuation). The refresh's solve reproduces the unchanged plan (2 of 2), so the cycle tail was the only part needed. Probes `boost_dhw` and `block_space` rc=1; `--perturb` gives 0 solves. For the other callers of the same seam (climate/switch mode, away switches, away return datetime) it is **guarded**: each changes a solve input first. |
| button.py:109 `ForceOptimizationButton.async_press` -> `async_run_optimization` | not applicable: the solve is the press's purpose (the instance is :110). |
| services.py:604 `handle_run_optimization` | not applicable: one solve, which is the service's purpose; no trailing refresh. |
| __init__.py:355 first solve | not applicable: no plan exists yet. |
| boost.py:681 `set_channel`, boost.py:696 `set_block` (`refresh=True` branch) | not applicable as their own seams: no caller in the package passes `refresh=True`. The path that is reached is entity.py:339 above. |
| button.py:175 ResetComfortWeight, button.py:192 ResetHeatLoss, services.py:1194 | **guarded**: a learned parameter that the solve reads is reset before the refresh. |
| coordinator.py:1449 adopt refit, :9760 restore snapshot, :11049 arm sysid, :6541 set_mode, :6592 thermal params, :9921 set_away, :8583/:8609 manual plan | **guarded**: each writes a solve input (learned params, sysid override, mode, options, away override, manual plan) before the refresh; the away arm shows the plan moves (distance 6). |
| coordinator.py:3590 away-input watch, :3592 `InputReturnWatch` | **guarded**: they fire on an input state change. |
| coordinator.py:6430 the cycle's own solve | **guarded** for per-iterate work by `tests/stress.py`'s production-call channel (`SCENARIO_CALLS_GROWTH` 5 %). |
| coordinator.py:6524 #1754 re-run | **guarded**: it runs only when a request arrived while a solve was in flight (`_optimization_rerun_requested`), and that solve did not see the request. |
| coordinator.py:2319, :2337 `_await_optimize` | not applicable: these implement the solve; they do not trigger it. |
| coordinator.py:7203 `_fetch_solar_forecast` | not applicable: `OpenMeteoSolar.async_refresh`, a forecast fetch, not the coordinator. |
| coordinator.py:11239, :11245 `async_simulate` | not applicable: the what-if's answer is the solve. |

**Count: 3 instances: 1 judged site and 2 beyond the finding.**

Caveat, the same one D9-s1-01 carries: the probe presses at the instant of
the last cycle. In practice a press comes minutes later, so its solve also
moves the plan forward to the press time. The timer cycle would buy that same
step at its next tick, so the press's solve is still work the press does not
need.

## Proposed barrier

The existing barrier is per-solve, and it cannot see the trigger seam. The
proposal is a static `tests/` arm built on this enumerator. Every call site
that triggers a solve outside `_async_update_data` must be on a reasoned list
naming the solve input it changes, or one of the not-applicable reasons above.
A new or unlisted refresh after an action that changes no input fails the arm.

- **Cost**: an AST pass over the package, under 1 s.
- **The fix it gates**: a publish-only path that runs the cycle tail without
  the solve. D9-s1-01's perturbation already demonstrates that path:
  `_build_data_dict` + `async_update_listeners`, plus `boost.apply` and
  actuation for the boost switches. Force Optimization would drop the
  trailing refresh or replace it with that publish-only path.
