R11-PRE-ROUND-METRICS part 3: card E11-N-P744-SCOPE (eval/r11 `dev/audit/yardstick/round11/EVALUATION.json`, accepted; tvofi 2026-11-15 ruled that the card gates the finders whole). Builds the two reads of decision 0018 section 2 the card names and parts 1 and 2 leave out, both by name in `tools/audit/seat/round_metrics.py` (`report`, and `produce` for the inputs):

- `closure_slip` (layer 2): over the plan pages on the round's state ref `handoff/audit-r<N>-plan` after the round's register (the commit that first adds `dev/audit/rounds/round<N>/JUDGE.json` to main), inside the window, sampled once a day (each day's last page with a forecast, days counted from the register: `SLIP_SAMPLE_S`), the days the forecast closure moved later between consecutive samples, over the days between the first and the last sample. The forecast is the `closure` that `plan_page.py` prints from `plan.json`'s `summary.closure` in the page's slots note. Shown beside it: the daily samples and the pages read, the net move, pages with no forecast (an UNAVAILABLE page), `thresholds.closure_slip_ceiling` from `dev/audit/config/objective.json` (null means undecided, per 0018), days from round start to closure (the `vN.0.0` tag, or the newest forecast while the round is open) and the round's groups at stage `deferred`. `produce` caches the history in `plans.json` for rounds N-1 and N, scanning forward from the cached tip, so the record outlives the state ref's deletion at branch cleanup. No `PLAN.json` sits on either state ref, so the rendered `PLAN.html` is what it reads.
- `unexamined` (layer 1): the window's production merges (machinery_ratchet class) that are not an ancestor of any finder baseline the round recorded, meaning any `"baseline_sha"` under `dev/audit/rounds/round<N>/` on `origin/main`. The denominator is the window's production merges. The unexamined merges are then broken down by roster group kind, which `produce` writes as `groups.json` from every `wave-r<N>` roster.

Design choice, stated (fixer step 11): roster group kinds cannot decide whether a merge was examined. 0018 counts "a fix's own diff" as unexamined, and a fix group's kind is the same before and after a catch-up pass. So examination is decided by git ancestry from the recorded finder baselines, and the kinds give the breakdown 0018's parenthesis lists (feature, outside change, fix). A baseline prefix that resolves to no commit, or a round with no recorded baseline, prints `unread` and never a partial value.

Both reads are a round's read. Under `--since`, each prints `unread (a round's read: --round names the round)`. `scorecard.py`, `loop_ledger.py` and `roster_lib.py` are untouched (part 2, #3657).

Alternatives considered: (1) reading the plan history live from the state ref in `report`. Rejected because the ref is deleted at cleanup, which would leave a closed round unread forever. (2) Adding `examined` and `kind` columns to `merges.tsv`. Rejected because `scorecard.py` (part 2's file) reads that file. (3) Counting net moves only. Rejected because 0018 says "moved later", so an earlier move pays nothing back. The net move is still printed beside.

## Repair (review round 1, verdict 8585b8959c73555c5c89e072d4bdf86317fd2c2e)

The block: nine mutants of the production half that feeds the two reads survived. Repairs:

1. A producer case (`producer_cases`) runs `produce` over the fixture repository, using the API half's fake paginator. The fixture has a `wave-r2` roster carrying `kind` and `resume.stage` (plus an entry with no `group` key) and state refs `handoff/audit-r1-plan` and `handoff/audit-r2-plan`, and the open round is 2. The case asserts `groups.json` and `plans.json` field by field from the producer's own output: `producer: groups.json carries each roster group's kind, resume.stage and round` and `producer: plans.json caches rounds N-1 and N from their state refs`.
2. `main(["report", "--round", "2", ...])` runs over the producer's output, with an `objective.json` whose ceiling is 0.5 and then null. Round 2 has two forecast pages a day apart after its register, so each run reaches past the slip read (`report --round: a set ceiling is read from objective.json's value`, `report --round: a null ceiling is undecided`). The test pins `main`'s clock (`m.time`) to T0 + 40 days, because the fixture's stamps lie after the real clock.
3. A branch `side` is checked out as HEAD, so origin/main differs from HEAD. It drops round 2's `LEADS.json` (its one baseline) and first adds round 3's `JUDGE.json`. Two cases assert that each read keeps origin/main's answer, and each first asserts its own precondition, that HEAD really differs: `unexamined: the baselines are origin/main's, not the checkout's` and `plan history: a register first added on a branch is no register`.
4. Each new predicate is in `MUTANTS`, and the reviewer's specs ran unchanged (see Mutation proof).
5. Disclosure, as a fixed cadence. Summing the later moves of every page made `closure_slip` a function of how often the plan page is committed. On round 10's history (ev/cadence.txt) the reviewer read 2.57, 1.52 and 1.22 days per day at three cadences. Only printing the cadence beside the read would leave two rounds with different commit habits unable to be compared. So the read now takes one sample a day, each day's last page with a forecast, with days counted from the register so the buckets are fixed per round. It prints `<S> daily samples of <P> pages` beside the read. A day is the read's own unit (days per day). A coarser bucket stays fully filled for any round whose page is committed at least daily, and round 10's 564 pages over 13.89 sampled days are well above that. The instrument page and the module docstring state this. Fewer than two daily samples read `unread`.

## Repair (review round 2, verdict 58207cfac200f8d6e0dec7b956bc8a5fc73eeefd)

The block: mutant `net-all-pages` survived. It puts the all-pages net (`hist[-1][1] - hist[0][1]`) back in `slip_line` in place of the daily net, and the two differ whenever the first sampled day holds more than one page with different forecasts.

Decision: the net is over the daily samples, the same samples as the slope (the last sample's forecast less the first's), so the first day's earlier pages do not enter it. That keeps every figure on the line at one cadence. The repair, in one commit:

1. A case `closure_slip: the net move is over the daily samples, the first day's last page to the last sample`, on the verdict's own history `[reg: +10 d, reg+0.5 d: +12 d, reg+1 d+1 s: +13 d]`, asserts `2 daily samples of 3 pages; net +1.00 days;` (the all-pages form prints `net +3.00 days`).
2. The in-file mutant `slip net daily` (`{(daily[-1][1] - daily[0][1]) / DAY_S:+.2f}` to the `hist` form), killed by that case.
3. The module docstring and `tools/audit/seat/instruments/round_metrics.py.md` now say what the net move is over: the last daily sample's forecast less the first's.

