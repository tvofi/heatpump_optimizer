# Design note: R11-OWNER-FAULT-HOLD -- suspend actuation while the pump reports a latched fault (rev 2)

Rev 2 answers `design-verdict/R11-OWNER-FAULT-HOLD` 20790180 (revise,
class-open, R1-R3 and seven carries on 6244553e45). Code read at
`origin/main` 3a98735a7e. Serial position (orchestrator ruling): FLOWCAP
(fa8cd134), then FROST-HOLD (e91a4e30, verdict 774250ff), then this group,
then MODE-LEGS (0e59437a), then STEP-KICK (238cf282); none has a handoff
head yet, so this note composes with their designs and the fixer re-measures
at its merge base. Evidence: owner report from a private diagnostics bundle;
**no finder harness: owner report** (a counts-only bundle harness is
planned below, never committed with data). Generically: a pump's fault
alarm latched for hours; through it the integration, in duty control, kept
alternating Heating and DHW and writing set-points into the faulted pump,
and nothing on the integration's side told the owner. Short self-clearing
faults clear in well under a minute; the longest in the owner's history
lasted a few minutes.

## What exists today (checked first)

`grep -rn "FAULT_ENTITY\|FREEZE_FAULT" custom_components/heatpump_optimizer/*.py`:
the fault slot (`CONF_HEAT_PUMP_FAULT_ENTITY`) is read in
`pump_signals.read` (learners freeze, `FREEZE_FAULT`, and diagnostics
`fault`) and by `pump_arbiter._switch_context` (a duty-switch episode is
voided). **No repair, no notifier event and no write guard reads it.**
Nothing below re-does the freeze or the void.

## Behaviour

**Reading** (R2). This consult reads the slot with `read_bool(...,
max_age_minutes=UNBOUNDED)` (`inputs.UNBOUNDED`): a legible value counts
at any age, so a fault that a push-only source reported once and never
again still reads on. The 60-minute horizon keeps governing the learner
freeze in `pump_signals`, unchanged. **Unusable** = unavailable, unknown,
not boolean, or no slot.

**Latch** (in memory, per config entry):
- `since` is set at the first legible **on** to that state's
  `last_changed` (bounded to now) and is kept through a code change and
  through unusable readings; only a legible **off** resets it.
- The hold is on while `since` is set and `now - since >=
  FAULT_HOLD_AFTER_MIN` (10 min, a constant in `fault_hold.py`).
- A legible off ends the hold. An unusable reading never starts a hold
  (no `since` is set from it) and never ends one.
- Optimizer Off answers False and clears the repair; the first consult
  after On re-seeds `since` from the entity's `last_changed`, so a fault
  older than 10 minutes holds again at once. A reload does the same (the
  entry object survives a reload; a re-seed from `last_changed` covers a new
  one). An HA restart stamps `last_changed`, so it holds 10 minutes after.
- A pass with `entry_released` answers False and raises nothing.

**While holding:**

