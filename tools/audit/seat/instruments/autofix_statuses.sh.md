# `autofix_statuses.sh`

- `autofix_statuses.sh` — re-derives what `mutation-autofix` and
  `closures-autofix` answered on recent pull-request runs, from their job
  logs, with the `closures` failure heading behind each closures skip. When:
  judging whether the autofix chain repairs anything. Refusal: a log GitHub
  no longer serves is counted beside the totals, never read as a status.
