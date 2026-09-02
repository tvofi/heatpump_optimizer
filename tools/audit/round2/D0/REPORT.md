# D0 — Price optimality, round 2

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree `audit-r2-D0`,
Apple M1 (8 cores, 8 GB), macOS 25.6, python 3.13.1, numpy 2.5.2, scipy
1.18.1, threadpoolctl 3.6.0. Every harness pins BLAS to one thread and runs
from the repository root with `PYTHONPATH=tests/hastub`. Every CPU/wall figure
here is provisional (ten other auditors shared the box; `load1` ranged 1.5–70
during the runs); the evidence is counts, SEK gaps on the production objective,
iteration counts and projected-gradient norms, which are contention-immune.
Exposure: none (no `docs/` read). No production or test file was edited;
`git status` shows only `tools/audit/`.

## Method

1. **Capture.** `d0lib.Recorder` monkeypatches
   `heatpump_optimizer.optimizer:_multi_start_minimize` (the seam
   `tests/optimality.py` uses) to record every call's objective closure,
   candidates, bounds, `args`, `maxiter`, batch objective and L-BFGS-B
   result, and `HeatPumpOptimizer._optimize_space_only/_optimize_with_dhw`
   to stash the `_Horizon`. `ThermalModel.simulate_trajectory[_batch]` are
   counted. Production runs otherwise untouched; the wrapper returns the
   real result.
2. **Race.** For the recorded call whose `x` became the plan, every
   challenger re-issues production's own `_scoped_minimize` call (same
   `jac` path — `_batch_fd_gradient` where `_bounds_supported_by_batch`
   allows, scipy's scalar FD otherwise — same bounds, same `args`, same
   options unless overridden) from a different start or with a different
   budget: the discarded third candidate; a same-settings **restart** from
   production's answer (fresh curvature memory, nothing else); a relaxed
   budget (`maxiter` 3000, `ftol` 1e-12); bang-bang seeds at
   0.6/0.8/1.0/1.2 × the answer's energy; zero and half-box seeds;
   uniform-random starts; a polish of the best arm. Every plan is scored
   with the production objective closure. **Feasibility parity**: a
   challenger counts only if its comfort floor and ceiling violation (the
   series `_comfort_terms` scores, in degree-steps) is no worse than
   production's; the DHW schedule is fixed in the space stage, so tank
   feasibility is identical by construction; power bounds and pins are the
   same bounds.
3. **Stationarity probe.** `|projected gradient|_∞` at production's answer
   with production's own gradient estimate (scipy's PGTOL quantity, default
   1e-5).
4. **Grid.** 8 prices × 5 weathers × {single, two-zone} × {DHW on, off} at
   24 h (160 cells); the golden feature scenarios (33); the capacity tariff
   and the small-tank valve config swept over the 8 prices; 6 h on a 16-cell
   two-zone subset; 48 h through the golden `horizon_48h` scenario only.
5. **Null control.** The `flat` price profile is in every sweep; the
   closed loop was also run at flat prices.
6. **MPC masking.** `rolling_gap.py` drives the real optimizer in the
   `tests/rolling.py:run_rolling` shape (re-plan every 2 h, perfect plant,
   2 days) with production's solver and with the race's cheap fixes patched
   in through the same seam (`d0lib.ImprovedSolver`), settling the end
   states with production's own `_deferred_energy_cost` (two DHW-cap
   conventions) and adding the realised `tariff.peak_cost`.
7. **Decomposition.** `dhw_coopt.py` wraps `_co_optimize` to run one extra
   DHW↔space pass on its output, and zeroes `_terminal_cost` to check the
   docstring's claim.

## Findings

### D0-01 (medium, bug) — With a capacity tariff the single-zone solver stops on a stalled iteration and returns plans 1–4 SEK/day dearer than its own objective allows

