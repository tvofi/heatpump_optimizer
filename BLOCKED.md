# BLOCKED: body_push refused CARRY-LANDED

Code is at refs/heads/handoff/r11-pre-round-metrics 46607a59fa76ab341eeec3b1ab4e06257e99355d (prepr rc=0); the body is kept at handoff-wip/r11-pre-round-metrics-body 5e0d2e8981bd34783876434e13479c96fc41c3c5. The relay folds the carry and re-runs body_push.sh.

~~~text
CARRY-MISSING R11-PRE-TOKEN-LEDGER body item ecf8207d: not in its brief or carries: "- R11-PRE-TOKEN-LEDGER: `round_metrics.token_line` (the scorecard's `R tokens` line, 0018's `tokens_"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
~~~
