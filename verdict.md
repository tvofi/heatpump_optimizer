Fix review: merge 1779fe5db4b4f0f90e081b0b83a0159edc576fea

bus-nonce: 7dd9db1ebb2c020d6124e0ca6f04b8c1

Round 1, record PR, proportionate review. Head measured: 1779fe5db4b4f0f90e081b0b83a0159edc576fea.

## Findings

none

## Evidence

- RESULT row shape: dev/programme/delivery/3087.md and 3088.md equal row_line (sourced from tools/audit/seat/delivery_row.sh) output with the group "dependabot", byte-for-byte including the trailing newline: ROW3087_MATCH, ROW3088_MATCH.
- RESULT titles: #3087 "build(deps): bump the actions group with 12 updates" and #3088 "build(deps): bump the pip group in /tests with 44 updates" read from the PRs via the GitHub API; both open, authored by dependabot[bot]. Counts 12 and 44 are the titles' own; I did not recount the bumps inside each PR.
- RESULT diff: three-dot diff holds exactly 3087.md, 3088.md and 3094.md (the PR's own row, the one-commit head delta the body names). VERSION, RELEASE_NOTES.md, tests/golden and the claim files are untouched.
- RESULT merge: git merge-tree --write-tree origin/main head exits 0, tree fe204b399062c7775913afa6c6ec9efad274285e, no conflict.
- RESULT structure: python3 tests/structure.py at the head: STRUCTURE RATCHET PASSED.
- RESULT delivery: tests/delivery_status.py --check at the head exits 0 (pending only). The ledger lists merged PRs only, so rows for open PRs are inert until #3087/#3088 merge; the files are in the one-file-per-PR location it reads, so they will satisfy it then.
- RESULT CI: merge_train.py classify at the head: GREEN, pending none, red none. No check was red, so the body's "Red checks: none" holds.
- Body: ## Head names the head; Mutation proof, Null control and Figures are n/a for a record-only change with no production line; Forward-carry none.
- tests/entities.py could not be run here (homeassistant is not installed in this seat); CI's tests passed at the head.
