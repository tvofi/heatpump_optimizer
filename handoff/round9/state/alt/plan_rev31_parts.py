#!/usr/bin/env python3
"""Assemble plan rev 3 from rev 2 (the file in place) and the rev-3 sections below.

    python3 plan_rev31_parts.py PLAN_REV2.md TABLE.md PRESTUDY_COMMIT ROSTER_COMMIT COVERAGE.md > PLAN_REV31.md

Replaces: the header (to section 0), section 4.1's table, sections 4.2-4.4, 6 and 7; inserts section 2.4 before
section 3 and appends one bullet to section 3. Sections 0-2.3, 4.5 and 5 are rev 2's text unchanged.
"""
import re, sys

plan, table, psc, rc, cov = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
P = open(plan).read()
T = open(table).read().strip()
COV = open(cov).read().strip()
n_open = len([ln for ln in T.splitlines() if ln.startswith('| ') and not ln.startswith('| wave')])

HEADER = f"""# Round 9 endgame, re-planned (rev 3.1): the architecture score, its 2× plan, every open issue, and the programme where it stands

**Status.**
- **Rev 1** was adopted on 2026-09-28 (roster `0f1f5263`/`27049219`, record PR #1749).
- **Rev 2** was adopted after that. The live roster on `handoff/audit-r9-fixplan` (`c5af8f3a`) carries its 66 groups. EG-R0 (#1763), EG-B9 (#1765) and F7.4 (#1766) have merged.
- **Rev 3** was pushed at `25c6151f`.
- **Rev 3.1** applies tvofi's decisions of 2026-09-29 and covers every open issue (§4.6). tvofi extended the programme mandate to programme completion, so **no step waits for a human decision**. What remains for tvofi's hands is mechanical, not a decision (§7): approving reviews on code-owned merges, and repository-settings changes.

Rev 3 was written 2026-09-29 by the same cloud review seat. It is measured at origin/main `7952d8f9` and re-based to `f88e6af8`:
- #1771 (register tranche 2) touches no production file.
- #1767 (F1.6) leaves the score vector and every cited figure unchanged. It is the first live PR scored: ΔS 0, NULL.

tvofi asked:
- whether the ratchet numbers could make a weighted score that a programme raises only by improving the architecture;
- then for a pre-study (a metric review, new metrics, a calibrated prototype, a wave-plan sketch);
- then for a plan to improve that score 2× honestly, and how to schedule it against round 9;
- then for this revision of the plan, roster and prompt;
- then (rev 3.1) to file all issues and make the plan cover every open issue, with the 30 legacy issues re-measured and closed inside the plan, not now.

**What rev 3 and 3.1 add:**
- **The pre-study:** `alt/archscore/PRE-STUDY.md` (commit `{psc}`). Its evidence sits beside it:
  - `a1/`: 30 perturbations of the 24 structure metrics, with nulls;
  - `a2/`: 45 labelled historical commits measured on both sides;
  - `a3/`: nine new metrics, each with a control, a fix and a null;
  - `b/`: the score, its frozen weights, calibration v0/v1, gate variants, sensitivity, the trajectory, and the 2× arithmetic;
  - `redteam/`.
- **Roster rev 3:** `ALT-ROSTER.json` (commit `{rc}`).
  - It is the live roster plus the deltas in `alt/build_roster_rev3.py`: F1.6 truthed to done at `f88e6af8` (#1767); score carries into F10.4, EG-B1, B2, B3, B5, B6 and B7; new groups EG-A1, EG-A2, EG-A3 and F7.5.
  - Rev 3.1 adds EG-L0 (re-measure and close the 30 legacy issues, and disposition #1655), EG-B11 (#1745, typed entry configuration) and EG-A4 (the score becomes a required check, R3-6). It also adds the decision carries (§7) and a closing group for every open issue.
  - No edge was added to a planned group.
  - 73 groups, acyclic, and `brief_lint.mjs` prints `TOTAL: 0 error(s)`.
- **Issues filed and read back:** #1774 (score, EG-A1 then EG-A4), #1775 (EG-A2), #1776 (EG-A3) and #1777 (F7.5). #1738 carries the addendum of eleven metric defects (comment `5901009400`).
- **Live status:** `alt/archscore/status/LIVE-STATUS.md`.
  - Measured at `4d33b25c`: 33 groups merged, 1 in review (F1.6), 31 not started, and EG-B0 `rca-done`.
  - F1.6 has since merged (#1767, `f88e6af8`), so **34 are merged and 31 are open, plus the 4 new groups.**
  - Seven disagreements between the record's sources are listed there; §6 step 3 corrects them.

**Owner direction this plan applies:**
- Everything rev 1 and rev 2 applied still stands.
- Rev 3 adds tvofi's 2026-09-29 direction: "construct a plan of how to honestly, using real, objective, honest improvements and not gaming the metric, improve the score by 2x. Plan how to most efficiently implement this plan, either combined with the ongoing round 9 fix programme, staggered with it, or after it."

"""

