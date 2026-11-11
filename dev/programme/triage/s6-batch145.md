# Proposal triage, session s14, batch 145 (P552 to P553)

This batch rules `s7/triage-queue-s7.txt` lines 236 and 237, which arrived after batch 144. The bar
and the denominators are batch 141's.

Sources: the roster at `origin/handoff/audit-r10-roster` `955fe985ea` and origin/main
`d08ed31049`.

## P552: S14-TICK-STALE-SILENT

Verdict: ACCEPT, narrowed, on the class-barrier route. The same cause stopped the relay three
times.

Source: queue line 236 (2026-11-11T00:43:16Z, an orchestrator slip).

Instances:
- **The mechanism.** `tick_loop.sh` `fresh_check` restarts itself only from a detached head.
  - On a branch-backed checkout it prints `TICK-STALE ... a branch is checked out, not a detached
    head`, sets `relay=stale`, and skips the relay and sweep arms on every pass.
  - Only the loop log and the heartbeat message carry the stale state. The board (`<out>`, from
    `orchestrator_tick.py`) does not.
- **The episodes.** `grep '^TICK-STALE' tick-loop.log`, grouped by code and cause, gives four.
  Three are the branch cause:
  - `d4e584e`: 9 passes, 2026-11-04 20:16-22:12Z;
  - `8bf45e5`: 17 passes, 2026-11-05 18:38-20:40Z;
  - `45adb0c`: 1 pass at 2026-11-11T00:37:41Z, until the loop was relaunched at 00:43:16Z.

  The relay was dark for about 4 h in all. The fourth, `82a2c14`, "a relay is in flight", lasted
  one pass and cleared itself.
- **The contradiction.** `worktree_gc.sh` removes a clean old detached worktree unless a process
  stands in it (its instrument page), so the tools-checkout rotation goes branch-backed. That
  defeats `fresh_check`'s restart.

Cost:
- **(1) The cause.** `fresh_check` also restarts from a branch-backed checkout that is clean and
  holds no commit outside origin/main (`git rev-list origin/main..HEAD` is empty). It does so by
  `git checkout -q -B <its branch> origin/main`. A branch holding its own commits still refuses,
  with a new why.
- **(2) The detection.** When the stale state persists into a second consecutive pass, the board
  gains one line in the board's existing `-> OWED` form: relay-skipped, with the why, code and
  behind. The one-pass, lock-held episode never raises it.
- **Dropped: the liveness-hook arm.** P550 already judges the relay live by its log's age, and a
  skipped relay leaves that log stale.

Self-test:
- a clean branch-backed checkout behind origin/main restarts;
- a branch with an unpushed commit stays stale, with the new why;
- two stale passes write the OWED line, and the null control, one stale pass, writes none;
- a mutant on each.

Binding: one carry, R10-TICK-RESIDUE, which owns the board. The orchestrator adds
`tools/audit/seat/tick_loop.sh` to its files; no live group lists it. Carry file:
`b145-P552.txt`.

## P553: S14-TRAIN-SUPERSEDED-DEFERRAL

Verdict: ACCEPT, narrowed. It repairs an observed wrong behaviour: a green PR sat skipped for about
13 h.

Source: queue line 237 (2026-11-11T00:47:25Z, the merge seat and the diagnosis seat on PR 3383).

Instances:
- **The mechanism.** `merge_train.py` `latest_runs` keeps the latest gate of every check suite, and
  the worst stands (A5). `_gate_busy` excuses a red gate only while a ci.yml run at the head is
  unfinished.
  - An edit run's gate fails deferring: gate.py `deferral`, "run(s) [N] at this head are still
    being judged; their gate decides".
  - Once run N concludes success, the deferring suite's red still stands, and nothing re-runs it.
- **The deferral is invisible to the API.** gate.py prints it to the job log and the step summary
  only. The live gate check-runs at PRs 3385 and 3386 carry no output title or summary.
  - So classify cannot read the cited ids without fetching logs.
- **The reported case.** The train log has `SKIP #3383 ci: #3383 red at its head: gate` in batch
  20261110-115043. The gate check-runs at PR 3383's head `1281f5c139` now show the three older
  suites re-run green at 2026-11-11T00:47:27-29Z: the hand re-run.
  - PR 3374's head shows the same signature: five suites green within 00:37:02-34Z. That is
    unconfirmed as a deferral.
- **The census.** Over the train logs, 18 `red at its head: gate` SKIPs hit 10 PRs. Only PR 3383 is
  confirmed as this class.
- **The tie.** `failure_logs.sh` sorts by `started_at` alone (line 130), so a tie can name a
  superseded red as the latest.

Cost:
- **(1) The re-run.** When the gate's only red is an older suite and a later gate suite at the
  same head is green, the train re-runs that suite's failed jobs (`gh run rerun --failed`) once per
  suite per head, recorded in its state, and reads WAIT.
  - The re-run judges again: a stale deferral turns green, and a real red re-fails and stands.
  - This keeps A5 whole and needs no log read.
- **(2) The tie-break.** `failure_logs.sh` sorts by `started_at` and then `completed_at`.

Rejected: classifying from the deferral text. It is absent from the check-run API, and reading
every red gate's log costs more than one gate-job re-run.

Self-test:
- three deferred suites behind a green suite re-run once each, then read green;
- the null control, a newest suite that is red, re-runs nothing;
- a re-run that re-fails stands red, with no second re-run;
- a started_at tie picks the later completed_at;
- a mutant on the once-bound, and a mutant on the tie.

Binding: one carry, R10-TRAIN-RESIDUE (`merge_train.py`). The orchestrator adds
`tools/audit/seat/failure_logs.sh` to its files. Carry file: `b145-P553.txt`.
