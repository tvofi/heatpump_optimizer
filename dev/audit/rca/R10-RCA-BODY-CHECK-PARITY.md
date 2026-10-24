# R10-RCA-BODY-CHECK-PARITY: a body check pr-contract runs has no pre-open twin

Root-cause seat (`root-cause.md`, `defect-root-cause.md`), beside R10-FLOW-JIDOKA and not inside it. Measured at origin/main `12032c43cc321160ab0278f417c9575b786a03b4` on 2026-10-23, from 13:20Z to 13:45Z. Every number below is this seat's own measurement unless it says otherwise. No code is pushed. The barrier is the JIDOKA fixer's to build, and this seat adds three requirements to it (section 4).

**Result: state (c). Cost test: build. Seconds per body push against at least 43 min of repair in 14.3 h. Barrier verdict: the parity test is necessary but not sufficient as briefed. A name-level parity over `pr-contract.yml` would not have caught P-F. It also passes a twin whose inputs differ from CI's, and this seat measured one red of that shape in the window.**

## Status at `origin/main` `50af6174f` (2026-10-24)

The analysis below was measured at `12032c43c` on 2026-10-23 and is kept as written;
only the points the tree has since moved are listed here, each by its command.

- **Neither carry destination has started.** `wave-r10-groups.json` has `R10-FLOW-JIDOKA`
  and `R10-POLICY-LINT-FAMILY` both at `resume.stage: not-started`. G1 to G3 are open.
- **The table's "full prepr (open_pr)" cell for `carry_audit` is now stale; the
  `--body-check` cell is not.** `5cee85cec` (U9d) gave `ci_predict.py` a `--body` option
  (`carry_preds`, which calls `carry_audit.audit`), and `tools/pr/prepr.sh` step 6d
  passes it the body (`predict_line origin/main "$UNPINNED_SITES" "${1:-}"`, line 3142),
  so a full prepr over a body now runs the carry check. `body_push.sh` does not:
  `grep -c carry_audit tools/pr/prepr.sh tools/audit/seat/body_push.sh` prints 0 for
  both, its `ci_predict.py` call (line 25) passes no `--body`, and `--body-check` runs
  step 7 only. The four recorded bodies would still pass at the handoff moment; the
  open now refuses them where it did not, which is the same late refusal.
- **The `fixer` dispatch still never names `carry_audit`.** The only mention in
  `tools/audit/seat/cloud_dispatch.py` is the reviewer text (line 131).
- **The two grammars still differ.** `isNone` is at `tools/policy/policy_lint.mjs:6244`
  (it was line 6076) and `NONE_ITEM` at `tools/audit/carry_audit.py:94`.
- The 14 reds, 4 PRs, 58 of 176 and the timings are that window's measurements and are
  not re-run.

## 1. Cause, reproduced at each instance

**Named cause.** Two programs grade `## Forward-carry`, and their grammars differ. Only one of them runs before a pull request opens.

- `policy_lint.mjs` (`isNone`, line 6076, from `6194234bc`, 2026-09-19) accepts `none` followed by prose on the same line. A section that is not `none` must name a path.
- `carry_audit.py` (`NONE_ITEM`, line 94, from `8011549f1`, 2026-10-18) accepts only a bare `none` or `n/a: <reason>`. Its `Carry:` grammar (`seg_dests`) takes a group, an issue, an O-brief or `dismissed:`. A path after `Carry:` reads as prose, so the item is unrouted.

The side that moved is CI. `8011549f1` added the carry step to `pr-contract.yml` and to `queue_pre_flight.py`, and left `tools/pr/prepr.sh` untouched. `prepr.sh --body-check`, added on 2026-10-22 by `2fe11ffbc` and run by `body_push.sh`, calls `body_line`, which runs `policy_lint.mjs` only. `open_pr.sh` calls `app_push.sh`, which calls full prepr, and that has no carry step either. `app_push.sh` line 240 says as much: "`carry_audit.py check`, which prepr does not run". Only `app_push.sh --row-only` and `body_patch.sh` run the carry check, and both act after the open.

Reproduction: each instance's handoff-body tip was run through `prepr.sh --body-check` in a detached worktree at that topic's `handoff/<topic>` head, as `body_push.sh` runs it. Each was then run through `carry_audit.py check --body` from the same tree.

