Design review: approve 55f90c7c63ae3f1609e6032959871e5ccbd867fe

Reviewed from a detached worktree at 55f90c7c6, the built head from one at 273079db5, against base ee64358be. Nothing was rerun: every figure quoted is the note's. The built merge base 8f97247fc is an ancestor of ee64358be; `git diff --stat 8f97247fc ee64358be` over coordinator.py, optimizer.py, price_tiles.py, const.py, thermal_model.py and tests/closure.py shows optimizer.py and price_tiles.py unchanged and coordinator.py moved only by #3225's combi store (`tank_levels`, `combi_tank_seed`), outside `async_simulate` (carried, item main-drift). The fixer does not start on the schedule branch before the owner answers item brief-departure below.

## Every harness finding of both verdicts: met or not met
| finding | verdict | measurement | null control | perturbation |
|---|---|---|---|---|
| 6cd70cf27 (i): the two energies over two windows | met | carrier harness at `AGE=1 STEP=4` and `AGE=2 STEP=4` on `_solve_coord`, 12 hours: schedule figures against the ask, 0 of 96 (design.md section 1 row 4, section 3 row 1) | the same at `AGE=0`, 0 of 96; `STEP=0` at AGE 2, 0 of 96 | M1, live energy read off the scheduled result: 24 of 96 at AGE 1 and 2, 0 at AGE 0 (row 2) |
| 6cd70cf27 (ii): branch chosen by float equality | met | the branch is the two target lists compared element by element (section 2); targets equal and difference exactly 0.0 on 108 of 108 no-schedule asks over AGE 0, 1, 2 | schedule asks: solve count 1 on 96 of 96 | M1: 0 of 36 at AGE 1, 2; M2, energy inequality with M1: the zero ask reads off 0 at AGE 1 |
| 6cd70cf27 (iii): age rows on a two-day outdoor series | met | check (a) and the carrier over AGE 0, 1, 2 x STEP 0, 4: zero ask 0.0 on 12 of 12 per cell, cap and hot-water ask on the pair (3 then 2), each panel ask on its side of 0 | cap figure none below -1 | M3, the passes on the horizon's own weather: 3 of 96 at STEP 4, 0 of 96 at STEP 0 |
| 6cd70cf27 (iv): the mutant | met | M1 | green at AGE 0 | red on (a) at AGE 1, 2 |
| 05e5b517b point 1: the panel's own asks | met | the six panel asks x 12 hours x AGE 0, 1, 2: 0 of 72 per age | the two tile asks, 0 of 24 | M4, energy priced at its own hours: 42 of 72 |
| 05e5b517b point 1: the zero-ask null and the bound | met | `panel_zero` exactly 0.0, 12 of 12 per cell, by identical inputs | - | the 0.05 K bound and its ratio are gone, so no threshold is left to size |
| 05e5b517b point 2: a small schedule ask on the rejected estimator | met | (a2), `comfort_temp_day` + 0.01: solve count 1, figure above 0 | an ask moving no target reads the pair | M5, branch on a target difference over 0.05 only: (a2) red |

Two of these rest on the tree, checked here at 273079db5. The shared instant is buildable as written: `_whatif_solve` (coordinator.py:11271-11352) returns an unsolved `HeatPumpOptimizer` with its `SolveInputs` and solves nothing, and both paths of `async_simulate` take `horizon` and `solve_at` from one `now` (:11167, :11180, :11190), so the user path and the background path each give both sides one set of arrays. The target comparison cannot be moved by a no-schedule ask: `_build_comfort_bounds` (optimizer.py:4127-4145) reads the comfort levels, the day window and the holiday and weekend fields through `_comfort_pair` (:2231-2257) and no cap, hot-water, quiet-window or wood field.

