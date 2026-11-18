# D4 — UI/UX, round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9).
Export: `~/audit-r6-baseline` (no `.git`). No earlier audit
record was read and no `gh`/GitHub access was used, so `exposure` is empty.
Machine: 8-core Apple M1, 8 GB RAM, darwin arm64, `load1 = 4.71` at the final
run (the box is shared with the other round-6 seats). Every number below is a
count, a pixel or a ratio taken from real layout, so contention cannot move it.

## Method

Two harnesses, each runnable by the one command in its header.

**`card_qa.mjs`** — the card in real Chromium (Playwright 1.49.0, the
pre-installed `chromium-1148`). It builds the card the way
`tests/card_browser.mjs` does, from
`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` itself,
and drives **22 states** across **3 viewports** (375x812, 768x1024, 1280x800) x
**2 themes** (Home Assistant light and dark token sets) x **2 pointers**
(`(pointer: coarse)` off and on, via a `matchMedia` arm) x **2 languages**
(`en`, `sv-SE`) = **528 cells**. Every measurement is
`getBoundingClientRect`/`getComputedStyle` on the card's own DOM after a real
render; nothing is read from the markup. Modes: `--selfcheck`, `--motion`,
`--focus`, `--hover`, `--shots`, `--only`, `--perturb`.

**`flow_rubric.py`** — the config flow scored from `_OPTION_PAGES`,
`_OPTION_FIELDS`, `strings.json` and `translations/sv.json`, through the same
stub `tests/entities.py`'s options loops use.

**Limit to state: there is no Home Assistant frontend in this export.** The
config-flow scores below are read from the schemas and the strings the flow
hands the frontend, not from pixels; `ha-form` and `section()` render as opaque
elements here. No rendering claim is made about the options pages.

Both harnesses are instrument-controlled. `card_qa.mjs --selfcheck` plants a
case for each counter and asserts it fires — `overflow=1 overlap=1 under=1
contrast=1` — and exits non-zero if any is dead. The motion arm has the
reduced-motion arm as its control, the hover probe reports
`hover_ctrl_landed`, and the rubric's perturbation drops one
`data_description` from `strings.json`.

## Finding

### D4-01 — the score pill is a control that never joined the card's own coarse-pointer target floor

*Severity:* **medium** (bounded cost: a touch user can still open the breakdown
by tapping, the miss rate is just higher than for every other control on the
surface). *Stop rule:* **bug**.

**Claim.** On the plan card the headline **optimization-score pill** is a
control — `role="button"`, `tabindex="0"`, an `aria-label`, and a click handler
that opens the score breakdown (`heatpump-optimizer-card.js` 10971-10979) — but
under a coarse pointer it renders **25 px** tall at 375x812 and **39 px** tall
at 768x1024 and 1280x800, below the **44 px** floor the card applies to every
other control on the same surface. It is the only control in the 528-cell
matrix that lands under the floor.

**Metric definition (one line).** `min(width, height)` in CSS px of each element
the card marks as a control, against the card's own floor for the pointer in
force (`TARGET_MIN_PX = 24` fine, `TARGET_MIN_PX_COARSE = 44` coarse, lines
1296-1297, selected by `_coarsePointer()`); counted as cells with at least one
under-floor control.

**Instrumented symbols.** `heatpump-optimizer-card.js`: `_render()` — its
emitted `[data-stat="score"]` element and the R5-D4-02 rule at 3080-3083 — and
`_coarsePointer()` (1310) with the `htmlTargetFloor` selector list it picks the
pixel value for (2969-2989).

**Evidence.**

```
$ NODE_PATH=<tmp>/node_modules PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers \
    HPO_PLANDATA=<plan>.json node tools/audit/round6/D4/card_qa.mjs --json /tmp/d4r6/final.json
cells=528
RESULT overflow_cells=0 cells
RESULT overlap_cells=0 cells
RESULT under_floor_cells=12 cells
RESULT contrast_cells=0 cells
RESULT hscroll_cells=0 cells
RESULT error_cells=0 cells
RESULT total_overflow=0 total_overlap=0 total_under=12 total_contrast=0

== under floor ==
  12x span.hl-stat hl-score @ score_open/375x812/light/coarse/en
== smallest targets ==
  25px span.hl-stat hl-score "Optimization score 82/10" @ score_open/375x812/light/coarse/en
  25px span.hl-stat hl-score "Optimeringsbetyg 82/100" @ score_open/375x812/dark/coarse/sv
  39px span.hl-stat hl-score ... @ score_open/768x1024/{light,dark}/coarse/{en,sv}
  39px span.hl-stat hl-score ... @ score_open/1280x800/{light,dark}/coarse/{en,sv}
```

The 12 cells are `score_open` at the 3 viewports x light/dark x en/sv, all
**coarse** (`--json /tmp/d4r6/final.json`; the element in every one is
`span.hl-stat.hl-score`, `role=button`, `tabindex=0`, `158.02 x 25` at 375x812
and `158.02 x 39` at the two wider viewports). Fine-pointer cells are **0**
under-floor, because the R5-D4-02 padding rule (`padding: 5px 0; margin: -5px 0`,
line 3080) adds exactly 10 px and clears the 24 px fine floor at 25 px. The
coarse floor is 44 px and no rule in the card knows about it for this element.

