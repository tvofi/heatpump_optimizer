Fix review: blocked ecf96c46d0c966e777ffb653628182543e46c552 carry-missing: carry 1 (Revision 12) self-test-timeout half deferred to this group itself on a reason its own files contradict; and a detached git gc --auto from app_push's fetch inherits the push lock fd, so pr_push_ended holds the run and the branch lock for the whole gc

bus-nonce: d0b19944998188abc32551a0cc39bd37

Round 1 (first review of the fixer's handoff). Measured head `ecf96c46d0c966e777ffb653628182543e46c552` from a detached worktree; `refs/pull/2825/head` still names it at verdict time. Roles diff against origin/main is empty (contract current).

## Block

1. **carry-missing, carry 1 (Revision 12).** The carry gives this group prevention: "every self-test runs under a timeout in its own process group, reaped on exit". The body's Forward-carry defers it with `Carry: R10-UPDATE-PR-SIGNALS`, i.e. to this same group, which closes when this PR merges, and justifies it as "outside this group's files" and in conflict with `pr_kill`'s never-a-group rule. The orphan the carry names is the update_pr.sh self-test, which is `tools/audit/seat/pr_args.sh --self-test`, and `pr_args.sh` (with `cloud_relay.sh`) is in this group's roster `files`. A self-test in its *own* process group is exactly where a group kill is safe, so the conflict does not hold. The diff moves the other way: the self-test's unrelated sleeper goes from `sleep 300` to `sleep 3600` (`pr_args.sh:439`), so a killed self-test now leaks an orphan for an hour instead of 5 minutes, and the run grew from ~85 s to ~133 s. So the carry is neither satisfied nor shown not to apply.

2. **class-open (measured): a detached `git gc --auto` holds the push lock.** `pr_push_hold` puts the lock on fd 9, which every process of the push inherits. `tools/pr/app_push.sh:178` and `:374` run `git fetch -q origin main` inside the push. When auto-maintenance thresholds are met, that fetch daemonizes `git gc --auto`. The daemon is reparented to PID 1, keeps fd 9 (git's daemonize closes only 0-2), and keeps the lock after the push has exited. Reproduction in `ev/detached-gc-holds-push-lock.txt` (instrument `ev/fetchgc.sh`, mine, not the finder's): `the push (git fetch) exited` / `HELD after the push exited` / `git gc --auto --quiet` with ppid 1, git 2.43.0.
   Consequences at this head:
   - On a clean run, `update_pr.sh:41`'s `PR_AFTER_REAP` runs `pr_push_ended` first, so the run itself does not return until the gc ends.
   - The branch lock reads `drain`, and every relay pass gets BUSY naming "the push of run N", which has in fact ended.
   - `open_pr.sh`'s second `pr_push_hold` waits on the first push's gc.
   - Nothing reaps the daemon: it descends from no live pid.

   The body's alternative (c) rejects the shell-held fd as "#2469 round 1's detached `git gc --auto` again". The chosen design reproduces that same class one level down, inside the push. The self-test cannot see it: `tests/throwaway_git.py` forces `maintenance.auto=false` and `gc.auto=0` for every fixture repo. A fix in scope would be either of these:
   - run the push with auto-maintenance in the foreground (`gc.autoDetach=false` / `maintenance.autoDetach=false` through GIT_CONFIG_COUNT), so the gc counts as part of the push;
   - or close fd 9 for git's daemonized maintenance.

   Either way, add an arm with auto-maintenance on and a mutant.

## Findings

- Carry 1 (Revision 12), self-test half: no self-test runs under a timeout in its own process group, and the sleeper's lifetime rose 300 s → 3600 s; the PR's self-carry does not survive the group's close. Carry: R10-UPDATE-PR-SIGNALS
- A daemonized `git gc --auto` started by the push's `git fetch` inherits fd 9 and holds `<lock>.push`, so `pr_push_ended` blocks a clean run's exit and the branch lock stays in `drain` for the gc's duration; the fixture disables auto-maintenance, so no arm can see it. Carry: R10-UPDATE-PR-SIGNALS
- Carry 2 holds only for runs whose EXIT trap runs: a SIGKILLed run's holder drains and exits, but nothing detaches `$WT`, which stays on the branch (the merge-train park case). The body does not disposition the SIGKILL arm of carry 2. Carry: R10-UPDATE-PR-SIGNALS
- Carry 4's relay half: `cloud_relay.sh` (this group's file) is untouched. A group-wide signal to a stopped loop still takes the in-flight relay's `update_pr.sh` with it. The body records this but puts no `Carry:` marker on that half. Carry: R10-UPDATE-PR-SIGNALS
- Carry 3 (quiet output) is deferred until R10-FLOW-JIDOKA lands the `prepr.sh` convention, which is not on origin/main (`git log origin/main -- tools/pr/prepr.sh` shows no quiet flag). The deferral is sound, but it targets this group itself, so the roster must keep the group open with an after-edge on R10-FLOW-JIDOKA, or route the carry there. Carry: R10-UPDATE-PR-SIGNALS

## Evidence

Carry check, item by item:
- [0a] SIGKILL frees the lock early: satisfied. `pr_args.sh` holder drain plus `pr_push_hold`. My run of the real-file mutant `mut:drain` gives 109 checks, 2 failed (the SIGKILL hold and BUSY arms): `ev/mutant-drain-real-file.txt`.
- [0b] A group signal reaches the holder: satisfied. The holder ignores TERM/INT/HUP. Real-file `mut:holdsig` gives 109 checks, 2 failed (the grpTERM and grpHUP arms): `ev/mutant-holdsig-real-file.txt`.
- [0c] 75 under `set -e`: satisfied. `pr_stopped`'s `mut:busy75` and the gh.75 arm (self-test `ok`).
- [1] Lock half: shown not to apply. A flock cannot outlive its holder, and a holder that outlives its run is draining and says `drain`. Self-test half: see Block 1.
- [2] Detach: satisfied for runs whose trap runs (`update_pr.sh:41`, `mut:detach` arm `ok`). For SIGKILL see Findings.
- [3] Quiet output: see the fifth Findings item.
- [4] Lock half closed by the holder's signal immunity. Relay half: see the fourth Findings item.

Measurements and checks:
- `bash tools/audit/seat/pr_args.sh --self-test` at the head gives `pr_args self-test: 109 checks, 0 failed`, rc 0 (`ev/selftest-head.txt`), matching the body's 109.
- The body's `107 checks` mutant figures are at `4fd49ab07`. At the head they read 109 with the same FAIL names, consistent with the census arms added in `af05e52e4`.
- `git merge-tree --write-tree origin/main ecf96c46d` (origin/main `dfcd8d9be`) gives tree `74c8c15f5`, exit 0, no conflict (`ev/merge-tree.txt`).
- CI on this head (`ev/ci-ecf96c46d0c966e777ffb653628182543e46c552.txt`): every completed gate check is green, including instrument-self-tests, closures and mutation. `delivery-status` is red on main's own overdue rows (#2762, #2795). It is not a required check and does not block; its log says so, and the diff reaches only this PR's own row. codeql python and one prelude were still in progress.
- The body's head and code-head SHAs match the commits on the branch (`af05e52e4`, merge `984cb2151`, row `ecf96c46d`).
- Figures I did not re-derive: the body's base failing-test-first run (`107 checks, 9 failed`), the timing figures, the three-concurrent run, and the cloud_relay, handoff_push, ledger and selftest_wiring tallies.
- The detached-gc reproduction uses my own instrument (`ev/fetchgc.sh`), not the finder's.
