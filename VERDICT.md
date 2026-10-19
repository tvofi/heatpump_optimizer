Fix review: blocked b9f72cb10e8f12798f0111189dedc607d3393acd carry-missing: not carried to the mutation instrument's owner (the entities.py --anchor vacuous-kill finding is in no brief, roster or carry file)

bus-nonce: 10a5a496b3980edb6b407c7cf9597fa5

PR: #2411 (R10-SAV-BASELINE, #2255). This is round 3. Round 1 (comment 6251182230) returned blocked at b7a34f98a. Round 2 (comment 6252668916) returned merge at 3b6e599df.
Reviewed head: b9f72cb10e8f12798f0111189dedc607d3393acd (`ev/HEAD`). It was still the PR head when I wrote this. The PR's base is fa5026c42, which is the merge base. origin/main has since moved to b87e8f19b (#2420).
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so my copy of the contract is current.

## What round 3 changes

- Production is the same as at round 2. The branch's own three-dot diff of coordinator.py, ledger.py and optimizer.py has identical +/- lines at 3b6e599df (vs 211c8290e) and at this head (vs fa5026c42).
- The harnesses and `tests/golden/claimed_drift.txt` are byte-identical to round 2's.
- New since round 2:
  - one value check in `tests/features.py`;
  - the `ledger.py:186` CMP_BOUND pin on `tests/features.py`, chosen over the autofix's `tests/entities.py` pin;
  - the `optimizer.py:324` BOOLOP pin on `tests/typing_ruler.py`;
  - the other autofix pins;
  - two merges of main.

## Blocking

**carry-missing (step 10, finding-propagation.md).** This round, the body establishes a new finding by measurement with a null control, and I reproduced it. Under `--pin-killed`, `tests/entities.py`'s R9-F10.13 `--anchor` self-test "kills" any edit to a line that already carries a pin. It does this by refusing the ledger/inventory disagreement. So a `killed_by: tests/entities.py` pin on such a line is unproven. CI's pin chain recorded exactly such a pin on this PR.

