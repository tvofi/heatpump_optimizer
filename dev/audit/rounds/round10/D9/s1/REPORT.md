# D9-s1 — round 10, baseline 17f1c55fad1b, step D9.M1

Cells: `**` x M1 x {sse_per_gradient, solves_per_cycle, gil_hold, loop_thread_work}.
Machine: Darwin arm64 (audit box B1), heavily loaded (load1 16-28 during every run);
every wall/CPU number below is provisional. Exposure: none (no docs/, no GitHub).

## Harnesses
- `sse_grad.py` — SSE per gradient by phase, hooks `ThermalModel.simulate_step`,
  `ThermalModel.simulate_trajectory_batch` (rows), `optimizer._batch_fd_gradient`,
  `optimizer._scoped_minimize`, scipy `approx_derivative`. `--perturb fuse`.
- `cycle.py` — `_multi_start_minimize` entries per `_async_update_data` cycle, split
  by the `_await_process` job and its caller; loop-thread `thread_time` minus offloaded jobs.
- `gil.py` — 1 ms heartbeat on a real asyncio loop, solve in a `ThreadPoolExecutor`;
  `idle` null control; `--perturb noyield|realsleep|contyield`.

## Findings
### D9-s1-01 (medium, bug, N-solve-recompute) — the two-zone continuation pays 3 simulations per gradient
`_optimize_space_only.move_starts` (optimizer.py ~4318) runs L-BFGS-B with
`jac=lambda x: _batch_fd_gradient(objective_batch, (), x, float(objective(x)), ...)` and
the scalar `objective` as `fun`. Per gradient that is 96 batch rows + one scalar
horizon in the jac (`f0`) + one scalar horizon in scipy's `fun` call at the same
point = 288 SSE, against 97 for the fused `_fused_value_and_gradient` the main loop uses.
Measured (exact counts): cont sse_per_grad 192 inside the jac plus 96/grad in `cont_fun`
(44 grads -> 4224 SSE) on winter_two_zone_no_dhw. Perturbation `--perturb fuse`
(fused value+gradient, jac=True): cont sse_per_grad 192 -> 97, `cont_fun` -> 0, main
grads unchanged (489, iterate path unchanged), total SSE 62121 -> 53717.
Grid (two-zone, no DHW; total-SSE share removed by the fuse): winter_typical/cold 13.5 %,
winter_extreme/cold 31.1 %, shoulder 25.9 %, winter_typical/mild 18.3 %,
summer_typical/cool 25.4 %, flat/cold 29.2 % (null control: price-independent, as a
mechanical cost should be). Range 13.5-31.1 %; dropping the largest cell 13.5-29.2 %.
CPU of the continuation (provisional, load1 ~20-26): 314->204, 1094->750, 611->418,
554->301, 353->205, 985->574 ms. Pi: assume 3-5x slower per core (assumption) -> 0.3-1.3 s
of extra CPU per two-zone no-DHW solve. Reaches only two-zone installs with DHW off
(DHW solves skip the continuation: cont grads 0 on every DHW scenario).
Property: every `_scoped_minimize` call in a solve whose `jac` is a callable rather than
`True` pays a separate scalar `fun`; seam rule `grep -n "jac=(lambda\|jac=lambda" custom_components/heatpump_optimizer/*.py`.

### D9-s1-02 (low, bug, P10, provisional) — `_gil_yield`'s `sleep(0)` does not bound the in-process hold
On the #511 fallback path (solve on an executor thread) the loop heartbeat's max gap
on two-zone solves is 87-124 ms with starvation share 0.70-0.89, against the idle null
control 14-21 ms / 0.08-0.17 in the same session. `--perturb noyield` barely moves it
(winter_two_zone_dhw 69 -> 57 ms; starvation 0.715 -> 0.709), so the per-evaluation
`sleep(0)` is not acting as a handoff; `--perturb realsleep` (0.1 ms sleep) drops the
max gap 124 -> 29 ms and 87 -> 32 ms. All wall numbers taken at load1 16-28: must be
re-taken quiet. The shipped path runs the solve in a worker process, so this binds
only when the worker is unusable.

## Non-findings
- Main multi-start gradient: 97.00 SSE/grad, 0 scalar steps, on winter_two_zone_dhw,
  winter_single_dhw, winter_two_zone_no_dhw, winter_single_no_dhw, fuse_guard (zero-range/
  capped bounds), shoulder_two_zone, tariff_plus_two_zone; no scipy `approx_derivative`
  call in any of them (`sse_grad.py`).
- Solves per cycle (`cycle.py`, 3 cycles each): all `_multi_start_minimize` entries come
  from `optimize_in_process<-async_run_optimization`; 2/cycle with DHW (space solve +
  the `_co_optimize` re-solve), 1/cycle space-only; no shadow/what-if/diagnose solve in
  a plain cycle of these configs.
- Loop-thread work per cycle: 7.6-12.1 ms thread CPU (0.16-0.25 reference_solve) after
  the first cycle (53.9 ms, imports/warm-up); provisional.

## Unfinished
- gil_hold: quiet-window re-take needed; the contyield arm (continuation without
  `_gil_yield`) was inconclusive under load.
- solves_per_cycle: shadow/what-if (coordinator ~11148) and diagnose paths were not
  triggered by the rig; a cycle that arms them was not built.
- Per-DHW-planning-loop SSE (DhwPlanner / `_co_optimize` inner loops) not split out.
