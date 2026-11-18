# D9 round 3 — verifier 2 of 3, refute-first

- Baseline SHA re-measured: `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`.
- Tree: `.../verify/D9-2`, the finder's harnesses copied in at
  `tools/audit/round3/D9/`. Every harness run from the repository root with
  `PYTHONPATH=tests/hastub`, so the `ROOT = Path(".")` / `__file__` root-rule
  trap in `tools/audit/README.md` does not apply: `d9lib.py` sets
  `ROOT = os.getcwd()` and I never `cd`'d.
- Box: 8-core Apple M1, 8 GB, shared, macOS 26.6, python 3.11.5.
  `load1` over my runs ranged **6.4 – 37.9**; `thread_factor` **0.9997 – 1.0004**
  on every run, inside the 1.05 bar. `concurrent_stress_procs = 0` throughout.
- No `tests/stress.py` sweep, no `./tests/run.sh`, no gate lock.
  `tests/stress.py:reference_solve` was imported as a ruler by `h4` only.
- Assigned line of attack: **consequence on the actual target hardware**.
- My Pi extrapolation factor is the finder's, adopted as an assumption and not
  independently sourced: **a Raspberry Pi 4B runs this CPython+NumPy workload
  4–8× slower per core than this M1**. Three things in this dimension do *not*
  take that factor and I say so where it matters: a **starvation share** is
  dimensionless (the loop is starved for the same *fraction* of a solve on a
  Pi; only the absolute window lengthens), **resident memory** scales with the
  host's RAM and not with its clock, and an **interpreter import** is
  I/O-bound on SD-card storage in a way a CPU factor understates.

## 0. Box conditions, stated once

This box was **swapping hard** during the session and that is load-bearing for
D9-04. `vmmap` on a child that had imported nothing but `numpy` and
`scipy.optimize` reported `Physical footprint: 50.6M` while `ps -o rss=` for the
same process read **21,696 KiB**, with `ReadOnly portion of Libraries: Total=901.2M
resident=113.8M(13%) swapped_out_or_unallocated=787.3M(87%)` and `Writable
regions: ... swapped_out=43.9M`. `d9lib.swapins()` climbed from 29,361,855 to
30,022,576 across my runs. Any `ps` RSS number taken here is a reading of what
happened to be paged in, not of what the process owns.

## Summary of votes

| id | vote | severity | the number I would put on it |
|---|---|---|---|
| D9-01 | weaken | low | work-weighted redundant share **0.38159**, not 0.5605; cutting to the finding's own perturbation costs **+14.24 SEK/day** over the grid |
| D9-02 | verify | medium | cycle wall ratio **2.43–2.66×** (worse than the 2.000× step claim), **+2,240 ms**, **+155 ms** of loop-thread CPU, on an opt-in population |
| D9-03 | weaken | low | my own real-entry-condition run: starvation **0.888–0.913** vs healed **0.181** vs idle **0.110**; and the state raises **1 persistent repair issue** and clears after **1** good cycle |
| D9-04 | weaken | low | stable metric is **58,266–60,006 KiB** physical footprint, of which **~50,278–51,405 KiB** is a second numpy+scipy image; the stated 43,744–61,552 KiB did not reproduce (**33,024 KiB**) |

---

## D9-01 — multi-start redundancy

