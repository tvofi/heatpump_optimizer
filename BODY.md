R11-PRE-ROUND-METRICS part 3: card E11-N-P744-SCOPE (eval/r11 `dev/audit/yardstick/round11/EVALUATION.json`, accepted; tvofi 2026-11-15 ruled that the card gates the finders whole). Builds the two reads of decision 0018 section 2 the card names and parts 1 and 2 leave out, both by name in `tools/audit/seat/round_metrics.py` (`report`, and `produce` for the inputs):

- `closure_slip` (layer 2): over the plan pages on the round's state ref `handoff/audit-r<N>-plan` after the round's register (the commit that first adds `dev/audit/rounds/round<N>/JUDGE.json` to main), inside the window, the days the forecast closure moved later between consecutive pages, over the days between the first and the last page. The forecast is the `closure` that `plan_page.py` prints from `plan.json`'s `summary.closure` in the page's slots note. Shown beside it: the net move, pages with no forecast (an UNAVAILABLE page), `thresholds.closure_slip_ceiling` from `dev/audit/config/objective.json` (null means undecided, per 0018), days from round start to closure (the `vN.0.0` tag, or the newest forecast while the round is open) and the round's groups at stage `deferred`. `produce` caches the history in `plans.json` for rounds N-1 and N, scanning forward from the cached tip, so the record outlives the state ref's deletion at branch cleanup. No `PLAN.json` sits on either state ref, so the rendered `PLAN.html` is what it reads.
- `unexamined` (layer 1): the window's production merges (machinery_ratchet class) that are not an ancestor of any finder baseline the round recorded, meaning any `"baseline_sha"` under `dev/audit/rounds/round<N>/` on `origin/main`. The denominator is the window's production merges. The unexamined merges are then broken down by roster group kind, which `produce` writes as `groups.json` from every `wave-r<N>` roster.

Design choice, stated (fixer step 11): roster group kinds cannot decide whether a merge was examined. 0018 counts "a fix's own diff" as unexamined, and a fix group's kind is the same before and after a catch-up pass. So examination is decided by git ancestry from the recorded finder baselines, and the kinds give the breakdown 0018's parenthesis lists (feature, outside change, fix). A baseline prefix that resolves to no commit, or a round with no recorded baseline, prints `unread` and never a partial value.

