Fix review: merge c391823f01f996bb4324815e31424657cd311a20

bus-nonce: b1f074f8ad017fb287185f2440251aee

Round: this is the third review of this PR (the body records a round-1 block at d7b25eca and a round-2 repair at be2cfbef5). It is before the fourth, so no re-cut is owed.

## Evidence
- Measured head: c391823f01f996bb4324815e31424657cd311a20 (ev/HEAD.txt).
- `git merge-tree --write-tree origin/main HEAD` exits 0; the only marker is `LEDGER-MERGE: resolved tests/closures.json`, the merge driver's own resolution.
- VERSION, the manifest and RELEASE_NOTES are not in the three-dot diff. No golden or claim file is touched.
- `merge_train.py classify <head> --pr 3305` printed `GREEN ... pending: none red: none`, rc 0 (ev/classify.txt). CI's heavy runs are cited, not re-run.
- Self-tests at the head all pass: `policy_lint.mjs --self-test` (93 errors, 276 pins), `review_packet.py --self-test` (72 checks), `merge_train.py --self-test` (509 checks).
- Hand mutants on policy_lint.mjs, each followed by `--self-test`, each restored (`git status` clean). All three exit rc=1 with a FIXTURE VACUOUS line:
  - `redOwed` returns true unconditionally (m1): FIXTURE VACUOUS, the stub tree did not answer.
  - `requiredFromTrain` drops the `r.status !== 0` check (m2): FIXTURE VACUOUS, a refused read must leave every red owed.
  - The `redOwed` filter is disabled in `checkPrBody` (m3): FIXTURE VACUOUS, the stub tree did not answer.
- The unmutated self-test is rc 0 (ev/base-selftest.txt).
- Red checks (step 11): the body names every red it records, with a detector or a finding. The head's red `gate` and `pr-contract` runs are answered there, and at the head every required check concluded success.
- Class enumeration: the readers of `## Red checks` are policy_lint (the one owner), prepr.sh, record_row.py, review_packet.py and ci_predict.py. The last three go through policy_lint or only mention the heading in text. The spawned-program closure is pinned by the new `_PCR` entities rule, with a null control, and pr-contract restores the base copy of that closure.
- The three entities.py failures the body cites (coverage-cache reuse, release ZIP, Pages probe) were not re-run. I did not re-derive that figure; I cite the green CI `tests / fast` and `gate` instead.
- The body's other figures that I did not re-derive (the 17 min recording, the 1144 s mutant wall, the 24-mutant list) are not relied on.
- Policy files `dev/governance/rules/defect-root-cause.md` and `dev/governance/roles/fix-review.md` change: this merges only on the owner's approving review (the body's Approval section says so).

## Findings
none