## The open question the designer raised (quoted, not a defect)
"Finding (iii) asks each panel ask on its side of 0 on an outdoor series that differs between the days. That is met only by the mean-weather passes, which make the figure blind to within-day weather by construction; a check that the figure is also *right in size* on a real diurnal forecast has no reference to compare against (the plan's and the thermostat's own-hour costs are both measured unsafe in sign). The note asserts sign and start-invariance, not magnitude."
- decision: orchestrator. Rule whether sign and start-invariance are enough for #2257 or a magnitude reference is owed and by whom. This seat names none either: finding (iii) asked for sign, and M3 with its STEP 0 null is what separates the mean-weather passes from fix (i) alone.

## Routed decisions (no revise)
- decision: owner. Item brief-departure, as both the note and 6cd70cf27 route it, now wider: a schedule ask's figure is a thermostat's day energy at the day's mean weather and mean price, so it no longer moves with within-day weather or price timing. Row 3 (3 of 96 against the ask at every age with the horizon's own weather) is the evidence that the mean moves with the sign.
- decision: orchestrator. Item mixed-ask, unchanged: a comfort ask sent with a hot-water, quiet-window or cap change has unequal targets, takes the schedule branch and prices its heating energy alone.

## Checked, no revise
- Seam (step 1): `async_simulate` owns the answer, price_tiles.py the arithmetic, optimizer.py the reference beside `_compute_baseline_power` (:5612-5690), whose only config read is `target_temp` (:5662). `OptimizationResult` gains nothing, so no new write path and no golden moves.
- Shape (step 2): every changed behaviour is #2257's sign or moves with it; the cap tile, the fuse advisor and the three other monthly keys keep their built arithmetic (price_tiles.py:110-119).
- Sibling sites (step 3): `_compute_baseline_power` has two callers (optimizer.py:4923, :5296), both untouched by an optional argument; the steady key's readers and `async_simulate`'s callers are as 6cd70cf27 found them.
- Evidence (step 4): check (a) is red at 273079db5 (the key comes from the pair on every ask, count 3 on schedule asks) and on main, where the key is absent.
- Consistency (step 5): of the 31 other open design refs, the retired R10-ADVISOR-WHATIF (349475976) and R10-COMBI-TANK-PR-B (079d303b0) are the only ones naming `async_simulate`, `price_tiles`, `_whatif_solve`, `_baseline_targets` or `_compute_baseline_power`; neither claims this seam.
- Cost (step 6): one method, one optional argument, one pure function, one branch, one harness file. Fits L.

## Notes for the fixer (carries, not revise points)
Carry: R10-ADVISOR-STEADY-START (item hotwater-fixture) - `_solve_coord` has no hot-water tank (tests/features.py:30674-30691 sets no dhw key), so check (a)'s hot-water ask runs the space-only path and its +0.0 is a house without one; this answers item pair-other-asks. Add the hot-water ask on a tank fixture: on the pair, count 2, and state its figure.
Carry: R10-ADVISOR-STEADY-START (item target-only) - `_build_comfort_bounds` never reads `target_temp`, and `_baseline_targets` (optimizer.py:373-382) uses it only where the schedule does not reach. Pin with a check what an ask moving `target_temp` alone shows, and which panel key moves the targets.
Carry: R10-ADVISOR-STEADY-START (item optimize-prelude) - the weather and the targets are built inline in `optimize` (optimizer.py:3807-3817) from step hours and datetimes it derives itself; item horizon-builder therefore needs that prelude callable without a solve. Pay it inside the structural ratchet; this verdict approves no budget raise.
Carry: R10-ADVISOR-STEADY-START (item main-drift) - main gained #3225's combi store in coordinator.py since 8f97247fc; rerun the carrier after the rebase, and add a combi fixture to item measured-fields.
Carry: R10-ADVISOR-STEADY-START (item m2-row) - M2's zero-ask range is quoted in section 3 only; print it from the carrier as a RESULT line before the body quotes it.
The note's own carries stand as written, with its three dismissals (result-overlap, both-paths, energy-tie) accepted: no result field is added, and the tie is decided in section 2 with check (a3).

Seat tokens: not reported by the harness for the seat; its one locator subagent reported 63170.
