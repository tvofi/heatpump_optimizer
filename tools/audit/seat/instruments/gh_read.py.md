# `gh_read.py`

- `gh_read.py` — the read rule every seat instrument's GitHub READS are
  under, stated here once: `app_push.sh`'s read-back rule, 4 reads settling
  5/15/45 s, retrying only a transport error, HTTP 5xx, 429 or a 403 whose
  status line names the secondary rate limit, or, with no status line, a
  body gh could not parse as JSON (`invalid character 'S' looking for
  beginning of value`); a failure naming a longer wait
  (Retry-After, or a spent bucket's reset on a rate-limit response: a 429,
  or a 403 naming a rate limit) is read no sooner, and one past 45 s refuses
  at once naming it; any other status is judged by its code alone, whatever
  bucket it carries. When: a new GitHub read in a seat instrument —
  `retry` with `gh_wait` (gh's output) or `urllib_wait` (urllib's), and
  `is_read` before retrying any `gh` call; `app_approve.sh`'s `gh_transient`
  is the bash twin its self-test compares row for row. Refusal: every other
  failure (401, a permission 403, 404, 422, an unclassified one) after its one
  call, a spent budget with its last error and the attempt count; a write is
  never retried. Its `self_test()` runs inside `record_row.py`'s. A workflow
  step reads through `gh_read_run.py`. `conditional_get` is the one ETag-conditional
  read of a single-page GET (`gh api -i`, `If-None-Match` from the ETag stored under
  `$HPO_STATE_DIR/gh-etag/`, shared by every process under that same state directory, not
  across state directories): a 304 serves the stored body, a 200
  replaces it, any other failure is UNREADABLE as a plain read's; `ruleset_checks` reads
  the required-status-checks rule through it for `merge_train.py` and `orchestrator_tick.py`,
  and the tick's comment and check-run reads go through it too. When: a seat instrument's
  repeated read of an object that changes rarely.
