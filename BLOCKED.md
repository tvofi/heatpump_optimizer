Question: body_push.sh refuses the body for r10-tick-levels-p2 at fb37cb5f7afbe2c00b1c2f2a153f64618caebb4f with one CARRY-MISSING: the ci_predict finding (body item 9615f50a, routed `Carry: R10-FLY-CIPREDICT-RESTORING`) is not in that group's carries, and landing it is a write to handoff/audit-r10-roster, which this seat's brief forbids. Will the orchestrator apply the op below (from `carry_audit.py land-ops`) so the body can be pushed, or name another destination?

    append-carry R10-FLY-CIPREDICT-RESTORING 'From this pull request, body item 9615f50a: ...' (run `python3 -I tools/audit/carry_audit.py land-ops --body <body>` on the kept body for the full text)

Why it cannot be dismissed: origin/main's tools/pr/ci_predict.py (425b85849), run with `--base 2865d3867` on the pre-repair tree 8f7ef132540bd70b9b1020f6212b929ae6aebcd1, prints `CI PREDICT: no closures, fast, governance or instrument red predicted`, while CI's closures job 128856975668 at that tree is UNDER-SCOPED on tests/entities.py: tools/audit/seat/topic_grammar.py. The finding is live.

The finding's group, R10-FLY-CIPREDICT-RESTORING, lists only #2952, and that issue is closed (by #3301), so `Carry: #2952` is no destination either.

State: code head fb37cb5f is on handoff/r10-tick-levels-p2; prepr.sh ran clean there (rc=0) at origin/main 20e83746f. The refused body is kept at handoff-wip/r10-tick-levels-p2-body a0f554ac4536d36b3a39d18fe126c3491667ce80. The rest of body_push's output is clean: figures 18 resolved, 0 not verified; review-packet 0 refused. Once the carry is landed, run body_push.sh on that body and no other change is needed. origin/main moved to 425b85849 (#3344, no conflict, no file shared with this PR) during the last prepr run. It was not merged: main landed in each of the four runs.
