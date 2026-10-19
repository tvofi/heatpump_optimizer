_Requested by **tvofi**_

The mechanical record beat (R9-FR-10): delivery rows for the merges that landed without one, generated from REST API facts by `tools/audit/seat/row` automation and written behind a guarded write set. Rows for merged pull requests #2379 (`5756f2b`), #2394 (`3d46d69`), #2396 (`106af95`), #2401 (`07a0940`), #2416 (`fd64a23`), #2418 (`86010e8`), and this pull request's own row #2420. The same commit upgrades the rows of the merged record pull requests #2407 (`3126b86`), #2412 (`003c373`) and #2413 (`be2d367`), from **open** to **merged**; the row of #2423 (`89e3385`) already reads merged on the autofix head. This pull request disposes itself as record-class (only row files change); a row whose subject no roster group claimed carries the neutral phrasing. The handover's updated-for line stays manual by design.

## Head

`328813ad5fb2055a07a4867c33f7cfc96d961168` merges the authored code head `c76799c5447a18fec355bce82ad084c807eb72a4` and then merges origin/main `fa5026c42` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`506655b17611e2a75dcc45b1c270ae9be501c587` merges the authored code head `c76799c5447a18fec355bce82ad084c807eb72a4` and then merges origin/main `89e33859a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`c76799c5447a18fec355bce82ad084c807eb72a4` (the row-repair commit on top of the autofix head `4ae96b9ccb59ce6ea24cefd3e6d56685009cde58`, itself on main at `89e3385`; computed against main at `89e3385`; a main that moved under the push is re-derived by the fetch/reset loop, never merged or forced)

## Figures

- delivery-status ledger at this head: `python3 tests/delivery_status.py` -- the instrument; re-derive at the head.
- each row file is exactly one line anchoring its own pull request number, never a table row: read back through the same anchor `policy_lint --record` applies.

## Mutation proof

n/a: record-only diff -- every file in this pull request is a `dev/programme/delivery/<N>.md` row file; there is no production, test or check code here to mutate.

## Null control

n/a: no quantified production claim; the one figure names its instrument and re-derives at the head.

## Red checks

- `delivery-status`: `DELIVERY STATUS OVERDUE -- 3 overdue`: #2413, #2412 and #2407 are merged record pull requests whose rows still read **open**, and `classify` does not count an open-anchored row over a landed merge as rowed. Fixed here: each row now names its merge SHA, and `python3 tests/delivery_status.py --check` prints OK, 0 overdue, at this head. Cheaper detector: the check that fired is already the cheapest, a sub-second local run; the status word is not reconciled when a row is written (`delivery-status-tracking.md`), so the standing cost is one row upgrade per merged record pull request, until the word is graded.
- `wave-script`: the agreement lane refused on `merge-subject-pr` at the earlier head, which predated main's fix. #2423 fixed it on main (one merge-subject grammar across the readers), and this head is replayed on top of that fix; the lane now prints AGREEMENT ok locally. The autofix head was already based on that fix. This diff touches only row files. Cheaper detector: `tools/policy/agreement_py.py --run`, under a second.

## Forward-carry

none

## Friction

none

## Approval

Opened by the hpo-author App. No review seat: where `record_row.py --automerge-check` passes at the head, the approver App approves and the beat merges it at that head once its required checks pass (tvofi, 2026-10-07); where it refuses, the review stays manual. The HANDOVER updated-for line stays manual; this automation never writes it.