### Re-run of the finder's harness, verbatim command

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h5_multistart_grid.py`
→ `verify-2/h5.v2.out`, `thread_factor=1.00014`, `load1=6.41943`, `swapins=29362964`.

**Exact reproduction, every cell, to the digit.** `grid.redundant_share_mean
=0.560532`, `grid.best_gain_mean=0.0118173`, `grid.cells_with_zero_gain=7`,
`grid.total_step_equivalents=573024`, `grid.total_redundant=213312`.

Stated perturbation `HPO_D9_STARTS=1` (`verify-2/h5.starts1.out`,
`thread_factor=1.0002`, `load1=37.8569`): 573,024 → **117,408** (4.879×), every
share and gain to 0. Direction **down**, as claimed.

### Attack 1 — the headline is a mean of ratios sold as a share of work

The report's sentence is *"56.05 % of in-solver step-equivalents go to
multi-start runs that do not improve the incumbent"*. That is a share of work.
`grid.redundant_share_mean` is the **unweighted mean of 16 per-cell ratios**,
and the cells differ in size by 38× (2,304 to 88,224 step-equivalents).

My harness `verify-2/v2_reaggregate.py` imports `h5_multistart_grid`'s own
`install()` and `cell()` — same hooks, same numerator — and aggregates as a
ratio of totals (`verify-2/v2_reaggregate.out`, `thread_factor` 0.9999):

```
grid.total_in_runs              = 559008
grid.total_redundant            = 213312
grid.in_runs_share_of_all       = 0.97554
grid.unweighted_mean_share      = 0.560532     <- the reported figure
grid.work_weighted_share        = 0.38159      <- what the sentence claims
grid.work_weighted_over_unweighted = 0.680764
```

**The share of in-solver step-equivalents is 0.38159, not 0.5605.** The headline
overstates by **1.469×**. The mechanism is the classic one: the two smallest
cells (`2z/summer_typical`, `2z/summer_negative`) carry **0.402 % of the grid's
work each** and contribute **0.800** apiece to the unweighted mean, while the
largest cell (`2z/winter_narrow`, 15.4 % of the work) contributes **0.156**.
The finder's own leave-one-out drops the *largest share*, which does not touch
this at all.

38 % is still a lot, and I am not disputing that some solver work does not move
the incumbent. I am disputing the number printed beside the claim.

### Attack 2 — the money side (my assigned angle)

The finder measured **objective** gain and stopped. `tests/profiles.py` and
`tests/backtest.py:score` exist, and the owner's brief for this dimension is
about what a user loses. I wrote `verify-2/v2_money_multistart.py`: the same 16
cells, `_MULTI_START_SOLVES` rewritten for the comparison arm, and the solved
plan priced two ways — production's own `OptimizationResult.predicted_cost`,
and `tests/backtest.py:score`'s `cost` re-derived by exec'ing that function's
source out of the file (it cannot be imported: it runs its checks at import and
`sys.exit`s). **The two agreed to the digit in all 16 cells**, which is the
cross-check that they are the same quantity.

Self-null control, `HPO_D9_STARTS=4` (both arms shipped):
`grid.cells_identical=16`, `grid.total_delta_sek_day=0`, and the grid total
reproduced at `725.345 SEK/day` in both runs. So the deltas below are solver
path differences, not nondeterminism.

| starts | grid step-equivalents | vs 4 | grid ΔSEK/day vs 4 | cells dearer | worst cell |
|---|---|---|---|---|---|
| 4 (shipped) | 573,024 | — | 0 | 0 | — |
| 3 | 418,848 | −26.9 % | **+1.610** | 3 | `1z/flat` +2.137 |
| 2 | 277,536 | −51.6 % | **+2.521** | 4 | `2z/winter_narrow` +2.558 |
| 1 | 117,408 | −79.5 % | **+14.236** | 7 | **`2z/winter_typical` +11.678** |

`2z/winter_typical` — a two-zone Nordic house on a Jan-2025 SE3 curve, which is
the archetype this integration exists for — costs **67.890 → 79.568 SEK/day, a
17.2 % rise**, when the starts are cut to the finding's own perturbation value.
That is the same cell the finder names as "the single best cell" for
`best_gain` (0.13366) and then sets aside.

This is not an accident of this audit. `optimizer.py:193-200` records that
`_MULTI_START_SOLVES` was raised *because* the D0-02 audit "measured the
DISCARDED candidate refining below the shipped result in 5 of 10 price
profiles". The parameter is a paid-for money decision, and the finding does not
say so.

Honest limits on my own control: I predicted `flat` would null out and **it did
not** (+2.137 / +0.903 SEK/day at starts=1). The reading is that the extra
starts do not buy price arbitrage — they buy plan quality on a non-convex
objective, which survives a flat tariff. Two cells go the other way
(`1z/shoulder` −1.600, `1z/winter_moderate` −1.904): in both the 4-start plan
has the *lower objective* and the *higher* `predicted_cost`, i.e. the 1-start
plan ended the horizon with less stored heat. `predicted_cost` excludes
`deferred_energy_cost` by construction (`optimizer.py:841-845`), so those two
cells are a metric boundary, not a win.

### Attack 3 — `redundant_share` is not a measure of removable waste

At `starts=3` it is still **0.512237**; at `starts=2`, **0.447438**. Cutting a
quarter of the work barely moves it. It reaches 0 only at `starts=1`, where it
is 0 *by construction* — with one refined run there is no earlier run for a
later one to fail to improve on, which the harness header concedes ("best_gain
must go to 0 by construction"). A metric that is structurally bounded away from
zero for any multi-start method is measuring that the method is a multi-start
method.

The finding's named mechanism — "no early exit on a tie" — is also not
implementable as stated: a run is only known to have reproduced the incumbent
*after* it has been paid for. The only saving on offer is running fewer starts,
which is the table above.

### Attack 4 — is the cost already gated?

Yes. `tests/stress_budgets.json` carries **51** per-scenario entries, each with
a `ratio` against the reference solve plus `rss_peak_mb` and `traced_peak_mb`,
policed at `SCENARIO_BUDGET_FACTOR` 3.0 with `DETECTION_TARGET=2.0`
(`tests/stress.py:258-290`). The multi-start's CPU cost cannot silently grow.

### Vote

**weaken**, severity **low**. The phenomenon is real and exactly reproducible;
the headline number is wrong by 1.47× for the sentence it is attached to; the
cost it proposes to remove was bought deliberately and costs **+14.24 SEK/day**
across the grid (**+11.68**, 17.2 %, on the archetypal cell) to give back; and
the metric goes to zero by construction under its own perturbation. What
survives as actionable: the top of the ladder is cheap to trim —
**4 → 3 buys back 26.9 % of solver work for +1.610 SEK/day across 16
day-scenarios** — and nobody has priced that trade before now.

---

## D9-02 — the fuse advisor's memory-only rate limit

### Re-run of the finder's harness, verbatim command

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h1_solve_work.py`
→ `verify-2/h1.v2.out`, `thread_factor=0.999713`, `load1=6.52539`.

