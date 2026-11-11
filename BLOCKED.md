# BLOCKED: body_push.sh exit 4 at the handoff

Code head: 5289e1fee495ba8d7e81a5c1e5c8c328aca77d7f on refs/heads/handoff/r10-duty-switch-restart-learning (first clean tools/pr/prepr.sh head, body check included).
Refused body: refs/heads/handoff-wip/r10-duty-switch-restart-learning-body 05d1c48ef58bd7be1bd1b5d3d1ecffcb9c37e05d.

The body carries one finding to R10-COMBI-TANK-PR-B that is not yet on the round roster, which this seat may not write: fold it (carry_audit.py land-ops), then re-run body_push.sh on the kept body.

Output of `bash tools/audit/seat/body_push.sh r10-duty-switch-restart-learning <body.md>`:

```
fill-red: `## Red checks` already names mutation; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-DUTY-SWITCH-RESTART-LEARNING at 5289e1fee495, 1 carries, 0 refused
CARRY-MISSING R10-COMBI-TANK-PR-B body item bcf2d3ca: not in its brief or carries: "- `tests/features.py`'s `combi_type_branch` census is red on `origin/main` itself since pull request"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-duty-switch-restart-learning-body 05d1c48ef58bd7be1bd1b5d3d1ecffcb9c37e05d
```
