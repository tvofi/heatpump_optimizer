# BLOCKED: r10-outside-learner-robustness

Code handed off at refs/heads/handoff/r10-outside-learner-robustness = da2eef8acd4d175dac1ffbfe6e8423a205d6b513 (prepr.sh rc=0).
Refused body kept at handoff-wip/r10-outside-learner-robustness-body 97955641f06ee70fd5b0abca9ad529157abacdda.

Question: the two split-part carries (parts 2 and 3 of #3435) must be landed on the round roster by the relay before body_push.sh is re-run.

```
review-packet handoff: R10-OUTSIDE-LEARNER-ROBUSTNESS at da2eef8acd4d, 0 carries, 0 refused
CARRY-MISSING R10-OUTSIDE-LEARNER-ROBUSTNESS body item 5da9e652: not in its brief or carries: "- Part 2, the boost settle tail scaled on the boost's length and persisted through `store.py` (`boos"
CARRY-MISSING R10-OUTSIDE-LEARNER-ROBUSTNESS body item 7a7906d8: not in its brief or carries: '- Part 3, refusal reasons at DEBUG (`heat_energy.log_close`, `coordinator._skipped`) and the frozen '
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
```
