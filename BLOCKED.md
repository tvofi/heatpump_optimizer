# BLOCKED: body_push REFUSED CARRY-LANDED (exit 4)

Code head: 6b9e873394a02ec82ec24d23dc454a99418e2366 on handoff/r10-duty-switch-restart-learning-pr-b, prepr.sh rc=0. Body kept at handoff-wip/r10-duty-switch-restart-learning-pr-b-body b958af083e3d5992e3719a616fed8f3a338436a3. The relay folds the carries and re-runs body_push.sh.

```text
review-packet handoff: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B at 6b9e873394a0, 6 live, 6 dispatched carries, 0 refused
CARRY-MISSING R10-DUTY-SWITCH-RESTART-LEARNING-PR-B body item a0f4b31e: not in its brief or carries: "- Carry 0: the module-level reader is added with its first caller, the arbiter's split; a reader wit"
CARRY-MISSING R10-DUTY-SWITCH-RESTART-LEARNING-PR-B body item ca1bcac3: not in its brief or carries: '- Carry 1: factory reset keeps the duty-switch store; the owner rules before the reader merges. Carr'
CARRY-MISSING R10-DUTY-SWITCH-RESTART-LEARNING-PR-B body item bed4c123: not in its brief or carries: '- Carry 4: a reader takes `span_days` 0 beside non-zero tallies as "nothing recent", and an absent k'
CARRY-MISSING R10-DUTY-SWITCH-RESTART-LEARNING-PR-B body item 71216302: not in its brief or carries: '- Carry 5: evidence accrues at different rates per set-point unit; a reader of `n` must not assume o'
CARRY-LANDED: 4 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-duty-switch-restart-learning-pr-b-body b958af083e3d5992e3719a616fed8f3a338436a3
```
