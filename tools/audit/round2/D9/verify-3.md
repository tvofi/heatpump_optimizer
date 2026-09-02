# D9 verifier 3 of 3 — perturbation and fix scope

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree `audit-r2-D9`,
interpreter `tvofi-claude/.venv/bin/python` (3.13.1), `PYTHONPATH=tests/hastub`
from the worktree root, the five BLAS variables pinned to `1` before every
numpy import. `thread_factor` was **1.000 on every run** reported here. The box
was shared: `load1` 2.0–5.7, so every wall/CPU/RSS figure below is provisional
and every count, path and payload diff is final. `tests/run.sh` was not run and
`/tmp/hpo-gate.lock` was not taken. Scratch under `/tmp/verify-D9-3/`.

My angle: execute each finding's stated perturbation and confirm the number
moves in the stated direction, then judge whether the proposed fix would clear
the finding and whether the same defect class lives elsewhere.

**Harnesses re-run as their headers say:** `h1_grad_equivalents.py`,
`h7_stress_gate.py` (twice: gate defaults, then
`STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75`), `h1b_dhw_loops.py`,
`h3_gil_hold.py` (twice).

**Harnesses I wrote**, in this directory, each self-contained and runnable from
the repository root:

| File | What it adds |
|---|---|
| `v3_d901_fixscope.py` | an independent path metric, the pin/cap perturbation in the removal direction, four further zero-range producers, the proposed fix applied end to end, the `fuse_guard` capture with and without it, and what scipy's own L-BFGS-B does with a fixed variable |
| `v3_d901_golden_scan.py` | all 49 golden scenarios: which have zero-range bounds, and the field-by-field fixture diff under the fix at the fixtures' own stored precision |
| `v3_d903_memo_golden.py` | the D9-03 fix implemented as proposed (not the finder's stand-in), plus all 49 fixtures diffed under it |

---

## D9-01 — one zero-range bound sends the whole solve to scipy's scalar FD path

**Vote: verify (high).** Deciding number: `fev_per_jev` **1.00 → 96.0** on the
same solve when one bound is pinned, and back to 1.00 when the pin is removed,
with the returned plan element-for-element identical to the never-pinned solve.

**My metric (different from the finder's).** The finder counts
`simulate_step` calls plus `simulate_trajectory_batch` rows per `njev`. I take
the path out of scipy's own counters instead and hook no thermal model at all:

> `fev_per_jev` = Σ`OptimizeResult.nfev` / Σ`OptimizeResult.njev` over the
> L-BFGS-B runs of one solve. A supplied jac makes scipy call fun and jac once
> each per iterate, so the ratio is 1.0; a withheld jac makes scipy estimate the
> gradient with n+1 evaluations, so the ratio is n+1 = 97 at n = 96.

**My number** (`v3_d901_fixscope.py`, load1 5.19, thread_factor 1.000):

| case | njev | nfev | fev_per_jev | path | simulate_step |
|---|---|---|---|---|---|
| two-zone DHW, no pin | 103 | 103 | **1.00** | batched | 20,736 |
| + pin off at step 40 | 173 | 16,608 | **96.0** | scalar | 1,595,328 |
| + cap 0.8·p_max every step | 164 | 15,744 | **96.0** | scalar | 1,512,384 |

**The finder's own metric re-run** (`h1_grad_equivalents.py`, load1 2.04,
thread_factor 1.000) reproduces the report exactly: 297.32 and 9221.55
equivalents per gradient, 20,736 and 1,595,328 `simulate_step`, 9221.85 for the
cap, 294 for the single dodged cap step. No count differed by one.

**Perturbation — passes, in the removal direction.** Re-solving the *same* case
with `space_pins=None`: `fev_per_jev` 96.0 → 1.00, path scalar → batched,
`simulate_step` 1,595,328 → 20,736 (×76.9), equivalents 9221.55 → 297.32
(×31.0), and `matches_no_pin_plan=1` — the removal returns the byte-identical
plan, so the pin and nothing else is what moved the number.

**Reachability, checked in the coordinator, not assumed.**
`coordinator.py:4676-4688` feeds the opt-in fuse guard's
`np.clip(fuse_kw − baseline_house_load, 0.0, None)` into the **live**
half-hourly solve, and `_manual_pins` (`coordinator.py:4674`) feeds the pins
into the same call. This is not confined to the advisor's shadow solve. The cap
is clipped *at* 0.0, so a house whose baseline load reaches the fuse produces
exact zeros — and one exact zero is enough (below).

**Scope — zero-range producers besides forced-off pins and `power_caps_extra`.**
All executed:

| producer | source | zero-range bounds | fev_per_jev | simulate_step |
|---|---|---|---|---|
| forced-**on** pin at a step whose headroom equals min-on power | `_apply_pins_to_bounds`, `(min(min_on, high), high)` | 1 of 96 | **96.0** | 959,424 |
| a single exact `0.0` in `power_caps_extra` | the fuse-guard clip above | 1 of 96 | **96.0** | 1,300,416 |
| pump-mode gate blocks space heating | `optimizer.py:2132`, `power_caps = np.zeros(n)` | 96 of 96 | — | 1,152 |

The mode gate is the interesting negative: with *every* variable fixed,
L-BFGS-B exits at `njev = 0, nfev = 2` and costs nothing. So the defect needs
*some* free variables to bite — which is exactly the realistic shape. The
forced-**on** pin is a producer the report does not name at all, and the single
zero cap entry contradicts the report's own hedge that "a cap at a single step
is dodged"; that hedge holds at 0.8·p_max (measured, 294 equivalents) and fails
at 0.0.

Not executed, code-read only: `_tighten_buffer_caps` (`optimizer.py:2553`)
writes `power_caps[i] = max(0.0, allowed) * 0.999`, exactly `0.0` whenever
`allowed <= 0`, on throttling/buffer installs with no pin and no fuse guard
configured. Same shape, reached automatically. Worth a harness.

**Is the proposed fix numerically sound against scipy?** This is the part the
report argues rather than executes, and the `_bounds_supported_by_batch`
docstring argues the opposite. I executed it on a two-variable quadratic
`(x0−3)² + (x1−1)²` over bounds `[(0,0), (−5,5)]`:

| jac supplied | x | fun | status | nit |
|---|---|---|---|---|
| none (scipy estimates) | (0, 0.99995) | 9 | 0 | 2 |
| **NaN at the fixed entry** | (0, 0) | 10 | **2** | **0** |
| **0.0 at the fixed entry** | (0, 1.0) | 9 | **0** | 2 |
| the true (nonzero) entry | (0, 1.0) | 9 | 0 | 2 |

This reproduces the docstring's observation ("jac-supplied dies in the first
line search ... status 2") and then isolates its cause: **the NaN is the whole
problem.** A fixed variable's breakpoint in L-BFGS-B's Cauchy-point pass is 0,
so it is active from the first iteration and its gradient entry never enters
the search direction — which is why even the *true* nonzero entry is harmless.
The docstring's reason (0/0 is undefined) is right about the arithmetic and
wrong about the consequence. The finder's fix is sound.

**Fix applied end to end** (batch kept, `lo == hi` given a zero step and an
explicit `0.0` entry):

| case | fev_per_jev | simulate_step | max Δ power | Δ cost (rel) |
|---|---|---|---|---|
| pin, two-zone DHW | 96.0 → **1.00** | 1,595,328 → 36,096 (×44) | 2.0e-04 kW | 4.1e-07 |
| cap, two-zone DHW | 96.0 → **1.00** | 1,512,384 → 32,448 (×47) | 7.7e-05 kW | 9.5e-07 |
| golden `fuse_guard` | 94.0 → **1.00** | 731,904 → 16,128 (×45) | 4.5e-05 kW | — |

No NaN reaches any output; `fuse_guard` reports `status = "optimal"` both ways.
The mode-blocked all-fixed case still exits at `njev = 0` under the fix.

**Correction to the report's fix scope — the fixture does move.** The report
says the expected `fuse_guard` drift is "last-decimal at most, possibly none".
`v3_d901_golden_scan.py` over all 49 scenarios:

- exactly **1 of 49** has any zero-range bound, and it is `fuse_guard`
  (`capacity_curve` does not: its envelope floors at 0.6·p_max and never
  collapses the headroom);
- under the fix `fuse_guard`'s payload changes **177 fields** at
  `golden.PRECISION = 6`, max abs delta **4.5e-05** on `power_schedule[49]`.

`golden.py` compares exactly against that 6-decimal rounding, so the fixture
**must be re-recorded**. 45 mW on a kilowatt schedule is behaviourally nothing,
but "possibly none" is not what the fixture does, and a fixer who believes the
report will be surprised by a red gate. One implementation note: masking the
gradient *after* `_batch_fd_gradient` still raises
`RuntimeWarning: invalid value encountered in divide` at `optimizer.py:201`; the
zero step has to be taken before the division.

Severity `high` is earned by consequence, not by the ratio: a shipped, opt-in,
default-off-but-documented guard and the shipped manual-plan card both put the
live half-hourly solve at 685–721× the reference (quiet re-take) with the loop
starved for 0.998 of it.

---

## D9-02 — the stress gate cannot see a 2× uniform solve regression

**Vote: verify (medium).** Deciding number: at the shipped defaults an exact 2×
injected at `HeatPumpOptimizer.optimize` trips **0 of 48** per-scenario checks
and **0** sweep checks; at 400/75 the same injection trips **2** and **1**.

**Metric.** As the harness states: per-scenario ratio = scenario solve CPU /
trailing-median reference CPU against `SOLVE_BUDGET_RATIO`; sweep ratio = total
solve CPU / total reference CPU against `SWEEP_BUDGET_RATIO`; both CPU ratios
against `tests/stress.py:reference_solve`, so both are contention-immune.

**My number** (`h7_stress_gate.py`, defaults 1400/450, load1 3.43,
thread_factor 1.0005 / 1.0002):

| sweep | worst scenario | worst | median | sweep | per-scenario tripped | sweep tripped |
|---|---|---|---|---|---|---|
| plain | shoulder/tariff+pv+cycle | 298.68 | 35.73 | 53.36 | 0 | 0 |
| injected 2× | same | 604.95 | 69.97 | 106.86 | **0** | **0** |

`injected_over_plain_worst = 2.025`, `injected_over_plain_sweep = 2.003` — the
injection really is a 2×. `smallest_detectable_uniform_regression = 4.687`
(report 4.69). `ci_sets_stress_ratio = 0`, `tests_memory_instrumentation = 0`,
both re-executed.

**Perturbation — passes.** `STRESS_SOLVE_RATIO=400 STRESS_SWEEP_RATIO=75`
(load1 5.66): plain worst 306.81, sweep 53.09, **0 / 0 tripped** — the plain run
still passes; injected worst 622.64, sweep 113.46, **2 per-scenario tripped, 1
sweep tripped**. Exactly the stated direction on both arms.

**Scope — the proposed constants are the edge, not "leaves 2×".** The report
proposes ≈600 / ≈100. Measured across my two full sweeps: plain worst 298.68 and
306.81 (2.7 % apart on the *same box, same tree*), injected 604.95 and 622.64.
A 600 budget therefore catches the 2× by **0.8 %–3.8 %**, and CI runs on Linux
GitHub runners whose solve-to-reference ratio need not match this M1's at all.
The sweep half is better: 100 against a plain 53.1–53.4 leaves 1.88× on the
false-trip side and trips the injection by 6.9–13.5 %.

The reason a single re-sized constant cannot do much better is structural and is
in the finder's own data: the worst cell (298.7) is **8.4×** the median (35.7),
so the budget has to clear the worst cell, and the entire design headroom is
then exactly the regression factor it can detect. Per-scenario budgets — each
of the 48 cells against its own recorded ratio — would give 2× detection with
~2× margin per cell. That is the fix; re-sizing one global constant is not.

Two further stale figures the fix must also carry, only one of which the report
names: `SOLVE_BUDGET_RATIO`'s docstring (`tests/stress.py:165-176`) still says
the dearest scenarios cost 655× and 662× — measured 298.7; and
`SWEEP_BUDGET_RATIO`'s (`:180-192`) says "expected around 250 ... leaves that
estimate a factor of ~1.8" — measured 53.4, so the real margin is 8.4×.
The memory line the report proposes is additive and carries no drift; confirmed
that nothing in `tests/*.py` measures memory today.

---

## D9-03 — the batched jac re-evaluates f(x) scipy just computed

**Vote: verify (low).** Deciding number: with the proposed fix implemented as
described, `trajectories_per_gradient` **2.068 → 1.039** and **0 of 49 golden
fixtures change, 0 fields at precision 6**.

**My metric.** `trajectories_per_gradient` = calls to
`ThermalModel.simulate_trajectory` / Σ`njev`. One scalar trajectory is one
evaluation of the scalar objective, so the duplicate f(x) reads as 2 per
gradient where 1 would do.

**Perturbation — passes twice.** The finder's stated one (`h1`, a one-entry memo
on `simulate_trajectory`): `scalar_steps_per_gradient` **201.32 → 100.66**,
`batch_rows_per_gradient` unchanged at **96**, `njev` unchanged at 103. Exactly
as stated. I then ran the *actual proposed fix* rather than its stand-in —
`objective` wrapped in a one-entry cache keyed on `x.tobytes()` at the
`_multi_start_minimize` boundary (`v3_d903_memo_golden.py`, load1 2.66):

