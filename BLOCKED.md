# BLOCKED: body_push.sh exit 4 at the handoff, round 2

Code head: bf9707ae03044f329bdbc5c3ce8d3249c51f955b on refs/heads/handoff/r10-duty-switch-restart-learning (clean `tools/pr/prepr.sh` head, body check included; it fast-forwards pull request 3461's branch e277df592e678982bb22fb48644482e30b5b86c7).
Refused body: refs/heads/handoff-wip/r10-duty-switch-restart-learning-body 76d80712f4417c5215b040833d303d0eb72eb2a0.

The body carries three findings that are not yet on the round roster, which this seat may not write: two to R10-DUTY-SWITCH-RESTART-LEARNING-PR-B and one to R10-DUTY-SWITCH-PLANNER-PRICE. They are what block 2 of the round-1 verdict (carry-missing) asked for. Fold them (`carry_audit.py land-ops`), then re-run `body_push.sh` on the kept body.

Question: none; the relay folds the three carries and re-runs body_push.sh.

Output of `bash tools/audit/seat/body_push.sh r10-duty-switch-restart-learning <body.md>`:

```
fill-red: `## Red checks` already names mutation; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-DUTY-SWITCH-RESTART-LEARNING at bf9707ae0304, 3 carries, 0 refused
CARRY-MISSING R10-DUTY-SWITCH-RESTART-LEARNING-PR-B body item 1b22f416: not in its brief or carries: '- Parts B and C get no ready read API from part A: `Direction.usable`, `.p` and `.median_off_s` hold'
CARRY-MISSING R10-DUTY-SWITCH-PLANNER-PRICE body item 3656875b: not in its brief or carries: "- The same finding for the planner's price of a switch: it reads the estimate through a reader it ad"
CARRY-MISSING R10-DUTY-SWITCH-RESTART-LEARNING-PR-B body item 3c666f5b: not in its brief or carries: '- Factory reset keeps the duty-switch store (`_FR_STORES`, "kept: observed facts"), where every othe'
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-duty-switch-restart-learning-body 76d80712f4417c5215b040833d303d0eb72eb2a0
```
