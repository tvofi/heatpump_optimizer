# BLOCKED: r10-outside-disinfection-setpoint

Code: f4ae78eb64bf6ecb7add66138b1b13e82f319c4b (pushed to handoff/r10-outside-disinfection-setpoint; prepr.sh rc=0 with the body).
Body: kept at handoff-wip/r10-outside-disinfection-setpoint-body b5bed50a62f57147865b07d86d7b16ef935bbfaa.

Question: the two own-group carries below need to land on the round's roster (carry_audit.py land-ops); fold them and re-run body_push.sh?

```
review-packet handoff: R10-OUTSIDE-DISINFECTION-SETPOINT at f4ae78eb64bf, 0 carries, 0 refused
CARRY-MISSING R10-OUTSIDE-DISINFECTION-SETPOINT body item 7052beca: not in its brief or carries: '- The no-cycle write rounds an off-step everyday set-point to the nearest step, which can exceed `dh'
CARRY-MISSING R10-OUTSIDE-DISINFECTION-SETPOINT body item 9ac8c410: not in its brief or carries: '- Bounding a cycle by the hard maximum leaves an off-step disinfection temperature above the everyda'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-outside-disinfection-setpoint-body b5bed50a62f57147865b07d86d7b16ef935bbfaa
```
