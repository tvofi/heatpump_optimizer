# D0 — verifier seat 1 (OWN-HARNESS stance)

Worktree `v-D0-1` at `c398fc84eec25fc44b60d74aae05b9a2da205884`, clean of any
production or test edit (`git status`: the only untracked path is
`tools/audit/round2/D0/out/`, which the finder's own harness writes when it is
run from a repository root; its five JSONs are copied to my scratch dir).
Pinned stack `tvofi-claude/.venv`: python 3.13.1, numpy 2.5.2, scipy 1.18.1,
threadpoolctl 3.6.0 — the stack the finder's report names. A second,
*different* stack (python 3.11.5, numpy 2.4.6, scipy 1.17.1, same
threadpoolctl) was used deliberately as a robustness arm. All five BLAS
variables pinned to 1 before numpy in every harness; `thread_factor` 1.000–1.024
throughout. `load1` ran 21–91 for the whole session (ten other auditors);
**no wall or CPU number is offered as evidence anywhere below.** Everything
that decides a vote is a count, an exit status, a projected-gradient norm or a
SEK figure produced by production code, all of which are contention-immune.

## My harness and my metric

`/private/tmp/claude-501/audit-scratch/D0-1/own_race.py`. I did **not** reuse
`d0lib.Recorder`, `race_grid.py` or any of the finder's race code as proof. My
rig is an *end-to-end* race, not a per-call one:

* the only patch is `mock.patch.object(optimizer, "_multi_start_minimize", …)`
  — the seam `tests/optimality.py` itself uses;
* the challenger implements restart-until-flat (re-submit the winner to the
  identical call until the objective stops improving, cap 6) plus box seeds
  (lb / midpoint / ub) and `_price_ranked_start` bang-bang seeds at 0.7/1.0/1.3
  of the winner's energy — **every one of those solves is production's own
  `_multi_start_minimize` invoked on a single-candidate list**, so bounds,
  `args`, options, the `_bounds_supported_by_batch` decision and the
  `_batch_fd_gradient` jac path are production's by construction, not
  re-implemented;
* both arms then run the *whole* `HeatPumpOptimizer.optimize()` pipeline —
  `_tighten_buffer_caps` re-solves, pin-safety, DHW planning and all — and I
  compare the two `OptimizationResult`s;
* scenarios come from `tests/golden.py:make(...)` and `tests/profiles.py`.

**My one-line definition of a cheaper plan.** *A challenger plan is cheaper iff
the production pipeline run with the challenger solver returns an
`OptimizationResult` whose bill — `predicted_cost + peak_cost`, both computed
by production — is lower by more than 1e-3 SEK, AND whose comfort violation
(degree-steps outside `OptimizationConfig.get_temp_bounds`, on the very series
`_comfort_terms` scores: `room[1:]` single-zone, `upper[1:]`+`lower[1:]`
two-zone) and DHW violation (degree-steps of `dhw_temp_trajectory[1:]` below
`params.dhw_min_temperature`) are each no worse than production's.*

`predicted_cost` is space+DHW energy on the DHW path (optimizer.py:4822) and
space-only on the other (:2898), and `dhw_heating_cost` is a slice of it, so it
is never added twice. I also report `bill + deferred_energy_cost` (production's
own end-of-horizon settlement) so a plan cannot look cheap by ending the day
cold, and the achieved `objective_value` of both arms, which is the finder's
quantity.

**Both numbers are reported everywhere, because they disagree.** A lower
objective is not the same thing as a lower bill: the objective prices comfort
*pull* (distance from target inside the band) that the bill does not. In
16 tariff cells the challenger's objective was better in 15 and its **bill was
worse in 3**. Any D0 verdict that quotes only one of the two is quoting the
half that suits it.

## Non-negotiables, discharged

1. **Feasibility parity before any cheaper verdict.** Enforced per cell by the
   definition above; a cell that fails parity contributes 0 to every gap I
   aggregate. Parity did fail: 4 of 16 `tz24` cells, 2 of 8 `smalltank` cells
   and 4 of 8 `bigtank` cells were challenger wins bought by breaching comfort,
   and are excluded. Both arms' violations are printed per cell.
   DHW: identical in every arm of every cell (the DHW schedule is fixed before
   the space stage), so no gain here is a skipped hot-water charge — stated as
   a measurement, not by construction.