No other change.

## Head

`a527be6f1950c241a2d1b44f6c7f2a0aeeafd8dd`, one commit on the reviewed head `1f6ea62fd0345ac0759997621fffe315ea11b139`, measured on origin/main `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so there was no merge.

prepr: passed rc=0 at a527be6f1950c241a2d1b44f6c7f2a0aeeafd8dd

## Mutation proof

Round 2 (this repair). The reviewer's `evidence/spec-r2.json` ran unchanged from the verdict commit, and round 1's `evidence/spec1.json` and `evidence/spec2.json` (verdict commit's parent) ran again, each with `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'python3 -I tools/audit/seat/round_metrics.py --self-test --no-mutants'` (default `--copy-tree`) at `a527be6f1950c241a2d1b44f6c7f2a0aeeafd8dd`:
- Before, at `1f6ea62fd0345ac0759997621fffe315ea11b139` (the verdict's `evidence/mutant_run-spec-r2.txt`): `SURVIVED net-all-pages`.
- After, `spec-r2.json`: `SURVIVED NULL`; `KILLED` for every other row: ceiling-proposed-key, produce-same-round, groups-round-open, groups-stage-wrong, groups-kind-wrong, groups-write-elsewhere, plans-write-elsewhere, baselines-all, register-head, sample-half-day, sample-epoch-days, sample-first-of-day, span-all-pages, later-all-pages, **net-all-pages**, pages-count-hist.
- After, `spec1.json`: `SURVIVED NULL`; `KILLED` ceiling-value-key, produce-prior-round, groups-json-round, groups-json-stage, baselines-ref, register-ref, newest-from-window, unexamined-window, closure-seconds, plan-sort.
- After, `spec2.json`: `SURVIVED NULL`; `KILLED` groups-json-kind, plans-json-write, groups-json-write.

Failing case first: the new case, run against a copy of this head's `round_metrics.py` with the `net-all-pages` edit applied, prints `FAIL closure_slip: the net move is over the daily samples, ...` and the self-test exits non-zero; at this head it prints `ok`. In-tree, `slip net daily` prints `mutant killed: slip net daily (by 'closure_slip: the net move is over the daily samples')`.

Round 1 (earlier repair).

The reviewer's specs ran unchanged from the verdict commit (`evidence/spec1.json`, `evidence/spec2.json`) with `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'python3 -I tools/audit/seat/round_metrics.py --self-test --no-mutants'` (default `--copy-tree`).
- Before, at `321d7f9f34526984b5eca8d18870cd14cffbe6f6` (the verdict's `evidence/mutant_run-spec1.txt` and `-spec2.txt`): all nine listed SURVIVED.
- After, at `ba18cacb13d51fcad5278a9ab9806554704e88ae` (the cases commit, before the cadence change) and again at `411d996cdd2879646543a448730f3a96e5b2ac73`, both specs rc 0. `SURVIVED NULL`, and `KILLED` for every survivor the verdict names: `ceiling-value-key`, `produce-prior-round`, `groups-json-round`, `groups-json-stage`, `groups-json-kind`, `groups-json-write`, `plans-json-write`, `baselines-ref`, `register-ref`. The reviewer's other four are still killed: `newest-from-window`, `unexamined-window`, `closure-seconds`, `plan-sort`.

In-tree, `python3 -I tools/audit/seat/round_metrics.py --self-test` runs one mutant per predicate on a temp copy, and each mutant must turn its named case `FAIL`. This repair adds 10 mutants, each with the case that kills it:
- `ceiling value key`: killed by `report --round: a null ceiling is undecided`
- `produce prior round`, `plans json write`: killed by `producer: plans.json caches rounds N-1 and N from their state refs`
- `groups json round`, `groups json stage`, `groups json kind`, `groups json write`: killed by `producer: groups.json carries each roster group's kind, resume.stage and round`
- `baselines ref`: killed by `unexamined: the baselines are origin/main's, not the checkout's`
- `register ref`: killed by `plan history: a register first added on a branch is no register`
- `slip daily cadence` (each page its own sample): killed by `closure_slip: read at a fixed daily cadence, the last page of each day from the register`

