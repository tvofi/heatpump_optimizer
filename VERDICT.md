Fix review: merge 3f5400667c3a726b1d63c2f861f83488a80fadf4

bus-nonce: 508cecf4b349a024fb05e981235af1d5

Round 1 (no earlier verdict on this PR is visible to this seat). Measured head 3f5400667c3a726b1d63c2f861f83488a80fadf4, re-read from refs/pull/2638/head after CI concluded: unchanged. Detached worktree at that head; role contract read from origin/main 4e38e7d7b (no roles/ diff against the merge base).

RESULT head=3f5400667c3a726b1d63c2f861f83488a80fadf4 moved=no
RESULT diff=3 files +99 -3 (tests/entities.py +64, tools/policy/policy_lint.mjs +34 -3, dev/programme/delivery/2638.md +1)
RESULT version_manifest_notes_touched=no claim_files_touched=no budgets_touched=no code_owned_paths_touched=no

## 1. definesJob / contractWorkflowFiles
The change holds. A job is a definer when `  <id>:` opens it, unless its own body carries a job-level `    uses:`. The body is the lines indented 3 or more spaces, skipping blank and comment lines, and it stops at the next two-space key. A step's `      - uses:` does not match `^    uses:\s`. assertAcceptance now calls contractWorkflowFiles() in place of the text match, and the rule that exactly one file defines the job is unchanged: 0 or 2 files still build the `(N files define pr-contract)` WORKFLOW, which reads null and refuses.

## 2. Mutation proof (ev/mutants.txt; my block runner executes the two checks' text from entities.py at the head, ev/runblock.py)
RESULT main_lint (origin/main 4e38e7d7b): both checks FAIL (definesJob is not exported, parsed={})
RESULT M1 caller rule dropped: caller check FAIL (caller=true, plant_one=['a.yml','ci.yml']); the null check holds
RESULT M2 body runs into the next job (no break): both FAIL (definer=false, plant_one=[], plant_two=[])
RESULT M3 step-level `- uses:` counted as a call: both FAIL (tree=[])
RESULT M4 body ends only at column 0: both FAIL (definer=false)
RESULT M5 absent job reads as defined: null check FAIL (other=true, the tree lists 16 files)
RESULT M6 blank line ends the body (my own mutant): SURVIVES. The two checks do not pin the blank-and-comment skip: no fixture has a blank or `#` line between `pr-contract:` and `uses:`. Not blocking; the PR claims no such behaviour. If it is wanted, plant a caller with a comment line before `uses:`. The real U0c caller has none.
RESULT clean head: both ok
Null controls at the head hold: definer=true (steps use actions, the next job is a caller); other=false; plant_two=['a.yml','b.yml']; tree=['pr-contract.yml'].

## 3. Lint across trees (ev/lint_runs.txt and the logs)
RESULT u0c d22b5f303 + main's lint: rc=1, FIXTURE VACUOUS: .github/workflows/(2 files define pr-contract) is unreadable
RESULT u0c d22b5f303 + U0c's own lint: rc=1, the same line
RESULT u0c d22b5f303 + head's lint: rc=0, 0 FIXTURE VACUOUS
RESULT origin/main 4e38e7d7b + head's lint: rc=0, 0 FIXTURE VACUOUS (main's own lint on main: rc=0)
RESULT head tree + head's lint: rc=0
RESULT merge result (origin/main 4e38e7d7b + head, tree 2b19347aa) + its lint: rc=0; the two checks ok

## 4. Is it policy under CLAUDE.md?
No. tools/policy/policy_lint.mjs is not named in CLAUDE.md, not matched by POLICY_GLOBS, and not code-owned in .github/CODEOWNERS (decision 0013: the governance scripts that required jobs execute carry no owner and are restored from the base). Test the honest description: this changes how the instrument recognises the one definer. It does not change what a seat must do; the rule that exactly one file defines pr-contract stands. It is a policy instrument, not policy. No owner approving review is required by CLAUDE.md, and the body's mandate (6329234399) is enough for the orchestrator to approve at merge. Nothing in the diff is code-owned.

## 5. CI and the body's figures
RESULT check_runs_at_head=all concluded, 0 red (ev/check-runs.tsv). policy-docs success (it grades with main's lint, which passes on this tree). pr-contract success after the last push. fast (3.14): ALL 2404 ENTITY CHECKS PASSED, 5 scripts passed, 30 scoped out, GATE_SCOPE_BASE=4e38e7d7b (ev/fast_excerpt.txt). closures, coverage, coverage-ratchet, mutation, instrument-self-tests, structure-related lanes and CodeQL: all green or skipped.
RESULT merge_tree vs origin/main 4e38e7d7b: rc=0, clean, no MERGE-CLAIM lines (ev/merge-tree.txt)
RESULT structure.py at head: STRUCTURE RATCHET PASSED
No check is red, so no root-cause trigger is owed.

Body figures that do not hold literally at this head. All are record errors, none blocking:
- "origin/main...HEAD: 2 files, 98 insertions, 3 deletions" holds at the code head 4ef641145. At 3f5400667 it is 3 files, +99 -3, because of the delivery row; the body's Head section names that row commit, so the gap is accounted for.
- "4ef641145 ... one commit on origin/main d6308d77c5d0" is wrong. 4ef641145's parent is e45fc34fb (the base its Red-checks read cites). d6308d77c came in through the merge f4db5e7ab, as the body's next paragraph says.
- The scoped-gate figures ("2 script(s) run, 31 scoped out", "4 of 2401 ENTITY CHECKS FAILED", the 4 py-spy reds being seat-local) are the fixer's machine at the code head. CI at this head reads 5 run / 30 scoped out and 2404/2404 passed. I could not re-run entities.py locally: this container's Python lacks voluptuous, and there is no seat venv on PATH. I cite CI's run instead.
- "Red checks" reads check-runs at origin/main e45fc34fb, not at the PR's head. At this head none is red (above).

Forward-carry: the body names the carry R10-CI-LAYOUT-P2 (P2b drops U0c's known template-arm red once this is on main). This is a pre-PR for that same group, and section 3 measures the precondition: U0c's tree goes rc 1 -> rc 0. I did not open a roster carry SHA; none is named.