**Claim.** With the golden `capacity_tariff_15min` settings
(`peak_price_per_kw` 20, threshold 6 kW, 15-min windows, 1 kW baseline)
the single-zone plan is beaten on its own objective at comfort parity in
15 of 16 `winter_cold` price×DHW cells; excluding the negative-price cell
the mean gap is 1.26 SEK per solve (2.19 % of the objective, 3.28 % of the
daily energy bill; winter cells 1.7–3.8 SEK = 6.7–9.4 % of their bills),
and on `summer_negative/winter_cold/sz/nodhw` the gap is 58.29 SEK (79.7 %
of the objective: production's plan carries ~62 SEK of peak charge that a
half-box seed avoids at the same comfort). In 16/16 cells production's
answer has `|proj. grad|` 0.03–20 SEK/kW against PGTOL 1e-5 and stopped
on `CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH`.

**Mechanism.** `tariff.peak_cost` sums the top-k window excesses (k =
`peak_count` = 3). Its docstring says this makes the term visible to the
solver; it does for k windows. Any plan with more than k metering windows
tied at the peak — the shape every cheap-hours plan takes once the pump is
held at the threshold — is a plateau on which the 2-point gradient sees
only k of the tied windows; L-BFGS-B moves those, the next k become the
top, the per-iteration reduction is tiny relative to a 70–120 SEK
objective, and the `ftol=1e-6` FACTR test fires. A same-settings restart
recovers 0.66–0.92 SEK in 7/16 cells; `ftol=1e-9` removes the restart gap
entirely; `peak_count=16` collapses the 58 SEK cell to 0.13 SEK.

**Evidence** (`tools/audit/round2/D0/race_grid.py`, 24 h, `--random 3`):

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 0 --weather winter_cold --quiet --random 3 --tag tariff15_baseline \
  --opt '{"peak_price_per_kw":20.0,"peak_threshold_kw":6.0,"peak_window_minutes":15,"baseline_load_kw":1.0}'
