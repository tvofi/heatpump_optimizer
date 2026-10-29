# `review_carry.py`

- `review_carry.py` — answers, from two shas and their commit range,
  whether a moved head still needs its own review: `review_carry.py
  <reviewed> <new>` prints the branch-only commit count, their subjects and
  exactly one `CARRY`/`FRESH-REVIEW` (`git rev-list --count <reviewed>..<new>
  --not origin/main`; CARRY needs zero, or every commit in it a merge, and
  then `tools/pr/app_approve.sh --carry` carrying the range — each merge
  git's automatic one, claim files a pure union, the branch's own diff equal
  — asked, never copied, so the two cannot answer one range oppositely; a
  merge of the branch's own previous head, update_pr.sh's re-cut, passes,
  and a hand-resolved conflict does not). When: before
  dispatching a reviewer at a moved head, and in a verdict that re-issues a
  prior one — the owner's 2026-10-27 ruling, "if there are no code changes,
  the previous review can be carried", made mechanical. Refusal: an unknown
  sha, a missing main ref or a missing commit cannot be decided (exit 2, no
  verdict line, so it is never read as CARRY); a force-push, a non-merge
  commit — including the commits a merge of a non-main branch brings in — and
  a `ci:`/`claims:` commit are all `FRESH-REVIEW`, and so is a range
  `app_approve.sh --carry` refuses, with its reason.
  `--verdict-only` prints the token alone; `bus.sh dispatch --reviewed-head`
  is its caller, and `--self-test` grades the ranges.