**Exact reproduction.** `fuse_first_cycle.optimize_calls=2`,
`step_equivalents=45888`; `fuse_rate_limited=1 / 22944`; flat arm
93,120 / 46,560. **2.000× in both arms**, as claimed. The mechanism is confirmed
by reading: `coordinator.py:1726-1727` initialises `_fuse_advisor = {}` and
`_fuse_advisor_at = None`, `:7014` publishes `_fuse_advisor` into the data dict,
and nothing restores either — while eight `Store`s restore other state
(`:1415, 1548, 1605, 1666, 1691, 1774, 1834, 1846`).

### Consequence on the target hardware — my assigned questions

**How long is that cycle, and is it doubled in seconds?** The count harness
cannot say. `verify-2/v2_pi_consequence.py` measures it on a **real asyncio
loop with a real `ThreadPoolExecutor` and the real process worker**, against a
pre-set-guard control built the same cold way (`verify-2/v2_pi.out`,
`thread_factor=0.99993`, `load1=24.3081`; every ms is **provisional**, the
ratios are what travel):

| arm | wall ms | loop-thread CPU ms | longest loop block ms | starvation share |
|---|---|---|---|---|
| idle, no cycle (NULL CONTROL) | 2000.68 | 209.00 | 13.32 | 0.110 |
| no fuse configured, warm | 1257.71 | 119.06 | 15.70 | 0.143 |
| **fuse first cycle (guard `None`)** | **3803.05** | **298.44** | **116.18** | **0.344** |
| fuse, guard set by that cycle | 1427.59 | 142.96 | 14.05 | 0.201 |
| fuse, guard pre-set (PERTURBATION) | 1563.41 | 158.59 | 24.56 | 0.236 |

