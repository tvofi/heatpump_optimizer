Round-10 protection census, repair of the blocked review at 23d7ac26: the 17 required contexts are now enumerated and each is classified by what its steps run, and that same rule is re-applied to every row of both ledgers. Study only; the diff is `CENSUS.md`, the read-only `main_reds.py`, and a measured re-record of `tests/entities.py` in `tests/closures.json` (rc 1 to 0).

## Head

6e8db8d8c12e480181e730bd30e01da3c97b733f

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

none

## Forward-carry

- Round 11, when it builds the product-only set (9 product contexts of 17): decide where `pr-contract`'s code-scanning-alert duty lives (it is the only check that turns an alert into a red; #3244 8bc540e), and whether `harness_headers.py` and the instrument self-tests leave `fast`. Carry: dev/programme/HANDOVER.md

## Friction

none

## Answers to the review's items

1. `tests / ci-ratchet` is reclassified: tests.yml:2301-2318 (push to main only, not required), `tests/ci_ratchet.py` reads Actions timings and archscore, so it is a programme instrument. The 28 main-push rows are therefore reds the product-only set stops grading, not "no information".
2. The 17 contexts are listed and classified in CENSUS.md: 9 product (`fast (3.14)`, `browser`, `typing`, `mutation`, `hassfest`, `validate-hacs`, three CodeQL legs), 8 programme (`briefs`, `closure-scope`, `closures`, `policy-docs`, `wave-script`, `env-matrix`, `pr-contract`, `budget-raise-gate`). The unsourced "B1 drop list" is removed. The one correction I found along the way: `fast` is a product check that also runs programme-rule scripts, and `pr-contract` carries a product duty.
3. Further rows that moved under the same rule: `tests / closures` in #3180 is programme; the 5 `fast` reds (#3180, #3189, #3208, #3227, #3242) are a product check red on a programme rule or script; the #3244 `pr-contract` row is a programme context carrying a product-code alert. Of 18 PR rows, 11 would stop being graded under contexts 1-9 and 7 would still be graded; of the 11, 7 are infrastructure, 2 grader skew, 2 real catch (#3167 replay, already not required; #3244 CodeQL alert).
4. Findings: the `entries.py` enumerator is replaced by `tail -1 ...entries_v7.1.2.tsv`; the harness_headers count is 4, not 5; the six cancelled runs are no longer classed as infrastructure (the job itself concluded `failure`, cause UNREAD); the "~560" denominator is dropped. The `gate` job and the names `replay`, `prelude`, `instrument-self-tests` are not in the 17 and were not read: placed n/r, not guessed.
5. `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` ran, exit 0, `tests/entities.py 567 files`, which changed `rc` from 1 to 0 in `tests/closures.json`; committed.
