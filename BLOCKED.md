# BLOCKED: r10-roster-write-sweep body push

Code head 2b27bf482e33ab4fd7e1fdb867353a74b8da10a3 is pushed to handoff/r10-roster-write-sweep; prepr rc=0 at it. The body (handoff-wip/r10-roster-write-sweep-body, ba9e796ae398) passes `prepr.sh --body-check`, `carry_audit.py check` (5 routed, 0 unrouted) and the review packet's brief-carries check.

`body_push.sh` then refuses: CARRY-LANDED, 4 missing. Its four `Carry: R10-CARRY-RESIDUE-2` items (carry 4 data, carry 9 data, carry 16 data, plant C6) are not yet in that group's brief or carries on origin/handoff/audit-r10-roster. Landing them is a roster-branch write (carry_audit.py land-ops), which this seat may not make.

Question: the roster seat lands the four carries on R10-CARRY-RESIDUE-2 (or names another live destination), then `bash tools/audit/seat/body_push.sh r10-roster-write-sweep <body>` is re-run with the kept body.
