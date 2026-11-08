# R10-GENERIC-HEAT-CURVE-PERSISTENT design note (designer seat, note 2, a re-cut)

This is the group's architect note, extended (`dev/governance/roles/designer.md`), at
`design/R10-GENERIC-HEAT-CURVE-PERSISTENT`. It never merges. Size L. **There is no finding and no finder harness.
No finder harness: owner report.** The evidence is the owner's rulings (tvofi, #201, 2026-11-07: "Offset kind and
a later persistent kind, both in this round. Turning the optimizer off should restore the baseline"; issue comment
6708225978: "Arbiter too"), the contributor's request (PR 3284, Bankaifan, fork head
16058355161065c24aaf9eeba496133240527c0f, read as data, its §Target contract (b) P1–P7 and O1–O5) and the research
body restated below.

**Read at.** Base `996ded2a6dc52816bd4c7dd873c048d85fc6adad` (= `origin/main`). The predecessor's handoff head is
#3299 at `85ba6cda83898bb3fcc1dee71432c1622f14a72e` (`verdict/3299` dfd0a3f7: `Fix review: merge`, not yet merged).
Its production tree equals d7d4c511, the head the round-1 review read, except the version stamp. Every
`off_restore.py`, `heat_curve.py` and `__init__.py` line below is at 85ba6cda. This re-cut answers
`design-verdict/R10-GENERIC-HEAT-CURVE-PERSISTENT` ae96e235 (`revise e2d81a61 architecture-unsound`), points 1–4
(§Answers to the review).

## Owning seam

There are two modules, and each concern has one owner. No concern is split between them.

- **`custom_components/heatpump_optimizer/off_restore.py`** owns everything persisted per entry, including the
  baseline: the armed record, the baseline capture, the MODE_OFF and unload restore, and the remove path. This group
  changes it in four named ways (§Shape, C1–C4). It gains no consumer knowledge.
- **`custom_components/heatpump_optimizer/heat_curve.py`** owns kind `persistent`'s mapping and write policy. It is
  a second `Restorer` (kind `persistent`, `neutral=None`) of the existing consumer key `heat_curve`. It persists
  nothing itself.

Callers only, unchanged in shape: `async_publish_ecl110_command` → `heat_curve.publish`; `async_set_mode`
(coordinator.py:6490) and `async_unload_entry` (`custom_components/heatpump_optimizer/__init__.py`:426) →
off_restore; `async_remove_entry` (`__init__.py`:438) → `async_forget`. Also `config_flow.py`, `entry_config.py`,
`sensor.py` and `diagnostics.py`. **No `baseline.py`, no second Store, no call from heat_curve.py at remove, and no
coordinator line.**

## Shape

**Options.** Add the value `persistent` to `HEAT_CURVE_TARGET_KINDS` (a value, not a key). This drops the fallback
at entry_config.py:222-224 for that value. Add three keys, each an `EntryConfig` field and a `_F("heat_curve", …)`
row shown only under kind `persistent`: `heat_curve_persistent_band_k`, `heat_curve_persistent_writes_per_day` and
`heat_curve_persistent_min_dwell_minutes`. The baseline is not an option (O1 does not arise). The options flow keeps
P7 as a **check only**: under kind `persistent` it refuses a save whose entity is unreadable or reads outside its
own range. It stores nothing.

**off_restore changes (C1–C4), each owned by off_restore alone:**

- **C1, the armed entry holds the entity (review point 3, carry a2b5f107).** Today `armed[key]` is
  `float | None` (:88). It becomes `{"entity_id": str, "value": float}`, where `value` is what the restore writes:
  the `neutral`, or the captured baseline. The restore writes the **recorded** value to the **recorded** entity
  (rule R).
  - `async_restore` (:149) uses the current factory only for its `write`. When the factory returns None, a
    writer registered per key at import supplies it: `register_consumer(key, factory, write)`. `Restorer.write` is
    removed, so there is one source.
  - `async_arm` (:123) on a key armed for entity A while the restorer now names B first restores A from the
    record. Only on success does it arm B, which captures B's baseline. A failed A restore is latched, and the
    write to B is refused. A key is armed on at most one entity.
  - **The legacy reader:** a stored `float | None` (the only shape #3299 writes, all from the neutral offset
    consumer) loads as `{entity_id: <the configured entity>, value: <its neutral>}`. That is exactly today's
    behaviour, so `OFF_RESTORE_STORE_VERSION` stays 1 and no migration runs.
  - `restored(entry, value)` becomes `restored(entry, entity_id, value)`. A consumer ignores a restore of an
    entity it no longer names.
