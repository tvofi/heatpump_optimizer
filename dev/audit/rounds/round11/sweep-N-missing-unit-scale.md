# Class sweep: N-missing-unit-scale (round 11, PLAN phase D)

Class: a declared unit is recognised but its scale factor is never applied, so
the value reaches the plan off by that factor. Finding: D2-s3-02 (critical,
`inputs.normalize_price_per_kwh`, minor currency units). `bugclasses.json` has
no entry for this class at `handoff/audit-r11-register` (28b864af6d); the
nearest one is `P8`.

## Enumerator

`dev/audit/rounds/round11/D14/N-missing-unit-scale/enumerate.py`, run as
`HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 <it> [--root DIR] [--perturb F]`.

The script works in two steps. The first is static: it finds every function in
`custom_components/heatpump_optimizer/*.py` that reads a unit table. A unit
table is a module-level name containing `UNIT` with `_TO_` or ending `_UNITS`,
or one of the `PRICE_ENERGY_TO_KWH` / `PRICE_MINOR_UNITS` /
`PRICE_MAJOR_SYMBOLS` names. The finding's seam rule
(`grep PRICE_MINOR_UNITS`) is a subset of this search. The second step is
dynamic: it runs every public normaliser over every spelling in its table and
compares the output to `value * factor`, where a minor currency unit counts as
a hundredth. The count it reports is `scale_mismatches`.

| control | command | result |
|---|---|---|
| clean tree (null) | no flags | seams=10, scale_mismatches=0 |
| positive (planted copy of D2-s3-02: `/ 100.0` deleted) | `--root <copy>` | scale_mismatches=30 (10 minor spellings x 3 energies) |
| perturbation, one line, price | `--perturb minor` | 0 -> 30 |
| perturbation, energy / power / flow | `--perturb energy|power|flow` | 0 -> 2 / 3 / 7 |

The finder's own harness (`D2/s3/m4_tariff.py --section cur`) prints
`unit_mismatches=0` on this tree. Its finding value came from a planted copy.
The `/ 100.0` is present here and at the finding's baseline 92d38ecb
(`inputs.py:791-792`).

## Seams and disposition

| seam | disposition |
|---|---|
| `inputs.py:780 normalize_price_per_kwh` (the D2-s3-02 site) | guarded: the minor branch applies `/ 100.0` (line 799). The `_P8_FACTORS` check in `tests/features.py` pins öre/kWh and c/kWh at 0.01. The probe passes, so this is not an instance at this head |
| `inputs.py:334 normalize_power_kw` | guarded: it returns `value * factor` and refuses unknown units; the probe is exact for all 4 spellings |
| `inputs.py:351 normalize_flow_kg_s` | guarded: same shape; exact for all 8 spellings |
| `inputs.py:363 normalize_temperature_c` | guarded: it applies offset and factor; exact for all 7 spellings |
| `inputs.py:381 normalize_energy_kwh` | guarded: exact for all 3 spellings |
| `inputs.py:443 temperature_from_c` | guarded: it inverts the table's own (offset, factor) pair |
| `inputs.py:526 read_temperature_delta_k` | guarded: it applies the factor only (a delta) and treats an unknown unit as no reading |
| `inputs.py:818 _value_in_model_units` | not applicable: a power unit is recognised here only to skip the debug line. It is adopted raw by design, because every power slot (`CONF_POWER_ENTITY`, `CONF_HOUSE_POWER_ENTITY`, `CONF_THERMAL_POWER_ENTITY`) reads through `read_power_kw`, and no generic `.read(` slot is a power slot (all 20 call sites were enumerated) |
| `coordinator.py:2931 _wind_speed_scale_of` | guarded: the scale is multiplied into every row (`coordinator.py:2961`) |
| `coordinator.py:2936 _forecast_in_model_units` | guarded: temperature, wind and rain are each applied per row (2958-2964) |

The price consumers `_entity_price` and `price_per_kwh` (export price, grid fee
entity) and `prices_from_entity_attributes` all go through
`normalize_price_per_kwh`, so they inherit its guard.

**Instances: 0** (beyond the finding: 0). The judged site does not reproduce at
this head.

## Barrier

The class is only partly barriered. The `_P8_FACTORS` check in
`tests/features.py` covers the price seam. Nothing pins the power, flow and
energy tables against their normalisers. Proposed barrier: promote the dynamic
half of `enumerate.py` into `tests/` (a table-driven check of each normaliser,
under a second of gate time). This goes to the round-end proposal triage and
is not built mid-round.
