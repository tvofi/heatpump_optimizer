# Proposal triage, session s14, batch 219

Sources: triage queue lines 346 to 349, four PROPOSAL lines of 2026-11-11, ruled as P669 to
P672. Line numbers are at origin/main 61afd4f2db. Roster read at handoff/audit-r10-roster
e2623f542c. Every accepted part is a carry on an existing group, so the open-PR cap does not
bear on them.

## P669: the core quota emptied, and the shim's count covers only a third of it

Verdict: ACCEPT (a) one host-wide gh call log, as a carry on R10-GH-READ-RESIDUE; DEFER (b) the cloud-share measurement and the second token.

Source: triage queue line 346 (orchestrator, 2026-11-11T22:25:23Z). The core bucket read 0 of
5000 at 22:25Z (reset 22:25:35Z). `gh_calls.py --top --since 21:26Z` counted 1180 calls, so the
line attributes about 3800 calls to callers the shim cannot see, chiefly cloud seats.

Instances, measured from the two shim logs over the bucket's hour (21:25:35Z to 22:25:35Z,
`awk '$1>=...&&$1<...'` over each log and its `.1`):
- `~/hpo-orch/r10s6/gh-calls.log`, the log `gh_calls.py` reads under the
  orchestrator's `HPO_STATE_DIR`: 1188 lines. That is the line's 1180.
- `~/.local/state/hpo/gh-calls.log`, the default home: 1833 lines in the same hour. No line
  shares a stamp and pid with the other log, so the two are disjoint.
- So the shim logged 3021 calls in that hour, not 1180. 1833 of them (61%) are invisible to the
  orchestrator's `--top`.
- Top callers in the default log: merge_train.py 1079, pass.py 331, blind_spots.py 321, `zsh -c`
  91. Across both logs merge_train.py logged about 1176 calls, about 24% of the bucket.
- The remainder the shim did not log is at most 5000 - 3021 = 1979 (about 40%). It also holds the
  extra pages of each `--paginate` call (the shim logs one line per call), and record_row.py's
  urllib read (the blind spot gh_calls.py states). The cloud share in it is not measured.

Cause of (a): tools/audit/seat/shims/seat-gh:64-65 writes to `${HPO_STATE_DIR:-$HOME/.local/state/hpo}/gh-calls.log`,
so each caller's environment chooses the log. gh_calls.py:744 reads only `state_dir()/gh-calls.log`.
The token and its bucket are host-wide, so a per-state-dir log splits a single quantity.

Duplicate check: R10-GH-READ-RESIDUE idx 5 (P588) is about the absence of the shim and the
tick loop's PATH. Idx 6 (P591) is about the comment guard. Neither names the split log. Not a
duplicate.

Accepted change (a): the call log is host-wide. The shim writes to one log fixed at install (the
default home's gh-calls.log) whatever the caller's HPO_STATE_DIR. `gh_calls.py --top` reads that
log, plus any distinct `$HPO_STATE_DIR/gh-calls.log` left by an older shim, and labels each
source's count. Self-test: a call made under HPO_STATE_DIR=X is counted by `--top` run with
HPO_STATE_DIR unset, and the reverse. Null control: one log and one call print today's tables.
Add a mutant that drops the second source.

Basis: a medium defect repair (R10-GH-READ-RESIDUE, severity medium, carries-open) and over 20% on
the API-call attribution measure (61% of logged calls were unread). The owner's no-API-hammering
order (2026-11-08) needs the spenders named.

Deferred (b): to measure the cloud share, by a per-seat count or a second token for cloud seats.
Re-raise it after (a) builds, if in an hour where the bucket empties the rate_limit `used` figure,
less the REST requests the host log accounts for (with paginated pages counted), exceeds 1000
(20% of the bucket). Issuing a second token is a credential action for the owner, not a triage
destination.

## P670: the relay relays a probe ref that was disposed at its sha

Verdict: ACCEPT as a carry on R10-REVIEW-DISPATCH-RESIDUE (probe_arm skips a rev-/revt- ref disposed at its sha).

Source: triage queue line 347 (the dispatch seat via the orchestrator, 2026-11-11T22:25:50Z).

Instances:
- ~/hpo-orch/r10s6/dispositions.tsv:164 holds `refs/heads/probe/rev-3481-c0d2fd50
  6f2ab2974dca... 2026-11-11T22:13:16Z relay-dispose`.
- ~/hpo-orch/r10s6/tick.txt.relay.log:29-38. At 22:23:24Z the relay relayed that
  ref at the same sha. It pushed review/3481 a61af580 and logged `OWED verdict-unposted #3481
  7c7f0608`. The verdict came from a reviewer below the fixer's model. The local stopgap disposed
  review/3481 at a61af580.
- Cause: in tools/audit/seat/cloud_relay.sh probe_arm, a ref that is not `probe/rev-*` or
  `probe/revt-*` checks `disposed` (:341). A rev-/revt- ref checks only cloud-relayed (:342) and the
  refused list (:343-348), then goes onto the relay list (:349). A disposition never stops a relay.
  The arm's own header (:38-42) says that probe/rev-* is OWED until disposed. Today a disposition
  takes the ref off the level but not off the relay.

Duplicate check: R10-REVIEW-DISPATCH-RESIDUE idx 12 (P546) makes dispose take handoff-wip refs
and makes the carry-fold arm and bus.sh orphans honour dispositions. Idx 20 (P575) is about
ledger.py covered(). R10-FLY-RELAY-REVIEW-FF idx 17 (P332) is about confirm_arm on closed PRs.
None covers the probe_arm rev-/revt- relay path. Not a duplicate.

Accepted change: before a rev-/revt- ref is written to the relay list, probe_arm skips it when
`disposed "$ref" "$sha"` holds, the same check :341 makes for other probe refs. A disposed ref that
moves is relayed again at its new sha. Self-test: a rev- ref disposed at its sha is not relayed
and no review/<n> is pushed. Null controls: an undisposed rev- ref is relayed as today, and a
disposed ref whose tip moved is relayed at the new sha. Add a mutant that drops the check.

Basis: under 20% on cost (1 instance). The basis is severity-exempt only: it repairs observed
wrong behaviour on a medium group, and the defect let a verdict from below the required model
reach the post path. On the cost bar alone it would be REJECTed. The cost is about 2 lines plus
a self-test arm, in a file the group already owns.

## P671: the train's head wait never runs the stale check

Verdict: ACCEPT as a carry on R10-TRAIN-RESIDUE-P2 (wait_ci runs the stale re-run while a required context stays pending).

Source: triage queue line 348 (orchestrator, 2026-11-11T22:27:34Z). Stopgap in
~/hpo-orch/r10s6/s14/sweep.md:675.

Instances:
- #3455 at cbf80c6e waited from poll 1 to poll 19 (t+4370 s of 7320 s). It was waiting on gate
  check-run 130782293389, which was queued over run 43089450993, a run that had already completed
  (left over from the GitHub outage). Four newer gate runs at the same head were green. A hand
  `merge_train.py unstale cbf80c6e` cleared it in one call (sweep.md:675). The line's cost figure
  is about 73 min of a stalled critical-path train, with 21 PRs spooled.
- Cause, at 61afd4f2db: tools/audit/seat/merge_train.py `unstale` (:3648-3672) runs only from
  `land` (:2722), and that is after the head wait. `wait_ci` (:1905 onward) polls `latest_runs`.
  A queued check-run over a completed run reads pending on every poll, so the wait never reaches
  `land`. The other way out of it is the wait cap.

Duplicate check: R10-TRAIN-RESIDUE-P2 idx 13 (P567) widens `unstale` to re-run red deferrals, and
it still runs inside `land`. Idx 20 (P659) is about the wait cap during an outage. Neither moves
the stale check into the wait. Not a duplicate.

Accepted change:
- Split the re-run half of `unstale` into its own step that returns the runs it re-ran, each run
  once per head. `unstale` keeps that step followed by its wait.
- `wait_ci` calls the re-run step at poll 3, and every 6th poll after that, while a required
  context is still pending. It logs the STALE line and goes on waiting. It never calls `wait_ci`
  recursively.
- Cost: one `actions/runs/<id>` read per pending required check-run, at those polls only.

Tests:
- Self-test: the #3455 shape (a queued check-run over a completed run, with green gate runs
  beside it) is re-run once by poll 3, and the wait then concludes.
