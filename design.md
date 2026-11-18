# Design: R11-SEAM-card (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75 (`PLAN.md`; move: adr
none, `card_clone_copies` named at 0.0). Code read at `origin/main`
bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; no `after` edge, so no predecessor
head. `$F` is `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`;
`:n` is its line at that SHA. No production code on this ref.

## 1. What each finding reads at the base (finder's harness, run here)

| finding | harness (`dev/audit/rounds/round11/` on `plan/r11`), RESULT | finder | base | live |
|---|---|---|---|---|
| D4-s1-01 | `D4/s1/m1_pipes.mjs` `pipe_hit_under_floor` | 576 | 576 (max 5.75 px; null port median 30.5 px) | yes |
| D4-s1-03 | `D4/s1/m1_browser.mjs` STATES=score_open `strict_small` | 72 | 72 | yes |
| D4-s3-01 | `D4/s3/m3_look.mjs --err=ha` `english_error_lines` | 24 | 24 (null `--err=plain` 0) | yes |
| D4-s3-02 | `m3_look.mjs`, six headline states, `tile_row_misaligned` | 12 | 12 (max 14 px) | yes |
| D4-s3-03 | `m3_look.mjs`, six states, `below_floor_cells` | 78 | 78 (9 elements) | yes |
| D4-s3-04 | `m3_look.mjs`, ten states, `role_colour_split` | 5 | 5 | yes |
| D4-s3-05 | `m3_look.mjs`, ten states, `offscale_font_sizes` | 14 | 14 (`offscale_spacing` 41) | yes |
| D9-s2-01 | `D9/s2/card_history_retained.mjs --days 30` | 1448/day | 1448/day (memo 192/day, 60 chunks) | yes |
| D6-s4-01 | `D6/s4/card_placeholders.mjs` `unresolved_sv` | 1 | **0** | **no** |

D6-s4-01: `STRINGS.sv["status.stale_title"]` reads `{minutes}` at the base and
at the finder's baseline 92d38ecb (`git log -G minuter` finds no commit); the
judge re-ran it on a planted copy (`JUDGE.json`). A **barrier, not a fix** (§3 F).

## 2. Owning seam

`card` (`COMPONENTS.md`): `$F` alone; `tests/seam_map.json` maps Python and has
no card entry. One owner per concern inside it: `cardStyleBlock` (:5062) for
A-C; `setupSvgHtml` (:4286) for the pipe markup; `LayoutEditor` (:14452) for
the removal gesture; `HistorySource` (:7127) for retention. The `exceptions`
of `custom_components/heatpump_optimizer/translations/en.json` and its sv/de
siblings (next edited by `R11-SEAM-product-text`) are read through
`hass.localize`, never edited. No Python file changes. No concern needs two owners.

## 3. Shape

**A. Targets and rows (D4-s1-01, D4-s1-03, D4-s3-02).**
- `setupSvgHtml`'s `line()` (:4618), while `editing` and `edge` is set, emits
  after the visible path `<path class="layout-pipe-hit" data-hit-edge="<edge>"
  d="<same d>" stroke-width="<w>" aria-hidden="true" />`, `w = unitsPerPx > 0 ?
  max(3.5, _targetMinPx() * unitsPerPx) : 3.5`; `unitsPerPx` (:4760) moves above
  `line()`. CSS as `.layout-port-hit` (:5884): `fill: none; stroke: #fff;
  stroke-opacity: 0.001; pointer-events: stroke; cursor: pointer`. The visible
  pipe, its `data-edge` and its keyboard stop are unchanged. `LayoutEditor`'s
  removal reads `data.edge || data.hitEdge` (:14923, :14944).
- `.hl-fold-head` (:5329): `min-height: ${Math.max(32, targetFloorPx)}px`, the
  `ha-card .chip` pattern (:5138).
- `.hl-stats` (:5291) and `.tiles` (:5214): each cell a row subgrid
  (`grid-template-rows: subgrid`, spanning label, value and, for `.hl-stat`,
  caveat), so values in one row share a line however their labels wrap.

