Fix review: merge 190ec599dac05e7a19e7639376c737d53ba40685

bus-nonce: 64073b5500bf244dac4adede47d85e74

## Scope

This is a later round, reviewed as a delta (fix-review.md step 12). The previous verdict was `Fix review: merge 80779d2e74` (verdict/3484, review/3484, probe/revt-r10-hotfix-opener-unblock-636931f7), and 93e4697879 was its main merge. `review_carry.py 93e4697879 190ec599da` prints `FRESH-REVIEW` (ev/review_carry.txt), so this round reviews the delta `93e4697879..190ec599da`:

- `cf26b254e6` merges origin/main `5365b18437` (v7.1.12) into `93e4697879`. Its one conflict is `tools/audit/seat/beatd.py` `cmd_run`.
- `f08baa3673` and `92ecb6c16e` are a closures re-record and its withdrawal. Their net effect is nil: the tree of `92ecb6c16e` equals the tree of `cf26b254e6`.
- `8c7ac4ce74` merges the handoff `92ecb6c16e`.
- `190ec599da` merges origin/main `6e100ef698` (#3479).

The delta touches no production code under `custom_components/`, so the review is not widened. The PR's own diff against main is unchanged: six files, all instruments, tests or records (ev/pr_files.txt).

## Evidence

- Head: `190ec599dac05e7a19e7639376c737d53ba40685`, which `git ls-remote` shows as both the branch and `refs/pull/3484/head` at verdict time. The PR body's `## Head` names it.
- Conflict reconstruction for `cf26b254e6`: `git merge-tree --write-tree 93e4697879 5365b18437` exits 1 with one conflict, `tools/audit/seat/beatd.py`. The conflicted file is ev/beatd_conflicted.py. The only difference between the resolution and the conflicted tree is the `cmd_run` hunk (ev/resolution_vs_conflicted.diff):
  - main's side contributes the `launch.json` write;
  - the branch's side contributes `beat = Beat(...)`;
  - the resolution keeps both, with the write first, then `beat = Beat(...)`, `rc = beat.run(...)` and the `if beat.restart: os.execve(...)` restart.
- I compared the three sides of the region at merge base `14c0012eb4`:
  - The base had `return Beat(...).run(...)`.
  - Main kept that return and added the write before it.
  - The branch replaced the return with the `beat`/`rc`/execve form.
  - The union drops neither side's clause, and it does not revive the base's `return Beat(...).run(...)`, which both sides removed.
- Read-back, my own check (ev/readback.txt, empty):
  - Every line added over `14c0012eb4` by `93e4697879`, by `5365b18437` and by `6e100ef698` is present in the merged `beatd.py` (`grep -qxF` per line), with 0 MISSING.
  - Every line removed by either side is absent from the merged file, with 0 REMOVED-BUT-PRESENT.
- `190ec599da` is a clean merge: `git merge-tree --write-tree 8c7ac4ce74 6e100ef698` exits 0, and its tree equals the actual merge's tree, so no hand edit was made.
- The branch's `beatd.py` delta against main `6e100ef698` is line-for-line the same as its delta against the old base `14c0012eb4` (ev/beatd_main_to_head.diff, ev/beatd_pr_side.diff). The merge therefore changed none of the reviewed Part A code.
- Both clauses are pinned at the merged head:
  - Branch side: `beatd.py --self-test 9` prints `beatd self-test: 34 checks, 0 failed` (ev/beatd_st9_head.txt). Each m9_* mutant turns its named check red, including `m9_no_exec` on the execve restart.
  - Main side: my own mutant renames the `launch.json` write in the merged file. `hooks_setup.py --self-test` then fails 1 check: `beatd: run at the floor starts, and records its cwd, argv and HPO_* environment` (ev/mutant_no_launch_hooks_setup.txt). Unmutated it prints `hooks_setup self-test: 61 checks, 0 failed` (ev/hooks_setup_selftest_head.txt).
  - Full `beatd.py --self-test` at the head prints `beatd self-test: 157 checks, 0 failed`, rc 0, which matches the body (ev/beatd_selftest_all_head.txt).
- Interaction between the two clauses: `RESTARTED_ENV` is `HPO_BEATD_RESTARTED`, so a beat that has restarted records the guard in `launch.json`'s `HPO_*` env, and `liveness.py` relaunches with it. That guard refuses only while origin/main still equals the sha the beat restarted to and the checkout is behind it. A relaunch that carries it can therefore only suppress a second restart to the same sha, which is the guard's purpose. It is benign, and I record no finding.
- `tests/closures.json` is byte-identical to origin/main `6e100ef698` (empty `git diff --stat`). The body's account of the withdrawn `--single` re-record is consistent: `cf26b254e6..92ecb6c16e` has an empty tree diff. No metric moves, and no budget, claim file, golden, VERSION, manifest or notes heading is in the PR diff.
- At the head:
  - `closure.py select --diff 6e100ef698` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (ev/scope.txt).
  - `structure.py` prints `STRUCTURE RATCHET PASSED` (ev/structure.txt).
  - Both match the body.
- Merge with main: `git merge-tree --write-tree origin/main(2b4515dc52) 190ec599da` exits 0 (ev/merge_tree.txt).
- CI: `merge_train.py classify 190ec599da --pr 3484` printed WAIT (rc 3) seven times, then `GREEN 190ec599dac05e7a19e7639376c737d53ba40685 pending: none red: none`, rc 0 (ev/classify8.txt). With CI concluded, the review packet re-renders with rc 0 and no refusal (ev/packet_render.txt). The first render refused `introduced-red: unreadable` only because instrument-self-tests was in progress. No red exists, so the body's `## Red checks: none` stands.
- Roles: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Figures I could not re-derive: the body's `--single` recording figures (75 to 1644 `inert_reads` entries, 1569 new) and its `prepr.sh` self-test 6b failure belong to a withdrawn commit and do not reach the head. I did not re-run them. The field figures stay host-only, as in the previous round.
- Open items of the earlier verdict: its three Follow-ups (`fresh()` `self.stop.set()`, the exec-env guard, and the BEAT-STALE/reset/untracked mutants) were carried to R10-SEAT-IDENTITY-P5 and are settled by that carry. The merge did not touch that code, as the identical branch delta above shows. The harness-stale Friction is likewise carried to R10-SEAT-IDENTITY-P5.
- Round: second review of this PR (the first merge verdict, then this delta).
