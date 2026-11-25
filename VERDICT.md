Fix review: blocked a7a9c09806e600bd3f8f5f38c6741004fe81ad71 introduced-red: tests / briefs fails at this head on carry-3885.json carry 0 control citing dev/audit/harnesses/ci3885_light.py, absent from the tree; clean at base 7f7e0511

bus-nonce: b413e8aec7cec359e5b486ac3c2324e1

## Block

`node tools/policy/brief_lint.mjs` at head a7a9c09806e600bd3f8f5f38c6741004fe81ad71 exits 1: `ERROR [carry-3885.json carry 0 control] path: dev/audit/harnesses/ci3885_light.py: not in the tree, and no tag SHA is cited alongside it`, `TOTAL: 1 error(s) across 41 file(s)` (ev/brief_lint-head.txt). At merge base 7f7e05118feebc6731b854a2a3c7a73b13e4cdd3 it exits 0, `TOTAL: 0 error(s) across 40 file(s)` (ev/brief_lint-base-7f7e0511.txt). CI's `tests / briefs` (job 139001025135) fails on the same line (ev/ci-briefs-excerpt.txt). `tests / briefs` is in `merge_train.py owed-reds`. The harness file exists only on PR #3888's head (4c985103bc48d09c7b21b3c822441f6f902a0891), so landing this PR first turns main's briefs check red until #3888 merges.

To clear it, the carry's control must resolve at this tree. One way is to cite a tag SHA carrying the harness beside the path (brief-citations.md rule 1), e.g. #3888's commit 7eb9b2fd81bbe71be048e730481470de62c0932c, which contains `dev/audit/harnesses/ci3885_light.py`. The orchestrator then decides whether #3888's copy moves with it, because the byte-identity with #3888 would otherwise break.

## Evidence

- RESULT: head reviewed a7a9c09806e600bd3f8f5f38c6741004fe81ad71 (ev/HEAD.txt). Round 1, full scope.
- RESULT: `git merge-tree --write-tree origin/main a7a9c09806e600bd3f8f5f38c6741004fe81ad71` exits 0 (tree 30336e3a702b), so the head merges cleanly.
- RESULT: f125eb72's tree (86018ae57663) equals the automatic merge of 7f7e0511 and 29bd37b5e52d04b5928a4abda9d5fe70d3bc2760. That is the live tip of handoff/audit-r11-roster, so the roster lands unaltered.
- RESULT: carry-3885.json blob d7be7f271e9f is identical at this head, at #3888's head 4c985103, at 7eb9b2fd (the body's cited copy) and at 29bd37b5.
- RESULT: the hand-added tests/closures.json line puts carry-3885.json in `closures["tests/entities.py"]` beside carry-1645.json. CI's `tests / closures` (job 139001421687) concluded success: it re-recorded tests/entities.py (exit 0) and printed no UNDER-SCOPED, only `tests/entities.py lists 3 file(s) this run did not touch (safe: over-scoped)`. `tests / closures-autofix` (139013959493) was skipped, so nothing was re-recorded (ev/ci-closures-excerpt.txt).
- RESULT: VERSION, RELEASE_NOTES.md and custom_components/ (the manifest included) are untouched (ev/checks.txt).
- RESULT: mutation proof n/a: records-only diff, no production, test or instrument code.
- RESULT: the carry_audit in the review packet at this head reports `1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
- CI: `merge_train.py classify a7a9c09806e600bd3f8f5f38c6741004fe81ad71 --pr 3889` still printed `WAIT ... pending: gate red: none` at the last poll (ev/classify-poll.txt), with `governance / instrument-self-tests` running. This verdict does not depend on it: the block is a reproduced, introduced red.
- Note: claims: the body's `## Red checks` says "`node tools/policy/brief_lint.mjs` at this tree exits 0"; at this head it exits 1, as reproduced above.
- Note: root-cause-detectable: tests / briefs: `node tools/policy/brief_lint.mjs`, which tools/pr/prepr.sh can run before the handoff, shows this red in seconds.