`A.wall_ratio_first_over_limited = 2.664`, `A.wall_ratio_first_over_preset =
2.433`, `A.extra_wall_ms = 2239.64`, i.e. the extra cycle is **1.78× a whole
ordinary cycle**. The perturbation moves it **down**, as the finding states.

**This is worse than the finding claims.** The step count says 2.000×; the wall
says 2.43–2.66×, because `async_simulate` (`coordinator.py:10679+`) also does
two `copy.deepcopy`s of the config and thermal params, `_forecast_arrays`, and
`simulate_wood_slots` — and all of that is on the loop thread, not in the
worker. Loop-thread CPU rises **+155 ms** and the longest single loop block
goes **14.05 → 116.18 ms** (one sample; the next-highest arm is 24.56 ms).
On the 4–8× band that is a **0.46–0.93 s contiguous event-loop block** on the
first cycle after every restart.

**Is the second solve on the executor or on the loop?** On **neither** — it is
on the **process worker**. `_maybe_run_fuse_advisor` → `async_simulate` →
`_await_optimize` (`coordinator.py:914`) → `_await_process` → the child
interpreter. So the *solve* CPU is entirely off HA's process. What lands on the
loop is the 155 ms of marshalling above.

**Does it land while HA is starting every other integration?** **No, and the
finder's strongest sentence is wrong.** `__init__.py:234` sets
`coordinator._skip_solve_once = True` *before*
`async_config_entry_first_refresh()`, and `coordinator.py:4593-4596` consumes
it into `_async_first_refresh_light()`, which fetches and publishes **without
solving**. The real first solve is a background task created at
`__init__.py:258-266`, after `async_forward_entry_setups`. The comment there
says this exists precisely because "on modest hardware ... a Python-heavy cold
solve add[s] up to minutes during which the whole instance is unresponsive".
So the claim that this "lands on the worst possible cycle ... which is the
situation the owner described as having made the whole instance unreachable"
describes a path that was deliberately closed. It lands on the first
*background* cycle, concurrent with the tail of startup, with the solve in a
child process.

**Population.** `const.py:391` `DEFAULT_MAIN_FUSE_A = 0`, and `_fuse_kw()`
(`coordinator.py:7931-7938`) returns `None` at `amps <= 0`, so
`_maybe_run_fuse_advisor` returns on its second line for any install that never
set a main fuse. `config_flow.py:1460` puts that field on the
`grid_connection` page with default 0. A fuse of 16 A also exits (no smaller
rung in `FUSE_LADDER_A`). **The finding applies only to installs that set a
main fuse above 16 A.**

### Vote

**verify**, severity **medium**. The defect is real, exactly reproducible, and
the consequence is *larger* than the finding claims in wall terms (2.43–2.66×,
+2,240 ms, +155 ms on the loop, a 116 ms loop block). The fix is one persisted
timestamp. Two corrections belong in the record: it does **not** land inside
`async_setup_entry` (the skip-solve flag closed that), and it affects only
fuse-configured installs. Neither is enough to drop it below medium, because on
the affected population the first post-restart cycle really does cost
two-and-a-half cycles: on the 4–8× band the guard-set cycle is **6.3–12.5 s**
of Pi wall and the guard-lost one adds **9.0–17.9 s** on top of it.

---

## D9-03 — the #511 in-process fallback

