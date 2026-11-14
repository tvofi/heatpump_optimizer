# Proposal triage, session s14, batch 213

Sources: triage queue lines 325 to 328, four PROPOSAL lines (orchestrator s14,
2026-11-11T19:32:39Z), ruled as P647 to P650. Line numbers are at origin/main 5cc6f6f2ef.
Roster read at handoff/audit-r10-roster b2e3bdbcdd. Open pull requests are over the cap of 20,
so no new non-priority group is started here.

## P647: the relay's handoff-update arm starves its verdict and confirm arms

Verdict: REJECT as duplicate of s6-batch182.md#P601 (RELAY-ARMS-FIRST, the brief of R10-RELAY-ARM-ORDER, #3465 open) and its carry check s6-batch202.md#P630.

Source: triage queue line 325.

Instances:
- `grep '^POSTED 2026-11-11' $HPO_STATE_DIR/cloud-relay.log`: 81 POSTED lines, 00:30:06Z to
  19:24:09Z. No POSTED line from 18:23:27Z to 19:23:04Z (59.6 min), the gap the proposal names;
  then 3428, 3452, 3468 and 3479 posted at 19:23-19:24Z. Six more gaps over 45 min that day
  (longest 89.9 min, 13:21:59Z to 14:51:54Z). A gap alone does not prove starvation; it is the
  bound the proposal's own measure would read.
- tools/audit/seat/cloud_relay.sh:860, pass(): `handoff_arm; carry_fold_arm; probe_arm;` then
  `confirm_arm`. On main the handoff arm still runs first.
- That is the cause P601 already accepted: R10-RELAY-ARM-ORDER (severity medium, stage
  in-progress, PR #3465 OPEN at head 97ecbaea1d) reorders pass() to run probe_arm and
  confirm_arm before handoff_arm. P630 made it a carry check on the same PR.

Cost: none new. The cure is already built and waits on #3465's merge.

Binding: duplicate. The proposal's "own beat row" alternative is not needed once the reorder
lands. The proposal's measure (minutes from probe-ref push to POSTED) belongs in #3465's review
as the before/after figure, not in a new group. To the orchestrator: drive #3465 to merge; the
by-hand relay/confirm is the local workaround until then.

## P648: a pending-ci verdict is refused on main's inherited red

Verdict: REJECT as duplicate of s6-batch162.md#P576 and s6-batch170.md#P585 (R10-REVIEW-DISPATCH-RESIDUE carries 21 and 23, accepted, not yet built).

Source: triage queue line 326.

Instances:
- $HPO_STATE_DIR/s14/sweep.md:586, `WORKAROUND 2026-11-11T19:30:49Z #3452 pending-ci verdict
  posted past classify: red is main's inherited instrument-self-tests, cured by remerge ... (also
  #3428, same)`.
- $HPO_STATE_DIR/cloud-relayed.refused-why: 6 `classify RED` refusals (rev-3430 three times,
  3404, 3425, 3442). #3452 and #3428 were refused as stale (review_carry FRESH-REVIEW) after the
  head moved.
- tools/audit/seat/cloud_relay.sh:273 still dies on RED, and the pending-ci block refuses a moved
  head before any carry test. On main `grep -c HELD-PENDING-CI-RED` finds nothing: neither carry
  is built.

The rule, run per instance:
- P585 holds a RED draft (return 75) instead of refusing it finally; P576 carries the verdict
  across the remerge when review_carry answers CARRY and posts on GREEN at the live head. Each of
  #3452, #3428 and #3430 is a red that "only a main merge cures" (P576's own words). Built, the
  pair posts all three with no hand post, which is the proposal's measure.
- What the proposal adds is posting at the red head itself, before the remerge, by an INHERITED
  class. That gain is the minutes between the red read and the remerge's green. It is
  unmeasured, and the train gates CI at the merged head anyway. It does not reach the bar on
  its own.

Cost: none new. A third pending-ci arm on the same block would compete with P576/P585's design.

Binding: duplicate. To the orchestrator: the reviewer of R10-REVIEW-DISPATCH-RESIDUE's next part
may check P576+P585 against #3452/#3428/#3430. If a held, carried verdict still needs a hand post
after they land, re-raise with the hand-post count.

## P649: body_push's carry-fold run fails for want of tools/pr/ci_predict.py

Verdict: REJECT the candidate (a worktree at origin/main): the stated cause is refuted and the fix would run body_push on the wrong tree; DEFER the residual transient to R10-RELAY-NOBODY-STALL on recurrence.

Source: triage queue line 327.

Instances:
- $HPO_STATE_DIR/digest/gone.txt:12,13,15: three `body_push rc=1: body_push:
  $HPO_STATE_DIR/cloud-fold-code carries no tools/pr/ci_predict.py` lines, for
  r10-outside-disinfection-setpoint, r10-relay-arm-order and r10-sav-valuation-residue. The
  digest has already moved them to gone.
- tools/audit/seat/cloud_relay.sh:837-841: cloud-fold-code is not a stale long-lived tree. Each
  fold does `rm -rf` on it, prunes, and adds a fresh detached worktree at FETCH_HEAD of
  refs/heads/handoff/<topic>, runs body_push.sh there, and removes it.
- tools/audit/seat/body_push.sh:123-124: ROOT is `git rev-parse --show-toplevel`, so the check
  reads the handoff head's own tree.
- `git cat-file -e <head>:tools/pr/ci_predict.py` at the live handoff heads: all three carry it
  (r10-relay-arm-order 9647bc111d, r10-sav-valuation-residue 611102f076,
  r10-outside-disinfection-setpoint f4ae78eb64). The file has been on main since 00007b44c0
  (2026-10-07).
- The two re-tried topics then got past the check. cloud-relay.log.level at 19:21:04Z and
  19:23:30Z shows r10-relay-arm-order and r10-sav-valuation-residue failing on `refused body
  kept`, a later step after ci_predict ran.
- `ls $HPO_STATE_DIR/cloud-fold-code` now: absent, as the arm leaves it.

The rule, run on the candidate:
- The tree is the code head by design. body_push predicts CI for the head it pushes the body
  for, so a worktree at origin/main would predict main's CI, not the PR's: a wrong result, not a
  repair.
- P283's relay-tools worktree is a different need (the relay's own scripts), not the head under
  fold.
