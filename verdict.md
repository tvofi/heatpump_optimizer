Fix review: merge 590b3abade1db9975cf93d17eaabc16905f497ee

bus-nonce: b830bd0eea4d7b4018c7b65cf42c4983

Round 3 scoped delta re-check, head 590b3abade1db9975cf93d17eaabc16905f497ee, measured from a detached worktree at that head.

## Findings

- Carry 7's 5 s cost cap on a strings.json-only diff is unmeasured (the claims generator needs scipy/homeassistant, absent here); the body says so and does not claim it. Carry: R10-PREPR-CAP
- Round-1 finding 3 (the cap) is the same item as above; round-1 finding 2 (the body's three-dot figure) is fixed, see Evidence. Carry: R10-PREPR-CAP
- Carries 8-27 are owed by part 3. Carry: R10-PREPR-CAP

## Evidence

- Clean head: bash tools/pr/prepr.sh --self-test prints 460 passed, 0 failed, rc 0, and git status --porcelain is empty afterwards (null control for the mutants).
- Round-1 mutant A (EARLY_REDS_RC=0 in step 1a2): 457 passed, 3 failed, rc 2; the three step 1a2 rows fail. Killed.
- Round-1 mutant B (--pr-branch guard replaced by if false): 458 passed, 2 failed, rc 2; the two --body-check --pr-branch rows fail. Killed.
- Own mutant C (WB=$DABS, restoring the write into the tracked fixture dir): 459 passed, 1 failed, rc 2; the porcelain-unchanged row fails (it shows ?? tools/policy/fixtures/policy-rot/prepr/wiring-body.md). Killed, so the clean-worktree assertion has teeth; its null control row (a write into the tracked dir changes porcelain) passes at the head.
- r3 repair: the body file is under WB=$(mktemp -d), which the self-test's mktemp wrapper places in ST_ROOT, removed by the existing EXIT trap at prepr.sh:1726. The diff adds no second EXIT trap in the self-test. Rows' stub rcs (1/0/3) and the body check running from this tree are unchanged.
- Body figure: git diff --stat origin/main...HEAD prints 3 files changed, 181 insertions(+), 26 deletions(-), matching the body.
- Standing checks: git merge-tree --write-tree origin/main HEAD exits 0; python3 tests/structure.py prints STRUCTURE RATCHET PASSED; no change to golden, claim files, VERSION, manifest or RELEASE_NOTES (empty three-dot diff); the delivery row dev/programme/delivery/3150.md is in the diff; scoped gate prints MODE: SCOPED -- 0 script(s) run, 33 scoped out.
- Red checks: the body says none; CI at this head is GREEN (merge_train classify rc 0: pending none, red none). No red check owes an answer.
- Round: this is round 3; a fourth owes a re-cut.
- Not re-run: CI's heavy gate and mutation lanes, cited from CI.
