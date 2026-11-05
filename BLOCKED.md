BLOCKED: body_push.sh r10-suite-host-determinism refuses the body.

Code is pushed: refs/heads/handoff/r10-suite-host-determinism at 0cac0fe21b10e28d0a6e99aafd7af0ac84625c09 (main cd0dd1691 merged, prepr.sh rc=0). The final body is on this ref as PR-BODY.md; `prepr.sh --body-check` reads 0 errors.

body_push output: `CARRY-MISSING R10-GATE-LEASE-TOCTOU body item 42008ca4: not in its brief or carries`. The group is in the roster at 7f6468d1 (line 16813), but its `carry` is [] and its brief says "PR 3170", which carry_audit.landed() does not match (it needs the item id or `#3170`/the topic as a whole token). Landing means `append-carry` on handoff/audit-r10-roster, a branch this seat may not write.

Question for the orchestrator: land the carry on the round's roster branch with `python3 tools/audit/carry_audit.py land-ops` (item 42008ca4, body text from PR-BODY.md `## Forward-carry`), then run `bash tools/audit/seat/body_push.sh r10-suite-host-determinism PR-BODY.md` from handoff/r10-suite-host-determinism. The step ref is left in place.
