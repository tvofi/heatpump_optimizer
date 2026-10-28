# `gh_read.py`

- `gh_read.py` — the read rule every seat instrument's GitHub READS are
  under, stated here once: `app_push.sh`'s read-back rule, 4 reads settling
  5/15/45 s, retrying only a transport error, HTTP 5xx, 429 or a 403 whose
  status line names the secondary rate limit; a failure naming a longer wait
  (Retry-After, or a spent bucket's reset on a rate-limit response: a 429,
  or a 403 naming a rate limit) is read no sooner, and one past 45 s refuses
  at once naming it; any other status is judged by its code alone, whatever
  bucket it carries. When: a new GitHub read in a seat instrument —
  `retry` with `gh_wait` (gh's output) or `urllib_wait` (urllib's), and
  `is_read` before retrying any `gh` call; `app_approve.sh`'s `gh_transient`
  is the bash twin its self-test compares row for row. Refusal: every other
  failure (401, a permission 403, 404, 422, an unclassified one) after its one
  call, a spent budget with its last error and the attempt count; a write is
  never retried. Its `self_test()` runs inside `record_row.py`'s.
