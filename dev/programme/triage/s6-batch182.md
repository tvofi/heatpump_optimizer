# Proposal triage, session s14, batch 182 (P601)

This batch rules `s7/triage-queue-s7.txt` line 280. The bar and the denominators are batch 141's.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster`, read at 10:20Z.
- `$HPO_STATE_DIR/cloud-relay.log`: its `POSTED <utc> <pr> <head>` lines.
- The committer times of the `origin/probe/rev-*` refs.
- No GitHub API calls.

## P601: RELAY-ARMS-BEFORE-HANDOFF-ARM

Verdict: ACCEPT, narrowed:
- arm 1 is accepted: the relay and confirm arms run first;
- arm 2 is rejected: detached per-branch updates.

The ruling opens the not-started group R10-RELAY-ARM-ORDER.

Source: queue line 280, 2026-11-11T10:08:41Z, orchestrator s14.

### Measured

**The order.** `pass()` (`cloud_relay.sh:860`) runs, serially:
`handoff_arm; carry_fold_arm; probe_arm; confirm_arm; stuck_arm; noreturn_arm`.

`handoff_arm` (`:572`) runs `update_pr.sh`, which runs a full prepr, inline. Every `probe/rev-*`
verdict returned in the meantime waits for it.

**Verdict-to-post latency, 24 h from 2026-11-10T10:00Z.** Each `POSTED` line is matched to the
latest `probe/rev-<pr>-*` commit at or before it. That gives n = 45:
- median 6.8 min;
- p75 18.1 min;
- p90 51.6 min;
- max 112.7 min.

16 posts waited more than 10 min, 11 more than 20 min, for 715 PR-minutes in total. The tail is the
proposal's class: 3449 waited 55 min and 3423 73 min, both posted at 10:09Z after the #3442 update.

**Confound.** The latency also holds confirm retries and refusals. For example, 3438's 113 min
includes a re-review. So the shares below are upper bounds.

**The coupling.** `confirm_arm` (`:433`) reads the open-PR list `handoff_arm` writes (`:588`, P332).
When that file is absent, it already lists the open PRs itself (`:434-436`). So the arms can be
reordered without losing confirm's open-PR filter.

### Bar

- **Benefit.** With the relay first, a returned verdict waits at most one pass interval plus the
  relay's own seconds, not an update queue. The 11 posts over 20 min carry about 510 of the 715
  PR-minutes. Capping them near one tick removes up to about 55-65% of verdict-wait minutes.
- **Why that counts on the bar.** Verdict wait is on the critical path of every PR between its
  review and its repair or merge. A cut of more than 20% therefore counts on the
  programme-completion axis. Reviewer idle time falls with it.
- **Cost.** One pass-order change plus hoisting the one open-PR listing, so that both arms share
  it. No extra API calls, and zero extra seconds per pass.

### Narrowed

Arm 2, detached updates under a per-branch lock, is REJECTED:
- it is not needed for the latency once arm 1 lands;
- it would run several full preprs at once on the local box;
- `update_pr.sh` already answers BUSY on a held worktree, 83 times in this log, so the lock already
  exists and a detached runner adds a second concurrency surface for no measured gain.

### Card (R10-RELAY-ARM-ORDER)

1. **`tools/audit/seat/cloud_relay.sh` `pass()` (`:860`).**
   - List the open PRs once at the head of the pass, into the file `confirm_arm` already reads.
   - Then run `probe_arm`, then `confirm_arm` (under `--confirm`), then `handoff_arm`,
     `carry_fold_arm`, `stuck_arm` and `noreturn_arm`.
   - `handoff_arm` reuses that listing instead of making its own call.
   - **Self-test.** With a stub `handoff_arm` that sleeps or records its order, a probe ref returned
     before the pass is POSTED before `handoff_arm` starts.
   - **Mutation proof.** Restoring the old order fails that check.
   - **Null control.** A pass with no probe ref posts nothing and still runs the handoff arm once.
   - The existing `pass` self-tests at `:1033-1035` stay green.

Destination: every group that lists `cloud_relay.sh` is done or absorbed, except
R10-REVIEW-DISPATCH-RESIDUE, which the brief excludes. So this is a new S group. Its overlap with
R10-REVIEW-DISPATCH-RESIDUE is on a distinct seam, the arm order in `pass()`.

### Local workaround, in force

Run `cloud_relay.sh --watch --once --confirm` beside the pass. This is the orchestrator's own
workaround and is unchanged.
