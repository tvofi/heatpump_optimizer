R10-PARTLOAD-RESIDUE: the three measure-first items #3182 left. Each was measured at this group's merge base. Repair round 3 adds carry 2's fourth seam, the wood advisor's pump-heat price, which is measured and **fixed in production** (`wood_fuel.py`, plus the one `partload_at` line in `coordinator.py`). The diff also lands the harness that re-derives the CPU figures and carry 2's stated-rate figures (`dev/audit/harnesses/r10_partload_residue.py`), plus its `INERT` classification. The linear-valuation bounds come from `r10_partload_pricing.py`, the finder's harness, which is already in the tree. Carries are numbered 1 to 3 in roster order, so the brief's carry 0, 1 and 2 are carries 1, 2 and 3 here.

- **Carry 1, the live buffer store's CPU.** A 750 L store costs about 1.9x per solve. One lever at a time: 1.87x on the seeded spread days, 1.93x on the flat null, and 1.15x for the price day alone. The worst solve is 1.83 s here, about 12 s scaled to Pi class. That is 2 % of the shortest optimisation interval the options flow accepts (10 min). The 272 s owner-box outlier did not reproduce in 80 seeded solves, and no harness in the tree re-derives it. **Refused:** no bound or warm start is earned at these numbers.
- **Carry 2, linear valuations under a convex cost.** The hot-water LP's secant error is at most 0.27 currency/day against a hot-water cost of about 7 to 8 per day (3.8 %).
  - This round states a refill rate for the terminal and deferred figures: the plan's own energy-weighted mean draw, `P_r`. At that rate their errors are at most 3.71 and 0.79 per horizon (flat day), against bounds of 4.37 and 2.14 at max power. The zero-derate null reads exactly 0 at both rates.
  - **Not immaterial at the stated rate**, so this measurement does not settle the carry. Whether to segment the hot-water LP and derate the terminal and deferred refill is a production decision on `_plan_dhw_min_cost`, `_terminal_cost` and `_deferred_energy_cost`.
  - The fourth seam, the wood advisor (`wood_fuel` `cheaper_steps` and `_scan_wood_night`), priced pump heat at `price / compute_cop(outdoor)` with no draw. At d = 0.112 that under-prices pump heat by up to 12.6 % (`d / (1 - d)`), and the advisor counted up to 19 (spread) and 58 (flat) fewer wood-cheaper steps than at the derated price. **Fixed here:** each step's COP is multiplied by `partload_factor` at the plan's own total draw (`## Repair round 3`). At the default derate 0 every factor is exactly 1.0, so the view is unchanged.
  - `_terminal_cost`'s docstring binds its refill pricing to the savings settle-up "exactly as `_deferred_energy_cost` prices it", so the decision cannot be taken in one of them alone. It is carried, with its control and these figures, to the live group that owns the savings settle-up's stored-heat term on `optimizer.py`: R10-SAV-COMFORT (`## Carry for the roster`).
- **Carry 3, Pi CPU of the relaxed start.** The worst clamped solve is 1.96 s and the relaxed pass inside it at most 0.32 s. At the derived Pi-class factor of 6.8x that is about 13.3 s and 2.2 s, against the 600 s budget. The null control holds: the unclamped cells start 0 relaxed runs and spend 0.000 s in the pass. **Refused:** a `maxiter` cap on the relaxed pass is not earned. It would become due only if a clamped solve ran 306x slower than here.


## Head

0940e9aae621ea196fa2db7842c802df30946467 is the pull request head this body was re-taken at. Its handoff tip 2f25b38933f0d297eb87da092433c3c68e25184e is contained, and the figures below were measured at 2f25b3893 (the code is the same).

