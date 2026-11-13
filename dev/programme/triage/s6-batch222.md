# Proposal triage, session s14, batch 222

Sources: triage queue line 352 (orchestrator, 2026-11-11T23:53:25Z), ruled as P675. Line numbers
are at origin/main 046736a49f. Roster read at handoff/audit-r10-roster 3c73aab046.

## P675: a retired seat's clean branch worktrees hold update_pr.sh at BUSY

Verdict: ACCEPT, as a new group R10-UPDATE-PR-SEAT-WORKTREE, which widens update_pr.sh's detach of a clean worktree at the origin head from $P to the whole state dir, guarded by a live-process check.

Source: triage queue line 352. update_pr.sh answered BUSY three times tonight. Each time
fix/<topic> was checked out in a worktree of the retired merge seat s14-7 (wt3442, wt3355,
wt3458), each clean and at the origin head. The relay retried silently every pass (13 min) until
the orchestrator detached them by hand, and #3458's repair handoff waited 40 min. Proposed:
widen update_pr.sh's existing detach to seat scratch worktrees under the state dir, or have the
merge seat's recycle step detach its worktrees. Stopgap: all of s14-7's are detached.

Instances:
- tools/audit/seat/update_pr.sh :44 sets `P=${HPO_STATE_DIR:-...}/pr`. :64-68 detach another
  worktree on $BR only if it is under `$P/`, clean, and its HEAD is an ancestor of origin/$BR.
  :69 exits BUSY (75) on any other worktree holding $BR. A seat's worktree under
  `$HPO_STATE_DIR/s14/seat/...` is clean at the origin head yet outside `$P/`, so it reaches
  :69.
- `grep -h -i 'checked out elsewhere' cloud-relay.log tick.txt.relay.log`: 5 logged BUSY lines.
  2 of 5 (40%) name a seat worktree, merge/s14-7 and merge/s14-5; the other 3 name `$P` itself.
  The relay retries without logging each pass, so tonight's three are mostly absent from the
  logs. These counts are a floor.
- `ls -d s14/seat/*/*/wt*`: 25 seat worktrees exist under the state dir. Merge s14-7 holds 18
  (detached tonight), merge s14-5 holds 4, and dispatch s14-40 and s14-41 hold 3. Each recycle
  of a standing merge seat leaves its set behind.
- Cost seen: #3458's repair handoff waited 40 min, about 3 relay passes. Each further hold costs
  13 min per pass until a person notices.

Duplicate check: R10-UPDATE-PR-LOCK, R10-UPDATE-PR-SIGNALS and R10-OPENPR-SILENT are done.
R10-OPENER-REUSE and R10-RELAY-HANDOFF-ARM are absorbed. R10-CLOSEOUT-CLEANUP is carries-open.
None names a seat worktree outside $P (roster 3c73aab046). tools/audit/worktree_gc.sh collects
only a merged pull request's worktrees, so an open PR's branch, as here, is out of its reach.

Accepted change: a new group, size S, severity medium (it holds relay repair handoffs, the
critical path's re-entry), sonnet fixer and reviewer. File: tools/audit/seat/update_pr.sh, plus
its instruments page.
- In the :64 loop, the candidate set is every worktree on $BR under `$HPO_STATE_DIR/`, not only
  under `$P/`.
- Keep both existing guards: clean, and HEAD an ancestor of origin/$BR.
- Add a third guard, for a worktree outside $P: no live process has its cwd inside it (`lsof -a
  -d cwd`, as worktree_gc.sh :66 reads it). An unreadable lsof keeps the worktree, so the run
  stays BUSY as today.

Demonstration, in update_pr.sh's self-test: a clean seat worktree at origin's head under the state
dir is detached and the run proceeds. That fails on the base, where the run is BUSY, and passes on
the fix. Null controls: with a live process cwd'd in that worktree, the run stays BUSY; with a
commit origin lacks, the run stays BUSY.

Cost: about 8 lines in update_pr.sh, plus a self-test arm of about 15 lines. No new file. No API
call; lsof is local. update_pr.sh has no row in tests/structure_budgets.json. The rejected
alternative, a detach step in the merge seat's recycle, costs no code. But it binds only a seat
that ends cleanly, and a recycled seat often ends on a token or time limit, so it fails exactly
when the worktrees are left behind.

Binding: the destination's severity is medium, which skips the 20% bar. On the bar alone, the
logged share is 2 of 5 BUSY holds, 40%, a floor, so it would pass. The live-process guard keeps
it from detaching a seat that is using the checkout, which is what the `$P/` scope protected.
