# BLOCKED: r11-repair-3882

Code is pushed: refs/heads/handoff/r11-repair-3882 at 0e4f7f97ed55bdace7ae233316e1618010e7a9cd (scoped prepr: `PRE-PR: 0e4f7f97ed55bdace7ae233316e1618010e7a9cd 00000000000000000 rc=0`). The body is kept at refs/heads/handoff-wip/r11-repair-3882-body. body_push.sh exited 4; the carries land on the roster, which this seat may not write. Its output:

```
fill-red: `## Red checks` already names mutation; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: no group at 0e4f7f97ed55, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-OWNER-MODE-LEGS body item 4f3e2ffe: not in its brief or carries: '- Carry 0 (roster item 71b98dc2, from R11-OWNER-MODE-LEGS): its precondition, `_kept_leg`, is not on'
CARRY-MISSING R11-OWNER-FAULT-HOLD body item b30b5660: not in its brief or carries: "- Carry 1 (roster item 033699bc, from R11-OWNER-FAULT-HOLD): FAULT-HOLD's module is not on main (`gi"
CARRY-MISSING R11-OWNER-STEP-KICK body item 3bb11bf7: not in its brief or carries: '- Carry 2 (roster item 50f1ee5c, from R11-OWNER-STEP-KICK, T11, design carry frost-entry): STEP-KICK'
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-repair-3882-body b8cf3762fe974a7ad38580164b16da3841952e6f
```
