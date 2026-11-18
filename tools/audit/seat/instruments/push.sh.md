# `push.sh`

- `push.sh` — pushes a branch and attaches a body that has already passed the
  contract check, in that order (#678). When: tvofi-identity pushes only;
  App-authored PRs go through `app_push.sh`. Refusal: the contract check runs
  before the push, so the red `pr-contract` can never land on your review
  head.
