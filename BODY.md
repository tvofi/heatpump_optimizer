R9-F10.4: the structural ratchet measures what its names say, and the I5 doc-claims barrier.

Fixes #1661 (N-dead-member); Part of #1650 (I4); Fixes #1686 (N-structure-blind); Fixes #1645 (I5)
Fixes #1738
Part of #201

Before: `tests/structure.py` priced a class by names, not by what reaches it. `dead_methods` skipped every `@property` and treated any bare-name load as a use, so a property nothing read and a method whose name was also a local were both "live". Moving a method body into a module-level `_helper(self)` lowered `cut_learning`, `cross_seam_edges`, `internal_call_edges` and `coordinator_loc` at once, so the ratchet paid for a cut that cut nothing (#1686). Copies across modules, private reads from a platform, attribute writes from outside the class, import cycles and names reached through `import *` moved no metric at all. `doc_claims.py` had no arm for the entity census, the options menu pages or the multi-start count, and F8.1's and F8.2's section anchors raised `IndexError` instead of failing when a heading moved (I5).

After: the ratchet finds the coordinator by role and prices each of those edits. A cross-module copy, a private read or write from a platform, an outside store, an unread property, a self-reached method and an import cycle each move a named metric, and a helper cut from a method is charged to the method's seam. Seven dead members are gone. `doc_claims.py` checks the entity census, the options pages, the multi-start count and the `py.typed` claim, and a moved anchor is a named FAIL.

The metric set changed shape, so the budget file was re-recorded at base 3bd6f122. Two caps rise by redefinition only, and the orchestrator posts both on #201 before this merges: `dead_methods` 0 → 3 (the base measures 9 under the new definition, this branch removes 6) and `coordinator_multiassigned_attrs` 117 → 120 (the base measures 120 under the new definition, which counts writers outside the class). Every other key is at or below its base value under its own definition.

How: a role engine (`CoordinatorRoles`) seeds from `self`, the annotation, `CoordinatorEntity.coordinator`, `entry.runtime_data` and calls of the class, and propagates through call parameters and `self` slots. `dead_members` resolves each load by receiver and keeps only what is reachable from the roots. `duplicate_clones` hashes normalized 2-statement AST windows of at least 30 nodes across the package. `import_cycle_modules` is Tarjan over relative imports, function-scope imports included and `TYPE_CHECKING` imports excluded. Star imports now bind. `role_self_check` plants 16 cases, which brings the counting rules to 40.

**Metrics.**
- Retired: `attrbag_classes_over_30`, `classes_over_300`, `internal_call_edges` and `coordinator_methods`.
- Merged: `coordinator_loc` into `max_class_loc`, and `cross_seam_edges` with `cut_*` into `seam_cut_total`.
- Replaced: duplication blocks by `duplication_copies`, and `local_imports` by `import_cycle_modules`.
- New: `coordinator_private_reach`, which counts reads plus 3× writes, an in-place mutator being a write.

**Helpers' seams** (`tests/seam_map.json`, 12 entries): `_cop_fold_blocked` and `_watch_lift` are learning; `_power_windows` is views; `_note_solve_failure`, `_republish_handover_ages`, `_fold_flow_lift`, `_freq_fold_blocked`, `_with_sensor_advisor`, `_warm_seeded`, `_diagnose_payload`, `_store_diagnosis` and `_space_pump_to_drive` are core.

**Deleted members (D7-s3-01):**
- `HeatPumpOptimizerCoordinator.current_action`;
- `DefrostDerate.samples()` and `measured()`;
- `InputHealth.healthy`;
- `IrradianceSeries.start`;
- `OpenMeteoSolar.last_success`;
- `_Horizon.weather`.

**Left in this branch's tree, as instructed.** `last_optimization`, `next_optimization` and `floor_return_temp` are dead too and show up as the 3 in `dead_methods`. EG-B2 deletes them, so they are not in this diff. Whichever of the two merges second takes main in and re-records.

**D7-s3-72, refused.** The four write-only `_step_*` scratch members stay. They are the instruments the energy-conservation pins read through the step ledger, so deleting them removes the pins' evidence and not dead state.

**I4 reader pair.**
- Readers: `structure.py dead_methods` against the round-9 D7 finders `screen.py` and `reach.py`.
- Corpus: class-body members of `custom_components/heatpump_optimizer/**/*.py`.
- Counts: base 9 / 11 / 9; head 3 / 3 / 3.
- At base, screen's two extra members are `hvac_mode` and `preset_mode`, which Home Assistant reads by convention. They are now in `HA_CONVENTION_METHODS`.

**I5.**
- Taken from c6ba6036: the doc_claims arms `entity_census`, `check_entity_prose`, `check_private_mentions`, `check_unit_typography` and `check_option_labels`.
- Not taken: c6ba6036's `check_service_fields`, which F8.3's version supersedes.
- New arms: `options_field_pages` with `page_placement_problems` (the menu-page census), `multistart_count_claims` (a corpus-wide count) and `check_py_typed_claim` (RCA-BULK-3).
- `_section()` guards F8.1's and F8.2's anchors.
- `tools/audit/bugclasses.json` marks I5 and N-structure-blind barriered.

**Residuals.**
- Moving a method into a helper still lowers `max_class_loc`, by the moved lines. Seam totals are now flat under that move, which was #1686's complaint.
- 92 members are kept by name (HA conventions, runtime-assembled names) and are not measured for liveness. `structure.py` prints them.
- D6-s1-02's unlabeled prose stays out of the census, because it names no entity.
- At this head, two D7 finder harnesses do not run as they did at base. `s1/helper_escape.py` refuses because inlining leaves a stale seam-map entry, which the #1539 rule rejects. `leads/sentinel.py` raises `KeyError: current_action` because the member is deleted. Both are expected.

`tests/entities.py` edits stay inside its existing #1453 and finite-cap sections, because EG-B2 also edits that file.

## Head

a980e1650524c3782976e0631b2b4271ee797435

## Mutation proof

Twelve mutants of `structure.py`, each breaking one new rule. All 12 turn its self-check red, and the unmutated file passes (`rc=0 []`). Some examples:
- Taking properties out of the census fails "a property nothing reads is a dead member".
- Liveness by name fails "a member reached only from its own body is dead".
- Not charging helpers fails "a helper is priced as the method it was cut from (#1686)".
- No role propagation fails "an in-place mutation is a write, through a renamed parameter".
- Per-module duplication fails "a copy in another module is one copy, renamed or not".
- Treating `TYPE_CHECKING` imports as edges fails "a TYPE_CHECKING import is not an edge".
- A star import that binds nothing fails "a star import binds the public names it brings".

For doc_claims: at c6ba6036^ the arms report 25 FAIL, and at base 3bd6f122 they report 0. With an F8.1 or F8.2 heading renamed, the base raises `IndexError` and this head prints 2 named anchor FAILs.

## Null control

On the base tree, the perturbation run's two null rows ("no edit", and renaming `_fold_flow_lift`'s coordinator parameter) move nothing under either ratchet. The unmutated `structure.py` self-check is green with 40 counting rules. `doc_claims.py` at this head passes 112 checks.

