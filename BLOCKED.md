BLOCKED: R10-CARRY-RESIDUE round 3 body -- the carry is not yet in the group's carries on the roster branch

Code head: bcbdcfb377d78433b122370bb21dc29b66371cfa (on handoff/r10-carry-residue, unchanged). The round-3 body is written and kept at
refs/heads/handoff-wip/r10-carry-residue-body (1665f1309), every figure re-measured at that head.

`bash tools/pr/prepr.sh --body-check BODY.md`: PR-BODY: 0 error(s); `carry_audit.py check`: 1 routed, 0 bad destination(s)
(R10-CARRY-RESIDUE-2 resolves on the roster). `body_push.sh` still refuses:
  CARRY-MISSING R10-CARRY-RESIDUE-2 body item fac7779b: not in its brief or carries
  body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops)

The group now exists, but the carry text is not in its carries. `carry_audit.py land-ops --body BODY.md` prints the op for standing-roster
(a fixer may not edit the roster):
  append-carry R10-CARRY-RESIDUE-2 'From this pull request, body item fac7779b: `dev/governance/roles/standing-tick.md` should name the `CARRY:` line beside its ancestor-recarry test; a policy edit, owner approval before merging. Carry: R10-CARRY-RESIDUE-2 (items fac7779b)'
Unblock: land that op with roster_edit.py, then run `bash tools/audit/seat/body_push.sh r10-carry-residue <body>` from a checkout at bcbdcfb with the kept body (git show origin/handoff-wip/r10-carry-residue-body:BODY.md).
