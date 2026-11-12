# BLOCKED: body_push.sh exit 4 (CARRY-LANDED), r10-outside-contributor-cycle repair round 1

Question: none for the owner. The relay folds the carry below onto the roster and re-runs `bash tools/audit/seat/body_push.sh r10-outside-contributor-cycle <body.md>`; the refused body is kept at handoff-wip/r10-outside-contributor-cycle-body 5e67df983b00102baa34a93fac7b65aefc6b3cb3.

State: the code is handed off. refs/heads/handoff/r10-outside-contributor-cycle is 87b116dd7bb0d42b244fcbf9beee8504802873db, fast-forward from 8e6e94427f86b0c15ecdbbe1ed639acc716737ee, and `tools/pr/prepr.sh` with that body printed `PRE-PR: 87b116dd7bb0d42b244fcbf9beee8504802873db ... rc=0`. Only the body's push is outstanding.

The destination of the one missing carry is this seat's choice and is not verified: the finding is about `tools/audit/seat/tick_loop.sh`, which is outside this group, and `R10-GATE-DEFER-BARRIER` was taken because this body's carry 4 already names it as a live group for a seat instrument. If another group owns `tick_loop.sh`, change the `Carry:` token on that body line before landing.

body_push.sh output:

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-OUTSIDE-CONTRIBUTOR-CYCLE at 87b116dd7bb0, 7 live, 7 dispatched carries, 0 refused
CARRY-MISSING R10-GATE-DEFER-BARRIER body item 0036f828: not in its brief or carries: '- `tools/audit/seat/tick_loop.sh --self-test` moves the HEAD of the checkout it runs in: run in a de'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-outside-contributor-cycle-body 5e67df983b00102baa34a93fac7b65aefc6b3cb3
```
