# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED)

Code head: df4af48ad90561c6259435441507f1451cad3913 (pushed to handoff/r10-gate-defer-barrier; prepr.sh rc=0 at this head).
Refused body kept at handoff-wip/r10-gate-defer-barrier-body 82c3f715ef0c1c503cc8c39b6f6082f12ed78b52.
The carry lands on the roster this seat may not write; the relay folds it and re-runs body_push.sh.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-GATE-DEFER-BARRIER at df4af48ad905, 11 live, 11 dispatched carries, 0 refused
CARRY-MISSING R10-CI-PRIORITY-PAUSE body item 6e06de7f: not in its brief or carries: '- The three residuals under `## Re-cut` (a gate-conclusion read that bypasses `classify`, an empty `'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-gate-defer-barrier-body 82c3f715ef0c1c503cc8c39b6f6082f12ed78b52
```
