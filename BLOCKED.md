# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED)

Code head: handoff/r10-standing-contracts-p2 at 5a4161d57647ccdfc82f9cd0e6988abcb81bfaed. Refused body kept at handoff-wip/r10-standing-contracts-p2-body d8be9f0acea71dbc00460af3d149842408447950.

The relay folds the four carries below onto the roster and re-runs `bash tools/audit/seat/body_push.sh r10-standing-contracts-p2 <body.md>`. Each names this group as its destination, pending an orchestrator ruling: the design verdict's fixer note item 22 puts carries 21, 22 and 23 outside the approved design, and the design's destination for carries 9, 12, 13 and 14 (R10-ORCH-LEDGER) is not among this group's valid targets.

body_push.sh output:

    fill-red: the diff adds no unpinned mutation site; nothing written
    ref_privacy (body) ok: no host identity in the body
    review-packet handoff: R10-STANDING-CONTRACTS-P2 at 5a4161d57647, 24 carries, 0 refused
    CARRY-MISSING R10-STANDING-CONTRACTS-P2 body item 70ba2a8b: not in its brief or carries: '- Carries 9, 12, 13 and 14 (the merge-seat retirement and the dispatch beat job) have no live owner:'
    CARRY-MISSING R10-STANDING-CONTRACTS-P2 body item d5bd97f0: not in its brief or carries: "- Carries 21, 22 and 23 (the liveness hook's three arms with their constraints, and pulse.py reading"
    CARRY-MISSING R10-STANDING-CONTRACTS-P2 body item d07e0d73: not in its brief or carries: '- `dev/programme/HANDOVER.md` names four standing seats in its standing-seats bullet; it is updated '
    CARRY-MISSING R10-STANDING-CONTRACTS-P2 body item d6daec6a: not in its brief or carries: '- fixer.md: cost: the layout guard refuses a re-wrapped line that keeps a retired `docs/decisions/` '
    CARRY-LANDED: 4 missing
    body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
    body_push: REFUSED CARRY-LANDED
    body_push: refused body kept at handoff-wip/r10-standing-contracts-p2-body d8be9f0acea71dbc00460af3d149842408447950
