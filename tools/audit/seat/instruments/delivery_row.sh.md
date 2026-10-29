# `delivery_row.sh`

- `delivery_row.sh` — the one seat-script writer of a PR's own `**open**`
  row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and
  `handoff_push.sh`: `commit_row` commits it as tvofi, `ensure_row` adds it
  only when the head lacks it. `record_row.py` is the other row writer, for
  the record beat's rows and its own PRs. When: never by hand; the openers
  call it. Refusal: none; `ensure_row` adds nothing to a head that carries
  the row, and `bus.sh --self-test` runs its self-test and refuses a seat
  script with its own `write_row` or row commit.
