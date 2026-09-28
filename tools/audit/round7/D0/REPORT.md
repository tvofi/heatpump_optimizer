# D0 round 7 — price optimality

Finder: D0 auditor, round 7. Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648`
(the round-6 fix wave fully merged). Machine: Apple M1 (arm64), 8 GB,
numpy 2.4.6 / scipy 1.17.1, OpenBLAS. Box shared with other finders during the
fan-out; load1 ~6-7 at measurement time. All numbers below are objective-value
ratios and counts, which are contention-immune; no wall/CPU/RSS number is
relied on.

## Method

Per `tools/audit/briefs/D0.md`: capture the space-only solve seam, race
challengers against the exact recorded objective, and look for plans a better
search finds strictly cheaper on the **same objective, bounds and inputs**
with comfort no worse. The seam is `heatpump_optimizer.optimizer:_multi_start_minimize`,
captured with `mock.patch.object` (the idiom in `tests/optimality.py`) to record
every call's objective closure, candidates, bounds, args and `maxiter`, and to
re-race the captured objective with extra bang-bang seeds at energy fractions of
the baseline energy. `_compute_baseline_power` is also captured to read the
baseline energy the seeds are scaled against. Feasibility parity: comfort floor
checked with `ThermalModel.simulate_trajectory` (the production symbol), and
every seed is raced through the same seam so bounds/pins are identical.

The challenger is the seed ladder the D0 brief names: `_price_ranked_start` at
energy fractions `{0.1, 0.2, 0.35, 0.5, 0.7, 1.0, 1.25, 1.5, 2.0, 2.5}` of the
baseline energy, each appended to the captured candidate list and refined by the
same `_multi_start_minimize`. The gap is keyed on the **production objective
value** `float(objective(plan))` delivered by the captured closure — never on an
energy attribute — so a fix that widens the seed set moves the shipped objective
and closes the gap.

A broad sweep (all 8 price profiles × 5 weather profiles × single/two-zone,
space-only, 24 h) was run to locate gaps; the finding below is the one cell
where the gap sits **below** production's lowest energy seed, which is a
direction the existing recorded claims (all "store *more* than baseline",
fractions > 1.0, single-zone) do not cover.

## Findings

### D0-01 — the space-only low-energy seed overshoots the optimum on the default two-zone winter cell

- **Severity**: medium (bounded cost, no user workaround).
- **Instrumented symbol**: `heatpump_optimizer.optimizer:_multi_start_minimize`.
- **Metric**: `gap = (f0 - f_best) / |f0|`, `f0` = production objective value of
  the shipped plan, `f_best` = minimum objective from re-racing the captured
  candidates plus the ladder seeds.
- **Executed numbers** (harness `tools/audit/round7/D0/underheat_seed.py`):

  | quantity | value |
  |---|---|
  | production objective (two-zone, `winter_typical`/`winter_cold`, dhw off) | 77.884228 |
  | best ladder objective | 77.543533 (winning fraction **0.20**) |
  | gap | **0.4374 %** |
  | energy cost production → ladder | 58.785 → 57.725 SEK (Δ **1.060 SEK/day**) |
  | comfort floor violation, both arms | 0.0 degree-steps |
  | perturbation (lower `_LOW_ENERGY_START_FRACTION` 0.35→0.2): shipped objective | 77.543533 → gap **0.0000 %** |
  | null control (flat prices, 0.20× seed): gap | **0.0000 %** |

- **What is happening**: `_optimize_space_only` builds four starting points, of
  which the two "bang-bang" seeds anchor energy at `1.0×` and
  `0.35×` (`_LOW_ENERGY_START_FRACTION`) of the thermostat baseline. On the
  default two-zone winter cell the optimum of the objective lies at ~`0.20×`
  baseline energy — under-heating the slab and buying the shortfall later in the
  day is cheaper because the price curve is steeper than the storage round-trip
  loss. The `0.35×` seed is not merely unhelpful: refined, it lands at 79.12, a
  *worse* basin than the shipped 77.88, and the smooth/baseline/1.0× seeds all
  refine into the ~77.88 basin. No seed covers `0.05–0.20`, so the `0.20×`
  basin is unreachable and production ships a plan 0.44 % above its own
  objective's fixed point from that seed. At flat prices the `0.20×` seed stops
  beating production (gap 0.0000 %), which is the null control confirming this
  is a **price** optimality gap, not a comfort or cycling artefact.

- **Why it is not covered by an existing claim**: the tree's recorded solve
  certificate (`tests/optimality.py`, `_CERT_CLAIMS`) claims three single-zone
  cells, all with the optimum *above* the baseline energy ("store more"), and
  its ladder `{0.7, 1.25, 1.5, 2.0, 2.5}` starts at 0.7 — it never tests a
  fraction below 0.35, and it is single-zone only. The under-heat direction on a
  two-zone cell is unclaimed and unmeasured.

- **Phenomenon property**: the space-only multi-start's structural seed set
  anchors energy to the two fractions `{0.35, 1.0}` of the baseline and does not
  bracket the optimum's energy on the default two-zone winter cell.
- **Seam rule** (enumerates the class): the seed construction sites are the
  `_price_ranked_start(...)` calls in `HeatPumpOptimizer._optimize_space_only`
  and `_solve_space`;
  `grep -n "_price_ranked_start\|_LOW_ENERGY_START_FRACTION" custom_components/heatpump_optimizer/optimizer.py`.
- **Stop-rule class**: bug.
- **Proposed fix scope**: add a bang-bang seed below `0.35×` baseline energy
  (e.g. `0.2×`) to the `starts` list in `_optimize_space_only`, or adapt
  `_LOW_ENERGY_START_FRACTION`; a one-line change whose plan-quality gain is
  this cell and whose solver-cost is one short extra L-BFGS-B run per solve.
- **Files**: `custom_components/heatpump_optimizer/optimizer.py`.

## Non-findings (checked and held)

1. **The DHW/space co-optimization converges in one pass.** Iterating
   `HeatPumpOptimizer._co_optimize` to 5 passes (re-threading the adopted score)
   changed the objective by 0.0000 % on 6 cells
   (single/two-zone × `winter_typical`/`winter_cold`, `shoulder`/`shoulder`,
   `summer_negative`/`summer_warm`, dhw on). The production objective and the
   5-pass objective were bit-equal: after one replan the `pinned` mask is empty.
2. **The low-energy seed gap does not appear on the DHW path.** Lowering
   `_LOW_ENERGY_START_FRACTION` 0.35→0.2 on dhw-enabled single/two-zone
   `winter_typical`/`winter_cold` moved the objective 0.0000 % (the DHW path's
   space solve is bounded by DHW headroom and seeded differently).
3. **Single-zone is insensitive to the ftol stop rule** (confirming the known
   #1293 mechanism is single-zone specific): the re-polish gap
   (`_scoped_minimize` from the returned point at ftol 1e-8) was 0.0000 % on
   every single-zone space-only cell of the 8×5 grid except
   `shoulder`/`winter_cold` (0.886 %, the recorded #1293 cell) and
   `summer_typical`/`summer_cool` (0.055 %).
4. **The "store more" missed-basin gap matches the recorded claims.** The
   largest ladder gaps on the grid are `summer_negative`/`shoulder` (single-zone
   9.96 %, two-zone 4.89 %) and `summer_negative`/`summer_cool` (single-zone
   1.36 %), all with the winning fraction above 1.0 — the same phenomenon the
   tree's `_CERT_CLAIMS` already records ("the optimum stores more than the
   baseline's energy"), so these are not new findings.

## Out of dimension (carried, not a D0 finding)

At **flat** prices on the two-zone `flat`/`winter_cold` cell the ladder still
finds a 0.209 % gap, but at fraction **1.25** (store *more*), not at the
under-heat 0.20. A gap that survives flat prices is not price optimality
(`D0.md` step 5); it is the terminal credit's 25th-percentile refill price
over-crediting stored heat. This belongs to D2 (objective correctness) and is
carried per `finding-propagation.md`, not filed here.

## Harnesses

- `tools/audit/round7/D0/underheat_seed.py` — the D0-01 number, its perturbation
  and its flat-price null control. One command:
  `PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tools/audit/round7/D0/underheat_seed.py`.

## Exposure

None. This dimension did not need to read `docs/` audit registers or GitHub.
