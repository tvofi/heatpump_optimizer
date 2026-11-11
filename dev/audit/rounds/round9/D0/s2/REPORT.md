# Round 9, D0 (price optimality), finder seat D0-s2

Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Box B2, a 4-CPU Linux container shared with other seats,
running `/home/claude/venv314/bin/python` (3.14) on OpenBLAS with the BLAS threads pinned to 1.
Cells (from `check_scopes.py --seat D0-s2`): steps D0.M1–M4 on the price axis `summer_typical`, `summer_negative`,
`shoulder` and `flat`, over `optimizer.py`, `thermal_model.py` and `coordinator.py`.

Every number below is a count or a ratio on the production objective, so none of them is a timing. load1 during
the runs was 3.1–6.2, from other seats sharing the box. thread_factor was 1.000 on every run.

## Method

- **M1, capture.** `race.py` wraps `optimizer:_multi_start_minimize` with `mock.patch.object`. For every seam call
  it records the objective closure, the candidates, the bounds, `args` (the fixed DHW plan on the with-DHW path),
  `maxiter`, `batch_objective`, `fd_eps` and the returned x. It also wraps `_scoped_minimize` to count L-BFGS-B
  runs and `nit` against `maxiter`.
- **M2, challengers.** Each challenger races on the exact recorded objective, bounds and args, and uses the same
  batched jac through the production seam. The arms are:
  - `polish`: production's own L-BFGS-B from the shipped point, at ftol=1e-12, gtol=1e-10 and maxiter=5000.
  - `ladder`: the recorded candidates plus bang-bang seeds `_price_ranked_start(prices, fr·Emax)`, re-raced
    through `_multi_start_minimize`. Emax is the bounds' maximum energy. The fractions are fr ∈ {0, .01, .02,
    .05, .1, .15, .2, .3, .4, .5, .6, .8, 1}.
  - `ladder_polish`: the ladder result, re-polished.
  - `anchor.py`: the #1294-style anchors at 1.25, 1.5 and 2.0 times production's own 1.0× anchor energy.
  - `seedwin.py`: the per-seed breakdown.

  Every plan is scored with the production objective closure, never with energy price alone.
- **M3, feasibility parity.** For each arm, `violation()` counts degree-steps below `temp_min_bounds`. It reads the
  closure's own `_space_traj` (room, or upper and lower zones when the house is two-zone). DHW feasibility is
  identical by construction, because the DHW plan is the recorded `args`.
- **M4, grid.** The 4 price profiles × 5 weather profiles × single/two-zone × DHW on/off × horizon 24 h make 80
  cells (every seam call). The same grid at 6 h makes 64 cells (weather without `summer_warm`). At 48 h the grid is
  32 cells: the first call only, with weather `winter_cold` and `shoulder`. The `flat` price is on this seat's axis
  and serves as the null control for every aggregate.

## Findings

### D0-s2-01: the ftol=1e-6 stop leaves L-BFGS-B short of its own fixed point (class P4; low)

- **Where it shows.** On `two|dhw|summer_typical|winter_cold` at a 48 h horizon, the shipped plan's objective is
  55.3274. Production's own L-BFGS-B, restarted from that plan at ftol=1e-12, reaches 54.9674: a gap of 0.6507 %,
  worth 0.36 objective units. Energy cost drops from 45.04 to 44.43 SEK over 2 days, comfort violation stays at 0
  in both arms, and step 0 moves from 0.99 to 0.93 kW.
- **Why it stops early.** Every main run stops with `RELATIVE REDUCTION OF F <= FACTR*EPSMCH` after 8–36
  iterations on 192 variables. The in-loop restart (`_lbfgsb_restart`) then stops after 1 iteration for the same
  reason, so the polish that exists to repair this repairs nothing here.
- **Perturbation.** Setting production's ftol to 1e-12 (`--perturb ftol_tight`) moves the shipped objective to
  54.7889 and the residual gap to 0.0000 %. The direction is down (`polish48_pert.log`).
- **Extent.** The same residue appears at 24 h on:
  - `one|nodhw|shoulder|winter_cold`: 0.8523 %, 0.42 SEK. This cell is already claimed in `tests/optimality.py`
    `_CERT_CLAIMS`.
  - `one|nodhw|shoulder|summer_cool`: 0.27 %. This cell is not claimed.

  With the perturbation, both go to 0.0000 % (`polish24_pert.log`).
- **Null control.** At `flat` prices and 48 h, the gap is at most 0.0231 % (0.048 SEK). At 24 h `flat`, it is at
  most 0.0070 %.
- **Leave-one-out** (48 h, 8 cells per price): the `summer_typical` maximum is 0.6507 % and the minimum 0. With the
  single most favourable cell dropped, the mean is 0.0005 %. The residue is concentrated in a few cells rather than
  spread across the grid.
- **Severity: low.** The cost is bounded, at about 0.3 SEK a day, and shows in 3 of about 110 cells on this axis.
- **Relation to a refused fix.** A tighter stop rule was refused on money (#1293, per the comment in
  `tests/optimality.py`). That refusal was measured on a closed-loop shoulder backtest. This finding supplies
  open-loop cells outside the one claimed cell for the owner to weigh against it.

### D0-s2-02: the seed set misses lower basins on shoulder prices, above the flat null (class P4; low)

- **Metric.** The call-0 `ladder` gap on the 24 h grid, with the 4 `summer_warm` cells excluded from each profile
  (16 cells per profile):

  | price profile | max | mean | mean, most favourable cell dropped | cells > 0.1 % | largest absolute gap |
  |---|---|---|---|---|---|
  | `shoulder` | 1.2012 % | 0.3909 % | 0.3369 % | 8 of 16 | 0.435 |
  | `flat` (null control) | 0.3247 % | 0.0918 % | 0.0763 % | 6 of 16 | 0.185 |

