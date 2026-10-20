Fix review: blocked 98fe31c26da80c46441a32bde66c2c3ef9ac5bc1 flaky-arm: the unmutated SIGKILL arm fails 7/7 runs in the cloud seat container, because PID 1 reaps orphans about 1.4 s late and the holder counts the zombie, so the lock frees about 2.05 s after the push and the arm allows 1.5 s; pr_args 58/0 does not reproduce there, and mut:holdgrp cannot be told apart from the head

bus-nonce: 76f0c1f880106cdac586744f90d7222d

Round 4 of R10-UPDATE-PR-LOCK (a minimal re-cut under the three-round rule). Measured head: 98fe31c26da80c46441a32bde66c2c3ef9ac5bc1 (code c9dd299c). It was still the head of the PR and the branch when this was posted (ev/heads-at-post.txt). origin/main is bb5b21a88. My copy of the roles is current: the role diff against origin/main is empty.

## RESULT lines

RESULT head-measured 98fe31c26da80c46441a32bde66c2c3ef9ac5bc1
RESULT merge-tree origin/main: clean, rc=0, tree c0c787587394893d4cad18567a2f8d6b5973d59a (ev/merge-tree.txt)
RESULT ci-check-runs (commit check-runs API): every completed run is success, skipped or neutral (CodeQL). instrument-self-tests passed, with `pr_args self-test: 58 checks, 0 failed` and `cloud_relay self-test: 74 checks, 0 failed`. Analyze (python) was still in progress when I read them.
RESULT pr_args-self-test-head, cloud container, unmutated: 58 checks, 1 failed on 7 of 7 runs (4 run one after another, ev/base-seq*.out; 3 run at the same time, ev/base-par*.out). The failing arm every time is "update_pr: a SIGKILLed run keeps the lock until its push has ended; then the next run takes it".
RESULT pr_args-origin-main: 46 checks, 0 failed (ev/main-counts.txt), which matches the body
RESULT cloud_relay-head: 74/0. cloud_relay on origin/main: 69/0. Both match the body.
RESULT mainupd (origin/main's update_pr.sh under the head's harness): 58 checks, 5 failed, which matches the body's "5 failed"
RESULT removed-mechanisms: gone. The push is in the foreground (update_pr.sh:93). There is no killpg, stop handshake, parent-pid watch or zombie filter in update_pr.sh, and tools/pr/prepr.sh is not in the diff, so 7a2 is gone.

## Root cause of the failing arm (mine, reproduced)

- PID 1 in this container (`process_api`) reaps an orphaned child only after a delay. ev/zombie-lifetime.txt (z2.sh) shows a killed group's orphan staying `Z` for about 1.4 s.
- The holder's `group()` counts every process whose pgid is the run's, and `ps -A -o pgid=` lists zombies. So after a SIGKILL, the push stub's zombie keeps the group non-empty for one or two more 1 s polls.
- Measured with lat.sh, a replica of the holder: the lock frees 2.049 to 2.060 s after the push ends, on 8 of 8 trials (ev/lock-free-latency.txt).
- stoprun starts run 3 only 1.5 s after `ended`, so run 3 gets BUSY. ev/dbg.txt shows out3 as `update_pr: BUSY: the lock holder of run 16847, which has ended but started processes that have not`.
- Adding about 0.1 s of extra work before run 3 (one `ps` dump, ev/dbg2.txt) makes it pass. So this is a timing margin that depends on the host's init, not a logic error in the arm. On GitHub's runner the arm passes.
- The production effect:
  - Where init reaps late, the lock outlives the push by the reaping delay, which is harmless.
  - Where PID 1 never reaps (a container whose PID 1 does not wait on orphans), every run on that branch is BUSY for good after one SIGKILL.
  - Round 4 removed the zombie filter that dealt with this. The fix could restore it with an arm that pins it, which this container would provide, or keep the filter removed and widen the arm's wait by polling run 3 with a bound. That choice is the fixer's.

## Mutation proof (each mutant applied by me to the real source, the self-test run in its own worktree; ev/<name>.diff and .out)

These ran nine at a time, under load. The named arm fails in each:

| mutant | result |
|---|---|
| lock | BUSY arm FAIL |
| unlock | "the lock holder has exited by the time a run returns" FAIL |
| stop | TERM arm FAIL |
| drain | SIGKILL arm FAIL (and TERM) |
| pgrp | SIGKILL arm FAIL (and TERM) |
| holdgrp | SIGKILL arm FAIL only |

- shellfd (my own revert: the shell opens fd 9 and the holder flocks it) fails the "detached child" arm.
- oldfd (49577add's update_pr.sh, the body's revert) fails the "detached child" arm, as the body says.
- relay-body fails both body-path checks. relay-rm fails the "directory is removed" check. relay-75 fails "tried again", "not recorded failed" and "nor logged OWED". All three match the body.

Every mechanism the body claims has a mutant, and I found none without one. But in this container the SIGKILL arm fails unmutated, so the drain, pgrp and holdgrp mutants "failing" it shows nothing here.

Worse, the harness's own `mut:holdgrp` arm passes vacuously here: it checks that out3 is BUSY, and the unmutated head's out3 is also BUSY. In this container the holdgrp mutant cannot be told apart from the head. The drain and pgrp mutant arms, which check that out2 is not BUSY, still separate from the head.

During the parallel mutant runs, several unrelated arms also failed (for example the TERM main arm under mut:lock and mut:drain). That is consistent with a timing-sensitive harness under load.

## Other checks

- VERSION, the manifest version and the notes heading are not touched. No claim file, budget, closures.json or INERT entry is in the diff.
- The body's Head paragraph names 98fe31c2 and code c9dd299c, which matches what I measured.
- Forward-carry: the body says `none`. The `ps` dependency was carried by the orchestrator at roster 25e9cdee (on origin/handoff/audit-r10-roster) to R10-ROSTER-OPS, and that carry states its control (an arm with `ps` off PATH that requires a refusal).
- The rc-75 trigger is answered in the body: the round-0 pr-contract reds and their cheaper detector.
- A minor point, not blocking: under `set -e`, any command inside update_pr.sh that exits 75 also reads to the relay as BUSY and is retried forever, not recorded. Today only the lock path exits 75.
- I built my own instruments: run.sh, lat.sh, z2.sh and zomb.sh, all in ev/. There is no committed finder harness for this instrument fix beyond the PR's own self-test.
