# Sweep: "pointer-only editing with no keyboard route"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D4-s1-04
(verified, medium). Not a ledger class (new).

## Enumerator

`enumerate.py` widens the seam_rule to every `pointerdown`-wired surface in
the card (4 total) and checks each for a `keydown` listener within 60 lines
(the same setup block).

```
$ python3 tools/audit/round9/D14/sweep/pointer_only_no_keyboard/enumerate.py
RESULT pointer_driven_surfaces=4
  line 5572: pan gesture, keyboard_route_nearby=False
  line 8502: dialog drag surface, keyboard_route_nearby=True
  line 9660: picker surface, keyboard_route_nearby=True
  line 10266: setup layout editor canvas, keyboard_route_nearby=False
```

## Disposition of the two candidates with no nearby `keydown`

- **line 10266** (`canvas.addEventListener("pointerdown", this.onDown)`, the
  setup layout editor): confirmed **instance** — D4-s1-04. Removing a pipe,
  drawing a pipe and moving a box (`onDown`/`onMove`/`onUp`/`onClick`, lines
  10266-10270) have no equivalent control reachable by keyboard; the block's
  own `keydown` neighbours (8507, 9682, 9698) belong to other surfaces, not
  this one.
- **line 5572** (`svg.addEventListener("pointerdown", this.onPanDown)`, the
  chart pan/zoom gesture): **guarded**. `attach()`'s docstring (read at
  lines 5540-5552) states the intent directly ("a zoom that only exists as
  a gesture is a zoom half the users never find") and `controlsHtml()`
  (line 5553) renders three native `<button type="button">` elements
  (zoom in/out/reset) wired via `wire(sel, fn)` to a `click` listener
  (line 5574-5579). A native HTML `<button>` is keyboard-focusable and
  fires `click` on Enter/Space without any explicit `keydown` handler, so
  the pan gesture's effect (zoom in/out, reset to the whole plan) has a
  keyboard-operable equivalent even though the pointer gesture itself has
  none. This is why the enumerator's 60-line window missed it: the guard is
  a same-effect button, not a `keydown` listener on the gesture surface.

## Positive control

Line 10266 re-finds D4-s1-04 exactly (the same file:line the finding cites).

## Null control

The two surfaces with `keyboard_route_nearby=True` (8502, 9660) are true
negatives on inspection: both have an explicit `keydown` handler on the
same dialog/picker element (`svg.addEventListener("keydown", ...)` at 8507;
`picker.addEventListener("keydown", ...)` at 9698).

## Perturbation

Direction check: removing the `controlsHtml()` zoom buttons (or the
`wire(".vc-in/.vc-out/.vc-reset", ...)` click wiring) would take line 5572
from `guarded` to the same shape as line 10266 (pointer-only, no keyboard
route) — the disposition is keyed on the presence of that equivalent
control, which the enumerator's window search cannot see directly (a
human-verified guard, not a re-derivable AST check without teaching the
detector the "equivalent control" relation).

## Baseline vs main

`git diff 1936d5ca..origin/main -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
is a 332/119-line diff; grep for `keydown`/`pointerdown`/`addEventListener\("click"` in the
diff hunks (checked earlier this sweep) shows no touch to either surface's
event wiring. Both dispositions hold on `origin/main`.

## Disposition table

| seam | disposition |
|---|---|
| card.js:10266-10270 (setup layout editor: draw/remove pipe, move box) | instance — D4-s1-04 |
| card.js:5572 (chart pan gesture) | guarded — equivalent zoom in/out/reset buttons, keyboard-operable natively |
| card.js:8502-8507 (dialog drag surface) | guarded — own `keydown` handler at :8507 |
| card.js:9660-9698 (picker surface) | guarded — own `keydown` handler at :9698 |

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). A lint pass flagging any `pointerdown`/`pointermove`
listener with no `keydown` on the same element AND no adjacent
`<button>`-wired equivalent would need the "equivalent control" relation
taught by hand per surface (as this sweep just did) — not cheaply
AST-derivable; left as a lead.

## Gate seconds

~0.02s (one regex scan of the card source).
