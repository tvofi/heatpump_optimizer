# Design note: R11-OWNER-FAULT-TEXT -- record the pump's fault codes for diagnostics

Code read at `origin/main` eaaaf24e5b; no predecessor handoff head exists.
Coordinates with `design/R11-OWNER-FAULT-HOLD` 57d5d278 (approved, not built).
Evidence: the owner's report, verbatim: "The Tuya heat pump integration
exposes the problem description, p3 e5 etc. Make the optimizer ingest this
data so it is visible in the diagnostics file". **No finder harness: owner
report.** The private bundle is never committed; every value below is invented.

## What exists today (checked first)

- `grep -rn "FAULT_ENTITY" custom_components/heatpump_optimizer/*.py`: one
  slot, `CONF_HEAT_PUMP_FAULT_ENTITY`, a flag. `pump_signals.read` samples it
  once per update cycle (30 min by default) into `PumpSignals.fault`; the
  diagnostics carry that one boolean. A fault that self-clears inside a cycle
  is never seen, and no code text is read anywhere (`docs/configuration.md`
  says so: "never the code itself").
- Neither prefill table discovers the fault slot: `device_prefill._TUYA_HEAT_PUMP`
  and `modbus_prefill._NAMED` have no fault row.
- Sources: the Tuya integration's model `000004k4z6` decodes dp 20 into a
  "Fault Description" sensor (model key `fault_description`) reading `OK` or
  a comma list such as `E5, P3`, beside the "Fault Alarm" binary (key `fault`).
  The GCHV Modbus package (`docs/modbus/rotenso_windmi_gchv.yaml` in the
  tuya_heat_pump repository) splits its codes over **four** text sensors,
  "HP Alarm bitmap 1..4" (`OK` or a comma list of long names), plus the
  binary "HP Alarm".

## Behaviour

