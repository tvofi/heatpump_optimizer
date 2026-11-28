# BLOCKED: r11-repair-3942

Question: body_push.sh exited 4 (REFUSED CARRY-LANDED); the three R11-CLOSEOUT-CLEANUP carries below land on the round's roster, which this seat may not write. Code head 76ecf989699c6b1ec0c9350a6d71e36a4f21af0d is on handoff/r11-repair-3942 (prepr.sh rc=0, scoped); the body is kept at handoff-wip/r11-repair-3942-body. Fold the carries and re-run body_push.sh.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: no group at 76ecf989699c, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R11-CLOSEOUT-CLEANUP body item b2749276: not in its brief or carries: '- Carry 0 and Carry 1 (merge-time undefined-name detector, `merge_train.py` merge step candidate sit'
CARRY-MISSING R11-CLOSEOUT-CLEANUP body item 94574098: not in its brief or carries: '- Carry 4, re-measured at ac9045c223 by reading `tools/audit/seat/`: merge_pr.sh deferral read is an'
CARRY-MISSING R11-CLOSEOUT-CLEANUP body item 3e628f26: not in its brief or carries: "- Round-1 reviewer follow-up: `dev/programme/HANDOVER.md`'s closeout dry-run enumerator omits `--orc"
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-repair-3942-body 46a00f82d5865c64b3a45dffc53a74e52dd8b010
```
