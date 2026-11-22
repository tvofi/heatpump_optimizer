Design review: revise 86338c13f15e9e86371986f3db7eb6e5c8f23fda architecture-unsound

This is the first review of design/R11-OWNER-FAULT-TEXT at 86338c13f1. The code was read at origin/main eaaaf24e5b, which is the note's base. The Tuya and GCHV sources were read at the local tuya_heat_pump checkout (models/000004k4z6.py, sensor.py, docs/modbus/rotenso_windmi_gchv.yaml). There is no finder harness, because this is an owner report. No private bundle was read or used.

## Revise points

- R1 (product-tradeoff-regression). The note's "Slot" paragraph adds `("binary_sensor", "fault")` to `device_prefill._TUYA_HEAT_PUMP` (device_prefill.py:124) and `binary_sensor.{p}_alarm` to `modbus_prefill._NAMED` (modbus_prefill.py:93), both mapped to `CONF_HEAT_PUMP_FAULT_ENTITY`. When a person accepts that suggestion, three things change on that install:
  - FAULT-HOLD's write hold (57d5d278) starts to apply.
  - The learner freeze applies (pump_signals.py:514-528, `FREEZE_FAULT`).
  - Duty-switch episodes are voided (`pump_arbiter._switch_context`).

  The owner's request asks only that the fault text be ingested for diagnostics. The text source alone serves that request (the note's table: "text list" wins over the flag slot), and no finding names these actuation and learner effects. The note's own carry (fault-slot-prefill) treats the effect as something to disclose, not as a change that needs a reason. Fix: drop both flag-slot prefill rows from this group and prefill only the text slot. Widening FAULT-HOLD's reach through discovery is `decision: owner`, routed separately.

- R2 (architecture-unsound). The prefill shape cannot carry a list slot.
  - `ResolvedRole.entity_ids` means "ids tried in order, first match wins" (modbus_prefill.py:72-77).
  - `snapshot` keeps one id per role (modbus_prefill.py:160-176).
  - `infer` suggests `snap[slot][0]`, a single string (modbus_prefill.py:266-268).
  - `_NAMED` is one template per key.

  So "`_NAMED` gains ... its four `sensor.{p}_alarm_bitmap_N` for the list" cannot be written in today's structures, and even the Tuya single-member case would suggest a string to a `multiple=True` selector. Note also that the device path suggests only `_NAMED` keys and registers (config_flow.py:2880-2885 into `infer`), so a `_TUYA_HEAT_PUMP` row alone suggests nothing. Fix: name the list-role extension. That means its owner (`modbus_prefill`), the type change (for example, a list role whose snapshot keeps every id that resolves), how `infer` and `_prefill_fields` render it, and the test. The other option is to cut the GCHV list prefill and state that.

- R3 (architecture-unsound). The flag-only source reads with "`parse_bool` reads True", which is non-strict. `pump_signals` and FAULT-HOLD read the same slot with `read_bool`, which is strict for a non-flag domain (inputs.py:1204-1212). Under the note's rule, a `sensor` fault slot showing `heating` or `running` is True (BOOL_TRUE, inputs.py:865-883), so it opens a null-text episode. The canonical reader returns None for the same state. One slot would then get two truth readings. Fix: read through the domain-strict rule (`parse_bool(text, strict=not is_flag_domain(entity_id))`), and add test 4's null case: `heating` in a sensor-domain fault slot records nothing.
  - The brief asked whether a status word in the text slot reads as no fault. It does only for the 8 `AMBIGUOUS_ACTIVITY_TOKENS` (inputs.py:924-927) and the BOOL_FALSE words.
  - `defrosting`, `cooling`, `dhw`, `on` and the GCHV state words such as `Unit in heat mode` are all recorded as fault texts.
  - The note's sentence "a status sensor placed in the slot never records 'heating' as a code" is true only for that word.
  - The note must state the out-of-set behaviour as decided (record it, since unknown words are the very codes) and pin it with a test. Otherwise it should say how it refuses such a sensor.

- R4 (architecture-unsound, lifecycle). The note never names where the per-entry record lives ("No coordinator line"; `async_flush(entry)`), and the unload order is wrong.
  - (a) Name the holder. The precedent is `off_restore._RECORDS`, a `WeakKeyDictionary` keyed by the entry (off_restore.py:114). Because a reload keeps the same ConfigEntry object, setup must replace the record rather than reuse the one from the previous setup.
  - (b) Home Assistant runs `entry.async_on_unload` callbacks after `async_unload_entry` returns. So the listener the note registers that way is still live during `async_flush`, which `__init__.async_unload_entry` calls beside `room_record.async_flush` (\_\_init\_\_.py:443). Events can close rows after the flush and schedule saves after the unload. Unload must unsubscribe and cancel any pending limiter timer before it flushes, and the note must say whether the limiter defers a trailing save (a timer) or drops it.
  - (c) The open row is saved only "on each closed episode ... and at unload", and the restart rule ("an `open` row is continued ...") depends on that row having been saved. Home Assistant does not unload config entries at stop, which is why coordinator.py:1945-1952 hooks `EVENT_HOMEASSISTANT_STOP` itself. A multi-hour P3 that is open across a restart therefore loses its start. That is exactly the long episode the record exists to keep.

  Fix: save on open as well as on close, under the same limiter, and flush at `EVENT_HOMEASSISTANT_STOP` through `entry.async_on_unload(hass.bus.async_listen_once(...))`. Then test 6 gains "open, stop event, reload: the row is continued with its original start".

