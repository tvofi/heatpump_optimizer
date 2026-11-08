R10-PARTLOAD-RESIDUE: the three measure-first items #3182 left. Each was measured at this group's merge base. Repair round 3 adds carry 2's fourth seam, the wood advisor's pump-heat price, which is measured and **fixed in production** (`wood_fuel.py`, plus the one `partload_at` line in `coordinator.py`). Repair round 4 re-cuts that fix's signature only: `build_wood_fuel_view` now takes the per-step COP series instead of an eleventh parameter, so `params_over_10` is back at main's 6 (`## Repair round 4`). The diff also lands the harness that re-derives the CPU figures and carry 2's stated-rate figures (`dev/audit/harnesses/r10_partload_residue.py`), plus its `INERT` classification. The linear-valuation bounds come from `r10_partload_pricing.py`, the finder's harness, which is already in the tree. Carries are numbered 1 to 3 in roster order, so the brief's carry 0, 1 and 2 are carries 1, 2 and 3 here.

- **Carry 1, the live buffer store's CPU.** A 750 L store costs about 1.9x per solve. One lever at a time: 1.87x on the seeded spread days, 1.93x on the flat null, and 1.15x for the price day alone. The worst solve is 1.83 s here, about 12 s scaled to Pi class. That is 2 % of the shortest optimisation interval the options flow accepts (10 min). The 272 s owner-box outlier did not reproduce in 80 seeded solves, and no harness in the tree re-derives it. **Refused:** no bound or warm start is earned at these numbers.
- **Carry 2, linear valuations under a convex cost.** The hot-water LP's secant error is at most 0.27 currency/day against a hot-water cost of about 7 to 8 per day (3.8 %).
  - This round states a refill rate for the terminal and deferred figures: the plan's own energy-weighted mean draw, `P_r`. At that rate their errors are at most 3.71 and 0.79 per horizon (flat day), against bounds of 4.37 and 2.14 at max power. The zero-derate null reads exactly 0 at both rates.
  - **Not immaterial at the stated rate**, so this measurement does not settle the carry. Whether to segment the hot-water LP and derate the terminal and deferred refill is a production decision on `_plan_dhw_min_cost`, `_terminal_cost` and `_deferred_energy_cost`.
  - The fourth seam, the wood advisor (`wood_fuel` `cheaper_steps` and `_scan_wood_night`), priced pump heat at `price / compute_cop(outdoor)` with no draw. At d = 0.112 that under-prices pump heat by up to 12.6 % (`d / (1 - d)`), and the advisor counted up to 19 (spread) and 58 (flat) fewer wood-cheaper steps than at the derated price. **Fixed here:** each step's COP is multiplied by `partload_factor` at the plan's own total draw (`## Repair round 3`). At the default derate 0 every factor is exactly 1.0, so the view is unchanged.
  - `_terminal_cost`'s docstring binds its refill pricing to the savings settle-up "exactly as `_deferred_energy_cost` prices it", so the decision cannot be taken in one of them alone. It is carried, with its control and these figures, to the live group that owns the savings settle-up's stored-heat term on `optimizer.py`: R10-SAV-COMFORT (`## Carry for the roster`).
- **Carry 3, Pi CPU of the relaxed start.** The worst clamped solve is 1.96 s and the relaxed pass inside it at most 0.32 s. At the derived Pi-class factor of 6.8x that is about 13.3 s and 2.2 s, against the 600 s budget. The null control holds: the unclamped cells start 0 relaxed runs and spend 0.000 s in the pass. **Refused:** a `maxiter` cap on the relaxed pass is not earned. It would become due only if a clamped solve ran 306x slower than here.


## Head

`5e21a591e7728b8ba4f103dcbc30f6e373371b8b` is this PR's head, the round-5 repair. It is a merge of origin/main 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a into the prior head 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 (parents in that order), made because origin/main had moved since 5fca8c70's base 16f3d9cc3. `git merge-tree --write-tree origin/main 5fca8c70` reported no conflict; the ledger driver merged `tests/closures.json`'s `inert_reads` as a set. No other commit is added.

