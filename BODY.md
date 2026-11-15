R11-PRE-ROUND-METRICS, part 1 of 2 (topic r11-pre-round-metrics): the brief (owner ruling 2026-11-13, cards P3 and P8; process convergence audit d5d7ff81 section 6 rows a3 and a7) and carries 0-4. Part 1 of the group (#3612, topic r11-pre-round-metrics-p1) landed the two held-out instruments; this part lands the flow reads.

- `tools/audit/seat/round_metrics.py` (new, code-owned): 0018 section 2's `lead_time` (clock read from the commit that first added `"group": "<G>"` to a roster file at the roster ref, never a filled field), `product_green` over the window with `tools/ci/gate.py`'s `REQUIRED["push"]` count at the window's two ends beside it, `restore` (time to restore), `runner_s` (job seconds per merge) and `tokens` (`tokens_per_change` over a `tokens.tsv` ledger), per round (`--round N`: tag v(N-1).0.0 to vN.0.0 or now, decision 0016) and per week (`--weeks`). It is the tracked form of the audit's scratch `W/merges.py` and `W/agg.py` (merges by `machinery_ratchet.diff_stats` class), and the scorecard's input producer (`produce`: runs, job listings, verdicts, merges, roster; one REST batch, job listings cached per run attempt).
- `tools/audit/seat/scorecard.py` (now code-owned, as the enumerator 0018 names for `product_green`): its gate read takes a run's latest attempt (shared `round_metrics.gate_conclusions`) and it prints round_metrics' lines over the open round as `R` lines; lead-time percentiles per class, the time-to-restore line and the token line are those.
- `tools/audit/seat/beat_jobs.py`: the `scorecard` row runs the producer before the report (a failed producer is `scorecard: UNREADABLE produce`, and the report then does not run on stale inputs); a new `ci-attempt` row (carry 4) flags a ci.yml run at attempt 20 or more among the newest 100, naming the run, its branch and its pull request. Both rows are in `beatd.jobs.json`.
- `tools/audit/seat/bottleneck_check.py` (row a7): a held breach prints its live line while the value is more than a quarter worse than the value its first line printed (lower is worse for yield and throughput), its first line otherwise. Merge-wait now prints "hours": the digest's `norm()` blanks "<n> h" as an age, so at the base the digest never showed a merge-wait value at all (Figures).

Carries: carry 0 and carry 2 (same text): every enumerator built here is code-owned in `.github/CODEOWNERS` in this pull request, built to section 2's clock, windows and denominators, a partial ledger is a NO-READ (a concluded run with no job listing makes `product_green` and `restore` unread; one CI run without its listing makes `runner_s` unread; a seat class without a ledger row makes `tokens` unread), and the definitions it cannot meet are the cards below. Carry 1 and carry 3 (same text): the two held-out instruments landed with #3612; this part builds `product_green` over the round's window with the gate's check count beside it, the `lead_time` clock from the roster commit, and runner seconds per merge, each unread on an empty input. Carry 4: the `ci-attempt` row; its self-test fires on the #3287 window (PR #3319's runs 42469369199 and 42469369682, the code run at attempt 44, per `dev/audit/rca/R10-RCA-SWEEP-SETTLE-LOOP.md`) and is silent at attempts 1 and 19; the fixer.md rule drafted with it is not built, as the carry says. Carries 5-8 are part 2's and are not answered here. Carry: R11-PRE-ROUND-METRICS

## Cards

Definitions of 0018 that cannot be met as written, returned rather than bent:

- **C5 lead_time has no clock for a merge outside every roster.** A hotfix or record branch whose pull request no roster group names (by `resume.pr`, else by branch) never entered a roster, so 0018's clock does not exist for it. Built: such merges are counted beside the term per class, never in it; a group entered after its merge (an age from a later stamp) is unknowable and counted beside too.
- **C6 the gap from a finding's judged date to the roster commit (section 5, `lead_time` row) is not built.** No record joins a group to the judge record's per-finding dates in a form the producer reads; it needs part 2's convergence records (carries 5-8). It stays NO-READ.
- **C7 runner seconds are job wall seconds, not billed runner seconds.** 0018 names the term without a definition. Built: the sum of `completed_at - started_at` over every job of every attempt of every completed `CI` run created in the window, over the window's merges; GitHub's billable minutes are a second API read per run and are not taken.
- **C8 rounds before v10 have no window.** Section 2's window runs from the previous closeout stamp, a major tag since decision 0016; v8.0.0 and v9.0.0 do not exist, so `--round 9` and `--round 10` print `unread`. `--since/--until` reads any window by hand.
- **C9 the token ledger's shape is this reader's proposal.** R11-PRE-TOKEN-LEDGER has not landed; `tokens` reads `tokens.tsv` with columns `t`, `seat_class`, `tokens` (seat classes orchestrator, local, cloud), carried to that group below. Until then the line is unread.