| writer | today | under the hold |
|---|---|---|
| power switch (`_write_supply`: cycle and step tick) | plan's ON/OFF | OFF becomes "leave", marked held so the step tick retries it (switch stays on); ON passes |
| early cut-off (`early_cutoff.on_room_event`) | `turn_off` | no cut |
| arbiter in control: mode, DHW and space set-points, silent switch, night schedule, `hold` re-sends, retries | per pass | nothing written; `space_before` and `held.retry` dropped each pass, as `_pump_off` drops `space_before` |
| `_lead_mode` | mode write | none |
| unload row (`pump_arbiter.release`) | baseline row | skipped; `off_restore`'s restore of the person's space set-point is kept (one write, the person's own value) |
| compressor frequency (`_command_frequency`) | rate-limited | none |
| every heat-curve displace (R1): cycle, `peak_guard` engage and release, all through `async_publish_ecl110_command` → `heat_curve.publish` | MQTT and entity arms | none |

The solver keeps planning; only actuation is suspended. After the clear the
next pass writes the step's row, and the step tick lands a held OFF.

**Repair** `pump_fault_hold` via `issues.set_issue` (warning, not fixable,
not persistent): raised on the hold's rising edge, cleared on its falling
edge, at Off and at unload. The rising edge also clears `pump_write_ignored`.
Title "The heat pump reports a fault; the plan is suspended"; description
names `{entity}` and `{since}`, says the optimizer stops changing the pump's
mode and set-points and does not switch it off until the fault clears, that
the notice clears itself, to read the code on the pump's own display or
app, and to turn Optimizer active off before switching the pump by hand.

**Ledger:** a step in which any pass held is `device-fault`, tested before
every other verdict (before frost's `frost-hold`). A short fault keeps
today's verdict. The step in which a long fault began closes before the
hold and keeps its verdict; `docs/configuration.md` says so (no
retroactive rescoring: a row is closed when its step ends).

**Opt-out:** `fault_hold` boolean, default on; off answers False everywhere
and raises nothing.

**Installs:**

| install | the hold |
|---|---|
| Tuya fork: binary "Fault Alarm" (bitmap != 0), or the raw bitmap sensor | `parse_bool` reads non-zero as on; holds after 10 min |
| GCHV/Rotenso Modbus: an alarm register or a template over it | same rule; a bitmap that also carries non-blocking warnings holds too: cost stated, opt-out |
| generic flag-domain fault entity | holds |
| generic status text sensor | an unparseable word is unusable: never starts a hold |
| no fault entity | nothing changes |
| duty off / observe | switch (no OFF), cut-off, frequency, curve held; observe ledger scores `device-fault` |
| no power switch | switch rows do nothing; the rest as above |

## Interaction with the frost hold (e91a4e30)

- **Switch: on wins.** `hold_supply` → `frost_hold.gate` → `fault_hold.gate`;
  the fault gate turns only `False` into `None`, so a frost switch-on passes.
- **Rows: fault wins.** With both latched, control writes nothing (the frost
  row is itself a mode and set-point write into a faulted pump).
- **Cut-off:** frost's single `arm` predicate is wrapped,
  `fault_hold.cutoff_hook(entry, frost_hold.cutoff_hook(coord))`, answering
  `holding or inner()`.
- Ledger `device-fault` before `frost-hold`; freezes unchanged; repairs independent.

**Pending owner override** (the design review recommends keeping both): ON
passes under the hold; X = 10 minutes as a constant.

## Owning seam and shape

Owner: `custom_components/heatpump_optimizer/fault_hold.py` (new), a leaf
importing `const`, `entry_config`, `inputs` and `issues`, never
`pump_arbiter`, so `pump_arbiter` and `heat_curve` may import it with no
cycle. The one writer of the latch and the repair; everything else consults.

- State per config entry in a `WeakKeyDictionary`: `since`, `holding`.
- `holding(entry, hass, config, *, off, released=False, now=None) -> bool`
  -- reads, moves the latch, writes the repairs on an edge. Synchronous.
- `held(entry) -> bool` -- the latch as last moved, no read.
- `gate(entry, value) -> bool | None` -- `False` → `None` while held.
- `cutoff_hook(entry, inner)`, `release(hass, entry)`, `diagnostics_view(entry)`.

Consults: `pump_arbiter.apply` once per pass, before the duty-off return
(every install each cycle; observe/control each minute), passing
`inp.entry_released`; `_arbitrate(..., faulted)` marks the row, drops
`space_before`/`retry`, returns before `_adopt`/`hold`/`_command`/night;
`_lead_mode` and `release` read `held(entry)`. `heat_curve.publish` -- the
one sink of `async_publish_ecl110_command`, so the cycle, the peak-guard
engage and its release are all covered -- calls `holding(..., off=mode_off)`
first and returns. `_command_frequency` reads `held(self.entry)` on its
existing guard (it runs after `_apply_action`, so the latch is this
cycle's). `diagnostics.py` gains one row.

```
cycle/tick ─ _write_supply ─ hold_supply ─ frost.gate ─ fault.gate ─ switch_supply
arbiter tick ─ apply ─ fault.holding ─┬ held: _observe(fault); drop retry; return
                                      └ free: _adopt, hold, _command, night
any displace ─ async_publish_ecl110_command ─ heat_curve.publish ─ fault.holding ─ arms | none
room event ─ on_room_event ─ hook(): fault.held or frost.take_off ─ cut | keep
```

## Alternatives

1. Latch in `pump_signals` -- lost: read once per cycle (30 min by default),
   too late for the 1-minute ticks and the clear.
2. State on `ArbiterState`, `fault_hold` importing `pump_arbiter` -- lost:
   `pump_arbiter.apply` and `heat_curve` consult it; that is a cycle.
3. Hold only after the compressor stopped -- lost: a meter that includes
   the backup heater reads a latched pump as running and releases it.
4. Consult in the coordinator's `async_publish_ecl110_command` -- lost to
   `heat_curve.publish`, its one sink: same coverage, no coordinator-class line.
5. The slot's 60-minute horizon for this consult -- lost (R2): a latch lost
   at Off or a reload never returns while a push-only fault persists.
6. X as an option -- lost: no finding asks to tune it; a `config_flow.py`
   row at zero headroom.

## Sibling sites

`grep -n "services.async_call\|switch_supply(\|write_setpoint(\|write_setpoint_c(\|async_publish_ecl110_command(" custom_components/heatpump_optimizer/*.py`:
switch (`_write_supply`, `early_cutoff`), arbiter `_write`, frequency, and
`async_publish_ecl110_command`'s three callers (cycle, peak-guard engage,
release via `async_publish_current_action`) are covered; `write_displace`
and `write_persistent` are reached only through `publish`. Out of scope:
`_async_set_pump` (external circulators), `_valve_write_problem` (mixing
valve), `DisinfectionSwitch` (one write per cycle; its own repairs),
`repairs.py` (a person's fix), the weather fetch (a read).

## Evidence plan

Tests in `tests/features.py` beside the `supply_hold.hold_supply` cases;
ledger cases in `tests/block_duty.py`, re-pointed to `duty_ledger`. Failing
first; null control in each: the same fixture with the fault reading a
fresh off (or `fault_hold` off) gives today's writes.

1. Control, fault on 11 min: no mode, set-point, silent or night write; 9 min: today's.
2. Step-boundary Heating→DHW under the hold: no mode write.
3. Drift under the hold: no re-send, no retry, `pump_write_ignored` cleared
   on the edge; after the clear, rewritten; a reset never adopted.
4. Switch: plan OFF left and marked held; after the clear the tick writes
   it; ON passes; with frost latched, frost's ON passes and no row.
5. Early cut-off: no `turn_off` under the hold.
6. Frequency, the cycle displace and the peak-guard engage: no write.
7. R2: a fault reading on for 70 min on an on-change source: Off→On holds
   at once; a reload holds at once. Unavailable/unknown/not-boolean never
   start a hold and keep an active one, and keep `since`.
8. Repair: rising edge, falling edge, Off, unload; `entry_released` raises
   none; a 9-min fault raises none.
9. Ledger: held steps `device-fault` (dhw, space, both, frost latched);
   an unheld short-fault step keeps `idle-instead`; the onset step keeps its verdict.
10. Duty off and observe: switch, frequency, curve held; observe scores `device-fault`.
11. Numeric bitmap and binary sources both hold.
12. Unload under the hold: no baseline row; the space restore runs.
13. Opt-out: no hold, no repair over a 60-minute fault.
14. Config flow: option, default, three translations; `const.py` check.
15. Synthetic replay (no install data): 24 h control, one multi-hour latch,
    several sub-minute and few-minute faults; mode and set-point writes and
    OFFs while latched past 10 min: 0; short faults change no count; null
    control (opt-out) reproduces today's counts.

Mutation targets: the 10-minute comparison, the unbounded read, the
legible-off reset, the unusable branch (start and keep), the re-seed at On,
the `released` guard, the `False`-only gate and its held mark, `apply`'s
consult and `_arbitrate`'s return, `_lead_mode` and `release` skips, the
`retry`/`space_before` drops, `publish`'s return, the frequency guard,
`_verdict`'s fault-first branch, the repair edges, the opt-out. Goldens: a
moved fixture is claimed, never re-recorded.

## Hot files and structure payment

Hot: `pump_arbiter.py`, `duty_ledger.py` (new), `coordinator.py`,
`supply_hold.py`, `early_cutoff.py`, `heat_curve.py`, `diagnostics.py`,
`config_flow.py`, `const.py`, `entry_config.py`, `strings.json`,
`translations/en.json`, `translations/sv.json`, `translations/de.json`,
`tests/features.py`, `tests/block_duty.py`, `tests/closures.json`. Both new
modules and the harness are classified (closure or INERT).

`module_excess_loc`, `class_excess_loc` and `max_class_loc` sit at zero
headroom; each over-limit file names its own payment, **claimed by this
group alone** and distinct from FLOWCAP's (its new `flow_limit.py`, fallback
`_flow_command`/`_full_draw_c`), FROST-HOLD's (`_write_supply`'s debug
branch to `frost_hold.log_skip`), MODE-LEGS' (`_valid_months_spec` to
`grid_fee.py`; `_share` plumbing, fallback `_switch_context`) and
STEP-KICK's (`FLOW_INLET_KEYS`, fallback `_or_hold`/`_gate_floor_c`).

