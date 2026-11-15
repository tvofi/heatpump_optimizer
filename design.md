# R11-OUTSIDE-ROOMS-P2: rooms as one pure module feeding the solver's two existing limit arrays (phases 1, 2, 3)

Base: origin/main 66865be375f4ee283ee556f53fcd76cc3dbf40e2. Predecessor R11-OUTSIDE-ROOMS-P1 has no handoff head (it is built to this note), so the code was read at the base only. Paths are under `custom_components/heatpump_optimizer/` unless they start with `tests/`, `docs/` or `README.md`. Names without backticks do not exist yet.

## Finding (owner report, #3616)

No finder harness: owner report. The reporter has about 20 `climate` room thermostats (current temperature, target, heating or idle; each opens its own underfloor loop; no per-loop flow). Evidence quoted from the issue: "Average indoor temperature: 19.6°C ... Planned space heating over the next 24 hours: 0 kWh" and "I would expect the heating plan to account for rooms that remain below their individual target temperatures." The 0 kWh itself was the slab seed (R11-OUTSIDE-SLAB-SEED-GUARD); what remains is the owner's three steps posted on the issue: a room list with average and spread (1), comfort from each room's own target (2), loop state as a delivery limit plus per-room history and an identifiability report (3). At the base the tree has no room concept: one `CONF_INDOOR_TEMP_ENTITY` read at `coordinator.py:6638`, targets from configuration only, and "zone" means the two floors.

## Owning seam

One new pure module, rooms (no `homeassistant` import, beside `comfort_band.py`), owns "what the room list says now": the reading record, the summary, the floor lift and the calling share. A second new pure module, room history, owns the ring and the identifiability report (phase 3), because it owns stored state and rooms owns none. Callers only: `inputs.py` (`InputReader` performs the entity reads), `coordinator.py` (passes readings in, composes two arrays), `config_flow.py`, `entry_config.py`, `sensor.py`, `payload.py`, `diagnostics.py`, `store.py` (a `DOMAINS` entry). `optimizer.py` and `thermal_model.py` are not edited in any phase, which is narrower than the roster's file lists. One owner per concern holds; no stop.

## Shape

```
options (room list key) -> EntryConfig tuple -> InputReader room read (per entity)
   -> rooms: readings -> summary ----------------------> payload -> 2 sensors        (P1)
                      -> floor lift K -> + _confidence_margins -> SolveLimits.min_temp_margins (P2)
                      -> calling share -> learned loop envelope -> min with caps -> SolveLimits.power_caps_extra (P3b)
                      -> room history ring -> own store; identifiability report -> diagnostics, 1 sensor (P3a)
```

**Phase 1 (P1).** Data: one new options key holding a list of entity ids (`climate`, or `sensor` with device class temperature), picked on its own new options page with a multiple entity selector (a variant of `_entity_of`, `config_flow.py:1111`, which is single-valued today); at most 32 entries. Its own page, so `_clear_absent` never writes the key for an install that does not open it. `EntryConfig` gains its first list parser (a tuple of ids; absent, None and empty all parse to the empty tuple). `InputReader` gains one room read built on `read(key, entity_id=...)` (`inputs.py:1094`): a `climate` yields the `current_temperature`, the target (`temperature` attribute, only while its HVAC mode heats, the rule the set-point code at `inputs.py:455-505` already states) and `hvac_action`; a `sensor` yields a temperature only. One age limit and the `ROOM_AIR_RANGE_C` range for the whole list, registered under the list key in `INPUT_MAX_AGE_MINUTES`; every room read lands in `InputHealth`. The rooms summary is the mean, the spread (warmest less coldest), the coldest entity and the valid count; it returns None under a quorum (fewer than half the list, minimum one). Entities: two sensors (room average, room spread), created in `sensor.py` `async_setup_entry` only when the list is non-empty; the options listener already reloads the entry (`__init__.py:398`), so the set is fixed for the entry's lifetime and `README.md:295`'s "One service device, statically" stays true. Per-room values are attributes of those sensors, keyed by entity id; no per-room entity, no room name stored. The summary does not replace `state.room_temperature`: swapping the model's sensor would void the learners keyed on `heat_loss_zone_entities`. Readings live in a per-coordinator `WeakKeyDictionary` side table in rooms (`boost.py`'s pattern), never a coordinator attribute.

