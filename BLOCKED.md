# BLOCKED: r11-arch-objective

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED). The carry to R11-ARCH-OBJECTIVE (the keyed objective-record rows, pending the orchestrator's ruling on 0018 section 6) must land on the round's roster, which this seat may not write. Please fold it (carry_audit.py land-ops) and re-run body_push.sh r11-arch-objective on the body at handoff-wip/r11-arch-objective-body ebaf676ff37762c2562a472bfe87f5e7b160c1c0.

Code head: handoff/r11-arch-objective at bf9c7acaa17106f538692dfc25de63859cbc1855 (prepr.sh rc=0 at that head).

```
figure_block: refreshed 1 block(s) at bf9c7acaa171
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-ARCH-OBJECTIVE at bf9c7acaa171, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-ARCH-OBJECTIVE body item 390ea33c: not in its brief or carries: "- The settlement reads keyed rows from an objective record's `keyed.<kind>` (`escapes` rows by `key`"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-arch-objective-body ebaf676ff37762c2562a472bfe87f5e7b160c1c0
```
