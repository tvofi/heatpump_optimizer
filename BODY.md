The merge train's cross-check read a head's statusCheckRollup contexts one page (first 100) at a time; a head with more than one page was classed `unread` ("more than 100 contexts: not read whole"), so a green approved head was refused its re-add. `rollup_walk` now follows `endCursor` and judges all pages: one extra read per extra page, only on such heads. The QUEUED-context arm stays in round 11. Alternatives rejected: `gh api --paginate` (the cloud proxy refuses the Link URL, see `gh_read.read_pages`), and raising `first:` (GraphQL caps it at 100).

## Head

dbe75142ac7cc3e505aebfc9758102132a102804

## Mutation proof

Predicate mutated: `if not more or not cursor:` -> `if True:` in `rollup_walk` (the walk stops after page 1). `python3 tools/audit/seat/merge_train.py --self-test` goes red on `A5 platform: a required context on page 2 that is red reads RED, green reads GREEN ...`. Baseline behaviour (single-page loop, as origin/main read) gives the same red; restored, 0 failed.

## Null control

The arm's null: a one-page listing returns green and records exactly one read (`[None]`), as before; a walk past `gh_read.MAX_PAGES` and a later page at another head both read `unread`, never truncated. Unmodified tree: `platform_gate` returns `unread` on any `hasNextPage`.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test` at the head: 0 failed (657 checks, count printed by the instrument).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

none

## Friction

none

Disclosure: `tools/pr/prepr.sh` ran once refusing `closures failed while being recorded: tests/entities.py (exit 1)` (the cloud BASH_ENV trap); the rerun used `PREPR_SKIP_CLOSURES=1` and passed rc=0 for the same head. Closures are left to CI.
