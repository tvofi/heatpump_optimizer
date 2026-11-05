Fix review: merge 645f009eb00999f26bb93b469412e5ef8c21e0d7

bus-nonce: fc0e797ff493d077dba6fab342e85447

Round: delta re-review of 749a3161 (blocked root-cause-unrecorded), head 645f009eb00999f26bb93b469412e5ef8c21e0d7 measured and still the PR head at posting.

## Evidence

- RESULT carry: review_carry.py 749a3161 645f009eb00999f26bb93b469412e5ef8c21e0d7 prints FRESH-REVIEW (branch commits change content), so the delta was re-reviewed by hand. Delta since 749a3161 in the PR's own files is one comment line in tools/audit/seat/body_push.sh (ev/body_push_delta.diff): "(handoff_push.sh, app_push.sh)" became "(its guard and the author-identity guard)". Comment/text only; no code line changed.
- RESULT pusher census: `bash tools/audit/seat/pr_args.sh --pushers` at the head exits 0, 0 OPEN lines (ev/pushers_at_head.txt). Null control: the same command in a worktree at 749a3161 prints "OPEN tools/audit/seat/body_push.sh: undispositioned -- it names a pusher", exit 1.
- RESULT main merges: three-dot diff origin/main...head lists 6 files (ev/threedot_stat.txt), all this PR's own; the two main merges (97cbe20b0, db127a753) brought nothing else into them. Base 0ae75bf3.
- RESULT checks: all check-runs of the head read (68 total, one page of 100). Concluded reds: governance / delivery-status (log: only other PRs' rows OVERDUE, #3174, #3091, #3089, #3192 ...; log states "NOT a required context") and tests / nightly-status (log: unrequired, repo-wide nightly state). Neither reads anything this diff changes beyond the orchestrator's added row dev/programme/delivery/3222.md, which is not among the overdue rows. governance / policy-docs and instrument-self-tests are success at this head (machinery_budgets.json present via main). pr-contract success. No cancelled runs at this head. merge_train.py classify 645f009eb00999f26bb93b469412e5ef8c21e0d7 --pr 3222 exits 0: GREEN, pending none, red none.
- RESULT body: ## Head names 645f009eb00999f26bb93b469412e5ef8c21e0d7; ## Red checks names instrument-self-tests, policy-docs, delivery-status and nightly-status with answers; pr-contract green on it. Small body slip, not blocking: the delivery-status line says the diff touches no delivery file, but it adds dev/programme/delivery/3222.md (a new row, not a deletion; the red is other PRs' overdue rows). The ## Head section also carries a stray bare SHA line (ab764c58).
- RESULT merge: git merge-tree --write-tree origin/main head exits 0, no conflict, no MERGE-CLAIM line.
- RESULT claims/version: three-dot diff touches no claim file, golden, budget file, VERSION, manifest or RELEASE_NOTES; tests/structure.py prints STRUCTURE RATCHET PASSED with no raise.
- Not re-run (cited from CI, per fix-review step 11): gate, mutation. The earlier code measurements (mutation proof, figures) carry from the previous verdict, which found no code finding; the code is byte-identical outside the comment.
