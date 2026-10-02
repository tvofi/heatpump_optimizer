Fix review: merge e2a7f402f58133097e653e35e9ef0d570668fee8

bus-nonce: 3af0a2a7dbbd159df6fe6249b801300c

PR #1844, round 1. Measured head e2a7f402f58133097e653e35e9ef0d570668fee8 (record head f4405d794e646e1b31db38bc6cf9c571b11b8393 + own row), merge base 492d84011512e1240e45b5cb4cc5d931e0a046d1 = origin/main at review time. Live head re-read before push: unchanged.

Harness: the reviewer's own (evidence/harness.py), not the author's. For every docs/delivery/<N>.md changed merge-base...head except the PR's own row, it requires that the head line equals the base line with only `**open**` replaced by `**merged** <8hex>`, that `gh pr view N --json state,mergeCommit` returns MERGED with a mergeCommit oid starting with that 8hex, and that the oid is reachable from origin/main.

RESULT non_delivery_paths=0
RESULT rows_checked=68 ok=68 failures=0 gh_calls=68 (gh failures 0)
RESULT own_row=present: docs/delivery/1844.md, a single line reading **open**, which is the shape delivery-status-tracking.md prescribes for an opened PR's own row
RESULT body_set=68 changed_set=68 base_open_set=68; all three sets are identical (evidence/body_set.txt, changed_set.txt, base_open.txt)
RESULT head_open_rows=1 (only 1844.md); this confirms the body's "after it lists none" for the 68 rows

Body figures re-derived with the body's own enumerator plus my harness: merged 68, closed-unmerged 0, skipped-open 0, gh failures 0. All four confirmed.
Row shape: `**merged** <8hex>,` matches the 11 rows already in that shape at the base.

Null control (evidence/nullcontrol-nc*.txt). Each run corrupts one row in a scratch copy:
- nc1 flips the last hex digit of #1720's sha (2d012406 -> 2d012400). Result: FAIL #1720 sha mismatch, failures=1
- nc2 puts #1721's real merge sha into #1720's row. Result: FAIL #1720 sha mismatch, failures=1
- nc3 alters #1720's title text. Result: FAIL #1720 text, failures=1

Steps not applicable:
- Mutation proof (step 1), drift claims (step 4) and class enumeration (step 6): the diff writes no code, so none applies.
- VERSION, manifest and notes heading: untouched. The only changed paths are under docs/delivery.
- Paths: docs/delivery is neither in POLICY_GLOBS nor code-owned.

Merge and CI:
- `git merge-tree --write-tree origin/main <head>` exits 0, so there is no conflict.
- Head CI, from the commit check-runs API (evidence/check-runs-e2a7f402f58133097e653e35e9ef0d570668fee8.txt): 35 runs, 24 success, 9 skipped, 2 cancelled, 0 failure.
- The two cancelled runs are superseded runs of pr-contract and budget-raise-gate. Each has a later successful run at the same head.
- The record head f4405d79 has 0 failures (5 cancelled, superseded).
- delivery-status and policy-docs are green. The body's "Red checks: none" holds, so no root-cause trigger is owed.

Forward-carry: the body declares none. A status-truthing record changes no later stage, so I agree.
