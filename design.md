# R10-GENERIC-HEAT-CURVE-PERSISTENT design note (designer seat, note 3, the re-cut for design round 2)

This is the group's architect note, extended (`dev/governance/roles/designer.md`), at
`design/R10-GENERIC-HEAT-CURVE-PERSISTENT`. It never merges. Size L. **There is no finding and no finder harness.
No finder harness: owner report.** The evidence is the owner's rulings (tvofi, #201, 2026-11-07: "Offset kind and
a later persistent kind, both in this round. Turning the optimizer off should restore the baseline"; issue comment
6708225978: "Arbiter too"), the contributor's request (PR 3284, Bankaifan, fork head
16058355161065c24aaf9eeba496133240527c0f, read as data, its §Target contract (b) P1–P7 and O1–O5) and the research
body restated below.

**Read at.** Base `c668197a3721e87e6b3fd2b893172cc8dd9264a7`. The predecessor is #3299 (R10-GENERIC-HEAT-CURVE,
not yet on main) at head `e066a630d3cd6a1d75e92088712b196541c5ff2a`. Between 85ba6cda, which note 2 read, and
e066a630, `off_restore.py`, `heat_curve.py`, `__init__.py` and `entry_config.py` are byte-identical (round 2's own
check), so every line cited in those files holds at e066a630; coordinator.py citations are re-anchored to e066a630
(ghcp-r8). This note answers `design-verdict/R10-GENERIC-HEAT-CURVE-PERSISTENT` ae96e235 (round 1, points 1–4) and
c9069f21 (round 2, `revise c52e3782 harness`, one point), with the orchestrator's rulings of the round-2 dispatch
(§Answers to the review). Note 2 (c52e3782) is changed only in §Shape C1, I4, I5, §Evidence plan, the citations and
the routed decisions the orchestrator has now ruled.

## Owning seam

There are two modules, and each concern has one owner. No concern is split between them.

- **`custom_components/heatpump_optimizer/off_restore.py`** owns everything persisted per entry, including the
  baseline: the armed record, the baseline capture, the MODE_OFF and unload restore, and the remove path. This group
  changes it in four named ways (§Shape, C1–C4). It gains no consumer knowledge.
- **`custom_components/heatpump_optimizer/heat_curve.py`** owns kind `persistent`'s mapping and write policy. It is
  a second `Restorer` (kind `persistent`, `neutral=None`) of the existing consumer key `heat_curve`. It persists
  nothing itself.

Callers only, unchanged in shape: `async_publish_ecl110_command` → `heat_curve.publish`; `async_set_mode`
(coordinator.py:6484, `async_mode_change` at :6491) and `async_unload_entry` (`custom_components/heatpump_optimizer/__init__.py`:426) →
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

