# Prompt (rev 4.1): the round-9 fixing orchestrator adopts lane UX (tvofi's UX decisions) into the live roster

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting. Nothing below loosens them.

**The mandate** of 2026-09-29 stands, with one exception tvofi made for this lane (U4): it does **not** pre-confirm structure-budget raises for lane UX. A UX PR that still needs a raise after designing to fit asks tvofi on #201 before its push. While that PR waits, you keep dispatching everything else.

What remains for tvofi's hands, and you request it; you never wait on it silently:
- approving reviews at the head for every UX PR that edits `tests/card_browser.mjs` (UX-1, UX-2, UX-3, UX-5, UX-6, UX-7), and for any budget raise;
- any raise confirmation under U4.

## Background

- Rev 4 (lane UI, feature issue #1791) is applied on `handoff/audit-r9-fixplan`. The live roster was at `1c3558f0` when this revision was written; origin/main was at `5dfa6684` (after #1788, F1.7).
- tvofi asked for the top five functions for usefulness and user experience, then a pre-study of items 1–4 placed in the plan, item 5 deferred as a feature request, and the design in the new identity. The decisions (2026-09-30):
  - U1: notifications are documented events plus a blueprint, with no option fields;
  - U2: the trust replay is the full day-ahead replay;
  - U3: item 5 (the shared household power budget) is deferred beyond round 9 as #1793, already filed and read back;
  - U4: "the budgets are in place to make sound architectural decisions, they can be raised as a last resort if payment does not yield better code, after codeowner approval";
  - U5: "make sure that the finished card pages gets described with screenshots in the documentation".
- Everything is on branch `handoff/audit-r9-alt`, at commit `eacbe622`:
  - `handoff/round9/state/alt/design/ux/` (commit `1a90e4cb`): `PRE-STUDY-UX.md`, `DESIGN-UX.md`, the mockups, `CONTRAST.json`;
  - `handoff/round9/state/ALT-ENDGAME-PLAN.md`, section R5 (rev 4.1);
  - `handoff/round9/state/ALT-ROSTER.json`: roster rev 4.1, 97 groups, acyclic, `brief_lint` `TOTAL: 0 error(s)`;
  - `handoff/round9/state/alt/build_roster_rev41.py`, which rebuilds it from the live file.

Before step 1, read plan section R5, `PRE-STUDY-UX.md` and `DESIGN-UX.md`.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `5dfa6684` and every commit on `handoff/audit-r9-fixplan` since `1c3558f0`, and truth each group's stage.
   - If a merge touched a file a UX brief names, check the brief still holds, and correct the figure, never the citation. The files are:
     - the card JS, `tests/card.mjs`, `tests/card_browser.mjs`, `tests/entities.py`;
     - `sensor.py`, `services.py`, `services.yaml`, `optimizer.py`, `narrative.py`, `coordinator.py`, `ledger.py`, `accuracy.py`, `diagnostics.py`, `__init__.py`;
     - `docs/dashboard-card.md`, `docs/automations.md`, `blueprints/automation/`.
   - Line numbers in `PRE-STUDY-UX.md` are at `5dfa6684`.

2. **Apply rev 4.1** to the live roster on `handoff/audit-r9-fixplan`.
   - Run `python3 handoff/round9/state/alt/build_roster_rev41.py <live wave-r9-groups.json> <out> 1a90e4cb`.
     - It refuses a file that already has R9-UX-1, a dangling edge, a cycle, and any result that lengthens the longest open chain or EG-A4's.
     - If a merged group moved the chains, it re-measures them at your roster.
   - Fetch `handoff/audit-r9-alt`, `handoff/silent-windows-plan` and `handoff/repo-reorg-plan`. Then lint with origin/main's `.claude/workflows/brief_lint.mjs`; it must print `TOTAL: 0 error(s)`.
   - Diff the output against the live file. Only these may differ:
     - the seven new groups;
     - RO-2's and RO-9's `after`;
     - the briefs of UI-3, UI-4, SW-3, RO-3, RO-4, EG-A4 and EG-B3;
     - one `_comment`.
   - Re-run the coverage (`alt/gen_coverage_rev31.py`) on the live open-issue list. #1793 is the one issue that is uncovered on purpose.
   - Commit the result as the live roster.

3. **File one feature issue for lane UX**, with the decisions U1 to U5, `DESIGN-UX.md` at `1a90e4cb`, the seven groups and their order, and a link to #1793 for the deferred item.
   - Read it back.
   - Write its number into the seven groups' `issues`. They are Part of it; the last UX PR to merge Fixes it.

4. **Post one #201 comment** with `gh_comment.py` and read it back. It covers:
   - rev 4.1 adopted, with the roster commit;
   - U1 to U5;
   - the new UX issue and #1793;
   - the chain arithmetic (unchanged; the new tie SW-1 → UX-5 → UX-7 → RO-9);
   - what is dispatched.

5. **Dispatch.**
   - UX-4 when EG-B3 merges.
   - UX-1 → UX-2 → UX-3 after UI-4.
   - UX-5 when its edges clear, then UX-6 ‖ UX-7 (siblings: merge order, not an edge).
   - Everything else continues per rev 4, one merge at a time.

## Rules specific to rev 4.1

- **Budgets are a design instrument (U4).** A UX PR designs to fit first: new logic goes where it belongs, not in the coordinator. It pays for lines only where the payment is itself the better design. The receipt freeze moving into `ledger.py` is the named example. Deleting working code or shuffling lines to hit a number is a blocked review.
- **A raise is the last resort.** The body shows why payment would not give better code, tvofi confirms before the push, and it merges only on tvofi's approving review (budget-raise-gate).
- **Documentation with screenshots (U5).** UI-3 lands the browser test's page-screenshot mode; the screenshots go to `docs/img/card`. Every card PR from UI-3 on regenerates the screenshots of the pages it changes and updates `docs/dashboard-card.md` in the same PR. A hand-captured screenshot, or a changed page without its section, is a blocked review.
- **Must keep working.** Each UX brief lists it, and `DESIGN-UX.md` repeats it. The reviewer runs each pinned test at the head.
- **UX-6's defect.** The monthly receipt's total counts the month's energy up to four times. It is fixed with the failing test first, and the body shows the wrong total before the fix.
- **Opt-in advisors are offered, never read.** `tests/entities.py` refuses card reads of sensors that are disabled by default.
- **UX-4 adds no line to `coordinator.py`**, and reads the typed payload contract EG-B3 lands.
- **The architecture score.** UX-5, UX-6 and UX-7 may land after EG-A4 makes the score required. Each shows its delta with the counters and explains a drop.
- **Rev 4's rules stand.** That includes lane UI's must-keep-working list and the one-SVG rule.
- **No `VERSION` edit.**

## Stop and tell tvofi (not ask) when

- `brief_lint` is non-zero after re-basing, and the only fix would weaken a citation;
- the build script refuses because a chain would grow;
- the diff in step 2 shows anything outside the listed entries;
- a UX PR's honest design needs a budget raise: say what, and why payment would not give better code; this one is also asked, per U4;
- SW-1, UX-5, UX-6 or UX-7 slips: they now tie the programme's longest chain.