RESULT cells_with_gap_sz=15 count            (of 16)
RESULT restart_improves_sz=7 count
RESULT pg_above_pgtol_sz=16 count
RESULT mean_gap_sek_sz=4.8198 SEK             (1.255 SEK with the 58 SEK cell dropped)
RESULT max_gap_sek_sz=58.2850 SEK
RESULT mean_energy_gap_pct_bill_sz=2.517 pct_of_bill
RESULT mean_restart_gap_sek_sz=0.1661 SEK
RESULT loo_mean_gap_pct_sz=2.192 pct_of_objective   (most favourable cell dropped)
RESULT thread_factor=1.000  load1=4.97
```

Per cell (gap SEK / % objective / restart SEK / bill SEK): winter_typical
dhw 0.92/1.26/0.92/32.2; winter_typical nodhw 1.69/2.54/0/25.1;
winter_extreme dhw 0.66/0.65/0.66/54.2; winter_extreme nodhw
3.80/4.23/0.005/52.7; winter_moderate dhw 1.19/1.36/0.03/53.0;
winter_moderate nodhw 3.74/4.58/0.15/40.0; winter_narrow dhw
0.41/0.35/0/84.5; winter_narrow nodhw 0.57/0.54/0/67.5; shoulder dhw
1.18/2.02/0.75/48.8; shoulder nodhw 0.54/1.04/0/39.2; summer_typical dhw
0.59/2.49/0/16.3; summer_typical nodhw 2.37/10.5/0/15.7; summer_negative
dhw 0/0/0/13.8; summer_negative nodhw 58.29/79.7/0.15/11.3; flat dhw
0.71/0.76/0/77.7; flat nodhw 0.48/0.57/0/67.5. The golden scenarios
themselves (`race_scenarios.py --only tariff --verbose`):
`capacity_tariff_15min` gap 0.919 SEK (1.26 %), all recovered by the
restart, pg 18; `capacity_tariff` (60-min windows) gap 0.749 SEK (1.02 %),
pg 2.2.

**Perturbations (all run, all move):**
- `D0_PERTURB=ftol9` (≡ `options["ftol"] = 1e-9` in
  `_multi_start_minimize`): `restart_improves_sz` 7 → **0**,
  `mean_restart_gap_sek_sz` 0.1661 → **0.0000**, `cells_with_gap_sz` 15 →
  10, energy gap 2.517 → 1.385 % of bill, mean gap (58 SEK cell dropped)
  1.255 → 0.634 SEK; `prod_nit` rises (26 → 70 on winter_typical/dhw).
- `--opt ... "peak_count":16` (config; every tied window carries a
  gradient): the negative-price cell's gap 58.285 → **0.130 SEK**; 16-cell
  mean gap 4.82 → 0.525 SEK.
- `D0_PERTURB=restart`: `restart_improves_sz` 7 → 4, mean restart gap
  0.166 → 0.088 (a second stall follows the first in 4 cells).

**Null control.** At `flat` prices the two cells still show 0.71 and 0.48
SEK (0.76 %, 0.57 % of objective) but a restart gap of 0.000: the
price-independent peak term's own kink leaves a basin gap; the stall
component vanishes without a price signal. `summer_negative × 5 weathers`:
the 58 SEK gap appears only with `winter_cold` (a non-physical pairing);
with `winter_mild` it is 0.24 SEK on a 0.68 SEK bill; with the summer
weathers 0.00 (no heating demand).

**MPC masking** (`rolling_gap.py --tz 0 --opt <tariff15>`, 2 days, replan
2 h, settled): winter_typical +0.355 SEK (0.33 % of bill, 0.18 SEK/day);
winter_moderate +0.849 SEK (0.65 %); flat +1.445 SEK (0.93 %); realised
peak charge 0.000–0.014 SEK in both arms; comfort degree-hours 0.000 in
every arm. The realised gain is small and no larger than at flat prices:
re-planning washes most of the single-solve gap out, which is why the
severity is medium (bounded cost) and not high.

**Leave-one-out.** 16 cells; range 0.00–79.7 % of objective; with the
most favourable cell dropped the mean is 2.19 % (14/15 cells > 1e-3 SEK).

**Files.** `custom_components/heatpump_optimizer/optimizer.py`
(`_multi_start_minimize`, `options={"maxiter", "ftol": 1e-6, "eps": 1e-4}`),
`custom_components/heatpump_optimizer/tariff.py` (`peak_cost`).
**Fix scope.** Re-submit the best L-BFGS-B result to the same call until
the objective stops improving (or `ftol` 1e-9 with a `maxiter` that covers
it), and give the peak term a gradient on every tied window (a smooth
top-k, or a per-window excess above the k-th). Expected golden drift:
`capacity_tariff`, `capacity_tariff_15min`, `tariff_plus_two_zone`,
`peak_masked`, `everything_on`.

### D0-02 (low, bug) — Two-zone solves stop on the FACTR test at non-stationary points; a same-settings restart recovers up to 2.16 SEK/day, but re-planning masks it

**Claim.** On the 24 h grid, re-submitting production's answer to the
identical L-BFGS-B call improves the two-zone plan by > 1e-3 SEK in 15/80
cells (mean 0.052 SEK; winter_narrow/winter_cold/tz/dhw 2.163 SEK = 1.75 %
of a 123.4 SEK bill, winter_typical/winter_cold/tz/dhw 0.954 SEK = 1.4 %
of 69.0 SEK); production's answer has `|proj. grad|` > 1e-5 in 64/80
two-zone cells (0.37–0.48 SEK/kW on the two cells above) and stopped on
FACTR in 62/80. The restart gap vanishes at flat prices (max 0.0011 SEK
over 10 flat cells): this component is a price-signal stall. Whole-race
gaps (any arm): 49/80 cells, mean 0.109 SEK (0.51 % of objective,
leave-one-out 0.23 %), but the seed-found part survives flat prices
(0.155 SEK mean at flat vs 0.102 non-flat) and is therefore not price
optimality (see non-findings).

**Evidence** (`race_grid.py`, full grid, `--random 4`):

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --quiet
RESULT cells_tz=80 count
RESULT restart_improves_tz=15 count
RESULT mean_restart_gap_sek_tz=0.0519 SEK
RESULT pg_above_pgtol_tz=64 count
RESULT cells_with_gap_tz=49 count
RESULT mean_gap_sek_tz=0.1088 SEK       max 2.5099 (winter_narrow/winter_cold/tz/dhw)
RESULT mean_gap_pct_tz=0.507 pct_of_objective   loo 0.232
RESULT null_flat_mean_gap_sek_tz=0.1553 SEK     nonflat 0.1022
RESULT cells_sz=80  restart_improves_sz=6  mean_restart_gap_sek_sz=0.0026 SEK
RESULT production_cpu_total=111.80 s (provisional)  thread_factor=1.000  load1=13.80
```

