# a3: nine static architecture metrics, prototyped and controlled

Baseline: origin/main `7952d8f9`, measured from the clean worktree `SCR/main`. Everything lives under `SCR/archscore/a3/`:

- `metrics/<name>.py`: one module per metric. Each exposes `measure(root: Path) -> dict` and returns `{"metric", "value", "details", "runtime_s"}`. Each is stdlib-only (`ast`, `json`, `re`, `hashlib`) and runs standalone as `python3 metrics/<name>.py ROOT`.
- `metrics/_common.py`: the shared package model and the role engine (see "The role engine" below).
- `run_all.py ROOT [--details] [--timing]`: prints every headline as JSON. It parses the package once.
- `controls.py WORKTREE --history PRE POST`: runs the planted control, fix and null arms. Its output is in `controls.out` and `controls.json`.

Determinism: `run_all.py --details` gives byte-identical output (runtime fields stripped) under `PYTHONHASHSEED` 1, 7 and 12345. The one ordering bug this check found, count ties in sorted dicts, is fixed.

Runtime: best of three standalone runs on this 4-core container, including interpreter start. About 0.9 s of each figure is parsing 53.6k lines. `run_all.py` runs all nine in 2.37 s.

P10, the loop kernel count, is deliberately left out. It is a runtime measurement: it needs a solve to execute, so no AST can see it.

## Summary

| # | metric | baseline | control | fix | null | runtime | verdict |
|---|---|---|---|---|---|---|---|
| 1 | hub_solve_writes | 40 | 41 (+1) | 39 (-1) | 40 | 1.29 s | ready |
| 2 | shared_inplace_writes | 22 | 34 (+12) | 21 (-1) | 22 | 1.62 s | ready |
| 3 | private_reach | 92 (80 reads + 4 writes x3) | 98 (+6 reads); 95 (+1 write, weighted +3) | 91 (-1) | 92 | 1.47 s | ready |
| 4 | untyped_payload_keys | 164 | 165 (+1) | 162 (-2) | 164 | 1.16 s | ready |
| 5 | xmodule_duplication | 5 | 7 (+2) | 3 (-2) | 5 | 1.27 s | ready (with the reformat caveat) |
| 6 | import_cycles | 0 | 9 (+9) | 0 (-9, fix applied on top of the control) | 0 | 1.03 s | ready (guard-only today) |
| 7 | public_surface | 515 | 516 (+1) | 514 (-1) | 515 | 1.08 s | not ready as a ratchet; ready as a report |
| 8 | dead_by_reachability | 6 | 8 (+2) | 5 (-1) | 6 | 1.51 s | ready |
| 9 | family_splits | 3 | 4 (+1) | 2 (-1) | 3 | 0.05 s | ready |

Cross-talk that the controls surfaced is all correct:

- Re-planting #1752 also adds one private read (`coord._current_action` in `boost.apply`) to metric 3.
- Adding a TypedDict class adds one internal-only public name to metric 7.
- The m5 copy and the new public helper are both dead, so each also adds 1 to metric 8.

