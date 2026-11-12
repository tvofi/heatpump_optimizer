# BLOCKED: r10-mode-before-supply-on

Code head 84fe94c780e04d5c0f39434550ef71268b1be19b is on refs/heads/handoff/r10-mode-before-supply-on (prepr.sh at that head: rc=0). Re-ran body_push.sh on the kept body; the carry is still not on the roster. CARRY-OWED.md holds the exact text and destination.

Question: fold the carry in CARRY-OWED.md into R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE's brief on the roster branch, then re-run body_push.sh for this topic with the kept body (handoff-wip/r10-mode-before-supply-on-body dd3b47d2601f5f976619769d07ef8ff324cede24).

body_push.sh output (exit 4):

```
review-packet handoff: R10-MODE-BEFORE-SUPPLY-ON at 84fe94c780e0, 1 live, 1 dispatched carries, 0 refused
CARRY-MISSING R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE body item 50b08d86: not in its brief or carries
CARRY-LANDED: 1 missing
body_push: REFUSED CARRY-LANDED
```
