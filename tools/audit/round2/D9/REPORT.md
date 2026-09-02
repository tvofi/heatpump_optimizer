# D9 — CPU and memory efficiency (Raspberry-Pi-class target), round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree `audit-r2-D9`.
Machine: Apple M1 8-core 8 GB, macOS, Python 3.13.1, numpy 2.5.2, scipy
1.18.1, OpenBLAS, threads pinned to 1 (`thread_factor` 1.000 on every run).
Every harness was run during the fan-out with `load1` between 2.3 and 9.4;
wall, CPU and RSS numbers are therefore **provisional** and carry
`load1`/`thread_factor` on their RESULT block. Counts, bytes and CPU ratios
against `tests/stress.py:reference_solve` are final.

**Pi factor (assumption, stated once, used everywhere):** a Raspberry Pi 4
(Cortex-A72 @ 1.5 GHz) runs CPython/numpy-scalar code about **7× slower**
than this M1 single-threaded (public Geekbench 5 single-core ≈ 230 vs ≈ 1700;
not measured here); a Pi 5 about 3×. Every Pi statement below is "M1 number ×
7 (assumed)".

## Method

One harness per metric under `tools/audit/round2/D9/`, all importing
`d9lib.py` (thread pin before numpy, RESULT printing, `load1`/`swapins`, and
a loader that executes `tests/stress.py` only up to its sweep marker so the
reference solve, `Calibration` and `build_case` are the gate's own, byte for
byte). Each harness monkeypatches the production symbol its metric names,
prints RESULT lines, and moves under a named perturbation; production was
never edited (`git status` shows only `tools/audit/`).

| Metric (brief) | Harness | Hooks | Perturbation |
|---|---|---|---|
| Simulate-step-equivalents per gradient | `h1_grad_equivalents.py` | `ThermalModel.simulate_step`, `simulate_trajectory_batch`, `optimizer._scoped_minimize` (njev/nfev), `_batch_fd_gradient`, `_multi_start_minimize` | horizon 24→48 h; one-entry memo on `simulate_trajectory` |
| … each DHW planning loop | `h1b_dhw_loops.py` | `simulate_dhw_only`, `compute_cop_dhw`, `_build_dhw_requirements`, `_plan_dhw_min_cost`, `_plan_dhw_cheapest_first`, `_apply_dhw_min_run`, `linprog` | horizon 24→48 h |
| Full solves per cycle | `h2_solves_per_cycle.py` | `_multi_start_minimize` (stack-attributed), `HeatPumpOptimizer.optimize` | `price_tiles_enabled`, `main_fuse_amperes` |
| Longest GIL hold / starvation share | `h3_gil_hold.py` | `HeatPumpOptimizer.optimize` in a `ThreadPoolExecutor` under a real loop, 1 ms heartbeat, stage attribution | `sys.setswitchinterval` 5→50 ms |
| Loop-thread work per cycle | `h4_loop_thread_work.py` | `_async_update_data` and 23 stage methods, real `run_in_executor` | horizon 24→48 h; price tiles |
| Retained bytes | `h5_retained_bytes.py` | every `vars(coordinator)` attribute, `tracemalloc`, Store stub | N = 12 → 48 cycles (RSS children) |
| Payload bytes | `h6_payload_bytes.py` | `_build_data_dict`, every platform's `async_setup_entry`, `extra_state_attributes` vs `_unrecorded_attributes` | horizon 24→48 h |
| Stress gate detection | `h7_stress_gate.py` | the gate's own 48 combinations + `Calibration`; 2× injected at `HeatPumpOptimizer.optimize` | `STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75` |

Coordinator cycles run on `tests/harness.py:FakeHass` (inline executor) for
counts and bytes, and on a `FakeHass` subclass with a real
`ThreadPoolExecutor` for the loop and GIL metrics; the three network fetches
are replaced by no-ops after the price/weather/irradiance lists are filled
the way `tests/golden.py:_capture_coordinator` fills them; the clock is
frozen with `dt_util.freeze`.

## Findings

### D9-01 (high, bug) — One zero-range bound sends the WHOLE solve to scipy's scalar finite-difference path: 9,222 simulate_step per gradient instead of 297, 1.5–1.6 M steps and 710–750× the reference solve

