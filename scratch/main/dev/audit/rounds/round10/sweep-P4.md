# Round 10 class sweep: P4 (the optimizer's seed set or stop tolerance does not bracket the optimum)

Baseline: `handoff/audit-r10-register` at 9355f107d, which carries production at 17f1c55fad1b. Machine: macOS arm64 with venv-ci. Ledger status of P4 in `dev/audit/config/bugclasses.json`: `detector`. The detector is `tests/optimality.py`'s solve certificate (#1409). The ledger records the barrier as refused on numbers (RCA-BULK-1, #1293/#1294).

Findings in the class: D0-s1-01 (seeds, space-only path), D0-s2-01 (ftol 1e-6 stop, two-zone+DHW).

## Enumerator (D14 method step 3)

`python3 dev/audit/rounds/round10/D14/sweep-P4/p4_seams.py [--null] [--perturb]` is a static AST scan of every `*.py` in the package. It lists two kinds of seam:
- **STOP**: every call to a scipy.optimize entry or to `_scoped_minimize`, with its literal tolerance.
- **SEED**: every assignment, append or concat to `starts` in a function that calls `_multi_start_minimize`.

It started from the two `seam_rule`s and widened them: s2's grep for `"ftol": 1e-6` became every optimizer call site, and s1's capture at `_multi_start_minimize` became every caller's seed list.

| control | result |
|---|---|
| positive (re-finds both findings) | `D0-s2-01 main` (`_multi_start_minimize` ftol 1e-6), `D0-s2-01 restart` (`_lbfgsb_restart` ftol 1e-6) and `D0-s1-01 seeds` all True |
| null (clean closed-form fixture) | `null_seams=0` (`p4_seams_null.out`) |
| perturbation (one appended `minimize(..., options={"ftol": 1e-6})`) | STOP 6 -> 7, delta 1 (`p4_seams.out`) |

Output: 14 seams (6 STOP, 8 SEED lines). Grouped by symbol, that is 7 seam units.

## Disposition (method step 4)

| seam | disposition | evidence |
|---|---|---|
| `optimizer.py:_multi_start_minimize` L827, ftol 1e-6 | **instance** (judged site, D0-s2-01) | `D0/s2/ftol_race.py`: winter mean 0.2025 %; `--ftol 1e-10` gives 0.0088 % |
| `optimizer.py:_lbfgsb_restart` L678, ftol 1e-6 | **instance** (judged site, named in the D0-s2-01 mechanism) | same probe; the perturbation overrides it |
| `optimizer.py:_optimize_space_only` seeds L4279-4333 | **instance** (judged site, D0-s1-01) | `D0/s1/race.py`: 26/80 cells over 1e-3. The certificate covers 5 of these cells, with claims (partly guarded) |
| `optimizer.py:_solve_space` seeds L3721-3732 (DHW path) | **instance, beyond finding** | see below |
| `optimizer.py:_optimize_space_only.move_starts` L4320, ftol 1e-6 | not applicable | It only moves the first start. Its output is re-refined by the L827 run and raced against every other start, so its stop does not decide the plan |
| `optimizer.py:_scoped_minimize` L375/L377 | not applicable | Thread-scope wrapper. It passes the caller's options and has no tolerance or seeds of its own |
| `dhw_planner.py:_plan_dhw_min_cost` L1491 `linprog(method="highs")` | not applicable | An LP solved to its global optimum. It has no seeds and no basin, and a failure falls back to greedy |

### The new instance: DHW-path seed set (`_solve_space`)

D0-s1-01 measured only DHW off (`race.py --dhw` default 0). Its proposed fix scope names the DHW path too, but nothing measured it. The certificate's cells are all space-only (`_cert_inputs`), so nothing guards this path.

`race.py --dhw 1` crashes at baseline on a stale keyword (`dhw_tank_temperature`; the field is `dhw_temperature`). That makes it a harness that does not run, so its DHW arm has never produced a number. `D14/sweep-P4/race_dhw.py` is the same harness with that one keyword fixed.

`race_dhw.py --dhw 1` over 4 prices x 2 weathers x tz 0/1 (`race_dhw1.out`) gave:
- 6/17 cells with gap_rel over 1e-3 and 1 over 1e-2.
- The largest gaps were tz1 winter_moderate/winter_cold at 1.065e-2 (c1 6.90e-3) and tz1 winter_narrow/winter_cold at 8.58e-3 (c1 7.88e-3).
- c1 is the same minimizer at the same ftol with structured seeds added, so this gap is caused by the seeds and not by the stop.
- Null: flat max 3.86e-3. As in D0-s1-01, the gap survives flat prices: it is a basin/seeding gap, not a missed arbitrage.

These DHW cells overlap D0-s2-01's cells, but the cause is a different seam: the stop tolerance is held constant here.

## Count and barrier

The sweep found 4 instances: 3 are judged sites and 1 is beyond the findings. It found no guarded seams. The certificate partly covers `_optimize_space_only`, but only as a claimed detector, not a barrier. There are 3 not-applicable seams.

The ledger's barrier refusal (RCA-BULK-1) still stands. The countermeasure this sweep supports is a detector fix: extend `_CERT_CELLS` with DHW-on cells, so that the certificate reaches `_solve_space`. That change belongs in the D0/D14 stage brief and is not filed as an issue.
