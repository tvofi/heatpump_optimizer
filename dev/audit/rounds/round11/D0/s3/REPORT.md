# Round 11, D0 (price optimality), seat D0-s3

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B3 (4 cores shared by three
seats, load1 5-13 throughout). Interpreter `$HOME/venv-ci/bin/python3`, `PYTHONPATH=tests/hastub`,
every harness thread-pinned (thread_factor 1.000 on every run). Every CPU number is
provisional; counts and objective values are contention-immune.

Cells (`check_scopes.py --seat D0-s3`): D0.M4, M5 and M6 on prices summer_typical,
summer_negative, shoulder and flat; D0.M7 and M8 on all eight prices; files
`coordinator.py`, `optimizer.py`, `thermal_model.py`.

The box restarted during the seat's run. This run resumed from the seat's own round-11
directory, which the checkpoint had restored. The resumable outputs (`race_out/`,
`decomp_out/`, `loop_out/`, `offstart_out/`) were carried forward and completed. No
earlier-round record was read.

## Method

- **M4 race** (`race.py`): the D0 grid lines on the seat's four prices (1200) plus the five
  `tests/golden.py` coordinator captures on each of those prices (20, `coord/<capture>/<price>`;
  built through `coordinator._solve_record` and `_warm_seeded`). Every `optimizer._multi_start_minimize`
  call is captured with `_commit_runs`. The challengers run in cost order: structured seeds
  (bang-bang at 0.5/1/1.5 of the shipped energy, the baseline energy, the lower and upper
  bounds, the previous plan), a looser budget where a run was budget-bound (0 cells were),
  hourly-block `differential_evolution` through the call's own batch objective, and a
  warm-started L-BFGS-B from the best challenger. Each is committed through production's
  `_commit_runs` and scored on its true objective, and must keep comfort parity on
  `ThermalModel.simulate_trajectory`. The two plant questions are answered per cell.
- **M4 off-start** (`offstart.py`): production's `_multi_start_minimize` from the lower bound
  alone, committed, on all 300 summer_negative cells and all 300 flat twins.
- **M5 null**: the flat arm of every M4 number.
- **M6 masking** (`loop.py`): the M6 universe is every race cell whose shipped call has a gap
  (`loop.py --list`, 555 cells). For each, step-0 differs is read from the race. Then one
  hourly re-plan is tested (`--mask`, 546 grid cells): production's plan is applied for 4
  steps, production re-plans warm-seeded, and the result is compared with the shifted
  challenger committed through the re-plan's own call. The 24 h closed loop (plant == model,
  and a plant with heat loss x1.2 and mass x0.85) runs on 24 cells, each scored with the
  plant's own full production objective (comfort pull, cycling and start terms, terminal
  credit, DHW). The 3-day loop runs on 2 cells.
- **M7** (`decomp_oracle.py`, all 2400 grid lines): `_co_optimize` is iterated to a fixed
  point (<= 5 passes), and `_terminal_cost` is zeroed (tail energy, tail floor breach).
  `terminal_claim.py` re-runs the docstring claim on 40 committed cells under three weight
  settings.
- **M8** (`decomp_oracle.py`, all 2400 grid lines): open-loop same-information oracle on a
  mis-learned plant (heat loss x1.2, mass x0.85). The oracle is production's solver on the
  plant with the comfort pull zeroed, scored on the plant.

## Findings

| id | step | severity | title |
|---|---|---|---|
| D0-s3-01 | M8 | medium | The finder export strips the evidence `bundles.json` names, so `enumerate.py d15-installs` refuses in every finder tree (before the strip: 1 line, rc 0; after: 0 lines, rc 2; with the keep set perturbed: 1 line) |
| D0-s3-02 | M4 | low | No all-off start. At negative prices, storage plants ship an open-loop plan their own objective scores 1.8-8.6 % worse than the plan from the off start (44/300 summer_negative cells, 22 above 1 %; flat null 0 above 1 %, max rel 0.27 %). M6: one re-plan leaves it unmasked on 18 cells, but the 24 h closed loop realises < 1 unit on 12/16, mean 1.59 units/day, -3.95 with the best cell dropped, money within 0.75 SEK/day |
| D0-s3-03 | M7 | low (hygiene) | `_terminal_cost`'s docstring says the plan breaches the comfort floor at the tail without it. On the grid: 0/2400 cells (1659 do dump tail energy). On the 40 committed cells: 0/40 at the default weight and at the learner's minimum. The breach appears only at comfort_weight x0.01 (13/40) |

Each finding's JSON is in `findings/`.

## Non-findings (checked, held)

