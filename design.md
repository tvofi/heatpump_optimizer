# R11-OWNER-FLOWCAP: a manual high limit for the space water set-point (revision 2)

Owner ruling (tvofi, 2026-11-22): "Flow cap: add an option to manually configure the high-limit if there is no such sensor."

Base: `origin/main` 3a98735a7ecc59e7ecc095a0429cdf6251d956ec. This group is built on the clamp handoff `handoff/r11-owner-flowcap` at 13290409848b92f2df92fe940b1036db6a3627b8, which is on origin.

## Problem

An entity's advertised set-point maximum can sit above the highest value the device accepts. The arbiter honours the advertised maximum: a space boost writes it (`pump_arbiter._boost_ceiling_c`), and the clamp handoff holds every write inside it (`inputs.write_setpoint`). So a device limit below the advertised one is honoured only through the optional sensor `space_setpoint_high_limit_entity`, and an install without such a sensor cannot state it.

## Seam ownership and order (orchestrator ruling, 2026-11-22)

This group lands first, and it owns the entity-range clamp in `inputs.write_setpoint` (the clamp handoff above). R11-SEAM-actuation-writes (design 28bedac8, section 3 "Grid and range") is amended to consume that clamp instead of adding its own. That amendment, and that group's sibling sites, are its own: `coordinator._command_frequency`'s `np.clip` to the entity's frequency range, and `setpoint_check.py`'s DHW Fix value, which is quantised with `quantise_setpoint_c` under the tank's hard maximum. Carry: R11-SEAM-actuation-writes. The orchestrator amends that note, by its own ruling.

## Option

- Key: `space_setpoint_high_limit_c`, a new `CONF_SPACE_SETPOINT_HIGH_LIMIT_C` in `const.py`.
- Type: an optional number in °C, in the set-point entity's own water terms (supply or return, as `flow_heat_c` is). The selector is `_number(30, FLOW_HEAT_C_MAX, 0.5, '°C')`.
- Shown only for a water set-point (`when=_water_space_setpoint`), so an indoor-unit entity never offers it. The runtime reads it only where `_flow_unit` is true (see "Excluded").
- Bounds: 30 to `FLOW_HEAT_C_MAX` (70). The floor matches `flow_heat_c`'s, which sits above the 25 °C flow gate.
- A stored value outside the bounds can reach the form. `_fit_stored_values` widens the schema and shows `stored_value_out_of_range`, and the build pins that path for the new row. At runtime, a value that is not a number, or is outside 30..70, reads as unset.
- Default: none (`_STORED`), so an untouched page stores nothing. The key is classified in `_ABSENT_IS_NOT_DEFAULT` by what `tests/config_flow_steps.py` measures. Unlike the two sensor keys, it is read on every boost and space-grid pass, and the build states the measured class. A case proves that a cleared value stays cleared, because no existing row pairs `_STORED` with `_number`.
- Placement: the `entities` step, group `indoor`, directly after `CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY`. It is read through `EntryConfig` only.

## The effective high limit: one owner

The new module `custom_components/heatpump_optimizer/flow_limit.py` is pure, with no `homeassistant` import. It is the one owner of the space water set-point's upper limit. One function takes, as inputs, the sensor pair's readings, the option's value, the gate floor, and the entity grid's minimum and step. It returns the effective high limit in °C or `None`, plus the reason for any source it dropped, for the log.

The rules, applied in this order:

1. Sources. The sensor's upper reading, where it reads and the pair is not crossed; and the option, where it is set and valid.
2. Both present: the lower of the two (orchestrator ruling 2, relayed to the owner). A sensor reading above the typed limit never lifts it.
3. A crossed sensor pair (lower >= upper) drops both sensor readings, as `_setpoint_limits_c` does today, and the option still applies. A sensor that is configured but unavailable also leaves the option in force.
4. Gate rule, one comparison for both sources. A limit that leaves no heating value, at or below the gate plus one entity step (the feedback loop's `lowest`), is dropped and logged once through `log_held`. Today `_feedback_bounds` uses `>= lowest` and logs nothing, and `_boost_ceiling_c` uses `> gate floor`. Both now call this one rule. The option's 30 °C floor keeps a typed value out of this case, so in practice it bites only a sensor.
5. Entity minimum wins. A limit below the entity's advertised minimum, rounded up onto the entity's step, is raised to that minimum and logged once. This keeps `SetpointGrid.bounded`'s rule that the minimum outranks a ceiling, so the arbiter never records a value under the minimum. If it did, the write clamp would send the minimum, and the arbiter would read its own write back as a person's edit (`_differs`, `_edited`).

The arbiter then caps at the lower of this limit and the entity's advertised maximum. The advertised maximum also stays a hard cap at `inputs.write_setpoint`.

The sensor pair's reads (`SETPOINT_LIMIT_KEYS`, `_setpoint_limits_c`) stay in `pump_arbiter.py`, because they read entities through `InputReader`. They feed the pure function.

## Every consumer the change reaches, and what it does

A second grid accessor carries the limit: `_space_grid`, the entity grid with `high_c` lowered to the effective maximum. `_grid` and `setpoint_grid` keep the advertised range. Each space-set-point consumer is named here with the grid it reads:

| consumer | grid | behaviour |
|---|---|---|
| `_flow_target` heating step (`hi=m.heat_c`) | limited | Moves: no heating write above the limit. |
| `_flow_target` fallback hold | limited | Moves: the hold never sits above the limit. |
| `_map_inputs` heat ceiling (`heat_c`) | limited | Moves: the level map's top is min(heat ceiling, limit), so partial levels slide on the band the pump can take. |
| `_boost_ceiling_c` | limited | Moves: a boost writes min(advertised max, effective limit). Its own sensor and cap reads go to the one function. |
| `_feedback` output and `_feedback_bounds` highs | limited | Moves: the loop's ceiling is the effective limit. It replaces the bare sensor read, so the option binds there too. |
| `_feedback_bounds` `lowest` | limited | Unchanged by rule 4: a kept limit sits above `lowest`. |
| `_gate_c` | limited | Unchanged by rule 4: a kept limit sits above the gate, so the gate rounds down as before. |
| `_flow_command` ceiling and gate (the `draw_range` censoring input) | advertised | Unchanged, deliberately. `FlowCommand.ceiling_c` means the set-point that commands the pump's maximum draw. A write capped below the heating ceiling by a limit does not command that draw, so `draw_range` must not fold it as ceiling evidence or count it as an overdraw. With the advertised grid, a capped write sits below `ceiling_c` and is censored, as any partial write is. Test: with a limit below the heating ceiling, a capped write is not `takes_ceiling` and not `_overdrawn`; the null control is the same write with no limit, which is. |
| `_adopt` baseline | advertised | Unchanged. The value is a person's edit that the device read back, so the device accepted it, and Off restores it as read. |
| `_arm_space` baseline | none | Out of scope. It is the device's own reading, captured raw, so the device accepted it. The PR body says so, so that a reviewer does not count it as a bypass. |

Excluded: the indoor-unit paths (`_flow_unit` false). These are `_space_target`'s room path (`_bounded(inp, "space_setpoint", room)`) and the DHW-duty space write (`_bounded(..., 5.0, rounding="down")`). `_space_grid` returns the advertised grid whenever `_flow_unit` is false, because the option is in water terms and must never bind a room set-point.

Other entities never read the option: DHW (`_dhw_write`, `repairs.py`), the valve (`coordinator._valve_write_problem`), the heat curve (`heat_curve.write_displace`) and the frequency write.

## Structure payment

`module_excess_loc` is at zero headroom, and `pump_arbiter.py` (2360 lines) and `config_flow.py` (4200 lines) are both over `MODULE_LOC_LIMIT`, so every line added to either is owed.

- `pump_arbiter.py`. The limit logic lives in `flow_limit.py`, which is under the limit and adds no excess. The one rule replaces `_boost_ceiling_c`'s cap-list body and `_feedback_bounds`' sensor-high handling, which removes lines. `_space_grid` and the call sites add some. The build measures the net change with `python3 tests/structure.py` at its merge base, and it must be zero or below. If it is above zero, the next payment is moving `_flow_command`/`_full_draw_c`/`FlowCommand` (the `draw_range` input, about 55 lines) into `flow_limit.py` or a sibling, a move judged by `tools/audit/archscore/score.py --diff`.
- `config_flow.py`. The `const` import line and the row add about 2 lines, and possibly 1 more for the `_ABSENT_IS_NOT_DEFAULT` tuple. The payment is a measured move of an equal number of lines out of `config_flow.py`, into the module already owning their concept. The build names the move and its archscore dS. Packing two names onto one line would only game the metric and pays nothing.
- If no improving payment exists in `config_flow.py`, the route is a budget raise under mandate 6893738184, which is scoped `all` (CLAUDE.md rule 2, decision 0013). The PR body carries `## Raise justification` with each payment tried and its `Architecture score: dS` line, and that has to be settled before the fixer pushes.

## UI strings

These go in `strings.json` plus the `en`, `sv` and `de` translations, under the `entities` step's `data` and `data_description`:

- data: "Controller's maximum set-point (°C, optional)"
- data_description: "Optional. The highest value the pump accepts for the set-point entity above, where that is lower than the entity's own maximum. No set-point above it is written, a boost's included. With a maximum set-point sensor as well, the lower of the two applies. Left empty, the entity's own maximum applies."

The existing `space_setpoint_high_limit_entity` description says "Used by that option alone", which is already untrue because the boost reads the sensor too. It is corrected to say that the sensor caps the feedback loop, a boost, and every space water write, and that with the manual limit also set, the lower of the two applies.

## Migration

None. The key is new and absent on every entry, and absent means no manual limit, so behaviour is unchanged. The entry version does not move.

## Tests the build owes

The tests use synthetic entities, with numbers chosen freely: an advertised maximum of 70, a sensor reading of 52, an option of 48, and an entity minimum of 40.

- Precedence. Sensor 52 with option 48 gives 48, and option 58 gives 52. A sensor that is unavailable with option 48 gives 48. A crossed sensor pair with option 48 gives 48. Neither source gives the advertised 70. An option above the advertised maximum gives the advertised maximum.
- Entity minimum. Entity minimum 40 with option 35 gives 40, logged; on a 5-degree step with minimum 41, the result is 45. The arbiter's record then equals its read-back, so `_edited` is false. Null control: option 45 with minimum 40 gives 45.
- Gate rule. A sensor at the gate plus one step or below is dropped and logged, with the option then in force. Null control: a sensor one step above that is kept.
- Each consumer that moves, per the table: a boost writes the limit; a band-top heating step is held at it; the fallback hold is held at it; the feedback loop stays under it. `draw_range`, per the table, with its null control.
- Excluded: an indoor-unit entity with the option stored writes its room value unchanged.
- Null controls on the whole: with the option unset, no write changes on any existing fixture; an untouched options page stores nothing; an out-of-range stored value shows `stored_value_out_of_range`.
- Mutation sites, each with a dying test and a null control that does not move: the sensor-unavailable fallback branch, the lower-of-two step, the `min(limit, advertised)` step, the gate-rule comparison, and the entity-minimum raise.

## Alternatives considered

- Reusing `flow_heat_c` as the cap: refused. It is also the full-power ceiling of the level map, so a high value raises every partial-level flow.
- Inferring the device ceiling from readback by generalising `_clamp_cut`: refused. A refused write and a clamped write read the same, and the first would learn the previous value as the ceiling.
- Lowering `high_c` on the one shared `_grid`: refused. It would move `_flow_command`'s ceiling and so the `draw_range` censoring input, and it would bind indoor-unit room set-points.
- Passing the limit as each caller's `hi`: refused. That is a per-caller clamp at six sites, and `_space_grid` keeps it to one.

## Size

About 50 lines in `flow_limit.py`, about 20 changed lines in `pump_arbiter.py` with a net change of zero or below, and 2-3 lines in `config_flow.py` with their payment. Strings, translations and tests are on top.