| PR | topic | handoff head | body commit | `--body-check` | `carry_audit` | unrouted item |
|---|---|---|---|---|---|---|
| #2643 | r10-fly-no-footers-ignore | `227e228f` | `21af14bd` | rc 0 (1) | rc 1, 2 unrouted | `Carry: dev/programme/rosters/wave-r10-groups.json (group …)`: a path where a group belongs; plus a lead "carried to R10-FLY-NO-FOOTERS" with no marker |
| #2658 | r10-ci-layout-p2-pre | `54c60b5a` | `888ce1e0` | rc 0 | rc 1, 1 unrouted | "`none`. P2b's re-run …" |
| #2664 | r10-fly-relay-review-ff | `af21edb9` | `99940d99` | rc 0 | rc 1, 1 unrouted | "`none`. The carries not built here … Carry: dev/programme/rosters/wave…" |
| #2666 | r10-rca-inert-closure-recording | `e9d169b7` | `66f506fc` | rc 0 | rc 1, 1 unrouted | "none. #2662's own repair is reported to the coordinator …" |

(1) The handoff head of #2643 is now in main, so `--body-check` against today's origin/main has an empty diff and refuses for that reason alone. Its step was run by hand instead: `policy_lint.mjs --pr-body` with the three-dot path list from main as of 02:40Z (`e30b24bb`, merge base `4e38e7d7`). That run gave `PR-BODY: 0 error(s)`.

For #2664, the CI log of pr-contract job 120428691732 prints the same item id as this replay, `97ab79eb`, and the same text. For the other three PRs, the failing step name in CI (below) agrees with the replay. Their item ids were not compared against the CI logs.

**The fixer obeyed one grader and was refused by the other.** #2643 and #2664 put a path after `Carry:`, which is the form `policy_lint` demands ("names no destination file. Write `none`, or the path …"). `carry_audit` refuses that same line. R10-RCA-BODY-LINT section 2 recorded this mismatch for pathless carries. These two instances show the converse. The cause is therefore wider than "carry_audit is not run". A writer who satisfies the one grader that does run is steered into the refusal of the grader that does not.

## 2. Process state: (c)

The process is the pre-open body gate: `body_push.sh` running `prepr.sh --body-check`. It was built so that "a body that passes … would not bounce" (R10-RCA-BODY-LINT section 6). It existed, it ran, and it passed all four bodies (section 1). Its unit was chosen by a class search, and the search ran. R10-RCA-BODY-LINT section 4 named `carry_audit.py check --body` and closed it with "the dispatch already tells seats to run it". That premise is false. `awk` over the `role == "fixer"` branch of `tools/audit/seat/cloud_dispatch.py` counts 0 mentions of `carry_audit` at `4d407a35f` (that RCA's base), at `cf01e82ee` (its merge) and at origin/main. The only mention in that file is in the reviewer branch, line 131.

A second class search repeated the closure. R10-RCA-RAISE-GATE-GRAMMAR (`handoff-body/r10-rca-raise-gate-grammar` `2eadf9061`, section 3) lists `carry_audit` as "already guarded" by `body_patch.sh:98` and pr-contract. Both of those run after the open.

- **Not (a).** The gate existed, and so did a written intention to close this gap. `c185c7257` (2026-10-21T15:39Z) carried "run `carry_audit.py check --body` beside prepr" to R10-POLICY-FIXER-MD. `388c037de` (2026-10-21T20:45Z) created R10-FLOW-JIDOKA with that step as its brief.
- **Not (b).** No rule binds a fixer to run `carry_audit`. `fixer.md` contains no occurrence of it, and the fixer dispatch has none. JIDOKA was at `resume.stage: not-started` on main's roster. A queued group is not a rule that someone disobeyed.
- **Not (d) for the gate.** Its precondition was already false when it was born: `--body-check` (2026-10-22) postdates the carry step (2026-10-18). The 2026-10-18 change alone, prepr's step 7 losing parity when CI gained a step, would be (d). That is not where these instances passed, because all four were opened after `--body-check` existed.

What this state implies: change the gate's unit from "prepr step 7" to "every body grader CI runs, run the same way". Writing a firmer instruction to run `carry_audit` would be a (b) countermeasure for a (c) state.

## 3. Class search and cost test

**Enumeration rule.** Every CI step that reads the pull-request body. That is, every workflow step reading `/tmp/pr-body.md`, `$RUNNER_TEMP/body.md`, or `.body` off `/pulls/<n>`. A `grep` over `.github/workflows/*.yml` for body reads finds three files: `pr-contract.yml`, `arch-score.yml` and `budget-raise-gate.yml`, the last through `budget_raise_gate.py`. A fourth hit, `governance.yml`, reads issue #201's body, not a PR body.

| CI body grader | where it runs in CI | `--body-check` (body_push) | full prepr (open_pr) | instances measured here |
|---|---|---|---|---|
| `policy_lint.mjs --pr-body` | pr-contract, "Check the body against the contract" | yes, but offline (`unset GITHUB_TOKEN GH_TOKEN`, prepr.sh:1294) and the head's copy (CI restores the base's) | yes, step 7, with the red history | 1 red-history refusal on `5907408d` (below) |
| `figure_lint.mjs --pr-body` | pr-contract, "Every figure's command resolves" | **no** | yes, step 7a | 0 reds in the window |
| `preflight.sh $INTENDED` | pr-contract, "Pre-flight the body" (INTENDED derived from rosters) | **no** | yes, with intended numbers from the seat | 0 reds in the window |
| `carry_audit.py check --body` | pr-contract, "Every finding the body records names its destination" | **no** | **no** | **14 reds, 4 PRs** |
| `archscore/gate.py --body` | arch-score.yml (required) | **no** | **no** (0 `archscore` hits in prepr.sh) | 1 arch-score red in the window; cause not read |
| `budget_raise_gate.justification()` | budget-raise-gate.yml, and the train | **no** (`raise_red` replaces `_reviews`/`_mandate`, so the arm is never reached) | **no** | P-F: 3 refusals, #2633 and #2647, its own RCA |