This changes how a later stage must work: the mutation-instrument lane, and anyone who trusts entities.py pins. The body's `## Forward-carry` sends it to "the mutation instrument's owner (the lane holding tests/mutation_table.py and tests/entities.py's R9-F10.13 block)" as a roster carry that "the orchestrator appends", with the text "in the seat's report". That destination is not in the tree:
- `ev/carry-search.txt`: I grepped every roster and carry branch (handoff/audit-r10-roster tip 202097855, 2026-10-18T19:23Z, which predates this round) and origin/main's `dev/programme` and `.claude/workflows` for the finding's text. Nothing matched.
- The body names no group or `carry-<N>.json`. finding-propagation.md's Enforcement section says "The producing PR does not merge until the carry is in the tree. Its body names the file and the stage that received it", and "Name a destination that exists".

What clears this block: land the carry, with its control (the equivalent rewrite `if 0 < dt:` fails the same single entities check) and the re-measure instruction, into a live group's brief or a `dev/programme/carries/carry-<N>.json`. Then name that destination in the body. Nothing in the code needs to change.

## Measured at this head

- Step 1, mutation proof for the new pin (worktrees at b9f72cb10, `ev/diff-{mut,null}.txt`):
  RESULT m0   tests/features.py ALL 4198 PASSED rc=0; tests/entities.py ALL 2349 PASSED rc=0
  RESULT mut  `if dt >= 0:` features.py 1 of 4198 FAILED: "an interval of no length settles no hours: the stored coverage takes no sample" [{'settled_hours': {'sum': 0.0, 'count': 1}, ...}] rc=1
  RESULT null `if 0 < dt:`  features.py ALL 4198 PASSED rc=0, so the features kill is real
  RESULT mut  entities.py 1 of 2349 FAILED: "--anchor re-drives one site ... (R9-F10.13)", MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory
  RESULT null entities.py 1 of 2349 FAILED, the same check, so the entities kill is vacuous, as the body says
  The seat's choice of the features.py pin is sound. M0 to M16 were not re-run, because production is unchanged since round 1's run, which killed all 16. I did not re-run the `optimizer.py:324` BOOLOP / typing_ruler mutant. CI's `typing` lane is green.
- Step 2, the fixer's harness (the finding had no committed harness, as disclosed in rounds 1 and 2), run at both ends:
  RESULT head transient 2.06 kW x4, spread 0.00 SOUND; base fa5026c42 0.00/6.00/6.00/0.00, spread 6.00 DEFECT
  RESULT head cost row 15.0 = receipt 15.0 SOUND; base 3.0 vs 15.0 DEFECT
  RESULT head coverage scale 28.00 SOUND; base 2.80 DEFECT
  RESULT head null 12.34 % (thermostat 128.4, plan 112.6 kWh, room 18.72 vs 20.44 C) DEFECT; base 43.76 % (201.0 / 113.0) DEFECT
  These match the body exactly. They differ from round 2's 10.83 % / 43.66 % because main's merges moved the plant or solver, not production of this diff. The body re-took them at fe4e0a3b0, and they reproduce at this head.
- Step 3, `r10_sav_null_terms.py` at head: gap 15.8 = comfort 6.9 (128.4 vs 121.5); timing +17.29 %; stored -20.1 kWh_th (-11.3 kWh_e); balance 236.0 vs 235.9. In the const arm: comfort 5.2, drawdown 9.3 kWh_e, timing +0.00 %, balance 202.3 vs 202.2. All of these match the body.
- Step 5: VERSION, manifest, RELEASE_NOTES.md and card_claimed_drift.txt are unchanged three-dot (`ev/version.txt`).
- Step 13: `git merge-tree --write-tree` exits 0 with empty stderr against fa5026c42 and against the current origin/main b87e8f19b (`ev/merge-tree.txt`).
- Step 14: structure.py prints STRUCTURE RATCHET PASSED. Every budget the diff touches moves down (class_excess_loc 18368->18302, max_class_loc 8547->8544, seam_cut_total 720->719), with recorded_at re-recorded. I did not plant a counter-move.
- `closure.py no-copies`: clean.
- Step 11, CI at this head (`ev/checkruns.tsv`): 30 success, 13 skipped, 1 failure, 1 in progress.
  - The failure is `delivery-status` (117831533983). Its overdue rows are #2413, #2412 and #2407, which are main's and exempt per the dispatch and step 11.
  - `closures` (117836639072) was still in progress when I wrote this.
  - `mutation` (117831533633) is green with a real evaluation: baselines features/entities/plan_view/env_drift rc=0, "PIN RE-VERIFICATION: 6 reproduced", "0 survivor(s) of 6 evaluated", "MUTATION TABLE PASSED", and "4211 unpinned of 6083, 4217 at the ratchet base fa5026c42; the ledger agrees". It is not INCONCLUSIVE (`ev/ci-mutation-117831533633.log`).
  - `fast (3.14)`, `typing`, `env-matrix`, `arch-score`, `budget-raise-gate` and `pr-contract` are all success.

## Figures I could not re-derive

- "The ledger holds 123 `killed_by: tests/entities.py` pins in all": I count 139 at this head with the body's own grep. The count is 122 at 90c104c5d, 1bbe062e2 and 74d66b355, and 139 at 339d4bce6, fa5026c42 and every later ref (`ev/entities-pin-count.txt`). It is a pre-merge figure that was not re-taken. It does not block, but the carry that clears the block should quote the count at its own ref.
- The `--max 0` line's "ratchet base 07a09406a" has the same counts that CI prints against fa5026c42. That base name is from before the merge.

## Not verified by me

- The golden drift with claims and the archscore dS. CI's env-matrix and arch-score are green and I did not re-run them.
- The typing_ruler BOOLOP mutant.
- Step 6 other configurations. Production is unchanged, so round 2's 12/12 transient check carries.
