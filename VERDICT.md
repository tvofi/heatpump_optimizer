Fix review: merge c0f221f76fe3c8fa41fa7d98ae352aa6e5554b43

bus-nonce: 8ae7264ca6499d64247efe2aadd47641

## Scope

This is a delta review of PR #2745 (R10-SAV-COMFORT, #2492) at head c0f221f76fe3c8fa41fa7d98ae352aa6e5554b43, after fixer round r3 (handoff/r10-sav-comfort-r3, c91cc71fe).
- The previous review's merge verdict was cut at 36c985d335d7dd9545a1df974442541bb65412b9 (probe/rev-2745-2ebbb79b). This review judges only the delta since then, plus the merged main.
- Round: this is the fifth verdict on this PR: blocked at c70c3e46, merge at c70c3e46 (roster delta), merge at 46dc1dda, merge at 36c985d3, and now this delta. No block is owed, so no fixer.md re-cut is owed.
- Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

The PR's own diff between 36c985d3 and this head is two things (ev/pr-interdiff.txt):
- six new `tests/mutation_ledger/killed_by/` files. These are mutation-autofix's 772d1b938, kept by c91cc71fe when it won the add/add conflict against ed1826c24;
- the `class_excess_loc` re-record line, which moves from 18209 → 18206 to 18202 → 18199 because main's own budget moved under it. The step is still −3.

