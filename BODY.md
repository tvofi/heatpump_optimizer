_Requested by **tvofi**_

The mechanical record beat (R9-FR-10): delivery rows for the merges that landed without one, generated from REST API facts by `tools/audit/seat/row` automation and written behind a guarded write set. Rows for merged pull requests #2379 (`5756f2b`), #2394 (`3d46d69`), #2396 (`106af95`), #2401 (`07a0940`), #2416 (`fd64a23`), #2418 (`86010e8`), and this pull request's own row #2420. The follow-up commit upgrades the rows of the merged record pull requests #2407 (`3126b86`), #2412 (`003c373`) and #2413 (`be2d367`) from **open** to **merged**. This pull request disposes itself as record-class (only row files change); a row whose subject no roster group claimed carries the neutral phrasing. The handover's updated-for line stays manual by design.

## Head

`55f73caa994e394e522886d597a3dbd757b4790d` (the row-repair commit on top of the opening row commit `b0140e47bc2faf7e4aa8848a521eedf4321587df`, computed against main at `07a0940`; a main that moved under the push is re-derived by the fetch/reset loop, never merged or forced)

## Figures

- delivery-status ledger at this head: `python3 tests/delivery_status.py` -- the instrument; re-derive at the head.
- each row file is exactly one line anchoring its own pull request number, never a table row: read back through the same anchor `policy_lint --record` applies.

## Mutation proof

n/a: record-only diff -- every file in this pull request is a `dev/programme/delivery/<N>.md` row file; there is no production, test or check code here to mutate.

## Null control

n/a: no quantified production claim; the one figure names its instrument and re-derives at the head.

## Red checks

- `delivery-status`: `DELIVERY STATUS OVERDUE -- 3 overdue`: #2413, #2412 and #2407 are merged record pull requests whose rows still read **open**, and `classify` does not count an open-anchored row over a landed merge as rowed. Fixed here: each row now names its merge SHA, and `python3 tests/delivery_status.py --check` prints OK, 0 overdue, at this head. Cheaper detector: the check that fired is already the cheapest, a sub-second local run; the status word is not reconciled when a row is written (`delivery-status-tracking.md`), so the standing cost is one row upgrade per merged record pull request, until the word is graded.
- `wave-script`: the agreement lane refuses on `merge-subject-pr`: two hand-written merge subjects on main, `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `Merge pull request #2379 (R10-SENSOR-PAYLOAD)`, are read as 2401 and 2379 by `stamp.py` and `delivery_status.py` but as null by both `policy_lint.mjs` readers. This reproduces from main's history alone and this diff touches no file the lane reads (row files only), so the red is not this pull request's and is not fixed here; the repair is a grammar change in `policy_lint.mjs`, which is policy and owner-approved. Cheaper detector: none exists below the lane itself, which runs locally in under a second via `tools/policy/agreement_py.py` and `tools/policy/agreement.mjs`; a commit-msg check on merge subjects would be the earlier one, not built here.

## Forward-carry

none

## Friction

none

## Approval

Opened by the hpo-author App. No review seat: where `record_row.py --automerge-check` passes at the head, the approver App approves and the beat merges it at that head once its required checks pass (tvofi, 2026-10-07); where it refuses, the review stays manual. The HANDOVER updated-for line stays manual; this automation never writes it.

