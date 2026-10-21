Group: R10-FLOW-YIELD-PROBE

Pinned pack file: `dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json` at pack commit 78117030 on branch `claude/dazzling-gauss-7l3u2b`.

R10-FLOW-YIELD-PROBE (owner ruling R13, expedite): why real-catch blocks per reviewed PR fell from 0.52 to 0.15, and a recommended threshold for the review-strength guardrail.

This PR adds two things:

- **The study record:** `dev/audit/rounds/round10/D13/yield-probe.md`.
- **The enumerator behind every figure:** `tools/audit/seat/review_strength.py`.
  - It reads the bus over git only: the `review/*`, `verdict/*` and `probe/*` refs and the `archive/probe/*` tags. It makes no REST call, so it is never rate-limited and never sees a 403.
  - The four fact strata (origin, size, product, fixer) are taken `--as-of` the latest window's until: the last verdict before it, and `--tree` and the roster ref each resolved to their last first-parent commit at or before it. The tool prints both SHAs.
  - It is self-tested (24 checks, including a roster, delivery rows, a merged PR and an unmerged one for each fact), wired into `governance.yml` `instrument-self-tests`, and has an entry in `tools/audit/seat/INSTRUMENTS.md`.

No production code changes. No budget, `VERSION`, manifest or claim file is touched.

**The explanation** (measured; counts beside every rate; the record has the strata):

1. **Under half of the headline fall is in what was counted.**
   - The study's 47-PR / 0.15 window reproduces only as the 48 h ending at 14:45–15:00Z on 10-21. That window includes the start of the 13:00Z sample: with L ending at 14:50Z (47 PRs, 7 real), 4 of its 7 real blocks fall at or after 13:00Z.
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

https://claude.ai/code/session_01M7BqPeDyVBhUhD9xPiDtY8

## Head

`816b1e20fdfd0a4b99bcc2b81361b70bd3007acb` merges the authored code head `ce0d6d261cd8e34c44f18f8807f90aed8b508b65` and then merges origin/main `1ebc737e7` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The code head is `ce0d6d261cd8e34c44f18f8807f90aed8b508b65`. It merges `origin/main` at `5006687576713535518634a154f7de1824432219` (2026-10-21T20:34Z) into the reviewed head `468781122d076f5396f4a27c171b78f64f1c5537`, never a rebase. Measured 2026-10-21T21:00Z (`date -u`).

The figures' closure rule (this round replaces the round-1 claim that "the figures are a function of the refs, not of `main`'s tip", which was false for the fact strata):

- **Bus counts** are cut by window: every window ends at or before 15:15Z, and a verdict counts by its committer time.
- **Fact strata** (origin, size, product, fixer) are cut at `--as-of`, by default the latest window's until (15:15Z). The tool resolves `origin/main` to `e7c664856776` and `origin/handoff/audit-r10-roster` to `2c76c3128bf6` and prints both (`facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`).
- **Not closed:** the reviewer kind reads the probe refs, the archive tags and the `verdict/*` copies present at the fetch. A probe ref pruned without its archive tag would move a verdict from cloud to local. The record says so.

The round-1 review's items, each answered in this diff:

- Figures not closed: the fact strata read `--tree`'s tip and the whole bus, so a stale or later tree moved a closed window's figures (the reviewer's 2529 case). Fixed in this diff with `--as-of` and seven fixture checks. Carry: dismissed: fixed in this pull request (item 9cdf8918)
- `pr_facts` mutation survivors: fixed in this diff by the fixture and mutants P1–P7 above. Carry: dismissed: fixed in this pull request (item 3f84a1e7)
- Wording, "5 of its 7 real blocks": reworded to the 14:50Z end's 4 of 7 in the body and the record. Carry: dismissed: fixed in this pull request (item 65976a91)
- Disclosure: the masked-catch counts and the 18 ledger models are disclosed as not re-derived, in the body and the record; the regex was not landed because no figure rests on it. Carry: dismissed: disclosed, not load-bearing (item 7e8a0c64)

## Mutation proof

Each mutant edits one predicate of `review_strength.py`. It is then run with `python3 -I tools/audit/seat/review_strength.py --self-test` and restored, and the restore is checked with `cmp` against a saved copy (`RESTORED` after every mutant). Unmutated: `review_strength self-test: 24 checks, 0 failed`.

The round-1 mutants, re-run at this head (same failing checks as round 1; the reviewer confirmed them):

- M1, the dedupe (`sha in seen` removed): FAIL `an out-of-grammar subject is its own row, never a verdict`, FAIL `a commit on two refs is read once` (2 failed).
- M2, the probe-ref join removed: FAIL `probe ref rev-<pr>-<nonce8> marks the verdict cloud` (1 failed).
- M3, the real-class predicate (`and m[4] in real` removed): 6 failed, among them `window E: 2 PRs, 5 verdicts, 1 real, 1 bookkeeping` and `--real-extra moves a word from bookkeeping to real, and only that word`.
- M4, the window's upper bound removed: 5 failed, among them `first-pass: PR 1 opened blocked, PR 2 blocked -> 0 of 2 in E`.
- M5, the prior-merge mark forced False: FAIL `one re-review after a merge verdict`, FAIL `crossed strata key on both: ...` (2 failed).
- M6, the trip verdict forced `ok`: FAIL `guardrail: 1/2 before L at p0=0.99 would trip (P(X<=1) = 0.020)` (1 failed).
- M7, the incidence set never filled: FAIL `incidence counts a PR once: 1 of 2` (1 failed).
- M8, the `bus-confirmed: cloud*` arm removed: FAIL `bus-confirmed cloud-* id marks the verdict cloud` (1 failed).

The `pr_facts` mutants, new this round (the fixture: a roster with a finding group and a group-origin group, delivery rows, PR 5 merged with 160 lines under `custom_components/`, PR 6 unmerged with 20 lines under `docs/`):

- P1, the origin label swapped `finding` → `group` (the reviewer's first mutant): FAIL `origin: a group listing issues is finding, one listing none is group` (1 failed).
- P2, the size threshold 150 → 15 (the reviewer's second): FAIL `size: merged PR 5 reads its merge diff (160 lines, M<600); unmerged 6 its verdict head (20, S<150)`, FAIL `as of: --tree is read at T (...)` (2 failed).
- P3, the product predicate forced False (the reviewer's third): FAIL `product: 5 touches custom_components/, 6 only docs/`, FAIL `as of: a verdict after T moves no fact (...)` (2 failed).
- P1+P2+P3 applied together, the reviewer's combination that survived round 1's 17 checks: 5 failed.
- P4, the fixer key read as `reviewer` instead of `fixer` (this seat's own): FAIL `fixer: the joined group's model.fixer, opus for 5 and sonnet for 6` (1 failed).
- P5, the verdict cut at as-of removed: FAIL `product: ...`, FAIL `as of: a verdict after T moves no fact (...)` (2 failed).
- P6, `--tree` not resolved at as-of: FAIL `as of: --tree is read at T (before the merge, 5 reads its verdict head and no row)` (1 failed).
- P7, the roster ref not resolved at as-of: FAIL `origin: a group listing issues is finding, one listing none is group` (1 failed).
- Wiring: `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 39 self-testing, 39 wired, 0 unwired` at this head (re-measured: main added one self-testing instrument since round 1's 38). The reviewer's wiring mutant at the previous head printed `39 self-testing, 38 wired, 1 unwired`; this diff does not touch the workflow step.

## Null control

- **The instrument.** The unmodified tree has no enumerator. The study's figures were hand-taken in STUDY.md "Guardrail baselines". The tool reproduces both of them exactly at the study's rule: 112 PRs, 0.52 (58) real and 0.58 (65) bookkeeping; and 47 PRs, 0.15 (7) and 0.64 (30). A wrong parser or window would have printed other counts.
- **The as-of rule.** With `--tree` pinned at `49c222280d46` (15:58Z, older than PR 2529's last head `8f026328d`, which already merged main at `f2fb1b0e950e`, 17:07Z) and `--as-of 2026-10-21T20:40Z`, L1's product row reads `True L1 PRs 8 ... incidence 1/8 (0.12)`: main's own commits between the two read as 2529's diff. That is the round-1 reviewer's 0.12 (1/8). Under the default rule (`--as-of` 15:15Z, tree resolved to `e7c664856776`) it reads `PRs 7 ... incidence 1/7 (0.14)`, the figure the study took; `--as-of` 18:55Z, 19:30Z and 21:00Z also read 1/7, each with the tree resolved at that time. A tree resolved at T is never older than a head verdicted before T, which is what the stale `--tree` violated.
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

The bundle prints every rate table in the record: `python3 tools/audit/seat/review_strength.py --fetch --window E=2026-10-15T12:37Z..2026-10-19T14:50Z --window L=2026-10-19T14:50Z..2026-10-21T14:50Z --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z --by kind --by prior-merge --by origin --by size --by product --by fixer --by class --by kind+origin --roster origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`. It prints `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`. Re-run at this head at 21:00Z: every figure below reproduced. Round 1's roster ref `origin/fix/audit-r10-roster` (`802b38503eb5`) no longer exists, so the fact strata were re-taken on `origin/handoff/audit-r10-roster` as of 15:15Z; each fact figure below reads the same under both.

Baselines and windows (bus counts, unchanged by this round's code):

- 112 PRs, 0.52 (58) real and 0.58 (65) bookkeeping, over 10-15 12:37Z → 10-21 11:00Z: `python3 tools/audit/seat/review_strength.py --window A=2026-10-15T12:37Z..2026-10-21T11:00Z`.
- 47 PRs, 0.15 (7) and 0.64 (30), over L: the bundle, `all` row, window L.
- 4 of L's 7 real blocks at or after 13:00Z: `python3 tools/audit/seat/review_strength.py --window L13=2026-10-21T13:00Z..2026-10-21T14:50Z` prints `PRs 11 verdicts 16 real 4`. The round-1 body's "5 of its 7" held only at the 15:00Z end, which gives 48 PRs (the reviewer's sweep).
- P1 0.90 (43/48), P2 0.36 (14/39), L1 0.08 (3/39), S 0.36 (5/14), with incidence 25/48, 10/39, 3/39 and 4/14: the bundle, `all` rows.
- 35 PRs and 0.06 (2) over the 48 h ending 11:00Z, and the 14:45–15:00Z end that gives 47: `python3 tools/audit/seat/review_strength.py --window A=2026-10-19T11:00Z..2026-10-21T11:00Z`. The end time was swept in 15-minute steps with the same tool (round 1; the reviewer re-swept it).

Strata, all from the bundle, under the as-of rule:

- Origin: finding 1.08 (40/37) in P1, 0.29 (5/17) in P2, 0.08 (1/13) in L1. Size: L ≥ 600 1.10 (22/20), 0.69 (11/16), 0.08 (1/13). Product: True 1.21 (17/14), 0.22 (2/9), 0.14 (1/7). The `origin`, `size` and `product` rows.
- Re-weighted expectations 0.50 (19.51/39), 0.89 (34.77/39) and 0.85 (32.97/39): L1's per-stratum PR counts times P1's per-stratum real/PR, over L1's 39 PRs (a stratum with no P1 PRs is taken at 0), computed from the bundle's rows.
- Reviewer kind (cloud 0.19 6/31, 0.12 3/24, 0.36 5/14; local 0.90 43/48, 0.57 8/14, 0.00 0/20) and kind+origin (P2 cloud+finding 3/13, local+finding 2/8): the `kind` and `kind+origin` rows.
- Fixer first-pass (opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6): the `fixer` rows.
- Prior-merge: 0 real; 33 verdicts on 22 PRs over the six days; 22 in E and 12 in L: the `prior-merge` rows, plus `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z --by prior-merge` (`after-a-merge-verdict A PRs 22 verdicts 33 real 0`).
- Classes (`harness` 25 / 3 / 2; `carry-missing` 3 / 15 / 7): the `class` rows.

The extended class list (bus counts):

- With the nine words: P1 0.90 (43), P2 0.49 (19/39), L1 0.21 (8/39); cloud incidence 8/31, 7/24, 4/14; local L1 0/20; POST 24/85. Command: `python3 tools/audit/seat/review_strength.py --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z --window POST=2026-10-18T08:00Z..2026-10-21T15:15Z --by kind --real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red`. Re-run at this head: reproduced.
- Binomial P values 0.0014, 0.017, 0.050 and 0.012: `review_strength.binom_cdf`, also run as `--guardrail`.
- Back-test minimum 5/30 (P = 0.116) and maximum 19/30: `python3 tools/audit/seat/review_strength.py --window W=2026-10-15T12:37Z..2026-10-21T13:00Z --real-extra regression,flaky-arm,claim-false,control-failed,claim-refuted,rule-dropped,null-control-false,red-at-head,tests-red --guardrail 30 --p0 0.28`, repeated at ten `until` points (round 1; the reviewer re-ran it over twelve).

Not re-derived by a tree instrument, and disclosed as such in the record:

- Masked catches (a real class named after `also` in a bookkeeping subject): 0/8, 1/31, 0/20 and 0/5. They came from a one-off regex over the subjects that is not in the tree. No figure rests on them.
- 18 verdicts with a ledger-recorded reviewer model (10 Opus, 8 Sonnet): read by hand from the `review-NNNN <model> <id>` lines in `wip-sync/orchestrator-scratch:orch/SEATS.md` and the seat ids naming `sonnet`. Neither this seat nor the reviewer re-derived them; they support only the statement that the model is unrecorded.

Counts and checks:

- 46 class words used, 17 taught, 16 in the real-catch list: the `class` rows; `VERDICT_CLASSES` in `.claude/workflows/web-fix-wave.js`; STUDY.md's list (`REAL_CATCH`).
- Self-test: `python3 -I tools/audit/seat/review_strength.py --self-test` prints `review_strength self-test: 24 checks, 0 failed`.
- Wiring: `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 39 self-testing, 39 wired, 0 unwired`.

Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py and tests/harness_headers.py). Results are under Red checks.

The class rule: no tree instrument enumerated the real-catch class before this PR, which is what step 8 asks for. The rule is the tool's `--by class` over every blocked subject. Every one of the 46 words it returns is dispositioned in the record: 16 on the study's list, 9 recommended for it, and the remaining 21 bookkeeping.

## Red checks

none at this head locally. Results with `/opt/hpo/venv-ci/bin/python3`, `PYTHONPATH=tests/hastub`: `tests/entities.py` "ALL 2382 ENTITY CHECKS PASSED"; `tests/harness_headers.py` "ALL 109 HARNESS HEADER CHECKS PASSED"; `tests/structure.py` "STRUCTURE RATCHET PASSED"; `tests/layout.py` "layout self-test: ok"; `tests/closure.py selftest` "ALL 124 closure shrink pins PASSED"; `tests/env_drift.py --claims-only <merge base>` rc=0; `tmp_paths.py --check` 0 refused; `ref_privacy.py --check` 0 refused. CI has not run on this head (the orchestrator opens the update).

`nightly-status` grades `main`'s scheduled run, not this diff (the reviewer read it at the previous head: main's run 39563978649). This diff touches neither `nightly_status.py` nor any workflow `nightly-status` reads. The predicted check is `instrument-self-tests`, graded by the self-test line above.

## Forward-carry

- **The guardrail threshold, the extended class list, the seat-family arm, and the calibration that a planted defect owes.** These change how the review-strength guardrail must work. The guardrail is the orchestrator beat's report (the study pack's future-state section 9 and the orchestrator prompt's "Review strength" row, on the study branch claude/dazzling-gauss-7l3u2b). R10-ORCH-MACHINERY is the live roster group that builds that beat. This seat may push only its return refs, so it edited neither file. `dev/audit/rounds/round10/D13/yield-probe.md` (it exists in the code tip tree: `git show ce0d6d261cd8e34c44f18f8807f90aed8b508b65:dev/audit/rounds/round10/D13/yield-probe.md`) "recommended threshold" section is the text to carry. Its control, a precondition of the carry: before the guardrail trips on anything, it must be run against an audit with a planted defect, and must trip there while not tripping at any of the back-test's cut points (minimum 5/30, P = 0.116); a guardrail that cannot separate the planted defect from the back-test measures nothing. Roster: at `origin/handoff/audit-r10-roster` `19427aee48b75d01f5dc2aac53930e530942cb78` (fetched 2026-10-21T21:08Z), R10-ORCH-MACHINERY's carry holds the orchestrator's line "From #2579 (item b8b28b28): the yield-probe guardrail (threshold, extended class list, seat-family arm, planted-defect calibration) ... Control: a planted defect of each class must trip the guardrail, and a null window must not." (`roster_edit append-carry`, commit `b6e8c76eb`). That control is this one, stated per class. Carry: R10-ORCH-MACHINERY (item b8b28b28)
- **The reviewer model is not on the bus.** `bus.sh dispatch` records a reviewer id but no model, so a model stratum is unmeasurable (18 of 306 verdicts have one in the orchestrator ledger). R12 already puts dispatch records (bus.sh dispatch and the workers record) in that group; the model belongs in the same record. Its control, a precondition of the carry: a dispatch record written with a model must read back on the bus as a `review_strength.py --by` stratum, and one written without must refuse rather than read `none`. Roster: the same line at `19427aee48b75d01f5dc2aac53930e530942cb78` carries this claim ("the reviewer model is unrecorded in the ledger"), but its control names only the guardrail; this control, a model read back as a stratum, is not yet on the roster, and this seat leaves the roster to the orchestrator. Carry: R10-ORCH-MACHINERY (item b8b28b28)

## Friction

- `fixer.md`: cost: the seat's default `python3` is 3.11 without `voluptuous`, so `tests/entities.py` (an f-string needing 3.12) and `tests/harness_headers.py` fail to import. The gate was run with `/opt/hpo/venv-ci/bin/python3` instead. Carry: dismissed: the environment's venv is the documented interpreter

