# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED), PR #3358 at 577c6974

Question: the relay folds the carry below onto the round roster (R10-FLY-GH-READ-RETRY) and re-runs body_push.sh r10-combi-tank-pr with the refused body kept at handoff-wip/r10-combi-tank-pr-body 08d8979dc1bab4752af835732da9c397daf17311.

body_push.sh output (tail):

    review-packet handoff: no group at 577c69742059, 0 carries, 0 refused
    CARRY-MISSING R10-FLY-GH-READ-RETRY body item d678abfc: not in its brief or carries: '- `tools/ci/codescan_wait.py` `settled()` fails closed on every partial re-run of a code run that ow'
    CARRY-LANDED: 1 missing
    body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
    body_push: REFUSED CARRY-LANDED
    body_push: refused body kept at handoff-wip/r10-combi-tank-pr-body 08d8979dc1bab4752af835732da9c397daf17311

State:
- Code head unchanged: handoff/r10-combi-tank-pr = 577c6974205926e7dbaa178b91af96a229ea02f3 = PR head.
- tools/pr/prepr.sh with the body at that head: `PRE-PR: 577c6974... rc=0`.
- The pr-contract red (job 129342618295, run 42635950938 attempt 4) is not a body refusal. The step `Wait for code scanning` failed: `FAIL closed: this run's codeql jobs were not listed finished after 600 s`, and the body steps were skipped. On a re-run attempt, the carried-over codeql jobs are listed without `steps`, and codescan_wait.settled() requires the `Perform CodeQL Analysis` step row (measured, with control, in the body's Forward-carry item d678abfc). Re-running pr-contract on the code run cannot turn it green; an edit run from the body PATCH is the repair.
- The live body already passed the contract offline (policy_lint 0 errors); the new body adds the pr-contract answer under ## Red checks and the d678abfc carry. Both pass offline: policy_lint `PR-BODY: 0 error(s)`, carry_audit 5/5 routed.
