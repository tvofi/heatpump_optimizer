Fix review: merge 8be64a110fa4e741889920c4eff2b6b4cb99cf3a

bus-nonce: 1104b1894311529b632f78e522883a4d

Round 5 (fix-review.md, main 64b0ae690; roles/ unchanged between merge base and origin/main). Code head unchanged since round 4, which verified the four carry controls at roster 1dc0151de and blocked only on step 11. This round re-takes step 11, step 13 and step 12, and spot-checks the step-1 mutants.

Step 11, red checks at this head (commit check-runs API, filter=all, 70 runs, all completed; ev/checkruns_all.json):
- arch-score 118114889124 and 118124086255: red. Each log ends `gh: API rate limit exceeded for installation ... (HTTP 403)` in the body-fetch step. Re-runs 118129031265, 118129773400 and 118129779749 are success at this head, and so is a later 118139886136. Named and answered in the body's `## Red checks`.
- env-matrix 118114889280: red, with a single FAIL, `pr / nothing skipped in a full clone -- skip required-contexts the GitHub API is unreachable`, and 15 of 16 held. Its re-run 118130669121 is success. Named and answered.
- validate-hacs 118114888472: red, `aiogithubapi.exceptions.GitHubRatelimitException: API rate limit exceeded for installation`. Its re-run 118129759636 is success. Named and answered. (The body lists re-run ids only for arch-score. The env-matrix and validate-hacs re-runs above are green but not named. This is noted, not blocking.)
- nightly-status 118114887989: red. This is main's lane: the diff does not touch nightly_status.py or record-autofix (0 diff lines naming nightly_status). The body names it with the main-side cause.
- pr-contract: 8 red runs between 14:25 and 15:10. The latest, 118139880936 (started 15:12:18Z), is success. It started after every other red concluded (the last was pr-contract at 15:10:50Z; every other workflow concluded by 15:09:06Z, apart from the green arch-score 118139886136 that concluded at 15:13:20Z), and its log prints `clean no refusal` and `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted`.
- Every answer gives a cause and either a cheaper detector or the finding that none exists (it names R10-FOLLOWER-DEBOUNCE and R10-CI-LAYOUT A1). Step 11 is satisfied.

Step 13: `git merge-tree --write-tree origin/main 8be64a11` exits 0 (tree ca4fcaab3; ev/merge-tree.txt). origin/main is 3 record commits ahead of the PR base e59f0291a.
Step 5: VERSION, manifest and RELEASE_NOTES are untouched (0 files).
Step 1 spot-check, from a worktree at the head:
- Hand mutant: selftest_wiring.py:103 `return 1 if unwired else 0` changed to `return 0` gives `15 checks, 1 failed` rc=1. The unmutated file gives `15 checks, 0 failed`, and `--check` gives `37 self-testing, 37 wired, 0 unwired`, matching the body.
- Finder's harness subset `r10_seat_selftests_mutants.py S30 S04 S04U W1 W2`: all KILLED, `RESULT survivors=0`, and git status is clean afterwards (ev/harness_subset.txt). W1 and W2 print 38/37/1 and 37/36/1, as the body says.
Step 12: the PR head re-read before writing is 8be64a110fa4e741889920c4eff2b6b4cb99cf3a.

RESULT step11=answered merge_tree_rc=0 S30=KILLED survivors=0
