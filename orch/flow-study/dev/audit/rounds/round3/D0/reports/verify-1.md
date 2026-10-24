# Panel D0 — verifier 1 of 2, refute-first

Baseline `ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`. 8-core Apple M1, python
3.11.5, numpy 2.4.6, scipy 1.17.1, OpenBLAS, five thread variables pinned to
`"1"` before every numpy import. `thread_factor` 0.882–0.999 and `load1`
6.50–31.83 across the runs, quoted per run below. **No number in this report is
a wall-clock, CPU or RSS number**: every figure is an objective value, a SEK
cost computed from a returned schedule, a temperature, a kWh, a cell count or a
`_scoped_minimize` call count. `tests/stress.py` was not run, no `tests/run.sh`
was run, the gate lock was neither taken nor stolen, and no production or test
file was edited — every hook is `unittest.mock`.

My own instruments are `tools/audit/round3/D0/verify-1/v1_race.py` (open loop,
four arms), `v1_mpc.py` (closed loop) and `v1_feasible.py` (feasibility
parity). Outputs are the `.txt` files beside them.

---

## 0. The headline: D0-02's perturbation, executed

The finder wrote that D0-02's perturbation was *"not executed as a separate run
inside the fan-out budget"* and offered a substitute arm. `judge.md` rule 2 is
unconditional, so I ran the stated one.

```
D0_NO_POLISH=1 PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/polish_race.py
RESULT cells=32                        RESULT gap_max_pct=0.0000
RESULT cells_with_gap=0                RESULT gap_mean_pct=0.0000
RESULT null_flat_gap_mean_pct=0.0000   RESULT gap_mean_structured_pct=0.0000
RESULT loo_mean_drop_best_pct=0.0000   RESULT comfort_regressions=0
RESULT step0_differs_where_gap=0/0
RESULT thread_factor=0.998   RESULT load1=19.52   concurrent_python=12
```

All 32 `CELL` lines print `gap +0.0000%` and an identical objective to six
decimals. **`to_zero` as stated. The harness is not void under `judge.md` rule
2**, and the same run incidentally proves that the `_MULTI_START_SOLVES` lift
the challenger carries contributes nothing on its own — with the restart
removed, the lifted challenger *is* production, to the last bit.

Full output: `verify-1/perturb_polish_NO_POLISH.txt`.

## 1. Re-running both harnesses as their headers say

Both reproduce, and D0-01's perturbation also goes to zero.

| RESULT | finder | verifier-1 | |
|---|---|---|---|
| `seed_race.py` `gap_max_pct` | 1.0430 | **1.0430** | exact |
| `seed_race.py` `cells_with_gap` | 15 | **15** | exact |
| `seed_race.py` `gap_mean_pct` | 0.1438 | **0.1438** | exact |
| `seed_race.py` `null_flat_gap_mean_pct` | 0.1570 | **0.1570** | exact |
| `seed_race.py` `null_structured_gap_mean_pct` | 0.1419 | **0.1419** | exact |
| `seed_race.py` `comfort_regressions` | 0 | **0** | exact |
| `seed_race.py` `step0_differs_where_gap` | 12/15 | **12/15** | exact |
| `polish_race.py` `gap_max_pct` | 1.1703 | **1.1703** | exact |
| `polish_race.py` `cells_with_gap` | 9 | **9** | exact |
| `polish_race.py` `loo_mean_drop_best_pct` | 0.0100 | **0.0100** | exact |
| `polish_race.py` `step0_differs_where_gap` | 2/9 | **2/9** | exact |
| `D0_NO_EXTRA_SEEDS=1` | 0.0000 ×32 | **0.0000 ×32** | `to_zero` |
| `D0_NO_POLISH=1` | *never run* | **0.0000 ×32** | `to_zero` |

`rerun_seed_race.txt` (thread_factor 0.999, load1 20.81),
`rerun_polish_race.txt` (0.998, 18.60),
`perturb_seed_NO_EXTRA_SEEDS.txt` (0.998, 31.83). The pipeline is
deterministic under a pinned BLAS: every re-run matched to the last printed
digit, so none of the disagreements below is noise.

