Fix review: merge 1dcb1fde33af27e33c380ccd0311638741684aa2

bus-nonce: c7b83a254e19ca57331c0cc512f3bd98

## Findings

none

## Evidence

- Diff (three-dot against origin/main 26c9d22) touches only dev/programme/delivery/*.md: 8 files, +8/-7 (ev/diffstat.txt). Seven rows rewritten from `**open**` to `**merged <sha>**`, plus the new own row 2979.md (one line, anchors #2979, `**open**`).
- Each row checked against the API and git: #2954 e867edb, #2964 8b3d430, #2967 2ab53fe, #2970 26c9d22, #2971 2f28a21, #2972 da06660, #2974 12c60f0 are all merged, merged_by tvofi. Each short SHA resolves to "Merge pull request #N" on origin/main and is an ancestor of it. Each row's title matches the PR title, except that the roster-group tag in parentheses is dropped (the neutral phrasing the body describes).
- `python3 tools/audit/seat/record_row.py --automerge-check --pr 2979 --head 1dcb1fde...` prints `AUTOMERGE OK #2979 at 1dcb1fde33af27e33c380ccd0311638741684aa2`, rc 0 (ev/automerge-check.txt).
- `git merge-tree --write-tree origin/main HEAD` is clean, rc 0 (ev/merge-tree.txt). `tests/delivery_status.py`: DELIVERY STATUS OK, 75 rowed, 0 pending, 0 overdue. Review packet: no refusals, no advisories, carry_audit 0 findings, figure_lint 1 resolved.
- `## Red checks`: the only concluded red at this head is tests / nightly-status, answered in the body, which also answers `record` and `governance / delivery-status`. `governance / record` is skipped and `delivery-status` is green. No other concluded red.
- CI: `governance / instrument-self-tests` concluded success while this review ran. At the time of the verdict `pr-contract / pr-contract` and `prelude` (superseded duplicate runs) were still in progress, so the merge waits on them as required checks. This is a state note, not a block.
- Mutation proof and null control are n/a: record-only diff, no code to mutate. Commit messages contain no Claude footers or trailers.