SEC24 = f"""### 2.4 Rev 3: the architecture score (`alt/archscore/PRE-STUDY.md` at `{psc}`)

**The answer.** No score built from the ratchet budgets, and no score of any kind, can be *necessarily* right. What was built is narrower, and it is calibrated.

**The instrument has two parts:**
- **A Pareto gate:** no score metric may rise.
- **A log-ratio score:** S = Σ wᵢ log₂((ref+1)/(cur+1)) over 12 static metrics.

The weights are log₂(1 + register-v2 defect cost in hours). They were frozen before calibration.

The index is AI = 100·D_ref/D, where D is the weighted log-debt: 212.8 at `7952d8f9`, where AI = 100.

**What the evidence shows:**
- **The 24 structure metrics are mostly unfit for this purpose.**
  - The perturbation review retires 11 from the architecture view, merges 7 into 2, and verifies 11 metric defects beyond #1738.
  - On 45 labelled historical commits the ratchet tracks size, not defect shapes. `duplication_blocks` never moved on any labelled GOOD or BAD commit.
- **Calibration v1: 79/103 cases correct.**
  - It catches planted defects 27/28 and historical BAD commits 11/14.
  - **No BAD change is credited as an improvement.**
  - It credits only 10/24 historical GOOD commits: 6 are invisible to it, and 8 fail on a +1 incidental rise or are mispriced.
  - Weight sensitivity is flat (×0.5, ×2 and all-equal give the same 79/103).
  - The historical corpus is a holdout: v1's fixes used planted cases only.
- **Red team:** RED_SUMMARY

**Use:** report-only, as a review trigger with a calibration self-check (**EG-A1**, #1774). tvofi decided (R3-6) that "ΔS ≥ 0 with the counters, or an explained rise" becomes a required check after one wave of report-only data. That is **EG-A4**, the programme's last PR.

**The 2× plan** (`b/plan2x.out`):

| step | group | ΔS |
|---|---|---|
| 1 | EG-B1 | +29.5 |
| 2 | EG-B3 | +50.9 |
| 3 | EG-B6 | +4.2 |
| 4 | EG-B2 | +3.8 |
| 5 | EG-B7 | +5.2 |
| 6 | F10.4 | +5.6 |
| — | subtotal: the six groups round 9 already plans | AI **187** |
| 7 | new EG-A2 (one copy per formula and helper) | +14.1 → AI 214 |
| 8 | new F7.5 (owner-gated names) | +10.9 → AI 240 |
| 9 | new EG-A3 | +0.6 → AI 242 |

How robust the 2× is:
- Halving the dominant weight gives AI 213; all weights equal gives AI 204.
- **Without EG-B3 the programme reaches only 153.** The typed payload is indispensable, and it must use real value types, not `Any`.
- Every step carries honesty obligations: a class instance removed, goldens held, no red-team move in the diff, and any gate rise explained.

**Schedule: combined with round 9.**
- 80 of the 106 points sit in EG-B1 and EG-B3, which round 9 already plans. After round 9 their deltas would go unmeasured.
- A staggered programme would re-open files those groups own.
- The instrument costs the critical path nothing. EG-A1 follows F10.4 beside EG-B3; EG-A2 follows EG-B3 and EG-B5; EG-A3 follows EG-B1. All sit at or below EG-B7's depth.

"""

