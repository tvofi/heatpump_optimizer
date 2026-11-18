# `app_push.sh`

- `app_push.sh` — pushes a branch and opens or re-bodies its pull request as
  the `hpo-author` App, with the body's contract check before the push. When:
  every handoff — pull requests are App-authored (decision 0011); `push.sh`
  is the tvofi-identity predecessor and must not author PRs. Refusal: a body
  failing the contract check never reaches the remote. `--row-only`
  (`update_pr.sh`'s) replaces prepr with pr-contract's two body checks (the
  contract, its red history read with prepr 7c's credential, and
  `carry_audit.py check`) only when the head
  is the live head plus one commit adding exactly that PR's own open row and
  the body is the live one under one new `## Head` note; else prepr runs.
  Every commit the PR adds over a freshly fetched `origin/main`, wherever it
  was first published (a `ci-probe/*` or `handoff/*` ref included), is
  judged by `ref_privacy.py guard --over` before anything is minted.
