Fix review: blocked c70c3e464a4edee48a81dd65c8c612f6e4139c3b carry-missing: carry 5 seam 2's controls are not stated in R10-SAV-ACTUATION's brief

bus-nonce: bb6d21d9179725e51fc68c914b3c12c2

PR #2745 (R10-SAV-COMFORT, #2492). Review round 1: no earlier review of this PR exists. I measured head c70c3e464a4edee48a81dd65c8c612f6e4139c3b. It was still the branch head when this verdict was written. The authored code head is acd865b03, and c70c3e46 adds only `dev/programme/delivery/2745.md`.

## Block

Fix-review step 10. The body forward-carries carry 5, seam 2 (actuating the supply switch at step boundaries) to a new group. The orchestrator created that group as R10-SAV-ACTUATION in `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`. I read it at 65c67fc26 and again at b90717be1 (ev/roster-R10-SAV-ACTUATION.json). Its `brief` names the work, the design note and "the failing test", and its `carry` is `[]`. It does not state the controls the body carries, which come from carry 5's own text:
- a synthetic install with the cycle phase at 0 and at 14 min books identical duty verdicts;
- one mutant per seam.

finding-propagation.md requires "Carry the control, not only the claim". Today the controls live only in R10-SAV-COMFORT's carry 5 and in this PR's body. A seat dispatched on R10-SAV-ACTUATION will not read either.

The remedy is an orchestrator-side `roster_edit.py` op that adds those two controls to R10-SAV-ACTUATION's brief as preconditions. The body says the fixer had no write access there, and nothing in the authored diff needs to change for it. Every other step below passed. A re-review after that edit is a delta, provided the head does not move.

**Stress growth and the brief's raise question.** There is no structural-budget raise in this diff, and the body has no `## Raise justification` section. Evidence:
- No `*_budgets.json` file changed.
- `python3 tests/structure.py` passes at the head with `class_excess_loc 18209 <= 18209` and `dead_methods 0 <= 0`.
- `budget-raise-gate` is green.

The growth the body names is stress.py's production-call channel. Its own rule (tests/stress.py, comment above `SCENARIO_CALLS_GROWTH = 0.05`) says a legitimate firing "passes for ONE pull request, never by a raise", on tvofi's approving review naming the merge and the measured growth. So the budget-raise mandate (0013) has nothing to rule here. What the PR needs is tvofi's review naming merge #2745 and this growth.

