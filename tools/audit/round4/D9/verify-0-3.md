# D9 round 4 — verifier 3 of 3 (panel D9-0)

Stance: refute-first. I re-ran every finder harness named in my brief under
the gate lock, wrote two harnesses of my own, and attacked each finding in
the contract's order. Worktree `../audit-r4-verify-D9-3` at `ae2a60b`
(HEAD of `claude/13-dimension-audit-920935`); `git diff 7dd68dd HEAD` under
`custom_components/` touches only `manifest.json` and the card JS (version
stamps), so the solve code, `tests/stress.py` and `tests/stress_budgets.json`
are byte-identical to the baseline `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`.

**Lock discipline.** `d9-verify-1` held a live lease from 19:38Z; I waited
30 minutes rather than steal it (renewals observed at 20:09/20:14/20:17
expiries — all live). I held `d9-verify-3` 20:08–20:19Z for every run that
imports `tests/stress.py` (h9, h9 HORIZON=12, h7, h1, my mmap arm), renewed
between commands, released at the end. `concurrent_gate_procs=0` beside
every RESULT below. My own D9-05 harness never touches `stress.py`
(`d9common` imports it lazily inside `reference_solve()`, which I never
call), so it ran before the lock; its final metrics are counts and CPU/CPU
ratios, which load does not move.

**My harnesses** (both in this directory, root rule `ROOT = os.getcwd()`,
run from the worktree root, headers per the contract):

- `verify3_h9_profile.py` — D9-05 by two instruments of my own:
  `time.process_time()` hooks (CPU/CPU, not the finder's wall/wall) and
  `cProfile` cumtime (biased high: ~1 µs per Python call, and the row loop
  is Python-call dense — stated in the header). It also measures
  `row_loop_share_pct`, the metric h9's header promises and never prints.
- `verify3_h7_mmap.py` — D9-06's blind-spot arm executed standalone:
  the shipped probe body (`stress.build_case` under `tracemalloc` +
  `stress.rss_mb`) with an anonymous, page-touched `mmap` sized to 2× the
  recorded RSS peak, both shipped rules then applied to the probe's output.

---

## D9-05 — the batched objective re-computes the cost per row. VOTE: **verify** (medium, bug)

**Re-run of the finder's harness** (`h9_batch_cost_loop.py`, exact header
command, load1 2.56, thread_factor 0.999999, procs 0):

| metric | finder | quiet | my re-run |
|---|---|---|---|
| comfort_terms_calls_per_solve | 29 591 | 29 591 | **29 591** (exact) |
| comfort_terms_calls_per_gradient | 97.0197 | 97.0197 | **97.0197** (exact) |
| batch_rows_per_gradient | 96 | 96 | **96** (exact) |
| comfort_terms_cpu_share_pct | 33.331 | 32.690 | **33.500** |
| comfort_over_simulate_batch | 0.8599 | 0.8613 | **0.8637** |
| null control (flat − winter share) | +0.82 pp | +1.32 pp | **+0.71 pp** |

