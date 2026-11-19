# D4-s1, round 11: D4.M1, the card in a real browser

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B9 (4 vCPU). Chromium 158.0.8127.18 headless shell,
playwright 1.65.0, the version `tests/pwlane/package-lock.json` locks (browser rev 1254). Plan payload from
`tests/plan_view.py` (`HPO_PLANDATA`). Exposure: none. No `docs/` and no GitHub were read.

## Method

- Universe: `REPO=<git repo> node dev/audit/rounds/round11/D4/s1/enumerate_m1.mjs` lists the 45 `card_drift --list`
  states times the 3 `language` population values, 135 items.
- `m1_browser.mjs` rebuilds card_drift's STATES for a real DOM. It injects the production card source and
  `tests/card_browser.mjs:instrument()` (`__p9.measure`, the lane's own contrast, overflow, ink-overlap, target
  and pop-up measures). It drives each item at 375x812, 768x1024 and 1280x800, in light and dark, with
  reduce and no-preference motion, and with a fine and a coarse pointer: 24 cells and 3240 renders. Per render
  it adds a hover over every interactive target (rect diff plus the PerformanceObserver layout-shift value), a
  Tab sweep through every tabbable (reach, indicator, visibility), console and pageerror capture, and F1 as
  written (`strict_small`). It then re-runs the tab sweep with `TABONLY=1` and a scroll-independent visual-order
  check.
- Three witness harnesses wrap it with `PROBE`/`HPO_PERTURB`: `m1_pipes.mjs`, `m1_tooltip.mjs`, `m1_slots.mjs`.
  Each has an in-memory one-line production perturbation.
- Results: `m1_full_results.txt` (RESULT block plus grouped summary), `m1_full_renders.jsonl.gz`, `m1_tab_renders.jsonl.gz`,
  `m1_*_result.txt`. Screenshots: `screens/<state>_<vp>.jpg` (en, light, reduce, fine pointer; 135), plus `witness_*.png`.
  Wall time (provisional): 1550 s for the grid's last 1249 renders, load1 1.15 at its end.

## Findings

| id | severity | what | number | perturbation |
|---|---|---|---|---|
| D4-s1-01 | medium | layout editor pipes (click to remove) hit band 2.75 / 3.25 / 5.75 px | 576/576 under F1 | stroke 3.5 -> 60: 296 |
| D4-s1-02 | low | shared-step tooltip runs 20.6 px past its chart at 375 fine: `fitWhy` trims only `.tt-why` | 12/72 renders (null tooltip_hover 0/72) | fitWhy also drops `.tt-reason`: 0 |
| D4-s1-03 | low | `.hl-fold-head` 32/39 px under coarse pointer, not on `htmlTargetFloor` | 72 targets | added to the list: 0 |
| D4-s1-04 | medium | slot-hit targets at 375 px under floor (min 17.7 px); 99 also fail WCAG 2.5.8's circle | 147 of 2700 (768/1280: 0) | skip boxed-in resolution: 0 |

All are class P9 guesses. Details are in `findings/*.json`.

## Non-findings (3240 renders)

- contrast 0, overflow 0, overlap 0, console errors 0, options 0.
- Tab reach: 0 unreached of 73472 tabbables. Indicator: 0 stops without a visible focus change. Visibility: 0 invisible stops.
- Hover CLS 0.0000. The 668 rect moves all occur in `draft_mid_drag` under the coarse arm, where a drag is held open
  by design, so they are a harness artefact.
- Tab order: 289 backward steps. All are column transitions (setup diagram columns, what-if columns at 768 and
  1280 px) or into the open slot menu, so I judged order held.
- The pop-up viewport overflow at 375 px for de/coarse comes from where the chart was scrolled (the chart's own
  bottom is past the viewport). The placement is not at fault.

## Not finished

- The released build in a real Home Assistant frontend: there is no recorded render and no instance on this box (brief, Limits).
- `editor_schema` x de, en, sv: the editor is HA's `<ha-form>`, which is undefined here, so it is not_reached.

## Redispatched

- C1 examined: the denominator is 135, of which 132 were examined.
- C2 examined: tab order, console, hover shift, the no-preference motion arm, screenshots, and the lock's Chromium.
  The lock has moved to rev 1254, which is the one this run used.

## Cells

Of the 15 files in this seat's cells, M1 has a browser surface only in `www/heatpump-optimizer-card.js`. The
config-flow, translation, services, icons and blueprint files render only inside HA's frontend; they are M2's
subject and outside this seat's steps.

## Note

This seat's directory held a partial run of this same seat from earlier in the session (1980 renders). The
grid was resumed with `RESUME=1` to 3240. The 7 renders that threw when the browser was lost were dropped and
re-run. The `TABONLY` and `tab_backward` additions to `m1_browser.mjs` came after the grid run and leave its
measured checks unchanged.
