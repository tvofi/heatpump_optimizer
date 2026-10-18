`prepr.sh` step 6d refused a predicted `closures` INERT READS and sent the seat to `ci-autofix.md`. That file names only the bot's route, which needs the push 6d forbids. A child-process read, such as `tests/harness_headers.py` over `dev/audit/harnesses/`, is also one a Darwin `--single` cannot record. On #2371 this cost two refusals and a move that review called metric-gamed. The root cause is in `dev/audit/rca/R10-RCA-INERT-PREDICT.md`. The process state is (d): #2049 (R9-CI-1) and #2129 moved both preconditions of the refusal, and neither change touched 6d.

What changes:
- `tools/pr/ci_predict.py --apply-inert` writes each predicted INERT READS entry through `closure.write_closures`, then predicts again.
- When any INERT READS is predicted, the predictor prints that route.
- The stale premise ("the autofix repaired none") is corrected in `ci_predict.py` and in `prepr.sh`'s 6d comment.
- Three `prepr.sh --self-test` arms pin the apply, the table layout and a null control.

The refusal stays. The bot's repair after the push costs a red `closures` run and a commit on the reviewed head.

A policy draft for `ci-autofix.md` is in the RCA's section 5. It is not landed and needs tvofi's approval.

Part of the R10 root-cause work for #2371.

## Head

03128f922678b73b15d5faf4f11e468d55d3f40d. The self-tests ran at c101fe76639651712ffaf438fe32677926c8e40c. The two heads differ only in `dev/audit/rca/R10-RCA-INERT-PREDICT.md`.

## Mutation proof

With `apply_inert`'s write disabled (`if added and False:`), `tools/pr/prepr.sh --self-test` prints `FAIL --apply-inert writes the predicted entry, and the prediction then clears (got 1, wanted 0)` and ends at `276 passed, 1 failed`, rc=2. The unmutated head ends at `277 passed, 0 failed`, rc=0.

## Null control

At `origin/main` `52f698905`, `--apply-inert` on a diff that changes only the predictor exits rc=0, and `git status --porcelain -- tests/closures.json` is empty. The self-test's `pnull` arm says the same: `--apply-inert leaves the table byte-identical where nothing is predicted (null control)`.

## Figures

- `prepr.sh --self-test`: 277 passed, 0 failed: `tools/pr/prepr.sh --self-test`
- The 6d prediction on this head is quiet: `python3 tools/pr/ci_predict.py --base origin/main`
- The class search counts are in the RCA's section 3. They were measured by the seat's `class_search.py`, which is not in the tree. The commit SHAs are listed there, so they can be re-derived with `git log -- tests/closures.json`.

## Architecture score

Architecture score: dS +0.0000 NULL (`tools/audit/archscore/score.py --diff origin/main`)

## Red checks

none

## Forward-carry

`dev/audit/rca/R10-RCA-INERT-PREDICT.md` section 5 holds the drafted `ci-autofix.md` sentence. It waits for tvofi's approval through the orchestrator.

## Friction

- ci-autofix.md: contradiction: prepr 6d refuses a predicted INERT READS before the push, and ci-autofix.md says wait for the bot, which runs only after it (dev/audit/rca/R10-RCA-INERT-PREDICT.md section 2)
- prepr.sh: stale: line 1741's label holds `` `slot` `` in double quotes, so the shell runs it ("slot: command not found") and the arm prints `ok   0`. The comparison still runs; this is outside this change.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
