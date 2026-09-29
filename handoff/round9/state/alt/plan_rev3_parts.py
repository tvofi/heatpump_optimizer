#!/usr/bin/env python3
"""Assemble plan rev 3 from rev 2 (the file in place) and the rev-3 sections below.

    python3 plan_rev3_parts.py PLAN.md TABLE.md PRESTUDY_COMMIT ROSTER_COMMIT > PLAN_REV3.md

Replaces: the header (to section 0), section 4.1's table, sections 4.2-4.4, 6 and 7; inserts section 2.4 before
section 3 and appends one bullet to section 3. Sections 0-2.3, 4.5 and 5 are rev 2's text unchanged.
"""
import re, sys

plan, table, psc, rc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
P = open(plan).read()
T = open(table).read().strip()
n_open = len([ln for ln in T.splitlines() if ln.startswith('| ') and not ln.startswith('| wave')])

HEADER = f"""# Round 9 endgame, re-planned (rev 3): the architecture score, its 2× plan, and the programme where it stands

**Status.**
- **Rev 1** was adopted on 2026-09-28 (roster `0f1f5263`/`27049219`, record PR #1749).
- **Rev 2** was adopted after that. The live roster on `handoff/audit-r9-fixplan` (`c5af8f3a`) carries its 66 groups. EG-R0 (#1763), EG-B9 (#1765) and F7.4 (#1766) have merged.
- **Rev 3** is for tvofi's decision and is not dispatched.

Rev 3 was written 2026-09-29 by the same cloud review seat. It is measured at origin/main `7952d8f9` and re-based to `f88e6af8`:
- #1771 (register tranche 2) touches no production file.
- #1767 (F1.6) leaves the score vector and every cited figure unchanged. It is the first live PR scored: ΔS 0, NULL.

tvofi asked:
- whether the ratchet numbers could make a weighted score that a programme raises only by improving the architecture;
- then for a pre-study (a metric review, new metrics, a calibrated prototype, a wave-plan sketch);
- then for a plan to improve that score 2× honestly, and how to schedule it against round 9;
- then for this revision of the plan, roster and prompt.

**What rev 3 adds:**
- **The pre-study:** `alt/archscore/PRE-STUDY.md` (commit `{psc}`). Its evidence sits beside it:
  - `a1/`: 30 perturbations of the 24 structure metrics, with nulls;
  - `a2/`: 45 labelled historical commits measured on both sides;
  - `a3/`: nine new metrics, each with a control, a fix and a null;
  - `b/`: the score, its frozen weights, calibration v0/v1, gate variants, sensitivity, the trajectory, and the 2× arithmetic;
  - `redteam/`.
- **Roster rev 3:** `ALT-ROSTER.json` (commit `{rc}`).
  - It is the live roster plus the deltas in `alt/build_roster_rev3.py`: F1.6 truthed to done at `f88e6af8` (#1767); score carries into F10.4, EG-B1, B2, B3, B5, B6 and B7; new groups EG-A1, EG-A2, EG-A3 and F7.5.
  - No edge was added to a planned group.
  - 70 groups, acyclic, and `brief_lint.mjs` prints `TOTAL: 0 error(s)`.
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

**Use:** report-only, as a review trigger with a calibration self-check (**EG-A1**). Whether "ΔS ≥ 0, or an explained rise" becomes a required check is a round-10 owner decision.

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

- **F1, the critical path:** F1.6 merged (#1767) → *(F2.4)* → F1.7 (+P10 barrier) → F1.8 (+P8) → F1.9 → F1.10 → F1.11.
- **F2 / F9 / EG-B10:** startable now. **EG-B8** follows F2.4.
- **F7:** **F7.5** whenever tvofi rules. It is names only, and it closes with no code if tvofi keeps the splits.
- **F6:** F6.3 (after F1.8) → F6.4.
- **F10:** F10.1b (after F1.7) → F10.1c ‖ F10.2 → F10.3 (+I2) → F10.4 (+N-structure-blind, #1545, **the metric review**) → F10.5 → F10.6 → F10.7.
- **F11:** F11.4 (after F10.4) → F11.5 → F11.7.
- **EG:**
  - EG-B2 after F1.11.
  - After F10.4: **EG-A1** ‖ EG-B3 ‖ EG-B5a, then EG-B4 and EG-B5.
  - **EG-A2** after EG-A1, EG-B3 and EG-B5.
  - EG-R1 after F11.4.
  - EG-B1 after F10.6, F11.5, EG-B4, EG-B5 and EG-B10.
  - Then **EG-A3** ‖ EG-B6, then EG-B7.
- **Structure-budget writers are serialised** (principle 2): EG-B5a, EG-B5, EG-B1, EG-B7, and now **EG-A2**, which moves optimizer and thermal-model code and may claim golden drift. EG-A1 and F7.5 write no production budget.

### 4.3 Critical path

- **Critical path:** F2.4 → F1.7 → F1.8 → F1.9 → F1.10 → F1.11 → F10.4 → F10.5 → F10.6 → EG-B1 → EG-B6 → EG-B7. That is 12 serial PRs from here.
- **The rev-3 groups add nothing to it.** EG-A1 runs at depth 8 beside EG-B3, EG-A2 at 10 beside EG-B1, and EG-A3 at 11 beside EG-B6.
- **Duration** (pre-study §9, measured from the 34 merges):
  - the serial F1 steps took 5.6–11.1 h each, a mean of 8.2 h; F1.6 took about 17 h with two review rounds;
  - 12 steps is about 67–133 h, **about 4 days at the mean** of continuous operation, and 5–7 days realistically;
  - owner-gated waits come on top;
  - AI passes 200 when EG-A2 merges, at depth 10 of 12.

### 4.4 Windows

**W0, now.** The 2026-09-29T18:15Z mandate has expired, so owner-gated work waits for renewal.
- **Stamp v6.7.11 now.** EG-B9 (#1765, sev:high) and F1.6 (#1767) are unstamped; #201 already promises this stamp.
- Apply roster rev 3 (§6 step 2).
- Land the record PR (§6 step 3).
- Post on #201.
- Dispatch **F2.4 ‖ F9.3 ‖ EG-B10**.
- tvofi's F7.5 ruling can come at any time.

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
- Then EG-B7, with F10.7 and F11.7 beside.
- Then a stamp.

**Endgame, as in rev 2**, plus one step: the round-10 decision on the score (§7, decision R3-6).

"""

