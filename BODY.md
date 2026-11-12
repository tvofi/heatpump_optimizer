Hotfix R10-HOTFIX-TRAIN-CONTEXT-PAGES: the merge train read only the first 100 rollup contexts, so a required context on a later page was never seen and a green approved head was refused as unread. `rollup_walk` follows `endCursor` and merges every page into one payload for `platform_gate`. This repair adds the self-test rows that kill the two mutants the handoff review (mutation-survivor at dbe75142ac7c) found surviving; no other change.

## Head

853c9f47ccb8704697c96afcce0d3916919acab0

## Mutation proof

Both survivors now fail the self-test (`python3 tools/audit/seat/merge_train.py --self-test`):
- rollup_walk per-page oid guard (`if commit.get("oid") != head:` made `if False and ...`): 2 checks go red (new row "a later page whose oid differs from the first page's is unread", plus the A5 page-cap row).
- Train fetch cursor argument (`(["-f", f"after={cursor}"] if cursor else [])` replaced by `[]`): 1 check goes red (new row "A5 serial: the train passes each page's endCursor on the next read", which serves page 2 only on `after=1`).
Survivors remaining in the diff mutant pass: none found. One hand mutant (`if merged is None and commit.get("oid") != head:`) crashes the self-test with a NameError (killed, not a survivor).

## Null control

The unmodified tree reads 660 checks, 0 failed. The new rows' nulls: the same two-page listing at one oid reads red from page 2; a one-page rollup is read once with no cursor and merges (`A5 serial null`).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