16-cell subset (`--tz 1 --weather winter_cold --random 2`): 13/16 with a
gap, restart improves 7/16, mean restart gap 0.218 SEK, mean gap 0.449
SEK, pg > PGTOL 16/16, flat mean 0.732 SEK (basin).

**Perturbations.**
- `D0_PERTURB=restart` (subset): mean restart gap 0.218 → **0.003 SEK**;
  mean gap 0.449 → 0.249; winter_narrow 2.51 → 0.53, winter_typical 1.22
  → 0.20.
- `D0_PERTURB=ftol9` (subset): mean restart gap 0.218 → **0.0005 SEK**,
  restart improves 7 → 2, cells with gap 13 → 7, mean gap 0.449 → 0.049
  SEK (0.461 → 0.072 % of objective), winter_typical 1.22 → **0.000**
  (nit 22 → 39), winter_narrow 2.51 → 0.16 (nit 19 → 76); the flat cells'
  gap also falls 0.73 → 0.17 SEK.
- `D0_PERTURB=solves3` (full 80 tz cells): mean restart gap 0.052 →
  0.010, cells with gap 49 → 41, mean gap 0.109 → 0.066 SEK.

**MPC masking** (`rolling_gap.py`, two-zone DHW, 2 days, replan 2 h,
perfect plant, settled with `_deferred_energy_cost`): winter_typical,
restart+third only: +0.208 SEK (0.135 % of bill); full improved solver:
+0.100 SEK (0.065 %) although it won 37/37 solves for 10.7 SEK of
objective; winter_narrow restart+third: +0.220 SEK (0.089 %) for 4.8 SEK
of objective; flat: −0.341 SEK. Comfort degree-hours ≤ 0.0023 in every
arm; step-0 action differs in 28 of the 98 gap cells. The gap is not
realised; severity low.

**Horizon.** At 6 h the same 16 cells show 0/16 gaps (mean 0.0001 SEK,
restart 0.0000); at 48 h the golden `horizon_48h` (single-zone) shows
0.325 SEK (0.25 %) with restart 0.

**Leave-one-out.** 80 cells; restart gap range 0–2.163 SEK; mean with the
most favourable cell dropped 0.025 SEK.

**Files.** `optimizer.py:_multi_start_minimize`. **Fix scope.** The same
restart-until-flat rule as D0-01 (or `ftol` 1e-9, which on the subset
removes 89 % of the whole-race gap); expected golden drift on every
two-zone fixture (`winter_two_zone_dhw`, `winter_two_zone_no_dhw`,
`shoulder_two_zone`, `tariff_plus_two_zone`, `everything_on`, the valve and
wood fixtures).

### D0-03 (medium, bug) — A small buffer tank with a mixing valve leaves the solve at a kink: 3.5–4.2 SEK/day dearer than a bang-bang seed, with a breached comfort floor

