R10-UPDATE-PR-SIGNALS: a stopped `update_pr.sh` keeps its branch lock until its push ends, whatever stops it (TERM, INT, HUP, SIGKILL, to the run or to its whole group). This round adds the lock-age andon (carry 6, triage P163) and makes the self-test's lock-free waits wall-clock deadlines.

What changes at this head, by file:
- `tools/audit/seat/pr_args.sh`: the lock holder writes `<run pid> <holder pid> <start epoch>`, plus a fourth field `drain` once the run has ended. A run counts the lock as taken only on its own two pids with no `drain` mark. The lock wait and the self-test's `untilfree` are deadlines on `date +%s`: 20 s, 10 s for the `mut:drain`/`mut:pushhold` arms, and 5 s in `bndkill`/`bndgrp`. They no longer count ticks.
- `tools/audit/seat/cloud_relay.sh`: `stuck_arm` runs at the end of every `pass`. Any `upd-*.lock` that is held now, with a recorded start older than `HPO_PUSH_STUCK_SECS` (default 900), prints `cloud_relay: STUCK <branch> <pid> <age>s` and is written to `<log>.level` as `OWED <utc> push-stuck <branch> <pid> STUCK <branch> <pid> <age>s`, where the tick reads it. It only reports. The reap stays with `update_pr.sh`.
- `tools/audit/seat/ledger.py`: `push-stuck` is a derived kind, so the tick prints the line instead of refusing it.
- `dev/audit/harnesses/r10_seat_selftests_mutants.py`: mutants `cloud_relay-30`..`33`, `ledger-1` and `pr_args-1` added.

