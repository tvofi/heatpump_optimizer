Group: R10-FLOW-YIELD-PROBE

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13, expedite) asks two things: why real-catch blocks per reviewed PR fell from 0.52 to 0.15, and what threshold to recommend for the review-strength guardrail. The study record is `dev/audit/rounds/round10/D13/yield-probe.md`. Every figure in it comes from `tools/audit/seat/review_strength.py`, which reads the bus over git only, takes its fact strata `--as-of` the latest window's until, and is self-tested and wired into `governance.yml` `instrument-self-tests`. No production code, budget, `VERSION`, manifest or claim file is touched.

This is a round-4 re-cut under fixer.md's three-round rule. The round-3 verdict blocked on a class: one-line mutants of `review_strength.py` that pass every self-test check. This round closes the class by enumeration rather than by instance:

- **The enumerator.** `dev/audit/harnesses/r10_review_strength_mutants.py` parses the file with `ast` and yields one mutant per site per replacement, across these operator classes: ordering, comparison, branch, threshold, class word, arithmetic, statement deletion and keyword deletion. Its header states each rule. It runs every mutant against `--self-test` and exits 1 on any survivor that has no written disposition, and on any disposition that matches no survivor.
- **The self-test.** It grows from 31 to 76 checks. The new fixture cases cover:
  - the guardrail's ordering, ties and boundaries;
  - a findings-only group;
  - PRs of 149, 150, 599 and 600 lines, with binary files;
  - `blueprints/`;
  - an octopus merge, a one-parent merge and an evil merge;
  - `-pr` and empty resume branches;
  - a nonce-less verdict and archive probe tags;
  - `main()` end to end against a hand-derived golden, plus each stratum alone, the refusals and `--fetch`.
- **Two tool defects the sweep surfaced, now fixed.**
  - `--as-of` earlier than a window's verdicts raised `KeyError`. Those PRs now print as their own `(unreviewed at T)` row.
  - A block that names no class was labelled `(merge)`. It is now `(no class)`.
- **Guardrail input order.** The guardrail now takes each PR's earliest verdict whatever order its input arrives in, and breaks ties by PR number.
- **The real-catch list.** The study record now states the list in full, and the self-test pins `REAL_CATCH` to it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DGdWepKSLE5G9a1v3Lviac

## Head

The code head is `80b4f2760` (full SHA in `git rev-parse handoff/r10-flow-yield-probe`). It has three commits on top of the reviewed head `eb9f7e89d0b258ca66a8d9757df0156a776b7332`:

- `7f251a783` merges `origin/main` at `93e6a63d2855651448a2b8f677b392feddc03c99` (a merge, never a rebase, and clean).
- `4a64049e0` adds the self-test cases, the two tool fixes, the sweep harness and the real-catch list line.
- `80b4f2760` adds the `tests/closures.json` INERT READS entry for the new harness under `tests/harness_headers.py`. `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` wrote it, after which the predictor prints `no closures or fast red predicted against 93e6a63d2855`.

Measured 2026-10-22T02:44Z–03:30Z (`date -u`), with `origin/main` at `93e6a63d2855` and `origin/handoff/audit-r10-roster` at `306a96d5f21f`.

The fix review's items:

- N3, the guardrail ordered by PR number, is killed by four checks (see Mutation proof). Carry: dismissed: fixed in this pull request (item 7a3c91e2)
- N6, the origin predicate without `findings`, is killed by the R1-FINDS check and the golden. Carry: dismissed: fixed in this pull request (item 8b4d02f3)
- N1 and N2, the 600-line cut moved to 700 or 650, are killed by the 599/600 size check and the golden. Carry: dismissed: fixed in this pull request (item 9c5e13a4)
- The round-4 self-test cases for N3, N6, N1 and N2 have landed. Carry: dismissed: fixed in this pull request (item ad6f24b5)
- N4, N7, N8 and N9 are each killed by a named check (see Mutation proof). Carry: dismissed: fixed in this pull request (item be7035c6)

## Mutation proof

**The class rule.** `python3 dev/audit/harnesses/r10_review_strength_mutants.py` is the command that enumerates the class's seams. Its header lists the operator classes:

- every `sorted`/`max`/`min`/`any`/`all` swap and slice bound (ordering);
- every comparison operator (comparison);
- every `and`/`or` arm, `not`, and `if`/conditional test, forced either way (branch);
- every int as n±1 and every float as ×½ or ×2 (threshold);
- every string literal emptied and every tuple, list or set element dropped (class words, which covers each `REAL_CATCH` word and each product prefix);
- every `+ - * / **` (arithmetic);
- every statement replaced by `pass`, and every keyword argument dropped.

It skips the docstring, the imports, `ROOT`, the self-test functions, type annotations and human-readable text (`help=`, `metavar=`, and the arguments of `print`, `.error` and `SystemExit`).

