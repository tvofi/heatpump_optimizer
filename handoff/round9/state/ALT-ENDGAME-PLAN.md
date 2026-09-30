# Round 9 endgame, re-planned (rev 4.2): lane UI, lane UX and the product page folded into the live programme

**Status.**
- **Rev 4.2** (2026-09-30, section R6) adds lane WEB: the product page tvofi asked for, built from the reader docs and
  pinned to them by a test, then served by GitHub Pages. It is re-based to origin/main `aac8fb77` and the live roster at
  `9e63d2a3`, where rev 4.1 is applied (#1795).
- **Rev 4.1** (2026-09-30, section R5) adds lane UX, seven feature groups for tvofi's UX decisions, re-based to
  origin/main `5dfa6684` and the live roster at `1c3558f0`, where rev 4 is applied; item 5 is deferred as #1793.
- **Rev 4** was written 2026-09-30 by the same cloud review seat. It is measured at origin/main `48786f65` (v6.7.12,
  after #1790) against the **live** roster rev 3.3 on `handoff/audit-r9-fixplan` at `35800d45`, not against ALT rev 3.1.
- It adds tvofi's design decisions of 2026-09-30 as a new lane **UI** of four feature groups, two after-edges and four
  carries, truths four groups that merged on main, and changes nothing else in the live roster (§R4.5 lists the
  asserted diff).
- Rev 3.1's text follows as the appendix. Its analysis (§0–§3, §5) stands; its schedule, adoption and decisions
  (§4, §6, §7) are superseded by §R4.3–§R4.7 wherever they differ, because the fixing session moved the programme on
  after rev 3.1 was adopted.

## R4.1 What tvofi asked, and decided

On 2026-09-29 tvofi asked for "professional looking graphic design elements for the integration, the card and the
readme", with a new identity. The proposal is the private showcase page https://claude.ai/artifact/1b27QyporrvqKN6Zjm5NEg
and the Figma file https://www.figma.com/design/qczGAP3b0RCXHuYJwPsKUL. On 2026-09-30 tvofi decided:

| # | decision | tvofi's words | group |
|---|---|---|---|
| D1 | primary mark | "dusk" | UI-1, UI-3 |
| D2 | plan chart | "A, make sure the plan editor and what-if-simulator still works" | UI-4 |
| D2b | stat tiles | "include a forth, indoor temperature, stat tile" | UI-3 |
| D3 | series palette | "adopt" | UI-4 |
| D4 | colour-vision gate | "agreed" (protanopia and tritanopia beside deuteranopia) | UI-4 |
| D5 | lock a manual plan for the full horizon, no automatic replanning until it passes or auto mode is toggled | asked, then withdrawn: "didn't know 20h was already locked. If slots can not automatically be changed during that window, no change is needed" | none |

**D5, verified.** A manual plan from the card's editor lasts up to 20 hours (`MANUAL_PLAN_WINDOW_HOURS`; `build_override`
in custom_components/heatpump_optimizer/manual_plan.py clamps the expiry and refuses later slots). The solver runs each
cycle, but the pins bound it: a pinned-off step is clamped to zero and a pinned-on step gets a raised lower bound
(`_apply_pins_to_bounds`), so the slot timing does not move. The exceptions are the power level inside an on-slot, which
stays the solver's; the safety release (`_safety_release_steps`), which frees an off-pin that would breach the comfort
floor or the hot-water minimum, legionella included, and reports it on the card; a channel the editor did not send; and
the hours of the 24-hour horizon beyond the window. A mode change does not end a manual plan; its window or "Back to
automatic" does. tvofi's condition holds, so no group is added.

## R4.2 The design of record

`alt/design/` (commit `7bca8ab3`): `DESIGN.md` with the decisions, the palette of record, component contrast, the token
list, the concept-A layout rule and the must-keep-working list; the scripts that render and measure it; and every
rendered asset (brand PNGs, SVG masters, card before and after with four tiles, chart concepts, README graphics).

**A correction to the proposal page.** The page said every panel's palette passes the dataviz validator. Re-run on
2026-09-30 (`alt/design/PALETTE-CHECKS.txt`), the temperatures panel failed with outdoor in slate grey (chroma floor;
protan ΔE 2.3 against the tank colour). Outdoor is now a cold blue that keeps its dash, actioned power has a colour of
record in the power panel, and the file ends `RESULT: every panel passes both`. Today's eight-series palette fails the
same validator (protan ΔE 0.4 between house and hot-water heating; chroma floor for the grey and the teal), which the
repository test misses because it simulates deuteranopia only: that is UI-4's failing test.

**The rule that keeps the plan editor and the what-if simulator working.** The card draws each chart copy as one SVG with
one plot box, one x-scale and a y-scale per unit. The lane editor, pan, wheel and the inline/dialog indexing use only
the x mapping; the what-if panel is HTML and calls `simulate_plan` and `apply_schedule`. So concept A draws its three
panels inside that one SVG with the shared x-scale and the lanes under the bottom panel, and changes only the y side.
DESIGN.md §4 lists what must keep working; it is a review blocker for UI-4.

## R4.3 Lane UI

| PR | after | fixer / reviewer | what | owner gate |
|---|---|---|---|---|
| UI-1 brand | — | sonnet / opus | the dusk icon and logo set in the integration's brand folder (8 files, Home Assistant's spec), the 512 px package icon, the root icon byte-identical to it (RO-4's premise), SVG masters in a new docs/img folder | tests/layout.json (the folder's glob) |
| UI-2 README | UI-1 | sonnet / opus | banner, recoloured badges with the License link made absolute (the HACS break), "At a glance" table, "how it works" figure and its generator in a new docs/img folder; hero line untouched; social preview uploaded by tvofi | tests/layout.json |
| UI-3 card visual system | F6.4 | opus / opus | token layer in `cardStyleBlock`, header mark and status pill (including "manual plan until HH:MM"), **four** stat tiles with indoor temperature joining the headline signature, savings and score kept, compact legend, footnote | tests/card_browser.mjs |
| UI-4 chart concept A | UI-3 | opus / opus | failing protan/tritan test first, then the palette of record and three panels inside the one SVG; plan editor and what-if unchanged; figures, hero and docs regenerated; drift claimed | tests/card_browser.mjs |

- **Edges on existing groups:** SW-3 after UI-4, so the silent-window band is drawn once, in the power panel; RO-2 after
  UI-2 and UI-4, because the RO lane runs after every code group. Neither costs time: SW-3 already waits on SW-1 (after
  EG-B1), and RO-2 on F11.7.
- **Carries:** RO-3 (the two new docs/img folders stay; the regenerated hero and card figures move as planned), RO-4
  (re-check the two icon blobs are equal before deleting the root copy), SW-3 (tokens for the rows, the band in the power
  panel, colours under UI-4's gate), F6.3 (write the P9 contrast and reach arms against computed colours, not source
  literals, so they keep measuring after UI-3).
- **Why here:** UI-1 and UI-2 have no dependency and dispatch now. UI-3 waits for F6.4 because F6.4 is the card lane's
  last PR, F1.8 (before it) changes the money units the tiles print, and F6.3 (before it) lands the P9 grid that measures
  what UI-3 paints. UI-4 follows UI-3 on the same file. No group on either long chain gains an edge, and the lane touches
  no Python module, so EG-A4's score check and every value-bearing golden are unaffected. No structure metric measures
  the card, so no budget raise is expected.
- **Issues:** the four groups start with empty `issues`, the SW and RO convention; the orchestrator files one feature
  issue at adoption and back-fills it (§R4.6).

## R4.4 The schedule (from ALT-ROSTER.json rev 4, `alt/gen_table_rev4.py`)

