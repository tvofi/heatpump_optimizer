# Design note: R11-OWNER-FAULT-TEXT -- record the pump's fault codes for diagnostics (rev 3)

Rev 2 answered `design-verdict/R11-OWNER-FAULT-TEXT` 45a37ffb (revise,
architecture-unsound, R1-R5 and eight carries, on 86338c13). Rev 3 applies the
owner's ruling of 2026-11-22, relayed by the orchestrator, which overrides R1:
"I think it should suggest it." (the fault-alarm entity). Only the Discovery
paragraph, test 9, the release note, the sibling-site line and one carry
moved from rev 2. Code read at
`origin/main` eaaaf24e5b; no predecessor handoff head exists. Coordinates with
`design/R11-OWNER-FAULT-HOLD` 57d5d278 (approved, not built). Evidence: the
owner's report, verbatim: "The Tuya heat pump integration exposes the problem
description, p3 e5 etc. Make the optimizer ingest this data so it is visible in
the diagnostics file". **No finder harness: owner report.** The private bundle
is never committed; every value below is invented.

## What exists today (checked first)

- `grep -rn "FAULT_ENTITY" custom_components/heatpump_optimizer/*.py`: one
  flag slot, `CONF_HEAT_PUMP_FAULT_ENTITY`, sampled once per update cycle by
  `pump_signals.read` into `PumpSignals.fault`; the diagnostics carry that one
  boolean. A fault that clears inside a cycle is never seen, and no code text
  is read (`docs/configuration.md`: "never the code itself").
- Sources: the Tuya integration's model `000004k4z6` decodes dp 20 into a
  "Fault Description" sensor (model key `fault_description`): `OK` or a comma
  list such as `E5, P3`. The GCHV Modbus package
  (`docs/modbus/rotenso_windmi_gchv.yaml` in the tuya_heat_pump repository)
  spreads its codes over four "HP Alarm bitmap N" sensors: `OK` or a comma
  list of names ending in the code, e.g. `IPM protection (P6)`.

## Behaviour

