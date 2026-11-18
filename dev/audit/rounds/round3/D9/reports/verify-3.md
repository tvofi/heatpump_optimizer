# D9 — verifier 3 of 3, refute-first, and the quiet-window re-taker

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. 8-core Apple M1, 8 GB,
python 3.11.5, OpenBLAS. Everything run from the tree root with
`PYTHONPATH=tests/hastub`. No `gh`, no GitHub, no other verifier's output, no
register. `tests/stress.py` was **not** run, no `./tests/run.sh` was run, the
gate lock was **not** taken; `tests/stress.py:reference_solve` was imported and
called as the CPU ruler only.

New files, all under `tools/audit/round3/D9/verify-3/`: `v3_gap.py`,
`v3_ticker.py`, `v3_worker_mem.py`, `v3_relocate.py`, `v3_multistart.py`, and
the `.out` / `.pre` transcripts of every run below. No production or test file
was edited; every hook is a runtime monkeypatch inside a harness.

## The window was not as quiet as dispatched — say it plainly

Dispatch stated `load1` 4.8 and ~1.3 GB swap free. At my first pre-run check
(02:08:40) it was **`load1` 7.27** with **625 MB swap free**, and over the
session it ran **5.4 – 23.9**, with 8 other `python3` processes on the box and
`vm.swapusage` showing 8.8 – 8.9 GB of swap in use throughout. `pgrep -fl
"stress\.py"` and `pgrep -fl "tests/run\.sh"` returned **no pids** before every
run — exclusive of the gate scripts, not exclusive of the box.

(One transcript, `h4-take2.pre`, shows two `ps aux | grep -E
"[s]tress\.py|[t]ests/run\.sh"` matches. Those are that command's **own
invocation shell**, whose command line contains the pattern text; the
`[s]`-bracket trick does not defeat self-matching through a `zsh -c` wrapper.
I switched to `pgrep -fl` afterwards, which cannot self-match. No gate script
ran at any point.)

Per dispatch I gated on `thread_factor`, not on `load1`. **Every RESULT below
came in at `thread_factor` 0.99977 – 1.00081, so nothing was rejected and
nothing needed re-taking on that bar.** Every number was taken twice, separated
in time, and both are reported.

---

## The table

`orig` = the finder's reported value. `quiet-1` / `quiet-2` = my two re-takes.
`conc` = concurrent `python3` processes at the pre-run check (`stress.py` /
`run.sh` count was 0 for all).