- R5 (architecture-unsound, bound). The 48-character cap per member destroys the code in the GCHV source the note itself prefills.
  - GCHV names put the code last, in parentheses. Two faults in bitmap 3 read `IPM protection (P6), 3x high discharge temp in 100 min (H6)`, which is 59 characters, so the cut drops `(H6)`.
  - Different combinations also collapse to one prefix in the 32-text tally.
  - The size claim is also wrong at the cap. A row with a 198-character text measures 391 bytes in Python (sys.getsizeof over the list, the two ints and the string), so the ring is about 78 kB, not "under 60 kB".

  Fix: truncate on whole comma items with a `+N` suffix, or raise the member cap. Then recompute the in-memory and on-disk bound from a measured row, and add a GCHV two-fault case to test 3.

## Checked and sound
- Seam: `fault_log.py` as a leaf, separate from `fault_hold.py`. The reasons hold: a different slot, sub-minute faults, persistence, and FAULT-HOLD's opt-out. `_VIEWS` rows receive the coordinator (diagnostics.py:375-385), so the row is `lambda c: fault_log.diagnostics_view(c.entry)`, which is a hint, not a defect.
- Redaction claim: holds. All three passes run over the whole payload, including `coordinator` and the debug bundle's store documents (diagnostics.py:399-420): `_without_private_ids`, then `async_redact_data(TO_REDACT)`, then `_without_values` over the entry's private values. `debugger.store_keys` reads every `DOMAINS` name (debugger.py:103-105), so the new store row is covered. The replay allowlist derives from every `CONF_*` value (replay_doc.py:133-139), and `_entry_shape` keeps `*_entities` lists (:338-341), so the claim that the replay needs no change holds.
- Payment: the compaction of `_user_sensors_fields` (config_flow.py:1422-1452) is real, in-file deduplication against `_USER_SENSORS_GROUPS` (:1467-1487). It is distinct from FAULT-HOLD's (the three selector functions, :1174-1214), from MODE-LEGS' (`_valid_months_spec` moved to `grid_fee`), and from FLOWCAP's (an unnamed cross-module move, so an in-file compaction cannot be claimed by it). There are 12 plain keys, not ten.
- Write rate (Raspberry Pi): steady state is near zero writes. The worst case, a sustained 1 Hz flap, is one save per minute of about 50 kB of JSON (233 B per row × 200, plus the tally), roughly 70 MB a day. That rate is bounded and acceptable. The note should state the number.
- Order: FAULT-TEXT after FAULT-HOLD, for the shared rows, translations and `const.py`. It is consistent with both siblings' notes, and no sibling design claims `fault_log` or the prefill tables.

## Carries for the fixer
- Carry: R11-OWNER-FAULT-TEXT (source-enum): the diagnostics `source` lists `bitmap`, but the table has no row named that. The fixer should either name the numeric row `bitmap` or drop the word. A non-integer numeric state (`2080.0`) needs a defined hex rule.
- Carry: R11-OWNER-FAULT-TEXT (healthy-case): the healthy vocabulary is matched case-folded (`OK`/`ok`/`Ok`); pin it with a test.
- Carry: R11-OWNER-FAULT-TEXT (limiter-null): test 6's limiter needs its null control. With the limiter mutated away, 120 flaps give 120 saves.
- Carry: R11-OWNER-FAULT-TEXT (redaction-null): test 7 needs a non-matching text that is kept, and an entry name at least `replay_doc.LEAK_MIN_CHARS` long.
- Carry: R11-OWNER-FAULT-TEXT (member-cap): the 1-to-4 cap is not enforced by `EntitySelector(multiple=True)`. Validate it in the step and add an error string.
- Carry: R11-OWNER-FAULT-TEXT (payment-claim): state that the `_user_sensors_fields` compaction is claimed by this group alone, as MODE-LEGS does for its move.
- Carry: R11-OWNER-FAULT-TEXT (free-text-member): an `input_text` member carries the person's own text into the bundle when it is not healthy. Say so in docs/configuration.md.
- Carry: R11-OWNER-FAULT-TEXT (qualifies): adding prefill roles can tip `prefill_offer.qualifies` for a borderline device. Check the threshold test.
- Carry: dismissed: different stage's finding (item room-record-stop). room_record.py:93-94 says "a Home Assistant stop included", but nothing in `__init__` flushes it at stop. This goes to the D1 brief by finding-propagation, not to this group.
