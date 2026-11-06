# BLOCKED: r10-train-merge-loop body-only continuation

The renumbered 1-based body clears the review packet: `review-packet handoff: R10-TRAIN-MERGE-LOOP at 23d83cad918b, 19 carries, 0 refused`. `prepr.sh --body-check` is ok.

body_push.sh then refuses at the carry-landing check (`carry_audit.py --roster-ref origin/main landed`): `CARRY-LANDED: 7 missing`, for the seven R10-TRAIN-MERGE-LOOP-2 forward-carry lines (Carries 3, 6, 7, 8, 9, 16, 17).

Cause: the check matches a body item by its item id or the topic token against the destination group's brief and carries on origin/main and the round branch. origin/main's roster has no R10-TRAIN-MERGE-LOOP-2 group. handoff/audit-r10-roster has it (7 carries, citing #3242), but its text holds neither this body's item ids nor `r10-train-merge-loop`.

Question for the orchestrator: land the seven carries on the roster branch (`carry_audit.py land-ops` prints the append-carry ops for the body at handoff-wip/r10-train-merge-loop-body), or merge the roster branch to main, then re-run `body_push.sh`. The refused body is kept at handoff-wip/r10-train-merge-loop-body. I did not use HPO_HANDOFF_LANDED or edit the roster.