Perturbation re-executed: `H9_HORIZON=12` → calls/gradient **49.0299**
(finder's `h9_h12.out`: 49.0299, identical), rows/gradient 48, share 32.04%
(finder 32.01%). Direction down, proportional to the horizon. `h1_grad_cost.py`
re-run reproduces the supporting numbers exactly (`equiv_per_grad=194.833`,
29 280 batch rows, 305 grads, 5 `_scoped_minimize` calls).

**My own number, my own instrument** (`verify3_h9_profile.py`, load1 4.01,
thread_factor 1.000, procs 0):

- `comfort_calls_per_solve = 29 591`, `per_gradient = 97.0197`,
  `batch_rows_per_gradient = 96` — bit-identical to the finder by a
  second instrument.
- `comfort_cpu_share_pct = 32.38` — **a different clock and a different
  denominator** (process-CPU of `_comfort_terms` over the solve's
  process-CPU, not wall/wall). Agrees with the finder's 33.3 within 1 pp.
- `prof_comfort_share_pct = 31.04` (cProfile cumtime/wall; biased, see
  header) — agrees.
- `comfort_over_simulate_batch_cpu = 1.10` against the finder's wall-ratio
  0.86: under CPU clocks the cost loop is the *larger* of the two halves.
  Both instruments put the loop at the same order as the vectorized physics
  it decorates; the claim's substance is if anything strengthened, not
  weakened, by mine.
- `prof_row_loop_share_pct = 43.28` — the phantom metric, measured by me,
  lands inside the 25–55 band h9's header promised for it.
- **Leave-one-out arm (single-zone, no DHW): 97.14 calls/gradient, 96
  rows/gradient, CPU share 23.7%.** The loop is a property of the batch
  shape, not of the two-zone arm; the share is lower there because the
  single-zone `_comfort_terms` is cheaper per call (one zone, not two
  averaged).

**Attacks, in the contract's order.**

1. *Contention:* counts are contention-immune and bit-identical across five
   executions (finder, quiet window, my instrument, my h9 re-run, the
   horizon-12 arm). Shares span 31.0–33.5% across three instruments and two
   sessions — inside every stated band.
2. *Wrong gate mode:* not a suite claim; n/a.
3. *Aggregate artefact:* single-scenario counts, no grid to drop cells
   from; the single-zone arm is the shape control and holds.
4. *Null control:* flat prices move the share +0.71 pp (my re-run) on a
   33% effect — the control holds; this is a structural cost, not a price
   artefact.
5. *Reachability:* the batched jac is the live route — my instrument
   counted 29 280 `simulate_trajectory_batch` rows in the default solve;
   `_bounds_supported_by_batch`'s own docstring (`optimizer.py:322`) says
   the fast path serves per-step-capped and DHW-pinned bounds (38 of 39
   DHW-enabled golden scenarios) and the finder's `zero_range_fuse_cap`
   arm shows the fuse-guarded shape takes it too (195.02 equiv/grad, h1
   re-run of that figure not needed — the quiet window reproduced it
   exactly). The loop at `optimizer.py:3454` and `:5552` is verified by
   reading: one `simulate_trajectory_batch`, then `for b in range(B)`
   calling `_comfort_terms`, `energy_cost_of`, `cycling`, `capacity`,
   `terminal_cost` per row on 96-element slices.
6. *Severity:* medium is earned. It is a bounded, silent CPU cost (the
   solve is out of process, no stall, no wrong number); not high (nothing
   user-visible), not low (a third of every solve's CPU, with a concrete
   vectorization fix that #97 already wrote the blueprint for). The Pi
   extrapolation (7×) is labelled an assumption, as the brief requires.

**Metric definition (mine):** entries into
`heatpump_optimizer.optimizer:HeatPumpOptimizer._comfort_terms` per
L-BFGS-B gradient evaluation (`njev`=305) of the default two-zone DHW
solve, and `_comfort_terms` process-CPU ÷ solve process-CPU.

---

## D9-06 — the stress gate cannot see a 2× memory regression. VOTE: **verify** (medium, bug)

**My own arithmetic, from the executed module constants and the shipped
rule read at `tests/stress.py:2467-2475`** (not the harness's restatement):
`MEMORY_BUDGET_FACTOR=1.5`, `DETECTION_TARGET=2.0`, `MEMORY_TOP_N=6` over
the committed `tests/stress_budgets.json` — every FINAL number exact:

- 51 scenarios recorded; 45 never memory-probed in check mode; the six
  probe labels my computation selects are **exactly** the six the quiet
  window's full-gate run printed (`winter/cycle`, `winter/pv+cycle`,
  `heavy_old/shoulder`, `winter/pv`, `winter/2z/dhw`, `typical_slab/winter`).
- RSS multiple required to fail: **2.52905 – 2.64294**; traced: **2.07637 –
  3.82558**; **all 51 pass a 2× on both axes**; the leader `winter/pv`
  (98.1 MiB) must reach **248.1 MiB**.

**Re-run of the finder's harness** (`h7_memory_gate.py`, load1 3.57,
procs 0): every one of those numbers identical, plus the executed probe
arms — clean 85.5 MiB / 3.46 MiB traced; numpy-injected 135.9 MiB
(1.589× clean), `inject2x_rss_rule_fires=False`, `inject2x_traced_rule_fires=True`
(same behaviour as finder and quiet window).

**My own executed blind-spot arm** (`verify3_h7_mmap.py`, load1 2.66,
procs 0): an anonymous page-touched `mmap` sized to take the leader's RSS
watermark to 2× the recorded peak — RSS landed at **196.0 MiB = 1.998×
recorded**, traced stayed at **3.46 MiB = 1.00× recorded** (the mmap is
outside PyMem, exactly the blind spot `stress.py:1512-1514` documents),
and **both shipped rules stayed silent** (196.0 < 248.1; 3.46 < 7.19). A
numpy-internal 2× regression is invisible to the whole memory section, not
just to the RSS arm. This closes the one gap in the finder's own arm (its
numpy injection is tracemalloc-visible) and matches the quiet window's
end-to-end full-gate run (2.03× RSS / 2.00× traced injected into
`winter/pv` → **ALL 62 STRESS CHECKS PASSED**, with `ok the budgets are
tight enough to see a 2x regression` printed three lines below).

