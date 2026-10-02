Fix review: merge 98dc6bc501bc283d84b93c9452d3daa75ee4c592

bus-nonce: 2b4bd973fbcb9ca413025369f077c258

PR #1842, delta review over the round-1 verdict `Fix review: merge b69961d780511b29af6e8d454c4ff829ec340783`. Measured and live head: 98dc6bc501bc283d84b93c9452d3daa75ee4c592.

## Delta b69961d7..98dc6bc5

- One commit, `record: #1842's own delivery row`; `git diff --stat` reports `docs/delivery/1842.md` only, 1 insertion (`delta.diff`). No code path moved, so round 1's matrix and mutants stand for this head unchanged.
- The row is `- [#1842](…/pull/1842) — **open**, <title> (R9-F10.4)`, the same form as main's `docs/delivery/1839.md` and `1840.md`, and the PR's own row as `delivery-status-tracking.md` prescribes (not a table-end row).
- origin/main 492d84011512e1240e45b5cb4cc5d931e0a046d1 is an ancestor of the head; `git merge-tree --write-tree origin/main 98dc6bc501bc283d84b93c9452d3daa75ee4c592` exits 0 (`merge-tree.txt`).
- `VERSION`, manifest and notes heading untouched (the delta is one file).

## Body

- The body names 98dc6bc501bc283d84b93c9452d3daa75ee4c592 as the head (code head b69961d7 plus the row only), matching what I measured.
- No closing keyword; `gh pr view 1842 --json body --jq .body | bash tools/audit/preflight.sh` exits 0 and prints `clean    no refusal` (`preflight.txt`). Its `check` lines are advisory and were present for the body round 1 passed.

## CI at the head (cited, not re-run)

`commits/98dc6bc501bc283d84b93c9452d3daa75ee4c592/check-runs`: 33 runs, 24 success, 9 skipped, 0 failure/cancelled/timed_out (`check-runs.json`), including `briefs`, `pr-contract`, `delivery-status`, `mutation`, `closures`, `fast (3.14)`. The earlier head b69961d7 carries 24 success, 9 skipped, 2 cancelled (superseded), no red (`check-runs-b69961d7.json`), so no red check owes an answer across the range.

## For the orchestrator

Round 1's notes still hold: brief_lint.mjs is policy and needs tvofi's approving review, and merging this makes #1838 conflict in `.claude/workflows/brief_lint.mjs`.
