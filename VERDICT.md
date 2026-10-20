Fix review: blocked 67ee6adfd712786da12241bf59bb5b78030c2d80 ci-red: pr-contract is red on both of this head's runs (carry_audit BAD-DEST x3: R10-UPDATE-PR-SIGNALS was not on main yet); the code verifies clean, and a head that merges origin/main at or after 1e30f876 routes 3/3

bus-nonce: 1808b2e15cb51d3f259ff03e92c6a423

Round 5 of R10-UPDATE-PR-LOCK: the split that the three-round rule required after round 4 (98fe31c2, blocked flaky-arm). Measured at head 67ee6adfd712786da12241bf59bb5b78030c2d80 (code head 931e9a0f). The PR head was re-read before writing this, and it is unchanged. The fix-review contract on main matches the head's copy (the roles diff is empty).

## The block, and only the block

- `pr-contract` failed on both of this head's runs: 118467040392 and 118467201379, started at 05:13:17Z and 05:13:52Z. Its log shows `carry_audit.py check` with 3 BAD-DEST lines: `R10-UPDATE-PR-SIGNALS is not a group of the roster`.
- Roster #2475 merged as 1e30f876 at 05:36:19Z, after both runs. It is not an ancestor of this head. carry_audit reads the roster from the checked-out tree, so re-running the same merge ref stays red.
- Against origin/main 558d509d, and against the merged tree 10ebe02c, `carry_audit.py check --body` prints `3 routed, 0 unrouted, 0 bad destination(s)`. At this head it prints `0 routed ... 3 bad`.
- The fix is a head that merges origin/main (the merge is clean), so that pr-contract runs fresh.
- This is not posted as root-cause-unanswered. No pr-contract run started after the head's last workflow concluded (Analyze (python), 05:31:22Z), and contract step 11 withholds that class until one has.
- The body's `## Red checks` answers only round 0's pr-contract reds. The next body should name this one too. Its cheaper detector is the one the body already gives, `carry_audit.py check` run by hand against origin/main before the push. Here it was run before the roster merged.
- No code defect was found. Every other item below verifies.

## RESULT lines (cloud container, Linux)

- RESULT self-test pr_args at head: `pr_args self-test: 56 checks, 0 failed` on 8 of 8 runs. 5 were sequential (seq1-5). 3 ran at once (par1-3), alongside the 10 mutant runs and the base-tree runs. This is the container where round 4's SIGKILL arm failed 7 of 7. The `a SIGKILLed run leaves no stale lock` arm is ok in all 8.
- RESULT self-test cloud_relay at head: `cloud_relay self-test: 74 checks, 0 failed` on 5 of 5 runs.
- RESULT base a65438c4, its own scripts: `pr_args 46 checks, 0 failed` and `cloud_relay 69 checks, 0 failed`. Both match the body.
- RESULT the head's pr_args with the base `update_pr.sh`: `56 checks, 3 failed`, namely the BUSY arm, the TERM arm, and the `mut:unlock` mutant arm. This matches the body.

Mutants: each one is a copy at the head with the full self-test run. Each named arm FAILs.

| mutant | result | the named arm fails |
|---|---|---|
| `mut:lock` deleted | 2 failed | BUSY (75) arm: yes |
| `mut:unlock` deleted | 4 failed | `the lock holder has exited by the time a run returns`: yes |
| `mut:stop` deleted | 1 failed | TERM arm: yes |
| `mut:watch` deleted | 2 failed | TERM arm: yes |
| hand `while True: time.sleep(2)` | 1 failed | `a SIGKILLed run leaves no stale lock`: yes |
| shell-fd lock of 49577add, spliced in | 5 failed | `a child the run left detached does not hold the lock`: yes |
| relay body back to `mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX"` | 2 failed | the body-path check and the dir-removed check: yes |
| relay final `rm -rf "$bd"` deleted | 1 failed | dir-removed: yes |
| relay `urc = 75` line deleted | 3 failed | retried, not recorded failed, not logged OWED: yes |

The mechanisms that moved out are gone from `update_pr.sh`. Grep finds no setsid, pgrp, pgid, drain, holdgrp, `ps` or setpgid. The only `mut:` lines are lock, unlock, stop, watch and prtopic, the last of which predates this PR.

carry_audit routes 3 of 3 against origin/main. The roster group R10-UPDATE-PR-SIGNALS carries all three items verbatim. Its brief states the control as a precondition: every arm deterministic, waits on a condition, never a fixed window. It also covers the ps dependency.

Merge: `git merge-tree --write-tree origin/main 67ee6adf` exits 0 with tree 10ebe02c. No claim file is touched.

VERSION, the manifest and RELEASE_NOTES are untouched. There is no golden or claim drift. The diff is 5 files: update_pr.sh, pr_args.sh, cloud_relay.sh, INSTRUMENTS.md and the delivery row.

CI from the check-runs API: 49 runs. Every run is success or skipped except the two pr-contract failures above; see ev/ci-check-runs.txt.

Instruments: the harness is the PR's own self-test arms, run unmodified. The mutants were built by me: grep -v of each `# mut:` line, the hand `while True` edit, and a python splice of 49577add's lock block for the shell-fd mutant. I also built the cloud_relay sed edits that emulate the base lines.