- **C1, a baseline entry holds the entity (review round 1 point 3, carry a2b5f107; round 2 point 1, ruling
  (a)).** C1 and rule R bind **only `neutral=None` consumers**: kind `persistent` and, later, the arbiter
  (R10-ARBITER-OFF-RESTORE). A neutral consumer (kind `offset`) keeps #3299's entry `None` in `armed[key]: float |
  None` (:88) and #3299's disarm-on-unconfigured rule (:153-154, :163-165), unchanged.
  - **Entry shapes.** `armed[key]` is `None` for a neutral arm (as #3299), or `{"entity_id": str, "value": float}`
    for a baseline arm, `value` being the captured baseline. `_armed_record` (:100-113) reads a mapping as a baseline
    entry and every other value exactly as today (:105-110); `OFF_RESTORE_STORE_VERSION` stays 1 and no migration
    runs. #3299 writes only `None` (its one consumer is neutral), so no stored record changes reading.
  - **The entry's shape decides its restore, not the current config.** A `None` entry is restored by #3299's path,
    unchanged: the current restorer's `neutral` to the current entity, else disarmed unwritten. A baseline entry is
    restored by **rule R**: its recorded `value` to its recorded `entity_id`, whatever the factory now names. When the
    factory returns None (entity cleared), a writer registered per key at import supplies the write:
    `register_consumer(key, factory, write=None)`, the keyword optional so kind `offset`'s registration line and its
    `Restorer.write` stay as they are. A key with a baseline entry and no registered writer is disarmed unwritten
    with one WARNING naming the entity and value (never reached by this group's consumer, which registers one).
  - `async_arm` (:123) when the key's entry does not match the restorer it is given: a baseline entry for entity A
    under a restorer naming B, or naming a neutral kind, first restores A by rule R. Only on success does it arm
    afresh (B's baseline captured, or `None` for a neutral restorer). A failed A restore is latched, the write is
    refused and A stays armed. A `None` entry under a `neutral=None` restorer (kind changed `offset` → `persistent`
    across a crash) is disarmed unwritten, as #3299 disarms a neutral consumer no longer configured, and the arm
    then captures the baseline afresh; it never writes the old neutral onto a `persistent` target. A key is armed
    on at most one entity.
  - A write returning False counts as a failed restore (`inputs.write_setpoint`, inputs.py:597-616, returns False
    for a domain with no set-point service; :166-176 today counts only a raise). This binds baseline entries; a
    neutral entry keeps #3299's handling so I4 holds (ghcp-r5).
  - `restored(entry, value)` gains the entity: `restored(entry, entity_id, value)`. A consumer ignores a restore of
    an entity it no longer names. Kind `offset`'s `_restore_recorded` (heat_curve.py:102-111) takes the extra
    argument and ignores it: a signature change only, its state update and every write unchanged (I4).
  - Read accessor: `armed_entry(entry, key) -> {"entity_id", "value"} | None`, beside C2 in off_restore, its one
    owner; the publish flow reads `armed.value` through it (ghcp-r6).
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
  baseline entry still armed (a failed unload restore), it logs one WARNING naming the recorded entity and the value
  to set by hand. A neutral (`None`) entry is dropped silently, exactly as #3299 drops it (I4).
  **It writes nothing**, so remove stays off_restore's alone. A retry at remove was rejected: the unload restore
  tried the same write moments before, and remove has no coordinator or config to judge it.

**heat_curve's persistent arm (the consumer).** `_restorer(config)` returns, for kind `persistent`,
`Restorer(entity_id, neutral=None, baseline_of=_baseline_reading, restored=_restore_recorded)`. Its persisted
state is `consumer_state(entry, "heat_curve")` = `{written, previous, written_at (UTC ISO), day (local date),
count}`. Kind `offset` keeps its in-memory `HeatCurveState`, byte for byte (I4). One publish, with `d` the
displace integer:

```
publish(d) ─► reading = number_reading(entity)            (unreadable / range: latched, not written)
   armed = off_restore.armed_entry(entry, heat_curve)         (None before the first write)
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
   ─► restored(entry, entity, b): state.written = b, written_at = now,
        count += 1 keyed to the restore write's local day (ghcp-r9)          (persisted by the restore's _save)
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
- I4: with kind `offset` or no entity, no behaviour, payload, golden or record shape moves. C1 and rule R do not
  bind a neutral consumer, so kind `offset` still persists `{"armed": {"heat_curve": null}}` and is still
  disarmed unwritten when its entity is cleared.
- I5: for a `neutral=None` consumer, a key is armed on at most one entity, and nothing restores a baseline onto an
  entity other than the one it was captured from. A neutral consumer restores its fixed neutral to the entity the
  current config names, as #3299 does.

## Answers to the review

Round 1 (ae96e235):

1. The baseline lives only in off_restore's armed record. The consumer-private state lives in C3's `state` section
   of that same record, with C2 and C3 as the named API. There is no second Store.
2. There is no `heat_curve.async_remove`. Remove is off_restore's alone (C4: it logs and writes nothing, for the
   reason given there).
3. C1 persists the entity, and rule R restores to the recorded entity. The evidence plan carries the arm "armed on
   A, options to B, restart → A restored, B untouched". R10-ARBITER-OFF-RESTORE gets C1 for free as the second
   consumer. Whichever group lands first carries C1: `decision: orchestrator`.
4. `baseline.py` is dropped. Classify reads heat_curve's own write state, so it stays in heat_curve.py. The shared
   baseline is off_restore's armed record. The arbiter consumes C1 and C2 and adds no module.

Round 2 (c9069f21), the one point, answered by the orchestrator's ruling **option (a)**: C1's entity record and rule
R bind only `neutral=None` consumers (kind `persistent`, the arbiter); a neutral consumer keeps `float | None` and
#3299's disarm-on-unconfigured rule (off_restore.py:153-154, :163-165). I4 and the null control therefore stand as
note 2 wrote them; §Shape C1, I4, I5 and §Evidence plan are restated to say so, and the evidence plan gains the arm
proving a kind-`offset` record byte-identical to #3299's. The round-2 notes for the fixer (ghcp-r5 … r9) are folded
in: r5 and r6 into C1, r7 is moot under (a) (no legacy entry is resolved against a config: a stored `None` stays a
neutral entry), r8 in the citations, r9 into the flow.

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

`git grep -n "off_restore\.\|MODE_OFF\|async_unload_entry\|async_remove_entry\|async_shutdown" e066a630 -- custom_components/heatpump_optimizer/`

| site | disposition |
|---|---|
| `async_set_mode` → `async_mode_change` coordinator.py:6484/6491; unload `__init__.py`:426; remove `__init__.py`:438 | the one hook, unchanged callers; C1–C4 change only off_restore |
| `heat_curve.publish(..., mode_off=...)` coordinator.py:7670, off guards coordinator.py:7677, 8819 | upstream of the arm; the OFF write is the hook's |
| other `MODE_OFF` guards coordinator.py:3751, 4513, 7696, 7758, 10831 | other writers (valve, pump on, frequency); not the heat curve |
| `async_shutdown` coordinator.py:6555 | the restore runs before it, in unload, unchanged |
| pump_arbiter.py:1131-1139 off rule, its Store pump_arbiter.py:1354-1393 | R10-ARBITER-OFF-RESTORE's; it becomes off_restore's second consumer through C1 and C2 and is not edited here |

