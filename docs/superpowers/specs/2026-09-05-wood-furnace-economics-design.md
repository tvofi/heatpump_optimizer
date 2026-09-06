# Wood furnace economics (config, sensor, card, what-if)

Approved design, 2026-09-05. Advisory wood-vs-heat-pump price, a binary
sensor, a Plan-tab alert, what-if wood slots, and a Wood lane for detected
fires. The live solver does not choose wood.

Part of #201. Issue **#463**. Programme seats: **3L-G8** then **3L-G9** (see Seat).

## Goal

Tell the user when burning configured firewood is cheaper than a remaining
planned heat-pump hour, let them simulate a fire in the what-if, and draw
detected external heat as its own slot type. Lighting a fire stays a human
decision.

## Non-goals

- The live optimizer scheduling or injecting wood. `optimize()` is unchanged.
- A fire-history Store or booked past fires.
- Capacity tariff in the comparison.
- Changing detection physics (`external_heat.py` laws stay).
- Re-recording value-bearing goldens. `claims-for:` stays `6.3.14`.
- `VERSION`, manifest version, or `RELEASE_NOTES.md` heading.
- Merging ahead of W3-G3.

## Architecture

New `custom_components/heatpump_optimizer/wood_fuel.py` owns densities,
packing, efficiency, `wood_sek_per_kwh`, and `wood_cheaper`. It does not
detect fires and does not run the solver.

Coordinator publishes `data["wood_fuel"]`. A new binary sensor mirrors
`cheaper` / `ready`. What-if overrides never write the config entry. Card
Plan tab reads `data.wood_fuel` (same bit as the sensor).

## Fuel math

Gross kWh per billed m³, air-dry, before furnace efficiency. Loose is
`0.60 × packed` (stjälpt vs travad).

| Type | Packed | Loose |
|---|---:|---:|
| Birch | 1900 | 1140 |
| Pine | 1500 | 900 |
| Mixed | 1700 | 1020 |

```
useful_kwh_m3 = table[type][packing] × efficiency / 100
wood_sek_per_kwh = price_sek_m3 / useful_kwh_m3
```

A remaining plan hour counts if space or DHW **electrical** power > 0.05 kW
(same threshold as `active_now`). Use the plan’s `space_power` / `dhw_power`
series only — not a separate immersion series. That hour is cheaper as wood when

```
wood_sek_per_kwh < plan_price[i] / COP(outdoor[i])
```

`plan_price[i]` is the series the plan already used (spot + DSO grid fee).
`COP` is `thermal_model.compute_cop` at that hour’s outdoor temperature
(same function as `CurrentCOPSensor`). The sensor is on if any remaining
counted hour is cheaper.

What-if liters are `0.001 m³` of the selected packing:

```
kWh = liters / 1000 × useful_kwh_m3
kW  = kWh / slot_hours
```

## Config

New `wood_furnace_enabled` on the Building options page, default **off**.
Off hides the whole wood block: tank volume, top/bottom probes, DHW wood
coil, external-heat detection, flue entity, min-rise, decay, wood type,
packing, SEK/m³, efficiency. Detection **moves** here from Learning — do
not leave a second copy on that page.

Off means unused, not deleted. Stored keys stay. The model is one-tank:
no 500 L default, `wood_tank_configured` false, detection off, sensor
unavailable.

If `wood_furnace_enabled` is absent (existing entries): infer **on** only
when any of these is already set — `wood_tank_top_entity`,
`wood_tank_bottom_entity`, `dhw_wood_coil_enabled` true,
`external_heat_detection_enabled` true, or `external_heat_entity`. A lone
`wood_tank_volume` (including the old 500 L default) does not infer on.

When the toggle is first turned on: type `mixed`, packing `packed`,
efficiency `75`, price empty. Volume default 500 L applies only while the
toggle is on. Efficiency slider 10–95 %.

Keys:

- `wood_furnace_enabled` (bool)
- `wood_type` (`birch` | `pine` | `mixed`)
- `wood_packing` (`packed` | `loose`)
- `wood_price_sek_m3` (float)
- `wood_furnace_efficiency` (float, percent)

## Sensor readiness

`wood_fuel.ready` is true only when all of these hold:

