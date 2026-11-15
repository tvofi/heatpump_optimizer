# BLOCKED: R11-PRE-BRIEFS-CENSUS, body push refused on carry landing

The code head is on `handoff/r11-pre-briefs-census` at db626fb9dde5ca152ce45e7c216e3c7676553b4e. `tools/pr/prepr.sh` is clean at that head and `prepr.sh --body-check` passes on the body. `bash tools/audit/seat/body_push.sh r11-pre-briefs-census <body.md>` exited 4: two forward-carries name live groups whose roster this seat may not write. The refused body is kept at `handoff-wip/r11-pre-briefs-census-body` (a5568526ab57bb1ee395b31fee72fa70da0d7150). Nothing else is owed by this seat: the relay folds the two carries and re-runs `body_push.sh`.

The output of `body_push.sh`, its own lines:

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-PRE-BRIEFS-CENSUS at db626fb9dde5, 1 live, 1 dispatched carries, 0 refused
CARRY-MISSING R11-PRE-NEW-DIMENSIONS body item dcd38e1b: not in its brief or carries: "- `d16-writes [--cells]` and `d17-features` are in `tools/audit/enumerate.py` under the prototype's "
CARRY-MISSING R11-PRE-OWNER-CRITERIA body item 803716a7: not in its brief or carries: '- `tank_volume` and `house_size` print `NO-READ` from `--population` until `dev/audit/config/objecti'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
```
