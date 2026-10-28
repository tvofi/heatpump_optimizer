Record PR: #2878 (`22a2c9c`), #2888 (`939f0c6`) and #2889 (`6b9bf5b`) merged and were stamped into v7.0.5 under `--allow-rowless`, while their `dev/programme/delivery/<N>.md` rows still read `**open**`. Each row is rewritten to the line `record_row.py --plan` computed from the REST API's merge facts (`--enumerate --since v7.0.4`, filtered to the three numbers) and written by `--apply`; none is hand-edited. Only these three row files change, so it merges in a `--bot-prs` train batch.

Two lines change wording beyond the status, both from the API rather than the old row: #2889's old row carried another PR's title ("record: delivery rows (autofix)"), and #2888 loses its `(R10-PREPR-CAP)` suffix because the roster at `origin/main` claims its head branch `fix/triage-s6-batch40-correct-pr` for no group.

## Head

`7a8c06a219f12ffb98bc66e8e5f533706ebe227e`, on main `e8cb7e68302b1d350bb8219fea99e911170af030`.

## Figures

- rows the three merges still owe at this head: `python3 tools/audit/seat/record_row.py --plan --merges-file <the three merges from --enumerate> --roster-ref origin/main` -- re-derive at the head; a merge whose row already records its sha is dropped.
- the stamp's bar over the v7.0.4 window: `python3 tests/delivery_status.py --require-rows --repo tvofi/heatpump_optimizer --since v7.0.4`

## Mutation proof

n/a: record-only diff -- every file is a `dev/programme/delivery/<N>.md` row; no production, test or check code to mutate.

## Null control

`tests/delivery_status.py --require-rows` classifies on a row's presence, not its word, so it passes on the base as well as at this head; the status word is what this PR changes, and `record_row.py --plan` is the instrument that sees it (it plans all three at the base and none at this head).

## Red checks

none

## Forward-carry

none

## Friction

none