### Re-run of the finder's harness, verbatim command

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h4_loop_thread.py`
→ `verify-2/h4.v2.out`, `thread_factor=1.0001`, `load1=29.1528`,
`swapins=29987938`.

**It did not reproduce, by the harness's own stated criterion.** The header
says: *"A run whose `inprocess_fallback.starvation_share` is not at least 5x the
`process_route` figure has not reproduced the finding."* I measured

```
idle.starvation_share               = 0.660529   <- NULL CONTROL, no solve at all
idle.longest_gil_hold_ms            = 129.483
process_route.starvation_share      = 0.873206   <- the SHIPPED route
process_route.longest_gil_hold_ms   = 286.185
inprocess_fallback.starvation_share = 0.921700
inprocess_fallback.longest_gil_hold_ms = 128.698
ratio fallback/process              = 1.06x      (criterion: >= 5x)
```

`process_route.wall_ms` was 20,692.6 against the finder's 1,836.0 — **11× the
cycle**. The box was thrashing, and at that point the instrument cannot tell the
fallback from an idle loop: the null control itself sits at 0.661. Per the
verifier contract this is **not** a refutation — a timing mismatch alone is
`unresolved` until the judge re-takes it on a quiet box. I record it as
evidence about the instrument's discriminating power, not as a verdict.

### My own instrument, with the REAL entry condition

The finder's `d9lib.break_worker()` replaces `_await_process` so it raises. That
exercises production's `except ProcessWorkerUnavailable` branch, which is honest,
but it never spawns the child and so never shows what a genuinely broken install
pays. I hooked **`coordinator._worker_env`** instead, returning an environment in
which the child cannot resolve the job's modules. `process_worker.run_worker`
then answers `load-err` from its own code, `_run_in_process` raises
`ProcessWorkerUnavailable` from its own code, and the whole path from
`_ensure_worker` down is production's.

`verify-2/v2_pi_consequence.py` section B (`load1=24.3081`, `thread_factor=0.99993`):

| arm | starvation share | longest loop block ms | wall ms |
|---|---|---|---|
| idle, no cycle (NULL CONTROL) | 0.110 | 13.32 | 2000.68 |
| broken, cycle 0 / 1 / 2 | **0.888 / 0.898 / 0.913** | 65.76 / 78.44 / 67.92 | 1469.8 / 1630.2 / 1473.6 |
| cause removed, next cycle (PERTURBATION) | **0.181** | 18.47 | 2265.97 |

**The effect reproduces in my hands**: 0.888–0.913 against a healed process
route at 0.181 (**4.9×**) and an idle floor at 0.110 (**8.1×**), in one session
at one load. The finder's 0.889 / 0.830 land inside my range. So the phenomenon
holds even though `h4`'s own numbers did not reproduce.

Starvation share is **dimensionless**: a Pi is starved for the same ~0.89 of the
solve. What scales by 4–8× is the window — the finder's 0.79 s of M1 fallback
solve becomes **3–6 s**, and the longest single block 65.8–78.4 ms becomes
**0.26–0.63 s**.

### How an install *gets* there, and how long it stays

**Entry.** `_run_in_process` (`coordinator.py:834-862`) raises
`ProcessWorkerUnavailable` on exactly three causes: pipes missing, a transport
error (the child exited), or `load-err` (the child could not unpickle the job).
The original #511 cause — the package not importable under both spellings — is
**fixed at this baseline** by `_worker_env` (`:726-749`) exporting both
`custom_components` and its parent. What is left for a Pi is a child that
**dies**: OOM-kill is the plausible one, and it ties this finding to D9-04.

**One entry condition does *not* reach the fallback at all.** `_ensure_worker`'s
`subprocess.Popen` sits *outside* `_run_in_process`'s `try` (`:836-840`), so a
spawn failure — `OSError`/`EAGAIN`, which is what a memory-pressured Pi
produces — propagates past `_await_optimize`'s `except ProcessWorkerUnavailable`
and becomes an `UpdateFailed`, not a degraded solve. Established by reading,
not executed. I am **not** filing this (it is not my finding and I did not
measure it); I record it for the judge because it bears directly on "how does an
install get into the fallback".

**A cost the finder did not count.** On `load-err`, `_run_in_process` sets
`_PROCESS_WORKER = None` and `run_worker` returns, so the child is gone. The
next cycle's `_ensure_worker` therefore Popens a **fresh interpreter that
imports numpy and scipy and fails again** — on top of the in-process solve, every
cycle. Established by reading `:834-860` and `process_worker.py:69-79`, and
consistent with the one `_ensure_worker` call per cycle I counted. On this box a
spawn+import is **1.21 s** (D9-04 below); on the 4–8× band, **4.8–9.7 s of Pi
core** per cycle, on an install that is already slow.

**Does it surface to the user?** **Yes, and clearly.** My first attempt said
zero repair issues; that was *my* instrument bug — `v2_pi_consequence.py` handed
the coordinator the `LoopHass` wrapper and then counted issues on the inner
`FakeHass`, and the hastub stores the list on whichever object it is handed.
Corrected in `verify-2/v2_fallback_surface.py` (`load1=14.1133`):

```
healthy.cycle0/1.issues   = 0, 0        warnings = 0, 0     (NULL CONTROL)
broken.cycle0/1/2.issues  = 1, 1, 1     warnings = 1, 1, 1
broken.cycle0.issue_ids   = solve_worker_fallback
broken.issue_persistent   = 1    severity = warning
broken.issue_translation_key = solve_worker_fallback
broken.warning_text = "Process-solve worker unusable (ProcessWorkerUnavailable:
    process worker cannot load the job: No module named 'homeassistant');
    solving in this process instead. ..."