Depth counts open groups only (stage other than done and rca-done). Rev 4 truths four groups that merged on main while
the live roster still showed them open: F2.4 (#1782, `3dfebc16`), F9.3 (#1785, `3d1826b2`), EG-B8 (#1786, `830f84ad`)
and RO-1 (#1790, `48786f65`). F1.7 is in review as draft #1788 on 2026-09-30; the roster keeps it not-started for the
orchestrator to truth.

Open groups: 48 of 90. Longest open chain (13): F1.7 → F1.8 → F6.3 → F6.4 → F1.11 → F10.4 → F11.4 → F11.5 → F11.7 → RO-2 → RO-7 → RO-8 → RO-9.
EG-A4 chain (12): F1.7 → F1.8 → F6.3 → F6.4 → F1.11 → F10.4 → F11.4 → F11.5 → EG-B1 → EG-B6 → EG-B7 → EG-A4.

| depth | PR | lane | open after-edges | issues (**Fixes**) | owner gate | fixer / reviewer | stage |
|---|---|---|---|---|---|---|---|
| 1 | F1.7 | F1 | — | #1644, #1649, **#1655**, **#1658** | — | opus / opus | not-started |
| 1 | UI-1 | UI | — | — | yes | sonnet / opus | not-started |
| 2 | F1.8 | F1 | F1.7 | #1644, **#1657** | — | opus / opus | not-started |
| 2 | F10.1b | F10 | F1.7 | **#1649**, #1740 | — | sonnet / opus | not-started |
| 2 | UI-2 | UI | UI-1 | — | yes | sonnet / opus | not-started |
| 3 | F1.9 | F1 | F1.8 | **#1660** | — | sonnet / opus | not-started |
| 3 | F10.1c | F10 | F10.1b | **#1756** | — | sonnet / opus | not-started |
| 3 | F10.2 | F10 | F10.1b | **#1653**, **#1656** | yes | opus / opus | not-started |
| 3 | F6.3 | F6 | F1.8 | **#1652** | yes | sonnet / opus | not-started |
| 4 | F1.10 | F1 | F1.9 | #1645, **#1654**, **#1741** | — | opus / opus | not-started |
| 4 | F10.3 | F10 | F10.2 | **#1646**, **#1663**, **#1748** | yes | opus / opus | not-started |
| 4 | F6.4 | F6 | F6.3, F1.8 | **#1687** | — | sonnet / opus | not-started |
| 5 | F1.11 | F1 | F1.10, F6.4 | **#1644**, **#1651** | — | opus / opus | not-started |
| 5 | UI-3 | UI | F6.4 | — | yes | opus / opus | not-started |
| 6 | EG-B2 | EG | F1.11 | #1739, **#1742** | — | opus / opus | not-started |
| 6 | F10.4 | F10 | F10.3, F1.11 | **#1645**, #1650, **#1661**, **#1686**, **#1738** | yes | opus / opus | not-started |
| 6 | UI-4 | UI | UI-3 | — | yes | opus / opus | not-started |
| 7 | EG-A1 | EG | F10.4 | #1774, #1738 | yes | sonnet / opus | not-started |
| 7 | EG-B3 | EG | F10.4, EG-B2 | **#1737** | — | sonnet / opus | not-started |
| 7 | EG-B5a | EG | F10.4 | #1743 | yes | opus / opus | not-started |
| 7 | F10.5 | F10 | F10.4 | — | yes | opus / opus | not-started |
| 7 | F11.4 | F11 | F10.4 | **#1650** | yes | sonnet / opus | not-started |
| 8 | EG-B4 | EG | F10.1b, F10.4, EG-B3 | **#1740** | — | opus / opus | not-started |
| 8 | EG-B5 | EG | EG-B5a, F1.10, F10.4 | **#1743**, #1748 | yes | opus / opus | not-started |
| 8 | EG-R1 | EG | F11.4 | **#1759** | yes | sonnet / opus | not-started |
| 8 | F10.6 | F10 | F10.5 | — | yes | opus / opus | not-started |
| 8 | F11.5 | F11 | F11.4 | — | yes | sonnet / opus | not-started |
| 9 | EG-A2 | EG | EG-A1, EG-B3, EG-B5 | **#1775** | — | opus / opus | not-started |
| 9 | EG-B1 | EG | F10.4, F10.6, F11.5, EG-B4, EG-B5 | **#1736** | yes | opus / opus | not-started |
| 9 | F10.7 | F10 | F10.6 | **#1758** | — | opus / opus | not-started |
| 9 | F11.7 | F11 | F11.5 | **#1757** | yes | opus / opus | not-started |
| 10 | EG-A3 | EG | EG-B1, EG-B5 | **#1776** | — | sonnet / opus | not-started |
| 10 | EG-B6 | EG | EG-B1 | **#1739** | — | sonnet / opus | not-started |
| 10 | RO-2 | RO | F10.7, F11.7, EG-R1, F11.5, F6.4, UI-2, UI-4 | — | yes | opus / opus | not-started |
| 10 | SW-1 | SW | EG-B1, F1.10, F10.1c | — | yes | opus / opus | not-started |
| 11 | EG-B11 | EG | EG-B1, EG-A3 | **#1745** | — | opus / opus | not-started |
| 11 | EG-B7 | EG | EG-B1, EG-B6 | **#1744** | yes | opus / opus | not-started |
| 11 | RO-3 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 11 | RO-4 | RO | RO-2 | — | yes | opus / opus | not-started |
| 11 | RO-5 | RO | RO-2 | — | yes | opus / opus | not-started |
| 11 | RO-6 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 11 | RO-7 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 11 | SW-2 | SW | SW-1, EG-B6 | — | yes | opus / opus | not-started |
| 11 | SW-3 | SW | SW-1, F6.4, UI-4 | — | yes | sonnet / opus | not-started |
| 11 | SW-4 | SW | SW-1 | — | yes | sonnet / opus | not-started |
| 12 | EG-A4 | EG | EG-A1, EG-B7, EG-A2, EG-A3, EG-B11 | **#1774** | — | sonnet / opus | not-started |
| 12 | RO-8 | RO | RO-7 | — | yes | opus / opus | not-started |
| 13 | RO-9 | RO | RO-3, RO-4, RO-5, RO-6, RO-8, EG-A4, SW-4 | — | yes | sonnet / opus | not-started |

**Windows.**
- **Now:** F1.7 (#1788 in review), UI-1, then UI-2; after F1.7, F1.8 and F10.1b.
- **Card lane:** F1.8 → F6.3 → F6.4, then UI-3 → UI-4 beside the F1/F10 chain, then SW-3 when SW-1 has merged.
- **Endgame:** the architecture chain to EG-A4 (12 open PRs) and the RO chain to RO-9 (13 open PRs) are the two long
  poles, as in rev 3.3; rev 4 lengthens neither.

## R4.5 The asserted diff against the live roster

`alt/build_roster_rev4.py` over `.claude/workflows/wave-r9-groups.json` at `35800d45` gives 90 groups (86 + 4), acyclic,
no dangling edge, and refuses a second run. Against the live file, exactly these entries differ: F2.4, F9.3, EG-B8 and
RO-1 (stage done at their merge commits); the four new groups;
SW-3 (after gains UI-4, wave 15 → 16, carry appended); RO-2 (after gains UI-2 and UI-4); RO-3, RO-4 and F6.3 (carry
appended); and one `_comment` line. The live waves are not strict depths (several groups sit below one plus their
after-edges), so rev 4 renumbers nothing else. `brief_lint.mjs` from origin/main prints `TOTAL: 0 error(s)`; a planted
bad path and a planted bad symbol in UI-1 each raise an error, so the check measured the new briefs.

## R4.6 Every open issue and the group that closes it

36 open issues besides #201 on 2026-09-30 (GitHub, read by this seat); uncovered: none. Lane UI closes no existing issue;
its feature issue is filed at adoption.

| issue | title | closed by | also part of |
|---|---|---|---|
| #1776 | [R9-EG-PARAM-OBJECTS] 28 functions take more than ten parameters | EG-A3 | — |
| #1775 | [R9-EG-ONE-COPY] Formulas and helpers exist in several copies | EG-A2 | — |
| #1774 | [R9-EG-ARCH-SCORE] Land the architecture score | EG-A4 | EG-A1 |
| #1759 | [R9-REGISTER-FOLD] Register never received rounds 8–9 | EG-R1 | — |
| #1758 | [R9-FREEZE-INSTRUMENT] The v6.6.0 options-flow freeze was never diagnosed | F10.7 | — |
| #1757 | [R9-GOV-HEADCOPY-PRINCIPAL] graders-head-copy omits the governance .mjs graders | F11.7 | — |
| #1756 | [R9-P7-TRACER-BLIND] F1.1's DST tracer catches 1 of P7's 3 members | F10.1c | — |
| #1748 | [R9-EG-RATCHET-MOVE-BLIND] mutation ratchet counts a moved site as new | F10.3 | EG-B5 |
| #1745 | [R9-EG-ENTRY-CONFIG] Configuration is a raw dict read per site | EG-B11 | — |
| #1744 | [R9-EG-COORDINATOR-SEAMS] Re-measure the coordinator's dhw and views seams | EG-B7 | — |
| #1743 | [R9-EG-DHW-PLANNER] Extract the DHW planner core | EG-B5 | EG-B5a |
| #1742 | [R9-EG-SURFACE-IDENTITY] Entity identity pinned at 9 constructors | EG-B2 | — |
| #1741 | [R9-EG-PLANT-FACT-COPIES] Step-start clock defined twice; 20 °C literal at 8 sites | F1.10 | — |
| #1740 | [R9-EG-STORE-VERSION] No store can change its version | EG-B4 | F10.1b |
| #1739 | [R9-EG-COLLABORATOR-INTERFACES] Collaborators reach into coordinator internals | EG-B6 | EG-B2 |
| #1738 | [R9-EG-RATCHET-DECOMPOSITION] The structural ratchet misprices decomposition | F10.4 | EG-A1 |
| #1737 | [R9-EG-TYPED-PAYLOAD] The coordinator's payload has no typed contract | EG-B3 | — |
| #1736 | [R9-EG-SOLVE-INPUTS] Each solve writes its inputs into the live hub objects | EG-B1 | — |
| #1687 | [R9-TEXT-PRODUCER-TAKES-NO-LANGUAGE-PARAMETER] | F6.4 | — |
| #1686 | [R9-STRUCTURE-METRIC-BLIND-TO-SHAPE] | F10.4 | — |
| #1663 | [R9-I2] A measured closure diverges from the dependency graph | F10.3 | — |
| #1661 | [R9-PRODUCTION-MEMBER-NO-CALLER] | F10.4 | — |
| #1660 | [R9-PERSISTED-FUTURE-INSTANT-TRUSTED-WITHOUT-BOUND] | F1.9 | — |
| #1658 | [R9-CPU-WORK-INLINE-ON-THE-EVENT-LOOP] | F1.7 | — |
| #1657 | [R9-P8] Currency or unit resolved by divergent precedence | F1.8 | — |
| #1656 | [R9-CPU-GATE-BLIND] | F10.2 | — |
| #1655 | [R9-P5] A sysid/adoption gate keyed on the wrong quantity | F1.7 | — |
| #1654 | [R9-P3] A capacity floor applied inconsistently | F1.10 | — |
| #1653 | [R9-AVOIDABLE-INTERPRETER-BOUND-RECOMPUTATION] | F10.2 | — |
| #1652 | [R9-P9] Card UI: clipping ancestor, colour token, hit target | F6.3 | — |
| #1651 | [R9-P6] A consumer reads a key no producer writes | F1.11 | — |
| #1650 | [R9-I4] Two parsers of one concept disagree | F11.4 | F10.4 |
| #1649 | [R9-P11] The only oracle for an external counterpart is a self-written double | F10.1b | F1.7 |
| #1646 | [R9-I1] A mutation kill miscounted | F10.3 | — |
| #1645 | [R9-I5] Docs or comments drift stale against the code | F10.4 | F1.10 |
| #1644 | [R9-P2] One fact decided twice by divergent predicates | F1.11 | F1.7, F1.8 |

## R4.7 Adopting rev 4, and what remains for tvofi's hands

1. Re-base: list every merge on origin/main since `48786f65` and every commit on `handoff/audit-r9-fixplan` since
   `35800d45`; truth F1.7 (in review, #1788) and anything newer. Rev 4 already truths F2.4, F9.3, EG-B8 and RO-1.
2. Apply: `python3 handoff/round9/state/alt/build_roster_rev4.py <live> <out> 7bca8ab3`, fetch `handoff/audit-r9-alt`,
   `handoff/silent-windows-plan` and `handoff/repo-reorg-plan` so every cited commit resolves, lint to
   `TOTAL: 0 error(s)`, re-run the coverage, and commit the result as the live roster.
3. File one feature issue for lane UI (the decisions, DESIGN.md at `7bca8ab3`, the four groups), read it back, and write
   its number into the four groups' `issues`.
4. One #201 comment with `gh_comment.py`, read back: rev 4 adopted with the roster commit, D1–D5, UI-1 dispatched.
5. Dispatch UI-1 now and UI-2 after it; UI-3 when F6.4 merges; UI-4 after UI-3.

The mandate of 2026-09-29 stands, and rev 4 needs no new decision. tvofi's hands, mechanical only: approving reviews
at the head for UI-1 and UI-2 (tests/layout.json) and UI-3 and UI-4 (tests/card_browser.mjs); uploading the social
preview image under the repository settings after UI-2 merges.

## R5 Rev 4.1: lane UX (explanations, advisor inbox, receipts and notifications, health)

Written 2026-09-30 by the same cloud review seat, at origin/main `5dfa6684` (after #1788, F1.7) against the live roster
on `handoff/audit-r9-fixplan` at `1c3558f0`, where rev 4 is applied (lane UI, feature issue #1791).

### R5.1 What tvofi asked and decided

tvofi asked for the top five functions that would improve usefulness and user experience, then: "Do a small pre-study
for items 1-4 and find optimal places for them in the ongoing plan. Defer 5 for later, add it as a feature request
issue." Then: "prepare the design in the new identity and do plan, roster and handover prompt as per normal".

| # | decision (2026-09-30) | where it lands |
|---|---|---|
| U1 | notifications are documented events plus a blueprint; no option fields | UX-4 |
| U2 | the trust replay is the full day-ahead replay | UX-6 |
| U3 | item 5, the shared household power budget, is deferred beyond round 9 | #1793, filed and read back |
| U4 | "the budgets are in place to make sound architectural decisions, they can be raised as a last resort if payment does not yield better code, after codeowner approval" | every UX brief; the mandate does not pre-confirm raises for this lane |
| U5 | "make sure that the finished card pages gets described with screenshots in the documentation" | UI-3 lands a page-screenshot mode in the browser test; every card group documents its pages in docs/dashboard-card.md with generated screenshots in docs/img/card |

### R5.2 The pre-study and the design

`alt/design/ux/` (commit `1a90e4cb`):
- **`PRE-STUDY-UX.md`:** the facts, with file and line at `5dfa6684`.
- **`DESIGN-UX.md`:** per group, the anatomy, copy, states, services and what must keep working.
- **Mockups in the dusk identity:** 15 renders, light and dark at 964 px, the phone at 390 px, drawn from the repository
  fixture with examples labelled.
- **`CONTRAST.json`:** 34 new colour pairs, all passing.

The findings that shape the groups:
- Four of the five ideas surface data the integration already computes:
  - six advisors, of which the card reads one;
  - receipts frozen for 24 months, published only on a sensor that is disabled by default;
  - a narrative the card cuts to one line;
  - a learning view that no entity or card reads.
- **A latent defect:** a monthly receipt's total counts the month's energy up to four times. It sums spot plus the
  space and hot-water lines that split it, plus both savings lines. It is untested. UX-6 fixes it with the failing test
  first.
- **Three setup gaps from the ideation are already fixed on main** (#123; `3110b24d`/`ed2318e6`; #110). The backlog and a
  coordinator comment are stale, and RO-4 and UX-6 correct them.
- **Budgets:** every structure metric sits at zero headroom, and no metric measures the card. So the card groups run
  early, and the backend groups put new logic outside the coordinator:
  - a notifier module;
  - the receipt freeze as a pure function in `ledger.py`;
  - sensors over published data.

### R5.3 Lane UX in the schedule

| PR | after | depth | gates | what |
|---|---|---|---|---|
| UX-1 | UI-4 | 6 | RO-2 | why now, why not: all narrative lines, idle-step explanations from published fields |
| UX-2 | UX-1 | 7 | RO-2 | advisor inbox over enabled advisors, actions through existing services |
| UX-3 | UX-2 | 8 | RO-2 | Health tab: inputs, plan freshness, waiting reasons, first-plan checklist, diagnostics link |
| UX-4 | EG-B3 | 7 | RO-2 | notifier module and blueprint, reading the typed payload EG-B3 lands |
| UX-5 | EG-B6, SW-1, EG-B5, EG-B1, EG-A2, UX-3 | 10 | RO-9 | persistent hot-water setpoint apply; exact idle sub-codes |
| UX-6 | EG-B7, EG-B11, UX-5 | 11 | RO-9 | receipt defect fixed, receipt freeze into `ledger.py`, capacity line, 24 receipts published, day-ahead snapshot, Savings views |
| UX-7 | EG-B6, EG-B11, UX-5 | 11 | RO-9 | model-status sensor, recorded next-interval prediction, richer diagnostics with redaction, the learned-model section |

**The arithmetic.** Open chains before and after, asserted by `alt/build_roster_rev41.py`, which refuses the result if
either grows:
- the longest open chain stays 12;
- EG-A4's open chain stays 11.

UX-1..4 sit at depth 8 or less, under RO-2's 9 with zero slack. UX-5..7 end at 11, under RO-9's 12.

**One consequence to watch.** SW-1 → UX-5 → UX-7 → RO-9 now ties the longest chain. SW-1, UX-5, UX-6 and UX-7 have zero
slack, so a slip in any of them delays the programme's end.

**Siblings and merge order:**
- UX-6 and UX-7 have no edge between them. Both edit the card and `sensor.py` in different functions, so whichever
  merges second merges main.
- UX-1..3 and SW-3 follow the same rule on the card.

**Carries:**
- **UI-3:** the page-screenshot mode, and document Plan, Setup, Savings and Advisor (U5).
- **UI-4:** regenerate the Plan screenshots.
- **SW-3:** merge order with UX-1..3, and screenshots of its section.
- **RO-3:** do not move `docs/img/card` screenshots.
- **RO-4:** close the three stale backlog entries with their references.
- **EG-A4:** UX-5..7 show their delta with the counters, and explain a drop.

**Re-truthing.** Rev 4.1 also corrects EG-B3's two `sensor.py` line numbers that #1788 moved (1511 → 1505, 1544 →
1539). The live roster fails `brief_lint` on it alone at `5dfa6684`, and rev 4.1 prints `TOTAL: 0 error(s)`.

### R5.4 Schedule (from ALT-ROSTER.json rev 4.1, `alt/gen_table_rev4.py`)

Open groups: 54 of 97. Longest open chain (12): F1.8 → F6.3 → F6.4 → F1.11 → F10.4 → F11.4 → F11.5 → EG-B1 → SW-1 → UX-5 → UX-7 → RO-9.
EG-A4 chain (11): F1.8 → F6.3 → F6.4 → F1.11 → F10.4 → F11.4 → F11.5 → EG-B1 → EG-B6 → EG-B7 → EG-A4.

| depth | PR | lane | open after-edges | issues (**Fixes**) | owner gate | fixer / reviewer | stage |
|---|---|---|---|---|---|---|---|
| 1 | F1.8 | F1 | — | #1644, **#1657** | — | opus / opus | not-started |
| 1 | F10.1b | F10 | — | **#1649**, #1740 | — | sonnet / opus | not-started |
| 1 | UI-1 | UI | — | #1791 | yes | sonnet / opus | not-started |
| 2 | F1.9 | F1 | F1.8 | **#1660** | — | sonnet / opus | not-started |
| 2 | F10.1c | F10 | F10.1b | **#1756** | — | sonnet / opus | not-started |
| 2 | F10.2 | F10 | F10.1b | **#1653**, **#1656** | yes | opus / opus | not-started |
| 2 | F6.3 | F6 | F1.8 | **#1652** | yes | sonnet / opus | not-started |
| 2 | UI-2 | UI | UI-1 | #1791 | yes | sonnet / opus | not-started |
| 3 | F1.10 | F1 | F1.9 | #1645, **#1654**, **#1741** | — | opus / opus | not-started |
| 3 | F10.3 | F10 | F10.2 | **#1646**, **#1663**, **#1748** | yes | opus / opus | not-started |
| 3 | F6.4 | F6 | F6.3, F1.8 | **#1687** | — | sonnet / opus | not-started |
| 4 | F1.11 | F1 | F1.10, F6.4 | **#1644**, **#1651** | — | opus / opus | not-started |
| 4 | UI-3 | UI | F6.4 | #1791 | yes | opus / opus | not-started |
| 5 | EG-B2 | EG | F1.11 | #1739, **#1742** | — | opus / opus | not-started |
| 5 | F10.4 | F10 | F10.3, F1.11 | **#1645**, #1650, **#1661**, **#1686**, **#1738** | yes | opus / opus | not-started |
| 5 | UI-4 | UI | UI-3 | #1791 | yes | opus / opus | not-started |
| 6 | EG-A1 | EG | F10.4 | #1774, #1738 | yes | sonnet / opus | not-started |
| 6 | EG-B3 | EG | F10.4, EG-B2 | **#1737** | — | sonnet / opus | not-started |
| 6 | EG-B5a | EG | F10.4 | #1743 | yes | opus / opus | not-started |
| 6 | F10.5 | F10 | F10.4 | — | yes | opus / opus | not-started |
| 6 | F11.4 | F11 | F10.4 | **#1650** | yes | sonnet / opus | not-started |
| 6 | UX-1 | UX | UI-4 | — | yes | sonnet / opus | not-started |
| 7 | EG-B4 | EG | F10.1b, F10.4, EG-B3 | **#1740** | — | opus / opus | not-started |
| 7 | EG-B5 | EG | EG-B5a, F1.10, F10.4 | **#1743**, #1748 | yes | opus / opus | not-started |
| 7 | EG-R1 | EG | F11.4 | **#1759** | yes | sonnet / opus | not-started |
| 7 | F10.6 | F10 | F10.5 | — | yes | opus / opus | not-started |
| 7 | F11.5 | F11 | F11.4 | — | yes | sonnet / opus | not-started |
| 7 | UX-2 | UX | UX-1 | — | yes | sonnet / opus | not-started |
| 7 | UX-4 | UX | EG-B3 | — | yes | sonnet / opus | not-started |
| 8 | EG-A2 | EG | EG-A1, EG-B3, EG-B5 | **#1775** | — | opus / opus | not-started |
| 8 | EG-B1 | EG | F10.4, F10.6, F11.5, EG-B4, EG-B5 | **#1736** | yes | opus / opus | not-started |
| 8 | F10.7 | F10 | F10.6 | **#1758** | — | opus / opus | not-started |
| 8 | F11.7 | F11 | F11.5 | **#1757** | yes | opus / opus | not-started |
| 8 | UX-3 | UX | UX-2 | — | yes | sonnet / opus | not-started |
| 9 | EG-A3 | EG | EG-B1, EG-B5 | **#1776** | — | sonnet / opus | not-started |
| 9 | EG-B6 | EG | EG-B1 | **#1739** | — | sonnet / opus | not-started |
| 9 | RO-2 | RO | F10.7, F11.7, EG-R1, F11.5, F6.4, UI-2, UI-4, UX-1, UX-2, UX-3, UX-4 | — | yes | opus / opus | not-started |
| 9 | SW-1 | SW | EG-B1, F1.10, F10.1c | — | yes | opus / opus | not-started |
| 10 | EG-B11 | EG | EG-B1, EG-A3 | **#1745** | — | opus / opus | not-started |
| 10 | EG-B7 | EG | EG-B1, EG-B6 | **#1744** | yes | opus / opus | not-started |
| 10 | RO-3 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 10 | RO-4 | RO | RO-2 | — | yes | opus / opus | not-started |
| 10 | RO-5 | RO | RO-2 | — | yes | opus / opus | not-started |
| 10 | RO-6 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 10 | RO-7 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 10 | SW-2 | SW | SW-1, EG-B6 | — | yes | opus / opus | not-started |
| 10 | SW-3 | SW | SW-1, F6.4, UI-4 | — | yes | sonnet / opus | not-started |
| 10 | SW-4 | SW | SW-1 | — | yes | sonnet / opus | not-started |
| 10 | UX-5 | UX | EG-B6, SW-1, EG-B5, EG-B1, EG-A2, UX-3 | — | yes | opus / opus | not-started |
| 11 | EG-A4 | EG | EG-A1, EG-B7, EG-A2, EG-A3, EG-B11 | **#1774** | — | sonnet / opus | not-started |
| 11 | RO-8 | RO | RO-7 | — | yes | opus / opus | not-started |
| 11 | UX-6 | UX | EG-B7, EG-B11, UX-5 | — | yes | opus / opus | not-started |
| 11 | UX-7 | UX | EG-B6, EG-B11, UX-5 | — | yes | opus / opus | not-started |
| 12 | RO-9 | RO | RO-3, RO-4, RO-5, RO-6, RO-8, EG-A4, SW-4, UX-5, UX-6, UX-7 | — | yes | sonnet / opus | not-started |

### R5.5 Every open issue and the group that closes it

35 open issues besides #201 on 2026-09-30, read after #1788 closed #1655 and #1658; uncovered: none.
#1793 (item 5) was filed after this table and is deliberately uncovered: it is deferred beyond round 9.

| issue | title | closed by | also part of |
|---|---|---|---|
| #1791 | Lane UI: new identity, card visual system, plan chart concept A and README graphics | — | UI-1, UI-2, UI-3, UI-4 |
| #1776 | [R9-EG-PARAM-OBJECTS] 28 functions take more than ten parameters | EG-A3 | — |
| #1775 | [R9-EG-ONE-COPY] Formulas and helpers exist in several copies | EG-A2 | — |
| #1774 | [R9-EG-ARCH-SCORE] Land the architecture score | EG-A4 | EG-A1 |
| #1759 | [R9-REGISTER-FOLD] Register never received rounds 8–9 | EG-R1 | — |
| #1758 | [R9-FREEZE-INSTRUMENT] The v6.6.0 options-flow freeze was never diagnosed | F10.7 | — |
| #1757 | [R9-GOV-HEADCOPY-PRINCIPAL] graders-head-copy omits the governance .mjs graders | F11.7 | — |
| #1756 | [R9-P7-TRACER-BLIND] F1.1's DST tracer catches 1 of P7's 3 members | F10.1c | — |
| #1748 | [R9-EG-RATCHET-MOVE-BLIND] mutation ratchet counts a moved site as new | F10.3 | EG-B5 |
| #1745 | [R9-EG-ENTRY-CONFIG] Configuration is a raw dict read per site | EG-B11 | — |
| #1744 | [R9-EG-COORDINATOR-SEAMS] Re-measure the coordinator's dhw and views seams | EG-B7 | — |
| #1743 | [R9-EG-DHW-PLANNER] Extract the DHW planner core | EG-B5 | EG-B5a |
| #1742 | [R9-EG-SURFACE-IDENTITY] Entity identity pinned at 9 constructors | EG-B2 | — |
| #1741 | [R9-EG-PLANT-FACT-COPIES] Step-start clock defined twice; 20 °C literal at 8 sites | F1.10 | — |
| #1740 | [R9-EG-STORE-VERSION] No store can change its version | EG-B4 | F10.1b |
| #1739 | [R9-EG-COLLABORATOR-INTERFACES] Collaborators reach into coordinator internals | EG-B6 | EG-B2 |
| #1738 | [R9-EG-RATCHET-DECOMPOSITION] The structural ratchet misprices decomposition | F10.4 | EG-A1 |
| #1737 | [R9-EG-TYPED-PAYLOAD] The coordinator's payload has no typed contract | EG-B3 | — |
| #1736 | [R9-EG-SOLVE-INPUTS] Each solve writes its inputs into the live hub objects | EG-B1 | — |
| #1687 | [R9-TEXT-PRODUCER-TAKES-NO-LANGUAGE-PARAMETER] | F6.4 | — |
| #1686 | [R9-STRUCTURE-METRIC-BLIND-TO-SHAPE] | F10.4 | — |
| #1663 | [R9-I2] A measured closure diverges from the dependency graph | F10.3 | — |
| #1661 | [R9-PRODUCTION-MEMBER-NO-CALLER] | F10.4 | — |
| #1660 | [R9-PERSISTED-FUTURE-INSTANT-TRUSTED-WITHOUT-BOUND] | F1.9 | — |
| #1657 | [R9-P8] Currency or unit resolved by divergent precedence | F1.8 | — |
| #1656 | [R9-CPU-GATE-BLIND] | F10.2 | — |
| #1654 | [R9-P3] A capacity floor applied inconsistently | F1.10 | — |
| #1653 | [R9-AVOIDABLE-INTERPRETER-BOUND-RECOMPUTATION] | F10.2 | — |
| #1652 | [R9-P9] Card UI: clipping ancestor, colour token, hit target | F6.3 | — |
| #1651 | [R9-P6] A consumer reads a key no producer writes | F1.11 | — |
| #1650 | [R9-I4] Two parsers of one concept disagree | F11.4 | F10.4 |
| #1649 | [R9-P11] The only oracle for an external counterpart is a self-written double | F10.1b | — |
| #1646 | [R9-I1] A mutation kill miscounted | F10.3 | — |
| #1645 | [R9-I5] Docs or comments drift stale against the code | F10.4 | F1.10 |
| #1644 | [R9-P2] One fact decided twice by divergent predicates | F1.11 | F1.8 |

### R5.6 Asserted diff against the live roster

- 97 groups (90 + 7).
- Changed:
  - the seven new groups;
  - RO-2's and RO-9's `after`;
  - the briefs of UI-3, UI-4, SW-3, RO-3, RO-4 and EG-A4 (carries), and of EG-B3 (the re-truthed line numbers);
  - one `_comment`.
- No stage and no issue changes.
- A second run is refused.
- `brief_lint` from origin/main prints `TOTAL: 0 error(s)`, and a planted bad path and a planted bad symbol in UX-4 each
  raise an error.

---

## R6 Rev 4.2: lane WEB (the product page, pinned to the master documentation)

Written 2026-09-30 by the same cloud review seat. It is measured at origin/main `aac8fb77` (after #1794, which touched
no reader document) against the live roster on `handoff/audit-r9-fixplan` at `9e63d2a3`, where rev 4.1 is applied and
lane UX is Part of #1795.

### R6.1 What tvofi asked and decided

tvofi asked: "Design a full product web page, based on the user facing documentation in the repo, in the same design
language as the showcase page, then make a rev 4.2 of the plan where implementation of this page and pining it to the
master documentation is added."

| # | decision (2026-09-30) | where it lands |
|---|---|---|
| W1 | pinning is test-pinned and linked: every claim carries a source anchor into the README or a reader doc, a test refuses drift, and the README links the page | WEB-1 |
| W2 | the page is served by GitHub Pages through a workflow | WEB-2 |
| S3 | a design decision, open to tvofi: no savings percentage, because the docs call the only one a one-off measurement on the author's house | the page; DESIGN-SITE.md |

The master documentation is `README.md`: `hacs.json` renders it as the integration's page, and its Documentation
table indexes every reader doc. Nothing in the tree is a web page today: there is no HTML, no Pages setup and no
`CNAME`.

### R6.2 The design

`alt/design/site/` (commit `2b5031bf`):
- `index.html`: the page, in the showcase's identity (frost, ink, fjord, ember; Outfit and Source Sans 3, self-hosted;
  the dusk mark). Its sections are the hero with the plan chart, four tiles, nine features, how it works, the card
  gallery, works with, get started, known limitations, written with AI, documentation, and the footer.
- Every sentence of fact is quoted from a README or reader-doc section and carries that section's GitHub heading slug
  in `data-src`.
- `check_site.py`: the pin prototype. It derives the claim set from the page and the fact set from the documents at a
  git ref, and every arm has an anchor.
  - It is green at `5dfa6684` and `aac8fb77`.
  - `controls.py` plants each refusal: a wrong number, a reworded quote, a dead slug, a dropped feature, an extra or
    missing docs row, a number outside a claim, a version literal, a missing image, an external script, a
    third-party stylesheet or font URL, a README sentence changed under an unchanged page, and both anchors. Each
    turns it red (`SITE-CHECKS.txt`).
- `CONTRAST.json`: every colour pair passes in both themes.
- `shots/`: renders at 1280 and 390 px, light and dark, with no horizontal overflow.
- `DESIGN-SITE.md`: decisions S1–S6, the claim rules, the implementation map, the hosting design and the gallery
  slots.
- Published for review as a private artifact; the showcase gains a "Product page" section.

### R6.3 Lane WEB in the schedule

| group | scope | after | depth | gates | owner gate |
|---|---|---|---|---|---|
| **WEB-1** page and pin | the page as `index.html` at the root of `docs/` with its fonts; one new arm in `tests/doc_claims.py` ported from `check_site.py`; the README link row; `INERT_EXCEPT`; one `tests/layout.json` glob | UI-2, UI-4, F10.4 | 6 | RO-2 | `tests/closure.py`, `tests/layout.json` |
| **WEB-2** Pages deploy | one workflow under `.github/workflows`: on a `v*` tag and on dispatch; stages the page and every png and svg under `docs/`, never a `.md`; runs no repository script; the README row switches to the served URL | WEB-1 | 7 | RO-3 | `.github/workflows`; tvofi enables Pages once |

Why these edges:
- UI-2 lands the mark masters, the how-it-works figure and the README table.
- UI-4 lands the concept-A chart at the README hero path the page shows.
- F10.4 is the sole owner of `tests/doc_claims.py` until it merges (the I5 barrier).
- RO-2 follows WEB-1 because both edit `tests/layout.json` and `tests/closure.py`.
- RO-3 follows WEB-2 because it moves the images the page references, and the pin refuses a dead reference.

Chain arithmetic:
- WEB-1 at depth 6 and WEB-2 at depth 7 sit under RO-2 (9) and RO-3 (10), with slack.
- The longest open chain stays 12, and EG-A4's stays 11. The build script asserts both.
- WEB-1 does not edit `tests/README.md`, which is code-owned and in the F11.4/F11.5 lane. If `tests/entities.py`
  demands a line there, WEB-1 orders after F11.5 (depth 8, still under RO-2's 9).

Carries:
- **RO-3** moves the page's image references with the images. The workflow stages by pattern, so it needs no edit.
- **RO-4**: archiving `docs/backlog.md` removes its README row, and the pin makes the page follow in the same PR.
- **RO-9** keeps the layout glob in its enforcement.
- **UX-1, 2, 3, 5, 6, 7**: a card page whose screenshot the PR regenerates takes its gallery slot on the page (U5
  extended). A README feature paragraph is forced onto the page by the pin.

### R6.4 Schedule (from ALT-ROSTER.json rev 4.2, `alt/gen_table_rev4.py`)

Open groups: 56 of 99. Longest open chain (12): F1.8 → F6.3 → F6.4 → F1.11 → F10.4 → F11.4 → F11.5 → EG-B1 → SW-1 → UX-5 → UX-7 → RO-9.
EG-A4 chain (11): F1.8 → F6.3 → F6.4 → F1.11 → F10.4 → F11.4 → F11.5 → EG-B1 → EG-B6 → EG-B7 → EG-A4.

| depth | PR | lane | open after-edges | issues (**Fixes**) | owner gate | fixer / reviewer | stage |
|---|---|---|---|---|---|---|---|
| 1 | F1.8 | F1 | — | #1644, **#1657** | — | opus / opus | not-started |
| 1 | F10.1b | F10 | — | **#1649**, #1740 | — | sonnet / opus | not-started |
| 1 | UI-1 | UI | — | #1791 | yes | sonnet / opus | not-started |
| 2 | F1.9 | F1 | F1.8 | **#1660** | — | sonnet / opus | not-started |
| 2 | F10.1c | F10 | F10.1b | **#1756** | — | sonnet / opus | not-started |
| 2 | F10.2 | F10 | F10.1b | **#1653**, **#1656** | yes | opus / opus | not-started |
| 2 | F6.3 | F6 | F1.8 | **#1652** | yes | sonnet / opus | not-started |
| 2 | UI-2 | UI | UI-1 | #1791 | yes | sonnet / opus | not-started |
| 3 | F1.10 | F1 | F1.9 | #1645, **#1654**, **#1741** | — | opus / opus | not-started |
| 3 | F10.3 | F10 | F10.2 | **#1646**, **#1663**, **#1748** | yes | opus / opus | not-started |
| 3 | F6.4 | F6 | F6.3, F1.8 | **#1687** | — | sonnet / opus | not-started |
| 4 | F1.11 | F1 | F1.10, F6.4 | **#1644**, **#1651** | — | opus / opus | not-started |
| 4 | UI-3 | UI | F6.4 | #1791 | yes | opus / opus | not-started |
| 5 | EG-B2 | EG | F1.11 | #1739, **#1742** | — | opus / opus | not-started |
| 5 | F10.4 | F10 | F10.3, F1.11 | **#1645**, #1650, **#1661**, **#1686**, **#1738** | yes | opus / opus | not-started |
| 5 | UI-4 | UI | UI-3 | #1791 | yes | opus / opus | not-started |
| 6 | EG-A1 | EG | F10.4 | #1774, #1738 | yes | sonnet / opus | not-started |
| 6 | EG-B3 | EG | F10.4, EG-B2 | **#1737** | — | sonnet / opus | not-started |
| 6 | EG-B5a | EG | F10.4 | #1743 | yes | opus / opus | not-started |
| 6 | F10.5 | F10 | F10.4 | — | yes | opus / opus | not-started |
| 6 | F11.4 | F11 | F10.4 | **#1650** | yes | sonnet / opus | not-started |
| 6 | UX-1 | UX | UI-4 | #1795 | yes | sonnet / opus | not-started |
| 6 | WEB-1 | WEB | UI-2, UI-4, F10.4 | — | yes | sonnet / opus | not-started |
| 7 | EG-B4 | EG | F10.1b, F10.4, EG-B3 | **#1740** | — | opus / opus | not-started |
| 7 | EG-B5 | EG | EG-B5a, F1.10, F10.4 | **#1743**, #1748 | yes | opus / opus | not-started |
| 7 | EG-R1 | EG | F11.4 | **#1759** | yes | sonnet / opus | not-started |
| 7 | F10.6 | F10 | F10.5 | — | yes | opus / opus | not-started |
| 7 | F11.5 | F11 | F11.4 | — | yes | sonnet / opus | not-started |
| 7 | UX-2 | UX | UX-1 | #1795 | yes | sonnet / opus | not-started |
| 7 | UX-4 | UX | EG-B3 | #1795 | yes | sonnet / opus | not-started |
| 7 | WEB-2 | WEB | WEB-1 | — | yes | sonnet / opus | not-started |
| 8 | EG-A2 | EG | EG-A1, EG-B3, EG-B5 | **#1775** | — | opus / opus | not-started |
| 8 | EG-B1 | EG | F10.4, F10.6, F11.5, EG-B4, EG-B5 | **#1736** | yes | opus / opus | not-started |
| 8 | F10.7 | F10 | F10.6 | **#1758** | — | opus / opus | not-started |
| 8 | F11.7 | F11 | F11.5 | **#1757** | yes | opus / opus | not-started |
| 8 | UX-3 | UX | UX-2 | #1795 | yes | sonnet / opus | not-started |
| 9 | EG-A3 | EG | EG-B1, EG-B5 | **#1776** | — | sonnet / opus | not-started |
| 9 | EG-B6 | EG | EG-B1 | **#1739** | — | sonnet / opus | not-started |
| 9 | RO-2 | RO | F10.7, F11.7, EG-R1, F11.5, F6.4, UI-2, UI-4, UX-1, UX-2, UX-3, UX-4, WEB-1 | — | yes | opus / opus | not-started |
| 9 | SW-1 | SW | EG-B1, F1.10, F10.1c | — | yes | opus / opus | not-started |
| 10 | EG-B11 | EG | EG-B1, EG-A3 | **#1745** | — | opus / opus | not-started |
| 10 | EG-B7 | EG | EG-B1, EG-B6 | **#1744** | yes | opus / opus | not-started |
| 10 | RO-3 | RO | RO-2, WEB-2 | — | yes | sonnet / opus | not-started |
| 10 | RO-4 | RO | RO-2 | — | yes | opus / opus | not-started |
| 10 | RO-5 | RO | RO-2 | — | yes | opus / opus | not-started |
| 10 | RO-6 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 10 | RO-7 | RO | RO-2 | — | yes | sonnet / opus | not-started |
| 10 | SW-2 | SW | SW-1, EG-B6 | — | yes | opus / opus | not-started |
| 10 | SW-3 | SW | SW-1, F6.4, UI-4 | — | yes | sonnet / opus | not-started |
| 10 | SW-4 | SW | SW-1 | — | yes | sonnet / opus | not-started |
| 10 | UX-5 | UX | EG-B6, SW-1, EG-B5, EG-B1, EG-A2, UX-3 | #1795 | yes | opus / opus | not-started |
| 11 | EG-A4 | EG | EG-A1, EG-B7, EG-A2, EG-A3, EG-B11 | **#1774** | — | sonnet / opus | not-started |
| 11 | RO-8 | RO | RO-7 | — | yes | opus / opus | not-started |
| 11 | UX-6 | UX | EG-B7, EG-B11, UX-5 | #1795 | yes | opus / opus | not-started |
| 11 | UX-7 | UX | EG-B6, EG-B11, UX-5 | #1795 | yes | opus / opus | not-started |
| 12 | RO-9 | RO | RO-3, RO-4, RO-5, RO-6, RO-8, EG-A4, SW-4, UX-5, UX-6, UX-7 | — | yes | sonnet / opus | not-started |

### R6.5 Every open issue and the group that closes it

The list is the 37 open issues listed on GitHub at the time of writing (#201 excluded; `alt/open_issues_rev42.json`).
#1793 is uncovered on purpose (deferred, U3). The lane WEB feature issue does not exist yet: the orchestrator files it
on adoption, and it then covers WEB-1 and WEB-2.

| issue | title | closed by | also part of |
|---|---|---|---|
| #1795 | Lane UX: explanations, advisor inbox, receipts and notifications, health (round-9 rev 4.1) | — | UX-1, UX-2, UX-3, UX-4, UX-5, UX-6, UX-7 |
| #1793 | [FEATURE] Shared household power budget: publish the heat pump's planned load and flexibil | — | — |
| #1791 | Lane UI: new identity, card visual system, plan chart concept A and README graphics | — | UI-1, UI-2, UI-3, UI-4 |
| #1776 | [R9-EG-PARAM-OBJECTS] 28 functions take more than ten parameters | EG-A3 | — |
| #1775 | [R9-EG-ONE-COPY] Formulas and helpers exist in several copies | EG-A2 | — |
| #1774 | [R9-EG-ARCH-SCORE] Land the architecture score | EG-A4 | EG-A1 |
| #1759 | [R9-REGISTER-FOLD] Register never received rounds 8–9 | EG-R1 | — |
| #1758 | [R9-FREEZE-INSTRUMENT] The v6.6.0 options-flow freeze was never diagnosed | F10.7 | — |
| #1757 | [R9-GOV-HEADCOPY-PRINCIPAL] graders-head-copy omits the governance .mjs graders | F11.7 | — |
| #1756 | [R9-P7-TRACER-BLIND] F1.1's DST tracer catches 1 of P7's 3 members | F10.1c | — |
| #1748 | [R9-EG-RATCHET-MOVE-BLIND] mutation ratchet counts a moved site as new | F10.3 | EG-B5 |
| #1745 | [R9-EG-ENTRY-CONFIG] Configuration is a raw dict read per site | EG-B11 | — |
| #1744 | [R9-EG-COORDINATOR-SEAMS] Re-measure the coordinator's dhw and views seams | EG-B7 | — |
| #1743 | [R9-EG-DHW-PLANNER] Extract the DHW planner core | EG-B5 | EG-B5a |
| #1742 | [R9-EG-SURFACE-IDENTITY] Entity identity pinned at 9 constructors | EG-B2 | — |
| #1741 | [R9-EG-PLANT-FACT-COPIES] Step-start clock defined twice; 20 °C literal at 8 sites | F1.10 | — |
| #1740 | [R9-EG-STORE-VERSION] No store can change its version | EG-B4 | F10.1b |
| #1739 | [R9-EG-COLLABORATOR-INTERFACES] Collaborators reach into coordinator internals | EG-B6 | EG-B2 |
| #1738 | [R9-EG-RATCHET-DECOMPOSITION] The structural ratchet misprices decomposition | F10.4 | EG-A1 |
| #1737 | [R9-EG-TYPED-PAYLOAD] The coordinator's payload has no typed contract | EG-B3 | — |
| #1736 | [R9-EG-SOLVE-INPUTS] Each solve writes its inputs into the live hub objects | EG-B1 | — |
| #1687 | [R9-TEXT-PRODUCER-TAKES-NO-LANGUAGE-PARAMETER] | F6.4 | — |
| #1686 | [R9-STRUCTURE-METRIC-BLIND-TO-SHAPE] | F10.4 | — |
| #1663 | [R9-I2] A measured closure diverges from the dependency graph | F10.3 | — |
| #1661 | [R9-PRODUCTION-MEMBER-NO-CALLER] | F10.4 | — |
| #1660 | [R9-PERSISTED-FUTURE-INSTANT-TRUSTED-WITHOUT-BOUND] | F1.9 | — |
| #1657 | [R9-P8] Currency or unit resolved by divergent precedence | F1.8 | — |
| #1656 | [R9-CPU-GATE-BLIND] | F10.2 | — |
| #1654 | [R9-P3] A capacity floor applied inconsistently | F1.10 | — |
| #1653 | [R9-AVOIDABLE-INTERPRETER-BOUND-RECOMPUTATION] | F10.2 | — |
| #1652 | [R9-P9] Card UI: clipping ancestor, colour token, hit target | F6.3 | — |
| #1651 | [R9-P6] A consumer reads a key no producer writes | F1.11 | — |
| #1650 | [R9-I4] Two parsers of one concept disagree | F11.4 | F10.4 |
| #1649 | [R9-P11] The only oracle for an external counterpart is a self-written double | F10.1b | — |
| #1646 | [R9-I1] A mutation kill miscounted | F10.3 | — |
| #1645 | [R9-I5] Docs or comments drift stale against the code | F10.4 | F1.10 |
| #1644 | [R9-P2] One fact decided twice by divergent predicates | F1.11 | F1.8 |

### R6.6 Asserted diff against the live roster

- 99 groups (97 + 2).
- Changed:
  - the two new groups;
  - RO-2's and RO-3's `after`;
  - appended carries on the briefs of RO-3, RO-4, RO-9, UX-1, UX-2, UX-3, UX-5, UX-6 and UX-7;
  - one `_comment`.
- No stage, no wave outside the new groups, and no issue changes.
- The build script refuses a roster without rev 4.1 and a second run.
- `brief_lint` from origin/main prints `TOTAL: 0 error(s)`, and the live file does too. Four planted errors in WEB-1
  (a bad path at the cited SHA, a bad path, a bad path:line and a bad symbol) are each reported.

---

# Appendix: rev 3.1 as adopted (superseded where §R4 differs)

## Rev 3.1 title: Round 9 endgame, re-planned (rev 3.1): the architecture score, its 2× plan, every open issue, and the programme where it stands

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
- **The pre-study:** `alt/archscore/PRE-STUDY.md` (commit `92b3ecc9`). Its evidence sits beside it:
  - `a1/`: 30 perturbations of the 24 structure metrics, with nulls;
  - `a2/`: 45 labelled historical commits measured on both sides;
  - `a3/`: nine new metrics, each with a control, a fix and a null;
  - `b/`: the score, its frozen weights, calibration v0/v1, gate variants, sensitivity, the trajectory, and the 2× arithmetic;
  - `redteam/`.
- **Roster rev 3:** `ALT-ROSTER.json` (commit `6a60e08a`).
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

## 0. The verdict on each draft item

| draft item | verdict | the measured reason | replaced by |
|---|---|---|---|
| EG-0a roster resume sidecar | **keep, out of tree** | The round-9 roster is not on main, so an in-tree sidecar is an orphan tracked file. `delivery-status-tracking.md` and `brief_lint` both read `resume` from the groups file. The wipe is live: the live roster shows 17 of the 27 merged groups as `not-started`. | Fix gen.py to carry each group's existing `resume` forward on regenerate, on the fixplan branch (§6 step 2) |
| EG-0b symbol-anchor 19 line pins | **drop** | The 14 "pins" are `last_measured.*.survivor_lines` in `tests/mutation_budgets.json`, a record of one run that no check reads against the tree. The ledger is already content-anchored. carry-1645's anchors are prose the carry itself tells readers not to trust. It would also have collided with F10.3/F10.5/F10.6 on `mutation_table.py` (principle 2). | none |
| EG-S1 surfaces identity core | **keep, re-scoped and re-timed** | In W3 it collides with the `sensor.py` borrows of F1.7, F6.4 and F1.11. A merged-config helper in `entity.py` would make the core import the surface layer. The surfaces already have `coordinator.effective_config`. It had no identity null control. | **EG-B2** (#1742) |
| EG-C1 clock/helper dedup | **shrink and re-home** | Not F1.6's files (`optimizer.py` is F2's). The "70 raw clock sites" are the P7 behaviour surface, not a dedup (72 real calls by AST). The rounding lead is refuted (§2.2). | Carry **A2 → R9-F1.10** (#1741) |
| EG-O1 `optimizer_dhw.py` | **keep, redesigned and re-sequenced** | In W2 it lands before the optimizer borrows of F1.7, F1.10 and F10.4 (principle 3) and before the F10.4 instrument (principle 1). It is unpriced: the tests call private DHW methods (the design spec counts them exactly), and a per-module duplication detector cannot see duplication a split leaves across modules. | **EG-B5a then EG-B5** (#1743), opted in; **EG-B8** (#1747) first |
| EG-X1 closures.json split | **drop** | `.gitattributes:24` already routes `tests/closures.json` to the `ledgermerge` driver: key-by-key merge, 60 conflicts to 0 on its own replay. Neither pre-study mentions it. | none |
| EG-X2 features.py split | **defer, round-10 pre-study** | Five premises fail (§1.1). | §5 |
| EG-S2 availability rule | **defer** | Unknown versus unavailable is a product ruling (the A3(e)/C15 precedent), and D8-s3-61 is F7.2's to fix. | §5 |
| EG-N1/N2 coordinator seams | **replace** | Not refused on budget grounds (§3). The #193 halts say hub attributes bind the class; B1 removes three of those hubs' per-solve writes, so re-measure and then extract. | **EG-B7** (#1744) |

**New, found by this review:**
- **EG-B0 and EG-B1** (#1736): solve-scoped hub writes, a five-instance recurring class.
- **EG-B3** (#1737): typed payload.
- **A1 → F10.4** (#1738): the ratchet misprices decomposition.
- **EG-B2 and EG-B6** (#1739): collaborator interfaces.
- **A4 → F10.1b and EG-B4** (#1740): store versions.
- **EG-B8** (#1747): the DHW-block replan defect, found while designing B5.
- **Carry → R9-F10.3** (#1748): the per-site ratchet is blind to a move.
- **Deferred:** #1745, typed configuration.

## 1. Review of the draft

### 1.1 Premises that do not hold

**EG-X2's five failed premises:**
1. **Classes are not the unit.** The 112 top-level classes of `tests/features.py` are fakes and stubs (`_T3Store`, `_R9F13Hass`), not test blocks. The units are 196 `R.section` blocks over one shared header: `NOW` is used 110 times, and helpers are defined mid-file and reused 13k lines later. `features.py` takes no CLI arguments.
2. **The ledger pins name the file.** 352 of the 415 `killed_by` ledger pins name `tests/features.py` as their killer (`grep -rh '"killed_by"' tests/mutation_ledger | sort | uniq -c`). The pre-study's "zero formal pins" is wrong, and a split has to re-attribute every one.
3. **Autofix cannot record new scripts.** `ci-autofix.md` says autofix "cannot invent a trace", so the pre-study's "~120-150 closures re-derived by CI autofix" does not happen. Each new script needs a recording.
4. **New scripts must be wired.** A new `tests/*.py` fails `run.sh` as `UNWIRED TEST` unless it is wired in, and `tests/README.md`, which describes the scripts, is code-owned policy.
5. **Touches are not conflicts.** "8 of 8 merges touched it" measures touches. No conflict count exists yet.

**EG-O1, EG-0b and EG-X1:** see the table in §0.

### 1.2 Sequencing against the draft's own principles

- **EG-O1 in W2.** It violates principle 3 against the optimizer borrows of F1.7, F1.10 and F10.4, and principle 1 against F10.4. The source pre-study said "after F2 drains **+ F10.4**".
- **W6 before W7.** W6 (X1/X2) is placed before W7 (F10.4), while the draft's own open question 2 recommends after F10.4.
- **EG-N timing.** EG-N is placed "post-F1.11, pre-register"; the pre-study says "last: after F1 drains, F10.4, register, prune".
- **EG-0b.** "Infra wave, immediately, no lane conflicts" is false (§0).

### 1.3 Costs it did not price

- **Per-module duplication.** `duplication_blocks` compares functions within one module (`structure.py:1080-1085`). Measured: a copy in another module leaves it unmoved, the same copy in its own module moves it by two. A move that splits a duplicated pair across modules therefore lowers it with no duplication removed. That is #1738 arm (a). For EG-B5 specifically, the design keeps both closures in `optimizer.py` and removes them in EG-B5a.
- **Out-of-class reads.** Out-of-class reads of coordinator state are unpriced (measured; #1738 arm (b)). A seam moved into its own module escapes the ratchet in exactly the way `docs/HANDOVER.md:58` refuses.
- **`classes_over_300`.** It scores the extraction itself as the one regression (#750; #1738 arm (c)).
- **EG-S1's registry sensitivity.** The `entity_id` pin is registry-compatibility sensitive, and the draft named no before/after identity snapshot.

### 1.4 Slips

- F1.4 appears in both the merged list and the remaining list.
- 30 PRs at 0.8 PR/h is about 37 h, not 30-34 h. Either way, a throughput figure does not bound a serial chain; §4.3 does.
- The surfaces pre-study's "rationale comment copied verbatim 5×" is one comment plus four pointers.
- Its count of 67 `coordinator.data or {}` sites in `sensor.py` is 66.

### 1.5 The draft's open questions, answered

1. **EG-O1 against F10.2:** a non-question. F10.2 owns `stress.py`, `stress_budgets.json` and `replay.py`, and a pure move changes no solve CPU. The real constraints are the optimizer borrows of F1.7, F1.10 and F10.4, the F10.4 instrument, and B1's interface, so EG-B5 goes after F10.4. The design spec showed B1 is not a prerequisite, so B5 goes before B1.
2. **EG-X2's window:** neither. Round 10, behind a pre-study (§5).
3. **EG-N opt-in:** replaced by EG-B7, a measured go/no-go after B1.
4. **Reviewer seats for EG items:** yes, all of them. That means `fix-review.md` from a detached worktree at the head SHA with the finder's enumerator at both ends. EG-B0 is a `root-cause.md` seat.
5. **Mandate:** W0 and W1 fit inside 2026-09-29T18:15Z. Nothing in lane EG gates an F-lane, so the EG tail can wait for renewal without holding the fixes.

## 2. What the draft misses: filed, verified, dispositioned

| issue | finding (measured at `31394964`) | evidence (`alt/evidence/`) | destination |
|---|---|---|---|
| **#1736** | Each solve writes 23 fields at 26 sites into the live, unfrozen `_opt_config` / `_thermal_params` / `_current_state`; the `finally` unwinds only the 6 setback fields. Four closed issues (#240, #1517, #1529, #1683) plus the configured-target rule are one class across three rounds. | `m1_hub_writes.*` | **EG-B0** root-cause seat now; **EG-B1** refactor |
| **#1737** | The payload is untyped: the coordinator base is unparameterised, and there are 0 TypedDicts. 120 top-level keys are read at 212 sites; `horizon_hours` has no producer (F1.11 fixes that instance). | `m2_payload.*` | **EG-B3** |
| **#1738** | The ratchet misprices decomposition in three ways: (a) per-module duplication, (b) out-of-class reach, (c) `classes_over_300` on extraction. | `m5_dup_control.*`, `m3_ratchet_control.*`, `m7_classes_over_300.out` | Carry **A1 → R9-F10.4** |
| **#1739** | 84 private coordinator reaches across 13 modules (`pump_arbiter.py` 37), including 3 writes; several reads bypass existing public accessors (`effective_config`, `mode`, `optimization_running`). | `m3_reach.*` | **EG-B2** (surfaces), **EG-B6** (collaborators) |
| **#1740** | No store can change version: there is no migration hook, and the stub drops `version`. On a bump, `legionella.py` would re-stamp its last cycle. | `m4_store_version.*`, `ha_storage_dev.py.txt` | Carry **A4 → R9-F10.1b** (P11, `Fixes #1649`); **EG-B4** |
| **#1741** | The step-start clock is defined twice, and the 20 °C tank-room ambient is a literal at 8 sites. | `m6a_step_starts.*` | Carry **A2 → R9-F1.10** |
| **#1742** | Identity is pinned at 9 constructors, and two platforms keep private config copies. | (the grep in the issue) | **EG-B2** |
| **#1743** | The DHW planner core is 19 methods, 1,851 lines, inside the 5,453-line `HeatPumpOptimizer`, and calls no other optimizer method. | `alt/EG-B5-DESIGN.md` | **EG-B5a**, then **EG-B5** (opted in) |
| **#1744** | The coordinator seams should be re-measured once the hubs stop being written per solve. | `tests/structure.py` | **EG-B7**, conditional |
| **#1747** | `_co_optimize`'s replan omits the DHW block. With mostly negative prices it ships DHW heat while blocked and masks the tank-floor breach: 9.22 kWh at a -2.0 shift, against 0 in the control. | `b8_replan_blocked.*` | **EG-B8**, before EG-B5 |
| **#1748** | R9-F10.3's per-site mutation ratchet keys a site by file, so a move counts every moved unpinned site as added. | the prototype at `8eda51a2`; a skeptic simulation | Carry → **R9-F10.3** |
| **#1745** | Configuration is read per site: 281 `.get(CONF_…)` reads of 149 keys in 20 modules, each with its own default and coercion. | (the enumerator in the issue) | **Deferred to round 10** |

### 2.1 Already scheduled, so not filed

- D1-s2-05 (worker reap under the solve lock) and D1-s2-04 (DEBUG-swallowed cycle failures): F1.5.
- D9-s1-03 (sysid fit on the event loop): F1.7.
- `horizon_hours`: F1.11.
- The #1686 instrument: F10.4.

### 2.2 Leads refuted, not filed

- **The `_utc_step_starts` rounding.** Unreachable, because `dt_hours` is `time_step_minutes / 60` (`optimizer.py:1343`): the two clocks agree on all 18 reachable grids across both DST days. What remains is structural (#1741).
- **`CONF_OPTIMIZATION_INTERVAL` in three coercion styles.** They cannot disagree, because the selector (`config_flow.py:1680`) stores a number. What remains is evidence for #1745.
- **`optimizer.py:2861` naive `datetime.now()`.** Unreachable in production: both solve callers (`coordinator.py:5109`, `:10807`) reach `start_time` positionally.

### 2.3 Rev 2: the RCA-1736 follow-up

**Code shape: other objects that carry an operation's value in place.** The full table is in `alt/SCREEN-1736-SHAPES.md`.

| issue | finding (probe vs null at `3490cb16`) | first release | destination |
|---|---|---|---|
| **#1752** (sev:high) | The boost overlay mutates `_current_action` in place. After a cancel, a `no_prices` or `solve_failed` cycle keeps the pump on at 5.0 kW and displace 20 for 90 min; the null gives off / 0 / -3. | v6.4.0 | **EG-B9**, in the F1 serial slot after F1.5 |
| **#1753** | The price tile and fuse advisor borrow the what-if limiter and cache and restore them unconditionally: a spurious rate limit and a lost user answer. | v4.0.0 | **EG-B9** |
| **#1754** | The "already in flight" guard drops the re-solve an input change asked for, so a manual plan applied mid-solve is not actuated for up to one interval. It also inherits the old plan's releases (O2 carries O1's 41). | v3.2.0 | **EG-B10** |
| **#1755** | The worker-fallback streak is per hass, so one entry's success resets another's #783 cap (8 in-process solves against 3 then capped). The trigger is conditional. | v6.4.2 | **EG-B10** |
| (#1736) | Blast radius the hub RCA did not list, carried into **EG-B1**'s brief:<br>- H1: a concurrent cycle publishes the setback into the card editor's pre-fill (day 16.0 vs 21.0).<br>- H3: two writers of `dhw_hourly_draw_pattern`.<br>- H4: the DHW learner's freeze reads a per-solve copy, frozen 6 of 6 cycles in comfort.<br>- H2: mechanism only, no effect reproduced.<br>- P12's argument blindness. | v2.8.0–v4.0.0 | EG-B1 carry |
| — | C3, what-if side effects on published PV and price-known. Cosmetic and self-healing, so not filed. | — | — |

**Process shape: the register and the RCA record.** Measured in `alt/register/REGISTER-V2.md`, `RCA-INVENTORY.md` and `rca/RCA-BULK-2.md` §3.
- At main, 186 register rows sit in no class; round 8 was never classified.
- The round-9 judge re-minted 20 of its 31 new classes and split mechanisms below the trigger.
- No step folds a round in.
- 40 of 82 RCAs are recorded in neither the register nor an issue, and 9 are lost.
- The 14 round-9 class RCA documents survive only in `handoff/audit-r9-plan` history.
- The rounds 1–7 source (`findings.tsv`) omitted **88 survivors**, including all of round 5's first run, and counted 3 non-survivors. The reconciliation adds and excludes them (`register/missing_rows.tsv`, `excluded.tsv`, `RECON.md`). With them, N-name-sort and I2 each reach 3 in round 5.

**The owed RCAs, conducted in bulk.** Four seats: RCA-BULK-1 to 4.

| issue / carry | RCA verdict | destination |
|---|---|---|
| **#1756** | P7: F1.1's DST tracer catches 1 of 3 historical members. Add a config arm and a straddle arm. | **F10.1c**, new, tests only |
| carry | P10: 2304 model-kernel calls on the loop at main (`topology.py:_advisor_replay`). Barrier: kernel calls outside the worker = 0. | **F1.7** (#1658) |
| carry | P8: the one resolver canonicalises the instance label, not the feed. Carry the feed currency; refuse #1657's metric. | **F1.8** (#1657); owner rules on the displayed currency |
| carry | P4: barrier refused on numbers (owner refusals #1293/#1294); the certificate is the detector. | **F2.4** (#1664) |
| carry | I2: a nightly strace oracle; 3 of 8 members reclassified. | **F10.3** (#1663) |
| carry | N-structure-blind: reachability liveness with a planted-shape self-check. #1545: a check for `qs_py_typed_files`. | **F10.4** |
| carry | #1041 silent-zero: the refusal is overturned, so land `merge_shape_guard` in `agreement.mjs`. The class barrier is tvofi's call. | **F11.4** (#1650) |
| **#1757** | #1721, trigger 2: `graders-head-copy` omits the governance graders, which ran under a different principal. | **F11.7**, new |
| **#1758** | The v6.6.0 options-flow freeze, trigger 1: cause not established. Instrument first. | **F10.7**, new; tvofi runs the host profiler |
| **#1759** | R-register: land register v2, then a deterministic fold with a check. | **EG-R0** (data) then **EG-R1** (fold; owner-gated policy) |
| **#1760** | N-name-sort, 8 instances: families are declared nowhere. Declare them, then one contiguity check. | **F7.4**, new |
| record | #1070: the band landed (#1124); the plan row still says "seat in flight". | the record PR corrects the row |

### 2.4 Rev 3: the architecture score (`alt/archscore/PRE-STUDY.md` at `92b3ecc9`)

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
- **Red team:** 13 of 16 attempts to raise S without improving anything succeeded (pre-study §7).
  - The worst is a 5-line class rename worth +101.
  - Without counters, v1 scores EG-B1's and EG-B3's honest steps exactly as it scores their evasions: `object.__setattr__` hub writes, and an all-`Any` TypedDict.
  - Eight prototyped counters (`archscore/redteam/counters/`) close every game except deleting a feature, which only the behaviour suite catches.
  - The counters change no GOOD holdout verdict, and correct one NEUTRAL (#1563).
  - **So S is a report and a review trigger, never a target**, and every ΔS is measured with the counters.

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

## 3. Ratchet stance

**The owner's direction (2026-09-28):** "The ratchets are not set in stone, and not inherently perfect. The end goal is optimal architecture." It restates the fixplan standing rule, "shape before flatness".

**How this plan applies it:**
- **Fix the instrument where it is wrong.** #1738 corrects the ratchet where it prices decomposition backwards, before any move lands.
- **Name the expected movement.** Every EG item states which budgets it expects to move, and in which direction.
- **Ask for the raise the better shape needs.** Do not avoid the shape to dodge the raise. The gate itself is unchanged: `CLAUDE.md` rule 2 still means the owner's confirmation before the push, and budget-raise-gate at the head. The owner's direction changes the default answer, not the gate.
- **No flatness trades.** No EG item may trade a proven-better shape for flatness.
- **Reinstated on architectural grounds.** The coordinator seams were deferred for architectural reasons (the hub coupling), not budget ones, and are reinstated as EG-B7 behind the change that removes that reason.
- **Rev 3: measure the architecture, not just the budgets.** Each EG brief now states its expected ΔS and the per-metric targets from `alt/archscore/PRE-STUDY.md` §8. The reviewer compares the measured value. A shortfall is information, not a failure. A score rise earned by a red-team move (§7 of the pre-study) is a review finding.

## 4. The schedule

### 4.1 Per PR

Generated from roster rev 3 (`ALT-ROSTER.json`) by `alt/gen_table_rev3.py`:
- The `wave` is the dependency depth over open groups; 1 means startable now.
- **Bold** issues are ones the PR fixes (`Fixes #N`); the rest are `Part of #N`.
- Expected ΔS is the pre-study's §8 figure under the frozen weights. The score does not price EG-L0, EG-B11 or EG-A4.
- 38 groups are open.

| wave | PR | lane | open after-edges | issues (**Fixes**) | owner gate | carry in | what | expected ΔS | stage |
|---|---|---|---|---|---|---|---|---|---|
| 1 | EG-B10 | EG | — | **#1754**, **#1755** | — | — | Solve lifecycle: dropped re-solve, override identity, per-entry fallback streak | — | not-started |
| 1 | EG-L0 | EG | — | **#1167**, **#1168**, **#1170**, **#1171**, **#1173**, **#1174**, **#1175**, **#1176**, **#1177**, **#1178**, **#1179**, **#1180**, **#1181**, **#1182**, **#1183**, **#1184**, **#1185**, **#1187**, **#1188**, **#1189**, **#1190**, **#1191**, **#1193**, **#1196**, **#1197**, **#1198**, **#1199**, **#1200**, **#1201**, **#1204**, #1655 | settings changes are tvofi's hand | — | Re-measure and close the 30 legacy round-5 issues; disposition #1655 | — | not-started |
| 1 | F2.4 | F2 | — | #1644, **#1664** | — | P4 refusal | On/off pump threshold at both seams; multi-start seeds | — | not-started |
| 1 | F7.5 | F7 | — | **#1777** | — | — | The three recorded family splits renamed (en/sv away, sv compressor) | +10.9 | not-started |
| 1 | F9.3 | F9 | — | **#1647** | — | — | P1 declared-domain barrier: stored fields held to their writers' domains | — | not-started |
| 2 | F1.7 | F1 | F2.4 | #1644, #1649, **#1658** | — | P10 barrier | Coordinator readers across lanes: loop CPU, auth, settlement scale | — | not-started |
| 2 | EG-B8 | EG | F2.4 | **#1747** | — | — | DHW block ignored by the co-optimisation replan | — | not-started |
| 3 | F1.8 | F1 | F1.7 | #1644, **#1657** | — | P8 feed currency | Currency and unit (P8) and entry identity | — | not-started |
| 3 | F10.1b | F10 | F1.7 | **#1649**, #1740 | — | A4 #1740 | Aware-default Home Assistant stub clock | — | not-started |
| 4 | F1.9 | F1 | F1.8 | **#1660** | — | — | Persisted future instants: the outage decision and the coordinator regressions | — | not-started |
| 4 | F10.1c | F10 | F10.1b | **#1756** | override-length fix or exemption | — | P7 tracer: config and straddle arms | — | not-started |
| 4 | F10.2 | F10 | F10.1b | **#1653**, **#1656** | stress.py code-owned; budget rows (B1, B2) | — | CPU gate blind spots; per-solve CPU budget | — | not-started |
| 4 | F6.3 | F6 | F1.8 | **#1652** | card_browser.mjs code-owned | — | P9 class barrier in the browser lane | — | not-started |
| 5 | F1.10 | F1 | F1.9, F2.4 | #1645, **#1654**, #1741 | — | A2 #1741 | P3 class barrier: one floor per thermal parameter; comment drift; the fourth on-threshold copy | — | not-started |
| 5 | F10.3 | F10 | F10.2 | **#1646**, **#1663**, #1748 | gate scripts code-owned | #1748; I2 strace | Owned gate scripts: verdict pins, mutation inventory, child-process closures; I1 barrier | — | not-started |
| 5 | F6.4 | F6 | F6.3, F1.8 | **#1687** | — | — | Language-aware setup text; raw-thermometer source for staleness gaps | — | not-started |
| 6 | F1.11 | F1 | F1.10, F6.4 | **#1644**, **#1651** | — | — | Class barriers P2 and P6; horizon_hours and the boost test hook | — | not-started |
| 7 | EG-B2 | EG | F1.11 | #1739, **#1742** | — | — | Surface identity and public accessors | +3.8 | not-started |
| 7 | F10.4 | F10 | F10.3, F1.11 | **#1645**, #1650, **#1661**, **#1686**, #1738 | B5 raise if honest re-record raises; #1738 arm (c) re-definition | A1 #1738; N-structure-blind; #1545; metric review (retire/merge/modify, 11 defects) | Structural ratchet truth: dead members and uncounted helpers; I5 barrier | +5.6 | not-started |
| 8 | EG-A1 | EG | F10.4 | #1774, #1738 | code-owned merge review | — | Architecture score, report-only, with its calibration self-check | — | not-started |
| 8 | EG-B3 | EG | F10.4, EG-B2 | **#1737** | — | — | Typed payload contract | +50.9 | not-started |
| 8 | EG-B5a | EG | F2.4, F10.4 | #1743 | downward re-record | — | One builder for the duplicated solve closures | — | not-started |
| 8 | F10.5 | F10 | F10.4 | — | new writer identity (0011); code-owned | — | Nightly mutation-kill ledger writer | — | not-started |
| 8 | F11.4 | F11 | F10.4 | **#1650** | audit-find.js code-owned | merge_shape_guard (#1041) | Class roster readers agree (I4 barrier); owed driver fixes | — | not-started |
| 9 | EG-B4 | EG | F10.1b, F10.4, EG-B3 | **#1740** | — | — | Store version seam | — | not-started |
| 9 | EG-B5 | EG | EG-B5a, EG-B8, F1.10, F10.4 | **#1743**, #1748 | opted in; classes_over_300 unless re-defined | — | DHW planner extraction (opted in) | ≈0 (limit) | not-started |
| 9 | EG-R1 | EG | F11.4 | **#1759** | policy clauses; audit-verify.js code-owned | — | Deterministic register fold and its check | — | not-started |
| 9 | F10.6 | F10 | F10.5 | — | mutation_table.py code-owned | — | Comparison-bound mutation operator | — | not-started |
| 9 | F11.5 | F11 | F11.4 | — | policy text (A1-A9) | — | Round-9 RCA policy text | — | not-started |
| 10 | EG-A2 | EG | EG-A1, EG-B3, EG-B5 | **#1775** | — | — | One copy per formula and helper (P2/P3 clones; dup_pairs_v1 121 → ≤40) | +14.1 | not-started |
| 10 | EG-B1 | EG | F10.4, F2.4, F10.6, F11.5, EG-B4, EG-B5, EG-B10 | **#1736** | any raise asked before push | H1-H4, P12 (#1736) | Per-solve immutable inputs | +29.5 | not-started |
| 10 | F10.7 | F10 | F10.6 | #1758 | host Profiler run (tvofi) | — | nightly-ha loop-stall heartbeat (v6.6.0 freeze diagnosis) | — | not-started |
| 10 | F11.7 | F11 | F11.5 | **#1757** | tests.yml code-owned | — | graders-head-copy governance arm under the Actions token | — | not-started |
| 11 | EG-A3 | EG | EG-B1, EG-B5 | **#1776** | — | — | Parameter objects for solver and planner signatures | +0.6 | not-started |
| 11 | EG-B6 | EG | EG-B1 | **#1739** | — | — | Collaborator interfaces | +4.2 | not-started |
| 12 | EG-B11 | EG | EG-B1, EG-A3 | **#1745** | — | — | Typed entry configuration, read once per entry (#1745) | — | not-started |
| 12 | EG-B7 | EG | EG-B1, EG-B6 | **#1744** | classes_over_300 unless re-defined | — | Coordinator seams, measured go/no-go | +5.2 | not-started |
| 13 | EG-A4 | EG | EG-A1, EG-B7, EG-A2, EG-A3, EG-B11 | **#1774** | ruleset required context is tvofi's hand | — | Architecture score becomes a required check | — | not-started |

### 4.2 Threads

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

### 4.5 Stamps and fixtures

Unchanged from rev 1. The remaining fixture movers are F1.7, F1.10 and F2.4. The EG refactors claim nothing. EG-B9, EG-B10 and F7.4 move no golden: goldens never boost, never swap an override mid-solve, and do not publish names.

### 4.6 Every open issue and the group that closes it

Generated from roster rev 3.1 and GitHub's open issues (tracking #201 excluded) by `alt/gen_coverage_rev31.py`.
- Every open issue has a closing group.
- #1655 is dispositioned by EG-L0, which closes it with R9-F4.2's record or schedules the remainder into its owning group.

| issue | title | closed by | also part of |
|---|---|---|---|
| #1777 | [R9-F7-FAMILY-SPLITS] Three declared entity families still split under the name sort | F7.5 | — |
| #1776 | [R9-EG-PARAM-OBJECTS] 28 functions take more than ten parameters | EG-A3 | — |
| #1775 | [R9-EG-ONE-COPY] 121 AST-identical clone pairs, incl. scalar and batch thermal physics | EG-A2 | — |
| #1774 | [R9-EG-ARCH-SCORE] Architecture score: report-only, then a required check | EG-A4 | EG-A1 |
| #1759 | [R9-REGISTER-FOLD] Register never received rounds 8-9; nothing folds a round in | EG-R1 | — |
| #1758 | [R9-FREEZE-INSTRUMENT] v6.6.0 options-flow freeze never diagnosed: loop-stall heartbeat | F10.7 | — |
| #1757 | [R9-GOV-HEADCOPY-PRINCIPAL] graders-head-copy omits the governance graders | F11.7 | — |
| #1756 | [R9-P7-TRACER-BLIND] DST tracer catches 1 of P7's 3 historical members | F10.1c | — |
| #1755 | [R9-EG-FALLBACK-STREAK] Worker-fallback streak shared across config entries | EG-B10 | — |
| #1754 | [R9-EG-INFLIGHT-REFRESH] Refresh requested while a solve is in flight is dropped | EG-B10 | — |
| #1748 | [R9-EG-RATCHET-MOVE-BLIND] Per-site mutation ratchet counts a moved site as new | F10.3 | EG-B5 |
| #1747 | [R9-EG-DHW-BLOCK-REPLAN] Co-optimisation replan ignores a DHW mode block | EG-B8 | — |
| #1745 | [R9-EG-ENTRY-CONFIG] Configuration is a raw dict read per site | EG-B11 | — |
| #1744 | [R9-EG-COORDINATOR-SEAMS] Re-measure and extract the coordinator's dhw and views seams | EG-B7 | — |
| #1743 | [R9-EG-DHW-PLANNER] Extract the DHW planner core from HeatPumpOptimizer | EG-B5 | EG-B5a |
| #1742 | [R9-EG-SURFACE-IDENTITY] Entity identity pinned at 9 constructors | EG-B2 | — |
| #1741 | [R9-EG-PLANT-FACT-COPIES] Step-start clock twice; 20 C tank-room ambient at 8 sites | F1.10 | — |
| #1740 | [R9-EG-STORE-VERSION] No store can change its version | EG-B4 | F10.1b |
| #1739 | [R9-EG-COLLABORATOR-INTERFACES] Collaborators reach into coordinator internals | EG-B6 | EG-B2 |
| #1738 | [R9-EG-RATCHET-DECOMPOSITION] Structural ratchet misprices decomposition | F10.4 | EG-A1 |
| #1737 | [R9-EG-TYPED-PAYLOAD] Coordinator payload has no typed contract | EG-B3 | — |
| #1736 | [R9-EG-SOLVE-INPUTS] Each solve writes its inputs into the live hub objects | EG-B1 | — |
| #1687 | [R9-TEXT-PRODUCER-TAKES-NO-LANGUAGE-PARAMETER] | F6.4 | — |
| #1686 | [R9-STRUCTURE-METRIC-BLIND-TO-SHAPE] | F10.4 | — |
| #1664 | [R9-P4] Optimizer seed set or stop tolerance does not bracket the optimum | F2.4 | — |
| #1663 | [R9-I2] Measured closure diverges from the real dependency graph | F10.3 | — |
| #1661 | [R9-PRODUCTION-MEMBER-NO-CALLER] | F10.4 | — |
| #1660 | [R9-PERSISTED-FUTURE-INSTANT-TRUSTED-WITHOUT-BOUND] | F1.9 | — |
| #1658 | [R9-CPU-WORK-INLINE-ON-THE-EVENT-LOOP] | F1.7 | — |
| #1657 | [R9-P8] Currency or unit resolved by divergent precedence | F1.8 | — |
| #1656 | [R9-CPU-GATE-BLIND] | F10.2 | — |
| #1655 | [R9-P5] Sysid/adoption gate keyed on a quantity other than the bias it gates | — | EG-L0 |
| #1654 | [R9-P3] Capacity floor or divisor applied inconsistently | F1.10 | — |
| #1653 | [R9-AVOIDABLE-INTERPRETER-BOUND-RECOMPUTATION] | F10.2 | — |
| #1652 | [R9-P9] Card UI: clipping ancestor, colour token, hit target | F6.3 | — |
| #1651 | [R9-P6] Consumer reads a key no producer writes | F1.11 | — |
| #1650 | [R9-I4] Two parsers or definitions of one concept disagree | F11.4 | F10.4 |
| #1649 | [R9-P11] The only oracle for an external counterpart is a self-written double | F10.1b | F1.7 |
| #1647 | [R9-P1] Non-finite or malformed value crosses a persisted-store boundary | F9.3 | — |
| #1646 | [R9-I1] Mutation kill miscounted, or a guard deletable with the gate green | F10.3 | — |
| #1645 | [R9-I5] Docs, comments or checklist drift stale | F10.4 | F1.10 |
| #1644 | [R9-P2] One fact decided twice by divergent predicates | F1.11 | F1.7, F1.8, F2.4 |
| #1204 | [D8-01-followup] Sensor-Gap Advisor probe terms have no upstream data source | EG-L0 | — |
| #1201 | [D13-04] Carried GOV set understates governance cost by 7% | EG-L0 | — |
| #1200 | [D13-03] Verdict histogram emits one key | EG-L0 | — |
| #1199 | [D13-02] 16 of 30 blocked verdicts outside the wave grammar | EG-L0 | — |
| #1198 | [D13-01] Friction histogram's top row is PR trailers | EG-L0 | — |
| #1197 | [D12-01] No-DHW plant still publishes dhw attributes | EG-L0 | — |
| #1196 | [D11-06] dismiss_stale_reviews_on_push=false contradicts 0008 | EG-L0 | — |
| #1193 | [D11-03] Reviewer != author not enforced | EG-L0 | — |
| #1191 | [D11-01] hpo-stamp deploy key bypass is 'always' | EG-L0 | — |
| #1190 | [D9-02] _apply_dhw_min_run re-simulates per weak slot | EG-L0 | — |
| #1189 | [D9-01] Stress gate work meter misses single-scenario cost regressions | EG-L0 | — |
| #1188 | [D8-03] 'Euro' advisor publishes the instance currency | EG-L0 | — |
| #1187 | [D8-02] Entity-id sort splits families into 13 runs | EG-L0 | — |
| #1185 | [D7-01] Mutation gate default driver list omits the module's own test | EG-L0 | — |
| #1184 | [D5-03] Two 'How the pieces fit' diagrams drifted | EG-L0 | — |
| #1183 | [D5-02] __init__ '40 modules' note is stale | EG-L0 | — |
| #1182 | [D5-01] Platform docstrings undercount entity rosters | EG-L0 | — |
| #1181 | [D4-03] Card sv missing stats.delta_detail_same | EG-L0 | — |
| #1180 | [D4-02] Picker .sp-filter input under the floor | EG-L0 | — |
| #1179 | [D4-01] Setup click-to-assign rows under the 24px floor | EG-L0 | — |
| #1178 | [D3-08] deployment_shape closure is 74/74 | EG-L0 | — |
| #1177 | [D3-07] Equivalent mutants not separated | EG-L0 | — |
| #1176 | [D3-06] Sysid plausible-bounds refusal untested | EG-L0 | — |
| #1175 | [D3-05] StartCounter early return untested | EG-L0 | — |
| #1174 | [D3-04] cheaper_hour_count non-positive-COP guard untested | EG-L0 | — |
| #1173 | [D3-03] flow_setpoint emitter-UA floor untested | EG-L0 | — |
| #1171 | [D3-01] Mutation instrument's driver set is not the gate's | EG-L0 | — |
| #1170 | [D2-01] Capacity term's soft top-k under-charges the peak | EG-L0 | — |
| #1168 | [D0-02] Polish runs on only one candidate | EG-L0 | — |
| #1167 | [D0-01] Solver polish <2% discarded | EG-L0 | — |

## 5. Deferred and dropped

**Round 10, pre-study only:**
- **The features.py split.** Measure first:
  - actual conflicts, with a replay in the style of `tools/merge/ledger_merge.py --replay`;
  - the dependency graph of the sections on the shared header;
  - the cost of re-attributing the 352 `killed_by` pins;
  - `run.sh` wiring and the `tests/README.md` policy edit.
  Candidate shape: about ten files, grouped by lane-owned module, not one per class.
- **#1745, typed configuration:** moved into round 9 as **EG-B11** (rev 3.1).
- **EG-S2.** Only after the owner rules on unknown versus unavailable.
- **The 121 `getattr(self, "_ctx", self)` sites** beside the `_hub` facade (`coordinator.py:1382`). Measure their effect on the cut metrics (#510, `docs/HANDOVER.md:316`) after #1738 has landed.

**Dropped:** EG-0b, EG-X1, and the 70-site clock migration.

## 6. Adopting rev 3.1

tvofi's decisions are given (§7), so nothing waits for approval. The orchestrator:

1. **The roster.** Replaces `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` with `ALT-ROSTER.json`.
   - If the live file has moved since `c5af8f3a`, run `alt/build_roster_rev3.py <live> <out>` on it, then replace the placeholder with the pre-study commit (`92b3ecc9`). Its sections 1–6 apply:
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

## 7. Decisions, all given 2026-09-29, and what remains for tvofi's hands

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
