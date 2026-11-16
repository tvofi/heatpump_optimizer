# BLOCKED: r11-pre-handoff-bookkeeping

body_push.sh exited 4 at code head 047ea3fddfdf4e90227010b4dacc2d38ec0b9f0a; refused body kept at handoff-wip/r11-pre-handoff-bookkeeping-body 49082865cb3f12a22e694c9310df5762f9fc809a. Its output:

```
CARRY-MISSING R11-PRE-PARALLEL-PIPELINE body item 79b11b82: not in its brief or carries: '- Step replay now runs the closure-only readers too, so `prepr.sh` step 6d on a diff touching a wide'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-handoff-bookkeeping-body 49082865cb3f12a22e694c9310df5762f9fc809a
```