| finding | metric | orig | quiet-1 | quiet-2 | load1 (1/2) | thread_factor (1/2) | conc | reproduced? |
|---|---|---|---|---|---|---|---|---|
| **D9-01** | `grid.redundant_share_mean` | 0.5605 | 0.560532 | — (bit-exact, once) | 15.26 | 0.999816 | 8 | **yes, bit-exact** |
| D9-01 | `grid.total_step_equivalents` | 573,024 | 573,024 | — | 15.26 | 0.999816 | 8 | yes, bit-exact |
| D9-01 | `STARTS=1` total | 117,408 | 117,408 | — | 12.40 | 1.0001 | 8 | yes, bit-exact |
| D9-01 | **pooled** share (mine) | *not reported* | **0.38159** | — | 15.63 | 0.999986 | 8 | n/a — new |
| D9-01 | permutation null (mine) | *absent* | **0.4169** [p05 0.3177, p95 0.5143] | — | 15.63 | 0.999986 | 8 | n/a — new |
| **D9-02** | `fuse_first_cycle.step_equivalents` | 45,888 | 45,888 | — | 16.41 | 1.00017 | 8 | **yes, bit-exact** |
| D9-02 | `fuse_rate_limited.step_equivalents` | 22,944 | 22,944 | — | 16.41 | 1.00017 | 8 | yes, bit-exact |
| D9-02 | ratio | 2.000× | 2.000× | — | 16.41 | 1.00017 | 8 | yes |
| D9-02 | flat null control | 93,120 / 46,560 | 93,120 / 46,560 | — | 16.41 | 1.00017 | 8 | yes, bit-exact |
| **D9-03** | `inprocess_fallback.starvation_share` | 0.889 / 0.830 | **0.897829** | **0.895682** | 6.99 / 5.91 | 1.00001 / 1.00007 | 5 / 8 | **yes — at/above the top of band** |
| D9-03 | `inprocess_fallback.longest_gil_hold_ms` | 40.5 / 49.5 | 41.2775 | 35.3945 | 6.99 / 5.91 | 1.00001 / 1.00007 | 5 / 8 | yes (t2 below band) |
| D9-03 | `process_route.starvation_share` | 0.0055 / 0.0764 | **0** | **0** | 6.99 / 5.91 | 1.00001 / 1.00007 | 5 / 8 | **no — and see below** |
| D9-03 | `process_route.longest_gil_hold_ms` | 5.1 / 8.3 | 4.497 | 3.060 | 6.99 / 5.91 | 1.00001 / 1.00007 | 5 / 8 | below band |
| D9-03 | `idle.starvation_share` (NULL CONTROL) | 0.006 – 0.033 | **0.121531** | 0.013442 | 6.99 / 5.91 | 1.00001 / 1.00007 | 5 / 8 | **no — 3.7× above band** |
| D9-03 | `idle.longest_gil_hold_ms` (NULL CONTROL) | 6.4 – 25.8 | 24.669 | 7.645 | 6.99 / 5.91 | 1.00001 / 1.00007 | 5 / 8 | in band, and the band is the problem |
| D9-03 | `thr_solve.starve` (mine, own metric) | *absent* | **1.0000** med | **1.0000** med | 8.67 / 10.49 | 1.00004 / 1.00006 | 8 | n/a — new, confirms direction |
| D9-03 | `sub_cpu.starve` (mine, shipped-route shape) | *absent* | **0.1334** med | **0.0735** med | 8.67 / 10.49 | 1.00004 / 1.00006 | 8 | n/a — new, voids comparator |
| D9-03 | `idle_5msHB.starve` (mine, zero work) | *absent* | **0.9978** med | **0.9985** med | 8.67 / 10.49 | 1.00004 / 1.00006 | 8 | n/a — new, voids metric at period≈cutoff |
| **D9-04** | `priced.worker_rss_kib` | 43,744 – 61,552 | **63,968** | **53,120** | 6.94 / 8.07 | 0.99988 / 1.0001 | 8 / 8 | q1 **above** band, q2 in band |
| D9-04 | `flat.worker_rss_kib` | (same band) | 49,568 | 51,024 | 6.94 / 8.07 | 0.99988 / 1.0001 | 8 / 8 | in band |
| D9-04 | `bare_interpreter_rss_kib` | 15,680 – 15,936 | 15,536 | 14,976 | 6.94 / 8.07 | 0.99988 / 1.0001 | 8 / 8 | **below** band both takes |
| D9-04 | worker RSS after **300 s idle** (mine) | claim implies 43,744–61,552 | **6,064** | **4,592** | 5.90 / 7.40 | 1.00081 / 1.00007 | 8 | **no — 7–10× below** |
| D9-04 | worker physical footprint, idle (mine) | *absent* | 60,620 flat | 56,115 flat | 5.90 / 7.40 | 1.00081 / 1.00007 | 8 | n/a — new, this one holds |
| D9-04 | `floor_scipy` RSS / footprint (mine) | *absent* | **65,040 / 51,507** | — | 16.79 | 1.00021 | 8 | n/a — new, voids the floor |
| D9-04 | `priced.deep_sizeof_slope_b_per_cycle` | −4 | −4 | −4 | 6.94 / 8.07 | 0.99988 / 1.0001 | 8 | yes, exact |
| D9-04 | `priced.traced_peak_bytes` | 4.98e5 | — | 497,588 | 8.07 | 1.0001 | 8 | yes |

---

## My assigned line of attack: THE METRIC

### The idle null control is not a control

`h4_loop_thread.py` takes four arms **sequentially**, each over its own wall
time, and compares them to one `idle` arm taken once at the start of the
process over a fixed 2.0 s. In my quiet-window take 1, taken minutes apart in
the same process:

```
RESULT idle.starvation_share=0.121531        <- NO SOLVE RUNNING AT ALL
RESULT idle.longest_gil_hold_ms=24.669
RESULT process_route.starvation_share=0      <- a real solve running
RESULT process_route.longest_gil_hold_ms=4.49704
```

