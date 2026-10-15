# Round 10 class sweep: I5 (prose drifts stale against the code)

Class status in `dev/audit/config/bugclasses.json`: **barriered**. The barrier
is `tests/doc_claims.py` with its prose-count census. Baseline: the
`handoff/audit-r10-register` tree at 9355f107d, whose code is 17f1c55fad1b.
Python: `~/.local/state/hpo/venv-ci/bin/python`.

## Enumerator (D14 step 3)

`PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D14/I5/sweep_i5.py`.
The full output is in `D14/I5/sweep_i5.out.txt`.

The enumerator combines the five findings' own seam rules (arms F1 to F5)
with four arms that widen the search to the whole repository:

| arm | seam rule | seams | stale |
|---|---|---|---|
| F1 | `D5/s1/ui_labels.py`: UI labels in README.md and docs/*.md vs strings.json and manifest | all labels | 5 |
| F2 | `D5/s2/card_banner.py`: the doc banner version vs the stamped CARD_VERSION | 1 | 1 |
| F3 | `D5/s3/comment_symbols.py`: backticked identifiers in the comments of 76 modules vs code tokens | 27 missing (26 triaged external) | 1 |
| F4 | `D5/leads/service_count_comments.py`: registry-count words vs 13 registered | 5 | 4 |
| F5 | `D11/leads/stale_structure_refs.mjs`: the D7.md metric count and retired keys | 4 | 4 |
| W1 | every `vX.Y.Z` in README.md and docs/*.md that is presented as current (no since/until/in vX/... marker) and differs from VERSION | 23 | 1 (= F2 site) |
| W2 | `cut_*`, `cross_seam_edges` and `cross_seam_fraction` in prose (dev/governance/**, CLAUDE.md, AGENTS.md, tests/README.md, structure.py comments and docstrings), excluding any sentence with a retirement or history marker | 7 | 3 |
| W3 | "N scenarios" (in digits or words) with N at least half the live set, in tests/stress.py and dev/governance/**, compared with len(tests/stress_budgets.json) = 54 | 9 | 2 |
| W4 | rows that `tools/audit/prose_counts_census.py` REFUSES (a count noun with no disposition) | 2 | n/a |

Result: `stale_total=21`.

- **Positive control.** The run re-finds every judged value exactly: F1=5, F2=1, F3=1, F4=4, and F5 = 1 count + 3 keys.
- **Null control.** `--null` runs W1 to W3 over a synthetic clean fixture, in which the version, keys and scenario counts all agree. It prints `null_stale=0`. F1 to F5 inherit the null controls of their own harnesses.
- **Perturbation.** `--perturb` adds, in memory, one line to D9.md that re-introduces the stale count ("records all 51 scenarios"). The result moves `stale_W3` 2 -> 3 and `stale_total` 21 -> 22.

## Dispositions (D14 step 4)

**Instances. These are the judged sites and are not beyond the findings.** All
17 instances fail their probe at the baseline:

- **D5-s1-01:** README.md:356, docs/configuration.md:23, :43 and :164, and docs/setup.md:70.
- **D5-s2-01:** the docs/dashboard-card.md:828 banner. W1 also finds this site.
- **D5-s3-01:** the coordinator.py:1976 `money_currency` comment.
- **D5-s3-51:** \_\_init\_\_.py:80, :266 and :365 (two statements).
- **D11-s1-51:** D7.md:13, :17 and :18, and tests/structure.py:369. W2 also finds D7.md:18 and structure.py:369.

**Instances beyond the findings (2).** Each probe is
`sweep_i5.py | grep '^STALE W3 <site>'`, which gives 1 at the baseline:

- **`dev/governance/dimensions/D9.md:15`:** *"rss_peak_mb/traced_peak_mb record all 51 scenarios"*. tests/stress_budgets.json records 54 scenarios, each with `rss_peak_mb` and `traced_peak_mb`. The sentence sits inside the owner's quoted brief, so this is a policy file, and the fix needs the owner's approval before it merges.
- **`tests/stress.py:4602`:** this present-tense comment says the captured baseline *"solves the same fifty-one scenarios"*, but the set is 54.

**Guarded:**

- F1's other labels, F4's services.py:1 "thirteen services", and the "13 services" counts in README.md:693, docs/configuration.md:946 and docs/architecture.md:64 and :179. These counts are guarded by doc_claims' service-count shape. The labels and services.py:1 are guarded by nothing permanent: they agree today only because F1 and F4 check them, so their protection is the proposed barrier below.
- tests/structure.py:143 and :365. These mark the key as retired, which is the guard the sentence carries.

**Not applicable:**

- **The other 22 version literals in W1.** Each is historical ("since v5.0.0", "until v4.1.0", "in v5.0.0", "(v6.2.5)").
- **W2's tests/structure.py:228 and :1960.** Both describe history (#1539, and "was an unlimited raise"). The live identifiers `cut_costs` and `cut_fetch` are code and are skipped.
- **W3's tests/stress.py:219, :3041, :4879 and :5245, and fixer.md:194.** These describe past runs (#949, round 4, R9 F2.5).
- **tests/stress.py:3407.** This is a synthetic `range(51)` fixture.
- **tests/stress.py:522 and :565.** "eleven scenarios of slack" and "ten of the fifty-one" count subsets, not the whole set, and fall below W3's half-set cut.
- **W4's docs/dashboard-card.md:537 "24 months" and :678 "about 30 samples".** Both hold today: ledger.KEEP_MONTHS = 24 and const.SOLAR_APERTURE_MIN_SAMPLES = 30. No arm prices them, so they are unpriced but true.
- **F3's 26 triaged "external" identifiers.** These are HA, MQTT or entity names, and harness paths.

## Proposed barrier

The class is barriered, yet all five findings and both beyond-finding sites
passed `tests/doc_claims.py` (169 checks pass at baseline). Proposal: fold
F1 to F5, W2 and W3 into doc_claims as arms that execute production code, and
give the W4 census rows a disposition that reads `KEEP_MONTHS` and
`SOLAR_APERTURE_MIN_SAMPLES`.

The arms run in seconds: one full sweep took under 30 s wall time, most of it
in comment_symbols.

Limits:

- W1 and W3 separate historical from current prose with marker regexes, and those regexes were tuned on this tree. A present-tense stale line that happens to carry "#NNN" nearby is missed.
- W3 covers only the stress scenario set. The golden-scenario counts (55 and 56) are another set and are not priced here.