2. **Flat-price null control.** `profiles.prices("flat")` is a cell of every
   grid I ran and I report flat vs non-flat means separately for all seven.
3. **Leave-one-out.** Every grid has 8 or 16 cells; every aggregate is given
   with the most favourable cell dropped.

---

## D0-01 — capacity tariff, single-zone stall on the top-k peak plateau

### Re-run of the finder's harness (exact)

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 0 \
  --weather winter_cold --quiet --random 3 --tag tariff15_baseline \
  --opt '{"peak_price_per_kw":20.0,"peak_threshold_kw":6.0,"peak_window_minutes":15,"baseline_load_kw":1.0}'

RESULT cells_with_gap_sz=15            (report: 15)
RESULT restart_improves_sz=7           (report: 7)
RESULT pg_above_pgtol_sz=16            (report: 16)
RESULT mean_gap_sek_sz=4.8198          (report: 4.8198)
RESULT max_gap_sek_sz=58.2850          (report: 58.2850)
RESULT mean_energy_gap_pct_bill_sz=2.517   (report: 2.517)
RESULT mean_restart_gap_sek_sz=0.1661  (report: 0.1661)
RESULT loo_mean_gap_pct_sz=2.192       (report: 2.192)
RESULT thread_factor=1.000  load1=74.45
```

Every stated figure reproduces to the last digit printed. Nothing differed.

### My own number

`own_race.py --grid tariff15 --mode full`, same 16 cells, end-to-end:

```
RESULT mean_gap_obj_sek=4.7942   LOO 1.2281   flat 0.5053   non-flat 5.4069
RESULT cells_obj_gap=15 of 16
RESULT mean_gap_bill_sek=6.0691  LOO 2.5415   (12/16 cheaper, 3/16 DEARER)
RESULT mean_gap_pct_bill=10.78 % LOO 5.98 %
RESULT pg_above_pgtol=16 of 16
RESULT restart_improves=8 of 16  (restart-until-flat; the finder's single
                                  re-submission finds 7)