**Slot.** New option `heat_pump_fault_text_entities`: **optional, a list of
1 to 4 entities** (`sensor`, `text`, `input_text`), options-only on the
`entities_pump` page beside the Fault alarm row, with no `topology._SLOTS`
row (the electric-heat slots' precedent: not a place on the diagram).
**Discovered alongside the fault slot**: `_TUYA_HEAT_PUMP` gains
`("sensor", "fault_description")` for the text list and
`("binary_sensor", "fault")` for `CONF_HEAT_PUMP_FAULT_ENTITY`; `_NAMED`
gains the GCHV package's `binary_sensor.{p}_alarm` and its four
`sensor.{p}_alarm_bitmap_N` for the list. Both are suggestions on the prefill
page, applied only where the slot is empty and the person accepts; signatures
are unchanged, so no other model resolves them.

**Source of an episode** (one rule, per install):

| configured | episode is open while | code text |
|---|---|---|
| text list | any member reads a fault text | members' fault texts, slot order, joined `"; "` |
| fault slot only, numeric state | `parse_bool` reads True (non-zero) | `0x` + hex of the integer (`0x0820`) |
| fault slot only, flag state | `parse_bool` reads True | none (`null`): times only |
| neither | -- | no listener, no store, no record |

A member reads **healthy** at `OK`, `None`, `Normal`, `No fault`, an empty
string, a `parse_bool` False, or a word in `inputs.AMBIGUOUS_ACTIVITY_TOKENS`
(a status sensor placed in the slot never records "heating" as a code); any
other text is a fault text, stripped, at most 48 characters per member.
`unavailable`/`unknown` changes nothing: it neither opens nor closes.

**Clock.** A state-change listener (`async_track_state_change_event`) on the
slot's entities, not the cycle and not the per-minute arbiter tick: the faults
that matter here clear in under a minute. Each event is stamped with the new
state's `last_changed`, seconds. A change of text while open closes the
episode and opens the next at the same instant, so each row carries one text.

**Record** (per config entry, persisted):
- `episodes`: a ring of at most **200** closed rows `[start_s, end_s, text,
  late]`, epoch seconds, oldest evicted first; `dropped` counts evictions.
- `open`: `[start_s, text]` or null.
- `codes`: per text, `[count, total_s, last_end_s]`, at most **32** texts;
  a 33rd text tallies under `other`. The tally outlives ring eviction, so a
  flapping code cannot hide the long one's existence.
- `since_s`: when the record began.
- Bound: a row is under 300 bytes in Python (two ints, a text of at most
  4 x 48 + 6 characters, a flag), so the ring is under 60 kB and the tally
  under 6 kB: fixed, not growing with time, so D9 B4's retained-growth slope is
  zero once full.
- **Restart.** The store is a `QuarantiningStore` keyed
  `heatpump_optimizer_<entry_id>_fault_log`, saved on each closed episode
  (rate-limited to one save per 60 s, so a 1 Hz flap writes the card once a
  minute) and at unload. At load an `open` row is continued when the first
  read gives the same text; otherwise it closes at that read's time with
  `late = true` (it cleared or changed while Home Assistant was down; the end
  is an upper bound). A store schema row `DOMAINS["fault_log"]` in `store.py`
  bounds every leaf, so the finite-boundary sweep and the debug bundle's store
  read (`debugger`, every `DOMAINS` name) both include it.

**Diagnostics.** `_VIEWS` gains `("fault_log", ...)`: the download's
`coordinator.fault_log` holds `source` (`text`, `flag`, `bitmap` or null),
`entities`, `open`, `episodes` newest last with ISO times and a `seconds`
field, `dropped`, `codes`, `since`. Null when neither slot is configured.
**Not redacted beyond today's passes**: the texts are the pump's own codes and
the entity ids follow the file's "ids are kept" rule; `_without_private_ids`,
`async_redact_data` and the value pass run over it unchanged. The replay half
needs nothing: `replay_doc._entry_shape` keeps a `_entities` list of ids, and
`text_ok` drops a comma-bearing state (`E5, P3`) to null, which is why the
replay is not the channel.

## Owning seam and shape

Owner: `fault_log.py` (new), a leaf importing `const`, `inputs`, `store`;
nothing imports it but `__init__.py` and `diagnostics.py`. Not in
`fault_hold.py`: that module is an actuation guard over the flag slot,
in-memory by design (its latch re-seeds from `last_changed`), consulted once
per arbiter pass, and off under its `fault_hold` opt-out. This record reads a
different slot, must see sub-minute faults, must persist, and must work with
the hold off or the flag slot absent; one module would make the opt-out blind
the diagnostics and give `fault_hold` a store. No coordinator line, no
`tests/seam_map.json` row (it maps coordinator methods only).

- `async_setup(hass, entry, config) -> None` -- registers the listener with
  `entry.async_on_unload`; nothing when no source.
- `async_flush(entry) -> None` -- saves the open row at unload.
- `diagnostics_view(entry) -> dict | None`.
- Pure core: `note(record, now_s, text_or_none) -> bool` (closed a row) and
  `loaded(raw) / stored(record)`, unit-testable without Home Assistant.

```
pump entity ─ state_changed ─ fault_log._on_event ─ healthy? ─ note ─ ring/tally ─ save (≤1/60 s)
__init__ setup ─ fault_log.async_setup ─ load ─ continue|close-late ─ listen
__init__ unload ─ fault_log.async_flush
Download diagnostics ─ diagnostics._VIEWS ─ fault_log.diagnostics_view
```

## Alternatives

1. Read the text in `pump_signals.read` -- lost: once per cycle; every
   sub-minute fault is invisible, the very episodes the investigation lacked.
2. Inside `fault_hold.py` -- lost, reasons above (state ownership and opt-out).
3. One text entity, not a list -- lost: on the GCHV package it records one of
   four alarm registers; a template joining them is work the prefill can do.
4. Decode a raw bitmap into labels -- lost: bit labels are model-specific
   (the Tuya corpus has 16-, 23- and 30-bit fault maps); the hex is exact and
   the person's manual reads it.
5. Recorder history at download time (the replay's path) -- lost: bounded by
   the recorder's purge window (10 days by default), absent with the
   recorder excluded, and read in the executor on every download.

## Sibling sites

`grep -rn "CONF_HEAT_PUMP_FAULT_ENTITY" custom_components/heatpump_optimizer/*.py`:
`pump_signals` (freeze, unchanged), `pump_arbiter._switch_context` (void,
unchanged), `topology` (card slot, unchanged), `config_flow` (row, unchanged),
`const` (horizon, unchanged). `grep -n "fault" ~/tuya_heat_pump/custom_components/tuya_heat_pump/models/*.py`
lists other Tuya models' description sensors; out of scope for prefill (no
signature proves them), covered by the slot itself.

## Evidence plan

Failing first; each case has a null control. Tests in `tests/features.py`
(core, listener, prefill), `tests/finite_boundary.py` (derives the new store
on its own), `tests/config_flow_steps.py` (the row), `tests/doc_claims.py`.

1. Text `OK`→`E5`→`OK` 40 s apart: one row, 40 s, `E5`. Null: `OK`→`OK`: none.
2. `E5`→`E5, P3`: two rows at one instant. `unavailable` mid-episode: no close.
3. GCHV list, members 2 and 4 faulted: text joins both in slot order.
4. Flag slot only: `on`/`off` give a null-text row; `2080` gives `0x0820`;
   `heating` in a text member records nothing.
5. Ring: 250 episodes keep the newest 200, `dropped` 50; 40 texts tally 32 +
   `other`; tally totals equal the sum over all 250 (null: cap removed by
   mutation fails it).
6. Restart: open `P3` stored, first read `P3` → continued; first read `OK` →
   closed `late`. Save limiter: 120 flaps in 120 s → at most 3 saves.
7. Diagnostics: the section with invented rows; null when no slot; a code
   text equal to the entry name comes out redacted (the value pass reaches it).
8. Prefill: Tuya records with the signature suggest both slots; without the
   signature, neither (null).
9. Synthetic replay (no install data): 24 h with one multi-hour `P3`, twelve
   sub-minute `E5`; the view lists 13 rows and the tally `E5` 12. Null: the
   same timeline sampled per 30-min cycle (today's path) sees at most 2.

Mutation targets: the healthy-vocabulary test, the unavailable skip, the
text-change split, the ring cap and `dropped`, the tally cap, the restart
continue/late branch, the save limiter, the view's null branch.

## Hot files, serial position, structure payment

Hot: `fault_log.py` (new, classified into a measured closure in
`tests/closures.json`), `__init__.py`, `diagnostics.py`, `store.py`,
`device_prefill.py`, `modbus_prefill.py`, `config_flow.py`, `const.py`,
`strings.json`, `translations/en.json`, `translations/sv.json`,
`translations/de.json`, `docs/configuration.md`, the tests above.
**No `pump_arbiter.py`, no `coordinator.py`.**

**Order:** FLOWCAP > FROST-HOLD > FAULT-HOLD > **FAULT-TEXT** > MODE-LEGS >
STEP-KICK. It shares no function with any of them; it follows FAULT-HOLD
because both write the `entities_pump` rows beside the fault-entity row,
`const.py`, the three translations and the Fault alarm row of
`docs/configuration.md`. It may be built at once in parallel; if not ready
when MODE-LEGS is, it yields its slot rather than hold that chain.

Structure (every metric at zero headroom at eaaaf24e5b, `python3 tests/structure.py`):
- `module_excess_loc`: only `config_flow.py` of the touched modules is over
  `MODULE_LOC_LIMIT` (+2: the row, the import name). **Payment**:
  `_user_sensors_fields` spells ten plain `vol.Optional(K): _prefill_row(K).widget`
  lines whose keys `_USER_SENSORS_GROUPS` already lists; build them from that
  tuple with the two defaulted keys as overrides. Net about -8. Distinct from
  FAULT-HOLD's (its three selector functions) and MODE-LEGS'
  (`_valid_months_spec`). If a reconfigure form's field order moves, the order
  test decides; fallback: the row's `multiple` selector built inline from
  `_room_thermometers`' shape, generalised to one function, deleting that one.
- `duplication_copies`: `fault_log`'s load/save must not clone
  `room_record._load`/`_persist`; if the detector reads a clone, both move to
  one `store.py` helper (a payment).
- `const.py`: one name. `const_modules_over_50`, `coordinator_attrs`:
  unchanged. Measure head and merge base, and `tools/audit/archscore/` before
  and after the move; a raise goes under mandate 6893738184 with a
  `## Raise justification`, settled before the push.

Docs: `docs/configuration.md` (a Fault text row; the Fault alarm row loses
"never the code itself"); `docs/architecture.md` one module line. Release
note: "With a Fault text entity configured (pre-filled for the Tuya
integration and the GCHV Modbus package), each fault's code, start and end
are kept, up to the last 200 episodes, and appear in Download diagnostics."

## Notes for the fixer

- Carry: R11-OWNER-FAULT-TEXT (fault-slot-prefill) -- discovery of the flag
  slot also widens FAULT-HOLD's reach on installs that accept it; the body and
  the release note say so.
- Carry: R11-OWNER-FAULT-TEXT (multi-entry) -- the store key carries the
  entry id; two entries on one pump keep two records, by design.
- Carry: R11-OWNER-FAULT-TEXT (bundle-count) -- `dev/audit/harnesses/r11_owner_fault_text.py`
  (new) `<bundle.json>` prints counts only (episodes, distinct texts) from a
  downloaded bundle, run by the owner; the bundle is never committed.
- Carry: dismissed: no finding asks FAULT-HOLD's repair text to name the
  live code; a later owner call.
