# D0 — verifier seat 3 (perturbation, grid artefacts and scope)

Worktree `v-D0-3` at the baseline SHA `c398fc84eec25fc44b60d74aae05b9a2da205884`
(`git log --oneline -1` → `c398fc8`, working tree clean apart from a read-only
copy of this directory's harnesses under `tools/audit/round2/D0/`, needed
because the harnesses resolve `d0lib` relative to the repository root). No
`git checkout/commit/fetch/push`. Scratch: `/private/tmp/claude-501/audit-scratch/D0-3`.
No `docs/`, no other `verify-*.md`, no `gh`, no round-1 register was read.

Every number below was executed by me. All BLAS threads pinned to 1;
`PYTHONPATH=tests/hastub`; run from the repository root. `load1` ranged 11–68
during the runs and `thread_factor` was 1.000 in every harness footer, so no
verdict rests on wall-clock — only on counts, SEK on production's own
objective and on production's own settlement.

## 0. The stack the report was measured on does not exist on this box

The REPORT header says every figure was taken on "python 3.13.1, numpy 2.5.2,
scipy 1.18.1". This machine has exactly one interpreter with numpy/scipy:

```
$ python3 -c "import sys,numpy,scipy;print(sys.version.split()[0],numpy.__version__,scipy.__version__)"
3.11.5 2.4.6 1.17.1
$ /opt/homebrew/bin/python3.13 -c "import numpy"   -> ModuleNotFoundError
$ ls ~/.pyenv/versions                              -> 3.11.5 only, no numpy
$ ls /Library/Frameworks/Python.framework/Versions/*/lib/python3*/site-packages/scipy-*
scipy-1.17.1.dist-info
```

There is no `.venv`, so `tests/run.sh`'s `PYTHON=python3` is this 3.11.5 /
scipy 1.17.1 stack — i.e. the stack the gate actually runs on. I therefore
re-measured everything on it. This is not a formality: the divergences below
are systematic and land exactly where L-BFGS-B's stopping test is
ill-conditioned. **Where the solve is well conditioned the two stacks agree to
four decimals; where the finding lives they do not.** Two examples, both from
this report:

* D0-03 perturbation arm (750 L tank, well conditioned): finder
  `mean_gap_sek_tz=0.2047`, `winter_moderate 0.1984`; mine **0.2047**,
  **0.1984**. Identical.
* D0-03 baseline arm (35 L tank, at the clamp kink): finder `winter_typical
  3.4708`, `winter_moderate 4.1884`; mine **1.1819**, **0.0000**.

Same for D0-01: every no-DHW cell reproduces to four decimals (58.2850 →
58.2850; 3.8025; 3.7419; 2.3670; 1.6850; 0.5668; 0.5367), every DHW-on cell
comes out about half the reported size. So the harnesses are sound and the
capture is honest; the *cell-level magnitudes* the three titles quote are not
a property of the repository, they are a property of a numeric stack that is
not present here. I have voided nothing on this ground alone — the
perturbations still move — but no title should quote a per-cell SEK figure as
if it were reproducible.

## 1. My own metric

At least one number per finding is mine. One line:

> **e2e gap** — per cell, `predicted_cost + peak_cost + deferred_energy_cost`
> of the plan `HeatPumpOptimizer.optimize()` *returns*, under production's
> solver, minus the same three production-computed figures of the plan the
> same `optimize()` returns when `optimizer._multi_start_minimize` re-submits
> its own best answer to itself until the objective stops improving (and,
> where noted, also refines bang-bang seeds at fractions of that answer's
> energy) — i.e. the gap on the object the integration publishes, settled
> production's own way (`savings = baseline − predicted − deferred`), not on
> the recorded sub-problem objective.

