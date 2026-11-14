Fix review: blocked d73ec97da13b4df42e7b7eef36731707b963fce7 architecture-unsound: departures 1 and 3 from the approved note are made in the build and not raised, and two further blocks stand under Block

bus-nonce: 5b1e346dcc033dd3c6e78d6aafc90a46

Round 1. Measured head `d73ec97da13b4df42e7b7eef36731707b963fce7`, still the tip of `handoff/r11-outside-honest-starts-runs` when this was written; body read at `handoff-body/r11-outside-honest-starts-runs` `3e115df4a5`. Merge base with `origin/main` `d7004eaa775d`; `origin/main` was `23cc7b8e1d` and `git merge-tree --write-tree origin/main <head>` exits 0, so nothing here blocks on main.

The code measures as the body says: every named mutant is killed, every figure I re-ran reproduces, the drift is exactly the two claimed fixtures. The three blocks are about what the build was allowed to decide and what the body tells the owner, not about a wrong number.

## Block

1. **architecture-unsound: two departures from the approved note are built, not raised** (`fixer.md` step 17 last bullet, `fix-review.md` step 15). The note at `0c692c86d2` was approved at `caab288c05`; no design verdict covers either of these.
   - Departure 1, the second descent. The note's round-2 point 3 and its Shape say the relaxed descent keeps the duty-switch operand as R10-DUTY-SWITCH-PLANNER-PRICE built it, and its test 5 asserts the shipped plan's true score is no higher than with the operand removed. The head adds `_relaxed_plans`' unpriced descent because that test's premise measured false. The measurement reproduces (Evidence, descents: all 12 cells equal the body's), so the departure may well be right; it is still a design change the fixer approved for itself, and it adds a multi-start to every install that prices a switch.
   - Departure 3, identity. The note's test 3 asks `commit` for identity on a realizable input and its invariants say a realizable relaxed plan ships unchanged. At the head `runs.commit` is not the identity (2180 of 3000 generated realizable plans come back as a different mask, `ev/leaf_props_head.txt`), and on full solves a realizable relaxed plan shipped changed in 13 of 149 engaged stage calls (`ev/solve_props_head.txt`). The body narrows the invariant to "no start has a price and the projection changes nothing"; that narrowing is the designer's to accept.
   - Departures 2, 4 and 5 I read as conformance: 2 follows this note's own Shape sentence, 4 uses the suspension the claims guard itself demands (the perturbed run's message says so), 5 is the note's own allowance for a fixture that reproduces.
   - What clears it: a design verdict (or the owner) accepting departures 1 and 3 at this head. No code change is asked for.

2. **carry-missing: own-group** (`fix-review.md` step 10, `fixer.md` "A finding in your own group's seam is built in this PR, not carried"). The Forward-carry line for note n6 (the finite-difference gradient skipping the variables a mask fixes) ends `Carry: R11-OUTSIDE-HONEST-STARTS-RUNS` and names neither exception: it is no pending ruling and no split part the note names, the note addressed it to this fixer with "Measure before and after with `tests/stress.py`", and neither the build nor the measurement is in the body. `carry_audit.py check` passes the line because the group resolves; the contract's test is what the line names. What clears it: build and measure n6, or a ruling that drops it, recorded as such.

