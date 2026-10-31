# D4-s1 — round 10, D4.M1 (the card in a real browser)

Baseline 17f1c55fad1b. Machine: macOS arm64 (B9), shared box (load1 22-40 during runs).
Chromium: the lock (tests/pwlane, playwright 1.56.1) wants rev 1194, which is not in any
local cache and `~/.cache/pw-browsers` does not exist; runs used the cached
chromium_headless_shell-1148 (Chromium 131) via `HPO_CHROME`. Font: "Liberation Sans" is
absent on macOS, so text metrics fall back to Arial.

## Method
- `grid_complement.mjs` slices `tests/card_browser.mjs`'s own `gridStates`, `instrument()` and
  `p9Grid` at run time (so it measures the tree it runs in) and substitutes the cell list:
  `complement` = the 5 viewport x theme x language cells the lane does not run (768/1280 dark en,
  375/768/1280 dark sv); `coarse` = 375/768 light en with hasTouch/isMobile and the measure called
  with `coarse=true` (the lane always passes `false`); `fine` = the control; `motion` (defined, not run).
  On the coarse arm the 2.5.8 spacing exception is dropped (WCAG 2.5.5 has none);
  `COARSE_EXCEPTION=1` restores it.
- `pipe_hit.mjs` hit-tests the layout editor's pipes, which the grid's bbox-based target rule
  cannot see (a path's bounding box is not its stroke; a vertical pipe's bbox width is <0.5 px and
  is filtered out entirely).

## Findings

### D4-s1-01 — layout-editor pipes are 1.25-5.75 px touch targets
In the setup page's layout editing state, "clicking a pipe is how one is removed" (card CSS
comment), but the hit-tested band of every pipe is 1.25-5.75 px (stroke-width 3.5 viewBox units,
no hit path). 30/30 pipe measurements under a fine pointer are below the card's every-pointer
24 px floor and 30/30 under pointer:coarse are below its own 44 px floor (2 topologies x 3
viewports x 2 pointers, 60 pipes). Perturbation `PIPE_STROKE=30` (in-memory edit of the editing
stroke rule): band_max 5.75 -> 52.75 px, under-24 30 -> 14, under-44 30 -> 23.
Outputs: `pipe_hit.out`, `pipe_hit_stroke30.out`. A keyboard route exists (`pipeKb`), so medium.
Why the lane misses it: `instrument().targets()` measures `getBoundingClientRect`, which for a
curved path is its bbox (60.2x10.7) and for a straight vertical pipe is filtered as <0.5 px wide;
the strict coarse arm of `grid_complement.mjs` caught only the bbox (4 instances, `grid_coarse.out`).

## Non-findings
- Complement cells (175 cell-states): 0 contrast, 0 overflow, 0 popup, 0 small-target,
  0 options, 0 threw, 0 missed (`grid_complement.out`).
- Coarse arm with 44 px floor, lane's exception: 0 small; without the exception only the pipe bbox
  (`grid_coarse.out`). The card's `_coarsePointer` floor holds for HTML targets.
- Overlap `text "2" x text "3"` 2 px shared ink at 375 px in 4 states, in both the fine control
  and the complement — harness-gap: present in a cell the CI lane already runs, attributed to the
  missing Liberation Sans font on macOS; not reported.
- One coarse cell threw a Playwright clip error (score_open/375) — harness gap, not a card defect.

## Unfinished (D4.M1)
Keyboard tab order through every focusable, console-error sweep, layout shift on hover, the
reduced-motion-off arm (`CELLS=motion`) and screenshots were not taken.

## Exposure
None.
