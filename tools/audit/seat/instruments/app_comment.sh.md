# `app_comment.sh`

- `app_comment.sh` — posts one fix-review verdict on a PR as `hpo-approver`
  and reads the posted comment back byte-identical. When: a reviewer seat
  delivers a verdict. Refusal: a read-back that differs from what it meant to
  post, or a stale head — "posted" is never taken from the send's exit code.