- Null control: a check-run that is pending over a run still in progress is not re-run.
- A second pass at the same head re-runs nothing.
- A mutant that drops the call keeps the fixture waiting to its cap.

Basis: under 20% on the cost bar (1 instance). The basis is severity-exempt only: R10-TRAIN-RESIDUE-P2
is a medium group, and this repairs observed wrong behaviour on the critical path. On the bar
alone it would be REJECTed.

## P672: REVIEW STALLED fires on a review that came back and is held for CI

Verdict: ACCEPT as a carry on R10-TICK-RESIDUE-P3 (REVIEW STALLED reads the dispatch's probe ref before it flags).

Source: triage queue line 349 (orchestrator, 2026-11-11T22:29:12Z).

Instances:
- #3479 at d925d867 printed `REVIEW STALLED ... 95m`. Its review had already returned as
  probe/rev-3479-aeb68873 f36a81b9 at 20:38:46Z. At 22:23:20Z the relay held it
  `HELD-PENDING-CI #3479 d925d867` (~/hpo-orch/r10s6/tick.txt.relay.log:27-28).
- Cause, at 61afd4f2db: tools/audit/seat/orchestrator_tick.py `verdict_levels` (:720-729) prints
  the line when three things hold: the head is in the dispatch record, no approver verdict names
  it, and `_reviewer_ref_age` (:1046) is over STALL_MINUTES (90, :133). It never looks for the
  returned probe ref.
- owed_unactioned.py.md:7 maps the line to "re-fire the reviewer". The false line therefore
  calls for a second reviewer seat on a review that is already finished, and it opens a race
  between two verdicts.

Duplicate check: R10-TICK-LEVELS and R10-FLY-TICK-APPROVAL-OWED built the line (P328) and are
done. R10-REVIEW-DISPATCH-RESIDUE idx 23 (P585) is about the relay's pending-ci RED. No carry
on R10-TICK-RESIDUE-P3 names REVIEW STALLED. Not a duplicate.

Accepted change:
- When the stall condition holds, the tick looks for the dispatch's probe ref,
  probe/rev-<N>-<nonce8>, with the nonce taken from the dispatch record. It uses one git read, and
  only for a PR that has already met the condition.
- If that ref exists, the tick prints `REVIEW RETURNED: #N <head8> probe <sha8> <m>m` instead. That
  line is not flagged and is not on owed_unactioned's re-fire list.
- With no probe ref, the line stays REVIEW STALLED.

Tests:
- Self-test: the #3479 shape (dispatched, no verdict, a probe ref at the nonce) prints REVIEW
  RETURNED and no REVIEW STALLED.
- Null control: the same case without the probe ref still prints REVIEW STALLED.
- A probe ref at another nonce does not suppress the line.
- A mutant that skips the probe read restores the false line.

Basis: under 20% on the cost bar (1 instance; the frequency is unmeasured because the board keeps
only its last state). The basis is severity-exempt only: R10-TICK-RESIDUE-P3 is a medium group, and
this repairs observed wrong behaviour whose instructed action wastes a reviewer seat. On the bar
alone it would be REJECTed.
