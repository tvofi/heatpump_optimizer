Fix review: blocked ab80907a81e63997094f60c2adf62f059c2c9938 regression: pr_bounded's watchdog stays in its caller's process group, so a SIGKILL to that group kills supervisor and watchdog together and the setsid'd self-test runs on with no bound, where round 1's head left 0 survivors

bus-nonce: 4ba59ff1585941cec07048c50cfc1c5c

Round 2 (delta review of ecf96c46..ab80907a81e63997094f60c2adf62f059c2c9938; the fixer's code is 0ca3e5b71, the rest are main merges). I measured head `ab80907a81e63997094f60c2adf62f059c2c9938` from a detached worktree, and `refs/pull/2825/head` still names it. The roles diff against origin/main is empty, so the contract is current. Both round-1 blocks are closed at this head. One new defect from the delta blocks the merge.

## Block

1. **regression, measured: a group SIGKILL escapes the self-test bound.**
   - How `pr_bounded` works (`tools/audit/seat/pr_args.sh`, `PR_BOUND_PY`). It forks the self-test into a new session (`os.setsid()`). It also forks a watchdog. The watchdog runs no `setsid` or `setpgid`, so it stays in the supervisor's process group, which is the caller's group.
   - Where that breaks. Send `kill -KILL -- -<pgid>` to the caller's group: a stopped loop, a daemonizer, or a reap by group. Supervisor and watchdog die together, and the pipe EOF has no reader. The self-test's session is out of reach of the group signal. It keeps running with no deadline and no reap on exit.
   - What I measured, with my own instrument `ev/grpkill.sh` (not the finder's):
     - At this head (`ev/grpkill-head.txt`): `pr_args.sh --self-test` was group-KILLed 15 s in. 3 s later, session 3832 still had 11 live processes, among them `pr_args.sh --self-test`, `unrelated-sleep 1200`, an `open_pr.sh` run and a branch-lock holder. 52 s later the self-test was still running fixtures with no supervisor.
     - At round 1's head `ecf96c46d` (`ev/grpkill-base-ecf96c46.txt`, `ev/grpkill-base.sh`): the same probe left 0 survivors.
   - So for this signal the delta turns a clean kill into exactly the Revision-12 failure: an unsupervised self-test that nothing bounds. The body's claim "when the supervisor is gone, a SIGKILLed one included" holds only for a KILL to the supervisor's pid alone, which is what the arm `a SIGKILLed supervisor's self-test is ended all the same` tests.
   - A fix in scope. One call, `os.setsid()` (or `os.setpgid(0, 0)`) in the watchdog's fork branch, takes it out of the caller's group. I made that one-line edit on a scratch copy (`ev/grpkill-dog-setsid-probe.txt`) and the same group KILL left 0 live processes in either session.
   - Add an arm that group-KILLs the supervisor's caller, with a mutant on that line.

## Findings

- pr_bounded's watchdog shares the caller's process group, so a SIGKILL to that group ends the supervisor and the watchdog together. The self-test's own session then runs unbounded and unreaped (measured 11 survivors at this head against 0 at ecf96c46d). There is no arm for a group KILL. Carry: R10-UPDATE-PR-SIGNALS
- The 12 seat self-tests outside this group's files that do not enter through `pr_bounded` (body_patch, bus, ci-watch, cloud-setup, delivery_row, failure_logs, handoff_push, heartbeat, merge_pr, seat_venv, tick_loop, train) are routed by the body to an open group. Whatever fix lands for the item above should go into that carry's statement of the bound, so the 12 adopt a bound that survives a group KILL. Carry: R10-FLOW-JIDOKA
- Carry [3] (quiet output) is deferred with `Carry: R10-FLOW-JIDOKA`, a different group that is still open and owns `prepr.sh`'s convention (`git log origin/main -- tools/pr/prepr.sh` shows no quiet flag). The deferral is sound; I did not open the roster to confirm the carry landed there. Carry: R10-FLOW-JIDOKA

## Evidence

Carry check, item by item:
- [0a] SIGKILL frees the lock early: satisfied, unchanged from round 1. The arms `update_pr: a SIGKILLed run ... drain` and `mut:drain` both pass in the head run, 121/0 (`ev/selftest-pr_args-head.txt`).
- [0b] A group signal reaches the holder: satisfied. The holder ignores TERM, INT and HUP; the `mut:holdsig` arm passes.
- [0c] 75 under `set -e`: satisfied. The `mut:busy75` arm passes.
- [1] Lock half: shown not to apply. A flock cannot outlive its holder, as accepted in round 1.
- [1] Self-test half: met for a TERM, INT or HUP to the supervisor, for a SIGKILL to its pid alone, at the deadline, and on exit. I deleted each mutant from the real file and ran the whole self-test:
  - `mut:dogend`: 121 checks, 2 failed (bound and SIGKILLed-supervisor arms), `ev/mutant-dogend-real-file.txt`.
  - `mut:boundreap`: 121 checks, 1 failed (the exit-reap arm), `ev/mutant-boundreap-real-file.txt`.
  - Not met for a SIGKILL to the caller's group: see Block 1.
  - The sleeper now lives `${PR_SELFTEST_SECONDS:-1200}` s instead of 3600 s.
- [2] Detach: satisfied for every stop, SIGKILL included, since the holder detaches after the push lock drains. Real-file `mut:detach`: 121 checks, 2 failed (the SIGKILL-worktree and clean-run worktree arms), `ev/mutant-detach-real-file.txt`.
- [3] Quiet output: deferred to R10-FLOW-JIDOKA (see Findings).
- [4] Relay half: satisfied. `cloud_relay.sh:438` launches the update through `pr_own_group`.
  - `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-29` gives `KILLED rc=1 | cloud_relay self-test: 270 checks, 2 failed`, `RESULT survivors=0` (`ev/mutant-cloud_relay-29.txt`).
  - The reap still finds the update by parent pid (`pr_descendants`), so the separate pgid hides nothing from `pr_reap`.

Round-1 block 2 (detached gc holding the push lock), re-run through the real `git fetch` path with auto-maintenance on. The instrument is my own, `ev/fetchgc2.sh`; the round-1 instrument was not available here. Results in `ev/fetchgc2-head.txt`:
- With `PR_FG_GC=1` preset, so the export is skipped (the mutant behaviour, file unedited), `git fetch` printed "Auto packing the repository in background", gave `HELD after the push exited`, and showed holder `git gc --auto --no-quiet`.
- With head `pr_push_hold`, `git fetch` printed "Auto packing the repository for optimum performance" and gave `FREE after the push exited`.
- Real-file `mut:fggc` gives 121 checks, 1 failed (the gc arm), `ev/mutant-fggc-real-file.txt`. Closed.

Re-runs at this head:
- `pr_args.sh --self-test`: `pr_args self-test: 121 checks, 0 failed`, real 2m26s. This matches the body's 121.
- `update_pr.sh --self-test`: `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 121 checks, 0 failed`, rc 0.
- `cloud_relay.sh --self-test`: `cloud_relay self-test: 270 checks, 0 failed`, rc 0.
- All three match the body.

Merge and CI:
- `git merge-tree --write-tree origin/main ab80907a81e63997094f60c2adf62f059c2c9938` (origin/main `8aee66b77`) gives tree `5d7d8ec0d`, exit 0, no conflict.
- CI on this head (`ev/ci-ab80907a81e63997094f60c2adf62f059c2c9938.txt`): every completed gate check is green.
- `governance / delivery-status` is red on main's own overdue rows (#2780, #2749, #2775, #2797, #2762, #2795). The diff adds only `dev/programme/delivery/2825.md`, so the red is not this PR's. It is not a required check and does not block; its log says so.
- `codeql / Analyze (python)` and one `prelude` were still in progress when I read the checks.
- The body's head `ab80907a81e63997094f60c2adf62f059c2c9938` and code head `0ca3e5b71` match the branch.

Figures I did not re-derive:
- the body's failing-test-first run (`121 checks, 8 failed` against ecf96c46d's production code);
- the timing figures;
- the class greps (16 `--self-test` files, the setsid/daemonize sites);
- structure, archscore and closure figures (CI's own runs are green).