healed.issues = 0    healed.warnings = 0    cleared_after_cycles = 1
```

The repair issue is **persistent**, carries the cause, and its user-facing text
(`translations/en.json` → `issues/solve_worker_fallback`) names the exact symptom
this finding measures: *"the solve holds the interpreter lock while it runs, so
Home Assistant may feel briefly unresponsive on each optimization"*, and tells
the user to report it. It is withdrawn after **exactly one** successful solve.
So "nothing bounds how long an install stays on the fallback" is true of the
duration and false of the visibility: the state is announced, diagnosable from
the notice alone, and exits on the first good cycle.

### Vote

**weaken**, severity **low**. The mechanism is real and I reproduced it with a
better entry condition than the finder's (0.888–0.913 vs healed 0.181, idle
0.110). But: the finder's own harness failed its own 5× criterion on my re-run
and its absolute figures want the quiet window; the degradation is a
**declared, persistent, self-clearing** fault notice that says exactly this, not
a silent one; the output is correct throughout; and the population is an install
that is already broken and is being told so. A `medium` is not earned by a
correct-but-slow path that raises a repair issue about itself. The judge should
re-take `h4` on a quiet box — my number, not `h4`'s, is the executed evidence I
am voting on.

---

## D9-04 — the solve worker's resident set

### Re-run of the finder's harness, verbatim command

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h3_memory.py`
→ `verify-2/h3.v2.out`, `thread_factor=0.999903`, `load1=18.5444`.

Every **count** reproduced: `coordinator_collections=24`, slope `-4` / `+8`
bytes/cycle, `traced_peak_bytes` 497,483 / 491,570 (header: 4.98e5 ±20 %),
`traced_slope` ~5.1e4. The no-unbounded-collection non-finding holds.

**The value the finding rests on did not.**

```
finder, run 1:  priced.worker_rss_kib = 43744
finder, run 2:  priced / flat        = 61552 / 52816
mine:           priced / flat        = 49040 / 33024
header EXPECTED: 43744-61552
```

33,024 KiB is outside the harness's own stated range. Across four of my own
measurements the same worker read **19,968 / 33,024 / 36,096 / 49,040 KiB**.

### Attack — `ps` RSS is the wrong instrument on this box

