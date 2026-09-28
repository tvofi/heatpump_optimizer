# D9 — CPU and memory efficiency, round 3

- Baseline SHA: `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`
- Tree: `git archive` export, no `.git`, `docs/audit-*.md` / `docs/backlog.md` /
  `RELEASE_NOTES.md` removed. No `gh`, no GitHub, no earlier-round findings read.
- Box: 8-core Apple M1, 8 GB, shared. python 3.11.5, numpy 2.4.6, scipy 1.17.1,
  OpenBLAS. `load1` during the measurements ranged **8.1 – 33.1**; every RESULT
  carries its own `load1` and `thread_factor` (all runs 0.9996 – 1.0019, well
  inside the 1.05 bar).
- `tests/stress.py` was **not** run and no full `./tests/run.sh` was run; the
  gate lock was not taken. `tests/stress.py:reference_solve` was imported and
  called as a ruler only (5 samples, median), which is what the harness
  contract asks for.
- No production or test file was edited. Every hook is a runtime monkeypatch
  installed and removed inside the harness, so the tree is byte-identical to
  the export apart from the new files under `tools/audit/round3/D9/`.

## Method

Five harnesses under `tools/audit/round3/D9/`, each runnable by the single
command in its own header, each importing `d9lib.py` first so the five BLAS
thread variables are pinned before numpy loads.

| harness | metric |
|---|---|
| `h1_solve_work.py` | full solves per cycle, step-equivalents per cycle and per gradient |
| `h2_payload_bytes.py` | published payload bytes vs the recorder exclusion set, and per-cycle churn |
| `h3_memory.py` | retained bytes per cycle, `tracemalloc` slope, RSS of the solve worker |
| `h4_loop_thread.py` | loop-thread CPU per cycle; longest GIL hold and starvation share on a REAL loop + REAL `ThreadPoolExecutor` |
| `h5_multistart_grid.py` | what the four multi-start L-BFGS-B runs cost and buy, over a 16-cell grid |

`d9lib.py` is import-only scaffolding (thread pin, path setup, the coordinator
builder, the RESULT/telemetry printers). It builds a real
`HeatPumpOptimizerCoordinator` the way `tests/entities.py:_honest_coordinator`
and `tests/golden.py:_capture_coordinator` do — one real input-read cycle plus
48 h of deterministic prices, weather and irradiance — and offers two
production-path switches: `inline_solves()` (replaces `coordinator._await_process`
so a call-counting harness can see the job, which a child interpreter's
counters cannot be) and `break_worker()` (makes `_await_process` raise
`ProcessWorkerUnavailable`, so `_await_optimize` takes **its own** #511 fallback
branch — the executor route, not the loop thread).

**Metric definitions are the brief's, verbatim.** Step-equivalents = scalar
`ThermalModel.simulate_step` calls + rows of
`ThermalModel.simulate_trajectory_batch`, both hooked by monkeypatching the
production symbols.

### Extrapolation to the Pi

Stated as an assumption, because no Pi was measured here: **a Raspberry Pi 4B
(Cortex-A72, 1.5 GHz) runs this CPython + NumPy workload 4–8× slower per core
than this M1, midpoint 6×.** Every Pi sentence below is the named M1 number
times that band, and says so.

## Findings

### D9-01 — 56 % of the solver's L-BFGS-B work goes to starts that change nothing

`optimizer._MULTI_START_SOLVES` is 4, and `_multi_start_minimize` refines all
four of the scored candidates with no early exit when a refined start merely
reproduces the objective an earlier start already reached.

Over the 16-cell grid (8 `tests/profiles.py` price profiles × single-zone and
two-zone, both DHW-enabled): **`redundant_share` mean 0.5605**, range 0 – 0.9362
across cells, **0.5355** with the single most favourable cell dropped
(leave-one-out). Total grid work 573,024 step-equivalents; 213,312 of them
inside L-BFGS-B runs that did not improve on the incumbent.

