# `update_pr.sh`

- `update_pr.sh` — brings an open PR branch to its head + a code SHA (merge) +
  origin/main (merged only when the PR is `DIRTY` or `git merge-tree
  --write-tree origin/main HEAD` conflicts: ruling R4), adds the PR's own
  delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head
  with what happened, pushes as `hpo-author`. A head that is the live head
  plus one commit asks `app_push.sh --row-only`, so a push that only adds the
  row takes the body contract instead of the full prepr, and prints
  app_push's `ROW-ONLY:` line naming which ran and why. A head the run leaves
  exactly where it was (the code sha already in it, or `-`; main clean; the
  row present) is BODY-ONLY: nothing is pushed, `body_patch.sh` runs the body
  contract at that head from the run's own worktree and PATCHes the body, and
  `update_pr: BODY-ONLY: #<n> at <sha>` says so; body_patch's refusal (a head
  that moved) is the run's. With `-`, a `handoff/<topic>` tip the head lacks
  refuses (pass it as the code sha). `cloud_relay.sh` calls this mode once per
  body move of a PR whose head holds its handoff.
  When: updating a PR after review prep or a main merge, or re-bodying it.
  Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
  silently; no open PR at the branch stops before any push. Up front, each an
  `update_pr: REFUSE:` line (`pr_args.sh`): fewer than three arguments; a
  code sha other than `-` that is not 40-hex, names no commit, or is not an
  ancestor of `origin/handoff/<topic>` (the topic `HANDOFF_TOPIC`, else the
  branch less `fix/`, then less `-pr`), naming a `handoff-body/<topic>` tip as
  the BODY sha; a missing `handoff/<topic>`; no body file. The body is a file
  here, so a missing body ref is no refusal. It detaches another instrument's
  clean worktree on the branch only when origin has that worktree's HEAD; one
  holding commits origin lacks (a PR's unpushed row) is refused, naming it.
  Any later stop prints `update_pr: STOPPED: ...`, and a refused push names its log.
  Its lock's holder leaves its own worktree detached once its push has
  ended, a SIGKILLed run's too, so no worktree of it holds the branch.
