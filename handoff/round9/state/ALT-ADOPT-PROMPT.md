# Prompt (rev 3.1): the round-9 fixing orchestrator adopts the ALT endgame plan's rev 3.1 and runs it to completion

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting. Nothing below loosens them.

**The mandate.** tvofi extended the programme mandate to programme completion (2026-09-29). Every decision the plan needs is given, so no step waits for a human decision.

What remains for tvofi's hands is mechanical, and you request it; you never wait on it silently:
- approving reviews on code-owned and budget-raising merges;
- repository-settings changes only the admin can make;
- F10.5's new writer identity.

## Background

- Rev 2 is live on `handoff/audit-r9-fixplan` (`c5af8f3a`, 66 groups).
- EG-R0, EG-B9, F7.4 and F1.6 (#1767, `f88e6af8`) have merged, so 34 groups are done.
- tvofi then commissioned an architecture-score pre-study and an honest 2× plan, then decided every open question and asked that the plan cover every open issue.

Everything is on branch `handoff/audit-r9-alt`:

- **`handoff/round9/state/ALT-ENDGAME-PLAN.md` (rev 3.1):**
  - §2.4: the score, calibration, red team and 2× plan;
  - §4: the schedule with expected ΔS;
  - §4.6: every open issue and its closing group;
  - §6: adoption;
  - §7: the decisions as given, and what is left for tvofi's hands.
- **`handoff/round9/state/ALT-ROSTER.json`:** roster rev 3.1, commit 6a60e08a.
  - 73 groups, acyclic, and `brief_lint` prints `TOTAL: 0 error(s)`.
  - `alt/build_roster_rev3.py` rebuilds it from the live file.
- **`handoff/round9/state/alt/archscore/`** (pre-study commit 92b3ecc9):
  - `PRE-STUDY.md`;
  - evidence in `a1/`, `a2/`, `a3/`, `b/` and `redteam/` (the counters are in `redteam/counters/`);
  - `status/LIVE-STATUS.md`.
- **Issues filed and read back:**
  - #1774, the score: EG-A1, then EG-A4;
  - #1775: EG-A2;
  - #1776: EG-A3;
  - #1777: F7.5.
  - #1738 carries the eleven-defect addendum (comment `5901009400`).

Before step 1, read the plan's §2.4, §4, §4.6, §6 and §7, and the pre-study's §1, §6, §7 and §8.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `f88e6af8`.
   - Apply each to roster rev 3.1's `resume` fields.
   - If a merge touched a file a rev-3 carry cites (`away.py`, `boost.py`, `pump_arbiter.py`, `sensor.py`, `thermal_model.py`, `config_flow.py`, `optimizer.py`, `tests/structure.py`), re-measure that figure with the prototype at 92b3ecc9 and correct the figure, never the citation.
   - Re-lint with `handoff/audit-r9-alt` and the evidence refs fetched: `TOTAL: 0 error(s)`.

2. **Adopt roster rev 3.1** on `handoff/audit-r9-fixplan`: replace `.claude/workflows/wave-r9-groups.json` with `ALT-ROSTER.json`.
   - If the live file moved after `c5af8f3a`, run `alt/build_roster_rev3.py <live> <out>` and replace the literal placeholder string for the pre-study commit in its output with 92b3ecc9.
   - Assert that every merged group reads `done` at its merge SHA, and that every open issue has a closing group (`alt/gen_coverage_rev31.py`).
   - Find out why the live file kept F1.6 `not-started`, with an empty commit, through two review rounds, and fix that. The record moves at each state change (`delivery-status-tracking.md`).

3. **Stamp v6.7.11** (`web-stamp`). EG-B9 (sev:high) and F1.6 are unstamped.

4. **One record PR** via `tools/audit/app_push.sh` (never `push.sh`), with its own delivery row, no budget and no `VERSION`:
   - the stale disposition rows (#1752/#1753, #1759, #1760, #1736);
   - `docs/delivery/1771.md`;
   - `tools/audit/round9/fixplan/standing.md`, missing the "Enumerators run INSIDE the tree" rule;
   - the rev-2 roster copy at `tools/audit/round9/prestudy/ALT-ROSTER.json`: label it or remove it;
   - disposition rows for #1774–#1777 and for the 30 legacy issues ("EG-L0: re-measure then close").

5. **Post one #201 comment** with `gh_comment.py` and read it back. It says:
   - rev 3.1 is adopted, with the roster SHA;
   - the mandate runs to completion, and the decisions are in plan §7;
   - the stamp;
   - what is dispatched.

6. **Dispatch W0:** F2.4 ‖ F9.3 ‖ EG-B10 ‖ F7.5 ‖ EG-L0.
   - Then follow §4, one merge at a time, respecting every `after` edge, through EG-A4, the programme's last PR, and the endgame.

## Rules specific to rev 3.1

- **The mandate replaces "ask tvofi".** Wherever a brief says a raise or a product rule is asked before the push, the decision is given in the brief's rev-3.1 carry or in plan §7.
  - Post each budget raise's measured value and reason on #201 before the push (CLAUDE.md rule 2).
  - Request tvofi's approving review at the head for every code-owned or budget-raising merge. That is a GitHub requirement no mandate removes.
  - While a PR waits on that review, keep dispatching everything its edges allow.
- **EG-L0 (the legacy issues)** runs in W0 on the `web-triage` procedure: re-measure each claim with its own round-5 harness and a null, then close it with one read-back comment and exactly one verdict:
  - **FIXED;**
  - **SUPERSEDED:** carried into the owning group's brief first, then closed as a duplicate;
  - **REFUTED** or **NOT-REPRODUCIBLE;**
  - **LIVE-CARRIED:** never close a live defect without its carry.

  Its carries must land before their destination groups start. A live governance gap (#1191, #1193, #1196) needs a repository-settings change: record the exact setting on #201 and in `docs/HANDOVER.md` owed work, and request it. EG-L0 also dispositions #1655.
- **The score is report-only until EG-A4, and never a target.**
  - Every EG PR reports its per-metric ΔS measured **with the red-team counters**. Before EG-A1 lands, use `b/arch_score.py --delta` with `redteam/counters/`.
  - The reviewer compares it with the brief's expected ΔS.
  - The moves in the pre-study's §7 are review findings, not progress: an `Any`-typed key, a passthrough property over a private, a reflective re-spelling, a class rename. A gain that appears only without the counters is not a gain.
  - EG-A1's self-check must reproduce §6 and keep every red-team attempt NULL or inadmissible. The weights stay at their recorded hash (R3-3: accepted).
- **F10.4** lands the approved metric review (R3-2), closes #1738, and enters each new metric at its measured baseline as a re-record with the reason in the commit message.
- **EG-A2 may move solver floats.** Claim drift with its direction in `tests/golden/claimed_drift.txt`; never re-record. The structure-budget writers are serialised: EG-B5a, EG-B5, EG-B1, EG-B7, EG-A2 and EG-B11.
- **F7.5** renames display strings only: no `translation_key`, `unique_id` or entity id.
- **EG-A4** makes the score a required check (R3-6) after the report-only wave:
  - write the comparison of every reported ΔS with its review verdict into the body;
  - turn any disagreement into a planted case in EG-A1's self-check first;
  - the ruleset's required context is a settings change you request of tvofi.
- **Rev 2's rules stand:**
  - EG-B10 before EG-B1;
  - the carries bind their fixers;
  - EG-B8 before EG-B5;
  - B5 per `alt/EG-B5-DESIGN.md`;
  - B1 after stamp point (c);
  - EG refactors never block an F lane.

## Stop and tell tvofi (not ask) when

- `brief_lint` is non-zero after re-basing, and the only fix would weaken a citation;
- the resume-truthing or coverage assertion in step 2 fails;
- a merge since `f88e6af8` changes a carried figure by more than re-measurement explains;
- a PR's measured ΔS is negative and its body does not explain the rise;
- a settings change or an approving review has been requested and not given for 24 h, while nothing else is dispatchable.