Failing case first. The self-test at this head, run against `ba18cacb13`'s `round_metrics.py` (before the read changed), prints FAIL for four cases. One is the cadence case. The other three, `closure_slip: later moves only` and the two `report --round` cases, assert the new beside-text. All four pass at this head. The mutants the producer, report and ref cases kill are exactly the survivors listed above at `321d7f9f`.

The `slip two pages` needle moved with the read (`len(daily) < 2`), and that mutant is still killed by `closure_slip: one page, no register, no history and no round are unread`.

## Unpinned sites

prepr's diff-mutant step at `a527be6f1950c241a2d1b44f6c7f2a0aeeafd8dd` (first 40 mutants of the PR's added lines) prints 3 survivors. None is on this repair's lines. The brief for this round allows no other change, so they are listed here for the reviewer and are not pinned in this commit:
- `round_metrics.py:302` CONST_SWAP `max(0.0, ...)` to `max(1.0, ...)` (from 411d996cdd): a move that is not later pays 1 second instead of 0. Divided by `DAY_S` and printed to 2 decimals, that cannot show until about 432 daily samples, so it is equivalent at print precision. The in-file `slip later only` mutant pins the later-only rule itself.
- `round_metrics.py:338` CMP_BOUND `a <= r["ct"]` to `a < r["ct"]` (from 42059551fe): a production merge at exactly the window's opening second. No case has a merge at that second, so the half-open window's lower bound in `unexamined` is unpinned.
- `round_metrics.py:350` GUARD_OFF `if groups is None:` to `if False:` (from 42059551fe): with no `groups.json`, `unexamined` would raise on `groups.get` instead of printing `by kind unread (groups.json)`. No case runs `unexamined` without `groups.json`, so this guard is unpinned.

## Null control

- This repair: the spec's `NULL` row (no edit) SURVIVED under all three specs. The intra-day cadence case (first page and first day's last page both +10 d) prints `net +1.00 days` under both forms, so only the new case separates them.

