# BLOCKED: body_push.sh refuses at the carry-landing step

The re-cut body (BODY.md here) passes `prepr.sh --body-check` and `carry_audit.py check` (3 routed, 0 bad destination). `body_push.sh r10-ext-3226` then refuses: "a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body". Landing writes the roster branch, which this brief forbids a fixer to write, and HPO_HANDOFF_LANDED would bypass the check, so I did not use it.

Question for the dispatch seat: land the two Carry: R10-CLONE-2238 lines (frame-read bound in coordinator.py; diagnose-service translation in services.py, no live group lists it) with `carry_audit.py land-ops`, then push BODY.md with body_push.sh r10-ext-3226. Or name a better live group and I re-cut.

Measured at 9a54629e: features green 4898; m4 and m6 each 1 of 4898 failed on the off-loop check; no code changed.
