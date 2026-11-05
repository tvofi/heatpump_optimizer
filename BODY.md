Accept a `water_heater` entity as the DHW set-point (`dhw_setpoint_entity`).

Some pumps expose their hot-water set-point only as a `water_heater` entity — Luxtronik's `water_heater.<id>_domestic_water` is one (state = operation mode, target in the `temperature` attribute, range `min_temp`/`max_temp`, step `target_temp_step`, all in the instance's unit). The selector offered only `number`, `input_number` and `climate`, so such an install could not configure the slot. A `water_heater` carries the climate shape, so this treats it as one: read, range, step and unit follow the climate path, and the write goes through `water_heater.set_temperature`.

Changes: `inputs.py` (`SETPOINT_SERVICES`, `_RANGE_KEYS`, `_STEP_KEYS`, and `setpoint_unit` now keys on `_ATTRIBUTE_TARGET_DOMAINS = ("climate", "water_heater")`), `config_flow.py` (selector domain list), the `dhw_setpoint_entity` help text in `strings.json` / `en.json` / `sv.json`, the #1526 service table in `tests/features.py`, one new check in `tests/features.py`, and `tests/golden/config_flow.json` re-recorded with `--only config_flow` (the two `dhw_setpoint_entity` filter lines move, nothing else).

**Contributor credit.** This change is by the outside contributor Bankaifan, first opened as PR #3224 (https://github.com/tvofi/heatpump_optimizer/pull/3224, head `a1fc6edb0e7fb51015bb50cb66b4c9bbbecfe877`). It is re-authored here as a seat pull request because decision 0011 gives an outside contributor no way to author one: the contributor's commits are cherry-picked unchanged, each keeping its author (Bankaifan), onto origin/main with no squash and no edit, and the three-dot diff is the same patch as the original (identical patch-id). The measurements below are the contributor's, from their own head; the review of this pull request re-derives them.

## Head

`9376cfbc585a64336136f3514588e14d09cfcee4`

## Mutation proof

Removing the one line `"water_heater": ("set_temperature", "temperature"),` from `SETPOINT_SERVICES` in `inputs.py` (everything else at the head unchanged) turns two checks red — `2 of 4831 FEATURE CHECKS FAILED`, `PYTHONPATH=tests/hastub python tests/features.py`:

- `every domain a written slot accepts is commanded through a service that domain implements (#1526)` — `water_heater.p6_dhw_setpoint_entity: the consumer issued no call`
- `a water_heater DHW set-point is read from its temperature attribute, clamped to min_temp/max_temp and written on its target_temp_step` — `'write 52.3': None, 'write 50 degC on degF': None` (read, range, step and clamp still pass: they are pinned by the `_RANGE_KEYS` / `_STEP_KEYS` / `setpoint_unit` changes, not by the service table)

## Null control

On unmodified `main` (`e57dfbbe0`), with the same Luxtronik-shaped state (`temperature` 62, `min_temp` 30, `max_temp` 65, `target_temp_step` 0.5):

- `setpoint_range_c` → `(None, None)` (range ignored, no clamp)
- `setpoint_step` → `1.0` (the 0.5 step ignored)
- `write_setpoint(…, 52.3)` → `False`, no service call
- selector → `_entity_of(['number', 'input_number', 'climate'])`

## Figures

- `ALL 4831 FEATURE CHECKS PASSED` at the head — `PYTHONPATH=tests/hastub python tests/features.py`
- live smoke test on a real Luxtronik install (HA 2026.10.4): read 62, range 30–65, step 0.5, write 52.3 → `water_heater.set_temperature(temperature=52.5)`

Environment caveat: measured on CPython 3.14.6 with `tests/requirements-ci.txt` hash-pinned; `seat_venv.sh` asks for 3.14.7, which `uv` could not fetch here, so the mypy census and the full `GATE_SCOPE=auto ./tests/run.sh` were **not** run.

## Unpinned sites

`custom_components/heatpump_optimizer/inputs.py:478` GUARD_OFF (`if entity_id.split(".", 1)[0] in _ATTRIBUTE_TARGET_DOMAINS:`) is the line the contributor's change edits; its old pin (`setpoint_unit.GUARD_OFF.2c91312e`) is dropped in this pull request's last commit because the edit made it stale, and `mutation-autofix` pins the line afresh if `tests/features.py` kills `if False:` there. Not yet pinned at open.

## Red checks

none: no check has concluded on this pull request yet (it was just opened); the reviewer reads every check-run of the head. The contributor's earlier note about `pr-contract` refusing the original author does not apply to this seat-authored pull request.
- `mutation` at 9376cfbc585a: red by construction on the 1 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

none

## Friction

none
