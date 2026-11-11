# Class sweep: N-staleness (round 10, PLAN phase D)

Class: a staleness limit is shorter than the legitimate quiet interval of a
source that reports only on change, so a valid unchanged reading is declared
stale or unavailable. `bugclasses.json` status: `open`, no detector, no barrier.
Finding swept: D14-s3-02 (power stale on 39 of 48 cycles, mode on 47, polling arm 0).
Tree: `handoff/audit-r10-register` at 9355f107d.

## Enumerator (D14 method step 3)
`python3 dev/audit/rounds/round10/D14/sweep-N-staleness/enumerate.py` is static (AST),
so it runs on any tree. Seam rule: every finite age limit applied to an entity read.
That covers every key of `const.INPUT_MAX_AGE_MINUTES` (the dict literal plus the
later subscript assigns) and every module-level `*_MAX_AGE_MINUTES`. A seam is
flagged when its limit is below the declared quiet interval of that source under
report-on-change. The `QUIET` table in the harness holds those intervals:
infinite where the value can hold indefinitely, 360 min for the quiet stores.
The table is the judgement input. Output: `enumerate.out`, **29 seams, 20 flagged**.

Controls (`--controls`, all pass, `RESULT controls_ok=True`):
- Positive: at HEAD it re-finds both D14-s3-02 seams (power, mode). It also
  re-finds R9 D1-s5-51 when the pre-fix indoor limit of 60 is restored. The s3
  replay detector could not re-find that one, because its fixture had no quiet gap.
- Null: a clean fixture const (indoor at 360, outdoor 180, house power 30) flags 0.
- Perturbation: appending the one line `INPUT_MAX_AGE_MINUTES[CONF_HOUSE_POWER_ENTITY] = 3.0`
  moves the count from 0 to 1.

Limit: the detector is only as good as the `QUIET` table. A new key that is
missing from the table is flagged as `unknown`, so it fails visible.

## Disposition of every flagged seam (method step 4)
Instance probe: `PYTHONPATH=tests/hastub python3 .../probe.py <KEY>`. It holds an
unchanged reading for limit+1 min through the real `InputReader`, which is inside
the quiet interval, and exits 1 when production calls it stale (`probe.out`).

| seam | limit / quiet (min) | disposition |
|---|---|---|
| CONF_POWER_ENTITY | 30 / inf | **instance**, finding site D14-s3-02, probe rc=1 |
| CONF_HEAT_PUMP_MODE_ENTITY | 60 / inf | **instance**, finding site D14-s3-02, probe rc=1 |
| CONF_ENERGY_ENTITY | 180 / inf | **instance**: the kWh counter holds while the pump idles more than 3 h, so `_measured_energy` becomes None. Probe rc=1 |
| CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY | 30 / 120 | **instance**: MQTT-push water temperature during an idle spell. Probe rc=1; downstream effect not measured |
| CONF_HEAT_PUMP_RETURN_TEMP_ENTITY | 30 / 120 | **instance**, same as supply. Probe rc=1 |
| CONF_FLOW_METER_ENTITY | 30 / inf | **instance**: flow holds 0 while the circulator is off. Probe rc=1 |
| coordinator.HUMIDITY_MAX_AGE_MINUTES | 120 / 240 | **instance**: indoor RH holds inside the report threshold for hours, so the mold floor drops. Probe rc=1 (constant probe) |
| MODE_LAST_GOOD_MAX_AGE_MINUTES | 180 / inf | not applicable as its own seam: it acts only after the mode reading is already stale, so it is part of the mode instance |
| CONF_HEAT_PUMP_FAULT/DEFROST/ONLINE/BACKUP_HEATER/DHW_BOOSTER/CAPACITY_LIMITED (6) | 30–60 / inf | **guarded**: `pump_signals.py` says staleness "demotes a signal to silence". The quiet value (off / no fault) equals the no-evidence default, so nothing changes |
| CONF_VALVE_OUTLET_TEMP, WOOD_TANK_TOP, WOOD_TANK_BOTTOM, EXTERNAL_HEAT (numeric) | 60 / inf | **guarded**: a stale reading means no free heat, which is the fail-safe direction documented at `const.py` 1471-1486. The external-heat flag case is read UNBOUNDED |
| CONF_SOLAR_RADIATION_ENTITY | 90 / inf | **guarded**: the reading is quiet only at night (0 W/m²). Open-Meteo observed irradiance takes over (`coordinator.py` ~6076), and with no Open-Meteo the last value, about 0, is kept |
| CONF_PV_PRODUCTION_ENTITY | 30 / inf | not applicable: no read site applies the limit. `_pv_measured_production` reads the raw state with no age gate. A missing staleness check belongs to class P6, not this one |

Unflagged seams (9): indoor, dhw, floor return, lower floor and buffer (360 = quiet store),
outdoor 180, house power 30, DHW inlet 1440, Open-Meteo observed 90 (an HTTP
payload, not an entity).

Instances: 7 seams. 2 are the judged finding sites and **5 are beyond the finding**.

## Proposed barrier
Move `QUIET` into `const.py`, next to `INPUT_MAX_AGE_MINUTES`, as a per-key
declared quiet interval. Then make the enumerator a `tests/` check that refuses
any key with limit < quiet unless the key is on a named-guard allow-list
(pump_signals silence demotion, the fail-safe free-heat probes). It is static,
so it costs under 1 s of gate time. For power and mode, add the s3 report's
replay `on_change` arm as the dynamic complement.
