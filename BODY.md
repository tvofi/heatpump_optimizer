_Requested by **tvofi**_

Record handoff: the `**open**` delivery rows for the three open dependabot pull requests #3321, #3322 and #3323. `bus.sh` refuses to dispatch reviewers for a dependabot head until origin/main carries its row, and a commit on the bot's branch would redden pr-contract, so the rows land from here and the dependabot branches are untouched. Each row was written by `record_row.py`'s own `open_row_line` through `write_rows` (the guarded write set), with the title read from the API; the CLI's `--write-self-row` only emits a row titled for the record PR itself, so the functions it calls were used directly with the dependabot titles.

## Head

`2325188b4e78bda34b599a2fee44c4c975c69c23` (the row commit, on origin/main `bb7dfb9bd6`)

## Figures

- delivery-status ledger at this head: `python3 tests/delivery_status.py` -- the instrument; re-derive at the head.
- each row file is exactly one line anchoring its own pull request number, never a table row.

## Mutation proof

n/a: record-only diff -- every file is a `dev/programme/delivery/<N>.md` row file; there is no production, test or check code to mutate.

## Null control

n/a: no quantified production claim; the one figure names its instrument and re-derives at the head.

## Red checks

none

## Forward-carry

none

## Friction

none