3. **The body's account of ruling c1's other arm is refuted by measurement.** The body says: "The other arm is one predicate (`_engaged` on `clamp_planned_levels` alone): no fixture is then claimed, and both claims below go." With exactly that predicate at this head both fixtures still move against the merge base (`ev/c1_other_arm.txt`): `cycling_cost` 44.96 to 46.39 kWh, predicted cost 34.48 to 36.39, space steps under the floor 5 to 8; `everything_on` predicted cost 60.27 to 64.88, steps under the floor 12 to 18, edges 4 to 2. The swing term is deleted for every install, so an unclamped priced solve then descends on the true objective with the start count inside it, the bilinear term the contributor measured as stalling, and ships uncommitted levels. So the other arm is not one predicate. For no fixture to move it must also restore the swing term for unclamped installs (the two cycling terms the note names as that arm's cost); left as one predicate it still owes two claims, with worse figures than the recommended arm's. This sentence is what the owner reads to decide c1, so it is corrected before the pull request opens. I do not decide c1. What clears it: the body's paragraph restated with the measured figures.

## Findings

- Seven reviewer mutants on lines this diff adds survive both of the body's commands (`ev/mutants_reviewer_cmdA.txt`, `ev/mutants_reviewer_cmdB.txt`, spec `ev/reviewer_mutants.json`): `REV_HEATS_HALF_FLOOR` (`_run_plans`, a space step beside a charge at half the floor), `REV_NO_POLISH` (`_resolved_runs`' restart), `REV_COMMIT_INITIAL_STATE` (`runs.commit` started as paused while the compressor runs), `REV_STAGE_BOX_TANK_ROOM` (`_stage_box`, space held under what the tank leaves), `REV_TIE_BREAK_ZERO`, `REV_ONE_RESOLVED` (`_RESOLVED_CANDIDATES` 2 to 1) and `REV_COMMIT_RUNNING` (`_run_plans` handing the commit program `running=False`). None is among the body's 39 or the note's mutation targets, so this is not `mutation-vacuous`; whether another block of `tests/features.py` kills them is unmeasured here and is the mutation lane's to say. `REV_COMMIT_RUNNING` and `REV_COMMIT_INITIAL_STATE` together mean no check in the two commands reads the running flag inside the commit program. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS
- Candidate (1) is not held to its scope's box when no stop is priced (`_best_runs` clips only on the `rescope` arm), so on a clamped install the per-step projection can still ship above an external total cap that sits under the floor: 8 of 140 generated cells at the head end over the cap (`ev/solve_props_head.txt`). It predates the diff and the head is better: 10 of the same 140 cells at the merge base, and in the targeted cells space over the cap goes from 3 cells to 0 while hot water over the cap stays in 2 (`ev/cap_repro_both_ends.txt`). What remains is the tank's projection, group B's seam in the note, which has no roster group yet. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS
- The group has no finder harness (an outside report). `dev/audit/harnesses/r11_honest_starts_runs.py` is the fixer's, and `ev/reviewer_*.py` are mine; neither is a finder's instrument (`fix-review.md` step 9). Carry: dismissed: the fixer's harness lands in this diff and the report had none to port
- The note names `tests/stress.py` against `tests/stress_budgets.json` at base and head on one machine as the solve-time measurement; the body reports the ported residue harness and a head-only pass. I ran it at both ends and it passes at both (Evidence), so the trace is met by this review and not by the body. Carry: dismissed: measured at both ends in this verdict

## Evidence

No review packet exists and no CI has run: there is no pull request yet, so no check was read and no red is answered here. The body's `## Red checks` line for `mutation` is a prediction; `ci_predict.py` at the head prints the same 92 unpinned sites and no other red. Everything below is my own run on one box (x86_64, 4 cores) from detached worktrees at the head and at the merge base.

Mutation proof (step 1), `mutant_run.py --spec` over the body's 39 mutants, copy-tree:
- RESULT CMD A: NULL survives, 33 killed, 6 survive (`RELAXED_SWITCH_OPERAND`, `TRUE_SWITCH_LEVEL`, `UNPRICED_DESCENT`, `RESCOPE_OFF`, `UNPRICED_DESCENT_COST_ARM`, `ADOPTED_VECTOR`), the six the body sends to CMD B.
- RESULT CMD B over those seven: 6 killed, `CANDIDATE_OWN_BOUND` survives B and is killed by A. Every one of the 39 is killed by the command the body names for it.
- RESULT unedited head: CMD A `ALL 41 FEATURES BLOCK PASSED` in 22 s, CMD B `ALL 100 FEATURES BLOCK PASSED` in 70 s.

