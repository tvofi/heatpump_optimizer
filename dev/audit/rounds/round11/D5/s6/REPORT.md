# D5-s6, round 11: comments in tools/audit, tools/{ci,coverage,devices,merge,plan,release,replay,site}

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B11. Cells: 258 files
(240 `.py`, 15 `.sh`, 3 `.mjs`), steps M1 to M4, as
`python3 tools/audit/check_scopes.py --repo <repo> --ref <sha> --seat D5-s6` prints them.
The export has no `.git`, so `--repo` points at a checkout that holds the baseline commit.

## Method

- **M1 to M3.** `text_ledger.py outline --seat D5-s6` prints 0 rows: these cells hold
  no Markdown or HTML. The universe of M1 (documents times reader paths), of M2
  (headings and links) and of M3 (the D6 units of those documents) is therefore 0.
  Redispatched C1, C4 and C5 are answered with that denominator. C2 and C3 cover
  `docs/*.md`, which belong to the cells of D5-s1 and D5-s2, so they go to those seats
  as leads.
- **M4.** `m4_ledger.py` enumerates all 3781 D5 units with the production enumerator
  (`text_ledger.units_of`). It then runs these checks against the tree at the ref:
  - (a) every repository path resolves to a tracked file or directory;
  - (b) every `file:symbol` citation names a symbol the cited file defines;
  - (c) every `name()` the comment mentions is a code token in the tree;
  - (d) no prose sentence is over 40 words (criteria C5);
  - (e) when a comment sits directly above a tuple, list, set or dict display and
    states a count, that count equals the number of items (the cited-number check
    that C7 asked to automate);
  - (f) every `--flag` on a usage line that names the file itself appears among that
    file's code strings.

  I read every flag of kinds (a), (e) and (f) in place. The script's `CONFIRMED`
  list holds the ones confirmed false. `truth_checks.py` runs each confirmed defect
  again against the production symbol, with a perturbation that drives the defect's
  count to zero. The script writes the ledger to `LEDGER.tsv`, and
  `text_ledger.py check --plant` accepts it: units=3781, unrowed=0, orphan=0,
  malformed=0, plant_refused=1.

## Findings

All are rated low and classed as hygiene. They come from step D5.M4, one per file
holding a false row, except the C5 group.

| id | file | what | number |
|---|---|---|---|
| D5-s6-01 | tools/release/stamp.py | The comment says "the same three regexes", but `RECORD_CLASS_RES` holds 6. It cites `.claude/workflows/policy_lint.mjs`, which has moved to tools/policy. It also cites a section of `tools/audit/README.md`, a file that does not exist. | 3 |
| D5-s6-02 | tools/audit/seat/replay_draws.py | The docstring names `tests/replay_draws.tsv`. `replay.COST_DRAWS` is `tests/replay_cost_draws.tsv`. | 1 |
| D5-s6-03 | tools/audit/seat/row_position.py | The usage line runs `dev/audit/harnesses/row_position.py`, which exits with rc=2. | 1 |
| D5-s6-04 | tools/audit/seat/plan_audit.py | The usage line documents `end-to-end ... [--target 22.7]`. `main`'s parser refuses it with rc=2. | 1 |
| D5-s6-05 | tools/audit/seat/update_pr.sh | The header calls the script `updatepr.sh`. | 1 |
| D5-s6-06 | tools/audit/seat/roster_lib.py | Three units define behaviour by reference to `gen_table_rev3.py`, which is not in the tree. | 3 |
| D5-s6-07 | tools/audit/seat/plan_table.py | The same citation of `gen_table_rev3.py`. | 1 |
| D5-s6-08 | 99 files (`C5_BY_FILE.tsv`) | 404 sentences are over 40 words. The longest is 166 words. Leave-one-out: 99 cells, range 1 to 35, 369 when the largest is dropped. | 404 |

I grouped C5 by phenomenon because it is a length rule, not a false or stale row.
The per-file split is in `C5_BY_FILE.tsv`, if the judge wants D5's
one-finding-per-file form.

## Non-findings

| check | result |
|---|---|
| `file:symbol` citations | 0 false of 3 |
| `name()` calls | 0 false of at least 150 |
| repository paths | at least 1605 checks: 9 confirmed false; 178 dismissed after reading. Dismissed tokens are runtime artefacts, f-string fragments, self-test fixtures, the deliberate `BRIEF_LINT_OLD` fallback, or scripts cited at another ref. |
| usage flags | at least 186 checks: 1 false; 9 dismissed because the parser builds those options in a loop |
| count against the adjacent literal | 44 pairs: 1 false; 28 dismissed because the number counts something else |

## Harnesses

- `m4_ledger.py`. Run with
  `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s6/m4_ledger.py --repo <checkout> --ref <sha>`.
  It writes `LEDGER.tsv`, `FLAGS.tsv` and `C5_BY_FILE.tsv`.
- `truth_checks.py [--perturb stamp|replay|row_position|plan_audit|update_pr|gen_table]`.

## Unfinished

- **M4.** Behavioural C1 truth was not checked for the 2941 units rowed `no-claim`;
  those rows only mean the automated checks found nothing to test. C3 (restatement)
  and C4 (share of history sentences) were not judged for any of the 3781 units.
  Issue numbers were not resolved.
- **M3.** Redispatched C6 is still open. The mechanism paragraphs in the 1336
  docstrings were not traced one by one.

## Leads

| seat | file | what |
|---|---|---|
| D5-s8 | `tools/policy/policy_lint.mjs` | `RECORD_CLASS_RES` has the same "three regexes" comment over 6 regexes |
| D5-s1 | docs | redispatched C2 |
| D5-s2 | docs | redispatched C3 and the docs part of C7 |
| D5-s4 | www JS | the C7 symbol scan |

## Exposure

Comments in the cells cite earlier finding IDs: D11-s1-72, D13-04, the R9 and R10
group IDs, and issue numbers. I read them as context only. I read no documents
under `docs/`.
