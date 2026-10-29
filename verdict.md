Fix review: merge 850c81c3fbc76a509adbfb5195774ad3d4adecff

bus-nonce: 708e426a5224ad4cdcb68475fc2f3aaa

Round 1. Record-only PR (8 modified delivery rows + 1 new row file). Head measured: 850c81c3fbc76a509adbfb5195774ad3d4adecff, still the PR head at read time (GitHub API `head.sha`).

## Findings

none.

## Evidence

- RESULT rows: each of #2939 `2795780`, #2953 `2033b87`, #2956 `ce5940c`, #2957 `553cee1`, #2958 `20c2051`, #2959 `2fde526`, #2960 `e5ddba1`, #2963 `7274f7f` is a "Merge pull request #N" commit reachable from origin/main (git merge-base --is-ancestor), so the word "merged" is true and the sha names the right PR (ev/merge-commits.txt). Each row is one line anchoring its own PR number and carries only that PR's own edit (open -> merged sha).
- RESULT diff scope: three-dot diff against merge base fbe5837 touches only dev/programme/delivery/*.md (9 files, +9/-8); no other PR's edits, no VERSION/manifest/notes, no claim files, no budgets (ev/diff-names.txt). New row 2966.md says "open", true for this PR.
- RESULT body: head in the body equals 850c81c3fbc76a509adbfb5195774ad3d4adecff; counts and shas in the body match the diff; Mutation proof and Null control n/a is correct for a rows-only diff.
- RESULT merge: `git merge-tree --write-tree origin/main 850c81c3fbc76a509adbfb5195774ad3d4adecff` exit 0, no conflict (ev/merge-tree.txt).
- RESULT red check: `tests / nightly-status` is the only red run on this head. Its log reads "NIGHTLY FAILED: slow failed in the last verification dispatch", run 40948493872 on head e5ddba1, a main commit; this diff reaches no nightly lane, and the check is not a required context. The body's Red checks section names `tests / nightly-status` by full name, says it grades main and answers it (no cheaper detector, standing cost one beat per batch). Answered.
- `governance / delivery-status` is green on this head (python3 tests/delivery_status.py locally prints pending only, not OVERDUE); `governance / record` was skipped. The body's account of these as possibly red on main is not contradicted.
- CI at read time: 41 of 43 runs concluded; `prelude` (rerun) and `governance / instrument-self-tests` were still in progress and not red. CI's heavy runs are cited, not re-run (fix-review.md 11).
- carry_audit at head: 0 findings. figure_lint: 1 resolved, 0 not verified. No finder's harness is named, and none applies to a row-only record.
- fix-review.md on origin/main unchanged against the merge base (empty diff of dev/governance/roles/).