SEC3_ADD = """- **Rev 3: measure the architecture, not just the budgets.** Each EG brief now states its expected ΔS and the per-metric targets from `alt/archscore/PRE-STUDY.md` §8. The reviewer compares the measured value. A shortfall is information, not a failure. A score rise earned by a red-team move (§7 of the pre-study) is a review finding.
"""

SEC41 = f"""### 4.1 Per PR

Generated from roster rev 3 (`ALT-ROSTER.json`) by `alt/gen_table_rev3.py`:
- The `wave` is the dependency depth over open groups; 1 means startable now.
- **Bold** issues are ones the PR fixes (`Fixes #N`); the rest are `Part of #N`.
- Expected ΔS is the pre-study's §8 figure under the frozen weights.
- {n_open} groups are open.

{T}

"""

SEC42_44 = """### 4.2 Threads

- **F1, the critical path:** F1.6 merged (#1767) → *(F2.4)* → F1.7 (+P10 barrier) → F1.8 (+P8, currency per D6) → F1.9 → F1.10 (+#1741) → F1.11.
- **F2 / F9 / EG-B10:** startable now. **EG-B8** follows F2.4.
- **F7:** **F7.5** is startable now. It renames the three family splits (R3-4).
- **EG-L0:** startable now, in W0. It re-measures and closes the 30 legacy issues, dispositions #1655, and carries anything still live into the owning group's brief before that group starts.
- **F6:** F6.3 (after F1.8) → F6.4.
- **F10:** F10.1b (after F1.7) → F10.1c (fix, D9) ‖ F10.2 → F10.3 (+I2, +#1748) → F10.4 (+N-structure-blind, #1545, **the metric review**, R3-2, closes #1738) → F10.5 → F10.6 → F10.7 (closes #1758).
- **F11:** F11.4 (after F10.4; builds the N-silent-zero barrier, D8) → F11.5 → F11.7.
- **EG:**
  - EG-B2 after F1.11.
  - After F10.4: **EG-A1** ‖ EG-B3 ‖ EG-B5a, then EG-B4 and EG-B5.
  - **EG-A2** after EG-A1, EG-B3 and EG-B5.
  - EG-R1 after F11.4 (clauses per D5).
  - EG-B1 after F10.6, F11.5, EG-B4, EG-B5 and EG-B10.
  - Then **EG-A3** ‖ EG-B6, then EG-B7 ‖ **EG-B11** (#1745).
  - **EG-A4** closes the programme after EG-B7, EG-B11, EG-A2 and EG-A3.
- **Structure-budget writers are serialised** (principle 2): EG-B5a, EG-B5, EG-B1, EG-B7, EG-A2 and EG-B11.

### 4.3 Critical path

- **Critical path:** F2.4 → F1.7 → F1.8 → F1.9 → F1.10 → F1.11 → F10.4 → F10.5 → F10.6 → EG-B1 → EG-B6 → EG-B7 → EG-A4. That is 13 serial PRs from here.
  - EG-A4 is rev 3.1's only addition to the chain.
  - EG-A1, A2, A3, EG-L0, F7.5 and EG-B11 all run beside it.
- **Duration** (pre-study §9, measured from the 34 merges):
  - the serial F1 steps took 5.6–11.1 h each, a mean of 8.2 h; F1.6 took about 17 h with two review rounds;
  - 13 steps is about 73–144 h, **about 4½ days at the mean** of continuous operation, and 5–7 days realistically;
  - add the time tvofi takes to click approving reviews on code-owned merges, the only waits left;
  - AI passes 200 when EG-A2 merges, at depth 10 of 13.

### 4.4 Windows

**W0, now.**
- **Stamp v6.7.11.** EG-B9 (#1765, sev:high) and F1.6 (#1767) are unstamped.
- Apply roster rev 3.1 (§6 step 1).
- Land the record PR (§6 step 2).
- Post on #201.
- Dispatch **F2.4 ‖ F9.3 ‖ EG-B10 ‖ F7.5 ‖ EG-L0**.

**W1 to W4:**
- **W1:** EG-B8 ‖ F1.7, then F1.8 ‖ F10.1b.
- **W2:** F1.9 ‖ F6.3 ‖ F10.2 ‖ F10.1c, then F1.10 ‖ F6.4 ‖ F10.3.
- **W3:** F1.11, then F10.4 ‖ EG-B2.
- **W4:**
  - F10.5 ‖ F11.4 ‖ EG-B3 ‖ EG-B5a ‖ **EG-A1**;
  - then F10.6 ‖ F11.5 ‖ EG-B4 ‖ EG-B5 ‖ EG-R1.
- **Stamp v6.8.0**, stamp point (c).

**W5:**
- EG-B1 ‖ **EG-A2**. EG-A2 needs EG-B5 and must not run beside it. It can run beside EG-B1 only if the two do not share a file; the orchestrator checks the scopes and otherwise serialises.
- Then EG-B6 ‖ **EG-A3**.
- Then EG-B7 ‖ **EG-B11**, with F10.7 and F11.7 beside.
- Then **EG-A4**.
- Then a stamp.

**Endgame, as in rev 2:**
- friction dispositions;
- #1730's row;
- the register PR;
- the stamp;
- the branch prune.

"""

