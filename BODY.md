open_pr.sh closed a freshly opened pull request when its row push was refused by a host-environment red (PR 3508). `op_close_unrowed` now asks `op_host_refusal` first: when every REFUSE row of the p2 log is prepr's `self-test` step (plus app_push's own summary line) and the PR's diff against origin/main leaves `tools/pr/prepr.sh` and `tools/audit/prepr.sh` alone, the PR stays open as `opened,PR=N`, one `open_pr: ROWLESS` line names `update_pr.sh <branch> - <body>` as the owed row, and the exit stays non-zero. Any other refusal still closes. Alternative rejected: classifying in `pr_push_failed` (shared with update_pr.sh, which has no PR to close).

## Head

4b91c2f9f705b76db9e041e1c88ad12bb79147f8

## Mutation proof

Deleting the `# mut:hostother` line (the other-REFUSE check) makes `pr_args.sh --self-test` fail "mutant mut:hostother" is the arm that pins it: a mixed log then leaves the PR open. Deleting `# mut:hostguard` leaves a branch touching prepr.sh open; the `mut:hostguard` arm kills it. The always-leave-open shape is the hostother mutant; the mixed-log and body-contract null-control arms kill it.

## Null control

At origin/main (before the fix) the new arm "a row push refused only by prepr's self-test step leaves the PR open" FAILS (the PR is closed), as do both mutant arms: `pr_args.sh --self-test` printed 3 failed. With the fix: 211 checks, 0 failed. Null controls in the suite: a body-contract REFUSE row closes; a self-test row beside another REFUSE row closes; a self-test refusal on a branch whose diff touches tools/pr/prepr.sh closes.

## Figures

`none`

## Red checks

none

## Forward-carry

none

## Friction

none

prepr.sh ran with PREPR_SKIP_CLOSURES=1 (cloud environment trap in the brief); rc=0 at the head above. tests/structure.py passes; it reports no row for tools/audit/seat, and the budgets file has no key naming it.
