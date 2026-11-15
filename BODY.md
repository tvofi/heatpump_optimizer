Hotfix (R11-HOTFIX-POLICY-DOCS-TIMEOUT, triage dev/programme/triage/r10-round-end.md#P786): `policy-docs` timed out at its 5-minute bound while field coverage ran, turning the required `gate` red on #3451 and on main b046b22d. One line: `timeout-minutes` 5 to 10 in `.github/workflows/governance.yml`. Root cause: dev/audit/rca/R10-RCA-FAMILY-POLICY-DOCS-TIMEOUT.md (state d, passes the cost test: zero standing seconds on a run that finishes). Code-owned path: needs tvofi's approving review or the mandate.

## Head

4104762b883314e92a130a482bea71ae5fd813d0 (merge base b3831ff64e, origin/main at 2026-11-15).

## Mutation proof

n/a: a workflow timeout value has no production predicate or check to mutate; the only check reading it is the job itself, and the RCA's detector is the measured wall below.

## Null control

Unmodified tree: job 132742498619 (run 43691296618, main b046b22d) started 07:45:30Z, completed 07:50:43Z, conclusion cancelled; step "Refuse a governance check input field no check reads" started 07:47:23Z and was cancelled at 07:50:40Z, 3 min 17 s in. Head's change leaves a run touching no listed input unchanged (the step prints "skipped").

## Figures

- Job wall on the instance, command `actions_get get_workflow_job 132742498619` (started_at to completed_at): 5 min 13 s against a 5-minute bound, cancelled; against the new bound of 10 min that leaves about 4 min 47 s of margin even though the step had not finished.
- `bash tools/pr/prepr.sh` at 4104762b883314e92a130a482bea71ae5fd813d0: rc=0, MODE: SCOPED, field coverage ok.
- The other two instance walls (#3451 run 43688486622; stamp 13cbe48d, job passed at 4 min 58 s) are quoted from the RCA, not re-measured here.
- Owed demonstration not done by this seat: a green run at the head. The pull request's own policy-docs run is that demonstration, since the diff touches the workflow and no step input.

## Red checks

none

## Forward-carry

none

## Friction

none