**The null control reported 12.2 % starvation and a 24.7 ms worst gap with
nothing running; the arm it is meant to bound reported 0 % and 4.5 ms.** A
floor that sits above the arm establishes nothing about the arm. Between my two
takes the same idle arm moved 0.1215 → 0.0134, a 9× swing, while the box's
`load1` moved only 6.99 → 5.91.

### What the instrument actually reads — `v3_gap.py`

My own harness runs six arms **round-robin over 5 passes** with **identical
1.000 s windows**, so drift hits every arm alike and `starvation_share` is
comparable across arms (the finder's windows are 0.71 – 2.05 s and the share is
not). Each window is measured simultaneously by `v3_ticker.py`, a 1 ms tick
loop in a **separate process** with no asyncio and no shared GIL — the machine
noise floor taken *under* the arm rather than before it.

| arm | what it models | starve med (take 1 / take 2) | longest ms med (1 / 2) | EXT starve med (1 / 2) |
|---|---|---|---|---|
| `idle` | the finder's null control | 0.0346 / 0.0000 | 10.95 / 3.14 | 0.0077 / 0.0000 |
| `thr_sleep` | busy executor holding no GIL | 0.0057 / 0.0000 | 5.68 / 3.12 | 0.0000 / 0.0000 |
| `sub_cpu` | **the shipped process route's shape** | **0.1334 / 0.0735** | **33.93 / 32.75** | 0.0133 / 0.0316 |
| `thr_solve` | **the #511 fallback's shape** | **1.0000 / 1.0000** | **63.78 / 51.50** | 0.0417 / 0.0000 |
| `idle_sleepHB` | idle, cheaper heartbeat | 0.0221 / 0.0000 | 8.44 / 2.46 | 0.0072 / 0.0000 |
| `idle_5msHB` | **idle, heartbeat period = cutoff** | **0.9978 / 0.9985** | 17.52 / 7.46 | 0.0055 / 0.0000 |

Three things follow, both takes agreeing:

1. **The in-process GIL holder is real and the finder is right about it.**
   `thr_solve` — `reference_solve` looped in a real `ThreadPoolExecutor`,
   nothing to do with the coordinator — pegs `starve` at **1.0000** while the
   external ticker in another process sees 0.0000 – 0.0417. The machine was
   fine; only the measured interpreter was starved. That is positive proof the
   effect is the GIL, and it is *worse* than the finder's fallback arm.

2. **"The process route is clean" is unmeasured, not measured.** `sub_cpu` is
   the same CPU work moved into a separate process — the shipped route's
   shape — and it reads **0.0735 – 0.1334 share and ~33 ms longest gap**, i.e.
   2 – 25× the finder's `process_route` figures (0.0055/0.0764, 5.1/8.3 ms), in
   the same instrument in the same session. The difference between the finder's
   `process_route` reading and mine is not the GIL; it is how much other CPU
   happened to be running. The asyncio heartbeat is also ~4–10× more sensitive
   to plain CPU contention than a bare tick loop is (`sub_cpu` in-process 0.133
   vs EXT 0.013), so it *amplifies* machine noise rather than rejecting it.

3. **The metric is coupled to the instrument's own period.** `idle_5msHB` is an
   idle loop doing **nothing**, with the heartbeat period set to the 5 ms
   cutoff: it reports `starve` **0.9978 / 0.9985**. `starvation_share` is a
   joint function of (heartbeat period, scheduler jitter, GIL holds) and is only
   interpretable when the period sits far below the cutoff. At the finder's 1 ms
   period the measured `gap_p50` is already 1.20 – 3.24 ms — within 1.5 – 4× of
   the cutoff, not far below it.

And the cutoff is not an independent choice:

```
sys.getswitchinterval() = 0.005 s
GAP_CUTOFF in h4        = 0.005 s
```

**"Gaps over 5 ms" is exactly "another thread held the GIL for at least one
CPython switch interval".** On any in-process CPU-bound work the metric is ≈1.0
by CPython's design. So the fallback arm's 0.83 – 0.90 is a true statement
about CPython, and the integration-specific quantity inside it is *how long the
solve runs* — 0.67 – 1.20 s of cycle wall in my quiet takes, not the 0.99 s the
report carries.

