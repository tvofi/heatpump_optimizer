Fix review: merge 35ede8b8aa9c1c216d5d3bbef9ff35d3589bf95c

bus-nonce: 5f644a1932e5f6468da619b6273394ac

Round 1. Record PR, reviewed at head 35ede8b8aa9c1c216d5d3bbef9ff35d3589bf95c (base c098261, still the PR base; origin/main has since moved to 7d6a95e).

## Findings

None.

## Evidence

- RESULT rows: each of the 8 rows (#2925 08f26aa, #2962 cc930cd, #2987 cf4f6b7, #2992 e035c66, #2994 ca0a6cf, #2995 166647f, #3001 3a9eca6, #3003 c098261) names a SHA equal to the "Merge pull request #N" commit on origin/main (ev/main-merges.txt). The state word is "merged" and the open-row it replaces is rewritten, not duplicated. The GitHub search listing gave no merged_at field, so merged state rests on those main merge commits, not on a separate API read.
- RESULT diff scope: every path is dev/programme/delivery/<N>.md; 8 modifications plus the PR's own 3008.md (open, one line). No duplicate rows (ev/diff-names.txt).
- RESULT merge: git merge-tree --write-tree origin/main head exits 0, clean (ev/merge-tree.txt).
- RESULT carry_audit: 0 finding items. figure_lint: 1 resolved, 0 refused. Body has Head, Figures, Mutation proof (n/a record-only), Null control, Red checks answered, Forward-carry none.
- record_row.py --automerge-check could not run in this seat (HTTP 404 from its API call); not a required check and does not block. The orchestrator's beat runs it with its own credentials.
- CI at read time: completed checks all success or skipped (CodeQL, arch-score, budget-raise-gate, delivery-status, policy-docs, wave-script, hassfest, env-matrix, validate-hacs, briefs, nightly-status). The tests/fast, typing, closures, graders-head-copy, browser, arch-instrument, mutation, closure-scope and instrument-self-tests jobs were queued or in progress. The merge is conditional on them concluding green, as the body's approval line states.
- Role-file drift check against main printed empty for dev/governance/roles/.
- No Claude footer, trailer or session link in commit messages of the range.
