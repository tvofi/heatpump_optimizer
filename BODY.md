Group: R10-FLY-YIELD-GUARD

Refs #2505

R10-FLY-YIELD-GUARD (a fly-in from R10-ORCH-MACHINERY's re-cut, row G) builds the review-strength guardrail that R10-FLOW-YIELD-PROBE (#2579) split out in its round 6 (item b8b28b28). The guardrail has four parts: a threshold, the extended class list, a seat-family arm and a planted-defect calibration. It lives in one module, `tools/audit/seat/review_strength.py`, as `--guardrail`. It is report-only. Owner ruling R13 holds until the owner adopts a threshold: a trip prints `would-trip: audit the last reviews with a planted defect` and changes no exit code.

- **Threshold.** Each arm takes the last N PRs by first verdict before the latest window's until, with ties broken by PR number. It reads their incidence k/N against the binomial P(X <= k | N, P0), with P0 = 0.28 and ALPHA = 0.05, and trips strictly below ALPHA. The all arm has N = 30 and trips at k <= 4. An arm with fewer than N PRs prints `insufficient` and never trips.
- **Extended class list.** `REAL_EXTRA` holds the record's nine words outside the study's list. `--guardrail` widens REAL by them. A last line names every blocked word that is neither real nor taught (`VERDICT_CLASSES`), so a new word is routed for classifying and never silently counted as bookkeeping.
- **Seat-family arm.** There is one arm per verdict kind, `cloud` and `local`. Each has N = 20, counts only the verdicts that family gave, and trips at k <= 1. At k = 2, P = 0.0526, which is above ALPHA, so 2 of 20 reads `ok`: this is the check point carry (2) asks for.
- **Planted-defect calibration.** The self-test (`_self_test_guardrail`) reads each word's realness through `load`, from a real verdict subject. It then plants a miss of every real class at both sides of each arm's line: 4/30 trips and 5/30 does not, 1/20 trips and 2/20 does not. It also checks a null window at the baseline (8/30 and 6/20), which trips nothing; blocks under a bookkeeping word or an unclassified word, which catch nothing; and the insufficient case.

The two figures of the second carry were re-derived at the merge base before being adopted (Figures). Carry (1)'s statistic is incidence (PRs with at least one real catch), not "first-pass merges" as its text says (Friction).

## Head

Code head `a78d4589742cfa405ff350735e84009e4fa0f2c9`, two commits on merge base `145bfe197b9e7c09eb90bedadec44c6bc19d679d`. It is not merged with origin/main (`e97f5749b`, 66 commits ahead at 2026-10-24T14:35Z). `git diff --stat HEAD...origin/main -- tools/audit/seat/review_strength.py dev/audit/harnesses/r10_review_strength_mutants.py tools/audit/seat/INSTRUMENTS.md dev/audit/rounds/round10/D13/yield-probe.md .claude/workflows/web-fix-wave.js tests/throwaway_git.py` is empty, and `git merge-tree --write-tree origin/main HEAD` is clean.

## Mutation proof

**Failing test first.** With only the new self-test in place, at the merge base's production code, `python3 -I tools/audit/seat/review_strength.py --self-test` stops with `NameError: name 'REAL_EXTRA' is not defined`, rc=1.

**Hand mutants at the head.** Each production line was changed one at a time and then restored; `cmp` against the head copy prints identical afterwards. Each run is `python3 -I tools/audit/seat/review_strength.py --self-test`:

- M1, the trip predicate `if cdf < ALPHA` forced to `if False`: `114 checks, 5 failed`, among them `FAIL: a planted miss of each class trips: 4/30 trips the all arm (P = 0.0495), 5/30 does not (0.1161)` and `FAIL: the seat-family arm at the carry's point: 2/20 is ok (P = 0.0526 > ALPHA), 1/20 trips (0.0123)`.
- M2, the family filter dropped: `2 failed`, among them `FAIL: each family arm reads only its own seats: cloud 6/20 ok, local 1/20 trips, the all arm the last 30`.
- M3, `--guardrail` no longer widening REAL by `REAL_EXTRA`: `1 failed`, `FAIL: main --guardrail counts the extended list and closes its output with one line per arm and the unclassified words`.
- M4, a real block no longer counted as a catch: `8 failed`.
- M5, `unclassified` no longer excluding taught words: `3 failed`.
- M6, the insufficient arm removed: `3 failed`, among them `FAIL: fewer PRs than N is insufficient, never a trip`.
- M7, `P0 = 0.28` changed to `0.24`: `4 failed`.
- M8, the `local` arm dropped from `ARMS`: `1 failed`.
- M9, `rule-dropped` dropped from `REAL_EXTRA`: `2 failed`, among them `FAIL: REAL_EXTRA is the study record's nine words outside the list, word for word`.

**The class rule** is the finder's harness for this module: `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4`, whose header states the operator classes and BOUNDS. `_self_test_guardrail` joins its `SKIP_DEFS`, as the other self-test helpers are. Results:

- At the first code head `8486800c8`: `RESULT mutants=3090 killed=3016 survived=74 disposed=50 undisposed=24 stale=0`, rc=1.
- The second commit kills 20 of those 24 with new checks: exact arm lines from `main`, a first-verdict order that a PR number or a re-review would move, a sorted and until-bounded unclassified list, and `-` when the list is empty. It disposes the other 4 in `DISPOSED`, each with its reason:
  - `cdf < ALPHA` → `<=`, which is equivalent because no CDF at the arms' N and P0 equals 0.05;
  - a parser registration swap;
  - two moves of the pure `until` binding.
- At the head `a78d45897`: `RESULT mutants=3090 killed=3036 survived=54 disposed=54 undisposed=0 stale=0`, rc=0, from 13:33Z to 14:35Z, with M0 at `114 checks, 0 failed`.

`## Unpinned sites`: n/a. `tools/pr/ci_predict.py --base origin/main` lists no unpinned site.

## Null control

- **M0.** The unmutated head prints `review_strength self-test: 114 checks, 0 failed`. The sweep's M0 run prints the same.
- **The finder's harness at the base.** The same harness at merge base `145bfe197` prints `RESULT mutants=2612 killed=2562 survived=50 disposed=50 undisposed=0 stale=0`, rc=0, from 10:24Z to 11:53Z, with M0 at `100 checks, 0 failed`. The 50 survivors disposed at the base are disposed identically at the head, and the head adds only the 4 new ones: a `diff` of the two runs' `DISPOSED` lines, line numbers stripped, shows only those 4 lines added.
- **The back-test is the guardrail's own null control on the real bus.** On it, the all arm trips at no cut point from 10-17 to 10-23. The local arm trips only from 10-21T06:00Z on, the trough the record found (L1 local 0/20, `(1 − 0.28)^20 = 0.0014`). Had the all arm been miscalibrated low, it would have tripped at 10-21T06:00Z (5/30, P = 0.1161). Had the family arm not been filtering, it would have read the same lines as the all arm.
- **The p0 baseline reproduces at the base.** Over the post-cloud window it reads 24/85 (Figures). Had the bus moved under the record, the count would differ.

## Figures

Every figure below was taken at merge base `145bfe197` or at the head named in `## Head`, with the bus fetched at 2026-10-24T10:20Z. Python 3.14.

- Carry (2) re-derived. The rule is `P(X<=k|n,p) = sum(comb(n,i) p^i (1-p)^(n-i), i=0..k)`, evaluated at p = 0.28 by a stand-alone `math.comb` loop at the base, which is the head's `binom_cdf` expression:
  - n = 30: k = 3 gives 0.0166, k = 4 gives 0.0495, k = 5 gives 0.1161. So the 30-PR arm trips at 4 or fewer, as carry (1) says.
  - n = 20: k = 1 gives 0.0123, k = 2 gives 0.0526, k = 3 gives 0.1466. So the family arm trips at 1 or fewer, and ALPHA = 0.05 reads 2 of 20 as `ok`.
  - Null control: the neighbouring k on each side falls on the other side of ALPHA, so the line is not an artefact of rounding.
- P0 = 0.28 re-derived at the merge base: `python3 tools/audit/seat/review_strength.py --fetch --real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red --window POST=2026-10-18T08:00Z..2026-10-21T15:15Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --by kind` prints `all POST ... incidence 24/85 (0.28)` and `local L1 ... incidence 0/20 (0.00)`, with the bus at 733 verdicts and 0 outside the grammar. The bus count is the bus, not a figure this body defends.
- Back-test at the head: `python3 -I tools/audit/seat/review_strength.py --window X=2026-10-01T00:00Z..<T> --guardrail` at nine values of T. The `all` arm:
  - 10-17T00:00Z: 13/30, `ok`;
  - 10-18T08:00Z: 19/30, `ok`;
  - 10-19T14:50Z: 9/30, `ok`;
  - 10-20T12:00Z: 8/30, `ok`;
  - 10-21T06:00Z: 5/30, P = 0.1161, `ok`;
  - 10-21T13:00Z: 5/30, `ok`;
  - 10-21T15:15Z: 7/30, `ok`;
  - 10-23T00:00Z: 8/30, `ok`;
  - 10-24T10:00Z: 3/30, P = 0.0166, `would-trip`.

  The `local` arm reads 0/20, P = 0.0014, `would-trip` from 10-21T06:00Z on; before that it reads 10/20, 15/20, 15/20 and 8/20. The `cloud` arm is `insufficient` before 10-19 and `ok` at every later T (lowest 3/20, P = 0.1466).
- The sweep figures at both ends are under Mutation proof and Null control, with their commands.
- Local gate, with `PYTHONPATH=tests/hastub`:
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <d>` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.
  - The `run_always` lines print `claims hygiene: 145bfe197b9e7c09eb90bedadec44c6bc19d679d ok`, `ALL 117 closure shrink pins PASSED`, `layout self-test: ok` and `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `python3 -I tools/audit/seat/ref_privacy.py --check` prints `0 refused`, `tmp_paths.py --check` prints `0 refused`, and `python3 tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`.
  - `tools/pr/ci_predict.py --base origin/main` prints `no closures or fast red predicted`.
  - `tests/entities.py` prints `2 of 2425 ENTITY CHECKS FAILED` both at the head and at the merge base, from a separate worktree with the same Python. Their `FAIL` lines are identical apart from timing figures, so this is the local interpreter, not this diff, and entities is scoped out here.

## Red checks

- **`nightly-status`** is red on main's ancestry. It grades main's scheduled run, not this diff, which touches nothing it reads.
- **`tests / ci-ratchet`** may be red on main's push CI. The orchestrator reports that GitHub's repo-wide artifacts listing returns 0 bytes and that a hotfix is in flight. It is main's, and this diff does not touch `tests/ci_ratchet.py`.
- Locally nothing is red but the two `tests/entities.py` checks that fail identically at the merge base (Figures).

## Forward-carry

- **The reviewer's model is still unrecorded per verdict**, so the seat-family arm keys on kind (`cloud` or `local`) only. A model arm needs the dispatch or the ledger to write the model onto the bus. That is a ledger and dispatch concern, not this module's. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY
- **A trip's planted-defect audit is not automated.** The guardrail names the audit when it trips. Planting a defect of a known class in a reviewed head, and scoring caught or missed, needs dispatch. The self-test calibrates the guardrail itself, not the reviewers. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY
- **The guardrail would trip on today's bus.** At 2026-10-24T10:00Z the all arm reads 3/30 (P = 0.0166), and the local arm has read 0/20 since 10-21. Both are report-only under R13. Whether to run the planted-defect audit is the owner's call. Destination: `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY

## Friction

- finding-propagation: unclear: carry (2) of R10-FLY-YIELD-GUARD says the 30-PR arm "trips at 4 or fewer first-pass merges". The arm's statistic is incidence (PRs with at least one real catch), as #2579's back-test evidence (`guardrail_k4.txt`, "incidence 4/30") and the record's recommendation both read. The guardrail implements incidence. Carry: R10-FLY-YIELD-GUARD
