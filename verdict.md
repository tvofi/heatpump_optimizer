Fix review: merge dac5a8086ec7c0b82a29d7ac9b00c773ed206798

bus-nonce: cce582845d606c56eb42b74831a9abf5

## Evidence

- Review packet: UNAVAILABLE (policy_lint saw an empty path list because the head is already an ancestor of origin/main). I built my own reading from the diff against base 870238e.
- PR #3517 was already merged by tvofi at 2026-11-12T19:24:38Z, so this verdict is retrospective. The head dac5a8086ec7c0b82a29d7ac9b00c773ed206798 is an ancestor of origin/main, and merge-tree against origin/main is clean. CI classify was not run because the PR is closed and merged.
- The diff adds nothing but row files: 10 modifications and 1 addition, all at dev/programme/delivery/<N>.md (ev/diff-names.txt), in 2 commits ("ci: record delivery rows").
- Each of the 10 rows is a single line anchored on its own PR number. Each states "merged" with a short sha that is an ancestor of origin/main and whose commit subject is "Merge pull request #N" for that same N: 3381 d927021, 3428 19baca7, 3430 45d21a6, 3448 43e9547, 3461 005eed2, 3484 402b0e7, 3500 cbe8d93, 3501 2b4515d, 3506 42828bf, 3509 870238e.
- The rewrite of 3381.md replaces the state word "open" with "merged" and keeps the sha and anchor.
- The new row 3517.md reads "open", which is correct at the time it was written. It is the PR's own row, and the next record beat flips it to merged.
- Mutation proof and null control: n/a, a record-only diff with no code.
- Red checks: I did not run `merge_train.py owed-reds`. The body answers record, nightly-status and delivery-status, which are non-required or main-grading checks.
