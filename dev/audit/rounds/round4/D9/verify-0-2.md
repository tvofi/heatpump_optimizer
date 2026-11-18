# D9 round 4 — verifier 2 report (panel D9-0, re-run)

- Worktree: `../audit-r4-verify-D9-2`, detached at `ae2a60b` (branch
  `claude/13-dimension-audit-920935`; production files identical to the
  finder's baseline `7dd68dd` for everything hooked here).
- Stance: refute-first. Finder report and quiet-window record read; no other
  verifier's output and no register column was read.
- Lock: `tests/stress.py`-touching runs (h9, h7, my probe arms) were made only
  under `tests/gate_lock.py` with label `d9-verify-2`, taken 20:14:43 UTC,
  renewed between commands, **released 20:50**. The box was contended before
  that: verifier 1 held the lease 19:38–~20:05 running memory probes of their
  own, verifier 3 ~20:09–20:14; I waited rather than steal a live lease.
  `concurrent_gate_procs` is quoted beside every number below; `load1` ran
  2.5–5.3 through my session.
- My own harness: `tools/audit/round4/D9/verify2_h9_sample.py` (in this
  worktree, uncommitted) — same thread pin, own builder, no `d9common` import,
  no stress import, so it needed no lock.

## D9-05 — the batched objective's per-row cost loop

**Re-run.** Executed under the lock once it freed (verifier 1 held it
19:38–~20:05 UTC running their own memory probes; verifier 3 ~20:09–20:14;
mine 20:14–20:50, renewed between commands, released at the end). Every FINAL
number reproduces: `comfort_terms_calls_per_solve=29591`, `per_gradient=
97.0197`, `batch_rows_per_gradient=96`, `njev=305` — bit-identical to finder
and quiet window; `comfort_terms_cpu_share_pct=33.2618` (finder 33.331, quiet
32.6895; band ±5 pp), `simulate_batch=38.5433` (38.76/37.95),
`comfort_over_simulate_batch=0.862974` (0.8599/0.8613); null control share
delta **+0.774 pp**, calls delta **+0.0036612** — the flat-price control
holds in my run too. `thread_factor 0.999998`, `load1 2.57`,
`concurrent_gate_procs 0`.

**My own way (`verify2_h9_sample.py`).** A statistical sampling profiler:
`signal.setitimer(ITIMER_PROF, 0.001, 0.001)` — CPU-time ticks, re-armed —
whose handler walks the interrupted Python stack and counts samples whose
stack contains `_comfort_terms` (resp. `simulate_trajectory_batch`). The
finder's h9 accumulates `perf_counter` inside a wrapper; sampling and wrapper
accumulation fail differently (a wrapper exaggerates cheap-but-hot functions;
a sampler under-attributes long C calls), so agreement is evidence, not
tautology. One macOS trap, recorded for whoever reuses this: `setitimer`
without the third (interval) argument is ONE-SHOT — it fires exactly once and
the run reports 1 sample; the re-arm argument is mandatory.

Two-zone DHW solve (same arm shape as h9's `winter_typical`):

```
comfort_calls_per_solve          = 29591      (finder/quiet: 29591, exact)
comfort_calls_per_gradient       = 97.0197    (finder/quiet: 97.0197, exact)
batch_rows_per_gradient          = 96         (finder: 96, exact)
njev                             = 305
comfort_share_by_sampling_pct    = 30.47      (finder 33.331, quiet 32.6895)
simulate_batch_share_by_sampling = 38.55      (finder 38.7611, quiet 37.9522)
comfort_over_simulate (samples) = 0.79        (finder 0.8599, quiet 0.8613)
solve wall 1.54 s, thread_factor 0.999999, load1 3.96, procs 0
```

The sampled share is 2.2 pp under the quiet-window instrumented share, inside
h9's own ±5 pp band; binomial sd at 978 samples is 1.5 pp. Space-only
topology (`V2_NO_DHW=1`, exercising the `:3432` twin): share 34.81 %, calls
97.0259/grad, 22510 calls over 232 grads — the loop cost is not an artefact of
the DHW arm.

**Code reading.** Both twins confirmed at the cited lines:
`optimizer.py:3432` (`objective_batch`, space-only) calls
`simulate_trajectory_batch` once for all B rows then `for b in
range(power_matrix.shape[0])` at `:3454`; the with-DHW twin at `:5528` loops
at `:5552`. Each row calls `_comfort_terms`, `energy_cost_of`, `cycling`,
`capacity`, `terminal_cost` on 96-element slices. `_comfort_terms`
(`optimizer.py:1560`) is np.sum reductions over `[n]` slices (8-9 per call,
two-zone branch) — exactly the shape that vectorizes to nine reductions over
`[B, n]`.

**Attacks, in the contract's order.**

- *Contention.* The share is a ratio inside one solve; my sampled share at
  load1 4-5 agrees with the quiet window's 4.31 within 2.2 pp. Not
  contention-borne.
- *Wrong gate mode.* Not a mutant claim; N/A.
- *Aggregate artefact.* Dropped the DHW half of the claim entirely: the
  space-only twin shows the same 97/grad and 34.8 % share. The finder's
  horizon perturbation (`H9_HORIZON=12`, captured in `h9_h12.out`: 49.0299
  calls/grad, 48 rows/grad, share still 32.01 %) shows the count is the batch
  width, not a constant; I did not re-execute that arm, and nothing in my
  verdict rests on it.
- *Null control.* Flat-price control is the finder's and the quiet window's
  (share delta +0.82/+1.32 pp — an order below the effect). I did not re-take
  it; nothing in my attacks questions it.
- *Reachability.* The loop is on the shipped route: the process worker runs
  the same `optimize()` (the counts above are from direct calls to it), the
  default bounds are batch-supported, and h2 (run here) confirms the solve
  goes out-of-process (0 in-process `_multi_start_minimize` per cycle) — the
  cost is real CPU in the worker, but never blocks the event loop.
- *Severity.* Medium is earned as scored: a bounded, silent ~33 % solve-CPU
  item, no wrong number, no user-visible stall; high would need a user-facing
  consequence. The Pi extrapolation is labelled an assumption in the report.

**Vote: verify.** Every FINAL count reproduced bit-identically under my own
harness and hooks; the share reproduces inside h9's own band under an
independent measurement method.

## D9-06 — the stress gate's memory budget cannot see a 2x regression

**Re-run (under lock).** All eleven FINAL numbers reproduce exactly:
`scenarios_recorded=51`, `memory_top_n=6`, `scenarios_never_memory_probed=45`,
`detection_target=2`, `min/max_rss_multiple_required_to_fail=2.52905/
2.64294`, `scenarios_where_2x_rss_passes=51`, `min/max_traced_multiple=
2.07637/3.82558`, `scenarios_where_2x_traced_passes=51`,
`rss_fail_threshold_mb=248.1`, leader `winter/pv`. The executed arm
reproduces too: `inject2x_rss_rule_fires=False`, `inject2x_traced_rule_fires=
True` (the traced fire is the numpy-PyTraceMalloc artefact the finder
documents — a ~24x traced spike from a numpy allocation, not a 2x). Probe MiB
drifted as PROVISIONAL figures do (clean 83.9, inject 154.6 = 1.84x clean on
this pass) without touching the verdict. `load1 3.36`, `procs 0`. Note for
D9-INST: this harness prints no `thread_factor` — confirmed by execution.

**Rule fidelity (code reading).** `tests/stress.py:2467` fails RSS when
`rss_peak > recorded_rss + max(150.0, recorded_rss * (MEMORY_BUDGET_FACTOR -
1.0))`; `:2475` fails traced when `traced_peak > recorded_traced *
MEMORY_BUDGET_FACTOR + 2.0`; `MEMORY_BUDGET_FACTOR = 1.5` (`:476`,
`STRESS_MEMORY_FACTOR`), `MEMORY_TOP_N = 6` (`:483`), `DETECTION_TARGET =
2.0` (`:261`). h7's transcription is byte-faithful to all of it.

**My own arithmetic** (committed `tests/stress_budgets.json`, my own code, no
h7 import): 51 scenarios; RSS multiple-to-fail min 2.52905 / max 2.64294
(recorded peaks 91.3-98.1 MiB; 0.5 x 98.1 = 49.05 < 150 so the floor binds
everywhere); 51/51 scenarios pass at exactly 2.0x RSS; traced
multiple-to-fail 2.07637-3.82558 (recorded 0.86-3.47 MiB), 51/51 pass at
2.0x; `winter/pv` leader 98.1 MiB, threshold 248.1 MiB; the six check-mode
probe labels my own selection code reproduces are `winter/cycle`,
`winter/pv+cycle`, `heavy_old/shoulder`, `winter/pv`, `winter/2z/dhw`,
`typical_slab/winter` — 45 scenarios never probed. All eleven FINAL numbers
match the finder to the digit.

**The CPU-only detection check (code reading).** The check that prints
`ok the budgets are tight enough to see a 2x regression, uniform or confined
to one scenario` (`stress.py:~2680`) examines only `SOLVE_BUDGET_RATIO`,
`SWEEP_BUDGET_RATIO`, `SCENARIO_BUDGET_FACTOR`, `SCENARIO_BUDGET_FLOOR_RATIO`
and `SCENARIO_WORK_FACTOR` — every one a CPU/work budget. No memory constant
appears in it. It prints after the Memory (D9-04) section, unqualified, and a
reader of the output cannot tell the assurance is CPU-only. And
`stress.py:1509-1520`'s claim that the ~80-90 MiB interpreter+numpy baseline
"cancels in the comparison" is false for an additive rule: with the floor
binding, the threshold is `recorded + 150`, which the baseline shifts one for
one.

**Guard inventory (the "could anything else catch it" attack).** (a) the RSS
rule — 2.53x+ required, no; (b) the traced rule — 2.08x+ on the leader, and
numpy-internal/mmap growth is invisible to tracemalloc by the file's own
admission (`:1509-1512`); (c) `MEMORY_TOP_N` selection — 45 of 51 never
probed in check mode, and selection is by *recorded* peaks, so a scenario
that grows can't promote itself into the probe set; (d) the parent-512-MiB
check (`:2532`) — probes are subprocesses, their RSS never lands in the
parent's watermark; (e) the CPU work-count and budget checks — a pure memory
regression changes no solver evaluation count and need cost no CPU; (f) no
other `ru_maxrss`/`tracemalloc` guard exists anywhere in `tests/` (grep, only
stress.py); (g) CI sets no `STRESS_*` variable (`.github/workflows/tests.yml`
287-293) and `run.sh` runs stress.py as its own lane, so the defaults I
checked are the defaults that run. Nothing catches a 2x.

**Attacks, in the contract's order.**

- *Contention.* The FINAL numbers are rationals of committed constants; they
  reproduce exactly at any load. Only the probe MiB are provisional, and the
  verdict does not rest on them.
- *Wrong gate mode.* `--record-budgets` re-records, it does not check; the
  default `run.sh`/CI path is the check mode measured. No tighter mode exists.
- *Aggregate artefact.* "All 51" is not a mean over cells — it is a
  per-scenario minimum (2.52905) over the whole table; dropping any subset of
  scenarios cannot make 2.0x fail anywhere.
- *Null control / executed arm, mine.* Through the SHIPPED probe entry
  (`python3 tests/stress.py --memory-probe`, `winter/pv`, spec taken from
  `sweep_combinations()`), with an env-gated production-file injection — a
  retained, page-touched anonymous `mmap` sized off the live `ru_maxrss` at
  the top of `ThermalModel.simulate_trajectory_batch`
  (`custom_components/heatpump_optimizer/thermal_model.py`; the mmap models
  exactly the numpy-internal/allocator-external growth `stress.py:1509-1512`
  delegates to the RSS arm). Four arms under the lock:

  | arm | probe RSS | vs recorded 98.1 | vs live clean | traced | RSS rule |
  |---|---|---|---|---|---|
  | (a) edit present, env unset — null control | 83.0 MiB | 0.85x | 1.00x | 3.46 | silent (as expected) |
  | (b) env `V2_INJECT_MEM2X=98.1` (target 2.00x recorded) | 172.5 MiB | 1.76x | 2.08x | 3.48 | **silent** |
  | (c) `=110` (target 2.24x recorded) | 219.2 MiB | 2.24x | 2.64x | 3.47 | **silent** |
  | (d) `=128` (target 2.60x recorded) | 254.8 MiB | 2.60x | 2.98x | 3.47 | **FIRES** |

  The live edge brackets the computed threshold: silent at 2.24x, firing at
  2.60x, arithmetic says 248.1 MiB = 2.53x. Arm (b) undershot its 196.2 MiB
  target (the mmap is sized from the watermark at the first batch call, and
  macOS's final `ru_maxrss` accounting came in below the arithmetic sum) —
  which is why (c) exists: even a clean **2.24x** recorded regression passes
  with 29 MiB to spare, and a true 2.00x passes with 52. The traced axis
  never moved (3.44-3.48 throughout; recorded 3.46, threshold 7.19), so the
  traced rule is silent too — the mmap is invisible to tracemalloc by
  construction. The edit was inert without the env (arm a), and the tree was
  restored and verified byte-identical afterwards, with a post-restore clean
  probe at 85.7/3.44. Together with the quiet window's full-gate `uniform2x`
  run (2.03x RSS, 2.00x traced, ALL 62 STRESS CHECKS PASSED, three
  controls), the executed record is complete and independent.
- *Reachability.* The blind spot is reachable from production code: the
  single-line production mutation is a retained buffer in
  `custom_components/heatpump_optimizer/thermal_model.py`
  (`simulate_trajectory_batch`), e.g. `self._hold = np.zeros(...)`,
  sized to double the probe's RSS; the gate's memory section stays green.
- *Framing attack.* "2x" is the generous reading: the recorded peaks are
  ~91-98 MiB of which ~80+ MiB is interpreter+numpy baseline, so a 2x of the
  *scenario-attributable* memory (~2x of ~15 MiB) is even further below the
  150 MiB floor. The claim survives its most charitable interpretation.
- *Severity.* Medium is earned: the gate is the repo's regression net and its
  memory half is decorative against its own stated detection target, but no
  user-facing behaviour is wrong today.

**Vote: verify.** Every FINAL number reproduced exactly by my own arithmetic
and by the h7 re-run; the blind spot is executed through the shipped probe
entry from a production-file injection, with a firing control proving the
rule is alive above 2.53x and silent below it — 2.0x passes with margin on
both axes.

## D9-INST — harness-contract gaps

**Executed.** `h2_cycle.py` re-run here: `thread_factor = 1.28957` at load1
3.73, `concurrent_gate_procs 0` — the quiet window's 1.29 reproduced. The
cause is structural, by code reading of the harness I ran: `RealExecHass`
dispatches `async_add_executor_job` to a real `ThreadPoolExecutor`
(`h2_cycle.py:87`), and `main()` prints `telemetry(proc / thr)` over the whole
run — `time.process_time()` sums all threads, `time.thread_time()` counts
only the calling thread, so any second thread doing real work makes the ratio
exceed 1.05 regardless of box quietness. The contract's rejection rule
(`tools/audit/README.md`: "A timing or memory RESULT whose `thread_factor`
exceeds 1.05 is rejected and re-taken") therefore cannot be satisfied by that
harness as written: re-taking changes nothing (quiet window: 1.29034, 1.29935,
1.29 across three re-takes). The rule assumes the factor is a BLAS signal; in
the one harness that deliberately crosses a real executor boundary it
measures the executor under the same name.

**Code reading, second prong.** `d9common.telemetry(tf=None)` prints
`thread_factor` only when given one; `h4_retained.py:272`,
`h5_worker_footprint.py:165`, `h7_memory_gate.py:186` and `h8_leak_attrib.py:108`
all call `C.telemetry()` bare, so their RESULT blocks carry `load1`, `swapins`
and `concurrent_gate_procs` but no `thread_factor` — while each prints
PROVISIONAL RSS or byte figures (h4 worker RSS, h5 control/worker RSS, h7
probe RSS, h8 traced bytes) beside which the contract requires the factor. I
add one label the finding missed: `h3_payload.py:243` also calls `C.telemetry()`
bare — five harnesses, not four.

**Attacks.** *Severity:* this weakens no product finding — h2's numbers feed
non-findings 3/5, and D9-06's FINAL numbers are arithmetic — but the
contract's acceptance rule is unrunnable for h2 and unrunnable-on-missing-data
for four (five) others; per `tools/audit/README.md` ("a defect in an
instrument is a finding") it is a finding of the dimension, low severity,
fixable by wording (scope the rule to BLAS-shaped factors / require the
factor printed) or by h2 reporting the loop-thread factor it actually
measures. *Refutation attempt:* one could argue the executor CPU belongs in
the factor (it is real CPU) — but then the pinned-BLAS rationale
(process/thread inflation from threading libraries, canceling in ratios)
does not apply, and the same rule would reject every honest executor-boundary
measurement forever; that is the defect, not the defence.

**Vote: verify** (severity low).

## Machine notes

python 3.11.5 (`/Library/Frameworks/.../3.11/bin/python3`), numpy 2.4.6,
8-core M1, `PYTHONPATH=tests/hastub`, five BLAS variables pinned to 1 in every
run. `swapins` at my last RESULT: 42831714.
