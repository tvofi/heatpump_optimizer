# `wt_sync.sh`

- `wt_sync.sh` — snapshots every worktree whose state is not already on
  origin (unpushed commits, uncommitted or untracked files) to
  `origin/wip-sync/<slug>`, plus the orchestrator scratch. The slug is
  `ref_privacy.py slug`'s, never a host path (#2310). When: loop it
  detached so a crashed seat is recoverable from its branch. Refusal: it
  never touches the worktree or its index — a snapshot, not a save; a
  worktree whose snapshot would name the host is skipped with the guard's
  reason.
  It never runs from a stale tree: it starts with `base_fresh.py ensure`
  over its own checkout, restarts from the moved tree on `BASE-RESET`, and
  on a checkout it cannot move exits 4 with `wt_sync: REFUSE BASE-STALE`
  and snapshots nothing.
