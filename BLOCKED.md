# BLOCKED: r10-gh-read-residue-p3 (repair of #3682, fix review blocked d5ba8b8ce56ba02776b02a1143657a8c98aec4d9)

Question: prepr.sh step 6d refuses with a predicted `tests / closures` red that its named repair does not clear and that CI does not produce: may I hand off with it named in the body, or does the orchestrator record tests/entities.py's closure (or rule the ci_predict arm) first?

Code: 4b0091b631a2e82950061c7b000bfd14bc51e726 (this commit's second parent; d5ba8b8c plus two commits). The block and both findings are built and proven; the body is BODY.md here.

## The refusal

`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at 4b0091b631, rc=1, one refusal left after the figure line was repaired (`--body-check` then passed: figures 7 resolved, 0 refused):

    PREDICT tests / closures SELF-TEST READS UNDER-SCOPED tests/entities.py: tools/audit/seat/owed_unactioned.py (its run of tools/audit/seat/orchestrator_tick.py's self-test, recorded by closure._exec_record)
    REFUSE   ci predict   CI PREDICT: 1 predicted red(s) on tests / closures

- The named repair, `bash tests/derive_closures.sh --single tests/entities.py` (Linux, rc 0, "updated 1 closure(s)", 582 files), leaves tests/closures.json byte-identical, and `python3 tools/pr/ci_predict.py --only self-test-reads` predicts the same red after it.
- The prediction is not this repair's: the same command at d5ba8b8c (detached worktree, clean) prints the same line.
- CI does not produce it: at d5ba8b8c, `tests / closures` completed `success` (check-runs read) and `merge_train.py classify d5ba8b8c... --pr 3682` printed `GREEN ... red: none`.
- Probable cause, not verified further: tests/entities.py runs `orchestrator_tick.py --self-test` as a subprocess (the "orchestrator tick's self-test runs where roster_lib changes" block), whose reads the `--single` recording does not attribute to entities.py, while ci_predict's arm records the tick's self-test directly with closure._exec_record. A repair is in ci_predict.py or the recorder, outside this group's brief ("No other change").

## Other notes

- `refs/heads/handoff-wip/r10-gh-read-residue-p3` held round 1's BLOCKED commit 2a133b7cef, not an ancestor of the PR head, so a step push was refused as non-fast-forward; this commit merges it so the push is a fast-forward, nothing forced.
- Every other step of that prepr run is ok or skip, including self-test 562 passed 0 failed and claim files byte-identical. `git merge-tree --write-tree origin/main HEAD` rc 0 at origin/main 38bf516bdd.
