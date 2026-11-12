# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED)

Code head: 29370fdbb59aeb18da82ebe9612e7c036e9dc29c on handoff/r10-duty-switch-restart-learning-pr-b-p2. Body kept at handoff-wip/r10-duty-switch-restart-learning-pr-b-p2-body af7b1c29908e7c7a92a7b103cf3f329ce4fad09a. The relay folds the carry onto the roster and re-runs body_push.sh.

~~~text
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at 29370fdbb59a
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B at 29370fdbb59a, 9 live, 9 dispatched carries, 0 refused
CARRY-MISSING R10-DUTY-SWITCH-PLANNER-PRICE body item c3ad1545: not in its brief or carries: "- R10-DUTY-SWITCH-PLANNER-PRICE's branch (`handoff/r10-duty-switch-planner-price`, unmerged) adds th"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-duty-switch-restart-learning-pr-b-p2-body af7b1c29908e7c7a92a7b103cf3f329ce4fad09a
~~~