I re-measured the growth myself (ev/calls-base.txt, ev/calls-head.txt; probe ev/calls_probe.py, which calls `stress.production_calls(stress.build_case(...))` exactly as stress.py's probe does):
- winter/1z/space/pin-off: 78480 calls at merge base 73b69fe0a and 84263 at the head, 1.074x.
- evals 42 vs 42; simulate 131232 vs 131328; vouched ratio 1.001x.
- objective unchanged at 60.1042784820211.
- thermal_model.py +4072 and optimizer.py +1654 beyond what is vouched. These match the body and CI's `tests / fast` log.
- summer/2z/dhw/pin-off grows 220938 → 221027 (+0.04 %).

I looked for a payment the body missed and found none for the firing scenario. Its growth is the second `_compute_baseline_power` at the comfort-matched targets. Carry 1 requires that run, and it already skips when the shortfall is not positive. The unmatched run is also needed, because it is the solver's start.

## Findings

- The finder's harness `dev/audit/harnesses/r10_sav_baseline.py` (#2255) had its verdicts redefined in this PR (commits 29f6d6cb, c57fb1bc). The body does not say so: it reports every base and head figure under the new definitions.
  - Under the base tree's own copy of the file, the base reads null DEFECT and transient SOUND (spread 0.00 kW). The head reads null DEFECT (7.59 % saved on a flat price, against the original < 3 % rule) and transient DEFECT (spread 0.07 kW, against the original < 0.05 kW rule). See ev/finder-base-*.txt and ev/finder-basefile-at-head-*.txt.
  - Both moves are by design. Carry 1's acceptance says the null "must separate [comfort, timing, stored heat], not drive the null to 0". A comfort-matched reference depends on the comfort each start delivers, so its step 0 cannot be the same from every start.
  - The redefined transient arm still guards #2255's defect: step 0 must equal the steady holding power at the matched target.
  - I judge the redefinition sound, but the body should have named it as the fixer's.
  - Carry: dismissed: the redefinition follows carry 1's binding acceptance, and both readings are recorded here for the owner.
- `custom_components/heatpump_optimizer/ledger.py:36-41` still says "the two ``savings_`` lines". This PR adds a third, `savings_plan`. The rule that comment states, that no savings line is in `BILLED_LINES`, holds for the third line too: `billed_total` is an allow-list. Only the count word is stale.
  - Carry: #2492
- The class-LOC ratchet was partly paid by cutting spent-history prose in `optimizer.py`: the measured 10-scenario rationale for a symmetric settlement, the min-power clamp history, and the transient history (commits 1b550bc3, 654aebf4). I planted the same kind of move: deleting comment lines with nothing else changed lowers `class_excess_loc`, because the metric counts a class's span. The same commits also hold real code payments, so the change is sound: `_settle_horizon` removes the duplicated end-less-start settlement, and the buffer and DHW re-pricing became one loop. The prose kept states the current "why", and the history is in the commit messages.
  - Carry: dismissed: under a sound change this is the known span-counting property of the instrument, not gaming by this PR.

## Evidence

- RESULT merge: `git merge-tree --write-tree origin/main c70c3e46` exits 0 with tree 1bf92cf6. There are no conflicts and no claim-file driver lines (ev/merge-tree.txt).
- RESULT version: no change to VERSION, the manifest version or RELEASE_NOTES.md.
- RESULT head: the body's head c70c3e46 is the head I measured. The roles directory has no diff from origin/main, so this contract is current.
- RESULT harnesses at both ends: I ran the head's harness files against the merge-base and head worktrees. Every figure matches the body.
  - volume flat: −64.51 (DEFECT, 0.2154 per kWh) → 0.00 (SOUND), k=1.56.
  - volume vary: 10.37 = −64.51 + 74.88 → 74.88 timing.
  - volume gap: 48.0 / 41.67 % at both ends, k=1.0.
  - comfort const: +4.95 % → +0.35 %.
  - comfort vary: +20.03 % vs timing +15.30 % → +16.04 % vs +15.31 %.
  - baseline null: DEFECT → SOUND.
  - baseline transient: DEFECT → SOUND.
  - Files: ev/harness-*.txt. The body's figures name ac5788f2 as the base. ac5788f2..73b69fe0a touches only dev/ governance and record files, so the base figures carry.
- The gap arm is not byte-identical: savings_pct is 41.66666666666677 at the base and 41.666666666666664 at the head. The pct is now computed from the rounded cells, which the body states by design. The published 2-dp cells are identical.
- RESULT mutation proof (my own mutants, ev/mut.py on a `git ls-files` copy of the head). Null: section rc=0, failing=0. Full tests/features.py: failing=1, the `#363 recorded_at` check that every copy without `.git` fails. Every mutant was killed:
  - R1, thermostat never calibrated: 3 failing.
  - R2, settlement passes no plan draw: 4.
  - R3, a legacy month gains a plan line: 1.
  - R4, no 1 kWh floor: 1.
  - R5, actual is the bill again: 9.
  - R6, saving off by 0.01 from the cells: 11.
  - R7, arbiter re-freeze deleted (full script): 2 against the null's 1.
  - R8, comfort matching removed: 8.
  - R9, the old start bound restored: 4.
  - R10, `held_cost` line deleted: NameError, a trivial kill. I replaced it with R11.
  - R11, coordinator reads `baseline_cost` for the held delta (full script): 2 against 1, the #2257 check.
  - R12, end credit dropped from the start bound: 1.
  - Files: ev/mutants-section.txt, ev/mutants-full.txt.
- RESULT golden: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 73b69fe0a` at the head prints NO UNCLAIMED DRIFT on 56 scenarios and NO STALE FIXTURE (ev/env_drift_all.txt). The 41 claims include summer_dhw_only −7.62 → 5.88 %, carry 1's second limit. away_setback is unclaimed, so it did not move.
- RESULT structure: STRUCTURE RATCHET PASSED. RESULT archscore: `Architecture score: dS +0.0000 NULL` against 73b69fe0a.
- RESULT card equality: `tests/plan_view.py && node tests/card.mjs` prints ALL CARD CHECKS PASSED (ev/card.txt).
- Seam census: the body's grep returns coordinator, sensor, notifier, payload and card. The census is in ev/seam_census.txt.
  - Card line 8587 reads the plan-horizon prediction, which is divergence (a), out of scope by carry 3.
  - Every other reader reads the row. No seam is open.
  - The receipt renders only `basis` lines, so `savings_plan` never reaches a receipt.
  - The arbiter's `"plan"` reference stays inside the step row. `_verdict` copies four fields, so diagnostics never serialise the plan.
- CI on c70c3e46 (run 40112142879), read from the check-runs API.
  - `tests / mutation` is red: `MUTATION TABLE REFUSED`, with the 14 ADDED UNPINNED sites the body lists one for one. The body answers it under Red checks. `mutation-pins` shards are running (4 is green).
  - `tests / fast (3.14)` is red with only `tests/stress.py` failing, 1 of 113: the production-call check the body names and answers. In CI `tests/entities.py` passed. The body's 2 local entities failures were environment-only, as the body says.
  - Everything else concluded is green: closures, coverage, typing, browser, briefs, arch-score, budget-raise-gate, hassfest, CodeQL.
  - lane-proofs and claims-autofix were still queued, so not every workflow had concluded when I read CI.
- Both red checks are named and answered in the body, so step 11 is satisfied.