**Verdict on the assigned attack: the instrument's noise floor is comparable to,
and on two arms exceeds, the signal on the process-route arm. It does not touch
the fallback arm's 0.83 – 0.90, which reproduced at 0.8978 / 0.8957 and hit
1.0000 in my own instrument. It voids the "process route is clean" half — the
`against 0.0055/0.0764 and 5.1/8.3 ms` clause of D9-03 and non-finding #4 —
which must be struck or restated as an upper bound below the instrument's
resolution.**

---

## D9-01 — the aggregate is a grid artefact, and the metric has no null

`h5_multistart_grid.py` re-ran **bit-exact**: 85 of its 88 RESULT lines
identical to `h5.out` — all 64 per-cell lines and all 10 `grid.` lines — the
three that differ being `thread_factor`, `load1` and `swapins`. The
`HPO_D9_STARTS=1` perturbation likewise: 573,024 → 117,408 (4.88×), and the
flat null-control cells 45,024 → 10,080 and 55,776 → 8,544. Contention-immune,
as claimed. The counts are not in doubt.

The **aggregation** is. `grid.redundant_share_mean` is an unweighted mean of 16
per-cell ratios over cells that differ in cost by 38× (2,304 to 88,224
step-equivalents) — and on the finder's own output the cheap cells carry the
high shares (`1z/summer_typical` 5,376 equiv, share 0.936) while the cells that
dominate the grid's cost carry the low ones (`2z/winter_narrow` 88,224 equiv,
share 0.156). `v3_multistart.py` reuses h5's own hooks unchanged and only
re-aggregates:

```
RESULT grid.total_in_lbfgs_equiv=559008
RESULT grid.total_redundant_equiv=213312
RESULT grid.mean_of_ratios=0.560532          <- the finder's headline
RESULT grid.POOLED_SHARE=0.38159             <- the share of in-solver work
```

The claim says *"56.05 % of in-solver step-equivalents go to non-improving
multi-starts"*. That sentence names the pooled quantity and reports the
mean-of-ratios. **The share of in-solver step-equivalents is 38.16 %.** (The
report's own prose gives 213,312 of 573,024 = 37.2 % two lines below the
headline, so both numbers are in the report and the larger one was promoted.)

Worse, there is no null for the metric. A multi-start cannot know which start
will improve until it has run it; the starts that improve on the running best
are the **record minima** of the sequence, whose count has expectation
H(4) = 2.083, so a perfectly working 4-start scheme still reports a large
"redundant share" by arithmetic alone. I measured that floor on this grid's own
numbers — 2,000 random permutations of the run order within each of the 17
`_multi_start_minimize` groups:

```
RESULT grid.perm_null_mean=0.416872
RESULT grid.perm_null_p05=0.317706
RESULT grid.perm_null_p95=0.51434
RESULT grid.pooled_minus_perm_null=-0.0352822
```

**The observed pooled share (0.3816) sits inside the null's 90 % interval and
below the null's mean.** There is no measured excess redundancy: the shipped
ordering is very slightly *better* than chance, not worse. `redundant_share`
measures the arithmetic of record minima, not removable work.

Two further method notes:

- The `HPO_D9_STARTS=1` perturbation drives `redundant_share` and `best_gain`
  to 0 **by construction** — with one run there is no earlier run to fail to
  improve on. The harness header says as much ("by construction"). It is a
  definitional identity, not a discriminating test. The only informative part is
  the 4.88× work drop, which is near-tautological for 4 starts → 1.
- The harness's own EXPECTED band fails on the finder's own recorded output on
  two of five lines: header `grid.best_gain_mean < 0.005` vs recorded
  **0.0118173**, and header `flat_vs_priced.step_equiv_ratio > 1.5` vs recorded
  `2z` = **1.13762**. A judge re-running this harness against its header would
  read a non-reproduction. The report's "Disproved lead" section shows the finder
  found the second one and did not carry the correction back into the header.

**What survives and is worth an owner decision:** four L-BFGS-B starts cost
**4.88×** what one costs across the grid and buy a mean `best_gain` of
**0.0118** (max 0.1337, **zero in 7 of 16 cells**). That is a real unmetered
cost/benefit. "56 % of the solver's work is waste" is not.

