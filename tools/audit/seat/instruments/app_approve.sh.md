# `app_approve.sh`

- `app_approve.sh` — approves a pull request as the `hpo-approver` App at one
  exact head SHA, only on a `merge` verdict for that SHA from an allowlisted
  account (`--carry` re-approves a carried verdict: no branch-authored commit
  in `git rev-list <verdict>..<head> --not main`, every merge git's automatic
  one and each `claimnotes` file a pure union of its parents' lines or main's
claim-driver output on them). When:
  landing a
  non-code-owned verdicted PR whose head the reviewer measured. Refusal: a
  head SHA that is not the PR's current head, or a verdict whose SHA or
  account does not match — the approval names one tree or it does nothing.
  Its GitHub reads -- the four `gh api` reads and curl's JWT read of the
  App's installation -- are under `seat/gh_read.py`'s read rule; the token
  mint and the review POST are never retried.