## Head

46607a59fa76ab341eeec3b1ab4e06257e99355d, measured at origin/main 31117b1029de63938d949e78dcbcd8f9451e5e33, 2026-11-15T23:14:41Z.

## Mutation proof

Each self-test edits a temp copy of its production code, one mutant per predicate, and fails unless the named case fails: `python3 -I tools/audit/seat/round_metrics.py --self-test` kills 23 (rank index, latest merge per group, unknowable lead dropped, class filter, concluded runs, gate not run conclusion, partial ledger, gate latest attempt, restore window and spell start, runner attempt and window, token class and production filters, roster first add and incremental scan, part suffix, resume.pr, cached class, producer main filter and cache, open-round window, week span); `python3 -I tools/audit/seat/bottleneck_check.py --self-test` adds 6 to its 12 (`worse` comparison, both directions and the direction set; the first line kept as the reference; the live line never chosen, which is the base's behaviour); `python3 -I tools/audit/seat/beat_jobs.py --self-test` adds 4 (ci-attempt comparison, row off, no-PR wording; producer failure ignored); `python3 -I tools/audit/seat/scorecard.py --self-test` keeps its own (one moved with the gate read into round_metrics: `gate latest attempt`).

Failing first: the `live-never` mutant restores the base's `remembered` (the first line always) and fails `memory: a held breach more than a quarter worse prints the live line`; `round_metrics.py` and the `ci-attempt` row do not exist at the base; the beat case `bottleneck: a merge-wait line keeps its live hours through the digest` fails on the base's "h" wording (Figures, null control).

Diff mutants (`fixer.md` step 2): `MUTANT_CMD="bash <scratch>/mut.sh" MUTANT_IN_PLACE=1 bash tools/pr/prepr.sh <body>`, where `mut.sh` (scratch, not in the tree) runs, under `set -e`, `beat_jobs.py --self-test --no-mutants`, `round_metrics.py --self-test --no-mutants`, `scorecard.py --self-test --no-mutants` and `bottleneck_check.py --self-test`; prepr's draw of the diff's first 40 mutants falls in `beat_jobs.py` and `beat_jobs_selftest.py`. At aef1c9e1 it printed three `SURVIVED`: `beat_jobs.py` `ci_attempt`'s `if got is None:` guard (GUARD_OFF and RETURN_DEL), now killed by the case `ci-attempt: an overlay without repo is UNREADABLE and calls no API` (the guard's `return` replaced by `pass` makes the self-test exit 1 on `TypeError: 'NoneType' object is not subscriptable`); and the third, with the one the head's run adds (the head's run prints two `SURVIVED`, both test fixtures), is under `## Unpinned sites`. A first run with `MUTANT_CMD` naming round_metrics' self-test alone printed 40 `SURVIVED`, all in `beat_jobs.py`, because that command never imports it; the per-file command above replaced it.

## Null control

An empty input directory prints every read unread, never a value: `round_metrics.window_lines` over a missing directory prints six `unread (` lines (self-test case `null: an empty input directory prints every read unread`), and `scorecard.py report` over one prints `R       unread (` without a checkout. A run failing only outside its gate counts green in `product_green`; attempts 1 and 19 are silent in `ci-attempt`; a held breach exactly a quarter worse, or improving, re-prints its first line.

## Figures

