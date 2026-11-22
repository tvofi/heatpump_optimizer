# Design note: R11-OWNER-COOLING-AUTORETURN -- an opt-in return to heating from a cooling mode

Revision 1. Base `origin/main` e3cb5c019b464a770cc7c6fe2fbc858ed29debf7. Code read at the
predecessor's handoff head, #3864 (R11-OWNER-COOLING-GUARD) ee4c34cd9c41c1c7ae2a5186b039edd1b88752f6;
every #3864 symbol cited below (`cooling_mode`, `note_cooling`, `ISSUE_COOLING`,
`cooling_asked`, `supply_write` in `supply_hold.py`) exists at that SHA, not on main.
Evidence: the owner's ruling (tvofi, 2026-11-22), "I want the automatic return as an
opt-in option." **No finder harness: owner report.** The failing checks below are the harness.

## Preconditions #3864 owes (its verdict `verdict/3864` b15f3816a3, `blocked`)

This design builds on two repairs that verdict owes; if #3864 lands either differently, step 9's
revalidation applies.
- **P1, readable select first.** `pump_arbiter.cooling_mode` must take the cycle's reading only
  when the select is unreadable. At ee4c34cd9c a readable Heating over a stale Cooling reading
  still reads cooling (`probe_stale_signals.log`). The return relies on a readable select being
  authoritative, both at the gate and in the per-cycle pass moved above the signal read (below).
- **P2, the tick releases a refused ON.** At ee4c34cd9c `note_supply` records the unwritten ON as
  the step's command and `supply_tick` writes only a change, so nothing re-offers it to the gate
  (`probe_release.log`). The return's switch-on, when the select acknowledges after the gate ran,
  lands through that release.
Carry: R11-OWNER-COOLING-GUARD (item P1-P2-precondition)

## Choice: (a) a declared "no cooling circuit" option, not a trigger

The option says "this install has no cooling circuit; a cooling mode is never intended".
With it on, a readable cooling mode is returned to heating whatever the plan asks. With it off,
nothing changes from #3864: the switch-on is refused in a cooling mode and released only by a person.

Alternatives, and why each lost in code:
- **(b1) outdoor temperature with hysteresis.** Two more options (threshold, band), an outdoor
  reading and a latched state in the switch gate, and it still writes Heating over a deliberate
  Cooling on any day under the threshold on an install that can cool: the intent it guesses is not
  in any reading the gate has.
- **(b2) heat demand plus a timeout.** In Cooling the planner blocks both channels
  (`PumpSignals.space_blocked`, `dhw_blocked`: Cooling has neither `space_heat` nor `dhw`), so
  the plan never asks heat and the trigger never fires in the owner's case, except under a boost.
  In Cooling + DHW the plan asks heat for hot water every day, so it would fight a person cooling
  on purpose. It also needs a persisted timer field.
- **(c) the arbiter's Control pass writes Heating** (`pump_arbiter.desired` / `_mode_for`).
  Unreachable in the owner's case: `pump_arbiter.apply` returns before writing under Observe or
  Off duty, `_pump_off` stops the pass while the switch reads off (the guard refused the switch-on),
  and `_lead_mode` only follows a gate ON, which cooling withholds.
- **(d) a state listener on the select** for an immediate return. That is a new listener lifecycle
  in `supply_hold.py` (register, unload) for a latency gain of at most one optimization interval.

## Owning seam

**`custom_components/heatpump_optimizer/supply_hold.py`** owns the decision, the return's
episode record and the notice, as #3864 made it the owner of the gate's cooling decision and its
repair. **`custom_components/heatpump_optimizer/pump_mode.py`** gains the select write primitive
(key to option, one `select.select_option` call, a refused write logged and reported as False)
and takes `pump_arbiter._option_for` with it, public, so the vocabulary is still encoded once.
`pump_arbiter._service` calls the moved resolver. Its docstring's "Written only by pump_arbiter,
per plan step" is amended to name the return. The primitive decides nothing, so the concern has one
owner. Callers only: `coordinator.py` (two call sites, no new state), `config_flow.py`,
`entry_config.py`, `const.py` (the option). No import cycle: `pump_mode` imports nothing in the package.