### One instrument defect: `seed_race.py`'s header is stale

`tools/audit/README.md` requires a harness to carry "the expected value ±
tolerance" because "the judge re-runs it without reading the finding".
`seed_race.py`'s `EXPECTED` block fails that on all four headline numbers, three
of them far outside their own stated tolerance:

| `seed_race.py` EXPECTED | header says | actually prints |
|---|---|---|
| `gap_max_pct` | 0.5618 ± 0.02 | **1.0430** |
| `cells_with_gap` | 8 ± 1 (of 32) | **15** |
| `gap_mean_two_zone_pct` | 0.2107 ± 0.02 | **0.1465** |
| `gap_mean_single_zone_pct` | 0.0000 ± 0.0005 | **0.1411** |

The report's prose is right and the header is stale — it reads like the
two-zone-only run that preceded the grid widening. A judge re-running the
harness cold and comparing against its own header gets four out-of-tolerance
numbers and would reasonably discard a sound instrument. `polish_race.py`'s
header, by contrast, matches its output exactly on all nine values. This is a
header edit, not a measurement problem.

### One mechanism sentence is imprecise (the finding does not rest on it)

The report says `_optimize_space_only` and `_solve_space` seed four points,
"none of them a constant-power schedule". I captured production's actual first
candidate list per cell. In `flat single` and `flat two_zone` the **first seed
is exactly constant at 3.000 kW** — `_price_guess_weights` on a flat curve
returns `clip(1.5 − p/mean, 0.2, 1.0)` = 0.5 everywhere, so the smooth guess
degenerates to `p_max/2`. That is the `f = 0.5` rung of the challenger's own
extra set, and it is present in the two cells where the flat null control is
largest — including `flat two_zone`, the biggest two-zone gap in the grid at
0.5618 %. In the DHW path the third seed is `headroom × 0.5`, constant relative
to a non-uniform box (measured range 0.600–3.000 kW).

So production *does* already seed one constant-power rung on flat prices, and
the challenger still beats it — the winning seed is one of
`f ∈ {0, 0.25, 0.75, 1.0}`. The claim is carried by the perturbation, not by
this sentence, but the sentence should be corrected before it is quoted into a
fix brief as the justification for which rungs to add.

### An id collision the judge should know about

`optimizer.py:194` and `:203` already cite an earlier audit's **`D0-02`** ("the
DISCARDED candidate refining below the shipped result in 5 of 10 price
profiles") and **`D0-01`** ("the low-energy bang-bang seed"). Round 3 reuses
both ids for different claims, and round-3 D0-01 is the *same mechanism* — seed
coverage — that the historical D0-01 comment says was already fixed, with the
comment claiming "a different step-0 action so MPC re-planning does not mask
it". Section 5 measures that claim for the current seed set.

---

## 2. My own instrument and my own metric

**My metric, one line:** per cell the **realised daily bill delta**
`bill_prod − bill_arm` in SEK/day, where
`bill = Σ_t price_t · (space_power_t + dhw_power_t) · Δt` is computed by
`v1_race.py` straight from the schedules each arm returned and the cell's own
price vector, reported in SEK/day and as a share of `bill_prod`; the objective
is reported as an **absolute** delta in objective units beside the finder's
percentage, and **both arms are re-scored under one captured production
objective closure**.