- This round's commits sit on the reviewed head 8bef9bc866a7458b19dbc00d0bf4ed07ed2f206a: 4555ba0c8 (harness: the wood arm and the positive control), 26fcbc7eb (the `wood_fuel` fix, its pins, the harness's production comparison and the structure re-record), ac397921e (a test name `prepr.sh`'s no-copies step refused), 8594a61c5 (the equivalent guard deleted, and pins for four diff-mutant survivors) and 2f25b3893 (the pin for the last survivor).
- Merge base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76. Every figure in this body was re-taken at 2f25b3893, or at the merge base where it says so.
- origin/main is 5bc009bc82962df5d239cbacc2e570dffd9a9cf9, read at 2026-11-08T05:59Z. `git merge-tree --write-tree origin/main HEAD` reports no conflict (the ledger driver merges `tests/structure_budgets.json` and `tests/closures.json`), so by the owner's 2026-11-07 ruling no merge is made.
- The CPU figures (carries 1 and 3) were taken at 67cc12cc52afaf347534fa2859a4d6d329ea5690 on merge base b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab. They read the solver alone. This round changes `wood_fuel.py` and one `coordinator.py` call, which no solve reaches. They were not re-taken.

## Repair round 3

The answer to the fix review's verdict at 8bef9bc86, one finding at a time.

- **Block: the wood advisor's pump-heat price was neither measured nor dispositioned.** Measured in 4555ba0c8, fixed in 26fcbc7eb (pins completed in 8594a61c5 and 2f25b3893).
  - Measured with `r10_partload_residue.py refill`'s new wood arm. It uses the same 16 installs x 2 price days x 2 derates and the same solves as the other three seams, and has the zero-derate null.
  - The production `cheaper_hour_count` and `_scan_wood_night` are each fed two COP lists. The first is the advisor's own `compute_cop`. The second is that COP derated at each running step's published draw.
  - Wood prices: 41 points spanning each cell's band, from its lowest linear to its highest derated pump-heat price.
  - At d = 0.112:
    - The pump-heat price error is up to 0.037629 (spread) and 0.061299 (flat) currency/kWh, relative 0.12613 = 0.112 / 0.888.
    - The cheaper-count shortfall is up to 19 steps (spread, on all 16 cells) and 58 (flat, 14 cells).
    - The night pick changes at 67 and 560 of 656 grid prices.
  - At d = 0 every wood figure reads 0.
  - This is not immaterial, and unlike the other three seams it binds no savings settle-up, so it is fixed rather than carried.
  - The fix: `wood_fuel_from_parts` builds the per-step factors with `_plan_partload`, `partload_factor` at space plus hot-water draw. `build_wood_fuel_view` and `_attach_night_advice` multiply the COPs by them (`_derated`).
  - `thermal_model` imports `wood_fuel`, so `partload_factor` is passed in by the coordinator (`partload_at`), as `compute_cop` is. A late import would add an import cycle, which `tests/structure.py` refuses.
  - After the fix, the harness's production comparison reads count residual 0 and night picks off 0 on every row. At the merge base the same harness reads 19/67 (spread) and 58/560 (flat) (`## Figures`). Carry: dismissed: fixed in this diff
- **Follow-up: `refill` had no positive control.** Added in 4555ba0c8. `refill` now exits 1 when a d > 0 price day's terminal, deferred or wood-price maximum is 0. Mutant `k_r = 0.0` now prints `positive (d>0) price days with a zero maximum 2` and exits 1 (`## Null control`). Carry: dismissed: fixed in this diff
- **Residual: carry 1's 272 s outlier.** Kept as stated. It is refused on non-reproduction in 80 seeded solves, on the synthetic owner shape alone, and it re-opens only from a diagnostics bundle (D15). Carry: dismissed: no in-tree input reproduces it; re-opens only from a diagnostics bundle (D15), which this group does not hold

## Mutation proof

Each fix line was mutated alone in the worktree, the pinning checks were run, and the line was restored. The checks: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/wood_advisor.py`, and the `tests/features.py` wood block through `python3 tools/audit/seat/features_block.py --prelude "from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator" --prelude "from harness import FakeEntry, FakeHass" --prelude "NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)" "from heatpump_optimizer.wood_fuel import (" "_wf_soc_kwargs = dict("`. Baseline: both exit 0.

| mutant | failing checks |
|---|---|
| M1 `coordinator.py` drops `partload_at=partload_factor` | features: "the published wood advisor prices a max-power step's pump heat at the derated COP (cheaper at d = 0.1, not at d = 0; R10-PARTLOAD-RESIDUE)" |
| M2 `_plan_partload` returns an empty list | wood_advisor: "the wood advisor prices pump heat at the derated COP of the plan's own draw ..." and "the night advice prices pump heat at the derated COP ..."; features: the check above |
| M3 `_derated` drops the factor | the same three |
| M4 `_attach_night_advice` gets no `partload` | wood_advisor: "the night advice prices pump heat at the derated COP ..." |
| M5 the cheaper count's COPs are not derated | wood_advisor: "the wood advisor prices pump heat ..."; features: the check above |
| M6 the hot-water draw is dropped from the total | wood_advisor: both checks (the space share sits at the floor, so only the total derates) |

The failing test came first. Its first version, run against the unfixed `wood_fuel.py`, read `[0, 0, 0]` where `[30, 0, 0]` was expected. The final checks pass `partload_at`, which the unfixed `wood_fuel_from_parts` does not accept, so at the merge base they raise `TypeError`.

Diff mutants (`prepr.sh` step 6d', owner ruling 2026-11-07): `MUTANT_CMD` was `bash <script>`, with `MUTANT_MAX=40`. The script, a short file in this seat's scratch directory, runs `tests/wood_advisor.py`, then the features wood block above, and exits non-zero on the first failure.
- The first standalone run of `python3 -I tools/audit/seat/mutant_run.py --diff 4b5d771bd...HEAD --cmd "bash <script>" --max-mutants 40 --report-only`, at ac397921e, took 20 s wall and found 8 `SURVIVED` sites, all in `wood_fuel.py`:
  - `_derated`'s empty guard, GUARD_OFF and RETURN_DEL. This mutant is equivalent: an empty `partload` gives `[] + cops`. The guard is deleted in 8594a61c5.
  - `_derated`'s `strict` swap. Pinned by a plan shorter than the outdoor list.
  - `_plan_partload`'s None guard, GUARD_OFF and RETURN_DEL. Pinned by the default `partload_at=None`.
  - Its `finite_float` default. Pinned by a non-finite space draw.
  - Its `fillvalue`. Pinned by no hot-water schedule.
  - The night advice's `[3.0]` fallback. Pinned in 2f25b3893.
- The rerun at 2f25b3893 took 14 s wall and printed no `SURVIVED` line.
- `prepr.sh`'s own step at 2f25b3893 printed `diff mutants no survivor`. Survivor count: 0.

## Unpinned sites

Listed by `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` (`ADDED UNPINNED`) at 2f25b3893. Each is killed by this diff's own tests: the diff-mutant run above has no survivor, and mutation-proof rows M3 and the `partload_at=None` edge check fail on them. The ledger pin is `mutation-autofix`'s to write.
- `custom_components/heatpump_optimizer/wood_fuel.py:546 RETURN_DEL` (`_derated`'s return): pinned by `mutation-autofix`; killed by `tests/wood_advisor.py` "the wood advisor prices pump heat at the derated COP of the plan's own draw ...".
- `custom_components/heatpump_optimizer/wood_fuel.py:666 GUARD_OFF` (`_plan_partload`'s `result is None or partload_at is None` guard): pinned by `mutation-autofix`; killed by `tests/wood_advisor.py` "the derate reads only what the plan publishes: no partload_at, ...".

## Null control

- Carry 1: the flat price day, with no cheap window to store for. The 750 L store still costs 1.93x there, so its cost is per-solve model work, not arbitrage search. The no-buffer arm separates the price lever: 0.455 s flat against 0.522 s spread, p50.
- Carry 2: zero derate.
  - `r10_partload_pricing.py` prints `null rows not zero 0`.
  - `r10_partload_residue.py refill`, at 2f25b3893 and at the merge base, prints `null rows not zero 0`. Its d = 0 rows read `0.000000` for the terminal, deferred and wood-price errors, a count shortfall of 0, 0 night picks changed, and production residual 0.
- Positive controls on `refill`, each on a mutated copy of the harness at 4555ba0c8 (outputs in this seat's evidence):
  - `k_r = 0.0`: `positive (d>0) price days with a zero maximum 2`, exit 1.
  - The wood derate dropped (`true = lin`): the same line, `2`, exit 1.
  - The null arm perturbed (factor - 1e-9): `null rows not zero 32`, exit 1.
- The production comparison is its own control. At the merge base it reads the defect (count residual 19 and 58, night picks off 67 and 560). At 2f25b3893 it reads 0 on all four rows. At d = 0 it reads 0 at both ends.
- The fix's own null is `tests/wood_advisor.py` and the features check at derate 0: 0 cheaper steps, and no night advice.
- Carry 3: the non-relaxed path, on the 32 unclamped cells. They show 0 relaxed runs and a maximum of 0.000 s inside the pass.

## Figures


All CPU times are `time.process_time` of one process pinned to one core (`taskset -c N`), with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`.
- Host: x86_64, `Intel(R) Xeon(R) Processor @ 2.30GHz`, family 6, model 173 (Granite Rapids class), Python 3.14.7, numpy 2.5.4, scipy 1.18.1.
- The budget is `config_flow`'s `CONF_OPTIMIZATION_INTERVAL` slider minimum, 10 min = 600 s; the default interval is 30 min.

**Carry 3, relaxed pass.** Command: `PYTHONPATH=tests/hastub:custom_components:tests taskset -c 0 python3 dev/audit/harnesses/r10_partload_residue.py relaxed`.
- It prints `clamped solves 32: solve_s p50 0.466 max 1.961; relaxed_pass_s p50 0.105 max 0.318; worst solve share of budget 0.00327` and `null (unclamped) cells with a relaxed run 0`, exit 0.
- Rule: 16 installs (`r10_setpoint_boost.CELLS`) x 2 price days x 2 derates (0 and the central plant's 0.112), timing only the cells whose levels ship clamped.
- The per-cell delta figures (p50 +0.150 s and maximum +0.667 s clamped; -0.082 to +0.056 s unclamped) are the median, minimum and maximum of the `delta_s` field over the printed per-cell lines, grouped by `clamped`.

**Carry 1, buffer store.** Command: `PYTHONPATH=tests/hastub:custom_components:tests taskset -c 1 python3 dev/audit/harnesses/r10_partload_residue.py buffer 20`. Over 20 seeded solves per arm (seed 2500, `r10_buffer_store.solve`'s owner shape) it prints:

| arm | p50 (s) | max (s) |
|---|---|---|
| 750 L spread | 0.975 | 1.828 |
| 750 L flat | 0.876 | 1.207 |
| 0 L spread | 0.522 | 0.949 |
| 0 L flat | 0.455 | 0.720 |

The ratios are p50 over p50 within a price day: 0.975/0.522 = 1.87x, 0.876/0.455 = 1.93x, and 0.522/0.455 = 1.15x for the price lever.

**Carry 2, the at-max bounds** (re-taken at 306a0b76e, digit-identical to round 1). Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py`. It prints:
- `spread d=0.112: cells 16 lp_err max 0.173106 (dhw cost max 8.0681) terminal-at-max max 3.723135 deferred-at-max max 0.963508`
- `flat d=0.112: cells 16 lp_err max 0.267290 (dhw cost max 7.0145) terminal-at-max max 4.368455 deferred-at-max max 2.139841`
- both `d=0.0` rows at `0.000000`, then `null rows not zero 0`, `failures 0`, exit 0.

The 3.8 % share is 0.267290 / 7.0145.

**Carry 2, at the stated rate.** Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_residue.py refill`.
- Rule: the same 16 installs x 2 price days x 2 derates through `r10_partload_pricing.solve` and `terminal_figure`.
- The stated rate is `P_r = sum(P^2) / sum(P)` over the published total draw's running steps (space heating plus hot water), the draw at which the plan bought its mean kWh. The error is the figure times `P_r / heat_per_cop_kw(P_r) - 1`.
- It prints:
  - `spread d=0.112: cells 16 terminal-at-P_r max 2.117798 deferred-at-P_r max 0.486127 (dhw cost max 8.0681, predicted max 33.6792) terminal-at-P_r / predicted max 0.08194`
  - `flat d=0.112: cells 16 terminal-at-P_r max 3.714491 deferred-at-P_r max 0.792466 (dhw cost max 7.0145, predicted max 64.5737) terminal-at-P_r / predicted max 0.79001`
  - both `d=0.0` rows at `0.000000`, then `null rows not zero 0`, `failures 0`, exit 0.
- The `/ predicted` column is a per-cell ratio. Its flat maximum comes from a cell whose `predicted_cost` is small, so it is reported as printed and does not set the materiality call. That call rests on the absolute 3.714491 and 0.792466 per horizon against the 7.0145/day hot-water cost the verdict used.

**Pi-class factor: 6.8x**, the ratio of Geekbench 6 single-core scores.
- Granite Rapids/Emerald Rapids GCP C4 vCPU: 1818 to 2319 across the published C4 results. Sources: <https://sparecores.com/server/gcp/c4-highcpu-2> (2292), <https://sparecores.com/server/gcp/c4-highcpu-4> (2319) and <https://browser.geekbench.com/v6/cpu/baseline/6766010> (1818).
- Raspberry Pi 4 (Cortex-A72 at 1.5 GHz): 340. Source: Raspberry Pi's own Geekbench 6.2 figure, <https://www.raspberrypi.com/news/benchmarking-raspberry-pi-5/>.
- 2319/340 = 6.8 is the top of the 1818/340 = 5.3 to 6.8 range, so the scaled figures are taken at the slow end.
- Pi-class figures: 1.961 x 6.8 = 13.3 s, 0.318 x 6.8 = 2.2 s and 1.828 x 6.8 = 12.4 s. The breach factor is 600 / 1.961 = 306.

**Carry 2's fourth seam, the wood advisor.** Command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub:custom_components:tests taskset -c 0 python3 dev/audit/harnesses/r10_partload_residue.py refill` at 2f25b3893. The harness sha1 is fc617bd018a323a13891beb284a733ce42ce31bc. The same command was run on a merge-base worktree with this harness copied in, `taskset -c 1`.
- Rule: per cell, the advisor's `wood_fuel._cops(outdoor, compute_cop)` against the same list times `partload_factor(P)` on each running step, where `P` is that step's published space plus hot-water draw.
- Both lists are fed to the production `cheaper_hour_count` and `_scan_wood_night`, at 41 wood prices evenly spanning each cell's band, from its lowest linear to its highest derated pump-heat price.
- "Production" is the COP list the tree's advisor uses: `production_cops`, which is `_cops` alone where `wood_fuel._plan_partload` is absent.
- At 2f25b3893 it prints:
  - `spread d=0.112: wood price err max 0.037629 rel max 0.12613; count short max 19 (share of running steps max 0.7368); cells with a count short 16; night picks changed 67 of 656 (cells 16)`
  - `flat d=0.112: wood price err max 0.061299 rel max 0.12613; count short max 58 (share of running steps max 1.0000); cells with a count short 14; night picks changed 560 of 656 (cells 14)`
  - `production advisor against the derated arm: count residual max 0, night picks off 0` on all four rows
  - the d = 0.0 wood rows at 0, then `null rows not zero 0`, `positive (d>0) price days with a zero maximum 0`, `failures 0`, rc 0.
- At the merge base 4b5d771bd, the wood rows are identical, and the production rows read:
  - `spread d=0.112: ... count residual max 19, night picks off 67`
  - `flat d=0.112: ... count residual max 58, night picks off 560`
  - 0 at d = 0.0, rc 0.
- The flat day's share of 1.0 is its constant price: every running step sits at one pump-heat price, so a wood price inside the 12.6 % band flips every step at max draw.
- The terminal and deferred rows printed by the same run are digit-identical to round 2 (`2.117798`/`0.486127` spread and `3.714491`/`0.792466` flat).

**Structure.** `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. The re-record lowered `class_excess_loc` from 17585 to 17584 and `max_class_loc` from 7955 to 7954. The coordinator gains one `partload_at` line, and `_wear_price`'s `int()` argument, which was split over three lines, is joined onto one. The reason is in the commit message. No budget rises.

**Gate.** `MUTANT_CMD="bash <script>" MUTANT_MAX=40 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` on 2f25b3893 printed `gate mode MODE: SCOPED`, `merged structure STRUCTURE RATCHET PASSED`, `CI PREDICT: no closures, fast, governance or instrument red predicted`, `diff mutants no survivor` and the result line `PRE-PR: 2f25b38933f0d297eb87da092433c3c68e25184e ... rc=0`, in 729 s wall. The scoped gate (`tests/closure.py select`) names 27 scripts, `tests/wood_advisor.py` and `tests/features.py` among them; this seat ran wood_advisor in full, and the features wood block through `features_block.py`, and leaves the rest to CI.

## Red checks

At head 0940e9aae621ea196fa2db7842c802df30946467 three checks concluded `failure` (CI code run 42457021003, merged into base 73365699a135). **All three are caused by this diff, not by main, and none is a stale red.** The earlier text of this section, which predicted only `tests / mutation`, was wrong about the other two.

- `arch-score / arch-score` (job 128658352537, step "Score the change, and refuse an unexplained rise"). Log: `Architecture score: dS -0.1926 WORSENS (inadmissible: params_over_10 6->7)`. Cause: this diff adds `partload_at` to `wood_fuel.build_wood_fuel_view` (10 -> 11 parameters) and to `wood_fuel_from_parts` (8 -> 9), which takes the function over the ten-parameter line. Main's count is 6, so the red is this diff's. The gate calls the rise inadmissible, so an `## Architecture score` paragraph cannot clear it. Cheaper detector: `python3 tools/audit/archscore/gate.py --base origin/main --head HEAD`, and `tests/arch_score_head.py`. Neither is a step of `tools/pr/prepr.sh` (it names only `tools/audit/archscore/ABOUT.md`), and the prepr run of `PREPR_SKIP_CLOSURES=1` selected 27 scoped scripts without it. The detector exists and was not run.
- `tests / arch-instrument` (job 128658496674, step "Run the architecture-score pair"). Log: `FAIL every function over ten parameters is a dispositioned row (#1776) [unlisted: ['wood_fuel.build_wood_fuel_view']: take the horizon, the weather series or a frozen record of the related arrays, or row the function here with why it stays over the line]`. 1 of 18 head checks failed. Cause: the same eleventh parameter. Same answer for the cheaper detector: `python3 tests/arch_score_head.py` runs in 42 s, is in the closure table, and was scoped out of the local gate. Not run before the push.
- `tests / mutation` (job 128658352721, step "Drive the table over what this diff tested"). Log: `MUTATION TABLE REFUSED -- 2757 unpinned site(s) against 2755 at the ratchet base 73365699a135, 2 of them added by this diff`, namely `wood_fuel.py:546 RETURN_DEL` and `wood_fuel.py:666 GUARD_OFF`. Cause: this diff's own two added sites have no ledger disposition yet. Both are named in `## Unpinned sites` and killed by this diff's tests, and `mutation-autofix` writes the ledger pins (`ci-autofix.md`). So this red is expected and self-repairing. Cheaper detector: `tests/mutation_table.py --scope changed --base origin/main`, which `tools/pr/ci_predict.py` already runs and the body predicted, so it was detected locally and not fixed before the handoff.

Handoff state: the two arch reds need a code change (give `build_wood_fuel_view` a frozen record or the existing horizon/series record instead of an eleventh parameter, or row it in `PARAMS_OVER_10_LEFT` with owner approval). This body-only seat did not touch code. It is blocked and the reviewer should not approve this head until the fixer repairs both.


## Carry for the roster

Destination: R10-SAV-COMFORT (`carries-open`; seam `optimizer.py`, `ledger.py`), appended to its `carry` list by the dispatch seat's append-carry op. Text:

> From R10-PARTLOAD-RESIDUE (#3182 carry 2, PR #3291): under a part-load derate, `_terminal_cost` and `_deferred_energy_cost` value refilled heat at a COP with no draw (`compute_cop` / `marginal_cop`), and `_plan_dhw_min_cost` values hot-water heat linearly at a COP. Each is a secant error that the derate makes convex. Precondition and control: at `cop_partload_derate = 0` every figure below must read exactly 0. `dev/audit/harnesses/r10_partload_pricing.py` and `dev/audit/harnesses/r10_partload_residue.py refill` both print `null rows not zero 0`; a re-measure that does not is void. Figures at PR #3291's head, re-measured at your merge base before use:
> - LP secant error: at most 0.267290 per day against a hot-water cost of 7.0145 (flat day, d = 0.112; 3.81 %).
> - Terminal and deferred errors at max power: at most 4.368455 and 2.139841 per horizon (`r10_partload_pricing.py`, `terminal-at-max` and `deferred-at-max`).
> - The same errors at the plan's own energy-weighted draw `P_r = sum(P^2)/sum(P)`: at most 3.714491 and 0.792466 (flat) and 2.117798 and 0.486127 (spread) (`r10_partload_residue.py refill`).
>
> The terminal error is not immaterial at the stated rate. The decision is yours: whether to price refill at a stated rate's derated heat (`heat_per_cop_kw`) or to segment the hot-water LP. It is legitimate only if the terminal and the deferred figure change together, because `_terminal_cost`'s docstring binds the plan to the savings settle-up "exactly as `_deferred_energy_cost` prices it". `_deferred_energy_cost` reaches `predicted_savings` (its docstring), so a derated refill moves the savings figures your flat-price null separates; keep that shift apart from your stored-heat term in the acceptance.

## Forward-carry

- Carry 2's segmenting and refill-rate decision, its zero-derate control and the figures in `## Carry for the roster`: `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster` (03c1c6c463aa352bf97214e0d70c747ad39f0ec9, where the group reads `carries-open`), group R10-SAV-COMFORT's `carry`, queued for the dispatch seat's append-carry op. Carry: R10-SAV-COMFORT

## Friction

- fixer-pi-measurement: cost: the brief prefers GitHub's ubuntu-24.04-arm runner or an arm64 container under a CPU quota. This seat has neither (x86_64 container, no runner dispatch from a fixer's return refs), so the Pi-class figure is an x86_64 single-core `process_time` scaled by a cited Geekbench 6 single-core ratio. The verdict holds under any factor below 306x. Carry: dismissed: verdict robust below a 306x factor
- fixer-wip-ref: cost: `refs/heads/handoff-wip/r10-partload-residue` held a prior seat's BLOCKED.md commits (19a838bc8), which are not ancestors of the PR head. A fast-forward-only step push was therefore refused, and this seat did not force it. The milestones are in the handoff commits instead. Carry: dismissed: the step ref is deleted after the body push
