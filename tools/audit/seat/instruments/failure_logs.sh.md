# `failure_logs.sh`

- `failure_logs.sh` — answers why a PR's newest red at its live head is red:
  latest failing check-runs (grouped by name, newest `started_at` wins, so
  red-then-green is not read as a failure) -> `details_url` -> job log ->
  error lines, per-check log files and a `HEAD.txt` under the out-dir. When:
  any red whose cause a watcher's state line does not carry. Refusal: a
  non-Actions check prints NO-JOB, an unserved log prints NO-LOG and exits 1
  with the count over readable logs beside the unread one; no error-marker
  match falls back to the log's tail, never a silent zero.
