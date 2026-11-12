# BLOCKED: r10-mode-before-supply-on

Code head 84fe94c780e04d5c0f39434550ef71268b1be19b is pushed to refs/heads/handoff/r10-mode-before-supply-on; prepr.sh at that head: `PRE-PR: 84fe94c780e04d5c0f39434550ef71268b1be19b 00000000000000000000000000000000 rc=0`. The refused body is kept at refs/heads/handoff-wip/r10-mode-before-supply-on-body a11f76cbafc46952cf464e35296196cdc77a2a77.

Question: fold the carry below into R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE's brief on the round's roster branch and re-run body_push.sh for this topic with the kept body.

body_push.sh output (exit 4):

```
review-packet handoff: R10-MODE-BEFORE-SUPPLY-ON at 84fe94c780e0, 1 live, 1 dispatched carries, 0 refused
CARRY-MISSING R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE body item 50b08d86: not in its brief or carries: "- Carry 0 (the brief's forward-carry from feature triage f4, outside pull request 3456), answered: t"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-mode-before-supply-on-body a11f76cbafc46952cf464e35296196cdc77a2a77
```
