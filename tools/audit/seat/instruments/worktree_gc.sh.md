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
  them all as `unmerged-head`. Every worktree removal is leased at the HEAD
  the listing read (`update-ref --no-deref -d HEAD <head>`): one whose HEAD
  moved since is kept and the refusal reported. An orphaned seat's removal
  is leased the same way, at the HEAD read in its unregistered `wt/`.
  Every removal arm, not only `on-remote`, keeps a worktree a process stands
  in (`cwd-inside`, `cwd-unread`). A seat branch (`work/`, `scratch/`, `seat/`)
  is judged by the pull request on `fix/<topic>`: merged or closed frees it
  when clean and pushed. Class E removes `*mutant*`, `*null*` and `*head*`
  copies without `.git` in a seat directory whose `fix/<topic>` PR merged.
  `WORKTREE_GC_SEATS_ROOT` is a colon-separated list (seats live under
  `~/hpo-seats/<round>`).
