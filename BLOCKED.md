# BLOCKED: r11-repair-3883 body (CARRY-LANDED)

Code head: handoff/r11-repair-3883 at 9740b9e336d8d845e61d9ce2d6f0813daa27c2a1 (prepr.sh rc=0 with this body). The refused body is kept at handoff-wip/r11-repair-3883-body 6889aa5f8122be885823a5ffffa69af9eb373d43.
#3930 is handed off: handoff/r11-repair-3930 16e9972f8bc88559a6f243c3991130705d8b07ff, handoff-body/r11-repair-3930 b7d9557eb057cb4b7c22ea39bd7d2b94fef53bbd.

Question: the two carries below sit on #3883's body from earlier rounds and are on no roster branch this seat may write; fold them and re-run `bash tools/audit/seat/body_push.sh r11-repair-3883 <body>` from the code head.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: no group at 9740b9e336d8, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-OWNER-STEP-KICK body item ba8f0ab3: not in its brief or carries: "- T11 pin owed by R11-OWNER-FROST-HOLD's carry (roster item c22c0c0e): whether a frost-hold entry af"
CARRY-MISSING R11-OWNER-STEP-KICK body item f6ad2e1b: not in its brief or carries: '- fixer.md: cost: two fixer seats built R11-OWNER-STEP-KICK. Their heads `58a605d3a6` (the other loc'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-repair-3883-body 6889aa5f8122be885823a5ffffa69af9eb373d43
```
