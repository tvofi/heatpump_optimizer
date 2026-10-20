_Requested by **tvofi**_

The mechanical record beat (R9-FR-10): delivery rows for the merges that landed without one, generated from REST API facts by `tools/audit/seat/row` automation and written behind a guarded write set. Rows for merged pull requests #2480 (`d99b400`), #2483 (`a2b25bb`), #2484 (`6233925`). This pull request disposes itself as record-class (only row files change); a row whose subject no roster group claimed carries the neutral phrasing. The handover's updated-for line stays manual by design.

## Head

`f851f243976a2a5e67b9813de47ae32b9b7814cd` (the row commit this pull request opens at, computed against main at `76bb456`; a main that moved under the push is re-derived by the fetch/reset loop, never merged or forced)

## Figures

- delivery-status ledger at this head: `python3 tests/delivery_status.py` -- the instrument; re-derive at the head.
- each row file is exactly one line anchoring its own pull request number, never a table row: read back through the same anchor `policy_lint --record` applies.

## Mutation proof

n/a: record-only diff -- every file in this pull request is a `dev/programme/delivery/<N>.md` row file; there is no production, test or check code here to mutate.

## Null control

n/a: no quantified production claim; the one figure names its instrument and re-derives at the head.

## Red checks

`record`, `the nightly lane` and `the delivery reporter` may stand red on main at the base this beat was computed against; each is answered here.

- `record`: a rowless merge is the batch interval the record protocol promises, and this pull request is that batch, which is the answer the check's own refusal text names. No cheaper detector exists than the check that already fired; its standing cost is one beat per batch.
- `the nightly lane` and `the delivery reporter` grade `main`, not this pull request. This beat's delivery rows are precisely the drain `the delivery reporter` batches, so the red is the batch this beat exists to close; `the nightly lane` executes nothing this diff changes and is answered because the shared reporter-input rule counts a row the diff rewrites. No cheaper detector exists than the check that already fired; its standing cost is one beat per batch.

## Forward-carry

none

## Friction

none

## Approval

Opened by the hpo-author App. No review seat: where `record_row.py --automerge-check` passes at the head, the approver App approves and the beat merges it at that head once its required checks pass (tvofi, 2026-10-07); where it refuses, the review stays manual. The HANDOVER updated-for line stays manual; this automation never writes it.
