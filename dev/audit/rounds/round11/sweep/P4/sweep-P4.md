# Round 11 class sweep: P4

Class P4 in `dev/audit/config/bugclasses.json` is "the optimizer seed set or
stop tolerance does not bracket the optimum". Its status is `detector`: the
class detector is `tests/optimality.py`, the solve certificate. RCA-BULK-1
refused a class-eliminating barrier on numbers: a tighter ftol cost 6.4 % money
on one backtest cell at 2.4x CPU. `barriered` is therefore `false`.

Two round-11 survivors:

| finding | shape | site |
|---|---|---|
| D0-s2-01 (weakened, low) | A charged wood tank sets `_wood_covered_share` to 1.0, so the seed power, the baseline energy and every price-ranked start built from them are all-zero. The space-only multi-start collapses to one live start. | `HeatPumpOptimizer._optimize_space_only` |
| D0-s3-02 (verified, low) | No production start set holds the lower bound (all-off). At negative prices a storage plant ships plans that its own objective scores worse than a descent from off. | `_optimize_space_only` and `HeatPumpOptimizer._solve_space` (the start set it hands `_relaxed_plans`) |

Measured at `handoff/audit-r11-register` @ 28b864af6, detached worktree, venv-ci
Python 3.14.7, Linux x86_64, `OPENBLAS_CORETYPE=Haswell`, BLAS threads pinned to
1. All the figures are counts or objective values, so CPU is not used.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P4/enumerate.py [--null | --perturb] [--json PATH]`

The enumerator widens two seam rules: D0-s3-02's
`grep 'starts = \[|starts.append|extra_starts'` and D0-s2-01's
`wood_seeds.py --census`. It has three arms:

| arm | seam rule | listed |
|---|---|---|
| S (static, AST) | every call in the package to a numerical optimizer or its wrappers (`_multi_start_minimize`, `_lbfgsb_run`, `_lbfgsb_restart`, `_scoped_minimize`, `minimize`, `linprog`, ...), with its enclosing function | 13 |
| Z (runtime) | a production `_multi_start_minimize` call site whose start set holds no lower-bound vector on some cell | 3 |
| C (runtime) | a call site where two or more starts coincide after clipping to the bounds on some cell | 1 |

The runtime arms wrap `_multi_start_minimize` and key each call on its
production caller (function:line). They run over 12 cells, using D0-s3's
builders (`d0s3_lib.build`) and D0-s2's own wood plant (`cells.cell_record`):
- space-only and hot-water cells;
- plain, valve-storage and wood plants;
- two cells with a learned stop and a start price
  (`duty_switch_stop_probability=(0.5, 0.5)`, `cycling_cost=0.5`), so that
  `_relaxed_plans`' free-room re-run executes.

`RESULT tree S=13 sites_runtime=3 Z=3 C=1 C_cells=1`:

```
ZC  optimizer.py:_optimize_space_only:5566 calls=5 starts=[4, 5] Z_cells=4 C_cells=1 max_dup=3
      C s2:winter_narrow/summer_cool/two-zone/no-dhw/wood/24h
Z   optimizer.py:_relaxed_plans:245 calls=8 starts=[1, 4] Z_cells=7 C_cells=0 max_dup=0
Z   optimizer.py:_relaxed_plans:251 calls=3 starts=[1, 4] Z_cells=2 C_cells=0 max_dup=0
```

**Positive control.**
- C flags `_optimize_space_only` on D0-s2-01's race cell
  `winter_narrow/summer_cool/two-zone/no-dhw/wood/24h`, where 3 of 4 starts
  coincide (the all-zero starts).
- Z flags both D0-s3-02 sites: `_optimize_space_only:5566`, and
  `_relaxed_plans:245`, which receives `_solve_space`'s start set.

**Null control.** `--null` replays the same calls, each with a bracketing start
set: the lower bound added and coincident starts dropped. It prints
`RESULT null ... Z=0 C=0 C_cells=0` and exits 0.

**Perturbation.** `--perturb` makes one one-line re-introduction in memory:
`optimizer._LOW_ENERGY_START_FRACTION = 1.0`. This is the R1-D0-01 shape: the
low-energy anchor collapses onto the full-energy price-ranked start. It prints
`RESULT perturb ... Z=3 C=3 C_cells=14`, so C moves from 1 site and 1 cell to
3 sites and 14 cells.

A note on the harness: a wrapper must not pass `move_starts=None` to
`_multi_start_minimize`. The function calls it unconditionally, so `None`
raises, and production then falls back to another solve. A first draft of this
enumerator made that mistake and reported spurious collapses on the hot-water
path. Both scripts now forward the argument only when it is set.

## Disposition of every seam

**Instances at judged sites** (`beyond_finding: false`):

| seam | probe |
|---|---|
| `HeatPumpOptimizer._optimize_space_only` (the start list near optimizer.py:5511, call :5566) | D0-s2-01: `dev/audit/rounds/round11/D0/s2/wood_seeds.py --census` / `--race ...` (race gap max 2.0292; `WOOD_SHARE_OFF=1` -> 0); D0-s3-02: `dev/audit/rounds/round11/D0/s3/offstart.py --workers 1` (16/60 gap cells, max 3204.33; `--perturb off_in_prod` -> 2) |
| `HeatPumpOptimizer._solve_space` (the start list near :4950, consumed at `_relaxed_plans:245`) | D0-s3-02, the same `offstart.py`. This sweep also measured it: `probe_offstart_sites.py --limit 6` gives `_relaxed_plans:245 gap_calls=12/14 max_gap=3204.3613`. On a warm-started re-solve (`_optimize_with_dhw`'s `solve_space(dhw_plan, warm_start)`) the set is the guess alone (`starts=[1]` above), because the structural starts are added only when `warm_start is None`. That is the same site and the same missing bracket. |

**Instance beyond the findings** (`beyond_finding: true`, 1):

| seam | what happens | probe |
|---|---|---|
| `_relaxed_plans`, the free-room re-run (optimizer.py:251) | Where a switch has a price (a learned stop and `cycling_cost > 0`), `_relaxed_plans` runs a second `_multi_start_minimize`. Its start set is the first set clipped to `free_room`, so it inherits the missing lower bound. Neither finding names this call, and it builds its own start set. | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P4/probe_offstart_sites.py --limit 6` exits 1: `_relaxed_plans:251 calls=14 gap_calls=12 max_gap=3204.3567` (summer_negative/summer_warm/single-zone/dhw/manual-valve-buffer/48h). `--null --limit 6` (flat twins) gives 0 gap calls and exits 0. |