- **C2, re-baseline (P6).** `async_rebaseline(hass, entry, key, entity_id, value) -> bool` replaces the armed
  value when `key` is armed on `entity_id`, saves, and returns True. Otherwise it writes nothing and returns False.
  The first arm keeps its baseline forever (:135), so this is the only way a baseline moves, and off_restore is its
  one owner.
- **C3, consumer state (write-ahead "previous", P4, P5; review point 1 bullet 2).** A second section of the same
  record, `{"armed": {...}, "state": {key: mapping}}`, is persisted per key and survives a restore, which pops
  only `armed`:
  - `consumer_state(entry, key) -> dict`, which is mutable;
  - `async_save_state(hass, entry)`.

  off_restore never reads inside a consumer's mapping. The restore loop's existing `_save` (:180) persists what
  `restored` changed. `async_forget` drops it with the rest, so remove keeps one owner.
- **C4, remove (review point 2).** `async_forget` (:197) reads the record before it deletes the Store. For each
  entry still armed (a failed unload restore), it logs one WARNING naming the entity and the value to set by hand.
  **It writes nothing**, so remove stays off_restore's alone. A retry at remove was rejected: the unload restore
  tried the same write moments before, and remove has no coordinator or config to judge it.

**heat_curve's persistent arm (the consumer).** `_restorer(config)` returns, for kind `persistent`,
`Restorer(entity_id, neutral=None, baseline_of=_baseline_reading, restored=_restore_recorded)`. Its persisted
state is `consumer_state(entry, "heat_curve")` = `{written, previous, written_at (UTC ISO), day (local date),
count}`. Kind `offset` keeps its in-memory `HeatCurveState`, byte for byte (I4). One publish, with `d` the
displace integer:

```
publish(d) ─► reading = number_reading(entity)            (unreadable / range: latched, not written)
   armed = off_restore record for heat_curve on entity      (None before the first write)
   b = armed.value if armed else reading                    (the arm captures exactly this reading)
   classify(reading, state):   ≈ written → ours   ≈ previous → refusal (W3 latch)   else, after HELD_GRACE_S → edit
       edit and armed → b := reading − delta(last d); off_restore.async_rebaseline(…, b); INFO   (P6)
   target = setpoint_step(clamp(b + delta(d), b ± delta(band), entity min/max))      (P2, I1)
   W1 reading ≈ target → nothing
   dwell: now − written_at < dwell → nothing                (P5; wall clock, so it survives restart and reload)
   budget: count + 1 + (target ≠ b) > writes_per_day → refused, INFO once per day (P4 + reserve rule)
   off_restore.async_arm(…)  → False: not written           (first arm persists {entity, b}; O3)
   state.previous, state.written = state.written, target; count += 1; await async_save_state  (write-ahead)
   write_setpoint(entity, target)
MODE_OFF / unload ─► off_restore.async_restore (unchanged owner) ─► write b to the recorded entity
   ─► restored(entry, entity, b): state.written = b, written_at = now, count += 1     (persisted by the restore's _save)
remove ─► off_restore.async_forget: WARNING per still-armed entry, delete record    (C4)
```

The **reserve rule** `+ (target ≠ b)` keeps one write back for the restore. So restores never exceed the budget,
and every displace has its way home. This is the research's "12/day = 6 displace-and-restore episodes". Kind
`persistent` uses this persisted budget **instead of** W4's `write_cap_per_day` (heat_curve.py:274), not on top of
it (carry ghcp-r2). A budget of 0 means no writes. With nothing displaced, there are no restores either.

