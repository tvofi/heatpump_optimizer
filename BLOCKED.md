# BLOCKED: R11-OUTSIDE-HONEST-STARTS-RUNS, body_push CARRY-LANDED

Question: none for the owner; the relay folds the carry below onto the round's roster and re-runs body_push.sh. Code head b9cd9629999d6fadccde39bf6c5e9c525e6c52c4 is pushed to handoff/r11-outside-honest-starts-runs; the refused body is at handoff-wip/r11-outside-honest-starts-runs-body f7a33ca32fc9ca43cb6a531093c84b39558dda2b.

```
fill-red: `## Red checks` already names mutation; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-OUTSIDE-HONEST-STARTS-RUNS at b9cd9629999d, 14 live, 14 dispatched carries, 0 refused
CARRY-MISSING R11-PRE-TOOLCHAIN-PIN body item a4ac1e10: not in its brief or carries: '- The cloud seat pins `OPENBLAS_CORETYPE=Haswell` (`tools/audit/seat/cloud-setup.sh`, `CORETYPE`), t'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-honest-starts-runs-body f7a33ca32fc9ca43cb6a531093c84b39558dda2b
```
