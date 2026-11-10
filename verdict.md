Fix review: merge 4660c050e431dde01c6b4d889f9d6b7572b90166

bus-nonce: d2847c205c5682c7a8ca3bbb8ff9d6dd

Round: second review (later round, scoped to the delta 97839ed6..4660c050 per the owner ruling of 2026-11-09).

## Evidence
- RESULT head measured: 4660c050e431dde01c6b4d889f9d6b7572b90166 (ev/HEAD.txt). It is still the PR head at verdict time. The body's `## Head` names code head 3a633040ae79c3db452e7d21c91ee5a7e631155f, and `git diff 3a633040 4660c050e431dde01c6b4d889f9d6b7572b90166` is empty, so the two trees are identical.
- RESULT delta is a merge resolution only: auto-merging 97839ed6 with origin/main 0362916a conflicts only in tools/audit/seat/review_packet.py. The head tree differs from that auto-merge tree only inside that file's one conflict hunk, the dict `gather()` returns (ev/resolution.diff). No production code (custom_components/) is in the delta, so the review was not widened.
- RESULT union check on review_packet.py: every line either parent added since merge base 1cabb845 is present verbatim in the head file. The resolution keeps main's rename `approval_owed` -> `required_read` (with `required_reading()` and its `(word, why)` reader at line 544) and keeps this branch's `head_named`, `figure_rc` and `pr_head` keys. The only dropped line is `"approval_owed": owed`, which main itself removed. No head line still references `approval_owed` or the removed `owed` variable. Neither parent's change was lost.
- RESULT `python3 tools/audit/seat/review_packet.py --self-test` at head: 85 checks, 0 failed (ev/review_packet-selftest.txt). This matches the body.
- RESULT `bash tools/audit/seat/bus.sh --self-test` at head: 170 checks, 0 failed (ev/bus-selftest-tail.txt). This matches the body.
- RESULT `python3 tests/structure.py` at head: STRUCTURE RATCHET PASSED. `tests/closure.py select`: MODE: SCOPED, running tests/doc_claims.py and tests/entities.py, as the body states.
- RESULT merge: `git merge-tree --write-tree origin/main 4660c050e431dde01c6b4d889f9d6b7572b90166` exits 0 (tree 895f2149) at origin/main 699f4d9e, with no conflict.
- RESULT CI: `merge_train.py classify 4660c050e431dde01c6b4d889f9d6b7572b90166 --pr 3366` exits 0, `GREEN 4660c050e431dde01c6b4d889f9d6b7572b90166 pending: none red: none` (ev/classify.txt). The body's `## Red checks: none` stands for the required set (ev/owed-reds.txt).
- Inherited red, not this PR's: `governance / instrument-self-tests` concluded failure at this head on `selftest_scope self-test: 103 checks, 1 failed` ("the live job parses (118 steps) and its gating is consistent"). The same self-test fails identically at origin/main 699f4d9e, and the context is outside the `merge_train.py owed-reds` set (ev/instrument-self-tests-tail.txt). Under the owner's 2026-11-09 rulings this is not a blocking reason.
- Previous verdict (probe/rev-3366-72b6ef1b, merge at 97839ed6) had one finding: the body's self-test count was stale by one. It was dismissed there, and this body's figures are re-taken at this head (85 and 170), so it is resolved.
- Policy approval: the delta carries policy files from the earlier head unchanged. The owner's approving review is still required before merge, and it is not mine to give.
- VERSION, manifest, RELEASE_NOTES, the claim files and the budgets are untouched by the delta.

## Findings
none