**Off rule** (owner, 2026-11-07): MODE_OFF and every unload restore the baseline, a reload and a Home Assistant stop
included, as #3299 already does (`__init__.py`:424-425). P3's stop exception is dropped. A reload's unload passes the
loaded coordinator's `effective_config` (`__init__.py`:427), which names the old entity. So an options change
from A to B on a loaded entry restores A before B is armed. Rule R covers the remaining path: a crash, or a failed
restore, followed by a changed config.

**Invariants.**
- I1: the entity never leaves `b ± band`.
- I2: writes per local day ≤ `writes_per_day`, restores included.
- I3: every MODE_OFF or unload leaves each armed entity at its recorded value, or leaves a latched failure that is
  still armed.
- I4: with kind `offset` or no entity, no behaviour, payload, golden or record shape moves (the legacy reader).
- I5: a key is armed on at most one entity, and nothing restores a value onto an entity other than the one it was
  captured from.

## Answers to the review (ae96e235)

1. The baseline lives only in off_restore's armed record. The consumer-private state lives in C3's `state` section
   of that same record, with C2 and C3 as the named API. There is no second Store.
2. There is no `heat_curve.async_remove`. Remove is off_restore's alone (C4: it logs and writes nothing, for the
   reason given there).
3. C1 persists the entity, and rule R restores to the recorded entity. The evidence plan carries the arm "armed on
   A, options to B, restart → A restored, B untouched". R10-ARBITER-OFF-RESTORE gets C1 for free as the second
   consumer. Whichever group lands first carries C1: `decision: orchestrator`.
4. `baseline.py` is dropped. Classify reads heat_curve's own write state, so it stays in heat_curve.py. The shared
   baseline is off_restore's armed record. The arbiter consumes C1 and C2 and adds no module.

## Defaults (O5), restated from the research body

Source: `handoff-body/r10-ghc-research` `52f5a44257ada6ed2b85d959337e1585dbd1cc72`, BODY.md (probe seat, tree
a37c58e5). Tags: D documented, F forum, E estimate, S snippet only.

| knob | default | range | reason and sources |
|---|---|---|---|
| band | 3 K | 0.5–5 K | Luxtronik user correction ±5 K (Homey Luxtronik app, D third-party); NIBE SG Ready +1/+2 offset steps (manualslib S1256PC p.44, D; step-to-K E); 3 K a midpoint (E) |
| writes/day | 12 | 0–48 | Daikin EKMBDXA guide "7000 per year" ≈19/day (P1P2Serial PR 87, F quoting D; budulinek Daikin-P1P2 gateway, D); 12 × 5475 d on a 100k SLC NAND cell (Micron datasheet, D) = 66 %; 12 rather than 19 rests on wear levelling (E) |
| dwell | 60 min | 15 min–6 h | 3τ with radiator τ ≈ 20 min (enpal.de, F); the SG-Ready 10 min minimum (gridx.ai, D secondary) is the floor; floor heating 2–3 h (GWF Stuttgart sheet, F) |

- python-luxtronik README (D): parameter writes reach NAND, and SHI registers are volatile. So the docs prefer kind
  `offset` wherever a volatile register exists, and use `persistent` only otherwise.
- Unverified: NIBE 1M writes (energiesparhaus.at, F/S) and the ioBroker counters (F/S).
- No data was found for Vaillant, Stiebel Eltron, Mitsubishi or Panasonic.
- The 48/day maximum is above Daikin's quota, and the option's description says so.

## Alternatives, and why each lost

- **A. The baseline in the options (contributor P1).** Every P6 adoption reloads the entry
  (`__init__.py`:373-399), and each reload costs a restore plus a rewrite (O1). It lost on call count.
- **B. heat_curve's own Store for the write state** (note 1's record without its baseline). The state must outlive a
  restore, so it cannot sit in `armed`. A second per-entry Store, though, needs a second remove owner, or off_restore
  knowing about it. It lost on remove-path ownership to C3.
