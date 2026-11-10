Fix review: merge b6a6c0271e3c017d179c32facd39a1fc5f386d1c

bus-nonce: 5bc3953c2c08cdb89f4d94b8814d2548

Round: re-review (delta c1c105eb..b6a6c0271e3c017d179c32facd39a1fc5f386d1c). Scope: the delta touches only dev/programme/triage/s6-batch131.md (no custom_components/ code), so no widening.

## Findings
none.

## Evidence
- Prior finding (stale-premise: P402 ACCEPT creates R10-FLY-STAMP-FLUSH-HOLD, already merged as #3280): resolved. The entry is now REJECT, already landed; roster_edit.ruling_verdict(..., 'P402') prints REJECT at this head.
- Re-derived at origin/main: aaaec2128 is an ancestor of main (prints anc); stamp.py has record_flush held=train_hold and the "if not hold and count < FLUSH_MAX_DISPATCHES" line, train_hold and hold_bound_s exist; git grep -c train-hold stamp.py = 4 (first ruling: 0); merge_train.py has stop_ignored with # mut:stopign and # mut:deferdeliver markers, used in Train.unwind at line 2911; commit 6cc9aa30b has the quoted subject; origin/handoff/audit-r10-roster carries the group citing s6-batch131 and delivery/3280.md reads merged aaaec21. I did not re-run the self-test arms stamp.py is said to hold; the note's claim of them is unverified by me, the code paths above are confirmed present.
- The note discloses the cause as process state (d) and records the roster citation conflict as the orchestrator's to reconcile, without writing the roster.
- Merge with origin/main: git merge-tree --write-tree origin/main b6a6c0271e3c017d179c32facd39a1fc5f386d1c exits 0, clean.
- CI: merge_train.py classify at this head exits 0: GREEN (pending: none red: none). The packet's early "gate failure" digest line was from render time; the live state settled green. VERSION, manifest and notes untouched (diff is the triage note and a delivery row).
- 4 figure_lint "unverified" commands are inline git/python calls the linter does not resolve; I ran each by hand above.
