# R11-OUTSIDE-ROOMS-P3: room history and the identifiability report (phase 3a), and what it records for the loop-capacity limit (3b)

Extends the phase-3 section of the approved design/R11-OUTSIDE-ROOMS-P2 note (4784b5940e, `Design review: approve` at design-verdict/R11-OUTSIDE-ROOMS-P2 e59dcfd724); nothing here changes phases 1 or 2. Base: origin/main f9b680fee43bb519996fc107c5f1c65df02683d7. Predecessors R11-OUTSIDE-ROOMS-P1 and R11-OUTSIDE-ROOMS-P2 have no handoff head (both are built to the P2 note), so the code was read at the base only; every line below is at the base. Paths are under `custom_components/heatpump_optimizer/` unless they start with `tests/`. Names without backticks do not exist yet.

## Finding

No finder harness: owner report, #3616, quoted in the P2 note. The P3 brief names three things: the loop's state as a delivery-capacity limit, per-room history, and an identifiability report. The approved P2 note re-cut the capacity limit (3b) out of this group (its "Decisions routed": "P3 is 3a only; 3b is a new group behind its own design"), for two reasons that still hold at the base: the only space-only power channel is the horizon's `power_caps`, set inside the optimizer (`power_caps_extra` is a total-draw cap, `optimizer.py:4750`), and the curve from loops-calling to deliverable heat is unknown until 3a has recorded it. This note designs 3a completely and adds to it the columns and the one report line 3b will fit on, because history not recorded cannot be recovered.

## Owning seam

One new module, room history, owns the per-room ring, its store and the report. Its ring, row builder and report are pure (numpy only, as `sysid.py:213` fits with "np.linalg.lstsq"); its glue holds one record per coordinator in a `WeakKeyDictionary`, made on first use with its own `QuarantiningStore`, the pattern of `duty_switch.py:452-462` `record_for`. Loaded once lazily and saved when dirty, as `duty_switch.py:495-512` "rec.store.async_save" does. Callers only: `coordinator.py` (one awaited cycle step beside the accuracy save, `coordinator.py:6116-6118` `_async_save_accuracy`, passing the house values as arguments, so no private reach), `sensor.py`, `diagnostics.py`, `store.py` (an entry in the table at `store.py:328` "DOMAINS: dict"), `__init__.py` (`async_unload_entry`, `__init__.py:401`, flushes the store). Readings come from P1's rooms side table through its public reader, module to module. `thermal_model.py` and `optimizer.py` are not edited (the roster's `files` names `thermal_model.py`; 3a does not need it). One owner per concern; no stop.

## Shape

```
cycle (coordinator)  --await-->  room history: note cycle(record, now, house values)
   house values: outdoor degC, floor return degC|None, measured kW|None,
                 executed step's space kW and hot-water kW (the pair _record_accuracy settles)
   room history --reads--> rooms side table: last readings (P1), valid ones only
   -> accumulate into the open period -> close period at the 30-min boundary -> ring row
   -> every 12th closed row: schedule save (async_delay_save); unload and HA stop flush
diagnostics / sensor --> room history: report(record)  (cached per ring length)
```

**Row.** One row per 30-minute period, aligned to the half hour, whatever the entry's interval (10 to 120 min, `config_flow.py:1868` "CONF_OPTIMIZATION_INTERVAL"): a 10-minute entry averages three cycles into a row, a 60-minute one leaves every other row empty. Per room: temperature (the period's last valid reading), target (last), calling share (percent of the period's valid samples with calling true; None for a `sensor` room or no valid sample). Per row, once: outdoor, floor return, mean measured power, and space share (percent of the period's cycles whose executed step had space power and no hot-water power). Every value an integer in centi-units; missing is null.

**Ring (carry r6).** Sized in time: rows older than 14 days are dropped, and the count is capped at 14 d / 30 min = `HISTORY_LENGTH` (`accuracy.py:51`) rows, which the fixed period makes the same thing. A room leaving the list drops its column at the next row; one joining starts empty.