SEC6 = f"""## 6. Adopting rev 3

Rev 2 is adopted. Rev 3 needs:

1. **Approval.** tvofi approves or amends this file, roster rev 3, `alt/archscore/PRE-STUDY.md`, and the §7 decisions.

2. **The roster.** Replace `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` with `ALT-ROSTER.json`.
   - If the live file has moved since `c5af8f3a`, run `alt/build_roster_rev3.py <live> <out>` on it instead. That applies:
     - (a) F1.6's resume, truthed to done at `f88e6af8` (#1767);
     - (b) the carries into F10.4, EG-B1, B2, B3, B5, B6 and B7;
     - (c) the new groups EG-A1, EG-A2, EG-A3 and F7.5.
   - Replace the placeholder with the pre-study commit (`{psc}`); `ALT-ROSTER.json` already has it.
   - Assert that all 34 merged groups read `done` at their merge SHAs.
   - Lint with `handoff/audit-r9-alt` fetched: `TOTAL: 0 error(s)`.

3. **The record PR** (the `hpo-author` App, via `tools/audit/app_push.sh`) corrects what `alt/archscore/status/LIVE-STATUS.md` found:
   - the disposition rows for #1752/#1753, #1759, #1760 and #1736 in `docs/plan-2026-09-open-issues.md` still say "scheduled", but their groups have merged or are done;
   - `docs/delivery/1771.md` says "open", but #1771 merged as `4d33b25c`;
   - `tools/audit/round9/fixplan/standing.md` lacks the "Enumerators run INSIDE the tree" rule that `c5af8f3a` added on the branch;
   - `tools/audit/round9/prestudy/ALT-ROSTER.json` is rev 2's roster copied onto main. Label it "rev 2 snapshot, not the live roster", or remove it.
   - It adds no budget and no `VERSION` edit.
   - Carries live in not-started briefs, so no carry file is owed.

4. **#1738** gains one comment listing the eleven verified metric defects, posted with `gh_comment.py` and read back. They go into F10.4's brief, and no further issue is filed.

5. **Issues for EG-A2 and EG-A3**, and for F7.5 if tvofi chooses renames, are filed **after** tvofi approves the groups. Each is filed with its evidence from the pre-study, deduped with `search_issues`, and read back.

6. **#201.** One comment, posted with `gh_comment.py` and read back.

7. **Dispatch** per §4.

"""

SEC7 = """## 7. Owner decisions rev 3 needs

**Rev 2's decisions:**
- 1–4 (register v2) were settled at EG-R0's merge (#1763, and #1762's deferral of the P2/I5 split).
- 10 was settled at F7.4's merge (#1766), which recorded the three splits. **F7.5 re-opens it** as a rename question.
- 5–9, 11 and 12 stand as rev 2 listed them.

**New in rev 3:**

| # | decision | where it gates |
|---|---|---|
| R3-1 | Adopt the architecture score as **report-only** (EG-A1), with an optional "Architecture score" line in the PR template. The template is policy. | EG-A1 merge |
| R3-2 | The F10.4 retirement list: 4 rows retired, 7 moved out of the architecture view, 7 merged into 2. **A retired row is a loosening.** | F10.4, before the push |
| R3-3 | The weights: accept the register-cost basis frozen in `b/weights.json` (hash in `b/weights.sha256`), or amend it before EG-A1 lands. A later change is a policy change. | EG-A1 |
| R3-4 | F7.5: rename or keep, for each of en `away`, sv `away` and sv `compressor`. | F7.5 |
| R3-5 | File issues for EG-A2 and EG-A3 and schedule them in round 9, or move them to round 10. | adoption |
| R3-6 | **Round 10:** after one wave of report-only data, does "ΔS ≥ 0, or a gate rise explained like a budget raise" become a required check? v2 of the metrics (§10 of the pre-study) is evaluated then, on a fresh holdout. | round 10 |
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
a = P.index('## 6. Adopting rev 2')
P = P[:a] + SEC6 + SEC7
sys.stdout.write(P)