The gap is measured on the call's own descent objective, against production's
multi-start from the lower bound alone. Whether a gap ships depends on
`_commit_runs` judging this plan against the first call's plan on the true
objective, and that was not measured; see "Not done".

**Guarded:**

| seam | guard |
|---|---|
| S `_lbfgsb_run` (`ftol 1e-6`, `eps 1e-4`, optimizer.py:1700) -> `_scoped_minimize` -> `minimize` (:1488, :1490, :1698) | The stop tolerance. `tests/optimality.py`, the class detector, re-polishes `_CERT_CELLS` at `ftol 1e-8` and certifies no unclaimed gap above the bar. RCA-BULK-1 recorded the refusal of a tighter ftol. |
| S `_lbfgsb_restart` (:1862, called :638 and :1990) | Restarts from its own returned point, with no new seed (#826). It adopts the restart only on a real relative drop. |

**Not applicable:**

| seam | reason |
|---|---|
| S `_multi_start_minimize` -> `_lbfgsb_run` (:1966) | The engine runs whatever start set its callers hand it. The disposition sits at each caller (above). |
| S `_resolved_runs` -> `_lbfgsb_run` (:635) | One local run per plan the multi-start already produced, inside that plan's run bounds. It polishes outputs and owns no start set. |
| S `_optimize_space_only.move_starts` -> `_lbfgsb_run` (:5554) | The R9-F2.1 continuation. It moves the first start under the call's own budget and is not a seed set. |
| S `dhw_planner.DhwPlanner._plan_dhw_min_cost` -> `linprog` (:1601, HiGHS) | A linear program solved to global optimality has no seed set and no basin. A failed solve falls back to the greedy planner. |

## Barrier proposal

The class status stays `detector`: the ftol refusal stands. The start-set half
of the class has a cheap barrier. Every production `_multi_start_minimize`
call gets a start set that holds the lower-bound vector and holds no
coincident starts. Put this in one place, inside `_multi_start_minimize`
itself, so that no caller can drop it:
- prepend `lo` (from `bounds`);
- drop starts that coincide after clipping.

D0-s3-02's own `--perturb off_in_prod` already measures the effect: 16 -> 2 gap
cells. A permanent check reruns this enumerator's Z and C arms as a
`tests/optimality.py` block, on the 12 cells here, and expects zero in each.
Its cost is about 15 s of gate CPU, which is the price of the runtime arms. A
static AST check alone cannot see D0-s2-01's collapse, because those starts
coincide only at run time.

The cost of an extra start per call was not measured here. RCA-BULK-1's CPU bar
applies.

## Not done

- These files are untracked. A committer must classify `D14/sweep-P4/`
  (`enumerate.py`, `probe_offstart_sites.py`, `seams.json`), or
  `tests/entities.py` fails.
- `probe_offstart_sites.py` ran on the first 6 of its 30 cells (`--limit 6`,
  about 43 s); the full run was not taken.
- The free-room gap is a descent-objective gap. Whether `_commit_runs` ships
  the worse free-room plan was not measured. D0-s3-02's committed-plan metric
  (`offstart.py`) is the next measurement, run on priced-stop cells.