Feasibility parity is read off each *returned* plan with production's own
series: `room_temp_trajectory` (single-zone) or `upper_/lower_temp_trajectory`
(two-zone) against the horizon's `temp_min_bounds`/`temp_max_bounds`, and
`dhw_temp_trajectory` against `params.dhw_min_temp`. A cell counts only if the
challenger's floor, ceiling and DHW violations are all no worse.

Harness: `/private/tmp/claude-501/audit-scratch/D0-3/e2e_gap.py`. The
re-seeding harness is `/private/tmp/claude-501/audit-scratch/D0-3/reseed.py`
(metric: gap from deterministic arms only, versus the same race with `k`
uniform-random starts drawn from `default_rng(seed)`).

**The deferred term matters.** My first pass omitted it and reported
`flat/winter_cold/sz/dhw` as 6.31 SEK cheaper; with production's own deferred
settlement the same cell is 2.58 SEK, because the cheaper plan ends the
horizon colder. Any "cheaper plan" number in this dimension that is not
settled overstates the gain — mine now are.

---

## D0-01 — capacity tariff, single-zone

### Re-run of the finder's own command

`race_grid.py --tz 0 --weather winter_cold --quiet --random 3 --opt <tariff15>`

| RESULT | finder | seat 3 |
|---|---|---|
| `cells_with_gap_sz` | 15 | **13** |
| `restart_improves_sz` | 7 | **4** |
| `pg_above_pgtol_sz` | 16 | 16 |
| `mean_gap_sek_sz` | 4.8198 | 4.5703 |
| `max_gap_sek_sz` | 58.2850 | **58.2850** |
| `mean_energy_gap_pct_bill_sz` | 2.517 | **1.333** |
| `mean_restart_gap_sek_sz` | 0.1661 | **0.0232** |
| `loo_mean_gap_pct_sz` | 2.192 | 1.732 |
| footer | — | `thread_factor=1.000 load1=16.67 swapins=0` |

The *whole-race* gap reproduces. The *stall* component does not: 0.1661 →
0.0232 SEK, a factor of seven, and `restart_same` carries the gap in **0 of
16** cells: it is named `best_feasible` in three, but in each of those the gap
is 0.0000, i.e. nothing beat production at all. Every cell with a real gap is
won by `seed_half`, `seed_zero`, `third_cand0`, `budget_warm` or a polish of
one of them. The three cells the report cites as the
stall's evidence — winter_typical/dhw 0.92, winter_extreme/dhw 0.66,
shoulder/dhw 0.75 — are 0.0004, 0.0628 and 0.0000 here. The mechanism the
title asserts ("stops on a stalled iteration") is not what produces the
reproducible part of the gap; the basin/seed coverage is.

### Perturbations — all three move, so the harness is not measuring a constant

| perturbation | quantity | before | after |
|---|---|---|---|
| `D0_PERTURB=ftol9` | `restart_improves_sz` | 4 | **0** |
| | `mean_restart_gap_sek_sz` | 0.0232 | **0.0000** |
| | `cells_with_gap_sz` | 13 | 8 |
| | `loo_mean_gap_pct_sz` | 1.732 | 1.172 |
| | `prod_nit` (winter_typical/dhw) | 29 | 45 |
| `--opt "peak_count":16` | summer_negative/nodhw gap | 58.2850 | **0.1296** (finder: 0.130) |
| | `mean_gap_sek_sz` | 4.5703 | **0.5782** (finder: 0.525) |
| *(mine)* tariff removed | `mean_gap_sek_sz` | 4.5703 | **0.1117** |
| | `cells_with_gap_sz` | 13 | 5 |
| | `prod_pg` | 0.025–20 | exactly 0.0 in 10/16 |

`ftol9` does **not** touch the 58 SEK cell (58.2850 → 58.1688) and makes
winter_extreme/nodhw worse (3.80 → 4.54); `peak_count=16` does. The two halves
of the proposed fix address two different defects, and only the second one
addresses the headline cell. My no-tariff control is the cleanest statement of
scope in this finding: without the capacity tariff the same sixteen solves are
41× closer to optimal and stationary to machine zero in ten of them. The
finding is genuinely tariff-specific.