## Figures

- Perturbation table (old ratchet against new, base tree): `python3.13 tools/audit/round9/F10/gate-infra-4/perturb.py <base-checkout> <base tests/structure.py> tests/structure.py tests/seam_map.json <base tests/seam_map.json>`
- Mutants: `python3.13 tools/audit/round9/F10/gate-infra-4/mutants.py .`
- Budgets, the 40 counting rules (24 + 16 planted role cases), and the 92 name-kept members it prints: `python3.13 tests/structure.py`
- Base under the new definitions (`dead_methods` 9, `coordinator_multiassigned_attrs` 120): `python3.13 tests/structure.py` run with this branch's `tests/structure.py` and `tests/seam_map.json` copied over a base 3bd6f122 checkout
- Duplication window of 2 statements and 30 nodes: the constants `DUP_WINDOW_STATEMENTS` and `DUP_MIN_NODES` in `tests/structure.py`, which `tests/features.py`'s #369 block pins
- doc_claims 112 checks: `python3.13 tests/doc_claims.py`
- entities 2053 checks: `python3.13 tests/entities.py`
- Scoped gate, `MODE: SCOPED`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- I4 reader counts: `python3.13 tests/structure.py`, alongside `tools/audit/round9/D7/s3/reach.py` and `tools/audit/round9/D7/s3/scan.py`, run at base and head.

## Red checks

none

## Forward-carry

none

## Friction

- `writing-for-agents: cost`: local `python3` is 3.11, CI is 3.13 and 3.14. `structure.py` uses `sys.monitoring` and nested f-strings, so every local run had to name `python3.13`. `tools/audit/prepr.sh` records closures with bare `python3`, so it refused `tests/entities.py` and `tests/harness_headers.py` as failed recordings on 3.11, at base 3bd6f122 as well. It passed once `python3` resolved to 3.13.
- `gate-scoping: cost`: the D7 finder harnesses patch `structure.is_property_getter`. Deleting it as dead broke them, so it stays with a docstring saying why.

_Requested by **tvofi**_
