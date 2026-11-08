Fix review: merge f6d7be0cd4ef22a353d72532ca18aae38089e5cc

bus-nonce: 3068bdf65752a20a3c9909a4aedff3e1

## Summary

First-round adversarial fix review of #3327 (R10-HOTFIX-SWEEP-SETTLE-LOOP) at head f6d7be0cd4ef22a353d72532ca18aae38089e5cc, merge base 4a9d2d5425ea13e728dca20aff15d7f76345dc73. I re-ran the finder's harness at both ends: 86 re-runs at the base and 1 at the head. Reverting the settle logic brings back 86. Every mutant fails the self-test. The head merges cleanly, CI is GREEN, and every figure in the body re-derives.

## Evidence

- Roles current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. The packet rendered with refusals: none.
- Finder's harness, `dev/audit/harnesses/r10_rca_sweep_settle_loop.py replay`, run from a detached worktree of handoff/r10-rca-sweep-settle-loop at 95f3e79e. Its harness and fixture are ae2bceee plus a0ee437f's repo_root fix. I passed `--ci` as `git archive` of each end (ev/harness_both_ends.txt):
  - base 4a9d2d54: `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`. This reproduces the finding.
  - head: `RESULT replay reruns=1 max_attempt=2 sim_minutes=1 alarm=no`.
  - null control `--no-restamp`: `reruns=1 max_attempt=2` at both ends.
- Perturbation with the finder's harness. Each line is a mutant of head sweep.py (ev/mutants.txt, ev/selftest_mutants.txt):
  - whole sweep.py reverted to base: replay 86, self-test 7 failed.
  - `sources()` counts skipped jobs again: replay 86, self-test 5 failed.
  - `source_after()` reads every non-gate job: replay 86, self-test 5 failed.
  - `settled()` returns False: replay 1, self-test 1 failed.
  - `settled()` accepts any actor: replay 1, self-test 1 failed (the tvofi null).
  - body's M3, `settled()` drops `not source_after`: replay 1, self-test 1 failed.
  - body's M4, settle skips `settled` (`if False:`): replay 1, self-test 1 failed.
  - What this shows: the skipped-is-no-source change alone accounts for the harness's 86 to 1. The `settled()` arm is pinned only by the fixer's self-test (see Findings).
- Self-tests at the head tree (ev/selftests_head_tree.txt): `sweep self-test: 60 checks, 0 failed` and `gate self-test: 77 checks, 0 failed`. Both match the body.
- Body figures re-derived:
  - base self-test: 7 failed.
  - #3308 replay posts (ev/rec3308_posts.txt): two posts from each of the three runs at the base (gates 128721143069 and 128721143539), and `[]` from each at the head.
  - The body's base 4fe7d593 and the merge base 4a9d2d54 carry identical tools/ci/sweep.py, sweep_selftest.py and gate.py.
- Not re-derived: the recorded attempts 39, 25 and 24 and the fixture's provenance. I did not re-read them, to keep REST off the shared bucket. I took them as recorded in the body.
- Class rule, run as the body states (ev/class_census.txt): outside sweep.py it returns gate.py 662, 664, 682, 739 and 740, all inside `self_test()` (def at line 360). That confirms the body's disposition.
  - A wider grep over tools/ also shows audit-seat readers (ci_critpath.py, governance_cost.py). They already exclude skipped jobs and re-run nothing, so they are not this class.
- Untouched (ev/untouched.txt, three-dot): VERSION, manifest, RELEASE_NOTES.md, both claim files, tests/closures.json and tests/structure_budgets.json. `env_drift.py --claims-only <base>`: ok. `tests/structure.py`: STRUCTURE RATCHET PASSED.
- Delivery row: dev/programme/delivery/3327.md is in the three-dot diff.
- Merge: `git merge-tree --write-tree origin/main <head>` rc=0, no conflict (ev/merge_tree.txt).
- CI: `merge_train.py classify <head> --pr 3327` exited 0, `GREEN f6d7be0cd4ef22a353d72532ca18aae38089e5cc pending: none red: none` (ev/classify.txt). A live get_check_runs read returned 68 runs on one page, with no failure or cancellation in any. The body's "Red checks: none" holds, so step 11 is not triggered.
- Accepted per the brief: the gate.py docstring hunk forces MODE: FULL. CI ran FULL green.
- Head check: the body names handoff 6158186e. The head f6d7be0c adds only the main merge (340b5e23) and the delivery row, and sweep files are identical. I measured f6d7be0cd4ef22a353d72532ca18aae38089e5cc, and it is still the PR head.
- This review's own probes (ev/attack_pair.py, ev/attack_mutual.py) are my instruments, not the finder's.
  - A bot re-run pair where the lower decides green and the higher defers to it: at the head the settle sweep from the higher leaves it, but the lower's covering sweep (`run()`, "completed red") still re-runs the higher. No regression.
- Round: first.

## Findings

- Residual: liveness trade in `settled()`. Suppose both gates of a bot re-run pair defer to each other again through a lagging listing, and no source finishes after either start. At the head, no sweep re-runs either gate, and both stay red until a new push. At the base, the lower id was re-run once.
  - Probe: ev/attack_mutual.py. Base posts `jobs/10/rerun` from both runs; the head posts `[]`.
  - The PR asserts this outcome deliberately (the self-test "overlapping pair ... re-run by github-actions[bot] ... is final"). It trades one rare recovery for bounded re-runs, which is sound for a hotfix. The body does not name the residual.
  - Carry: R10-RCA-SWEEP-SETTLE-LOOP
- Follow-up: the finder's replay World does not model `triggering_actor`, so it never exercises fix (2), `settled()`. Only the fixer's self-test pins that arm (M2, M3 and M4 all leave the replay at 1). The RCA harness should model the bot actor so the second mechanism has a finder-side measurement.
  - Carry: R10-RCA-SWEEP-SETTLE-LOOP