What the extra starts buy: mean objective gain **0.0118** (1.18 %), **zero in 7
of the 16 cells**, and 0.1337 in the single best cell (`2z/winter_typical`) —
so the mechanism is not worthless, it is unmetered.

Perturbation `HPO_D9_STARTS=1` (rewrites `_MULTI_START_SOLVES`): grid total
573,024 → **117,408** step-equivalents, a **4.88×** cut, `redundant_share` and
`best_gain` both to 0. Null control (the flat price profile, where the *gain*
must vanish and the *cost* must not, because the cost is structural):
`1z/flat` 45,024 → 10,080 (4.47×), `2z/flat` 55,776 → 8,544 (6.53×) — the cost
effect survives at flat prices, so it is a property of the mechanism, not of
the priced arm.

Pi: the two-zone winter solve is 54,240 step-equivalents; on the assumed 4–8×
band the M1-measured 0.99 s warm cycle wall (provisional, `load1` 8.1) is
4.0 – 7.9 s of Pi CPU per 30-minute cycle, of which ~56 % of the solver part
produced nothing.

Severity **medium**: bounded cost, no wrong output.

### D9-02 — the fuse advisor's weekly rate limit is memory-only, so every restart doubles the first cycle's solve

`HeatPumpOptimizerCoordinator._maybe_run_fuse_advisor` is gated on
`self._fuse_advisor_at`, initialised to `None` at
`coordinator.py:1727` and never restored from any store (`_fuse_advisor` is
published into the data dict at `:7014` but nothing reads either back at
setup). So the "at most weekly" guard is empty after every Home Assistant
restart, every integration reload and every options save, and the shadow solve
runs on the first cycle whatever the real interval was.

Measured, fuse guard + peak tariff configured, one full `_async_update_data`:

| arm | `optimize()` calls | step-equivalents |
|---|---|---|
| first cycle after a restart (guard `None`) | 2 | 45,888 |
| rate limit already satisfied | 1 | 22,944 |
| **flat prices**, first cycle (NULL CONTROL) | 2 | 93,120 |
| **flat prices**, rate limit satisfied | 1 | 46,560 |

**Exactly 2.000× in both arms.** The null control shows the doubling is
structural, not price-driven. The perturbation is the pre-set guard
(`_fuse_advisor_at = now`, `_fuse_advisor["month"] = month_key(now)`), and it
collapses the doubling exactly.

This lands on the worst possible cycle: the first refresh after a restart, when
every other integration is also setting up — which is the situation the owner
described as having made the whole instance unreachable.

Pi: 45,888 step-equivalents against 22,944, on the assumed 4–8× band, is an
extra 4 – 8 s of solve on the busiest cycle the host has.

Severity **medium**.

### D9-03 — the #511 in-process fallback starves the event loop for 83–89 % of the solve

Measured on a real `asyncio` loop with a real `ThreadPoolExecutor` and a 1 ms
heartbeat, never on `FakeHass` (whose `async_add_executor_job` runs inline and
would measure nothing). The fallback arm makes `_await_process` raise, so
`_await_optimize`'s own `except ProcessWorkerUnavailable` branch runs — the
shipped degradation, not a harness invention.

| arm | starvation share | longest gap | ticks in window |
|---|---|---|---|
| idle, no solve (NULL CONTROL) | 0.0055 – 0.0084 … 0.0333 | 6.4 – 25.8 ms | 839 – 1424 |
| shipped process route | 0.0055 / 0.0764 | 5.1 / 8.3 ms | 694 / 843 |
| **#511 in-process fallback** | **0.889 / 0.830** | **40.5 / 49.5 ms** | 87 / 356 |

