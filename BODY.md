Tooling fix by owner request (tooling-freeze exception, owner, 2026-11-22T19:05Z): `tools/audit/seat/corpus_mirror.py`'s S3 `item batches` pass kept hitting GraphQL's rate limit. **Cause, by GitHub's documented cost formula** (now `formula_cost` in the file): one item of `ITEM_FIELDS` asks 308 requests (each comment's and each review's `userContentEdits(first:20)` is one request per parent node, 100 parents each), so the base's 50-item query costs **154 points**, not thousands. The base checked the budget only once per `gh_read.BATCH` (200) calls and otherwise kept only `MIN_GAP_S` (1 s) between calls, so about 13 queries take the 5000-point bucket under the 60 % shared floor, and about 32 spend it, all before the next budget read; the 32nd-or-so answer is `RATE_LIMITED` and the scan pauses.

## Summary

- **Paced by cost.** `ITEM_QUERY` asks `rateLimit{cost remaining limit resetAt}`; `Mirror.observe` keeps it (and pops it from the stored items). `Mirror.graphql_wait`, called from `_gate` for the `graphql` bucket only, holds the next query `c*3600/limit` s after a query of cost `c` (a token bucket spending at most the hourly limit an hour), and when `remaining - c` would go under the floor, sleeps until `resetAt`; a reset `RESET_WAIT_CAP_S` (3600 s) or more away raises `Paused` as before. The wait is the larger of that and `MIN_GAP_S`, one sleep.
- **30 items per query.** `GRAPHQL_BATCH` 50 -> 30: 92 points by `formula_cost`, under `QUERY_COST_CAP` (100); 32 items is 99 and 33 is 102. Fields and every `first:`/`last:` value are unchanged, so coverage and the `hasNextPage` truncation line are unchanged. The API's own cost per query is recorded in the cursor and printed by `cost` (last, max): the first real scan measures it.
- **Secondary limit.** The query is read with `-i`, classified by `gh_read.included_wait` (was `gh_wait`, which cannot see headers). A secondary-limit answer naming a `Retry-After` up to `SECONDARY_WAIT_CAP_S` (300 s) is slept out and the query asked once more; a longer one, a second one, or a spent primary bucket (even one naming a `Retry-After`) pauses at the cursor as before.
- **Gate.** `_gate` judges a `gh api -i graphql` call as the same call without `-i` (`-i` adds headers to the output, nothing to the request); a mutation or search is still refused, with or without `-i`.
- **Partition.** A batch key of another partition kept in the cursor (the owner's paused 50-item keys, or a last batch since grown) is dropped before the pass, so `universe` and `examined` count the current batches; those items are read once more under the new keys.
- REST paths unchanged; `gh_read.py` unchanged.

## Head

`1cfbe54f944b6c3db6335b69bf5c102f2efcf8ff`, three commits on `origin/main` `1207ee13b0` (measured 2026-11-22T19:24Z). Read the diff three-dot.

## Mutation proof

Failing test first (`87d73018b9`, tests only), at that commit `python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants` printed these FAIL lines and exit 1:

```
FAIL graphql pace: after a query of cost c each GraphQL call waits c*3600/limit, proportional to the cost
FAIL graphql pace: the rateLimit read for pacing is not stored with the items
FAIL graphql floor: a query the last cost would take under the floor sleeps until resetAt (under an hour), and the scan completes
FAIL graphql floor: a reset an hour or more away pauses at the cursor instead of sleeping, and the run after it completes
FAIL graphql secondary: a secondary limit naming a 60 s Retry-After is waited out and the query retried once, and the scan completes
FAIL graphql secondary: a second secondary answer after the one retry pauses at the cursor
FAIL cost: GitHub's documented example costs 51 by the formula, and one item query of GRAPHQL_BATCH items stays under QUERY_COST_CAP
FAIL partition: a batch key of another GRAPHQL_BATCH kept in the cursor is no unit of this pass: universe and examined count the current batches
FAIL gate null: a query read with its headers (-i) is admitted
```

At the head, `python3 -I tools/audit/seat/corpus_mirror.py --self-test` runs the in-tree `MUTANTS` table (each mutant edits a copy above the self-test mark and must turn its named case FAIL): `corpus_mirror self-test: ok (with mutants)`, 67 `ok   mutant killed` lines, 18 of them new: `graphql paced` (the `_gate` call removed), `pace by cost` (next = now), `token bucket waited` (returns 0), `rateLimit read`, `rateLimit not stored`, `floor before a query`, `expected cost` (remaining alone), `sleep to reset` (always pause), `reset past an hour` (never pause), `secondary retried`, `secondary once` (retry while secondary), `secondary cap`, `secondary only` (any Retry-After), `query read with -i`, `partition`, `cost cap` (batch 50), `formula per parent`, `formula nesting`; plus `gap` and `reads only` re-anchored on the restructured `_gate` lines.

Diff mutants (fixer.md step 2, `prepr.sh` step 6d's drawer run directly): `python3 -I tools/audit/seat/mutant_run.py --diff 1207ee13b0...HEAD --cmd "python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants" --max-mutants 40 --report-only --in-place`. At the second commit 18 of the 40 survived (the four constants, the formula's start, parent index and floor of 1, `epoch`'s `return None`, the first-call gap, `graphql_wait`'s 0.0 returns and both boundaries, `observe`'s early returns and its limit guard). The third commit adds direct cases for each (`cost: the formula counts each connection once per parent node...`, `graphql observe: ...`, `graphql wait: ...`, `graphql secondary: a Retry-After of 300 s is waited, 301 s is not...`, the first call's no-sleep, and value pins `(92, 100)` for the chosen batch's cost and the cap); the same command then printed no `SURVIVED` line over the same 40 mutants (`--list` names 40, the last at `observe`'s guard).

## Null control

- `graphql pace null: a query of cost 1 waits only the gap`: at cost 1 (0.72 s by the rule) every GraphQL call is preceded by exactly `MIN_GAP_S`, and the base's `budget ... gap is kept between calls` case (`set(sleeps) == {MIN_GAP_S}`) still passes unedited.
- `graphql secondary: a Retry-After past the cap, or a spent primary bucket, pauses at once without sleeping` passes at the base too: the pause paths the fix keeps are the base's.
- `formula_cost` against GitHub's documented worked example (repositories 100 x issues 50 x labels 60): 5101 requests, 51 points; the `formula per parent` and `formula nesting` mutants each break it.

## Figures

- Cost per query, base (50 items) and head (30 items), by GitHub's formula: `python3 -I -c "import sys; sys.path.insert(0, 'tools/audit/seat'); import corpus_mirror as m; d = lambda n: m.ITEM_QUERY % chr(10).join(m.ITEM_FIELDS % (k, k) for k in range(1, n + 1)); print([(n, m.formula_cost(d(n))) for n in (1, 30, 32, 33, 50)])"` printed `[(1, 3), (30, 92), (32, 99), (33, 102), (50, 154)]`. `ITEM_FIELDS` is byte-identical to the base's (`git diff 1207ee13b0...HEAD -- tools/audit/seat/corpus_mirror.py | grep -c '^[-+]ITEM_FIELDS'` printed `0`), so the base query's 154 is the same formula on the same text.
- Base pacing: 13 queries cross the 60 % floor (2000 / 154, rounded up) and 32 spend 5000 (5000 / 154), against one budget read per 200 calls (`gh_read.BATCH`).
- Issue count (issues plus pull requests): `gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:issue' --jq .total_count` printed `1082`, the same with `is:pull-request` `2785`: 3867 items, 129 queries of 30 (`ceil(3867/30)`), 11868 points at 92.
- Expected S3 GraphQL wall time at the head, assuming each hour's bucket starts full at 5000 and nothing else spends it, by `graphql_wait`'s rule (query while `remaining - 92 >= floor * 5000`): shared token (floor 0.60) 21 queries a window (23 min at the 66.24 s pace, then a sleep to reset), so 129 queries take six windows plus 3 queries, about 6.1 h; `--own-identity` (floor 0.10) 48 queries a window (53 min), two windows plus 33 queries, about 2.6 h; the pace alone bounds it below at 129 x 66.24 s = 2.37 h. Query latency adds to each gap; a first bucket below full shortens the first window. Arithmetic over the figures above, no API call.
- `python3 -I tools/audit/seat/corpus_mirror.py --self-test`: `corpus_mirror self-test: ok (with mutants)`, 127 `ok` lines of which 67 are `ok   mutant killed`, no `FAIL`.
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff 1207ee13b0 --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