**Phase 2 (this group).** For each fresh room with a target, the room's shortfall is its target less its temperature; the house's is the live comfort target less `state.room_temperature`. The floor lift is the largest room shortfall less the house shortfall, clipped to [0, cap]: the mean temperature at which the worst room would sit at its own target, assuming its offset from the mean persists, expressed as a raise of the configured floor with the configured band width kept under each room's target. It is held constant over the horizon and added to `_confidence_margins`' array at the two `SolveLimits` builds (`coordinator.py:6315` and `coordinator.py:11354`), so `_build_comfort_bounds` applies it at `optimizer.py:4563` and its existing clamp (`temp_max_bounds - 0.5`, `optimizer.py:4576`) still bounds the sum. Rooms returns the base array object untouched (None stays None) when the feature is off, the list is empty, the quorum fails, no room has a target, the away setback is active, or the lift is zero. Stateless: no store, no migration. One sensor attribute on the spread sensor names the room that set the lift and its size.

**Phase 3 (P3), two parts.** P3a, recording only: room history keeps, per room, a ring of `HISTORY_LENGTH` rows (`accuracy.py:51`, the fortnight the accuracy tracker keeps) of time, temperature, target and calling, in its own `QuarantiningStore` (`store.py:696`) at version 1 with a `DOMAINS` entry; rows are keyed by entity id and a room removed from the list drops its ring. The identifiability report is a pure function of the rings: per room a verdict, separable or one reason code (no action reported, short history, never or always calling, no temperature response to calling, calling pattern collinear with a named room), from the calling duty share, the difference in temperature slope while calling against idle over its standard error, and the largest pairwise calling correlation. It is published in diagnostics and as one sensor (count of separable rooms, verdicts as attributes). This is the evidence phases 4 and 5 gate on. P3b, the limit: a learned envelope of delivered heat per calling-share bucket, folded where `_fold_capacity_envelope` folds (`coordinator.py:9287`, same vetted tail, same `CAPACITY_MIN_SAMPLES` and `CAPACITY_FLOOR_FRACTION`), converted to electrical per step and composed by `np.minimum` beside `_capacity_caps` (`coordinator.py:9322`) into `power_caps_extra` at `coordinator.py:6313` and `coordinator.py:11349`. The share is known only now, so the cap holds for a short window and then releases; an unsampled bucket caps nothing.

**Invariants.** (i) No room list: plan, entity set and stored options byte-identical, in every phase. (ii) The lift only raises the floor, never the target, the ceiling or the measured state, and never lowers anything. (iii) A cap never falls below `CAPACITY_FLOOR_FRACTION` of nameplate. (iv) A missing, stale or implausible room is dropped, never guessed. (v) No `entry.options` read below the glue; the coordinator composes, rooms computes.

**Migration.** None. `CONFIG_ENTRY_VERSION` stays; every new key reads with a default; the new store starts at version 1. Phases 4 and 5 stay reachable without one: zone groups add a second key mapping entity id to group (absent means one group), thermostat writes go through `pump_arbiter.py`, and both read the same reading record and history rows.

## Solve cost (production solver, measured at the base)

No decision variable, constraint or objective term is added; only values in an existing per-step array change. Instrument: `HeatPumpOptimizer.optimize` driven through `tests/profiles.py` `solve_inputs`, 24 h at 15 min, `weather("winter_cold")`, `prices("winter_typical")`, hot water on, floor 19.5, start 20.0, five runs each, single-threaded BLAS, on the seat's Linux container (not a Raspberry Pi; ratios, not milliseconds, carry over). Null control: a zero margin array reproduces the plan of None byte for byte (same sha1 of `power_schedule`) in both models, and every non-zero lift changes it.