## Shape

- **Option.** One boolean beside `CONF_PUMP_DUTY_MODE` in `const.py`, default False. A field on
  `EntryConfig`. One `_F` row in the `entities_pump` step of `config_flow.py`, a `BooleanSelector`,
  shown only when a mode entity is assigned (`when=`). It does not depend on Pump duty control.
  The power switch gate it releases runs under every duty mode, and the option is its own opt-in
  to the one write it names.
- **Episode record.** `ArbiterState` gains the time of the episode's last return write, beside
  `cooling_asked`. It is never persisted, and it is cleared where `note_cooling` clears
  `cooling_asked`, when the mode leaves cooling.
- **The return** is one async function in `supply_hold.py`. It writes only when all of these hold:
  the option is on, the optimizer mode is not Off, the entry is not released, the **live select
  reads a cooling mode** (never over an unavailable select or the cycle's last good reading), the
  mode slot's domain is writable (`pump_arbiter._MODE_DOMAINS`), and no return was written in this
  episode within `RETRY_MINUTES`. It writes the counterpart, Cooling to Heating and Cooling + DHW
  to Heating + DHW, falling back to Heating when the select does not offer the second. The return
  then never blocks a channel the cooling mode left open.
- **Call sites, net zero `coordinator.py` lines** (`class_excess_loc` and `module_excess_loc` sit
  at zero headroom). (1) The per-cycle `note_cooling` line in `_update_current_state` moves above
  the `pump_signals.read` assignment and becomes `await` of the cycle pass: return if due, then
  `note_cooling` with no heat asked. The cycle then reads the select after the write. This ordering
  needs P1, because the pass now sees last cycle's signals. (2) `supply_write` becomes async and
  returns if due before its cooling check. `_write_supply` gains `await` inside its existing
  expression. The cycle's gate and the tick's gate (P2) both pass through it.
- **Notice.** With the option on, `note_cooling` raises a new repair, "the pump stays in cooling
  after the optimizer wrote a heating mode", instead of `ISSUE_COOLING`. It is raised once per
  episode when the select still reads cooling `ECHO_GRACE_S` after a return write, whatever the
  plan asks. It clears with the episode. With the option off, `ISSUE_COOLING` behaves as at #3864.

```
cycle:  _update_current_state
          -> supply_hold cycle pass: live select Cooling, option on -> pump_mode write (Heating)
          -> pump_signals.read   (reads Heating if the integration updated the state in the call)
          ... solve on that reading ...
        _apply_action -> _write_supply(on) -> supply_write: return if due; live select heating? ON : refuse
tick:   supply_tick (P2: a refused ON is re-offered) -> _write_supply -> supply_write -> ON once the select reads heating
```

**Invariants.** No switch-on while the live select reads a cooling mode, with the option on or off.
A return is never written over an unreadable select, with the optimizer Off, or with the option off.
At most one return write per `RETRY_MINUTES` per episode. The arbiter's own record
(`ArbiterState.written`) is untouched, so `hold` and `_not_held` see no write of theirs.

**Latency, stated.** If the select's state updates inside the blocking service call, everything
lands in the same cycle: the solve plans heat and the gate switches on. If the acknowledgement lags,
the refused ON lands at the first tick (`_TICK`, one minute) after the select reads heating (P2).
The space plan, solved on the Cooling reading, follows at the next cycle.

## Sibling sites

`git grep -n "select_option\|_option_for\|cooling_mode(\|capability.cooling\|\.cooling\b" -- custom_components/heatpump_optimizer`
at ee4c34cd9c. Dispositions:
- `pump_arbiter._service` (the mode write) now calls the moved resolver, behaviour unchanged.
- `desired`, `_mode_for` and `early_cutoff._exempt` read the live select, so they stay hands-off
  until the acknowledgement. After it, Control writes the step's mode as usual.
- `supply_write` and `note_cooling` change.
- `pump_signals` `FREEZE_COOLING` and the `cooling` diagnostics key are unchanged: the next read ends the freeze.
- The `pump_mode` docstring is amended.
- The `README.md` repair bullet ("never changes the mode back") and the
  `docs/configuration.md` "A pump in cooling is left alone" bullet each gain the option's exception.

## Evidence plan, by file

- `tests/features.py`, beside #3864's cooling block (its `_cg_coord` fixture gains the option and a
  select whose `select_option` either sets the state or leaves it, which is the acknowledgement lag):
  - **E1 entry state, synchronous acknowledgement.** Select reads Cooling, option on, a boost, switch
    off. One `_update_current_state` then `_write_supply`. Expect `select_option` Heating, then
    `turn_on`, and no repair. **Null control:** the option off gives no select call, no `turn_on`,
    and `ISSUE_COOLING` raised.
  - **E2 lagged acknowledgement.** The same cycle gives one select call and no `turn_on`. The state is
    then set to Heating and `supply_tick` runs at +1 minute: `turn_on`, with no second cycle. **Null
    control:** the state stays Cooling, so the tick writes nothing and the new repair rises after
    `ECHO_GRACE_S`.
  - **E3 counterpart.** Cooling + DHW is written as Heating + DHW. With that option absent, Heating.
  - **E4 no write,** one check each: optimizer Off, select unavailable with a Cooling last good
    reading, a `sensor` mode slot, select reading Heating.
  - **E5 cadence.** Two cycles inside `RETRY_MINUTES` give one write, a third after it gives a
    second. The mode leaving cooling clears the record, and the next episode writes at once.
