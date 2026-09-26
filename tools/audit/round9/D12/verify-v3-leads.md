# D12 leads, verifier V3 (reach and class), round 9

Box G2-V3, lens V3 (reach and class), leads unit. Read at evidence 96b89163 (leads harnesses under `tools/audit/round9/<dim>/leads/`); own harnesses under `verify-v3/leads/` here. Real HA: core 2026.2.3 on CPython 3.14.0rc2, numpy/scipy from the gate venv; shims: stand-in `typing.ByteString` ABC before importing HA, `http` marked loaded.

## D12-s3-81 — Grid-fee bounds are SEK numbers: 0.05 EUR/kWh unenterable in HUF, ISK, JPY and KRW

**Step 1.** `l4_fee_bound.py`: `blocked_verdicts=8`, `blocked_currencies=4 of 12` (HUF, ISK, JPY, KRW), `rules_refused=2`, `fixed_over_selector_max=4`, `repair_raised=2`, `null_blocked=0 of 4`. thread_factor 1.000, load1 2.11. Exact.

**Step 2 / reach, real HA.** `realha_fee_currency.py`: real options flow (init → advanced → grid_fees by real menu `async_configure`) with `hass.config.currency` per currency; posts validated by the page's real `vol.Schema`/`NumberSelector`.
- HUF/ISK/JPY/KRW at the lead's FX table, 0.05 EUR/kWh: `real_rules_refused=2 of 8` (HUF, KRW), `real_fixed_selector_invalid=4 of 8` (a genuine `vol.Invalid` on submit), `real_blocked_currencies=4`, `real_null_blocked=0 of 4` (SEK/EUR/NOK/DKK).
- Perturbation (`IMPLAUSIBLE_FEE_SEK_PER_KWH` 10 → 1e6 in memory): rules refused 0 of 8; fixed selector unchanged at 4 of 8 (independent `max=5`), as the lead predicted. load1 0.75–0.86.
- A first harness version called `async_step_grid_fees()` directly, leaving `cur_step` unadvanced; fixed by driving the real menu. A harness bug, not a product defect.

**Attacks.** Contention: counts. Gate mode: n/a. Grid: per-currency, additive. Null control: 0 of 4 on both engines. Reachability: real and strengthened — the fixed-fee refusal is a real submit-time rejection.

**Severity:** medium confirmed (a hard configuration wall in 4 of 12 modelled currencies; no mispricing). A case for higher is left to the judge.

**Seam rule.** 8 hits covering grid_fee.py's constant and `spec_problem`, config_flow.py's two `fee_bound` reads and the `grid_fee_fixed` selector, coordinator.py's imported copy and repair check. **Partial**: misses `contract_fixed_price`'s sibling selector `_number(0, 10, 0.01, f"{resolve_currency(hass)}/kWh")` (config_flow.py:1723), the same unconverted SEK-sized bound on a second money field, which the literal `5` does not match.

**Class:** P8 confirmed as closest. Mechanism note for the judge: the unit label follows `hass.config.currency` correctly; the magnitude bound is an unconverted SEK constant — a currency-unaware bound beside a currency-aware label rather than divergent precedence.

**Vote: verify, medium.**
