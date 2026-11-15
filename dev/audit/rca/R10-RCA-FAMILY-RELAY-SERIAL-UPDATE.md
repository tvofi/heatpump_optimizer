# R10-RCA-FAMILY-RELAY-SERIAL-UPDATE: returned verdicts wait behind one pull request's update

Round-end family analysis (loop card L8) of the family `relay-serial-update` and proposal
PC-1113-03. Its countermeasure is already ruled (tvofi's card P12, R11-PRE-RELAY-REBUILD); this
record names the cause and states what the build must cover. Measured at `origin/main`
`a39627da59` on 2026-11-15. Lands no code.

## 1. Instances

From intake carry 87 and the sweep log:
1. 2026-11-11 13:21-14:18Z: five merge verdicts held behind one `update_pr.sh` of #3462 (intake
   carry 4).
2. 2026-11-12T11:27Z: 36 min.
3. 2026-11-13T08:49Z: 57 min, the pass inside `update_pr.sh` for #3531 (sweep line 1522).
4. 2026-11-13 16:20-17:56Z: 1 h 34 min.
5. 2026-11-13T18:00Z on: over 70 min inside #3451's update, whose handoff conflicted with main;
   #3557, the fix for a red main, waited from 18:25Z to 19:09Z (line 1830).
6. 2026-11-14T16:10Z on: 48 min inside a full pre-PR check for non-gating #3560 (line 2347).
7. 2026-11-14T23:10Z on: inside #3491's update (line 2521).

Seven. The fifth held a required-red fix of main.

## 2. Named cause

`cloud_relay.sh`'s pass runs its arms in one serial loop, and its handoff arm calls
`update_pr.sh` per pull request, which runs the full pre-PR check (35-94 min in the instances);
every arm after it, and the next pass, wait. #3465 moved the probe and confirm arms before the
handoff arm (intake carry 4), which covers verdicts present at a pass's start and not those
returning during it. A conflicting update is retried every pass.

## 3. Process state: (c)

The relay ran as designed every pass; the design couples an unbounded step to a latency-bound
one.

## 4. Class reach

The opener and the tick's own pass have the same coupling (sweep line 1751: new handoffs reached
the board only as the tick's line while the pass stood in an update). The pre-PR check's own wall
(R10-RCA-OPEN-PREPR-SLOW: step 6d measured 1561 s on a 4-CPU container against 40 s scoped) is
the multiplier.

## 5. Cost test

- cost(defect): 36 min to over 90 min of verdict latency per instance, on any pull request.
- P(recurrence): seven in four days.
- cost(countermeasure, recurring): none standing; posting is moved out of the serial loop.

Passes; tvofi ruled it (P12).

## 6. Countermeasure

R11-PRE-RELAY-REBUILD (triage `dev/programme/triage/r10-round-end.md#P750`), with these
acceptance conditions drawn from the instances: a verdict returning during an update posts
within one probe interval; a conflicting update is owed to a fixer, not retried; a pass inside
one update past a bound prints a digest line; a retired worktree holding the branch does not
make the pass BUSY (P760). The local prototype (a second detached relay in watch mode) retires
with it. The pre-PR wall (OPEN-PREPR-SLOW C1-C4) is deferred until the rebuild lands and is
re-measured (intake carries 6-9).
