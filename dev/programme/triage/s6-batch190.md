# Proposal triage, session s14, batch 190 (P612)

The bar and the denominators are batch 141's.

Sources:
- origin/main `ee64358be7`.
- The beatd journal (`beatd/journal.log`), and the events file the local arm writes (`s9/events.txt`).
- The orchestrator's local `s14/beat_extras.sh` (`:42-63`) and its sweep record (`s14/sweep.md`).
- The live `beatd.py status` and the daemon's argv, read at 11:48Z.
- The roster at `origin/handoff/audit-r10-roster`.

## P612: BEAT-FRESHNESS-ARM

Verdict: ACCEPT narrowed. The local arm is fixed in place, as an orchestrator-local change with no roster
group: it waits for an idle instant instead of skipping, and it relaunches with the daemon's own argv. The
P581 carry is not pulled forward.

Source: queue line 290, 2026-11-11T11:45:10Z, orchestrator s14.

Measurements:
- **The arm never fired today.** The extras loop has been alive since 00:06Z (pid 78497). It wrote 11
  `PLAN MOVED` lines today. It wrote no `BEAT-RESTARTED` and no `BEAT-RESTART refused` line after
  2026-11-10T12:55:53Z.
  - In the same window the checkout went stale 5 times, and each was rotated by hand: 02:04Z, 04:00Z,
    06:12Z, 08:18Z and 11:45Z.
  - If the arm worked, at least some of those 5 would be `BEAT-RESTARTED` lines.
- **Why it never fires.** The guard restarts only when `beatd.py status` shows zero ` running ` jobs at
  the moment of the check. A job busy at the check silently defers it to the next loop, 900 s later.
  - The check was simulated at the loop's 15-min instants (offsets 0, 300 and 600 s) against today's
    journal pass intervals (00:06Z to 11:45Z). 71-76% of the checks land on a running job.
  - On 30 s samples, a job is running 67.3% of the time. `pulse` alone is running 59% of the time, at a
    median pass of 165 s and up to its 240 s timeout, about every 5 min. `roster-drain` is running 30% of
    the time.
  - Live status at 11:48Z showed 2 running jobs on 3 of 3 reads.
- **Idle windows exist, but they are short.** There were 108 idle runs of 60 s or more in 11.6 h, about
  9.3 an hour. A guard that polls for up to 15 min almost always meets one. A guard that samples one
  instant every 15 min mostly does not.
- **The relaunch drops `--jobs`.** The running daemon's argv carries `--jobs <the local table>`. The
  arm's relaunch (`beat_extras.sh`, the `daemonize.py ... beatd.py run --state --repo` line) passes no
  `--jobs`. A restart by the arm would therefore come back with the default job table.
- **The P581 carry cannot run soon.** R10-SEAT-IDENTITY-P5 is `not-started`, `after: R10-TICK-RESIDUE`,
  and it holds 6 carries. No `*seat-identity-p5*` ref exists, so no fixer is live.
  - It shares `beat_jobs.py` with R10-TICK-RESIDUE, which is still open.
  - Pulling it forward means re-cutting the order behind an open group that shares a file. The local
    fix closes the gap the same turn, at no repository cost.

Disposition:
- **ACCEPT narrowed (local, the orchestrator's to apply).** In `beat_extras.sh` arm (d):
  - When the checkout is stale, poll `beatd.py status` every 10 s for up to 900 s, and restart at the
    first read with zero ` running ` jobs.
  - When no idle read arrives, write one `BEAT-RESTART deferred: busy <n> reads` line to the events file.
    The silent skip goes.
  - Relaunch with the daemon's current argv, `--jobs` included: read it from the running pid before the
    TERM, or from the launch file.
- This needs no roster entry: it is not a repository change.
- **P581 stays where it is**, as the durable fix, on R10-SEAT-IDENTITY-P5. Not pulled forward.
- Re-open trigger: this returns as a queue line if a manual rotation is still needed after the local
  fix, or if a `BEAT-RESTART deferred` line appears twice in one day.
