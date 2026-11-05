Fix review: merge 4e4bb291b503be5abac829a6a068358ffdea1091

bus-nonce: 26b510e24ba766ede3e3e8a2a4e138e4

## Head

CI-only re-check of 4e4bb291b503be5abac829a6a068358ffdea1091 under the prior block (probe/rev-3167-4c809e02, ci-red: gate cancelled). refs/pull/3167/head and the PR API head are both still 4e4bb291b503be5abac829a6a068358ffdea1091, so the code is the head already reviewed: no code measurement is repeated and the prior mutation proof (ev/prev-mutants.txt) and figures carry.

## Evidence

- classify: `GREEN 4e4bb291b503be5abac829a6a068358ffdea1091 pending: none red: none`, rc=0 (ev/classify.txt).
- Check runs of the head, all pages (ev/check-runs.txt): gate success (01:05:59 and 01:14:01), prelude success, pr-contract / pr-contract success (two runs), budget-raise-gate success (two runs), tests / fast (3.14), coverage, replay, lane-proofs, graders-head-copy all success. Only tests / nightly-status is failure: main-inherited, reads nothing this diff reaches, and is not a required context.
- Body `## Red checks` answers the round-1 red (tests / replay, now success) and states gate and pr-contract were re-run at the new head; both now conclude success.
- Prior review found the code clean (four open_recorder lines pinned, defaults survivor equivalent, merge-tree clean); unchanged.

## Findings

none
