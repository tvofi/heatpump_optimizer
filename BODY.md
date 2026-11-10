Fix review: blocked 3e02ec82ddb548512adbdbed658106cef2cb57ff wrong-removal-target: the refusal cleanup removes the lint clone, not the worktree holding the refused edit

## Block
The PR's own finder harness fails on the cascade scenario at this commit (`RESULT: FAIL`). After a refused op, the cleanup removes the wrong path, so the "is on no origin ref" cascade the fix names is not removed.

## Findings
- tools/audit/seat/roster_queue.py:398: `sh("git", "-C", a.edit_checkout, "worktree", "remove", "--force", a.lint_clone)` should remove `a.worktree`. The comment above it says the refused edit is a local commit in the worktree. `a.lint_clone` is the lint clone, so the next op is still refused ("HEAD ... is on no origin ref", rc=2) for the earlier op's fault. When the lint clone is a registered worktree (provisioned at roster_queue.py:407-412) it is deleted instead, and the next refresh_lint refuses it as "is not a directory".
- tools/audit/seat/roster_queue.py `_self_test`: no check covers the refusal cleanup. 62 checks, 0 failed, while the line targets the wrong path. The harness cascade scenario is the only coverage, and it fails.

## Evidence
- `python3 -I tools/audit/seat/roster_queue.py --self-test`: `roster_queue self-test: 62 checks, 0 failed`.
- `python3 -I dev/audit/harnesses/roster_queue_stale_lint.py`: `stale: RESULT: PASS`, `cascade: RESULT: FAIL`, `follow: RESULT: PASS`, `RESULT: FAIL`. The cascade output is op1 `refused rc=4 REFUSED: unrelated`, then op2 `refused rc=2 ... HEAD 919d5ad3d93e is on no origin ref`.
- Mutation: copy of roster_queue.py with line 398 targeting `a.worktree` run through the same harness gives `stale PASS`, `cascade PASS`, `follow PASS`, `RESULT: PASS`. So the one-token target is the defect.
- Not run: CI, per the brief.