## D9-02 — exact, premise sound, consequence overstated

`h1_solve_work.py` re-ran **bit-exact**: 74 of its 77 RESULT lines identical
to `h1.out`, the three that differ being `thread_factor`, `load1` and
`swapins`. `fuse_first_cycle` 45,888 / 2 `optimize()` calls against
`fuse_rate_limited` 22,944 / 1 — **2.000×** — and the flat null control 93,120
against 46,560, also 2.000×. The perturbation (pre-setting `_fuse_advisor_at`
and `_fuse_advisor["month"]`, which is production's own rate-limit state)
collapses it exactly.

Premise verified by reading, not inferred: `coordinator.py:1726-1727` sets
`self._fuse_advisor = {}` and `self._fuse_advisor_at = None`; the only
assignments are at `:8096` and `:8104`, at runtime; `"fuse_advisor"` is written
into the published data dict at `:7014` and read back nowhere. **Both** guard
clauses at `:8061-8063` are memory-only — the `< 7 days` test and the
`_fuse_advisor.get("month") == month_key(now)` test — so a mid-month restart
re-runs it.

Two attacks land on the severity, not the number:

- **Scope.** `DEFAULT_MAIN_FUSE_A = 0` (`const.py:391`) and `_fuse_kw()` returns
  `None` when `amps <= 0`, so `_maybe_run_fuse_advisor` returns before any of
  this on an install that has not configured a main fuse. This is not a
  default-install cost; the harness arm sets `main_fuse_amperes: 20`.
- **It does not block the loop.** The shadow solve goes through
  `async_simulate` → `_await_optimize` → the **process worker**. The report ties
  it to "the situation the owner described as having made the whole instance
  unreachable"; that attribution is not supported by this mechanism. The cost is
  one extra child-process solve on the first cycle, ~0.7 – 0.9 s of M1 CPU off
  the loop thread, once per restart/reload, then not again for 7 days.

## D9-04 — the number was taken at the one moment the claim is not about

Three separate problems, each with an executed number.

**(a) The claimed band is one slice of a very wide distribution.** Across six
post-solve readings in my session, `worker_rss_kib` was **13,584 / 23,056 /
53,120 / 54,464 / 57,904 / 63,968 KiB** — a 4.7× spread on identical code. Two
fall below the claimed 43,744 – 61,552 band, one above it. `bare_interpreter_rss_kib`
came in at 15,536 and 14,976, below its claimed 15,680 – 15,936 both takes.

**(b) The retention half is contradicted, twice.** The claim is about the
**idle** window — *"holding 43,744 – 61,552 KiB resident … for the ~29.98 of
every 30 minutes it is idle"*. `h3_memory.py` reads `ps -o rss=` **immediately
after the solve**, at peak residency, and the claim extrapolates that instant
across the idle window. `v3_relocate.py` holds the worker and re-reads it:

| idle | run 1 `worker_rss_kib` | run 2 `worker_rss_kib` | footprint (both) |
|---|---|---|---|
| t=0 (post-solve) | 13,584 | 23,056 | 60,620 / 56,115 |
| 10 s | 7,696 | 22,976 | flat |
| 30 s | 7,728 | 22,976 | flat |
| 60 s | 8,832 | 21,952 | flat |
| 120 s | 6,944 | 6,256 | flat |
| **300 s** | **6,064** | **4,592** | flat |

After five minutes idle the worker's RSS is **4.6 – 6.1 MiB**, 7 – 10× below
the claimed band, monotonically declining. Its **physical footprint** stays
flat, so the pages are compressed rather than freed — the memory is still owed
on the ledger, but it is not resident, which is the metric the claim is stated
in. *Confound the judge should weigh:* this box ran with 8.8 – 8.9 GB of swap
in use all session, so macOS reclaims aggressively. A Raspberry Pi without swap
would not necessarily decay the same way. The re-take settles the claim **on
this box**, which is where it was taken.

**(c) The floor is the wrong floor.** `v3_worker_mem.py` measures all three in
one session:

```
RESULT floor_bare.rss_kib=12512    floor_bare.footprint_kib=5617
RESULT floor_numpy.rss_kib=27056   floor_numpy.footprint_kib=17920
RESULT floor_scipy.rss_kib=65040   floor_scipy.footprint_kib=51507
RESULT route.worker_rss_kib=57904  route.worker_footprint_kib=59699
```

A bare `python3 -c "import numpy, scipy.optimize"` already costs **65,040 KiB
RSS / 51,507 KiB footprint**. The solve worker's whole image is **at or below**
that. "28 – 46 MiB above a bare-interpreter floor" charges the integration for
the numpy/scipy stack that any process running this solve must load. Against
the scipy floor the integration's own marginal image is single-digit MiB.

**What does survive, and it is the useful form of the finding:** the child is a
genuine *duplicate*, not a relocation. `v3_relocate.py`, one arm per fresh
interpreter (a single process cannot measure this — `ru_maxrss` is a high-water
mark, which is why `v3_worker_mem.py` dutifully reported a relocation cost of
exactly 0 KiB):

```
arm=route   parent_peak_rss_kib=87808   worker_rss_kib=54464  worker_footprint_kib=58880
arm=inline  parent_peak_rss_kib=92208   worker_alive=0
```

Moving the identical solve into the parent raises the parent's peak by only
**4,400 KiB**, while the child owns **~56 – 61 MiB of physical footprint** that
stays flat while idle and is released only at `EVENT_HOMEASSISTANT_STOP`
(`coordinator.py:822-831`) or the `atexit` backstop. So the honest statement is
*"the process worker costs a second Python+numpy+scipy image, ~52 – 61 MiB of
physical footprint, held for the life of the entry, to buy the GIL escape that
D9-03 measures"* — a real low-severity cost, and the deliberate #199/#290/#511
trade against D9-03, not a leak and not 28 – 46 MiB of integration data.

---

## Attacks run that did **not** land (recorded, in the finding's favour)

- **The `FakeHass` trap.** `tests/harness.py:147` confirms
  `FakeHass.async_add_executor_job` runs the function inline on the calling
  thread. `h4_loop_thread.py` does **not** use it: `LoopHass` wraps a real
  `asyncio` loop and a real `ThreadPoolExecutor`. D9-03 avoids the trap.
- **Reachability in real HA.** `break_worker()` replaces only the module-level
  `_await_process`; the branch that runs is production's own
  `except ProcessWorkerUnavailable` at `coordinator.py:926-929`, which
  re-submits through `hass.async_add_executor_job`. The fault shape is the one
  `_note_worker_fallback` and the persistent repair issue exist for, and that
  shipped in v6.3.15 per the code comment. The path is real.
- **The two GIL yields.** The report's claim that they cannot bound the fallback
  is correct: `optimizer.py:429` sits in the
  `for solve_index, (_, guess) in enumerate(scored[:_MULTI_START_SOLVES])` loop
  (between starts) and `optimizer.py:5498` at the stage seam. Neither is inside
  an L-BFGS-B iteration.
- **D9-04's `deep_sizeof` and `tracemalloc` non-finding (#5).** Slopes of −4 and
  +8 B/cycle, 24 collections, traced peak 497,588 B, all reproduced exactly.
  One note for the judge: on the shipped route `tracemalloc` never sees the
  solve, which runs in the child, so `traced_peak_bytes` is the coordinator's
  bookkeeping, not the process's peak.

## Instrument notes for the judge

- `h4`'s `flat_warm.loop_cpu_over_reference` read **0.4506** in my take 2
  against the header's 0.137 – 0.191 band for the loop-CPU arms. The loop-CPU
  ratio is a small difference of small numbers (12.7 ms vs 7.4 ms of thread
  CPU) and is noisier than its band admits; non-finding #3 should carry a wider
  band or more samples.
- `h4`'s warm cycle wall came in at **672 – 883 ms** in the quiet window against
  the 0.99 s the report extrapolates its Pi figures from. Every Pi sentence in
  the report should be rescaled by ~0.7 – 0.9.
- `h3`'s `HPO_D9_NOWORKER=1` arm takes **>600 s** against 23 s for the default
  arm, because `tracemalloc` is active across the cycles and, with the solve
  in-process, traces every allocation the solver makes. Its memory figures are
  inflated by the tracer and should not be compared to the default arm's.