| case | njev | trajectories | per gradient | cache hits |
|---|---|---|---|---|
| two-zone DHW, current | 103 | 213 | 2.068 | — |
| two-zone DHW, fix | 103 | **107** | **1.039** | 106 |
| single-zone no-DHW, current | 11 | 29 | 2.636 | — |
| single-zone no-DHW, fix | 11 | **16** | **1.455** | 13 |

`njev` does not move, so the iterate path does not move — which is the claim.

**Scope — the "bit-identical, no golden drift" claim is executed and holds.**
All 49 fixtures captured with and without the cache: `golden_scenarios_changed
= 0`, `golden_fields_changed_at_precision6 = 0`.

Two scope notes the report's wording omits. First, the 106 hits against 103 jac
`f0` calls show the cache also absorbs `optimizer.py:339`
(`score = float(objective(res.x, *args))` after each L-BFGS-B run); the other
re-evaluations of the same class — `optimizer.py:2895` and `:4778`
(`achieved_objective`) and `:4725` (`solve_space`'s final score) — call the
*outer* closure and sit outside a cache scoped to `_multi_start_minimize`. Their
volume is 2–4 per solve against 103, so the fix as scoped captures essentially
all of it; it is worth saying so rather than leaving the reader to wonder.
Second, `simulate_trajectory` writes side channels on the model
(`last_buffer_trajectory`, `last_buffer_refused`, `last_wood_trajectory`) that
`_tighten_buffer_caps` reads — the finder's own harness memo had to save and
restore all three. An objective-level cache skips those writes on a hit. My
49-fixture run says nothing currently depends on them being fresh at a cached x,
but the fix should state the invariant instead of inheriting it by luck.

`low` is right: it is 25 % of one solve's scalar simulation on a path that is
already the fast one.

---

## D9-04 — DHW planning re-simulates the tank once per weak slot

**Vote: verify (low).** Deciding number: `simulate_dhw_only` calls per planning
call **64 → 118** at horizon 24 h → 48 h, tank steps 6,144 → 22,656.

**Metric.** As the harness states: calls to `ThermalModel.simulate_dhw_only` and
the tank steps they run, per `_build_dhw_requirements` call; CPU shares are
thread-CPU ratios inside one process.

**My number** (`h1b_dhw_loops.py`, load1 5.61, thread_factor 1.000). Counts
match the report exactly: two-zone winter 2 requirement calls, 2 LP calls, 4
`linprog`, 4 greedy passes (re-simulations 4,2,4,2), 2 min-run passes,
**64 `simulate_dhw_only` per planning call, 6,144 tank steps, 14,168
`compute_cop_dhw`**.

**Perturbation — passes.** Horizon 24 → 48 h: **118** calls per planning call,
**22,656** tank steps (×3.69 for ×2 steps), planner 356 ms = 12.9× reference
(report 13.5×, quiet re-take 13.8×). Exact match on both counts.

Provisional shares under load1 5.6 sit close to the report but not inside every
stated band: min-run share of planner 0.434–0.645 (report 0.43–0.59 — my summer
0.645 and shoulder 0.617 are above it), tank simulation 0.588–0.743 (report
0.60–0.71), planner/reference 1.79–3.59 (report 1.68–3.84), single-zone winter
`planner_share_of_solve` 0.594 (report 0.630, quiet re-take 0.621). Timing
shares under contention are provisional by rule; none of this touches the
counts the finding rests on.

**Scope — two more loops in the same class, unnamed.** The fix names only
`_apply_dhw_min_run` (`optimizer.py:4271`). The same shape — a full
`simulate_dhw_only` per repair round — lives at `optimizer.py:3996`
(`for _ in range(48)`) and `optimizer.py:4364` (`for _ in range(400)`). h1b's
own shares say these are the cheap ones today (greedy 0.027–0.081 of planner
CPU against min-run's 0.43–0.65), so fixing min-run alone does clear the
measured cost — but their iteration caps mean the bad case is 48 or 400 full
tank re-simulations, and a fix that hoists `simulate_dhw_only`'s per-step
attribute lookups (which the report also proposes) helps all three at once.
The report's own warning that a joint raise changes which slots survive and
would drift the DHW fixtures is correct, and is why this stays `low`.

---

## D9-05 — the solve starves the event loop for its whole duration

**Vote: verify (medium) on the number — but the stated perturbation is void,
and the report's gap-distribution figures are refuted.** Deciding number:
starvation share **0.000 idle → 0.945 / 0.961 under the default solve → 0.9976 /
0.9989 under the D9-01 path**, at load1 2.98 and 3.47 with a clean null control.

**Metric.** As the harness states: with the solve in a `ThreadPoolExecutor`
under a real asyncio loop, a 1 ms heartbeat records the gap between wake-ups;
starvation share = Σ(gaps > 5 ms) / solve wall; longest hold = max gap.

**My number** (`h3_gil_hold.py`, two runs, thread_factor 1.000):

| case | starvation share (run 1 / run 2) | report | quiet re-take |
|---|---|---|---|
| idle control | **0.000 / 0.000** | 0 | 0 |
| two-zone DHW | **0.945 / 0.961** | 0.967 | 0.950 |
| single-zone DHW | 0.702 / 0.748 | 0.748 | 0.741 |
| `dhw_cap_zero_range` | **0.9976 / 0.9989** | 0.998 | 0.998 |

The headline reproduces, and the null control is the reason it survives the
shared box: at load1 3.5 an idle loop still shows **zero** gaps over 5 ms, so
the gaps under the solve are the solve's.

**Perturbation — fails.** Stated: `sys.setswitchinterval(0.05)` puts "the
longest hold up, the starvation share unchanged."

| | run 1 | run 2 | quiet re-take |
|---|---|---|---|
| longest hold, 5 ms | 348.9 ms | 186.2 ms | 265 / 313 / 376 / 412 ms |
| longest hold, 50 ms | **156.8 ms** | **59.4 ms** | 404 ms |
| gap p50, 5 ms → 50 ms | 2.22 → 1.93 | 13.15 → 13.29 | 2.36 → — |
| starvation share, 5 ms → 50 ms | 0.945 → 0.963 | 0.961 → 0.960 | 0.950 → 0.949 |

The longest hold goes **down** in both of my runs; the quiet re-take moved it up
by 7 % against a baseline spread of 186–412 ms across five samples. `gap_p50`,
which is what the switch interval should actually set, is flat. And the half
that does behave as stated — the starvation share unchanged — is a number
expected *not* to move, so it cannot validate the harness. The harness's
nominated perturbation does not move its headline number in a stated direction.

**What does carry it** is the harness's own idle arm: remove the solve and the
same metric goes 0.945–0.999 → 0.000, at load1 3.0–3.5. That is an executed,
correctly-directed move on the headline number. The harness is not void; the
perturbation the report nominated is the wrong one, and the idle control should
be named as the perturbation as well as the null control.

**Refuted: the report's gap distribution, in the direction of worse.** Reported
p50 13.3 ms / p99 35.8 ms / longest 39.4 ms, "39–75 ms across runs". Measured
p99 274.6 and 143.2 ms, longest **348.9 and 186.2 ms**; the quiet re-take
independently got 265/313/376/412 ms. The stage attribution differs too: the
report attributes the longest hold to `simulate_trajectory_batch`, both of my
runs attribute it to `scalar_sim`. The defect is 5–10× larger than written.

**Scope — the proposed fix does not compile as described, and misses two
call sites.** `coordinator.py:4735` hands the solve to the executor as a
**lambda closure** over `solve_optimizer` and `solve_state`. A lambda is not
picklable, so `ProcessPoolExecutor` needs the call restructured into a
module-level function taking picklable arguments first; "the snapshot is already
a deep copy, so the inputs are picklable by design" is true of the inputs and
says nothing about the call site. Two other executor jobs run the same
GIL-holding work and the fix scope names neither: the what-if / fuse-advisor
shadow solve at `coordinator.py:10776` — a full `optimize`, and h2's non-finding
says price tiles double cycle CPU 526 → 1,036 ms — and `diagnose_last_interval`
at `coordinator.py:10104`. Nor does the report price what the fix costs: a
spawned interpreter plus numpy plus scipy import per solve, on the
Raspberry-Pi-class host the whole finding is about.

`medium` stands. The consequence is real and understated; the fix scope is
incomplete but points the right way.

---

## Summary

| finding | perturbation | my deciding number | vote |
|---|---|---|---|
| D9-01 | **passes** (removal direction, plan identical) | `fev_per_jev` 96.0 → 1.00; 177 `fuse_guard` fields drift at precision 6 | verify (high) |
| D9-02 | **passes** | 0/0 tripped at defaults, 2/1 at 400/75 | verify (medium) |
| D9-03 | **passes**, and the real fix passes too | trajectories/gradient 2.068 → 1.039, 0/49 fixtures move | verify (low) |
| D9-04 | **passes** | `simulate_dhw_only` per planning call 64 → 118 | verify (low) |
| D9-05 | **fails** (longest hold moves down twice); the idle control carries the number instead | starvation share 0.000 idle → 0.945/0.961/0.9989 | verify (medium), perturbation void |

Corrections the fixer needs, in order of how much trouble they save:

1. **D9-01** — `fuse_guard` **will** need re-recording (177 fields, 4.5e-05),
   not "possibly none". Exactly 1 of 49 fixtures is affected.
2. **D9-01** — the producer list is wider than pins and `power_caps_extra`:
   forced-**on** pins, a single exact `0.0` cap entry, and (unmeasured)
   `_tighten_buffer_caps`. All go through the one gate, so one carve-out fixes
   all of them — but the "one capped step is dodged" hedge is false at 0.0.
3. **D9-05** — the fix does not compile as written (lambda closure at
   `coordinator.py:4735`) and leaves `:10776` and `:10104` on the shared GIL.
4. **D9-02** — 600/100 detects a 2× by under 4 % on a box whose own run-to-run
   spread is 2.7 %. Per-scenario budgets, not a re-sized global constant.
5. **D9-05** — the report's gap figures understate the hold by 5–10×.