<!-- figure-block: scope-line mb=31117b1029de63938d949e78dcbcd8f9451e5e33 head=46607a59fa76ab341eeec3b1ab4e06257e99355d -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- a7 before and after, a scratch driver (`a7.py`, not in the tree) feeding `judge` and `remembered` a merge-wait trip at 2.1 hours then 4.2 hours with one memory file: base (`git show origin/main:tools/audit/seat/bottleneck_check.py`) prints the 2.1 line both times; head prints the 2.1 line, then the 4.2 line.
- The base's digest never carried a merge-wait value: `python3 -c "import beat_jobs as bj; print(bj.norm('BOTTLENECK: merge-wait 4.2 h median (3 PRs, 24 h; worst #1 4.2 h) vs 2 h'))"` (in tools/audit/seat) prints `BOTTLENECK: merge-wait <age> median (3 PRs, <age>; worst #1 <age>) vs <age>`; the head's "hours" wording keeps `4.2 hours`.
- Round 10's span by tag, git half only (this seat has no Actions API read, so `product_green`, `restore` and `runner_s` are not taken here): a scratch driver wrote `merges.tsv` with `round_metrics.merge_rows` since v7.0.0 over the rosters at `origin/handoff/audit-r10-roster` 21f39d77, then `python3 -I tools/audit/seat/round_metrics.py report --dir <that dir> --repo . --since 2026-10-14T15:27:06+02:00 --until 2026-11-15T06:22:47+01:00` (v7.0.0 to v10.0.0) prints `merges 1139: production 155, machinery 516, record 468`; `lead_time production p50 63.6 h p90 234.3 h (n=117 groups; 24 production merges name no roster group; 1 groups entered after their merge)`; `lead_time machinery p50 23.8 h p90 171.0 h (n=315 groups; ...)`; `lead_time record p50 6.7 h p90 9.8 h (n=4 groups; 464 record merges name no roster group; ...)`. The audit's R10 production p50 of 21.7 h ran from the branch's first commit; 0018's clock starts at the roster entry, earlier, so the two are different terms, not a regression.
- Cost of the producer's git half on this container: `roster_entries` cold over the full roster history 34.4 s, incremental from the cached tip under 0.1 s; `merge_rows` cold over 1159 merges since v7.0.0 32.9 s (each later pass re-derives only uncached merges).
- Branch-to-group mapping, a scratch driver over origin/main 31117b10's first-parent merges since 2026-10-14T13:27Z (`git log --first-parent --merges --since=...`, the merge subject's PR and branch), rosters at 21f39d77: by `resume.pr` and branch both 308 agree, 0 disagree; 166 by branch only, 38 by `resume.pr` only; the rest name no group (record, triage, hotfix and dependabot branches, among others): the C5 card.
- Gate check count: `round_metrics.gate_checks` over v7.0.0..v10.0.0 prints `unread at the window's start, 17 at its end` (`tools/ci/gate.py` did not exist at v7.0.0).
- Self-tests at the head: round_metrics, bottleneck_check, beat_jobs and scorecard each end `ok` with mutants.
- Read sets re-recorded with `python3 -I tools/ci/selftest_scope.py record` for steps round-metrics, scorecard, beat-job-rows, bottleneck-alert, selftest-wiring, self-tests-outside-seat, temp-or-machine-path, field-coverage and hooks-setup (`recorded 9 step(s) ... 0 failed [], 0 broken trace(s)`).
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Gate scope: the block above is `MODE: FULL` because `tests/closures.json` (repaired by `python3 tools/pr/ci_predict.py --apply-inert`, which added round_metrics.py and its self-test to entities' inert reads) is a gate file; left to CI. Before that repair `python3 tests/closure.py select --diff 31117b10` printed `MODE: SCOPED -- 3 script(s) run`, and those three (`tests/doc_claims.py`, `tests/entities.py`, `tests/harness_headers.py`) plus run_always's `tests/env_drift.py --claims-only` and `tests/closure.py selftest` exited 0 with `PYTHONPATH=tests/hastub` (`ALL 2723 ENTITY CHECKS PASSED`).

## Unpinned sites

- `tools/audit/seat/beat_jobs_selftest.py`, the a7 digest case's fixture `{"pr": 1, "hours": 4.2}` (CONST_SWAP 1 to 2): a test fixture's pull-request number, which the case does not assert; equivalent, no check owed.
- `tools/audit/seat/beat_jobs_selftest.py`, the case `scorecard: the producer runs first, ...`'s fixture `"scorecard.py": (0, sc_out, "")` (CONST_SWAP 0 to 1): that case asserts the call order and the producer's arguments, which the report's exit code does not move; a failing report is pinned by `scorecard: a failed instrument is UNREADABLE, never written`. Equivalent for this case, no check owed.

## Red checks

none

## Forward-carry

- R11-PRE-TOKEN-LEDGER: `round_metrics.token_line` (the scorecard's `R tokens` line, 0018's `tokens_per_change`) reads `<state>/scorecard/tokens.tsv` with tab-separated columns `t` (UTC ISO stamp), `seat_class` (`orchestrator`, `local` or `cloud`) and `tokens`, and is unread while any of the three classes has no row in the window. The ledger writes that file in that shape, or changes this reader in its own pull request (round_metrics.py is code-owned); control: `python3 -I tools/audit/seat/round_metrics.py --self-test` cases `tokens:`. Carry: R11-PRE-TOKEN-LEDGER

## Friction

none
