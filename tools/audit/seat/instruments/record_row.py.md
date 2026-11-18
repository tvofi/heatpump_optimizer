# `record_row.py`

- `record_row.py` — the record-autofix generator: enumerates merged PRs from
  the REST API, plans the delivery rows the tree still lacks, applies them
  behind a guarded write set (`dev/programme/delivery/<N>.md` only). When: the periodic
  `record` beat. Refusal: any path outside `dev/programme/delivery/<N>.md` — the plan
  table and HANDOVER are a seat's dispositions, never this generator's — and
  a window it cannot attribute refuses rather than reports empty. Every API
  read is `_api`'s, under `gh_read.py`'s read rule.
  `--automerge-check --pr N [--head SHA] [--hold] [--require-green]` is the
  guard CI approves and merges a record pull request behind (exit 3: guard
  passes, a required check has not yet); `--replay-moved` replays one
  older than the row directory's move. Refusal: any file but a new one-line
  row at its canonical path that the API's facts re-generate, or an author
  other than the hpo-author App.
