Fix review: blocked ad8658c26ad6e9a7d4d0fdbbcce3b07e19b63be7 ci-red: required check gate is red at this head only because codeql / Analyze (python) was cancelled; the diff has no defect, re-run that job

bus-nonce: 4b653fcf7de38b29c76598e2f8dc8fec

Round 2 (resolution-delta review against the merge verdict at 1d6414078555e396b0fa5e23327be31050c5ce2a). Measured at ad8658c26ad6e9a7d4d0fdbbcce3b07e19b63be7.

## Block

`merge_train.py classify ad8658c26ad6e9a7d4d0fdbbcce3b07e19b63be7 --pr 3355` polled from 09:24 to 10:03Z: WAIT until 10:03:20, then RED (rc 1), "red: gate". Both gate jobs at this head (129094469779, run 42591662384, and 129094916756, run 42591663354) log one line, "FAIL codeql / Analyze (python): cancelled". Every other check at the head, including tests / fast, closures, browser, arch-instrument, coverage-ratchet, mutation, typing, pr-contract, arch-score and budget-raise-gate, is success or skipped. I judge the cause infrastructure (a cancelled CodeQL job), not this diff, but a red required gate is not mine to waive and I cannot re-run it. Re-run codeql / Analyze (python) at this head; if gate then concludes green, the review below stands and the head is merge-ready.

## Evidence

- Head reviewed: `ev/HEAD.txt`.
- Resolution delta: V=1d64140 is an ancestor of the head. `review_carry.py V head` prints FRESH-REVIEW (main merges in the range). I compared the PR's own patch: name-only diffs are the same 15 files, and per file the +/- changed lines (md5 of the changed lines) at the old merge base d4f5a413a..V and at ba6fd7e8b..head are identical for all 15 files. The main merges changed the PR's patch nowhere, so the earlier review of the patch holds.
- `git merge-tree --write-tree origin/main ad8658c26ad6e9a7d4d0fdbbcce3b07e19b63be7`: rc 0, no conflict (`ev/merge_tree.txt`).
- `python3 -I tools/pr/figure_block.py --self-test` at the head: 11 checks, 0 failed (`ev/selftest.txt`). `node tools/policy/policy_lint.mjs --self-test`: FIXTURE ok.
- Mutant at the head, verify's `if body != want:` replaced by `if False:`: self-test 11 checks, 1 failed (`ev/mut_verify.txt`); restored, 0 failed.
- Red checks: `governance / delivery-status` is red and the body answers it (main's overdue rows; not a required context). The earlier policy-docs red is answered in the body. The gate red above is a cancellation, not a check this diff turned red.
- Not re-derived: the body's entities (2668) and field_coverage counts; the packet's figure_lint reads 8 resolved, 0 not verified. The packet also printed REFUSE red-unanswered / required-red for `gate` at render time, the same gate red.

## Findings

- Follow-up: re-run codeql / Analyze (python) at ad8658c26ad6e9a7d4d0fdbbcce3b07e19b63be7 so gate concludes green before the train merges; no change to the diff is owed. Carry: dismissed: CodeQL job cancellation, orchestrator-side CI mechanics, not a defect in this diff