- The branch's own three-dot diff from merge base 51cd5ec8a has the same `git patch-id --stable` (f7727f66e6957271c8062dbbaf045e2f43453894) as 5fca8c70's own diff from 16f3d9cc3. A different patch would have printed a different id.
- `git diff --quiet 5fca8c70 HEAD` passes on `custom_components/heatpump_optimizer/{coordinator,wood_fuel,thermal_model,optimizer}.py`, `tests/wood_advisor.py`, `tests/profiles.py` and the four `dev/audit/harnesses/r10_*` harnesses the figures read; the only `custom_components` paths main moved are `manifest.json` and the card JS (the stamp). So every figure below, taken at a3a54793c (tree-identical to 17e891bf0) or earlier as each states, holds at this head for the branch's own code; none was re-taken.
- `tools/pr/prepr.sh` was re-run at this head (`## Figures`, **Gate**).

## Repair round 5

The answer to the round-5 verdict at 5fca8c70 (`ci-red`). The verdict owes no code change: the head's units were all green and the two red `gate` jobs were deferrals to an edit run. Its one body finding was that `## Red checks` did not name 5fca8c70's reds; they are now named there. Carry: dismissed: fixed in this body
- origin/main had moved (16f3d9cc3 -> 51cd5ec8a), so the brief's merge-and-rerun applies, and the new head gets fresh code-run gates. Carry: dismissed: fixed in this diff

## Repair round 4

The answer to round 3's three reds at 0940e9aae (`## Red checks`), in one commit, a3a54793c.

- **`build_wood_fuel_view` had eleven parameters.** It took `outdoor`, `cop_at` and the new `partload` only to build one per-step COP series. It now takes that series, `cops`. `wood_fuel_from_parts` builds it as `_derated(_cops(outdoor, compute_cop), _plan_partload(...))`, and `_attach_night_advice` reads the same series. The view goes from 11 parameters to 8 keyword ones plus `config` (9), and `_attach_night_advice` from 10 to 8. No budget is raised and no `PARAMS_OVER_10_LEFT` row is added. Carry: dismissed: fixed in this diff
  - The night scan's flat-COP fallback now reads `cops` instead of `outdoor`. The two are empty together: `_derated` keeps the length of its COP list, which is the length of `outdoor`.
  - Callers updated: two in `tests/wood_advisor.py` and three in `tests/features.py`, each `outdoor=[x] * n, cop_at=lambda _t: c` becoming `cops=[c] * n`. Each fed a constant COP, so each test reads the same numbers as before. The `wood_fuel_from_parts` tests are unchanged.
  - `dev/audit/rounds/round9/D12/leads/l2_wood_currency.py` calls `build_wood_fuel_view` with `space_kw` and `dhw_kw`, which the function has not taken at main either. It is a round-9 lead record, so it is left as it was.
- **The pins `mutation-autofix` wrote at 9211bed5a are kept.** The two pinned lines (`_derated`'s return and `_plan_partload`'s `result is None or partload_at is None` guard) are unchanged in text, now at lines 541 and 660. Each mutant was applied by hand at a3a54793c and still fails `tests/wood_advisor.py` (`TypeError` from a `None` list and from a `None` callable). Carry: dismissed: fixed in this diff
- **Architecture score.** Before, at 9211bed5a: `python3 tools/audit/archscore/score.py --diff 73365699a HEAD` printed `Architecture score: dS -0.1926 WORSENS (inadmissible: params_over_10 6 -> 7)`, and `tests/arch_score_head.py` printed `1 of 18 ARCHITECTURE SCORE HEAD CHECKS FAILED`. After, at a3a54793c: `Architecture score: dS +0.0000 NULL` and `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`. Carry: dismissed: fixed in this diff

Architecture score: dS +0.0000

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
  - The fix: `wood_fuel_from_parts` builds the per-step factors with `_plan_partload`, `partload_factor` at space plus hot-water draw. `_derated` multiplies the COPs by them. Since round 4, `wood_fuel_from_parts` does this and passes the series to `build_wood_fuel_view` as `cops`.
  - `thermal_model` imports `wood_fuel`, so `partload_factor` is passed in by the coordinator (`partload_at`), as `compute_cop` is. A late import would add an import cycle, which `tests/structure.py` refuses.
  - After the fix, the harness's production comparison reads count residual 0 and night picks off 0 on every row. At the merge base the same harness reads 19/67 (spread) and 58/560 (flat) (`## Figures`). Carry: dismissed: fixed in this diff