**Claim.** With the golden `valve_storage_small_tank` config (35 L buffer,
manual valve, tank at 32 °C) swept over the 8 prices (two-zone, no DHW,
`winter_cold`), production's plan is beaten at comfort parity in 5/8
cells, mean 1.13 SEK per solve (4.4 % of the energy bill), max 4.19 SEK
(winter_moderate, 4.0 % of objective) and 3.47 SEK on winter_typical
(3.9 %; the challenger also spends 9.9 SEK less energy, 61.95 vs 71.84
SEK). On winter_typical production's own plan breaches the comfort floor
(0.112 K-steps) while the bang-bang challenger has 0.000. `|proj. grad|`
at production's answer is 2–1.1e4 SEK/kW in 8/8 cells.

**Mechanism.** The `_tighten_buffer_caps` loop in `optimize` lowers the
per-step space-power caps where the tank clamp refused heat and re-solves
from the same three starts (winter_typical: 3 `_multi_start_minimize`
calls, the third adopted). The clamp deletes heat, so the objective is
kinked at the cap; production's starts descend to the kink and the FACTR
test fires there with a projected gradient of 131 SEK/kW.

**Evidence** (`race_grid.py`, 8 cells, `--random 3`):

```
PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py --tz 1 --dhw 0 --weather winter_cold --quiet --random 3 --tag smalltank \
  --cfg '{"mixing_valve_mode":"manual","buffer_tank_volume":35.0,"buffer_max_temperature":70.0}' --state '{"buffer_tank_temperature":32.0}'
RESULT cells_with_gap_tz=5 count   (of 8)
RESULT pg_above_pgtol_tz=8 count
RESULT mean_gap_sek_tz=1.1333 SEK   max 4.1884
RESULT mean_energy_gap_pct_bill_tz=4.396 pct_of_bill
RESULT loo_mean_gap_pct_tz=0.804 pct_of_objective
RESULT null_flat_mean_gap_sek_tz=0.1411 SEK   (0.13 % of objective)
RESULT thread_factor=1.000  load1=3.31
```

Per cell: winter_typical 3.47 (3.90 %, pg 1.3e2); winter_extreme 1.05
(0.81 %, pg 8.5e2); summer_typical 0.22 (0.79 %); summer_negative 0.00;
shoulder 0.00 (pg 4.6e3); winter_narrow 0.00 (pg 1.1e4); winter_moderate
4.19 (4.00 %, pg 84); flat 0.14 (0.13 %). `race_scenarios.py --only
small_tank --verbose` shows the arms: production obj 88.975, under 0.112;
`seed_bang1.0` obj 85.504, under 0.000, min room 16.72 vs 16.89.

**Perturbation** (config): `buffer_tank_volume` 35 → 750 L (the golden
`valve_storage` config): mean gap 1.133 → **0.205 SEK**, winter_typical
3.47 → **0.000**, winter_moderate 4.19 → 0.20, pg ≤ 0.18 in every cell.

**Null control.** flat: 0.14 SEK (0.13 %) — a residual basin gap, not the
kink. **Leave-one-out.** 8 cells, range 0.00–4.00 % of objective; most
favourable dropped: 0.80 %. **MPC masking**: not run (budget); the comfort
breach is a single-solve property of the plan the sensors publish.

**Files.** `optimizer.py` (`_tighten_buffer_caps`, the re-solve in
`optimize`, `_multi_start_minimize`). **Fix scope.** Seed the cap-tightened
re-solve from the previous answer clipped to the new caps plus a bang-bang
seed, and apply the restart rule; expected golden drift:
`valve_storage_small_tank`, possibly `valve_storage_low_target`.

## Non-findings (checked and held)