**Attacks, in the contract's order.**

1. *Contention:* nothing load-bearing is timed — the FINAL numbers are
   exact rationals of committed constants, and they reproduce to the digit.
2. *Wrong gate mode:* no. CI sets no `STRESS_*` variable
   (`.github/workflows/tests.yml:287-293`, read), so check mode runs on
   the defaults I verified.
3. *Aggregate artefact:* no grid — per-scenario arithmetic over all 51,
   worst case quoted.
4. *Null control:* the null is the rule's own behaviour on the clean tree
   (probe 79–86 MiB against threshold 248.1 — silent, correctly), and the
   injection is inert unless switched on (quiet window's three-arm table).
5. *The gate says the opposite about itself:* read at `stress.py:2654-2686`
   — the `_blind` list that backs `the budgets are tight enough to see a
   2x regression, uniform or confined to one scenario` is built only from
   `SOLVE_BUDGET_RATIO`, `SWEEP_BUDGET_RATIO`,
   `SCENARIO_BUDGET_FLOOR_RATIO` and `SCENARIO_WORK_FACTOR`. **No memory
   quantity enters it.** And `stress.py:466`'s own principle — a floor may
   not blind a scenario to a `DETECTION_TARGET`-fold regression — is
   violated by the `max(150.0, …)` term with no check over it. The
   `:1517-1519` claim that the interpreter+numpy baseline "cancels in the
   comparison" is false for an additive rule: the ~80 MiB baseline is
   *inside* the measured peak and inside the recorded peak, and the rule
   then requires the *sum* to grow by 150 MiB.
6. *Severity:* medium stands. The gate is what is wrong, not the product;
   the consequence is that a memory regression on the Pi-class target this
   dimension exists for lands undetected, and the gate's own output
   asserts coverage it does not have. The one mitigation I can construct —
   the 150 MiB floor as deliberate cross-platform RSS headroom, since
   baselines differ across runners — does not survive the file's own
   behaviour: it documents the traced arm's numpy blindness and leans on
   the RSS arm to cover it, and it is the RSS arm the floor blinds. The
   finder's fix scope (budget the scenario-attributable component against
   a same-run empty-probe baseline) answers portability and detection at
   once.

**Metric definition (mine):** the multiple of a scenario's recorded
`rss_peak_mb` its probe must reach before `tests/stress.py:2467`'s
`rss_peak > recorded + max(150.0, recorded × (MEMORY_BUDGET_FACTOR − 1))`
fires — minimum over the 51 committed scenarios — plus the executed mmap
arm showing both memory rules silent at 1.998×.