### Re-seed (the gain is not the draw)

`reseed.py --tz 0 --dhw 0 --weather winter_cold --seeds 0,1,2 --starts 0,4,8 --opt <tariff15>`

```
RESULT det_cells_with_gap=8 count            (with ZERO random starts)
RESULT det_mean_gap_sek=8.9332 SEK
RESULT k4_mean_gap_by_seed=8.9332,8.9349,9.2261 SEK   spread 0.2929
RESULT k8_mean_gap_by_seed=8.9332,8.9349,9.2261 SEK   spread 0.2929
RESULT k4_random_only_contribution=0.0982 SEK
```

8/8 cells have their full gap with no random start at all; the random arms add
1.1 % of it and never create it. The 58.285 SEK cell is `seed_half`, identical
at every seed and every `k`. **The findings in this dimension are not seed
artefacts** — that attack fails and I say so.

### Leave-one-out over the 16 cells

| aggregate | value |
|---|---|
| mean gap, all 16 | 4.5703 SEK / 6.605 % of objective |
| **drop the single most favourable cell** | **0.9893 SEK / 1.732 %** |
| drop the two most favourable | 0.7883 SEK / 1.554 % |
| median | 0.5302 SEK / 0.589 % |
| LOO mean range over all 16 leave-outs | 0.9893 – 4.8750 SEK |

92 % of the aggregate is `summer_negative/winter_cold/sz/nodhw`. On the
shipped plan (below) it is 95 %.

### My number: does it reach the plan the integration publishes?

`e2e_gap.py --tz 0 --weather winter_cold --fracs 0.4,0.5,0.6,0.8,1.0 --opt <tariff15>`

```
RESULT cells=16  e2e_cells_with_gap=5  e2e_cells_worse=1  e2e_parity_ok=15
RESULT e2e_mean_gap_sek=3.8281 SEK      e2e_max_gap_sek=56.8191 SEK
RESULT e2e_loo_mean_gap_sek=0.2953 SEK  e2e_loo_dropped=summer_negative/winter_cold/sz/nodhw/24h
RESULT thread_factor=1.000 load1=35.65
```

The 58 SEK cell is real and it is *money*, not an objective artefact:
production ships a plan whose own `peak_cost` is **60.00 SEK** (energy 11.34,
deferred −0.93) where a half-box seed ships one at **13.59 SEK total** with
identical comfort (`under` 0.0000 both). A capacity charge, once set, is not
undone by re-planning, so the finder's MPC argument does not bound this cell.

But that is one cell, and it needs one weather. I swept the five weathers
(`--price summer_negative --tz 0 --dhw 0 --opt <tariff15>`):

| weather | sub-problem gap | e2e settled gap | prod peak_cost |
|---|---|---|---|
| winter_cold | 58.2850 (79.7 %) | **+56.8191** | 60.00 |
| winter_mild | 0.2370 | 0.0000 | 0.00 |
| summer_warm | 0.0000 | 0.0000 | 0.00 |
| summer_cool | 0.0148 | −0.0136 | 0.00 |
| shoulder | 0.0091 | −0.1197 | 0.00 |

**1 of 5.** Drop it and the shipped-plan aggregate is 0.2953 SEK/day.

### Null control at `profiles.prices("flat")` — the finding fails it

The two flat cells are in every sweep above. On the sub-problem their gap is
0.5432 and 0.4811 SEK (0.58 %, 0.57 %), restart 0.0000 — the finder reports
this. On the *shipped settled plan* it is worse than that:

| arm | mean e2e gap |
|---|---|
| the two `flat` cells | **1.3896 SEK** |
| the twelve priced cells (excluding `summer_negative`) | **0.1375 SEK** |

The realised gain is **ten times larger with no price spread than with
one** (10.1×). Outside the single negative-price cell, this is not a price-optimality
gain; it is a solver-coverage gain that the capacity tariff exposes.