- **`pump_arbiter.py`** (+ about 10: consult, `faulted`, drops, `_lead_mode`
  and `release` skips). Payment: the step ledger moves to
  `duty_ledger.py` (new) -- `_observe`'s row logic, `_not_startable`,
  `_missed`, `_verdict` and the ledger paragraph of the docstring.
  **No cycle:** `duty_ledger` imports only `plan_step`; `pump_arbiter`
  computes and passes the values the ledger read from it (`ran` from
  `_ran_kw`, `dhw_mode` from `_slot_state`, `start_below` from
  `_dhw_start_below_c`, which keeps `_dhw_target`), and `held` is passed
  as the row owner. Expected net well below zero.
- **`config_flow.py`** (+ about 3: the `_F` row beside the fault-entity row
  and its `const` import names). Payment: `_meter_source_selector`,
  `_freq_mode_selector` and `_solar_source_selector` each re-spell
  `_select`; their four `_F` rows call `_select(...)` with the same
  options and translation keys, the three functions are deleted, and each
  docstring's reason survives as a one-line comment at its row. Net about −30.
- **`coordinator.py`** (target 0): the fault gate joins the existing
  `value =` statement; `_command_frequency`'s guard gains `held(...)`; the
  displace consult is in `heat_curve.py`; the import joins the existing
  `from . import` line. **Fallback** if the class or module is above zero:
  `_write_supply` (after frost's move) leaves the class as
  `supply_hold.write_gated(coord, on)`; the cycle calls it and
  `SupplyWiring` takes `functools.partial(supply_hold.write_gated, self)`.
- **`const.py`** (1954 lines, under `MODULE_LOC_LIMIT`): only
  `CONF_FAULT_HOLD` and its default; the 10-minute constant lives in
  `fault_hold.py`, so the four groups' const lines do not cross the limit.
  Confirm at the merge base.
- Measure with `python3 tests/structure.py` at the merge base and head, and
  `tools/audit/archscore/` before and after each move. If a payment reads
  worse or nets above zero, the raise goes under mandate 6893738184 (scope
  `all`) with a `## Raise justification`, settled before the push.

Docs: `docs/configuration.md` (Fault alarm row, `device-fault` and the
onset step in the ledger line, the option row); `docs/architecture.md`
(two module lines). Release note: "With a Fault alarm entity configured,
the optimizer stops changing the heat pump's mode, set-points, compressor
frequency and heat-curve offset, and no longer switches it off, once the
alarm has been on for 10 minutes, and raises a repair until it clears. A
fault entity that also reports non-blocking warnings holds too: turn
*Fault hold* off to keep the old behaviour."

## Notes for the fixer

- Carry: R11-OWNER-FAULT-HOLD (skip-log) -- the gate's held mark sets
  `held.supply_held`, so `frost_hold.log_skip` never prints the cooling
  text for a fault `None`; it names the fault.
- Carry: R11-OWNER-FAULT-HOLD (multi-entry) -- `pump_fault_hold` is one
  domain-wide id like `pump_write_ignored`; clear it only when no entry
  holds, or key it per entry; state which in the body.
- Carry: R11-OWNER-FAULT-HOLD (hand-reset) -- a person switching the pump
  off by hand sees the next ON within a minute, as today; the repair text
  says to turn Optimizer active off first.
- Carry: R11-OWNER-FAULT-HOLD (entry-released) -- `holding` answers False
  and raises nothing when `inp.entry_released` is set (the consult sits
  before `apply`'s `entry_released` return).
- Carry: R11-OWNER-FAULT-HOLD (supply-after-clear) -- `note_supply` records
  the plan's OFF the gate turned into `None`; the held mark makes
  `supply_tick` retry it each minute, so it lands after the clear.
- Carry: R11-OWNER-FAULT-HOLD (ignored-repair) -- the rising edge clears
  `pump_write_ignored`, and `_arbitrate` drops `held.retry` while faulted.
- Carry: R11-OWNER-FAULT-HOLD (unload-row) -- `release` skips the baseline
  row under the hold; `off_restore`'s space restore still runs.
- Carry: R11-OWNER-FAULT-HOLD (onset-step) -- the onset step keeps its
  verdict, stated in the docs ledger line.
- Carry: R11-OWNER-FAULT-HOLD (cc-headroom) -- `functions_cc_over_15` is at
  zero headroom and frost and STEP-KICK branch the same functions; fold
  `faulted` into `_arbitrate`'s existing return condition and measure at the
  merge base.
- Carry: R11-OWNER-FAULT-HOLD (bundle-latch-count) --
  `dev/audit/harnesses/r11_owner_fault_latch.py` (new) `<bundle.json>`, beside
  STEP-KICK's, replays the bundle's fault-alarm timeline through the latch
  rule and prints counts only (latches, short faults held); expected one
  latch and none among the short faults. The bundle is never committed.
- Carry: R11-OWNER-FAULT-HOLD (seam-actuation) -- if R11-SEAM-actuation-writes
  or -release lands first and moves the frequency or displace tail, the
  consult moves with it, into that tail's gate.
- Planning around a faulted pump -- dismissed: no finding names a planner
  change; actuation alone is suspended.
