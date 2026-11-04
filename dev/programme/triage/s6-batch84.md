# Proposal triage, session s8, batch 84 (P321)

The rolling batch (V182) after batch 83 (handoff `triage-s8-batch83`). Facts were read at
origin/main `861f949ae` and on the roster branch.

## P321: the relay updates a pull request from the previous round's body

Verdict: ACCEPT as already carried, with a priority flag; narrowed against the filing's timestamp
form. **R10-FLOW-BODY-ONLY** (`not-started`, S) has held this exact fix since 2026-10-28 as P233
(`s6-batch46.md#P233`, V147, "A handoff updates only with the body pushed for it"):
- `body_push.sh` writes a `Code: <40-hex>` trailer naming the handoff tip the body was written
  for;
- `cloud_relay.sh`'s `handoff_arm` does not update when the body tip's `Code:` names another sha,
  writing `level_line handoff-body-stale ... body names <sha12>` and retrying on its next pass;
- a failed update's level line carries the `REFUSE` reason.

It is unbuilt. The group's `next_step` has read "DISPATCH NOW: every `after` group is done" since
2026-10-27.

- **Priority.** The roster op raises R10-FLOW-BODY-ONLY to be dispatched next. This is the
  recurrence its brief was written for.
- **REJECTED: the filing's form, "refuse when the body ref's newest commit is older than the
  code ref's head commit".** A timestamp order is not an identity. A body re-pushed for an
  unchanged head (P233's #2890, #2891 re-bodies) is newer than the code yet correct. A stale body
  committed after a quick code push can also be newer, under clock skew between a cloud runner and
  this host. P233's `Code:` trailer names the head exactly and needs no clock.
- **Residual, not carried: "BUSY on a dead lock, no retry for 4 minutes".** `update_pr.sh` exits
  75 (BUSY) while `$WT.lock` is held, and the relay retries on its next pass (`update_pr.sh:12-16`).
  The group's carry 7 (exit 75 for a branch held elsewhere) covers that path. A lock held by a dead
  process that is never reclaimed would be a separate defect. This instance gives no evidence of it
  beyond "did not retry for at least 4 minutes", which may be the pass interval. DEFER: one
  instance with its cause unmeasured. A second relay BUSY on a lock whose holder pid is dead
  (`ps -p` empty), lasting more than two passes, re-opens it on this group.

Source: the orchestrator s8's message of 2026-10-31 (slip, 02:42Z, #3016).

Instances:
- **#3016, by the orchestrator's account.** The relay ran `update_pr` at `460e4b76` against the
  round-1 body `af5caa138` (`FIGURES: 9 resolved`, `CARRY-AUDIT: 1 finding item`). Prepr refused
  it on 11 unpinned sites and 5 unanswered reds, while the round-2 body (`1858b19a2`/`5dcf18b8`,
  `PR-BODY: 0 error(s)`, `18 resolved`) had not yet landed. About 15 minutes of orchestrator time
  and a fixer turn went into the diagnosis.
- **Earlier instances**, in P233's ruling: #2890 and #2891 were re-bodied stale (2026-10-27), and
  #2894 likewise. So this is the fourth or later, an audit class whose barrier is carried and not
  built.
- **The fix is not on main.** `git grep -n 'Code:' origin/main -- tools/audit/seat/body_push.sh
  tools/audit/seat/cloud_relay.sh` prints nothing at `861f949ae`.

Cost: as carried in P233, about 20 lines across `body_push.sh` and `cloud_relay.sh` with their
self-tests, in a group sized S whose after-edges are all done. This ruling adds only the priority
and the residual's re-open condition.

Binding: a carried, sized, unblocked fix for a recurring defect, still undispatched three days and
at least one more incident later. Raising its priority costs nothing beyond the dispatch it was
already owed. The timestamp variant would add a second, weaker check beside it.

Carry text (for `roster_edit.py append-carry R10-FLOW-BODY-ONLY`, citing
`triage: dev/programme/triage/s6-batch84.md#P321`): "P321 (orchestrator 2026-10-31, slip, #3016).
PRIORITY: dispatch this group next. Its P233 carry (the `Code:` trailer in `body_push.sh`, and
`cloud_relay.sh` `handoff_arm` not updating on a body naming another head) is the fix for this
recurrence.
- Observed 2026-10-31 02:42Z: the relay ran `update_pr` at `460e4b76` against #3016's round-1
  body `af5caa138` before the round-2 body landed. Prepr refused on 11 unpinned sites and 5
  unanswered reds the new body answered. About 15 orchestrator minutes and a fixer turn were lost.
  At 861f949ae neither file has a `Code:` line.
- Do not add a commit-time comparison (body newer than code): re-bodies of an unchanged head are
  newer and correct, and clocks skew between runner and host.
- Add one fixture row: the relay given a body tip whose `Code:` names the previous head writes
  `handoff-body-stale` and runs no `update_pr.sh`. Null: a `Code:` naming the current head
  updates."
