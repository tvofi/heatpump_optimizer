# `worktree_gc.sh`

- `worktree_gc.sh` — collects a merged PR's worktree, branch and seat
  scratch. When: after merges, before the disk fills (9.5 GB of orphaned seat
  directories once). Refusal: `--dry-run` prints the collection list; a
  worktree with unpushed work is left alone.
  Keeps a branch worktree holding a commit no remote ref has (`unpushed`),
  whatever its pull request says. A clean, old, detached worktree whose head a
  remote ref or tag holds (after one `git fetch --prune origin`) is removed as
  `on-remote` unless a process has its cwd inside (`cwd-inside`; an unreadable
  lsof is `cwd-unread`) or the head is the origin/main tip; a failed fetch keeps
  them all as `unmerged-head`.
