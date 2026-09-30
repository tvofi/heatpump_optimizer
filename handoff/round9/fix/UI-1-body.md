<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Part of #1791 (lane UI) and #201. Replaces the integration's Home Assistant brand images with tvofi's decided "dusk" mark (D1 in `handoff/round9/state/alt/design/DESIGN.md` at `7bca8ab3`). No Python module is touched; no golden moves; no `VERSION` edit.

Before: `brand/icon.png` and `brand/logo.png` were one 256 px square on an opaque grey ground, and the package and root `icon.png` were that older artwork.

After: the eight-file Home Assistant brand set (`icon`, `logo`, `dark_icon`, `dark_logo`, each with `@2x`) is transparent and trimmed; the package `icon.png` and root `icon.png` are the 512 px dusk icon; the SVG masters live in a new `docs/img/brand/`.

## Head

1b02904523fca54f96c185262cbbcd5cbb174b12 (code head; this body sits in a commit above it touching only `handoff/` paths).

## Mutation proof

The change adds data files, not logic, and no script pins the pixels. The sites it adds and what detects their removal:
- Delete the six new `brand/*` entries from the `tests/env_drift.py`, `tests/golden.py` and `tests/deployment_shape.py` closures in `tests/closures.json`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D` reports `MODE: FULL` with "no recorded closure mentions ...brand/dark_icon.png ..." (measured before the closures were re-recorded; that run is the red state). It does not fail a check; it forces the full suite.
- Remove the `docs/img/brand/*` glob from `tests/layout.json`: `python3 tests/layout.py` stays rc=0, because it reports unclassified paths as findings and `docs/img/*.svg` already sat there as planned moves. So the glob is not pinned by a failing check; n/a: no detector exists, recorded here rather than claimed.
- Delete the `deployment_shape.py` docstring edit: `tests/entities.py` fails the check "the lane's docstring records those measured numbers as the selection-cost note (#1218)" (seen red with 85 files and stale 79).
`--max 0` was not used.

## Null control

Unmodified tree at `48786f65`: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 1990 ENTITY CHECKS PASSED`. With only the six new PNGs added and closures not re-recorded, the same command printed `2 of 1990 ENTITY CHECKS FAILED` (the #1218 pair above). After the closure re-record and docstring fix it prints `ALL 1990 ENTITY CHECKS PASSED`.

## Figures

Brand images, measured with Pillow (`Image.size`, `.mode`, `getchannel('A').getextrema()` and `.getbbox()`); alpha extrema (0, 255) means real transparency, the bbox is the opaque extent:

| file | size | mode | alpha | opaque bbox |
|---|---|---|---|---|
| custom_components/heatpump_optimizer/brand/dark_icon.png | 256x256 | RGBA | (0, 255) | (8, 46, 248, 209) |
| custom_components/heatpump_optimizer/brand/dark_icon@2x.png | 512x512 | RGBA | (0, 255) | (21, 96, 491, 415) |
| custom_components/heatpump_optimizer/brand/dark_logo.png | 558x130 | RGBA | (0, 255) | (0, 0, 558, 130) |
| custom_components/heatpump_optimizer/brand/dark_logo@2x.png | 1116x259 | RGBA | (0, 255) | (0, 0, 1116, 259) |
| custom_components/heatpump_optimizer/brand/icon.png | 256x256 | RGBA | (0, 255) | (8, 46, 248, 209) |
| custom_components/heatpump_optimizer/brand/icon@2x.png | 512x512 | RGBA | (0, 255) | (21, 96, 491, 415) |
| custom_components/heatpump_optimizer/brand/logo.png | 558x130 | RGBA | (0, 255) | (0, 0, 558, 130) |
| custom_components/heatpump_optimizer/brand/logo@2x.png | 1116x259 | RGBA | (0, 255) | (0, 0, 1116, 259) |
| custom_components/heatpump_optimizer/icon.png | 512x512 | RGBA | (0, 255) | (21, 96, 491, 415) |
| icon.png | 512x512 | RGBA | (0, 255) | (21, 96, 491, 415) |

Logos have their opaque content filling the canvas (trimmed); the shortest logo side is 130 px, inside Home Assistant's 128 to 256 range. Icons are square; the dusk icon's opaque extent is inside the square canvas as designed.

- Byte identity of the two `icon.png` (RO-4 deletes the root copy on this premise): `git rev-parse HEAD:icon.png HEAD:custom_components/heatpump_optimizer/icon.png` prints `dbed6dd4e4566808761e563423796eebe73969af` twice.
- Layout barrier: `python3 tests/layout.py` before (at `48786f65`, no `docs/img/brand`) and after (code head) both exit 0 and print `layout self-test: ok`; `docs/img/brand/*` is added to the docs category in the same commit as the eight SVGs.
- Classification: the six new PNGs sit inside `custom_components/`, so `tests/closure.py` widens `env_drift.py` and `golden.py` over them and `deployment_shape.py` materialises them; `tests/derive_closures.sh --single` was run for those three scripts and only adds the six paths (plus timing noise) to `tests/closures.json`. `docs/img/brand/*.svg` is INERT via the `docs/` prefix; no script pins them (INERT_EXCEPT untouched).
- `deployment_shape.py` docstring: the lane now reaches 85 production files, 67 of 378 pairs at 0.80 or more, twelve pairs at exactly 1.00; counts re-derived by the script in `tests/entities.py` (#1218 check) and by the same Jaccard rule on `tests/closures.json`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget moved.
- Scope: `python3 tests/closure.py select` reports `MODE: FULL` because `tests/closures.json` changes the gate itself; the full run is below.

## Red checks

none known before CI. Expected: `tests/layout.json` is code-owned, so the merge waits on tvofi's approving review at the head.

## Forward-carry

none

## Friction

none
