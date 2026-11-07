# R10-GENERIC-HEAT-CURVE-PERSISTENT design note (designer seat, note 1)

The group's architect note, extended (`dev/governance/roles/designer.md`), at
`design/R10-GENERIC-HEAT-CURVE-PERSISTENT`; it never merges. Size L. **There is no finding and no finder harness:
the evidence is the owner's ruling** (tvofi, #201, 2026-11-07: "Offset kind and a later persistent kind, both in
this round. Turning the optimizer off should restore the baseline, retract my 26 september ruling"), the
contributor's request (PR 3284, Bankaifan, fork head 16058355161065c24aaf9eeba496133240527c0f, read as data) and
the research body below. No finder harness: owner report.

**Read at.** Base `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76` = `origin/main` at writing. The predecessor
R10-GENERIC-HEAT-CURVE has dispatched its fixer but has no handoff head, so the code is read at the base; its
approved note is `design/R10-GENERIC-HEAT-CURVE` tip `6564b0c7f40c5c81b7d9556ed3dcda8926d91bad`, approved by
`design-verdict/R10-GENERIC-HEAT-CURVE` `16e67bb5cbc00b87718008c6818b5fed176df13f` with carries ghc-d01…d07. This
note starts from that note's §Target contract (b), P1–P7 and O1–O5, and builds on its module, which is not yet in
the tree.

## Owning seam

`custom_components/heatpump_optimizer/heat_curve.py` (created by the predecessor) owns kind `persistent` too: the
mapping, the write policy, the record and the restore. One owner, as the predecessor note's §Owning seam states and
ghc-d01 makes the restore owner. Callers only: `async_publish_ecl110_command` (unchanged), the predecessor's
MODE_OFF and unload calls (reused, not duplicated), `async_remove_entry` (`custom_components/heatpump_optimizer/__init__.py`:429,
one new call), `config_flow.py`, `entry_config.py`, `sensor.py`, `diagnostics.py`. A pure helper,
`custom_components/heatpump_optimizer/baseline.py` (new, no `hass`), holds the baseline classification both this group and
R10-ARBITER-OFF-RESTORE need (§Shared baseline). No coordinator method or attribute is added.

## Shape

**Options.** Kind value `persistent` added to `CONF_HEAT_CURVE_TARGET_KIND` (a value, not a key, as the
predecessor arranged). Three new keys beside it: `heat_curve_persistent_band` (K), `heat_curve_persistent_writes_per_day`,
`heat_curve_persistent_min_dwell_minutes`, each an `EntryConfig` field and a `_F("heat_curve", ...)` row shown only
under kind `persistent`. **The baseline is not an option** (this solves O1): it lives in the record.

**The record** (solves O1, O2, O3). A per-entry `QuarantiningStore` keyed by the entry id, like the arbiter's, in the
shape of the arbiter's ownership record (`_store`/`_persist`/`_load`,
`custom_components/heatpump_optimizer/pump_arbiter.py`:1354-1393):
`{entity_id, baseline, written: [value, at], previous: [value, at], day: "YYYY-MM-DD", count}`. Written
**before** each entity write (write-ahead: a crash between the save and the call leaves a reading equal to
`previous`, which `baseline.classify` reads as ours). An options save no longer touches it, so P6 adoption costs no
reload; the budget and dwell survive reload and restart.

