# D0 panel, verifier 2 of 2 — the construction

Stance: refute-first. Assigned line of attack: **is the challenger solving the
same problem?** Everything below was executed in this tree at baseline
`ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1`, from the tree root, with
`PYTHONPATH=tests/hastub` and all five BLAS thread variables exported `"1"`
before every run (`d0lib.py` also `setdefault`s them before its numpy import).
8-core Apple M1, python 3.11.5, numpy 2.4.6, scipy 1.17.1 — the finder's
platform exactly.

**Contention.** The box was shared throughout: `load1` 8.94–33.03 and 9–22
concurrent python processes across my runs; `thread_factor` 0.871–0.999 on
every run (never above the 1.05 bar). **No number in this report is a wall,
CPU or RSS number** — every figure is an objective value, a SEK cost computed
from a plan, an iteration count, a solver status or a call count, so none of
them is provisional under load. `tests/stress.py` was not run, no `tests/run.sh`
was run, the gate lock was neither taken nor stolen, and no production or test
file was modified (every hook is `unittest.mock`; my own files live only under
`tools/audit/round3/D0/verify-2/`).

My own instruments, with their own metric definitions:
`verify-2/construct_probe.py` (per-**call** gap, seven start-set variants and
the restart, measured in place inside the production call),
`verify-2/stop_reason.py` (every L-BFGS-B run in the grid, full termination
message, captured at `_scoped_minimize`), `verify-2/ftol_probe.py` (a
tolerance-only arm), `verify-2/analyse_probe.py` (re-aggregates the first,
measures nothing). Raw output of every run is beside them as `*.out`.

---

## 1. Reproduction — every finder number reproduces exactly

Four of the finder's harnesses, re-run with the command in their own headers.
Not "within tolerance": identical to the last printed digit.

| harness | finder's RESULT | mine | agreement |
|---|---|---|---|
| `seed_race.py` | `gap_max_pct=1.0430`, `cells_with_gap=15`, `gap_mean_pct=0.1438`, `null_flat_gap_mean_pct=0.1570` vs `null_structured=0.1419`, `comfort_regressions=0`, `step0_differs_where_gap=12/15` | `1.0430`, `15`, `0.1438`, `0.1570` vs `0.1419`, `0`, `12/15` | exact |
| `polish_race.py` | `gap_max_pct=1.1703`, `cells_with_gap=9`, `gap_mean_pct=0.0462`, `null_flat=0.0051` vs `structured=0.0521`, `loo_mean_drop_best=0.0100`, `comfort_regressions=0`, `2/9` | `1.1703`, `9`, `0.0462`, `0.0051` vs `0.0521`, `0.0100`, `0`, `2/9` | exact |
| `price_seed_race.py` | `gap_max_pct=1.1087`, `cells_with_gap=13`, `null_flat=0.3187` vs `structured=0.1616`, `loo_structured_mean_drop_best=0.1265`, `9/13` | `1.1087`, `13`, `0.3187` vs `0.1616`, `0.1265`, `9/13` | exact |
| `budget_slack.py` | `solver_calls=39`, `calls_hitting_maxiter=0`, `max_nit=47`, `max_nit_over_maxiter=0.2350`, `candidates_discarded_max=0`, `calls_on_batched_jac=39`, `status_histogram={0: 39}` | identical | exact |

`load1` at the end of those runs: 21.21, 17.43, 14.56, 18.83; `thread_factor`
0.871, 0.998, 0.998, 0.993.

**Neither finding fails reproduction, and neither number is BLAS noise**: my own
`identity` control (production's own candidate list, re-run through the same
superset plumbing with the cap lifted) reads `identity_gap_max_pct=0.0000`,
`min=0.0000`, `mean=0.0000` over all 39 solver calls. These solves are
bit-deterministic on this box.

## 2. Perturbations, including the two nobody had run