- **Unclaimed cells**, where the shoulder price gap exceeds the matched flat cell:

  | cell | shoulder price | matched flat |
  |---|---|---|
  | `one\|nodhw\|shoulder\|shoulder` | 1.20 % (0.069) | 0.325 % |
  | `one\|dhw\|shoulder\|shoulder` | 1.17 % (0.107) | 0 % |
  | `one\|nodhw\|shoulder\|summer_cool` | 1.14 % | 0.027 % |
  | `one\|dhw\|shoulder\|summer_cool` | 1.06 % (0.065) | 0.053 % |
  | `two\|nodhw\|shoulder\|winter_cold` | 0.30 % (0.179) | 0.070 % |

  In the last cell, step 0 also moves from 1.52 to 0.89 kW.
- **Feasibility parity.** Comfort violation is 0 in both arms in every cell.
- **What finds the lower basin.** `seedwin.py` shows the landscape is rugged. On `one|nodhw|shoulder|shoulder`,
  single seeds land between −3.5 % and +1.2 % of the shipped objective, and the winner is fr=0.8·Emax, ending at
  8.5 kWh against the shipped 7.25. The #1294-style anchors at 1.25–2.0× the baseline energy (`anchor.py`) do not
  reach it: the gap stays at 0 on that cell, and the shoulder maximum through that route is 1.08 %. So the missing
  piece is start diversity, not one energy anchor.
- **Perturbation.** Handing production's seam the same Emax-fraction seeds (`--perturb add_emax_ladder`) takes the
  shoulder call-0 gap from a 0.3909 % mean and 1.2012 % max down to a 0.0503 % mean. Fifteen of 16 cells reach
  0.0000 %. The remaining 0.80 % cell's residue comes from the polish arm, which is D0-s2-01's mechanism.
- **Price context.** On the `summer_*` prices, relative gaps reach 13.87 % on `one|nodhw|summer_negative|shoulder`.
  The day there is 0.31 objective units, so the absolute gap is at most 0.062. Per the D0 brief, those are not
  material.
- **Severity: low.** The cost is at most about 0.1 SEK a day on shoulder days of 3–9 SEK, or 0.18 SEK on the 59 SEK
  two-zone winter-weather cell.

## Non-findings (held)

- **Budget does not bind.** No `_scoped_minimize` run reached `maxiter` on any grid: 0 of 698 runs at 24 h and 0 of
  544 at 6 h (`maxiter_hits` in `grid24.jsonl` and `grid6.jsonl`).
- **Every candidate is refined.** Runs equal 2 × candidates (main plus polish): 8 per single-zone space-only solve,
  10 for two-zone, and 8 for the with-DHW first call. None is discarded.
- **The co-optimize replan never flips.** The replan (`_co_optimize`, a single warm start) was checked on 9 cells
  with a second seam call. Improving its solve to the best challenger never flips the adoption decision
  (`flips 0`).
- **The 6 h horizon has no gap.** Across 64 cells the maximum gap is 0.0005 %.
- **Feasibility parity holds** in every raced cell: the challenger's violation is never above production's
  (`viol_worse=0` in `anchor.log`, and 0.0000 → 0.0000 throughout the grid logs).
- **The deep 0.20× anchor is not a factor on this axis.** It is missing from the with-DHW seam (`_solve_space`), but
  giving it back (`race.py --perturb deep_anchor_dhw`, `evidence/deep_anchor_dhw.log`) changes little.
  `two|dhw|summer_typical|winter_cold` moves only from 28.1152 to 28.1039, and its gap goes from 0.2199 % to
  0.1797 %, still open. `two|dhw|shoulder|winter_cold` is unchanged at 65.3202.

## Harnesses

- `race.py`: M1–M4 capture and race; the perturbations are `add_emax_ladder`, `deep_anchor_dhw` and `maxiter_hi`.
- `polish.py`: stop-rule residue; the perturbation is `ftol_tight`.
- `anchor.py`: #1294-style baseline-multiple anchors; the perturbation is `add_anchors`.
- `seedwin.py`: per-seed diagnostic.
- `evidence/`: the logs and jsonl files of every run quoted here.

## Unfinished

- **D0.M4.** The grid did not cover valve storage, the wood tank, the coordinator captures
  (`golden.py:_capture_coordinator`), or the 48 h cells with `winter_mild` and `summer_cool` weather.
- **D0.M2.** No global outer bound was run (differential evolution or a coarsened dynamic program). The ladder and
  polish arms are the best challengers measured.

## Exposure

I listed the directory names under `tools/audit/round8/` (`BASELINE.md` and the dimension folders) but opened no
file there. I read `tests/optimality.py`, which names earlier round ids and the claimed certificate cells, as test
code, and the comments in `optimizer.py` that cite earlier D0 ids.

## Leads (outside this seat's cells)

- **To D0-s3 (M6).** Both findings change step 0 in some cells: `two|nodhw|shoulder|winter_cold` from 1.52 to
  0.89 kW, and the 48 h `two|dhw|summer_typical|winter_cold` from 0.99 to 0.93 kW. A receding-horizon replay is
  needed to show whether either gap is realised.
- **To D0-s3 (M7).** At a 6 h horizon, 36 of 64 cells plan 0 kWh of space heating (`grid6.log`). The terminal
  credit alone decides that plan.
- **To an unknown seat (D2).** Under `summer_warm` weather the objective is a plan-independent constant: 6435
  (single-zone) or 10598 (two-zone), from the overshoot penalty on warmth no heater can remove. It dominates
  `objective_value`.
