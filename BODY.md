Group: R10-FLY-YIELD-GUARD

Refs #2505

R10-FLY-YIELD-GUARD (a fly-in from R10-ORCH-MACHINERY's re-cut, row G) builds the review-strength guardrail that R10-FLOW-YIELD-PROBE (#2579) split out in its round 6 (item b8b28b28). The guardrail has four parts: a threshold, the extended class list, a seat-family arm and a planted-defect calibration. It lives in one module, `tools/audit/seat/review_strength.py`, as `--guardrail`. It is report-only. Owner ruling R13 holds until the owner adopts a threshold: a trip prints `would-trip: audit the last reviews with a planted defect` and changes no exit code.

- **Threshold.** Each arm takes the last N PRs by first verdict before the latest window's until, with ties broken by PR number. It reads their incidence k/N against the binomial P(X <= k | N, P0), with P0 = 0.28 and ALPHA = 0.05, and trips strictly below ALPHA. The all arm has N = 30 and trips at k <= 4. An arm with fewer than N PRs prints `insufficient` and never trips.
- **Extended class list.** `REAL_EXTRA` holds the record's nine words outside the study's list. `--guardrail` widens REAL by them. A last line names every blocked word that is neither real nor taught (`VERDICT_CLASSES`), so a new word is routed for classifying and never silently counted as bookkeeping.
- **Seat-family arm.** There is one arm per verdict kind, `cloud` and `local`. Each has N = 20, counts only the verdicts that family gave, and trips at k <= 1. At k = 2, P = 0.0526, which is above ALPHA, so 2 of 20 reads `ok`: this is the check point carry (2) asks for.
- **Planted-defect calibration.** The self-test (`_self_test_guardrail`) reads each word's realness through `load`, from a real verdict subject. It then plants a miss of every real class at both sides of each arm's line: 4/30 trips and 5/30 does not, 1/20 trips and 2/20 does not. It also checks a null window at the baseline (8/30 and 6/20), which trips nothing; blocks under a bookkeeping word or an unclassified word, which catch nothing; and the insufficient case.

The two figures of the second carry were re-derived at the merge base before being adopted (Figures). Carry (1)'s statistic is incidence (PRs with at least one real catch), not "first-pass merges" as its text says (Friction).

## Head

Code head `b66cbf0bec9734d3c5db66b79d625d3d07fca025`, one commit on PR head `4df5a42f137bbc9392bb41e79f0d9d08ae956a5b`. That PR head is the round-1 code head `a78d45897` plus the orchestrator's merge of origin/main (`b4a6bfbaa`) and its delivery row (`4df5a42f1`). The merge base with origin/main is `0810d5b8f30a`. `git merge-tree --write-tree origin/main HEAD` is clean against origin/main `5c0ee1093` (2026-10-25T00:40Z). The round-2 commit changes only `dev/programme/carries/carry-201.json`; no production line moved, so the round-1 mutation proof and sweep below still describe `tools/audit/seat/review_strength.py` byte for byte (`git diff 4df5a42f1 HEAD -- tools/` is empty).

## Round 2: the carry block

The round-1 review (review/2765, `Fix review: blocked 4df5a42f1 carry-missing`) found that all three forward-carries named R10-ORCH-MACHINERY, which the roster records as `resume.stage: absorbed`, so nothing dispatches them. Each carry is now routed to a destination that a seat reads:

- **The reviewer's model** and **the planted-defect audit dispatch** change what dispatch must do, so they go to the live group **R10-ORCH-DISPATCH-REG** (`resume.stage: not-started`, after R10-ORCH-LEDGER). Its brief owns `bus.sh dispatch` and the worker registry, and its carries already make the dispatch half of standing-dispatch.md a beat job of its registry. One owner, not two: R10-ORCH-LEDGER's PR (#2671) is open and the model is written at dispatch. This seat's brief allows writes only to its return refs, so it cannot push `handoff/audit-r10-roster`. Both `append-carry` ops were run with `tools/audit/seat/roster_edit.py` without `--push`, from a fresh origin/main checkout as `--lint-cwd`. Each printed `lint gate: TOTAL: 0 error(s) from a fresh origin/main checkout` and a local commit on top of `handoff/audit-r10-roster` tip `3d1c5efcc`. **Not yet in the tree: the roster seat must land them, and the roster branch SHA is owed to this body before merge.** The op text is under Forward-carry, verbatim.
- **The owner's call on a trip** goes in the tree in this PR, as an entry of `dev/programme/carries/carry-201.json` (#201, the programme's standing issue, which no live group lists). Its `stage` now names the owner's decision on the guardrail's trip, following the file's existing owner-decision entry for the off-host liveness barrier.
- **The review's non-blocking finding 2** (the `unclassified` words make k a lower bound) is carried into the same file. Its destination is the D13 seat of a later audit round, which the file's `stage` already names: R10-FLY-YIELD-GUARD ends at this merge, so the review's `Carry: R10-FLY-YIELD-GUARD` would reach no seat after it. Re-measuring the review's figure turned up a fact the carry now holds. The review's nine words do not move today's lines, but all 41 unclassified words do: the all arm goes from 3/30 would-trip to 6/30 ok (Figures).
- **The review's finding 1** (`carry_audit.py` reads `absorbed` as live) is the review's own carry to R10-ORCH-ROSTER-SCHEMA. This body does not touch it.

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

Figures not marked round 2 were taken in round 1 at merge base `145bfe197` or at code head `a78d45897`, with the bus fetched at 2026-10-24T10:20Z; no production line has moved since. Python 3.14.

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
- Round 2, with the bus fetched at 2026-10-25T00:37Z (812 verdicts, 0 outside the grammar). Each command is `python3 -I tools/audit/seat/review_strength.py --window X=2026-10-01T00:00Z..<T> --guardrail`:
  - T = 2026-10-24T10:00Z: all 3/30, P = 0.0166, would-trip; cloud 3/20, P = 0.1466, ok; local 0/20, P = 0.0014, would-trip. This matches round 1's back-test at the same T, on a bus that grew from 733 verdicts at the base fetch.
  - T = 2026-10-25T06:00Z (after the fetch, so every verdict on the bus): all 2/30, P = 0.0041, would-trip; cloud 2/20, P = 0.0526, ok; local 0/20, would-trip.
  - Null control, T = 2026-10-20T12:00Z: all 8/30 (P = 0.5282), cloud 7/20, local 8/20, every arm ok.
  - The unclassified line names 41 words at 10-24T10:00Z and 51 at 10-25T06:00Z (`tail -1 | tr ',' '\n' | wc -l`).
  - Sensitivity at 10-24T10:00Z: `--real-extra` set to the review's nine words leaves all three arm lines identical to the unwidened run, which reproduces the review's figure. The perturbation that shows the widening is read: `--real-extra` set to all 41 words gives all 6/30, P = 0.2238, ok; cloud 6/20; local 0/20, would-trip. So the all arm's trip rests on how the other 32 words are classified.
- Round 2 gate at `b66cbf0be`, with `PYTHONPATH=tests/hastub` and BASH_ENV unset:
  - `tests/closure.py select` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. The one script is `tests/entities.py`, whose closure holds `carry-201.json`.
  - `tests/entities.py` prints `2 of 2425 ENTITY CHECKS FAILED` (rc=1) at the head and, in a separate worktree, at merge base `0810d5b8f`. A `diff` of the two runs' FAIL lines differs only in timing figures and in the set order of a planted `a8:register_once` duplicate fixture. So this is the local environment, not this diff.
  - `node tools/policy/brief_lint.mjs` prints `TOTAL: 0 error(s) across 48 file(s)`, with `carry-201.json` at `0 error(s), 0 warning(s)`.
  - `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `tools/pr/ci_predict.py --base origin/main` prints `no closures or fast red predicted`.
  - `review_strength.py --self-test` prints `114 checks, 0 failed`.

## Red checks

- **CI on PR head `4df5a42f1`** (check-runs API, read 2026-10-25T00:45Z): of 53 runs, none is red. Each run is success or skipped; `tests / ci-ratchet` is skipped.
- **`tests / ci-ratchet`** may be red on main's push CI. The orchestrator reports that GitHub's repo-wide artifacts listing returns 0 bytes and that a hotfix is in flight. It is main's, and this diff does not touch `tests/ci_ratchet.py`.
- Locally nothing is red but the two `tests/entities.py` checks that fail identically at the merge base (Figures, round 2).

## Forward-carry

- **The reviewer's model is still unrecorded per verdict**, so the seat-family arm keys on kind (`cloud` or `local`) only, and a model arm needs the dispatch to write the model where `review_strength.load` reads it. Destination: R10-ORCH-DISPATCH-REG's roster `carry` on `handoff/audit-r10-roster`, op `roster_edit.py append-carry R10-ORCH-DISPATCH-REG @<file>`, lint-gated clean and not pushed (Round 2); the roster SHA is owed here before merge. Text, verbatim: "From #2765 (R10-FLY-YIELD-GUARD, round-1 fix review review/2765): the reviewer's model is not on the bus, so the review-strength guardrail (tools/audit/seat/review_strength.py --guardrail) keys its seat-family arm on the verdict's kind (cloud or local) only, and a model arm cannot be built. The dispatch is the one writer that knows which model a reviewer seat runs, so this group's bus.sh dispatch records it: the dispatched record (and the verdict line it pairs with) carries the reviewer's model, and review_strength.load reads it as a third family beside kind. Precondition, not opportunity: no seat may add a model arm by inferring the model from a ref name, a session title or a timestamp. Control: a reviewer dispatched through dispatch_group leaves its model in the record review_strength reads, and `review_strength.py --guardrail` prints one arm per recorded model; the null control is a verdict whose dispatch predates the record, which must read as kind-only (today's two family arms, unchanged) and never as a guessed model. Re-measure at your merge base: `python3 -I tools/audit/seat/review_strength.py --fetch --window X=2026-10-01T00:00Z..<now> --guardrail` prints three GUARDRAIL arm lines (all, cloud, local) and no model arm." Carry: R10-ORCH-DISPATCH-REG
- **A trip's planted-defect audit is not automated**: the guardrail names the audit and nothing dispatches it. Destination: R10-ORCH-DISPATCH-REG's roster `carry`, the same op and state as above. Text, verbatim: "From #2765 (R10-FLY-YIELD-GUARD, round-1 fix review review/2765): a review-strength guardrail trip names a planted-defect audit that nothing dispatches. `review_strength.py --guardrail` prints `would-trip: audit the last reviews with a planted defect` and stays report-only under owner ruling R13; low incidence is also what a scarce supply of defects produces, and only a defect of a known class planted in a reviewed head, scored caught or missed, separates weak review from scarce defects. Dispatching that audit is this group's work (the dispatch half of standing-dispatch.md becomes a beat job owned by this group's registry). Precondition, not opportunity: the dispatch is built behind the owner's ruling on whether a trip dispatches at all (dev/programme/carries/carry-201.json, the R10-FLY-YIELD-GUARD entry); until the owner rules, a trip dispatches nothing and changes no exit code. Control, once built: a `would-trip` arm line dispatches one audit seat per tripped arm, keyed arm and cut, and a repeat of the same line dispatches none; the null control is an `ok` or `insufficient` arm line, which dispatches nothing. Re-measure at your merge base: `python3 -I tools/audit/seat/review_strength.py --self-test` (every check ok), then `--fetch --window X=2026-10-01T00:00Z..<now> --guardrail` and read which arms trip on the live bus; the trip state is a snapshot of the bus at its fetch." Carry: R10-ORCH-DISPATCH-REG
- **The guardrail trips on today's bus and the owner rules on what a trip does**: all 3/30 (P = 0.0166) at 2026-10-24T10:00Z, and local 0/20 since 10-21; the null cut at 10-20T12:00Z trips nothing. It is report-only under R13 until the owner rules. Destination: `dev/programme/carries/carry-201.json`, the R10-FLY-YIELD-GUARD entry with `effect: narrows`, in this PR's tree. Carry: #201
- **The unclassified block words make every arm's k a lower bound**: widening REAL by all 41 words at 10-24T10:00Z clears the all arm's trip, while the review's nine words do not move it. Destination: `dev/programme/carries/carry-201.json`, the R10-FLY-YIELD-GUARD entry with `effect: invalidates`, whose stage is the D13 seat of a later audit round, owner of REAL's list; P0 is re-derived under any widening. Carry: #201

## Friction

- finding-propagation: unclear: carry (2) of R10-FLY-YIELD-GUARD says the 30-PR arm "trips at 4 or fewer first-pass merges". The arm's statistic is incidence (PRs with at least one real catch), as #2579's back-test evidence (`guardrail_k4.txt`, "incidence 4/30") and the record's recommendation both read. The guardrail implements incidence. Carry: R10-FLY-YIELD-GUARD
