# Class sweep — P8: "A currency or unit resolved by divergent precedence on different surfaces"

Ledger: `tools/audit/bugclasses.json`#P8, status `open`, 7 historical rounds (R1 D4-04, R2
D2-02, R4 D12-01/D2-04/D6-02, R5 D12-01, R7 D4-03), detector never recorded.

Round-9 findings in this class: **D12-s3-81** (verified, medium — the fixed
`IMPLAUSIBLE_FEE_SEK_PER_KWH` bound is compared against a fee whose currency may not be SEK)
and **D14-s2-02** (verified, medium — three seam families: A the price feed's declared money
code is parsed for scale and dropped, coordinator/sensor read the once-resolved
`coordinator.currency` instead; B config-flow money widgets mostly resolve through
`resolve_currency(hass)` except the firewood widget, hard-coded `SEK/m³`; C the card's
`currency()`/`savingsUnit()` let a card-config value or the sensor's own unit lead ahead of
`hass.config.currency`).

## Enumerator

`tools/audit/round9/D14/sweep/P8/enumerate.sh` — reuses the finder's own class detector
(`tools/audit/round9/D14/s2/p8_currency.py --seams`, an AST walk over every `.py` file for
`resolve_currency(...)` calls, unguarded `*.currency` reads, money-shaped string literals, and
unit-parse call sites, plus a scan of `strings.json`/`translations/*.json` and the card's own
currency methods) for families A/B/C, and adds a family D grep for
`IMPLAUSIBLE_FEE_SEK_PER_KWH` (definition + both comparison/formatting sites) for D12-s3-81's
mechanism.

Positive control: the harness's own `--seams` output lists both findings' exact lines
(`config_flow.py:1645` for D14-s2-02's firewood widget, `grid_fee.py:240`/`coordinator.py:6388`
for D12-s3-81's bound comparison). Family A/B/C also carries the finder's executed positive
control (`p8_currency.py` main mode: `A_unflagged_mismatch=8`, `B_money_widgets_off_instance[EUR]=1`,
card distinct-token mismatches) — not re-run here (D3/heavy-rerun rule does not apply, this is a
cheap in-repo script, but the sweep's job is enumeration/disposition, not re-verification of
numbers the judge already accepted).
Null control: on a fixture where every money surface reads through
`resolve_currency(hass)`/`coordinator.currency` and no literal currency code or hard-coded bound
appears, the enumerator returns 0 `instance`-dispositioned sites (see disposition below — the
"frozen at setup" and "`resolve_currency(hass)`" sites themselves are the *correct* pattern and
are dispositioned `guarded`/`not applicable`, not `instance`).
Perturbation: reintroducing a one-line literal (`unit_of_measurement="SEK/kWh"` in place of a
`resolve_currency` call) makes the enumerator's AST walk pick up a new money-shaped string
literal seam — moves under the one-line change.

## Disposition (42 family-A/B/C seams + 5 family-D lines)

| seam group | count | disposition | note |
|---|---|---|---|
| `config_flow.py:1645` literal `'SEK/m³'` | 1 | **instance** | D14-s2-02 family B — the only money widget that does not call `resolve_currency`. |
| `coordinator.py:1326`, `:1344`; `inputs.py:328`; `price_model.py:700` — "price unit parsed; money code discarded" | 4 | **instance** | D14-s2-02 family A — the feed's declared ISO code is parsed for scale only; nothing records it, so the coordinator falls back to `hass.config.currency`. |
| `www/heatpump-optimizer-card.js:4481-4496,6844-6867,7439,11034,11380` — `currency()`/`savingsUnit()` precedence chain | 10 | **instance** | D14-s2-02 family C — card-config and sensor-attribute values can outrank `hass.config.currency`. |
| `IMPLAUSIBLE_FEE_SEK_PER_KWH` definition + both comparison/format sites (`grid_fee.py:70,240`; `coordinator.py:6388`; `config_flow.py:3596,3655`) | 5 | **instance** | D12-s3-81 — the bound is a bare SEK figure compared against a fee in the instance's own currency. |
| `resolve_currency(hass) [instance config]` call sites (`config_flow.py:1673,1720,1723,3595,3654`; `coordinator.py:1824,10009`) | 7 | **guarded** | These *are* the canonical resolution function being invoked — the correct precedence, not a second divergent one. |
| `self.currency` / `coordinator.currency` / `self.coordinator.currency` "frozen at setup" reads (`coordinator.py:6403,6430,7141,8648,8663`; `sensor.py:437,460,523,539,558,1221,1473,1578,1825,2198,2750`) | 16 | **guarded** | All read the one value `coordinator.currency` assigned once from `resolve_currency(hass)` in `__init__` — consuming the resolved value, not re-deriving it. |
| `strings.json`/`translations/{en,sv}.json` literal `SEK` in the firewood service-field description | 3 | **not applicable** | Static help text describing a service parameter's unit, not a surface that resolves a currency for a live published value. |

## Count

N = 2 verified findings (D12-s3-81, D14-s2-02) + 0 additional sweep-confirmed instances (every
`instance`-dispositioned seam above restates one of the two findings' own named families; the
sweep found no new family). **rca = false** (N=2 < 3, class not `barriered`).

## Barrier proposal

A `tests/currency_seams.py` structural check: every money-shaped `unit_of_measurement`/widget
unit and every plausibility bound compared against a price must be produced by (or parametrised
on) `resolve_currency(hass)`, checked by grepping for literal 3-letter currency codes and
currency-named constants outside `currency.py` and failing the gate if any exist outside an
allow-list. Estimated gate cost: under 1s (static AST/regex scan, no HA boot). Proposed for
`tests/structure.py`'s metric set (structural ratchet, not a new script) since it is a pure static
count.
