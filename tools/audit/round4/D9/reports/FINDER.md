# D9 — CPU and memory efficiency (Raspberry-Pi-class target), round 4

- **Baseline**: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- **Tree**: `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-D9` (isolated worktree, instrumentation permitted)
- **Machine**: 8-core Apple M1, 8 GB, macOS 25.6, python 3.11.5, numpy 2.4.6
- **Interpreter**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, always `PYTHONPATH=tests/hastub`, always from the worktree root
- **Wave**: 2. D4 (Chromium) and D8 (entity matrices) shared the box. `load1` ran
  2.4–6.2 throughout; the concurrent gate-process count
  (`ps aux | grep -E "[s]tress\.py|[t]ests/run\.sh"`) was **0 or 1** beside every
  timing RESULT and is printed by every harness as `concurrent_gate_procs`.
- **Thread pin**: every harness sets the five BLAS variables to `1` before numpy
  is importable. Measured `thread_factor` was **0.99999–1.009** in every timed
  arm; none exceeded 1.05, so no RESULT was rejected on that ground.
- **Gate lock**: `tests/stress.py` was never *run*; it was **imported** (its
  `__main__` guard means an import runs no sweep) for `reference_solve()`,
  `build_case()`, `sweep_combinations()` and the budget constants. `stress.py`'s
  `reference_solve` is the ruler for every "share of a solve". No lock was taken
  because no sweep and no `run.sh` ran; `closure.py select` was not invoked.
- **Exposure**: none. No `gh`, no GitHub, no `docs/audit-*.md`, no
  `docs/backlog.md`, no `docs/plan-*.md`, no `tools/audit/round3/` (removed from
  this tree before the round). `docs/` was not read at all.

## What the shipped route turned out to be

The single most load-bearing fact for this dimension, and it changes what is
worth measuring: **the solve does not run in the Home Assistant process.**
`coordinator._await_optimize` pickles `optimize_in_process` through
`coordinator._run_in_process` to a persistent child interpreter
(`coordinator._ensure_worker` → `custom_components/heatpump_optimizer/process_worker.py`),
with an in-process fallback that is loud and capped (#199 #290 #511 #783).
Every GIL and loop-thread number below is measured against that route.

## Findings

Ids follow `tools/audit/finding.schema.json`'s `^D9-[0-9]{2}$`. `D9-01`, `D9-03`
and `D9-04` are already cited in the tree by earlier rounds, so round 4 starts
at **D9-05**; `D9-02` is left alone in case an archived round holds it.

### D9-05 (round 4) — the batched objective vectorizes the simulation and then re-computes the cost in a Python loop over the batch rows

`high`-cost-shaped but scored **medium**: it is a bounded, silent CPU cost, not
a wrong number and not a user-visible defect.

**Claim.** `optimizer.py`'s two `objective_batch` twins (`:3432` space-only,
`:5528` with-DHW) call `ThermalModel.simulate_trajectory_batch` once for all
B perturbed schedules — #97's win — and then run `for b in range(B)`
(`:3454`, `:5552`), calling `HeatPumpOptimizer._comfort_terms`,
`energy_cost_of`, `cycling`, `capacity` and `terminal_cost` once per row on
96-element slices. `_comfort_terms` alone is entered **97.02 times per gradient
evaluation** and **29 591 times per default two-zone DHW solve**, and accounts
for **33.3 % of the solve's wall time** — **0.86×** the cost of the entire
batched simulation it decorates. The physics half of the objective was
vectorized in #97; the cost half was not, and it is now the larger of the two
Python-side items.

**Evidence.** `tools/audit/round4/D9/h9_batch_cost_loop.py`, hooking
`optimizer:HeatPumpOptimizer._comfort_terms`,
`thermal_model:ThermalModel.simulate_trajectory_batch` and
`optimizer:_scoped_minimize`:

```
winter_typical.comfort_terms_calls_per_solve      = 29591 calls     (FINAL)
winter_typical.comfort_terms_calls_per_gradient   = 97.0197         (FINAL)
winter_typical.batch_rows_per_gradient            = 96 rows         (FINAL)
winter_typical.comfort_terms_cpu_share_pct        = 33.331 pct      (ratio)
winter_typical.simulate_batch_cpu_share_pct       = 38.7611 pct     (ratio)
winter_typical.comfort_over_simulate_batch        = 0.8599          (ratio)
cpu_ratio_vs_reference                            = 0.078388        (ratio)
winter_typical.solve_wall_s_PROVISIONAL           = 1.9733 s
thread_factor 0.999998 · load1 4.31 · concurrent_gate_procs 0
```

