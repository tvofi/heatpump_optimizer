R10-PARTLOAD-RESIDUE: the three measure-first items #3182 left. Each was measured at this group's merge base. Each comes out immaterial or reserved to a later stage, so **no production line changes**. The diff lands the harness that re-derives the two CPU figures (`dev/audit/harnesses/r10_partload_residue.py`) and its `INERT` classification. The linear-valuation figures come from `r10_partload_pricing.py`, which is already in the tree. Every carry is answered below with its number. Carries are numbered 1 to 3 in roster order, so the brief's carry 0, 1 and 2 are carries 1, 2 and 3 here.

- **Carry 1, the live buffer store's CPU.** A 750 L store costs about 1.9x per solve. Measured one lever at a time: 1.87x on the seeded spread days and 1.93x on the flat null. The price day alone costs 1.15x. The worst solve is 1.83 s here, about 12 s scaled to Pi class, which is 2 % of the shortest optimisation interval the options flow accepts (10 min). The 272 s owner-box outlier did not reproduce in 80 seeded solves, and no harness in the tree re-derives it. **Refused:** no bound or warm start is earned at these numbers.
- **Carry 2, linear valuations under a convex cost.** The hot-water LP's secant error is at most 0.27 currency/day against a hot-water cost of about 7 to 8 per day (3.8 %). The terminal and deferred figures state no refill rate, so their error lies between 0 (refilled at the floor) and 4.37 / 2.14 (refilled at maximum power). The zero-derate null reads exactly 0 on every row. The carry reserves the segmenting decision to a later D0 pass on `_plan_dhw_min_cost` and `_terminal_cost`. That ruling is not this group's, and this body waits on it: nothing is segmented. The numbers are re-derivable for that pass by `dev/audit/harnesses/r10_partload_pricing.py`, already in the tree.
- **Carry 3, Pi CPU of the relaxed start.** The worst clamped solve is 1.96 s and the relaxed pass inside it at most 0.32 s. At the derived Pi-class factor of 6.8x that is about 13.3 s and 2.2 s, against the 600 s budget. The null control holds: the unclamped cells start 0 relaxed runs and spend 0.000 s in the pass. **Refused:** a `maxiter` cap on the relaxed pass is not earned. It would become due only if a clamped solve ran 306x slower than here.

## Head

219c27b5d6c404b833cc1cfbe34cf03e2292bb7b.

The figures were taken at 67cc12cc52afaf347534fa2859a4d6d329ea5690, on merge base b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab. That head adds only the harness and its `tests/closures.json` entry; no production file differs from the base: `git diff --quiet b4ec2f332 67cc12cc5 -- custom_components && echo PRODUCTION-IDENTICAL` prints `PRODUCTION-IDENTICAL`.

`origin/main` then moved to 1c1ae100b59e29564c7aec069b257dface6ef50f (2026-11-07 UTC, delivery-record commits only) and was merged in. The merge's delta reaches nothing the figures read: `git diff --quiet b4ec2f332 219c27b5d -- custom_components dev/audit/harnesses/r10_buffer_store.py dev/audit/harnesses/r10_partload_pricing.py dev/audit/harnesses/r10_cop_partload.py dev/audit/harnesses/r10_setpoint_boost.py tests/profiles.py && echo MEASURED-INPUTS-IDENTICAL` prints `MEASURED-INPUTS-IDENTICAL`. So the figures stand at this head, and `tools/pr/prepr.sh` was rerun after the merge.

## Mutation proof

n/a: no production line is added or changed. There is no fix line to delete. Each carry is a measure-first item whose measurement came out immaterial, or reserved to a later stage's ruling. The harness's own refusal arm is exercised by its null control instead: `relaxed` exits 1 when an unclamped cell starts a relaxed run, and it read 0 such cells.

## Null control

- Carry 1: the flat price day, with no cheap window to store for. The 750 L store still costs 1.93x there, so the store's cost is per-solve model work, not arbitrage search. The no-buffer arm separates the price lever: 0.455 s flat against 0.522 s spread, p50.
- Carry 2: zero derate. `r10_partload_pricing.py` prints `null rows not zero 0`, and `lp_err`, terminal, deferred and baseline change all read `0.000000` at `d=0.0`, on both price days and all 16 installs.
- Carry 3: the non-relaxed path, on the 32 unclamped cells. They show 0 relaxed runs and a maximum of 0.000 s inside the pass. The whole-solve delta between the production arm and the pass-removed arm ranges from -0.082 to +0.056 s there; that is the timing noise floor. The clamped cells' delta has a p50 of +0.150 s and a maximum of +0.667 s.

## Figures

