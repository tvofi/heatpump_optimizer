# Design note: R11-OWNER-FAULT-HOLD -- suspend actuation while the pump reports a latched fault

Code read at `origin/main` 3a98735a7e. Predecessor on the same hot files:
R11-OWNER-FROST-HOLD, approved design `design/R11-OWNER-FROST-HOLD`
e91a4e30 (verdict 774250ff), being built, no handoff head yet; this note
composes with that design's shape and runs after it. Evidence: owner report
from a private diagnostics bundle; **no finder harness: owner report**.
Generically: a pump's fault alarm latched for hours; through it the
integration, in duty control, kept alternating Heating and DHW and writing
set-points into the faulted pump, and nothing on the integration's side told
the owner. Short self-clearing faults (protection trips at a duty switch)
clear in well under a minute, and the longest self-clearing fault in the
owner's history lasted a few minutes.

## What exists today (checked first)

`grep -rn "FAULT_ENTITY\|FREEZE_FAULT" custom_components/heatpump_optimizer/*.py`:
the fault slot (`CONF_HEAT_PUMP_FAULT_ENTITY`) is read in
`pump_signals.read` (learners freeze, `FREEZE_FAULT`, and diagnostics
`fault`) and by `pump_arbiter._switch_context` (a duty-switch episode is
voided). **No repair, no notifier event and no write guard reads it**: the
issue keys in `strings.json` hold none, `notifier.py` has no fault detector,
and no writer consults it. Nothing below re-does the freeze or the void.

## Behaviour

**Latch** (in memory, per coordinator): set when the fault slot reads on,
fresh and legible (`InputReader.read_bool`, `ok`), continuously for
`FAULT_HOLD_AFTER_MIN` = 10 minutes; cleared by the first fresh legible
**off**. Onset is the state's `last_changed` at the first on-reading (a
code change inside one fault keeps the onset). An unusable reading
(stale, unavailable, not boolean, no slot) never starts a hold, and never
ends an active one: the slot's 60-minute horizon would otherwise release a
latched fault on a push-only source. Under Optimizer Off the latch and the
repair clear (Off writes nothing already). A restart starts unset; HA
stamps `last_changed` at restart, so a fault on across it re-holds 10
minutes later; a reload keeps the stamp and re-holds at once.

**While holding:**

| writer | today | under the hold |
|---|---|---|
| power switch (`coordinator._write_supply`, step tick, cycle) | plan's ON/OFF | OFF becomes "leave" (switch stays on); ON passes |
| early cut-off (`early_cutoff.on_room_event`) | `turn_off` | no cut |
| arbiter slots in control: mode, DHW and space set-points, silent switch, night schedule, `hold` re-sends, retries | per pass | nothing written; `space_before` dropped each pass, as `_pump_off` does, so a reset during the fault is never adopted as an edit |
| `_lead_mode` (mode ahead of a switch-on) | mode write | none |
| compressor frequency (`_command_frequency`) | rate-limited | none |
| heat-curve displace (`async_publish_current_action`, MQTT and entity arms) | per cycle | none |

The solver keeps planning; only actuation is suspended, so the first pass
after the clear writes the current step's row (a reset value still there is
rewritten as any difference is, by `hold`).

**Repair** `pump_fault_hold` through `issues.set_issue` (warning, not
fixable, not persistent), raised on the latch's rising edge and cleared on
its falling edge, at Off, and at unload. Title "The heat pump reports a
fault; the plan is suspended"; description names `{entity}` and `{since}`
(local time), says the optimizer stops changing the pump's mode and
set-points and does not switch it off until the fault clears, that the
notice clears itself, and to read the code on the pump's own display or app.