Harness at both ends (step 2), the fixer's, disclosed as such:
- RESULT fixtures, base to head: `cycling_cost` space steps under the floor 5 to 0, edges 5 to 4, 44.96 to 40.97 kWh, predicted cost 34.48 to 32.07, lowest room 17.20 to 17.16; `everything_on` 12 to 0, 4 to 5, 67.18 to 68.83 kWh, 60.27 to 61.48, 17.78 to 17.88; combined-draw steps under the floor 8 to 11 and 11 to 4. Equal to the body and to both claim lines.
- RESULT grid, base to head: priced modulating at 1.1 kW 10 to 0 steps under the floor, edges 2 to 2, 2.83 to 2.75 kWh; at 0.53 kW 10 to 0, 2 to 2, 2.83 to 2.79; clamped unpriced edges 2 to 5, objective 7.8698 to 7.6826; the unpriced duty-cycle null 7.6183 at both ends, stage never entered. Equal to the body.
- RESULT descents at the head: all 12 cells and the three null rows equal the body's figures to the fourth decimal; null cells that moved or descended twice 0.
- RESULT `r10_setpoint_power.py` at the head: spread 32 lower / 0 higher / 0 identical, flat 32 / 0 / 0; failures 0.
- `r10_partload_residue.py relaxed` (the solve-time ratios) and `r10_setpoint_boost.py` were not re-run: those figures are unverified here.

Null controls (step 3):
- RESULT `env_drift.py --all` against the merge base: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc 0. With the `cycling_cost` claim line removed: `MAY-DRIFT UNCOVERED ... cycling_cost`, rc 1.
- RESULT unengaged solves: 28 generated unpriced duty-cycle cells are identical at base and head (objective, energy, steps under the floor), and flipping the running flag moved no unengaged plan (`ev/solve_props_*.txt`).

Claims, versions, numbers the diff moves (steps 4, 5, 14):
- `claimed_drift.txt` claims exactly the two moved fixtures under `claims-for: 7.1.17`, equal to `VERSION`; `--claims-only origin/main` is clean. `VERSION`, the manifest and the notes heading are untouched.
- Structure: three budgets move down, none up; `tests/structure.py` passes. Architecture score `dS +0.0000 NULL`. The candidate stage as module-level functions is what note n1 directed, so the class-size movement is the design's shape and not a counter move.
- Ledger: 11 pins deleted, 5 of them on functions that survive; the pinned `old` line of each is gone from the head, so none is a pin of a surviving line (note n2 holds).
- `tests/doc_claims.py` `ALL 410 checks PASSED`; `docs/architecture.md` states 93 modules.
- `tests/stress.py`: `ALL 116 STRESS CHECKS PASSED` at the head and at the merge base.

Other configurations (step 6), my own instruments:
- RESULT leaf, 3000 generated cases: start count equals the edge count on realizable plans from a stopped and a running compressor; batch rows equal the scalar bit for bit in both memory orders; every boundary's start share plus switch weight is at most one start; `commit` keeps every forced step, runs no free step under the floor, reports `tracked` truthfully and holds the run and pause lengths at 5, 15, 30 and 60 minute steps. One property fails, identity on a realizable input (Block 1).
- RESULT full solves, 140 generated cells (4 installs including a zero floor and a fixed-speed pump, 3 start prices, with and without hot water, 3 stop pairs, both running readings, 3 price profiles including negative prices, caps, pins and off windows): no solve raised, none reported failed, the shipped score was never above candidate (1)'s, the published start count always equalled the edge count with the running reading, no space step shipped between the running rule and the floor off a capped step, no space on an off step.
- RESULT cost of the commit program: 576 steps at 5 minutes, three masks in 0.21 CPU-seconds.
- Sibling sites: the body's `git grep` prints the three harness notes, three `done` roster brief lines in two files under `dev/programme/rosters/` and one dated claim comment; no caller of a deleted name is left. The enumeration returns nothing open.

Contributor's commit and privacy:
- `62701bf993` keeps Bankaifan as author with hpo-fixer as committer; the note's blob is identical at the pull request's `054a866c94`, at `62701bf993` and at the head. The author address is already in the numbered-noreply grammar, so `ref_privacy.py guard --commits <head> --over origin/main` exits 0 with and without `--adopt-email`: no adoption of an outside address was needed, and the body claims none. No commit message in the range carries a tool attribution.

Stated here, not verified: the body's solve-time ratios, the committed-harness figures "at the base" for `r10_setpoint_power.py`, and the full `tests/features.py` and `tests/entities.py` counts, which are CI's to run once the pull request exists.
