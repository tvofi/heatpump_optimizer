# BLOCKED: r11-repair-3870b

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED) on a carry this repair did not write; the relay folds the carry onto the round's roster and re-runs body_push.sh r11-repair-3870b on the body at handoff-wip/r11-repair-3870b-body.

Code head: a268a50d12978e067c9d87d5b1bfc72692974085, pushed to refs/heads/handoff/r11-repair-3870b (one commit on PR #3870's head a9c10725f6: D5 seat s7 re-cut to tests/features.py; both instrument-self-tests steps pass at it and fail at a9c10725f6).
Scoped prepr: PRE-PR: a268a50d12978e067c9d87d5b1bfc72692974085 0000000000000000 rc=0 elapsed=118s

body_push.sh output:
```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: no group at a268a50d1297, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-OWNER-FAULT-HOLD body item b9c2dda5: not in its brief or carries: "- FAULT-HOLD's text: when FAULT-TEXT lands first, the pre-fill and docs Fault alarm rows name the fr"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-repair-3870b-body c9fac1e5784db012f5d280c36e32c956c945ab41
```
