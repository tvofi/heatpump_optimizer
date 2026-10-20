Fix review: blocked 2351c1c7bb6d71e455a7fd164f42f67091491d0f claim-false: the residual's Carry dismissal rests on a group kill, but daemonize.py's documented stop is kill <pid>, and a TERM of a daemonized update_pr.sh frees the branch lock at once while its push runs on in the worktree

bus-nonce: 7afa2927b864ae0cc10681c2c3af33cc

Round 2 (R10-UPDATE-PR-LOCK). Measured head 2351c1c7bb6d71e455a7fd164f42f67091491d0f = the PR's head at review time (pulls API) = the body's `## Head`. Contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty (merge base 52011c69a = origin/main tip).

## The blocking finding

The body routes the residual as `Carry: dismissed: daemonize.py runs every detached update as a session leader, so a kill of its group ends the push with it, and no incident involved a kill`. The first premise does not hold for the way a run is actually stopped:
- `tools/audit/seat/daemonize.py:52`: "`kill` by that pid is the stop story". INSTRUMENTS.md says the same: "the printed pid and `kill` are the stop story". `sweep_template.md:56` runs each `update_pr.sh` "detached under `tools/audit/seat/daemonize.py`". So the documented stop is a kill of the shell's pid alone, which is the residual's own case. A kill of the group is not the documented stop. HANDOVER item 43 records a healthy daemonized instrument read as dead and killed.
- The default `kill` is TERM, and it is worse than the body's SIGKILL case. The EXIT trap runs and kills the holder **at once**, not "within 2 s". The foreground `app_push.sh` → `prepr.sh` (update_pr.sh:83, cwd `$WT`) is not signalled and runs on.
- Probe (`ev/probe_term_kill.txt`). This is my own harness: update_pr.sh's lock lines at this head, extracted verbatim, followed by a foreground stand-in for the push, launched through the head's `daemonize.py`. After `kill <printed pid>`, the push stand-in is STILL RUNNING 0.5 s later, and the next run takes the lock at once with no BUSY. A real next run, which is the relay's every-tick handoff arm, would then reach update_pr.sh:60 `git worktree remove --force $WT` under that live push. That is this incident's own mechanism, so "not this incident's class" does not hold either.
- The second reason ("no incident involved a kill") is true, but alone it is not the stated basis.

Repair is the fixer's call. Possible repairs:
- Have a TERM or INT of the run end its children before the holder. For example, a TERM/INT trap that signals the run's own descendants, then exits, so the EXIT trap frees the lock last.
- Or route the residual to a real destination with a correct reason.

Whatever the repair, pin it with an arm. Today the holder's self-exit on parent death has no arm either: replacing `while os.getppid() == p` with `while True` gives `pr_args self-test: 51 checks, 0 failed` (`ev/mut_noparentexit.txt`). It is verified only by the body's offline repro, which I reproduced (below).

## What verified (RESULT)

- RESULT self-test head: `delivery_row self-test: 5 checks, 0 failed`, `pr_args self-test: 51 checks, 0 failed`, `cloud_relay self-test: 74 checks, 0 failed`. origin/main: 46 and 69. Matches the body.
- RESULT test-first, with the head's pr_args.sh:
  - round-0/1 update_pr.sh (d2d361a4): `FAIL update_pr: a child the run left detached does not hold the lock…`, 51 checks, 1 failed.
  - origin/main's: `FAIL … refuses BUSY (75) …` plus `FAIL mutant mut:unlock …`, 51 checks, 2 failed.
  - Both match the body's counts. The body quotes only the first line of main's two.
- RESULT harness mutants: `mut:lock` and `mut:unlock` killed, both `ok` at the head.
- RESULT own mutants on update_pr.sh:
  - BusyIO exit 3 instead of 75: 2 FAIL.
  - Drop `f.truncate(0)`: 2 FAIL (dead-run null and detached arm).
  - Parent-death loop → `while True`: **survives** (above).
- RESULT cloud_relay mutants, matching the body:
  - Base body line: 2 failed of 74, the same with `TMPDIR` unset.
  - Final `rm -rf "$bd"` deleted: 1 failed.
  - The `urc = 75` line deleted: 3 failed.
  - The per-run directory under `$TMPDIR` instead of the state dir: 0 failed. This is consistent with `shared_root`, which refuses only a file directly in a root.
- RESULT round-1 finding fixed:
  - The shell holds 0 fds on the lock file.
  - The holder's fd has O_CLOEXEC set (flags 02102001).
  - A post-checkout-hook detached child no longer holds the lock (arm `ok`).
- RESULT SIGKILL repro (body's):
  - `kill -9` the run, then a run 0.2 s later: rc=75, `BUSY: the lock holder of run N, which has ended (the holder exits within 2 s)`.
  - A run 2.5 s later takes the lock.
  - Reproduced.
- RESULT carry_audit, the prepr 7a2 command:
  - On the PR body: `1 routed, 0 unrouted`, rc 0.
  - The same body with the residual's `Carry:` removed: `UNROUTED body item … [lead]`, rc 1.
  - I did not run the full prepr.
- RESULT merge: `git merge-tree --write-tree origin/main 2351c1c7` rc 0, tree b62a9e00 = the head's own tree (the head already merges origin/main 52011c69a).
- RESULT CI at this head (check-runs API, 46 runs, `ev/check_runs.tsv`):
  - 29 success, 14 skipped, CodeQL neutral, none red.
  - `closures` and `Analyze (python)` were still in_progress at 02:16Z.
  - Both pr-contract runs: success, `record red-history`, `CARRY-AUDIT: 1 routed, 0 unrouted`.
- RESULT range reds (`ev/range_reds.txt`): pr-contract failed on d2d361a4 (118384716655, 118384845043), which the body names. It also failed on 02369b10 (118384376991, 118384517187), which the body does not list by id. Same cause: the logs show `UNROUTED … (## Forward-carry)`, so the body's pr-contract answer covers them. The cancelled runs there are cancel-superseded.
- Not touched: VERSION, manifest, RELEASE_NOTES, claim and golden files. No budget file in the diff.
- Not re-run by me: the body's relay-vs-manual probes in both orders. The 75 handling they rest on is pinned by the BUSY self-test arm and the cloud_relay retry arms, which I mutated above.