- **Follow-up: `refill` had no positive control.** Added in 4555ba0c8. `refill` now exits 1 when a d > 0 price day's terminal, deferred or wood-price maximum is 0. Mutant `k_r = 0.0` now prints `positive (d>0) price days with a zero maximum 2` and exits 1 (`## Null control`). Carry: dismissed: fixed in this diff
- **Residual: carry 1's 272 s outlier.** Kept as stated. It is refused on non-reproduction in 80 seeded solves, on the synthetic owner shape alone, and it re-opens only from a diagnostics bundle (D15). Carry: dismissed: no in-tree input reproduces it; re-opens only from a diagnostics bundle (D15), which this group does not hold

## Mutation proof

Re-executed at a3a54793c, because round 4 changes where the derate is applied. Each fix line was mutated alone in the worktree, the pinning checks were run, and the line was restored. The checks: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/wood_advisor.py`, and the `tests/features.py` wood block through `python3 tools/audit/seat/features_block.py --prelude "from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator" --prelude "from harness import FakeEntry, FakeHass" --prelude "NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)" "from heatpump_optimizer.wood_fuel import (" "_wf_soc_kwargs = dict("`. Baseline: both exit 0 (25 and 31 checks).

| mutant | failing checks |
|---|---|
| M1 `coordinator.py` drops `partload_at=partload_factor` | features: "the published wood advisor prices a max-power step's pump heat at the derated COP (cheaper at d = 0.1, not at d = 0; R10-PARTLOAD-RESIDUE)" |
| M2 `_plan_partload`'s guard always returns the empty list | wood_advisor: "the wood advisor prices pump heat at the derated COP of the plan's own draw ...", "the derate reads only what the plan publishes ..." and "the night advice prices pump heat at the derated COP ..."; features: the check above |
| M3 `_derated` drops the factor (`c` for `c * f`) | the same four |
| M4 the night scan ignores `cops` and always reads the flat COP 3 | wood_advisor: "the night advice prices pump heat at the derated COP ..." |
| M5 `wood_fuel_from_parts` derates by an empty factor list | the three wood_advisor checks of M2, and the features check |
| M6 the hot-water draw is dropped from the total | the three wood_advisor checks of M2 |

The failing test came first in round 3. Its first version, run against the unfixed `wood_fuel.py`, read `[0, 0, 0]` where `[30, 0, 0]` was expected. The final checks pass `partload_at`, which the unfixed `wood_fuel_from_parts` does not accept, so at the merge base they raise `TypeError`.

Diff mutants (`prepr.sh` step 6d', owner ruling 2026-11-07): `MUTANT_CMD` was `bash <script>`, with `MUTANT_MAX=40`. The script, a short file in this seat's scratch directory, runs `tests/wood_advisor.py`, then the features wood block above, and exits non-zero on the first failure.
- Standalone at a3a54793c: `python3 -I tools/audit/seat/mutant_run.py --diff 73365699a...HEAD --cmd "bash <script>" --max-mutants 40 --report-only` listed 7 mutants (`--list`), took 12 s wall, printed no `SURVIVED` line and exited 0. Survivor count: 0.
- `prepr.sh`'s own step: see `## Figures`, **Gate**.

## Unpinned sites

none: the two sites this diff added (`_derated`'s RETURN_DEL and `_plan_partload`'s GUARD_OFF, numbered 546 and 666 at 0940e9aae and 541 and 660 now) were pinned by `mutation-autofix` at 9211bed5a, killed by `tests/wood_advisor.py`. Those ledger files are kept, and both mutants still fail `tests/wood_advisor.py` at a3a54793c (`## Repair round 4`).

## Null control

- Carry 1: the flat price day, with no cheap window to store for. The 750 L store still costs 1.93x there, so its cost is per-solve model work, not arbitrage search. The no-buffer arm separates the price lever: 0.455 s flat against 0.522 s spread, p50.
- Carry 2: zero derate.
  - `r10_partload_pricing.py` prints `null rows not zero 0`.
  - `r10_partload_residue.py refill`, at 2f25b3893, at a3a54793c and at the merge base, prints `null rows not zero 0`. Its d = 0 rows read `0.000000` for the terminal, deferred and wood-price errors, a count shortfall of 0, 0 night picks changed, and production residual 0.
