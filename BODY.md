R10-DOCS-STRINGS-RESIDUE part 1 of 3: carries 0 to 4 (production text). Each changed sentence is corrected to the code that decides the behaviour; the evidence line under each carry is that code (call path, constant, or a check that runs it), never a comment or docstring.

Carry 0 (P-OUTSIDE-3529-C, contributor Bankaifan, thanks): delivered before this part by pull request 3536 (merge commit 0cc5647545, the contributor's commits 091b777390, dc5ef2d555, ba25baa7d5, authored by Bankaifan); nothing is built here for it. The `combi_dhw_effectiveness` description in `strings.json`, `en.json`, `de.json` and `sv.json` on this base is byte-equal to 81b21d7733's, and the 0.1 to 1.0 bound and the clamp stay untouched. For the reviewer's check of the recipe sentence "the ratio belongs to that sensor": `thermal_model.dhw_store_of` reads `combi_dhw_effectiveness` as `min(1.0, eps)` above `COMBI_DHW_EFFECTIVENESS_FLOOR` (0.1) and applies it in `DhwStore.tap_temp_for_store` / `store_temp_for_tap` against the store temperature read from that one tank sensor, so a ratio measured against another point of the tank does not match the model; the docs' "1.10 to 1.15 against 0.96" reading on a part-charged tank lies above the clamp, which caps it at 1.0.

Carry 1 (86f47084): the `space_setpoint_unit` description (options, entities, indoor) ended "this integration never recommends a space set-point". It now reads that the optimizer never infers the unit from the entity and only the heat-pump pre-fill suggests one, in strings.json, en, de and sv. Evidence: the unit is read only from the entry configuration (`EntryConfig.space_setpoint_unit`, consumed by `pump_arbiter._flow_unit` / `pump_arbiter._return_unit` and `thermal_model.py` via `SPACE_SETPOINT_WATER_UNITS`); its one suggestion source is `modbus_prefill._plant`, `CONF_SPACE_SETPOINT_UNIT: WRITE_TARGET_FLOW if water else None`, keyed on register 4109 (100DH). Whether the optimizer writes the set-point is the sentence #3561 (r10-hotfix-flow-setpoint-stuck, unmerged) corrects in `space_setpoint_entity`; this diff touches the adjacent `space_setpoint_unit` value only, but the two lines are neighbours, so `git merge-tree --write-tree HEAD a02783d44d` reports a textual conflict in strings.json and the three translations: whichever of the two merges second takes both lines as they stand, no semantic overlap.

Carry 2 (2de47db2): docs/configuration.md (Away table, "Hot water minimum while away"), docs/how-it-works.md (Away and holiday mode), the `away_dhw_min_temperature` description in strings.json, en, de and sv, and away.py's module docstring said the anti-legionella cycle is timed to finish before the user returns. They now say it keeps its usual interval and is not timed to the return. Evidence: the due time is `legionella.py` `params.dhw_legionella_interval_days * 24.0 - since`, and `legionella.py` reads no away input (the count in `## Null control`); away sets only `state.target_temperature` and `state.dhw_min_temperature` (`away.resolve` and the override branch below it). The code was the defect's carrier too: `AwayConfig.legionella_before_return` was read by nothing, and its comment promised the behaviour; it is deleted (dead field, no constructor passes it).

Carry 3 (9ae2be30): docs/configuration.md and docs/how-it-works.md (Hot water circulation, and the Circulation pumps bullet), and the `vvc_pump_entity` description in strings.json, en, de and sv said the VVC pump runs only during the hot-water frames. They now add that with hot water off or no frames it is left on. Evidence: `pump_schedule.vvc_should_run` returns `True, "no demand windows; hot water always required"` on an empty window list, and `_async_drive_pumps` in coordinator.py passes `[]` unless `params.dhw_enabled and params.dhw_windows_active`; pinned by features.py check "with no windows the loop is simply left on".

Carry 4 (55051373): docs/configuration.md ("Credit disinfection from any heat source"), docs/how-it-works.md (the Free disinfection bullet, now "Hold-verified disinfection") and the `dhw_free_disinfection_enabled` description in strings.json, en, de and sv described free disinfection as an opt-in credit. They now say any source is credited either way; off at once, on only after the 20-minute hold. Evidence: `LegionellaGuard.async_track` in legionella.py credits with the flag off whenever `dhw_temp >= target - 1.0` (its `elif dhw_temp < target - 1.0: return`), and with it on only once `hold_minutes >= DHW_LEGIONELLA_HOLD_MINUTES` (const.py, 20.0) accumulated at `dhw_temp >= target - 0.5`; pinned by features.py's "#24 hold-verified free disinfection" block. The option's label is kept: it names the setting users already have, and the description now states what it does.

Carries 5 to 13 are later parts of this group, not built here: Carry 5 (4ab03548), Carry 6 (af528396), Carry 7 (31878861) and Carry 8 (734b6d33) are part 2; Carry 9 (753b6610), Carry 10 (f14f17f5), Carry 11 (c7e69450), Carry 12 (a0e752f6) and Carry 13 (3bbcabdc) are part 3, both dispatched at this part's handoff.

## Head

c79e44e2e6929a393a9542cc74b29b5ee3dcd776, measured against origin/main e23124ff6e45bac1d48b4a775dad555a37965355 at 2026-11-13T21:15Z.

## Mutation proof

The diff changes text and deletes one unread field, so no production line of the fix can be deleted to turn a check red; the proof is that the behaviour each new sentence states is pinned by a check that a mutation of the deciding predicate turns red:

Each run is `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('OUT').read())" START END` on a detached worktree of the head, OUT written by `features_block.py --emit-prelude OUT START END` from that tree; control first, unmutated: 4 of 4 ok in each block.

- Carry 3, M1: in `pump_schedule.vvc_should_run`, the empty-window `return True, "no demand windows; hot water always required"` to `return False, ...`. Block `# --- #6 the pump schedule` .. `_SAFE = dict(`: `FAIL with no windows the loop is simply left on`, 1 of 4 failed.
- Carry 4, M2: in `LegionellaGuard.async_track`, the flag-off predicate `elif dhw_temp < target - 1.0:` to `elif True:` (no credit with the option off). Block `# --- #24 hold-verified free disinfection` .. `# --- #47 the elastic legionella gate`: `FAIL with the flag off the historical instant credit is untouched`, 1 of 4 failed. The same block's `61 °C held past the hold time writes the completion timestamp` pins the on-side 20-minute hold.
- Restored with `git checkout -- .`; `git diff --quiet` passed.

Carries 1 and 2 state an absence (no inference of the unit from the entity; no return-time input to the legionella timing), which no mutant can delete; their control is the grep in `## Null control`.

Deleting `legionella_before_return` has no mutant by construction: restoring it changes no behaviour, which is the finding.

## Null control

At the base the old sentences stood against the same code: `git grep -c legionella_before_return e23124ff6e -- custom_components tests docs` prints `away.py:1` (the definition, no reader), and at the head the same command prints nothing. `python3 -c "print(open('custom_components/heatpump_optimizer/legionella.py').read().lower().count('away'))"` prints 0 at base and head, while the same command over `boost.py`, which imports away, prints a non-zero count: the count finds an away input where one exists. Unmutated, both pinning checks pass at base and head (scoped gate below).

## Figures

- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, then `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`: `MODE: SCOPED`, `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`, exit 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=c79e44e2e6929a393a9542cc74b29b5ee3dcd776 -->
~~~text
MODE: SCOPED -- 23 script(s) run, 10 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
