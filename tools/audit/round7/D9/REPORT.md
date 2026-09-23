# D9 — CPU and memory efficiency, round 7

Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave fully
merged), measured in `/Users/timmalmstrom/audit-r7-D9` with
`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` and
`PYTHONPATH=tests/hastub`, always from that root. Box: 8-core Apple M1, 8 GB,
shared with other finders (`load1` between 3.1 and 4.3 on every run, quoted in
each RESULT block).

`exposure`: none — no `docs/`, no GitHub, no earlier round's findings were read.
The only tree text I read that cites earlier findings is the `D<k>-nn` / `#NNN`
prose inside production and test comments (e.g. `optimizer.py`'s D9-01 notes),
which COMMON.md classifies as context, not a to-do.

## Method

Three metrics, one harness each, all under `tools/audit/round7/D9/`. Every
harness pins BLAS threads to one before importing numpy, prints `thread_factor`,
`load1` and `swapins`, hooks a named production symbol, and was re-run under a
named perturbation whose direction is stated.

| harness | metric | ruler |
|---|---|---|
| `payload_bytes.py` | recorder attribute bytes per cycle | bytes (final) |
| `polish_cost.py` | share of the solve spent in the per-candidate polish | `stress.py:reference_solve` CPU |
| `gradient_cost.py` | simulate-step-equivalents and their two committed definitions | `stress.py:SolverWork` plus its own counters |

Counts and bytes are the final half of every number here; each CPU or wall figure
is **provisional** (fan-out box) and is reported as a ratio against
`tests/stress.py:reference_solve`, the ruler the gate itself uses.

One trap cost time and is worth recording: my first version of
`gradient_cost.py` patched `ThermalModel.simulate_step` before `import stress`,
which is silently useless — `stress.SolverWork` captures those four symbols into
class attributes at import and its `__enter__` puts them back over anything
patched afterwards. The counters read 0 while `_batch_fd_gradient` counted 442
gradients. The fix is to rebind `SolverWork`'s own leaves (`_step_wrapped`,
`_dhw_step_wrapped`, `_batch_wrapped`), which puts both instruments on the same
call path so their numbers cannot disagree.

## Findings

### D9-01 — a third of the recorder payload is series-shaped or byte-identical on repeat

`payload_bytes.py`, shipped arm:

```
RESULT entities=64 count
RESULT cycles_per_day=48 count
RESULT recorded_bytes_per_cycle=9512 bytes
RESULT excluded_bytes_per_cycle=15026 bytes
RESULT duplicated_attribute_bytes_per_cycle=1684 bytes
RESULT duplicated_attribute_pairs=23 count
RESULT recorded_bytes_per_day=456576 bytes
RESULT recorded_bytes_per_entity_min=2 bytes
RESULT recorded_bytes_per_entity_max=1097 bytes (PredictiveInsightSensor)
RESULT recorded_bytes_per_cycle_drop_largest=8415 bytes
```

3,437 of the 9,512 bytes written per cycle (36.1 %) is either a series the
project's own plan sensors declare unrecorded (`dhw_usage_profile` 481 B on
`PredictiveInsightSensor`, `components` 470 B on `ThermalBatterySensor`,
`candidates` 504 B on `DHWSetpointAdvisorSensor`, `gaps` 298 B on
`SensorGapAdvisorSensor` = 1,753 B) or a byte-identical repeat of a `(key, value)`
published by another entity in the same cycle (1,684 B over 23 pairs — `period`
and `split_method` ride unchanged on all six accumulating energy/cost sensors).
The plan sensors already exclude 15,026 B/cycle by the same rule, which is what
makes the inconsistency the finding rather than the taste.

