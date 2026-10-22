Roster for round 10, twelfth landing (after #2603). It registers three groups from the install-rate-limit record and the nightly heartbeat residual, revises one of them after the refutation at review/2606, and appends two carries. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `aa38bdd5f65ce4327c6def865107d17864bf7926`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `6c8903a44ca294bb5c59e440d163eacf13128eab` (which holds the #2603 merge) is `33138bc2f49b85f4f94c9edfad422789ef00eee3`, the roster as #2603 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 140 insertions and 2 deletions over 8 commits (`git rev-list --count 33138bc2f..aa38bdd5f` prints 8), each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 6c8903a44ca294bb5c59e440d163eacf13128eab 33138bc2f49b85f4f94c9edfad422789ef00eee3 -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote is overwritten. The `removed` list below is empty.

## Figures

The eight ops, with their roster commits and sources:

- `459ef684a` `append-group` `R10-RCA-INSTALL-RATELIMIT` (lane IN, kind rca, size S, wave 1, in-review): source the RCA return `handoff-body/r10-rca-install-ratelimit` at `28a20e95`; code at `handoff/r10-rca-install-ratelimit` `0a8c4523a`.
- `9326f8a4e` `append-carry` `R10-FLY-GH-READ-RETRY`: same record; an exhausted hourly bucket returns a 403 that is not transient, so a retry waits for the named reset and never loops.
- `d9f33a0f2` `append-carry` `R10-CI-LAYOUT-P2`: same record; the record job's API budget is owned by `R10-RECORD-API-BUDGET`.
- `2a64d2b5e` `append-group` `R10-RECORD-API-BUDGET` (lane IN, kind instrument, size S, high, wave 1, queued, after `R10-RCA-INSTALL-RATELIMIT`): source the same record, orchestrator decision O-1, and orchestrator option (a): the brief's first sentence cites `0a8c4523a` so the record path resolves at a cited ref.
- `7ab485ae9` `append-group` `R10-NIGHTLY-HB-RESPAWN` (lane F, kind instrument, size S, wave 4, queued, after `R10-NIGHTLY-PYSPY-RETRY`): source #2605's verdict review/2605 `f00094d17`, finding 2, and orchestrator decision O-4 (mandate 6329234399).
- `9619aa9b1` `edit-brief` `R10-RECORD-API-BUDGET`: source review/2606 `3f3e5bda1`, which refuted the 1,000/hr bucket; M3 becomes conditional on the measured limit and the bucket size is called unmeasured.
- `8a64c46d2` `append-carry` `R10-RECORD-API-BUDGET`: source review/2606 `3f3e5bda1`; the harness `record_api_calls.sh` must refuse a zero on a non-empty window and a partial mode.
- `aa38bdd5f` `append-carry` `R10-RECORD-API-BUDGET`: source review/2606 `3f3e5bda1`; M1 and M2 pull against each other, so measure the run count after both.

Measured with `B=origin/main`, `H=aa38bdd5f`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 148 and 151 groups, none removed, new `R10-NIGHTLY-HB-RESPAWN`, `R10-RCA-INSTALL-RATELIMIT`, `R10-RECORD-API-BUDGET`, changed `R10-CI-LAYOUT-P2` and `R10-FLY-GH-READ-RETRY`. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/6c8903a44ca294bb5c59e440d163eacf13128eab/check-runs` (main's tip), failures, cancellations and timeouts only: `rerun-stale-contract` 10 cancelled; no failure. This diff changes the roster and one delivery row, and that workflow does not read them. Checks at this PR's own head are read by CI.

## Forward-carry

none

## Friction

none
