Fix reviewer for PR #2639, group R10-FLY-GH-READ-RETRY, round 3, head 1cf9ca11b30c639c7608f549ba94a08e9b3f10b1. Round 2 was blocked as retry-rule-unsound (probe/rev-2639-369e5c9b, head b79c3d4f): urllib_wait checked x-ratelimit-remaining==0 before the status, so a 404, 401, 422 or permission 403 with a spent bucket was retried 4 times. Read the group with jq from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. Use the finder harness the group brief names, never the fixer harness. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(a) The bucket is consulted only for the rate-limit codes (403/429 with the rate-limit signal). Every other 4xx makes exactly one call whatever its headers. The new self-test rows for 404, 401, 422 and permission-403 with bucket 0 assert one call, are red at b79c3d4f and green at the head. A mutant that re-orders the checks turns them red. Plant your own 404 with bucket 0, and a real 429.
(b) The rate-limit arm's rows stay green, and the bound and the no-write-retry rule still hold.
(c) ## Red checks names nightly-status with its cause and run id, and answers every other red at the head.
(d) The touched self-tests pass (gh_read, merge_train, record_row, app_approve, pr_args, merge_pr), and carry_audit reads 0 unrouted, 0 bad.

Model for this review: claude-opus-5-5.
bus-nonce: 999f1fb7227192fc4ed414eaeb1919e5
