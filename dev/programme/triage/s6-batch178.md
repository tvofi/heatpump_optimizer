# Proposal triage, session s14, batch 178 (P597)

This batch rules queue line 276 (the orchestrator's intake), 2026-11-11.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster branch at `f4d478511d` or later.
- The relay logs under the state directory: `cloud-relay.daemon.log` and `tick-loop.log`.
  Both are local, so no API was used.

## P597: TRAIN-SKIP-RELEASES-WORKTREE

Verdict: ACCEPT, widened from recarry-conflict skips to every SKIP phase, as the new not-started
group R10-TRAIN-RESIDUE-P2 (S, after R10-TRAIN-RESIDUE).

Why a new group:
- The seam's owner, R10-TRAIN-RESIDUE, is carries-open. Its part #3424 merged at 07:47:51Z.
  `roster_lib.carry_receivable` refuses a carries-open destination (R10-CARRY-SINK-BARRIER), and
  `queue_carry.py` refused it.
- Two receivable groups list `merge_train.py`, and neither owns this seam:
  - R10-SEAT-SCRIPT-OUTPUT covers output calls only.
  - R10-GATE-DEFER-BARRIER is a class barrier over gate-conclusion readers, and it carries a
    policy file.
- Neither of the two has a `handoff/`, `handoff-wip/` or `dispatch/` ref in flight.

Source: queue line 276. The train skipped #3404 on a recarry conflict, but kept
`merge_train/wt/3404` on the PR branch until the train closed. The relay's `update_pr` for the
conflict-repair handoff answered BUSY on every pass for more than 25 min. The orchestrator
detached the worktree by hand.

Measured in the code:
- The recarry makes `state/wt/<pr>` with `git worktree add -B <branch>` and appends it to
  `made_wts` (`:2525`).
- `release_worktrees` (`:2895`) removes `made_wts`, but only before the run's closing line.
- `skip` (`:3681`) logs the line, records the row and calls `seen_mark`. It never touches the
  entry's worktree.
- `update_pr.sh` (lines 14-16) exits 75, BUSY, while the branch is checked out in a worktree that
  is not its own run's.
- So a skipped entry's branch stays held for the rest of the train. A batch that holds for a
  rejoin can run for an hour or more.

Instances:
- `grep -h "BUSY.*merge_train/wt/" cloud-relay.daemon.log` gives 22 lines: wt/3297 5,
  wt/3350 13, wt/3361 4.
- The same grep on `tick-loop.log` gives 18 lines: wt/3297 2, wt/3350 4, wt/3355 3, wt/3361 1,
  wt/3398 6, wt/3404 2.
- So there are 40 BUSY relay passes against a train worktree, across 6 pull requests.
- `grep -rh "SKIP #<pr> "` finds a SKIP line for each of the 6, at more than one phase:
  - 3297: recarry and ci.
  - 3350: carry and ci.
  - 3355: ci.
  - 3361: carry and ci.
  - 3398: recarry and ci.
  - 3404: recarry, from the orchestrator's line.
- The fix must therefore release at every SKIP, not only at a recarry conflict.
- Across all logs, 23 distinct pull requests hit a recarry-conflict SKIP ("main does not merge
  without a resolution").
- The relay pass interval defaults to 120 s (`cloud_relay.sh:164`). So 40 passes is a lower bound
  of about 80 min of repair handoffs waiting, plus the hand detach each time.

The fix:
- `skip(pr, ...)` releases that entry's worktree at the SKIP line, if this run made it. The
  release takes it out of `made_wts`, so the closing release does not repeat it.
- A conflicted or dirty tree first gets `git merge --abort` when a merge is in progress.
- Then `git worktree remove` runs, never forced. If the remove fails, the fallback is
  `git -C <wt> checkout -q --detach`.
- It logs `released <wt> at SKIP` or `NOT released ...`, the same as `release_worktrees`.
- A queue entry's own `worktree` is never touched (`release_worktrees`'s rule).
- A rejoin of a skipped entry re-makes the worktree, because the recarry path already makes it when
  absent (`:2513`).

Self-test:
- A SKIP at the recarry phase leaves `wt/<pr>` gone, or detached, before the next entry's first
  line.
- A SKIP at the ci phase does the same.
- A worktree that holds unpushed commits stays. The skip logs `NOT released`.
- Null control: a non-skipped entry's worktree is still released only at close, as today.

Cost:
- About 20 lines in `merge_train.py` and four checks.
- `merge_train.py` has no row in `tests/structure_budgets.json` at `cbd23f1c8b`.

Binding:
- This removes a recurring slip class: 6 pull requests and 40 BUSY passes, each followed by a hand
  detach.
- The group's severity is `medium`, so the machinery bar does not apply.
- No ratchet exemption is claimed.
