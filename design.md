# Design note: R11-OWNER-COOLING-AUTORETURN -- an opt-in return to heating from a cooling mode

Revision 2. It answers `design-verdict/R11-OWNER-COOLING-AUTORETURN` 7a9783a29c (revise, class-open,
R1 on 41979366f8) and the orchestrator's serial-position ruling. Base `origin/main`
49cb3207a997b4f38c11cb2f1adf4b8d613e06ea. Code read at the predecessors' handoff heads: #3864
(R11-OWNER-COOLING-GUARD) 0f9fc88ff36dd0326fa7f862e38d909b95133138 and #3872 (R11-OWNER-FAULT-HOLD)
d6a54399a63b76d43c4f3a84e1d2ac518da28ed0. Notes read: R11-OWNER-FAULT-HOLD 57d5d278f0 (approved,
verdict e9598ceb7e), R11-OWNER-FROST-HOLD e91a4e30d7 (approved, verdict 774250ff3d). The #3864 and
#3872 symbols cited below exist at those SHAs, not on main.
Evidence: the owner's ruling (tvofi, 2026-11-22), "I want the automatic return as an
opt-in option." **No finder harness: owner report.** The failing checks below are the harness.

## Preconditions #3864 owes (verdict `verdict/3864` b15f3816a3 blocked ee4c34cd9c)

Both are now built at #3864's a90d7bc9da, pending its re-review. If they land differently, step 9's
revalidation applies.
- **P1, readable select first.** `pump_arbiter.cooling_mode` takes the cycle's reading only when
  the select reads no known mode (`live.known`). The return and the moved cycle pass rely on it.
- **P2, the tick releases a refused ON.** `supply_tick` retries while `held.cooling_asked` stands.
  The return keeps setting `cooling_asked` on a refusal with the option on (below), so a lagged
  acknowledgement lands at the next tick.
Carry: R11-OWNER-COOLING-GUARD (item P1-P2-precondition)

## Choice: (a) a declared "no cooling circuit" option, not a trigger

The option says "this install has no cooling circuit; a cooling mode is never intended". With it on,
a readable cooling mode is returned to heating whatever the plan asks. With it off, nothing changes
from #3864: the switch-on is refused in a cooling mode and released only by a person.

Alternatives, and why each lost in code (unchanged from revision 1, held by the review):
- **(b1) outdoor temperature with hysteresis.** Two more options, an outdoor reading and a latched
  state in the switch gate, and it still writes Heating over a deliberate Cooling under the threshold
  on an install that can cool: the intent is in no reading the gate has.
- **(b2) heat demand plus a timeout.** In Cooling the planner blocks both channels
  (`PumpSignals.space_blocked`, `dhw_blocked`), so the plan never asks heat in the owner's case
  except under a boost. In Cooling + DHW it asks heat for hot water daily and would fight a person
  cooling on purpose. It also needs a persisted timer.
- **(c) the arbiter's Control pass writes Heating.** Unreachable: `pump_arbiter.apply` returns
  under Observe or Off duty, `_pump_off` stops the pass while the refused switch reads off, and
  `_lead_mode` follows only a gate ON.
- **(d) a state listener on the select.** A new listener lifecycle in `supply_hold.py` for at most
  one optimization interval of latency.

## Owning seam

**`custom_components/heatpump_optimizer/supply_hold.py`** owns the decision, the episode record and
the notice, as #3864 made it the owner of the gate's cooling decision. **`custom_components/heatpump_optimizer/pump_mode.py`**
gains the select write primitive (key to option, one `select.select_option` call, a refused call
logged and reported as False) and takes `pump_arbiter._option_for` with it, public, so the
vocabulary is encoded once; `pump_arbiter._service` calls the moved resolver. **The fault hold is
consulted, never re-decided**: the return calls `fault_hold.consult(entry, inp)`, the accessor
`fault_hold.gate` and `pump_arbiter.apply` already call. `fault_hold` imports `const`,
`entry_config`, `inputs`, `issues`; `supply_hold` importing it adds no cycle. Callers only:
`coordinator.py` (two call sites, no new state), `config_flow.py`, `entry_config.py`, `const.py`.

## Shape

- **Option.** One boolean in `const.py`, default False; an `EntryConfig` field; one `_F` row in
  `config_flow.py`'s `entities_pump` step, a `BooleanSelector` shown only when a mode entity is
  assigned. Independent of Pump duty control (the gate it releases runs under every duty mode).
- **Episode record.** `ArbiterState` gains the time of the episode's last return write, beside
  `cooling_asked`; never persisted; cleared where `note_cooling` clears `cooling_asked`.
- **The return**, `async supply_hold.return_heating(entry, held, inp) -> bool`, writes only when all
  hold, in this order: the option is on; the optimizer mode is not Off; the entry is not released;
  the **live select reads a cooling mode** (never over an unavailable select or the cycle's last
  good reading); the mode slot's domain is writable (`pump_arbiter._MODE_DOMAINS`); no return in
  this episode within `RETRY_MINUTES`; and **`fault_hold.consult(entry, inp)` is False** (R1). The
  consult is last so a pass that writes nothing for another reason moves no latch it would not
  have moved. It writes the counterpart (Cooling to Heating, Cooling + DHW to Heating + DHW, Heating
  where the select offers no second).
