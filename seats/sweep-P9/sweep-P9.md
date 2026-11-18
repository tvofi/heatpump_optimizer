# Class P9 sweep, round 11 (D14 method steps 3-4)

Class P9 in `dev/audit/config/bugclasses.json` is card UI: a clipping ancestor,
a missing colour token, or an unfloored hit target. The class row is
`barriered` by the P9 browser grid in `tests/card_browser.mjs`.

The findings in the class are D4-s1-01, D4-s1-03, D4-s3-02, D4-s3-03,
D4-s3-04 and D4-s3-05. This sweep ran in a detached worktree at
`origin/handoff/audit-r11-register`, with Chromium on this box and a
`tests/plan_view.py` payload.

## Property

Every pointer target the card draws meets the 24/44 px floor or WCAG 2.5.8's
spacing exception. Every status colour comes from the token layer
(`CARD_TOKENS`). Every text run meets the card's own type floor:

- 12 px for HTML text;
- 8 px (`MIN_AXIS_FONT_PX`) for SVG text.

No ancestor clips ink that cannot be reached, and the values in one stats row
share a baseline.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-P9/enumerate_p9.py` is a line scan
of the card source. It generalises the six findings' seams into five families:

- **TARGET**: a literal `min-height` under 44 px, or an `.editing` SVG stroke
  used as a hit band.
- **TYPE**: a `font-size` that is neither `var(--hpo-text-*)` nor `max(12px, …)`.
- **COLOUR**: an interpolated `*_READABLE` constant, or a direct HA
  `--error/--warning/--success-color`.
- **CLIP**: `overflow: hidden`.
- **STACK**: `display: block; margin-top` on a value under its label.

It returns
`RESULT seams=69 TARGET=2 TYPE=55 COLOUR=7 CLIP=3 STACK=2`, saved as
`enumerate.out`.

- **Positive control**: the scan lists every judged site.
  - `.setup-svg.editing .setup-pipe` (D4-s1-01).
  - `.hl-fold-head` (D4-s1-03).
  - `.hl-value` (D4-s3-02).
  - The tooltip, `tt-shared`, `sp-note` and `layout-verdict` sizes (D4-s3-03).
  - The `ERROR_READABLE` lines and the wood/space-blocked `--warning-color`
    stripes (D4-s3-04).
  - The off-scale type declarations (D4-s3-05).
- **Null control**: `--fixture clean` returns `seams=0`.
- **Perturbation**: `--fixture perturbed` adds one line,
  `.x-btn { min-height: 32px; }`, and returns `seams=1`.

## Measurements on this box

- **`m3_look.mjs`, full 900-cell grid**:
  - `tile_row_misaligned=12`, all in `.hl-stats`; the 684 other grid rows read 0.
  - `below_floor_cells=78`, over 9 elements, all of them inside the tooltip,
    `sp-note` and `layout-verdict`.
  - `offscale_font_sizes=17`.
  - `role_colour_split=5`.

  These reproduce the four D4-s3 findings and show nothing outside them.
- **`m1_browser.mjs`, `history_unavailable` at 375 px**: `small=0` and
  `strict_small=0`. The finder's full run had 24 `rect.slot-hit` at 19.9 px
  failing even with the spacing exception; that did not reproduce here, and
  `slotHitExtents` lays those targets out against the floor.
- **`probe_svg_text.mjs`** (new; it runs the finder's `m1_browser.mjs` with a
  PROBE):
  - The setup diagram's SVG text renders at least 8.56 px at 375 px:
    0 runs under the 8 px SVG floor, but every run under the 12 px HTML floor
    (824 of 1648 at 375 and 1280 combined).
  - The perturbation (setup rules at 16 px) moves the 12 px count from
    824 to 576.
  - Null control: chart text under 8 px is 0, because it is floored by
    `chartFontUnits`.
- **`probe_token.py`**: `.setup-pipe.invalid` strokes with
  `var(--error-color, #db4437)` and exits 1. `--perturb` exits 0, and the null
  control `.status-pill.tone-crit` exits 0.

## Dispositions (69 seams)

### Instances

**Judged sites (48, `beyond_finding: false`)**: every TARGET, STACK `.hl-value`,
the `READABLE` and alert-stripe COLOUR seams, and the HTML TYPE seams. Each is
attributed to its finding and carries its harness command.

**Beyond the findings (1)**: `.setup-pipe.invalid`, card line 5876.

- The error role on an invalid layout pipe is painted from Home Assistant's
  `--error-color` (default `#db4437`). That is a third error shade beside the
  token `--hpo-crit` (`#b3261e`) and `ERROR_READABLE` (`#ca4c46`).
- This is D4-s3-04's mechanism on a seam its states did not draw: the m3_look
  catalogue has no invalid-pipe state.
- Probe: `probe_token.py '.setup-pipe.invalid'`.

`instances` = **1**.

### Guarded (12)

- **3 CLIP seams**: the P9 grid's clipped-ink zero rule; `m1` measured
  `overflow=0` over the finder's full grid.
- **`.tile-v` STACK**: measured 0 misaligned rows of 684.
- **8 chart SVG text sizes**: `chartFontUnits` / `MIN_AXIS_FONT_PX`; probe
  reads 0 under the floor.

### Not applicable (8)

- **5 setup-diagram SVG text rules**: they render at or above the card's own
  8 px SVG floor at every grid viewport, and the 12 px floor applies to HTML.
  No rule floors them, though: a card narrower than 375 px would cross 8 px.
  This is recorded as a barrier gap, not an instance.
- **3 replay-SVG lines**: drawn at the SVG's own width inside an `overflow-x: auto`
  scroller, and measured 0 under the floor.

## Barrier

The class stays barriered in the row, but `barriered: false` here: the grid let
six findings through, and its colour reach control cannot see a state it does
not drive.

Proposed barrier: `enumerate_p9.py` as a zero rule in `tests/card.mjs`:

- **COLOUR**: no direct HA status var and no `*_READABLE` constant in a rule.
- **TARGET**: no literal `min-height` under the floor on a control.
- **TYPE**: every `font-size` drawn from the scale or a `max(12px, …)` guard.

Its allow-list would be the guarded and not-applicable seams above, and it
costs well under 1 s. Add an invalid-pipe state to the grid's catalogue.

`root-cause.md`'s P9 record is in the class row's `rca` entries.
