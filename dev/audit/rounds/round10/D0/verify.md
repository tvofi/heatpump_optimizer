# D0 verifier, round 10

Worktree detached at handoff/audit-r10-register 9355f107d (the branch itself was already checked out in
r10-repo); production code at baseline 17f1c55fad1b. venv-ci python, PYTHONPATH=tests/hastub, Apple Silicon
macOS. All numbers are objective ratios or counts, so contention does not affect them; load1 8.9-30.9 and
thread_factor 1.000 on every run.
My own harnesses: `verify_s1_random.py` and `verify_s2_shipped.py`, both in this directory.

## D0-s1-01: vote weaken, severity low, class P4 (not new)

V1, reproduce: `race.py` with the default grid matches the report exactly: cells=80, 26 cells > 1e-3,
2 cells > 1e-2, max 5.0648e-2, mean 2.0019e-3, drop-max mean 1.3861e-3, flat max 4.9813e-3 (load1 11.56,
tf 1.000).
- Perturbation `--perturb-maxiter 20`, tz1 winter_typical/winter_cold: 3.99e-3 -> 5.80e-3. That is up, as
  stated. It shows only that starving the budget raises any gap; it does not single out the seed mechanism.
- Perturbation `--perturb-fd-eps 1e-6`: 3.99e-3 -> 8.24e-3. The harness header says this "must go down:
  the finding's mechanism"; it went up. REPORT.md re-frames this as "not an FD artefact", so the header and
  the report contradict each other.
- Attribution: in all 26 of the cells > 1e-3, C1 (seeds only) alone is > 1e-3. In 23 of the 26, C1 carries
  at least half of the gap. So "most reached by C1" holds.
- Leave-one-out: both cells > 1e-2, including the max, are summer_negative/shoulder, with a bill under
  2 SEK. Without the 10 summer_negative cells: max 8.82e-3, 0 cells > 1e-2, 21 cells > 1e-3, mean 1.08e-3.
- Null control: flat max 4.98e-3 against a non-flat max of 8.8e-3 once summer_negative is dropped. The gap
  survives flat prices, so it is a basin/seeding gap of the solver, not a missed price arbitrage.

V2, independent: `verify_s1_random.py` runs production's own `_multi_start_minimize` from 12 random
uniform starts (seed 0), with no structured seeds, no polish and no feasibility filter. On 30 cells
(5 prices x 3 weathers x tz 0/1):
- gap_rand > 1e-3 in 11 of 30 cells; max 4.48e-2, again summer_negative/shoulder tz1.
- Random starts did worse than production in 13 of 30 cells.
- Flat max 1.47e-3.
An unstructured seed set also finds lower basins in about a third of the cells, so the phenomenon is
real. Its size is what I dispute: about 1e-3 to 8e-3 in the cells with a real bill.

V3, reach and class:
- Reachable in real Home Assistant: the solve is pure numerics, reached through coordinator
  `_await_optimize`. No hastub symbol sits on this path.
- seam_rule is the harness path. It names the demonstrated seam only and does not enumerate the
  candidate-construction sites (the space path near optimizer.py:3744 and the move_starts/DHW path near
  4336).
- class_guess "new" is wrong. This is bugclasses.json P4, "seed set or stop tolerance does not bracket
  the optimum".
- Severity: low. The consequential cells are at most 8.8e-3 of the objective, and the gap does not
  separate from flat.

Why weaken: the headline ">1e-2 in 2 cells, max 5.06e-2" rests entirely on near-zero-bill summer_negative
cells, and the stated mechanism perturbation (fd-eps) moved the wrong way.

## D0-s2-01: vote verify, severity low, class P4 (not new)

V1, reproduce: `ftol_race.py` matches exactly: winter mean 0.2025 %, max 1.2344 % (winter_moderate/cold),
flat mean 0.0787 % (load1 30.87).
- Perturbation `--ftol 1e-10`: winter mean 0.0088 %, flat mean 0.0028 %. Down, as stated.
- nfev 408 -> 906 on winter_typical/cold.
- Leave-one-out on the finder's metric: drop-max winter mean 0.0551 % is *below* flat mean 0.0787 %. The
  finder's "winter vs flat" contrast is a single-cell artefact of its own metric.

V2, independent: `verify_s2_shipped.py` re-runs the whole optimize with every production ftol forced to
1e-10 and scores both shipped x on the default run's captured objective. This is not a polish from prod.x.
- shipped_gain winter mean 0.395 %, max 0.92 % (winter_narrow/cold), min -0.096 %.
- drop-max mean 0.320 %.
- Flat mean 0.098 %, max 0.135 %.
Under this metric the winter-over-flat excess survives leave-one-out (0.32 % vs 0.10 %), so a tighter
ftol ships better plans. The bill proxy is mixed in sign (from -5.8 to +3.1 SEK), consistent with the
finder's MPC result that the gain is not consistently realised in SEK.

V3, reach and class:
- Reachable in real Home Assistant: the same pure-numeric solve path.
- seam_rule `grep -n '"ftol": 1e-6' optimizer.py` enumerates all three sites (685 restart, 834 main
  run, 4326 two-zone move_starts pre-solve). No ftol exists elsewhere in custom_components.
- class_guess "new" is wrong. This is P4: the stop tolerance does not bracket the optimum.
- Severity: low. The objective effect is under 1 %, the realised cost is mixed, and the cost is about
  2x nfev.
