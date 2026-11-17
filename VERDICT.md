Fix review: merge 39174541fd3707da591f62d5c08e21af06235d0f

bus-nonce: 7bdb5071677fc301138a83cf9d5b6ca2

## Findings

none

## Evidence

- Head reviewed: 39174541fd3707da591f62d5c08e21af06235d0f (ev/HEAD.txt). It is the PR's head and the body's `## Head`. This is a later round (third) over the reviewed head 2061e87b067922853a5f890dad9ea21d835f593e, and its scope is the delta (packet `## Review scope: delta`). The delta's own commits are 26b20a7faa (merge of origin/main 30f9caac90), 2cb653f2dd (one self-test row), 3e2b3f9a35 and 39174541fd (merges). `review_carry.py` prints FRESH-REVIEW because the own diff moved. The delta has no custom_components/ change, so the scope is not widened.
- Previous verdict, block (merge-conflict, tools/audit/seat/roster_edit.py against #3657): resolved. In 26b20a7faa, the hand resolution against git's conflicted auto-merge tree (ev/resolution-26b20a7faa.diff) touches only roster_edit.py. It keeps both sides exactly: `SET_FIELDS = (..., "class", "gates_finders") + roster_lib.CONVERGENCE_FIELDS`, with `|gates_finders` on the usage line followed by main's `|found_by|...|follows` continuation. The `op_set_field` branches auto-merged. 3e2b3f9a35 and 39174541fd are git's clean auto-merges: each commit tree equals `git merge-tree` of its parents (ev/merge-resolutions.txt).
- Mutation proof of the resolution: I applied each mutant alone to roster_edit.py at the head and restored it afterwards. The worktree was clean after the runs (ev/mutants-resolution.txt).
  - RESULT M1, `"gates_finders"` dropped from SET_FIELDS: KILLED, `318 checks, 3 failed`.
  - RESULT M2, `+ roster_lib.CONVERGENCE_FIELDS` dropped: KILLED, `318 checks, 5 failed`.
  - RESULT M3, `|gates_finders` dropped from the usage line: KILLED, `318 checks, 1 failed`.
  - RESULT M4, main's usage continuation dropped: KILLED, `318 checks, 1 failed`.
  - RESULT NULL, the file unchanged: `318 checks, 0 failed` (ev/self-tests.txt).
  These counts match the body's, although the body labels M1 and M2 the other way round: its M1 is main's side and its M2 is this part's.
- Previous verdict, note (figure-stale, 223 against 249): resolved. The body now states 249 at the head. With 9fb327ecb3's `.claude/workflows/audit-plan.js` copied over the head's copy, `node tools/policy/check-wave-script.mjs` printed `249 passed, 0 failed`; `cmp` confirmed the file was restored afterwards (ev/part3-grader.txt).
- Self-tests re-run at the head (ev/self-tests.txt), each matching the body's `## Figures`:
  - `roster_lib self-test: 101 checks, 0 failed`
  - `roster_edit self-test: 318 checks, 0 failed`
  - `check_scopes.py --repo . --self-test`: rc 0 with `evaluation arms: 66/66 held`
  - `brief_lint.mjs`: rc 0
  - `check-wave-script.mjs`: `249 passed, 0 failed`
- Figure block: `figure_block.py verify` over the body's scope-line block, run with `--base b98c78e0f6144a5ea5b48a032e30bf2d085c2d61 --head 39174541fd...`, printed `1 block(s), 0 refused`, rc 0 (ev/figure-verify.txt).
- Merge with main: `git merge-tree --write-tree origin/main 39174541fd` exits 0 against origin/main 54cb721164 (ev/scope.txt).
- The three-dot diff from merge base b98c78e0f6 is the same 9 files as at the previous round. VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched. `dev/governance/roles/` has no change between the merge base and origin/main, so this contract is current (ev/scope.txt).
- Forward-carry: the body's `Carry: R11-PRE-ROUND-CHECK-GATE` routes. The packet's carry_audit reports `1 routed, 0 unrouted, 0 bad destination(s)`.
- Red checks: tests / nightly-status is failure at the head, but it is not in `merge_train.py owed-reds` (ev/owed-reds.txt), so no answer is owed and it blocks nothing.
- CI: `merge_train.py classify 39174541fd3707da591f62d5c08e21af06235d0f --pr 3633` printed `GREEN 39174541fd3707da591f62d5c08e21af06235d0f pending: none red: none`, rc 0, at 00:06:21Z (ev/classify.txt).