| perturbation | stated direction | executed result |
|---|---|---|
| `D0_NO_EXTRA_SEEDS=1 … seed_race.py` | `to_zero` | **32 of 32 cells exactly `+0.0000%`**, `gap_max_pct=0.0000`, `cells_with_gap=0` ✔ |
| `D0_NO_POLISH=1 … polish_race.py` (never executed by anyone) | `to_zero` | **32 of 32 cells exactly `+0.0000%`**, `gap_max_pct=0.0000` ✔ |
| `D0_FRACTIONS="1.0,0.35" … price_seed_race.py` | `to_zero` ("the challenger then adds nothing production does not have") | **fails: `gap_max_pct=0.8145`, `cells_with_gap=5` of 32** ✘ (§9) |
| `V2_MAXITER_CUT=3 … verify-2/stop_reason.py` (mine) | maxiter stops appear | `solves_hitting_maxiter=130` of 132, `max_nit_over_maxiter=1.0000`, `STOP: TOTAL NO. of ITERATIONS REACHED LIMIT=130` ✔ |
| `V2_FTOL=1e-6 … verify-2/ftol_probe.py` (mine) | `to_zero` | 32 of 32 cells exactly `+0.0000%` ✔ |

Both findings' own perturbations behave as declared. Note what the two
`to_zero` controls actually prove: with the extra seeds removed (or the restart
dropped) the challenger's seed list *is* production's list, and the
`_MULTI_START_SOLVES` lift cannot bind (§4), so the challenger becomes
production byte-for-byte. They are **identity controls** — they establish that
the harness plumbing (the `min`-over-results selection, the lift, the extra
objective evaluations) introduces no drift of its own. That is worth having,
and it is not the same thing as discriminating "these starts" from "more
starts": nothing in the finder's evidence set does that. §3 does.

## 3. The strict-superset construction: real, but the attribution to *these*
seeds is not

**The construction is sound.** Read against `optimizer.py:365-485`,
`_multi_start_minimize` scores every candidate, refines the first
`_MULTI_START_SOLVES` of them and returns the lowest `objective(res.x, *args)`
found. `d0lib.stronger()` calls that same function, on the same closure,
bounds, `args`, `maxiter`, `batch_objective` and `fd_eps`, with production's
candidate list plus five points, and lifts the cap so all of them are refined.
Per solver call the returned value therefore cannot exceed production's. I
measured the per-call claim directly (`construct_probe.py`, metric: per-call
gap, not the finder's end-to-end one): `const5_gap_min_pct=0.0000` over 39
calls, and `identity` flat zero.

Two caveats on "cannot be negative by construction":

- It is a **per-call** guarantee, not an end-to-end one. For the 16 DHW cells
  the pipeline runs a second stage (`_co_optimize`, `optimizer.py:1872`) whose
  re-planned hot-water schedule is a function of the space profile and is
  adopted only if it beats *that arm's own* score — so an arm that wins stage 1
  can lose stage 2. Empirically it never did here: `seed_race` min gap
  `0.0000`, **0 negative cells of 32** (same for the ladder arm and for
  `polish_race`). The guarantee as worded is stronger than what holds; the
  measurement is unaffected.
- The gap is a **one-sided bound on non-convexity**, not a recoverable saving —
  which is where the attribution breaks.

**The seeds the finder names are not what earns the number.** Same rig, same
calls, only the extra start list changed (mean over all 39 calls, per-call
metric):

| extra starts added | gap max | gap mean | calls with gap (of 39) | mean ÷ const5 |
|---|---|---|---|---|
| `const5` — the finder's `lo+f·(hi−lo)`, f ∈ {0,¼,½,¾,1} | 1.4704 | 0.1966 | 19 | 1.000 |
| `rand5` — 5 **uniform-random** points in the same box | 1.3666 | 0.1876 | 17 | **0.954** |
| `jitter5` — 5 copies of **production's own starts**, jittered ±5 % of range | 0.9151 | 0.1221 | 15 | **0.621** |
| `zero1` — the all-minimum-power corner alone | 1.0430 | 0.0964 | 9 | 0.490 |
| `mid1` — the mid-bounds constant alone | 1.1580 | 0.0823 | 6 | 0.418 |
| `max1` — the all-maximum corner alone | 0.9493 | 0.0771 | 8 | 0.392 |

Five arbitrary random points recover 95 % of what the named family recovers,
and **beat it in 7 of 39 calls**; a ±5 % jitter of production's own four starts
recovers 62 % and beats the named family in 6 calls. The finder's second seed
family agrees per-cell only in aggregate: `winter_extreme/two_zone` gaps
`0.1478 %` under the constant family and `0.0000 %` under the ladder;
`summer_typical/two_zone+dhw` `0.0363 %` and `0.0000 %`. So "two different
families, one mechanism" is right about the *mechanism* (a basin-rich
objective) and wrong as evidence that a *particular* seed family is missing:
any sufficiently diverse start set moves the number, by a comparable amount, in
cells that do not coincide.

