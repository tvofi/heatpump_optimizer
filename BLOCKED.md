# BLOCKED: r10-docs-strings-residue part 1 (carries 0-4)

Question: carry 0 (P-OUTSIDE-3529-C) is already on main: the contributor's three commits reached main as 091b777390, dc5ef2d555 and ba25baa7d5 (author Bankaifan) through 0cc5647545 (#3536), so this part builds nothing for it. The body says so in one line, "... landed on main as 091b777390 ...". `review_packet.py`'s LANDED rule reads that as a roster-carry landing citation and refuses (output below). Should the body describe carry 0's state in other words (the refusal is about roster landings, not merged commits), or does the relay/orchestrator dispose of carry 0 another way? I did not reword it myself: rewording to get past a refusal was refused as a workaround.

Code head (prepr.sh rc=0 at c79e44e2e6929a393a9542cc74b29b5ee3dcd776, PRE-PR all zeros): pushed to refs/heads/handoff/r10-docs-strings-residue. The refused body is kept at handoff-wip/r10-docs-strings-residue-body 6c1355acb1b4c36a65c32df336497bea1ed22292.

body_push.sh output (rc=1):
```
review_packet: REFUSE carry-landed: carry 0 is cited as landed at 091b777390, which is not on the roster ref
review-packet handoff: R10-DOCS-STRINGS-RESIDUE at c79e44e2e692, 14 live, 14 dispatched carries, 1 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
```