**Null control (mandatory, and it holds).** The same solve at the `flat` price
profile: `comfort_terms_cpu_share_pct = 34.1485` (delta **+0.82 pp**) and
`comfort_terms_calls_per_gradient = 97.0233` (delta **+0.0037**). The cost is a
property of the batch shape, not of the price structure — which is exactly what
distinguishes a structural inefficiency from an arms artefact.

**Perturbation, executed.** `H9_HORIZON=12` halves the horizon, so the batch is
~49 rows instead of ~97. Measured: `comfort_terms_calls_per_gradient`
**97.0197 -> 49.0299**, `batch_rows_per_gradient` **96 -> 48**, and the share
holds at **32.01 %** (the loop scales with the batch, so the share is
invariant). Direction: **down**. Output in `h9_h12.out`.

**Pi statement.** M1 number: 1.958 s of solve CPU, of which 0.652 s is
`_comfort_terms`. Extrapolation factor **7×** — **an assumption**, not a
measurement: Raspberry Pi 4 Cortex-A72 at 1.5 GHz against M1 Firestorm at
3.2 GHz on scalar Python/NumPy. On that assumption a cycle's solve is ~13.7 s
of Pi CPU and ~4.6 s of it is this loop; at 48 cycles/day
(`const.DEFAULT_OPTIMIZATION_INTERVAL = 30`) that is ~3.7 minutes/day of one
Pi core spent re-deriving cost terms row by row. It is **not** a stall: the
solve is out of process and the event loop does not wait on it (see the GIL
non-finding).