- Positive controls on `refill`, each on a mutated copy of the harness at 4555ba0c8 (outputs in this seat's evidence):
  - `k_r = 0.0`: `positive (d>0) price days with a zero maximum 2`, exit 1.
  - The wood derate dropped (`true = lin`): the same line, `2`, exit 1.
  - The null arm perturbed (factor - 1e-9): `null rows not zero 32`, exit 1.
- The production comparison is its own control. At the merge base it reads the defect (count residual 19 and 58, night picks off 67 and 560). At 2f25b3893 and at a3a54793c it reads 0 on all four rows. At d = 0 it reads 0 at both ends.
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
- At 2f25b3893, and again at a3a54793c (round 4, digit-identical on every printed row, rc 0), it prints:
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

**Structure.** Round 4, at a3a54793c: `PYTHONPATH=tests/hastub python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. Round 4 re-records nothing; `tests/structure_budgets.json` is as round 3 left it. Round 3's re-record lowered `class_excess_loc` and `max_class_loc` by 1 each (the coordinator's `_wear_price` `int()` argument joined onto one line; the reason is in that commit's message). No budget rises.

**Architecture score.** `python3 tools/audit/archscore/score.py --diff 73365699a HEAD`: `Architecture score: dS -0.1926 WORSENS (inadmissible: params_over_10 6->7)` at 9211bed5a (49 s wall), `Architecture score: dS +0.0000 NULL` at a3a54793c. `PYTHONPATH=tests/hastub python3 tests/arch_score_head.py`: `1 of 18 ARCHITECTURE SCORE HEAD CHECKS FAILED` at 9211bed5a, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED` at a3a54793c. No gate metric rises, so no `## Architecture score` explanation is owed.

**Gate.** Round 5, at 5e21a591e: `MUTANT_CMD="bash <script>" MUTANT_MAX=40 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` (the same script as round 4's, recreated in this seat's scratch directory) printed `gate mode MODE: SCOPED`, `CI PREDICT: no closures, fast, governance or instrument red predicted against 51cd5ec8a42a`, `merged structure STRUCTURE RATCHET PASSED`, `diff mutants no survivor`, `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted` and the result line `PRE-PR: 5e21a591e7728b8ba4f103dcbc30f6e373371b8b ... rc=0`, in 796 s wall. Round 4's run was at a3a54793c, `PRE-PR: a3a54793cf23ee4d5c6b790969e722b901625f56 ... rc=0`.

## Red checks

At head 5fca8c7042a0b1b11057b9694a55e9965a07bdf4 (the prior head) the only concluded non-success runs were two `gate` jobs, as the round-5 verdict read from all 94 check runs: job 128826607391 (code run 42501481491) and job 128826617125 (code run 42501476955). Every other required leg, `codeql / Analyze (python)` included, concluded `success` or `skipped`.

- `gate` (jobs 128826607391 and 128826617125): **a gate deferral to the body-edit run, not a failed unit; this diff did not cause it.** Both logs read only `FAIL run(s) [42511845716] at this head are still being judged; their gate decides` and exit 1. Edit run 42511845716's own `gate` (job 128827075024) concluded `success`. With `gate-sweep.yml` disabled nothing re-ran the deferred gates. Cheaper detector: none; the deferral happens only at CI time, when a body edit races a code run's gate. This head is new, so its code-run gates run afresh. Carry: dismissed: a CI-time gate deferral with no cheaper detector; R10-HOTFIX-TRAIN-DEFER-WAIT holds the class
- At this head, 5e21a591e: no check had concluded when this body was written, because the head is pushed with it.

Earlier, at head 17e891bf0, the check runs that concluded non-success, read from all check-run pages of the commit, are three: `codeql / Analyze (python)` (`cancelled`, job 128686972435, run 42461842836) and two `gate` jobs (`failure`, jobs 128686936720 and 128687225710). No code-scanning alert is attached to this head: `Perform CodeQL Analysis` was cancelled, not failed, so no analysis was uploaded to raise one on a line this diff added.

- `codeql / Analyze (python)`: **cancelled at the 45-minute cap, runner-speed variance; this diff did not cause it.**
  - Evidence: the job ran 08:12:02Z to 08:57:09Z (45 min 7 s). Every step before `Perform CodeQL Analysis` succeeded, that step ran 08:12:27Z to 08:57:02Z (44 min 35 s) and is the only `cancelled` step, and the next step (the INERT-list check) was skipped. A real alert concludes `success` with an alert attached; a timeout concludes `cancelled`.
  - This is the recorded R10-HOTFIX-CODEQL-HEADROOM finding (branch `fix/r10-hotfix-codeql-headroom`, 55a2753a6), whose measured analysis time is p50 41.4 min and p90 44.4 min against the 45-minute cap, so a slow runner cancels about one run in ten regardless of the diff.
  - Not this diff: it adds a few dozen lines to `wood_fuel.py` and one keyword argument in `coordinator.py`, plus tests and one harness. That does not move a whole-tree extraction by minutes. Main's own run of the same check at 72940b795 (started 09:07:57Z) had not concluded when read, so no same-check main comparison exists yet; the cause rests on the step record above and on the recorded p90.
  - Cheaper detector: none that predicts a runner-speed cancellation before it happens; the standing countermeasure is the headroom hotfix itself, which is the recorded finding and is not this group's to build. Carry: dismissed: recorded as R10-HOTFIX-CODEQL-HEADROOM; a rerun of the cancelled job is the repair
- `gate` (jobs 128686936720 and 128687225710): **a consequence of the CodeQL cancellation, not an independent red.** The log of the first reads `FAIL codeql / Analyze (python): cancelled (this run)` and of the second `FAIL codeql / Analyze (python): cancelled (run 42461842836)`, then `Process completed with exit code 1`. The gate aggregates the required contexts and fails on that one cancelled leg; nothing else failed. This diff did not cause it. Cheaper detector: none needed; the gate is itself the aggregator, and it turns green once `codeql / Analyze (python)` concludes `success` on a rerun.
- Round-3 reds, already answered and fixed in a3a54793c, kept for the record: `arch-score / arch-score` and `tests / arch-instrument` at 0940e9aae and 9211bed5a (cause: `build_wood_fuel_view`'s eleventh parameter; fixed, `dS +0.0000 NULL` and `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`), and `tests / mutation` at 0940e9aae (self-repaired by `mutation-autofix`'s pins).
  - `arch-score` (jobs 128662784884 and 128662815628 at 9211bed5a; 128658352537 at 0940e9aae). Log: `Architecture score: dS -0.1926 WORSENS (inadmissible: params_over_10 6->7)`. Cheaper detector: `python3 tools/audit/archscore/score.py --diff <base> HEAD`, about 50 s. **`tools/pr/prepr.sh` does not run it**: it names only `tools/audit/archscore/ABOUT.md`, and `PREPR_SKIP_CLOSURES=1`'s scoped selection does not reach it. The detector existed and round 3 did not run it.
  - `arch-instrument` (jobs 128662902095 and 128663003289 at 9211bed5a; 128658496674 at 0940e9aae). Log: `FAIL every function over ten parameters is a dispositioned row (#1776) [unlisted: ['wood_fuel.build_wood_fuel_view'] ...]`. Cheaper detector: `PYTHONPATH=tests/hastub python3 tests/arch_score_head.py`, about 40 s; not run by `prepr.sh` with `PREPR_SKIP_CLOSURES=1` unless the scoped selection names it.
  - `mutation` (job 128658352721 at 0940e9aae): `wood_fuel.py:546 RETURN_DEL` and `:666 GUARD_OFF`, self-repaired by `mutation-autofix`'s pins at 9211bed5a. Cheaper detector: `tools/pr/ci_predict.py` (`ADDED UNPINNED`), which `prepr.sh` runs; it predicted this red, and `ci-autofix.md` assigns the repair to the bot.
  - Root cause of the two arch reds, for `defect-root-cause.md`: a cheaper detector existed (both instruments run locally in under a minute) and the fixer's gate with closures skipped does not include either. Process state: detector exists, not in the seat's gate. Recorded without building a countermeasure: adding both to `prepr.sh` changes a policy instrument, outside this minimal re-cut. Carry: dismissed: recorded here; a `prepr.sh` arch step is a tooling proposal for `proposal-triage.md`, outside this group's scope

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

