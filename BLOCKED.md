body_push: REFUSED CARRY-LANDED (exit 4) for r11-advisor-measures-p2 at code head c03ab4b85fd9a08ce6ecc072670a223018a808db.

The code is on refs/heads/handoff/r11-advisor-measures-p2; the refused body is kept at handoff-wip/r11-advisor-measures-p2-body 608eb10046e82c709c252aa002522b74c93a586e. The relay folds the carry and re-runs body_push.sh.

body_push.sh output (tail):

review-packet handoff: R11-ADVISOR-MEASURES at c03ab4b85fd9, 3 live, 3 dispatched carries, 0 refused
CARRY-MISSING R11-VALVE-REFERENCE body item fcac48c8: not in its brief or carries: '- R11-VALVE-REFERENCE\'s body states the `fields` arm\'s `valve, one tank` count as "24 of 72 rows at '
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-advisor-measures-p2-body 608eb10046e82c709c252aa002522b74c93a586e