Every other line of the PR's diff against its merge base is identical, text for text, outside the hunk headers and index lines. The merged main (5c0ee1093 → 21a1e04a7) moves coordinator.py, store.py, thermal_model.py and const.py. Between ab00437c9 (the fixer's measurement base) and 21a1e04a7 it moves no production, golden or tests/*.py file. So the body's figures, taken against ab00437c9, carry. I re-took them anyway against 21a1e04a7, below.

## Findings

The two findings of the 36c985d3 review are not closed at this head. Each was routed to #2492 rather than required to be fixed here, and round r3 did not touch either. I re-confirm both and carry them on:
- `dev/audit/harnesses/r10_sav_baseline.py`'s `cost` arm still asserts the rule this PR retires, "row actual_sek == receipt total_sek". At this head, `r10_sav_baseline.py cost` prints `receipt total_sek = 15.0; row actual_sek = 4.2`, `cost: DEFECT` (ev/finder-baseline-both-ends.txt). The arm should be re-pointed to the covered-interval invariant, or retired with its reason, so that a later seat does not read this stale DEFECT as a regression. Carry: #2492
- `custom_components/heatpump_optimizer/ledger.py:39-40` still says "the two ``savings_`` lines". The PR adds a third, `savings_plan`. The rule the comment states still holds, because `billed_total` is an allow-list. Only the count word is stale. Carry: #2492

## Evidence

- RESULT structure (the brief's requirement). `python3 tests/structure.py` at the head exits 0 (ev/structure.txt):
  - It prints `ok   class_excess_loc 18199 <= 18199` and `STRUCTURE RATCHET PASSED`, rc=0.
  - At the merge base 21a1e04a7 it measures `class_excess_loc=18202` and passes.
  - The budget move is a re-record down (18202 → 18199), with its reason in 8f5fd0295's message: "the HeatPumpOptimizer span shrinking by the three lines the hoist removed".
  - Step 14: the 36c985d3 review established that the move is earned by the hoist, and the hoist's code is unchanged in this delta.
- RESULT head: the PR body's `## Head` names c0f221f76fe3c8fa41fa7d98ae352aa6e5554b43, the head I measured. `git ls-remote` read it as the branch head at 08:06Z, after every measurement.
- RESULT merge. `git merge-tree --write-tree` exits 0 against both mains, with no conflict and no claim-driver output (ev/merge-tree.txt):
  - against origin/main f40142d66: tree a66a90f3;
  - against origin/main 880b667aa: tree b1b3015d.
- RESULT version: VERSION, the manifest version and RELEASE_NOTES.md show 0 diff lines, three-dot against 21a1e04a7 (ev/cheap.txt).
- RESULT claims (ev/cheap.txt):
  - `env_drift.py --claims-only` prints `claims hygiene: origin/main ok`.
  - The three-dot claim diff removes 0 lines that are not may-drift lines.
  - `card_claimed_drift.txt` diff: 0 lines.
- RESULT golden: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 21a1e04a7` at the head prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`, rc=0 (ev/env_drift_all.txt). The baseline was captured fresh, after a cache miss.
- RESULT harnesses at both ends: I ran the head's harness files from worktrees of 21a1e04a7 and of the head (ev/harness-both-ends.txt). Every Null-control figure in the body reproduces exactly:
  - volume flat: −64.51, DEFECT 0.2154/kWh → 0.00, SOUND, k 1.56.
  - volume vary: 10.37 = −64.51 + 74.88 → 74.88.
  - volume gap: 48.0 at both ends, k 1.0.
  - comfort const: +4.95 % vs +0.00 % → +0.35 % vs −0.00 %.
  - comfort vary: +20.03 % vs +15.30 % → +16.04 % vs +15.31 %.
  - baseline null: 128.4 vs 121.5 → 121.8 vs 121.5.
  - baseline transient: 1.81e-01 → 8.88e-16 kW off.
- RESULT finder's harness, main's own copy of `r10_sav_baseline.py`, at both ends (ev/finder-baseline-both-ends.txt):
  - base: `arms run 4, defect 1: null`;
  - head: `arms run 4, defect 3: transient cost null`.
  - The transient and null moves are the redefinition that carry 1's acceptance requires, judged sound at c70c3e46. The cost arm is the first finding above. Neither result changed since 36c985d3.
- RESULT mutation proof: the fixer's `r10_sav_comfort_mutants.py` on a `git ls-files` copy of the head (ev/mutants.txt).
  - M0: rc=0, failing=0. This is the null.
  - M1 6, M2 2, M3 8, M4 5, M5 1, M6 4, M7 4, M8 1, M9 1, M10 1, M11 1, M12 1, M13 1, M14 1, M15 1, M16 2, M17 3, M18 6, M19 1, M20 1, M21 9, M22 4, M23 2, M24 2.
  - Every count equals the body's, and every mutant is killed.
- RESULT the delta's six pins, re-driven by me. I drove `mutation_table.candidates()`'s own mutants with `r10_sav_comfort_opmutants.py <copy> full <key>` on a `git ls-files` copy of the head (ev/opmutants.txt):
  - The NULL reads rc=1, failing=1. That is the `#363 recorded_at` check, which every copy without `.git` fails.
  - optimizer.py:324 RETURN_DEL: failing=3.
  - optimizer.py:333 GUARD_OFF: failing=7.
  - optimizer.py:336 RETURN_DEL: failing=3.
  - optimizer.py:5294 BOOLOP: failing=2.
  - optimizer.py:5294 GUARD_OFF: failing=2.
  - optimizer.py:5335 CLAMP_DROP: failing=2.
  - All six are killed under `killed()`'s rule: more failing checks than the NULL.
  - Each pin's `old` text equals its head line, found with `grep -Fx`.
  - Two pins record a smaller kill set with tests/plan_view.py: `_baseline_target.RETURN_DEL.26d08f36` and `_baseline_targets.RETURN_DEL.e3ab3cc7`, each at failed=1. That is a different driver, and those counts are the bot's, which I did not re-take.
- RESULT mutation inventory: `tests/mutation_table.py --base origin/main` at the head prints `3966 unpinned site(s) of 6333 candidate sites, 3969 at the ratchet base 21a1e04a7...; the ledger agrees with the deterministic inventory` (ev/mutation_table.txt).
  - I stopped that run after the inventory and null-control lines, because step 11 says never to re-run the mutation table.
  - CI's `tests / mutation` is success at this head, and I cite that instead.
- RESULT stress: `GOLDEN_REF=21a1e04a7 python3 tests/stress.py` at the head exits rc=0 (ev/stress_head.txt):
  - `production calls: 20 of 20 family members judged against 21a1e04a7...; re-planned: []; new on this branch: []`;
  - `ok no scenario's production calls grew past what its work counts vouch for, on an unchanged plan (round 9)`.
- RESULT cheap checks (ev/cheap.txt): `node tools/policy/policy_lint.mjs --budgets` exits 0.
- RESULT class (step 6) and forward-carry (step 10): the delta adds no production line, so it opens no new seam. Carry 5 seam 2 to R10-SAV-ACTUATION is unchanged since the round that confirmed roster edit 1debc245a.
- CI at c0f221f76fe3c8fa41fa7d98ae352aa6e5554b43, read from the commit's check-runs API at 08:06Z (ev/ci_check_runs.tsv):
  - Every check run is completed, with conclusion success or skipped. That includes `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `tests / coverage`, `tests / lane-proofs`, `pr-contract / pr-contract` (×2), `gate` (×2), `budget-raise-gate`, `arch-score`, codeql (python, actions, javascript-typescript), hassfest and validate-hacs.
  - No check is red at this head, so step 11 owes no root-cause answer for this head.
  - The earlier heads' reds were answered in the body and judged by the 36c985d3 review.
- UNCERTAINTIES:
  - I did not re-take the plan_view.py kill counts the bot recorded in the two RETURN_DEL pins. My tests/features.py drive kills both sites, so each pin's site is covered either way.
  - The interdiff method compares the two PR diffs with their `index` and `@@` lines stripped. A move inside a hunk header alone would not show. Hunk headers carry only line positions and context, so I judged that acceptable.
  - Two of my runs collided with my own cleanup of a shared scratch copy. The rc=1 FileNotFoundError seen was caused by this seat's process, not by the code under review, and the clean third run is the one recorded in ev/opmutants.txt.
- My instruments: none of my own this round. Every run used the PR's committed harnesses, main's copy of the finder's harness, or the tree's own tests and tools, named above.
