Tooling fix by owner request (tooling-freeze exception, owner, 2026-11-22T19:05Z): `tools/audit/seat/corpus_mirror.py`'s S3 `item batches` pass kept hitting GraphQL's rate limit. **Cause, by GitHub's documented cost formula** (now `formula_cost` in the file): one item of `ITEM_FIELDS` asks 308 requests (each comment's and each review's `userContentEdits(first:20)` is one request per parent node, 100 parents each), so the base's 50-item query costs **154 points**, not thousands. The base checked the budget only once per `gh_read.BATCH` (200) calls and otherwise kept only `MIN_GAP_S` (1 s) between calls, so about 13 queries take the 5000-point bucket under the 60 % shared floor, and about 32 spend it, all before the next budget read; the 32nd-or-so answer is `RATE_LIMITED` and the scan pauses.

## Summary

- **Paced by cost.** `ITEM_QUERY` asks `rateLimit{cost remaining limit resetAt}`; `Mirror.observe` keeps it (and pops it from the stored items). `Mirror.graphql_wait`, called from `_gate` for the `graphql` bucket only, holds the next query `c*3600/limit` s after a query of cost `c` (a token bucket spending at most the hourly limit an hour), and when `remaining - c` would go under the floor, sleeps until `resetAt`; a reset `RESET_WAIT_CAP_S` (3600 s) or more away raises `Paused` as before. The wait is the larger of that and `MIN_GAP_S`, one sleep.
- **30 items per query.** `GRAPHQL_BATCH` 50 -> 30: 92 points by `formula_cost`, under `QUERY_COST_CAP` (100); 32 items is 99 and 33 is 102. Fields and every `first:`/`last:` value are unchanged, so coverage and the `hasNextPage` truncation line are unchanged. The API's own cost per query is recorded in the cursor and printed by `cost` (last, max): the first real scan measures it.
- **Secondary limit.** The query is read with `-i`, classified by `gh_read.included_wait` (was `gh_wait`, which cannot see headers). A secondary-limit answer naming a `Retry-After` up to `SECONDARY_WAIT_CAP_S` (300 s) is slept out and the query asked once more; a longer one, a second one, or a spent primary bucket (even one naming a `Retry-After`) pauses at the cursor as before.
- **Gate.** `_gate` judges a `gh api -i graphql` call as the same call without `-i` (`-i` adds headers to the output, nothing to the request); a mutation or search is still refused, with or without `-i`.
- **Partition.** A batch key of another partition kept in the cursor (the owner's paused 50-item keys, or a last batch since grown) is dropped before the pass, so `universe` and `examined` count the current batches, and the item file of each such key (`graphql/items/<key>.json`, any stem that is no current key) is removed with it; those items are read once more under the new keys, so the directory holds each item once.
- REST paths unchanged; `gh_read.py` unchanged.

## Head

`f737eed72009e0ff4bf1f4126e929c5430b39684`, eight commits on `origin/main` `1207ee13b0` plus main merged at `0812e8b2e4`. Read the diff three-dot. Round 3 (repair of the `mutation-vacuous` block at `0812e8b2e4`, verdict `0a4ce66fa9`): one commit, `git diff 0812e8b2e4 f737eed720`.

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

At the head, `python3 -I tools/audit/seat/corpus_mirror.py --self-test` runs the in-tree `MUTANTS` table (each mutant edits a copy above the self-test mark and must turn its named case FAIL): `corpus_mirror self-test: ok (with mutants)`, 72 `ok   mutant killed` lines, 23 of them new: `graphql paced` (the `_gate` call removed), `pace by cost` (next = now), `token bucket waited` (returns 0), `rateLimit read`, `rateLimit not stored`, `floor before a query`, `expected cost` (remaining alone), `sleep to reset` (always pause), `reset past an hour` (never pause), `secondary retried`, `secondary once` (retry while secondary), `secondary cap`, `secondary only` (any Retry-After), `query read with -i`, `partition`, `cost cap` (batch 50), `formula per parent`, `formula nesting`, and round 2's five below; plus `gap` and `reads only` re-anchored on the restructured `_gate` lines.

Diff mutants (fixer.md step 2, `prepr.sh` step 6d's drawer run directly): `python3 -I tools/audit/seat/mutant_run.py --diff 1207ee13b0...HEAD --cmd "python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants" --max-mutants 40 --report-only --in-place`. At the second commit 18 of the 40 survived (the four constants, the formula's start, parent index and floor of 1, `epoch`'s `return None`, the first-call gap, `graphql_wait`'s 0.0 returns and both boundaries, `observe`'s early returns and its limit guard). The third commit adds direct cases for each (`cost: the formula counts each connection once per parent node...`, `graphql observe: ...`, `graphql wait: ...`, `graphql secondary: a Retry-After of 300 s is waited, 301 s is not...`, the first call's no-sleep, and value pins `(92, 100)` for the chosen batch's cost and the cap); the same command then printed no `SURVIVED` line over the same 40 mutants (`--list` names 40, the last at `observe`'s guard). That run did not reach the defects below: a killed operator mutant is no proof that each changed line's own undo is killed, and the third commit's subject ("the formula's rounding, each pinned") was wrong.

**Round 2 (repair of the `mutation-vacuous` block at `273e5ece99`).** The reviewer's three survivors and the stale partition files, each now a named case, failing first at `841d0155c8` (tests only). At that commit `python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants` printed exit 1 and exactly one FAIL, the one with no fix yet:

```
FAIL partition files: an item file of another GRAPHQL_BATCH is removed, so the directory holds each item once, under the current keys
```

Each reviewer mutant, applied by hand to a copy of that commit's file and driven by the same command (scratch driver: the needle must occur once, the copy beside `gh_read.py`), printed exit 1 with its killing case beside that one:

- `formula_cost` `round(requests / 100)` -> `int(requests / 100)`: `FAIL cost: the formula counts each connection once per parent node, rounds the hundreds and is at least 1` (the case adds `query{a(first:150){b(first:1){x}}}`, 151 requests: 2 by rounding, 1 by flooring, read from `formula_cost` itself).
- `observe` `seen["max"] = max(seen["max"], cost)` -> `= cost`: `FAIL graphql cost: the cursor keeps the last cost answered and the largest, and 'cost' prints both` (costs 46, 92, 30 observed; the cursor must hold `{"last": 30, "max": 92}` and `main(["cost", ...])` must print it).
- `query`'s `attempt` 2xx range dropped: `FAIL graphql status: an answer exiting 0 with a non-2xx status is no answer: its body is never stored, the query is asked again` (the stub answers exit 0 with an HTTP 502 whose body is valid GraphQL data marked `i999`). The guard is kept and pinned rather than dropped: it costs one comparison, and the guarantee no longer rests on `gh`'s exit code.

Fix (`4e0eac2e3c`): `s3` unlinks every `graphql/items/*.json` whose stem is no current batch key, beside the cursor key's removal. Stub fidelity (`dada3d3808`): the stub answered a `rateLimit` whether or not the query asked one, so restoring the base `ITEM_QUERY` survived; it now answers one only when the query document holds `rateLimit{`, as GitHub does. New in-tree mutants, each `ok   mutant killed` at the head: `partition files` (the unlink -> `pass`), `formula rounds` (round -> int), `largest cost kept` (max -> last), `2xx only` (the range dropped), `rateLimit asked` (the base `ITEM_QUERY`).

Line reverts (each production line the PR modifies, restored to its base text: the reviewer's undo): 9 mutants, `python3 -I tools/audit/seat/mutant_run.py --spec <spec> --cmd "python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants" --in-place` at the head printed `KILLED` for all 9 and `SURVIVED NULL` (its null control): `corpus_mirror.py:124:LINE_REVERT` (`ITEM_QUERY`), `corpus_mirror.py:436:LINE_REVERT` (the bare `return json.loads(...)`), `revert batch 50`, `revert gate is_query(argv)`, `revert gap block`, `revert query argv -i`, `revert attempt status`, `revert retry gh_wait`, `revert cost print`. The two `corpus_mirror.py:` entries are `vacuous_probe.py --rules ABC --revert-path tools/audit/seat/ --spec-out` output; the other seven are written by hand for the modified production lines the probe pairs with no one-for-one `+` line. The probe's five other pairs (`corpus_mirror.py:893`, `:894`, `:1030`, `:1050`, `:1052` at `4e0eac2e3c`) are self-test lines below `SELF_TEST_MARK` (the stub and case bodies), not production: their undo edits a test, not the code under it. Before `dada3d3808` the same spec printed `SURVIVED corpus_mirror.py:124:LINE_REVERT`, the stub defect above.

Every diff mutant on a production line, not the first 40: `prepr.sh`'s drawer stops at 40, which ends at `observe`'s guard and never reaches `secondary_wait`, `query`, `s3` or `main`. A scratch driver (each mutant `mutant_run.diff_mutants(repo, "1207ee13b0...HEAD")` draws on a line above `SELF_TEST_MARK`, operators and `STMT_DEL` both, run by `--self-test --no-mutants` in its own copy beside `gh_read.py`; the unedited file first, its null control) found two survivors at `dada3d3808`, both equivalent: `observe`'s initial `{"last": 0, ...}` (`last` is assigned on the next line) and `secondary_wait`'s trailing `return None` (falling off the end returns None). Both are removed at the source in `a36a6b14a5`: the cursor's figure starts empty and `max` reads `seen.get("max", cost)`, and `secondary_wait` is one conditional expression. At the head the driver printed `NULL (unedited) rc=0`, then `done: 86 mutants, 0 survived`. `mutant_run.py --diff 1207ee13b0...HEAD --max-mutants 40 --report-only --in-place` (the drawer's own first 40) printed no `SURVIVED` line at `dada3d3808`. The self-test lines below the mark draw the rest of `--list` (the stub's constants, the case bodies); a mutant there edits a test, not the code it pins, and none was run as a kill claim.

`vacuous_probe.py --rules AB --repo . --head HEAD --base origin/main --body <this body>` printed `VACUOUS-PROBE: PASS -- 0 changed production file(s); rule A 0, B 0, C 0`: rules A and B read `custom_components/` only, so they pass here by reach, not by content; rule C over `tools/audit/seat/` is the line-revert run above.

**Round 3 (repair of the `mutation-vacuous` block at `0812e8b2e4`).** The reviewer's two survivors, each now killed. New case `partition keep: a pass resumed under the same partition keeps the file of every batch answered before the pause, so each batch holds its file` (on the `ghour` pause-then-resume run: the 3 files held at the pause are byte-identical after the resume, and the directory's stems equal the cursor's batch keys). `observe`'s max is rewritten `max(seen["max"], cost) if "max" in seen else cost`, so the first cost has no default figure to mutate, and `graphql cost` also observes `92, 30` (the first answer the largest) and must hold `{"last": 30, "max": 92}`. A scratch driver applied each mutant to the file at `f737eed720` and ran `python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants`:

```
null control (unmutated): rc=0 fails=0
reviewer 'unlink all': rc=1 fails=1
    FAIL partition keep: a pass resumed under the same partition keeps the file of every batch answered before the pause, so each batch holds its file
reviewer 'max default 0' (re-cut needle: first cost -> 0): rc=1 fails=1
    FAIL graphql cost: the cursor keeps the last cost answered and the largest, and 'cost' prints both
reviewer 'unlink none glob': rc=1 fails=1
    FAIL partition files: an item file of another GRAPHQL_BATCH is removed, so the directory holds each item once, under the current keys
```

New in-tree mutants: `partition keeps current` (`if stale.stem not in batches:` -> `if True:`) and `first cost is a max` (`else cost` -> `else 0`); `largest cost kept` re-anchored on the rewritten line.

## Null control

- `graphql pace null: a query of cost 1 waits only the gap`: at cost 1 (0.72 s by the rule) every GraphQL call is preceded by exactly `MIN_GAP_S`, and the base's `budget ... gap is kept between calls` case (`set(sleeps) == {MIN_GAP_S}`) still passes unedited.
- `graphql secondary: a Retry-After past the cap, or a spent primary bucket, pauses at once without sleeping` passes at the base too: the pause paths the fix keeps are the base's.
- `formula_cost` against GitHub's documented worked example (repositories 100 x issues 50 x labels 60): 5101 requests, 51 points; the `formula per parent` and `formula nesting` mutants each break it.

## Figures

- Cost per query, base (50 items) and head (30 items), by GitHub's formula: `python3 -I -c "import sys; sys.path.insert(0, 'tools/audit/seat'); import corpus_mirror as m; d = lambda n: m.ITEM_QUERY % chr(10).join(m.ITEM_FIELDS % (k, k) for k in range(1, n + 1)); print([(n, m.formula_cost(d(n))) for n in (1, 30, 32, 33, 50)])"` printed `[(1, 3), (30, 92), (32, 99), (33, 102), (50, 154)]`. `ITEM_FIELDS` is byte-identical to the base's (`git diff 1207ee13b0...HEAD -- tools/audit/seat/corpus_mirror.py | grep -c '^[-+]ITEM_FIELDS'` printed `0`), so the base query's 154 is the same formula on the same text.
- Base pacing: 13 queries cross the 60 % floor (2000 / 154, rounded up) and 32 spend 5000 (5000 / 154), against one budget read per 200 calls (`gh_read.BATCH`).
- Issue count (issues plus pull requests): `gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:issue' --jq .total_count` printed `1082`, the same with `is:pull-request` `2785`: 3867 items, 129 queries of 30 (`ceil(3867/30)`), 11868 points at 92.
- Expected S3 GraphQL wall time at the head, assuming each hour's bucket starts full at 5000 and nothing else spends it, by `graphql_wait`'s rule (query while `remaining - 92 >= floor * 5000`): shared token (floor 0.60) 21 queries a window (23 min at the 66.24 s pace, then a sleep to reset), so 129 queries take six windows plus 3 queries, about 6.1 h; `--own-identity` (floor 0.10) 48 queries a window (53 min), two windows plus 33 queries, about 2.6 h; the pace alone bounds it below at 129 x 66.24 s = 2.37 h. Query latency adds to each gap; a first bucket below full shortens the first window. Arithmetic over the figures above, no API call.
- `python3 -I tools/audit/seat/corpus_mirror.py --self-test`: `corpus_mirror self-test: ok (with mutants)`, 138 `ok` lines of which 74 are `ok   mutant killed`, no `FAIL` (`grep -c '^ok'` and `grep -c '^ok   mutant killed'` over its output; at `0812e8b2e4` the same counts were 135 and 72, at `1cfbe54f94` 127 and 67).
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff 1207ee13b0 --workdir "$D"` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

fixer.md: unenforced: step 2 says `prepr.sh` draws only the first 40 mutants of added `.py` lines, and `mutant_run.py --diff` orders every line operator by line before any `STMT_DEL`, with a same-file self-test's lines in that order, so on this diff the 40 never reached `secondary_wait`, `query`, `s3`, `main` or any statement deletion, where two of the block's three survivors sat (the third, round -> int, is no operator the drawer has); an overlay driver ran every production-line mutant (Mutation proof, round 2). Carry: dismissed: instrument proposal P-R11-MUTANT-DIFF-ORDER, in the round's proposals register for its round-end instrument triage