Perturbation `--exclude dhw_usage_profile` (the one-line production edit: the key
added to that entity's `unrecorded_attributes`): recorded drops 9,512 → 9,008 B.
Null control `--exclude nosuchkey`: byte-identical at 9,512 B, so the harness is
counting the payload and not its own edit.

### D9-02 — the per-candidate polish is 35 % of every solve's CPU and 37 % of its gradients

`polish_cost.py`, shipped arm (winter/2z/dhw, the default two-zone DHW shape):

```
RESULT polish_calls=4 count
RESULT polish_gradients=164 count
RESULT main_gradients=278 count
RESULT polish_gradient_share=0.3710 fraction
RESULT polish_cpu_ms=762.1 ms
RESULT solve_cpu_ms=2170.4 ms
RESULT polish_cpu_share=0.3511 fraction
RESULT polish_cpu_ratio=40.216 reference_solves
RESULT solve_cpu_ratio=114.5 reference_solves
```

Perturbation `--no-polish` (the one-line production edit `return best` at the top
of `_lbfgsb_restart`): polish gradients 164 → 0, solve CPU 2,170.4 → 1,415.3 ms —
a 755.1 ms (34.8 %) fall — and the gradient count falls 442 → 278, the same 164.
Null control `--dhw-free` (the space-only shape, a different candidate set and no
DHW stage): polish share 0.3580 of CPU and 0.3595 of gradients, so the cost is
the polish's and not the DHW planner's (`_build_dhw_requirements` measured 93.3 ms,
4.3 %, under the same instrument).

The code's own cost model is "it costs one short L-BFGS-B run per candidate, not
a second solve" (`optimizer.py:620-625`). Measured: four polish runs cost 35 % of
a solve, and at 41 gradients each against the main runs' ~70 they are not short —
they are 59 % of a run, eight L-BFGS-B runs where four would do.

### D9-03 — the shape family the sweep documents as leaving the batched jac still batches, and the work channel cannot tell the two paths apart

`gradient_cost.py`, three arms of the same solve:

| arm | batched gradients | work (steps) | kernel CPU ms | solve CPU ms | scipy evals |
|---|---|---|---|---|---|
| shipped | 442 | 4,128,216 | 1,238.1 | 2,233.9 | 884 |
| `--zero-range` (cap 3.0 kW) | **316** | 2,949,058 | n/a | 1,599.9 | n/a |
| `--scalar` | **0** | 4,128,984 | 29,807.9 | 35,940.1 | 43,316 |

`tests/stress.py:1052-1058`, in `build_case`'s own docstring, tells a reader that
both zero-range channels — `power_cap_kw` and `pin_off_steps` — "take the whole
solve off the batched jacobian" so that "scipy estimates every gradient with n
scalar objective calls instead of three batched ones". Measured on the fuse-cap
shape the same builder produces: **316** batched gradients, not 0. The carve-out
that sentence describes was removed by D9-01 (the fixed-variable NaN was moved
into `_batch_fd_gradient`), and the sweep's cap and pin scenarios now sample the
*batched* path on both sides of that change. Perturbation `--scalar` (the
one-line production edit `can_batch = False`): 316 → 0, the direction the
docstring predicts for the shipped code and the opposite of what ships.

The second half is why that matters. The same edit moves the gate's own work
channel — `stress.SolverWork.simulate_steps`, the #1229 channel the
single-scenario work rule budgets — by **+0.019 %** (4,128,216 → 4,128,984),
while the solve's CPU moves 16.1x and its physics-kernel CPU 24.1x. A batch is
charged at `rows x steps`, so replacing 96 scalar trajectories with one 96-row
batch records the same work for the same solve; and the D9 brief's own definition
of the same quantity ("scalar `simulate_step` calls + rows of
`simulate_trajectory_batch`") records 42,432 rows batched against 4,117,920
scalar steps — 97x, for the same edit. The two committed definitions disagree by
a factor of 96, in opposite directions, so a fixer who reads one sees a 97x win
where the other sees 0.02 %. The gate as a whole is not blind — its `kernel_ms`
(24.1x) and evaluation (49.0x) channels both move — which is why this is `low`
and not higher.

## Non-findings

| checked | command | value |
|---|---|---|
| One cycle's loop-thread CPU (solve is off the loop) | `cycle_solves.py --cycles 2` | 2.6 ms/cycle = 0.135 reference solves; the solve ran in the process worker (2,647 ms wall/cycle) |
| Full solves per cycle, all features on | `cycle_solves.py --cycles 2` | 1 job/cycle, submitted by `async_run_optimization` |
| The DHW planning loops are not the cost | `polish_cost.py` probe of `_build_dhw_requirements` | 93.3 ms of a 2,174 ms solve (4.3 %) |
| The batched jac buys CPU, not work | `gradient_cost.py` vs `--scalar` | 16.1x CPU at +0.019 % step-equivalents — both are the documented design |
| The scalar objective evaluation per gradient is not waste | `gradient_cost.py` step_callsites | 43,392 of 43,680 scalar steps are scipy's own `_update_fun` at the iterate; one per iteration is inherent to L-BFGS-B |
| Zero-range bounds are served by the batch and converge | `gradient_cost.py --zero-range` | `status='optimal'`, 316 batched gradients, 1,599.9 ms |
| Retained coordinator payload is small | `payload_bytes.py` | `_build_data_dict()` = 9,412 B JSON over 162 keys |

## Harnesses

- `tools/audit/round7/D9/payload_bytes.py`
- `tools/audit/round7/D9/polish_cost.py`
- `tools/audit/round7/D9/gradient_cost.py`
- `tools/audit/round7/D9/cycle_solves.py` (non-findings only: its
  `optimize_in_process` wrapper is unpicklable and poisons the process worker, so
  the run falls back to the in-process solve and the integration's own warning
  says so)

## What I could not finish

- The longest contiguous GIL hold and the starvation share (the brief's metric
  3). It needs a real `ThreadPoolExecutor` with the solve submitted the way
  production submits it, and the shipped route puts the solve in another
  *interpreter*, where the hold is zero by construction; the fallback route is
  what `tools/audit/harnesses/j5_gil.py` already measures. I did not re-run it in
  this round's window, so I make no claim about a residual hold.
- Whether the stress memory budgets (`rss_peak_mb`, `traced_peak_mb`) are
  enforced, i.e. the brief's last question. The detection arithmetic is present
  and detailed; confirming it needs a sweep, which this fan-out box must not run.
