Accept a `water_heater` entity as the DHW set-point (`dhw_setpoint_entity`).

Some pumps expose their hot-water set-point only as a `water_heater` entity — Luxtronik's `water_heater.<id>_domestic_water` is one (state = operation mode, target in the `temperature` attribute, range `min_temp`/`max_temp`, step `target_temp_step`, all in the instance's unit). The selector offered only `number`, `input_number` and `climate`, so such an install could not configure the slot. A `water_heater` carries the climate shape, so this treats it as one: read, range, step and unit follow the climate path, and the write goes through `water_heater.set_temperature`.

Changes: `inputs.py` (`SETPOINT_SERVICES`, `_RANGE_KEYS`, `_STEP_KEYS`, and `setpoint_unit` now keys on `_ATTRIBUTE_TARGET_DOMAINS = ("climate", "water_heater")`), `config_flow.py` (selector domain list), the `dhw_setpoint_entity` help text in `strings.json` / `en.json` / `sv.json`, the #1526 service table and one new check in `tests/features.py`, and `tests/golden/config_flow.json` re-recorded (the two `dhw_setpoint_entity` filter lines move, nothing else).

**Contributor credit.** This change is by the outside contributor Bankaifan, first opened as PR #3224 (https://github.com/tvofi/heatpump_optimizer/pull/3224, head `a1fc6edb0e7fb51015bb50cb66b4c9bbbecfe877`). It is re-authored here as a seat pull request because decision 0011 gives an outside contributor no way to author one: the contributor's three commits are cherry-picked unchanged, each keeping its author (Bankaifan), with no squash and no edit, and their three-dot diff is the same patch as the original (identical patch-id). The feature measurements below are the contributor's, from their own head.

**Repairs on top of the contributor's commits.** The contributor's three commits are untouched. Earlier rounds added the `config_flow` claim in `tests/golden/claimed_drift.txt` (the re-recorded fixture moves two leaves; without the claim `tests/env_drift.py --all <base>` reads `1 UNCLAIMED DRIFT(S)`) and the `setpoint_unit.GUARD_OFF.d9727610` pin. This round (the review of bd0ee867e49b blocked on mutant m4) adds one test-only commit: a degF leaf for the water_heater DHW slot in `tests/features.py` as its own check, plus a commit dropping the earlier round's stale `PR-BODY.md` from the tree (it failed the `tests/entities.py` classification check once merged in). No production, golden or claim-file change in this round.

## Head

`b3bb708c05a3bfb54797cb62f0cedf6a48c8d763` (the previous PR head `bd0ee867e49bf6f0af414efcf2aa29ae775ac926` plus the test commit, the PR-BODY.md removal and two merges of origin/main, the last at `c679f4b692f483959769ec5b5147aa4d624c45f4`). The two earlier seat commits are authored as `seat` (disclosed in earlier rounds); this round's commits are authored as `hpo-fixer`.

## Mutation proof

The new check `a water_heater DHW set-point on a degF instance reads its range in degC and is clamped to it` pins `setpoint_range_c` == (30.0, 65.0) and the arbiter's DHW clamp (70 degC -> 65.0, 20 degC -> 30.0) for a degF water_heater with min_temp 86 and max_temp 149. Measured on tests/features.py, each mutant in a copy of the head:

- m4, `_ATTRIBUTE_TARGET_DOMAINS = ("climate",)`: `1 of 4860 FEATURE CHECKS FAILED`, the new check, reading `range (86.0, 149.0)`. Before this commit the same mutant printed `ALL 4859 FEATURE CHECKS PASSED` (the review's block).
- m1 (water_heater out of SETPOINT_SERVICES): 2 failed (the #1526 service-table check and the contributor's water_heater check).
- m2 (out of _RANGE_KEYS): 2 failed (the contributor's check and the new one).
- m3 (out of _STEP_KEYS): 1 failed (the contributor's check).
- m6 (`if False` at inputs.py:478): 4 failed (three climate checks and the new one), which now matches the pin reason's `failed=4`.

## Null control

Unmutated head: the new check passes (`ALL 4860 FEATURE CHECKS PASSED`, 4859 plus the one new check). On unmodified main the contributor's water_heater slot reads `range=(None, None)`, `step=1.0`, and `write_setpoint(..., 52.3)` makes no call (the contributor's null control, re-read by the reviewer).

## Figures

- `ALL 4860 FEATURE CHECKS PASSED` at the test commit — `PYTHONPATH=tests/hastub python3 tests/features.py`
- `ALL 2632 ENTITY CHECKS PASSED` — `PYTHONPATH=tests/hastub python3 tests/entities.py` (after the PR-BODY.md removal; the first run failed only on that file)
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`, also at the merged head inside prepr
- `PIN KILLED -- 0 new unpinned site(s) against 750a6001ae4d…; PIN KILLED: nothing to pin`; `3091 unpinned site(s) of 6799 candidate sites, 3091 at the ratchet base` — `python3 tests/mutation_table.py --pin-killed --base origin/main`
- `PRE-PR: … rc=0` on the merged head — `bash tools/pr/prepr.sh` (no body passed; the body check runs in body_push). Main had moved (750a6001 to c679f4b6), so it was merged and prepr run once more after.

## Red checks

The final head is not pushed to the pull request yet, so it has no check-runs. At the PR's current head `bd0ee867e49b` the only concluded red the review read was `tests / nightly-status` (`NIGHTLY FAILED`, main's scheduled nightly, not required, outside this diff). Everything else was green (`merge_train.py classify`: `GREEN … red: none`). CI's `mutation` lane stayed green while m4 survived because a tuple-literal edit is not a mutant its operators draw; this commit closes that gap with a check.

## Forward-carry

none

## Friction

none
