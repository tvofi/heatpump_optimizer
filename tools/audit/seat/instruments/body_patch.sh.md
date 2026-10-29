# `body_patch.sh`

- `body_patch.sh` — repairs an open pull request's BODY without moving its
  head: `body_patch.sh [--dry-run] [--repo O/R] <pr> <expected-head-sha>
  <body.md>`. Reads the live head, runs the body contract offline at it
  (`policy_lint.mjs --pr-body` with pr-contract's arguments, then
  `carry_audit.py check --body`), PATCHes as `hpo-author` through
  `tools/pr/app_mint.sh` (the mint `app_push.sh` shares), reads the body back
  and re-reads the head. When: a body `pr-contract` or `carry_audit` refuses
  on a head that must not move (ruling R4; `update_pr.sh` merges main on every
  run). Refusal: a live head other than the expected sha, before any mint or
  write; a body the contract refuses is never sent; `--dry-run` prints the
  PATCH request and signs nothing; a read-back that cannot be performed in
  three tries refuses, never reports OK. The offline contract runs the
  caller's checkout, so it can differ from pr-contract's (the script header
  says how). One `--once` unit: its last line is `body_patch: OK|REFUSE ...`.
