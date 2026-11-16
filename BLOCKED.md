# BLOCKED: body_push.sh REFUSED CARRY-LANDED (exit 4)

Code head: b02d5b3aabcf4dfed82c6a68d7068c45243f7a1a, pushed to refs/heads/handoff/r11-pre-standing-scripts.
`tools/pr/prepr.sh` at that head: `PRE-PR: b02d5b3aabcf4dfed82c6a68d7068c45243f7a1a 0000000000000000000000000000000 rc=0`.
The refused body is kept at handoff-wip/r11-pre-standing-scripts-body 68c2fc1ed7abdc9b15f92ad58d967eb310ffb494.

Command: `bash tools/audit/seat/body_push.sh r11-pre-standing-scripts <body.md>`

Its last lines:

```
review-packet handoff: R11-PRE-STANDING-SCRIPTS at b02d5b3aabcf, 18 live, 5 dispatched carries, 0 refused
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 4427fe25: not in its brief or carries: '- dev/programme/rosters/wave-r10-groups.json, group R11-INTAKE-R10-RESIDUE: `sweep_gantt.recent_fire'
CARRY-MISSING R11-PRE-STANDING-SCRIPTS body item 00d4b808: not in its brief or carries: '- part-cut: contradiction: this seat\'s brief reads "Part 1 of 4: build carries 0-4". The approved de'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-standing-scripts-body 68c2fc1ed7abdc9b15f92ad58d967eb310ffb494
```

Both carries land on the roster, which this seat may not write: the relay folds them and re-runs body_push.sh.