RESULT parity_failures=0         thread_factor=1.017
```

Cell-by-cell my objective gaps land on the finder's to four decimals wherever
the winning arm coincides — `winter_typical/dhw` 0.9187 vs 0.9187,
`winter_extreme/dhw` 0.6567 vs 0.6567, `summer_typical/nodhw` 2.3670 vs 2.3670,
`shoulder/nodhw` 0.5367 vs 0.5367, `summer_negative/nodhw` **58.2850 vs
58.2850**. Two independently written harnesses, one racing a recorded call and
one racing the whole pipeline, agree to 1e-4 SEK.

**The decisive cell, in production's own published fields**
(`summer_negative × winter_cold`, single-zone, no DHW):

| | peak kW | `peak_cost` | energy | bill | comfort under | status |
|---|---|---|---|---|---|---|
| production | 7.000 | **60.000** | 11.338 | 71.338 | 0.0000 | **"optimal"** |
| challenger | 6.000 | 0.000 | 12.355 | 12.355 | 0.0000 | — |

Production spends 60.00 SEK of capacity charge to save 1.02 SEK of energy, at
identical comfort, and labels the result `optimal`; L-BFGS-B stopped at
`nit=9` on `CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH`. The threshold
is 6 kW, the plan sits at 7 kW, and 20 SEK/kW × 3 tied windows × 1 kW = exactly
the 60.00 — i.e. three metering windows tied at the peak with `peak_count=3`,
which is the plateau the mechanism describes, arithmetically visible.

### Perturbations (both run; both move)

* `D0_PERTURB=ftol9`, finder's harness: `restart_improves_sz` 7 → **0**;
  `mean_restart_gap_sek_sz` 0.1661 → **0.0000**; `cells_with_gap_sz` 15 → **10**;
  `mean_energy_gap_pct_bill_sz` 2.517 → **1.385**; `prod_nit` on
  winter_typical/dhw 26 → **70**. Every one matches the report. It does *not*
  fix the plateau cell (58.285 → 58.169), which is the report's own claim.
* `peak_count` 3 → 16 (config), my harness: `mean_gap_obj_sek` 4.7942 →
  **0.6520**; the plateau cell 58.2850 → **0.3561**, and production's own bill
  there falls 71.338 → **13.242** — with a gradient on every tied window
  production stops buying the peak itself. Mechanism confirmed, not asserted.

### Attacks I ran

* **Contention** — no timing evidence offered; `thread_factor` 1.000/1.017.
* **Negative control on my own harness.** Same topology, same weather, same
  8 prices, same challenger, **tariff switched off** (`notariff_sz`):
  `mean_gap_obj_sek` **0.1098** (LOO 0.0732), `cells_obj_gap` 5/16,
  `pg_above_pgtol` **8/16**, mean bill gap LOO 0.0039 SEK. Turning the capacity
  tariff on is what takes the objective gap from 0.11 to 4.79 SEK and the
  non-stationary count from 8/16 to 16/16. My rig does not manufacture gaps.
* **Flat-price null control.** flat mean objective gap 0.5053 vs non-flat
  5.4069 (10.7×); dropping the plateau cell, non-flat is still 1.340 vs 0.505
  (2.65×). Passes. The *restart* sub-component is weaker than claimed, though:
  the report says the flat cells' restart gap is 0.000, and under a single
  re-submission it is; under restart-until-flat the `flat/nodhw` cell still
  yields 0.1248 SEK. So "the stall component vanishes without a price signal"
  is true of one restart, not of the rule the fix proposes.
* **Grid artefact / LOO.** 16 cells. The 58 SEK cell is one cell and it is the
  one LOO drops; the report drops it and quotes 2.192 % of objective, which I
  reproduce. My own LOO: objective 1.2281 SEK, bill 2.5415 SEK.
* **Cross-stack robustness.** Re-ran three cells on python 3.11.5 / numpy 2.4.6
  / scipy 1.17.1. The plateau cell is **byte-identical** (bill 71.338 → 12.355,
  objective gap 58.2850, pg 0.0254) — not a BLAS artefact. Small cells are not:
  `winter_typical/dhw` collapses 0.9187 → 0.0003 on the other stack.
* **Physicality of the decisive cell.** `summer_negative × winter_mild` instead
  of `winter_cold`: gap 58.285 → **0.2967 SEK on a 0.678 SEK bill**, peak charge
  zero. The 58 SEK lives entirely in a synthetic pairing of a July price curve
  with a January cold snap. The report says so itself.
* **Reachability.** Real: `CONF_PEAK_TARIFF_*` are config-flow options and
  `coordinator.py:4562` sets `peak_price_per_kw` from
  `tariff.marginal_price_per_kw`; `DEFAULT_PEAK_TARIFF_COUNT = 3`
  (`const.py:315`) is the default that produces the plateau.
* **Severity by consequence.** The single-solve harm is real and material
  (LOO 2.19 % of objective, 2.54 SEK/day of bill). The realised harm is not:
  the finder's own closed loop settles at 0.18 SEK/day and is **larger at flat
  prices** (+1.445 SEK/2 d) than at winter_typical (+0.355). That bounds it
  below high, which is exactly the severity claimed.
* **The fix, against the repo's own gate — executed, not argued.**
  `restart-until-flat` is not algebraically the shipping code (which runs two
  starts and keeps the best, no restart). I patched it in at the same seam and
  ran `tests/optimality.py`
  (`/private/tmp/claude-501/audit-scratch/D0-1/fix_gate.py`):
  `RESULT optimality_exit=0`, **ALL 11 OPTIMALITY CHECKS PASSED** — including
  challenger 3 (starved budget: 67.76 → 64.91 SEK, still the required margin)
  and challengers 4/5 (batched-FD bit-identity, both zones, DHW on and off).
  The gate's own two plans are **bit-unchanged**: 23.28 SEK single-zone and
  58.30 SEK two-zone under stock and under the fix alike, matching my negative
  control — so the golden drift the findings predict is confined to the
  tariff / valve / two-zone-narrow fixtures, not the core paths.
  The fix's *cost* is understated, though: I measured **mean 3.11 extra
  L-BFGS-B solves per call (max 6)** on the two-zone winter_cold grid and
  20 extra over 9 calls (2.22/call) on the optimality gate — not "roughly one".
  `_MULTI_START_SOLVES = 2` is justified in-code by Raspberry-Pi-class
  hardware, so the fixer must price that. Second half of the fix:
  `tariff.peak_cost` is called both from `_grid_terms` (the objective) and from
  `_grid_report` (the *published* `peak_cost` field), so a smooth top-k changes
  a user-visible cost figure, not only the search.

### Vote: **verify (medium)**

Deciding number: on `summer_negative/winter_cold/sz/nodhw` production returns a
7.000 kW plan carrying 60.000 SEK of `peak_cost` against a challenger's 6.000 kW
plan carrying 0.000, at identical comfort (under 0.0000 both) — 58.98 SEK of
bill on production's own published fields, byte-identical on two numpy/scipy
stacks, and collapsing to 0.356 SEK under `peak_count=16`.

---

## D0-02 — two-zone FACTR stops at non-stationary points

### Re-run of the finder's harness

I ran the 16-cell subset the report cites, not the 160-cell full grid: the box
carried `load1` 21–91 all session and a full grid would have taken hours of
shared CPU for numbers the report already states per-cell for this subset.

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py \
  --tz 1 --weather winter_cold --quiet --random 2

RESULT cells_with_gap_tz=13 of 16      (report: 13/16)
RESULT restart_improves_tz=7           (report: 7/16)
RESULT mean_restart_gap_sek_tz=0.2183  (report: 0.2183)
RESULT mean_gap_sek_tz=0.4494          (report: 0.449)
RESULT pg_above_pgtol_tz=16 of 16      (report: 16/16)
RESULT null_flat_mean_gap_sek_tz=0.7319 vs nonflat 0.4091   (report: 0.732 / 0.409)
RESULT thread_factor=1.000  load1=21.87
```

