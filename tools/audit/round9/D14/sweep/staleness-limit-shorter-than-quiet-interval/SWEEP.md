# Class sweep — "staleness limit shorter than a report-on-change sensor's quiet interval"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D1-s5-51** (verified, medium — Indoor Temperature (`CONF_INDOOR_TEMP_ENTITY`,
`INPUT_MAX_AGE_MINUTES`=60) is a report-on-change thermometer: HA does not re-write its state
while the value is unchanged. Silent for more than 60 minutes with an unchanged, still-valid
reading, `IndoorTempSensor.available` goes `False` (`InputReader._age_gate` reads the entity's
age against the 60-minute limit, not whether HA still considers the value current). The finder's
harness (`tools/audit/round9/D1/leads/indoor_silence.py`), re-run here, reproduces
`unavailable=4 of 7` at the silence cells 61/90/240/480 min, exactly at baseline; the re-report
arm (`rereport_unavailable=0 of 1`) confirms `InputReader` does honour `last_reported` when HA
supplies it — the gap is only when the source integration never re-reports at all).

## Enumerator

`tools/audit/round9/D14/sweep/staleness-limit-shorter-than-quiet-interval/enumerate.sh`: lists
every `INPUT_MAX_AGE_MINUTES[...]` keyed limit and every `sensor.py` entity whose availability
follows the same `_reading_key`/age-gate mechanism as `IndoorTempSensor`, then re-runs the
finder's harness as the positive control.

Positive control: `unavailable=4 of 7` reproduces the finding's own `Expected` line exactly.
Null control: the 5/30/59-minute silence cells (`silent_5min`, `silent_30min`, `silent_59min`)
all read `available=1` — the gate does not false-positive under the limit.
Perturbation: `--scale 8` (the shipped `staleness_max_age_scale` option at its ceiling) or
`--no-watchdog` (`staleness_watchdog_enabled` off) reduce or zero `unavailable` — documented in
the harness header (both are existing user-facing mitigations, not a code fix).

## Disposition

| seam | disposition | note |
|---|---|---|
| `IndoorTempSensor` / `upper_floor_temperature` (`CONF_INDOOR_TEMP_ENTITY`, 60 min) | **instance** | D1-s5-51 itself — reproduced by the harness. |
| `slab_temperature`, `lower_floor_temperature`, `floor_return_temperature`, `buffer_tank_temperature`, `dhw_temperature` (×2 sensors) — all `_reading_key`-gated temperature entities on the same 60-minute-class limits (`CONF_DHW_TEMP_ENTITY`, `CONF_FLOOR_RETURN_TEMP_ENTITY`=60; `CONF_BUFFER_TANK_TEMP_ENTITY`, `CONF_LOWER_FLOOR_TEMP_ENTITY`=60) | **instance** | Same mechanism, same `_age_gate`/`_reading_ok` function, same class of report-on-change temperature entity — not a second finding, the same underlying gate applied to every temperature reading key. |
| `CONF_HEAT_PUMP_ONLINE_ENTITY` (30 min) | **guarded** | `const.py`'s own comment explicitly reasons about this entity's reporting behaviour: it is written on every poll cycle by the source integration (not report-on-change), so an old reading genuinely means the source has gone silent. |
| `CONF_OUTDOOR_TEMP_ENTITY` (180 min), `CONF_SOLAR_RADIATION_ENTITY` (90 min), `CONF_ENERGY_ENTITY` (180 min), `CONF_HEAT_PUMP_MODE_ENTITY`/`FAULT_ENTITY` (60 min, `MODE_LAST_GOOD_MAX_AGE_MINUTES`=180 min separately) | **not applicable** | Each carries its own deliberate, generous-horizon justification in `const.py`'s comments addressing exactly this kind of slow-moving/report-on-change signal (e.g. mode's 180-minute `MODE_LAST_GOOD` fallback horizon is explicitly sized against "a cooling mode read six hours ago"). |
| `CONF_HEAT_PUMP_DEFROST_ENTITY`, `BACKUP_HEATER_ENTITY`, `DHW_BOOSTER_ENTITY`, `CAPACITY_LIMITED_ENTITY`, `SUPPLY_TEMP_ENTITY`, `RETURN_TEMP_ENTITY`, `PV_PRODUCTION_ENTITY`, `POWER_ENTITY`, `HOUSE_POWER_ENTITY` (30 min) | **not applicable** | `const.py`'s comments justify these limits as *fast-moving* signals ("what the machine is doing RIGHT NOW"), the opposite regime from the report-on-change/quiet-interval mechanism this class targets — a short limit is the deliberate design for a fast signal, not an instance of the mismatch. |

## Count

N = 1 verified finding (D1-s5-51, covering the whole family of `_reading_key`-gated temperature
entities sharing the same age-gate mechanism as one finding) + 0 additional sweep-confirmed
instances beyond that family. **rca = false** (N=1 < 3, not a ledger class, not barriered) —
matches the class table's precomputed N=1/rca=no.

## Barrier proposal

None proposed at N=1: the fix (distinguish "entity age" from "entity value staleness" for
report-on-change sources, e.g. honouring `last_reported` the way the re-report arm already shows
`InputReader` can) is a design decision for the fixer, not a structural gate.
