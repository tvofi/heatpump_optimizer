R10-PARTLOAD-RESIDUE: the three measure-first items #3182 left. Each was measured at this group's merge base, and **no production line changes**. The diff lands the harness that re-derives the CPU figures and carry 2's stated-rate figures (`dev/audit/harnesses/r10_partload_residue.py`), plus its `INERT` classification. The linear-valuation bounds come from `r10_partload_pricing.py`, the finder's harness, which is already in the tree. Carries are numbered 1 to 3 in roster order, so the brief's carry 0, 1 and 2 are carries 1, 2 and 3 here.

- **Carry 1, the live buffer store's CPU.** A 750 L store costs about 1.9x per solve. One lever at a time: 1.87x on the seeded spread days, 1.93x on the flat null, and 1.15x for the price day alone. The worst solve is 1.83 s here, about 12 s scaled to Pi class. That is 2 % of the shortest optimisation interval the options flow accepts (10 min). The 272 s owner-box outlier did not reproduce in 80 seeded solves, and no harness in the tree re-derives it. **Refused:** no bound or warm start is earned at these numbers.
- **Carry 2, linear valuations under a convex cost.** The hot-water LP's secant error is at most 0.27 currency/day against a hot-water cost of about 7 to 8 per day (3.8 %).
  - This round states a refill rate for the terminal and deferred figures: the plan's own energy-weighted mean draw, `P_r`. At that rate their errors are at most 3.71 and 0.79 per horizon (flat day), against bounds of 4.37 and 2.14 at max power. The zero-derate null reads exactly 0 at both rates.
  - **Not immaterial at the stated rate**, so this measurement does not settle the carry. Whether to segment the hot-water LP and derate the terminal and deferred refill is a production decision on `_plan_dhw_min_cost`, `_terminal_cost` and `_deferred_energy_cost`.
  - `_terminal_cost`'s docstring binds its refill pricing to the savings settle-up "exactly as `_deferred_energy_cost` prices it", so the decision cannot be taken in one of them alone. It is carried, with its control and these figures, to the live group that owns the savings settle-up's stored-heat term on `optimizer.py`: R10-SAV-COMFORT (`## Carry for the roster`).
- **Carry 3, Pi CPU of the relaxed start.** The worst clamped solve is 1.96 s and the relaxed pass inside it at most 0.32 s. At the derived Pi-class factor of 6.8x that is about 13.3 s and 2.2 s, against the 600 s budget. The null control holds: the unclamped cells start 0 relaxed runs and spend 0.000 s in the pass. **Refused:** a `maxiter` cap on the relaxed pass is not earned. It would become due only if a clamped solve ran 306x slower than here.

## Head

306a0b76e8bdd3e82e7370e3f1ad7bc08be832c1.

- The CPU figures (carries 1 and 3) were taken at 67cc12cc52afaf347534fa2859a4d6d329ea5690, on merge base b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab.
- Two `origin/main` merges followed: 219c27b5d (bringing in 1c1ae100b) and 12a5d22a5 (bringing in 4b5d771bd). Neither moved anything the figures read: `git diff --quiet b4ec2f332 306a0b76e -- custom_components dev/audit/harnesses/r10_buffer_store.py dev/audit/harnesses/r10_partload_pricing.py dev/audit/harnesses/r10_cop_partload.py dev/audit/harnesses/r10_setpoint_boost.py tests/profiles.py && echo MEASURED-INPUTS-IDENTICAL` prints `MEASURED-INPUTS-IDENTICAL`.
- This round's one commit, 306a0b76e, adds the harness's `refill` subcommand. Its two removed lines are the docstring's usage line and the `thermal_model` import; the `relaxed` and `buffer` bodies are untouched.
- Carry 2's figures (both harnesses) were re-taken at 306a0b76e.
- `origin/main` has since moved to 53273de4d449a990bc29734565f63babada9ff7f. `git merge-tree --write-tree origin/main 306a0b76e` reports no conflict, so by the owner's 2026-11-07 ruling no third merge is made; the merge train recarries the head.
- Carry 2's `refill` and `r10_partload_pricing.py` figures were re-derived a second time by the body re-take seat (at 306a0b76e and at merge base 4b5d771bd) and matched every printed digit; the zero-derate null read `null rows not zero 0` on both.