- **M4 race, 1220/1220 cells**: 555 have a gap above 1e-4 objective units. Excluding
  summer_negative, the largest gap is 1.567 units (shoulder/shoulder/two-zone/no-dhw/wood/6h,
  rel 15.5 %, flat twin 0.02 %, closed loop -0.63, i.e. production's loop is better).
  Per price, mean gap / mean with the most favourable cell dropped: summer_typical
  0.0046/0.0040, shoulder 0.0186/0.0135, flat 0.0147/0.0118. These are SEK-scale amounts on
  2-17 SEK days; by the brief's bill-share rule they are not findings. The winning arm on
  the 555: warm 357, seeds 149, de_block 46, eps 3. No L-BFGS-B run was budget-bound
  (binding 0 of 1220), so the budget challenger never ran.
- **Coordinator captures**: 9/20 have a gap. The largest is
  coord/coord_all_features/summer_negative at 0.200 units (rel 2.5 %). The rest are
  <= 0.078 units.
- **flow-setpoint-behind-valve, 240 cells, all clamped (`levels_clamped`)**: the plan leaves
  the minimum level on 53/60 summer_negative, 46/60 summer_typical, 46/60 shoulder and 47/60
  flat cells. Total power (space + DHW) is sub-minimum on 0 of the 217 cells that record it.
- **manual-valve-buffer, 240 cells**: the plan differs from the no-buffer plan on 195
  (L1 > 0.01 kWh; median 6.2 kWh, max 98.5).
- **M5 flat null**: 154/305 flat cells have a gap above 1e-4. Only one is above 1 %
  (flat/summer_cool/two-zone/no-dhw/wood/24h, 0.877 units, a de_block win), and one re-plan
  masks all 152 grid ones. That one is a seed-basin effect on storage plants that survives a
  flat price, so it is not price optimality. It is recorded as a lead.
- **M6**: one hourly re-plan masks the race gap on 512/546 grid gap cells. The 34 unmasked
  include all 18 above 1 %, and all 18 are D0-s3-02's off-start cells. 24 h closed loop,
  plant == model, on 9 non-off-start cells: mean realised gap -21.5 units (non-flat, the
  augmented arm is worse) and -0.68 (flat). 3-day loop: 987 units on 182843 (0.54 %,
  -0.19 SEK) on the off-start cell; 2.0 units on 158 (1.3 %) on the flat null cell.
- **M7a decomposition, 2400/2400**: no `_co_optimize` pass after the first adopts anything
  (0 cells; 1200 cells call it). decomp_delta is 0 everywhere, so iterating DHW <-> space does
  not change cost.
- **M7b**: the "dumps the last couple of hours" half of the docstring holds. Zeroing the
  credit moves 1811 plans and lowers tail energy on 1659; on 19 it raises tail energy.
- **M8, 2400/2400**: the settled regret (the plant's pull-free objective, production minus
  oracle, on cells where both hold the floor) averages 0.421 SEK/horizon non-flat
  (n = 1638; 0.279 with the largest dropped) and 0.374 at flat (n = 218). The
  price-attributable part is about 0.05 SEK/horizon. On the plant, production's plan breaches
  the floor on 459/2100 non-flat and 82/300 flat cells against a 20 % heat-loss mismatch. That
  is the open-loop cost of a mis-learned model, it is the same at flat prices, and it is not
  price optimality. Mean model gap at the end room: 0.83 K.

## Harnesses

`race.py`, `offstart.py`, `loop.py`, `decomp_oracle.py`, `terminal_claim.py`, `wall_d15.py`
(with `d0s3_lib.py`, the shared builders). Each header holds its command, metric,
perturbation and expected value. The outputs sit beside them: `race_out/`,
`offstart_out/`, `loop_out/`, `decomp_out/`, `terminal_out*.txt`.

## Redispatched items

- **C1** (M6 recorded as "spot" with no denominator): examined. The universe is
  `loop.py --list` (555); 546 had the re-plan test and the 9 coordinator cells did not.
- **C2** (M4: valve storage, wood, 6/48 h horizons and coordinator captures not run in the
  winter cells): examined on this seat's four prices. All five plants and all three horizons
  ran on every weather, including winter_cold and winter_mild, and the coordinator captures
  were raced. The winter price profiles are D0-s2's M4 cells.
- **C3** (closed loop cut, realised objective not scored, no multi-day loop): examined. The
  closed loop ran on 24 cells, scored on the realised full production objective, and the
  3-day loop ran on 2 cells.
- **C4** (valve storage, wood, 6/48 h horizons and coordinator captures not raced on the
  price axis): examined, all 1220.
- **C5** (rolling ran on one cell with plant == model; score omitted the pull and cycling
  terms): examined. 24 cells ran with plant == model and with a mismatched plant, scored on
  the plant's whole production objective.

## Not finished

- M6: the one-re-plan masking test did not run on the 9 coordinator-capture gap cells, so
  only step-0 was read for them (it differs on 0 of 9).
- M8: the per-install-day oracle. `enumerate.py d15-installs` refuses in the export
  (D0-s3-01), and the bundle evidence is not in the tree.

## Exposure

None. `docs/` and GitHub were not read.
