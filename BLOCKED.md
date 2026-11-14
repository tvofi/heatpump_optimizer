# BLOCKED: R11-PRE-OBJECTIVE-FUNCTION re-handoff (repair round after the blocked sufficiency review)

Question: none. body_push.sh exited 4 at code head 018b520580cfd80b828687418f13672a4c03051d (handoff/r11-pre-objective-function); the relay folds the carries onto the roster branch and re-runs body_push.sh with the body kept at handoff-wip/r11-pre-objective-function-body.

prepr.sh at this head: rc=0.

The check names one missing carry. The body's `## Forward-carry` holds six items, five of them new text this round (the blocked verdict's item 6 asked that each name decision 0017 and its section). The four new items to R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER and R10-DIMENSIONS-FULL-COVERAGE pass the landed check on the topic token of the first handoff's carries there, not on their own text, which is not on the roster: fold all five new items, not only the one named.

```
review-packet handoff: R11-PRE-OBJECTIVE-FUNCTION at 018b520580cf, 5 live, 5 dispatched carries, 0 refused
CARRY-MISSING R10-D5-D6-FULL-SCOPE body item 479c4962: not in its brief or carries: "- Decision 0017 (`dev/governance/decisions/0017-objective-function.md`) section 1's table reads D6's"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-objective-function-body 39841fa8105e308546cfbc3ae44837f5114a9f92
```