## Mutation proof

n/a: no production line is added or changed, so there is no fix line to delete. Each harness's refusal arm is exercised by its null control instead:
- `relaxed` exits 1 when an unclamped cell starts a relaxed run. It read 0 such cells.
- `refill` exits 1 when a `d=0` row's terminal or deferred error is not exactly 0. It read `null rows not zero 0`.

## Null control

- Carry 1: the flat price day, with no cheap window to store for. The 750 L store still costs 1.93x there, so its cost is per-solve model work, not arbitrage search. The no-buffer arm separates the price lever: 0.455 s flat against 0.522 s spread, p50.
- Carry 2: zero derate.
  - `r10_partload_pricing.py` prints `null rows not zero 0`. Its `lp_err`, terminal, deferred and baseline-change figures all read `0.000000` at `d=0.0`, on both price days and all 16 installs.
  - `r10_partload_residue.py refill` prints `terminal-at-P_r max 0.000000 deferred-at-P_r max 0.000000` on both `d=0.0` rows, then `null rows not zero 0`.
- Carry 3: the non-relaxed path, on the 32 unclamped cells. They show 0 relaxed runs and a maximum of 0.000 s inside the pass. The whole-solve delta between the production arm and the pass-removed arm ranges from -0.082 to +0.056 s there, which is the timing noise floor. The clamped cells' delta has a p50 of +0.150 s and a maximum of +0.667 s.

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

**Gate.** `bash tools/pr/prepr.sh` on 306a0b76e printed `gate mode MODE: SCOPED` and the result line `PRE-PR: 306a0b76e8bdd3e82e7370e3f1ad7bc08be832c1 ... rc=0`. `bash tools/pr/prepr.sh --body-check <this body> --pr-branch fix/r10-partload-residue` printed `PR-BODY: 0 error(s)` and `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`. On this head, prepr's merged `tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.

## Red checks

Every check run at PR head d5f8f410c, read with `filter=all` across both pages (156 runs at 2026-11-07 20:12 UTC, re-runs included; the in-progress re-runs are not concluded and not listed), with each concluded run not `success`, `skipped` or `neutral`:
- `gate`, check run 128454048061 (edit run 42388390774), failure. It was a deferral: `FAIL run(s) [42388250566] at this head are still being judged; their gate decides`. The code run's own `gate` (check run 128463363585) then concluded success at 16:43 UTC, and the edit run's `gate` re-ran as check run 128465293496, success at 16:53 UTC. Class: gate deferral, not a defect. Answer: no cheaper detector exists, because the deferral is the gate waiting on the run it defers to. None.
- `gate`, check run 128453123588 (edit run 42388250955), cancelled at 16:06 UTC. Class: superseded gate run, not a defect; run 42388250955's `gate` is re-running as check run 128513716807 (in progress at the read). Answer: none owed; a cancellation carries no verdict on this diff, and the code run's `gate` (128463363585) concluded success.
- `tests / nightly-status`, check run 128451039899, failure. It grades `main`, and this diff touches none of what it reads (its scripts, the workflows, the plan, `HANDOVER.md` or a delivery row). By `defect-root-cause.md` it is the orchestrator's on `main`. None owed here.
- `governance / instrument-self-tests`, check run 128451039876, cancelled after 30 min 14 s (15:53:40 to 16:23:54 UTC). It is a cancellation, not a failure, and the gate that judged its run concluded success afterwards. This diff changes nothing under `tools/`. The cause was not established in this seat. Named here; this head re-runs it.

Each is a red at d5f8f410c. The new head 306a0b76e has not run CI yet, so the reviewer reads its own checks.

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
