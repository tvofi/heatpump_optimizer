Fix review: merge c4fb06753b40e3fac0d758202bfcede6c30f934f

bus-nonce: 51e871e11b88b6b27ad839e9ae005816

Round: first review of this head. Docs-only PR: adds dev/programme/triage/s6-batch131.md (the P402 triage note) and dev/programme/delivery/3386.md. No production code, no VERSION/notes change (three-dot diff of VERSION and RELEASE_NOTES.md empty), so the mutation, harness, null-control, claim-file and class-enumeration steps have nothing to run; the PR names no mutant or finder harness.

## Evidence
- RESULT classify c4fb06753b40e3fac0d758202bfcede6c30f934f: GREEN, pending none, red none (rc 0), ev/classify.txt.
- RESULT merge-tree origin/main vs head: clean, rc 0, ev/merge-tree.txt. The head is behind main and merges cleanly.
- RESULT carry_audit in the packet: 0 finding items, 0 unrouted. figure_lint: 1 unverified (a git diff --stat range quoted in a comment), 0 refused.
- Premise check against current main: the note's flush half is already in the tree. f46d160d2 (2026-11-07T06:43Z, before this PR's base 01782a1e3) gave record_flush its held collaborator, and roster group R10-FLY-STAMP-FLUSH-HOLD on handoff/audit-r10-roster (dd478521f) is stage done, PR 3280. The note is therefore a historical record of the verdict that dispatched that group, not an open proposal, and its facts were read at be813ecd4, before f46d160d2. Landing it is what makes that group's brief citation (triage/s6-batch131.md#P402) resolve in the tree.
- The note's claims about unchanged code hold at origin/main: nightly.yml HOLD_MAX_AGE_S=3600 at line 1096 and skip-train-hold at 1116; merge_train.py stop_on_signal at 306 and hold_release at 2893; FLUSH_POLL_S=60, FLUSH_REDISPATCH_S=900, FLUSH_MAX_DISPATCHES=3, FLUSH_TIMEOUT_S=7200. Its line numbers for record_flush (2410) and the absence of train-hold in stamp.py are the pre-f46d160d2 state and no longer hold on main. Host-local figures (orchestration logs, 23 min, 6129 s p90) I could not re-derive; the note says they are host-local.
- Red-check ruling: merge_train.py owed-reds (no per-PR arguments in this version) lists tests/coverage-ratchet, fast (3.14), mutation, typing, validate-hacs; every one is green on this head, so no red is owed an answer.
- brief_lint output: ev/brief_lint.txt.

## Findings
- Follow-up: the note's "No group that is still open owns stamp.py's flush" and its Binding section describe a group and a fix that main already has; a seat reading the file alone could redispatch it. Carry: dismissed: the roster group is stage done at PR 3280 and the note records its own read point (be813ecd4), so no later stage changes how it must work.