- **C. Disarm with an INFO when the recorded entity differs** (the review's other option). A stays displaced
  forever, by up to the band, on a non-volatile parameter, which is the harm the off rule exists to undo. It also
  drops the retry a failed restore keeps today (off_restore.py:24-25). It lost to rule R on the off rule.
- **D. Skip the restore on reload and on stop (P3).** It saves two writes per reload, but contradicts "on unload"
  and #3299's tree. The reserve rule already bounds the cost. It lost on the ruling.
- **E. A separate `baseline.py`.** Its only content would be classify, which reads heat_curve's state, plus record
  helpers that off_restore owns. It lost on coupling: it would be a third module for one record.

## Sibling sites (step 5)

`git grep -n "off_restore\.\|MODE_OFF\|async_unload_entry\|async_remove_entry\|async_shutdown" 85ba6cda -- custom_components/heatpump_optimizer/`

| site | disposition |
|---|---|
| `async_set_mode` → `async_mode_change` coordinator.py:6490; unload `__init__.py`:426; remove `__init__.py`:438 | the one hook, unchanged callers; C1–C4 change only off_restore |
| `heat_curve.publish(..., mode_off=...)` coordinator.py:7671, off guards coordinator.py:7676, 8817 | upstream of the arm; the OFF write is the hook's |
| other `MODE_OFF` guards coordinator.py:3750, 4512, 7695, 7757, 10831 | other writers (valve, pump on, frequency); not the heat curve |
| `async_shutdown` coordinator.py:6554 | the restore runs before it, in unload, unchanged |
| pump_arbiter.py:1131-1139 off rule, its Store pump_arbiter.py:1354-1393 | R10-ARBITER-OFF-RESTORE's; it becomes off_restore's second consumer through C1 and C2 and is not edited here |

## Evidence plan (by file)

- **Failing test first**, in `tests/features.py`, beside #3299's heat-curve block. Kind `persistent`, entity
  `number.x` (°C, 5…35, step 0.5, state 22), no record. `async_publish_ecl110_command(2.0, True)` writes 24, and
  the off-restore record holds `{entity_id: number.x, value: 22}`. It is red at 85ba6cda because the unknown kind
  falls back to offset, whose `range_excludes_zero` refuses 5..35 (carry ghcp-r1). It is not red because the kind is
  refused.
- **Arms (heat_curve).**
  - band clamp (d = 8 → 25) and the °F delta;
  - W1 no call;
  - the dwell holds a second change and releases it after;
  - budget 4 with the reserve: one displace plus its restore pass, and a second displace is refused;
  - MODE_OFF and unload each write 22 once, and `restored` marks 22 as written;
  - the dwell and the count survive a restart (a new coordinator, same record);
  - crash residue (written 24, reading 24, still armed): 22 is kept and not re-captured (O3);
  - write-ahead crash (reading = previous) reads as ours;
  - edit (reading 21 while written 24, d = 2): adopts 19 through `async_rebaseline`, then restores 19;
  - local midnight resets the count;
  - with kind `persistent`, W4 is not consulted.
- **Arms (off_restore).**
  - **"armed on A, options to B, restart → A restored, B untouched, then B armed with its own baseline"**;
  - the A restore fails → the B write is refused and latched, and A stays armed;
  - the entity is cleared with A armed → A restored through the registered writer;
  - `async_rebaseline` on a wrong entity → False and no save;
  - the legacy `float | None` record loads as before;
  - `async_forget` with an armed entry logs one WARNING, writes nothing and deletes the record;
  - the `state` section survives a restore and is dropped by `async_forget`.
- `tests/config_flow_steps.py`: kind `persistent` is accepted, its three rows appear only under it, the ranges are
  enforced, and P7 refuses an unreadable or out-of-range entity.
- **Null control:** with kind `offset` or an empty entity, #3299's checks and every MQTT payload are unchanged, and
  the stored record is byte-identical to #3299's for kind `offset`, with no `state` key written.
- **Goldens:** none move (I4). No claim file is touched.
- **Mutation targets:**
  - the reserve comparison, the band clamp, the dwell comparator and the day key;
  - each classify branch;
  - C1's mismatch test and the legacy-reader branch;
  - C2's guard and C4's armed loop.

  New sites are killed or triaged (`tests/mutation_budgets.json`).

## Cost against the ratchet

`tests/structure_budgets.json` has several metrics at zero headroom. No coordinator line is added. heat_curve.py
grows: split publish's decision into classify, clamp, dwell and budget to keep `functions_cc_over_15` flat, and
watch `GOD_CLASS_LOC_LIMIT`. off_restore.py grows by roughly 40 lines. No raise is expected. A raise needs the
owner first (CLAUDE.md rule 2).

## Docs

- `docs/ecl110.md`, "Kind persistent": the baseline record, I1–I3, the off rule (reload and stop included), the
  reserve rule, rule R, the three defaults with their tags, a note that the budget rests on E/F/S evidence, and
  "prefer offset where a volatile register exists".
- `docs/configuration.md`: the rows.
- `README.md`: the surface row.
- `strings.json` and translations.

## Hot files and serial position

`off_restore.py`, `heat_curve.py`, config_flow.py, const.py, entry_config.py, sensor.py, diagnostics.py, the
strings and translations, docs/ecl110.md, docs/configuration.md, README.md, tests/features.py and
tests/config_flow_steps.py.

`__init__.py` is no longer touched. The fixer starts after #3299 merges. R10-ARBITER-OFF-RESTORE shares
`off_restore.py` (C1, C2). It goes serially after this group, or it lands C1 itself if it goes first:
`decision: orchestrator`.

## Routed, not built here

- `decision: orchestrator`: R10-ARBITER-OFF-RESTORE's brief still reads "on unload (while Home Assistant is not
  stopping)". One hook carries one rule, and the hook restores on a stop (`__init__.py`:424-425), so that brief
  should be re-read against the 2026-11-07 ruling.
