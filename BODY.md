The pre-edit hook decided its RELEASE_NOTES heading rule from the top-level new_string, content and new_source fields. MultiEdit, which the matcher admits, carries its text in edits[*].new_string, so a MultiEdit could write a new version heading on a branch without a refusal (round-10 D11-s1-01, class I3: 16 seams, 1 escape). The rule now also reads edits[*].new_string, one entry per line, so a heading in a later edit still starts a line; a malformed edits value is skipped and the hook still fails open.

Closes #2220.

## Head

6d0df376aca755d3c6fd2a67be4d9623f92c555f

## Mutation proof

Each mutation is of the predicate or the join, not the tail, and each turns a case in `bash .claude/hooks/pre-edit.sh --self-test` red:
- edits branch disabled (`isinstance(edits, list)` to `False`): 2 red (MultiEdit heading, later-edit heading).
- dict entries not read: 2 red, and 1 red on the mixed-list case [7, heading].
- join with a space instead of a newline: 1 red (heading in a later edit).
- heading predicate `"## "` to `"### "`: 3 red.

## Null control

Unmodified tree: `python3 dev/audit/rounds/round10/D11/s1/pre_edit_multiedit.py` reads escaped_heading_writes=1 with control_refused=1; the sweep `dev/audit/rounds/round10/D14/I3/hook_shape_seams.py` reads seams=16 escapes=1. Fixed head: 0 and 16/0. The sweep's perturbed arm, measured on the fixed head: dropping new_string from the tuple gives escapes=1, dropping the edits read gives escapes=1, both give escapes=2 (clean arm 0). The self-test's null controls (a MultiEdit body line, malformed edits, non-object entries) stay allowed.

## Figures

- self-test 22 passed, 0 failed (was 16): `bash .claude/hooks/pre-edit.sh --self-test`
- hook wired and self-testing: `node tools/policy/policy_lint.mjs --hooks`
- escapes 1 to 0: `python3 dev/audit/rounds/round10/D14/I3/hook_shape_seams.py` (from handoff/audit-r10-register)
- arm B of #2220 (yield.mjs, D13-s1-01) was closed by #2294, merged as 98fe51b42; this change is arm A, the hook

## Red checks

none

## Forward-carry

none

## Friction

none
