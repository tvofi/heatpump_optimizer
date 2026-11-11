# BLOCKED: r10-advisor-steady-start (fixer, continuation), body_push.sh exit 4

The code is handed off: refs/heads/handoff/r10-advisor-steady-start at 5b1078ea0f212bbc9dd1dc575d673225a56633ee, `tools/pr/prepr.sh` rc=0 at that head with the body. The body is not on handoff-body/: body_push.sh refused it with CARRY-LANDED, because three Forward-carry items name this group and the roster, which this seat may not write, does not hold them yet. The refused body is kept by body_push.sh at refs/heads/handoff-wip/r10-advisor-steady-start-body f21648dbb63a3ed520bf201d12ef064fb12dd270. The relay folds the carries and re-runs `bash tools/audit/seat/body_push.sh r10-advisor-steady-start <body.md>`.

This commit sits on the step ref only; the handoff head is its parent and is not moved.

## body_push.sh output

```
review-packet handoff: R10-ADVISOR-STEADY-START at 5b1078ea0f21, 2 carries, 0 refused
CARRY-MISSING R10-ADVISOR-STEADY-START body item c7424eb8: not in its brief or carries: '- The ruling\'s "one real high-spread price day" is not met: dev/audit/harnesses/r10_advisor_steady_b'
CARRY-MISSING R10-ADVISOR-STEADY-START body item ccc86b13: not in its brief or carries: '- Item pair-other-asks of the design: the hot-water ask reads +0.0 on `_solve_coord`, which has no t'
CARRY-MISSING R10-ADVISOR-STEADY-START body item 70e463f9: not in its brief or carries: '- Items measured-fields, weekday-day and pv-price of the design are not measured: the schedule figur'
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-advisor-steady-start-body f21648dbb63a3ed520bf201d12ef064fb12dd270
```

## The three items, in full in the kept body's Forward-carry

- The ruling's "one real high-spread price day" is not met: the bracket ran a synthetic peaks day (no recorded full price day in the tree, no network in this container). The range the ruling attaches to a high ratio is built unconditionally.
- Design item pair-other-asks: the pair's money for a hot-water, weight or floor ask alone is not measured for sign on a tanked fixture.
- Design items measured-fields, weekday-day and pv-price are not measured.
