# D0 verification — seat 0-2, round 4 (re-run of a dead seat)

- Worktree: `../audit-r4-verify-D0-2`, detached at `3e91f85` (branch head).
- Production `optimizer.py` is byte-identical between the findings' baseline
  `7dd68dd` and this head (`git diff 7dd68dd..HEAD -- custom_components/`
  touches only `manifest.json` and the card), so the baseline numbers apply
  to this tree without translation.
- Interpreter `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  scipy 1.17.1, numpy 2.4.6, always `PYTHONPATH=tests/hastub` from the
  worktree root. No lock taken: no `stress.py`, no full gate.
- `load1` at the end of each run: 3.48 / 11.51 / 6.71 / 11.82 / 8.95 — a busy
  shared box (other verifiers live). Every number below is an objective
  value, a ratio of objective values, an iteration count, a status count or a
  schedule/temperature element: deterministic arithmetic. `thread_factor`
  1.0000–1.0002 on every harness. No timing, CPU or RSS claim is made or
  relied on anywhere in this report, so nothing below is provisional by the
  contention rule.
- Not read, per the contract: `verify-0-1.md`, the other seat's harnesses
  (`d0_own_*.py`) and `.verify-0-1.out` files, and the register.

## Re-runs of the finder's harnesses (step 1 of the contract)

All four re-run commands exactly as their headers state. Every `RESULT`
reproduced to the last printed digit — this box, this BLAS, this tree:

| harness | verdict |
|---|---|
| `ftol_gap.py` (80 cells, ~35 min) | all 24 RESULTs identical: mean 0.117642 %, max 0.799815 %, 34/70 > 0.01 %, comfort-parity 0/80, flat null 0.104822 %, 420 solves / 0 on cap, step-0 max 4.05621 kW (`ftol_gap.rerun-0-2.out`) |
| `mpc_realised.py` (10 cells) | identical: priced +0.320965 SEK/day, LOO 0.147996, flat null **−2.11318** SEK/day, 4/8 cells production cheaper (`mpc_realised.rerun-0-2.out`) |
| `budget_knobs.py` (12 cells) | identical: maxiter×15 = 0.0000 % in every cell, gtol 1e-12 = 0.0000 %, ftol arm mean 0.164503 % / max 0.795787 %, 68 solves, 0 on cap, max nit 52, median 8 (`budget_knobs.rerun-0-2.out`) |

The finder's per-profile table re-derived from my re-run's 80 CELL lines
matches their table row for row (e.g. summer_negative 0.238/0.686,
shoulder 0.150/0.800, winter_moderate 0.045/0.184).

## My own instruments (step 2 — written before any of the above were read)

### `v02_own_D0-01.py` — 22 cells, different hook, own metric

Differences from the finder's method, all deliberate: the ftol rewrite is
intercepted at `optimizer.py`'s imported `scipy.optimize.minimize` symbol
(one level closer to scipy than their `_scoped_minimize` hook, so it cannot
miss a call); the grid adds a second weather (summer_cool), two
phase-shifted cells (day starts 08:00, outside the finder's midnight-only
grid) and a **bitwise identity control** (rewriting ftol to its own value
1e-6 must reproduce the unpatched plan bit for bit — a control the finder's
harness lacks); comfort is re-simulated here through
`ThermalModel.simulate_trajectory_with_dhw` over min(room, upper, lower)
rather than read off `result.room_temp_trajectory`; and a
**starts-vs-restart decomposition** separates where the gain comes from.

Metric definition (one line): the fraction of cells in which rewriting only
L-BFGS-B's `ftol` to 1e-14 makes `HeatPumpOptimizer.optimize` return a plan
whose production `objective_value` is strictly lower, with median/mean/max
relative drop and a top-5-dropped mean.

Results (`v02_own_D0-01.out`):

```
cells_improved_strictly_priced   15 of 18      (finder, >0.01% bar: 34 of 70)
mean_gap_priced_pct              0.181192 %    max 0.795787 %
median_gap_priced_pct            0.085414 %    top-5-dropped 0.063532 %
mean_gap_flat_null_pct           0.157685 %    max 0.554255 %
cells_tight_worse_priced         0
identity_control_bitwise_equal   22 of 22      max |dJ| at identity: 0.0 %
mean_gap_starts_only_pct         0.206474 %    == the full tight arm, cell for cell
mean_gap_restart_only_pct        0.000000 %    (all 11 decomposition cells)
mean_gap_loose_1e-4_pct          -0.219180 %   (loosening makes it worse: direction holds)
cells_step0_differs_gt_0p01kW    4 of 18       max 4.056214 kW (same shoulder cell)
```

Every cell that overlaps the finder's grid agrees with their number to four
decimals (winter_typical/tz1 0.7958 %, shoulder/tz0 0.0834 %,
summer_negative/tz0 0.3652 %, flat/tz1 0.5543 %, ...). The two definitions
are comparable: same relative-gap form, same production objective source.

New facts my instrument adds:

1. **The identity control passes 22/22.** The comparison method is sound:
   the hook is inert when it rewrites ftol to the value production already
   passes. The finder had no such control; it now exists.
2. **The whole gain is in the four main starts.** The starts-only arm
   reproduces the tight arm exactly in every decomposition cell, and the
   restart-only arm is +0.0000 % everywhere — as it must be, since
   `_LBFGSB_RESTART_KEEP_REL = 2e-2` discards any sub-2 % restart gain. This
   kills the alternative explanations (the patch working through some side
   door; the restart threshold being the real story — the finder's
   non-finding 1 said the same thing from the other side).
3. **The perturbation direction holds**: mean −0.219 % at ftol 1e-4
   (production gets *further* from the minimum as ftol loosens).
4. **Comfort parity is not fully universal under a stricter metric.** In one
   phase-shifted cell (winter_typical/winter_cold/tz1, start 08:00 — outside
   the finder's grid) the tightened arm violates more under my
   re-simulated min(room,up,lo) metric: 1.4185 vs 1.2214 degree-steps
   (both arms violate; the floor is soft in the objective). Under the
   finder's stated metric (room trajectory) and grid their 0-of-80 claim
   reproduced exactly. This trims the *side-claim* "comfort never worse"
   from "always" to "on the measured grid and metric"; it does not touch
   the core claim and does not move severity.
5. **The gap survives a day-phase shift** (+0.218 % at the 08:00 start) —
   not an artefact of the midnight alignment.

### `v02_own_D0-02.py` — census through `O.minimize`, horizons 6/24/48 h

The finder only ran 24 h; if the iteration cap were ever to bind it would
be at the longest horizons, so this is the scope attack. 136 L-BFGS-B calls
over 24 cells (4 prices × 2 topologies × {6, 24, 48} h, DHW on):

```
lbfgsb_calls                     136      (all maxiter=300 on this grid)
calls_status_1                   0
calls_nit_ge_maxiter             0
max_nit                          62       (max_fraction_of_cap 0.2067)
median_nit                       10       p99 57.9
calls_above_quarter_cap          0
max_nit at the 48 h cells        62       (192-variable solves)
x15 arm at 48 h                  +0.0000 % in all 8 cells
```

The census idiom is different (one hook at the scipy symbol catches every
call — it observes 5 or 7 calls per optimize, including paths the finder's
`_multi_start_minimize` framing does not name), and the conclusion is the
same and now extends to 48 h: **the iteration budget is nowhere near
binding, and multiplying it by 15 cannot change a plan because every solve
has already stopped on ftol long before the cap.** The reachability/scope
attack strengthened the finding rather than weakening it.

## Mutation evidence for D0-02's gate claim (contract step 4)

`tests/optimality.py` passes 14/14 unmodified (~70 s). Then, each reverted
immediately after (tree left clean, `git status` empty in
`custom_components/`):

| production mutation (single line, `optimizer.py`) | optimality.py |
|---|---|
| line 529 `"ftol": 1e-6` → `1e-3` (1000× looser) | **ALL 14 PASSED** |
| line 529 `"ftol": 1e-6` → `1e-2` (10 000× looser) | **ALL 14 PASSED** — while the winter_typical/tz1/winter_cold plan degrades **1.07 %** on the production objective (J 87.273 → 88.211) |
| line 3530 `maxiter=200` → `3` (contrast) | **1 of 14 FAILED** — "the production iteration budget buys a materially better plan [0.0 % gap]" |

This is the asymmetry D0-02 claims, executed: the suite's quality gate
fires on a starved iteration budget and is blind to a stop-rule knob loose
enough to cost 1 % of objective. The killing mutation lives in
`custom_components/heatpump_optimizer/optimizer.py` (production), not in a
test file.

One nuance, recorded so the judge sees it: the golden drift gate would flag
*any* plan movement — a ftol change included — but that is a
reproducibility pin on whatever the current knobs produce, not a quality
gate; it would flag a maxiter change the same way if any plan moved (none
does, which is the finding). "No gate" in D0-02 means no *quality* gate on
the knob that decides every plan, and that is what the mutations show.

## Attacks, in the contract's order

1. **Contention.** No number in either finding is a wall/CPU/RSS figure;
   everything re-ran to identical digits at load1 3.5–11.8. Nothing
   provisional.
2. **Wrong gate mode.** Not a `env_drift.py --all` claim; the gate named is
   `tests/optimality.py`, run directly, with the mutation table above.
3. **Aggregate artefact.** Re-cut the finder's own 80 cells my own way:
   strictly-positive in 40/70 (30 exactly zero, 0 negative), positive mean
   in 7/7 priced profiles and both topologies, but top-skewed — median
   0.0045 %, drop-top-10 mean 0.037 % against the 0.118 % headline. The
   mean is carried by the top third of cells; the phenomenon is not one
   cell or one profile. The finder printed an LOO (0.108 %) but not the
   median; the skew is the only thing my re-aggregation adds against them,
   and it does not overturn a mean stated over a stated grid.
4. **Null control.** Present in both findings and honestly read. The flat
   gap does not vanish (0.105 % finder / 0.158 % mine), so no price-basin
   claim is made; the MPC null control moves the wrong way (−2.11 SEK/day
   flat against +0.32 priced) so no money claim is made. The finder's
   "the honest half is the null control" is exactly what the numbers say.
5. **Reachability.** Every cell drives the real production
   `HeatPumpOptimizer.optimize` with shipped defaults (DHW on), no
   `FakeHass`, no stub; the loose ftol is in every real solve the
   integration performs. The gap reaches the step-0 actuator command in
   9/70 (finder) and 4/18 (mine) cells — and the MPC harness then measures
   whether that survives re-planning: on average it does not convert into a
   reliable bill saving, which the finding concedes.
6. **Severity earned by consequence.** D0-01: a real, replicated solver
   defect, bounded (mean ~0.1 %, max 0.8 % objective), no demonstrated
   money (null control fails), no comfort regression under the shipped
   metric on the measured grid — `low` is earned, and my one
   stricter-metric out-of-grid comfort counterexample does not raise it.
   D0-02: nothing a user sees; a control aimed at a knob with 4–5× slack
   while the knob that decides every plan is ungated (a 1 %-worse plan
   passes) — `low` is earned.

Bookkeeping note on D0-02, immaterial to the verdict: "488 observed
L-BFGS-B calls" sums 420 (ftol_gap) + 68 (budget_knobs), but budget_knobs'
12-cell grid is a subset of ftol_gap's 80-cell grid, so 68 solves are
counted twice; the distinct count is 420. Zero of them bind, as is zero of
my 136.

## Votes

| id | vote | severity | one-line metric |
|---|---|---|---|
| D0-01 | **verify** | low | rel. objective gap (J_prod − J_ftol=1e-14)/\|J_prod\| per cell, production objective on the returned plan; reproduced exactly (finder) and independently (mine: 15/18 cells improved, mean 0.181 %, max 0.796 %, flat null 0.158 %, identity control 22/22 bitwise, restart-only arm exactly 0) |
| D0-02 | **verify** | low | L-BFGS-B calls terminating on the iteration cap (status 1 or nit ≥ maxiter) over a solve grid, plus the objective change from maxiter×15; 0 of 420 (finder, reproduced) and 0 of 136 (mine, 6/24/48 h, max nit 62 = 20.7 % of cap), while a 1e-2 ftol mutation costing 1.07 % objective passes `tests/optimality.py` 14/14 and a maxiter=3 mutation fails it |

Both findings also stand as bugs of exactly the severity filed: D0-01 is a
stopping-rule defect with no money or comfort consequence demonstrated; D0-02
is a control that does not control.