At the head, under `/opt/hpo/venv-ci/bin/python` (3.14), it prints `RESULT mutants=799 killed=787 survived=12 disposed=12 undisposed=0 stale=0` (rc=0). Every surviving seam and its disposition:

| survivor | disposition |
|---|---|
| `load`: `m[4] or ''` loses its `''` arm | equivalent: `cls` None and `''` read alike (stratum's `or`, the REAL_CATCH test) |
| `pr_facts`: `if mb else []` forced True | equivalent: with no merge base the size is `?`, and `files` stays empty either way |
| `pr_facts`: drop `check=` on the numstat `git diff` | equivalent: the diff runs only with a merge base, so it cannot exit non-zero |
| `pr_facts`: numstat `split('\t', 2)` → 3 | equivalent: numstat quotes any path holding a tab |
| `pr_facts`: `g[1]` → `g[0]` | equivalent: GROUP_RE's one group is its whole match |
| `guardrail`: `cdf < ALPHA` → `<=` | equivalent: no binomial CDF equals 0.05 in floating point (none for N ≤ 5 on a 1e-5 p0 grid); "below 0.05" is R13's wording |
| `main`: `--repo` default dropped | unpinned: the default is the running checkout; the fixture must pass `--repo` |
| `main`: `--tree` default dropped, or `'origin/main'` → `''` (2 mutants) | unpinned: the fixture has no `origin/main` and passes `--tree` |
| `main`: `--window` default dropped | equivalent: `not a.window` refuses None and `[]` alike |
| `main`: `split('=', 1)` → 2, and `split('..', 1)` → 2 | equivalent: a window spec holds one `=`, and an ISO stamp holds no `..` |

**The verdict's named mutants**, each applied by exact replacement in a scratch root and run with `--self-test`. The runner is a scratch probe, and the sweep above enumerates a superset of them. Unmutated: `review_strength self-test: 76 checks, 0 failed`.

| mutant | at eb9f7e89 | at head | failing checks at head |
|---|---|---|---|
| N1 `lines < 600` → `< 700` | survived (31, 0 failed) | 2 failed | size: 149+binary S, 150+binary M, 599 M, 300+300 L; main golden |
| N2 `lines < 600` → `< 650` | survived | 2 failed | the same two |
| N3 guardrail `sorted(first, key=…)` → `sorted(first)` | survived | 4 failed | guardrail LATEST N; orders by FIRST VERDICT, not PR number; PR first reviewed at until; first-verdict tie |
| N4 guardrail `v["t"] < until` → `<=` | survived | 1 failed | guardrail: a PR first reviewed exactly at until (7, 03:00) is outside |
| N6 drop `or grp.get("findings")` | survived | 2 failed | origin: a group listing findings alone is finding; main golden |
| N7 pr_facts `v["t"] < until` → `<=` | survived | 1 failed | as of: a verdict exactly at T is after T |
| N8 drop `"blueprints/"` | survived | 2 failed | product: blueprints/ is product; main golden |
| N9 `len(parents.split()) == 2` → `>= 2` | survived | 3 failed | size 599/600 check; merge join: octopus and one-parent are not merges; main golden |

## Null control

- **The sweep's null is M0.** The unmutated module, re-emitted by `ast.unparse`, prints `review_strength self-test: 76 checks, 0 failed` before any mutant runs. A harness that killed everything would fail M0.
- **The sweep's baseline end.** The same harness, run at `eb9f7e89` with the head's study record beside it, prints `RESULT mutants=786 killed=484 survived=302 disposed=12 undisposed=290`, so the 31-check self-test left 290 undisposed seams open. The 12 dispositions match the same 12 equivalent or unpinned seams at both ends.
- **The named-mutant null.** At eb9f7e89 all eight print `31 checks, 0 failed` (see the table), as the verdict found.
- **No figure moves.** The study bundle (Figures) printed by the eb9f7e89 tool and by the head's tool over the same fetched bus is byte-identical: `diff bundle_old bundle_new && echo BUNDLE-IDENTICAL` prints `BUNDLE-IDENTICAL`. The ten back-test guardrail lines are identical too (`BACKTEST-IDENTICAL`). The real bus has no PR first reviewed after the as-of time, no classless block shown as `(merge)` in any window, and no first-verdict tie at a slice edge. The new `(no class)` and `(unreviewed at T)` rows print in none of them (`grep` finds neither in the bundle).
- **The fixture golden's null.** Every row was checked by hand against the fixture's 18 verdicts before it was frozen. The N1, N2, N6, N8 and N9 mutants each turn it red.

## Figures

The finder's harness is the bundle, re-run at the head after `--fetch` at 02:44Z. The bundle command: `python3 tools/audit/seat/review_strength.py --fetch --window E=2026-10-15T12:37Z..2026-10-19T14:50Z --window L=2026-10-19T14:50Z..2026-10-21T14:50Z --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z --by kind --by prior-merge --by origin --by size --by product --by fixer --by class --by kind+origin --roster origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`.

It prints `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`. Both refs are resolved at 15:15Z, so later commits on main and the roster move neither. The bus count is printed on the tool's `verdicts on the bus` line and grows as reviews land; no figure below depends on it, because every window ends by 15:15Z.

- Baselines:
  - `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `PRs 112 verdicts 257 real 58 (0.52/PR) book 65 (0.58/PR)`.
  - The bundle's `all L` row prints `PRs 47 ... real 7 (0.15/PR) book 30 (0.64/PR)`.
  - `--window A=2026-10-19T11:00Z..2026-10-21T11:00Z` prints `PRs 35 ... real 2 (0.06/PR)`.
- `--window L13=2026-10-21T13:00Z..2026-10-21T14:50Z` prints `PRs 11 verdicts 16 real 4`.
- `all` rows (P1 / P2 / L1 / S), real/PR: 0.90 (43/48), 0.36 (14/39), 0.08 (3/39), 0.36 (5/14). Incidence: 25/48, 10/39, 3/39, 4/14.
- Strata (P1 / P2 / L1), real/PR:
  - finding: 1.08 (40/37), 0.29 (5/17), 0.08 (1/13);
  - `L>=600`: 1.10 (22/20), 0.69 (11/16), 0.08 (1/13);
  - product True: 1.21 (17/14), 0.22 (2/9), 0.14 (1/7).
- Re-weights 0.50, 0.89, 0.85: L1's per-stratum PR counts times P1's per-stratum real/PR, over 39, from those rows.
- Reviewer kind, real/PR:
  - cloud: 6/31 (P2), 3/24 (L1), 5/14 (S);
  - local: 43/48 (P1), 8/14 (P2), 0/20 (L1);
  - P2 cloud+finding 3/13, local+finding 2/8.
- Fixer first-pass (P1 / P2 / L1): opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6.
- Prior-merge: `after-a-merge-verdict` reads 0 real in every window, with 22 verdicts in E and 12 in L. `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z --by prior-merge` prints `after-a-merge-verdict A PRs 22 verdicts 33 real 0`.
- Classes (P1 / P2 / L1): `harness` 25 / 3 / 2; `carry-missing` 3 / 15 / 7.
- Extended list: `--real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red` over windows P1, P2, L1, S and POST=2026-10-18T08:00Z..2026-10-21T15:15Z, `--by kind`.
  - P2 0.49 (19/39), L1 0.21 (8/39).
  - Cloud incidence 8/31, 7/24, 4/14.
  - Local L1 0/20.
  - POST incidence 24/85.
- Back-test: the extended list with `--guardrail 30 --p0 0.28` at ten `until` points, from 2026-10-20T01:00Z to 2026-10-21T13:00Z in 4-hour steps (W from 2026-10-15T12:37Z). Incidence is 8, 8, 8, 8, 7, 7, 6, 5, 5, 5 of 30. Every line reads `ok`, the lowest being 5/30 at P = 0.116.
- Self-test: `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 76 checks, 0 failed` (3.11 and 3.14).
- Sweep: `python3 dev/audit/harnesses/r10_review_strength_mutants.py` prints `RESULT mutants=799 killed=787 survived=12 disposed=12 undisposed=0 stale=0`.

## Red checks

- **Local runs at `80b4f2760`.** All with `PYTHONPATH=tests/hastub`, `PREPR_SKIP_CLOSURES=1` and `/opt/hpo/venv-ci/bin/python`:
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/entities.py`, `tests/harness_headers.py`).
  - `ALL 2382 ENTITY CHECKS PASSED`; `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tmp_paths.py --check`: 0 refused.
  - `selftest_wiring.py --check`: `74 self-testing, 74 wired, 0 unwired`.
  - `ci_predict.py --base origin/main`: no closures or fast red predicted.
- **Check-runs API at the reviewed head `eb9f7e89` (49 check-runs).** Every gate check is success or skipped, `pr-contract` included (twice). The one failure is `nightly-status`.
- **The three new commits** carry no check-runs yet. The orchestrator's push starts them.
- **`nightly-status`** grades `main`'s scheduled run. This diff touches nothing it reads, so it is not this pull request's. Carry: dismissed: grades main, not this diff (item 2579n1)

## Forward-carry

- The guardrail threshold, the extended class list, the seat-family arm and the planted-defect calibration are on R10-ORCH-MACHINERY's roster carry, and the reviewer-model-in-dispatch control is routed to the same group. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY (item b8b28b28)

## Friction

none
