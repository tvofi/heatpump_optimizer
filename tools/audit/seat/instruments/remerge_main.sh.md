# `remerge_main.sh`

- `remerge_main.sh` — merges origin/main into an open PR (claimnotes merge
  driver), drops inherited claims, pushes as the App with `app_push.sh
  --recarry`, which prefixes ## Head with what happened and skips prepr only
  on a clean 2-parent merge of the live head and main under the live body.
  When: main moved under an open PR. Refusal: a conflict is not
  auto-resolved — it stops loudly instead, the merge aborted, so the worktree
  is left clean at origin/<branch> for the train to release.
