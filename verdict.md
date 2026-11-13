Fix review: blocked b63d67cc3d9219b6dca0a53b54f679c045320c44 harness: design-trace-missing red-then-green demonstration at 19baca76 and Mac wall time, and the worktree-cwd requirement has a surviving mutant

bus-nonce: 930d29b93c45af129c3d7f9150b6ff2c

## Block

- design-trace-missing (fix-review.md step 9; defect-root-cause.md "A detector must be shown to detect"): the brief asks for a red-then-green demonstration (RED naming mutant_run.py at main 19baca76, nothing once the mutant_run.py Darwin hotfix is on main) and for the wall time of one run on the Mac. The body's own Figures mark both NOT MEASURED, and no tvofi waiver is cited. The stub self-test runs with the platform forced to darwin, so it never touches a real Darwin red. That leaves the detector unshown on the defect it was written for. A Linux seat cannot produce either run, because the Darwin-only /proc read is green on Linux. A Darwin host has to take both measurements, record them in the body, and then hand off again. The detector's two runs go in the report and are not carried past the merge.
- The worktree requirement ("never writes into any checkout it tests") is not pinned. My mutant cwd_repo changes `ctx.run(argv, wt, env)` to `ctx.run(argv, ctx.repo, env)` in darwin_selftest, which runs every self-test in the orchestrator's own checkout, and the self-test still reports rc=0 (ev/mutant-cwd_repo.tail.txt). The case "the heavy slot is held around a detached worktree the row makes and removes" checks the order of the calls but never the cwd the self-tests run in. The fake run must record the cwd, and a case must assert that every self-test ran in the worktree.

## Findings

- The mutant keep_state_dir survives: dropping the HPO_STATE_DIR strip (`if k != "HPO_STATE_DIR"` -> `if True`) leaves the self-test green, so the claim "a self-test never reaches this digest" is untested. Carry: O1
- The mutant wired_filter_dropped survives: dropping `and p in wired` in darwin_instruments leaves the self-test green, because the real-tree case asserts only that mutant_run.py is a member and that every path carries the seat prefix. Removing the filter widens the run to unwired self-tests, and nothing notices. Carry: O1
- The mutant remember_on_wt_fail survives: remembering the tip when worktree add fails would skip that tip forever after one transient failure, and no case covers worktree add failing. Carry: O1
- The row ignores slot-take's exit code. gate_lock slot-take blocks until it takes a slot (tests/gate_lock.py take_slot, wait=True), so a busy slot is safe, but a slot-take that crashes runs the heavy work without the lease. A self-test that hangs past timeout_s 3600 is killed before the tip is remembered, so it re-runs every 900 s pass and takes the slot each time. Low severity. Carry: O1
- The round-end measures (detection lag, refused opens per Darwin red) are owed at round end, as the body says. Carry: O1

## Evidence

- This is round 1 of review. Measured head: b63d67cc3d9219b6dca0a53b54f679c045320c44 (ev/HEAD.txt). It matches the body's ## Head and the handoff-body ref at fetch time.
- No pull request exists yet, so there is no review packet and no CI to read. Red checks: none apply. The owed-reds set is in ev/owed-reds.txt.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test` at the head gives rc=0 in 50 s wall. All 9 darwin-selftest cases are ok, and the 5 named mutants (darwin_gate_dropped, darwin_first_fail_is_last_line, darwin_tip_not_skipped, darwin_red_dropped, darwin_lease_not_released) are each killed by the case the body names (ev/selftest.txt).
- RESULT, my own mutants (ev/my_mutants.py, logs in ev/mutant-*.tail.txt):
  - killed (5): no_detach, no_final_remove, no_prepr (StopIteration crash, rc=1), no_remember, no_take (StopIteration crash, rc=1).
  - survived (4): cwd_repo, keep_state_dir, wired_filter_dropped, remember_on_wt_fail.
- Merge with main: `git merge-tree --write-tree origin/main b63d67cc3d9219b6dca0a53b54f679c045320c44` exits 0 with tree 2eecf319, so it merges cleanly (ev/merge-tree.txt).
- The diff touches no VERSION, manifest or RELEASE_NOTES file, and no claim file.
- fix-review.md is unchanged between the merge base e4ca2d94 and origin/main.
- Figures I could not re-derive: the Mac wall time and the red/green runs at 19baca76. Both need a Darwin host, and this seat runs Linux.
