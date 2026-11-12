Hotfix R10-HOTFIX-TRAIN-CONTEXT-PAGES: the merge train read only the first 100 rollup contexts, so a required context on a later page was never seen and a green approved head was refused as unread. `rollup_walk` follows `endCursor` and merges every page into one payload for `platform_gate`. This repair adds the self-test rows that kill the survivors the handoff reviews found (dbe75142ac7c, then 853c9f47ccb8: the page-merge node concatenation, the `endCursor` text and the `after:$after` text of `ROLLUP_Q`); no other change.

## Head

7090e74587bbebe2371d01be682b57b1512c9d93

## Mutation proof

Each fails the self-test (`python3 tools/audit/seat/merge_train.py --self-test`), measured at this head:
- rollup_walk oid guard (`if commit.get("oid") != head:` made `if False and ...`): 1 check red (the "later page whose oid differs" row).
- Train fetch cursor argument (`(["-f", f"after={cursor}"] if cursor else [])` replaced by `[]`): 1 check red ("A5 serial: the train passes each page's endCursor").
- M5, `have["nodes"] = list(ctx["nodes"])` (drops page 1's nodes): 1 check red (new row "the merge keeps page 1's nodes", a red gate or another required context on page 1 with a green gate rerun on page 2).
- M9, `pageInfo{hasNextPage endCursor}` made `pageInfo{hasNextPage}` in `ROLLUP_Q`: 1 check red (new row "the query the train sends asks for the page cursor...", which reads the query text the faked `gh api graphql` receives).
- M8, `contexts(first:100,after:$after)` made `contexts(first:100)` in `ROLLUP_Q` line only: 1 check red (same row). A sed over the whole file also rewrites the test's own literal and reads green; the mutant is the production line alone.
M6 and M10 are equivalent mutants (the changed return still carries hasNextPage true or no rollup, so `platform_gate` reads unread either way), per the review.

## Null control

The unmodified tree reads 662 checks, 0 failed. The new rows' nulls: the same two-page listing at one oid reads red from page 2; a one-page rollup is read once with no cursor and merges (`A5 serial null`); a red other-required context on page 2 reads red too (the page-merge row's control).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