---

## D9-INST — harness-contract gaps. VOTE: **verify** (low, hygiene)

**(a) h2's thread_factor is not a BLAS signal, and the contract's
rejection rule cannot be satisfied by that harness as written.** The quiet
window measured **1.29034 / 1.29935 / 1.29** across three re-takes at
load1 3.16–3.42 with `concurrent_gate_procs=0`; re-taking does not fix it.
My own execution of the mechanism (`threadpoolctl.threadpool_info() == []`
— this numpy 2.4.6 box has **no BLAS threadpool at all**, so any factor
> 1.0 here is by definition genuine threads): the same numpy work
main-thread-only under the five pinned variables gives thread_factor
**0.9999**; the same work dispatched through a real `ThreadPoolExecutor`
gives **135.09**. `time.process_time()` sums every thread's CPU,
`time.thread_time()` only the caller's — and `h2_cycle.py` by design
pushes the cycle through a real executor (`RealExecHass`, exactly what
`tools/audit/README.md`'s FakeHass trap demands). The README therefore
requires two incompatible things of one harness: a real second thread
(the trap list) and `thread_factor ≤ 1.05` (the contract). The defect is
in the contract's wording — the rule assumes the ratio is a BLAS signal —
and per the README an instrument defect is a finding of the dimension.
Mechanism verified by construction; magnitude verified by the quiet
window's three re-takes.

**(b) h4/h5/h7/h8 print no `thread_factor` beside PROVISIONAL RSS figures.**
Verified by grep: `h4_retained.py:272`, `h5_worker_footprint.py:165`,
`h7_memory_gate.py:186`, `h8_leak_attrib.py:108` all call
`d9common.telemetry()` with no argument, and `telemetry(tf=None)` skips
the `RESULT thread_factor` line. Each of the four carries a PROVISIONAL
RSS or byte figure. The contract's rejection rule ("a timing or memory
RESULT whose `thread_factor` exceeds 1.05 is rejected") cannot be applied
to a harness that never prints the factor. (The same grep shows h3 and h6
also print no factor, but they carry no PROVISIONAL memory figure; the
quiet window's "four of seven" is the right count.)

**(c) Carried with it, verified:** `h9_batch_cost_loop.py`'s header names
`row_loop_share_pct` with an expected band (25–55 ± 8 pp) and the script
never prints it (grep: the only two hits are header docstring lines). I
measured it myself: **43.28%** (`prof_row_loop_share_pct`, cProfile,
biased high) — inside the promised band, so no number in the finding was
resting on a metric that does not exist, but the header is still wrong
about its own output.

**Severity:** low — hygiene of the audit instrument itself; no product
consequence; the consequence inside the audit is that a judge cannot apply
the contract's rejection rule to four of the seven re-executed harnesses
and must auto-reject h2's with no remedy.

**Metric definition (mine):** `time.process_time()/time.thread_time()` for
identical pinned numpy work run main-thread-only versus executor-dispatched
(0.9999 vs 135.09), against h2's measured 1.29 and the contract's 1.05 bar.

---

## What I could not do

- I did not re-run the ~9-minute full gate with the uniform2x injection:
  the quiet window already executed it end to end (§5 of
  `quiet-window.md`), and my standalone mmap arm reproduces its decisive
  property through the shipped probe body. Re-running it would have spent
  the lock without adding information.
- h1's `nobatch` perturbation arm was not re-executed by me (it is the
  47.8× counterfactual that supports a non-finding, not D9-05's claim);
  its captured output `h1_nobatch.out` and the quiet window's exact
  reproduction of `equiv_per_grad` stand.

## Environment

python3 = `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
numpy 2.4.6 / scipy 1.17.1, always `PYTHONPATH=tests/hastub` from the
worktree root, five BLAS variables pinned before numpy. Runs at load1
2.40–4.02, `concurrent_gate_procs=0` throughout, swapins 42 833 447 →
42 849 422 over the session.
