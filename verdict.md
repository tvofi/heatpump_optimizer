Fix review: merge b9f72cb10e8f12798f0111189dedc607d3393acd

bus-nonce: 2a9e8d822680feb2e82ddadf4b2f8365

PR: #2411 (R10-SAV-BASELINE, #2255). This is round 4. Round 1 (comment 6251182230) blocked b7a34f98a. Round 2 (6252668916) returned merge at 3b6e599df. Round 3 (6257471886) blocked this same head, b9f72cb10, as carry-missing. The head has not moved since round 3. This round re-checks round 3's block and re-takes the cheap measurements. Fourth-round note (fix-review.md): the code was not repaired between rounds 3 and 4. The only change is the carry the orchestrator landed out of the branch, so no re-cut is owed.
Reviewed head: b9f72cb10e8f12798f0111189dedc607d3393acd (`ev/HEAD`). It was still the PR head at writing (`ev/head-at-writing.txt`). Merge base: fa5026c42. origin/main: b87e8f19b.
Contract: `git diff fa5026c42...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Round 3's block, re-checked

carry-missing (step 10): **cleared.** The carry is now in the tree. It is roster group **R10-MUTATION-ANCHOR**, added to `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster` by 21612f5e5 (2026-10-19T01:11Z, after round 3's 01:05Z post). That branch is where `roster_edit append-carry` lands carries; round 2 accepted the same branch for this PR's earlier carries.
- The group is live: `resume.stage: not-started`, branch `handoff/r10-mutation-anchor`. Its seams are `tests/mutation_table.py` and the R9-F10.13 block of `tests/entities.py`. That is the "mutation instrument's owner" the body names.
- Its brief carries the finding verbatim. It includes the control (the equivalent rewrite `if 0 < dt:` fails the same single entities check) and the re-measure (`env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`; "the equivalent rewrite must survive"). It is stated as the acceptance: "the finding above, with its control and its re-measure, is the acceptance; re-derive the 123 and the second-pin count at your merge base". Its first deliverable is a failing test first on that control.
- `brief_lint.mjs` on the roster at that tip finds nothing for R10-MUTATION-ANCHOR (`ev/brief-lint.txt`). The lint reports 1 error, in R10-SCORES (`coordinator.py:10281` anchor). That error is the same on origin/main's roster, so it predates this round and is not this PR's.
- Not blocking, for the orchestrator: the body's `## Forward-carry` still describes the destination ("the lane holding ...", "roster carries the orchestrator appends") and does not name the group. Add `R10-MUTATION-ANCHOR` in `dev/programme/rosters/wave-r10-groups.json` to the body. Editing the body does not move the head. The carried count of 123 is a pre-merge figure: I count 139 `killed_by: tests/entities.py` pins at this head, as round 3 did. The brief tells its fixer to re-derive the count at its merge base, so the stale figure misleads no one.

## Measured at this head

- Step 1, mutation proof of this round's pin (`ledger.py:186`), with worktrees at b9f72cb10 (`ev/diff-mut.txt`, `ev/diff-nul.txt`, `ev/features-*.txt`):
  RESULT m0   tests/features.py ALL 4198 FEATURE CHECKS PASSED rc=0
  RESULT mut  `if dt >= 0:` 1 of 4198 FAILED: "an interval of no length settles no hours: the stored coverage takes no sample" [{'settled_hours': {'sum': 0.0, 'count': 1}, ...}] rc=1
  RESULT null `if 0 < dt:` ALL 4198 PASSED rc=0, so the kill is real and reads the zero-length sample
  The pin file `ledger.py/MonthlyLedger.observe_spot_and_settle_savings.CMP_BOUND.f0f29f9a.json` names `killed_by: tests/features.py`, as the body says.
  - M0 to M16 were not re-run. Production code is unchanged since round 1's run, which killed all 16, and rounds 2 and 3 confirm that.
  - The typing_ruler BOOLOP mutant was not re-run. CI `typing` is green.
- Step 2, the fixer's own harness (disclosed; the finding had no committed harness). I ran `r10_sav_baseline.py` at the head and at the merge base fa5026c42, with the harness copied into the base tree (`ev/harness-{head,base}.txt`):
  RESULT head transient 2.06 kW x4, spread 0.00 SOUND; base 0.00/6.00/6.00/0.00, spread 6.00 DEFECT
  RESULT head cost row 15.0 = receipt 15.0 SOUND; base 3.0 vs 15.0 DEFECT
  RESULT head coverage scale 28.00 SOUND; base 2.80 DEFECT
  RESULT head null 12.34 % (thermostat 128.4, plan 112.6 kWh, room 18.72 vs 20.44 C) DEFECT; base 43.76 % (201.0 / 113.0) DEFECT
  RESULT head "defect 1: null"; base "defect 4"
  These match the body exactly. The null is DEFECT by design, and its three terms are carried to R10-SAV-COMFORT and R10-ADVISOR (round 2).
- Step 5: VERSION, the manifest, RELEASE_NOTES.md and card_claimed_drift.txt show no three-dot diff (`ev/version.txt` is empty).
- Step 13: `git merge-tree --write-tree origin/main(b87e8f19b) b9f72cb10` exits 0 with empty stderr (`ev/merge-tree.txt`).
- Step 11, CI at this head, read from the check-runs API (`ev/checkruns.tsv`): 48 runs, all completed. 32 succeeded, 15 were skipped and 1 failed.
  - The failure is `delivery-status` (117831533983): "DELIVERY STATUS OVERDUE ... 3 overdue". The overdue rows are #2413, #2412 and #2407, all main's records (`ev/ci-delivery-status.log`). By step 11 it is not this PR's red, and the body answers it.
  - `pr-contract` 117832268980 started at 00:23:50Z, after delivery-status concluded red at 00:20:48Z, and it succeeded. Its body check prints `record red-history 46 commit(s) ... delivery-status, fast (3.14), mutation, nightly-ha (stable), wave-script` (`ev/ci-pr-contract.log`). The body's `## Red checks` answers all five.
  - `mutation`, `fast (3.14)`, `typing` and `closures` all succeeded. Round 3 read the mutation lane's log: it evaluated real mutants and was not INCONCLUSIVE.

## Not verified by me

- The golden drift with claims, the structure rows and the archscore dS. I cite these from CI (env-matrix, arch-score and budget-raise-gate are green) and from round 3.
- `r10_sav_null_terms.py`, which was not re-run this round. Round 3 reproduced it at this same head.
- Step 6, other configurations. Production is unchanged, so round 2's 12/12 transient sweep carries.
