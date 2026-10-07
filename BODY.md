Closes #1745.

The entry's merged data and options are parsed once, at coordinator construction, into a frozen `EntryConfig`. Each stored key it declares has one default and one coercion. Readers in the migrated modules take the field. A mapping handed to a price reader is parsed at that boundary; an `EntryConfig` is returned unchanged. Whole-mapping parsers (thermal parameters, grid fee, topology, wood, the options form, service data, the quiet-window what-if) still take the mapping; `tests/entities.py` names each of those modules and why.

`const_modules_over_50` stays at its cap because `entry_config` reads `const` by attribute, the binding `store.py` already uses. `CONF_COP_SCALE` stays a live name because the thermal-learning store uses it.

### Merging origin/main (twice: 3910026e, then 38c03d94)

The branch conflicted with main in eight files, then in two more after main moved again. Each resolution keeps main's change and reads the configuration through the parsed object:

- `__init__._handover_interval_minutes` takes #1739's merged mapping and parses it with `EntryConfig`.
- `away`, `diagnostics`: #1739's explicit inputs and `CoordinatorDiagnostics` view kept; the presence and return slots read as parsed fields; `cop_scale` stays keyed by `CONF_COP_SCALE`.
- `pump_arbiter`, `setpoint_check`, `sensor`, `coordinator.configured_quiet_windows`: R9-SW-1/4/5's capacity-limited slot, silent and off specs and the published fraction read as parsed fields. `EntryConfig` declares `heat_pump_capacity_limited_entity`, `quiet_silent_windows` and `quiet_off_windows` (`""` where none is stored). `ArbiterInputs.config` is a `Mapping`, since the coordinator passes its `EntryConfig`.
- `coordinator.model_restart_advice` (#1936) read `CONF_OPTIMIZATION_INTERVAL` off the mapping using names this branch had dropped from the import: a `NameError` the auto-merge would have shipped. It reads the parsed field.
- `optimizer`: #1955's `clamp_planned_levels` joins the parsed-field build.
- **A behaviour change the reviewer should judge.** `quiet_windows.apply_config_keys` wrote a `set_thermal_parameters` call's quiet keys into the live configuration. That configuration is now frozen, so the write raises. The options write that follows it differs from the configuration the coordinator was built from, so the update listener reloads the entry, and the new coordinator parses the keys. The fold, its `features.py` check and its two mutation pins are removed. The SW-1 check that pinned the live write now pins the options write, the reload condition and the reloaded parse. On main, a call that changed only quiet keys was applied live without a reload; here it reloads, like every other options change.
- Module counts: both sides added a module, so the agreeing `70 -> 71` edits are 72 (`docs/architecture.md`, the `claims.py` header, the regenerated D6 claims), and the deployment-shape closure is 90 files.
- Main's new tests and `tools/audit/harnesses/solve_inputs_parity.py` wrote into `coord._config`; they go through `harness.with_config`. The harness falls back to the dict write in a base tree.

## Head

5947316c55e06b03c9e37fca93f4bf8e9b64a9fb

## Mutation proof

The merge's own behaviour is pinned by a new `tests/entities.py` check, "a stored None quiet spec reads unset, and a quiet window set by the service persists through the options write while the parsed configuration stays as built". A standalone driver of that check's exact inputs (an entry with `quiet_off_windows: None` and an empty capacity-limited slot, then `async_update_thermal_params({"quiet_silent_windows": "22:00-06:00"})`) was run against a copy of the package at this head with one replacement each:

- M0, null (a no-op replacement): PASS.
- M1, the fold restored (`ctx._config[k] = params[k]` for the two quiet keys before the DHW-windows block): FAIL, `TypeError: 'EntryConfig' object does not support item assignment`.
- M2, `_spec` unguarded (`return str(value)`): FAIL, `quiet_off_windows == 'None'`.
- M3, the slot stored raw (`_key(None, _as_stored)`): FAIL, slot `''`.

A full `tests/entities.py` run under M1 was attempted and is not cited: the interpreter on `PATH` had changed to 3.11, which cannot parse the file. Under the owner's 2026-10-07 rule the mutation drive is CI's.

The branch's original proof stands: replacing the parse in `EntryConfig.from_mapping` with the raw stored value fails "a stored value no reader can parse builds, and every reader takes the one declared default" and "a number stored as text is the same number to every reader".

## Null control

M0 above. The undefined-name scan used on the merged package (a module-level `ast` walk for loaded names that nothing defines or imports) prints `files=72 with_undefined=0` at this head. The same scan over `coordinator.py` with the `#1936` line as main wrote it prints `['CONF_OPTIMIZATION_INTERVAL', 'DEFAULT_OPTIMIZATION_INTERVAL']`.

## Figures

Merge base `38c03d9419248322079dc3ba2fad9edcc931e961`. `origin/main` at measurement `45142cc3b2302b646ebd2d5b45e2d7664152a7bb`, which merges with this head without conflict (`git merge-tree --write-tree`). 2026-10-07T14:52Z. Interpreter: `~/.local/state/hpo/venv-ci/bin/python3` (3.14.7).

```
python3 tests/closure.py select --diff 38c03d9419248322079dc3ba2fad9edcc931e961 --workdir <dir>
```

`MODE: SCOPED -- 28 script(s) run, 4 scoped out.`

Local, at this head, run one at a time with `PYTHONPATH=tests/hastub`:

- `python3 tests/entities.py`: `ALL 2209 ENTITY CHECKS PASSED`. The entry-config census reports no stray mapping read in a migrated module, no stale disposition, and no unclassified module. Residuals: `away.py`, `dhw_schedule.py`, `grid_fee.py`, `price_model.py`, `quiet_windows.py`, `thermal_model.py`, `topology.py`, `wood_fuel.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `max_class_loc` was recorded 8883 -> 8880 in 8c04fcd7, with the reason in that commit. `duplication_copies` is 38 within 38: the head before this merge measured 39, because `_optional_number` duplicated `_number`; it now reuses `_refused_number`.
- `python3 tests/config_flow_steps.py`: `ALL 496 checks PASSED`. `tests/doc_claims.py`: `ALL 160 checks PASSED`. `tests/dst_checks.py`: `ALL 131`. `tests/typing_ruler.py`: `ALL 11`. `tests/deployment_shape.py`, `tests/guard_pins.py` (`ALL 47`), `tests/solar_alignment.py`: passed. `tests/wood_advisor.py`: `ALL 7`.
- `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` regenerates `claims.json` and `claims.md` byte-identical to the committed files.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/harnesses/solve_inputs_parity.py`: exit 0 (at bdc519b9's tree plus the harness change; it raised on the frozen config before).

Heavy scripts are CI's (owner, 2026-10-07): `tests.yml` was dispatched on `handoff/r9-eg-entry-config` at this head, run 37640455476. Its check-runs are to be read through the API at this head; none are cited here.

Before the owner's rule, `tests/features.py` ran locally at this head (`1 of 3822 FEATURE CHECKS FAILED`, only R9-F2.1 P3) and `tests/arch_score.py` passed (`ALL 158`). Those are recorded as context only.

Disclosed self-correction: the previous body named fc0aff72 as its head, not the handoff head 3f593fda. Its `structure.py` exit 0 was taken before fc0aff72, the commit that put `duplication_copies` at 39.

## Red checks

`tests/features.py` `R9-F2.1 P3` (two-zone), locally only: shipped 110.4366, seeded 110.1297. These are the same figures the previous body recorded for both this branch and the 86dbf0ca merge-base package on this machine, so the merge does not move it. CI's Linux lane decides it.

## Forward-carry

none. The modules that still read a mapping are named, with why, in `tests/entities.py`'s `_EC_RESIDUAL` and `_EC_NOT_ENTRY`.

## Friction

none.
