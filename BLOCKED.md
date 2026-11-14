# BLOCKED: r11-outside-honest-starts-runs (fixer seat, code handed off, body refused CARRY-LANDED)

Question: seven of the body's carries name R11-OUTSIDE-HONEST-STARTS-RUNS and are not in its brief or carries on the round's roster branch, which this seat may not write. Will the relay land them (`carry_audit.py land-ops`) and re-run `body_push.sh`?

Question: ruling c1 (a priced start engages on a modulating install too) is `decision: owner` in the design note at 0c692c86d2 and "still open" in the verdict at caab288c05. The head builds the recommended arm and the body's second paragraph marks it `pending owner confirmation`. Does the owner confirm it?

## State

- Code head: `handoff/r11-outside-honest-starts-runs` at d73ec97da13b4df42e7b7eef36731707b963fce7. `tools/pr/prepr.sh <body>` printed `PRE-PR: d73ec97da1... rc=0` at that head. It merges `origin/main` d7004eaa77; both stacked bases (#3481, #3532) are on main.
- Refused body, kept by `body_push.sh`: `handoff-wip/r11-outside-honest-starts-runs-body` at 8aaeaddf034832ece6d967568aa2bf27c731dc2c. `tools/pr/prepr.sh --body-check` on it: pr-body, carry, preflight, figures, ref_privacy all ok.
- `body_push.sh r11-outside-honest-starts-runs <body>` exited 4. Its output from the review packet's line to its end:

```
review-packet handoff: R11-OUTSIDE-HONEST-STARTS-RUNS at d73ec97da13b, 3 live, 1 dispatched carries, 0 refused
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item edbb6759: not in its brief or carries: '- Ruling c1 (engaged on a modulating install) is built as recommended and is `pending owner confirma'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item 0661d6fd: not in its brief or carries: '- Groups B (hot-water charges as runs, `dhw_planner.py`, design first, ruling b in its brief) and C '
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item 6f871e1c: not in its brief or carries: '- A clamped install that prices no start can plan more starts than before (grid figure, 2 to 5): the'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item b91703ab: not in its brief or carries: '- Note n6 (the finite-difference gradient skipping the variables a mask fixes) is not built: a pinne'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item 6157844a: not in its brief or carries: "- fixer.md: cost: the note's test 5 and R10-DUTY-SWITCH-PLANNER-PRICE's acceptance both assume a pri"
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item 7e48b773: not in its brief or carries: '- design-review.md: unclear: an owner decision routed in round 1 and "still open" at `approve` reach'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS body item ab721197: not in its brief or carries: "- finding-propagation.md: unclear: the note asks that R10-DUTY-SWITCH-PLANNER-PRICE's failing tests "
CARRY-LANDED: 7 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-honest-starts-runs-body 8aaeaddf034832ece6d967568aa2bf27c731dc2c
```
