# BLOCKED: r10-water-setpoint-feedback

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED). The body's Forward-carry to R10-ARBITER-OFF-RESTORE must land on handoff/audit-r10-roster, which this seat may not write; please fold the carry and re-run body_push.sh.

Code head: 5a03cadb30bd0e8fad1ee70d6bc044bc0ec0da96 (pushed to refs/heads/handoff/r10-water-setpoint-feedback). prepr.sh rc=0 at that head. Refused body kept at handoff-wip/r10-water-setpoint-feedback-body 3f005a35701af039ec04d238c1451d6f289e8dbe.

```
fill-red: `## Red checks` already names mutation; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-WATER-SETPOINT-FEEDBACK at 5a03cadb30bd, 5 carries, 0 refused
CARRY-MISSING R10-ARBITER-OFF-RESTORE body item a070f930: not in its brief or carries: "- R10-ARBITER-OFF-RESTORE reuses this group's write record (roster ordering note). At this head the "
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-water-setpoint-feedback-body 3f005a35701af039ec04d238c1451d6f289e8dbe
```