**Claim.** Any bound with `lo == hi` in the space-heating solve — a manual
pin forced off, or a fuse/capacity cap (`power_caps_extra`) that equals the
DHW run power at a step hot water is planned in — makes
`_bounds_supported_by_batch` return False, so every gradient of every
L-BFGS-B run in that solve is scipy's own 2-point estimate: n+1 scalar
trajectories per gradient.

**Numbers (h1, counts final).**

| case | path | njev | simulate_step | batch rows | equiv/gradient | CPU (M1, provisional) | ×reference |
|---|---|---|---|---|---|---|---|
| two_zone_dhw (default) | batched | 103 | 20,736 | 9,888 | **297** | 908 ms | 38.5 |
| pin_zero_range (1z, no DHW, step 40 pinned off) | scalar | 11 | 102,240 | 0 | **9,295** | 923 ms | 39.1 |
| pin_zero_range_two_zone_dhw (same pin, default solve) | scalar | 173 | **1,595,328** | 0 | **9,222** | 25,046 ms | **751** |
| dhw_cap_zero_range (cap = 0.8·p_max every step) | scalar | 164 | **1,512,384** | 0 | 9,222 | 17.7–23.7 s | **711–750** |
| golden `fuse_guard` fixture (cap = 0.6·p_max) | scalar | 81 | 731,904 | 0 | 9,036 | 8,164 ms | — |
| dhw_cap_one_step_zero_range (cap at ONE step) | batched | 160 | 31,680 | 15,360 | 294 | 1,824 ms | 54.7 |

The last row bounds the claim: a cap at a single step is dodged when the DHW
plan does not land there; a uniform cap (the fuse guard, whose cap is
`fuse_kw − baseline_house_load` — one value per step) or a pin is not.

**Perturbation.** Remove the pin (`space_pins=None`) / the cap: the same
solve returns to 297 equivalents per gradient (h1 `two_zone_dhw` vs
`pin_zero_range_two_zone_dhw`, direction down, ×31).

**Consequence.** On the batched path a two-zone DHW solve is 0.9 s of M1 CPU
(≈ 6 s on a Pi 4, assumed ×7). With one pin or a binding fuse cap it is
18–25 s on the M1 (≈ 2–3 min on a Pi 4), every 30 minutes, with the event
loop starved for its whole duration (h3: starvation share 0.998, loop at
68 Hz, see D9-05). The manual-plan card is a shipped feature and the fuse
guard is a shipped option; the integration's own golden `fuse_guard`
fixture is on this path.

**Mechanism.** `optimizer.py:_bounds_supported_by_batch` returns False for
any `lo >= hi`; `_multi_start_minimize` then passes `jac=None` and scipy
estimates the gradient with n scalar `objective` calls. The docstring's
reason is a 0/0 NaN at a fixed variable; scipy's own path only survives by
an ULP nudge. `solve_space` produces the (0, 0) bound whenever
`headroom = min(p_max − dhw, caps_extra − dhw) == 0`, and
`_apply_pins_to_bounds` produces it for every forced-off pin.

**Fix scope.** `optimizer.py` `_bounds_supported_by_batch` /
`_batch_fd_gradient`: a fixed variable (lo == hi) has no free direction — set
its step to 0 and its gradient entry to 0.0 explicitly (no 0/0), keep the
batch for the rest; or drop fixed variables from the L-BFGS-B problem. Expected
golden drift: `fuse_guard` (its iterates currently come from the ULP-nudged
scalar path; a fixed variable's gradient entry is projected away by
L-BFGS-B, so drift is last-decimal at most, possibly none).

### D9-02 (medium, bug) — The stress gate as shipped cannot see a 2× (or 4×) uniform solve regression: budgets sit 4.7× (per scenario) and 8.9× (sweep) above what the tree costs, and CI sets no override