### Scope (fraction of configurations in which it holds)

| axis | configuration | holds? |
|---|---|---|
| capacity tariff | on | 13/16 cells, mean 4.57 SEK |
| | **off** | 5/16 cells, mean **0.1117 SEK**, pg = 0 in 10/16 |
| DHW | off | 8/8 cells; mean 1.88 SEK excl. summer_negative; e2e mean 0.163 excl. it |
| | **on (the default)** | 5/8 cells; sub-problem mean 0.207 SEK; **e2e mean 0.411 SEK, of which 2.58 is the flat cell** |
| topology | single-zone | 13/16 |
| | two-zone + tariff + DHW | 7/8 cells, mean 0.6404 SEK, LOO 0.260 %, restart improves 5/8 |
| horizon | 24 h | LOO 1.732 % |
| | 48 h (sz, nodhw, tariff) | 8/8 cells, LOO **2.525 %**; grows with the horizon |
| weather | 5 pairings for the headline cell | 1/5 |

The class of defect holds broadly (tariff on: 13/16 sz, 7/8 tz, 8/8 at 48 h).
The **title's magnitude** does not: "1–4 SEK/day" is the no-DHW cells
(1.69/3.80/3.74 SEK, which reproduce exactly); with DHW on — the shipped
default — the same sixteen solves give 0.207 SEK/solve on the sub-problem.

### Vote — `weaken(low)`

Decisive number: **on the shipped, settled, feasibility-parity plan the gap is
0.2953 SEK/day once the single most favourable of sixteen cells is dropped,
and the flat-price cells (1.3896 SEK) beat the priced cells (0.1375 SEK) by
10.1×.** Add that the stall mechanism the title names recovers 0.0232 SEK
(not 0.1661) and wins no cell, and that the finder's own MPC arm already
reports 0.18 SEK/day with the largest realised gain at flat prices.

Corrected title I would accept:

> *With a capacity tariff the single-zone solver leaves the top-k peak
> plateau in a worse basin than a half-box or bang-bang seed; with DHW off the
> plan is 1.7–3.8 SEK/day dearer on its own objective, and in one cell
> (negative prices with the coldest weather, 1 of 5 weather pairings) it ships
> a 60 SEK capacity charge that a seeded solve avoids at equal comfort. The
> gap is not removed by tightening `ftol`; `peak_count` = number of windows
> removes it. Outside that cell the realised, settled gain is 0.30 SEK/day and
> is larger at flat prices than at priced ones.*

I flag for the judge: if the finding is re-scoped to the peak-plateau cell
alone, the 60 SEK monthly capacity charge is a month-scale consequence that
re-planning cannot undo, and a case for `medium` could be rebuilt on that one
cell. On the finding as written — a 1–4 SEK/day aggregate — `medium` is not
earned.

---

## D0-02 — two-zone FACTR stops

### Re-run (the 16-cell subset the report cites)

`race_grid.py --tz 1 --weather winter_cold --quiet --random 2`

| RESULT | finder (subset) | seat 3 |
|---|---|---|
| cells with a gap | 13/16 | **13/16** |
| `restart_improves_tz` | 7 | **6** |
| `mean_restart_gap_sek_tz` | 0.2183 | **0.1997** |
| `mean_gap_sek_tz` | 0.449 | 0.3361 |
| `pg_above_pgtol_tz` | 16/16 | **16/16** |
| winter_narrow/tz/dhw restart | 2.163 | **2.3291** (gap 2.5475) |
| flat cells mean gap | 0.732 | 0.5645 |

This one reproduces. It is the only finding of the three whose headline cell
lands in the same place on this stack.

### Perturbation — moves

`D0_PERTURB=restart` (subset): `mean_restart_gap_sek_tz` **0.1997 → 0.0017**
(finder 0.2183 → 0.0030); `mean_gap_sek_tz` 0.3361 → 0.1986;
winter_narrow/tz/dhw 2.5475 → 0.3158; `restart_improves_tz` 6 → 3. Not a
constant.

