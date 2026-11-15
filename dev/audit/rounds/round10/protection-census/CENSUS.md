# R11-PROTECTION-CENSUS (round 10): the required set, sorted by what each check reads

Read-only study, no production or tool code. Written without `gh` or an API
token. The classification below needs none: each check's steps are in the tree.
Only the per-head check conclusions of PRs outside the ledger, and the job logs
of the main `tests / ci-ratchet` reds, are **UNREAD**.

## Rule (applied to every check, never to a name)

A check is **product** when a step of its job runs the shipped code or its
metadata: `custom_components/`, `blueprints/`, the card, the HA manifest, HACS
metadata. It is **programme** when its steps read only the governance corpus,
pull-request bodies, rosters, the test-selection machinery, CI timings or
archscore. A job with both says so; it is placed by its purpose and the
mixed part is named.

## Sources and enumerators

| figure | enumerator | prints |
|---|---|---|
| required contexts | `python3 -c "import json;r=json.load(open('tools/ci/fixtures/ruleset/ruleset_23698884.json'));print(len([c for x in r['rules'] if x['type']=='required_status_checks' for c in x['parameters']['required_status_checks']]))"` | 17 |
| recorded test scripts / scripts whose closure reaches `custom_components/` or `blueprints/` | `python3 -c "import json;d=json.load(open('tests/closures.json'))['closures'];p=[k for k,v in d.items() if any(f.startswith(('custom_components/','blueprints/')) for f in v)];print(len(d),len(p))"` | 33 29 |
| the 4 scripts that reach no product file | same, `sorted(set(d)-set(p))` | `tests/arch_score.py tests/ha_contract.py tests/layout.py tests/md_tables.mjs` |
| main-push red-job rows | `python3 -I dev/audit/rounds/round10/protection-census/main_reds.py \| wc -l` | 28 |
| ... by run conclusion and job | `... main_reds.py \| awk '{print $3,$4}' \| sort \| uniq -c` | 8 failure `gate`, 8 failure `tests` (the ci-ratchet job), 6 cancelled `gate`, 6 cancelled `tests` |
| PR-head ledger | `tail -1 dev/audit/rca/ci-red/entries_v7.1.2.tsv` | `ENTRIES 18 PRS 14` |
| `harness_headers.py` reds | `grep -c harness_headers dev/audit/rca/ci-red/entries_v7.1.2.tsv` | 4 (#3180, #3189, #3208, #3242) |
| delivery files, all rounds | `ls dev/programme/delivery \| wc -l` | 1614 (no round-10 denominator is claimed) |

Null control: `main_reds.py | awk '$1==4080||$1==4107||$1==4116' | wc -l` prints 0 (those runs are `success`).

## The 17 required contexts, classified (9 product, 8 programme)

Context list: the ruleset fixture named in the first enumerator row.

| # | context | job (file:line) | what its steps run | side |
|---|---|---|---|---|
| 1 | `fast (3.14)` | tests.yml:163 | `tests/run.sh` with RUN_PART=fast; 29 of 33 recorded scripts reach product files; `arch_score*.py` are skipped here (run.sh:657-659), `layout.py`, `md_tables.mjs`, `ha_contract.py` run here and read no product file | **product**, mixed: also runs programme-rule scripts (`harness_headers.py`, instrument self-tests) |
| 2 | `browser` | tests.yml:503 | `tests/plan_view.py`, `tests/card_browser.mjs` (card layout in Chromium) | **product** |
| 3 | `typing` | tests.yml:675 | `tests/typing_ruler.py` (mypy --strict ruler, three ratcheted numbers) | **product** |
| 4 | `mutation` | tests.yml:1036 | `tests/mutation_table.py` over production files the diff touched | **product** |
| 5 | `hassfest` | hassfest.yml:14 | `home-assistant/actions/hassfest` on the manifest | **product** |
| 6 | `validate-hacs` | validate.yml:14 | `hacs/action` | **product** |
| 7-9 | `Analyze (actions)`, `(javascript-typescript)`, `(python)` | codeql.yml `analyze` | CodeQL over the tree; `tools/pr/codeql_scope.py` decides skip-with-stand-in. The python and javascript legs read product code; the `actions` leg reads the workflows (programme files). Counted product as a set; the `actions` leg is the exception. | **product** (3), `actions` leg reads programme files |
| 10 | `briefs` | tests.yml:602 | `tools/policy/brief_lint.mjs` over wave rosters | **programme** |
| 11 | `closure-scope` | tests.yml:1749 | `tests/lane_skip.py`, `tests/closure.py`: decides which lanes may skip | **programme** (test-selection machinery) |
| 12 | `closures` | tests.yml:1966 | `tests/derive_closures.sh` and `closure.py`: re-records and checks the measured closures | **programme** |
| 13 | `policy-docs` | governance.yml:61 | policy lint, rules_sync, fragments_sync, machinery ratchet, CODEOWNERS gap | **programme** |
| 14 | `wave-script` | governance.yml:1664 | `check-wave-script.mjs`, agreement lane, `fold_ledger.py` | **programme** |
| 15 | `env-matrix` | governance.yml:1552 | `policy_lint_envmatrix.mjs`: declared environment shapes of the governance checks | **programme** |
| 16 | `pr-contract` | pr-contract.yml:40 | PR-body contract, figure lint, version-edit refusal, `carry_audit.py`; **also** `tools/ci/codescan_wait.py` lists the open code-scanning alerts as reds | **programme**, with one product duty: it is the only check that turns a CodeQL alert into a red |
| 17 | `budget-raise-gate` | budget-raise-gate.yml:57 | `tools/policy/budget_raise_gate.py`: owner approval of a budget raise | **programme** |

Sizing for round 11: the product-only set is contexts 1-9 (9 of 17, 8 dropped).
Two decisions the study cannot make and a round-11 seat must: (a) the CodeQL
alert duty of `pr-contract` (row 16) has no home in a product-only set unless it
is moved into the CodeQL legs or kept; (b) `fast` still grades programme-rule
scripts (`harness_headers.py`, instrument self-tests), so splitting those out of
`fast` is a further move, priced by the 5 `fast` reds below that those scripts
caused. `hassfest` and `pr-contract` also have a second definition in ci.yml
(224, 270); the ruleset names the context, not the file.

## Not required contexts that appear in the ledgers

| name | read | side |
|---|---|---|
| `tests / ci-ratchet` | tests.yml:2301-2318: runs only on push to `refs/heads/main`, comment says not a required context; `tests/ci_ratchet.py` docstring: measures `script_runs_per_push` and `critical_path_minutes` from Actions run timings, plus archscore counts | **programme instrument**, not required |
| `gate` | not in the 17 and its steps were not read in this study | **UNREAD**, not required |
| `tests / replay`, `prelude`, `instrument-self-tests` | not in the 17 | not required; steps UNREAD |

## Main-push reds (28 rows, 14 runs)

Each of the 14 runs carries a red `tests / ci-ratchet` job and a red `gate`.
Runs 4009, 4015, 4028, 4035, 4046, 4055, 4056, 4128 concluded `failure`; runs
4036, 4037, 4038, 4040, 4044, 4045 concluded `cancelled`. In all six cancelled
runs the `tests / ci-ratchet` job itself concluded `failure` (counted from
`runs_red4.json` job conclusions by `main_reds.py`, which prints only
`failure` jobs and printed all 14), so "cancelled" is the run's conclusion and
says nothing of the job's cause. Cause of every one of the 14 ci-ratchet reds:
**UNREAD** (job logs are not in the tree). No infrastructure class is assigned.

Class: the 14 ci-ratchet rows are reds of a **programme instrument** that is
not a required context; the 14 `gate` rows are not a required context either.
These 28 rows are therefore exactly the class a product-only set stops
grading, not rows "said nothing about". They are not a product-check signal.

## PR-head reds (18 rows) re-sorted by required context

Same rows and same causes as the previous cut; the new column is the side of
the required context that carried the red (1-17 above), or "n/r" for a name
outside the 17. Class column unchanged where the cause is read.

| PR | head | red | class | context side |
|---|---|---|---|---|
| 3167 | 7637d66 | tests / replay | real catch (timing budget; runner noise possible) | n/r |
| 3167 | 4e4bb29 | gate | infrastructure (cancelled run) | n/r |
| 3180 | 3f7777a | tests / fast, tests / closures | real catch: `harness_headers.py` rule on the PR's own harness | `fast` (product, but cause is a programme rule) + `closures` (programme) |
| 3181 | bb730c1 | gate | infrastructure (CodeQL python cancelled) | n/r (the cancelled leg is product) |
| 3189 | fd9c5ba | tests / fast | real catch (`harness_headers.py`) | product check, programme-rule cause |
| 3195 | 6f742a3 | tests / typing | real catch (9 no-untyped-call) | **product** |
| 3195 | c383169 | prelude, gate | infrastructure (prelude wait expired); also real: 8 unpinned sites | n/r |
| 3195 | 611e1aa | gate (tests / mutation) | real catch (unpinned-site refusal; cured by bot commit) | **product** (`mutation`, via `gate`) |
| 3204 | e5381d9 | gate | infrastructure (cancelled) | n/r |
| 3208 | 327d83e | tests / fast | real catch (`harness_headers.py`) | product check, programme-rule cause |
| 3211 | 1fca63c | gate | infrastructure (PR closed, run cancelled) | n/r |
| 3217 | 1c42ca3 | gate | infrastructure (CodeQL python cancelled) | n/r |
| 3219 | aca5009 | gate | infrastructure (+ body defect) | n/r |
| 3227 | a52354e | instrument-self-tests, fast | real catch (`body_patch.sh:146`) | `fast`, cause is a programme script |
| 3240 | 79cf40f | gate | grader skew | n/r |
| 3242 | e836876 | tests / fast | real catch (`harness_headers.py`) | product check, programme-rule cause |
| 3244 | a258212 | gate | grader skew | n/r |
| 3244 | 8bc540e | pr-contract / gate | real catch (CodeQL alert 50, `py/jinja2/autoescape-false`) | **programme** context carrying a product-code alert |

Counts, each by hand from the table (18 rows): real catch 9, infrastructure 7,
grader skew 2.

Rows moved by the re-applied rule (all prior classes kept, sides added or
changed):
- the 28 main-push rows: from "product check `ci-ratchet`" to programme
  instrument, non-required (the block);
- 3180 `tests / closures` is programme (it was not separated);
- the 5 `fast` rows (#3180, #3189, #3208, #3227, #3242) are a product check
  whose red was caused by a programme rule or script, not by product code:
  `grep -c harness_headers` is 4 (the 5th is `body_patch.sh` in #3227);
- 3244 `pr-contract` is a programme context whose red was a product-code alert;
- `gate`, `replay`, `prelude`, `instrument-self-tests` are placed "n/r", not
  guessed.

## Which reds would have reached main under a product-only set (contexts 1-9)?

Rows whose every required red is programme or n/r stop being graded: 3167
(both), 3181, 3195 c383169, 3204, 3211, 3217, 3219, 3240, 3244 a258212, and
3244 8bc540e: **11 of 18**. Rows with a product context graded: 3180, 3189,
3195 6f742a3, 3195 611e1aa, 3208, 3227, 3242: **7 of 18** (11 + 7 = 18).
Among the 11: infrastructure 7, grader skew 2, real catch 2. One real catch
is **3167 `tests / replay`**, which is n/r today, so no required-set change
touches it. The other is **3244 8bc540e**, the CodeQL alert enforced only by
`pr-contract`: the one catch a product-only set loses unless the alert duty
moves (decision (a) above).

Verdict: **the ledgers do not show a product-only set missing a catch except
via `pr-contract`'s alert duty**; 28 main-push rows and 11 PR rows are
programme or non-required reds. Decision stays tvofi's.

## Limits

14 PRs are covered; per-head conclusions for the rest need the API
(`dev/audit/harnesses/r10_red_list_lag.py --rows`, needs a token), classed by
the table above. The `gate` job and the n/r names were not read.
