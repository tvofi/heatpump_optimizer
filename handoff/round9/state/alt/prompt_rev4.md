# Prompt (rev 4): the round-9 fixing orchestrator adopts lane UI (tvofi's design decisions) into the live roster

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting. Nothing below loosens them.

**The mandate** of 2026-09-29 stands: it runs to programme completion, so no step waits for a human decision. Rev 4 needs no new decision; tvofi gave all of them on 2026-09-30.

What remains for tvofi's hands is mechanical, and you request it; you never wait on it silently:
- approving reviews at the head: UI-1 and UI-2 (`tests/layout.json`), UI-3 and UI-4 (`tests/card_browser.mjs`);
- uploading the README social-preview image under the repository settings, after UI-2 merges (the file is named in UI-2's body).

## Background

- The live roster is rev 3.3 on `handoff/audit-r9-fixplan` at `35800d45` (lanes SW and RO added).
- tvofi commissioned a design proposal for the integration, the card and the README, then decided it on 2026-09-30:
  - D1: the "dusk" mark;
  - D2: plan chart concept A (stacked panels), "make sure the plan editor and what-if-simulator still works";
  - D2b: a fourth stat tile, indoor temperature;
  - D3: adopt the series palette;
  - D4: extend the card's colour-vision test to protanopia and tritanopia;
  - D5: no plan-lock change. A manual plan already holds its slots for its 20-hour window; tvofi withdrew the request.
- Everything is on branch `handoff/audit-r9-alt`, at commit `d66d209d`:
  - `handoff/round9/state/alt/design/`: the design of record (`DESIGN.md`, the palette checks, the scripts and every rendered asset), commit `7bca8ab3`;
  - `handoff/round9/state/ALT-ENDGAME-PLAN.md`, rev 4, sections R4.1 to R4.7 (rev 3.1 follows as its appendix);
  - `handoff/round9/state/ALT-ROSTER.json`: roster rev 4, 90 groups, acyclic, `brief_lint` `TOTAL: 0 error(s)`;
  - `handoff/round9/state/alt/build_roster_rev4.py`, which rebuilds it from the live file.

Before step 1, read plan rev 4 (R4.1 to R4.7) and `DESIGN.md` sections 1, 4 and 6.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `48786f65` and every commit on `handoff/audit-r9-fixplan` since `35800d45`.
   - Rev 4 already truths F2.4 (#1782), F9.3 (#1785), EG-B8 (#1786) and RO-1 (#1790) to done. Truth F1.7 (draft #1788 on 2026-09-30) and anything newer.
   - If a merge touched a file a UI brief names (the card JS, `tests/card.mjs`, `tests/card_browser.mjs`, `tests/layout.json`, `docs/img/make_card_figures.mjs`, `README.md`, the brand folder), check the brief still holds and correct the figure, never the citation.

2. **Apply rev 4** to the live roster on `handoff/audit-r9-fixplan`:
   - `python3 handoff/round9/state/alt/build_roster_rev4.py <live wave-r9-groups.json> <out> 7bca8ab3`. It refuses a file that already has R9-UI-1, and a dangling edge or a cycle.
   - Fetch `handoff/audit-r9-alt`, `handoff/silent-windows-plan` and `handoff/repo-reorg-plan` first, so every cited commit resolves locally. Then lint with origin/main's `.claude/workflows/brief_lint.mjs`: `TOTAL: 0 error(s)`.
   - Diff the output against the live file. Only these may differ:
     - the four truthed stages;
     - the four new groups;
     - SW-3's after, wave and brief;
     - RO-2's after;
     - the RO-3, RO-4 and F6.3 briefs;
     - one `_comment` line.
   - Re-run `alt/gen_coverage_rev31.py` on the live open-issue list: nothing uncovered.
   - Commit the result as the live roster.

3. **File one feature issue** for lane UI:
   - the decisions D1 to D5 in tvofi's words, `DESIGN.md` at `7bca8ab3`, the four groups and their order;
   - read it back, then write its number into the four groups' `issues` (Part of; the last UI PR to merge Fixes it).

4. **Post one #201 comment** with `gh_comment.py` and read it back. It says:
   - rev 4 adopted, with the roster commit;
   - D1 to D5;
   - the four truthings;
   - UI-1 dispatched.

5. **Dispatch.**
   - UI-1 now, and UI-2 after it.
   - UI-3 when F6.4 merges, and UI-4 after UI-3.
   - Everything else continues per rev 3.3, one merge at a time, respecting every `after` edge.

## Rules specific to rev 4

- **The must-keep-working list is a review blocker for UI-4.** It is in `DESIGN.md` section 4 and in UI-4's brief. The reviewer runs each pinned test at the head, and a change to either manual-plan payload or either what-if payload is a blocked verdict.
- **Failing test first on the colour-vision gate (D4).** UI-4's body shows the protan and tritan cases red on the current series definitions, then green on the palette of record.
- **Keep one chart SVG per copy.** Concept A's three panels are drawn inside it with the shared x-scale. A design that splits the chart into several SVGs changes what the lane editor, pan, wheel and the two-copies tests index, and needs a new plan, not a fixer's call.
- **Savings and score tiles stay** beside the four new ones: CLAUDE.md forbids deleting working functionality merely to fit.
- **New docs/img folders** are admitted in `tests/layout.json` by the PR that creates them, in the same commit as their files. The dead-category arm refuses an empty glob.
- **The root and in-package `icon.png` stay byte-identical** after UI-1; RO-4 re-checks before deleting the root copy.
- **Structure budgets:** no metric measures the card, so no raise is expected. If an honest re-record still needs one, the mandate confirms it: post the measured value and the reason on #201 before the push, and it merges only on tvofi's approving review (budget-raise-gate).
- **No `VERSION` edit.** Moved card states are claimed in `tests/golden/card_claimed_drift.txt`, never re-recorded.
- **Rev 3.3's rules stand**, including every SW and RO rule and the serialised structure-budget writers.

## Stop and tell tvofi (not ask) when

- `brief_lint` is non-zero after re-basing, and the only fix would weaken a citation;
- the diff in step 2 shows anything outside the listed entries;
- F6.4's scope moved in a way that changes what UI-3 may assume (the money units, the P9 grid);
- RO-3 is about to dispatch before UI-2 and UI-4 have merged;
- a review finds that concept A cannot keep a must-keep-working item without leaving the one-SVG rule.
