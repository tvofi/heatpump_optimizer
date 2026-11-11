# D0 round 8, seat s1: seeding, multi-start and solver budget

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`, tree `/home/claude/audit-r8/seats/D0-s1` (a git worktree).
Machine: 4-vCPU cloud container. load1 was 11 to 23 throughout the fan-out. No timing number is used anywhere.
The evidence is objective ratios and counts, and function-evaluation counts stand in for cost.
thread_factor was 1.000 on every run.

## Method

- **Capture.** I used `mock.patch.object(optimizer, "_multi_start_minimize" | "_scoped_minimize", ...)`.
  Every call hands over its objective, candidates, bounds, args, `maxiter` and batch objective. Every L-BFGS-B run returns its `nit`, `nfev` and `message`.
- **Challengers.** These were raced on the exact captured objective, using production's own jac path (`_batch_fd_gradient` through the `batch_objective` kwarg):
  - each candidate refined alone;
  - ten extra structural seeds;
  - a stopping budget of maxiter ×10 or 20000, ftol 1e-12 or 1e-13, gtol 1e-10 and maxfun 1e6;
  - fd_eps of 1e-6 and 1e-3;
  - a derivative-free coordinate search alternated with the production polish.
- **Feasibility parity.** The best challenger is injected back into `optimize` end to end. It counts only if room degree-steps below 17 °C are no worse and the DHW schedule is identical.
- **Grid.** 8 price × 5 weather profiles. The runs covered single-zone with DHW off, single-zone with DHW on, and two-zone with DHW off. The flat price profile is the null control inside every grid.

## Finding

### D0-s1-01 (low, bug): ftol=1e-6 is the binding stop and leaves descent unused

Both option dicts, in `_multi_start_minimize` and `_lbfgsb_restart`, pass `ftol: 1e-6`. Neither sets `gtol` or `maxfun`.

On the two-zone grid, 219 of 320 production runs stop on "RELATIVE REDUCTION OF F". None stops on maxiter.

Re-running the same `optimize` with ftol set to 1e-12 at the `_scoped_minimize` seam gives these reductions in shipped `objective_value`:

| grid | cells >0.1 % | mean | mean with best cell dropped | max | flat mean | nfev ×, median |
|---|---|---|---|---|---|---|
| two-zone, DHW off | 15/40 | 1.12e-3 | 8.70e-4 | 1.11e-2 | 7.29e-4 | 1.82 |
| single-zone, DHW on | 12/40 | 1.67e-3 | 9.79e-4 | 2.88e-2 | 1.57e-3 | 1.59 |
| single-zone, DHW off | 8/40 | 3.60e-3 | 1.75e-3 | 7.59e-2 | 2.41e-4 | 1.63 |

- **Null control.** The gap survives flat prices, and the largest absolute gap (0.39 objective units) is `flat|winter_cold`. So this is not price optimality. It is a convergence-tolerance gap on the whole objective, and energy cost moves in either direction.
- **Size.** The largest relative gaps fall on summer days with small objectives (J < 1). Winter-day gaps are 0.2–0.4 % of the objective. That is why the severity is low.
- **Step 0 changes.** The first step of the plan changes in 4 of the 5 perturbed cells, so re-planning at the next MPC step would not simply undo the difference.
- **Perturbation.** `s1_budget_perturb.sh` edits both literals to 1e-12 and restores the file with `git checkout` in an EXIT trap. The result on the five cells:
  - production J fell by exactly the ftol-arm gap in every cell, for example 77.884228 → 77.699680;
  - the ftol gap went to 0;
  - ftol stops fell from 37/40 to 11/40.

## Non-findings

All numbers are in `report-s1.json`.

- **Nothing is discarded before refinement.** Four candidates give 8 L-BFGS-B runs per call, which is refine plus polish for each one.
- **maxiter is never binding.** 0 of 970 runs stopped on it, and the highest `nit` seen was 33.
- **gtol is not binding.** Tightening it changes the result by at most 4e-15.
- **Extra seeds.** They beat production by more than 0.1 % in 9 of 40 cells. With the best cell dropped the mean gap is 1.2e-3. The largest cell is a J=0.31 summer day, and flat cells move just as much. I read this as basin selection on the comfort and cycling terms, not on price.
- **Warm-start seed (#1295).** `coordinator._warm_seeded` hands the previous plan over unshifted, so at the 30-minute default it is misaligned by 2 steps (32 of 40 cells). Aligning it moves the result with mixed sign: 8 cells better, 5 worse, and a mean of 1.3e-4 with the best cell dropped. The effect survives the flat control. I have recorded the mechanism for the MPC seat (s2).
- **fd_eps.** Changing it moves the result with mixed sign and by at most 3.7e-3.
- **Cold bang-bang days.** These are already at KKT vertices: PGTOL in 2–5 iterations, and no challenger finds anything.

## Harnesses

Each harness carries its command, metric and count key in its header.

- `s1_race.py`: capture and the challenger race.
- `s1_budget.py`: the stopping-option arms, scored end to end.
- `s1_budget_perturb.sh`: the production-edit perturbation, with automatic restore.
- `s1_warm.py`: the alignment of the warm-start candidate.

Raw logs are in `s1_logs/`.

## Unfinished

- **The full 4-arm race** was cut short by the box load. It covers 8 of 40 single-zone cells with DHW off, 6 of 40 with DHW on, and 2 of 40 two-zone. The partial logs are `s1_logs/g_*.log`. Two-zone cell 1 showed a 0.62 % gap in the combined budget arm.
- **Never raced:**
  - the second co-optimisation space solve, which refines only the warm start and extra starts, raced against the structural seeds;
  - a DE or DP outer bound;
  - valve, wood and 6 h / 48 h variants.
- **Schema conflict.** The id `D0-s1-01` fails `finding.schema.json`'s id pattern (`^D[0-9]+-[0-9]{2}$`). I followed the task's naming. It is the only validation error.

## Exposure

None.
