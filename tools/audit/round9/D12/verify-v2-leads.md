Evidence tree for this unit: handoff/audit-r9-evidence at 96b89163 (the finders' leads harnesses live there, not on this branch). Box G2-V2, verifier V2.

# D12-s3-81 verify-v2 (leads unit)

Finder harness re-run: `tools/audit/round9/D12/leads/l4_fee_bound.py` at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Baseline: `blocked_verdicts=8 count`, `blocked_currencies=4 of 12 (HUF,ISK,JPY,KRW)`, `null_blocked=0 of 4` (exact match). load1=0.36, thread_factor=1.000. `--perturb` (`IMPLAUSIBLE_FEE_SEK_PER_KWH` 10->1e6): `blocked_verdicts=4 count`, `blocked_currencies` unchanged at 4 of 12 (exact match to expected_direction=down, observed_value=4 -- seam (b), the selector max, is independent of this constant and correctly stays).

Own harness (V2, independent instrument): `tools/audit/round9/D12/verify-v2-leads/v2_fee_bound.py`. Different fee assumption (0.04 EUR/kWh vs. the finder's 0.05) and an independently-rounded FX table over 8 currencies (drops GBP/CHF/PLN/CZK, keeps the null arm and the 4 flagged currencies). Result: `blocked_currencies=4 of 8 (HUF,ISK,JPY,KRW)`, `null_blocked=0 of 4`. Leave-one-out over that 8-currency grid: `loo_min=3 loo_max=4` -- dropping any single currency (including HUF or KRW) still leaves at least 3 blocked, so the effect is not a single favourable cell. load1=0.16, thread_factor=1.000.

Source check: `grid_fee.py:70` `IMPLAUSIBLE_FEE_SEK_PER_KWH = 10.0`, compared with no currency conversion at `grid_fee.py:240` (`rule.rate > IMPLAUSIBLE_FEE_SEK_PER_KWH`). `config_flow.py:1720`: `_number(0, 5, 0.01, f'{resolve_currency(hass)}/kWh')` -- the numeric bound (0, 5) is a literal, only the unit label follows currency. Both confirm the finder's `mechanism` at the source, independent of the harness.

Attacks:
- Contention: load1 0.12-0.36, thread_factor 1.000 both harnesses.
- Gate mode: n/a.
- Grid artefact: leave-one-out (absent from the finder's harness; run here) shows the aggregate survives dropping any one currency -- not an artefact of a single cell.
- Null control: finder's `null_blocked=0 of 4` reproduced exact; independently reproduced at a different fee/FX table (0 of 4).
- Reachability: the `NumberSelector` max is enforced by the real HA frontend, and `_audit_grid_fee`'s issue creation is the genuine repair-issue path (`_create_issue`), not a stub-only artifact.
- Severity: kept at the finder's `medium` -- an ordinary fee becomes unenterable or under-reported in 4 of 12 (finder's set) / 4 of 8 (mine) currencies; workaround is manual currency conversion by the installer, so not `critical`.

Vote: **verify**, severity `medium`.
