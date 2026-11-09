# BLOCKED: r10-process-slim (conflict repair for #3245)

The code is ready. The body cannot pass prepr.sh's `carry` step, because the destination of its Forward-carry closed while this seat was running.

## What is done (on this ref's second parent, c09a9acb7a7d5806c5db8881404ebd808a23daf0)

- 0712679bf merges origin/main 0a803330 into the PR head f5af5b51. Its four conflicts (defect-root-cause.md and its two generated copies, fix-review.md) are resolved by union, and the copies are regenerated with rules_sync.mjs.
- 0aa9d4f2f pays the union's caps by cutting text, not by raising a budget.
- c09a9acb7 merges origin/main 806e952c. Main moved during prepr and then conflicted in governance.yml.
- `git merge-tree --write-tree origin/main c09a9acb` exits 0.
- policy_lint, rules_sync --check, selftest_scope, handoff_push, entities and structure all pass. BODY.md (on this commit) lists the resolution delta.
- No push went to handoff/r10-process-slim, because prepr has not been clean.

## The refusal

prepr.sh at 0aa9d4f2f, with a local handoff/audit-r10-roster branch per Friction r10-process-slim-4:

    REFUSE   carry                  BAD-DEST body item ada60feb: R10-FLY-STAMP-FLUSH-COST: R10-FLY-STAMP-FLUSH-COST is done (resume.stage done); valid targets: unknown (no --pr-group) -- CARRY-AUDIT: 6 finding item(s): 5 routed, 0 unrouted, 1 bad destination(s), at origin/handoff/audit-r10-roster b03fd2f9e

That carry is "delete Nightly's record-autofix beat once no stamp rule reads it". It is still owed: `git grep -c -- '--require-rows' origin/main -- tools/release/stamp.py` prints 8, so the stamp still reads the rows. Its group R10-FLY-STAMP-FLUSH-COST (#3296) merged without retiring them.

Every other prepr step was ok on that run. Run 1 refused `ci predict` with a transient `OSError: Directory not empty .../bg`, and a standalone `ci_predict.py` exited 0. Run 3 refused a predicted pr-contract red for the same carry.

## What unblocks it

The orchestrator chooses a live destination for the Forward-carry: a roster group or a carry file at an open issue. This seat may write neither the roster nor an issue. Then it updates the body's `Carry:` marker, runs `tools/pr/prepr.sh` at c09a9acb (or later), pushes c09a9acb to handoff/r10-process-slim, and runs `body_push.sh r10-process-slim BODY.md`.

One check will be red at the new head, as expected:
- budget-raise-gate stays red until tvofi approves at that head. This is the proposal-triage cap removal, and an approval covers only the commit it was given on.
