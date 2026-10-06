Closes #1745.

The entry's merged data and options are parsed once, at coordinator construction, into a frozen `EntryConfig`. Each stored key it declares has one default and one coercion. Readers in the migrated modules take the field. A mapping handed to a price reader is parsed at that boundary; an `EntryConfig` is returned unchanged. Where the per-solve record already carries `price_risk_lambda`, `holiday_calendar_entity` or `fuse_guard_enabled`, it reads those fields. Whole-mapping parsers (thermal parameters, grid fee, topology, wood, the options form, service data) still take the mapping; the test names each of those modules and why.

`const_modules_over_50` stays at its cap because `entry_config` reads `const` by attribute, the binding `store.py` already uses. `CONF_COP_SCALE` stays a live name because the thermal-learning store uses it; the learning view still publishes the string `cop_scale`, which is what the payload census reads. `max_class_loc` and `seam_cut_total` are recorded down in the commit that states why.

## Head

fc0aff72aa1f28b5bbbcc898b919ed2b7d101b29

`tests/features.py` completed at 007d2cb9 (1 of 3699, the arm below). fc0aff72 replaces `_optional_number`'s type ignore with the same fallback; a stored `21.5`, an empty string, and an unparsable string still produce 21.5, None, and None.

## Mutation proof

In `EntryConfig.from_mapping`, the parse call was replaced by the raw stored value, the four-reader probe was run, and the file was restored (`git diff` empty).

FAIL a stored value no reader can parse builds, and every reader takes the one declared default
FAIL a number stored as text is the same number to every reader

Both fail as `TypeError: unsupported type for timedelta minutes component: str`. The well-formed arm stays green: a stored 15 and 7.0 still reach all four readers.

## Null control

The same probe with a well-formed stored interval and weight returns `(15 minutes, 15.0, 7.0, 7.0)`, which differs from the declared defaults. The configuration-read enumerator on a pattern that names no key prints 0.

The R9-F2.1 P3 two-zone storage solve prints shipped 110.4366 and seeded 110.1297 from both this tree's package and the package at 86dbf0ca. The single-zone arm passes on both.

## Figures

Merge base `86dbf0ca1d5e1bed903ec83b676a147f2eee8e49`. `origin/main` at measurement `51ebfc879e5854fc4a9b0d41ca56d026a94c85a8`. Measured 2026-10-05T23:59:35Z.

```
python3 -c "import re,pathlib,subprocess
def go(rev):
    files=subprocess.check_output(['git','ls-tree','-r','--name-only',rev,'custom_components/heatpump_optimizer'],text=True).splitlines() if rev else [str(p) for p in pathlib.Path('custom_components/heatpump_optimizer').glob('*.py')]
    texts=[]
    for p in files:
        if not str(p).endswith('.py'):
            continue
        texts.append(subprocess.check_output(['git','show',f'{rev}:{p}'],text=True) if rev else pathlib.Path(p).read_text())
    ms=[m for t in texts for m in re.findall(r'\.get\(\s*(CONF_[A-Z0-9_]+)', t)]
    print(rev or 'HEAD', len(ms), len(set(ms)), len({}))
"
```

That enumerator, run for `86dbf0ca1d5e1bed903ec83b676a147f2eee8e49` and for the worktree: base 283 reads, 150 keys, 20 modules; head 126 reads, 65 keys, 8 modules (`config_flow.py` 64, `wood_fuel.py` 23, `quick_setup.py` 17, `topology.py` 7, `services.py` 6, `price_model.py` 5, `away.py` 3, `modbus_prefill.py` 1). The null pattern `CONF_THIS_KEY_IS_ABSENT` on `coordinator.py` prints 0.

```
python3 tests/structure.py
```

`const_modules_over_50` 3, `dead_top_level_symbols` 1, `max_class_loc` 8751, `seam_cut_total` 757, exit 0, after the two improved rows were recorded.

```
python3 tools/audit/archscore/score.py --diff 86dbf0ca1d5e1bed903ec83b676a147f2eee8e49
```

`dS +0.0126 IMPROVES`. `coord_footprint` 2523 -> 2501, +0.0126. No other score metric moved. 2026-10-05T23:51:04Z.

```
GOLDEN_MODE=drift GOLDEN_REF=86dbf0ca1d5e1bed903ec83b676a147f2eee8e49 python3 tests/env_drift.py --all 86dbf0ca1d5e1bed903ec83b676a147f2eee8e49
```

`NO UNCLAIMED DRIFT: 56 scenario(s)`. `NO STALE FIXTURE: 56`.

```
PYTHONPATH=tests/hastub python3 tests/entities.py
```

`ALL 2176 ENTITY CHECKS PASSED` (run before fc0aff72; that commit does not change a field default).

```
PYTHONPATH=tests/hastub python3 tests/features.py
```

`1 of 3699 FEATURE CHECKS FAILED`, only `R9-F2.1 P3` two-zone, at 007d2cb9. The legionella unverified-cycle check is green in that run.

```
PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py
```

`ALL 496 checks PASSED`.

```
python3 tests/closure.py select --files <the diff including tests/closures.json>
```

`MODE: FULL` — `tests/closures.json` changes the gate itself. The same select without that file: `MODE: SCOPED -- 27 script(s) run, 4 scoped out`.

`tests/stress.py` was not run. `python3 tests/typing_ruler.py` with `HPO_TYPING_PYTHON` unset: `ALL 11 typing-ruler source checks PASSED`, including `type_ignores did not grow`.

Also green on this tree: `tests/deployment_shape.py`, `tests/doc_claims.py` (`ALL 160`), `tests/harness_headers.py` (`ALL 105`, after the claims record was committed), `tests/arch_score.py`, `tests/arch_score_head.py`, `tests/guard_pins.py`, `tests/solar_alignment.py`, `tests/edge.py`, `tests/validate.py`, `tests/backtest.py`, `tests/optimality.py`, `tests/plan_view.py`, `tests/manual_plan.py`, `tests/finite_boundary.py`, `tests/boost_drift_replay.py`, `tests/wood_advisor.py`, `tests/md_tables.mjs`, `tests/card.mjs`, `tests/card_drift.mjs`.

The entry-config census in `tests/entities.py` (`_ec_mapping_reads`) reports no stray mapping read in a migrated module, no stale disposition, and no module outside the migrated, residual, and not-an-entry sets. Residuals are `away.py`, `dhw_schedule.py`, `grid_fee.py`, `price_model.py`, `thermal_model.py`, `topology.py`, `wood_fuel.py`.

## Red checks

`tests/features.py` `R9-F2.1 P3` (two-zone). The check is the detector. On this machine the merge-base package and the head package both print shipped 110.4366 and seeded 110.1297, and the single-zone arm passes on both, so the diff does not move it. `tests/env_drift.py --all` against the same base reports no unclaimed drift.

## Forward-carry

none. The modules that still read a mapping are named, with why, in `tests/entities.py`'s `_EC_RESIDUAL` and `_EC_NOT_ENTRY`.

## Friction

none.
