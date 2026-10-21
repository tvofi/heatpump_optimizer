Group: R10-FLOW-YIELD-PROBE (registration pending: roster PR-B)

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13, expedite): why real-catch blocks per reviewed PR fell from 0.52 to 0.15, and a recommended threshold for the review-strength guardrail.

This PR adds two things:

- **The study record:** `dev/audit/rounds/round10/D13/yield-probe.md`.
- **The enumerator behind every figure:** `tools/audit/seat/review_strength.py`.
  - It reads the bus over git only: the `review/*`, `verdict/*` and `probe/*` refs and the `archive/probe/*` tags. It makes no REST call, so it is never rate-limited and never sees a 403.
  - It is self-tested, wired into `governance.yml` `instrument-self-tests`, and has an entry in `tools/audit/seat/INSTRUMENTS.md`.

No production code changes. No budget, `VERSION`, manifest or claim file is touched.

**The explanation** (measured; counts beside every rate; the record has the strata):

1. **Under half of the headline fall is in what was counted.**
   - The study's 47-PR / 0.15 window reproduces only as the 48 h ending at 14:45–15:00Z on 10-21. That window includes the 13:00Z sample, which holds 5 of its 7 real blocks.
   - Nine class words outside the study's real-catch list name engineering catches, for example `flaky-arm`, `claim-false` and `control-failed` (a surviving mutant). Counting them moves L1 (10-19 14:50Z → 10-21 13:00Z) from 0.08 (3/39) to 0.21 (8/39).
2. **Round 10's first days were wave 1 of the finding fixes.** In P1 (10-15 12:37Z → 10-18 08:00Z), 37 of 48 reviewed PRs were finding-fix groups. They drew 40 of the 43 real blocks, 25 of them `harness`, concentrated in a few multi-round PRs.
   - Re-weighting by origin alone moves the expected rate from 0.90 to 0.50.
   - Size and product mix move it to 0.89 and 0.85, so they explain almost none of the fall.
3. **The cloud reviewers' rate is flat.** Their incidence reads 8/31 in P2, 7/24 in L1 and 4/14 in the sample (extended list). The trough is L1's local seats, at 0/20. At the post-cloud incidence of 0.28 (24/85), the chance of 0 in 20 is 0.0014.
   - Those seats were the Sonnet roster reviewers, the seats after the 10-20 session crash, and the next session's `reviewer` seats.
   - Their model is not recorded per verdict. The ledger stops at 10-20T13:34Z.
4. **Carries are rejected as a cause.** Re-reviews after a merge verdict, the ones a carry replaces, caught 0 real in every window (33 verdicts on 22 PRs over the six days).
5. **Fixer quality cannot be separated from reviewer strength on the bus.** First-pass share rose (opus fixers 7/22 in P1, 5/7 in L1), and it rose under the fixed cloud reviewer too (8/25 to 9/20).

**The recommendation:**

- **Metric.** Incidence: the PRs with at least one real block, over reviewed PRs. It is not blocks per PR, which counts one PR's repeated rounds.
- **Class list.** The study's list plus the nine words. An untaught word is routed to a row that needs classifying, never to bookkeeping.
- **Window.** The last 30 reviewed PRs.
- **Baseline.** p0 = 0.28.
- **Trip rule.** Trip at 3 or fewer of the 30 PRs (P = 0.017).
- **Second arm.** For each seat family, the last 20 PRs that family reviewed, tripping at 1 or fewer (P = 0.012).
- **Back-test.** The first arm would have tripped at none of ten cut points; the lowest was 5/30, P = 0.116.
- **Calibration owed.** A trip calls for an audit with a planted defect; only a planted defect separates defect supply from detection.
- **Until adopted.** R13 stands: the guardrail reports and trips on nothing.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TK6mKUXAxvPYEwHCB7ed3j

## Head

The code head is `7864970031c4c9a24b077a6ccd01fdf02ba192a0`. The base is `origin/main` at `e7c664856776542bf60bd770c98aba1eaadb4041`; the bus was measured 2026-10-21T15:24Z (`date -u`). Every window is closed (it ends at or before 15:15Z) and the bus is append-only, so the figures are a function of the refs, not of `main`'s tip.

## Mutation proof

Each mutant deletes or neutralises one predicate of `review_strength.py`. It is then run with `python3 -I tools/audit/seat/review_strength.py --self-test` and restored, and the restore is checked with `cmp` against a saved copy (`RESTORED`).

