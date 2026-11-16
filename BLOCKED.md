# BLOCKED: r11-pre-no-read-builders

Question: none. `bash tools/audit/seat/body_push.sh r11-pre-no-read-builders <body>` exited 4; the relay folds the two carries below onto the round's roster and re-runs it.

- Code head, pushed to refs/heads/handoff/r11-pre-no-read-builders: 08c41f0a3505d67af9a64bf8d7c19781262c7458 (`tools/pr/prepr.sh` rc=0 at this head).
- Refused body, kept by body_push.sh: refs/heads/handoff-wip/r11-pre-no-read-builders-body at f7b8ffb72ea020b2605f04e1163bb30c88adf7f3.
- Scope of the handoff: parts A and B of the approved design. Parts C and D wait on R11-PRE-TOKEN-LEDGER and R11-PRE-ROUND-METRICS parts 2 and 3, none on main; the body says so and carries them to this group.

body_push.sh's output:

```
CARRY-MISSING R11-PRE-NO-READ-BUILDERS body item 4847b00a: not in its brief or carries: "- Parts C and D of the approved design, with the design note's fixer notes [paths], [d-p2-head], [P1"
CARRY-MISSING R11-PRE-NO-READ-BUILDERS body item f54f0692: not in its brief or carries: '- The two departures above (a rule dated through a copy; `conflict` mapped to `null`) await the orch'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-no-read-builders-body f7b8ffb72ea020b2605f04e1163bb30c88adf7f3
```