Two runs, `load1` 8.1 and 33.1; every figure here is `"provisional": true`. The
*shipped* route sits at or below this box's idle noise floor — the GIL problem
the two `sleep(0.002)` yields were added for is solved by the process worker,
not by the yields, and those two yields do not bound the fallback because they
sit between L-BFGS starts and at the DHW/space seam, not inside an iteration.
Nothing bounds how long an install stays on the fallback: `_note_worker_fallback`
warns and raises a repair issue, and the next cycle tries the worker again, but
a persistently broken worker (the #511 shape) starves the loop on every cycle
for as long as it lasts.

Pi: 0.79 s of M1 fallback solve × the assumed 4–8× band is 3 – 6 s of ~85 %
event-loop starvation every 30 minutes.

Severity **medium**, `provisional`.

### D9-04 — the solve worker holds ~43–62 MiB resident for a ~0.06 % duty cycle

`coordinator._ensure_worker` spawns a persistent child interpreter on the first
solve and reaps it only at `EVENT_HOMEASSISTANT_STOP` (or the `atexit`
backstop). Measured RSS of that child after one real solve: **43,744 KiB** and
**61,552 / 52,816 KiB** on a second run, against a bare `python3` floor of
**15,680 – 15,936 KiB** measured in the same harness. So the integration adds
roughly 28 – 46 MiB of resident numpy/scipy/integration image on top of Home
Assistant's own interpreter, and holds it for the ~29.98 of every 30 minutes
the worker is idle (measured cycle wall 0.99 s → 0.055 % duty).

Perturbation `HPO_D9_NOWORKER=1`: no worker is spawned, `worker_rss_kib` is 0
and the work lands in the parent. Null control: the bare-interpreter floor is
what is *not* attributable to this integration, and the flat-price arm gives
the same worker RSS, so it is not a property of the price arm.

Pi: assuming the aarch64-Linux resident image is within ±30 % of this M1 figure
(an assumption — not measured), 43.7 MiB is 4.3 % of a 1 GB Pi 3B and 2.1 % of
a 2 GB Pi 4.

Severity **low**, `provisional` (RSS).

## Non-findings — what held, with the number

1. **The finite-difference gradient is no longer the cost.** `steps_per_gradient`
   = **96** on every arm measured (default two-zone DHW cycle, single-zone,
   no-DHW, flat) — one batch row per free variable, one
   `simulate_trajectory_batch` call per `_batch_fd_gradient` call, 115 gradient
   evaluations in a default cycle. The brief's "~9,300 `simulate_step` calls per
   L-BFGS iteration" premise does not hold at this baseline.
   `h1_solve_work.py`.
2. **Full solves per cycle at the default config: one.**
   `cycle.optimize_calls=1`, `cycle.multi_start_entries=2` (the space stage and
   `_co_optimize`'s re-solve), no shadow, diagnose or what-if solve. The only
   config that adds one is the fuse advisor — D9-02.
3. **Per-cycle loop-thread work outside the executor is negligible.**
   `time.thread_time()` on the loop thread across one whole cycle with the
   heartbeat off: **5.67 – 8.28 ms**, i.e. **0.137 – 0.191 ×
   `reference_solve`** CPU in the same process, and 0.4 – 0.6 % of the cycle's
   wall. Cold and warm are within 20 % of each other. `h4_loop_thread.py`.
   (A first attempt at this number measured 162 ms — the 1 ms heartbeat's own
   loop-thread cost. Naming the gap: a GIL harness and a loop-CPU harness
   cannot be the same run.)
4. **The longest contiguous GIL hold on the shipped path is 5.1 – 8.3 ms**, at or
   below this box's own idle floor (6.4 – 25.8 ms with no solve running at all).
   The process worker, not the two 2 ms yields, is what achieves that.
5. **No retained collection grows without a trim.** Deep `sys.getsizeof` over
   all **24** list/dict/set/tuple attributes the coordinator holds, after 1
   cycle vs after 6: slope **−4 B/cycle** (priced) and **+8 B/cycle** (flat).
   `tracemalloc` over the same six cycles: ~50 KB/cycle of churn with a traced
   peak of 0.49 MB and no monotone growth. The appenders that exist are all
   capped in place (`_immersion_evidence[:-6]`, `_immersion_events[:-20]`,
   `_month_reports` to `KEEP_MONTHS`, `accuracy.py`'s `deque(maxlen=...)`).
   `h3_memory.py`.
6. **The recorder exclusion set is doing its job.** Across all 74 entities the
   six platforms add: **12,699 bytes** of recorded attributes per publish
   against **85,246 bytes** excluded — **87.0 % excluded**. The honest per-cycle
   recorder cost (only the entities whose recorded attributes actually change
   between two consecutive cycles, since HA stores one row per distinct
   attribute set) is **8,236 bytes over 20 of 74 entities**, i.e. **386 KiB/day**
   at the default 30-minute interval. `_build_data_dict` itself is 160 keys /
   84,751 JSON bytes and is not written to the recorder. The flat-price arm is
   within 0.6 % of the priced arm, so the payload is structural.
   `h2_payload_bytes.py`.
   Largest *recorded* attributes, for whoever tightens this next:
   `ThermalBatterySensor.components` 651 B, `DHWSetpointAdvisorSensor.candidates`
   520 B, `PredictiveInsightSensor.dhw_usage_profile` 504 B,
   `PlanNarrativeSensor.items` 412 B, `PowerHeadroomSensor.horizon_headroom_kw`
   265 B — all on classes that declare no `_unrecorded_attributes` at all (only
   4 of the entity classes declare one).
7. **The stress gate's two stated holes are already closed at this baseline.**
   `.github/workflows/tests.yml` sets **no `STRESS_*` variable at all** (only
   the three thread pins); `STRESS_SOLVE_BUDGET_MS` is retired in
   `tests/stress.py:171`. The "CI sets it 4× looser than the default" premise
   does not hold. Memory instrumentation exists: `MEMORY_BUDGET_FACTOR`,
   `MEMORY_TOP_N` and a memory pass, with `rss_peak_mb` and `traced_peak_mb`
   recorded for all **51** scenarios in `tests/stress_budgets.json`. The "no
   memory instrumentation anywhere" premise does not hold either. Established by
   reading and by `python3 -c "import json; ..."` on the budget table; the sweep
   itself was **not** run, per the dispatch conditions.

## Disproved lead

**"A flat tariff doubles the solve."** The coordinator cycle at a flat price
profile costs 46,560 step-equivalents against 22,944 priced — 2.03× — which
looked like a finding about fixed-price contracts. It does not survive the
grid: `1z/flat` at 45,024 is 2.44× the 1z priced *mean* but below
`1z/winter_moderate` at 51,648, and `2z/flat` at 55,776 is 1.14× the 2z mean and
well below `2z/winter_narrow` at 88,224. Flat is an expensive profile to solve,
not the most expensive, and "fixed-price contracts pay double" is not
supportable. Recorded here so the next round does not re-derive it.

## What I could not finish

- No absolute wall/CPU/RSS number here is final: `load1` ran 8.1 – 33.1
  throughout. D9-01 and D9-02 rest entirely on counts and are unaffected;
  D9-03 and D9-04 are marked `provisional` and want a quiet-window re-take.
- The DHW planning loops were measured only in aggregate (they are inside the
  cycle totals above); a per-loop split of `_plan_dhw_min_cost`,
  `_plan_dhw_cheapest_first` and `_repair_dhw_floor` did not fit the budget.
- Whether the stress gate detects a synthetic 2× regression was not executed:
  it requires running `tests/stress.py`, which the dispatch conditions forbid.
  `tools/audit/harnesses/h8_single_scenario.py` is the instrument for it.

## Exposure

`docs/plan-open-issues.md` was matched by one repository-wide `grep` for
`STRESS_`, and one line of it was read in the grep output. No other `docs/`
file, no GitHub, no `gh`, no earlier-round findings, no `docs/audit-*.md`
(absent from the export). `D<k>-nn` ids appearing in production comments
(`D9-01`, `D9-03`, `D9-04` in `optimizer.py` and `stress.py`) were read as
context in the code being audited and were not chased.
