Fix review: merge 7dc1c501a4dcd18f8a54383295a9d873880cf244

bus-nonce: 6c17ebe104d960f16c0e3bcb54267f61

Round 1. Record PR (mechanical beat R9-FR-10), measured from a detached worktree at 7dc1c501a4dcd18f8a54383295a9d873880cf244.

## Head
7dc1c501a4dcd18f8a54383295a9d873880cf244, base 0166aefd7. PR body names this head.

## Red checks
No concluded red check at the head across the whole check-run set (46 runs). merge_train classify: GREEN, pending none, red none. The body's answers for record / nightly-status / delivery-status are moot: all skipped or success.

## Evidence
- Three-dot diff: only dev/programme/delivery/{3047,3050,3118,3141,3142,3155}.md; no production, test, claim, VERSION, manifest or RELEASE_NOTES change.
- Each existing row (open) becomes merged with its SHA; each SHA matches the real merge commit on origin/main: 3047 f04b25a, 3050 0166aef, 3118 6d5c235, 3141 7f849a2, 3142 a2d8797. Each row is one line; titles and group phrasing are unchanged from the open rows, with only a trailing period added. 3155.md is this PR's own new open row.
- python3 tests/delivery_status.py at head: DELIVERY STATUS OK, 99 rowed, 0 pending, 0 overdue.
- git merge-tree --write-tree origin/main head: clean, rc 0.
- Roles contract unchanged since the merge base. Mutation proof and null control n/a (no code). carry_audit: 0 findings.
- Carry text: forward-carry none; nothing owed.

## Findings
none
