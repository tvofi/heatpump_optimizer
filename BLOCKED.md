# BLOCKED: r10-hotfix-nonrequired-reds-2

Code head 790e98bde8d7a162b5be137af83317ea4c8bc098 is pushed to refs/heads/handoff/r10-hotfix-nonrequired-reds-2; `tools/pr/prepr.sh` at that head: `PRE-PR: 790e98bde8d7a162b5be137af83317ea4c8bc098 ... rc=0`; `git merge-tree --write-tree origin/main HEAD` clean.

`bash tools/audit/seat/body_push.sh r10-hotfix-nonrequired-reds-2 <body.md>` exited 1:

    review_packet: REFUSE hot-file: #3304 holds an unboarded merge verdict and shares tools/audit/seat/orchestrator_tick.py
    review_packet: REFUSE hot-file: #3245 holds an unboarded merge verdict and shares dev/audit/harnesses/r10_seat_selftests_mutants.py
    review-packet handoff: R10-HOTFIX-NONREQUIRED-REDS-2 at 790e98bde8d7, 0 carries, 2 refused
    body_push: REFUSED REVIEW-PACKET
    body_push: refused body kept at handoff-wip/r10-hotfix-nonrequired-reds-2-body a8f25b9672ace7b4fb56bab41d97024c7bbf51c1

The brief requires the orchestrator_tick.py change, so the #3304 overlap cannot be routed around in this seat. The unboarded state is the train's (the cloud container has no HPO_BUS_TRAIN_STATE, so it reads every merge verdict as unboarded). Once #3304 and #3245 are boarded or merged, re-run body_push.sh on the kept body. The step ref is left in place because the handoff did not complete.