**Why this is not just prose about the code.** The `htmlTargetFloor` block
(2969-2989) is one template whose selector list *is* the register of controls on
the HTML surface; its own comment says "A control added to this surface joins
the selector list below; the comments on the last two groups say why each
joined". `.expand, .close, .viewctl button, .chip, .dlg-tab, .adv-row,
.sp-filter, .sp-select, .slot-menu button, .away-strip ...` are all in it.
`.hl-stat`/`.hl-score` is not — and the pill is a keyboard tab stop (see the
focus non-finding), so it is a control on that surface that did not join.

**Perturbation** (the judge runs it; the number must move down):

```
$ ... node tools/audit/round6/D4/card_qa.mjs --only score_open \
    --perturb '.hl-stat.hl-score{min-height:44px;min-width:44px;box-sizing:border-box}'
cells=24
RESULT under_floor_cells=0 cells          # was 12
RESULT overflow_cells=0 overlap_cells=0 contrast_cells=0 hscroll_cells=0 error_cells=0
```

`--perturb` appends exactly the declarations the floor template applies to the
other controls to the card's own shadow root *after* the state has rendered (so
a re-render cannot wipe it). The count moves **12 -> 0** and nothing else in the
matrix moves.

**Null control.** The same cells read at `pointer=fine` in the full matrix:
`under_floor_cells=0`. The effect is coarse-pointer-only and vanishes where the
floor is 24 px, which is what the mechanism predicts.

**Leave-one-out.** The 12 cells carry the values `{25 px x 4, 39 px x 8}` —
range 25-39 px against a 44 px floor, so no cell is near it (the best is 19 px
short). Dropping the single most favourable cell (one 25 px cell) leaves
**11 cells** under the floor and the worst still 39 px.

**Files.** `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
— 3080-3083 the padding rule, 2969-2989 the selector list, 10971-10979 the
control wiring.

**Proposed fix scope.** One line: add `.hl-stat.hl-score` to the
`htmlTargetFloor` selector list, with a comment in the group-comment style that
block already uses. No new rule, no new token. The perturbation above *is* that
change.

**Reproduction.**
1. `npm i --prefix /tmp/d4r6/pw playwright@1.49.0`
2. `NODE_PATH=/tmp/d4r6/pw/node_modules PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers HPO_PLANDATA=<plan>.json node tools/audit/round6/D4/card_qa.mjs --only score_open`
3. The same command with the `--perturb` argument above.

## Non-findings (each with the command and the number that showed it)

All from `card_qa.mjs` unless stated.

| claim | command | value |
|---|---|---|
| No text overflows its box, in any state, viewport, theme, language or pointer | `--json` | `overflow_cells=0/528`, `total_overflow=0` |
| No two text boxes overlap | `--json` | `overlap_cells=0/528`, `total_overlap=0` |
| No text/background pair fails WCAG AA, in the card's light or the Home Assistant dark token set | `--json` | `contrast_cells=0/528` |
| No state scrolls horizontally, at 375 px or anywhere else | `--json` | `hscroll_cells=0/528` |
| No console error and no uncaught page error in any of the 528 cells, including the empty and error states (`no_plan`, `plan_unavailable`, `plan_missing`) | `--json` | `error_cells=0/528` |
| Every keyboard focus stop shows an indicator under a real `Tab` keypress (`:focus-visible`), including the stroke-ring SVG targets `rect.setup-hit` and `rect.lane` | `--focus --only plan,score_open,expanded,picker_open,setup,whatif,away,wood_alert` | `focus_stops=603 focus_stops_without_indicator=0` (no `NO-RING` line in the per-control roll-up) |
| The reduced-motion preference removes the card's only animation | `--motion` | `arm=no-preference: cells_with_motion=18 elements=24 (div.viewctl)` -> `arm=reduce: cells_with_motion=0 elements=0` |
| Hovering the chart, a legend chip, the expand control, a zoom control or a setup target moves no layout | `--hover --only plan,expanded,setup` | `hover_shift_cells=0/72`, `hover_shift_worst=0px`, every selector `max=0px`; probe control `hover_ctrl_landed=24/60`, `hover_ctrl_target_style_changed=12/60` |
| No ghost tab stops: nothing focusable that is not painted | `--json` | `ghostStops` empty in all 528 cells |
| Nothing spills out of the card surface horizontally | `--json` | `card-surface spill > 1px` empty in all 528 cells |
| The setup picker's fields over the setup page are an opaque overlay, not text read through text | `--json` (occlusion roll-up) | 5 pairs, all `picker_open`, all `sp-*` over `setup-value`/`setup-hint`/`layout-edit-toggle`; each offending element's composited ancestor background reaches alpha 1.0 before the card surface, so the modal covers rather than blends |
| The counter harness is not a dead probe | `--selfcheck` | `selfcheck_control=fires overflow=1 overlap=1 under=1 contrast=1` |
| **Flow:** 23 options pages (8 top menu, 15 advanced) and 197 registry rows, every row landing on a leaf page | `flow_rubric.py` | `pages=23 top_menu=8 advanced_menu=15`, `fields=197`, `orphan_rows=0 []` |
| **Flow:** every labelled field on every options page has help text in **both** `strings.json` and `translations/sv.json` | `flow_rubric.py` | `missing_help_text_en=0 missing_help_text_sv=0` |
| **Flow:** that help-coverage number moves when a `data` key loses its `data_description`, so the 0 above is a fact and not a dead probe | `flow_rubric.py` | `perturbation_missing_help heat_curve 0 -> 1` |
| **Flow:** 10 of 23 pages group their fields with `section()`; the widest page is `building` at 23 fields; 5 pages exceed 12 fields | `flow_rubric.py` | `pages_with_sections=10`, `widest_page=building fields=23`, `pages_over_12_fields=5 ['comfort','hot_water','entities','building','hot_water_tank']` |
| **Flow:** a first-time user reaches a first plan through the quick path in 3 screens, or the full questionnaire in 10 | `flow_rubric.py` | `install_quick_path_screens=3 ['user','user_sensors','quick_setup']`, `install_full_path_screens=10` |
| **Flow:** 4 groups are split in the registry table, so the rendered section order on those pages is not the table order | `flow_rubric.py` | `split_groups=4 {'tuning':['wear','risk'],'entities':['indoor'],'hot_water_tank':['tank'],'learning_features':['weather']}` |

