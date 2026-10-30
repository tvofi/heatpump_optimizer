Fix review: merge 5682d74e56315ec90ef394191170147111e35382

bus-nonce: 0c42f6fd29d53dded6005ef51c8f4e36

Round 10 of PR #2925, measured at 5682d74e56315ec90ef394191170147111e35382 (detached worktree). Delta reviewed: 5a1d1e097..5682d74e56315ec90ef394191170147111e35382.

## Findings

- review_packet.py render refuses host-path on a cloud seat (ref_privacy.Identity.of_host). The body already dispositions this. Carry: dismissed: body's disposition stands; no live roster group owns tools/audit/seat/ref_privacy.py and it bites only a cloud seat
- briefs, pr-contract and budget-raise-gate restoring jobs are unpredicted by the graders arm. Carry: R10-FLY-CIPREDICT-RESTORING

## Evidence

- Delta is one authored commit, 7e2346d0e, touching only dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md (2 lines, 2 deletions): line 8 now says the carry lives in the roster group R10-FLY-CIPREDICT-RESTORING, line 247 names the group without the issue number. The other two commits are merges of the code tip and origin/main 2d151411f.
- Zero occurrences of #2952 in the tree at head (git grep), and the PR body's Delta section also names the roster group and no issue number.
- git diff 5a1d1e097 head over tools/pr/ci_predict.py, tools/policy and dev/audit/rca/prepr-head-graders is empty: arm code unchanged, so round 9's acceptance of the code carries.
- Re-ran at head: ci_predict --self-test prints 0 failed; mutants.py M3, M4, M5 print bad 1, 1, 3 with the named FAILs (the unmutated tree is clean). ev/selftest_mutants.txt holds the tail only; M1/M2 were not seen in the captured tail, so those two figures are the body's, not re-derived by me.
- git merge-tree --write-tree origin/main head: rc 0, no conflict. VERSION, manifest and RELEASE_NOTES untouched in the delta.
- Commit messages in the delta carry no Claude footer or trailer.
- CI on head (check-runs API): green on briefs, policy-docs, env-matrix, wave-script, closure-scope, mutation, arch-score, budget-raise-gate, delivery-status, hassfest, hacs, typing, browser, codeql actions/js. Still in progress when read: closures, coverage, fast (3.14), instrument-self-tests, codeql python. Not concluded, so not cited as green. Red: tests / nightly-status only; it is not a required check for this diff and does not block (it reads nothing the diff touches, red on main too), and the body names it.
- review_carry.py prints FRESH-REVIEW because a code-carrying commit is on the branch; the commit is a record edit, reviewed above.
