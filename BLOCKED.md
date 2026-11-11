# BLOCKED

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED); the relay should fold the two carries below onto the roster and re-run body_push.sh. The code is pushed at handoff/r10-tick-residue (88a5ebe1415d); the body is kept at handoff-wip/r10-tick-residue-body.

```
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-TICK-RESIDUE at 88a5ebe1415d, 25 carries, 0 refused
CARRY-MISSING R10-TICK-RESIDUE body item a5ff6af4: not in its brief or carries: 'Not built in this pull request; they stay open as carries of R10-TICK-RESIDUE in dev/programme/roste'
CARRY-MISSING R10-TICK-RESIDUE body item 68d1bc79: not in its brief or carries: 'Carry 0: not built in this pull request; stays open in R10-TICK-RESIDUE. Carry 1: not built in this '
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-tick-residue-body ca77c2de6dab2f3a1c15525801434aa8fe2d8708
```