**Numbers (h7, CPU ratios against the gate's own reference solve, final).**
48 combinations, gate defaults `STRESS_SOLVE_RATIO=1400`,
`STRESS_SWEEP_RATIO=450`.

| sweep | worst scenario | worst ratio | median | sweep ratio | per-scenario tripped | sweep tripped |
|---|---|---|---|---|---|---|
| plain | shoulder/tariff+pv+cycle | 298.8 | 33.9 | 50.7 | 0 | 0 |
| `optimize` doubled (exact 2× injected) | same | 590.5 | 72.6 | 105.2 | 0 | 0 |

`smallest_detectable_uniform_regression = 4.69` (1400/298.8); the sweep check
needs 8.87×. `ci_sets_stress_ratio = 0` (grep of `.github/workflows/tests.yml`
and `tests/run.sh` for a non-comment `STRESS_SOLVE_RATIO`/`STRESS_SWEEP_RATIO`
assignment) — CI runs these defaults. `tests_memory_instrumentation = 0`
(grep of `tests/*.py` for `tracemalloc|getrusage|ru_maxrss`).

**Perturbation.** `STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75` (between the
plain and injected ratios): plain passes (0/0 tripped), the injected 2×
trips (2 scenarios, sweep 1) — observed on the fan-out box (plain worst
299.5, sweep 52.1; injected 492.9, 106.9).

**Leave-one-out (48 cells).** Per-scenario ratios 0.9 … 298.8; dropping the
most favourable cell (the worst scenario) leaves 267.7 (shoulder/tariff+pv)
and a headroom of 5.2×. All 48 combinations are on the batched jac path
(289–720 equivalents/gradient; the dearest has 786 gradients, not a
different path).

**Mechanism.** The budgets were sized when the dearest scenarios cost
655–662× (the docstring at `tests/stress.py:165` still says so); the batched
jac (D9-01 of the previous round) made every combination 10–20× cheaper and
the budgets were not re-sized. What the gate covers: the optimizer's CPU
per solve, a wall ceiling for hangs. What it cannot see: anything below a
4.7× uniform regression, any memory growth, anything in the coordinator
cycle, the event loop or the entity payloads.

**Fix scope.** `tests/stress.py`: re-size `SOLVE_BUDGET_RATIO`/`SWEEP_BUDGET_RATIO`
from the printed run figures (≈ 600 / ≈ 100 leaves 2×), add a memory line
(`ru_maxrss` before/after the sweep, or tracemalloc peak per solve) and print
its figure so it accumulates as the ratios do. No golden drift.

### D9-03 (low, bug) — The batched jac re-evaluates f(x) that scipy just computed at the same x: 2n scalar simulate_steps per gradient where n would do

**Numbers (h1, counts final).** `two_zone_dhw`: `nfev = njev = 103`,
`scalar_steps_per_gradient = 201.3` (= 2n + candidate scoring), batch rows 96
per gradient; the scalar simulation is 25 % of the solve's thread CPU, the
batch 32 %, DHW planning 10 %. Perturbation "one-entry memo on
`ThermalModel.simulate_trajectory`" (stands in for reusing scipy's f(x) as
the jac's f0): scalar steps per gradient 201.3 → **100.7**, equivalents 297 →
197, batch rows unchanged at 96, solve CPU 908 → 789 ms (−13 %, provisional;
the count is final).

**Mechanism.** In `_multi_start_minimize` the jac closure calls
`float(objective(x, *a))` for f0 immediately after scipy's `ScalarFunction`
called `objective(x)` at the same point (L-BFGS-B evaluates fun and jac
together). One scalar trajectory (n `simulate_step`) is wasted per gradient.

**Fix scope.** `optimizer.py:_multi_start_minimize`: wrap `objective` in a
one-entry cache keyed on `x.tobytes()` (and `args`), used by both scipy's fun
and the jac's f0. Bit-identical (same float returned), no golden drift.

### D9-04 (low, bug) — DHW planning is 3.4–3.8× a reference solve per solve and 63 % of a single-zone winter DHW solve; half of it is `_apply_dhw_min_run` re-simulating the tank once per weak slot

**Numbers (h1b, counts final, shares are CPU ratios in one process).** Per
`_build_dhw_requirements` call, winter two-zone: 2 LP solves, 4 greedy passes
(2–4 re-simulations each), 1 min-run pass; **64 `simulate_dhw_only` calls =
6,144 tank steps** and 7,084 `compute_cop_dhw` calls; 2 planning calls per
solve (the `_co_optimize` re-plan). Planner CPU 70–76 ms = 3.4–3.8× the
reference solve; share of the solve: two-zone 0.108, single-zone winter
**0.630**, summer 0.419, shoulder 0.088, heavy_old 0.111. Inside the planner:
min-run rounding 0.43–0.59, LP build + `linprog` 0.25–0.31, greedy 0.03–0.07;
the tank simulation itself (a Python loop over 96 steps with a per-step
`compute_cop_dhw`) is 0.60–0.71.

**Perturbation.** Horizon 24 → 48 h: 118 `simulate_dhw_only` calls and 22,656
tank steps per planning call (×3.7 for ×2 steps), planner 266 ms = 13.5×
reference.

**Leave-one-out (5 cells at n = 96).** planner/reference 1.68 … 3.84, mean
2.91; dropping the most favourable (3.84) leaves 2.68.

**Fix scope.** `optimizer.py:_apply_dhw_min_run`: raise every weak slot in one
pass and simulate once, falling back to per-slot only when the joint
trajectory breaches the ceiling; `thermal_model.py:simulate_dhw_only`: hoist
the per-step attribute lookups. Order-preserving rewrites carry no golden
drift; a joint-raise change alters which slots survive and would drift
DHW fixtures — keep the per-slot decision order if that is unwanted.

### D9-05 (medium, bug) — The solve starves the event loop for its whole duration: the loop turns at 68–74 Hz (p50 gap 13–15 ms) against 780 Hz idle, starvation share 0.97–0.998, and the two 2 ms yields cover 0.5 % of it

**Numbers (h3, wall, provisional; idle heartbeat is the null control).**

| case | wall | ticks/s | gap p50 | gap p99 | longest hold | gaps > 5 ms | starvation share |
|---|---|---|---|---|---|---|---|
| idle control (no solve) | 2000 ms | 779 | 1.28 ms | 1.37 ms | 2.1 ms | 0 | **0** |
| two_zone_dhw (batched) | 795 ms | 74 | 13.3 ms | 35.8 ms | 39.4 ms (in `simulate_trajectory_batch`) | 42 | **0.967** |
| single_zone_dhw | 137 ms | 190 | 1.7 ms | 23.2 ms | 24.0 ms | 6 | 0.748 |
| dhw_cap_zero_range (D9-01 path) | 14.7 s | 68 | 15.1 ms | 16.5 ms | 20.8 ms | 983 | **0.998** |
| perturbation switch interval 50 ms | 868 ms | 59 | 14.2 ms | 62.2 ms | 82.9 ms | 32 | 0.961 |

The longest contiguous hold on the batched path was 39–75 ms across runs,
attributed to the vectorised batch simulation (numpy on 96×97 arrays holds
the GIL between ops). The `sleep(0.002)` yields sit between starts and
between the DHW and space stages: 2 × 2 ms of an 800 ms solve.

**Consequence on a Pi (×7 assumed).** The 13–15 ms loop period is set by the
interpreter's 5 ms switch interval plus one GIL hand-off, and the per-op
hold scales with CPU speed, so expect ~40–100 ms loop periods for 6 s
(batched) or 2–3 min (D9-01 path) every 30 minutes: a laggy but reachable
instance on the default path, and minutes of it on the pinned/capped path.

**Fix scope.** `coordinator.py:async_run_optimization` /
`_solve_snapshot`: run the solve in a process (`ProcessPoolExecutor` or
`loop.run_in_executor` with a one-shot subprocess) so the GIL is not shared —
the snapshot is already a deep copy, so the inputs are picklable by design;
short of that, a `time.sleep(0)` every k objective evaluations only shortens
the holds, not the share. No golden drift.

## Non-findings

- **Full solves per cycle** (h2): default two-zone DHW cycle = **1**
  `optimize` call and 2 `_multi_start_minimize` entries (`solve_space` +
  `_co_optimize`'s re-solve, both "main"); minimal no-DHW = 1 and 1.
  `price_tiles_enabled` (default off) adds exactly one what-if solve per
  cycle (2 → 4 entries, cycle CPU 526 → 1,036 ms); the fuse advisor adds one
  on its weekly cycle only (cycle 1: 4 entries, cycle 2: 2); the card's
  what-if is on demand, rate-limited at 3 s, 1 solve; diagnose runs
  `simulate_step` only (0 solves). `card_what_if.optimize_calls=1`.
- **Loop-thread work per cycle** (h4): 3.1–3.6 ms of loop-thread CPU
  against 666–857 ms in the executor (ratio 0.004–0.005); `_build_data_dict`
  1.3 ms (42 %), `_build_plan_views` 0.5 ms, `_forecast_arrays` 0.4 ms,
  `_solve_snapshot` 0.16 ms. Horizon 48 h: 4.4 ms; price tiles: 3.7 ms. On a
  Pi (×7) ≈ 25 ms per half hour — nothing to fix.
- **Retained bytes** (h5): coordinator collections deep-size 361.8 KB after
  cycle 1, 382.0 KB after 16 (386.2 KB after 24); slope over the second half
  **0.5–0.8 KB/cycle**, almost all `_accuracy` (0.55–0.60 KB/cycle: the
  samples deque filling towards `HISTORY_LENGTH = 672` and `lead_pending`
  capped at 512 — bounded at ~200 KB) and the monthly `_ledger` (0.17
  KB/cycle, `KEEP_MONTHS`-bounded). Every list found is trimmed (`del
  …[:-6]`, `[-20:]`, `[-90:]`, `RING_SIZE`, `KEEP_MONTHS`). tracemalloc with
  the harness's own allocations filtered out: 3.35 KB/cycle traced growth,
  of which the integration's own lines are **1.68 KB/cycle** —
  `coordinator.py:9237` (accuracy samples) 235 B, `accuracy.py:184`
  (lead_pending) 180 B, `coordinator.py:6156` (datetime parsing in
  `_get_current_price`) 288 B, `optimizer.py:145/:509/:497` (threadpoolctl
  scratch) +120/+108/−108 B; the rest is the Store stub's JSON strings
  (0.75 KB) and scipy `array_api` scratch (0.37 KB). `ru_maxrss` from 12 to
  48 cycles moved +1.9 MB, +0.5 MB and −1.6 MB across three runs
  (provisional; noise, no growth). The `:6156` grower was not chased to its
  retainer (288 B/cycle ≈ 14 KB/day at worst).
- **Persistence traffic** (h5): 2.1 Store saves per cycle, 7–10 KB/cycle
  (the accuracy store, 6.6–9.2 KB, is rewritten every cycle; energy 0.2 KB
  every cycle; price model and thermal learning less than daily) →
  ≈ 0.3–0.5 MB/day to `.storage`.
- **Payload bytes** (h6): `_build_data_dict` 155 keys, **52,720 B per cycle**
  (`dhw_plan` 17.4 KB, `space_plan` 17.2 KB, `schedule` 5.6 KB) = 2.5 MB/day
  in memory, never recorded as such. 65 entities, 43 with attributes:
  63,086 B per cycle of which **52,387 B (83 %) are excluded** by
  `_unrecorded_attributes` (both plan sensors' `forecast`/`slots`, the
  schedule sensors' lists); the recorded remainder is 10,699 B per cycle,
  ≤ 514 KB/day (an upper bound: HA de-duplicates identical attribute blobs).
  Largest recorded: PredictiveInsightSensor 1,233 B, ThermalBatterySensor
  894 B, the climate entity 856 B. Horizon 48 h: payload 87,270 B, recorded
  remainder 10,800 B (the exclusion set holds).
- **Gradient path coverage** (h7 survey): all 48 stress combinations run on
  the batched jac, 289–720 equivalents per gradient; single-zone no-DHW
  winter solve 2.7× reference (64 ms), single-zone DHW 6.1×.
- **Thread pin**: `thread_factor` 1.000 ± 0.0002 on every harness.

## What could not be finished

- Quiet-window re-takes of every wall/CPU/RSS number (load1 2.3–9.4 during
  the runs). The CPU ratios and counts do not need them.
- A Pi measurement: the ×7 factor is an assumption from public single-core
  benchmarks, stated as such wherever used.
- The `dhw_cap_one_step` case shows a single capped step can be dodged; the
  exact condition (a DHW block coinciding with a capped step) was not swept
  over cap positions.
- The 288 B/cycle tracemalloc grower at `coordinator.py:6156` was not traced
  to what retains it.

## Harnesses

`tools/audit/round2/D9/d9lib.py` (shared scaffolding), `h1_grad_equivalents.py`,
`h1b_dhw_loops.py`, `h2_solves_per_cycle.py`, `h3_gil_hold.py`,
`h4_loop_thread_work.py`, `h5_retained_bytes.py`, `h6_payload_bytes.py`,
`h7_stress_gate.py`. Each runs from the repository root with
`PYTHONPATH=tests/hastub python <path>`; `h7` takes the perturbation from the
environment (`STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75`). `h5` takes
about five minutes (tracemalloc slows the solve ~15×).

## Exposure

None: no `docs/`, no earlier audit records, no GitHub. Comments in
`optimizer.py` citing `D9-01` and `#97` (the batched jac) were read as
context.
