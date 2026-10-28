Fix review: merge bb190ecd62b52cc202c58ab5a6d61de9f47ff49e
bus-nonce: 85f1437d4b7a8e41edf81b33feb39075

# Fix review -- PR #2900, triage s7 batch 45: rule P227-P231 (V141-V145)

Round 3. I reviewed head `bb190ecd62b52cc202c58ab5a6d61de9f47ff49e` in a detached worktree at that
head, against origin/main `aaf8af512`. `dev/governance/roles/` has no diff between the merge base
and origin/main.

## Results

- Since the round-2 head `ebbc01eaa`, the only authored commit is `2d296452f`. Its diff hunks
  (`@@ -84`, `@@ -102`, `@@ -120`) all fall inside P228, which runs from line 71 to line 163.
  P227, P229, P230 and P231 are unchanged from the text rounds 1 and 2 verified. The rest of
  `ebbc01eaa..HEAD` is main merges.
- The round-2 F1 re-cut holds. I checked each part against the tree and against the instance log,
  which I fetched again from the API (`ev/gate-122526090837.log`, 4,387 lines, byte-identical to
  round 2's copy).
  - Line 4372 is `FAIL governance / env-matrix: failure (this run)` and line 4373 is the
    unprefixed `validate / validate-hacs: failure (this run)`. Line 4374 is
    `##[error]Process completed with exit code 1.` No other line sits between the outcome line and
    `##[error]`: `summary()` writes only to `$GITHUB_STEP_SUMMARY` (`gate.py:254-259`).
  - These cited lines in `gate.py` read as the ruling says:
    - `:224` is `f"FAIL {why[0]}"`.
    - `:295` is `"\n".join([outcome] + why[1:])`.
    - `:345` pins the single-reason format.
    - `:144-171` walks `required` in table order and de-duplicates with
      `sorted(set(bad), key=bad.index)`. So a set reading is the right one.
  - The Instances line now names both reasons. The stamp fixture is the two-reason log in either
    order. The absent-job null control puts the bad reason second (`tests / browser: SKIPPED (this
    run)`, or a `(run <id>)` source), and a FAIL-line-only mutant must fail that control.
- The rule discriminates. I modelled it myself (`ev/p228_rule.py`, my instrument, not the
  finder's; P228 has no committed harness, because it is a ruling). Results are in
  `ev/p228-rule.txt`:
  - The real instance log is re-run, and so is the fixture in both orders.
  - A SKIPPED or `(run <id>)` second reason is not re-run.
  - The FAIL-only mutant re-runs the SKIPPED-second control, so the mutant is caught.
  - Attempt 2 is not re-run, and a mixed failure is not re-run.
  - The any-match mutant re-runs the mixed case, so that mutant is caught.
  - A `RATE-LIMITED` gate counts as matching.
- Times, from the API again (`ev/p228-jobs.txt`):
  - validate-hacs ran 22:36:42Z-22:37:27Z, env-matrix 22:37:08Z-22:43:03Z and gate
    23:09:58Z-23:10:21Z. This closes round-2 F2: the 23:09:58Z start is now verified.
  - Attempt 2 ran from 01:07:45Z to 01:17:17Z and succeeded.
  - So the red lasted 2 h 06 min 56 s, and the first failure to the re-run took 2 h 30 min 18 s.
    The re-run is due at 23:43:03Z, 1 h 24 min 42 s before the hand re-run. All three figures
    match the ruling.
- The `RATE-LIMITED` clause is correct. `gate.py:288-290` prints
  `RATE-LIMITED reset_epoch=<n> <path>` as the outcome line and exits 3, never reaching `:295`.
  The gate job's `GH_TOKEN` is `github.token` (`ci.yml:340`), which is the installation bucket
  whose exhaustion the instance shows. So that epoch is the due time for the run. See F1 on the
  stated justification.
- Mutation proof, re-run (`ev/mutation.txt`):
  - `roster_edit.ruling_verdict` reads P227-P231 as ACCEPT/ACCEPT/ACCEPT/DEFER/ACCEPT.
  - The P228 carry passes.
  - The heading mutant and the DEFER mutant each refuse the carry.
  - Both null controls (a missing file, an uncited text) refuse.
- Other facts:
  - `merge_train.py` still has 5,831 lines, with `main_green` at 2422 and its `Stop` at 2450.
  - The roster at `de410e4c9` has R10-FLOW-MAIN-GATE at `done` with 1 carry.
  - `dev/audit/rca/ratelimit-recur.md` exists.
- Checks and merge state:
  - Live check-runs at the head (`ev/check-runs.txt`): 38 success, 17 skipped, 0 failure.
    `pr-contract` and `gate` are green.
  - `tests / nightly-status` is green at this head (job 122648451903). main's Nightly
    40595637258 is at attempt 2, completed success at 05:22:43Z.
  - The packet refuses nothing, and `carry_audit` routes 0 items.
  - `git merge-tree --write-tree origin/main <head>` exits 0.
- No version file, claim file or budget is touched. The diff is two INERT markdown files.

## Findings

- F1 (non-blocking): commit `2d296452f` says a RATE-LIMITED gate is a matching job because "it is
  the only printer of reset_epoch". That is false in the tree. `tools/ci/prelude.py:284` prints
  `RATE-LIMITED reset_epoch=<n>` to stderr in the same `CI code` run's prelude job, and
  `tools/ci/sweep.py:160` prints it in gate-sweep. The ruling text does not make this claim, and
  nothing turns on it:
  - A prelude rate-limit is itself a matching failed job.
  - The `gate` that then runs (`if: !cancelled()`) prints a reason that does not have the
    `<job>: failure (this run)` shape, so the gate does not qualify and the run is left as today.
  - The correct justification is the gate's token (`ci.yml:340`).
  Carry: dismissed: the commit message's justification only; the ruling's rule is correct
- F2 (non-blocking): the null control "a `gate` whose first reason names a job that failed on a
  non-infra cause" is decided by the every-match arm before the gate arm is read. So that control
  cannot fail a gate-parsing mutant. The SKIPPED-second control is the one that discriminates, and
  it is present. Carry: dismissed: redundant control, the discriminating one is in the carry text

RESULT p228-instance-rerun: true (gate log 4372-4373, both reasons, set reading)
RESULT p228-null-skipped-second: not re-run; fail-only mutant caught
RESULT p228-null-mixed: not re-run; any-match mutant caught
RESULT mutation: heading and DEFER mutants refuse the P228 carry
RESULT checks: 38 success, 17 skipped, 0 failure; nightly-status success
RESULT merge-tree: rc 0
