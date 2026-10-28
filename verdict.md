Fix review: merge fe7bf31dd31266d4d23ff567a94cb26afa731361

bus-nonce: 0184c93e7ffd395f133a5675e91992af

## Findings

none

## Evidence

- Round 1. Measured head fe7bf31dd31266d4d23ff567a94cb26afa731361 (still the PR head per ls-remote refs/pull/2932/head at post time). origin/main had moved to b0b2d7697; `git merge-tree --write-tree origin/main fe7bf31dd31266d4d23ff567a94cb26afa731361` exits 0, no conflicts (ev/merge-tree.txt).
- Diff is two files: `dev/programme/triage/s6-batch57.md` and `dev/programme/delivery/2932.md` (the required delivery row). The body says "one markdown file"; the delivery row is the only addition and is expected. No production code, no VERSION, manifest or RELEASE_NOTES touch (ev/version-touch.txt). No claim files, golden fixtures, budgets or closures move, so steps 4, 5 and 14 have nothing to measure.
- Mutation proof re-run with the roster_edit.py `ruling_verdict` reader: P268 ACCEPT, P269 ACCEPT, P270 DEFER; with P268's verdict rewritten to DEFER in a copy the reader returns DEFER, so the gate reads that line (ev/mutation.txt). I did not re-run the seven held-text citation checks or the file-absent null control (they need the roster-branch edit ops); those figures are the body's.
- Figures re-derived at the head: replan.py:100 PRODUCTION lanes, dispatch_tier at 316, dispatch_key at 327; merge_train.py AUTO_TRAIN_FLAGS at 2861 (body says near 2862); standing-merge.md line 9 flag list; train.sh 398 lines; cloud_dispatch _prompt lines 107-160 = 4872 bytes. Roster counts read from the roster branch wave-r10-groups.json at be898eae and at its current head 47184070: instrument 95, owner 14, production 13, rca 12, policy 9, study 7, process 7, 7 with no class; no group has source or hotfix; 11 briefs open Owner-reported/Owner request/User-reported; R10-UX-HEALTH's three files are under custom_components/, R10-ROUND-PLAYBOOK's are dev/audit/README.md and CLAUDE.md. Not re-derived: the claim that exactly 2 of the 11 are live, and the cloud_dispatch line numbers 109-132 within _prompt.
- Class rule (step 6): the body names three carries for the three seams P268 touches (roster_lib/roster_edit, replan, ci_priority.json and reader), each routed to a roster group; review_packet carry_audit: 4 items, 4 routed, 0 unrouted. The packet notes R10-FLOW-TOOLKIT-MODEL and the two others exist on the roster branch.
- Forward-carry (step 10): the three P268 carries are written to the roster groups named in the body; P269 is dismissed as registered by the held append-group op after merge, which the body states needs this file on main first.
- Harness (step 9): packet shows no finder harness named; this PR is a ruling document, not a fix with a measured claim.
- CI at read time (check-runs API, 37 runs): no red. Green: arch-score, budget-raise-gate, codeql x3, delivery-status, policy-docs, wave-script, hassfest, validate-hacs, briefs, closure-scope, arch-instrument, typing, mutation, nightly-status. Still in progress: tests/fast (3.14), coverage, closures, browser, governance/env-matrix, governance/instrument-self-tests. Body's "Red checks: none" agrees. I did not re-run any heavy gate.
