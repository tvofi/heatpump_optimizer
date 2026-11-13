Question: body_push.sh exited 4 (REFUSED CARRY-LANDED); the five R11-INTAKE-R10-RESIDUE carries need landing on the round roster (carry_audit.py land-ops), which this seat may not write. Relay: fold the carries and re-run body_push.sh.

Code head: handoff/r10-user-text-verify-card f11bdd4d483c0509ad108b0e00112aaae8f1368d (prepr.sh rc 0 at that head).
Body: handoff-wip/r10-user-text-verify-card-body f06d6c3aeee5502f8dd1a19fcd4bc27f1e2a3401 (the refused body, kept by body_push.sh).

body_push.sh output:

CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 753b6610: not in its brief or carries: '- `docs/dashboard-card.md` (Savings receipt paragraph) still says the savings figure "compares spot '
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item f14f17f5: not in its brief or carries: '- `docs/dashboard-card.md` (Advisor page) says the replay uses "your install\'s measured delivery". `'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item c7e69450: not in its brief or carries: '- `docs/dashboard-card.md`\'s Health picture alt text says "waiting for the first settled month", and'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item a0e752f6: not in its brief or carries: "- `docs/img/card/advisor-*.png` show the old basis line and fuse step. This host's render of the mer"
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 3bbcabdc: not in its brief or carries: '- `translations/de.json`\'s `grid` options page is titled "Netz-Spitzentarif", but its menu entry is '
CARRY-LANDED: 5 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-user-text-verify-card-body f06d6c3aeee5502f8dd1a19fcd4bc27f1e2a3401