`--version-edit` (pr-contract's version step) grades the diff, not the body, and full prepr runs it as step 5.

**Window.** From `cf01e82ee`, when `--body-check` reached main at 2026-10-22T23:20Z, to 2026-10-23T13:40Z, which is 14.3 h. One listing of failed pr-contract runs, then one jobs read per run, gives 28 failed runs out of 209. By failing step:

- 14 at "Every finding the body records names its destination". These are the four PRs above, at both pushes of each open.
- 13 at "Check the body against the contract". Seven of these are on `record/autofix` (#2653); the other six are on three fix branches (`r10-loop-cpu`, `r10-fly-gh-read-retry-2`, `r10-ci-layout-p2-probe-A`).
- 1 with no failing step recorded.

This seat read one of those `policy_lint` logs, job 120197045259 on `5907408d`. It is `record red-history … instrument-self-tests` followed by "`## Red checks` does not name it", an arm `--body-check` skips by running offline. The other twelve were not classified.

**P-N and P-F, reconstructed.**
- **P-F** is this family with a different grader. The refusals were at the merge train and the budget gate, not pr-contract. R10-RCA-RAISE-GATE-GRAMMAR reproduced them: `justification()` failed `c6c8fee16`, `84e2aaf66` and `f2b98c1df`, and its state is (c). A parity test confined to `pr-contract.yml` does not reach P-F.
- **P-N** is a sibling: `--body-check` is a strict subset of what the open itself runs. Its subjects are the agreement lane (prepr.sh:2938) and step 7d's `## Unpinned sites` check (prepr.sh:464-481), neither of which `--body-check` calls. Its refusals were at open_pr's prepr, not pr-contract. This seat did not reproduce P-N's refused versions. The current tips of `handoff-body/r10-orch-ledger` and `r10-input-staleness` each carry `## Unpinned sites` and pass `--body-check`, and the refused bodies are not on those refs. P-N is not counted below.

**Cost test.** Both sides are wall-clock.

- **cost(defect), measured.** Time from each PR's first carry-step red to its repair event (pr-contract runs listed per branch):
  - #2643: 02:46:28Z to green 02:59:27Z, 13.0 min.
  - #2658: 09:04:40Z to green 09:12:50Z, 8.2 min.
  - #2666: 13:20:07Z to green 13:31:30Z, 11.4 min.
  - #2664: 12:55:46Z to the repair event at 13:06:14Z, 10.5 min. That run was still `queued` at 13:40:24Z, so #2664 had been red for at least 44.6 min.

  The sum is at least 43.1 min of main-seat repair in 14.3 h, and it includes relay and idle time. Re-review cost: 0 measured. Each repair was a body edit at an unchanged head, or between the open's two pushes, so no head moved because of a repair. This seat did not read the verdict records.
- **P(recurrence), measured.** 4 PRs, or 14 red runs out of 209 pr-contract runs (6.7 %), in 14.3 h. Exposure: today's `carry_audit` refuses 58 of 176 body commits on `handoff-body/*` topics that also have a `handoff/*` ref (70 body refs fetched at 13:2xZ). This is an upper bound, because the checker and the roster are today's and many of those commits were later repaired.
- **cost(countermeasure, recurring), measured.**
  - `carry_audit.py check --body`: 103, 105, 121, 146 and 156 ms over 5 runs.
  - `figure_lint.mjs --pr-body`: 103, 113 and 128 ms over 3 runs (load 0.25).
  - At R10-RCA-BODY-LINT's measured 65 body pushes a day, both together are under 20 s a day.
  - The static parity test runs only in the self-test. Its time is **not measured**: an estimate of under 1 s for parsing three workflow files.

**Verdict: build.** Seconds a day against at least 43 min in 14.3 h. The class owes a barrier anyway: with P-F's 3 refusals and these 4 PRs, it is past the three-in-a-round trigger.

## 4. Countermeasure: the JIDOKA parity test, judged

As briefed, the barrier is: every pr-contract body check is run by `--body-check` or listed with a reason. It catches a step added to `pr-contract.yml` after the test is written. With the carry step in `--body-check`, all four instances above would have been refused at `body_push`. A changed grader *program* such as `carry_audit.py` also needs nothing more, because the twin calls the same file. Three gaps remain:

- **G1, scope.** A test that enumerates `pr-contract.yml` misses `arch-score.yml` (`gate.py --body`, required) and `budget-raise-gate.yml` (`justification()`), the grader behind P-F. The unit must be every workflow step that reads the PR body, found by the enumeration rule in section 3, not one file.
- **G2, a changed invocation.** Parity keyed on the program name stays green when CI's call to it changes. Three differences exist today, and a name-level test passes all of them:
  - `policy_lint` runs offline at body push and with the red history in CI. This is measured above (`5907408d`).
  - CI runs the base's copy of a pinned grader, and `--body-check` runs the head's.
  - CI derives preflight's `$INTENDED` from the rosters.

  The test must pin each body step's run line against a twin table: CI's exact argv and inputs, the twin's argv, and a stated reason for each difference. Editing the step's line without editing its row then fails the test. That is what catches a changed check.
- **G3, two graders of one section.** Parity runs both graders before the open, but it leaves `policy_lint` and `carry_audit` defining `## Forward-carry` differently. Two of the four instances were written to satisfy `policy_lint` and were refused by `carry_audit`. The section's grammar should have one owner. Either `policy_lint`'s Forward-carry arm calls `carry_audit`'s parser, as P-F's design has `policy_lint` call `justification()`, or `policy_lint` stops demanding a path where `carry_audit` refuses one.

Who owns what. G1 and G2 belong to R10-FLOW-JIDOKA, the same test widened. G3 belongs to R10-POLICY-LINT-FAMILY, the group that already owns `policy_lint`'s grammar seams (P-F's M1 is there). This seat builds nothing in parallel: a second test would be the parallel mechanism `fixer.md` forbids, and G3 changes a grader's grammar, which is the owning group's call.

Demonstration owed by the builder:
- On the four recorded bodies (section 1), the new step refuses each one at `body_push`. Null controls: the repaired bodies, for example `r10-orch-ledger` `b3b67b1b`, pass the carry step's own fixture.
- For G2, a mutant that edits one argument of the carry step's run line in `pr-contract.yml` must fail the parity test.
- For G1, deleting the arch-score row must fail it.

## Forward-carry

- G1: the parity test enumerates every workflow step that reads the pull-request body (`pr-contract.yml`, `arch-score.yml`, `budget-raise-gate.yml`), not `pr-contract.yml` alone. P-F's grader is in the second set. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-FLOW-JIDOKA
- G2: the parity test pins each body step's run line against a twin table (CI argv and inputs, twin argv, a reason per difference), so a changed invocation fails it. A mutant editing one argument of the carry step must fail the test. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-FLOW-JIDOKA
- G3: `## Forward-carry` has two graders with different grammars (`policy_lint.mjs` `isNone` and its path demand, against `carry_audit.py` `NONE_ITEM` and `seg_dests`). One parser must own the section. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-POLICY-LINT-FAMILY
- The `bugclasses.json` citation of `dev/audit/rca/R10-RCA-BODY-CHECK-PARITY.md` lands with the JIDOKA pull request. This seat pushes no code. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-FLOW-JIDOKA