| Claim | Command | Value |
|---|---|---|
| Single-zone default solves (no tariff) are at their optimum: every one of 16 arms ties production to 1e-6 on winter_typical/winter_cold sz cells | `race_grid.py --price winter_typical --weather winter_cold --tz 0` | gap 0.0000 SEK in both cells; whole sz grid mean 0.041 SEK, max 0.66 (flat/sz/dhw), restart improves 6/80 (mean 0.0026 SEK) |
| The seed-found two-zone gap survives flat prices and is therefore non-convexity, not price optimality | `race_grid.py --quiet` | flat tz mean 0.155 SEK (8/10 cells) vs non-flat 0.102 SEK; subset flat 0.732 vs 0.409 |
| Larger budget / tighter `ftol` / other `eps` from production's answer does not move single-zone plans | `race_grid.py` arms `budget_warm`, `eps*` | winter_typical sz: 0 iterations, identical x; sz restart improves 6/80 |
| A second DHW↔space co-optimization pass never changes the plan | `dhw_coopt.py` | pass 2 re-solved 4/20, adopted 0/20, gain 0.000 SEK (pass 1: adopted 3/20, 0.558 SEK) |
| The terminal credit does what its docstring claims (without it the tail is dumped) | `dhw_coopt.py` | end-of-horizon room −2.05 K mean, last-2 h energy −6.55 kWh mean, 19/20 cells |
| The discarded third candidate rarely wins | `race_grid.py`, `race_scenarios.py` | best arm was `third_cand*` in 0/160 grid cells (`polish[third_cand2]` in 2 wood scenarios) |
| The closed loop does not realise the two-zone gap | `rolling_gap.py` | +0.10 SEK / 2 d (0.065 %) full improved; +0.21 restart-only; flat −0.34 |
| Golden feature scenarios: single-zone ones tie or nearly tie | `race_scenarios.py` | sz 20: 8 with gap, mean 0.16 %, LOO 0.105 %; extreme/negative/wide_band/peak_masked/price_risk/building_preset/capacity_curve 0.0000 |
| Horizon 6 h solves are at their optimum | `race_scenarios.py` (`horizon_6h`), `race_grid.py --hours 6 --tz 1 --weather winter_cold --random 2` | horizon_6h gap 0.0000; 6 h subset 0/16 cells with gap, mean 0.0001 SEK, restart 0.0000 |
| Horizon 48 h | `race_scenarios.py` (`horizon_48h`, sz) | gap 0.325 SEK (0.25 %), restart 0 |
| Wood/valve two-zone scenarios show only the D0-02 class of gap | `race_scenarios.py` | wood_coil 0.85 SEK (0.86 %), everything_on 0.55 (0.71 %), wood_two_tank 0.39, valve_storage 0.000, valve_upper_direct_slab 0.000 |
| Batched jac path is what the race uses | `d0lib.make_jac` | `_bounds_supported_by_batch` honoured per call; fuse_guard (zero-range bounds) raced on the scalar path, gap 0.28 SEK (0.37 %) |
| With a capacity tariff the closed loop realises no peak charge in either arm | `rolling_gap.py --tz 0 --opt <tariff15>` | realised peak charge 0.000–0.014 SEK; settled gap 0.36 / 0.85 / 1.45 SEK per 2 days (winter_typical / winter_moderate / flat) |

## Harnesses

- `tools/audit/round2/D0/d0lib.py` — capture, race, feasibility, improved solver (library, imported by the others)
- `tools/audit/round2/D0/race_grid.py` — the price×weather×topology×DHW race, perturbations (`D0_PERTURB=solves3|ftol9|restart`), `--opt/--cfg/--state` overrides
- `tools/audit/round2/D0/race_scenarios.py` — the golden feature scenarios
- `tools/audit/round2/D0/rolling_gap.py` — closed-loop realised gap with settlement and realised peak charge
- `tools/audit/round2/D0/dhw_coopt.py` — DHW↔space second pass and terminal credit
- `tools/audit/round2/D0/out/*.json` — per-cell, per-arm records of every run cited

## Not finished

- 48 h on the grid (only the golden `horizon_48h` scenario); the coordinator
  captures (`_capture_coordinator`) were not raced; no global outer bound
  (DE / coarse DP) was attempted — the restart and seed arms already prove
  the production point is not stationary, which is the cheaper proof.
- `rolling_gap.py` for D0-03, and at the production 30-min re-plan interval.
- All CPU figures (production 111.8 s for 160 solves) are fan-out numbers.