All times are `time.process_time` of one process pinned to one core (`taskset -c N`) with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`. Host: x86_64, `Intel(R) Xeon(R) Processor @ 2.30GHz`, family 6, model 173 (Granite Rapids class), Python 3.14.7, numpy 2.5.4, scipy 1.18.1. The budget is `config_flow`'s `CONF_OPTIMIZATION_INTERVAL` slider minimum, 10 min = 600 s; the default interval is 30 min.

- Carry 3, relaxed pass. Command: `PYTHONPATH=tests/hastub:custom_components:tests taskset -c 0 python3 dev/audit/harnesses/r10_partload_residue.py relaxed`. It prints `clamped solves 32: solve_s p50 0.466 max 1.961; relaxed_pass_s p50 0.105 max 0.318; worst solve share of budget 0.00327` and `null (unclamped) cells with a relaxed run 0`, exit 0.
  - Rule: 16 installs (`r10_setpoint_boost.CELLS`) x 2 price days x 2 derates (0 and the central plant's 0.112), timing only the cells whose levels ship clamped.
  - The per-cell delta figures (p50 +0.150 s, maximum +0.667 s clamped; -0.082 to +0.056 s unclamped) are the median, minimum and maximum of the `delta_s` field over the printed per-cell lines, grouped by `clamped`.
- Carry 1, buffer store. Command: `PYTHONPATH=tests/hastub:custom_components:tests taskset -c 1 python3 dev/audit/harnesses/r10_partload_residue.py buffer 20`. Over 20 seeded solves per arm (seed 2500, `r10_buffer_store.solve`'s owner shape) it prints:

  | arm | p50 (s) | max (s) |
  |---|---|---|
  | 750 L spread | 0.975 | 1.828 |
  | 750 L flat | 0.876 | 1.207 |
  | 0 L spread | 0.522 | 0.949 |
  | 0 L flat | 0.455 | 0.720 |

  The ratios are p50 over p50 within a price day: 0.975/0.522 = 1.87x, 0.876/0.455 = 1.93x, and 0.522/0.455 = 1.15x for the price lever.
- Carry 2, linear valuations. Command: `PYTHONPATH=tests/hastub:custom_components:tests taskset -c 2 python3 dev/audit/harnesses/r10_partload_pricing.py`. It prints:
  - `spread d=0.112: cells 16 lp_err max 0.173106 (dhw cost max 8.0681) terminal-at-max max 3.723135 deferred-at-max max 0.963508`
  - `flat d=0.112: cells 16 lp_err max 0.267290 (dhw cost max 7.0145) terminal-at-max max 4.368455 deferred-at-max max 2.139841`
  - both `d=0.0` rows at `0.000000`, then `null rows not zero 0`, `failures 0`, exit 0.

  The 3.8 % share is 0.267290 / 7.0145.
- Pi-class factor: 6.8x. This is the ratio of Geekbench 6 single-core scores.
  - Granite Rapids/Emerald Rapids GCP C4 vCPU: 1818 to 2319 across the published C4 results. Sources: <https://sparecores.com/server/gcp/c4-highcpu-2> (2292), <https://sparecores.com/server/gcp/c4-highcpu-4> (2319) and <https://browser.geekbench.com/v6/cpu/baseline/6766010> (1818).
  - Raspberry Pi 4 (Cortex-A72 at 1.5 GHz): 340. Source: Raspberry Pi's own Geekbench 6.2 figure, <https://www.raspberrypi.com/news/benchmarking-raspberry-pi-5/>.
  - 2319/340 = 6.8 is the upper end of 1818/340 = 5.3 to 6.8, so the scaled figures are taken at the slow end.
  - Pi-class figures: 1.961 x 6.8 = 13.3 s, 0.318 x 6.8 = 2.2 s and 1.828 x 6.8 = 12.4 s.
  - The breach factor is 600 / 1.961 = 306.
- Gate: `python3 tests/closure.py select --diff b4ec2f332 --workdir $D` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `PYTHONPATH=tests/hastub python3 tests/entities.py`, `tests/entities.py` (`ALL 2645 ENTITY CHECKS PASSED`), `tests/env_drift.py --claims-only origin/main` (`claims hygiene: origin/main ok`), `tests/closure.py selftest` (`ALL 118 closure shrink pins PASSED`), `tests/layout.py` (`layout self-test: ok`), `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`) and `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`) were run on this head.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` wrote the harness's `INERT READS` entry, then printed `CI PREDICT: no closures, fast, governance or instrument red predicted against b4ec2f332fe3`.

## Red checks

none

## Forward-carry

none

## Friction

- fixer-pi-measurement: cost: the brief prefers GitHub's ubuntu-24.04-arm runner or an arm64 container under a CPU quota; this seat has neither (x86_64 container, no runner dispatch from a fixer's return refs), so the Pi-class figure is an x86_64 single-core process_time scaled by a cited Geekbench 6 single-core ratio. The verdict holds under any factor below 306x. Carry: dismissed: verdict robust below a 306x factor