## Evidence plan (by file)

- **Failing test first**, in `tests/features.py`, beside #3299's heat-curve block. Kind `persistent`, entity
  `number.x` (°C, 5…35, step 0.5, state 22), no record. `async_publish_ecl110_command(2.0, True)` writes 24, and
  the off-restore record holds `{entity_id: number.x, value: 22}`. It is red at e066a630 because the unknown kind
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
  - the entity is cleared with A armed (kind `persistent`) → A restored through the registered writer;
  - kind `persistent` armed on A, options to kind `offset` on A, restart → A restored to its baseline before the
    first offset write arms `None`;
  - a `None` entry (kind `offset` crashed displaced), options to kind `persistent`, restart → the entry is disarmed
    unwritten and the baseline is captured afresh; 0 is never written to the persistent target;
  - a restore write returning False (no set-point service) is a failure: latched, still armed (ghcp-r5);
  - `async_rebaseline` on a wrong entity → False and no save;
  - a stored #3299 record `{"armed": {"heat_curve": null}}` loads and restores exactly as at e066a630;
  - `async_forget` with an armed baseline entry logs one WARNING, writes nothing and deletes the record; with a
    `None` entry it logs nothing, as at e066a630;
  - the `state` section survives a restore and is dropped by `async_forget`.
- `tests/config_flow_steps.py`: kind `persistent` is accepted, its three rows appear only under it, the ranges are
  enforced, and P7 refuses an unreadable or out-of-range entity.
- **Null control:** with kind `offset` or an empty entity, #3299's checks and every MQTT payload are unchanged, and
  the stored record is byte-identical to #3299's for kind `offset`, with no `state` key written.
  - **The kind-`offset` record arm (round 2, ruling (a)).** Run one script twice, at e066a630 and at the fix head:
    kind `offset` on `number.o`, publish displace 2 (arms), then (i) dump the off-restore Store's saved JSON,
    (ii) MODE_OFF and dump the writes and the Store, (iii) re-arm, clear the entity in the options, restart, MODE_OFF
    and dump the writes and the Store. The two runs' dumps are byte-identical: (i) `{"armed": {"heat_curve": null}}`,
    (ii) one write of 0 and `{"armed": {}}`, (iii) no write and `{"armed": {}}` (disarmed unwritten). Perturbation:
    applying rule R to neutral entries flips (i) to a mapping and (iii) to a write of 0, so the arm goes red.
- **Goldens:** none move (I4). No claim file is touched.
- **Mutation targets:**
  - the reserve comparison, the band clamp, the dwell comparator and the day key;
  - each classify branch;
  - C1's mismatch test, the entry-shape branch (mapping vs `None`) and the `neutral is None` guard that confines rule R;
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

`__init__.py` is no longer touched. The fixer starts after #3299 merges. **This group lands C1 and C2**
(orchestrator ruling, round-2 dispatch); R10-ARBITER-OFF-RESTORE goes serially after it, sharing `off_restore.py`,
and builds on C1 and C2 without re-landing them.

## Ruled, and carried as constraints

- Order (orchestrator, round-2 dispatch): this group lands C1 and C2; R10-ARBITER-OFF-RESTORE builds on them.
- Stop (orchestrator, round-2 dispatch): the hook's restore on a Home Assistant stop (`__init__.py`:424-427,
  untouched) stands. R10-ARBITER-OFF-RESTORE's brief, "on unload (while Home Assistant is not stopping)", is that
  group's to reconcile with this hook; it is a **constraint carried to R10-ARBITER-OFF-RESTORE**, not a change here.
  Carry: R10-ARBITER-OFF-RESTORE (item ghcp-08)

## Open owner decision (does not block this design)

- `decision: owner` (ghc-d02, carry 711d4be1): whether the MQTT ECL110 arms also publish displace 0 on MODE_OFF and
  unload. #3299's behaviour is kept unchanged (W7 keeps MQTT byte-identical); nothing in C1–C4 or the persistent arm
  depends on the answer.

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
- The citations are at e066a630 in this note (coordinator.py:6484/6491/6555/7670, inputs.py:597,
  `__init__.py`:426/438, entry_config.py:289; off_restore.py, heat_curve.py and `__init__.py` unchanged from
  85ba6cda). Re-check them at the merged head (ghcp-r8 folded in). Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r3)
- C3's `written_at` is wall clock (UTC), not monotonic, because it must survive a restart. A clock step backwards
  reads as "dwell not elapsed" only until the clock passes it again. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r4)
