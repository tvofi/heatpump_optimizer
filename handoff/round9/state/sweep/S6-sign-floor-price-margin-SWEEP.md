# Class sweep — "a sign floor on a price margin breaks the stated piecewise identity"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D2-s3-02** (weakened(low) — `pv.import_margin(import_prices, export_price)`
floors `import_prices - export_price` at 0. When `export_price > import_price`, the margin goes
to 0, and `blended_block_prices`' piecewise identity `effective = prices -
import_margin(prices, export_price) * covered_fraction` silently degrades to `effective = prices`
(PV self-consumption credited at zero) rather than the signed discount the function's own
docstring implies for that regime).

## Enumerator

`tools/audit/round9/D14/sweep/sign-floor-price-margin/enumerate.sh`: greps `pv.py`/`optimizer.py`
for `import_margin` and every `np.clip(..., 0.0, None)` site, to check whether any *other*
zero-floor in the pricing path is applied to a signed price margin (this class) rather than a
non-negative physical quantity (a different, legitimate pattern).

## Disposition

| seam | disposition | note |
|---|---|---|
| `pv.py:92-101 import_margin` (the floor itself) | **instance** | D2-s3-02 itself. |
| `pv.py:123 blended_block_prices` (consumes the floored margin) | **instance** | Same mechanism, one call site downstream — not a second phenomenon. |
| `optimizer.py:2428` (`pv.import_margin(prices, self.config.pv_export_price)`) | **instance** | Same mechanism, production call site. |
| `pv.py:68 irradiance` clip | **not applicable** | Irradiance is a genuinely non-negative physical quantity; not a price margin. |
| `optimizer.py:2465,2819,3160,3205,3350,5186,5187` (`surplus`, `external_heat_kw`, `price_sigma`, `min_temp_margins`, deficit, `space_demand`, `headroom` clips) | **not applicable** | Each clips a non-negative physical or deficit quantity (energy, temperature margin, headroom), not a *signed price margin* whose piecewise identity assumes both signs. |

## Count

N = 1 verified finding (D2-s3-02, weakened(low)) + 0 additional sweep-confirmed instances (the
widened grep found no second price-margin floor; every other clip in the pricing path floors a
genuinely non-negative quantity). **rca = false** (N=1 < 3, not a ledger class, not barriered).

## Barrier proposal

None proposed at N=1 — too small to justify a permanent gate check; note the mechanism in
`tools/audit/bugclasses.json` as a candidate class if `import_margin`'s floor recurs elsewhere
after a fix.
