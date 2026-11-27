# BLOCKED: r11-repair-3872

Question: the relay folds the two carries below onto the round's roster (carry_audit.py land-ops) and re-runs body_push.sh r11-repair-3872; this seat may not write the roster.

Code head: ae282a8eaeb2347f94fe676cba6fa8eceed26799 at handoff/r11-repair-3872 (and handoff/r11-owner-fault-hold-repair2), prepr.sh rc=0 (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1). Refused body kept at handoff-wip/r11-repair-3872-body 7ffcab1d68ffa85ec27a764e6e61c4a2518bbc80.

body_push.sh output (exit 4):

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: no group at ae282a8eaeb2, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-OWNER-MODE-LEGS body item b41faa3f: not in its brief or carries: '- Carry 0 (from R11-OWNER-MODE-LEGS, body item 411606ae, the pin "the fault hold wins with a young l'
CARRY-MISSING R11-OWNER-FROST-HOLD body item 021db87b: not in its brief or carries: "- Carry 2 (from R11-OWNER-FROST-HOLD, body item 0846c1b4, the composition owed by this group's merge"
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-repair-3872-body 7ffcab1d68ffa85ec27a764e6e61c4a2518bbc80
```
