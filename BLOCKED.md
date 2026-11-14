# BLOCKED: r10-sav-valuation-residue-p3 (Carry 10)

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED): the forward-carry to R11-INTAKE-R10-RESIDUE (body item 5a1ba9c2) is not yet on the roster, which this seat may not write. Please fold the carry and re-run body_push.sh.

Code head: handoff/r10-sav-valuation-residue-p3 at 8341359750 (clean tools/pr/prepr.sh, rc 0, merge base a2ef25b4b2).
Refused body kept at handoff-wip/r10-sav-valuation-residue-p3-body c4a731542d.

body_push.sh output:

```
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at 83413597506a
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-SAV-VALUATION-RESIDUE at 83413597506a, 16 live, 1 dispatched carries, 0 refused
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 5a1ba9c2: not in its brief or carries: "- The one-channel recount (route (b) in the predecessor's BLOCKED question). On a combi store the th"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
fatal: expected 'acknowledgments', received 'packfile'
body_push: refused body kept at handoff-wip/r10-sav-valuation-residue-p3-body c4a731542dc8572a3bc19b754b695ace11158836
```