### Leave-one-out and the one-cell question

Sub-problem, 16 cells: mean 0.3361 SEK, LOO drop-most-favourable
0.244 % of objective. On my shipped-plan metric it is much starker:

`e2e_gap.py --tz 1 --weather winter_cold` (restart-until-flat, settled)

```
RESULT cells=16  e2e_cells_with_gap=7  e2e_cells_worse=1  e2e_parity_ok=15
RESULT e2e_mean_gap_sek=0.2088 SEK   e2e_max_gap_sek=2.3738 SEK
RESULT e2e_loo_mean_gap_sek=0.0645 SEK
RESULT e2e_loo_dropped=winter_narrow/winter_cold/tz/dhw/24h
```

**`winter_narrow/winter_cold/tz/dhw` is 71.1 % of the entire benefit of the
finding's own proposed fix across sixteen cells.** Drop it and the fix is
worth 0.0645 SEK/day — 0.06 % of an ~85 SEK bill. In that cell the fix is also
strictly better on comfort (production `under` 0.0079 K-steps, fix 0.0000), so
it survives parity; in one other cell the fix is 0.0746 SEK *worse*.

### Null control — passes for the component claimed, at 24 h only

At `profiles.prices("flat")` the restart gap is 0.0000 and 0.0011 SEK, against
a non-flat mean of 0.2282 SEK: the stall component does vanish without a price
signal, as claimed. Two caveats, both executed:

* The *whole-race* gap does the opposite (flat mean 0.5645 vs non-flat
  0.3035); the finder already books this as a non-finding, and my numbers
  agree.
* At 48 h (`--tz 1 --dhw 1 --hours 48`) the largest cell of eight **is** the
  flat one: gap 1.2516 SEK, restart 0.8052 SEK, against a mean restart gap of
  0.1458. The "price-signal stall" reading holds at 24 h and inverts at 48 h.

### Scope

