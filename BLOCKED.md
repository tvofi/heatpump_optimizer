# BLOCKED: r10-docs-strings-residue-p2

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED); the relay folds the carries below onto handoff/audit-r10-roster and re-runs body_push.sh for topic r10-docs-strings-residue-p2.

Code head: handoff/r10-docs-strings-residue-p2 at 3047b48a3e7ceb9731d43d1a8ff040d8727bf3d4 (prepr.sh rc=0 with PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1). Refused body kept at handoff-wip/r10-docs-strings-residue-p2-body fb1a7679ee7b6da9de59708adf3315dd123aced2.

~~~text
review-packet handoff: R10-DOCS-STRINGS-RESIDUE at 3047b48a3e7c, 14 live, 14 dispatched carries, 0 refused
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 4d485f3d: not in its brief or carries: 'Carry 12 (a0e752f6): not built here. Re-measured at this head (`plan_view.py`, then `HPO_PAGES_OUT=<'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item c07c1278: not in its brief or carries: "- Carry 12's re-take of docs/img/card/advisor-*.png on the recording host, with the re-measure above"
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-docs-strings-residue-p2-body fb1a7679ee7b6da9de59708adf3315dd123aced2
~~~
