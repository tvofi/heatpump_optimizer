# Proposal triage, session s14, batch 207 (P638)

Sources:
- The live merge-train log, `~/.local/state/hpo/merge_train/train.log`, and the train's skip list,
  `~/.local/state/hpo/merge_train/skipped.json`, read 2026-11-11T15:26Z.
- `tools/audit/seat/merge_train.py` at origin/main: `rejoin_candidate` and `rejoin` (:3710-3760),
  and `platform_gate` (:480).
- Roster `handoff/audit-r10-roster` at its tip, 2026-11-11T15:28Z.

## P638: re-admit a skipped green entry (TIMEOUT, A5, CARRY) without ending the train

Verdict: DEFER.

Source: triage queue line 315, 2026-11-11T15:24:16Z, PROPOSAL (orchestrator s14) a green PR the
live train skipped cannot land until the whole train ends.

Instances:
- The train's current skips (`jq '.[]' skipped.json`):
  - #3438: TIMEOUT.
  - #3445: TIMEOUT, then parked (BLOCKED: a review missing after the recarry).
  - #3449: A5. The train reads its gate green, and GitHub's required-check evaluation reads
    "unread (more than 100 contexts: not read whole)".
  - #3454, #3451 and #3458: real gate reds, which are out of scope.
- How long those three have waited (`gh pr view N --json reviews`, first approval to 15:26Z, all
  three still open):
  - #3445: approved 08:20:56Z, open 7.1 h.
  - #3438: approved 08:58:46Z, open 6.5 h.
  - #3449: approved 10:10:29Z, open 5.3 h.
- What rejoins already, within the same train. `rejoin_candidate` queues only a `HeadRed`
  holding GATE (Card 1). The log holds 2 GREEN rejoins, at 359 s and 7229 s after their skips
  (`grep "REJOIN.*GREEN"`), and 18 `RED; stays skipped`. TIMEOUT, A5 and parked skips are final
  for the run.
- The same skip classes across the whole log. The awk pass counts distinct PRs per class at their
  first `SKIP #N` line, then `PRE-FLIGHT` starts until `#N MERGED`:
  - timeout: 5 PRs. #2872 took 17 trains, #3304 took 10, #3006 took 1, and 2 are open.
  - parked: 25 PRs, median about 3 trains.
  - A5 disagreement: 2 PRs.

  Train starts are not wall-clock time. train.log carries no timestamps on SKIP or MERGED
  lines, so the hours a skipped green entry waits cannot be read from it. Train starts
  inside one run (293 `PRE-FLIGHT` lines in the log) also inflate the counts.
- The proposal names two classes, and each already has an owner fixing its cause:
  - TIMEOUT on #3445 and #3446 is the gate re-dispatch livelock. R10-HOTFIX-GATE-REDISPATCH-LOOP
    is `in-progress` on it (triage P620), and it covers part (3) of the proposal too.
  - A5 "more than 100 contexts" is `platform_gate`'s unpaginated read (:480).
    R10-GATE-DEFER-BARRIER's carry A5-ROLLUP-PAGES owns it.

  Once both land, TIMEOUT and A5 skips at a green head no longer arise from these causes. On
  those two classes, readmission would build machinery over symptoms that are already being
  removed.
- CARRY, the third class (a head moved by a clean main merge), and letting `merge_pr.sh --mandate`
  run `app_approve --carry` itself. This changes which tool approves a moved head, which is
  decision 0011's identity route. It has one instance this round (#3445), and no wall-clock
  measure against the one-entry merge_train route that exists today.

Cost:
- A re-admission path in `merge_train.py`, a hot file of over 7000 lines. It needs `_seen` and
  ALREADY bypasses by skip class, its self-tests, and a review round.
- Plus a `merge_pr.sh` approval branch, whose identity semantics need the owner's view (0011).

Binding: unmeasured. The benefit cannot be stated in hours, because the log has no timestamps,
and after the two in-flight cause fixes it may be near zero on the classes named. An unmeasured
proposal is DEFERred, never ACCEPTed.

What would change it:
- (a) R10-HOTFIX-GATE-REDISPATCH-LOOP and A5-ROLLUP-PAGES both merge, and a green, verdicted entry
  is still skipped as TIMEOUT or A5. That reopens it with that instance.
- (b) The train timestamps its SKIP and MERGED lines (or the skip rows in `skipped.json`), and a
  2-day window shows parked or CARRY entries that skipped green waiting at least 20% of
  merged-PR latency.

Owner today: the local workaround (stop in a CI wait, remerge, fresh train) stands.