- The one shared fixed path ($state/cloud-fold-code, `rm -rf` before add) would let a second
  relay pass (a by-hand `--once --confirm` beside the loop) delete the tree under a running
  body_push. That fits a transient missing file, but it is not shown: no log line carries a
  pass pid or a timestamp for the three failures.
- Count: 3 lines on one board, all cleared without a fix. Under 20% of the day's folds on any
  reading, and unmeasured as a rate.

Cost: none now.

Binding: misdiagnosis. Re-raise condition, to the orchestrator: a further `carries no
tools/pr/ci_predict.py` line from cloud-fold-code, with `git -C <wt> rev-parse HEAD` and the pass
pids at the time. If it is the concurrent-pass race, it is a per-pid worktree path (one line) on
R10-RELAY-NOBODY-STALL, which lists cloud_relay.sh and body_push.sh.

## P650: the standing dispatch seat's token burn

Verdict: DEFER: the benefit is unmeasured, it is a new instrument while open PRs exceed 20, and part of the load is P647's hand relay, which #3465 removes; re-raise after #3465 merges with the measure below.

Source: triage queue line 328.

Instances:
- $HPO_STATE_DIR/s14/seat/dispatch/STATE-HANDOFF.md recycle headings: s14-31 ~17:30Z, s14-32
  ~18:00Z, s14-33 ~18:40Z, s14-34 ~19:02Z, s14-35 ~19:40Z. That is 4 recycles in about 2 h 10 min
  (about 2 per hour), as stated. The 106k/126k token figures are the orchestrator's (cited, not
  re-measured).
- The same file, line 590, holds a BY-HAND RELAY/CONFIRM RECIPE. The seat relays and confirms by
  hand because the relay's own arms are starved (P647), which is #3465's cure.

The rule:
- The cost side is measured: tokens per seat-hour, about 2 recycles an hour. The benefit side is
  not: no figure says what share of the seat's tokens is board reading that a ref-change event
  line would replace, rather than acting, relaying or confirming.
- Unmeasured is DEFER, never ACCEPT. A tracked watcher plus a READY/FIRE generator is a new
  instrument group (new files, a self-test, review rounds). While open PRs exceed 20 it may not
  start.
- Some of its target goes away when #3465 merges, because the relay posts and confirms itself
  and the seat stops relaying by hand. Measuring before that would overstate the gain.

Cost: a new S group (two new tracked scripts, self-tests, one review cycle), plus the cost of
reading events in the seat contract (standing-dispatch.md, policy, owner approval at merge).

Binding: unmeasured gain; cap. Re-raise condition, to the orchestrator: after #3465 merges, take
one dispatch seat's transcript and report two figures. (1) Tokens per seat-hour and recycles per
day. (2) The share of its tool-output tokens that are board, ledger or ref listings, as opposed
to action outputs. If (2) is over 20% of (1), it is ACCEPTable on token usage once open PRs are
at or under 20. Likely home: a carry on R10-REVIEW-DISPATCH-RESIDUE (dispatch seam), or
R10-STANDING-CONTRACTS-P2 carry 16 (fold standing loops into the beat) for the contract side.
