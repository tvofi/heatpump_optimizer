# R11-PROTECTION-CENSUS (round 10): does the tree support B1?

Read-only study, no production or tool code. Written without `gh` or an API
token, so every row that needs a per-pull-request check read is **UNREAD**.
Two tracked ledgers are readable; both are partial, and the census says so.

## Sources and enumerators

| source | window | enumerator | count |
|---|---|---|---|
| `dev/audit/harnesses/r10_rca_ci_critpath_3/runs_red4.json` (API read 2026-11-04 14:00Z, ci.yml push runs on main 4009..4128) | main, 2026-11-02..04 | `python3 -I dev/audit/rounds/round10/protection-census/main_reds.py \| wc -l` | 28 red-job rows: 14 runs x 2 jobs (`tests / ci-ratchet`, `gate`); 8 runs `failure` (16 rows), 6 `cancelled` (12 rows) |
| `dev/audit/rca/ci-red/entries_v7.1.2.tsv` (fix-review blocks citing a red) | PRs #3167..#3244, 2026-11-02..07 | `python3 -I dev/audit/rca/ci-red/entries.py` prints `ENTRIES 18 PRS 14` | 18 entries |

Null control: runs 4080, 4107, 4116 are `success` and yield zero rows (`main_reds.py | awk '$1==4080||$1==4107||$1==4116' | wc -l` prints 0).

## Main-push reds (runs_red4.json)

Runs 4009, 4015, 4028, 4035, 4046, 4055, 4056, 4128 (`failure`) and the six
`cancelled` runs 4036-4045 each carry `tests / ci-ratchet` + `gate` red.
Cause of the ci-ratchet red: **UNREAD** (job logs are not in the tree; only
timings). Class: UNREAD for the 8 failed runs; infrastructure for the 6
cancelled (superseded by the next push, concurrency cancel). These reds are
already on main, i.e. they reached main under the current required set; they
say nothing about a product-only set, since `tests / ci-ratchet` is a product
check in either.

## PR-head reds (entries_v7.1.2.tsv), 18 rows

| PR | head | red | class | evidence |
|---|---|---|---|---|
| 3167 | 7637d66 | tests / replay | real catch (timing budget; runner noise possible) | cpu_ratio 2.615 > 2.173 |
| 3167 | 4e4bb29 | gate | infrastructure | cancelled run, tests/fast+coverage unfinished |
| 3180 | 3f7777a | tests / fast, tests / closures | real catch (rule on non-product harness path) | harness_headers.py depth root |
| 3181 | bb730c1 | gate | infrastructure | codeql / Analyze (python) cancelled |
| 3189 | fd9c5ba | tests / fast | real catch (same rule) | harness_headers.py replay.py:51 |
| 3195 | 6f742a3 | tests / typing | real catch | 9 no-untyped-call |
| 3195 | c383169 | prelude, gate | infrastructure | prelude 8700 s wait expired; also real: 8 unpinned sites |
| 3195 | 611e1aa | gate (tests / mutation) | real catch | unpinned-site refusal; cured by bot commit |
| 3204 | e5381d9 | gate | infrastructure | cancelled |
| 3208 | 327d83e | tests / fast | real catch (same rule) | inlined repo_root differs |
| 3211 | 1fca63c | gate | infrastructure | PR closed unmerged, run cancelled |
| 3217 | 1c42ca3 | gate | infrastructure | codeql python cancelled |
| 3219 | aca5009 | gate | infrastructure (+ body defect) | cancelled; body names stale SHAs |
| 3227 | a52354e | instrument-self-tests, fast | real catch | body_patch.sh:146 bare array expansion |
| 3240 | 79cf40f | gate | grader skew | cross-run deferral, gate judged early |
| 3242 | e836876 | tests / fast | real catch (same rule) | harness_headers.py refuses critpath_fetch.sh:12 |
| 3244 | a258212 | gate | grader skew | three edit-run gates deferring to one another |
| 3244 | 8bc540e | pr-contract / gate | real catch | CodeQL alert 50 py/jinja2/autoescape-false |

Counts by class, counted by hand from the table above: real catch 9, infrastructure 7, grader skew 2 (total 18).
Grader-version product reds: the 2 grader-skew rows are both `gate`, not a
product check; 5 `harness_headers.py` reds sit in `tests / fast`, a product
check, but each is the rule working on the PR's own new harness (real catch).

## Which reds would have reached main under product-only checks?

Of the 18 readable rows, **none** is a `briefs`, `governance / policy-docs` or
`governance / wave-script` red: the reds B1 would stop grading are absent from
this ledger, so the ledger neither shows B1 dropping a real catch nor
showing it saves anything. The only non-product check among them is
`pr-contract` (3244 8bc540e, a CodeQL alert): CodeQL stays outside B1's drop
list, so it would still be graded. **Reds that would reach main: 0 of 18
readable rows; 0 is a statement about this ledger's coverage, not a
finding.**

## Verdict

**The census cannot support B1.** 14 PRs of ~560 round-10 delivery rows are
covered; per-head check conclusions for the rest, and the job logs for the
main ci-ratchet reds, need the API (UNREAD). The enumerator to complete it is
`dev/audit/harnesses/r10_red_list_lag.py --rows` (needs a token). Decision
stays tvofi's. A re-run with a token should add per-head check names for every
round-10 PR and class them by the same table.
