# R10-RCA-ORCH-CONTINUITY: when the orchestrator's session or host stops, the programme stops silently

A root-cause seat (`dev/governance/roles/root-cause.md`, `dev/governance/rules/defect-root-cause.md`),
class `N-silent-stop`. Measured from GitHub alone (refs, merge history, the REST API, #201) at
`origin/main` `0cc148b2f` on 2026-10-21 between 09:00Z and 09:20Z; the orchestrator host's files
(`SEATS.md`, the tick log) are not readable from this seat and are cited from #201, never measured.
Kept apart from R10-RCA-HANDOFF-SLIP (the orphaned-handoff record, `N-orphaned-handoff`) and
R10-TICK-OWED-LEVEL (the tick's replay of historical `OWED` lines, the 4.5 MB board): both are
cited here and neither is redone.

## 1. The instances, re-verified

Each is a stop of the orchestrator's session or host that the next session found by a hand
survey. The GitHub footprint is what the stop left on origin; the takeover note is the #201
comment that recorded it.

| # | stop | takeover note | GitHub footprint |
|---|---|---|---|
| I1 | 2026-10-16 ~10:45Z, session killed, every seat with it | 6216882536, 13:46Z | no #201 comment 06:05Z-13:46Z; `pulse_replay.py` opener STOPPED 08:45Z-14:45Z (`r10-ref-privacy-scrub` waiting, nothing opened) |
| I2 | 2026-10-17, session 3 found "nothing was running (no train, tick, beat or sync loop)" at ~20:45Z | 6240942713, 20:57Z | main `8c6d940b0` 20:02Z unfollowed by the state ref for 51 min; earlier the same day state-beat STOPPED 11:15Z-15:15Z (main `fbd99a3d9` 10:28Z unfollowed 300 min) inside a #201 silence 02:23Z-15:29Z; counted once |
| I3 | 2026-10-20, session crash; instruments "crashed with the session" | 6285467757, 07:10Z | no main merge 06:06Z-07:39Z, no pull request opened 06:07Z-07:05Z |
| I4 | 2026-10-21, host reboot; train `b22-0724`, tick loop, state beat, `wt_sync` dead | 6310926491, 07:51Z | `review/2527` `blocked` at head `de28f656` from 00:00Z unrouted at the takeover (7.7 h); last pull request opened from a handoff 2026-10-20 23:44Z (#2531, `fix/r10-ci-ratchet-red`); after it only `record/autofix` (CI's) and dependabot; state commits follow main to 07:26Z, so the beat and train died with the reboot after 07:26Z |

Corrections to the brief, each from the footprint above:

- **2026-10-18 is not an instance of this cause.** The session was alive that day: 23 tvofi
  comments on #201 between 05:17Z and 23:20Z. The three missed cloud handoffs are a detector
  failing open while the session ran — R10-RCA-HANDOFF-SLIP measured 143 passes printing
  `bus.sh orphans unavailable (exit 1)`, 15:50Z Oct 18 to 06:06Z Oct 19 — which is
  `N-orphaned-handoff`'s. It shares the symptom (silence read as health), not the cause.
  It is not counted here.
- **I4's stop was two stops.** The reboot itself cost about 15 minutes (state commit 07:26Z,
  takeover ~07:40Z). The 8 h verdict and the ten unrecorded merges accrued before it, while
  the host ran: main merged #2516 at 02:20Z and #2511 at 05:16Z under a live train, and
  no session turn routed `review/2527` or opened a pull request after 23:44Z. A session that
  is alive but not taking turns stops the session-owned consumers exactly as a dead one does,
  and nothing distinguishes the two from outside.
- **The nine stranded handoffs (oldest 110 h) are mostly not I4's.** Under the opener rule in
  section 5 all nine predate the last opening at 23:44Z: they are the standing backlog the
  orphan record owns (R10-RCA-HANDOFF-SLIP), not input that arrived on a stopped opener.
- **I2 is an instance the brief did not list**, found by the class search (section 3).

Four instances in round 10 (I1-I4): an audit class by `defect-root-cause.md`'s per-round rule.

## 2. Named cause

**The programme's liveness is not a level anyone can read.** Every consumer the programme runs
is a process or a turn on one host: the merge train, the tick loop, `state_docs.py beat` and
`wt_sync.sh` are launched by hand through `daemonize.py`, which states "No daemon bookkeeping
is kept: the pid is printed and logged"; the opener (`open_pr.sh`), the verdict router and the
per-merge record are turns of the session (`sweep_template.md` steps 2, 4 and 6). What should
be running is held in the session's memory and a host file (`SEATS.md`), not on origin. The
only watchdog, sweep step 5's tick watcher, runs inside the session it would have to watch, and
reads one file (`tick_alive`) that describes one consumer. So when the session or its host
stops, every consumer and its only detector stop together, the output is silence, and silence
reads exactly like "nothing owed". Each recovery is a ritual from memory: I2, I3 and I4's
takeover notes each enumerate the dead loops by hand.

Which side moved: nothing regressed. `git log` shows no change that removed a supervisor; none
existed. R10-ORCH-MACHINERY's design (`dev/audit/design/orch-machinery/DESIGN.md` at
`09174d94`, unmerged, slip S5: "Six `daemonize` launches of one loop; each relaunch a human
act ... Should have caught it. A supervisor with a schedule. Why not. None exists.") reached
the same state from the inventory side.

## 3. Process state: (a)

No process existed to detect a stop of the session or the host. Evidence: the sweep's only
liveness step is step 5, which watches the tick seat from inside the session; `nudge.md`'s
"heartbeat" is the timer that fires a turn, not a check of one; `daemonize.py` keeps no record
of what it started; the tick (`orchestrator_tick.py`) runs on the same host. It is not (b):
no rule said to watch the session from outside and was skipped. It is not (c): step 5 was
followed on every sweep that ran, and its unit — the tick seat, read from inside the session —
cannot reach a stop of the session itself; a sweep that does not run produces no result to be
wrong. Not (d): the preconditions did not change underneath a sound check; the check never
covered this.

**Class search: what else the same cause reaches.** Any consumer whose only observer is on the
same host. Enumerated by the inventory of what the sweep and its daemons consume, each judged
against what it leaves on origin:

| consumer | owed input on origin | footprint on origin | disposition |
|---|---|---|---|
| opener | `handoff-body/<t>` | a pull request from `fix/<t>` | `pulse.py` opener arm |
| verdict router, train | `review/<N>` verdict at a head | merge, or the head moves | `pulse.py` verdict arm |
| state beat | a main move | a `handoff/audit-r<N>-plan` commit | `pulse.py` state-beat arm |
| per-merge #201 record | a merge on main | a #201 comment naming it | not covered: a turn, not an input an off-host producer writes; the reconciler of R10-ORCH-MACHINERY §6.4 |
| tick loop | none of its own | none on origin | not covered; its readers are on the host (R10-TICK-OWED-LEVEL owns the board) |
| `wt_sync.sh` | a local worktree change | `wip-sync/*` | not covered: its input is on the host by construction |

Replaying the three covered arms over 2026-10-15 00:00Z..10-21 08:00Z (609 samples, 15 min)
found the state beat silent while main moved in four windows on 2026-10-19 (11:15Z-11:45Z,
13:15Z, 15:00Z-16:45Z, 19:00Z-20:45Z) that no #201 comment mentions: the same cause reaching a
single daemon while the session ran. They are beyond the four instances and not counted.

## 4. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per day of round
10:

- **cost(defect)**, per occurrence: the owed work idle until the next session noticed, plus the
  survey. Idle: I1 3.0 h (10:45Z kill to 13:46Z note), I2 at least 4.0 h (the state-beat
  window alone), I3 about 1.0 h (06:06Z-07:05Z), I4 7.7 h (`review/2527`). Mean 3.9 h. Survey,
  takeover note to the first merge after it: I3 0.5 h (07:10Z-07:39Z), I4 1.2 h
  (07:40Z-08:41Z, #2519). About 4.8 h per occurrence.
- **P(recurrence)**: measured, 4 in 6.33 days (I1-I4 over 10-15T00Z..10-21T08Z), 0.63 per day.
  Product: **3.0 h per day**.
- **cost(countermeasure)**: one `pulse.py` run measured 7.7-8.2 s over three runs, of which
  `bus.sh orphans` is 4.8-6.4 s (three runs) — the call sweep step 2 already makes. On the
  host, one run per sweep is at most 39 min per day at a 5-minute sweep (288 x 8.2 s), 20 min
  at 10 minutes. Off the host, hourly: 24 x 8.2 s = 3.3 min per day of runner time and no
  session time.

Both forms pass: 39 min < 180 min per day on the host, 3.3 min < 180 min off it. Only the
off-host form shortens I1-I4's idle time; the on-host form removes the survey (0.9 h x 0.63 =
34 min per day, against 20-39 min) and catches a single dead daemon while the session runs
(the 2026-10-19 windows).

## 5. Countermeasure: `tools/audit/seat/pulse.py`

A consumer is judged by its owed input, never by a process: an input an off-host producer
already delivered to origin that the consumer's own footprint on origin has not answered within
a bound. Every input and footprint is a ref or a REST fact, so the verdict is the same from the
orchestrator's host, a cloud seat, or a runner where the host is not — which is what lets it
see a stop of the host. Three arms (rules in the instrument's docstring):

- **opener**: `bus.sh orphans` (invoked, never re-derived) lines aged >= 3 h **that arrived
  after the newest pull request opened from a `fix/` or `handoff/` head**. The second half is
  the replay's correction: the first cut fired on any aged orphan and read STOPPED in 123 of 153
  hourly samples, because standing orphans nobody clears (`r10-handover-1`,
  `r10-earlycutoff-coverage`, ...) never age out. A backlog older than the last opening is the
  orphan record's and is counted in the detail only.
- **verdict**: a `review/<N>` verdict whose pull request is still open at exactly that head,
  older than 2 h — a merge verdict nothing landed, or a blocked one nobody routed.
- **state-beat**: the oldest main first-parent commit newer than the state ref's last commit,
  older than 45 min. The oldest unfollowed move, not main's tip: with the tip, the 2026-10-19
  windows read ok because each new merge reset the age. 45 min is above every healthy latency
  measured (198 of 215 main moves since 10-15 18:08Z followed within 30 min, p90 19.2 min;
  the smallest of the other 17 is 49.2 min).

Fail closed: an input not read is `UNREADABLE`, exit 2, never ok (principle 3 of the design).
A stamp ahead of the clock is never aged (`fixer.md` step 16).

Stated limits: a programme with nothing owed reads ok however long it has been stopped (no cost
accrues there but time); a deliberate hold reads as owed — at 09:18Z it reported #2526's merge
verdict at `baa75f58`, 3.6 h, which the session is holding for a main merge (comment
6312035865); the per-merge record and the host-only consumers are not covered (section 3).

Wiring: the self-test runs in `governance.yml`'s `instrument-self-tests` job;
`selftest_wiring.py --check` read `UNWIRED tools/audit/seat/pulse.py` before the step and
`38 self-testing, 38 wired, 0 unwired` after. Sweep step 5 runs it after the tick watcher.
`INSTRUMENTS.md` lists it.

### Demonstration

- **Fails on the defect.** The I4 snapshot (self-test fixture, measured values) reads
  `verdict STOPPED ... #2527 blocked de28f656 7.7 h`, exit 1. The replay
  (`dev/audit/harnesses/pulse_replay.py --since 2026-10-15T00:00Z --until 2026-10-21T08:00Z`)
  reads opener STOPPED 08:45Z-14:45Z on 10-16 (I1) and state-beat STOPPED 11:15Z-15:15Z on
  10-17 (I2), plus the four 10-19 windows. I3 is not seen: at 15-minute samples nothing owed
  aged past a bound in its hour. The verdict arm is not replayable (`review/*` refs are
  overwritten).
- **Passes once fixed.** The same fixture after the takeover consumed it, and the healthy
  fixture, read ok on all three arms, exit 0.
- **Null control.** The replay with `--opener-h 1000 --state-min 100000` reads 0 windows on
  both arms, so the windows come from the bounds, not the harness. Live at 09:18Z, with
  `--verdict-h 100 --opener-h 1000` on the dumped snapshot: 0 stopped, exit 0.
- **Mutation.** Each predicate deleted in a copy, `--self-test` run (M0, an inert comment edit,
  is the null mutant: 0 failed): backlog test removed (4 checks fail); the
  consumed-verdict test reduced to presence (1 fails); the oldest-unfollowed rule replaced by
  the tip (1 fails); the state arm's unread inputs (the self-test raises, exit 1); the unread
  last opening (1 fails); the skew guard (1 fails); exit 2 for unreadable (1 fails).

## 6. The barrier owed, and the owner's call

With four instances this is an audit class that owes a class-eliminating barrier. `pulse.py`
is the detector — the command enumerates every covered seam — but the class is the stop being
*silent*, and only a run where the host is not, with a channel that reaches the owner, removes
that. Two forms, neither landable from this seat:

- **(A, recommended) a scheduled cloud probe**, hourly, at `origin/main`: `cloud_dispatch.py
  --role probe` with a brief that runs `pulse.py --dump` and, on exit 1 or 2, notifies the
  owner. Runner cost 3.3 min per day; no tree change; the trigger is account configuration the
  orchestrator or the owner creates.
- **(B) an hourly CI cron job** running `pulse.py`. It would make the class `barriered` in the
  register's sense, but it puts `pulse.py` and `bus.sh` on the required-check enforcement surface
  (`CODEOWNERS`, decision 0013's pinning) and its failure mail reaches only the cron line's last
  editor, so its alarm channel is unverified.

Until one runs, the register records the class `detector`, not `barriered`.

## 7. Root cause (for the defect's record)

- State: **(a)**, no process watched the session or host from outside it.
- Cost test: 3.0 h per day defect cost against 3.3 min per day off-host or 20-39 min per day
  on-host.
- Countermeasure: `tools/audit/seat/pulse.py` (detector), its self-test in CI, sweep step 5;
  the off-host schedule is the owner's call (section 6).
- This record: `dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md`.