Exact. Per-cell too: `winter_narrow/dhw` 2.5099 on a 123.40 SEK bill,
`winter_typical/dhw` restart 0.9541.

### My own number

`own_race.py --grid tz24`, the same 16 cells, end-to-end, both modes:

```
full     : mean_gap_obj 0.4099  LOO 0.2791  flat 0.6449  non-flat 0.3763
           mean_gap_bill 0.2611 LOO 0.1303  (6/16 cheaper, 4/16 DEARER)
           pg_above_pgtol 16/16   parity_failures 4
restart  : mean_gap_obj 0.2261  LOO 0.0966  flat 0.0005  non-flat 0.2583
   only     mean_gap_bill 0.1566 LOO 0.0568 = 0.09 % of the daily bill
           restart_improves 8/16  pg_above_pgtol 16/16
```

### Perturbation (run; moves)

`D0_PERTURB=restart` on the same subset: `mean_restart_gap_sek_tz` 0.2183 →
**0.0030**, `mean_gap_sek_tz` 0.4494 → **0.2494**, `winter_narrow/dhw` objective
137.230 → 135.067 (gap 2.51 → 0.53), `winter_typical/dhw` gap 1.22 → 0.20.
All match the report. The split it exposes is the point: the perturbation
removes 53 % of the **non-flat** gap (0.4091 → 0.1926) but only 12 % of the
**flat** gap (0.7319 → 0.6471).

### Attacks I ran

* **Null control, the one that matters here.** The *whole-race* two-zone gap
  **fails** it — flat 0.7319 > non-flat 0.4091 on the finder's harness, and
  flat 0.6449 > non-flat 0.3763 on mine. It is non-convexity, not price
  optimality. The finder does not claim otherwise: this is in its own
  non-findings table and D0-02 is scoped to the restart component. That
  component **passes** cleanly: restart gap at flat 0.0011 max on the finder's
  harness and **0.0011 max / 0.0005 mean** on mine, against 0.2583 non-flat —
  a 516× ratio, produced by two unrelated harnesses landing on the same 0.0011.
  This is the one place in the report where the null control does real work,
  and it holds.
* **LOO.** 80 cells in the report (0.025 SEK with the best dropped); my 16-cell
  subset gives restart-only LOO 0.0966 SEK of objective, 0.0568 SEK of bill.
* **Money.** 4 of 16 cells the challenger's *bill* is worse while its objective
  is better. The realised money at parity is 0.09–0.17 % of a 16–123 SEK day.
