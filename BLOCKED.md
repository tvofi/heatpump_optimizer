# BLOCKED: r11-repair-3869

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED); the two pre-existing Forward-carry items of PR #3869 (Carry 0 to R11-OWNER-FAULT-HOLD, Carry 1 to R11-OWNER-FROST-HOLD) are not in those groups' brief or carries on the roster this seat may not write. Will the relay fold them (carry_audit.py land-ops) and re-run body_push.sh r11-repair-3869 with the body kept at handoff-wip/r11-repair-3869-body 042189e397?

Code head, pushed: handoff/r11-repair-3869 928dcb1ac3c0c92d0aed762ee67c400de0bfae3d (one commit on 337e6cbbb0: dev/audit/config/scopes.json D5-s7 re-cut to tests/features.py; repairs governance / instrument-self-tests). PRE-PR: 928dcb1ac3c0c92d0aed762ee67c400de0bfae3d 0000000000000000 rc=0 elapsed=122s (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1).

body_push.sh output, verbatim:

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: no group at 928dcb1ac3c0, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-OWNER-FAULT-HOLD body item 05701723: not in its brief or carries: '- Carry 0 (roster, from R11-OWNER-FAULT-HOLD item 346bf281, "the fault hold wins with a young leg la'
CARRY-MISSING R11-OWNER-FROST-HOLD body item 4148e760: not in its brief or carries: '- Carry 1 (roster, from R11-OWNER-FROST-HOLD item 8bcbefe1, "frost wins with a young DHW leg latched'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
body_push: refused body kept at handoff-wip/r11-repair-3869-body 042189e3977bcf7c67f259565790b8d8406568bb
```
