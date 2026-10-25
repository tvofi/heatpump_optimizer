Fix review: blocked e414c7eab5da7a478ee96627656ab490ad9f7554 nondeterministic-arm: the mut:drain and mut:pushhold mutant arms read the lock the instant the holder's mark says drain, but since round 2's detach the mutant holder frees it only after its git checkout, so the head's own self-test fails 4 of 6 runs under load where round 1's head failed 0 of 6

bus-nonce: 0caa7251ee0c171e6143d2d6b1410280

Round 3, a delta review of `ab80907a..e414c7eab5da7a478ee96627656ab490ad9f7554`. The fixer's code is `cfc707961`; the rest are main merges. Inside this PR's files the delta is exactly `cfc707961`, one file: `tools/audit/seat/pr_args.sh`, 40 lines added and 1 removed. I measured from a detached worktree at the head, and `refs/pull/2825/head` still named it when I wrote this (`ev/head-at-post.txt`). The roles diff (`merge-base...origin/main -- dev/governance/roles/`) is empty, so the contract is current.

Round 2's block is closed. I measured that with the round-2 finder's own harness, at both ends and under the perturbation. Both round-1 blocks are still closed. One defect blocks the merge. It was not in the delta. Round 2's detach brought it in, and round 2's review did not catch it. It breaks carry [0]'s rule that every arm must be deterministic across containers.

## Block