| margin | single-zone median ms (min-max) | plan kWh el | two-zone median ms (min-max) | plan kWh el |
|---|---|---|---|---|
| None | 1157 (1099-1375) | 63.60 | 2751 (2524-3268) | 92.35 |
| zeros | 1129 (1028-1308) | 63.60 | 2966 (2710-3079) | 92.35 |
| 0.6 K held | 1250 (1111-1397) | 70.27 | 2872 (2642-2966) | 97.89 |
| 1.5 K held | 894 (799-1023) | 82.15 | 2060 (2034-2220) | 104.89 |

Solve time with a lift sits inside the None row's own min-max spread or below it. The cost that is real is energy: a held 0.6 K lift plans about a tenth more electricity on this day, 1.5 K about 29 % (single-zone), which is why the cap is an owner decision. The fixer re-measures on its branch with `tests/stress.py`'s budgets; `tests/stress_budgets.json` is not raised.

## Alternatives

- **Feed the coldest room (or a room-weighted value) as `state.room_temperature`.** Lost: that state also drives the RC dynamics, `_async_learn_house_heat_loss` and the accuracy record, so a comfort preference would bias the model and void learners; two concerns in one field.
- **A per-step target array or per-room states in `optimizer.py`.** Lost: a new `SolveInputs` field and a third comfort term at `_comfort_terms_batch`, where the two-zone solve already costs 2.4 times the single-zone one (table), and room parameters the issue's own study shows are not identifiable from one heat input.
- **Use `min_temp_floors`.** Lost: that array is reported and ranked as the mold floor (`_mold_floor_series`, capped at the configured target, outranking the window relax); a second producer would need a new discriminator in the optimizer.
- **`replace(config, min_temp=...)` in `_solve_hubs`, as away does.** Lost: it moves the night setback arithmetic and `comfort_band`'s validation onto a per-cycle value and hides the lift from the why-now drivers, which read margins.
- **Per-room entities or config subentries.** Lost: `tests/entities.py` pins static README counts and the tree has no dynamic entity machinery; two aggregate sensors with attributes carry the same data.

## Sibling sites

`git grep -n "min_temp_margins=" -- custom_components/heatpump_optimizer/coordinator.py` returns the two builds named above (the solve and the what-if); both take the lift. `git grep -n "power_caps_extra=" -- custom_components/heatpump_optimizer/coordinator.py` returns the same two for P3b. Out of scope, with reason: the coordinator's own floor checks (`worst_zone_margin_k`, `_sim_coldest`, the force-on and pump-scheduling zone lists) judge model zones against the configured floor as safety, and the lift is a planning preference; they do not move.

## Evidence, by file

- `tests/features.py` (modules driven directly; imports the production symbols): P1 summary, quorum, stale and implausible rooms dropped, the room read for a `climate` and a `sensor`. P2 failing test on today's code (the symbol is absent, then the assertion): rooms A 18.0 with target 21.0, B 20.4 with target 20.0, C 20.4 with target 16.0, model temperature 19.6, live target 20.0; expected lift is the cap, and C (deliberately cool) contributes nothing. Null controls: A raised to 21.0 gives no lift and the base array object back; empty list, feature off, away active each give the base object back.
- `tests/validate.py` or `tests/edge.py`: one production solve with and without the fixture's lift; the lifted plan's lowest room temperature and space energy are both higher; the zero-array control equals None by plan hash, as in the table.
- `tests/config_flow_steps.py`: the new page saves a list, clears it, and an install that never opens it stores no new key.
- `tests/golden.py`: the null control for invariant (i). No fixture moves, so neither claim file is touched; a fixture that moves is a defect in the change, not a claim.
- `tests/entities.py`: counts unchanged with no list; `docs/configuration.md` names the new page and fields; `strings.json` and the three translations stay in parity. `tests/finite_boundary.py`: the P3a store's `DOMAINS` entry.
- P3a: a synthetic two-room history generated by `simulate_step` with independent calling reads separable; calling of room B copied from A reads collinear; the calling column shuffled in time reads no response; fewer rows than the minimum reads short history. P3b: an envelope bucket under `CAPACITY_MIN_SAMPLES` caps nothing (plan hash equal); a sampled bucket lowers the first steps' ceiling and never below the floor fraction.
- Mutation targets: the clip of the lift at zero and at the cap; the house-shortfall subtraction; the quorum predicate; the away gate; the hold-window release in P3b; each verdict threshold in the report.

