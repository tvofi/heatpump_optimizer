# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED)

Code head: handoff/r10-rca-roster-drain-replay at f4fecc828bca91b403cf9395f2b00fa28a713c03 (prepr.sh rc=0). Refused body kept at handoff-wip/r10-rca-roster-drain-replay-body 0fb38f03d0a98b804cfa566ce18c679f1ab096be; the relay folds the two carries below onto R10-TICK-RESIDUE and re-runs body_push.sh.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-RCA-ROSTER-DRAIN-REPLAY at f4fecc828bca, 0 carries, 0 refused
CARRY-MISSING R10-TICK-RESIDUE body item 6b03fdc8: not in its brief or carries: '- **Restore four lost carries.** R10-HOTFIX-GATE-BUSY-DEFER (stage `done`) lost four carries to repl'
CARRY-MISSING R10-TICK-RESIDUE body item 1307a50a: not in its brief or carries: "- **Correct carry[11]'s premise.** R10-TICK-RESIDUE carry[11] judged the drain's replay harmless bec"
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-rca-roster-drain-replay-body 0fb38f03d0a98b804cfa566ce18c679f1ab096be
```