**B. Type and spacing on the scales (D4-s3-03, D4-s3-05).** Every `font-size`
in `cardStyleBlock` reads a `--hpo-text-*` token; padding, margin and gap read
`--hpo-space-*`. One step is added, `--hpo-text-base: 14px`: the body size the
dialog's phone floor already fixes (H1, :6276), carried today by 37 element
classes (what-if, advisor, health, savings, picker, layout bar). Every other
measured size goes to the nearest step, anything under 12 px to `xs`:

| measured px (elements) | token |
|---|---|
| 9.28, 10.92, 10.95, 11.2, 11.9, 12.16, 12.48 (tooltip at phone, tt-shared, sp-note, layout verdict, legend note, sb-text) | `--hpo-text-xs` 12 |
| 12.6, 12.88, 13.12 (wi-group-title, wi-add, tooltip, hl-caveat, sb-*) | `--hpo-text-sm` 13 |
| 14 (body) | `--hpo-text-base` 14 |
| 15.4, 16, 16.66 (wi-remove, dialog chips and layout bar, dlg-tab) | `--hpo-text-md` 15 |
| 17.5, 19.6 (delta, title) | `--hpo-text-lg` 18 |

Spacing snaps to the nearest of 4/8/12/16/24 px (em spacings become px tokens);
a value kept off the scale is listed with its reason in the PR body. The phone
tooltip (`dialog.expanded .tooltip`, :6279) stays inside its chart by
`max-width` and wrapping. The four inline `style=` (:6889, :15824, :15904,
:15908) become classes. One rule family per commit (tooltip; picker; layout;
headline and tiles; what-if; dialog and tabs; legend; title), each re-measured.

**C. One colour per status role (D4-s3-04).**
- Text: error `var(--hpo-crit)`, success `var(--hpo-ok)`, warning
  `var(--hpo-warn)` at :6178, :6217, :6264, :6267; `.setup-pipe.invalid` (:5876)
  leaves `--error-color` for `--hpo-crit`.
- Fills under white text (:5935, :6231): new `CARD_TOKENS["--hpo-crit-fill"]`
  `{light: "#b3261e", dark: "#b3261e"}`, 6.54:1 in both themes.
- `.wood-alert`, `.space-blocked-alert`: stripe `var(--hpo-warn)`, background
  `var(--hpo-warn-bg)`, text `var(--hpo-ink)`, the token-pair rule at :5000.
- The six status `*_READABLE` constants (:41-46) and `cardStyleBlock`'s three
  colour locals (:5063-5065) go; `ACCENT_READABLE` is the accent role, kept.

**D. Translated failure lines (D4-s3-01).** Top-level
`serviceFailureText(hass, err)`: when `err.translation_domain` and
`err.translation_key` are set and `hass.localize` gives a non-empty
`component.<domain>.exceptions.<key>.message` (placeholders
`err.translation_placeholders`), that; else `err.message`; else `String(err)`.
`HeatpumpOptimizerCard`'s `set hass` (:15278) calls
`hass.loadBackendTranslation("exceptions", "heatpump_optimizer")` once per
language when the method exists (the editor, :16253, calls no service). The
ten sites take it: :11038, :11082, :11091, :11641, :11660, :13332, :13437,
:13937, :14173, :15098.

**E. Bounded history (D9-s2-01).** `HistorySource.prune(now)` at the top of
`ensure()`. Cut `c = floor((now - HISTORY_SPAN_MS) / HISTORY_CHUNK_MS)`: delete
`chunks` and `covered` keys below `c`; drop `log[field]` and `actionLog` rows
before `c * HISTORY_CHUNK_MS`, keeping each series' last row before the cut (a
sample and a mode hold forward); rebuild `seen` from the kept rows; bump
`version` only when a row went. `overlays()` iterates `covered`, so `memo`
follows.

