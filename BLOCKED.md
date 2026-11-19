# BLOCKED: r11-seam-solver

Question: the D0-s2-01 start set (price-ranked seeds drawn at the reference's own energy, f in 1.0 and the low-energy fractions, when the wood tank covers the reference whole) costs `summer/2z/space/wood-two-tank` 2.08x solver evaluations and 3.24x simulate step-equivalents on an unchanged plan, over `tests/stress.py`'s SCENARIO_WORK_FACTOR 1.80 (a `tests / fast (3.14)` red, owed), and every narrower start set measured below reopens the finding's race; may this group raise STRESS_WORK_FACTOR / re-record the scenario's budget for that one scenario (owner, CLAUDE.md rule 2), or is the start set to be re-designed (a design seat), or narrowed to variant A at the race cost listed?

Code head: 320c063489bb6100742e80697e2a5728b58551a7 (step ref handoff-wip/r11-seam-solver). Merge base: fd847a550c12060f745c82bed99551dff4781e58. Measured 2026-11-19, venv-ci python3, OPENBLAS_CORETYPE Haswell.

## What this fire did (on the code head)

- Merged origin/main (fd847a55) into the previous handoff head 261a3998; no conflict.
- docs/how-it-works.md: the multi-start paragraph names five starts, the all-off plan among them. Before: `tests/doc_claims.py` FAIL "doc states 'four', measured 5". After: ALL 439 checks PASSED.
- tests/features.py: main's R11-OUTSIDE-HONEST-STARTS-RUNS block read relaxed[-1] / first[-1] as the descent's plan; the space-only commit stage is now handed [descent, all-off], so it reads candidate 1 as [0], asks the all-off bound the stage holds on every kernel, and carries the start-pricing identity on the same house at out_mean 5.0 (a priced 2-start run). The cold-solve seed-count check counts 5. Block: ALL 61 PASSED under SkylakeX, Haswell, Sandybridge, Nehalem (`cloud-setup.sh --kernels`). Mutants: dropping the all-off candidate from the commit stage fails the new check; dropping the first-solve all-off start fails the seed-count check (nstarts=4).
- Scoped gate (`GATE_SCOPE=auto tests/run.sh`, MODE: SCOPED, 28 scripts): all ok but tests/stress.py (below) and tests/golden.py, whose local default GOLDEN_MODE=strict compares this machine's BLAS against canonical fixtures (55/56 "changed"); the drift comparison `tests/env_drift.py origin/main` in the same gate is ok.
- Not done: `tests/mutation_table.py --pin-killed --base origin/main` (mutation-autofix reported skip-measure-failed); its run here read INCONCLUSIVE on the doc_claims baseline red, since fixed, and was not re-run.

## The stress red, and the variants measured

Commands, each from the worktree root under PYTHONPATH=tests/hastub: `python3 tests/stress.py`; `python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --race <the finding's 7 cells>` ($EXPORT = `git archive 819aa2e3 dev/audit/rounds/round11`, wood_seeds.py sha1 1b03dd54ee64a4f6067982001f1abe3dbbdd4fcc). Stress baselines are captured live at origin/main by stress.py itself.

| start set (optimizer.py `_space_only_starts`) | stress, wood-two-tank | race gap_abs winter_moderate/summer_cool, winter_extreme/summer_cool, flat/summer_cool |
|---|---|---|
| head: ref-energy seeds f in (1.0, fractions) when covered > 0 | 3 FAIL: 54/26 evals 2.08x, 122592/37824 sim 3.24x, CPU 7.4x vs 6.6x | 0.0065, 0.0000, 0.0000 |
| A: f in (1.0,) only | 116/116 PASSED | 1.3571, 0.1287, 0.1292 |
| B: f in fractions only | 1 FAIL: sim 94368/37824 = 2.49x | not run |
| L: head less the space-only all-off start | 3 FAIL: 50/26 evals 1.92x, sim 3.24x | not run |
| F: head, gated on covered >= 1.0 (full cover only) | 3 FAIL, identical counts to head: the stress scenario is itself fully covered | 0.0065, 0.0000, 0.0000 |

The fractional ref-energy seeds are what close the race (A against head) and what carry the simulate cost (B, A); the stress scenario is the finding's own case (F), so no gate on the cover separates them. stress.py has no per-scenario or per-PR allowance for the work checks: only a changed plan is exempt (work_drift_compare's replanned arm), and SCENARIO_WORK_FACTOR's last change was an owner override (#1208).