**Store (carry 5a1c0e07).** Own `QuarantiningStore`, version 1, keyed by entry id as the duty-switch store is. Columns are stored as one comma-joined string per room and field, not a JSON list: measured on the design seat with 32 rooms by 672 rows (spike below), a list layout is 0.89 MB under a 2-space indent and the packed layout 0.29 MB under any indent. `DOMAINS` declares each column as text with `whole=` (an unparsable cell, a cell outside `ROOM_AIR_RANGE_C` (`const.py:1876`) or a length different from the time column drops that room's ring whole, never one cell). Saved every 12th row (6 h), and on unload and Home Assistant stop: a crash loses at most 6 h of a 14-day record. Factory reset keeps it (measured readings, like `energy`; the report is re-derived on every read, so no learned estimate survives a reset), so it joins neither the reset table at `coordinator.py:1452` "_FACTORY_VOID: Final" nor the restored set at `coordinator.py:1332` "def _restored_stores", and a snapshot rollback never rewrites it. It does join the census at `tests/features.py:15040` "_FR_STORES = {", which finds every `QuarantiningStore` by name.

**Report.** A pure function of the ring, recomputed only when the ring has grown. Per room, the first code that applies, in this order: no action reported (calling None throughout), short history (under 144 consecutive row pairs, three days), never calling or always calling (share at or above 50 in under 5 % or over 95 % of rows), collinear with a named room (absolute correlation of calling shares at or above 0.9 over common rows; the most correlated room is named), no response (in the fit dT = a (outdoor - T) + b calling + c over consecutive pairs, b's t-statistic under 3 or b not positive), else separable with a and b published (1/h and K/h at full calling). Every threshold is a named constant from one reasoning, not a measurement, as `duty_switch.py` states of its own. One house line for 3b: over rows with measured power and space share at or above 50, the fit of measured power on the calling fraction of counting rooms, with its slope, t-statistic and row count; verdict enough, or one of no power meter, short history, calling fraction flat (interquartile range under 0.25).

**Published.** Diagnostics: the report and the house line under one key (entity ids unredacted, as the indoor sensor's are; no free-text room name is stored, so `TO_REDACT`, `diagnostics.py:100`, is unchanged: carry 5a1c0e08). One sensor, room separability, created only when the list is non-empty (P1's conditional creation): state the count of separable rooms, attributes the per-room code and the house line. The ring itself is not published.

**Invariants.** (i) No room list: no store file is created, no sensor exists, no diagnostics key changes, and the cycle step returns before any read; plan and every golden byte-identical. (ii) Recording never moves a plan, a health reading or an input problem (the report is read by nobody but diagnostics and the sensor until phase 4). (iii) A missing room sample is null, never filled. (iv) The rings' times never run backwards: a clock step back closes no period until the clock passes the last row.

**Migration.** None: a new store at version 1, no option key.

## Spike (design seat, not in the tree)

32 rooms, 672 rows, random centi-unit columns, numpy 32 single fits plus one 32x32 correlation, 4-core Linux container: report median 1.4 to 2.3 ms over two runs of 20; store 0.29 MB compact, 1.43 MB at indent 4, 0.89 MB as lists at indent 2, 0.29 MB packed at indent 2. The fixer re-measures file size and resident memory under `tests/stress.py`; on a Raspberry Pi the milliseconds do not carry, the ratio to a solve (0.7 to 3.4 s per solve in the P2 note's table, one solve per `DEFAULT_OPTIMIZATION_INTERVAL`) does.

## Alternatives

- **Rows in the accuracy store.** Lost: that store is partly voided at factory reset and rewritten by a snapshot rollback (`_restored_stores`), coupling measured room evidence to learner rollback, and it is saved every cycle, which would write 0.29 MB each interval instead of each 6 h.
- **Read Home Assistant's recorder instead of keeping a ring.** Lost: the integration cannot guarantee retention (ten days by default), inclusion of the thermostats, or the `hvac_action` attribute's history, and a database query per report needs an executor job; the house columns would still need a ring of their own.
- **A per-room RC fit in `thermal_model.py`.** Lost: that is phase 4's model, and the report exists to say first whether it is identifiable; it would add learner state to a module whose stores factory reset voids.
- **A coordinator attribute for the ring.** Lost: state ownership (`fixer.md` step 17) and the coordinator's zero-headroom metrics; the side-table record is the tree's pattern.
- **Store one row per cycle.** Lost: the row count would then depend on the entry's interval, the carry r6 trap, and a 10-minute entry would triple the store.

## Sibling sites

`git grep -n "QuarantiningStore(" -- custom_components/heatpump_optimizer` returns every store (eighteen lines at the base, two in `store.py` itself); each has a `_FR_STORES` row and a `DOMAINS` entry, and the new one needs both. `git grep -n "_best_effort_cycle_step(" -- custom_components/heatpump_optimizer/coordinator.py` returns the cycle's steps; the new one sits after `_record_accuracy` so it reads the step the accuracy pairing settled. Out of scope: `_async_save_restored` and the snapshot ring (the store is kept, by design above).

## Evidence, by file

- `tests/features.py` (room history driven directly). Failing test first: the module symbol absent, then the assertions. Ring: three cycles at 10 min make one row whose calling share is 67 when two of three samples call; a 60-minute entry leaves alternate rows null; 15 days of rows keep 672; a removed room's column is gone at the next row. Store: a round trip is equal; one corrupt cell drops that room's ring and keeps the others; a clock step back adds no row. Null control for invariant (i): an empty list makes no store file and no row, and `_FR_STORES` gains the store as kept, with a reset case showing the file survives `async_factory_reset`.
- Report, from a synthetic history built with `simulate_step` (`thermal_model.py:4056`), one model per room, heat on while that room calls: independent calling reads separable with b within 20 % of the simulated gain; B's calling copied from A reads collinear naming A (null control: the same B with its own schedule reads separable); A's calling shuffled in time reads no response; 100 pairs reads short history; a `sensor` room reads no action reported; the house line reads enough with a simulated power proportional to calling fraction and calling fraction flat with every room calling together.
- `tests/finite_boundary.py`: the new `DOMAINS` entry. `tests/entities.py`: the separability sensor in a `collect()` with a non-empty list, absent with the default `DATA`; its name in `strings.json` and the three translations.
- `tests/stress.py`: 32 rooms by 672 rows, file size and resident memory recorded; `tests/stress_budgets.json` is not raised.
- Mutation targets: the period boundary; the 14-day cut and the row cap; each report threshold (144, 50, 5 %, 95 %, 0.9, 3) and the b sign test; the code order; the `whole=` drop; the save cadence; the empty-list early return.

## Hot files, position, carries

Roster: after R11-OUTSIDE-ROOMS-P2. 3a reads only P1's side table and list option, nothing P2 adds, so it can run after P1 in parallel with P2 (the brief's "may land first"). Hot: `coordinator.py` (one cycle step), `sensor.py`, `diagnostics.py`, `store.py`, `__init__.py`, `strings.json`, the translations, `tests/features.py`. Shared files, not a shared seam, with design/R11-OUTSIDE-HONEST-METERED-FLOOR (`store.DOMAINS`, `sensor.py`). No pinned grader added, so no p1/p2 split. Received and answered: r6 (ring in time), 5a1c0e07 (store size, cadence), 5a1c0e08 (redaction).

## Decisions routed

- decision: orchestrator. Roster P3 to read 3a only and its `after` edge to R11-OUTSIDE-ROOMS-P1; 3b becomes its own group, designed once a live install's house line reads enough. Size: M.
- decision: owner. Factory reset keeps room history (designed so; the alternative is voided whole, a `_FACTORY_VOID` row and a coordinator edit).
- decision: owner. A crash loses up to 6 h of history (designed so; saving every row writes 0.29 MB each half hour on the Pi's card).

## Notes for the fixer

- Re-anchor every cite at the merge base after P1 lands, above all the cycle-step block (`coordinator.py:6110-6125` here, "_async_save_accuracy") and P1's side-table reader, whose name P1 sets. Carry: R11-OUTSIDE-ROOMS-P3 (item p3a1)
- The coordinator gets one step line and nothing else: house values pass as arguments; every key of `tests/structure_budgets.json` sits at zero headroom (`python3 tests/structure.py`), so pay for the line in the same pull request. Carry: R11-OUTSIDE-ROOMS-P3 (item p3a2)
- The new module must sit in a measured closure: the single-script form of `tests/derive_closures.sh`, on Linux only. Carry: R11-OUTSIDE-ROOMS-P3 (item p3a3)
- The record holds plain data only and reads the same whether its load lands before or after the first cycle: rows that close before the load completes merge by time into the loaded ring, never overwrite it. Carry: R11-OUTSIDE-ROOMS-P3 (item p3a4)

Seat tokens: the harness reports none for the main loop; no scouts were used.