```
before: pan -> ensure -> fetchChunk -> absorb (append; seen.add) -> overlays(every chunk ever)   +1448 rows/day
after:  pan -> ensure -> prune(now) -> fetchChunk -> absorb -> overlays(chunks within 48 h)     flat
```

**F. D6-s4-01.** No production edit. The `tests/card.mjs` placeholder-parity arm
(R10-I18N-DE) is the check the finder names as refusing `{minuter}`; the fixer
plants it, records the arm red, and adds no check.

**Invariants kept:** no payload, entity, service or `STRINGS` key changes; the
mouse-arm geometry of pipes, ports and folds is unchanged; each chunk inside
48 h is still fetched once per card life; every text run stays AA.

## 4. Alternatives (lost on the code)

- Pipe stroke widened to the floor: paints a 44 px band over the boxes it
  joins. `.slot-hit`, `.layout-port-hit` and `setup-chip-hit` are hit twins.
- `.hl-fold-head` into `htmlTargetFloor` (:5103): that rule is emitted later at
  equal specificity, so it takes the header from 32 to 24 px under a mouse.
- Labels `nowrap` (the finder's perturbation): truncates German labels; values
  pushed to the cell end: misaligned when only one cell has a caveat.
- Body text to `--hpo-text-sm` 13 or `md` 15 instead of a 14 px step: moves 37
  element classes off the 14 px phone floor H1 set, or grows every table and
  button.
- Error fill from `--hpo-crit`: 2.39:1 for white text in the dark theme.
- `serviceFailureText` async, awaiting `loadBackendTranslation` per failure: ten
  catch paths become awaits and gain a round trip on a connection that may be
  what failed. Translating on the server: it formats before it knows the viewer.
- `HistorySource` cleared on dialog close: up to five chunk fetches per open,
  and a dialog left open on a wall still grows.

## 5. Sibling sites (commands, at the base)

| command | hits | disposition |
|---|---|---|
| `grep -nE 'class="[a-z-]*-hit"' $F` | 4 | px-keyed but `layout-port-hit` (r=16, 30.5 px median by the finder's null): no finding, out of scope |
| `sed -n '/^function cardStyleBlock/,/^}/p' $F \| grep -n 'min-height: *[0-9]'` | 4 | only `.hl-fold-head` sizes a control (§3 A) |
| `grep -nE 'err(\.message\| && err\.message)' $F` | 10 | all §3 D |
| `grep -nE 'READABLE\|var\(--(warning\|error\|success)-color' $F` | 21 | status uses all §3 C; `ACCENT_READABLE` kept |
| `grep -nE 'font-size: *[0-9.]+(em\|px)' $F` | 41 | §3 B, but three 11 px SVG-text rules (:5774, :5792, :5797) no metric reads: carry |
| `grep -nE 'style="[^"]*(font-size\|color\|padding\|margin)' $F` | 4 | §3 B/C |
| `grep -n 'this\.\(log\|actionLog\|seen\|covered\|memo\|chunks\)\b' $F` | 25 | all `HistorySource` (§3 E) |
| `grep -n 'this\.[a-zA-Z_]* = new \(Map\|Set\)()' $F` | 4 | `SetupPage.unsetOpen` bounded by the layout's places; the rest are `HistorySource`'s |

## 6. Evidence plan

- **Failing tests first**, `tests/card.mjs` (production source in its `vm`
  context), each red at the base: (1) setup editing at width 375: every
  `.layout-pipe-hit` stroke in px >= 24 (44 coarse) and names its pipe; (2)
  `cardStyleBlock` with `_coarsePointer()` true: `.hl-fold-head` min-height 44,
  32 under a mouse; (3) `serviceFailureText` with a `localize` stub: the sv
  exception text; with no `translation_key`: `err.message`; a pin failure under
  sv shows no `en.json` exception prefix; (4) `cardStyleBlock(false|true)`
  names no status `*_READABLE` literal and no `--(warning|error|success)-color`;
  (5) `HistorySource` over `tests/card_rig.mjs` `historyApi`, panned daily for
  30 days: `covered.size <= 5`, rows no more than a fresh 48 h source's.
- **Finder's harnesses, both ends** (§1), predicted after: D4-s1-01 0, D4-s1-03
  0, D4-s3-01 0, D4-s3-02 0, D4-s3-03 0, D4-s3-04 0, D9-s2-01 slopes 0 and
  `covered_chunks` <= 5. D4-s3-05: 1, the 14 px step alone (its scale set is
  fixed at {12, 13, 15, 18}); `offscale_spacing` 0 less the PR body's list.
  D6-s4-01: 0 both ends; planting `{minuter}` reads 1 and reddens the parity arm.
- **Null controls**, the finder's (§1), flat throughout: `--err=plain` 0, port
  median 30.5 px, fine-pointer fold arm 0, en/sv rows 0, dark ok one colour,
  `--arm nopan` 0.
- **Goldens:** no solver or payload change: `tests/golden/claimed_drift.txt`
  byte-identical. Card markup moves; the states `node tests/card_drift.mjs --list`
  names that move are claimed in `tests/golden/card_claimed_drift.txt` by the
  measurer, `claims-for:` equal to `VERSION` (`claim-files.md`).
- **Mutation targets:** the `Math.max` in the hit width and in the fold
  height; `serviceFailureText`'s `translation_key` branch and empty-localize
  fallback; `prune`'s cut compare and its keep-last-row rule; the dark literal
  of `--hpo-crit-fill`.
- **Layout and contrast:** `tests/card_browser.mjs` P9 grid (contrast, overflow,
  small all 0) after each rule family.
- **Score:** `python3 tools/audit/archscore/score.py --diff origin/main`. Base:
  `card_clone_copies` 103, `card_rule_copies` 70, `card_dead_definitions` 0; none
  may rise. The ten `(err && err.message) || err` sites are one rule spelled ten
  times, so `card_rule_copies` should fall; a `card_clone_copies` fall is banked
  only with the reviewer's diff and a reason.

## 7. Hot files, serial position, carries

- One hot file, `$F`, first in its `PLAN.md` hot-file row (card, then
  product-text); `R11-SEAM-comments-production`'s card part is released after
  both. No `after` edge. No pinned grader in a restoring job registers what
  this adds: no p1/p2 split.
- **D5-s4-01's card units are not in this group.** `PLAN.json` puts D5-s4-01 in
  `R11-SEAM-comments-production` (groups[23], triage[160]) and this group's
  roster row names nine findings without it. This seat's brief says the card's
  comment units are "assigned there": recorded **pending owner confirmation**,
  `decision: orchestrator`. Meanwhile every comment this fix writes or rewrites
  meets C5, so that part's card count does not rise.

## Notes for the fixer

- The hit path's class must not start `setup-pipe` and it must not carry
  `data-edge`: `tests/card.mjs` counts `<path class="setup-pipe` (:3353, :3369)
  and reads topology from `class="setup-pipe[^"]*" data-edge=` (:5008, :6615).
  Carry: R11-SEAM-card (item pipe-hit-name)
- Draw the hit paths after the pipes and before ports and boxes, so a port or
  a box still wins where they overlap; the finder's scan reads the midpoint
  only, so check both ends too.
  Carry: R11-SEAM-card (item pipe-hit-order)
- `tests/card_rig.mjs`'s `hass` has no `localize` or `loadBackendTranslation`,
  and its rejections carry no `translation_*` fields: shape them on Home
  Assistant's websocket error, or test 3 pins the rig.
  Carry: R11-SEAM-card (item rig-localize)
- `prune` must keep the last `actionLog` row before the cut, or the mode band
  at the window's left edge goes blank (`actionRuns` forward-fills).
  Carry: R11-SEAM-card (item prune-keep-last)
- SVG text at 11 viewBox units (:5774, :5792, :5797).
  Carry: dismissed: no finding names SVG text size (item svg-11px)