1. Wood-furnace toggle on (explicit or inferred).
2. At least one wood-tank probe set.
3. External-heat detection enabled **or** DHW wood coil enabled.
4. Type and packing set, `wood_price_sek_m3 > 0`, efficiency in 10–95.

Otherwise the binary sensor is `unavailable` (`available` false). No silent
defaults for price.

New `WoodCheaperBinarySensor` in `binary_sensor.py`:

- unique key `wood_cheaper`, translation key `wood_cheaper`
- object id `binary_sensor.heat_pump_optimizer_wood_cheaper`
- no device class (on means “wood is cheaper”, not heat present)
- `is_on` = `data["wood_fuel"]["cheaper"]` when ready
- attributes: `sek_per_kwh`, `cheaper_hour_count`

Always created. Unavailable until ready.

## Publish

`data["wood_fuel"]`:

```
ready: bool
cheaper: bool   # false when not ready
show_whatif: bool   # wood_furnace_on(config)
sek_per_kwh: float | null
type: str | null
packing: str | null
efficiency: float | null
price_sek_m3: float | null
slots: [{start, end, source: "detected"}]
```

`slots` is the live detector window: while `external_heat.suppressing`, plus
the remaining `forecast_free_heat` fade, capped by
`EXTERNAL_HEAT_FORECAST_MAX_HOURS`. Empty when not suppressing.

Do not put these fields on a plan sensor. Claim new `data[]` key paths
against `origin/main`.

## Card

Plan tab. Banner above the chart while `data.wood_fuel.cheaper` is true.
Not dismissible; it tracks the flag. Keys (en + sv): `wood.alert`.

Third lane, Wood, under the existing space and DHW lanes. Live slots from
`data.wood_fuel.slots`. Observational only — not pinable, not written by
`apply_manual_plan`. Keys: `slots.lane_wood`, `series.wood_slots`,
`menu.add_slot_wood` (what-if only).

Legend: wood chip on the Plan tab only.

## What-if

Shown only when the wood-furnace toggle is on. Add slots `{start, end, liters}`.
Optional overrides: type, packing, price, efficiency. Overrides live in the
what-if draft only; they never write the config entry.

Each slot becomes `external_heat_kw` on the **shadow** solve for those
hours (`kW = (liters/1000 × useful_kwh_m3) / hours`). Live
`_await_optimize` / `optimize()` do not see them.

SEK result = (shadow electricity − live plan electricity) + wood SEK for
the liters (price × liters/1000). Liters ≤ 0 or hours ≤ 0 is refused.

What-if wood slots draw on the Wood lane for that simulation only.

## Tests

- `wood_fuel.py`: table values; SEK/kWh for one known triple; cheaper-hour
  rule (one hour above 0.05 kW cheaper → true; idle-only plan → false).
  Mutation: delete the comparison, the cheaper check fails.
- Config: toggle off hides the wood block; infer-on from a probe; 500 L
  alone does not infer on; volume default unused while toggle off.
- Sensor: not ready → unavailable; ready and one cheaper hour → on; ready
  and none → off.
- What-if: injects `external_heat_kw` on the shadow path; SEK adds wood;
  overrides do not persist. Mutation: `cp` coordinator, restore md5.
- Card: banner when `cheaper`; Wood lane renders a detected slot.

`cp` backups for mutation. Gate lock if select is `MODE: FULL` or names
`tests/stress.py`. No `SOLVE_BUDGET_RATIO` raise. Pay `coordinator_loc` or
stop and ask; do not raise without the owner.

## Seat

After **3L-G7 (#460)**, before Wave 4 (principle 3: config and coordinator
behaviour before `#223` / `#193` moves). Do not merge ahead of W3-G3.

| group | model | after | scope |
|---|---|---|---|
| **3L-G8** | Grok 4.6 extra high | 3L-G7 | Toggle, migration, `wood_fuel.py`, coordinator publish, binary sensor |
| **3L-G9** | Grok 4.6 extra high | 3L-G8 | Plan banner, Wood lane, what-if slots and overrides |

Issue **#463** is filed. G8 leaves it open. **G9** has `Closes #463` on
its own line. Do not reuse #457 or #460.
