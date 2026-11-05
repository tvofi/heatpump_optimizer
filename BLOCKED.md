BLOCKED: body_push refuses CARRY-MISSING for r10-raise-gate-shim. Code is pushed to handoff/r10-raise-gate-shim at 725410a6b1e7685c4889f68b14ec686ef14a6c3f; the final body is PR-BODY.md on this ref.

Two body items under `## Forward-carry` are not in the group's brief or carries (carry_audit.py: CARRY-LANDED: 2 missing):
1. item 870f6b21: "Carry: R10-RAISE-GATE-SHIM (c) measured, no change needed" - the budget-raise-gate job's duration over 31 CI jobs: min 19 s, median 28 s, max 48 s against the 5-minute timeout; the scorer's cost on a raise diff stays unmeasured.
2. item aae60647: "Carry: R10-RAISE-GATE-SHIM, residual, exec -a argv0 spoofing" - the ps-based parent check, no fix, as the coordinator ruled.

Question for the orchestrator: land these two with `carry_audit.py land-ops` on the round's roster branch, then run `bash tools/audit/seat/body_push.sh r10-raise-gate-shim PR-BODY.md` (the body passes every other check: reds answered, brief carries 1 and 2 named, figures resolved). Per the brief this seat does not edit the roster.
