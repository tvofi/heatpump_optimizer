# D9 panel, round 3 — verifier 1 of 3 (refute-first, own-harness seat)

- Tree: `tools/audit/round3/D9/verify-1/` in the D9-1 verification copy of
  baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`.
- Box: 8-core Apple M1, python 3.11.5, numpy 2.4.6, scipy 1.17.1, OpenBLAS.
  All five BLAS thread variables pinned to `"1"` before numpy, via `d9lib`.
  Every RESULT line carries `thread_factor`, `load1`, `swapins` and
  `concurrent_stress_procs`; `thread_factor` was 0.9999 – 1.0023 on every run
  (bar 1.05), `concurrent_stress_procs` 0 on every run.
- `tests/stress.py` was **not** run; no `./tests/run.sh`; no gate lock taken.
  `tests/stress.py:reference_solve` was imported and called as a ruler only.
- No production or test file was edited (`find custom_components tests -newer
  VERSION -type f` returns only `__pycache__`). Every hook is a runtime
  monkeypatch installed and removed inside a harness.
- Nothing read from the register, from another verifier, or from GitHub.

## Step 1 — the finder's harnesses, re-run as their headers say

| harness | my re-run | verdict |
|---|---|---|
| `h5_multistart_grid.py` | every one of the 85 count/ratio RESULT lines **byte-identical** to `h5.out` (`diff` differs only in `thread_factor` / `load1` / `swapins`) | reproduces |
| `h5` + `HPO_D9_STARTS=1` | `grid.total_step_equivalents` 573024 → **117408**, identical to the finder's | reproduces |
| `h1_solve_work.py` | every count RESULT **byte-identical** to `h1.out` | reproduces |
| `h4_loop_thread.py` | **failed its own reproduction bar at `load1` 10.62** (fallback/process 3.45×, bar is 5×); **passed at `load1` 8.84** (8.06×) — see D9-03 | load-dependent |
| `h3_memory.py` | the retention arms reproduce to the byte (`deep_sizeof_slope` −4 / +8 B/cycle, `traced_peak` 4.99e5); the RSS arm is inside the finder's band (57,056 / 51,888 KiB) but see D9-04 | direction only on RSS |

Outputs: `verify-1/rerun-h5-baseline.out`, `rerun-h5-starts1.out`,
`rerun-h1.out`, `rerun-h4.out`, `rerun-h4-quiet.out`, `rerun-h3-quiet.out`.

## Step 2 — my own harnesses and my own metrics

| harness | what it measures that the finder's does not |
|---|---|
| `verify-1/v1_starts_policy.py` | the multi-start **policy curve**: the same 16 cells solved at `_MULTI_START_SOLVES` ∈ {1,2,3,4}, with work, selected objective, `predicted_cost` and the step-0 action at each k; plus the finder's own redundancy rule re-aggregated as a **ratio of sums** |
| `verify-1/v2_fuse_shadow.py` | step-equivalents **per entry into `HeatPumpOptimizer.optimize`**, so the advisor's shadow solve is separately visible, over a five-point main-fuse sweep and three consecutive cycles |
| `verify-1/v3_loop_starvation.py` | loop starvation as **ratios** — heartbeat tick rate against the same session's idle arm, excess lateness with no 5 ms cliff, longest hold in units of `reference_solve` |
| `verify-1/v4_worker_rss.py` | the **marginal** resident cost of the process route: (parent + child) with the worker minus parent without it, in a genuinely separate interpreter, plus a numpy+scipy floor |
| `verify-1/v5_winner_rank.py` | whether a "redundant" start is identifiable **before** it is paid for: the score-order rank of the start that actually wins |

---

## D9-01 — **refute**

**Claim.** 56.05 % of the step-equivalents spent inside L-BFGS-B runs go to
starts whose final objective does not improve on the best already reached in
the same `_multi_start_minimize` call; the extra starts buy a mean objective
gain of 1.18 %, zero in 7 of 16 cells.

**My metric.** `pooled_redundant_share` = Σ over the grid of step-equivalents
in L-BFGS-B runs that did not improve on the best already reached in the same
`_multi_start_minimize` call, ÷ Σ over the grid of step-equivalents inside
L-BFGS-B runs. (The finder's rule, aggregated as a ratio of sums.) Second
metric: `wasted_work_share` = the share of the grid's total step-equivalents
removable at the largest `k` whose selected objective is no worse than k=4 in
**every** cell and whose step-0 action moves in none.

**My numbers** (`verify-1/v1.out`, `verify-1/v5.out`; counts, contention-immune;
`thread_factor` 0.9999, `load1` 8.46 / 19.19):

| number | value |
|---|---|
| `grid.total_in_run_equivalents` | 559,008 |
| `grid.total_redundant_equivalents` | 213,312 |
| **`grid.pooled_redundant_share`** | **0.38159** |
| `grid.mean_of_cell_redundant_shares` | 0.560532 (the finder's figure, exactly) |
| `grid.cell_equiv_min / max / spread` | 2,304 / 88,224 / **38.29×** |
| **`verdict.smallest_lossless_k`** | **4** |
| **`verdict.wasted_work_share`** | **0** |
| `grid.rank0_wins_share` | 0.4706 (8 of 17 multi-start calls) |
| `grid.winner_rank_histogram` | `{0: 8, 1: 3, 2: 2, 3: 4}` |

### Attacks run

1. **Grid artefact — confirmed.** 0.5605 is a *mean of per-cell ratios* over
   cells whose work spans 38.29×. The claim's own words ("of the
   step-equivalents … go to") describe a ratio of sums, and the ratio of sums
   is **0.38159**. The headline overstates its own metric by 47 % relative.
   The small cells carry the large shares: `2z/summer_typical` is 2,304
   step-equivalents at share 0.800 and `1z/summer_typical` 5,376 at 0.936,
   while the two largest cells (`2z/winter_narrow` 88,224 and
   `2z/winter_moderate` 84,672) sit at 0.156 and 0.758 and `2z/winter_typical`
   (54,240) at 0.000.
2. **Waste vs insurance — the 56 % is insurance.** The policy curve
   (`v1.out`) shows **no** k below 4 is free:

   | k | grid step-equivalents | removable work | cells with a worse objective | cells whose step-0 action moves | max cost penalty |
   |---|---|---|---|---|---|
   | 1 | 117,408 | 79.5 % | **8 / 16** | **4 / 16** | +17.2 % |
   | 2 | 277,536 | 51.6 % | **6 / 16** | **3 / 16** | +2.90 % |
   | 3 | 418,848 | 26.9 % | **4 / 16** | **1 / 16** | +2.90 % |
   | 4 | 573,024 | 0 | 0 | 0 | 0 |

   `verdict.wasted_work_share = 0`. The cells that lose at k=2 —
   `1z/shoulder`, `1z/winter_moderate`, `1z/flat`, `2z/winter_typical`,
   `2z/winter_narrow`, `2z/flat` — are exactly the shapes the D0-02 raise from
   2 to 4 was recorded for, and the step-0 action moves in 3 of them, which by
   this repository's own D0-01 standard is a loss MPC re-planning cannot mask.
   An independent measurement therefore **corroborates the 2 → 4 raise** rather
   than the finding.
3. **The named mechanism cannot fire.** The claim attributes the cost to "no
   early exit on a tie". A tie is only observable *after* the start has
   converged, i.e. after its cost is paid, so the only removable work is a
   start skippable on evidence available beforehand — which is the
   pre-refinement candidate score `_multi_start_minimize` already computes and
   sorts on. `v5.out`: over 17 multi-start calls the best-scoring candidate
   wins only **8** (`rank0_wins_share = 0.4706`), and the **worst**-scoring of
   the four refined candidates wins **4** times — more often than rank 1 or
   rank 2. The cheap pre-filter does not rank the winner, so there is no
   evidence on which a start could have been skipped.
4. **The perturbation is tautological.** Under `HPO_D9_STARTS=1`
   `redundant_share → 0` *by definition* (the metric counts runs after the
   first; with one start there are none). It is an identity, not a
   measurement, and cannot support the metric. What the perturbation does show
   — 573,024 → 117,408, a 4.88× cut — is itself inconsistent with the metric:
   a 56.05 % redundant share predicts at most a 2.27× cut, and the 38.16 %
   pooled share predicts 1.62×. The extra factor is the *whole* of starts 2–4
   (79.5 % of the work), of which less than half was ever labelled redundant.
5. **Latent attribution weakness, did not fire.** `h5`'s
   `if GROUPS: GROUPS[-1].append(...)` charges any `_scoped_minimize` call made
   *outside* a `_multi_start_minimize` call to the previous group, which would
   compare objectives of different sub-problems. I instrumented depth
   explicitly: `grid.orphan_run_equivalents = 0` on this grid, so the number is
   not contaminated. It is a trap for whoever re-uses the harness elsewhere.
6. **Null control present and passing.** `flat` is in the grid; the *cost*
   effect survives at flat prices (`1z/flat` 45,024 → 10,080 under the k=1
   perturbation) and the *gain* does not vanish there either (`1z/flat` and
   `2z/flat` both lose objective at k=1, k=2 and k=3) — so what the extra
   starts buy is not a price-arbitrage artefact.
7. **Severity by consequence.** Bounded cost, no wrong output, and no part of
   it removable without a worse plan somewhere on the grid. Not `medium`.

**What survives.** Two true, reproduced sub-facts: `_MULTI_START_SOLVES = 4`
refines every scored candidate unconditionally, and 79.5 % of the grid's solver
work is in starts 2–4. Neither is a defect at this baseline; if the judge keeps
anything it should be reclassified as an *unmetered-insurance* observation at
`info`, not a `medium` efficiency finding. An adaptive rule is not ruled out by
my measurement — but no rule keyed on the evidence the solver has before
refining can be built from the 47 % rank-0 hit rate, and nothing keyed on the
objective after refinement can save the work.

---

## D9-02 — **weaken to `low`**

**Claim.** `_fuse_advisor_at` is `None` and never restored, so after every
restart, reload or options save the shadow solve runs, costing **exactly
2.000×** the cycle's simulation work.

**My metric.** `solve_equiv[i]` = step-equivalents charged to the *i*-th entry
into `HeatPumpOptimizer.optimize` during one `_async_update_data`;
`shadow_ratio` = `solve_equiv[1] / solve_equiv[0]`.

**My numbers** (`verify-1/v2.out`; counts, contention-immune; `thread_factor`
0.99994, `load1` 6.84):

| arm | candidate cap | optimize entries | main / shadow | cycle ratio |
|---|---|---|---|---|
| 20 A × 3 (the finder's) | 11.04 kW | 2 | 22,944 / 22,944 | **2.000** |
| 25 A × 3 | 13.8 kW | 2 | 22,944 / 22,944 | 2.000 |
| 63 A × 3 | 34.5 kW | 2 | 22,944 / 22,944 | 2.000 |
| **25 A × 1** | **4.6 kW** | 2 | 22,944 / **17,088** | **1.745** |
| **20 A × 1** | **3.68 kW** | 2 | **17,088** / **19,104** | **2.118** |
| 16 A × 3 (bottom of `FUSE_LADDER_A`) | — | **1** | 22,944 / — | 1.000 |
| no fuse configured (shipped default) | — | **1** | 22,944 / — | 1.000 |
| flat prices, 20 A × 1 (null control) | 3.68 kW | 2 | 51,168 / 47,904 | 1.936 |
| **three consecutive cycles, one coordinator** | 11.04 kW | **4 over 3 cycles** | advisor solved **once** | — |

### Attacks run

1. **"Exactly 2.000×" is an artefact of a cap that never binds — confirmed.**
   On every three-phase setting the candidate cap (11.04 – 34.5 kW) is far
   above anything the plan draws, so the shadow solve is a *bit-identical
   repeat* of the main solve and the ratio is exactly 2. Make the cap bind
   (single phase, 3.68 – 4.6 kW) and the ratio moves to **1.745× and 2.118×** —
   and at 20 A × 1 the fuse guard's own cap changes the **main** solve too
   (22,944 → 17,088), so even the denominator is not the finder's. The
   *structural* part — one extra entry into `optimize` — holds on every arm
   where the advisor solves at all. The precision does not.
2. **Population.** `DEFAULT_MAIN_FUSE_A = 0` (`const.py:391`), and
   `config_flow.py:1460` offers that default, so `_fuse_kw()` returns `None`
   and the advisor never solves on an install that has not configured a main
   fuse (`E_no_fuse_config`: 1 entry). At 16 A there is no smaller rung in
   `FUSE_LADDER_A` and it returns early (`B_16Ax3`: 1 entry). The affected
   population is installs that set a main fuse of 20 A or more.
3. **Frequency is bounded — once per coordinator, not per cycle.** Three
   consecutive `_async_update_data` calls on one coordinator produced **4**
   `optimize` entries, with the advisor solving on cycle 1 only
   (`D_three_cycles.advisor_entries_that_solved = 1`).
4. **The consequence sentence is contradicted by production.** The claim says
   it "lands on the worst possible cycle: the first refresh after a restart,
   when every other integration is also setting up".
   `custom_components/heatpump_optimizer/__init__.py:233-235` sets
   `coordinator._skip_solve_once = True` *before*
   `async_config_entry_first_refresh()`, and `coordinator.py:4593-4597`
   consumes it and returns `_async_first_refresh_light()` — **the first refresh
   does not solve at all**. The real first solve is deferred to
   `entry.async_create_background_task(..., "heatpump_optimizer_first_solve")`
   after `async_forward_entry_setups`, and it goes through the process worker,
   so it does not hold the loop. The doubling is on the first *background*
   solve, which is the mitigation this integration already built.
5. **Persistence premise holds.** The coordinator opens nine `Store`s and
   restores nine pieces of state at setup; `_fuse_advisor_at` is in none of
   them. `grep -rn fuse_advisor custom_components/` outside `coordinator.py`
   finds only `sensor.py:1917-1919`, which reads the published dict outward.
   Nothing reads it back. The claim is right about the mechanism.
6. **Null control passes.** At flat prices the doubling survives
   (`C_flat_20Ax3` 93,120 = 2 × 46,560), so it is structural, not price-driven.

**Why `low`.** One extra solve, once per coordinator lifetime, only on installs
with a main fuse ≥ 20 A configured, off the setup path, in a child process, and
its size is 0.745× – 1.118× of the cycle's own solve rather than exactly 1×.

---

## D9-03 — **weaken** (severity `low`; the fallback arm verifies, the process-route baseline does not)

**Claim.** The #511 in-process fallback loses 0.889 / 0.830 of the solve's wall
time to gaps over 5 ms, longest gap 40.5 / 49.5 ms, against 0.0055 / 0.0764 and
5.1 / 8.3 ms on the shipped process route and 0.006 – 0.033 idle.

**My metrics.** `tick_rate_ratio` = heartbeat ticks per second of wall in the
arm ÷ the same in the **idle** arm of the same process in the same session;
`excess_lateness_share` = Σ max(0, gap − 1 ms) ÷ wall (no 5 ms cliff);
`longest_hold_over_reference` = longest inter-tick gap ÷ the median process-CPU
ms of `tests/stress.py:reference_solve` in this process in this session.

**My numbers** (`verify-1/v3-quiet.out`, `verify-1/rerun-h4-quiet.out`;
`load1` 9.65 – 10.06 and 8.84, `thread_factor` 1.0002 / 1.000000,
`concurrent_stress_procs` 0, `reference_solve_cpu_ms` 28.4 / 31.7):

| arm | tick rate ÷ idle | excess lateness | longest gap | gaps > 5 ms | longest ÷ reference_solve |
|---|---|---|---|---|---|
| idle (NULL CONTROL), 2 runs | 1.000 | 0.255 / 0.281 | 1.89 / 7.59 ms | 0 / 5 | 0.066 / 0.267 |
| shipped process route, 2 runs | **0.700 / 0.908** | 0.487 / 0.334 | **23.7 / 17.7 ms** | 19 / 4 | 0.833 / 0.623 |
| process route, flat prices | 0.956 | 0.300 | 5.45 ms | 1 | 0.192 |
| **#511 in-process fallback**, 2 runs | **0.142 / 0.128** | **0.895 / 0.905** | **58.8 / 43.0 ms** | 29 / 25 | 2.07 / 1.51 |
| fallback, flat prices (null control) | **0.0789** | 0.942 | 77.5 ms | 52 | 2.72 |
| **`verdict.fallback_over_process_tick_rate`** | **0.168** | — | — | — | — |

`rerun-h4-quiet.out`, the finder's own harness on the same window:
`inprocess_fallback.starvation_share` **0.8965**, longest **50.8 ms**;
`idle` 0.0105 / 8.15 ms; `process_route` **0.1113** / **17.3 ms**.

### Attacks run

1. **Contention — this one bit, and it is why the verdict is `weaken` and not
   `verify`.** My first re-run of `h4_loop_thread.py` at `load1` 10.62
   (`rerun-h4.out`) **failed the harness's own stated reproduction bar**: it
   gave `idle.starvation_share` 0.155, `process_route` 0.272 with a
   **138.4 ms** longest hold — *longer than the fallback's 77.6 ms* — for a
   fallback/process ratio of 3.45×, under the header's "not at least 5× … has
   not reproduced". On the later window at `load1` 8.8–10.1 it passes at
   8.06×, and my own tick-rate ratio gives 5.95×. So the finding reproduces,
   but `starvation_share` is not a stable instrument on this box and a single
   pair of windows is not enough to carry it.
2. **The fallback figures verify.** Claim 0.889 / 0.830 and 40.5 / 49.5 ms;
   I measured 0.895 / 0.905 and 58.8 / 43.0 ms on my harness and 0.8965 /
   50.8 ms on the finder's. Direction and magnitude class confirmed, and the
   perturbation (`d9lib.break_worker()`, which makes production's own
   `except ProcessWorkerUnavailable` branch in `coordinator.py:926-930` run)
   moves it the stated way.
3. **The contrast does not.** The claim says the shipped route "sits at or
   below this box's idle noise floor". It does not on my measurements: the
   process route showed **19 gaps over 5 ms and a 23.7 ms longest hold**
   against an idle floor of 1.89 / 7.59 ms, and 17.3 ms on the finder's own
   harness against an 8.15 ms idle. The honest contrast is **6×** on tick
   rate (0.804 vs 0.135) and **8×** on `starvation_share`, not the ~100× the
   quoted 0.0055 vs 0.889 implies.
4. **Reachability in real HA — sound construction.** The arms run on a real
   `asyncio` loop with a real `ThreadPoolExecutor` (`LoopHass` wraps
   `FakeHass` for state only), so the `FakeHass.async_add_executor_job`
   inline-execution trap is avoided. The fallback branch executed is
   production's.
5. **Null control passes and is stronger, not weaker.** At flat prices the
   fallback's tick-rate ratio is 0.079 against 0.956 for the process route on
   the same profile, so the effect is structural, not a property of the priced
   arm.
6. **Severity by consequence — `low`.** The fallback only runs when
   `_ensure_worker`/transport/unpickle fails. When it does,
   `_note_worker_fallback` logs a warning **every cycle** and raises a
   **persistent** repair issue, and `_await_optimize`'s own docstring calls it
   "the accepted trade -- a slow plan beats none". This is a documented,
   announced degradation on a broken install, not a defect of the normal
   path. It would be `medium` for an install actually stuck there — 0.65 s of
   ~87 % loop starvation per cycle on this M1, more on a Pi — but nothing in
   the measurement shows an ordinary install reaching it.

---

## D9-04 — **weaken** (severity stays `low`; the magnitude does not survive)

**Claim.** The persistent worker means an install carries 43,744 – 61,552 KiB
extra resident — 28 – 46 MiB above the 15,680 – 15,936 KiB bare-interpreter
floor — for the ~29.98 of every 30 minutes it is idle.

**My metric.** `route_marginal_rss_kib` = (parent RSS + child RSS) in the
worker arm − parent RSS in a **separate interpreter** that never spawned a
child (`d9lib.inline_solves()`), both after the same two cycles; plus
`worker_over_numpy_scipy_floor` = child RSS ÷ the RSS of a fresh interpreter
that imported only `numpy` and `scipy.optimize`.

**My numbers** (`verify-1/v4.out` at `load1` 21–24, `verify-1/v4-quiet.out` at
`load1` 11.5–13.3, `rerun-h3-quiet.out` at `load1` 11.5):

| number | run 1 | run 2 (quiet window) |
|---|---|---|
| bare interpreter | 15,408 KiB | 15,408 KiB |
| **interpreter with only `numpy` + `scipy.optimize`** | **65,696 KiB** | **71,840 KiB** |
| worker child RSS | 55,024 KiB | 78,144 KiB (peak 83,968) |
| parent **with** the worker | 38,864 KiB | 49,872 KiB (peak 87,520) |
| parent **without** the worker | 62,928 KiB | 78,576 KiB (peak 99,984) |
| `parent_rss_delta_without_worker_kib` | **+24,064 KiB** | **+28,704 KiB** |
| **`route_marginal_rss_kib`** | **30,960 KiB** | **49,440 KiB** |
| `route_marginal_peak_rss_kib` | — | 71,504 KiB |
| **`worker_over_numpy_scipy_floor`** | **0.838** | **1.088** (peak 1.169) |
| `idle_duty_share` | 0.0021 | **0.000464** |

The finder's own harness re-run gave `priced.worker_rss_kib = 57,056` and
`flat.worker_rss_kib = 51,888` — inside their band.

### Attacks run

1. **Wrong baseline.** The claim subtracts a bare-interpreter floor from the
   child's RSS ("28 – 46 MiB above 15,680 KiB"). The child would not exist
   without the process route, so its interpreter floor is part of the cost,
   not part of the baseline — the two halves of the claim's own sentence
   ("43,744 – 61,552 KiB extra" vs "28 – 46 MiB above the floor") disagree by
   a whole interpreter.
2. **The marginal is smaller than the child.** In the no-worker arm the parent
   grows by **24.1 / 28.7 MiB**, because it then runs the solve itself. The
   number an install actually pays is (parent + child) − (parent alone) =
   **30,960 / 49,440 KiB**, not the child's whole RSS. The finder had the
   right perturbation ("the parent RSS must rise instead") and did not net it
   out of the headline.
3. **The child is numpy and scipy, not this integration.** A fresh interpreter
   that imports only `numpy` and `scipy.optimize` measures 65,696 / 71,840
   KiB; the child measures **1.09× and 1.17×** that (0.84× on the first run).
   Almost none of the resident image is integration code, and
   `subprocess.Popen([sys.executable, ...])` (`coordinator.py:757-762`) means
   no copy-on-write sharing on Linux either, so the Pi extrapolation is at
   least the right shape.
4. **RSS on this box is not a settled number.** The same child measured
   55,024 / 57,056 / 78,144 KiB across three runs in one session, and the
   parent 38,864 / 49,872 / 78,704 KiB; `swapins` rose from 29.36 M to
   30.18 M during my session on an 8 GB box. A single `ps -o rss=` read can
   land **below** what a process holds — my first run's parent read 38,864 KiB
   while a bare interpreter that merely imports numpy and `scipy.optimize`
   reads 67,376 KiB. Any absolute RSS band from this box, the finder's
   included, is a range of instrument readings.
5. **Duty cycle corroborated.** 0.046 % of a 30-minute interval on my quiet
   run, 0.21 % on the loaded one, against the claim's 0.055 %. The
   "held for ~29.98 of every 30 minutes" framing is right.
6. **Null control passes.** The flat-price arm gives the same worker RSS class
   (51,888 vs 57,056 in `h3`), so it is not a property of the priced arm.

**Why the severity stays `low` rather than dropping.** The mechanism is real
and the order of magnitude — tens of MiB resident for a sub-0.1 % duty cycle,
never released until `EVENT_HOMEASSISTANT_STOP` — survives every attack. Only
the band and the subtraction do not.

---

## Summary

| id | vote | severity I would give | my number | metric |
|---|---|---|---|---|
| D9-01 | **refute** | `info` if anything is kept | `pooled_redundant_share` **0.38159**; `verdict.wasted_work_share` **0**; `rank0_wins_share` **0.4706** | work-weighted share of L-BFGS-B work in non-improving runs; share of grid work removable with no cell losing objective or step-0 action |
| D9-02 | **weaken** | `low` | `shadow_ratio` **1.000** at a non-binding cap, **0.745 / 1.118** when it binds; **1** advisor solve over 3 cycles; **1** optimize entry with no fuse configured | step-equivalents per entry into `HeatPumpOptimizer.optimize` in one `_async_update_data` |
| D9-03 | **weaken** | `low` | `fallback_over_process_tick_rate` **0.168**; fallback `starvation_share` **0.895 / 0.905 / 0.8965**; process route **17.3 – 23.7 ms** longest hold against a **1.9 – 8.2 ms** idle floor | heartbeat tick rate ÷ the same session's idle arm on a real loop + real `ThreadPoolExecutor` |
| D9-04 | **weaken** | `low` (unchanged) | `route_marginal_rss_kib` **30,960 / 49,440**; `worker_over_numpy_scipy_floor` **1.088**; `idle_duty_share` **0.000464** | (parent + child) with the worker − parent in an interpreter that never spawned one |

### Files

Harnesses I wrote: `verify-1/v1_starts_policy.py`, `v2_fuse_shadow.py`,
`v3_loop_starvation.py`, `v4_worker_rss.py`, `v5_winner_rank.py`.
Outputs: `v1.out`, `v2.out`, `v3.out`, `v3-quiet.out`, `v4.out`,
`v4-quiet.out`, `v5.out`, `rerun-h1.out`, `rerun-h5-baseline.out`,
`rerun-h5-starts1.out`, `rerun-h4.out`, `rerun-h4-quiet.out`,
`rerun-h3-quiet.out`, `quiet-watch.log`.

### What I could not settle

- Every millisecond and every KiB here is provisional. `load1` never fell
  below 8.5 in the ~45 minutes I watched for it (`quiet-watch.log`), so the
  D9-03 and D9-04 windows were taken at 8.8 – 13.3 and reported with their
  load beside them, as `tools/audit/README.md` asks. The D9-03 numbers moved
  materially between `load1` 10.6 and `load1` 8.8 — a judge re-take on a
  genuinely quiet box would be worth having for that finding alone.
- I did not test whether an adaptive multi-start rule keyed on something other
  than the pre-refinement score could recover part of D9-01's 79.5 %. My
  measurement rules out the two rules the finding names or implies; it does
  not prove no rule exists.
- `tests/stress.py` was not run, so I did not check whether the stress gate
  would catch a regression in any of these paths.