Carries, item by item:
- Carry 1 (#2469 split), SIGKILL: met. The holder drains on `<lock>.push`, which every process of the push holds through an inherited fd (arms `a SIGKILLed run's lock stays held while its push runs`, `mut:drain`, `mut:pushhold`).
- Carry 1, group signal: met. The holder ignores TERM, INT and HUP (`grpTERM`/`grpHUP` arms, `mut:holdsig`).
- Carry 1, exit 75 under `set -e`: met. Only the lock path says BUSY (`mut:busy75`, the `gh.75` arm).
- Carry 2 (Revision 12), lock half: does not apply. A flock cannot outlive its holder, and a holder that outlives its run says `drain` (null control `a lock left by a dead run ... does not block`).
- Carry 2, self-test half: met. Every self-test of this group runs under `pr_bounded`, a session of its own with a deadline and a watchdog outside the caller's group.
- Carry 3 (worktree left on the branch): met. The holder detaches `$WT` once the push has ended, for a SIGKILLed run too (`mut:detach`).
- Carry 4 (quiet output). Carry: R10-FLOW-JIDOKA
- Carry 5 (#2549 relay half): met. `handoff_arm` launches the update through `pr_own_group` (`cloud_relay-29`).
- Carry 6 (P163, STUCK andon): implemented here. Its controls are the four `stuck` arms of `cloud_relay.sh --self-test` and mutants `cloud_relay-30` (reads mtime), `-31` (no age bound), `-32` (no held test), `-33` (not wired into `pass`) and `pr_args-1` (no recorded start). `git grep -nE 'STUCK|HPO_PUSH_STUCK' HEAD -- tools/audit/seat` is non-empty.

## Head

Measured at `e115738fd662db360f97b901d624a3dd90fc65b7`, a merge of origin/main `7d2056970` into the round-4 head `5e83e3d8`, plus three commits. Figures were taken 2026-10-26T02:00Z–02:53Z (`date -u`), with origin/main at `7d2056970`.

## Mutation proof

Each mutant edits the committed file in place and runs that file's CI step, after the same step passed on the unmutated file: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-29 cloud_relay-30 cloud_relay-31 cloud_relay-32 cloud_relay-33 ledger-1 pr_args-1` gives `RESULT survivors=0`.
- `cloud_relay-30`: the age is read from the file's mtime. KILLED, 2 failed: `a held branch lock aged 901 s ... is STUCK` and `and it is push-stuck on the level`. Every fixture file is written at the moment of the pass, so its mtime ages it 0.
- `cloud_relay-31`: the age bound is deleted. KILLED, 1 failed: `a held lock aged 899 s is not reported`.
- `cloud_relay-32`: the held test is deleted. KILLED, 2 failed: the released-lock arm and `once every lock is released nothing is reported`.
- `cloud_relay-33`: `stuck_arm` is unwired from `pass`. KILLED.
- `cloud_relay-29`: still KILLED.
- `ledger-1` (`push-stuck` removed from KINDS): KILLED. The ledger self-test fails `every kind cloud_relay.sh writes is a ledger kind`.
- `pr_args-1` (the holder records `start = 0`): KILLED. The self-test fails `update_pr: the held lock records its holder's start epoch beside the pids`, 125 checks, 1 failed.

## Null control

On the unmutated head:
- `bash tools/audit/seat/cloud_relay.sh --self-test` gives `275 checks, 0 failed`.
- `bash tools/audit/seat/pr_args.sh --self-test` gives `125 checks, 0 failed`.
- `python3 -I tools/audit/seat/ledger.py --self-test` gives `56 checks, 0 failed`.

The 899 s fixture is the 901 s fixture's null control: it is held too and is not reported. The released 5000 s fixture is the held test's control. The new `BOUNDED=1 sigrun - KILL` arm is the 10 s bound's null control: an unmutated run goes through the same wall-clock wait (it lasted at least 10 s) and its lock still reads held.

## Figures

- The round-3 perturbation, six parallel `pr_args.sh --self-test` runs on 4 CPUs (`nproc` 4), driven by `for i in 1 2 3 4 5 6; do bash tools/audit/seat/pr_args.sh --self-test > run$i.txt 2>&1 & done; wait`, red counted by exit status (scratch driver sha1 `f3dc6a0e06be21cbd254de523abfce16cd1e7614`): 0 red of 6 runs at this head, each `125 checks, 0 failed`; 0 red of 6 runs at `5e83e3d8`, each `123 checks, 0 failed`.
- The round-2 finder's harness, `git show d75317e532e7b90104b409d33e8a0f5e7a03e1c5:ev/grpkill.sh` (sha1 `4f547e9ed3995f81f7ade7ad3ff880b07c534bc0`, from `probe/rev-2825-4ba59ff1`), `bash grpkill.sh tools/audit/seat/pr_args.sh 15`: 0 live processes in either session 3 s after the group KILL, at this head and at `5e83e3d8`. That harness's own perturbation (the head with `# mut:dogsid` deleted, 12 survivors) was measured in round 3 and not re-taken.
- Class seams for a tick count read as seconds. The rule: `git grep -nE '"\$\(lockstate [^)]*\)" = held \] && \[ \$k -lt' 5e83e3d8 -- tools/audit/seat/pr_args.sh`, plus `untilfree` and `pr_branch_lock`'s wait, which both claim seconds in their text. Disposition of each seam it returns:
  - `untilfree`: closed, now a deadline.
  - `pr_branch_lock`'s wait (its BUSY text says "20 s"): closed, now a deadline.
  - `bndkill`'s and `bndgrp`'s lock-free waits ("a bound below the child's 20 s sleep"): closed, now `untilfree "$t/bl" 5`.
  - `sigrun`'s wait for the drain mark or a free lock: already guarded. It ends on its condition, and an expiry fails the arm whichever way it goes.
  Every other `$k -lt` loop in the four files waits on a condition and claims no seconds. An expiry only fails its arm.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, wave-script or instrument red predicted against 7d2056970e08`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 1 script(s) run`, which is `tests/entities.py` (see Red checks).

## Red checks

- `governance / delivery-status` is red on main's own overdue rows. It is not a required context, and this diff touches only this PR's own row.
- `tests/entities.py` locally: `2 of 2445 ENTITY CHECKS FAILED` (`gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`). A detached checkout of origin/main `7d2056970` gives the same two failures in this container, so they are not this diff's. They are also the cause of `prepr.sh`'s one refusal, `closures: failed while being recorded: tests/entities.py (exit 1)`. CI's entities run on main is the detector of record, and none cheaper exists.
- This head has no CI run yet.

## Forward-carry

- The 12 seat self-tests outside this group's files that do not enter through `pr_bounded` (body_patch, bus, ci-watch, cloud-setup, delivery_row, failure_logs, handoff_push, heartbeat, merge_pr, seat_venv, tick_loop, train) adopt the bound, a bound that survives a group KILL. Carry: R10-FLOW-JIDOKA
- The startup window in `PR_BOUND_PY` before the watchdog's `setsid`. Carry: dismissed: a group KILL would have to land in the self-test's first millisecond; no realistic caller does that, and the fix costs a handshake pipe
- The group-KILL arm skips on a host without `/proc`. Carry: dismissed: every runner that runs this self-test has /proc; the skip is printed, not silent
- `stuck_arm` takes a lock with `LOCK_NB` for a moment, and only for a lock whose recorded age is already past the bound. A run that starts in that moment reads BUSY, exits 75 and is retried, as any BUSY is. Carry: dismissed: the only non-intrusive read is parsing /proc/locks by device and inode, which overlay filesystems report differently, for a window of one syscall once per relay pass
- The andon's 48 h trial, removed if it reports no STUCK line, is the trial clause P163 already states in `dev/programme/triage/s6-batch29.md`. Carry: dismissed: the triage entry is the record that clause lives in; nothing in it changes a later stage's brief

## Friction

none