What does support "a reasonable implementation should have had one": production
already ships a constant-fraction seed on one path and not the other —
`_solve_space` seeds `headroom * 0.5` (`optimizer.py:2895`), exactly the
finder's `mid1`, while `_optimize_space_only` (`optimizer.py:3415-3425`) seeds
no constant at all. The report's "seeds four of the same shape" glosses over
that asymmetry, which is the strongest argument available *for* the finding and
it is not made.

## 4. The `_MULTI_START_SOLVES` lift contributes nothing — confirmed, and it
cannot

`budget_slack.py` reproduces `candidates_discarded_max=0` and
`multi_start_solves=4`. Independently: my `stop_reason.py` counts **135**
L-BFGS-B runs over the 32-cell grid = 32 calls × 4 starts + 7 co-optimisation
re-solves × 1 start (the warm-start path passes a single candidate). No call in
the grid ever passes more than 4 candidates, so the cap is never reached and
lifting it is a no-op on this grid. The finder's claim ("that also proves the
lift on its own contributes nothing") is true here, but it is true by
arithmetic, not by the perturbation it is attached to.

## 5. The `jac` path — captured, not re-derived, and identical in every arm

`tools/audit/README.md` warns that a race must use the same `jac` path
production would, *captured*. The finder's `calls_on_batched_jac=39 of 39` is
**re-derived**: `d0lib.Capture` recomputes `_bounds_supported_by_batch(bounds)`
outside the solve rather than observing what the solve was handed. Same
predicate, so the same answer, but it is not a capture.

I captured it at `_scoped_minimize`, which is the function that actually
receives `jac`:

- production: `solves_with_supplied_jac=135` of **135** (`stop_reason.py`);
- `prod_solves_on_batched_jac=1.0000`, and **1.0000 in every challenger arm**
  (`const5` 330/330, `rand5` 330/330, `jitter5` 330/330, `zero1`/`mid1`/`max1`
  174/174 each, the restart arm 73/73) — `construct_probe.py`;
- the production gate agrees on all 39 calls (`gate_says_batched=39/39`).

No arm anywhere in this panel ran on scipy's scalar finite differences. This
attack is closed: the challenger is on production's gradient path.

## 6. The budget is not the constraint — confirmed and widened

