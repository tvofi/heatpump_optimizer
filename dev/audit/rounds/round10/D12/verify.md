# D12 verify, round 10 (single verifier, lenses V1-V3)

Worktree: detached at handoff/audit-r10-register 9355f107d. load1 7.6-9.1 during runs, thread_factor 1.000 (no timing claims made).

## D12-s3-01 -- climate set-point written in degC on a degF instance: VERIFY, high
- V1: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D12/s3/surface_units.py` -> misdelivered_cells=2 of 6 (degF; climate space 21 -> -6.11 degC, DHW 50 -> 10.0 degC); null (degC arm) 0 of 6; `--perturb` -> 0 of 6. Moves as stated.
- V2: own sweep `verify-harness/s3_climate_sweep.py` (climate entity, intents 5/21/35/50/60 degC, both unit systems, delivered payload read back via inputs.temperature_c in the instance unit): 5 of 5 degF cells off by >0.5 degC (sent value == degC intent), 0 of 5 degC cells.
- V3: reachable in real HA: a climate state carries no unit_of_measurement, and climate.set_temperature takes the instance unit. pump_arbiter.py:845 is the seam; setpoint_check._setpoint_and_unit (read path) already falls back to hass.config.units. Severity high: DHW commanded to ~10 degC / space to ~-6 degC on any degF install using a climate surface. Class: P8 (unit resolved by divergent precedence on different surfaces), not new. Seam rule (grep temperature_from_c) enumerates conversion sites (2) but not set-point writes that bypass conversion (repairs._write_setpoint callers, repairs.py:53, which is fed already-converted values) -- partial.

## D12-s2-71 -- lower-floor ratio unanchored on options edit: VERIFY (mechanism), medium
- V1: `reparam_sites.py` (s=1.567, r=1.922): options_reseed_both_zones house_rel_err 0.0011, upper 0.3681, lower 0.2145; snapshot restore lower 0.2145. Perturbation `--ratio 1.0` -> 0.0000 all rows; null `--scale 1.0 --ratio 1.0` -> 0.0000. Upper-only edit -> 0.
- V2: own metric = lower-zone rel err vs ratio sweep: r=1.2 0.0873, 1.5 0.1659, 1.922 0.2145, 2.5 0.2288; monotone, zero at r=1. The scale re-anchor (_reanchor_house_heat_loss_scale) restores the total; the ratio is kept verbatim over a nameplate that already contains it, so the zone split is wrong. Correction to the claim's wording: the lower zone is not r x learned (that would be 521 W/K) -- the total is preserved and the split is skewed (lower +21 %, upper -37 %).
- V3: reachable: CONF_LOWER_FLOOR_HEAT_LOSS is an options-flow field (config_flow.py:1722). Class P2 (one fact -- nameplate change -- anchored at the scale seam, missed at the sibling ratio seam). Seam rule: none stated in a form I could run; harness covers options load and snapshot restore only -- demonstrated seams only.