- An empty input directory under `--round` prints all 8 reads `unread (...)` (case `null: an empty input directory prints every read unread`).
- The cadence change leaves a history of one page a day where it was. The original `closure_slip: later moves only` and `the window cuts the history` cases have one page per day, and their slip, net and ceiling figures are unchanged. Only the beside-text changed, to `4 daily samples of 5 pages` and `1 pages without a forecast`. On the intra-day history (five pages over two days) the read is 0.67 and not the all-pages 1.50, which is the case that separates the two.
- The ref cases are vacuous unless HEAD differs. Each case asserts `side()` first: HEAD's round-2 tree holds only `JUDGE.json`, and HEAD's log has round 3's `JUDGE.json` at T0 + 30 h.
- Round 10 on real data: `python3 -I <scratch>/r10slip.py <round_metrics.py>` runs `plan_history(repo, 10, {})` on `origin/handoff/audit-r10-plan` (tip ef9c90680bb24ce468066ecb3137b4b6141dd5ea, register 1792054747), then `slip_line` from the register to now. Round 10 has no `v9.0.0` opening tag, so the register stands in for the round start. At this head it prints `closure_slip 1.27 days per day (17.60 days later over 13.89 days of plan history after the register, 15 daily samples of 564 pages; net +14.94 days; 1 pages without a forecast; ...)`. The control, the same script on `321d7f9f`'s `round_metrics.py`, prints `closure_slip 2.57 days per day (37.08 days later over 14.43 days ...; net +15.24 days; 563 pages, 1 without a forecast; ...)`, which is the verdict's all-pages figure.

## Figures

- self-test: `python3 -I tools/audit/seat/round_metrics.py --self-test` returns rc 0 and ends `round_metrics self-test: ok (with mutants)`, with 50 `mutant killed` lines (`grep -c "mutant killed"`) and 100 `ok` lines: 49 before this repair plus `slip net daily`.
- structure ratchet: `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`.
- architecture score: `python3 tools/audit/archscore/score.py --diff ef6363d5f291e2eaa60620b5ea12d8d5fb902478` prints `Architecture score: dS +0.0000 NULL`.
- scope: `python3 tests/closure.py select --diff ef6363d5f291e2eaa60620b5ea12d8d5fb902478 --workdir <dir>` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` CI runs `instrument-self-tests`, which is the authority.

<!-- figure-block: scope-line mb=ef6363d5f291e2eaa60620b5ea12d8d5fb902478 head=a527be6f1950c241a2d1b44f6c7f2a0aeeafd8dd -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Carries

This part's scope comes from the dispatch brief: the two reads `closure_slip` and `unexamined` (card E11-N-P744-SCOPE). Here is each roster carry of R11-PRE-ROUND-METRICS (0-based, `handoff/audit-r10-roster`) and what this part does with it:
- Carry 0 and Carry 2 (build to 0018 section 2's definitions, enumerator in `.github/CODEOWNERS`, return an unmeetable definition as a card): built here for both reads, as described above. `/tools/audit/seat/round_metrics.py` is already in `.github/CODEOWNERS`. No definition went unmet, so there is no card.
- Carry 1 and Carry 3 (recall, overlap, `product_green`, the `lead_time` clock, runner seconds): not in this part. Recall and overlap are part 1 (#3612, merged). `product_green`, `lead_time` and `runner_s` are already in `round_metrics.py` on main (#3644). This part builds none of them. Carry: dismissed: built on main by #3612 and #3644
- Carry 4 (the CI-attempt alarm): not in this part. The `ci-attempt` row is in `tools/audit/seat/beat_jobs.py` on main. Carry: dismissed: built on main in beat_jobs.py
- Carry 5 and Carry 6 (convergence records: found-by, owner, the injected bug's cause, denominators, an examining pass over a late merge, a re-report naming its fix): not built here. `unexamined` counts any recorded finder baseline under `dev/audit/rounds/round<N>/` as examining, so an examining pass over a late merge is read once its report records a `baseline_sha`. The rest is outside this part's brief.
- Carry 7 (loop-study L1, the loop ledger): part 2 (#3657, open: `loop_ledger.py`). Not touched here.
- Carry 8 (process card P7, `caused_by` and `found_by`): part 2 (#3657). Not touched here.

## Red checks

none

## Forward-carry

none

## Friction

none
