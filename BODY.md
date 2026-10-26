A TERM, INT, HUP or SIGKILL of a running `update_pr.sh`, sent to the run alone or to its whole process group, no longer frees the branch lock while the run's push still runs. Seat self-tests run bounded, in a session of their own (`pr_bounded`). A push's git auto-maintenance runs in the foreground. The lock's holder detaches the worktree after the drain. `cloud_relay.sh` starts the update in a process group of its own. This round changes one thing: in the self-test, the `mut:drain` and `mut:pushhold` arms now wait for the lock to be free, bounded at 10 s, a third of the stub push's 30 s, before they read it (`sigrun`, `tools/audit/seat/pr_args.sh`). Before, they read it once at the holder's `drain` mark, which raced the holder's post-drain detach.

Part of #2502.

## Head

`37bd048581a03d7001cc52f4805b018c8b896ac9`. It contains the PR head `e414c7eab5da7a478ee96627656ab490ad9f7554` and origin/main `5261ba84139d9459465ccd842b61b04c2b1329d8`, merged. Every figure below was taken at this head, with origin/main at `5261ba841`, on 2026-10-26 between 00:20Z and 00:58Z (`date -u`), on a 4-CPU container.

## Mutation proof

The perturbation is this head with the new wait line (`case $1 in drain | pushhold) untilfree "$lf" 200 ;; esac`) deleted. With that deletion, 6 parallel runs of `pr_args.sh --self-test` were red as follows:
- 1 of 6 red at plain 6-way load: `FAIL   mutant mut:drain (its line deleted): the holder lets go once the run is gone, while the push runs`.
- 0 of 6 red in a second 6-way batch.
- 1 of 6 red with 4 extra CPU burners: `FAIL   mutant mut:pushhold (its line deleted): the push holds no lock, so the holder lets go while it runs`.

That is 2 red of 18, on the two arms the review named.

Every `# mut:` arm of the self-test passes in every head run below, `mut:dogsid` among them, whose arm is `pr_bounded: a SIGKILL to its caller's whole group still ends the self-test, 0 survivors in either session`.

## Null control

- The same 6-way run at round 1's head `ecf96c46d`, where the holder exits right after the drain: 0 of 6 red, each `pr_args self-test: 109 checks, 0 failed`.
- Head: 0 red of 18. That is 6 at 6-way load, 6 more at 6-way load, and 6 at 6-way load plus 4 CPU burners, each `pr_args self-test: 123 checks, 0 failed`.
- The round-2 finder's harness `grpkill.sh` (`probe/rev-2825-4ba59ff1`; the one change puts its ps file under `$W`) was run with `pr_args.sh 15`, unloaded:
  - at the head, the sessions held 0 and 0 live processes 3 s after the group KILL;
  - at round 2's head `ab80907a`, the self-test's session held 12. I killed those 12 by hand afterwards.

## Figures

| command | result |
|---|---|
| `bash tools/audit/seat/pr_args.sh --self-test` (alone) | `pr_args self-test: 123 checks, 0 failed`, rc 0, real 171 s |
| `bash tools/audit/seat/update_pr.sh --self-test` (alone) | `pr_args self-test: 123 checks, 0 failed`, rc 0, real 170 s |
| `bash tools/audit/seat/cloud_relay.sh --self-test` (alone) | `cloud_relay self-test: 270 checks, 0 failed`, rc 0, real 55 s |
| six parallel `pr_args.sh --self-test` (the head, the head again, then the head with 4 burners) | 0 of 6, 0 of 6 and 0 of 6 red; wall 184 s, 198 s and 231 s |
| the same six at `ecf96c46d` | 0 of 6 red, wall 157 s |
| the same six, with the wait line deleted (plain load, plain load again, then with 4 burners) | 1 of 6, 0 of 6 and 1 of 6 red |
| `git merge-tree --write-tree origin/main HEAD` | exit 0, tree `0d4de5f29` |
| `PYTHONPATH=tests/hastub python3 tests/structure.py` | `STRUCTURE RATCHET PASSED` |
| `python3 tools/audit/archscore/score.py --diff 5261ba841 HEAD` | `Architecture score: dS +0.0000 NULL` |
| `python3 tests/closure.py select --diff 5261ba841` | `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` |
| `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` | `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 5261ba84139d` |

### Carries, item by item

- [0] #2469's round-4 split:
  - SIGKILL frees the lock early: met. Arm `update_pr: a SIGKILLed run's lock stays held while its push runs`, with `mut:drain` and `mut:pushhold`.
  - Determinism: met. Both mutant arms now wait on the lock free under a bound, and the head was 0 red of 18 under load.
  - A group signal reaches the holder: met. The grpTERM and grpHUP arms, with `mut:holdsig`.
  - 75 under `set -e`: met (`mut:busy75`).
- [1] Revision 12:
  - Lock half: does not apply. A flock cannot outlive its holder; arm `a lock left by a dead run (the kernel freed it) does not block`.
  - Self-test half: met by `pr_bounded` in `pr_args.sh`, `update_pr.sh` and `cloud_relay.sh`, with `mut:dogend`, `mut:boundreap` and `mut:dogsid`, and the grpkill figure above.
- [2] The worktree left on the branch: met by the holder's detach (`mut:detach`).
- [3] Quiet output: not built here. Routed under Forward-carry.
- [4] #2549's relay half: met. `pr_own_group` in `cloud_relay.sh`, its two group arms, and harness mutant `cloud_relay-29`.
- [5] Lock-age andon (triage P163): not built. It was appended to the roster at 2026-10-25T22:52Z, after round 3's handoff, and this round's brief limits the code to the race fix. `git grep -n HPO_PUSH_STUCK -- tools/audit/seat` is empty at this head. The orchestrator decides where it goes.

## Red checks

- `governance / delivery-status`: red at `e414c7ea` on main's own overdue delivery rows, which this diff does not touch; it adds only `dev/programme/delivery/2825.md`. It is not a required context. Cheaper detector: none; the check reads main's rows as a whole.
- Nothing else was red at `e414c7ea`. This head has no CI run yet.

## Forward-carry

- Quiet output (roster carry [3]) for `update_pr.sh`, `open_pr.sh` and `merge_train.py`'s per-car progress follows `prepr.sh`'s convention, which that group owns. Carry: R10-FLOW-JIDOKA (item 2aabed9d)
- The 12 seat self-tests outside this group's files (`body_patch.sh`, `bus.sh`, `ci-watch.sh`, `cloud-setup.sh`, `delivery_row.sh`, `failure_logs.sh`, `handoff_push.sh`, `heartbeat.sh`, `merge_pr.sh`, `seat_venv.sh`, `tick_loop.sh`, `train.sh`) do not run under `pr_bounded`. A bound adopted for them must survive a group KILL. Carry: R10-FLOW-JIDOKA
- `PR_BOUND_PY`'s startup window, between the child's `setsid` and the watchdog's. Carry: dismissed: a millisecond startup window that needs a group KILL timed to the self-test's first millisecond; no realistic caller does that, and a fix costs a handshake pipe
- The group-KILL arm prints `skip` on a host without `/proc`, so `mut:dogsid` is unpinned on macOS. Carry: dismissed: every runner that runs this self-test has /proc; the skip is printed, not silent

## Friction

none