- **Mutation targets.** Each guard of the return: the option, live-cooling-only, Off, writable domain,
  the cadence. The counterpart map. The moved coordinator call (deleted, and moved back below the read:
  E1 must fail). The gate's await-then-check order. The notice branch on the option. The `pump_mode`
  primitive's False on a refused call.
- **Goldens:** none move with the option off by default. If `diagnostics.py` dumps `EntryConfig`
  fields, its fixture moves, and that is an option key, not a value-bearing float. No claim file
  changes.
- Strings: the option's label and description, and the new repair's title and description, in
  `strings.json` and `translations/` en, sv, de, with `docs/configuration.md` (the option, default off,
  and what it writes).

## Hot files, serial position, carries

Hot files: `coordinator.py`, `supply_hold.py`, `pump_arbiter.py`, `pump_mode.py`, `const.py`,
`entry_config.py`, `config_flow.py`, the four string files, `docs/configuration.md`, `README.md`,
`tests/features.py`, `tests/entities.py`. Serial: the fixer branches from #3864's merge, never
before it (P1, P2). No grader registration is expected; if `ci_predict.py` prints `BOOTSTRAP`
for the log-flood registry in `tests/entities.py`, split p1/p2 by `fixer.md` step 7.

## Decisions routed to the owner (defaults stated, the fixer builds the default)

- Q1: write the counterpart (Cooling + DHW to Heating + DHW) rather than plain Heating. Default: counterpart.
- Q2: retry every `RETRY_MINUTES` while the episode lasts, the cadence of `pump_arbiter`'s own
  rewrite of a write that did not hold, rather than once per episode. Default: retry.
- Q3: an early refresh when a lagged acknowledgement lands, so the space plan does not wait for the
  next cycle. This needs one more `SupplyWiring` field and one extra solve per episode. Default: not built.

## Notes for the fixer

- Check that `InputReader` in `_update_current_state` reads `hass.states` when called, not a snapshot
  taken earlier in the method. Otherwise move point (1) above the reader's construction, still net zero.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N1)
- The return's log line, if it is a warning, is per write and bounded by the cadence. Register it in
  `_R10_LOG_ALLOWED_BY_REASON` beside `note_cooling`'s entry.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N2)
- Pay `config_flow.py`'s +1 against `module_excess_loc` with the `_option_for` move out of
  `pump_arbiter.py`. Re-measure with `python3 tests/structure.py` at the merge base. Do not carry a figure.
  Carry: R11-OWNER-COOLING-AUTORETURN (item N3)
