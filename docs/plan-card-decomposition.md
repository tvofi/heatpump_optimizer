# The card decomposition — program plan

## Context

`custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` is 8,200
lines. The custom element `HeatpumpOptimizerCard` is ~5,000 lines with 165
members and ~65 `this._*` fields. Issue #95 (PR #125, v6.1.1) took the two
seams that extracted cleanly — `cardStyleBlock()` and `setupSvgHtml()` — as
top-level functions behind thin same-named seams and closed with: "a god class
of 4,895 lines is still a god class; ... leaves the rest for whoever finds the
third."

The cost is real: the document-level keydown leak (#95's motivating defect) and
the memoised-`_runs` stale-state bug (v3.2.0) are the shape of bug this class
invites — state owned by one feature, reset (or not) by another, on a render
path that rebuilds the whole shadow root on the coordinator's schedule. The
card changes in most releases, so every feature PR pays the navigation tax.

**Outcome.** The custom element becomes a thin host that owns the Lovelace
contract and the render cycle, and delegates each feature to a collaborator
with an explicit, injected dependency surface and explicitly owned state.
Behaviour is byte-identical at every step; every existing test stays green at
every step; a differential markup gate (`tests/card_drift.mjs`, PR 0) proves it
per PR.

**Decisions (2026-09-01).**
- One file. Collaborators are classes / function groups inside the same
  script, in delimited sections. No build step, no `www/src/`. A physical
  split can follow later as a mechanical one-class-per-file step; it is out
  of scope here because it adds a build step the docs promise not to have.
- Seams are transitional. The closing PRs migrate `tests/card.mjs` onto the
  collaborators' public API and delete the seams.
- Latent defects the surveys found are logged as issues in PR 0 and fixed
  after the decomposition, each in its own PR. Every refactor PR is
  byte-identical.

This document is the program's source of truth, written to be executed PR by
PR by a session with only this repository in front of it. Line anchors are
from the v6.2.7 tree (the card is unchanged since v6.2.6); treat them as
anchors, not gospel.

## Hard constraints (verified)

1. **The shipped artifact stays one classic-script-compatible file.**
   `tests/card.mjs` and `tests/setup_qa_render.mjs` run it with
   `vm.runInContext(src, ctx)` — a *script*; `import`/`export` would throw.
   `tests/card_browser.mjs` injects it with `page.addScriptTag({ path })` on
   `about:blank`. `docs/dashboard-card.md` promises "one resource, no build
   step, no second chunk". `frontend.py`'s `?v=` cache-bust covers only the
   entry URL. No `package.json`/`node_modules` by design.
2. **Tests reach private members and script scope.** `tests/card.mjs` calls
   `_`-methods and pokes `_`-fields directly (`_layoutEdit` ×66, `_hass`
   written ×52, `_render` ×35, `_onCardClick` ×33, `_draftRuns` ×31,
   `_whatIfDraft` ×22, `_dialogPage` ×20, `_editBounds` ×16, `_slotMenu`
   ×14, `_hass.callService` monkey-patched ×11, `Card.slots` static ×15). It
   evaluates script-scope bindings with `vm.runInContext("<expr>", ctx)` —
   `NODE_SHAPES`, `SETUP_COL_W`, `SETUP_PAD`, `SETUP_ROW_GAP`,
   `SETUP_MIN_LABEL_W`, `setupTextW`, `fitSlotRow`, `PICKER_MAX_OPTIONS` —
   and swaps `ctx.Date` after load, both of which only work for a classic
   script in one realm.
3. **Source-text assertions.** ~28 assertions regex the card's source: ~22 on
   CSS rules inside the one `<style>` template literal (some indentation-
   sensitive), 4 on emitted markup literals (`<rect class="estimated"
   pointer-events="none"`, `<line class="crosshair" pointer-events="none"`,
   every `<div class="tt-*">`), 3 on dictionary literals, 2 on code.
   `tests/features.py` counts `"reasons.scheduled"` **exactly 3 times** in
   the file; `tests/entities.py` regexes `CARD_VERSION = "x.y.z"`;
   `tests/setup_qa_render.mjs` regex-extracts the `.setup-page … 
   .setup-pipe.invalid {…}` CSS run. No string literal, CSS rule or
   dictionary entry moves out of the file or gets re-indented.
4. **Pinned literal contracts** (#95): `data-edge="a>b"` with class order
   `setup-pipe[ layout-match| invalid]`, one `rect.setup-hit` per slot with
   `data-key`, the `apply_topology {layout, positions}` payload, the
   `0 0 720 H` setup viewBox, four editor ports per node; plus what
   `card_browser.mjs` measures in Chromium.
5. **Version pinning.** `VERSION`, `manifest.json`, the `RELEASE_NOTES.md`
   heading and both claim files' stamps are pinned by the suite; the card
   version moves whenever the card file changes.
6. **Scoped gate.** A new test script needs a `run` line in `tests/run.sh`,
   a `tests/closures.json` entry and — if it reads the plan payload — a
   `PRODUCERS` entry in `tests/closure.py`. Files with no recorded closure
   force a full PR run (safe); the `closures` job on main goes red until
   closures are re-derived.
7. **Program conventions** (`docs/plan-open-issues.md`, "Standing rules"):
   one PR per issue, squash-merged; tests import production symbols; claim
   files rewritten deliberately with the drift explained.

## Render model today (what every collaborator must respect)

- `set hass` → `setLanguage` → `_maybeRender(false)`; `_signature()` joins 17
  tokens; on change: `if (!this._runsDirty) this._runs = null;` then
  `_render()`.
- `_render()`: `_teardown()` (document Escape listener) → save dialog scroll
  → `_buildSeries()` (which calls `_applyView` mid-flight) → style, legend →
  topology/expandable → body → default dialog page → `_dialogHtml` (runs
  `_chartSvg` a **second** time) → `_dialogFontPx = 0` →
  `shadowRoot.innerHTML = …` → `_attachChartEvents` (chips, pointer tooltip,
  `_attachViewControls`, `_attachWhatIf`, `_attachSlotActions`,
  `_attachSlotEditing`) → expand button → score handlers → ha-card click →
  `_syncDialog` (dialog listeners, tabs, **`_attachSetupEvents` before
  `showModal`** — the picker focuses its `<select>`, order is observable) →
  `_cacheRect` → `_scaleDialogFont`.
- Cross-feature state: `_plot`/`_geom` written by `_chartSvg` (twice; last
  writer = expanded copy wins; `_geom.font` is the only divergent field and
  `_laneGroupInner` reads it), read by tooltip / pan / lanes. `_view`
  written by zoom, by slot-drag auto-pan (sync `_render()` every 90 ms,
  **not** the rAF path) and by `_onDialogClose`. `_suppressClick` written by
  pan and drag, read by `_onCardClick`. `_runs`/`_runsDirty` written by
  lanes, by `_applyManualPlan` and by `_maybeRender`.
- Two render idioms and both must survive: **forced** (`renderForced()`:
  `_sig = null` then rebuild) and **unforced** (`render()` / `_render()`
  alone, deliberately so a view change does not drop the draft).
- Partial paths that bypass `_render`: `_refreshLanes` (rewrites **all**
  `.lanes` groups from the one stored geom) → `_updateDelta`; `_renderView`
  (rAF-coalesced full render); `_refreshLayout`; picker filter;
  `_onPointerMove`; `_scaleDialogFont`; what-if result text.

## Target architecture

All inside `heatpump-optimizer-card.js`, each collaborator in its own
`// ---- <Name> ----` section between the module helpers and the host class.
Classes hold state; groups of module-level functions hold pure logic. Fewer,
larger collaborators beat many tiny ones here (no framework, no DI).

### The host: `HeatpumpOptimizerCard`

Keeps only: constructor (constructs collaborators), `setConfig` (validation
moved to a module-level `parseConfig(config)` that returns `cfg` or throws
the same `L("errors.*")`), `hass` accessors, `getCardSize`, statics,
`connectedCallback`/`disconnectedCallback`, `_signature` (composition),
`_maybeRender`, `_render` (composition, same order), `_chartBlock`,
`_noPlanHtml`, `_title`, `_onCardClick`/`_onExpandClick`, `_cacheRect`,
`_scoreOpen`, `_svgRect`, `_resizeObserver`, `_config`, `_hass`, `_sig`.

The contract a collaborator may use on its host, documented in the comment
block above the class:

```
host.hass, host.config          Lovelace inputs
host.shadowRoot                 the DOM it renders into
host.plan                       PlanSource                       (from PR 1)
host.frame                      last built frame {series, windowStart, windowEnd, plot, geom}  (from PR 1)
host.render()                   rebuild, keeping _sig
host.renderForced()             _sig = null, then rebuild
host.suppressNextClick()        the next ha-card click was the end of a gesture
host.onDraftChanged()           fan-out after a slot edit (lanes → manual-plan delta)  (from PR 5b)
host.title()
```

A collaborator never touches a sibling except through a dependency handed to
its constructor. The graph is acyclic (topological order below).

### Collaborators

| Name (instance prop) | Kind | Owns (state) | Depends on | Absorbs |
|---|---|---|---|---|
| `PlanSource` (`plan`) | class | `_resolvedCache`, `_statCache`, `_statMissAt`, `_sensorCountFor/N` | host | `_resolveEntity`, `_stateOf`, `_forecast`, `_forecastOf`, `_planAttr(Raw)`, `_diagnose`, `_estimatedPricesFrom`, `_lowerFloorModelled`, `_manualOverride`, `_currency`, `_priceUnit`/`_seriesUnit`, `_statEntity`, `_sensorCount`, `_statNumber`, `signatureParts()` |
| series functions | module fns | — | args only | `defaultWindow(spFc, dhwFc, hours, now)` (the first half of `_buildSeries` plus `dataEnd`); `buildSeries({spFc, dhwFc, solarFc, cfg, hidden, window, priceUnit, lowerModelled})` (the rest); `fieldPoints`, `extraFields`, `lineNote`, `nearestPoint`, `lineLabel`, `bandRow` (take `priceUnit`/`lowerModelled` as args — they are not pure today) |
| `ViewWindow` (`view`) | class | `_view`, `_viewLimits`, `_viewFrame`, `_pan` | host | `_applyView` → `apply(start, end, dataEnd)`, `_viewAdjustable`, `_zoomView`, `_panView`, `_resetView`, `_viewSpan`, `_viewCurrent`, `_onChartWheel`, `_onPanDown`, `_viewControlsHtml`, `_attachViewControls` → `attach(root)`, `_renderView`, `onDialogClosed()`, **`setStart(start)`** render-free setter for auto-pan |
| geometry functions | module fns | — | args | `timeAtClientX(svg, clientX, geom)`, `wrapOf(el, root)`, `chartSvgs(root)` |
| chart functions | module fns | — | args + `overlay(geom)` callback + `nextPatternId()` callback | `renderChart(frame, opts) → {svg, plot, geom}` = `_chartSvg` with `opts = {expanded, editing, title, priceUnit, estimatedFrom, now, overlay, nextPatternId}`; `timeAxis`, `valueAxis`, `seriesPath`, `steppedLine`, `smoothLine`, `sharedSpanBands` |
| tooltip functions | module fns | — | args | `tooltipRowsAt(frame, t)`, `tooltipHtml(rows, …)`, `reasonHtml`, `sharedTooltipHtml`; host keeps `_onPointerMove`/`_onPointerLeave` as thin DOM writers |
| `Legend` (`legend`) | class | `_hidden` | host, series fns | `_storageKey(Legacy)`, `_loadHidden`, `_saveHidden`, `_legendHtml`, `_onLegendClick`; `signature()` = `JSON.stringify(hidden)` |
| headline functions | module fns | — | PlanSource, cfg, `scoreOpen` | `headlineHtml(plan, cfg, scoreOpen)`, `scoreParts`, `finiteScore`, `scoreBreakdownHtml`, `headlineSignature(plan, cfg)`; `_scoreOpen` stays on the host with its two handlers |
| `ExpandedDialog` (`dialog`) | class | `_expanded`, `_dialogPage`, `_dialogScroll`, `_dialogFontPx` | host, `view` | `_dialogHtml` → `html({title, legend, body})`, `_syncDialog` → `sync(root, {attachBody, onPageChange})` (**`attachBody` before `showModal`**), `saveScroll(root)`, `pickDefaultPage(anyData)`, `resetFontMemo()`, `_onDialogClick`, `_onDialogClose` → `view.onDialogClosed()`, `_openExpanded`, `_closeExpanded(Quietly)`, `_scaleDialogFont` |
| bounds functions | module fns | — | args | `planEnd(forecasts)`, `editFloor(geom, now)`, `editCeilingParts(geom, now, windowHours, planEnd)`, `editCeiling`, `editBounds(...)`, `viewLimitsEditing(parts)` |
| `ManualPlan` (`manual`) | class | `_runs`, `_runsDirty` | host, `plan`, `view` (reset button), bounds fns, `SlotModel` | `_draftRuns` → `draft()`, `_resetRuns`, `set(channel, runs)`, `onPlanRefresh()`, `_laneSpecs`, `_editingEnabled`, `bounds()`/`ceilingParts()`, `_costDelta`, `_deltaHtml`, `_updateDelta`, `_overrideHtml`, `_applyManualPlan`, `_clearManualPlan`, `_attachSlotActions` → `attach(root)` (also takes `.wi-viewreset` from `_attachWhatIf`), `_slotResult`, **`sectionHtml()`** = `_whatIfHtml` section 1 |
| `LaneEditor` (`lanes`) | class | `_drag`, `_dragPan`, `_slotMenu`, `_menuOrigin`, `_menuEscape(Target)` | host, `manual`, `view`, geometry fns, `SlotModel` | `_laneGroupInner` → `laneGroupInner(geom)`, `_attachSlotEditing` → `attach(root)` with the closures promoted to methods, `_commitRuns` → `commitRuns` (= `manual.set` + `refreshLanes` + `host.onDraftChanged()`), `_refreshLanes`, `_openSlotMenu`, `_closeSlotMenu` → `teardown()`, `_globalKeyTarget`, `_restoreSlotFocus` |
| `WhatIfPanel` (`whatIf`) | class | `_whatIf`, `_whatIfTimer`, `_pendingSave`, `_saveTimer` | host, `plan` | `sectionsHtml()` = `_whatIfHtml` sections 2–3 incl. the `draft.dhwMin = ceiling` clamp, `_whatIfDraft`, `_currentComfortTemp/DhwMin/DhwWindows`, `_dhwMinCeiling`, `_attachWhatIf` → `attach(root)`, the `_on*` handlers, `_draftSignature`, `_onSaveSchedule`, `_cancelPendingSave`, `_whatIfOverrides`, `_runWhatIf`, `_whatIfSummary`, `disconnect()` |
| `SetupPage` (`setup`) | class | `_picker*`, `_pendingClear`, `_clearTimer`, `_setupNote` | host, `plan` | `_setupPageHtml` → `pageHtml({editing, bar, edit})` (layout facts passed in), `_setupSvg` → `svg(topo, edit) → {html, boxes}` (side-effect free), `redrawCanvas(edit)`, `_slotLive`, `_solarFallback`, `_setupPickerHtml` (the `_pickerSlot` write moves out of the markup builder — **verify byte identity**), `_pickerModel`, `_closePicker`, `_cancelPendingClear`, `_disarmClear`, the picker half of `_attachSetupEvents` → `attach(root, {layoutEditing})`, `_blurSetupRow`, `_restoreSetupFocus`, `note`, `applyNote(dlg)` |
| `LayoutEditor` (`layout`) | class | `_layoutEdit`, `_layoutBoxes` | host, `setup`, `plan` | `_layoutEditing/Saveable/Undoable`, `_copyPositions`, `_layoutBarHtml`, `_attachLayoutEditor` → `attach(root)`, `_toggleLayoutEdit` (calls `setup.closePicker()`), `_layoutEvaluate`, `refresh()` (= `_refreshLayout`: `setup.redrawCanvas(edit)` then verdict/buttons), `_layoutPoint`, `_layoutBoxAt`, `_onLayout{Down,Move,Up,Click}`, `_layoutAddEdge`, `_layoutRemoveEdge`, `_undoLayout`, `_saveLayout` (writes `setup.note`) |

Topological order: `plan` → series/geometry/chart/tooltip/bounds/headline fns
→ `legend` → `view` → `dialog` → `manual` → `lanes` → `whatIf` → `setup` →
`layout` → host. `SlotModel` stays as is (`Card.slots` static too).

### Frame, geometry and the overlay

`_render` builds one frame per render:

```
const now = Date.now();
const fcs = this.plan.forecasts();                       // sp, dhw, solar
const dw  = defaultWindow(fcs.sp, fcs.dhw, cfg.hours, now);
const win = this.view.apply(dw.start, dw.end, dw.dataEnd); // mutates view state, as today
this._frame = buildSeries({ ...fcs, cfg, hidden: this.legend.hidden, window: win,
                            priceUnit: this.plan.priceUnit(), lowerModelled: this.plan.lowerFloorModelled() });
```

`renderChart` is called once for the inline chart and once for the expanded
copy, exactly as today, and the host stores **the last** returned `plot` and
`geom` on the frame (last-writer-wins is today's behaviour; `_geom.font`
consumers see the expanded font while the dialog is open — logged, not
fixed). The overlay callback must set the frame's geom *before* drawing the
lanes, because lane bounds read it: `overlay: (geom) => { this._frame.geom =
geom; return this.lanes.laneGroupInner(geom); }`. `renderChart` returns `geom:
null` when editing is off and the host nulls `plot` on the no-data path only —
keep both quirks.

### Signature and lifecycle composition (explicit, not a loop)

```
_signature(): [...plan.signatureParts(), cfg.hours, cfg.title, ...,
               legend.signature(), ACTIVE_LANG, plan.currency(), headlineSignature(plan, cfg)].join("|")
_maybeRender(force): ... ; this.manual.onPlanRefresh(); this._sig = sig; this._render();
disconnectedCallback(): lanes.teardown(); if (dialog.expanded) dialog.closeQuietly();
                        whatIf.disconnect(); setup.cancelPendingClear(); resize observer
```

Only the collaborators that have something to say get a hook; no no-op
protocol methods. The `disconnectedCallback` sequence is preserved exactly
(the missing cleanups are issue material, below).

## Transition mechanics (every extraction PR)

1. **Move, don't rewrite.** Method bodies move verbatim; `this._x` becomes
   `this.x` / `host.x` / an argument. Do not reorder arithmetic (trailing
   float digits change), do not reorder attach calls, do not swap
   `undefined` sentinels (`_dialogPage === undefined` is load-bearing), do
   not route auto-pan through rAF.
2. **Seams.** Every moved method leaves a one-line same-named `_` delegate on
   the host; every moved field that `tests/card.mjs` reads *or writes* gets
   a `get _x()` / `set _x(v)` accessor pair on the host (fields tests write:
   `_view`, `_hidden`, `_sig`, `_dialogPage`, `_layoutEdit`, `_layoutBoxes`,
   `_setupNote`, `_pickerKey/Filter/Choice`, `_resolvedCache`,
   `_dialogFontPx`, `_expanded`, `_hass`, `_whatIfTimer`, `_pendingSave`,
   `_runsDirty`, `_geom`, `_plot`, `_slotMenu`, `_pan`, `_suppressClick`).
   Bound-handler identity (the constructor's `bind`s) is preserved by binding
   inside the collaborator's constructor and delegating from the host's
   same-named property.
3. **`tests/card.mjs` is untouched** in PRs 1–8 (the #125 rule). PR 9
   migrates it.
4. **Gate:** `node tests/card.mjs`, `node tests/card_drift.mjs origin/main`
   ("identical in all N states", empty claim list), `node
   tests/setup_qa_render.mjs`, then `GATE_SCOPE=auto ./tests/run.sh`. CI adds
   the Chromium lane.
5. **Release hygiene per PR:** bump `CARD_VERSION` (patch); the stamp commit
   that follows the merge carries the `RELEASE_NOTES.md` section ("No
   behaviour change; card markup identical in all N gate states") and restamps
   both claim files.

## The markup gate: `tests/card_drift.mjs` (PR 0, shipped)

Differential, not golden-based — mirrors `tests/env_drift.py`'s
tree-vs-`GOLDEN_REF` convention and needs no fixtures that Node/ICU/TZ could
move. See its header and `tests/README.md`. In short: the working-tree card
and `git show <ref>:<card>` run in two vm contexts from the shared rig
(`tests/card_rig.mjs`), each with a frozen Date at the same instant; twenty-
odd states are driven on both sides; every rendered tree must be identical
unless `tests/golden/card_claimed_drift.txt` claims the state (same grammar
and rules as `claimed_drift.txt`; `card.mjs` also checks the stamp).
`run.sh` skips it when `GOLDEN_REF` is unreachable or is this commit.

## PR sequence

Each PR is one issue, squash-merged, byte-identical, gated as above.

**PR 0 — Safety net and scaffolding (this PR).** `card_drift.mjs`,
`card_rig.mjs` (the vm context, states and topologies `card.mjs` and
`setup_qa_render.mjs` now share), the claim file, `run.sh`/`closure.py`/
`closures.json` wiring, `tests/README.md`. Card: delete the dead
`_styleBlock`; declare the 18 lazily-created fields in the constructor with
their exact sentinels; add `render()`, `renderForced()`,
`suppressNextClick()` and point the six forced sites and the three
`_suppressClick` writers at them; the host-contract comment; `CARD_VERSION`
5.4.2. Issues filed for the latent defects below.

**PR 1 — `PlanSource` + series functions.** Hoist `defaultWindow` /
`view.apply` / `buildSeries` into the host's `_buildSeries` seam (tests call
`_buildSeries()` for its `_viewLimits` side effect — the seam keeps it).
`lineLabel`/`seriesUnit`/`bandRow` take `lowerModelled`/`priceUnit` as
arguments. Drop `built.zoomed` only if no reader exists.

**PR 2 — `ViewWindow` + geometry functions.** Auto-pan (still in the host's
`_attachSlotEditing`) uses `view.setStart()` + sync `this._render()`, not
`panView`. `_viewLimitsEditing` stays a host seam over `_editCeilingParts`
until PR 5a.

**PR 3 — chart + tooltip functions.** `renderChart` returns `{svg, plot,
geom}`; host stores the last on `_frame`; overlay callback sets geom before
calling `_laneGroupInner()` (which still reads `this._geom` via the accessor
seam until PR 5b). `sharedSpanBands` gets `nextPatternId` backed by the
existing static counter — keep the static for identity. `_cacheRect` stays
on the host.

**PR 4a — `Legend` + headline functions.** Small, leaf.

**PR 4b — `ExpandedDialog`.** `sync(root, {attachBody, onPageChange})`;
`attachBody` = the host's `_attachSetupEvents` until PR 7a; `onPageChange`
closes the picker, resets scroll, renders. `_attachSetupEvents` runs before
`showModal`, as today.

**PR 5a — `ManualPlan` + bounds functions + the `_whatIfHtml` split.**
Section 1 → `manual.sectionHtml()`; sections 2–3 stay a host method
`_whatIfSectionsHtml()` until PR 6; the host's `_whatIfHtml` seam reproduces
the wrapper, the literal inter-section whitespace and the `!cfg.what_if →
""` early return. `.wi-viewreset` wiring moves from `_attachWhatIf` to
`manual.attach` (listener move, no markup change — say so in the PR).

**PR 5b — `LaneEditor`.** The 285-line `_attachSlotEditing` becomes methods;
`commitRuns` = `manual.set` + `refreshLanes` + `host.onDraftChanged()`;
`laneGroupInner(geom)` and the bounds take geom explicitly; slot menu +
document Escape + `teardown()`; keyboard + focus restore.

**PR 6 — `WhatIfPanel`.** Timers and `disconnect()`; `sectionsHtml()`.

**PR 7a — `SetupPage`** (page html, side-effect-free `svg()`, picker, note,
focus helpers, `attach(root, {layoutEditing})`). The layout↔picker cycle
resolves by folding the picker into the page; the page↔layout cycle by
passing layout facts into `pageHtml` and returning boxes from `svg()`.

**PR 7b — `LayoutEditor`.** Owns `_layoutEdit`/`_layoutBoxes`; `refresh()`
calls `setup.redrawCanvas(edit)` then updates verdict/buttons. PRs 7a/7b
can run in parallel with 5a–6 after PR 4b.

**PR 8 — Host cleanup.** `_render` is pure composition; `_signature` and
`disconnectedCallback` are explicit compositions in today's order;
`parseConfig`; remaining `this.shadowRoot` reach-ins from collaborators go
through `host.shadowRoot`.

**PR 9 (a/b/c) — Test migration + seam removal.** `tests/card.mjs` moves to
`card.view`, `card.manual`, `card.lanes`, `card.whatIf`, `card.setup`,
`card.layout`, `card.dialog`, `card.legend`, `card.plan` and the module
functions (via `vm.runInContext` expressions, as it already does for
`fitSlotRow`); delete the delegate and accessor seams; keep the genuine host
members (`_hass`, `_config`, `_sig`, `_render`, `_maybeRender`,
`_onCardClick`, `_openExpanded`, `_buildSeries`). Split by cluster if the
diff is too large to review (9a setup/layout; 9b slots/what-if/view; 9c the
rest). Add the **ratchet**: a card.mjs check that
`Object.getOwnPropertyNames(Card.prototype)` (minus `constructor`) is at most
the count PR 9 lands at, with a comment that it may only go down.

## Issues filed in PR 0 (fixed after the program, one PR each)

1. `disconnectedCallback` leaves the auto-pan interval (`_dragPan`), the pan
   rAF (`_viewFrame`) and the window-level pointer listeners alive when a
   card is removed mid-gesture.
2. With the dialog open, `_refreshLanes` redraws the **inline** chart's lanes
   at the expanded font: `_geom` is last-writer-wins and `_laneGroupInner`
   reads `geom.font`.
3. `_forecast` (guards unavailable/unknown, JSON-decodes) and `_forecastOf`
   (neither) read the same attribute differently.
4. `_setupPickerHtml` writes `_pickerSlot` from inside a markup builder.
5. `HeatpumpOptimizerCard._sharedPatternSeq` is a page-global counter shared
   by every card instance; pattern ids depend on render history.
6. A stale `_geom` survives a no-data render (only `_plot` is reset).

## Verification (per PR)

1. `python tests/plan_view.py && node tests/card.mjs` — every check, file
   untouched (PRs 1–8).
2. `node tests/card_drift.mjs origin/main` — "identical in all N states",
   claim list empty.
3. `node tests/setup_qa_render.mjs`.
4. `GATE_SCOPE=auto ./tests/run.sh` and the CI PR gate incl. the Chromium
   lane.
5. After merge: the `closures` job on main must stay green.
6. Program end: the host class's line count and the ratchet number in the
   PR 9 description; `docs/architecture.md` ("one self-contained file") and
   `docs/dashboard-card.md` stay true.

## Out of scope / follow-ups

- Physical split into one file per collaborator with a stdlib-only
  concatenation build and a CI staleness check (the closures.json pattern).
- The six issues above.
- Unifying the two pointer-down protocols on the chart svg (pan vs drag,
  coordinated only via `dataset.channel`).
