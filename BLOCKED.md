BLOCKED: body_push.sh refused the body at head f60b4d8c0f5c219e6b8c6d506f4874ce4c8f2a0a.

prepr.sh --body-check is clean at that head (pr-body 0 errors, figures 15 resolved / 3 not verified / 0 refused).
The refusal is from body_push.sh's carry audit:

CARRY-MISSING R10-I18N-DE body item c7e2fe29: not in its brief or carries
CARRY-MISSING R10-USER-DOCS-VERIFY body item cc1cca91: not in its brief or carries
CARRY-MISSING R10-MIN-POWER-FLOOR body item a4565419: not in its brief or carries
CARRY-MISSING R10-MIN-POWER-FLOOR body item de37a181: not in its brief or carries
CARRY-MISSING R10-MIN-POWER-FLOOR body item b8c2d996: not in its brief or carries
CARRY-LANDED: 5 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body

Landing them writes the roster branch (handoff/audit-r10-roster), outside this seat's permitted refs. Orchestrator: land the five carries, then re-run body_push.sh with the kept BODY.md.
