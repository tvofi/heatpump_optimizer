Fix review: merge 7628bb71a83955da84647646afee6629a04f1388

bus-nonce: 3e69eb35253cf34811881b7578fbcada

Round: second review of this PR, delta-scoped (owner ruling 2026-11-09): `git diff c4fb06753b40e3fac0d758202bfcede6c30f934f 7628bb71a83955da84647646afee6629a04f1388`. The delta is two record files only (dev/programme/triage/s6-batch131.md rewritten, dev/programme/delivery/3385.md added via a main merge). No custom_components/ or tools/ code changed, so nothing is widened. review_carry prints FRESH-REVIEW (the head moved), so this is the delta review.

Previous verdict (c4fb067): one finding, that the note described an ACCEPT of a fix main already had. Resolved: the note is now a REJECT, already landed; `roster_edit.ruling_verdict` on the head's note prints REJECT.

## Evidence
- RESULT classify 7628bb71a83955da84647646afee6629a04f1388: GREEN, pending none, red none (rc 0), ev/classify.txt. All owed-reds contexts (closure-scope, closures, coverage, coverage-ratchet, fast 3.14, mutation, typing, validate-hacs) are green in the packet digest.
- RESULT merge-tree origin/main vs head: rc 0, clean (ev/merge-tree.stderr).
- The new note's claims, re-read at origin/main: `aaaec2128` is an ancestor of main (prints anc); `git grep -c train-hold tools/release/stamp.py` gives 4; stamp.py line 2701 reads `if not hold and count < FLUSH_MAX_DISPATCHES ...`; its self-test has the live-hold, stale-hold, absent-hold and mutant arms (lines 2014-2050), and the bound is read from nightly.yml by source read; `stop_ignored` is at merge_train.py:315 with the `mut:stopign` and `mut:deferdeliver` markers, and `Train.unwind` calls release_worktrees then hold_release (2955-2956); the roster branch carries delivery/3280.md "merged aaaec21" and a group brief citing s6-batch131.md. All hold. The note's 2026-11-10 read-timestamp and the exact commit `6cc9aa30b` were not independently re-derived beyond these checks.
- Version files untouched by the delta. carry_audit at the head: 2 items, 2 routed, 0 bad. figure_lint: 4 unverified commands (git/python inline), 0 refused.
- No production code, no mutant, no claim file, no budget moved: steps 1-4, 6, 14, 15 have nothing to run.

## Findings
- Follow-up: the note's Binding section says the roster group's brief citation now resolves to a REJECT and the brief and ordering are the orchestrator's to reconcile; that reconcile is owed after merge, outside this PR. Carry: dismissed: the note itself records it for the orchestrator and the group (R10-FLY-STAMP-FLUSH-HOLD, PR 3280) is merged, so no later stage changes how it must work.