**Fix scope.** Vectorize the cost terms across the batch the way
`simulate_trajectory_batch` vectorized the physics — `_comfort_terms` is nine
`np.sum` reductions over a `[B, n]` array instead of B × nine over `[n]`. Both
twins, one shared helper, bitwise parity asserted the same way #97's was
(`tests/features.py::_grad_parity`, `tests/optimality.py`'s race). Not a
one-liner and not for this round.

### D9-06 (round 4) — the stress gate's memory budget cannot detect a 2× memory regression on any of its 51 scenarios

`medium`. The gate is the thing that is wrong, not the product.

**Claim.** `tests/stress.py` states its own detection target,
`DETECTION_TARGET = 2.0`, and sizes the CPU rules against it. Neither memory
rule meets it. The RSS rule is
`probe_rss > recorded_rss + max(150.0, recorded_rss × (MEMORY_BUDGET_FACTOR − 1))`;
with `MEMORY_BUDGET_FACTOR = 1.5` and recorded peaks of 91.3–98.1 MiB, the
`150.0` floor always dominates (0.5 × 98.1 = 49.1), so a scenario must reach
**2.53×–2.64×** its recorded RSS before the check fires. The traced rule,
`recorded × 1.5 + 2`, requires **2.08×–3.83×**. **All 51** recorded scenarios
pass a doubling on both axes. Compounding it, check mode re-probes only
`MEMORY_TOP_N = 6` of them, so **45 of 51** recorded memory budgets are never
compared at all. The comment at `stress.py:1512` asserts the interpreter+numpy
baseline "cancels in the comparison" — it does not: the rule is additive with
an absolute floor, and that ~91 MiB baseline is what makes the per-scenario
signal (a 6.8 MiB spread across the whole sweep) undetectable.

**Evidence.** `tools/audit/round4/D9/h7_memory_gate.py`, reading the executed
module constants `stress.MEMORY_BUDGET_FACTOR`, `stress.DETECTION_TARGET`,
`stress.MEMORY_TOP_N` and the committed `tests/stress_budgets.json`, and then
executing the shipped probe body (`stress.build_case` under `tracemalloc` plus
`stress.rss_mb`, which is what `--memory-probe` runs) in a fresh subprocess on
the recorded RSS leader `winter/pv`:

```
scenarios_recorded                     = 51            (FINAL)
memory_top_n                           = 6             (FINAL)
scenarios_never_memory_probed          = 45            (FINAL)
detection_target                       = 2.0           (FINAL)
min_rss_multiple_required_to_fail      = 2.52905       (FINAL)
max_rss_multiple_required_to_fail      = 2.64294       (FINAL)
scenarios_where_2x_rss_passes          = 51            (FINAL)
min_traced_multiple_required_to_fail   = 2.07637       (FINAL)
scenarios_where_2x_traced_passes       = 51            (FINAL)
rss_fail_threshold_mb                  = 248.1 MiB     (FINAL)
clean_probe_rss_mb_PROVISIONAL         = 82.0 MiB
inject2x_probe_rss_mb_PROVISIONAL      = 131.6 MiB  (1.605× clean)
inject2x_rss_rule_fires                = False         <-- executed proof
inject2x_traced_rule_fires             = True
load1 5.65 · concurrent_gate_procs 1
```

The injected arm is the brief's "inject work into the solve and run its
checks", applied to memory: a real numpy allocation sized to double the probe's
RSS watermark leaves the shipped RSS rule silent. The traced arm did fire on
that particular injection because `tracemalloc` sees the Python-side
allocation; it would not see a numpy-internal one, which is precisely the blind
spot `stress.py:1512` documents for `tracemalloc` and then relies on the RSS arm
to cover.

**Perturbation, executed.** `H7_PERTURB=nofloor` sets
`STRESS_MEMORY_FACTOR=1.05` (a factor that should tighten the rule by 9x) and
re-evaluates both with and without the `150.0` floor. Measured:
`memory_budget_factor = 1.05` yet `min_rss_multiple_required_to_fail` is
**still 2.52905** — the factor cannot move the threshold at all, because the
floor dominates — while `nofloor_min_rss_multiple_required_to_fail` = **1.05**.
That immobility is the finding, and the floor-removed arm is the direction:
**down**, and only when the floor goes. Output in `h7_nofloor.out`.

**What can it not see (the brief's question, answered).** (a) any memory
regression under 2.5× on any scenario; (b) any memory regression at all in 45 of
51 scenarios; (c) anything the RSS arm would have caught but `tracemalloc`
cannot — numpy-internal growth — because the RSS arm is the one that is blind.
What it *can* see: a >2.5× RSS blow-up in one of the six dearest recorded
scenarios, and a >2.08× Python-object allocation growth in the same six.

**Fix scope.** Budget the *scenario-attributable* component (probe RSS minus a
measured empty-probe baseline taken in the same run) rather than the absolute
watermark, and size the headroom from the measured spread instead of a 150 MiB
constant; or state a different detection target for memory and say why. Raising
`MEMORY_TOP_N` alone fixes nothing while the threshold is unreachable.

## Non-findings — everything that held, with the number that showed it

Each is a lead that did not become a finding, and each is worth as much as a
finding for the next round.

1. **The batched finite-difference gradient is live and doing its job.**
   `h1_grad_cost.py`: the default two-zone DHW solve costs **194.83
   simulate-step-equivalents per gradient** (30 144 scalar `simulate_step` +
   29 280 `simulate_trajectory_batch` rows over 305 gradient evaluations).
   Forcing `_bounds_supported_by_batch` to `False` (`H1_PERTURB=nobatch`) moves
   it to **9 316.41** — a **47.8×** difference, and the brief's "~9,300" is the
   counterfactual, not the baseline. The 195 is ~96 batch rows plus the one
   96-step scalar trajectory scipy evaluates at the same iterate; the #288 memo
   already shares that value with the jac's `f0`, so it is not double work.
2. **D9-01's widening still holds on the zero-range-bounds shape.** The fuse-cap
   arm (`power_cap_kw=3.5`, below the DHW run power, which pins space bounds to
   `(0, 0)` inside a DHW block) costs **195.02 equivalents/gradient** — within
   0.1 % of the unconstrained solve, against 9 028.70 with the batch path
   disabled. `h1_grad_cost.py`, arm `zero_range_fuse_cap`.
3. **One full solve per coordinator cycle, and no hidden second one.**
   `h4_retained.py`: `solves_through_process_worker = 8` over 8 cycles of the
   real `_async_update_data`. `h2_cycle.py` finds **0** in-process
   `_multi_start_minimize` entries per cycle — the shipped path is entirely
   out-of-process. The shadow/what-if solve (`coordinator.py:10332`) is
   user-triggered and rate-limited (`SIMULATE_MIN_INTERVAL_SECONDS`), never part
   of the scheduled cycle.
4. **Event-loop starvation is at the idle noise floor on the shipped route.**
   `tools/audit/harnesses/j5_gil.py` (the kept #290 instrument, run from this
   tree, a real asyncio loop with a 1 ms heartbeat and a real
   `ThreadPoolExecutor` — never `FakeHass`): `J5_ROUTE=production`,
   `two_zone_dhw.starvation_share = 0.0247`, `longest_gil_hold_ms = 21.98`,
   against the idle null control at `0.0354` / `12.27 ms`. The pre-fix
   `J5_ROUTE=thread` arm on the same box in the same session:
   `starvation_share = 0.9752`, `longest_gil_hold_ms = 65.48`. The process route
   removes the starvation; the two `sleep(0.002)` yields are no longer load-bearing.
   PROVISIONAL (wall), taken at load1 5.3–5.5.
5. **Loop-thread work per cycle is negligible.** `h2_cycle.py`, measuring
   `time.thread_time()` on the event-loop thread across one `_async_update_data`
   with the executor boundary real: **3.87 ms/cycle** loop CPU against **0.28 ms**
   of executor CPU and 1.28 s of wall (the wall is the child's solve). PROVISIONAL.
6. **Nothing in the coordinator grows without bound over 8 cycles.**
   `h4_retained.py`: deep `sys.getsizeof` over every `self._*` list/dict/set/
   ndarray is **43 269 B** after 8 cycles with a slope of **−5.26 B/cycle**. The
   largest retained collections are `_weather_forecast` (14 087 B, len 48) and
   `_prices` (13 941 B, len 48), both replaced rather than appended.
7. **The per-cycle allocation slope is not a coordinator leak.**
   `h8_leak_attrib.py` differences `tracemalloc` snapshots between cycle 2 and
   cycle 10: total growth **50 910 B**, of which **30 117 B** is production
   (3 765 B/cycle), led by `coordinator.py:877/879` (the pickle buffers of the
   current plan, replaced each cycle) and `accuracy.py:184` (a
   `deque(maxlen=HISTORY_LENGTH)` filling up). **Limitation, stated plainly:
   8 cycles cannot separate a bounded history filling from an unbounded one.**
   A 200-cycle run in the quiet window would settle it; I did not do it.
8. **The published payload and the recorder exclusion set are in proportion.**
   `h3_payload.py`, driving every platform's real `async_setup_entry` after one
   real solve: 74 entities, 5 carrying `_unrecorded_attributes`;
   `attr_bytes_total_per_cycle = 89 900 B`, of which **77 891 B (86.6 %) are
   excluded** and 12 009 B recorded — **0.55 MiB/day**, 5.5 MiB over the default
   10-day purge. The exclusions land where the bytes are:
   `SpaceHeatingPlanSensor` excludes 24 688 B and records 513;
   `DHWHeatingPlanSensor` excludes 23 506 B and records 510. No entity publishes
   a per-step series to the recorder. `_build_data_dict` is 160 keys /
   **77 374 B** per cycle, held in memory only.
9. **The solve worker is not a memory tax beyond numpy and scipy.**
   `h5_worker_footprint.py`, asking the child itself through the production
   pipe: **725 modules**, of which 11 `homeassistant.*` and 10
   `heatpump_optimizer.*`; a control child importing only `numpy` and
   `scipy.optimize` loads 689 — a **36-module** overhead. RSS after ten solves
   **57.2 MiB** against the control's **69.2 MiB** (PROVISIONAL; RSS
   double-counts shared library pages, so the incremental cost on a Pi is lower
   still). Pipe traffic `h4_retained.py`: **12 081 B** job + **18 183 B** reply
   per solve, **1.45 MB/day**.
10. **The BLAS pin question could not be settled on this box, and the green arm
    is dead-code green — say so rather than claim a pass.**
    `coordinator._worker_env()` exports no thread variable, so a real install's
    solve worker inherits none. `h6_worker_blas.py` measures `thread_factor`
    *inside* the child: **1.000** both with the five variables exported and with
    them stripped (`cpu_ratio_ha_like_over_pinned = 1.054`). But
    `H6_PERTURB=nolimits`, which disables `threadpoolctl` in the child as the
    documented fallback does, **also** reports 1.000 — and
    `threadpoolctl.threadpool_info()` on this numpy 2.4.6 returns `[]`. There is
    no OpenBLAS here for either mechanism to pin, so the harness cannot
    distinguish a working `_scoped_minimize` from a no-op one. The README's
    "measured 3.33× on this box" no longer reproduces on this numpy. **This
    needs a Linux/OpenBLAS run to answer.**
11. **`maxiter` is not a lever on this solve.** `H1_PERTURB=maxiter` (300 → 150)
    changes `equiv_total` by **0** — the five L-BFGS-B runs total `nit = 82`, so
    the cap is never reached. A verifier reaching for `maxiter` as a
    perturbation will measure nothing; `nobatch` and the horizon are the levers
    that move.
12. **CI sets no `STRESS_*` variable**, so the gate runs on the defaults this
    report measured (`.github/workflows/tests.yml:287-293` says so explicitly and
    records that `STRESS_SOLVE_BUDGET_MS` is retired). That is a *deliberate*
    state, and with the CPU rules per-scenario at `SCENARIO_BUDGET_FACTOR = 3.0`
    over all 51 it is defensible; only the memory arms (D9-06) are not.

## Harnesses

All under `tools/audit/round4/D9/`, each with the contract header (metric,
command, expected ± tolerance, baseline SHA, machine), each hooking a named
production symbol, each printing `RESULT` lines plus `thread_factor`, `load1`,
`swapins` and `concurrent_gate_procs`. Root rule: **`ROOT = os.getcwd()`** —
every one must be run from this worktree's root, and none resolves from
`__file__` (the trap `tools/audit/README.md` records).

| file | measures |
|---|---|
| `d9common.py` | shared builders (not a harness; prints nothing). Solve arms, telemetry, `stress.reference_solve` ruler |
| `h1_grad_cost.py` | simulate-step-equivalents per gradient, five arms, exclusive phase attribution |
| `h2_cycle.py` | solves per cycle, loop-thread CPU vs executor CPU, real `ThreadPoolExecutor` |
| `h3_payload.py` | `_build_data_dict` bytes and every entity's attribute bytes split by `_unrecorded_attributes` |
| `h4_retained.py` | retained-bytes slope per cycle, worker RSS, pickle bytes per solve |
| `h5_worker_footprint.py` | what the solve worker imports, and what it costs against a numpy+scipy control |
| `h6_worker_blas.py` | `thread_factor` inside the worker, pinned vs Home-Assistant-like environment |
| `h7_memory_gate.py` | the stress gate's memory rules against its own `DETECTION_TARGET`, with an executed 2× injection |
| `h8_leak_attrib.py` | attributes the per-cycle allocation slope to production / tests / other |
| `h9_batch_cost_loop.py` | the per-row cost loop inside the batched objective, with the flat-price null control |

Captured outputs kept beside them: `h1.out`, `h1_maxiter.out`, `h1_nobatch.out`,
`h9_h12.out`, `h7_nofloor.out`, `h6_nolimits.out`, `j5_production.out`,
`j5_thread.out`.

## What I could not finish

- **No full `tests/stress.py` sweep.** It needs the gate lock and an exclusive
  box; at ~22–25 s per `reference_solve` alone it would not fit the budget
  beside D4 and D8. So D9-06 rests on the shipped probe body executed
  directly and on the shipped constants, not on a red gate run. The confirming
  run is: inject a 2× allocation into one scenario, run the full gate, watch the
  memory section stay green.
- **The BLAS-pin question (non-finding 10) is open** and needs a Linux/OpenBLAS
  host.
- **The 8-cycle retention window (non-finding 7) is too short** to prove
  `accuracy.py:184` plateaus. A 200-cycle run settles it.
- **The `_lbfgsb_restart` and the third and fourth multi-start** were not costed
  individually. `h1_grad_cost.py` shows 5 `_scoped_minimize` calls per solve
  (4 starts + 1 restart) but attributes no CPU per start; "what the marginal
  starts cost, and how often they win" is a joint D0/D9 question I left alone.
- **All wall, CPU-second and RSS numbers are PROVISIONAL** and want the quiet
  window. Counts, bytes and the ratios against `reference_solve` are final.