Both reads are a round's read. Under `--since`, each prints `unread (a round's read: --round names the round)`. `scorecard.py`, `loop_ledger.py` and `roster_lib.py` are untouched (part 2, #3657).

Alternatives considered: (1) reading the plan history live from the state ref in `report`. Rejected because the ref is deleted at cleanup, which would leave a closed round unread forever. (2) Adding `examined` and `kind` columns to `merges.tsv`. Rejected because `scorecard.py` (part 2's file) reads that file. (3) Counting net moves only. Rejected because 0018 says "moved later", so an earlier move pays nothing back. The net move is still printed beside.

## Carries

This part's scope comes from the dispatch brief: the two reads `closure_slip` and `unexamined` (card E11-N-P744-SCOPE). Here is each roster carry of R11-PRE-ROUND-METRICS (0-based, `handoff/audit-r10-roster`) and what this part does with it:
- Carry 0 and Carry 2 (build to 0018 section 2's definitions, enumerator in `.github/CODEOWNERS`, return an unmeetable definition as a card): built here for both reads, as described above. `/tools/audit/seat/round_metrics.py` is already in `.github/CODEOWNERS`. No definition went unmet, so there is no card.
- Carry 1 and Carry 3 (recall, overlap, `product_green`, the `lead_time` clock, runner seconds): not in this part. Recall and overlap are part 1 (#3612, merged). `product_green`, `lead_time` and `runner_s` are already in `round_metrics.py` on main (#3644). This part builds none of them. Carry: dismissed: built on main by #3612 and #3644
- Carry 4 (the CI-attempt alarm): not in this part. The `ci-attempt` row is in `tools/audit/seat/beat_jobs.py` on main. Carry: dismissed: built on main in beat_jobs.py
- Carry 5 and Carry 6 (convergence records: found-by, owner, the injected bug's cause, denominators, an examining pass over a late merge, a re-report naming its fix): not built here. `unexamined` counts any recorded finder baseline under `dev/audit/rounds/round<N>/` as examining, so an examining pass over a late merge is read once its report records a `baseline_sha`. The rest is outside this part's brief.
- Carry 7 (loop-study L1, the loop ledger): part 2 (#3657, open: `loop_ledger.py`). Not touched here.
- Carry 8 (process card P7, `caused_by` and `found_by`): part 2 (#3657). Not touched here.

## Head

42059551febb1e21c006fa1a2d64b47231c65064, measured on origin/main 4ce615b5e6c3fe2cfdf05aae9fd81e8af896b3fc at 2026-11-16T06:33Z.

## Mutation proof

`python3 -I tools/audit/seat/round_metrics.py --self-test` runs one mutant per predicate on a temp copy, and each mutant must turn its named case `FAIL`. Here are the 16 new mutants with the case that kills each:
- `slip later only`, `slip register`, `slip blank page`, `slip ceiling`, `slip deferred round`: killed by `closure_slip: later moves only, over the plan-history days after the register`
- `slip window`: killed by `closure_slip: the window cuts the history`
- `slip two pages`: killed by `closure_slip: one page, no register, no history and no round are unread`
- `slip closed round`: killed by `closure_slip: a closed round closes at its tag; a null ceiling is undecided`
- `unexamined ancestry`, `unexamined production`, `unexamined kind`: killed by `unexamined: production merges no finder baseline contains, by roster group kind`
- `unexamined partial`: killed by `unexamined: a baseline that resolves to no commit is unread, never partial`
- `unexamined none`: killed by `unexamined: a round with no baseline, no round, no merges and no production merge are unread`
- `plan register first add`: killed by `plan history: one forecast per page commit, an UNAVAILABLE page null, the register the first add`
- `plan incremental`: killed by `plan history: an incremental scan from the cached tip keeps the cache`
- `plan cache on a gone ref`: killed by `plan history: a round with no state ref keeps its cached history`

A case that raises reads `False` (`chk`), so a mutant that crashes a read is still reported as a killed case and cannot pass as a crash. The existing `tokens production` needle matched twice once the new production filter landed; it was lengthened to stay unique, and that mutant is still killed.

## Null control

An empty input directory under `--round` prints all 8 reads `unread (...)`, including both new ones (case `null: an empty input directory prints every read unread`). At the merge base, `report` prints neither line. On the real tree, `unexamined` for round 11 prints `unread (no finder baseline recorded under dev/audit/rounds/round11/ on origin/main)`: round 11's finders have not yet run.

## Figures

- self-test: `python3 -I tools/audit/seat/round_metrics.py --self-test` ends `round_metrics self-test: ok (with mutants)`, with every case and all 39 mutants `ok` (23 existing, 16 new).
- structure ratchet: `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.
- architecture score: `python3 tools/audit/archscore/score.py --diff 4ce615b5e6c3fe2cfdf05aae9fd81e8af896b3fc` prints `Architecture score: dS +0.0000 NULL`.
- scope: `python3 tests/closure.py select --diff 4ce615b5e6c3fe2cfdf05aae9fd81e8af896b3fc --workdir <dir>` prints `MODE: SCOPED -- 0 script(s) run`. CI runs `instrument-self-tests`, which is the authority.
- round 10 through `report --round 10` is `round 10 unread`: `git tag -l v9.0.0` prints nothing, so the window rule of the existing instrument has no opening tag.

<!-- figure-block: scope-line mb=4ce615b5e6c3fe2cfdf05aae9fd81e8af896b3fc head=42059551febb1e21c006fa1a2d64b47231c65064 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
