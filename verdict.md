Fix review: merge 36c985d335d7dd9545a1df974442541bb65412b9

bus-nonce: 2ebbb79b24a0de6a97163e7a90efdb21

## Scope

PR #2745 (R10-SAV-COMFORT, #2492). This review measured head 36c985d335d7dd9545a1df974442541bb65412b9, from a detached worktree.
- That head merges the authored code head 28ddae464 (the r2 handoff) and origin/main 5c0ee1093.
- Round: the brief labels this the r4 dispatch on the r2 handoff. The earlier rounds were:
  - blocked c70c3e46 (carry-missing);
  - merge on the 46dc1dda delta;
  - a return over main's five deleted claim lines, which 28ddae464 restores.
- Because this is the fourth round, a further block would owe a re-cut under fixer.md, not a repair. None is owed.

The contract was current at dispatch: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty against 5c0ee1093. While I worked, main moved to 662a3809 and edited fix-review.md and fixer.md.
- Those edits are wording, plus one widening of step 6's class-open clause: "a site or a predicate's unguarded domain".
- I checked that clause against the added predicates (Evidence). Nothing in it changes this verdict.

## Findings

- The committed copy of the finder's harness reads DEFECT on its `cost` arm at this head, and the body does not say so.
  - The file is `dev/audit/harnesses/r10_sav_baseline.py`. Its `cost` arm pins #2255 item 5's rule, "row actual_sek == receipt total_sek".
  - At this head the arm reads receipt 15.0 against row 4.2, so a no-argument run prints `arms run 4, defect 1+`.
  - The PR retires that rule on purpose. Carry 3's owner acceptance puts the row's Baseline, Actual and Savings on one covered-interval basis, and M21 pins it.
  - The PR edited this file's transient and null verdicts but left the `cost` arm asserting the retired rule. The body runs only `null` and `transient`.
  - The arm should be re-pointed to the new invariant (actual_sek equals the covered intervals' metered cost) or retired with its reason, so a later seat does not read a stale DEFECT as a regression.
  - The earlier reviewer's dismissal of the transient and null redefinition (comment 6387209379) did not cover this arm.
  - Carry: #2492
- `custom_components/heatpump_optimizer/ledger.py:39-40` still says "the two ``savings_`` lines", and the PR adds a third (`savings_plan`).
  - The rule the comment states still holds, because `billed_total` is an allow-list. Only the count word is stale.
  - The c70c3e46 review carried this, and it is unchanged at this head.
  - Carry: #2492

## Evidence

- RESULT head:
  - The body's `## Head` names 36c985d335d7dd9545a1df974442541bb65412b9, the head I measured.
  - The branch has since moved one commit to 772d1b9387cd66d4dd59006e0112bf3806f180ce, "ci: pin killed mutants" by github-actions[bot] (ci-autofix's mutation-autofix job).
  - That commit adds exactly six files under `tests/mutation_ledger/killed_by/` and touches nothing else (ev/head-delta-772d1b9.txt).
  - The six anchors are the body's six Unpinned sites, and each one is killed (RESULT opmutants below).
  - Whether this verdict carries to 772d1b9 is the orchestrator's section-11 carry predicate. I did not run it.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exits 0 for both heads:
  - against 5c0ee1093: tree ed0560eb;
  - against main 662a3809: tree edae3540 for 36c985d3 and 264d6d90 for 772d1b9;
  - no conflict and no claim-driver output (ev/merge-tree.txt).
- RESULT version: VERSION, the manifest version and RELEASE_NOTES.md are untouched. The diff moves none of them, and CI's pr-contract version-edit step agrees.
- RESULT claims, checked three-dot against the merge base 5c0ee1093 (ev/claim-diff.txt):
  - All five of main's `coord_*` R10-SCORES lines are present once each: coord_all_features, coord_dhw, coord_grid_fee, coord_minimal, coord_two_zone.
  - The only `-` lines are 15 may-drift comments. Each is restated under its "R10-SAV-COMFORT suspends ..." note, so no claim line is removed.
  - Each of the 41 new claim lines carries a direction (`a -> b`).
  - `claims-for: 7.0.4` equals VERSION in both claim files. card_claimed_drift.txt is byte-identical to main's.
  - `env_drift.py --claims-only`: `claims hygiene: origin/main ok`.
- RESULT golden: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 5c0ee1093` at the head (ev/env_drift_all.txt), rc=0:
  - `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`.
  - 41 CLAIMED fixtures moved, every claim moved, and the five coord_* fixtures are byte-identical to main.
  - The moved leaves are baseline_cost ×39, deferred_energy_cost ×41, predicted_savings ×41 and savings_percentage ×2. No plan key moved, as every claim states.
- RESULT finder's harness, main's own copy (ev/finder_r10_sav_baseline.main.py, ev/finder_baseline_both_ends.txt). Base 5c0ee1093 against head:
  - transient: SOUND (spread 0.00) → DEFECT (spread 0.07 kW).
  - cost: SOUND → DEFECT (15.0 vs 4.2).
  - coverage: SOUND both ends.
  - null: DEFECT 12.34 % → DEFECT 7.59 %.
  - The transient and null moves follow from carry 1's acceptance and were judged sound by the earlier reviewer. The cost move follows from carry 3, and the stale arm is listed under Findings.
- RESULT finder's carry harness `dev/audit/harnesses/r10_sav_null_terms.py`, main's copy (the #2411 reviewer's probe named in carry 1), both ends (ev/finder_null_terms_both_ends.txt). The comfort term is gone and the timing term survives:
  - vary arm: booked thermostat 128.4 → 121.8 kWh, against steady at the delivered room 121.5 at both ends. Outdoor-timing gain +17.29 % → +17.27 %.
  - const arm: booked 124.9 → 119.2 against 119.4 steady at the delivered room. Timing +0.00 % → −0.00 %.
  - The const arm's remaining gap of 9.1 kWh is its stored-heat drawdown (9.3 kWh_e). Settled, it reads about 0, which is carry 1's acceptance.
- RESULT body figures, re-taken with the head's harness files at both ends (ev/pr_harnesses_both_ends.txt). Every figure in the body's Null control reproduces exactly:
  - volume flat: −64.51, DEFECT 0.2154/kWh → 0.00, SOUND, meter_calibration 1.56.
  - volume vary: 10.37 = −64.51 + 74.88 → 74.88.
  - volume gap: 48.0 at both ends, meter_calibration 1.0.
  - comfort const: +4.95 % vs +0.00 % → +0.35 % vs −0.00 %.
  - comfort vary: +20.03 % vs +15.30 % → +16.04 % vs +15.31 %.
  - baseline null: 128.4 vs 121.5 → 121.8 vs 121.5.
  - baseline transient: 2.06 kW, 1.81e-01 off → 1.95 kW, 8.88e-16 off.
- RESULT mutation proof, the fixer's `r10_sav_comfort_mutants.py` on a `git ls-files` copy of the head (ev/mutants.txt). Every count equals the body's:
  - M0: rc=0, failing=0.
  - M1 6, M2 2, M3 8, M4 5, M5 1, M6 4, M7 4, M8 1, M9 1, M10 1, M11 1, M12 1, M13 1, M14 1, M15 1, M16 2, M17 3, M18 6, M19 1, M20 1, M21 9, M22 4, M23 2, M24 2.
- RESULT reviewer mutants, my own (ev/reviewer_mutants.py, ev/reviewer_mutants.txt, same runner). M0: rc=0, failing=0. All four are killed:
  - X1: the space path matches against `room_temps[:-1]` → failing=3, the matched-target step-0 checks.
  - X2: the hot-water `held_cost` drops `baseline_dhw` → failing=1, "held_cost is the thermostat at the schedule itself, on both paths".
  - X3: calibration inverted (model over meter) → failing=5.
  - X4: shortfall taken as the max, not the mean → failing=6, including "moves the reference down by its mean shortfall, uniformly".
- RESULT opmutants, for the 6 previously unpinned sites. I drove `mutation_table.candidates()`'s own mutants with `r10_sav_comfort_opmutants.py <copy> full <key>` (ev/opmutants.txt). The NULL is rc=1, failing=1: the `#363 recorded_at` check that fails in every copy without `.git`. All 6 are killed by the `killed()` rule:
  - optimizer.py:324 RETURN_DEL failing=3 and :336 RETURN_DEL failing=3: D1-s2-51, D1-s4-02 and D1-s2-04, all `solve_failed`.
  - :333 GUARD_OFF failing=7, among them "a night setback lowers the reference, not the reported savings".
  - :5294 BOOLOP and :5294 GUARD_OFF, failing=2 each: "the savings reference backs off by the wood share on the two-tank layout ...".
  - :5335 CLAMP_DROP failing=2: "a demand past the pump's nameplate holds the reference at max_electrical_power", reading 1.469 kW against a 1.0 kW pump.
  - Every pin in 772d1b9 matches these sites. Its `killed_by` drivers are tests/features.py and tests/plan_view.py, with the same failing counts.
- RESULT predictor: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head prints the same 6 ADDED UNPINNED sites and "no closures, fast, wave-script or instrument red predicted" (ev/ci_predict.txt).
- RESULT stress: the earlier head's stress red is gone, paid in code.
  - Local run: `GOLDEN_REF=5c0ee1093 PYTHONPATH=tests/hastub python3 tests/stress.py` at the head exits 0 with 0 FAIL lines (ev/stress_head.txt). It prints `production calls: 20 of 20 family members judged against 5c0ee109305f ...; re-planned: []; new on this branch: []` and `ok no scenario's production calls grew past what its work counts vouch for, on an unchanged plan (round 9)`.
  - CI: `tests / fast (3.14)` is success at this head (job 121031503938).
  - The payment is the per-pass hoist in `_compute_baseline_power`. No allowance and no raise was made.
  - Bitwise equivalence is shown by the golden run above: no unclaimed drift, and no plan key moved.
  - `documented` in stress.py moves with docs/how-it-works.md:1315 in the same diff, so the README table and its test agree.
- RESULT owner specification (carry 4), checked against the code:
  - The baseline runs at the meter's power levels: `meter_calibration` = metered kWh over the plan's modelled kWh, both on the same intervals.
  - DHW thermostat always on: `dhw_planner._baseline_dhw_economics` holds the tank at setpoint around the clock, unchanged.
  - One price profile on both sides: spot plus fee, `settle_interval_savings`.
  - Card equals ledger cell for cell: tests/card.mjs, killed by M24.
  - At one flat price the timing is 0 (volume flat arm). COP timing at a flat price is a volume difference, which the specification lets remain.
- RESULT class and domain (step 6). The body's reader census, `grep -rnE "savings_months|savings_sek|savings_pct|baseline_sek|actual_sek" custom_components/` with ledger.py excluded, returns coordinator, sensor, notifier, card and payload. Each reads the row.
  - I also listed readers of `OptimizationResult.baseline_cost` outside optimizer.py. They are coordinator.py:2435 (the payload) and sensor.py:546 (an attribute). Neither differences it across what-ifs.
  - The one what-if difference, coordinator.py:11243, now reads `held_cost`, which M16 pins.
  - `_comfort_matched_targets`'s domain: a NaN trajectory returns the schedule, which is tested. Length mismatch is unreachable, because both solve paths build `comfort_targets` at n_steps.
  - `meter_calibration`'s domain: a plan under 1 kWh returns None, pinned by M20. Non-finite inputs never book (`add_savings_settlement`'s finite guard). No seam is open.
- RESULT forward-carry: carry 5 seam 2 goes to R10-SAV-ACTUATION. The c70c3e46 block's remedy, roster edit 1debc245a, put both controls in that group's `carry`; the 46dc1dda delta review confirmed it.
- RESULT metrics (step 14). Each move is earned by the change:
  - `class_excess_loc` 18209 → 18206 is a lowering. Its reason is in 8f5fd0295's message. `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.
  - `node tools/policy/policy_lint.mjs --budgets` exits 0, and `rules_sync.mjs --check` is ok (ev/cheap_checks.txt).
  - The mutation ledger drops `_baseline_target`'s four pins. Their line no longer exists: the hoist rewrote it into a delegation, re-pinned in 772d1b9.
  - The golden and claim moves are the 41 measured above. `budget-raise-gate` and `arch-score` are green.
- CI at 36c985d335d7dd9545a1df974442541bb65412b9, read from the commit's check-runs API (ev/ci_check_runs.tsv). These are success:
  - tests: fast (3.14), closures, coverage, coverage-ratchet, typing, browser, arch-instrument, briefs, closure-scope, nightly-status, graders-head-copy, mutation-pins (1) and (2), mutation-autofix.
  - governance: delivery-status, env-matrix, instrument-self-tests, policy-docs, wave-script.
  - codeql: actions, javascript-typescript, python.
  - also arch-score, budget-raise-gate, hassfest and validate-hacs.
  - `tests / lane-proofs` was still queued when I read CI.
- The three red checks at this head:
  - `tests / mutation` failed at 00:31. It is the 6 ADDED UNPINNED sites that the body's Red checks names and answers. mutation-autofix has since pinned them in 772d1b9.
  - `pr-contract / pr-contract` failed in its code-scanning wait: `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. codeql / Analyze (python) concluded success later, at 01:01:13.
    - Every body check in that run is clean: `FIGURES: 15 resolved, 2 not verified, 0 refused`; preflight `clean    no refusal`; `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted`; no version edit.
    - This is a timing red with no content defect for the body to answer. No pr-contract run had started after it when I read CI.
  - `gate` (edit run) failed with `FAIL run(s) [40145720045] at this head are still being judged; their gate decides`. That is a deferral to the code run, not a content red.
  - All three are this head's timing or ordering artefacts, or answered in the body, so step 11 owes no root-cause answer for them. The orchestrator's section-11 gate check is still owed at whichever head it merges.
- My instruments: the mutant runner ev/reviewer_mutants.py is my own; it reuses the fixer's runner and swaps in my M list. All other runs used the finder's (main's) harness copies or the PR's committed harnesses, named file by file above.
