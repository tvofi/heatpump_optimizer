# D9 verifier seat 2 of 3 — production reachability and consequence

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree
`audit-r2-D9`. Interpreter
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python`,
`PYTHONPATH=tests/hastub`, the five BLAS thread variables exported before
any numpy import, every harness run from the worktree root. Stance:
refute-first.

**Conditions.** Not a quiet window. `load1` at the close of my runs was
1.89–4.51 with 60–85 % idle CPU; `thread_factor` was 1.000 on every run.
Per the contract, **every wall/CPU/RSS number below is provisional**;
counts, ratios against `reference_solve`, and the coordinator's
`simulate_step` totals are final. QUIET.md's caveat applies here too —
this Mac carries a standing `load1` of ~1.4–2.0 even idle, so the
contract's ≤1.5 gate is not reachable on it.

| harness | log | load1 | thread_factor |
|---|---|---|---|
| `h1_grad_equivalents.py` | `/tmp/verify-D9-2/h1.log` | 3.551 | 1.000 |
| `h1b_dhw_loops.py` | `/tmp/verify-D9-2/h1b.log` | 2.848 | 1.000 |
| `h3_gil_hold.py` | `/tmp/verify-D9-2/h3.log` | 2.503 | 1.000 |
| `h7_stress_gate.py` | `/tmp/verify-D9-2/h7.log` | 4.510 | 1.00015 |
| `v2_reachability.py` (mine) | `/tmp/verify-D9-2/v2.log` | 3.407 | 1.000 |
| `v2b_f0_identity.py` (mine) | — | 2.713 | 1.000 |
| `v2c_consequence.py` (mine) | `/tmp/verify-D9-2/v2c.log` | 1.887 | 1.000 |

My three harnesses are committed beside the finder's:
`tools/audit/round2/D9/v2_reachability.py`, `v2b_f0_identity.py`,
`v2c_consequence.py`. Each carries the contract header, hooks a named
production symbol and moves under a named perturbation.

---

## D9-01 — one zero-range bound puts the whole solve on the scalar path

**Vote: verify. Severity high is earned, with one scope correction the
judge should carry into the register (see "What I would change").**

**My metric definition.** *Scalar-path rate* = of the
`_multi_start_minimize` entries one **production coordinator cycle**
makes (`HeatPumpOptimizerCoordinator._async_update_data` driven on a real
asyncio loop with a real `ThreadPoolExecutor`, not `FakeHass`'s inline
executor), the fraction whose `bounds` carry at least one `lo >= hi`
entry; reported beside `simulate_step` calls for that whole cycle. The
finder's metric is per-gradient at the optimizer; mine is per-cycle at
the coordinator, so the two are not numerically comparable — they answer
different questions, and mine is the reachability question.

**Finder's number, re-run once (h1).** Every count is bit-exact against
the report and against the quiet re-take:

| RESULT | report | quiet | mine |
|---|---|---|---|
| `pin_zero_range_two_zone_dhw.equivalents_per_gradient` | 9221.55 | 9221.55 | **9221.55** |
| `pin_zero_range_two_zone_dhw.simulate_step_calls` | 1595328 | 1595328 | **1595328** |
| `dhw_cap_zero_range.equivalents_per_gradient` | 9221.85 | 9221.85 | **9221.85** |
| `two_zone_dhw.equivalents_per_gradient` (control) | 297.32 | 297.32 | **297.32** |
| `pin_zero_range_two_zone_dhw.solve_over_reference` | 751 | 721.1 | 735.9 |

**Reachability, measured at the coordinator (my `v2_reachability.py`
section A and `v2b` section A2).** `simulate_step` per cycle, default =
18,336:

| config | solves | scalar | zero-range vars | simulate_step / cycle | × default |
|---|---|---|---|---|---|
| default install | 2 | 0 | 0 | 18,336 | 1.0 |
| fuse guard on, 3-ph 20 A, house at 10 kW | 2 | **2** | 9 | **736,800** | **40.2** |
| fuse guard on, 1-ph 16 A, house at 2 kW | 1 | **1** | 2 | 238,080 | 13.0 |
| fuse guard on, 3-ph 20 A, house at 2 kW | 4 | 0 | 0 | 36,672 | 2.0 |
| **fuse guard OFF**, only `main_fuse_amperes` entered | 3 | **1** | 8 | **284,160** | **15.5** |
| ↳ perturbation: that one key removed | 2 | 0 | 0 | **18,336** | 1.0 |
| manual plan, card-shaped (2 dropped peak hours) | 1 | **1** | 9 | **330,432** | **18.0** |
| manual plan, sparse (one 2 h slot) | 1 | **1** | 73 | 60,864 | 3.3 |
| manual plan, DHW channel only | 5 | 0 | 0 | 49,536 | 2.7 |
| learned capacity envelope, cold snap | 1 | **1** | 1 | 268,224 | 14.6 |

Four things follow, three of which the report does not state.

1. **The default install is clean.** 0 of 2 solves scalar, 18,336 steps.
   The finding is about opted-in configurations, not everyone.

2. **The cap lands on `lo == hi` structurally, not by coincidence.**
   `optimizer.py:3195-3197` clamps the DHW run power to
   `p_dhw_run = max(0.1, min(0.8·p_max, min(power_caps_extra)))`;
   `solve_space` (`optimizer.py:4680-4694`) then takes
   `headroom = min(p_max − dhw, caps_extra − dhw)`. At the
   horizon-minimum-cap step the second term is **identically zero**
   whenever the cap lies between 0.1 kW and 0.8·p_max. The fuse guard's
   cap is `np.clip(fuse_kw − baseline, 0, None)` over `np.full(...)`
   (`coordinator.py:4676-4690`, `8901-8908`) — uniform — so *every*
   planned DHW step is zero-range, not one unlucky one. This is why the
   finder's "a uniform fuse cap guarantees it" is right, and it is worth
   recording as the mechanism rather than as an empirical observation.

3. **A path the report does not name: the fuse advisor.**
   `coordinator.py:7961-8020` (`_maybe_run_fuse_advisor`) runs a shadow
   solve at `power_cap_kw = next_smaller_fuse_kw − baseline_house_load`
   on **any install that entered its main fuse size**, whether or not
   `fuse_guard_enabled` is on — and the candidate cap is deliberately the
   *tighter* one, so it is more likely to fall under 0.8·p_max than the
   guard's own. The row above isolates it: the fuse guard off in both
   arms, `main_fuse_amperes` the only difference, 284,160 vs 18,336
   `simulate_step` in the cycle. `docs/configuration.md:292` describes
   the field as coming "From your grid contract" and the config flow
   offers it on the Grid-costs page. Rate: at most weekly
   (`7 * 24 * 3600` guard), so this is a weekly ~2.3 s (M1) / ~16 s (Pi)
   solve, not a per-cycle one — but it needs **no** feature switched on.

4. **The card's own gesture is near the worst case, not the best.**
   `manual_plan.py:163-201` pins a step *off* when no slot overlaps it,
   so the expensive shape is the one with few off steps and many live
   ones. `docs/dashboard-card.md:195-225` says the lanes start from
   today's plan redrawn, which is exactly that shape. Measured:
   card-shaped (2 gaps, 9 zero-range) 330,432 steps; sparse (73
   zero-range) only 60,864, because 73 fixed variables collapse the
   problem. The finder's single-pin construction is therefore the
   *realistic* end of the range, not a contrivance.

**Is the golden `fuse_guard` fixture on the scalar path today?** Yes, and
it is the only one. My `v2_reachability.py` section B ran all 49 golden
plan scenarios with my own hook on `_multi_start_minimize`:

```
RESULT golden_scenarios_total=49
RESULT golden_scalar_scenarios=1
RESULT golden_scalar_names=fuse_guard
RESULT golden.fuse_guard.simulate_step_calls=731904   (= the finder's 731,904)
RESULT golden.fuse_guard.zero_range_vars=3
RESULT golden.scalar_over_batched_cpu=9.05
```

`capacity_curve` — the other capped fixture, a per-step ramp to the
0.6·p_max floor — did **not** land on the scalar path, because DHW is not
planned at its minimum-cap step. So the exposure in the fixtures is one
scenario, not two.

**Consequence at a 30-minute cycle.** From h3's *uninstrumented*
`dhw_cap_zero_range` run — 1,512,384 `simulate_step` in 12,092 ms wall —
the marginal cost is 8.0 µs/step on this M1. Applying it, and the
finder's stated ×7 Pi-4 assumption:

| path | M1 solve | Pi 4 (×7, assumed) | rate |
|---|---|---|---|
| default | 0.67–0.72 s | ~4.7–5 s | every 30 min |
| fuse guard biting | ~5.9 s | **~41 s** | every 30 min |
| card-shaped manual plan | ~2.6 s | ~18 s | every 30 min for 20 h |
| fuse advisor only | ~2.3 s | ~16 s | weekly |

The stake is stated in the tree itself. `RELEASE_NOTES.md:433-437`
credits #97's batched jac with taking "the coldest solve's GIL hold …
from eleven seconds to one — and with it the event-loop exposure the
v5.1.1 freeze class was made of", against `RELEASE_NOTES.md:1768-1795`,
where v5.1.1's freeze made the instance "unreachable for minutes". My h1
re-run puts the pinned two-zone DHW solve at **13.9 s of CPU**
(quiet re-take 12.8 s) — *above* the 11.5 s pre-#97 figure that claim
rests on. One config field restores the class the release notes say was
retired. That is what earns `high`.

**My reading of the quiet re-take.** It strengthens the finding. Every
count reproduced exactly; only the absolute `solve_cpu` milliseconds fell
(25.0 s → 12.8 s), and every ratio against `reference_solve` held
(751 → 721, tolerance-wide). The report's headline is a count, so the
quiet window cost it nothing. `load1` was 2.19 on the D9-h1 quiet run —
above the contract's gate — which matters only for the milliseconds, and
those are not what the finding rests on.

**Attacks run and their outcomes.**
- *Contention*: the headline is a count; reproduced bit-exact at load1 3.55.
- *Test-stub reachability*: attacked and survived — I drove the real
  coordinator through `_async_update_data` on a real loop with a real
  `ThreadPoolExecutor`, not `FakeHass`'s inline executor. The bounds are
  built in the executor from `caps_extra`/`space_pins` the coordinator
  itself produced.
- *Grid artefact*: not an aggregate. Eight independent coordinator
  configs, one golden population of 49.
- *Null control*: `coord.default` (0 scalar, 18,336 steps) and the
  single-key perturbation (fuse size removed → 18,336) are both clean.
- *Severity by consequence*: earned, but only on opted-in configurations
  (see below).

**What I would change in the register entry.** The claim says "a real
install", which reads as the default. It is not: the default install is
batched. Say instead — *any install with the fuse guard on and a cap that
bites, any install using the manual-plan card, any install with the
capacity curve on, and, weekly, any install that entered its main fuse
size.* And add the fuse advisor to the `mechanism` field; it is the only
one of the four that needs no feature switched on.

**Deciding number: `coord.fuse_guard_3ph20a_10kwhouse.simulate_step_calls
= 736,800` against `coord.default.simulate_step_calls = 18,336` — 40.2×,
from production config keys, in one production coordinator cycle.**

---

## D9-02 — the stress gate cannot see a 2× solve regression

**Vote: verify. Severity medium stands.**

**My metric definition.** Unchanged from the finder's (this is the one
finding where a second definition would only muddy it): the gate's own
per-scenario CPU ratio against its trailing-median `reference_solve`
versus `SOLVE_BUDGET_RATIO`, and the sweep total versus
`SWEEP_BUDGET_RATIO`; headroom = budget / observed. What I added is the
*coverage* question below, which is a count of my own.

**Finder's number, re-run once (h7).**

| RESULT | report | quiet | mine |
|---|---|---|---|
| `smallest_detectable_uniform_regression` | 4.685 | 4.763 | **4.704** |
| `plain.worst_ratio` (budget 1400) | 298.8 | 293.9 | 297.6 |
| `plain.sweep_ratio` (budget 450) | 50.7 | 53.4 | 55.1 |
| `injected_2x.per_scenario_tripped` | 0 | 0 | **0** |
| `injected_2x.sweep_tripped` | 0 | 0 | **0** |
| `injected_over_plain_worst` | — | — | **1.992** (a true 2×) |
| `ci_sets_stress_ratio` | 0 | 0 | **0** |
| `tests_memory_instrumentation` | 0 | 0 | **0** |

**Is the blindness real in CI as configured?** Yes. I read
`.github/workflows/tests.yml` end to end. The `fast`, `slow` and
`closures` jobs set `GOLDEN_MODE`, `SLOW`, `GATE_SCOPE`, `DRIFT_WARM_CACHE`
and the three thread variables — and nothing else. The `fast` job's env
block names `STRESS_SOLVE_RATIO`, `STRESS_SWEEP_RATIO` and
`STRESS_SOLVE_CEILING_MS` **in a comment**, as "the knobs if it ever needs
one", and sets none of them. `tests/run.sh` sets none either. So CI runs
`SOLVE_BUDGET_RATIO=1400` / `SWEEP_BUDGET_RATIO=450`
(`tests/stress.py:177,192`), sized (the docstrings still say so at
`tests/stress.py:165-175`) when the dearest scenarios cost 655–662×
against a tree that now costs 298×. The blindness is CI's, not a local
artefact. `tests/stress.py` is in the closure of `optimizer.py`
(`tests/closures.json`, 61 entries, `optimizer.py` and `thermal_model.py` among them), so it does run on a PR touching the solver; it
simply cannot see.

**Does #145's per-scenario table change the answer?** Not at this
baseline: **`tests/stress_budgets.json` is absent** from the worktree at
`c398fc8` (`ls` → No such file). #145 landed after. On its merits a
per-scenario table would fix the *sizing* half — it cannot fix the two
halves below, so the finding does not evaporate when #145 is considered:
there is still no memory line anywhere in `tests/*.py`, and the table
cannot budget a cell that is never run.

**My own addition — the sweep does not sample the expensive path at
all.** `grep -n "power_caps_extra\|space_pins" tests/stress.py` → 0 hits;
same in `tests/optimality.py`. `build_case(...)` has no cap or pin
parameter. So none of the 48 combinations ever produces a zero-range
bound, and the 13–40× scalar path D9-01 names lives **outside the gate's
sample entirely** — not merely under-budgeted, unsampled. A regression
confined to that path is invisible at any budget, and re-sizing the
budgets from the printed figures (the finder's proposed fix) would not
change that.

**The one-line production mutation the gate fails to notice**, as the
contract requires — and it is in a production file, not a test file:

> `custom_components/heatpump_optimizer/optimizer.py:199`
> `f = batch_objective(perturbed, *args)`
> → `f = np.mean([batch_objective(perturbed, *args), batch_objective(perturbed, *args)], axis=0)`

Bit-identical result (the mean of two identical arrays is the array), and
it doubles the batched simulation, which h1 measures at 32.6 % of the
solve's thread CPU (`two_zone_dhw.share_batch_sim=0.326`) — a ~1.33×
solve regression, far inside the 4.70× blind zone. The 2× case does not
need arguing: h7's injection at `HeatPumpOptimizer.optimize`, the symbol
every one of the 48 scenarios enters through, measured 1.992× and tripped
0 per-scenario and 0 sweep checks.

**One correction for the register.** The owner's brief says "CI sets it 4×
looser than the default". That is stale — it described the retired
`STRESS_SOLVE_BUDGET_MS`, which `tests/stress.py:159-162` says is now only
read to complain about. CI sets no override at all; the 4.7× blindness is
in the *defaults*. The finder's version is the correct one and the
register should carry it rather than the brief's.

**Deciding number: `injected_2x.per_scenario_tripped = 0` and
`injected_2x.sweep_tripped = 0` at a measured `injected_over_plain_worst
= 1.992`.**

---

## D9-03 — the batched jac re-evaluates f(x) scipy just computed

**Vote: verify. Severity low is right.**

**My metric definition.** *f0 point identity* = of the
`_batch_fd_gradient` calls in one solve, the fraction whose `x0` is
byte-identical (`ndarray.tobytes()`) to the `x` of the objective call
scipy made **immediately before it**, with no intervening objective call.
This is the premise the finding stands or falls on, and the finder's
`nfev == njev == 103` does not establish it: equal counts do not mean
equal points.

**Finder's number, re-run once (h1).** `two_zone_dhw.nfev=103`,
`njev=103`, `scalar_steps_per_gradient=201.32`, memo arm `100.66` — all
bit-exact against the report and the quiet re-take.

**My number (`v2b_f0_identity.py`).**

```
RESULT two_zone_dhw.batch_fd_calls=103
RESULT two_zone_dhw.njev=103
RESULT two_zone_dhw.f0_x_identity=1              <- 103 of 103
RESULT two_zone_dhw.f0_x_identity_any=1
RESULT two_zone_dhw.scalar_trajectories_per_gradient=2.068
RESULT single_zone_dhw.f0_x_identity=1           <- 9 of 9
RESULT single_zone_dhw.scalar_trajectories_per_gradient=2.778
```

So the answer to the question posed is unambiguous: **it is scipy's own
f(x), at the same point, every time.** scipy's `ScalarFunction` updates
`fun` and `grad` against one cached `x`, and L-BFGS-B asks for both
together, so the jac closure's `float(objective(x, *a))`
(`optimizer.py:325`) is always a recomputation of the value scipy already
holds. A one-entry memo keyed on `x.tobytes()` would hit 100 % of the
time, not "usually". `scalar_trajectories_per_gradient = 2.068` is the
count it would halve.

*(My first attempt at this measurement returned `f0_x_identity=0`, which
would have refuted the finding. It was my instrumentation that was wrong,
not the finding: the jac closure captures the *original* `objective`, so
wrapping the function handed to `_scoped_minimize` never sees the f0
call. Recording it here because a reviewer reproducing this will hit the
same trap.)*

**Consequence.** 13 % of a 0.67–0.72 s solve is ~90 ms on this M1,
~0.6 s on a Pi at ×7, every 30 minutes: a 0.03 % duty-cycle improvement.
And it does nothing at all on D9-01's path, where the jac is never built.
Real, cheap to fix, no golden drift — and low is the honest severity.
No quiet re-take issue: both numbers are counts and both reproduced.

**Deciding number: `f0_x_identity = 1.000` over 103 gradient evaluations.**

---

## D9-04 — the DHW planner's cost

**Vote: verify. Severity low is right; one framing correction.**

**My metric definition.** *Planner share, one hook* = thread CPU inside
`HeatPumpOptimizer._build_dhw_requirements` divided by the solve's thread
CPU, with **only that one wrapper installed**. The finder's figure is
taken with seven wrappers, one of which (`compute_cop_dhw`) fires 14,168
times per solve — that is the artefact question, and it is the right
question to ask.

**Finder's number, re-run once (h1b).** Counts bit-exact:
`simulate_dhw_only_per_planning_call=64`,
`tank_steps_per_planning_call=6144`, `compute_cop_dhw_calls=14168`,
`dhw_requirement_calls=2`. Shares:
`single_zone_dhw.planner_share_of_solve=0.6266` (report 0.6296, quiet
0.6213); `two_zone_dhw.planner_over_reference=3.91` (report 3.4–3.8,
quiet 4.08); `minrun_share_of_planner=0.481`.

**My number (`v2_reachability.py` section D), the artefact test.**

| | seven hooks (finder) | one hook (mine) | difference |
|---|---|---|---|
| `single_zone_dhw.planner_share_of_solve` | 0.6266 | **0.6191** | −1.2 % |
| `two_zone_dhw.planner_share_of_solve` | 0.1010 | **0.1043** | +3.3 % |
| `two_zone_dhw.planner_over_reference` | 3.91 | **3.47** | −11 % |

**The cost is real work, not the harness's hooks.** Removing the
14,168-call counter moves the headline share by 1.2 %, well inside the
report's own ±15 %. The structural counts — 64 whole-tank re-simulations
and 6,144 Python-loop tank steps per planning call, twice per solve — are
hook-independent by construction: they are call counts of production
loops.

**Reachability: this one is the default path.** Hot water is on in the
ordinary install (a tank volume is all it takes — `tests/entities.py:727-731`
says so in production's own terms), and `_build_dhw_requirements` ran
twice in every DHW-enabled cycle I measured, including
`coord.default`. Unlike D9-01, no opt-in is required.

**The framing correction.** "63 % of a solve" is true and misleading: it
is 63 % of the *cheapest* solve — the single-zone one, whose whole thread
CPU is 129 ms. On the two-zone solve the same absolute planner cost
(~80 ms both times) is **10.4 %**. The invariant across both is the
absolute figure: ~80 ms, 3.4–3.9× the reference solve, ~0.56 s on a Pi at
×7, every 30 minutes — a 0.03 % duty cycle. That is worth a cheap fix and
is not worth more than `low`. I would have the register lead with
`planner_over_reference` (3.4–4.1, stable across every re-take) rather
than with `planner_share_of_solve`, whose value is set by which solve you
divide by.

**My reading of the quiet re-take.** Unremarkable and confirming: every
count exact, every share inside tolerance, `planner_over_reference`
drifting 3.4 → 4.08 → 3.91 across three boxes because it is a ratio of
two small CPU numbers. The perturbation (24 h → 48 h) reproduced at
13.80 quiet against 13.5 reported.

**Deciding number: `planner_share_of_solve = 0.6191` with one hook
against `0.6266` with seven — the cost survives its own instrumentation.**

---

## D9-05 — the solve starves the event loop for its whole duration

**Vote: verify. Severity medium stands — the number that would raise it
belongs to D9-01, which already carries `high`. The report's gap
distribution must be re-stated from the quiet numbers; it understates its
own defect by 8×.**

**My metric definition.** *Plain-thread starvation share* = summed gaps
over 5 ms between 1 ms `time.sleep` wake-ups of an **ordinary
`threading.Thread`** — not the asyncio loop — running beside the solve,
divided by the solve's wall time. Same threshold and same idle control as
h3. The point is to separate "the event loop is scheduled badly" from
"the whole Python process is stopped", which decides how wide the
consequence is and whether the proposed fix is the right one.

**Finder's number, re-run once (h3).**

| RESULT | report | quiet (run 4) | mine |
|---|---|---|---|
| `idle_control.starvation_share` | 0 | 0 | **0** |
| `idle_control.ticks_per_second` | 779 | 758 | 786 |
| `idle_control.longest_gil_hold` | 2.1 ms | — | 1.33 ms |
| `two_zone_dhw.starvation_share` | 0.967 | 0.950 | **0.9666** |
| `two_zone_dhw.longest_gil_hold` | 39.4 ms | 376 ms | **319.1 ms** |
| `two_zone_dhw.gap_p50` | 13.3 ms | 2.36 ms | **2.54 ms** |
| `two_zone_dhw.gap_p99` | 35.8 ms | 304 ms | **265.0 ms** |
| `two_zone_dhw.ticks_per_second` | 74 | 44.5 | 40.5 |
| `dhw_cap_zero_range.starvation_share` | 0.998 | 0.9976 | **0.9987** |
| `dhw_cap_zero_range.wall` | 14.7 s | 11.4 s | 12.09 s |

**My reading of the quiet re-take: it is right and the report is wrong.**
My independent run at `load1` 2.50 lands on the quiet numbers, not the
report's, on every disputed statistic — longest hold 319 ms against a
reported 39.4, `gap_p99` 265 ms against 35.8, `gap_p50` 2.54 ms against
13.3. Two samples on different boxes agreeing against the original is not
a load artefact. The report's headline — the starvation share — is the
one number that reproduces everywhere (0.967 / 0.950 / 0.9666), which is
why the finding survives its own mis-stated distribution. The stage
attribution also needs correcting: my longest hold landed in `scalar_sim`
(319 ms), the next in **no instrumented stage at all** (126 ms), the
third in `dhw_lp_build` (51 ms); the report names
`simulate_trajectory_batch`. Between the quiet window's samples
(`dhw_lp_build` ×3, `batch_sim` ×1) and mine, the report's attribution is
the least-supported reading of the five.

**The perturbation arm is unreliable and should be re-stated.** Switch
interval 5 ms → 50 ms took my `longest_gil_hold` *down*, 319 → 57 ms, the
opposite of the report's stated direction, because the max is a tail
statistic on 29 samples. The mechanism does show, robustly, in the
median: `gap_p50` 2.54 → 17.24 ms, a 6.8× rise that is exactly the
switch-interval hand-off. Judge: score the perturbation on `gap_p50`, not
on the max.

**My number — the stall is process-wide, not loop-specific
(`v2c_consequence.py` section E).**

```
RESULT idle_plain_thread.plain_thread_starvation_share=0        (786→660 Hz idle)
RESULT two_zone_dhw_plain_thread.plain_thread_starvation_share=0.9386
RESULT two_zone_dhw_plain_thread.longest_hold=402.7 ms
RESULT dhw_cap_zero_range_plain_thread.plain_thread_starvation_share=0.9971
RESULT dhw_cap_zero_range_plain_thread.wall=11554 ms
```

An ordinary Python thread with no asyncio anywhere near it starves as
badly as the loop does — 0.939 against the loop's 0.967, longest hold
402.7 ms against 319.1 ms. So this is GIL starvation of the whole
interpreter, and the consequence is wider than the finding states: in a
real Home Assistant process the recorder thread, every integration's
executor job and every MQTT/HTTP callback thread are stopped for the same
window, not only the event loop. It also settles the fix: the
`time.sleep(0)` alternative the report mentions in passing shortens holds
in *one* thread's favour at best, while the `ProcessPoolExecutor` route is
the only one that removes the shared GIL. Recommend the register carry
the process fix as the fix, not as the first of two options.

**Does any Home Assistant subsystem notice a 376 ms loop stall?** I could
not read Home Assistant's own source in this worktree — only
`tests/hastub` is installed, and no real `homeassistant` distribution is
in the interpreter — so this paragraph is reasoning, not an executed
measurement, and the judge should treat it as such. On a default install
nothing acts at that scale: `DataUpdateCoordinator` warns only when an
update outruns its own `update_interval`, which is 30 minutes here
(`DEFAULT_OPTIMIZATION_INTERVAL = 30`, `const.py:1070`); the Supervisor's
health check acts on minutes of API unresponsiveness; asyncio's
slow-callback warning is debug-mode only; and `homeassistant.util.loop`'s
blocking-call detector fires on blocking I/O *called on the loop*, which
this is not. So: no watchdog, no restart, and — worth saying plainly —
**no log line either**. The user's only evidence is latency. That is the
argument for `medium` rather than `high` on the default path, and it is
also the argument that this defect will not be noticed until someone
measures it, which is what the audit is for.

**How it compares to the v5.1.1 incident.** v5.1.1's freeze made the
instance "unreachable for minutes" when an options save forced a reload
that ran a cold solve (`RELEASE_NOTES.md:1768-1795`); the shipped
mitigation was the two `sleep(0.002)` stage-boundary yields, which h3
puts at 4 ms of a ~700 ms solve — 0.6 %, as the report says. On the
**default** path today the equivalent exposure is 0.67–0.72 s on this M1,
~4.7–5 s on a Pi at ×7, every 30 minutes: a different order of magnitude
from "minutes", laggy rather than frozen, and it is the exposure v5.1.1's
fix consciously accepted. On **D9-01's** path it is 12.09 s of M1 wall at
0.9987 starvation — ~85 s on a Pi, every 30 minutes — which *is* the
v5.1.1 class, and which `RELEASE_NOTES.md:433-437` claims was retired by
#97. D9-05 is the mechanism; D9-01 is what makes it an incident again.
Keeping the severities at medium/high split that way is the honest
allocation: rating D9-05 `high` on its own would double-count D9-01's
reachability.

**Attacks run and their outcomes.**
- *Null control*: held in my run — the idle heartbeat produced **zero**
  gaps over 5 ms on both the loop (786 Hz) and a plain thread (660 Hz),
  so the 5 ms threshold sits far above this box's own noise floor even at
  `load1` 1.9–2.5.
- *Contention*: the share is contention-tolerant (0.967 at fan-out load,
  0.950 quiet, 0.9666 at load1 2.50); the gap distribution is not, and is
  *worse* when the box is quiet — the report's direction of error is the
  favourable one, which is the direction a finder is most likely to
  publish and least likely to re-check.
- *Test-stub reachability*: h3 already uses a real loop and a real
  `ThreadPoolExecutor`; my section E adds a bare thread with no asyncio.
  Neither goes through `FakeHass`.
- *Alternative mechanism*: a 126 ms hold landed in no instrumented stage,
  so some of the tail is not accounted for by the named symbols — GC over
  a large solve heap is the obvious candidate and I did not test it. It
  does not change the consequence (either way the process is stopped) or
  the fix (a separate process moves both), so I leave it as an open
  mechanism note rather than an attack.

**Deciding number: `two_zone_dhw_plain_thread.plain_thread_starvation_share
= 0.9386` with a 402.7 ms longest hold, against `idle_plain_thread = 0` —
the stall is the whole interpreter's, not the event loop's.**

---

## Summary

| finding | vote | severity | deciding number |
|---|---|---|---|
| D9-01 | verify | high (scope corrected) | 736,800 vs 18,336 `simulate_step` per production coordinator cycle (40.2×) |
| D9-02 | verify | medium | injected true 2× (1.992) trips 0 of 48 per-scenario and 0 sweep checks |
| D9-03 | verify | low | `f0_x_identity = 1.000` over 103 gradient evaluations |
| D9-04 | verify | low (framing corrected) | planner share 0.6191 with one hook vs 0.6266 with seven |
| D9-05 | verify | medium (numbers re-stated) | plain-thread starvation 0.9386, longest hold 402.7 ms, idle control 0 |

No refutes. Three corrections the judge should carry into the register:
D9-01's reachability is opted-in configurations plus a weekly path via the
fuse advisor, not "a real install" unqualified; D9-04's headline should be
`planner_over_reference`, not a share of the cheapest solve; and D9-05's
gap distribution must be re-stated from the quiet numbers, with its
perturbation scored on `gap_p50` rather than on the maximum hold.
