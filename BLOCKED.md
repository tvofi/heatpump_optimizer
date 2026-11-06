# BLOCKED: r10-train-merge-loop round 2, body_push refused on the part-2 carry destination

The code head is pushed: handoff/r10-train-merge-loop = 23d83cad918b2310245f9fd1902a4b482befbf78 (merge base and origin/main dc0a170b6, unmoved).

The body has not been handed off. `bash tools/audit/seat/body_push.sh r10-train-merge-loop <body>` exits 1:

    REFUSE carry: BAD-DEST body item f4bc638f: R10-TRAIN-MERGE-LOOP-2: R10-TRAIN-MERGE-LOOP-2 is not a group of the roster -- CARRY-AUDIT: 9 finding item(s): 2 routed, 0 unrouted, 7 bad destination(s), at origin/handoff/audit-r10-roster f85b3b4d5
    body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again

The refused body is kept at handoff-wip/r10-train-merge-loop-body 48e0fe8651b06f46c322d49cc2e7782fca983b90 (PR-BODY.md). Every other prepr step is ok or skip. The seven bad destinations are carries 3, 6, 7, 8, 9, 16 and 17, each routed `Carry: R10-TRAIN-MERGE-LOOP-2` as the dispatch ruled.

Question: will the orchestrator land the R10-TRAIN-MERGE-LOOP-2 group on handoff/audit-r10-roster now, rather than after #3239? Once it is there, re-run `body_push.sh r10-train-merge-loop` on the kept body with no edit. The alternative is to rule another destination for the seven carries. The dispatch says the group is applied once #3239 merges. body_push's carry refusal cannot be passed before then, and this seat does not work around it.
