# Away Plan-page toggle and return time

Approved design, 2026-09-05. A Plan-tab Away control and a service-backed
store replace the Home Assistant helpers that away mode used to require.

Part of #201. Issue **#465**. Programme seat: **3L-G10** (see Seat).

## Goal

Turn away on from the Plan page, optionally set a return date/time, and
have recovery still buy heat before that instant. Automations use the
integration’s own switch and datetime. No user `input_boolean` or
`input_datetime`.

## Non-goals

- Changing recovery math (`RECOVERY_MARGIN_HOURS`, `MAX_RECOVERY_HOURS`,
  `estimate_recovery_hours`).
- Replacing `binary_sensor.heat_pump_optimizer_away_mode` (resolved state).
- Re-recording value-bearing goldens. `claims-for:` stays `6.3.14`.
- `VERSION`, manifest version, or `RELEASE_NOTES.md` heading.
- `CONFIG_ENTRY_VERSION` bump.
- Merging ahead of W3-G3 or 3L-G8/G9.

## Architecture

Coordinator persists `{active, return_time}` in its own Store (same
pattern as the manual plan). `set_away` is the only writer. The Plan
toggle, `switch.heat_pump_optimizer_away`, and
`datetime.heat_pump_optimizer_away_return` all call that service.

`away.resolve()` checks the store first. If `active`, source is
`service` and a person entity cannot clear it. If `active` is false,
optional person / device_tracker / calendar / binary_sensor still works
as today. Person-away return time is calendar end, or the store’s
`return_time` when that is set (the mapped replacement for
`away_return_entity`).

`away_enabled` is gone. `AwayConfig.enabled` is gone. `resolve()` has no
feature-off gate.

## Store and service

Payload: `{"active": bool, "return_time": iso-8601 | null, "migrated_helpers": bool}`.

`heatpump_optimizer.set_away`:

| field | required | meaning |
|---|---|---|
| `active` | no | `true` / `false`. Omit to leave on/off unchanged. |
| `return_time` | no | ISO datetime, or empty / null to clear. Omit to leave the stored time. |

At least one field is required. Turning `active` false also clears
`return_time`. Setting `return_time` while `active` is false stores the
time and does not turn away on. A return already in the past, with
`active` true, expires immediately.

Switch `turn_on` → `set_away(active=true)` (keeps return).
Switch `turn_off` → `set_away(active=false)` (clears return).
Datetime `set_value` → `set_away(return_time=...)`.

## Auto-off

`expire_override(active, return_time, now)` in `away.py`: if `active` and
`return_time` is not None and `now >= return_time`, return
`(False, None)`. The coordinator writes that result back through
`set_away` before `resolve()`, so the switch turns off at the return
instant. Recovery has already run (`hours_left <= recovery + 1 h`).

No return time means away until the switch is turned off. Auto-off does
not clear person-away.

## Resolve

```
expire override; persist if it changed
if override active:
    away, source=service, return=store return_time
elif person/calendar/device/binary says away:
    away, source=that entity, return=calendar end or store return_time
else:
    not away
```

Recovery timing is unchanged. `interpret_presence` still understands
`input_boolean` polarity; the config picker no longer offers that domain.

## Entities

| object id | role |
|---|---|
| `switch.heat_pump_optimizer_away` | override on/off; `is_on` = store `active` |
| `datetime.heat_pump_optimizer_away_return` | store `return_time`; new `datetime` platform |
| `binary_sensor.heat_pump_optimizer_away_mode` | resolved `away_active` (unchanged) |

Switch and datetime call `set_away`. They do not hold a second copy of
the store. Always created. On the integration device.

## Publish

Next to the existing resolved `away_*` keys:

```
away_override_active: bool
away_override_return_time: iso | null
```

Do not put these on a plan sensor. Claim the new key paths against
`origin/main`. The switch and datetime entities read these. The card
reads those two entities (pinned object ids, then unique-id suffix
`_away` / `_away_return`) and the existing away-mode binary sensor for
the person-away status line.

## Config

Setup Away page:

- Setback temperature (unchanged).
- DHW minimum while away (unchanged).
- Optional presence picker: `person`, `device_tracker`, `calendar`,
  `binary_sensor`. Not `input_boolean`.

Removed from the form: `away_enabled`, `away_return_entity`. Their
config keys, if still present, are ignored after migration.

Live on/off and return datetime do not appear on Setup.

## Migration

On first coordinator load, once:

1. If `away_return_entity` has a parseable datetime, copy it into the
   store’s `return_time`.
2. If `away_presence_entity` is an `input_boolean` and
   `interpret_presence` is true, set store `active` true. Then drop that
   presence key.
3. Drop `away_return_entity` and ignore `away_enabled`.
4. Person / device_tracker / calendar / binary_sensor IDs stay.

A marker in the store (`migrated_helpers: true`) prevents a second copy
after the user clears the datetime. No config-entry version bump.

## Card

Expanded Plan tab only — not the collapsed card, not Setup. Strip above
the chart:

- Away toggle bound to the away switch (`is_on`), not to resolved
  `away_active`. Change calls `set_away` immediately.
- When the toggle is on, a return datetime control bound to the
  datetime entity. Change or clear calls `set_away`. Empty means no
  return.
- No separate Apply button.
- If the away-mode binary sensor is on and the switch is off, one
  status line (person/calendar away). The toggle stays off and cannot
  clear that.

Keys (en + sv): `away.toggle`, `away.return`, `away.status_presence`.
No new tab.

## Tests

- `expire_override`: past return → `(False, None)`; future return
  unchanged; no return unchanged.
- `resolve`: override on wins over person home; override off + person
  away still away; auto-off then person still away if the person is
  away.
- Service / store: on without return stays on; on with past return
  expires; off clears return.
- Migration: boolean-on copies active; person id kept; return entity
  copied then dropped; second load does not recopy.
- Config flow: no `away_enabled` / `away_return_entity`; presence
  domains exclude `input_boolean`.
- Entities: switch mirrors override; datetime mirrors return; binary
  sensor still follows resolved `away_active`.
- Card: strip on Plan; datetime hidden when toggle off; status line
  when person-away and switch off; collapsed card has no toggle.

`cp` backups for mutation. Gate lock if select is `MODE: FULL` or names
`tests/stress.py`. No `SOLVE_BUDGET_RATIO` raise. Pay `coordinator_loc`
or stop and ask.

## Seat

After **3L-G9 (#463)**, before Wave 4 (principle 3: coordinator, config,
and card behaviour before `#223` / `#193` moves). Do not start
production while W3-G3 or 3L-G8/G9 hold `coordinator.py` or the card.

| group | model | after | scope |
|---|---|---|---|
| **3L-G10** | Grok 4.6 extra high | 3L-G9 | Store, `set_away`, entities, config migration, Plan strip |

Issue **#465** is filed. **3L-G10** has `Closes #465` on its own line.
Do not reuse #457, #460, or #463.
