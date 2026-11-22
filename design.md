# R11-OWNER-FLOWCAP: a manual high limit for the space water set-point

Owner ruling (tvofi, 2026-11-22): "Flow cap: add an option to manually configure the high-limit if there is no such sensor."

## Problem

An integration can advertise a set-point maximum above what the device accepts. The reported case is a number entity advertising 65 for a device that takes 62. The arbiter honours the advertised maximum: a space boost writes it (`pump_arbiter._boost_ceiling_c`), and from the clamp handoff `handoff/r11-owner-flowcap` on, every write is held inside it (`inputs.write_setpoint`). So a device limit below the advertised one is honoured today only through the optional sensor `space_setpoint_high_limit_entity`, and an install without such a sensor has no way to state it.

## Option

- Key: `space_setpoint_high_limit_c`, a new `CONF_SPACE_SETPOINT_HIGH_LIMIT_C` in `const.py`, beside `CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY`.
- Type: an optional number in °C, in the set-point entity's own terms (supply or return, the same as `flow_heat_c`). The selector is `_number(30, FLOW_HEAT_C_MAX, 0.5, '°C')`.
- Bounds: 30 to `FLOW_HEAT_C_MAX` (70). The floor matches `flow_heat_c`'s, which sits above the 25 °C flow gate: a limit at the gate would leave no heating value. A stored value outside the bounds, or one that is not a number, reads as unset at runtime (`finite_float`, then the range test). The options flow never offers such a value.
- Default: none. The row is `_STORED`, so an untouched page stores nothing and the entry is unchanged (`tests/config_flow_steps.py`'s untouched-page proof). No existing row pairs `_STORED` with `_number`; the fixer adds a `config_flow_steps` case proving that a cleared value stays cleared.
- Placement: the `entities` step, group `indoor`, `when=_water_space_setpoint`, directly after `CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY`.
- Read: through `EntryConfig` (`entry_config.py`) only, never from `entry.options` below the glue (`fixer.md` step 17).

## Precedence: the effective high limit

One pure function owns it in `pump_arbiter.py`, next to `_setpoint_limits_c`. Every reader of the upper limit calls it.

1. The high-limit sensor, where it is configured and reads (`_setpoint_limits_c`'s upper value, under its existing validity rules).
2. Otherwise the manual option, where it is set and valid. This includes a configured sensor that is unavailable, so a sensor dropping out never lifts the limit to the advertised maximum.
3. Otherwise none.

The effective maximum is then the lower of this limit and the entity's advertised maximum. The advertised maximum stays a hard cap at `inputs.write_setpoint` (the clamp handoff), so no limit can raise a write above what the entity states.

## Where it binds

These are the readers of the upper limit, all moving to the one function:

- `_boost_ceiling_c`, where it already caps on the sensor;
- `_feedback_bounds`, where the feedback loop already caps on the sensor;
- the space slot's grid (`pump_arbiter._grid` for `space_setpoint`). Its `high_c` becomes the effective maximum, so every `_bounded` space value (heating, gate, hold, adoption) is held under it, with no per-caller clamp.

Writes to other entities do not read the option: DHW set-points, valve, heat curve and frequency. It is the space water set-point's limit, as its sensor is.

When a limit sits at or below the gate it leaves no heating value, so it is ignored with a log line. That is the existing rule for the sensor in `_feedback_bounds` (`v >= lowest`), and it now applies to both sources. The option's 30 °C floor keeps a manual value out of that case.

## UI strings

These go in `strings.json` and the `en`, `sv` and `de` translations, under the `entities` step's `data` and `data_description`:

- data: "Controller's maximum set-point (°C, optional)"
- data_description: "Optional. The highest value the controller accepts for the set-point entity above, where its own maximum is higher than what the pump takes. No set-point above it is written, a boost's included. A maximum set-point sensor, where configured and reading, is used instead. Left empty, the entity's own maximum applies."

The existing `space_setpoint_high_limit_entity` description says "Used by that option alone". That is already untrue, because the boost reads the sensor too. It is corrected to say what the sensor caps: the feedback loop, a boost, and every space write.

## Migration

None. The key is new and absent on every existing entry, and absent means no manual limit, so behaviour is unchanged. The entry version does not move.

## Tests the fixer owes

- Precedence, on synthetic entities: sensor reading 60 with the option at 62 gives 60; the sensor unavailable with the option at 62 gives 62; neither gives the entity maximum; an option above the entity maximum gives the entity maximum.
- Each reader, against its own mutant: a boost writes the effective maximum; a band-top heating step whose ceiling sits above it is held at it; the feedback loop stays under it.
- Null controls: the option unset changes no write on any existing fixture, a limit at the gate is ignored, and an untouched options page stores nothing.

## Alternatives considered

- Reusing `flow_heat_c` as the cap: refused. It is also the full-power ceiling of the level map, so a value of 62 raises every partial-level flow above today's 55.
- Inferring the device ceiling from readback by generalising `_clamp_cut`: refused. A refused write and a clamped write read the same, and the first would learn the previous value as the ceiling.
- Clamping per caller: refused. The one space grid is the arbiter's seam, and the entity range already binds at `inputs.write_setpoint`.

## Size

About 60 production lines: const, entry_config, config_flow row, the limit function and three reader edits. That excludes strings and translations, plus tests.