History checks against the real S1/S2 fix (#1752/#1753):

| commit | shared_inplace_writes |
|---|---|
| `47353326` (before `ac65f2aa`) | 38: 34 in-place + 4 borrow/restore |
| `ac65f2aa` (the fix) | 22 |

At `47353326` the 34 in-place sites include 12 overlay writes into the live `_current_action` (`boost.py:118-133`), and the 4 borrow/restore sites are `_maybe_refresh_price_tile` and `_maybe_run_fuse_advisor` each restoring `_last_simulation` and `_simulation_cache`. The fix removes exactly those 16. No other metric moved on that commit except `private_reach`, 90 → 91: the fix added a foreign write, `coord._current_action = action` in `boost.apply`.

Calibration against the round-9 enumerators at `31394964`:

- **m3 (private reach):** m3 counted 84 sites. `private_reach` also counts 84 sites there (81 reads + 3 writes), with the same three write sites.
- **m1 (hub writes):** m1 counted 26 write sites in two functions (19 + 7). `hub_solve_writes` counts 40, a superset:
  - 19 + 9 in those two functions. The extra 2 are the tuple-target pair at `params.flow_curve_bias, params.flow_curve_indoor_target = ...`, which m1's single-target walk missed.
  - 12 more that m1 could not see: 9 in `away.py`, and 3 in two other coordinator helpers.
- **structure.py duplication anchor:** the per-module row count computed by metric 5's own code path is 14, equal to `tests/structure.py`'s `duplication_blocks` of 14.

## The role engine (`_common.py`), shared by metrics 1–4

A role says what an expression is, as far as the coordinator is concerned:

- `("coord",)`: the coordinator itself.
- `("obj", path, cls)`: an object reached from it along an attribute/item path.
- `("self", cls)`: a method's own `self` in another class.

**Seeds.** An expression gets the coordinator role from:

- `self` in `HeatPumpOptimizerCoordinator`;
- `getattr(self, "_ctx", self)` and `self._ctx`, the context hop, which is transparent;
- `entry.runtime_data`;
- a constructor call of the coordinator class;
- parameters and locals named `coord` or `coordinator`, or annotated with a `*Coordinator` or `*Coord` type;
- `self.coordinator` on CoordinatorEntity subclasses, and any `self.X` a class stores a coordinator parameter into.

**Propagation.**

- Roles flow through arguments, to a context-insensitive fixpoint over the call graph.
- They flow through local aliases, flow-insensitively. This covers assignments, `for` loops over literal tuples, `with ... as`, and the walrus operator.
- They flow through callback references: `self.m` passed without being called is still an edge.
- They flow through `other_module.hook = fn` injections made at import time (the pattern at `setpoint_check.dhw_gated`).

**Call resolution.** Calls resolve through imports and re-exports, the MRO, `super()`, and typed owned attributes. A typed owned attribute is one assigned as `self.A = K(...)` or `self.A = K.from_dict(...)`.

**Hub aliases.** These are derived, not listed by hand. When the coordinator constructs `self.A = K(..., <coord path>, ...)` and `K.__init__` stores that parameter as `self.F`, then `coord.A.F` is that path. At baseline this derives four aliases:

- `_thermal_model.params` → `_thermal_params`
- `_legionella._params` → `_thermal_params`
- `_dhw_learner._params` → `_thermal_params`
- `_optimizer.config` → `_opt_config`

**Write sites.** A write site is any of: a store, an augmented assignment, a `del`, `setattr`/`delattr`, an item store, or a container mutator (`update`/`append`/`pop`/...). Mutators are counted only when the receiver's class is unknown or does not define that name itself.

## 1. hub_solve_writes

**Property.** Whether the live, event-loop-shared parameter hubs are mutated by the solve. Each such write is a value that outlives the solve unless something unwinds it: the D1-s3-04 / #1517 / #1529 / H1 class.

**Definition.**

- Roots are `async_run_optimization` and `async_simulate`, with `self` bound to the coordinator. Everything reachable from them counts, in any module.
- A site is an in-place write whose base resolves to `_opt_config`, `_thermal_params` or `_current_state`, or to anything under them, however spelled.
- Rebinding a hub itself (`ctx._opt_config = replace(...)`) is excluded: that is the copy-on-write the frozen `CoordinatorContext` exists for.
- **Headline:** distinct (file:line, hub, field) sites.

**Baseline: 40.** All 40 come from `async_run_optimization`; `async_simulate` contributes 0 because it deep-copies.

- By hub: `_opt_config` 23, `_thermal_params` 15, `_current_state` 2.
- These cover 35 distinct fields.
- By function: `async_run_optimization` 19, `_prepare_dhw_inputs` 9, `away.apply_setback` 6, `away.restore_setback` 2 (the `setattr` loop), `_apply_comfort_weight` 2, `away.lower_floor` 1, `_apply_house_heat_loss_scale` 1.

**Arms.**

- **Control:** `away.lower_floor` gains `opt_config.max_temp = ...`, a write through a parameter in a module m1 never read. 40 → 41.
- **Fix:** delete the `peak_offpeak_factor` write. 40 → 39.
- **Null:** rename the alias `params` → `hub_params` in `_prepare_dhw_inputs` and `ctx` → `c2` in `async_run_optimization`. Stays at 40.

**Blind spots.**

- Hubs reached through a container: `x = [ctx._opt_config]; x[0].f = v`.
- Writes through `getattr(obj, name)` with a dynamic name. The `setattr` loop is counted as one `<dynamic>` site per hub.
- Writes the solve makes inside `numpy` arrays held by the hubs (`arr[:] = ...` on a field is counted; `np.copyto(field, ...)` is not).
- Restore writes count as writes. The metric prices exposure, not net leakage, so `restore_setback` is 2 of the 40.

## 2. shared_inplace_writes

**Property.** Whether coordinator-held state is mutated in place where another task, or the published `coordinator.data`, can observe it half-done. These are the S1 (boost overlay on `_current_action`) and S2 (borrow/restore of the what-if cache across an await) shapes.

**Definition.**

- A long-lived object is anything at least one hop from the coordinator (`coord.A`, `coord.A.B`, `coord.A[k]`), minus the three hubs, which metric 1 owns.
- It counts an in-place write into such an object when the write is either:
  - (a) in an `async def` coordinator method, or
  - (b) in any function of a collaborator module.
- Excluded:
  - the construction phase, derived from the code: `__init__`, `_init_*`, and every function `__init__` references directly (the 12 spawned loaders, `boost.restore_session`);
  - a collaborator mutating its own fields through its own `self`, or through locals aliasing parts of it (`state = self.state`).
- It also counts BORROW/RESTORE: in an async function containing an `await`, a coordinator slot saved into a local (`snap = (self.A, self.B)`) and written back from it (`self.A, self.B = snap`). One site per (function, slot).
- **Headline:** in-place sites + borrow/restore sites.

**Baseline: 22.** 18 are in coordinator async methods and 4 in collaborators; there are 0 borrow/restore sites.

- `_away_state` 9: 6 in the coordinator's async away handlers, 3 in `away.apply_override_payload`.
- `_price_tiles` 2.
- One each: `_current_action["price"]` (`coordinator.py:4812`), `_pump_commanded[..]`, `_accuracy.lead_pending.clear()`, `_dhw_accuracy.lead_pending.clear()`, `_background_tasks.clear()`, `_solar_radiation_forecast.append`, `_store_digests[..]`, `_price_days_seen.add`, `_price_qdays_seen.add`, `_sysid.config.enabled`.
- One more: `boost_calls.append` (`boost.py:241`), a recorder hook `getattr(coord, "boost_calls", None)` that only tests set.

**Arms.**

- **Control:** re-plant #1752 (`action = coord._current_action` in `boost.apply`). 22 → 34: the 12 overlay item writes.
- **Fix:** `self._current_action["price"] = ...` becomes a rebind `{**..., "price": ...}`. 22 → 21.
- **Null:** the `_price_tiles` write spelled through a local alias. Stays at 22.
- **History:** 38 → 22 across the real #1752/#1753 fix (detailed above).

**Blind spots.**

- Sync coordinator methods are out by definition. A sync helper called from an async method that mutates `self._x` is not counted unless it lives in a collaborator module.
- Module-level helpers in `coordinator.py` taking `coord` are neither (a) nor (b).
- Borrow/restore is recognised only through a named local. Something like `self.A, self.B = self._saved` is missed.
- Mutation through a method of an untyped owned object (`self._x.set(...)`) counts only for the listed container mutators.

## 3. private_reach

**Property.** Encapsulation of the coordinator: how many foreign lines depend on its private names, and how many of them write its state.

**Definition.**

- Scope: every function outside `coordinator.py`.
- A site is a `<c>._x` access (not a dunder, not the `_ctx` hop) or `getattr/hasattr/setattr/delattr(<c>, "_x")`, where `<c>` has the coordinator role.
- WRITE: a store, `del` or `setattr` on it, OR an in-place mutation based on it (`coord._x[k] = v`, `coord._x.append`). Everything else is READ.
- **Headline:** reads + 3 × writes over distinct (file, line, col, member) sites.

**Baseline: 92** = 80 reads + 4 writes × 3, over 13 files and 24 members.

- The writes: `__init__.py:299` `_reload_handover`, `__init__.py:308` `_skip_solve_once`, `boost.py:117` and `boost.py:181` `_current_action`.
- Per file, weighted: pump_arbiter 37, boost 9, diagnostics 8, sensor 8, `__init__` 7, away 7, wood_fuel 7.

**Arms.**

- **Control:** m3's arm A, six reads in `pump_arbiter.state_for`. 92 → 98. `tests/structure.py` returns rc=0 on the same edit, re-run at `7952d8f9`.
- **Control (write):** one `coord._skip_solve_once = False`. 92 → 95.
- **Fix:** diagnostics' `getattr(coord, "_mode")` → `"mode"`. 92 → 91.
- **Null:** every `coord` in `pump_arbiter.py` renamed `owner`, so the name convention no longer applies and the roles must come from call sites. Stays at 92.
  - This null first read 91. The lost site was `dhw_gated`, reached only through the import-time injection `setpoint_check.dhw_gated = dhw_gated`.
  - The engine now resolves that injection, and the null holds.

**Blind spots.**

- A coordinator held in a container (`self._coords[entry_id]._x`) or returned by an unresolved call.
- A collaborator whose coordinator parameter is named something else and that is only called through an untyped receiver.
- Reads through `vars(coord)` / `coord.__dict__`.

## 4. untyped_payload_keys

**Property.** The contract between the coordinator and its ~120 entity read sites is a bare `dict[str, Any]`. The metric counts the keys that no type contract declares.

**Definition.**

- The producer is `_async_update_data`'s returned dict, followed through:
  - `return [await] f()` and `return self._build_data_dict()`;
  - dict literals and `**` spreads;
  - `d["k"] = ...` (tuple targets too), `update({...})` / `update(f())` / `update(k=...)`, `setdefault`, and `|=`;
  - `for view in (self._a_view, ...): data.update(view())`;
  - `g(..., d, ...)` into `g`'s writes on that parameter.
- A key is TYPED only if a package `TypedDict` (class or functional form) declares it and is attached to the path: the tracked variable's annotation, the parameter's annotation, or the emitting function's return annotation.
- **Headline:** produced keys that are untyped.

**Baseline: 164** produced, 0 typed (there is no TypedDict in the package).

- **Golden cross-check:** the union of `tests/golden/coord_*.json` has 162 keys.
  - 156 of them are produced statically.
  - The other 6 are the energy-total keys, which come from the one dynamic site (`coordinator.py:7289`, a comprehension over `_energy_totals`).
  - 8 produced keys are conditional and appear in no golden, e.g. `manual_plan`, `mixing_valve_mode`, `valve_target_recommendation`.
- **Consumer side:** surfaces read 121 top-level keys.
  - Exactly one is read but never produced: `horizon_hours` (`sensor.py:1511`, `sensor.py:1544`). That is a live dangling read; m2 had it too.
  - 44 produced keys are read by no surface module.

**Arms.**

- **Control:** one more literal key in `_build_data_dict`. 164 → 165.
- **Fix:** `class CoordinatorData(TypedDict, total=False)` with `mode` and `plan_stale`, annotating `data`. 164 → 162.
- **Null:** rename local `data` → `payload`. Stays at 164.

**Blind spots.**

- Dynamic keys: 6 keys from 1 site are listed but not counted.
- Nested keys: `data["insight"]`'s sub-keys are out of scope.
- Keys added to `coordinator.data` after publication by other paths (`async_set_updated_data`: none at baseline).
- A TypedDict annotated on the variable is trusted without checking `total=` or value types.

## 5. xmodule_duplication

**Property.** Copy-paste across module boundaries: the drift risk of two copies that `tests/structure.py` cannot see (#1738 arm a).

**Definition.** It uses structure.py's `normalized_function_lines` and `duplicate_runs` unchanged:

- a window of 10 lines;
- lines stripped, with blank and comment-only lines dropped;
- nested defs cut out and never bridged;
- maximal-run merge.

The only change is that the window digest table is package-wide, and a window counts only when the functions sharing it live in two or more modules.

- **Headline:** (function, maximal run) rows. This is structure.py's row shape, so one copy adds 2.

**Baseline: 5.**

- `binary_sensor.__init__` ↔ `button.__init__`: 12 lines, 2 rows.
- `optimizer._replay_end_state` ↔ `thermal_model.simulate_trajectory` / `simulate_trajectory_with_dhw`: 10 lines, 3 rows.

The same-module count on the same code path is 14, equal to `duplication_blocks`.

**Arms.**

- **Control:** m5's arm A, `tariff._window_slot` (32 lines) copied into `sysid.py`. 5 → 7. Re-run at `7952d8f9`, structure.py's `duplication_blocks` stays 14 → 14; it fails only `dead_top_level_symbols` +1, because the copy is dead.
- **Fix:** both entity bases call one `entity.pin_identity` helper. 5 → 3.
- **Null:** comments and blank lines inside a duplicated body, plus a trailing comment in `tariff.py`. Stays at 5.

**Blind spots.**

- All inherited from the line-level normalisation. Joining the button `__init__` signature onto one line (a pure reformat) drops the metric from 5 to 3, so a formatter pass can move it.
- Renamed-identifier clones (type-2) and sub-10-line clones are invisible.
- Fix this with a token- or AST-normalised window before using it as a ratchet across a formatter change.

## 6. import_cycles

**Property.** Layering. Also, per module, Martin's instability `I = Ce/(Ca+Ce)`, abstractness `A`, and distance from the main sequence `D = |A+I-1|`.

**Definition.**

- Node: package module.
- Edge: any intra-package import, module-level or function-local, plus the package's lazy `import_module` / `_lazy` / `_async_lazy(..., "x")` calls.
- `if TYPE_CHECKING:` imports are excluded.
- SCCs are found by Tarjan. The details also give the module-level-only graph, which is what Python actually hits at import time.
- A (abstractness) = the share of the module's classes that are Protocol, ABC or `abstractmethod`-bearing.
- **Headline:** modules in non-trivial SCCs.

**Baseline: 0** (197 edges, no cycle). Mean D is 0.523. The "zone of pain" (`I<0.3`, `A<0.3`, `Ca≥5`) is `const`, `dhw_schedule`, `drift`, `entity`, `inputs`, `mixing_valve`, `store`. `coordinator` has Ca 9, Ce 45 and I 0.83.

**Arms.**

- **Control:** `drift.py` imports `coordinator`. 0 → 9: the SCC pulls in every module on a coordinator → … → drift path.
- **Fix:** applied on top of the control, since the baseline has no cycle to remove. The same import moved under `if TYPE_CHECKING:`. 9 → 0.
- **Null:** swap two import lines. Stays at 0.

**Blind spots.**

- `importlib.import_module` with a computed name.
- Imports of the package through its absolute path, other than `custom_components.heatpump_optimizer.X`.
- Abstractness counts only `Protocol`/`ABC`/`abstractmethod`. Duck-typed protocols (`Any` parameters) read as concrete, which is why A is ≈0 everywhere and D mostly tracks I.

At 0 this is a guard, not a trend. It is worth wiring because the cost of a new cycle is paid at import time on HA startup.

## 7. public_surface

**Property.** The breadth of each module's public API against what other modules actually consume.

**Definition.**

- **Public names counted:**
  - public module-level names, minus HA convention names and ConfigFlow/OptionsFlow classes;
  - public methods of package classes whose MRO stays inside the package and that are not Protocol/TypedDict/NamedTuple/Enum declarations.
- **Cross-module use of a module-level name:** another module imports it (through re-exports), reads `mod.N`, or reads `x.N` on an untyped receiver (structure.py's rule 4).
- **Cross-module use of a method:** any other module reads `.N` or `getattr(x, "N")`.
- Runtime-assembled names are credited, generalising structure.py's `DYNAMIC_REFERENCES`: `getattr(x, f"PREFIX{..}")` plus a literal S in the same module.
- **Headline:** public names with no cross-module use: `internal_only`, plus `unused` (the dead public API).

**Baseline: 515.**

- 1,209 module-level names + 291 methods are public; 985 are used across modules.
- 509 are internal-only.
- 6 are unused: `const.ENTITY_FAMILY_OVERRIDES` (read only by `tests/entities.py`), plus five properties: `DefrostDerate.measured`, `InputHealth.healthy`, `IrradianceSeries.start`, `OpenMeteoSolar.last_success` and `_Horizon.weather`.

**Arms.**

- **Control:** a new unused public helper in `tariff.py`. 515 → 516.
- **Fix:** `boost.overlay`, internal-only, becomes `_overlay`. 515 → 514.
- **Null:** `boost.held_for` → `held_state_for` in every module. Stays at 515.

**Blind spots.**

- Method use is name-based, so a common name (`update`, `get`) always reads as used.
- Entity/flow classes are excluded wholesale.
- The internal_only bucket includes things that are public on purpose, like platform entity classes and constants tests import.

**Verdict.** As a ratchet the 509 is mostly naming convention, not architecture. Wire the `unused` subcount (6) as the gate and keep `internal_only` as a report.

## 8. dead_by_reachability

**Property.** Code that no production path reaches, including code that is called, but only from other dead code. This is the shape `tests/structure.py`'s name-based `dead_methods` says it cannot see.

**Roots.**

- Every module's import-time code: module statements, class statements, decorators, defaults.
- HA_CONVENTION_NAMES functions: every platform's `async_setup_entry`, diagnostics, repairs, migrate/unload.
- Module dunders.
- `manifest.json` `config_flow: true` → ConfigFlow/OptionsFlow subclasses.
- In any live class with an external base: its public and HA-convention members.
- Dunders of every live class.

**Traversal.** A rapid-type-analysis sweep:

- a bare name resolves through imports;
- `Class.m` resolves through the MRO;
- `self.m` resolves through the MRO, plus overrides in live subclasses;
- `super().m`;
- typed `self.A.m`;
- an untyped `x.m` reaches every member named `m` of every live class, and every top-level `m` (a module returned by `_async_lazy` is untyped). This errs toward "live".

Protocol members (9) are declarations and are excluded from the census. Tests are not roots.

- **Headline:** unreached members (functions, methods, property accessors).

**Baseline: 6** of 1,560.

- `drift.Cusum.reset`: its name is live, because `FrequencyWatchdog.reset` and `ComfortLearner.reset` are called, but no `Cusum` receiver ever calls it.
- Five properties: `DefrostDerate.measured`, `InputHealth.healthy`, `IrradianceSeries.start`, `OpenMeteoSolar.last_success`, `_Horizon.weather`.
- All 6 names occur in `tests/`.
- structure.py reports `dead_methods=0` (it skips properties, and `reset` is a live name).

**Arms.**

- **Control:** `Cusum._probe_a` calling `_probe_b`, with nothing calling `_probe_a`. 6 → 8. structure.py's `dead_methods` gives 0 → 1: it cannot see `_probe_b`.
- **Fix:** delete `Cusum.reset`. 6 → 5.
- **Null:** a consistent rename plus blank lines. Stays at 6.

**Blind spots.**

- A name built at runtime (`getattr(x, f"async_{name}")`).
- HA reaching a private member by convention that is not in the list.
- The untyped-receiver arm keeps anything alive whose name is spoken anywhere on a live path, so the metric under-reports by design.
- Public helpers on entity classes are treated as framework API.

## 9. family_splits

**Property.** Discoverability of the entity roster. A declared family, meaning the translation key's lead token or `const.ENTITY_FAMILY_OVERRIDES`, should sort as one run in the entity list, in both shipped languages.

**Definition.** RCA-BULK-4's definition is kept: 75 names from `translations/{en,sv}.json`; en sorts by `casefold`; sv sorts by `casefold` with å<ä<ö after z.

- The family declaration now includes the production override table, read from `const.py`'s AST. That table landed after bulk4 measured.
- **Headline:** split declared families in en + in sv.

**Baseline: 3.** These are en `away`, sv `away` and sv `compressor`, exactly `tests/entities.py`'s `_FAM_SPLIT_ALLOWED`. The raw lead token without overrides (bulk4's original KEY arm) gives 2 + 3.

**Arms.**

- **Control:** en "Cost Predicted" → "Predicted Cost". 3 → 4.
- **Fix:** en "Expected Return" → "Away Expected Return". 3 → 2.
- **Null:** "Away Mode" → "Away mode" (the sort casefolds). Stays at 3.
- **History:** at `31394964`/`47353326` the metric reads 5 (the cost family's lifetime members before the override landed). At `7952d8f9` it reads 3.

**Blind spots.**

- The sv collation is an approximation of `Intl.Collator('sv')`.
- Other languages are not measured.
- Entities without a translation `name` are invisible.

## Known limits of the whole set

- **Stated approximations.** Everything is static. The role engine is context-insensitive and flow-insensitive, and the call graph over-approximates through name-based fallbacks. Every "blind spot" above is a place where the answer can be wrong, and each errs in the stated direction.
- **Coordinator-specific configuration.** Metrics 1–4 assume the coordinator class name and module (`_common.COORD_CLASS` / `COORD_MODULE`) and the three hub names. They are the constants to change if the decomposition renames them.
- **Wiring into the gate.** Adding these to the gate would need a budget file and a closure entry. That is out of this prototype's scope: nothing here touches the repository.