**Ledger:** a step in which any pass held is `device-fault`, tested before
every other verdict (before frost's `frost-hold`). A step with a fault
shorter than the hold keeps today's verdict, so a short trip never hides a
real `idle-instead`.

**Opt-out:** `fault_hold` boolean, default on; off is a branch where every
consult answers `False` and no repair is raised.

**Installs:**

| install | the hold |
|---|---|
| Tuya fork: binary "Fault Alarm" (bitmap != 0), or the raw bitmap sensor | `parse_bool` reads non-zero as on; holds after 10 min |
| GCHV/Rotenso Modbus package: an alarm register or a template over it | same rule; a bitmap that also carries non-blocking warnings holds too: cost stated, opt-out |
| generic, flag-domain fault entity (binary_sensor, switch, input_boolean) | holds |
| generic, status text sensor | strict parse; an unparseable word is no evidence, never holds |
| no fault entity | nothing changes: no hold, no repair |
| duty off / observe | switch (no OFF), cut-off, frequency, curve held; observe ledger scores `device-fault` |
| no power switch | switch rows do nothing; the rest as above |

## Interaction with the frost hold (e91a4e30)

- **Switch: on wins.** Chain in `_write_supply`: `hold_supply` → `frost_hold.gate`
  → `fault_hold.gate`. The fault gate turns only `False` into `None`, so a
  frost switch-on passes and a frost "leave" stays "leave". Neither hold
  ever moves the switch toward off.
- **Rows: fault wins.** With both latched, control writes nothing: the
  frost hold row (Heating at the floor) is itself a mode and set-point write
  into a faulted pump. `_arbitrate` returns before `_command`;
  `_lead_mode` writes no mode.
- **Cut-off:** the frost design's single `arm` predicate becomes
  `fault_hold.cutoff_hook(coord, frost_hold.cutoff_hook(coord))`, answering
  `holding or inner()`; no second `arm` parameter.
- Ledger `device-fault` before `frost-hold`; freezes unchanged
  (`FREEZE_FAULT` already covers the interval); repairs independent.

Decisions pending owner override: ON passes under the hold (one write,
never churn, and keeps "on wins" symmetric); X = 10 min as a constant.

## Owning seam and shape

Owner: `custom_components/heatpump_optimizer/fault_hold.py` (new), a leaf
beside `custom_components/heatpump_optimizer/supply_hold.py`: it imports
`const`, `entry_config`, `inputs` and `issues`, never `pump_arbiter`, so
`pump_arbiter` may import it with no cycle. It is the one writer of the
latch and the repair; `pump_arbiter`, `coordinator` and `early_cutoff`
only consult it.

- `FaultState`: `since: datetime | None`, `holding: bool`; per-coordinator
  in a `WeakKeyDictionary` (no coordinator attribute).
- `holding(coord, inp, now) -> bool` -- `inp` duck-typed (`hass`, `config`,
  `mode`); reads the slot, moves the latch, writes the repair on an edge.
  Synchronous, no `await`: atomic on the event loop.
- `gate(coord, inp, value) -> bool | None` -- `False` → `None` while holding.
- `cutoff_hook(coord, inner) -> Callable[[], bool]`; `release(coord)`
  clears the repair; `diagnostics_view(coord)` → `holding`, `since`, `after_min`.

Consults: `pump_arbiter.apply` once per pass, before the duty-off return,
so every install consults each cycle and observe/control each minute;
`_arbitrate(..., faulted)` marks the row then returns before
`_adopt`/`hold`/`_command`/`_write_night_schedule`; `_lead_mode`;
`pump_arbiter.release` calls `fault_hold.release`; `_observe` sets
`row["fault"]`; `_verdict` reads it first. Coordinator: the gate wraps the
existing `value =` statement; `_command_frequency` and
`async_publish_current_action` add the consult to their existing
Off guard. `diagnostics.py` gains one `("fault_hold", ...)` row.

```
cycle/step tick ─ _write_supply ─ hold_supply ─ frost.gate ─ fault.gate ─ switch_supply
arbiter tick ─ apply ─ fault.holding ─┬ held: _observe(fault) ; return
                                      └ free: _adopt, hold, _command, night
room event ─ on_room_event ─ hook(): fault.holding or frost.take_off ─ cut | keep
```

## Alternatives

1. Latch in `pump_signals` -- lost: read once per cycle (the optimization interval, 30 min by default), so
   neither the 1-minute arbiter tick nor the repair's clear sees it in time.
2. State on `ArbiterState` with `fault_hold` importing `pump_arbiter` (the
   frost pattern) -- lost: `pump_arbiter.apply` must consult the hold,
   and that import direction makes a cycle (`import_cycle_modules`).
3. Hold only after the compressor stopped (measured draw below
   `_ran_kw`) -- lost: a meter that includes the backup heater reads a
   latched pump as running, which releases the hold while the heater runs.
4. `_apply_action` returning early, as the stale-plan guard does -- lost:
   skips the frost gate's switch-on, and misses the arbiter and step ticks.
5. X as an option -- lost: no finding asks to tune it; a row, four string
   files and bound tests for a constant.
6. Treat a missing fault entity as a fault from "commanded, no draw" -- lost:
   an idle pump on its own thermostat reads the same; no finding names it.

## Sibling sites

`grep -n "services.async_call\|switch_supply(\|write_setpoint(\|write_setpoint_c(" custom_components/heatpump_optimizer/*.py`:
switch (`pump_arbiter.switch_supply` via `_write_supply` and
`early_cutoff`), arbiter `_write` (covered); frequency
(`coordinator._command_frequency`), `heat_curve.publish` (covered);
`heat_curve.write_displace` (`_send`) is reached only through `publish`.
Out of scope: `_async_set_pump` (external circulators: frost protection of
the emitter loop, not the pump), `_valve_write_problem` (mixing valve),
`DisinfectionSwitch` (one write per cycle, not churn; an unreachable cycle
raises its own `dhw_legionella_*` repair), `repairs.py` (a person's fix
flow), the weather fetch (a read).

## Evidence plan

Tests in `tests/features.py` beside the `supply_hold.hold_supply` cases,
ledger cases in `tests/block_duty.py` beside the `not-startable` cases;
failing first. Null control in each: the same fixture with the fault slot
reading off (or `fault_hold` off) gives today's writes.

1. Control, fault on 11 min: no mode, set-point, silent or night write;
   on 9 min: today's writes (the boundary).
2. Step-boundary duty change (Heating→DHW) under the hold: no mode write.
3. Drifted set-point under the hold: not re-sent, no retry; after the clear,
   rewritten; a reset during the fault never adopted as an edit.
4. Switch: plan OFF under the hold leaves it; ON passes; with frost
   latched too, frost's ON passes and its row is not written.
5. Early cut-off under the hold: no `turn_off`; frost-only: as frost's tests.
6. Frequency and curve displace: no write under the hold.
7. Stale / unavailable / not-boolean: never starts a hold; an active hold
   holds; a fresh off clears it. Code change inside a fault keeps the onset.
8. Repair raised on the rising edge, cleared on a fresh off, at Off, at
   unload; a 9-min fault raises none.
9. Ledger: a held step is `device-fault` (planned dhw, space, both); a
   held step with frost latched is `device-fault`; an unheld step with a
   short fault keeps `idle-instead`.
10. Duty off and observe: switch, frequency, curve held; nothing else
    changes; observe scores `device-fault`.
11. Numeric bitmap source (non-zero) and a binary source both hold.
12. Opt-out off: every consult `False`, no repair, a 60-minute fault writes as today.
13. Config flow: option, default, three translations; `const.py` check.
14. Synthetic replay harness (no install data): 24 h of control with a
    multi-hour latched fault and several sub-minute and few-minute faults;
    count mode and set-point writes and switch OFFs while latched past
    10 min: must be 0; short faults change no count; null control (opt-out)
    reproduces today's counts.

Mutation targets: the 10-minute comparison, the fresh-off clear, the
unusable-reading branch (start and keep), the `False`-only gate, the
`apply` consult and `_arbitrate`'s return, `_lead_mode`'s skip, the
`space_before` drop, `_verdict`'s fault-first branch, the repair edges,
the opt-out branch, the frequency and curve guards. Goldens: the fixer's
gate run decides; a moved fixture is claimed, never re-recorded.

## Hot files, ratchet, docs

Hot: `pump_arbiter.py`, `coordinator.py`, `early_cutoff.py`,
`diagnostics.py`, `config_flow.py`, `const.py`, `entry_config.py`,
`strings.json`, `translations/en.json`, `translations/sv.json`,
`translations/de.json`, `tests/features.py`, `tests/block_duty.py`; every one
but `diagnostics.py`, `entry_config.py` and `tests/block_duty.py` is
R11-OWNER-FROST-HOLD's too, so this group runs after it, serially.
`fault_hold.py` (new) is classified into a measured closure (`tests/closures.json`).

Ratchet, re-measured at the merge base (`tests/structure.py`): the
coordinator class aims at net zero lines -- every consult joins an existing
statement (the gate on `value =`, the two Off guards, the `arm` hook) and
the import joins the existing `from . import` line. `pump_arbiter.py` (past
`MODULE_LOC_LIMIT`) gains about eight lines (the consult, the `faulted`
parameter, the row flag, the verdict branch, `_lead_mode`'s skip, the
release call); paid in-file. A candidate payment the fixer weighs with
`tools/audit/archscore/` before and after: move the step ledger
(`_observe`, `_dhw_start_below_c`, `_not_startable`, `_missed`,
`_verdict`) into its own module, a concern the arbiter only feeds. If no
payment improves the code, the raise follows CLAUDE.md rule 2 with a
`## Raise justification`.

Docs: `docs/configuration.md` -- the Fault alarm row says what the hold
does, the ledger list gains `device-fault`, the option row;
`docs/architecture.md` -- the module tree line; strings and translations
for the option and the repair.

Release note: "With a Fault alarm entity configured, the optimizer stops
changing the heat pump's mode and set-points, and no longer switches it
off, once the alarm has been on for 10 minutes, and raises a repair until
it clears. A fault entity that also reports non-blocking warnings holds
too: turn *Fault hold* off to keep the old behaviour."

## Notes for the fixer

- Carry: R11-OWNER-FAULT-HOLD (skip-log) -- the frost design moves
  `_write_supply`'s "Not switching off" debug branch into
  `frost_hold.log_skip`; a `None` from the fault gate must log the fault
  reason, never the cooling text, which today prints for any `None` with
  `supply_held` false.
- Carry: R11-OWNER-FAULT-HOLD (multi-entry) -- `pump_fault_hold` is one
  domain-wide id like `pump_write_ignored`; two entries with different fault
  entities share it. Clear only when no entry holds, or key it per entry
  with a translation key; state which in the body.
- Carry: R11-OWNER-FAULT-HOLD (hand-reset) -- a person who switches the pump
  off to reset a latched fault sees the next ON pass within a minute, as
  today; the repair text says to turn Optimizer active off first.
- Planning around a faulted pump (zero capacity in the solve) -- dismissed:
  no finding names a planner change; actuation alone is suspended.