`verify-2/v2_worker_lifecycle.py` measures the same processes two ways:
`ps -o rss=` (the finder's metric) and `vmmap -summary`'s **Physical footprint**
— the dirty + compressed + swapped memory the task *owns*, the macOS analogue of
Linux `Private_Dirty`/USS.

| process | `ps` RSS, run A / run B | footprint, run A / run B |
|---|---|---|
| bare `python3` (NULL CONTROL) | 7,408 / 7,360 | 5,537 / 5,426 |
| child with only `numpy, scipy.optimize` | **56,976 / 21,712** (2.6× apart) | **50,278 / 51,405** (2.2 % apart) |
| the real solve worker after one real solve | **36,096 / 19,968** (1.8× apart) | **60,006 / 58,266** (2.9 % apart) |
| the parent | 30,448 / 24,976 | 66,560 / 65,741 |

`ps` RSS swings by 1.8–2.6× on identical work; the footprint is stable to 3 %.
The claim *"holds 43,744–61,552 KiB resident permanently"* is a statement about
what was paged in, not about what the host must find.

### What the number actually is, and whose it is

The stable figure is **58,266–60,006 KiB**, and of that **50,278–51,405 KiB is a
bare numpy+scipy interpreter**. The worker's marginal cost above that is
**~7–9 MiB** of integration code plus the solve's arrays.

The finder's counterfactual — a bare `python3` at 15,680–15,936 KiB — is the
wrong one. Home Assistant's own process already carries numpy and scipy:
`optimizer.py` imports `scipy.optimize.minimize` at module scope and the
coordinator imports `optimizer`. So the honest statement is *"a second
numpy+scipy image, ~58–60 MiB of owned memory"*, not *"28–46 MiB the
integration adds"*.

Share of a Pi, on the finder's own unmeasured ±30 % aarch64 assumption which I
also did not test: **5.6–5.7 % of a 1 GiB Pi 3B, 2.8–2.9 % of a 2 GiB Pi 4.**

### Is reaping better or worse for a Pi user? — my assigned question

**Worse, on both arms I can measure.**

*Arm 1 — run the solve in the parent instead* (`HPO_D9_NOWORKER=1`,
`verify-2/h3.noworker.out`, `thread_factor=0.999823`, `load1=16.4678`):

```
worker_rss_kib          0        (perturbation confirmed, direction to_zero)
priced.traced_peak      3,751,557 B   vs   497,483 B with the worker  (7.5x)
flat.traced_peak        2,260,337 B   vs   491,570 B                  (4.6x)
self_maxrss_kib_end     95,840        vs   78,128                     (+17.3 MiB)
```

The solve's allocation peak moves into Home Assistant's own heap, where it is
transient but has to be *available* — on a 1 GB host that is the same page
budget, now inside the process that must not be OOM-killed. And this arm **is
D9-03**: every install would be permanently in the 0.888–0.913 starvation state.

*Arm 2 — keep the worker but reap it between cycles*
(`verify-2/v2_worker.out` vs `verify-2/v2_worker.reap.out`; absolutes
**provisional**, load rose from 17.0 to 26.7 between the arms):

| | persistent (shipped) | reaped before every solve |
|---|---|---|
| cold solve | 7.229 s | 10.642 s |
| repeats | 3.979 / 6.018 / 7.400 s | 14.149 / 25.843 / 30.532 s |
| median repeat | **6.018 s** | **25.843 s** |
| cold / warm within the run | 1.201 | — |

Every repetition in the reaped arm exceeds every repetition in the persistent
arm by at least 2×, and the medians by **4.29×**. The clean within-run figure is
the persistent arm's own cold-minus-warm: **1.21 s of spawn + interpreter start
+ numpy/scipy import**, taken seconds apart in the same process. On the 4–8× band
— and this is the one place the band *understates*, because a Pi imports numpy
and scipy off SD-card storage — that is **4.8–9.7 s of extra wall on every
30-minute cycle** to give back ~58 MiB.

The finder's own supporting figure points the same way: cold-vs-warm cycle wall
1.61 s vs 0.99 s (my `h4` run: 2.845 s vs 2.008 s at `load1` 33.1). A "0.06 %
duty cycle" framing prices the idle worker at zero benefit, when what it buys is
that ratio, every cycle, forever.

### Vote

**weaken**, severity **low** (the finder already says low; I would say the
finding as *framed* is not supported at all). Three executed reasons: the stated
value does not reproduce (33,024 KiB against a stated 43,744–61,552); the metric
is wrong for the claim on a box whose `ps` RSS swings 2.6× on identical work,
and the stable metric says 58–60 MiB of which ~50 MiB is a second numpy+scipy
image the parent already pays for once; and the implied remedy is dominated —
reaping costs 4.8–9.7 s of Pi wall per cycle, and removing the worker converts
every install into D9-03. **D9-03 and D9-04 are the same design trade seen from
two sides and cannot both be acted on.** What is actionable: re-measure with a
footprint/USS metric before anyone quotes a number.

---

## Instrument notes for the judge

1. **`h5_multistart_grid.py`'s header EXPECTED block is stale** and contradicts
   the report on two of five stated expectations: it predicts
   `best_gain_mean < 0.005` (measured 0.0118, 2.4× over) and
   `cells_with_zero_gain >= 8 of 16` (measured 7). `redundant_share_mean`
   0.5605 sits on the bottom edge of the stated `0.66 ± 0.10`. A judge re-running
   it will see two failed expectations against a report that quotes the measured
   values honestly.
2. **`h4_loop_thread.py` has no load guard and its null control can exceed its
   signal.** At `load1` 29.15 the idle arm reported `starvation_share=0.661` and
   a 129 ms longest gap. The harness should refuse a run whose idle arm is above
   some fraction of its fallback arm.
3. **`d9lib.break_worker()` is a weaker entry condition than production's.** It
   replaces `_await_process`, so the per-cycle re-spawn a genuinely broken
   install pays is invisible. Hooking `_worker_env` instead reaches the same
   fallback through `_ensure_worker` → `run_worker` → `load-err` →
   `_run_in_process`, all production code.
4. **The `D9-01` / `D9-03` / `D9-04` ids in `optimizer.py` and `tests/stress.py`
   are a previous round's** (the batched-gradient widening, the per-scenario
   budget table, the memory pass). They are unrelated to this round's findings
   with the same ids. The finder noted seeing them; the collision is worth one
   line in the register so nobody merges the two sets.
