# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED)

Topic r10-generic-heat-curve-persistent. Code head `f483180ffa75b0eb464666f359ed2c9bad22532b` is on `handoff/r10-generic-heat-curve-persistent`; the body is kept at `handoff-wip/r10-generic-heat-curve-persistent-body` `ceea669fcff9d69b8a97900a7f5ce179af53e651`. prepr.sh rc=0 at that head. The three items below land on R10-ARBITER-OFF-RESTORE's roster entry; this seat may not write the roster. Fold them, then re-run `bash tools/audit/seat/body_push.sh r10-generic-heat-curve-persistent <BODY.md>`.

```
fill-red: `## Red checks` already names mutation; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-GENERIC-HEAT-CURVE-PERSISTENT at f483180ffa75, 7 carries, 0 refused
CARRY-MISSING R10-ARBITER-OFF-RESTORE body item 8755bcb3: not in its brief or carries: "- The off_restore API as built, which R10-ARBITER-OFF-RESTORE consumes instead of the note's sync na"
CARRY-MISSING R10-ARBITER-OFF-RESTORE body item 76ae476a: not in its brief or carries: '- The reserve-rule correction (departure 1) binds the arbiter too if it budgets writes: a write that'
CARRY-MISSING R10-ARBITER-OFF-RESTORE body item 2bcac34a: not in its brief or carries: "- design-note: contradiction: the note's reserve rule `count + 1 + (target ≠ b)` admits a return-to-"
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-generic-heat-curve-persistent-body ceea669fcff9d69b8a97900a7f5ce179af53e651
(exit 4)
```
