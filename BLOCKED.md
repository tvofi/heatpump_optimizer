# BLOCKED: r11-repair-3805

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED) on carry body item 1ecbd3b9 (R11-OUTSIDE-HONEST-DHW-RUNS); the relay folds it onto the roster this seat may not write, then re-runs body_push.sh.

Code head: dffa3f7df9d53298155ab326f9879c4d024ea5f8 (pushed to handoff/r11-repair-3805; prepr.sh scoped, PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1: rc=0). Body kept at handoff-wip/r11-repair-3805-body 848d2fc027a510331e90ac6527ecfe890b7f7859.

body_push.sh output:

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review_packet: UNAVAILABLE: git merge-base --is-ancestor b2ce461c origin/handoff/audit-r11-roster: fatal: Not a valid object name b2ce461c
body_push: the review packet's handoff refusals were not run (rc 3, above); dispatch still runs structure and hot-file
CARRY-MISSING R11-OUTSIDE-HONEST-DHW-RUNS body item 1ecbd3b9: not in its brief or carries: '- On the base and the head alike the two-descent solve scores above one of its arms alone on some da'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-repair-3805-body 848d2fc027a510331e90ac6527ecfe890b7f7859
```