1. **nondeterministic-arm, measured: two mutant arms race the holder's exit, so the head's `pr_args.sh --self-test` goes red at random.**
   - The mechanism. `sigrun` (in `pr_args.sh`'s self-test) waits until the lock's mark reads `drain` or the lock is free. It then reads `lockstate` once.
     - With `mut:drain` deleted, the holder writes the `drain` mark. Since round 2 it then runs `git -C <worktree> checkout -q --detach` (the `mut:detach` line), because `update_pr.sh` passes `detach`. Only after that does it exit and free the flock.
     - So the arm's one read lands inside that window. It reads `held`, and the arm `mutant mut:drain (its line deleted): the holder lets go once the run is gone, while the push runs` fails on a correct tree.
     - `mut:pushhold`'s arm has the same shape and fails the same way.
   - What I measured, with my own diagnostic, which adds one line printing the arm's state files (`ev/diag/diag-print.diff`). Six head runs in parallel on 4 CPUs:
     - 4 of 6 were red (`ev/diag/diag-{1..6}.txt`).
     - Every red `mut:drain` read `treen=4 state=held mark=drain after=free`. So the wait ended on the mark, the read saw the lock still held, and the lock freed later.
     - One run also failed `mut:pushhold`, and one failed only `mut:pushhold`.
   - The other 8 runs of the head file, 4 run alone and 4 run four at a time:
     - 1 of 8 was red, `mut:drain`: `ev/mutant-dogsid-real-file.txt`, run alone, whose 2 failures are dogsid's expected one plus `mut:drain`.
     - The other 7 were green: `ev/selftest-pr_args-head.txt`, `ev/selftest-update_pr-head.txt`, `ev/mutant-dogsid-real-file-run2.txt` and `ev/rep-head-{1..4}.txt`.
   - The same six-way load at round 1's head `ecf96c46d`: 0 of 6 red, each run `109 checks, 0 failed` (`ev/diag/r1-*.txt`). There the holder exited right after the drain, with no checkout.
   - My isolated reproduction (`ev/race-isolated.sh`, the head's holder text with `mut:drain` removed, 40 trials each with and without detach, unloaded) read 0 `held`. The window is milliseconds and shows only under scheduler load, which is what a CI runner or a busy seat container supplies.
   - Why it blocks. This self-test is what CI and every seat run as the bound self-test. A flaky arm there turns a correct PR red on random runs. Carry [0] states the rule outright: "Every arm must be deterministic across containers: wait on a condition, never a fixed window." Here the wait condition (the mark) is not the condition the mutant arm asserts (the lock free).
   - A fix in scope.
     - For the two mutant arms, wait for the holder's own exit before reading. Its pid is the second field of the lock file, so poll `kill -0`, bounded below the stub push's duration, and only then read `lockstate`.
     - Or, for those two mutants only, wait until the lock is free under a bound shorter than the push. A free lock within that bound is the mutant's failure, and `held` at the bound is the pass.
     - Re-run six in parallel and expect 0 of 6 red.

## Findings

- `mut:drain` and `mut:pushhold` race the holder's post-drain detach, so `pr_args.sh --self-test` is red in 4 of 6 head runs under load and 1 of 8 otherwise, against 0 of 6 at `ecf96c46d` under the same load. This is Block 1. Carry: R10-UPDATE-PR-SIGNALS
- Startup window in `PR_BOUND_PY`. The self-test child is forked and `setsid`'d before the watchdog is forked and runs its own `os.setsid()`. A group SIGKILL landing between those two steps kills the supervisor and the not-yet-detached watchdog, and leaves the self-test unbounded. The window is one Python `fork()` plus one syscall, about a millisecond. A group KILL has to arrive within the first millisecond of a self-test's start. Forking the watchdog first, and having the child wait for it, would close the window, but that is more code than the exposure is worth. Carry: dismissed: a millisecond startup window that needs a group KILL timed to the self-test's first millisecond; no realistic caller does that, and a fix costs a handshake pipe
- The group-KILL arm reads sessions through `/proc` and prints a `skip` line (not a check) on a host without it, so `mut:dogsid` is unpinned on macOS. CI and the seat containers are Linux, where the arm runs. Carry: dismissed: every runner that runs this self-test has /proc; the skip is printed, not silent
- The body routes the 12 seat self-tests outside this group's files to R10-FLOW-JIDOKA. The routing text now says the bound must survive a group KILL, which is what round 2's second finding asked for. I did not open the roster to confirm the carry landed there. Carry: R10-FLOW-JIDOKA
- Carry [3] (quiet output) is still deferred to R10-FLOW-JIDOKA, which remains open and owns `prepr.sh`'s convention. Carry: R10-FLOW-JIDOKA

## Evidence

Round-2 block, measured with the round-2 finder's harness `ev/grpkill.sh`. It is copied verbatim from `probe/rev-2825-4ba59ff1`; the only change moves its scratch ps file under `$W`. It group-KILLs the caller of `pr_args.sh --self-test` 15 s in and counts each session 3 s later:
- RESULT at the head (`ev/grpkill-head.txt`): before the kill the caller's group held 1 process, since the watchdog has left it. Sessions 811 and 812 held 0 live processes after the kill, and 53 s later no `pr_args.sh --self-test` and no `unrelated-sleep` was alive.
- RESULT at round 2's head `ab80907a` (`ev/grpkill-base-ab80907a.txt`): the group held 2 processes. Session 2893 held 12 live processes after the kill, among them the self-test, `unrelated-sleep 1200`, an `open_pr.sh reap` run and the branch-lock holder. Round 2 measured 11, the same failure.
- RESULT under the perturbation, the head with its `# mut:dogsid` line deleted (`ev/mutant-dogsid.diff`, `ev/grpkill-head-mut-dogsid.txt`): 12 live survivors. The harness moves under its own perturbation, and the one line the PR adds is what closes the block. I killed the survivors of both runs by hand afterwards.
- Real-file mutation proof, with `mut:dogsid` deleted and the whole self-test run (`ev/mutant-dogsid-real-file-run2.txt`): `pr_args self-test: 123 checks, 1 failed`, rc 1. The one failure is `pr_bounded: a SIGKILL to its caller's whole group still ends the self-test, 0 survivors in either session`. That matches the body. The first such run (`ev/mutant-dogsid-real-file.txt`) failed 2: the same arm plus the Block 1 flake.

Round-1 blocks stay closed:
- Delta inside this PR's files: only `cfc707961`'s watchdog line, its comment and the new arm. Nothing touches `pr_push_hold`, the gc export or the holder.
- The arms `update_pr: the push's git gc --auto runs in the foreground ...` and `update_pr: a SIGKILLed run's lock stays held while its push runs` pass in every head run.

Carry check, item by item (the base list):
- [0a] SIGKILL frees the lock early: satisfied. The arm `a SIGKILLed run's lock stays held while its push runs` passes in every head run I made (14).
- [0a] The determinism clause: not met. The arms are `mut:drain` and `mut:pushhold`; see Block 1.
- [0b] A group signal reaches the holder: satisfied. The grpTERM and grpHUP arms and `mut:holdsig` pass.
- [0c] 75 under `set -e`: satisfied. `mut:busy75` passes.
- [1] Lock half: shown not to apply, as accepted in round 1.
- [1] Self-test half: met now for a SIGKILL to the caller's group as well. See the grpkill RESULTs above and the new arm with its `mut:dogsid` mutant.
- [2] Detach: satisfied. `mut:detach` passes. It is the detach line that widened the Block 1 window, and the line itself is sound; the defect is in the arms that read around it.
- [3] Quiet output: deferred to R10-FLOW-JIDOKA (see Findings).
- [4] Relay half: satisfied, unchanged since round 2. `cloud_relay.sh --self-test`: `270 checks, 0 failed`, and both group arms pass (`ev/selftest-cloud_relay-head.txt`).

Re-runs at the head, against the body's figures:
- `pr_args.sh --self-test`: `123 checks, 0 failed`, rc 0, real 173 s. The body says 2m44s. Matches, in the runs that did not hit Block 1.
- `update_pr.sh --self-test`: `delivery_row self-test: 6 checks, 0 failed`, `pr_args self-test: 123 checks, 0 failed`, rc 0. Matches.
- `cloud_relay.sh --self-test`: `270 checks, 0 failed`, rc 0. Matches.

Merge and head:
- `git merge-tree --write-tree origin/main e414c7eab5da7a478ee96627656ab490ad9f7554`, with origin/main at `f3ffb1c63`: tree `f024624a3`, exit 0, no conflict (`ev/merge-tree.txt`).
- The body's head and code head match the branch, and its `Head` section describes the orchestrator's main merge.

CI on this head (`ev/ci-e414c7eab5da7a478ee96627656ab490ad9f7554.txt`, read about 22:00Z):
- Every completed gate check is green.
- `governance / delivery-status` is red on main's own overdue rows, as in round 2. The diff adds only its own delivery row, so the red is not this PR's. It is not a required check and does not block.
- `tests / closures`, `governance / instrument-self-tests`, `codeql / Analyze (python)` and one `prelude` were still in progress.
- Whether `instrument-self-tests` meets the Block 1 race, I did not wait to see.
- The body's `## Red checks` was written before CI ran on this head.

Figures I did not re-derive: the timing figures beyond my own runs, the class greps, and the structure, archscore, closure and `ci_predict` rows. CI's own runs of those are green or still pending.

Instruments: `ev/grpkill.sh` is the round-2 finder's. `ev/race-isolated.sh` and `ev/diag/diag-print.diff` are my own, built for this review.