5. **My own instrument bug, recorded because it nearly became a finding.**
   `v2_pi_consequence.py` reported `broken.*.issues = 0`, which would have said
   the fallback is silent. It was mine: the coordinator was handed the
   `LoopHass` wrapper and I counted on the inner `FakeHass`; the hastub's
   `issue_registry` stores the list on whichever object it is given.
   `v2_fallback_surface.py` corrects it and measures 1 persistent issue.

## Files

Under `tools/audit/round3/D9/verify-2/`:

| file | what |
|---|---|
| `h1.v2.out`, `h5.v2.out`, `h3.v2.out`, `h4.v2.out` | the finder's four harnesses re-run verbatim |
| `h5.starts1.out`, `h5.starts2.out`, `h5.starts3.out` | the stated `HPO_D9_STARTS` perturbation and two intermediate rungs |
| `h3.noworker.out` | the stated `HPO_D9_NOWORKER=1` perturbation |
| `v2_money_multistart.py` + `v2_money.out`, `v2_money.starts{2,3,4}.out` | my SEK harness and its four arms, including the `starts=4` self-null |
| `v2_reaggregate.py` + `v2_reaggregate.out` | work-weighted re-aggregation of h5's own grid |
| `v2_worker_lifecycle.py` + `v2_worker.out`, `v2_worker.reap.out` | footprint vs `ps` RSS, and the reap-cost perturbation |
| `v2_pi_consequence.py` + `v2_pi.out` | D9-02 wall on the real route; D9-03 through the real entry condition |
| `v2_fallback_surface.py` + `v2_fallback_surface.out` | what the #511 state shows the user, corrected |