* **Severity.** Claimed low. LOO 0.057 SEK/day of bill, masked further by
  re-planning. Low is right; anything higher would not be earned.
* **The fix** — same restart rule; executed against `tests/optimality.py` above
  (exit 0, 11/11, the gate's own two plans bit-unchanged), same
  3.11-extra-solves-per-call correction.

### Vote: **verify (low)**

Deciding number: restart-only mean objective gap **0.2583 SEK non-flat against
0.0005 SEK at flat prices** (max 0.0011), reproduced independently by my
end-to-end rig and the finder's per-call rig, with `pg_above_pgtol` 16/16 — a
real, price-dependent stall whose money value is 0.057 SEK/day after
leave-one-out, which is a low.

---

## D0-03 — small buffer tank with a mixing valve

### Re-run of the finder's harness (exact)

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 1 --dhw 0 \
  --weather winter_cold --quiet --random 3 --tag smalltank \
  --cfg '{"mixing_valve_mode":"manual","buffer_tank_volume":35.0,"buffer_max_temperature":70.0}' \
  --state '{"buffer_tank_temperature":32.0}'

RESULT cells_with_gap_tz=5 of 8        (report: 5/8)
RESULT mean_gap_sek_tz=1.1333          (report: 1.1333)
RESULT max_gap_sek_tz=4.1884           (report: 4.1884)
RESULT mean_energy_gap_pct_bill_tz=4.396   (report: 4.396)
RESULT pg_above_pgtol_tz=8 of 8        (report: 8/8)
RESULT loo_mean_gap_pct_tz=0.804       (report: 0.804)
RESULT null_flat_mean_gap_sek_tz=0.1411    (report: 0.14)
RESULT thread_factor=1.000  load1=42.66
```

All eight per-cell figures match too (winter_typical 3.4708 / 3.90 % / pg 1.3e2,
winter_moderate 4.1884 / 4.00 %, shoulder 0.0000 at pg 4.6e3, winter_narrow
0.0000 at pg 1.1e4).

### My own number

`own_race.py --grid smalltank`, same 8 cells, end-to-end:

```
RESULT mean_gap_obj_sek=0.7087   LOO 0.4553   flat 0.1411   non-flat 0.7898
RESULT cells_obj_gap=6 of 8      pg_above_pgtol=8 of 8   parity_failures=2
RESULT mean_gap_bill_sek=0.9832  LOO -0.2465  (2/8 cheaper, 3/8 DEARER)
RESULT mean_gap_pct_bill=0.99 %  LOO -0.78 %
```

On the golden fixture's own cell (`valve_storage_small_tank`, winter_typical) I
reproduce the report's headline through a different path: production objective
**88.975**, production energy **71.843** (report: 88.975 and 71.84), production
comfort under **0.1119 K-steps**, challenger **0.0000**, challenger bill 62.252
(report's challenger energy 61.95). The floor breach is real and reproduces —
and note its direction: the challenger's *minimum* zone temperature is
**colder** (16.727 vs production's 16.888); production breaches because its dip
falls inside the 07–22 window where the floor is 17.0, the challenger's inside
the night window where it is 16.5. The report's "min room 16.72 vs 16.89" reads
the other way round on a fast pass.

### Perturbation (run; moves hard)

`buffer_tank_volume` 35 → 750 L (the golden `valve_storage` config), my harness:
`mean_gap_obj_sek` 0.7087 → **0.0964**; `winter_typical` objective gap 2.1828 →
**0.0000** and its comfort breach 0.1119 → **0.0000**; max |projected gradient|
falls from 6.0 to 0.112. And the residual after the perturbation is
price-independent (flat 0.0939 ≈ non-flat 0.0968) — i.e. what survives the fix
is basin noise, not a price effect. Not a constant; direction as stated.

### Attacks I ran

* **Feasibility parity.** 2 of 8 cells are challenger wins bought by breaching
  comfort (`winter_extreme` challenger under 0.1579 vs production 0.0000;
  `winter_narrow` 0.0148 vs 0.0000) and are excluded from my aggregates. The
  finder's `parity_ok` excludes them too — its winter_narrow cell reads 0.00.
* **The aggregate does not survive an end-to-end race.** The headline
  "4.4 % of the energy bill" is a per-call energy gap of the best-objective arm
  on a recorded call. Run end-to-end, so that the improved first solve feeds
  `_tighten_buffer_caps` and the re-solve as it would in production, the same
  8 cells give **0.99 % of bill, and −0.78 % once the most favourable cell is
  dropped** — i.e. on average the challenger's pipeline output is *dearer*.
  Two of eight cells carry the entire result.
* **Flat null control.** Passes: 0.1411 flat vs 0.7898 non-flat objective (5.6×),
  and my flat bill gap is −0.169 SEK.
* **LOO.** 8 cells; the finder's own LOO is 0.804 % of objective (from 1.203 %),
  mine is 0.4553 SEK of objective and **−0.2465 SEK of bill**.
* **Cross-stack.** On python 3.11.5 / numpy 2.4.6 / scipy 1.17.1 the class
  survives but the magnitudes do not: winter_typical production under
  **0.0229** (not 0.1119), objective gap 0.532 (not 2.183), bill gap 4.69 (not
  9.59); winter_extreme becomes a clean parity win of 10.59 SEK. flat is exactly
  0.0000. So the mechanism is real on both stacks; the quoted sizes are not
  portable.
* **The committed fixture does not breach.** Computed straight off
  `tests/golden/valve_storage_small_tank.json` (no harness at all), against
  `get_temp_bounds` (17.0 day / 16.5 night): **under = 0.0000 K-steps**,
  tmin 17.115, `predicted_cost` 73.073 against this box's 71.843. The plan CI
  recorded is feasible. The breach is a property of the basin this stack lands
  in, not of the shipped fixture — so "the plan the sensors publish" is
  stronger than the evidence supports.
* **Magnitude of the breach.** 0.1119 degree-*steps* over 96 quarter-hours is
  0.028 K·h below floor. Real, and negligible.
* **Reachability.** `buffer_tank_volume` 35 L is below
  `BUFFER_STORE_MIN_VOLUME = 100.0` (`const.py:863`) — a configurable but
  narrow corner (a 35 L buffer behind a manual mixing valve), which is exactly
  why it exists as a golden fixture.

### Vote: **weaken (low)**

Nothing here is refuted — every number the report states reproduces exactly,
and the perturbation moves. What is not earned is *medium*. The claim's cost
half ("3.5–4.2 SEK/day dearer") holds in 2 of 8 cells and reverses in
aggregate when the race is run through the pipeline that actually ships:
**end-to-end mean bill gap −0.2465 SEK/day after leave-one-out**, with the
comfort breach measuring 0.028 K·h, absent from the recorded golden fixture,
and five times smaller on a second numpy/scipy stack. A genuine kink in a
sub-100 L buffer corner, worth fixing, worth low.

---

## What I did not do

* The full 160-cell `race_grid.py --quiet` for D0-02 (the box was at `load1`
  21–91 all session); I ran the 16-cell subset the report cites per-cell and
  reproduced it exactly, and my own 16-cell end-to-end grid alongside it.
* `rolling_gap.py` and `dhw_coopt.py` were not re-run. D0-01's and D0-02's
  MPC-masking numbers are the finder's own, and both *reduce* the severity they
  argue for, so I did not spend shared CPU attacking evidence that already
  works against its own finding.
* No global outer bound (DE / coarse DP). Not needed: 16/16 and 8/8 cells have
  `|projected gradient| >> PGTOL` at production's answer, which settles
  non-stationarity without one.

## Harnesses and raw output

Mine, in my scratch dir (`/private/tmp/claude-501/audit-scratch/D0-1/`):
`own_race.py` (the end-to-end race, grids `tariff15`, `tariff15_pk16`, `tz24`,
`smalltank`, `bigtank`, `notariff_sz`, modes `observe|restart|full`),
`fix_gate.py` (the proposed fix against `tests/optimality.py`), `out/*.json`
per-cell records, and `finder_out/` — the five JSONs the finder's own
`race_grid.py` wrote while I re-ran it. Running `race_grid.py` from a
repository root creates an untracked `tools/audit/round2/D0/out/` in that
worktree; it is present and untracked in `v-D0-1` and contains no repository
change (an attempt to delete it was refused by the sandbox, so it is left in
place, copied and noted rather than removed).