**Why a second definition.** The finder's metric divides by `|objective|`, and
the objective ranges 13.14 → 135.57 over this grid, so the same absolute
improvement reads eight times larger on a summer day than on a cold one. On the
finder's own metric the biggest cell in both findings is `summer_negative`; in
absolute objective units it is not (arm S: `obj_gap_max_abs=0.564626`, which is
the `flat two_zone` cell, not `summer_negative`'s 0.137084).

Arms: **P** production; **S** = D0-01's challenger rebuilt; **Q** = D0-02's
challenger rebuilt; **C** = the cheap fix variant (section 6). My perturbation
`V1_NULL=1` makes every arm a verbatim production call: **all three arms print
`obj_gap_max_pct=0.0000`, `bill_net_sek=+0.0000` and `refinement_ratio=1.0000`
over 32 cells** (`v1_null_perturbation.txt`).

### Is the comparison even fair? Yes, and this is now measured

The one structural worry with a pipeline-level comparison is that each arm
builds its own objective closure, so the two `objective_value`s could be two
functions. `v1_race.py` finds the closure that reproduces production's own
`objective_value` to 1e-9 and then re-scores **both** arms' `(space, dhw)`
plans with it:

```
S_closure_mismatch_max=0.000e+00   S_closure_unresolved_cells=0
Q_closure_mismatch_max=0.000e+00   Q_closure_unresolved_cells=0
```

exact, over 32 winter_cold cells and 96 extension cells. The two arms are
priced by one function. **This attack closes in the finder's favour.**

### Is the "strict superset ⇒ one-sided bound" claim true, or just untested?

The report asserts `challenger ≤ production` "by construction". A pipeline that
calls `_multi_start_minimize` several times is not monotone in general, so I
tested it rather than accepting it: `negative_gap_cells=0` for arm S over
**128 cells** (32 winter_cold + 96 on `winter_mild`, `summer_warm`,
`shoulder`). The claim survives. It is, however, load-bearing on the
`_MULTI_START_SOLVES` lift, not on the seeds — see arm C in section 6, which
drops the lift and goes negative in 5 of 32 cells.

---

## 3. The null control — verified, and it strengthens

**I confirm the finder's naming and I could not break it.** On winter_cold my
own instrument reproduces `null_flat 0.1570` against `null_structured 0.1419`,
ratio **1.106** — the gap is larger at flat prices. Dropping the most
favourable cells makes it *more* so, which is the opposite of a grid artefact:

```
S_null_flat_over_structured        = 1.106
S_null_flat_over_structured_drop1  = 1.447
S_null_flat_over_structured_drop2  = 1.879
```

Widening the weather grid moves the ratio the other way
(`winter_mild`/`summer_warm`/`shoulder`: flat 0.0517 vs structured 0.1194,
ratio 0.433) but **the gap never vanishes at flat prices in either set**, which
is the question `D0.md` §5 actually asks: *"A gap that survives flat prices is
not price optimality; name what it is."* It survives in both. The finder's
naming — basin selection in a non-convex objective, not price optimality — is
**correct and verified**.

Two precisions the judge should carry forward:

- the stronger phrasing "the gap is **larger** at flat" is true on `winter_cold`
  and false on the other three weather profiles. The naming does not depend on
  it; the phrasing should be attached to the weather it was measured on.
- I searched the finder's `REPORT.md`, `FINDINGS.md` and all nine harnesses:
  **D0-01 is nowhere reported as a price defect**. Every mention names it
  basin selection. Nothing to correct.

---

## 4. Money — the metric `D0.md` demands, which neither finding reported

> *"Report SEK/day only beside the flat-price arm and the percentage of the
> daily bill; a 1 % gap on a 60 SEK day is a finding, a 1 % gap on a 2 SEK
> summer day is not."*

### D0-01 (arm S)

| | winter_cold, 32 cells | + 96 extension cells |
|---|---|---|
| net bill delta | **+0.2466 SEK/day** | **−9.7090 SEK/day** |
| net over structured prices only | **−0.9351 SEK/day** | **−9.8518 SEK/day** |
| net over flat cells only | +1.1817 | +0.1428 |
| cells cheaper / dearer | 10 / 5 | 16 / **22** |
| best single cell | +2.3543 (`flat two_zone` — the **null-control** cell) | +0.9993 |
| worst single cell | **−3.4867** (`winter_moderate two_zone`) | −3.7798 |
| net after dropping the best money cell | **−2.1076 SEK/day** | −10.7084 |

The two largest money movements in the whole winter_cold grid are (a) adverse,
−3.4867 SEK/day on an 81.36 SEK day, and (b) in the flat null-control cell. Over
128 cells the superset arm is a clear **net loss**.

That is not an inconsistency in the finding — the objective prices comfort and a
terminal credit as well as energy, and the finder said plainly that the bill
rises in 5 of 15. But it does decide "is the severity earned by consequence".
I therefore measured what the extra money buys:

```
S_dearer_cells_energy_delta_kwh   = +4.4951 kWh   (winter_cold)
S_dearer_cells_bill_sek           = -5.4632 SEK/day
S_dearer_cells_mean_room_delta_c  = +0.0436 C
S_dearer_cells_end_room_delta_c   = +0.1317 C
```
and on the 96-cell extension `+11.9465 kWh` for `−13.5980 SEK/day` at
`+0.0378 °C` of mean room temperature. Where the challenger's objective is
better and its bill worse, the extra kilowatt-hours raise the mean room
temperature by four hundredths of a degree. Whether that is the objective's
fault is D2's question, not mine; for D0 it means the gap has no user-visible
consequence in either direction.

### D0-02 (arm Q)

`bill_net_sek = +0.7781` over 32 cells, of which `+0.6789` is one cell —
`summer_negative single`, **0.679 SEK/day of an 11.34 SEK day**, which is
exactly the case `D0.md` says is not a finding. Drop that cell and the whole
grid is `+0.0992 SEK/day`. The second cell is `winter_moderate two_zone` at
0.200 SEK/day of an 81.36 SEK bill = 0.25 %. Every other gap cell moves by under
0.02 SEK/day and **three of them move the wrong way**.

---

## 5. MPC masking — the test the finder could not finish

`mpc_realised.py` was committed but produced no number; the proxy inside
`seed_race.py` is a one-step comparison. I ran the receding horizon.

`v1_mpc.py`: each hour the policy re-plans a full 24 h horizon from the **true**
thermal state, commits 4 steps, and the state advances through production's own
`_replay_end_state`; 24 hours; realised bill, realised comfort, committed kWh
and end state all reported, so a saving bought by ending the day colder is
visible. `V1_NULL=1` gives `mpc_bill_delta_sum_sek=+0.0000` in all 5 cells.

### Arm S, D0-01 (`v1_mpc_S.txt`, thread_factor 0.895, load1 11.10)

| cell | open-loop bill delta | **closed-loop** | end room Δ | identical committed steps |
|---|---|---|---|---|
| `summer_negative single` | +0.797 | **+0.158** (+1.5 %) | −0.084 °C | 68/96 |
| `shoulder single` | +0.537 | **−0.957** (dearer) | −0.015 °C | 84/96 |
| `flat two_zone` | +2.354 | **−0.868** (dearer) | +0.122 °C | **0/96** |
| `winter_typical two_zone` | +0.436 | **+4.714** | **−0.496 °C**, −2.96 kWh | 54/96 |
| `winter_moderate two_zone` | −3.487 | **−2.784** (dearer) | +0.348 °C | 28/96 |

`mpc_bill_delta_sum_sek = +0.2633` over 5 cells; **3 of 5 cells dearer**; the
sign flips against the open-loop reading in 2 of 5, including the largest
open-loop money win. The one large closed-loop win ends the day half a degree
colder in the room and three quarters of a degree colder in the slab, having
bought 2.96 kWh less — borrowed heat, not a saving.

### Arm Q, D0-02 (`v1_mpc_Q.txt`, thread_factor 0.882, load1 6.50)

`mpc_bill_delta_sum_sek = **−0.9348**` — the restart policy is a net loss over
the five cells. `summer_negative single`, the cell that carries the entire
finding, goes from `+0.679 SEK/day` open loop to **`−0.149 SEK/day` dearer**
closed loop. `shoulder single` is 96/96 identical committed steps and exactly
`0.0000` — fully masked.

### Open-loop step-0 counts at a physical threshold

The finder counts a step-0 difference above `1e-3 kW`, which on a 6 kW pump is
0.017 % of full power. At **1 % of `p_max`**, and adding the first *committed*
hour's energy:

| | finder (`>1e-3 kW`) | mine (`>1 % p_max`) | first committed hour's kWh (`>1 %`) |
|---|---|---|---|
| D0-01, winter_cold | 12/15 | **9/15** | **8/15** |
| D0-01, 96-cell extension | — | **10/39** | 11/39 |
| D0-02, winter_cold | 2/9 | **1/9** | **0/9** |

**D0-02 changes the first committed hour's energy by more than 1 % in zero of
its nine cells.** Combined with the closed-loop sign flip, its gap is not
realised.

---

## 6. Feasibility parity, and the price of the proposed fix

### Parity (`v1_feasible.py`, `v1_feasible.txt`)

My own detectors, on all 32 winter_cold cells × both arms: the returned space
schedule against the bound box captured from the live solver call; comfort
degree-steps from `simulate_trajectory`; tank shortfall and overheat from
`simulate_dhw_only` against **production's own** `requirement`, `draw_rates`,
`initial_temp`, `outdoor_temps` and `max_temp`, captured from
`_plan_dhw_cheapest_first`.

```
S_comfort_regressions=0   S_dhw_shortfall_regressions=0   S_dhw_overheat_regressions=0
Q_comfort_regressions=0   Q_dhw_shortfall_regressions=0   Q_dhw_overheat_regressions=0
pins_exercised=0          power_caps_exercised=0
```

and the physical power bound, checked separately across all 16 DHW cells:
`Σ_t max(0, space_t + dhw_t − p_max)` is **`0.0000` in all three arms** — `P`,
`S` and `Q` alike — with the peak sitting exactly on `6.0000 kW` in 15 of the
16 cells and at 5.64–5.84 kW in the sixteenth. **The finder's
`comfort_regressions=0` is verified.**

Two honesty notes. First, my bounds detector's raw count (`S=3`, `Q=4`) is a
**detector artefact, not a solver defect**: it scores the final plan against a
co-optimisation pass's DHW headroom, and production trips it identically
(4.80e+00 → 4.80e+00 in six of the seven rows, and *lower* in the arm in the
seventh). The physical check above is the real one. Second, this grid builds
**no manual pins and no power caps**, so those two feasibility surfaces of
`D0.md` §3 are untested by both the finder and me — said, rather than folded
into a green tick.

The detectors are live, not dead code: `V1_FEAS_MUTATE=1` (challenger schedule
replaced by `max(p − 1.5 kW, −0.2)`) moves bounds violations `0 → 32/31` and
comfort regressions `0 → 26/26`.

### The fix's price — measured, not argued (arm C)

D0-01's fix note reasons that adding seeds either raises the refinement count
proportionally (which `tests/stress.py`'s per-scenario budgets police at zero
ratchet headroom) or needs the pre-score to prune, and that "the pre-score at a
raw bang-bang seed is a poor predictor of its refined value". I built the cheap
variant and measured both halves. Arm **C** adds the same five constant starts
and leaves `_MULTI_START_SOLVES` at its shipped 4, so the pre-score prunes.

| | arm S (as proposed) | arm C (cheap) |
|---|---|---|
| `_scoped_minimize` calls, 32 cells | 135 → 330, **×2.4444** | 135 → 156, **×1.1556** |
| `obj_gap_max_pct` | 1.0430 | 0.8464 |
| cells improved | 15 | 8 |
| **cells made worse** | **0** | **5** |
| `obj_gap_min_pct` | 0.0000 | **−0.6894** |
| net objective change, 32 cells | +2.421921 units | **−0.666484 units** |

So the cheap variant recovers 81 % of the headline gap at 16 % extra solver
cost **and regresses the objective in 5 of 32 cells, net worse over the grid**.
The finder's fix note is right in substance and now has a number behind it; the
"replace the weakest rung rather than add" route does not work, because the
pre-score prunes a production seed that would have refined better. The
deliverable fix costs **2.44× the L-BFGS-B refinements** and must go to the
owner against the stress budgets, not into a branch.

Arm C also settles the structural question from section 2: without the
`_MULTI_START_SOLVES` lift, a larger seed set is not a superset of what is
*refined*, and the pipeline-level comparison stops being one-sided. D0-01's
one-sidedness is real but comes from the lift, not from the seeds.

---

## 7. Aggregate, leave-one-out

| | D0-01 (arm S) | D0-02 (arm Q) |
|---|---|---|
| mean over 32 cells | 0.1438 % | 0.0462 % |
| drop most favourable | **0.1148 %** | 0.0100 % |
| drop two most favourable | **0.0933 %** | **0.0008 %** |
| net bill after dropping best money cell | −2.1076 SEK/day | +0.0992 SEK/day |

**D0-01's aggregate is not a grid artefact** — it keeps 65 % of its mean after
two cells are removed, and the 96-cell weather extension finds 39 more gap cells
with a larger maximum (4.1754 %). **D0-02's is.** The finder conceded one
carrying cell; there are two, and after both the mean is 0.0008 %, i.e. eight
parts per million of the objective.

### D0-02's cell count is a threshold artefact

`polish_race.py` counts a cell when `gap > 1e-4 %`. L-BFGS-B in this repo runs
with `options={"maxiter": …, "ftol": 1e-6, "eps": 1e-4}`, and `ftol = 1e-6`
**is** a relative-improvement stopping test of 1e-4 %. The count is therefore
taken at exactly the tolerance the solver is contractually entitled to stop at:

```
Q_cells_above_ftol       = 9   (the finder's 9)
Q_cells_above_10x_ftol   = 5
Q_cells_above_100x_ftol  = 3
Q_cells_obj_gap_over_0p1pct = 2
```

Seven of the nine cells sit between 0.0001 % and 0.0194 %. Finding a further
relative descent of 1e-6…2e-4 below a point declared converged at `ftol = 1e-6`
is the tolerance working as specified, not a defect. The honest statement of
D0-02 is **2 of 32 cells**, not 9.

### D0-02's price-shape claim does not survive its own carrying cells

The report says the effect "*is* price-shaped ... That is what a
price-optimality defect is supposed to look like", on
`null_flat 0.0051` vs `null_structured 0.0521`, a factor of ten. But the entire
structured mean is those same two cells. Removing them:

```
Q_null_flat_over_structured        = 0.098   (flat 10x smaller — the claim)
Q_null_flat_over_structured_drop1  = 0.480
Q_null_flat_over_structured_drop2  = 36.193  (flat 36x LARGER)
```

**The null control inverts.** Outside its two carrying cells D0-02's effect is
36 times larger at flat prices than at structured ones — the same signature
D0-01 has, and the same reading: basin/stopping behaviour in a non-convex
objective, not price optimality. D0-02 is filed under the one naming this
project has killed five measurement designs for using.

---

## 8. Votes

### D0-01 — `weaken`, severity `low` (finder said `medium`)

Everything the finding measures is true and reproduces exactly, and the parts
that most often fail here all hold: the perturbation goes to zero, the two arms
are priced by one closure to 0.000e+00 over 128 cells, the one-sided bound holds
with 0 negative cells in 128, comfort and tank feasibility have no regression
with detectors proven live by a mutation control, the aggregate survives
leave-one-out at 0.0933 % after two drops, and the effect generalises to 39 more
cells across three more weather profiles. **Above all, the null control holds
and the naming is right**: the gap survives flat prices in every weather set I
ran and strengthens against structured prices as cells are dropped
(1.106 → 1.447 → 1.879). It is basin selection, it is not price optimality, and
it is reported as such everywhere in the finder's output.

The severity is what does not survive. `verifier.md` §3 asks whether severity is
earned by consequence, and `D0.md` asks for the money:

- net **−9.71 SEK/day** over 128 cells; 22 cells dearer against 16 cheaper;
- the largest single money movement on the primary grid is **adverse**
  (−3.4867 SEK/day), and the largest favourable one is the flat null-control
  cell;
- where the bill rises, the extra kWh buy **+0.04 °C** of mean room temperature;
- closed loop over 24 h, **3 of 5 cells dearer**, net +0.2633 SEK/day, sign
  flipped against the open-loop reading in 2 of 5, and the one large win ends
  the day 0.50 °C colder;
- the first *committed* hour's energy differs in 8 of 15 cells, and step-0 at
  1 % of `p_max` in 9 of 15, not 12 of 15.

A solver-quality defect with a verified mechanism and no realisable consequence
in either money or comfort is `low`. The fix as proposed costs 2.44× the
L-BFGS-B refinements against zero ratchet headroom on the stress budgets; the
cheap alternative regresses the objective in 5 of 32 cells. This is an owner
conversation, not a branch.

### D0-02 — `weaken`, severity `low` (severity unchanged; the claim must be restated)

The mechanism is real and reproduces exactly, and **its never-executed
perturbation now runs and gives `to_zero` in all 32 cells**, so the harness is
not void. L-BFGS-B does stop at a point from which the same solver, same
closure, same budget, can still descend — in 2 cells, by 1.1703 % and 0.2846 %,
comfort no worse, priced by one closure.

Three of the claim's four quantifiers do not survive:

1. **"9 of 32" is a threshold artefact.** The threshold equals `ftol = 1e-6`.
   Above 10× it: 5 cells. Above 100×: 3. Above 0.1 %: **2**.
2. **"price-shaped" is refuted by its own null control.** Drop the two carrying
   cells and the flat-over-structured ratio goes 0.098 → 0.480 → **36.193**.
   Outside those cells the effect is 36× *larger* at flat prices. It should be
   renamed to the same basin/stopping-rule family as D0-01.
3. **It is not realised.** `hour1_energy_differs = 0/9`; closed loop over 24 h
   the net is **−0.9348 SEK/day** and the one cell carrying the whole finding
   flips sign to −0.149 SEK/day dearer. Its open-loop money is 0.679 SEK/day of
   an **11.34 SEK day** — the case `D0.md` names as not a finding.

Severity stays at `low` because `low` is the floor; the claim itself needs
restating to "2 of 32 cells, mechanism only, not price-shaped, not realised
under re-planning". The finder was right to call it `low` and right about
`step0_differs_where_gap` being why.

---

## 9. Files

Harnesses I wrote: `verify-1/v1_race.py`, `verify-1/v1_mpc.py`,
`verify-1/v1_feasible.py`. Outputs: `rerun_seed_race.txt`,
`rerun_polish_race.txt`, `perturb_seed_NO_EXTRA_SEEDS.txt`,
`perturb_polish_NO_POLISH.txt`, `v1_main.txt`, `v1_nullctl_wintercold.txt`,
`v1_energy_ext.txt`, `v1_weather_ext.txt`, `v1_null_perturbation.txt`,
`v1_mpc_S.txt`, `v1_mpc_Q.txt`, `v1_mpc_null.txt`, `v1_feasible.txt`,
`v1_feasible_mutate_control.txt`.

**Not re-run**, and no claim is made about them: `price_seed_race.py`,
`arms_decomposition.py`, `budget_slack.py`, `coopt_gate.py`, `dhw_relocate.py`
and `mpc_realised.py`. The two findings' own primary harnesses are
`seed_race.py` and `polish_race.py`, and both were re-run with both
perturbations. The finder's non-findings table is therefore unverified by me.

Exposure: `CLAUDE.md`, `tools/audit/briefs/verifier.md`,
`tools/audit/briefs/D0.md`, `tools/audit/README.md`, the finder's `FINDINGS.md`,
`REPORT.md`, `d0lib.py`, `seed_race.py` and `polish_race.py`, and the relevant
parts of `custom_components/heatpump_optimizer/optimizer.py`,
`thermal_model.py` and `tests/profiles.py`. No `gh`, no GitHub, no other
verifier's output, no audit register, no `tests/stress.py`, no `tests/run.sh`,
no gate lock.
