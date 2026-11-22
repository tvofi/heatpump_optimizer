Design review: approve cd54988f8f07bc53432956f825acdf3943562820

This is a delta review of design/R11-OWNER-FAULT-TEXT from 86338c13f1 to cd54988f8f, checked against revise points R1-R5 and the carries of design-verdict 45a37ffb0f. Code was read at origin/main eaaaf24e5b. The orchestrator ruled on R1: drop the fault-alarm discovery rows, so that discovery never widens FAULT-HOLD.

## Prior points
- R1 resolved, as the orchestrator ruled. No prefill row is added for `CONF_HEAT_PUMP_FAULT_ENTITY`; only the text slot is suggested. Test 9 pins "no flag slot". The widening question is a dismissed carry routed to the owner.
- R2 resolved by cutting scope. The GCHV list prefill is cut, and the note gives the reason (a list role would change the meaning of `ResolvedRole`). docs/configuration.md names the four sensors instead. The Tuya path checks out:
  - The `("sensor","fault_description")` row resolves only under the unchanged signature.
  - `infer` gains a list-slot loop that suggests `[snap[slot][0]]`.
  - `_prefill_fits` returns True for a non-number widget (config_flow.py:2226-2228).
  - `_prefill_row` finds the options-only row in `_OPTION_FIELDS` (:2186-2188).
  - The `qualifies` claim holds: a signature-proven device already has `tabled > 0` (prefill_offer.py:83-84), so the answer does not change for any device.
- R3 resolved. The flag reading is `parse_bool(state, strict=not is_flag_domain(entity_id))`, the same rule `read_bool` applies (inputs.py:1204-1212). Test 4 pins `heating` on a `sensor` slot as recording nothing, with the binary_sensor null. The text reading is now decided: the healthy set is case-folded, and every other word is recorded as a code. The decision has a reason, a docs caveat, and test 5 (`heating` and `idle` record nothing; `defrosting` and `Unit in heat mode` record a row).
- R4 resolved.
  - The holder is a `WeakKeyDictionary` keyed by the entry, and setup replaces the record.
  - Saves happen on open and on close, limited to one per 60 s, and a save asked for inside the window is deferred by a timer, never dropped.
  - A stop hook goes through `async_on_unload(async_listen_once(EVENT_HOMEASSISTANT_STOP))`.
  - One idempotent `async_close` unsubscribes, cancels the timer, then saves. It is called from the stop handler and from `async_unload_entry`. Because the listener handle is kept on the record, nothing fires after the save.
  - Test 6 pins three cases: open, stop, reload; an event after close; and the limiter null.
- R5 resolved.
  - Items are kept whole up to 160 characters, with ` +N` counting the items dropped. A single item over the cap keeps its tail, because GCHV names end in the code.
  - The 59-character two-fault GCHV text is kept whole (test 3).
  - The bound is re-measured. A 168-character row is 361 B by the same getsizeof method I measured at 391 B for 198 characters, so the ring is at most about 73 kB and the saved JSON about 48 kB. Writes run to about 69 MB a day under a sustained 1 Hz flap, and steady state writes nothing.
- Carries: all eight are taken into the note.
  - source-enum: a `bitmap` row, and `2080.0` reads as `0x0820`.
  - healthy-case: test 1.
  - limiter-null: test 6.
  - redaction-null: test 8.
  - member-cap: a step check with its own error string.
  - payment-claim: "claimed by this group alone", 12 lines; config_flow is +5 against -6.
  - free-text-member: the docs caveat.
  - qualifies: test 9.
  - room-record-stop stays dismissed here, routed to the D1 brief.

## Notes for the fixer
- Carry: R11-OWNER-FAULT-TEXT (list-loop-empty): the new list-slot loop in `modbus_prefill.infer` keeps the guard `_NAMED` uses, `not current.get(slot)` (modbus_prefill.py:266-268), so it never suggests over a configured list. Add the null case: a configured slot gets no suggestion.
- Carry: R11-OWNER-FAULT-TEXT (item-split): items are split on `, ` both inside members and across them. A member state with a bare `,` and no space stays one item. Pin that with one case so the truncation count ` +N` is defined.
