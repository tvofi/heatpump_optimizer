# BLOCKED: r10-ci-edit-runner body

Code head daa600e64c477630674f534e2b7d9e82a7e2e286 is pushed to handoff/r10-ci-edit-runner. The earlier refusal was a code conflict: the head did not merge into main (tools/ci/gate.py, against r10-gate-busy-defer-3). It was merged and reconciled (every deferral publishes at once; the code run's gate still re-runs the latest deferring body run), the gate and prelude self-tests pass, and prepr.sh's code steps were all ok.

The body (kept at handoff-wip/r10-ci-edit-runner-body) is still refused by body_push.sh on one arm only:

    CARRY-MISSING R10-HOTFIX-GATE-BUSY-DEFER body item 27233708: not in its brief or carries

The finding is real (a body run numbered below its code run is shadowed by the code run's own units), and its carry has to land on origin/handoff/audit-r10-roster, a branch this seat may not write. Needed from the orchestrator or roster seat:

    python3 tools/audit/carry_audit.py land-ops --body <body.md> --topic r10-ci-edit-runner

(its one op is `append-carry R10-HOTFIX-GATE-BUSY-DEFER 'From r10-ci-edit-runner, body item 27233708: ...'`), applied to the roster; then re-run `bash tools/audit/seat/body_push.sh r10-ci-edit-runner <body>` with the kept body.

Not re-taken after the merge: the mutation proof M5-M8 and the replay figures in the body were measured on the wait-based gate; the body says so. The diff-mutant step was skipped (MUTANT_CMD unset).