SEC6 = f"""## 6. Adopting rev 3.1

tvofi's decisions are given (§7), so nothing waits for approval. The orchestrator:

1. **The roster.** Replaces `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` with `ALT-ROSTER.json`.
   - If the live file has moved since `c5af8f3a`, run `alt/build_roster_rev3.py <live> <out>` on it, then replace the placeholder with the pre-study commit (`{psc}`). Its sections 1–6 apply:
     - F1.6 truthing;
     - the carries;
     - the rev 3 groups;
     - the rev 3.1 decisions, the mandate text, EG-L0, EG-B11, EG-A4, and one closing group per open issue.
   - Assert that all 34 merged groups read `done` at their merge SHAs.
   - Assert that every open issue has a closing group (`alt/gen_coverage_rev31.py`).
   - Lint: `TOTAL: 0 error(s)`.

2. **The record PR** (the `hpo-author` App, via `tools/audit/app_push.sh`) corrects what `alt/archscore/status/LIVE-STATUS.md` found:
   - the disposition rows for #1752/#1753, #1759, #1760 and #1736 in `docs/plan-2026-09-open-issues.md`;
   - `docs/delivery/1771.md`;
   - `tools/audit/round9/fixplan/standing.md`, which lacks the "Enumerators run INSIDE the tree" rule;
   - `tools/audit/round9/prestudy/ALT-ROSTER.json`: label it a rev-2 snapshot or remove it.

   It also adds disposition rows for #1774 to #1777 and for every legacy issue, as "EG-L0: re-measure then close". It adds no budget and no `VERSION` edit.

3. **Already done by the review seat:** #1774 to #1777 are filed and read back, and the #1738 addendum is posted (comment `5901009400`).

4. **#201.** One comment, posted with `gh_comment.py` and read back.

5. **Dispatch** per §4, starting with W0.

"""