**Value.** `written = baseline + delta(d)` in the entity's own unit, `delta` the predecessor's T1 conversion
(identity for K/°C, ×9/5 for °F, else refused), clamped to `baseline ± delta(band)`, then to the entity's `min`/`max`,
then on `setpoint_step`, sent by `write_setpoint` (inputs.py:596).
No absolute helper is used (the predecessor's K trap does not arise: only deltas are converted).

**Flow.**
```
setup ─► heat_curve.load(record) ─► reconcile(reading):   baseline.classify(record, reading)
            none        -> baseline := reading (P1; refuse at save if unreadable or outside range, P7)
            ours        -> keep baseline (O3: a crash residue at baseline+d is recognised, not captured)
            edit        -> baseline := reading − last d, INFO (P6)
          mode OFF at setup and record dirty -> restore
publish(d) ─► target = clamp(baseline + delta(d))
            W1 equal reading -> nothing
            dwell (P5) not elapsed -> wait for the next publish after it
            budget (P4): allowed iff count + 1 + (target != baseline) <= budget
            -> persist record, write, count += 1
MODE_OFF / unload ─► restore: write baseline if reading != baseline; bypasses dwell, counted, never refused
remove entry     ─► if record dirty (an unload restore failed): one restore from the record, then delete the store
```
**The reserve rule** (`+ (target != baseline)`) keeps one write back for the restore, so restores never exceed the
budget and every displace has its way home: the research's "12/day = 6 displace-and-restore episodes".

**Off rule** (owner, 2026-11-07). MODE_OFF and every unload write the baseline, including a reload (options save,
O1) and a Home Assistant stop: the ruling says "on unload" without exception, so P3's shutdown exception is
**dropped**. Cost: up to two writes per reload or restart, inside the budget by the reserve rule; after a reload the
dwell runs from the restore, so the curve sits at baseline for one dwell. A failed restore is latched and leaves
the record dirty, which setup and remove retry (O4). The pump arbiter's off rule
(`custom_components/heatpump_optimizer/pump_arbiter.py`:1131-1133) is unchanged.

**Restore hook** (solves O4). The predecessor's unload and MODE_OFF calls into heat_curve.py are the one owner;
kind `persistent` adds only a branch inside them. `async_remove_entry` runs after the unload with no coordinator,
so it calls `heat_curve.async_remove(hass, entry)`, which acts only on a dirty record and deletes the store: no
duplicated restore.

**Invariants.** I1 the entity never leaves `baseline ± band`. I2 writes per local day ≤ the budget option (0 = no
writes, restores included, since nothing was displaced). I3 every unload or MODE_OFF leaves the entity at baseline
or a latched failure with a dirty record. I4 with kind `offset` or no entity, no behaviour, payload or golden moves.

## Shared baseline (R10-ARBITER-OFF-RESTORE)

Sound to share the **logic**, not the state: `baseline.py` exposes `classify(record, reading, step) -> "none" | "ours"
| "edit"` and the record's to/from-mapping. Each owner keeps its own Store (the arbiter already has one); the
arbiter group adds a `baseline` field per slot to its own record and calls `classify`. Sharing the Store would
couple two owners' persistence (D7). Serial: this group lands `baseline.py`; the arbiter group goes after it or
reuses it from this group's branch, `decision: orchestrator`.

## Defaults (O5), restated from the research body

Source: `handoff-body/r10-ghc-research` `52f5a44257ada6ed2b85d959337e1585dbd1cc72`, BODY.md (probe seat, tree
a37c58e5). Tags: D documented, F forum, E estimate, S snippet only.

| knob | default | range | reason and sources |
|---|---|---|---|
| `_WIRING` at entry_config.py:284 | kind already added (ghc-d03); the three tuning keys reset on factory reset, the record (baseline) is untouched |
| band | 3 K | 0.5–5 K | Luxtronik user correction ±5 K (Homey Luxtronik app, homey.app/de-at/app/com.luxtronik.heatpump, D third-party); NIBE SG Ready +1/+2 offset steps (manualslib S1256PC manual p.44, D; step-to-K ratio E); 3 K a midpoint (E) |
| writes/day | 12 | 0–48 | Daikin EKMBDXA design guide "7000 per year" ≈19/day (quoted in github.com/Arnold-n/P1P2Serial/pull/87, F quoting D; github.com/budulinek/Daikin-P1P2---UDP-Gateway, D); 12×5475 d on a 100k SLC NAND cell (Micron MT29F4G08ABADAH4, D) = 66 %; 12 over 9 rests on wear levelling (E) |
| dwell | 60 min | 15 min–6 h | 3τ with radiator τ ≈ 20 min (enpal.de consumer guide, F); SG-Ready 10 min minimum (gridx.ai/knowledge/sg-ready, D secondary) is the floor; floor heating users 2–3 h (gwf-stuttgart.de sheet, F) |

python-luxtronik README (github.com/Bouni/python-luxtronik, D): parameter writes reach NAND; SHI registers are
volatile. So the docs **prefer kind `offset` wherever a volatile register exists**, and persistent only otherwise.
Unverified: NIBE 1M writes (energiesparhaus.at, F/S), ioBroker counters (forum.iobroker.net, F/S); no data for
Vaillant, Stiebel Eltron, Mitsubishi, Panasonic. 48/day is above Daikin's quota: the option's description says so.

## Alternatives, and why each lost

- **A. Baseline in the options (contributor P1).** Every adoption (P6) and capture writes the options, the listener
  reloads (`custom_components/heatpump_optimizer/__init__.py`:372-398), and each reload costs a restore plus a
  rewrite: O1. Lost on call count.
- **B. Budget and dwell in coordinator memory (P4/P5 as sketched).** Reset by every reload and restart, so not a
  budget: O2. Lost on state ownership.
- **C. Skip the restore on reload and stop (P3).** Saves two writes per reload but contradicts the owner's "on
  unload" ruling; the reserve rule already bounds the cost. Lost on the ruling.
- **D. One Store shared with the arbiter.** Two owners of one persistence; lost on coupling (§Shared baseline).
- **E. Restore from `async_remove_entry` unconditionally (O4).** Duplicates the unload restore and needs a
  coordinator it does not have. Lost on ownership.

## Sibling sites (step 5)

`grep -n "MODE_OFF\|async_unload_entry\|async_remove_entry\|async_set_mode\|async_shutdown" custom_components/heatpump_optimizer/coordinator.py custom_components/heatpump_optimizer/__init__.py`

| site | disposition |
|---|---|
| `async_unload_entry` at `__init__.py`:401, `async_set_mode` at coordinator.py:6509 | predecessor's hook (ghc-d01); this group adds a branch in heat_curve.py only |
| `async_remove_entry` at `__init__.py`:429 | one call into heat_curve.py |
| off guards `MODE_OFF` at coordinator.py:7714, :8855, :7795 | upstream of the arm; unchanged, the OFF write is the hook's |
| other `MODE_OFF` guards, coordinator.py:3768, 4533, 7733, 10880 | other writers' off guards (valve, frequency, pump on); out of scope, not heat curve |
| `async_shutdown` latch, coordinator.py:6579 | the restore runs before it, in unload, as the predecessor orders |

## Evidence plan (by file)

- **Failing test first**, `tests/features.py` beside the predecessor's heat-curve block: kind `persistent`, entity
  `number.x` (°C, 5…35, step 0.5, state 22), no record; `async_publish_ecl110_command(2.0, True)` writes 24 and
  the record holds baseline 22. Red at the predecessor's head (kind refused).
- Arms: band clamp (d 8 → 25); °F delta; W1 no call; dwell holds a second change, releases after; budget 4 with
  reserve allows one displace and its restore, refuses a second displace; restore on MODE_OFF and on unload writes
  22 once; reload restores then rewaits the dwell; crash residue (record written 24, reading 24) keeps 22; edit
  (reading 21 while written 24, d 2) adopts 19; write-ahead crash (reading = previous) is ours; unreadable or
  out-of-range at save refuses; `async_remove_entry` with a dirty record restores once and deletes the store, with a
  clean one writes nothing; day rollover at local midnight resets the count; record survives a restart.
- `tests/config_flow_steps.py`: kind `persistent` accepted, three rows shown only under it, ranges enforced, P7.
- **Null control:** kind `offset` and empty entity: the predecessor's tests and every MQTT payload unchanged, no
  store created.
- **Goldens:** none move (I4); no claim file touched.
- **Mutation targets:** the reserve comparison, the band clamp, the dwell comparator, the day key, each `classify`
  branch, the dirty check in `async_remove`. New sites killed or triaged (`tests/mutation_budgets.json`).

## Cost against the ratchet

`tests/structure_budgets.json` is at zero headroom on several metrics. No coordinator line is added; heat_curve.py
grows, so watch `GOD_CLASS_LOC_LIMIT` and `functions_cc_over_15` (split decide into clamp, dwell, budget) and
`duplication_copies` against pump_arbiter's store trio (share via `baseline.py` record helpers, ghc-d07). No raise is
expected; one needs the owner first (CLAUDE.md rule 2).

## Docs

`docs/ecl110.md` "Kind persistent": the record, I1–I3, the off rule including reload and stop, the reserve rule,
the three defaults with their tags and that the budget rests on E/F/S evidence, "prefer offset where a volatile
register exists"; `docs/configuration.md` rows; `README.md` surface row; `strings.json` and translations.

## Hot files and serial position

heat_curve.py, baseline.py (new), `__init__.py`, config_flow.py, const.py, entry_config.py, sensor.py,
diagnostics.py, strings and translations, docs/ecl110.md, docs/configuration.md, README.md, tests/features.py,
tests/config_flow_steps.py. The fixer starts after R10-GENERIC-HEAT-CURVE merges, since that group creates heat_curve.py.
R10-ARBITER-OFF-RESTORE shares baseline.py and `__init__.py`: serial, `decision: orchestrator`.

## Notes for the fixer

- The build PR carries `Co-authored-by: Bankaifan <476059+Bankaifan@users.noreply.github.com>` (owner ruling,
  relayed 2026-11-07). Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-01)
- Cite each default to its source line in the research body; the user docs say the budget and band rest partly on
  F, S or E evidence. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-02)
- Before starting, re-read the predecessor's merged diff: the restore entry points, `state_for` shape and the
  delta conversion this note reuses; if they moved, the designer revalidates. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-03)
- U4 (what the Luxtronik "parallel shift" parameter is) stays open: if it is a foot point, `baseline + d` rotates
  the curve about the end point (predecessor note A2); the docs say so and do not name it a parallel shift.
  Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-04)
- heat_curve's store file and baseline.py, plus any new test script, are new tracked files: classify them in
  `tests/closures.json` or `tests/closure.py`'s INERT list. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-05)
- R10-ARBITER-OFF-RESTORE reuses `baseline.classify` and keeps its own store; it adds no second owner of the
  unload restore. Carry: R10-ARBITER-OFF-RESTORE (item ghcp-06)
- A Home Assistant stop may unload the target integration first; the restore then fails, latches, and leaves the
  record dirty for the next setup (same as ghc-d04). Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-07)