- M1, the dedupe (`sha in seen` removed): FAIL `a commit on two refs is read once`, FAIL `an out-of-grammar subject is its own row, never a verdict` (2 failed).
- M2, the probe-ref join (`(pr, nonce[:8]) in probes` removed): FAIL `probe ref rev-<pr>-<nonce8> marks the verdict cloud` (1 failed).
- M3, the real-class predicate (`and m[4] in real` removed): 6 failed. They include `window E: 2 PRs, 5 verdicts, 1 real, 1 bookkeeping`, `a class word without its colon is a block of class '' (bookkeeping), not real` and `--real-extra moves a word from bookkeeping to real, and only that word`.
- M4, the window's upper bound removed: 5 failed. They include `window E: ...` and `first-pass: PR 1 opened blocked, PR 2 blocked -> 0 of 2 in E`.
- M5, the prior-merge mark forced False: FAIL `one re-review after a merge verdict`, FAIL `crossed strata key on both: ...` (2 failed).
- M6, the trip verdict forced `ok`: FAIL `guardrail: 1/2 before L at p0=0.99 would trip (P(X<=1) = 0.020)` (1 failed).
- M7, the incidence set never filled: FAIL `incidence counts a PR once: 1 of 2` (1 failed).
- M8, the `bus-confirmed: cloud*` arm removed: FAIL `bus-confirmed cloud-* id marks the verdict cloud` (1 failed).
- Wiring, the new `governance.yml` step removed: `selftest_wiring.py --check` prints `UNWIRED tools/audit/seat/review_strength.py: no workflow run line names its self-test` and `38 self-testing, 37 wired, 1 unwired`. With the step it prints `38 self-testing, 38 wired, 0 unwired`.

## Null control

- **The instrument.** The unmodified tree has no enumerator. The study's figures were hand-taken in STUDY.md "Guardrail baselines". The tool reproduces both of them exactly at the study's rule: 112 PRs, 0.52 (58) real and 0.58 (65) bookkeeping; and 47 PRs, 0.15 (7) and 0.64 (30). A wrong parser or window would have printed other counts.
- **The PR-mix candidate.** Its null is the rate inside each stratum, which must not move if mix is the cause. Every stratum falls: finding-fix 1.08 (40/37) to 0.08 (1/13); L ≥ 600 lines 1.10 (22/20) to 0.08 (1/13); product 1.21 (17/14) to 0.14 (1/7).
- **The reviewer-kind candidate.** At P2, where both kinds ran, finding-fix PRs read cloud 0.23 (3/13) and local 0.25 (2/8).
- **The carries candidate.** The `after-a-merge-verdict` stratum reads 0 real in E (22 verdicts), L (12) and P1, P2 and L1 alike.
- **The class-list extension.** P1 holds none of the nine words and reads 43 real under both lists.
- **The fixer candidate.** First-pass share under the fixed cloud reviewer, 8/25 in P2 and 9/20 in L1, moves the same way as overall.

## Figures

The windows used below:

- E=2026-10-15T12:37Z..2026-10-19T14:50Z
- L=2026-10-19T14:50Z..2026-10-21T14:50Z
- P1=..2026-10-18T08:00Z
- P2=2026-10-18T08:00Z..2026-10-19T14:50Z
- L1=2026-10-19T14:50Z..2026-10-21T13:00Z
- S=2026-10-21T13:00Z..2026-10-21T15:15Z
- POST=2026-10-18T08:00Z..2026-10-21T15:15Z

The bundle prints every rate table in the record: `python3 tools/audit/seat/review_strength.py --fetch --window E=2026-10-15T12:37Z..2026-10-19T14:50Z --window L=2026-10-19T14:50Z..2026-10-21T14:50Z --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z --by kind --by prior-merge --by origin --by size --by product --by fixer --by class --by kind+origin --roster origin/fix/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`. The roster ref was at `802b38503eb5`.

Baselines and windows:

- 112 PRs, 0.52 (58) real and 0.58 (65) bookkeeping, over 10-15 12:37Z → 10-21 11:00Z: `python3 tools/audit/seat/review_strength.py --window A=2026-10-15T12:37Z..2026-10-21T11:00Z`.
- 47 PRs, 0.15 (7) and 0.64 (30), over L: the bundle, `all` row, window L.
- P1 0.90 (43/48), P2 0.36 (14/39), L1 0.08 (3/39), S 0.36 (5/14), with incidence 25/48, 10/39, 3/39 and 4/14: the bundle, `all` rows.
- 35 PRs and 0.06 (2) over the 48 h ending 11:00Z, and the 14:45–15:00Z end that gives 47: `python3 tools/audit/seat/review_strength.py --window A=2026-10-19T11:00Z..2026-10-21T11:00Z`. The end time was swept in 15-minute steps with the same tool.

Strata, all from the bundle:

- Origin, size and product rates: the `origin`, `size` and `product` rows.
- Re-weighted expectations 0.50, 0.89 and 0.85: L1's per-stratum PR counts times P1's per-stratum rates, over L1's 39 PRs (a stratum with no P1 PRs is taken at 0).
- Reviewer kind (cloud 0.19 6/31, 0.12 3/24, 0.36 5/14; local 0.90 43/48, 0.57 8/14, 0.00 0/20) and kind+origin (P2 cloud 3/13, local 2/8): the `kind` and `kind+origin` rows.
- Fixer first-pass and real/PR (opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6): the `fixer` rows.
- Prior-merge: 0 real; 33 verdicts on 22 PRs over the six days; 22 in E and 12 in L: the `prior-merge` rows, plus `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z --by prior-merge`.
- Classes (`harness` 25 / 3 / 2; `carry-missing` 3 / 15 / 7): the `class` rows.

The extended class list:

- With the nine words: P1 0.90 (43), P2 0.49 (19/39), L1 0.21 (8/39); cloud incidence 8/31, 7/24, 4/14; local L1 0/20; POST 24/85. Command: `python3 tools/audit/seat/review_strength.py --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z --window POST=2026-10-18T08:00Z..2026-10-21T15:15Z --by kind --real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red`.
- Masked catches (a real class named after `also` in a bookkeeping subject): 0/8, 1/31, 0/20 and 0/5. This was a one-off scratch regex over the subjects; no tree instrument takes it.
- Binomial P values 0.0014, 0.017, 0.050 and 0.012: `review_strength.binom_cdf`, also run as `--guardrail`.
- Back-test minimum 5/30 (P = 0.116) and maximum 19/30: `python3 tools/audit/seat/review_strength.py --window W=2026-10-15T12:37Z..2026-10-21T13:00Z --real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red --guardrail 30 --p0 0.28`, repeated at ten `until` points.

Counts and checks:

- 18 verdicts with a ledger-recorded reviewer model (10 Opus, 8 Sonnet): the `review-NNNN <model> <id>` lines in `wip-sync/orchestrator-scratch:orch/SEATS.md`, plus seat ids naming `sonnet`.
- 46 class words used, 17 taught, 16 in the real-catch list: the `class` rows; `VERDICT_CLASSES` in `.claude/workflows/web-fix-wave.js`; STUDY.md's list (`REAL_CATCH`).
- Self-test: `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 17 checks, 0 failed`.
- Wiring: `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `38 self-testing, 38 wired, 0 unwired`.

Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py and tests/harness_headers.py). Results are listed below.

The class rule: no tree instrument enumerated the real-catch class before this PR, which is what step 8 asks for. The rule is the tool's `--by class` over every blocked subject. Every one of the 46 words it returns is dispositioned in the record: 16 on the study's list, 9 recommended for it, and the remaining 21 bookkeeping.

## Red checks

none. Local results at this head with `/opt/hpo/venv-ci/bin/python3`, `PYTHONPATH=tests/hastub`: `tests/structure.py` "STRUCTURE RATCHET PASSED"; `tests/entities.py` "ALL 2375 ENTITY CHECKS PASSED"; `tests/harness_headers.py` "ALL 109 HARNESS HEADER CHECKS PASSED"; `tests/layout.py`, `tests/closure.py selftest` and `tests/env_drift.py --claims-only <merge base>` rc=0; `tmp_paths.py --check` 0 refused; `ref_privacy.py --check` 0 refused. The predicted check is `instrument-self-tests` (the new step), graded by the self-test line above. `nightly-status` grades `main`, not this diff. A red there at this head is `main`'s lane, and this diff touches neither `nightly_status.py` nor any workflow `nightly-status` reads.

## Forward-carry

- **The guardrail threshold, the extended class list, the seat-family arm, and the calibration that a planted defect owes.** These change how the review-strength guardrail must work. The guardrail is the orchestrator beat's report (the study pack's future-state section 9 and the orchestrator prompt's "Review strength" row, on the study branch claude/dazzling-gauss-7l3u2b). R10-ORCH-MACHINERY is the live roster group that builds that beat. This seat may push only its return refs, so it edited neither file. `dev/audit/rounds/round10/D13/yield-probe.md` (it exists in the code tip tree: `git show 7864970031c4c9a24b077a6ccd01fdf02ba192a0:dev/audit/rounds/round10/D13/yield-probe.md`, 271 lines) "recommended threshold" section is the text to carry. Carry: R10-ORCH-MACHINERY
- **The reviewer model is not on the bus.** `bus.sh dispatch` records a reviewer id but no model, so a model stratum is unmeasurable (18 of 306 verdicts have one in the orchestrator ledger). R12 already puts dispatch records (bus.sh dispatch and the workers record) in that group; the model belongs in the same record. Carry: R10-ORCH-MACHINERY

## Friction

- `fixer.md`: cost: the seat's default `python3` is 3.11 without `voluptuous`, so `tests/entities.py` (an f-string needing 3.12) and `tests/harness_headers.py` fail to import. The gate was run with `/opt/hpo/venv-ci/bin/python3` instead. Carry: dismissed: the environment's venv is the documented interpreter

