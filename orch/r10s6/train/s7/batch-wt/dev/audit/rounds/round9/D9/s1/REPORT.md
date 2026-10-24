# Round 9, D9, seat D9-s1: CPU and memory in the solver cells

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Cells: D9.M1 over
`optimizer.py`, `thermal_model.py`, `sysid.py`, `process_worker.py`,
`defrost.py` and `flow_lift.py`. Machine: an x86_64 cloud container with 4 CPUs
(box B4), CPython 3.14.0rc2, numpy 2.4.6 and scipy 1.17.1, with BLAS pinned to
one thread. Every harness runs from the repository root as
`PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D9/s1/<h>.py`.
Each harness imports `_common.py` first, which pins the BLAS threads before
numpy is imported.

Status of the numbers:

- **Final:** counts, bytes, bit-parity results and plan hashes.
- **Provisional:** every CPU, wall and RSS number. They were taken during the
  fan-out, at load1 between 1.3 and 2.9 with no `stress.py` or `run.sh`
  running, and need a re-take in the quiet window.

Pi extrapolations assume that one Pi-4 core is 4 to 6 times slower than one
core of this box for Python and numpy dispatch. That factor is an assumption,
not a measurement.

**Exposure: none.** At start-up one directory listing showed the file names
under `tools/audit/round8/D9/`. None of those files was opened or cited.

## Method

Every "share of a solve" figure divides thread CPU inside a hooked production
symbol by the thread CPU of the `optimize()` call made by
`tests/stress.py:build_case`. The ruler is `reference_solve`. The harnesses
hook symbols by attribute swap, and they chain under `stress.SolverWork`'s
meters, because `build_case` re-binds `optimizer._scoped_minimize` and the
simulate seams.

## Findings

### D9-s1-01 (medium): per-row loop in `_comfort_terms_batch`

Harness: `comfort_rowloop.py`.

The per-row Python loop in `HeatPumpOptimizer._comfort_terms_batch` takes
0.134 to 0.321 of solve CPU. On every two-zone cell it takes 0.32.

- **Leave-one-out:** 7 cells, mean 0.262. With the most favourable cell
  dropped, the mean is 0.252.
- **Null control:** at flat prices the share is 0.3195, so the cost is built
  into the objective and does not depend on the price shape.
- **Alternative tested:** a twin does the same elementwise operations on the
  whole `[B, n]` batch and reduces with `axis=1`. It gave **0 bit-mismatched
  values** over about 240k rows and **identical plan hashes in 8 of 8
  cells**, at a share of 0.012 to 0.039.
- **Back-to-back timing on the two-zone winter cell:** solve CPU went from
  4.47 s and 4.86 s down to 3.30 s and 3.25 s.
- **Why the loop exists:** the method's docstring keeps it for bit parity
  across backends, and names x86_64 CI as the place where a batched
  reduction once differed. This box is also x86_64. The fix still has to
  prove parity on CI's x86_64 and arm64 runners.

### D9-s1-02 (medium): scalar objective evaluated on every iterate

Harness: `scalar_objective.py`.

`_multi_start_minimize` gives scipy a scalar objective and a batched jac as
separate functions. As a result, every L-BFGS-B iterate evaluates the scalar
objective once, at 1.0 to 1.6 ms. That is 18.6 to 25.9 times the cost of one
batched row, and adds up to 0.087 to 0.192 of solve CPU.

- **Leave-one-out:** 6 cells, mean 0.156. With the most favourable cell
  dropped, the mean is 0.149.
- **Null control:** at flat prices the share is 0.156.
- **Perturbation `--fused`:** f(x) is served from an extra row 0 of the same
  batch, with `jac=True`. The share falls to 0.005 to 0.018, and the plan
  hashes stay identical in 7 of 7 cells. Row 0 matched the scalar objective
  bit for bit on 2,493 calls (0 mismatches). Solve CPU fell 14 to 22 %.
- **Negative arm, recorded:** `--via-batch` evaluates each scalar call as a
  one-row batch. The share went up, from 0.15 to 0.31, because the batch
  kernel has a fixed overhead per call.

### D9-s1-03 (low): the sysid fit runs on the event loop

Harness: `sysid_loop.py`.

The coordinator calls `SystemIdentification.step` on the event loop. The call
that ends the relax phase runs the whole `identify_slab` fit inside that one
call:

| Cadence | Worst `step()` call | Multiple of `reference_solve` |
|---|---|---|
| 30 min (default) | 43 ms | 1.14x |
| 15 min | 95 ms | 2.46x |
| 5 min | 228 ms | 5.95x |

Every other `step()` call costs 0.17 ms, and stubbing out the fit
(`--no-fit`) brings the worst call down to that as well. The fit happens at
most once every 30 days, which is why this is rated low.

### D9-s1-04 (low): DHW min-run repair re-simulates the whole suffix

Harness: `dhw_min_run.py`.

On the single-zone DHW winter cell, `_apply_dhw_min_run` makes 7,758 of the
solve's 11,064 `simulate_dhw_step` calls. That is 0.17 to 0.23 of solve CPU
on four single-zone cells.

- **Where the calls go:** 42 of the 52 weak slots are refused. Each refused
  slot costs two full-suffix re-simulations, although the refusal is already
  decided at the first step that breaches.
- **Perturbation `--early-exit`:** checking in chunks and stopping at the
  first breach cuts the calls by 26 to 40 % (7,758 down to 4,780). The plans
  are bit-identical in 6 of 6 cells.
- **Horizon:** at 48 h the call count is 25,313, which is 3.26 times the 24 h
  count for twice the horizon.

## Non-findings (the checks held)

- **Gradient cost:** every gradient costs 96 batch rows and 0 scalar steps on
  all six bound shapes, including both zero-range shapes. Across the shapes
  that is 0 scalar-FD gradients. The `--no-batch` arm raises the cost to 8,928
  scalar steps per gradient (`grad_steps.py`).
- **Solves per `optimize()`:** one multi-start entry with 4 candidates. The
  `_co_optimize` re-solve takes 1 candidate, runs only when space heating is
  pinned against the DHW plan, and costs 0.127 of the solve where it runs
  (`solves_per_cycle.py`).
- **GIL starvation in the in-process fallback solve:** on a real asyncio loop
  with a `ThreadPoolExecutor`, the heartbeat's median gap is 8.5 ms and the
  largest gap is 28 to 48 ms. The starvation share is 0.91 to 0.94. With
  `_gil_yield` removed, the largest gap is 122 ms. This is not filed as a
  finding: the coordinator treats this route as its accepted degraded path
  and caps it with `WORKER_FALLBACK_CAP` (`gil_hold.py`). The harness's
  residual `thread_factor` is 1.058.
- **Solve worker memory:** no leak. RSS settles at about 101 to 102 MB, and
  over jobs 40 to 80 it grows 4.6 kB per solve; a synthetic 1 MiB leak shows
  as 912.6 kB per solve. The IPC payload is 10,120 bytes for the job and
  16,546 bytes for the reply. Respawning the worker for every solve would
  cost about 416 ms of CPU here (`worker_rss.py`).
- **Other DHW planner loops are cheap:** each takes at most 0.124 of the
  solve, and none gets near its iteration bound (`dhw_loops.py`).
- **`get_current_action`** costs 10 to 18 µs (`loop_action.py`).
- **Defrost and flow-lift payloads stay bounded:** the defrost summary is
  about 1.65 kB for 12 rows, and the flow-bias store is 36 bytes
  (`learner_payload.py`).

## Harnesses

`_common.py` (shared plumbing), `grad_steps.py`, `comfort_rowloop.py`,
`scalar_objective.py`, `gil_hold.py`, `dhw_loops.py`, `dhw_min_run.py`,
`solves_per_cycle.py`, `sysid_loop.py`, `worker_rss.py`, `loop_action.py`,
`learner_payload.py`. Each harness's header states its metric, its command,
its perturbation and the key it counts on. Every harness resolves the
repository root from the working directory (`tests/`, `tests/hastub` and
`custom_components` relative to the cwd), so run them from the tree under
test.

## Not finished (D9.M1)

- The per-row loop in `_terminal_cost_batch`: estimated at about 3 % of a
  solve from a profile only, with no harness.
- The per-step `dataclasses.replace` in the scalar `simulate_step`: not
  harnessed separately; the D9-s1-02 fix would absorb it.
- The two-zone plant variant of the sysid fit.
- The quiet-window re-take of every provisional number.

## Leads (for D9-s2, which owns `coordinator.py`)

- The call site of D9-s1-03: `_run_system_identification`.
- A count of full solves per coordinator cycle, including the fuse-advisor
  what-if.
- The loop-thread cost of `_solve_snapshot`.
- The in-process fallback policy.
