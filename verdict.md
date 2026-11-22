Fix review: merge 6a76c6071db6d7e4abaadcc9b9f4b0605d16c3a5

bus-nonce: 0da85d4885983db007cb8ea87d1d1393

## Summary

Round 1 (first review, scope full). Record-class PR from the hpo-author App: 20 files, all `dev/programme/delivery/<N>.md` row files (19 rows flipped or added as merged, plus its own open row). No production, test or check code; VERSION, the manifest and RELEASE_NOTES.md are untouched.

## Evidence

- RESULT head: the body's `## Head` names 6a76c6071db6d7e4abaadcc9b9f4b0605d16c3a5, the head reviewed (ev/HEAD.txt).
- RESULT rows: every one of the 19 merged SHAs in the rows equals the first-parent merge commit for that PR on origin/main (3728 4ebd430, 3729 f269ecc, 3735 59b17e9, 3737 35402f7, 3814 e4c929b, 3821 608c95d, 3822 8ef4509, 3832 726e5bb, 3836 6f6a85c, 3837 fc06c46, 3839 505ed38, 3840 35c3e31, 3842 2ceb62b, 3843 40e513e, 3846 3a98735, 3850 024895c, 3851 eaaaf24, 3852 0c69bd1, 3853 0ff1b6b); checked by git log on origin/main.
- RESULT figure: `python3 tests/delivery_status.py` at the head prints `DELIVERY STATUS OK -- 20 rowed, 0 pending, 0 overdue`, the same as the body's figure.
- RESULT mutation: the body says n/a (no code lines). I agree. My targeted mutant that turns the 3851 row back to open moves the instrument to `19 rowed, 1 pending`, so it does see a row's state. A mutant that changes a row's SHA (3728 4ebd430 -> 4ebd431) survives; see Findings.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exits 0, and the head is 0 commits behind main (ev/ci-and-merge.txt).
- RESULT CI: `merge_train.py classify 6a76c6071db6d7e4abaadcc9b9f4b0605d16c3a5 --pr 3844` -> `GREEN ... pending: none red: none`. The packet's live digest shows `gate` success at this head.
- RESULT red: the board's red `gate` is not on this head. For the earlier head f150b5dd79, classify prints `WAIT ... pending: gate`: that run was superseded, not failed on this diff. At 6a76c6071db6d7e4abaadcc9b9f4b0605d16c3a5 no context in the owed-reds set is red, so no `## Red checks` answer is owed here. The body still answers record, nightly-status and delivery-status.
- RESULT claims and goldens: no claim file and no fixture changed, so the drift comparison is empty.
- RESULT carry: no forward-carry named (none owed for a record beat).

## Findings

- Follow-up: `tests/delivery_status.py` checks that a row exists and its open or merged state, but not that the row's merged SHA matches the real merge commit. A row with a mistyped SHA passes (mutant 4ebd430 -> 4ebd431 stays OK). I checked all 19 SHAs in this PR by hand, so this PR is correct. The gap is in the instrument, not in this diff, and the rows are written by automation from REST merge facts. Carry: dismissed: instrument scope; rows are generated from API merge facts and every SHA here was verified independently