SEC7 = """## 7. Decisions, all given 2026-09-29, and what remains for tvofi's hands

**The mandate.** tvofi extended the programme mandate to programme completion. No step waits for a human decision.
- **A budget raise an honest re-record requires** is confirmed by the mandate. The orchestrator posts the measured value and reason on #201 before the push (CLAUDE.md rule 2).

**Rev 3 decisions:**

| # | decision | given | carried in |
|---|---|---|---|
| R3-1 | adopt the score as report-only, with the PR-template line | **adopt** | EG-A1 (#1774) |
| R3-2 | F10.4 retirement list: 4 rows retired, 7 moved out of the architecture view, 7 merged into 2 | **approve**; this also settles #1738 arm (c) by retiring `classes_over_300` | F10.4 |
| R3-3 | the weights | **the seat's recommendation: accept the frozen register-cost basis unchanged** (hash in `b/weights.sha256`) | EG-A1 |
| R3-4 | F7.5, rename or keep | **rename** all three: display strings only, no `translation_key`, `unique_id` or entity id | F7.5 (#1777) |
| R3-5 | EG-A2/A3 issues | **file, round 9** (#1775, #1776) | EG-A2, EG-A3 |
| R3-6 | the score becomes a required check | **yes**, after one wave of report-only data | EG-A4 (#1774) |

**Why R3-3 is "accept":**
- Classification is invariant to the weights: ×0.5, ×2 and all-equal each give the identical 79/103.
- The 2× target is reached under all three weightings (242, 213, 204).
- Every amendment was recorded before the first calibration run.
- Changing the weights now would be fitting them to the results.

**Rev 2's open decisions, given under the mandate by the seat's default.** Each is written into its group's brief:

| # | question | default | group |
|---|---|---|---|
| D5 | the four policy clauses | adopt as specified in RCA-BULK-2 §3.4 | EG-R1 |
| D6 | displayed currency | follows the feed's currency where the feed declares one; the configured currency otherwise | F1.8 |
| D7 | the P4 refusal | record it on #1664 and in the body | F2.4 |
| D8 | the N-silent-zero barrier | build it (the refusal was overturned on cost) | F11.4 |
| D9 | the 20 h override that lasts 21 h | fix it: the stated length in absolute time | F10.1c |
| D11 | the host Profiler run | optional; F10.7 does not wait for it | F10.7 |
| D12 | EG-H2 | judge quiet periods against the configured band | EG-B1 |

tvofi may override any default by saying so. Rev 2's decisions 1–4 and 10 are settled (§2.4).

**What remains for tvofi's hands.** These are mechanical, not decisions:
- **Approving reviews.** Every code-owned or budget-raising merge (branch protection and budget-raise-gate): F6.3, F10.2, F10.3, F10.4, F10.5, F10.6, F11.4, F11.5, F11.7, EG-R1, EG-A1, EG-A4, and any raise.
- **Repository settings only the admin can change.** Any the legacy governance issues prove (EG-L0: #1191, #1193, #1196), and EG-A4's required context. The orchestrator records each exact setting on #201.
- **F10.5's writer identity.** A new App and credential under decision 0011 are a Mac/tvofi action.
"""

# ---- splice
i0 = P.index('## 0. The verdict on each draft item')
P = HEADER + P[i0:]
i3 = P.index('## 3. Ratchet stance')
P = P[:i3] + SEC24 + P[i3:]
i4 = P.index('## 4. The schedule')
sec3 = P[:i4].rstrip('\n') + '\n' + SEC3_ADD + '\n'
P = sec3 + P[i4:]
a = P.index('### 4.1 Per PR')
b = P.index('### 4.5 Stamps and fixtures')
P = P[:a] + SEC41 + SEC42_44 + P[b:]
c = P.index('## 5. Deferred and dropped')
P = P[:c] + "### 4.6 Every open issue and the group that closes it\n\nGenerated from roster rev 3.1 and GitHub's open issues (tracking #201 excluded) by `alt/gen_coverage_rev31.py`.\n- Every open issue has a closing group.\n- #1655 is dispositioned by EG-L0, which closes it with R9-F4.2's record or schedules the remainder into its owning group.\n\n" + COV + "\n\n" + P[c:]
P = P.replace("- **#1745, typed configuration.** After EG-B1.", "- **#1745, typed configuration:** moved into round 9 as **EG-B11** (rev 3.1).")
a = P.index('## 6. Adopting rev 2')
P = P[:a] + SEC6 + SEC7
sys.stdout.write(P)