- `decision: owner` (ghc-d02, carry 711d4be1): whether the MQTT ECL110 arms also publish displace 0 on MODE_OFF and
  unload. It is not built, because W7 keeps MQTT byte-identical.

## Notes for the fixer

- The build PR carries `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>` (owner ruling,
  relayed 2026-11-07). Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-01)
- Cite each default to its source line in the research body. The user docs say that the budget and band rest
  partly on F, S or E evidence. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-02)
- Re-read #3299's merged diff before starting: `Restorer`, `async_arm`, `async_restore`, `async_forget`,
  `restored`, `state_for` and the delta conversion. If any of them moved, the designer revalidates.
  Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-03)
- U4 (what the Luxtronik "parallel shift" parameter is) stays open. If it is a foot point, `b + d` rotates the
  curve about the end point. The docs say so and do not call it a parallel shift.
  Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-04)
- Classify any new test script in `tests/closures.json` or on `tests/closure.py`'s INERT list. No new production
  file is created. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-05)
- R10-ARBITER-OFF-RESTORE registers a consumer with `neutral=None` and arms before its first write. It takes its
  baseline from C1's record, adopts edits through C2 and keeps no baseline in its own Store. It adds no owner of
  unload, MODE_OFF or remove. Carry: R10-ARBITER-OFF-RESTORE (item ghcp-06)
- A Home Assistant stop may unload the target integration first. The restore then fails, latches and stays armed,
  so the next off or unload retries it (off_restore.py:24-27). Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-07)
- The failing test's reason is the offset fallback's `range_excludes_zero`, not a refused kind (review note).
  Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r1)
- The persisted budget replaces W4 for kind `persistent` and does not stack on it. 
  Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r2)
- The citations are refreshed to 85ba6cda in this note (coordinator.py:6490/6554, inputs.py:597, `__init__.py`:426/438,
  entry_config.py:289). Re-check them at the merged head. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r3)
- C3's `written_at` is wall clock (UTC), not monotonic, because it must survive a restart. A clock step backwards
  reads as "dwell not elapsed" only until the clock passes it again. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r4)
