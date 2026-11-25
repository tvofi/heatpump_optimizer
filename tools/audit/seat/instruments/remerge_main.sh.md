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
  `--head-repo <owner/repo>` (decision 0017, a head that is not a branch of
  ours) is refused before anything is fetched, minted, merged or pushed: `REMERGE
  FAILED <pr> at fork (<owner/repo>:<branch>)`, exit 1, saying the contributor
  brings the branch up to date with main. No identity of ours merges into,
  pushes to or `update-branch`es a contributor's fork (tvofi, 2026-11-22: "DO
  NOT MERGE ANYTHING ON ANOTHER USERS FORK"). The train does not call it for a
  fork head at all: it parks the entry `[OUTSIDE]`. The self-test refuses a
  stale head and a conflicting head and checks that no fetch, token, curl,
  `app_push.sh` or push was made; the attached-branch case is the null control
  for our own heads.