| axis | value |
|---|---|
| two-zone, 24 h | 13/16 cells; restart 6/16 |
| two-zone + capacity tariff, DHW on | 7/8 cells, mean 0.6404 SEK, restart 5/8 |
| two-zone, 48 h, DHW on | 7/8 cells but mean 0.3446 SEK / 2 days = 0.17 SEK/day, LOO 0.135 % |
| single-zone (finder's control) | 6/80 restart cells, 0.0026 SEK — not re-run by me |
| 6 h (finder's control) | 0/16 — not re-run by me |
| shipped plan, all 16 | 7 better, 1 worse, LOO 0.0645 SEK/day |

### Vote — `verify` (severity stays `low`)

Decisive number: **the restart perturbation drives `mean_restart_gap_sek_tz`
from 0.1997 to 0.0017 SEK, and the shipped-plan benefit after dropping the one
lucky cell is 0.0645 SEK/day.** The claim is true, the perturbation moves, the
null control passes for the component claimed, and `low` is exactly what
0.065 SEK/day deserves. The report already discloses the one-cell dependence
(`drop_most_favourable: 0.025`) and the masking, so nothing here is hidden.
The 48 h flat inversion should be recorded beside the claim.

---

## D0-03 — small buffer tank with a mixing valve

### Re-run of the finder's own command

`race_grid.py --tz 1 --dhw 0 --weather winter_cold --quiet --random 3 --cfg <small tank> --state <32 °C>`

| RESULT | finder | seat 3 |
|---|---|---|
| `cells_with_gap_tz` | 5/8 | **5/8** |
| `pg_above_pgtol_tz` | 8/8 | **8/8** |
| `mean_gap_sek_tz` | 1.1333 | **0.6898** |
| `max_gap_sek_tz` | 4.1884 | 3.6364 |
| `mean_energy_gap_pct_bill_tz` | 4.396 | 5.531 |
| `loo_mean_gap_pct_tz` | 0.804 | **0.496** |
| `null_flat_mean_gap_sek_tz` | 0.1411 | **0.0000** |

Per cell the two runs do not agree on *which* cells carry the gap:

| cell | finder | seat 3 |
|---|---|---|
| winter_typical | **3.4708** (3.90 %) | 1.1819 (1.36 %) |
| winter_extreme | 1.05 | **3.6364** (2.80 %) |
| winter_moderate | **4.1884** (4.00 %) | **0.0000** |
| winter_narrow | 0.00 | 0.2962 |
| summer_negative | 0.00 | 0.3434 |
| shoulder | 0.00 | 0.0602 |
| summer_typical | 0.22 | 0.0000 |
| flat | 0.1411 | 0.0000 |

Both of the title's cells move; one to zero. The count (5/8), the
stationarity failure (8/8, pg 24–7.0e3 SEK/kW) and the shape survive; the
quoted "3.5–4.2 SEK/day" does not. See §0 — the 750 L arm of the *same*
harness agrees with the finder to four decimals, so this is the kink, not the
harness.

### Perturbation — moves, and lands on the finder's own number

`buffer_tank_volume` 35 → 750 L (the golden `valve_storage` config):

| quantity | 35 L (mine) | 750 L (mine) | 750 L (finder) |
|---|---|---|---|
| `mean_gap_sek_tz` | 0.6898 | **0.2047** | 0.2047 |
| winter_typical | 1.1819 | **0.0000** | 0.0000 |
| winter_moderate | 0.0000 | **0.1984** | 0.1984 |
| `prod_pg` range | 23.6 – 7.0e3 | **0.0027 – 0.18** | ≤ 0.18 |

The projected gradient falls by four orders of magnitude. The mechanism —
the tank clamp kinks the objective at the tightened cap and L-BFGS-B stops on
it — is confirmed.

### The comfort breach reproduces

Production's own plan breaches the comfort floor where the challenger does
not, in the two cells that carry the gap:

| cell | production `under` | best challenger `under` |
|---|---|---|
| winter_typical/tz/nodhw | **0.0229** K-steps | 0.0000 |
| winter_extreme/tz/nodhw | **0.0365** K-steps | 0.0000 |

(finder: 0.112 on winter_typical). Smaller than reported, same sign, same
cells-with-a-gap. The challenger is cheaper *and* warmer.

### My number: the shipped plan, settled, with parity

`e2e_gap.py --tz 1 --dhw 0 --weather winter_cold --fracs 0.6,0.8,1.0,1.2 --cfg <small tank>`

```
RESULT cells=8  e2e_cells_with_gap=5  e2e_cells_worse=1  e2e_parity_ok=7
RESULT e2e_mean_gap_sek=1.2352 SEK   e2e_max_gap_sek=4.7076 SEK
RESULT e2e_loo_mean_gap_sek=0.7392 SEK
```

The 4.7076 SEK cell (`winter_moderate`) **fails feasibility parity** — the
improved solver's plan breaches the floor by 0.0373 K-steps where
production's does not — so it must be discarded, exactly as the brief
requires. Parity-clean, over the seven remaining cells:

| | value |
|---|---|
| mean settled gap | **0.7392 SEK/day** |
| max settled gap | **1.9354 SEK/day** (2.50 % of a 77.57 SEK settled bill) |
| parity-clean LOO (drop most favourable) | 0.5398 SEK/day |
| cells where the "fix" is worse | 1 (−0.6927 SEK) |
| `flat` (null control) | **0.0000** |

Note how much the settlement matters here: without production's
`deferred_energy_cost` the same run reads 7.5550 SEK on winter_typical; with
it, 1.9354. The 3.5–4.2 SEK/day in the title is an unsettled sub-problem
figure.

### Null control — passes cleanly

`profiles.prices("flat")` gives 0.0000 SEK on the sub-problem and 0.0000 SEK
on the shipped plan (the finder reported 0.1411). **This is the one finding of
the three whose gain does not survive flat prices.** It is a genuine
price-optimality finding: the kink only bites when a price spread makes the
plan want to charge a tank too small to hold the charge.

### Scope

| axis | result | holds? |
|---|---|---|
| two-zone, DHW off (as claimed) | 5/8 price profiles; parity-clean settled mean **0.7392** SEK/day, max 1.9354 | yes |
| two-zone, **DHW on** | 7/8 cells with a gap; 2/8 fail parity; parity-clean settled mean **1.8742** SEK/day, max 4.8924 (summer_negative, 22.8 % of its bill), LOO 1.2706 | **yes, and larger** |
| **single-zone**, same small tank and valve | **1/8** cells; mean 0.0257 SEK; LOO **−0.0430** SEK (the "fix" is net worse); 1 cell −0.3007 | **no** |
| big tank (750 L) | mean gap 0.6898 → 0.2047, pg → ≤ 0.18 | perturbation |
| flat prices | 0.0000 (nodhw); with DHW on the flat cell's 0.3041 SEK fails parity and is discarded | null clean |
| 48 h | **not measured** | — |

So the finding is two-zone-specific: with the identical small tank, valve and
state, the single-zone solve is at its optimum in 7 of 8 price profiles and
the proposed fix costs 0.043 SEK/day on average. That is a scope limit the
report does not state.

### Vote — `verify` (severity stays `medium`)

Decisive number: **the tank perturbation drives `mean_gap_sek_tz` 0.6898 →
0.2047 and `prod_pg` from 7.0e3 to 0.18, while the flat-price null is 0.0000
and production's shipped plan breaches the comfort floor (0.0229 / 0.0365
K-steps) in the two cells where a bang-bang seed is both cheaper and at
0.0000.** Medium is earned by the comfort breach plus the settled shipped-plan
gap — 0.74 SEK/day mean with DHW off, **1.87 SEK/day mean and 4.89 SEK/day max
with DHW on**, all after parity filtering — not by the quoted SEK figure.

The title must be corrected — it quotes two cells that do not reproduce and an
unsettled number:

> *A **two-zone** house with a small buffer tank and a mixing valve leaves the
> cap-tightened re-solve at a kink (|proj. grad| 24–7.0e3 SEK/kW in 8/8
> cells): in 5 of 8 price profiles a bang-bang or zero seed is cheaper on the
> same objective, worth 0.7 SEK/day mean (max 1.9) with DHW off and 1.9
> SEK/day mean (max 4.9) with DHW on, measured on the shipped plan after
> production's own deferred settlement and after discarding every challenger
> that breaks comfort parity; in two cells production's own plan breaches the
> comfort floor while the challenger does not. Single-zone is unaffected
> (1/8 cells, LOO −0.04 SEK). Raising the tank to 750 L removes it; flat
> prices remove it.*

---

## Voided

Nothing. All three harnesses hook the named production symbols, all three
stated perturbations move the stated quantity in the stated direction, and no
RESULT is computed from constants. What fails is not the instrumentation but
the aggregation: two of three titles quote per-cell SEK figures that are
neither stack-reproducible nor robust to dropping one cell.

## What I did not do

* `rolling_gap.py` and `dhw_coopt.py` were not re-run — my e2e metric replaces
  the single-solve→plan step, but it is a one-shot solve, not a receding
  horizon, so the finder's MPC numbers stand un-verified by me.
* D0-03 at 48 h did not run. D0-01's `--random 3` default seed is the only one
  used inside `race_grid.py`; the seed sweep is in `reseed.py` instead.
* `race_scenarios.py` (the golden feature scenarios) was not re-run.
* No full `tests/run.sh` gate: `/tmp/hpo-gate.lock` was held by another
  worktree throughout and nothing in my verdicts needs it.
