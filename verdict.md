Fix review: merge 6c966f403516d2bc06a336110eb3ae50169fc9e2

bus-nonce: 28023f762e8a106513f9e93d876dd2be

Round 1. Reviewed from a detached checkout at 6c966f403516d2bc06a336110eb3ae50169fc9e2.

## Head

6c966f403516d2bc06a336110eb3ae50169fc9e2 (matches the PR body and the live head).

## Red checks

None concluded red at the head. classify: GREEN, pending none, red none (rc 0). The body's governance / record, nightly-status and delivery-status answers are present; none of them is red at this head.

## Evidence

- Record-only: the three-dot diff touches only dev/programme/delivery/*.md (9 files). No production, test, claim-file, VERSION, manifest or RELEASE_NOTES change. Commit messages carry no Claude footer or trailer.
- The eight rows 3049, 3051, 3066, 3073, 3074, 3084, 3096, 3097 already existed on main as "open" lines. This PR rewrites each to "merged `<sha>`" and does not add a second row. The brief expected no existing row; it is a flip of stale open rows, and I judge that correct.
- Each cited SHA is the real "Merge pull request #N" commit and is an ancestor of origin/main: 3049 407eb0c, 3051 239e5e4, 3066 07207ce, 3073 ddf4bfd, 3074 c88d552, 3084 ca63333, 3096 d052f80, 3097 56630e7.
- Each row is one line in the row_line shape. Titles are unchanged apart from dropping the duplicated trailing group tag. 3148.md is new and says open.
- tests/delivery_status.py at the head: OK, 93 rowed, 1 pending (#3047), 0 overdue.
- git merge-tree --write-tree origin/main (f04b25a) merges cleanly (rc 0); main has moved past the PR base 56630e7 and the PR is mergeable-clean.
- Mutation proof and null control: n/a, since no code changes.
- The merge-train classify run is GREEN at this head.

## Findings

None.