The finder's figures describe only the *winning* start of each call (39 of the
135 L-BFGS-B runs). Measured over all 135 (`stop_reason.py`):
`solves_hitting_maxiter=0`, `max_nit=49` (the finder's winner-only max is 47),
`mean_nit=14.66`, `max_nit_over_maxiter=0.2450` against `maxiter` 200/300. With
`V2_MAXITER_CUT=3` the same counter reports 130 of 132 solves at the limit and
`max_nit_over_maxiter=1.0000`, so it is reading the real solver. **"The solver
ran out of budget" is refuted for every solve in the grid, not just the winners.**

## 7. D0-02's mechanism: real descent in two cells, tolerance noise in the rest

The claim is about the optimizer's stopping rule. Three measurements, mine:

1. **Why the solver stops.** `budget_slack.py` reports
   `termination_reasons={'CONVERGENCE': 39}` — but it keys on
   `message.split(":")[0]`, and for every status-0 stop that prefix is the
   constant `CONVERGENCE`. The half of the message that names the rule is
   discarded, so the finder's instrument cannot see its own mechanism. Full
   messages over all 135 solves: **98 `CONVERGENCE: RELATIVE REDUCTION OF F <=
   FACTR*EPSMCH`** (`rel_reduction_share=0.7259`) and 37 `CONVERGENCE: NORM OF
   PROJECTED GRADIENT <= PGTOL`. The relative-reduction stop is the majority
   rule, as claimed.
2. **The returned points are not stationary.** Projected-gradient infinity norm
   at production's own returned `x`, computed with production's batched
   gradient: `max=2.022e-01`, `median=2.545e-02` kW, above scipy's `pgtol`
   (1e-5) in **28 of 39** calls — typically ~2,500× above it. In D0-02's
   carrying cell (`summer_negative/single`) production stopped after `nit=9`
   with `pg=2.54e-02`.
3. **Is the second descent noise?** No, in two cells; yes, in the rest. The
   restart's relative reduction `(f₀−f₁)/max(|f₀|,|f₁|,1)` — scipy's own
   stopping quantity — is `1.170e-02` at its maximum, i.e. **11,703 × `ftol`
   (1e-6)**, far above any tolerance-level artefact, and the chain converges:
   `summer_negative/single` restarts for 16 iterations, drops 1.538e-01
   absolute, and a second restart drops exactly 0.000e+00.
   `winter_moderate/two_zone`: 15 then 4 iterations, drops 2.721e-01 then
   1.010e-02, then zero. But the **median** restart gain over the 39 calls is
   `1.085e-08` relative — a hundred times *below* `ftol` — and in
   `shoulder/two_zone` the chain is not even monotone in step size (drops
   1.481e-03, 1.690e-06, 5.111e-03), which is what floating-point crawling
   looks like rather than descent.

So the mechanism is confirmed, and so is the finder's own reading that the
aggregate is carried by one cell. Its `cells_with_gap=9` is counted at a
threshold of 1e-4 % = 1e-6 relative — numerically *equal to the solver's own
`ftol`*. Of those 9 cells, 7 sit at or below 0.0025 % and four are within ~3×
of the threshold; only 2 cells exceed 0.05 %. The honest count is 2 of 32.

## 8. One number recovers more than either challenger — and it is not a seed

The D0 brief lists "tighter `ftol`" among the challengers; no harness in this
panel ran one, and `arms_decomposition.py`'s budget arm moves `maxiter`, which
135 of 135 solves never reach. `verify-2/ftol_probe.py` changes exactly one
thing — `options["ftol"]` from 1e-6 to 1e-12 — keeping production's own four
starts, no restart, no new seed, same bounds, args, `maxiter`, `eps` and jac
path:

```
RESULT gap_max_pct=1.2048   RESULT cells_with_gap=21   RESULT gap_mean_pct=0.2283
RESULT comfort_regressions=0   RESULT tightened_mean_nit=30.46 (vs 14.66)
RESULT null_flat_gap_mean_pct=0.3635  RESULT gap_mean_structured_pct=0.2090
```

Larger than D0-01's arm (1.0430 / 15 / 0.1438) and larger than D0-02's
(1.1703 / 9 / 0.0462), at about twice the iterations and with comfort no worse.
Per cell, the tolerance-only arm matches or beats **the seed superset in 9 of
its 15 gap cells** and **the restart in 8 of its 9**. Its flat-price arm is
again larger than its structured arm, exactly as in D0-01.

Two consequences for the panel. First, D0-01 and D0-02 are not independent
findings: the same premature stop is reachable from a different direction, and
the cheaper description of most of what `seed_race` measures is "the solve stops
on a loose relative-reduction test", not "the candidate set under-covers the
basins". Second, whatever fix is eventually priced, the seed list is not
obviously the lever.

## 9. Instrument defects found (none of them invalidates a headline number)

1. **`price_seed_race.py`'s stated perturbation fails.** Its header:
   `D0_FRACTIONS="1.0,0.35"` "restricts the ladder to the two rungs production
   already seeds. Every gap must collapse to 0.0000%." Executed:
   `gap_max_pct=0.8145`, `cells_with_gap=5` of 32. The cause is in
   `d0lib.stronger_price_seeds`: it rebuilds the ladder from `max(sum(c)·dt)`
   over the candidates and from the **raw** `prices` array passed to
   `optimize()`, not from production's own `baseline_energy` and its internal
   price horizon — so its "f = 1.0 and f = 0.35" rungs are not production's two
   rungs. The superset property survives (extra points are extra), so the
   ladder arm's gap is still a valid one-sided bound; what fails is the control.
   It matters concretely: `shoulder/single` reads `0.8145 %` under the full
   ladder and `0.8145 %` under the two "production" rungs — the row the report
   quotes in its money table is produced entirely by seeds the perturbation
   claims production already has.
2. **`seed_race.py`'s header EXPECTED block contradicts the report it supports.**
   Header: `gap_max_pct = 0.5618 ± 0.02`, `cells_with_gap = 8 ± 1`,
   `gap_mean_two_zone_pct = 0.2107 ± 0.02`, `gap_mean_single_zone_pct = 0.0000
   ± 0.0005`. Measured by me and printed by the report body: `1.0430`, `15`,
   `0.1465`, `0.1411`. Four of five are outside the stated tolerance, the last
   by 282×. A judge re-running this harness against its own header records a
   mismatch on a finding that in fact reproduces perfectly.
3. **`budget_slack.py`'s `termination_reasons` is a constant** (§7.1) — the one
   line of evidence that would have supported D0-02's mechanism claim cannot
   distinguish the two convergence rules.
4. `price_seed_race.py`'s docstring calls itself "D0-02 harness"; it is D0-01's
   second family.
5. Comfort parity is measured only at the 17.0/23.0 °C band
   (`d0lib.comfort_of`), while the objective also prices deviation *inside* the
   band (`_COMFORT_PULL_TWO_ZONE`). `comfort_regressions=0` therefore means "no
   worse at the floor or ceiling", not "no less comfortable". No challenger in
   this panel breached the band, so no verdict turns on it.
6. My own first `stop_reason.py` run printed `rel_reduction_stops=0` because my
   substring test used the underscored form of a message that contains spaces;
   the histogram beside it carried the real counts. Fixed and re-run; the first
   run is kept at `verify-2/stop_reason_firstrun.out`.

## 10. Consequence, which is where my severity disagreement lives

The report prices the finding per cell and discloses that the bill rises in 5
of the 15 gap cells. It never nets them. Summed over exactly the cells it
claims (`seed_race`, the 15 with a gap, whose production bills total
871.71 SEK/day):

```
net bill change = +0.247 SEK/day   (+0.028 % of those days' bills)
falls in 10 cells, rises in 5, worst single row -3.487 SEK/day on an 81.36 SEK day
```

The ladder arm on the same grid nets `+7.387 SEK/day`, and reverses the sign of
the very cell the seed arm loses most on (`winter_moderate/two_zone`:
−3.487 SEK/day under the constant seeds, +4.413 SEK/day under the ladder — the
report quotes both rows, to its credit). The money attached to D0-01 is a
property of the challenger's start list, not of the defect.

And both findings' headline percentages come from the cheapest day in the grid:
`summer_negative/single`, an 11.34 SEK day (0.797 SEK under D0-01, 0.679 SEK
under D0-02). The D0 brief's own trap list says "a 1 % gap on a 60 SEK day is a
finding, a 1 % gap on a 2 SEK summer day is not"; 11.34 SEK is nearer the second
than the first. D0-01 does have real gaps on substantial days
(`winter_typical/two_zone` 0.4202 % / +0.436 SEK on 58.30;
`shoulder/single` 0.7571 % / +0.537 SEK on 40.09; `flat/two_zone` 0.5618 % /
+2.354 SEK on 90.75), which is why I do not refute it. D0-02 does not: after
its one carrying cell the next is 0.200 SEK/day on an 81.36 SEK day and the
remaining seven move the bill by under 0.02 SEK/day (two of them the wrong way).

## 11. Votes

**D0-01 — `weaken`, severity `low`** (finder: `medium`).
Metric I measured under: *per-call objective gap = (f_production −
f_variant)/|f_production| × 100, for one `_multi_start_minimize` call, the
variant differing only in its starting-point list* — `const5_gap_max_pct=1.4704`,
`mean=0.1966`, 19 of 39 calls, `min=0.0000`, against `identity` flat 0.0000.
The finder's end-to-end number reproduces exactly (1.0430 / 15 / 0.1438), its
perturbation goes to zero in 32 of 32 cells, comfort parity holds, the null
control is genuinely inverted (flat 0.1570 > structured 0.1419) and the
renaming to basin selection is correct. Nothing here is refuted. What does not
survive is the severity and the attribution: 5 uniform-random starts recover
95 % of the same gap and beat the named family in 7 of 39 calls; a ±5 % jitter
of production's own starts recovers 62 %; a tolerance-only arm recovers more
than the seeds in 9 of the 15 gap cells; and the net bill effect over the whole
claimed cell set is +0.247 SEK/day on 871.71 SEK/day of bills (+0.028 %), with
five cells moving the wrong way. The finding is a true, reproducible lower
bound on the objective's non-convexity, not an identified missing seed family
and not a quantified saving.

**D0-02 — `verify`, severity `low`** (finder: `low`).
Metric I measured under: *per-call objective gap from restarting L-BFGS-B at
production's own returned point, same closure, bounds, args, maxiter, ftol, eps
and jac path* — `polish_gap_max_pct=1.1703`, `mean=0.0424`, 10 of 39 calls, and
end-to-end 1.1703 / 9 / 0.0462, identical to the finder. The perturbation
nobody had run (`D0_NO_POLISH=1`) goes to exactly 0.0000 % in 32 of 32 cells.
The mechanism claim is confirmed by an instrument the finder did not have: 98
of 135 L-BFGS-B runs stop on `RELATIVE REDUCTION OF F`, and the returned points
carry a projected gradient of median 2.545e-02 kW, above `pgtol` in 28 of 39
calls. It is not tolerance noise where it matters — the carrying cell's restart
reduces f by 1.170e-02 relative, 11,703 × `ftol`, over 16 iterations, and the
chain then converges to zero — but it *is* tolerance noise almost everywhere
else: the median restart gain is 1.085e-08 relative, 100× below `ftol`, and the
9-cell count is taken at a threshold numerically equal to `ftol`, so the
material count is 2 of 32 and the max sits on the grid's cheapest day.
`low` is the right severity and the finder's own "read the max, not the mean"
is the right reading.

## Files

- report: `tools/audit/round3/D0/verify-2.md` (this file)
- my harnesses: `tools/audit/round3/D0/verify-2/construct_probe.py`,
  `stop_reason.py`, `ftol_probe.py`, `analyse_probe.py`
- raw output of every run above: `tools/audit/round3/D0/verify-2/*.out`
  (`seed_race.out`, `seed_race_NOSEEDS.out`, `polish_race.out`,
  `polish_race_NOPOLISH.out`, `price_seed_race.out`,
  `price_seed_race_TWORUNGS.out`, `budget_slack.out`, `construct_probe.out`,
  `stop_reason.out`, `stop_reason_CUT3.out`, `stop_reason_firstrun.out`,
  `ftol_probe.out`, `ftol_probe_SAME.out`)