- **Gate refusal with the option on.** `note_cooling` still sets `cooling_asked` (P2's tick retry
  flag); only `ISSUE_COOLING` is replaced by the new notice below.

**Which holds the return honours, by rule.** The set is every early return before
`pump_arbiter._command` at #3872 (`apply`, `_arbitrate`): duty Off, `entry_released`, `MODE_OFF`,
duty not Control, `_pump_off`, `_fault_stands`. Honoured: `entry_released`, `MODE_OFF`, the fault.
Not honoured, by design: duty (the option is its own opt-in to one write) and `_pump_off` (the
switch is off because the cooling gate refused it; that is the case being served).

**Call sites, composed with the `_write_supply` chain** (`class_excess_loc` and `module_excess_loc`
at zero headroom; no new `coordinator.py` line).
1. **Cycle.** #3864's per-cycle `note_cooling` line (coordinator.py, after `pump_signals.read`)
   moves above the `self._pump_signals = ... pump_signals.read(` assignment and becomes `await
   supply_hold.cycle_pass(self.entry, ...)`: return if due, then `note_cooling` with no heat asked.
2. **Gate.** `supply_write` becomes async, takes `entry` first and calls the return before its
   cooling check. It stays **innermost**: the outer gates see the value they would see had a person
   set Heating. As FAULT-HOLD leaves `_write_supply` (#3872 coordinator.py:7784) and FROST-HOLD adds
   its gate, the one statement reads
   `value = fault_hold.gate(self.entry, held, inp, frost_hold.gate(held, inp, supply_hold.hold_supply(held, ..., await supply_hold.supply_write(self.entry, held, ...))))`:
   `await` and `self.entry` are added inside the existing expression, no line. If FAULT-HOLD's
   fallback lands instead (`_write_supply` leaves the class as `supply_hold.write_gated(coord, on)`),
   the same awaited call is the innermost term inside `write_gated` and `coordinator.py` is untouched
   at this site. Whichever form is on main at the fixer's merge base is the one composed with.
3. **Under a latched fault** the return writes nothing, the cooling check refuses the ON (`None`),
   `hold_supply`, frost and `fault_hold.gate` pass `None` unchanged: no mode write and no switch
   write, as FAULT-HOLD's table asks. `cooling_asked` stands, so the tick re-offers each minute; the
   first tick after the clear writes the return, then the ON. The cadence record is empty, since
   nothing was written, so the return is due at once.

```
cycle: _update_current_state -> cycle_pass: option, not Off, live Cooling, ..., not faulted -> pump_mode write
         -> pump_signals.read -> solve -> _write_supply(on)
gate:  fault.gate( frost.gate( hold_supply( await supply_write: return_heating if due -> cooling? None : on )))
tick:  supply_tick (cooling_asked) -> _write_supply -> same chain -> ON once the select reads heating
```

- **Notice.** With the option on, a new repair, "the pump stays in cooling after the optimizer
  wrote a heating mode", once per episode when the select still reads cooling `ECHO_GRACE_S` after a
  return write; it clears with the episode. Under the fault hold no return is written, so only
  `pump_fault_hold` is raised. With the option off, `ISSUE_COOLING` behaves as at #3864.

**Invariants.** No switch-on while the live select reads cooling, option on or off. No return over
an unreadable select, with the optimizer Off, with the entry released, while the fault hold holds,
or with the option off. At most one return per `RETRY_MINUTES` per episode. `ArbiterState.written`
is untouched, so `hold` and `_not_held` see no write of theirs.

**Latency.** Synchronous acknowledgement: all in the cycle. Lagged: the ON at the first tick
(`_TICK`, one minute) after the select reads heating; the space plan at the next cycle.

## Sibling sites

Two axes, each by its rule, at #3864 0f9fc88ff3 and #3872 d6a54399a6:
- **Cooling class:** `git grep -n "select_option\|_option_for\|cooling_mode(\|capability.cooling\|\.cooling\b" -- custom_components/heatpump_optimizer`.
  `_service` calls the moved resolver. `desired`, `_mode_for`, `early_cutoff._exempt` read the live
  select, hands-off until the acknowledgement. `supply_write`, `note_cooling` change.
  `pump_signals` `FREEZE_COOLING` and the `cooling` diagnostics key are unchanged. The `pump_mode`
  docstring ("Written only by pump_arbiter") names the return. `README.md`'s repair bullet and
  `docs/configuration.md`'s cooling bullet gain the option's exception.
- **Pump actuation writers** (R1), FAULT-HOLD's own rule:
  `grep -n "services.async_call\|switch_supply(\|write_setpoint(\|write_setpoint_c(\|async_publish_ecl110_command(" custom_components/heatpump_optimizer/*.py`.
  The return adds one member, the new `services.async_call` in `pump_mode.py`. Its row in
  FAULT-HOLD's "While holding" table: **mode select (the return): today none; with the option, one
  return per episode; under the hold none.** Every other member keeps FAULT-HOLD's disposition. The
  frost hold's row writes a heating mode too; the two never disagree, and the return consults no
  frost state.

## Evidence plan, by file

`tests/features.py`, beside #3864's cooling block; its `_cg_coord` fixture gains the option, a fault
slot, and a select whose `select_option` sets the state or leaves it (the lag).
- **E1 entry state, synchronous.** Cooling, option on, a boost, switch off: one
  `_update_current_state`, then `_write_supply`: `select_option` Heating, then `turn_on`, no repair.
  **Null control:** option off: no select call, no `turn_on`, `ISSUE_COOLING` raised.
- **E2 lagged.** One select call, no `turn_on`; the state set to Heating, `supply_tick` at +1 min:
  `turn_on`, no second cycle. **Null control:** state left Cooling: no write; the new repair after
  `ECHO_GRACE_S`.
- **E3 counterpart.** Cooling + DHW to Heating + DHW; with that option absent, Heating.
- **E4 no write**, one check each: optimizer Off; select unavailable over a Cooling last good
  reading; a `sensor` mode slot; select reading Heating; entry released; **the fault slot on for 11
  minutes (FAULT_HOLD_AFTER passed): no `select_option`, no `turn_on` at the cycle or at the tick,
  `pump_fault_hold` raised, no cooling-return repair. Null control:** the same fixture with the
  fault reading a fresh off: `select_option` then `turn_on`. **Then the clear:** fault set off,
  `supply_tick` at +1 min: `select_option`, then `turn_on` at that tick or the next.
- **E5 cadence.** Two cycles inside `RETRY_MINUTES`: one write; a third after it: a second. Leaving
  cooling clears the record.
- **Mutation targets.** Each guard: the option, live-cooling-only, Off, released, writable domain,
  the cadence, **the fault consult** (E4's fault case must fail). The counterpart map. The moved
  cycle call (deleted, and moved back below the read: E1 fails). `supply_write`'s
  return-before-check order. `cooling_asked` set on refusal with the option on (E2 fails). The
  notice branch. The primitive's False.
- **Goldens:** none move with the option off by default; an `EntryConfig` key in a diagnostics
  fixture is not value-bearing. No claim file changes.
- **Strings:** the option's label and description, the repair's title and description, in
  `strings.json` and `translations/` en, sv, de; `docs/configuration.md`: the option, default off,
  what it writes, and that it writes nothing while the fault hold holds.

## Hot files, serial position, carries

Hot: `coordinator.py`, `supply_hold.py`, `pump_arbiter.py`, `pump_mode.py`, `const.py`,
`entry_config.py`, `config_flow.py`, the four string files, `docs/configuration.md`, `README.md`,
`tests/features.py`, `tests/entities.py`.
**Serial (orchestrator ruling):** R11-OWNER-FLOWCAP, R11-OWNER-FROST-HOLD, R11-OWNER-FAULT-HOLD,
**this group**, R11-OWNER-MODE-LEGS, R11-OWNER-STEP-KICK. The fixer branches from main after #3864
and FAULT-HOLD's #3872 have merged, never before.
**Structure payment, this group's alone:** `_option_for` leaves `pump_arbiter.py` (over
`MODULE_LOC_LIMIT`) for `pump_mode.py`; it pays `config_flow.py`'s row. None of FAULT-HOLD's
payments (`duty_ledger.py`, the `_select` re-spells, `write_gated`) and none of FROST-HOLD's
(`log_skip`), FLOWCAP's, MODE-LEGS' or STEP-KICK's are counted. If the move does not cover the row,
the fixer looks for a further sound move; only after none exists, a raise under mandate 6893738184
with a `## Raise justification` and its archscore line.
No grader registration expected; if `ci_predict.py` prints `BOOTSTRAP` for the log-flood registry in
`tests/entities.py`, split p1/p2 by `fixer.md` step 7.

## Decisions routed to the owner (defaults stated, the fixer builds the default)

- Q1: write the counterpart rather than plain Heating. Default: counterpart.
- Q2: retry every `RETRY_MINUTES` per episode rather than once. Default: retry.
- Q3: an early refresh when a lagged acknowledgement lands. Default: not built.

## Notes for the fixer

- Check that `InputReader` in `_update_current_state` reads `hass.states` when called; otherwise move
  call site 1 above the reader's construction, still net zero.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N1)
- A warning log on the return is per write, bounded by the cadence; register it in
  `_R10_LOG_ALLOWED_BY_REASON` beside `note_cooling`'s entry.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N2)
- Re-measure with `python3 tests/structure.py` at the merge base and head; carry no figure.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N3)
- If `fault_hold`'s accessor is renamed or its signature changes in #3872's merge, call whatever
  `fault_hold.gate` calls; the guard is "the same answer the gate gets", not a name.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N4-fault-accessor)
- MODE-LEGS and STEP-KICK follow this group: the return is a mode writer their notes compose with.
  Carry: R11-OWNER-MODE-LEGS (item return-mode-writer)
