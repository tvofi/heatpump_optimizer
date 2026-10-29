# `worktree_gc.sh`

- `worktree_gc.sh` — collects a merged PR's worktree, branch and seat
  scratch. When: after merges, before the disk fills (9.5 GB of orphaned seat
  directories once). Refusal: `--dry-run` prints the collection list; a
  worktree with unpushed work is left alone.
