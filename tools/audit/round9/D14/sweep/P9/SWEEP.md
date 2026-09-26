# S5 class sweep: P9 -- Card UI: a clipping ancestor, missing colour token or unfloored hit target

Ledger class `P9`, open since round 1, instances in rounds 1, 2, 4, 5, 6, 7. Round-9 verified /
weakened findings: D4-s1-01 (verified, medium), D4-s1-02 (weakened low), D4-s1-03 (verified,
medium), D4-s1-05 (weakened medium).

## Enumerator

Reused `tools/audit/round9/D4/s1/sweep.mjs` (the D4-s1 finder's browser geometry sweep) unchanged,
copied here as `enumerate.mjs`. It renders the real card in headless Chromium over
`tests/card_rig.mjs`'s state catalogue and measures, per (state x viewport x theme x lang x mode)
cell: clipping overflow, text overlap, WCAG contrast, hit-target floor and its 24px spacing
exception, keyboard reachability, pop-up viewport/chart clamping, listbox option legibility, and
console errors.

Command (from the export root):
```
T=$(mktemp -d) && HPO_PLANDATA=$T/plandata.json PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  python3 tests/plan_view.py >/dev/null && \
  HPO_PLANDATA=$T/plandata.json NODE_PATH=tests/pwlane/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
  node tools/audit/round9/D14/sweep/P9/enumerate.mjs --no-keys --modes normal \
    --states x_pin_ok,x_pin_fail,x_save_ok,x_save_fail,x_dhw_clamped,x_save_confirm,\
draft_dirty_menu_open,x_menu_right_edge,x_menu_right_edge_dhw,picker_open_filtered,\
x_live_default,x_live_default_expanded
```
(`tests/pwlane` needed `npm ci` and Playwright's browser download skipped in favour of this box's
pre-installed Chromium at `/opt/pw-browsers`, since neither was present in this cloud container.)

## Controls (re-run on this box, this session)

- **Baseline, canonical targeted grid** (12 states x 3 viewports x 2 themes x 2 languages,
  `cells=144`): `overflow_instances=0`, `overlap_instances=160` (60 cells), `contrast_instances=90`
  (72 cells), `pointerOnly_instances=204` (144 cells), `now_marker_collisions=24`,
  `option_indistinct_pairs=8`, `option_cut=16`, `popup_out_cells=6`,
  `max_popup_viewport_out_px=9.7`, `kb_unreached=0`, `console_error_cells=0`. Bit-for-bit identical
  to the numbers documented in the D4-s1 finder's own harness header.
- **Perturbations** (all four re-run this session, each moving in the documented direction):
  - `--perturb status_text_token` (swap the hard-coded error/success/warning colours for HA's
    theme tokens): `contrast_instances` 90 -> 12.
  - `--perturb menu_clamp` (clamp the slot-menu placement to the chart box): `popup_out_cells`
    6 -> 0.
  - `--perturb picker_wrap` (wrap or widen the setup picker's `<option>` text): `option_indistinct_pairs`
    8 -> 0.
  - `--perturb now_temp_below` (place the now-temp label below the now-marker instead of over it):
    `now_marker_collisions` 24 -> 0.
- **Null control**: the same grid's non-flagged cells are the within-sweep null (72 of 144 cells
  have 0 contrast instances, 138 of 144 have 0 popup-out, etc.) -- there is no separate "clean
  fixture" for a rendered UI; a `--fixture` arm would require a second card build with no known
  bug, which does not exist. This is a limitation, noted below, not a control we ran.

## Disposition

Full instance listing in `seams.txt` beside this file (grouped by mechanism, with the CSS
selector, contrast ratio or pixel spillover, and the cell(s) it occurs in).

- **4 instance** (the round-9 findings): D4-s1-01 (contrast, 90 instances across the delta/pin/
  save/dhw-warn text), D4-s1-02 (popup viewport/chart overflow, 6 cells), D4-s1-03 (listbox option
  legibility, 8 pairs), D4-s1-05 (now-marker/now-temp collision, 24 instances).
- **1 instance, new**: the SVG axis-label overlap (`overlap_instances=160`, "60"/"°C", "6"/"kW",
  "400"/"W/m²" pairs, distinct from the now-marker collision above and not covered by any of the
  four findings) -- the chart's unit suffix is drawn at a fixed offset from its numeric label with
  no measured-width check, the same class of bug as D4-s1-05 (a label placed by a constant offset,
  not by the sibling's measured box) but at a different DOM seam. Probe: any cell with
  `viewport width <= 1280` and the chart's numeric/unit label pair renders overlapping (contention-
  immune; reproduces every run at 1280x800 and 375x812).
- **1 instance, new**: `pointerOnly_instances=204` across 8 distinct selectors (both chart pan
  surfaces plus the 6 setup-picker entity rows) -- none of these is reachable by keyboard (no
  `tabindex`, no native focusable ancestor) despite being the card's only route to some actions
  (panning the chart, picking a sensor in the six-way `setup-hit` rows). This is outside the four
  round-9 findings' shape (which were about visual clipping/colour/hit-size, not keyboard route)
  but matches P9's stated mechanism ("unfloored hit target") only loosely; recorded here because
  `kb_unreached=0` in this sweep's `--no-keys` run does NOT check it (the flag skips the keyboard
  cells entirely) -- flagged as **exposure**, not counted toward N, since it was not actually swept
  this session (see Unfinished).
- **0 guarded, 0 not applicable** among the swept mechanisms -- every mechanism the harness
  measures at the canonical grid produced at least one instance.

## Count and RCA

N = 4 verified/weakened round-9 findings (D4-s1-01, -02, -03, -05) + 1 sweep-confirmed new instance
(the SVG unit-label overlap) = **5**. The keyboard-route gap is exposure, not counted (not
actually measured this session). **rca: true** (N >= 3; the brief's table already carried
`rca: yes` at N=4).

## Barrier proposal

`enumerate.mjs`'s canonical-grid invocation above as a CI lane (already close to the shape of a
"browser" CI job per `.claude/workflows/web-fragments.md`'s job list): assert
`contrast_instances == 0`, `popup_out_cells == 0`, `option_indistinct_pairs == 0`,
`now_marker_collisions == 0`, and a new `overlap_instances == 0` once the SVG label fix lands.
Cost: ~35s wall for the 144-cell canonical grid on this box (measured, uncontended, 4-core); the
full 1626-cell grid (`--shots`, no `--states`) is documented at ~10-15 min and is not proposed for
the gate, only for a periodic (nightly) full sweep.

## Unfinished / exposure

- The keyboard cells (`--no-keys` was passed to keep this run inside the sweep's time budget) were
  not run this session; `kb_unreached` and the pointer-only-vs-keyboard-route cross-check are
  therefore not verified at the canonical grid, only asserted from the D4-s1 finder's own
  documented `kb_unreached=0` at the FULL 1626-cell grid (a different, wider run than this
  session's). Flagged as exposure: the keyboard route for the pointer-only seams above should be
  re-checked by whoever fixes P9.
- The full 1626-cell grid (every one of the 47 launch states) was not re-run this session; only
  the documented canonical 144-cell subset, per the class sweep's time budget.
- No `--fixture` (clean-tree null) arm exists for a rendered UI; the within-grid non-flagged cells
  serve as the null, as stated above.