## Hot files, position, carries

Serial: R11-OUTSIDE-SLAB-SEED-GUARD, then P1, P2, P3a, P3b. Hot across all three: `coordinator.py` (the two `SolveLimits` builds, `_update_current_state`, `_build_data_dict`), `const.py`, `config_flow.py`, `entry_config.py`, `inputs.py`, `sensor.py`, `payload.py`, `strings.json`. P1 creates rooms; P2 only adds to it; P3 creates room history. No overlap with design/R11-OUTSIDE-HONEST-STARTS-RUNS on `optimizer.py`, because no phase edits it. No pinned grader is added, so no p1/p2 split. Carries owed: the notes below; received: none.

## Decisions routed

- decision: owner. The lift cap. Recommended 1.0 K (beside `CONFIDENCE_MARGIN_CAP_C` at 0.8), given the energy figures above.
- decision: owner. Whether phase 2 is its own opt-in flag, default off, separate from configuring the list. Recommended yes: listing rooms then changes no plan.
- decision: owner. P3b's floor: reuse `CAPACITY_FLOOR_FRACTION` (recommended; the cap then rarely binds with few loops open) or a lower loop-specific floor once P3a's history shows delivered heat per calling share.
- decision: orchestrator. P3 splits into P3a (recording and report) and P3b (the cap); P3b's constants wait for P3a's evidence from a live install.

## Notes for the fixer

- Every key of `tests/structure_budgets.json` sits at zero headroom at the base (`python3 tests/structure.py`): no new coordinator attribute (side table), no new branch in `_build_data_dict` or `_solve_record` beyond one call each, and every symbol phase 1 adds needs a reader in phase 1 or `dead_top_level_symbols` fails. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e01)
- A new coordinator method needs a `tests/seam_map.json` entry and may cost `seam_cut_total`; prefer module functions in rooms that take the readings. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e02)
- A new module must sit in a measured closure: re-derive with the single-script form of `tests/derive_closures.sh`, on Linux only. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e03)
- A `climate` target is in the instance's unit system; convert as the set-point code in `inputs.py` does, and test a Fahrenheit instance. Carry: R11-OUTSIDE-ROOMS-P1 (item 5a1c0e04)
- Sum of the two margins: test the clamp with confidence margins on and the lift at its cap, in a narrow band. Carry: R11-OUTSIDE-ROOMS-P2 (item 5a1c0e05)
- The why-now drivers and the plan narrative read the margin; name the room lift there or the raised floor reads as model uncertainty. Carry: R11-OUTSIDE-ROOMS-P2 (item 5a1c0e06)
- Worst-case store size is 32 rooms by `HISTORY_LENGTH` rows by four values; store centi-degrees as integers, measure the file and resident memory under `tests/stress.py`, and save on the accuracy store's cadence. Carry: R11-OUTSIDE-ROOMS-P3 (item 5a1c0e07)
- Entity ids are exported unredacted in diagnostics, as the indoor sensor is today; store no free-text room name, or add its key to `TO_REDACT`. Carry: R11-OUTSIDE-ROOMS-P3 (item 5a1c0e08)

Seat tokens: three read-only scouts, 112461, 138137 and 184466 (harness figures); the harness reports none for the main loop.
