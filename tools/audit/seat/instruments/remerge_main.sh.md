# `remerge_main.sh`

- `remerge_main.sh` — merges origin/main into an open PR (claimnotes merge
  driver), drops inherited claims, pushes as the App with `app_push.sh
  --recarry`, which prefixes ## Head with what happened and skips prepr only
  on a clean 2-parent merge of the live head and main under the live body.
  When: main moved under an open PR. Refusal: a conflict is not
  auto-resolved — it stops loudly instead, the merge aborted, so the worktree
  is left clean at origin/<branch> for the train to release. `MERGE CONFLICT
  <pr>` names only a merge that left unmerged paths; a fetch, reset or merge
  that failed otherwise prints `REMERGE FAILED <pr> at <step> (rc=N)` under
  git's own words, which the train stops on as a failure, never a conflict.
  `--head-repo <owner/repo>` is a head that is not a branch of ours (decision
  0017; the train passes the head repository the pulls API names): nothing of
  `origin/<branch>` is read, no claims commit is made, and the head moves only
  by GitHub's own `update-branch` at the expected head, asked as the
  hpo-author App, then read back as the automatic two-parent merge of that head
  and main. A refusal there prints `REMERGE FAILED <pr> at push (fork ...)`,
  which the train parks `[OUTSIDE]`. No tool of ours pushes a fork's head to a
  branch of origin: the train fetches it to `refs/remotes/pull/<pr>/head` only.