Two notes on the config-flow rows:

- **The coverage claims are already gated by the suite, so the config-flow half
  of this dimension is verified rather than newly found.** `tests/entities.py`
  line 611 asserts the README's options-page count matches `_OPTION_PAGES`;
  ~line 6859 asserts every labelled flow field has a `data_description`;
  `tests/config_flow_steps.py` ~line 6092 asserts the ten wide options pages
  group with `section()`. A "finding" here would duplicate a live check.
- **`split_groups=4` is a rubric observation, not a finding.** `_page_schema()`
  merges a split group into the `section()` of its *first* row and fields inside
  a section keep table order, so on those four pages the on-screen section order
  differs from the table order. No measurement here shows a user is misled by
  it, and it needs the HA frontend to be called user-visible, so it is recorded
  and not filed.

## Hover detail

`--hover --only plan,expanded,setup` (72 cells, fine pointer only, both themes
and both languages): `hover_shift_cells=0/72`, `hover_shift_worst=0px`, and each
of the five selectors reports `max=0px`. The probe is live —
`hover_ctrl_landed=24/60` (`.viewctl` opacity rose on hover; that control only
applies to `.chartwrap`) and `hover_ctrl_target_style_changed=12/60`. A previous
narrower run (`--only plan --hover`, 12 cells) reproduced both: `maxshift=0` for
`.chartwrap`, `.chip`, `.expand` and `.vc-out`, `viewctl_landed=12/12` for
`.chartwrap` and `.vc-out`, `target_style_changed=12/12` for `.expand`, and
`0/12` for `.chip`.

**Two observations, neither filed.** (a) **`.chip` has no hover rule.** The card
has `.chip:focus-visible` (line 3024) and `.chip { cursor: pointer }` (3115) but
**no `.chip:hover`**, so a legend chip gives no hover feedback. `cursor: pointer`
is the standard affordance, the chip has a visible focus ring and an `.off`
state, and zero pixels of layout move, so no user action is blocked — a polish
item. (b) **The score pill, which is the D4-01 control, is not styled as one:**
it paints as plain headline text (no chip, no underline, no cursor in the
screenshot at `shots/score_open_375x812_light_coarse.png`); the larger hit box
the fix adds is invisible, so the fix changes hit area, not affordance. Adding a
visual affordance would be a design decision for the owner, not a defect I can
measure.

## What I could not finish

- **No Home Assistant frontend in the export**, so the config-flow rows above
  are schema-and-strings scores. The real rendering of `section()` grouping,
  `ha-form` widget choice and error placement was not measured and is not
  claimed. `tests/card_browser.mjs` has no config-flow lane.
- **`sv` strings were checked for presence, not for quality.** Every key exists;
  whether each translation reads naturally to a Swedish user is not measured.
- **The coarse-pointer arm is a `matchMedia` stub** — exactly the predicate
  `_coarsePointer()` reads — but it does not emulate a touch device's
  hit-testing or scroll snapping. The 44 px consequence is a layout fact, not a
  measured tap-miss rate.

## Harnesses and artefacts

- `tools/audit/round6/D4/card_qa.mjs` — 22 states x 3 viewports x 2 themes x
  2 pointers x 2 languages; `--selfcheck`, `--motion`, `--focus`, `--hover`,
  `--shots`, `--only`, `--perturb`.
- `tools/audit/round6/D4/flow_rubric.py` — the config-flow rubric.
- `tools/audit/round6/D4/shots/` — 138 screenshots: every state at each viewport
  in both themes (fine pointer, `en`), plus `score_open` at every tier including
  the 12 coarse-pointer cells the finding names.

## Exposure

None. Nothing under `docs/` was read, no earlier audit round was consulted, and
no GitHub record was opened.