**Slot.** New option `heat_pump_fault_text_entities`, **optional**, a list of
1 to 4 entities (`sensor`, `text`, `input_text`), options-only on the
`entities_pump` page beside the Fault alarm row, no `topology._SLOTS` row (the
electric-heat slots' precedent). The 4-member cap is validated in the step
with its own error string (`EntitySelector(multiple=True)` does not enforce it).

**Discovery (owner ruling over R1; R2).** Both slots are suggested.
- **Fault alarm (flag slot), restored from rev 1:** `device_prefill._TUYA_HEAT_PUMP`
  gains `("binary_sensor", "fault")`, and `modbus_prefill._NAMED` gains
  `CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.{p}_alarm"`. The GCHV
  package's "HP Alarm" is an OR over the four alarm registers. `_NAMED` is a
  scalar entity slot, so `infer`'s existing loop suggests it on both the
  device path and the Modbus path, and no new shape is needed. As with every
  prefill row, it is a suggestion applied only where the slot is empty and
  the person accepts it.
- **What accepting it changes:** it brings the install under three existing
  readers of the slot:
  - FAULT-HOLD (57d5d278): after 10 minutes of fault, actuation is held and a
    repair is raised.
  - The learner freeze: `pump_signals` sets `FREEZE_FAULT` while the slot reads on.
  - The duty-switch void: `pump_arbiter._switch_context` voids an episode that
    has a fault in it.
- **GCHV warnings:** the GCHV alarm registers can carry non-blocking warnings
  (for example a sensor-fail bit while the unit runs), and "HP Alarm" reads on
  for them too. Such an install holds as if latched. The way out is the
  `fault_hold` opt-out on the options page, which ends the hold but not the
  freeze or the void.
- The prefill page's description and `docs/configuration.md` state all of the
  above beside the suggestion.
- **Fault text:** `_TUYA_HEAT_PUMP` gains `("sensor", "fault_description")`
  for the text slot.
- **Signatures are unchanged.** A table row applies only to a device its
  signature already proves, and such a device already has tabled roles, so
  `prefill_offer.qualifies` reads the same for every device. The flag slot
  read stays strict (see below).
- `modbus_prefill.infer` suggests entity slots only from `_NAMED`. It gains a
  second loop over a new one-key tuple of **list slots**, suggesting
  `[snap[slot][0]]`, a one-member list. `_prefill_fits` passes a non-number
  widget, and `_prefill_fields` renders the suggestion through the row's
  `multiple=True` widget unchanged. About 4 lines.
- **GCHV list prefill is cut.** It would need a list role: `ResolvedRole`
  ("ids tried in order, first match wins") would change meaning, `snapshot`
  would keep every id that resolves rather than the first, and `infer` would
  join them. That is about 20 lines over three functions whose null control
  compares the role map byte for byte against the merge base, all to save a
  GCHV person picking four sensors by hand. `docs/configuration.md` names the
  four sensors to pick.

**Source of an episode** (one rule per install; `source` in the view):

| configured | `source` | open while | code text |
|---|---|---|---|
| text list | `text` | any member reads a fault text | the fault members' items, slot order |
| flag slot only, integral number | `bitmap` | strict read True | `0x` + hex (`2080` and `2080.0` give `0x0820`) |
| flag slot only, other | `flag` | strict read True | null: times only |
| neither | null | -- | no listener, no store |

**The flag reading (R3)** is the canonical one:
`parse_bool(state, strict=not is_flag_domain(entity_id))`, the rule
`InputReader.read_bool` applies. A `sensor` fault slot reading `heating` gives
None and records nothing, as `pump_signals` and FAULT-HOLD read it. A
non-integral number such as `1.5` reads True and records as `flag`.
`unavailable`, `unknown` and None change nothing.

**The text reading (R3, decided).** A member is **healthy** when its state,
stripped and case-folded, is in: `ok`, `none`, `normal`, `no fault`, the empty
string, `BOOL_FALSE`, or `AMBIGUOUS_ACTIVITY_TOKENS`. **Every other text is
recorded as a code**, including `defrosting`, `cooling`, `on` and
`Unit in heat mode`. The reason: the slot exists for vocabularies this
integration does not know, and an unknown word is exactly the code a person
needs to see. The cost is that a status sensor put in the slot fills the
record with its words. `docs/configuration.md` says the slot wants a fault
description and that the record shows whatever the entity says, a person's
own `input_text` included.

**Code text and truncation (R5).** The members' states are split on `, ` into
items, kept in slot order, and joined with `, `. Items are kept whole while
the text stays within 160 characters, and ` +N` counts the items dropped. A
single item longer than 160 keeps its **last** 160 characters behind `…`,
because GCHV names end in the code. A row's text is therefore at most 168
characters. `IPM protection (P6), 3x high discharge temp in 100 min (H6)` is
kept whole, so two different code combinations never collapse into one prefix.

**Clock.** A state-change listener on the slot's entities: the faults that
matter clear in under a minute. Each event is stamped with the new state's
`last_changed`, in seconds. A change of text while open closes the row and
opens the next at that instant.

**Record (R4).**
- **Holder:** `fault_log._RECORDS`, a `WeakKeyDictionary` keyed by the config
  entry (the `off_restore._RECORDS` precedent). A reload keeps the same entry
  object, so setup **replaces** the record, never reuses it.
- **Contents:**
  - `episodes`: a ring of at most **200** closed rows `[start_s, end_s, text, late]`, oldest evicted first.
  - `dropped`: the number of evicted rows.
  - `open`: `[start_s, text]` or null.
  - `codes`: per text `[count, total_s, last_end_s]`, at most 32 texts plus `other`.
  - `since_s`: when the record began.
- **Saves.** The store is a `QuarantiningStore` keyed by the entry id, with a
  `store.DOMAINS["fault_log"]` schema row. It is saved on every **open and
  close**, limited to one save per 60 s. A save asked for inside the window is
  **deferred, never dropped**: one `async_call_later` timer saves at the
  window's end.
- **Stop and unload.**
  - Setup registers `entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, ...))`,
    because Home Assistant does not unload entries at stop. The coordinator
    hooks stop itself for the same reason.
  - The stop handler and `async_unload_entry` call one
    `fault_log.async_close(entry)`. It **unsubscribes the listener, cancels the
    timer, then saves**, and is idempotent: the second call finds the record closed.
  - `__init__.async_unload_entry` calls it beside the `room_record` flush,
    before Home Assistant runs the `async_on_unload` callbacks. The listener is
    not registered through `async_on_unload`: its handle is on the record, so
    nothing fires after the save.
- **Restart.** At load, an `open` row is continued when the first read gives
  the same text. Otherwise it closes at that read's time with `late = true`:
  it cleared while Home Assistant was down, and the end is an upper bound.
- **Bound,** measured with `sys.getsizeof` over a row list, its two ints and a
  168-character string:
  - A row is 361 B, so the ring is at most 73 kB. The 33-key tally is at most
    14 kB.
  - The saved JSON is at most about 48 kB.
  - Steady state writes nothing. A sustained 1 Hz flap writes one save a
    minute, about 69 MB a day, bounded.
  - Memory is fixed once the ring is full, so the D9 B4 retained-growth slope
    is zero.

**Diagnostics.** `diagnostics._VIEWS` gains
`("fault_log", lambda c: fault_log.diagnostics_view(c.entry))`. The download's
`coordinator.fault_log` holds `source`, `entities`, `open`, `episodes` newest
last with ISO times and `seconds`, `dropped`, `codes` and `since`. It is null
when no source is configured. **No redaction beyond today's passes**:
`_without_private_ids`, `async_redact_data` and the value pass run over the
whole payload. The debug bundle reads every `DOMAINS` store. The replay keeps
a `_entities` list of ids, and `text_ok` drops a comma-bearing state.

## Owning seam and shape

Owner: `fault_log.py` (new), a leaf importing `const`, `inputs` and `store`,
imported only by `__init__.py` and `diagnostics.py`. It is **not** part of
`fault_hold.py`, which is an in-memory actuation guard over the flag slot,
consulted once per arbiter pass and off under its `fault_hold` opt-out. This
record reads another slot, must see sub-minute faults, must persist, and must
work with the hold off or the flag slot absent. There is no coordinator line
and no `tests/seam_map.json` row.

- `async_setup(hass, entry, config)`: builds the record (replacing any old
  one), loads it, subscribes, and registers the stop hook. Does nothing when
  there is no source.
- `async_close(entry)`: unsubscribe, cancel the timer, save; idempotent.
- `diagnostics_view(entry) -> dict | None`.
- Pure core, testable without Home Assistant: `note(record, now_s, text) -> bool`
  (whether it opened or closed a row), `code_text(states) -> str | None`,
  `loaded(raw)` and `stored(record)`.

```
pump entity ─ state_changed ─ _on_event ─ code_text ─ note ─ ring/tally ─ save|defer (≤1/60 s)
setup ─ async_setup ─ load ─ continue|close-late ─ subscribe ─ stop hook
stop event | async_unload_entry ─ async_close ─ unsubscribe ─ cancel timer ─ save
Download diagnostics ─ _VIEWS ─ diagnostics_view
```

## Alternatives

1. Read the text in `pump_signals.read`. Lost: it runs once per cycle, so the
   sub-minute faults the investigation lacked stay invisible.
2. Build it inside `fault_hold.py`. Lost: state ownership and the opt-out, as above.
3. A list role for GCHV prefill. Lost: R2's cut, explained above.
4. Decode a raw bitmap into labels. Lost: the bit labels are model-specific,
   while the hex is exact.
5. Read recorder history at download time. Lost: the purge window, an
   excluded recorder, and executor work on every download.

## Sibling sites

`grep -rn "CONF_HEAT_PUMP_FAULT_ENTITY" custom_components/heatpump_optimizer/*.py`:
`pump_signals`, `pump_arbiter._switch_context`, `topology`, `config_flow` and
`const` are unchanged in code. The restored prefill rows change who reaches
them (see Discovery). Other Tuya models'
description sensors are out of scope for prefill, because no signature proves
them; the slot itself covers them.

## Evidence plan

Every case fails first and has its null control. `tests/features.py` holds the
core, listener, lifecycle and prefill cases; `tests/finite_boundary.py` derives
the store; `tests/config_flow_steps.py` holds the row and the cap error;
`tests/doc_claims.py` checks the docs.

1. `OK`→`E5`→`OK` 40 s apart gives one row of 40 s with `E5`. Null: `OK`→`OK`
   gives none. `ok`, `Ok` and `OK` all read healthy.
2. `E5`→`E5, P3` gives two rows at one instant. `unavailable` mid-episode does
   not close the row.
3. GCHV, two members faulted: the items are kept in slot order. A two-fault
   bitmap-3 text keeps `(P6)` and `(H6)` whole. 30 items give the kept items
   plus ` +N`, at most 168 characters. A single 300-character item keeps its tail.
4. Flag slot only:
   - `on`/`off` on a binary sensor gives a `flag` row.
   - `2080` and `2080.0` give `0x0820`.
   - `heating` on a `sensor` fault slot records nothing (strict). Null: the same
     state on a `binary_sensor` domain stub reads through the flag path.
5. Text decision: `heating` and `idle` record nothing; `defrosting` and
   `Unit in heat mode` record a row.
6. Lifecycle:
   - 120 flaps in 120 s give at most 3 saves, and the last state is saved by the
     deferred timer. Null: with the limiter mutated away, 120 saves.
   - Open, then the stop event, then reload: the row continues with its
     original start.
   - Open, then unload, then an event fired after close: no row and no save.
   - A stored `P3` with a first read of `OK` closes `late`.
7. Ring and tally:
   - 250 episodes keep 200 and record `dropped` 50.
   - 40 texts give 32 plus `other`, and the totals equal the sum over all 250.
8. Diagnostics:
   - The section is built from invented rows, and is null with no slot.
   - A code text equal to an entry name of at least `replay_doc.LEAK_MIN_CHARS`
     characters comes out redacted, while a non-matching text is kept.
9. Prefill:
   - Signed Tuya records suggest a one-member text list and the `fault`
     binary sensor for the flag slot.
   - A GCHV prefix suggests `binary_sensor.<p>_alarm` for the flag slot and
     no text slot (the list is cut).
   - Null: without the signature there is no suggestion. With the flag slot
     already set, it is not suggested.
   - `qualifies` is unchanged on its threshold fixtures.
10. Synthetic replay (no install data): 24 h with one multi-hour `P3` and
    twelve sub-minute `E5`s gives 13 rows and a tally of 12 for `E5`. Null:
    sampling per 30-min cycle, today's path, sees at most 2.

Mutation targets: the healthy set, the strict flag, the unavailable skip, the
text split, item truncation and the tail, both caps and `dropped`, the save on
open, the deferred timer, the close order (unsubscribe before save), the stop
hook, the continue/late branch, the view's null branch, and the list-slot loop
in `infer`.

## Hot files, serial position, structure payment

Hot files:
- `fault_log.py` (new), classified into a measured closure in `tests/closures.json`.
- `__init__.py`, `diagnostics.py`, `store.py`, `device_prefill.py`, `modbus_prefill.py`.
- `config_flow.py`, `const.py`.
- `strings.json`, `translations/en.json`, `translations/sv.json`, `translations/de.json`.
- `docs/configuration.md`, and the tests above.

There is no `pump_arbiter.py` or `coordinator.py` change.

**Order:** FLOWCAP > FROST-HOLD > FAULT-HOLD > **FAULT-TEXT** > MODE-LEGS >
STEP-KICK. This group shares no function with the others. It follows
FAULT-HOLD for these shared edits: the `entities_pump` rows, `const.py`, the
translations and the Fault alarm doc row. It can be built in parallel now, and
yields its slot rather than hold up MODE-LEGS.

**Structure.** Every metric is at zero headroom at eaaaf24e5b
(`python3 tests/structure.py`).
- **`module_excess_loc`.** Of the touched modules, only `config_flow.py` is
  over `MODULE_LOC_LIMIT`. It gains about 5 lines: the row, the import, the
  cap check and the error.
  - **Payment, claimed by this group alone:** `_user_sensors_fields` spells
    12 plain `vol.Optional(K): _prefill_row(K).widget` lines whose keys
    `_USER_SENSORS_GROUPS` already lists. They are built from that tuple, with
    the two defaulted keys as overrides, for a net of about −6.
  - This is distinct from FAULT-HOLD's payment (three selector functions) and
    MODE-LEGS' (`_valid_months_spec`).
  - If a reconfigure field order moves, the order test decides. The fallback is
    a selector shared with `_room_thermometers`.
- **`duplication_copies`.** If the load and save code clones `room_record`'s,
  both move to one `store.py` helper.
- Measure at the head and the merge base, and run `tools/audit/archscore/`
  around each move. A raise goes under mandate 6893738184 with a
  `## Raise justification`, settled before the push.

**Docs and release.**
- `docs/configuration.md`: a Fault text row (what it records, the free-text
  caveat, the four GCHV sensors), and the Fault alarm row loses "never the
  code itself".
- `docs/architecture.md`: one module line.
- Release note. It **leads with** the suggestion, ahead of everything else
  in the entry: "The heat pump pre-fill now suggests the pump's Fault alarm
  entity (the Tuya integration's Fault Alarm, the GCHV Modbus package's HP
  Alarm). Accepting it means that while the pump reports a fault, the
  optimizer stops changing the pump after 10 minutes (Fault hold), pauses its
  learning, and discards the duty-switch measurement. The GCHV alarm
  registers also report non-blocking warnings; if those hold your pump, turn
  *Fault hold* off. With a Fault text entity configured (pre-filled for the
  Tuya integration), each fault's code, start and end are kept for the last
  200 episodes and appear in Download diagnostics."

## Notes for the fixer

- Carry: R11-OWNER-FAULT-TEXT (multi-entry). The store key carries the entry
  id, so two entries on one pump keep two records.
- Carry: R11-OWNER-FAULT-TEXT (bundle-count). A new harness,
  `dev/audit/harnesses/r11_owner_fault_text.py` `<bundle.json>`, prints counts
  only (episodes and distinct texts) from a downloaded bundle. The owner runs
  it, and the bundle is never committed.
- Carry: R11-OWNER-FAULT-TEXT (flag-prefill-reach). The flag-slot suggestion
  brings an accepting install under FAULT-HOLD, `FREEZE_FAULT` and the
  duty-switch void (owner ruling 2026-11-22). The prefill page text, the docs
  row and the leading release-note line say so. If FAULT-HOLD has not merged
  when this group lands, the text names only the freeze and the void, and
  FAULT-HOLD's own docs row adds the hold.
- Carry: dismissed: no finding asks FAULT-HOLD's repair text to name the live
  code; it is left for a later owner call.
