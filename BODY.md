Round-10 protection census, repair of the blocked review at b131ad0a (closures-regressed): the 17 required contexts are enumerated and each is classified by what its steps run, and that same rule is re-applied to every row of both ledgers. Study only; the three-dot diff against `origin/main` is `CENSUS.md`, the read-only `main_reds.py`, the delivery row `dev/programme/delivery/3503.md` (commit 7033a7e4), and in `tests/closures.json` the `closures-autofix` bot's `inert_reads` line for `main_reds.py` under `tests/harness_headers.py` plus that re-record's `seconds` values. The earlier `tests/entities.py` rc 1 to 0 re-record is no longer in the diff: `origin/main` already records rc 0.

## Head

`08caf4d1c3c04925be2d4172fcd9e70d7a3d03b7` is the head: the blocked repair head `b131ad0ad8c8e8e9710681160a8b539ab88137ff`, merged with `origin/main` `005eed2573da9e946fa4838de147401d0ff36cc1` (3a7757bd), then merged with the live PR head `origin/fix/r10-protection-census` `29996fad50c4674742016b26a83bb0ce2b53ad1c`, which holds the bot commit `5d647dd055d7e08e1073bedbe570257c606b98b3` (`ci: re-record closures`). Both merges were clean; no authored file moves. `git diff HEAD 29996fad` is empty: the head's tree is the live PR head's tree. `tests/closures.json` was not re-derived or hand-edited; `grep -c protection-census/main_reds.py tests/closures.json` prints 1 (0 at `b131ad0a`). Figures stamped against `origin/main` `005eed25`, Thu Nov 12 16:48 UTC 2026.

08caf4d1c3c04925be2d4172fcd9e70d7a3d03b7

## Repair of `instrument-self-tests` (Show the tick loop refusing its own fixtures)

The step went red at `5d647dd0` (run 43242542423, job 131266913985: `30 checks, 1 failed`, `FAIL a seat bin dir with no gh shim…`). The earlier body attributed this to a defect in an older `tools/audit/seat/tick_loop.sh` repaired on main by `e899dde4ab`; that was false: the review measured `e899dde4ab` an ancestor of both `6e8db8d8` and `5d647dd0`, and `tick_loop.sh` byte-identical at `5d647dd0` and `b131ad0a`.

The cause the review measured: the self-test's first three rows (`tick_loop.sh:206-215`) run `fresh_check` against the real checkout, before line 218 sets `HPO_TICK_CODE_DIR=$t/nogit`. With CI's branch checkout, a head more than `HPO_TICK_STALE_BOUND` (25) commits behind live `origin/main` on `CODE_PATHS` prints an extra `TICK-STALE` line, and row 3 counts exactly 2 `TICK-` lines, so it fails. `5d647dd0` was 26 behind; the review's null control at `5d647dd0` with `HPO_TICK_STALE_BOUND=30` printed `30 checks, 0 failed`. The red is not introduced by this diff, which touches nothing the self-test reads; it recurs whenever main moves more than 25 commits on those paths before CI runs. That self-test isolation defect is carried as R10-HOTFIX-TICK-SELFTEST-CHECKOUT (`handoff-wip/r10-hotfix-tick-selftest-checkout`), not built here.

At this head, branch `work` checked out, 0 commits behind `origin/main` (`git rev-list --count HEAD..origin/main`): `env -u BASH_ENV bash tools/audit/seat/tick_loop.sh --self-test` printed `tick_loop self-test: 30 checks, 0 failed`. `instrument-self-tests` is not in `merge_train.py owed-reds`, so it owes no `## Red checks` entry.

## Mutation proof

n/a: the diff adds no production or tool code. `python3 -I tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --cmd true --list` lists zero mutants (it reads only added Python outside `tests/` and `dev/`; the added Python is under `dev/`), so there are no survivors to list.

## Null control

Runs 4080, 4107, 4116 are `success` and yield no row: `main_reds.py | awk '$1==4080||$1==4107||$1==4116' | wc -l` prints 0. The unmodified tree has no census file.

## Figures

- 17 required contexts: `python3 -c "import json;r=json.load(open('tools/ci/fixtures/ruleset/ruleset_23698884.json'));print(len([c for x in r['rules'] if x['type']=='required_status_checks' for c in x['parameters']['required_status_checks']]))"` prints 17.
- 33 recorded scripts, 29 reaching product files; the other 4 are `arch_score.py`, `ha_contract.py`, `layout.py`, `md_tables.mjs`: the closures one-liner in CENSUS.md's enumerator table.
- 28 main-push red-job rows: `python3 -I dev/audit/rounds/round10/protection-census/main_reds.py | wc -l`.
- 18 entries over 14 PRs: `tail -1 dev/audit/rca/ci-red/entries_v7.1.2.tsv` prints `ENTRIES 18 PRS 14`.
- 4 `harness_headers.py` reds: `grep -c harness_headers dev/audit/rca/ci-red/entries_v7.1.2.tsv`.

## Red checks

Read per commit from the PR's check-runs (runs 8032-8036, 8059/8060, 8069/8070/8072), not from the earlier body. Every check that concluded red on any commit of the branch:

- `tests / closures`: red at `b7a838c1ef516f840530eb85b4c94c6fdfdab0f1` (run 8060, job 131170648315), `INERT READS UNDER-APPROXIMATED`: `tests/harness_headers.py` opened `dev/audit/rounds/round10/protection-census/main_reds.py`, which the committed `inert_reads` did not list. Repaired by the `closures-autofix` bot commit `5d647dd055d7e08e1073bedbe570257c606b98b3` (one added `inert_reads` line in `tests/closures.json`), which the repair head `b131ad0a` dropped and this head carries again through the merge of `29996fad`. The earlier body said `none` here, which is why `pr-contract` went red. **Cheaper detector:** `python3 tools/pr/ci_predict.py --apply-inert` before the handoff, but it does not exist for this red: run on a clean worktree at `6e8db8d8` (base `02a73718`, then `origin/main`) it printed `CI PREDICT: no closures, fast, governance or instrument red predicted` in 2.6 s and wrote nothing, and `--apply-inert` the same (a data-file read is not seen). The detector that does reproduce the red is `env -u BASH_ENV ./tests/derive_closures.sh --single tests/harness_headers.py`: it wrote exactly the one missing line (`main_reds.py`), 169.6 s wall (2m49.6s) on this diff, against the CI closures job's 25 min (12:08 to 12:33) plus one bot commit and a second full run. **Process state: (c)**, the process existed and ran and did not produce the intended result: the step 6d predictor is the pre-handoff path `ci-autofix.md` names for INERT READS, and it is blind to a file a harness reads at run time by directory, so a green `ci_predict` said nothing about this red. **Cost test:** adding a standing `--single tests/harness_headers.py` (about 170 s) to every handoff costs more than it saves, because the red is repaired mechanically by the `closures-autofix` job with no seat action and no manual cost; the defect cost here was wall-clock only (about 25 min of one CI cycle). No measured class frequency exists; the estimate is one occurrence for a diff that adds a file under a directory `harness_headers.py` scans, so P is low per PR. **Recorded decision: no countermeasure built in this body-only repair;** teaching `ci_predict` to see directory-scanned data reads is a separate code change and is not smuggled in here.
- `pr-contract / pr-contract`: red at `b7a838c1` and `5d647dd0` (`Check the body against the contract`), because the body above said `none` for `tests / closures`. A consequence of the same answer, cleared by this body; the contract excludes its own verdict from the set it asks a body to answer.
- `gate`: red at `7033a7e4`, `b7a838c1` and `5d647dd0` (`Judge this head`), the verdict over the checks above (at `7033a7e4` over the cancelled code run); it is excluded the same way.
- `tests / nightly-status`: red at `b7a838c1` and `5d647dd0` (`Report the last scheduled run's conclusion`). It grades `main`'s last scheduled run, not this head, and this diff touches none of its inputs; the orchestrator's to clear on `main`.

Runs 8032, 8033 and 8035 at `2c803484` and `7033a7e4` concluded `cancelled` (superseded by the next push), not red.

## Forward-carry

- Round 11, when it builds the product-only set (9 product contexts of 17): decide where `pr-contract`'s code-scanning-alert duty lives (it is the only check that turns an alert into a red; #3244 8bc540e), and whether `harness_headers.py` and the instrument self-tests leave `fast`. Carry: dismissed: both decisions are written in CENSUS.md under "Sizing for round 11", the file the round-11 build reads, and no group id exists yet to route them to

## Friction

none

## Answers to the review's items

1. `tests / ci-ratchet` is reclassified: tests.yml:2301-2318 (push to main only, not required), `tests/ci_ratchet.py` reads Actions timings and archscore, so it is a programme instrument. The 28 main-push rows are therefore reds the product-only set stops grading, not "no information".
2. The 17 contexts are listed and classified in CENSUS.md: 9 product (`fast (3.14)`, `browser`, `typing`, `mutation`, `hassfest`, `validate-hacs`, three CodeQL legs), 8 programme (`briefs`, `closure-scope`, `closures`, `policy-docs`, `wave-script`, `env-matrix`, `pr-contract`, `budget-raise-gate`). The unsourced "B1 drop list" is removed. The one correction I found along the way: `fast` is a product check that also runs programme-rule scripts, and `pr-contract` carries a product duty.
3. Further rows that moved under the same rule: `tests / closures` in #3180 is programme; the 5 `fast` reds (#3180, #3189, #3208, #3227, #3242) are a product check red on a programme rule or script; the #3244 `pr-contract` row is a programme context carrying a product-code alert. Of 18 PR rows, 11 would stop being graded under contexts 1-9 and 7 would still be graded; of the 11, 7 are infrastructure, 2 grader skew, 2 real catch (#3167 replay, already not required; #3244 CodeQL alert).
4. Findings: the `entries.py` enumerator is replaced by `tail -1 ...entries_v7.1.2.tsv`; the harness_headers count is 4, not 5; the six cancelled runs are no longer classed as infrastructure (the job itself concluded `failure`, cause UNREAD); the "~560" denominator is dropped. The `gate` job and the names `replay`, `prelude`, `instrument-self-tests` are not in the 17 and were not read: placed n/r, not guessed.
5. `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` ran, exit 0, `tests/entities.py 567 files`, which changed `rc` from 1 to 0 in `tests/closures.json`; `origin/main` now records the same rc 0, so the line is no longer in this diff.
