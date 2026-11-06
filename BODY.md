Accept a `water_heater` entity as the DHW set-point (`dhw_setpoint_entity`).

Some pumps expose their hot-water set-point only as a `water_heater` entity — Luxtronik's `water_heater.<id>_domestic_water` is one (state = operation mode, target in the `temperature` attribute, range `min_temp`/`max_temp`, step `target_temp_step`, all in the instance's unit). The selector offered only `number`, `input_number` and `climate`, so such an install could not configure the slot. A `water_heater` carries the climate shape, so this treats it as one: read, range, step and unit follow the climate path, and the write goes through `water_heater.set_temperature`.

Changes: `inputs.py` (`SETPOINT_SERVICES`, `_RANGE_KEYS`, `_STEP_KEYS`, and `setpoint_unit` now keys on `_ATTRIBUTE_TARGET_DOMAINS = ("climate", "water_heater")`), `config_flow.py` (selector domain list), the `dhw_setpoint_entity` help text in `strings.json` / `en.json` / `sv.json`, the #1526 service table and one new check in `tests/features.py`, and `tests/golden/config_flow.json` re-recorded (the two `dhw_setpoint_entity` filter lines move, nothing else).

**Contributor credit.** This change is by the outside contributor Bankaifan, first opened as PR #3224 (https://github.com/tvofi/heatpump_optimizer/pull/3224, head `a1fc6edb0e7fb51015bb50cb66b4c9bbbecfe877`). It is re-authored here as a seat pull request because decision 0011 gives an outside contributor no way to author one: the contributor's three commits are cherry-picked unchanged, each keeping its author (Bankaifan), with no squash and no edit, and their three-dot diff is the same patch as the original (identical patch-id). The feature measurements below are the contributor's, from their own head.

**Repair on top of the contributor's commits (this revision).** Two seat commits and a merge of main, nothing in the contributor's commits touched:
1. `tests/golden/claimed_drift.txt` gains a `config_flow` claim. The re-recorded `config_flow.json` moves two leaves against base; with no claim, `tests/env_drift.py --all <base>` reports `1 UNCLAIMED DRIFT(S)`, which is what turned `tests / fast (3.14)` red, and that same red baseline made `mutation-autofix` end `skip-measure-failed` (its pin drive refuses to read any verdict from a red baseline). The claim states the footprint: two leaves, the plain and the seeded render of `dhw_setpoint_entity.config.filter`, nothing else moves. The brief for this repair listed the claim files as untouched; this one claim is the repair, since the red cannot be cleared otherwise (claim-files rule: drift is declared, a fixture is not re-recorded to hide it).
2. `tests/mutation_ledger/killed_by/inputs.py/setpoint_unit.GUARD_OFF.d9727610.json`, written by `mutation_table.py --pin-killed`.

## Head

`70a1c95f0a2ceb7602b48164a37368a52d8d389f` (the previous PR head `6f3b23fd9c8984479046d6a4e88b857acff3ae3c` plus the two seat commits plus two merges of origin/main, the last at `785c2b604ba4c01891737a5285f4f4f49394c18f`; the drift and pin figures below were measured at the first merge, `7c83525cd52c243a3a4a6c18a5eb02578d0b803b`, and the second merge touches neither the golden fixtures nor `inputs.py`, `config_flow.py` or `tests/features.py`). The seat commits are authored under the seat's configured identity, not `hpo-fixer`: an environment-level author variable overrode the per-commit setting, and rewriting pushed history was not worth it.

## Mutation proof

Removing the line `"water_heater": ("set_temperature", "temperature"),` from `SETPOINT_SERVICES` turns two checks in `tests/features.py` red (contributor's run):

- `every domain a written slot accepts is commanded through a service that domain implements (#1526)` — `water_heater.p6_dhw_setpoint_entity: the consumer issued no call`
- `a water_heater DHW set-point is read from its temperature attribute, clamped to min_temp/max_temp and written on its target_temp_step`

The newly pinned site, `custom_components/heatpump_optimizer/inputs.py:478 GUARD_OFF` (`if False:` in place of the domain test in `setpoint_unit`), is killed by `tests/features.py`: the pin drive recorded `rc=0 failed=0` unmutated and `rc=1 failed=4` mutated, the file being the pin's `reason`. The null control of that drive (`inputs.py:88 NULL_COMMENT`, a comment-only edit) survived every driver.

## Null control

On unmodified `main`, with the same Luxtronik-shaped state (`temperature` 62, `min_temp` 30, `max_temp` 65, `target_temp_step` 0.5): `setpoint_range_c` → `(None, None)`, `setpoint_step` → `1.0`, `write_setpoint(…, 52.3)` → `False` with no service call, and the selector is `_entity_of(['number', 'input_number', 'climate'])`.

## Figures

- `ALL 4831 FEATURE CHECKS PASSED` at the contributor's head — `PYTHONPATH=tests/hastub python3 tests/features.py` (contributor's figure, not re-run as a whole by this seat; the pin drive's unmutated baseline run of the same script at this head read `rc=0 failed=0`)
- unpinned mutation sites: 3091 at this head against 3091 at base, 0 added by this diff — `python3 tests/mutation_table.py --pin-killed --base origin/main` (before the pin: 3094 against 3093, 1 added; the same command)
- `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 7d95405e384e1ebf8223f04657c85996af55f3d9` at this head — `python3 tests/env_drift.py --all 7d95405e384e1ebf8223f04657c85996af55f3d9` (before the claim: `1 UNCLAIMED DRIFT(S)`, the same command)
- `PRE-PR: … rc=0` on the committed merged head — `bash tools/pr/prepr.sh` (no body passed, so its body check was not run; main had moved between the first and the final run, so it was merged and prepr re-run once)

Toolchain: the seat's cached venvs matched the locks (numpy 2.5.4 and scipy 1.18.1, as `tests/requirements-ci.txt` pins) after `tools/audit/seat/cloud-setup.sh`; CI remains the authority for the goldens.

## Red checks

Every concluded red across all 56 check-runs of the previous head `6f3b23fd9c8984479046d6a4e88b857acff3ae3c` (and its two runs), causes read from the logs. The final head has no concluded check yet; the reviewer reads its check-runs.

- `tests / fast (3.14)` — `FAILED python3 tests/env_drift.py --all 203b4dfc…`, `DRIFT config_flow: 2 leaves moved`, `1 UNCLAIMED DRIFT(S)`. Cause: the re-recorded fixture with no claim. Cheaper detector: it existed — `tests/env_drift.py --all <base>` is in the scoped `scope.run` and `prepr.sh` and takes about 3 minutes (CI's was 174 s); the outside contributor had no 3.14.7 environment to run it in (their note said so). Standing cost of a countermeasure: none worth adding; the existing local check was not reachable from the contributor's box. Fixed by the claim commit.
- `tests / mutation` — `MUTATION TABLE REFUSED -- 3094 unpinned site(s) against 3093 … 1 of them added by this diff`, the site `custom_components/heatpump_optimizer/inputs.py:478 GUARD_OFF`. Cause: the edit made the old pin stale and the new line had no pin. Cheaper detector: `mutation_table.py --pin-killed` (about 5 minutes) and the `mutation-autofix` job. Fixed by the pin commit.
- `tests / mutation-autofix` — `skip-measure-failed -- THE REPAIR DID NOT HAPPEN`. Cause: its baseline `tests/env_drift.py` run was red on the unclaimed `config_flow` drift above (reproduced here: the first `--pin-killed` run read `MUTATION TABLE INCONCLUSIVE`, baseline red in `tests/env_drift.py`; after the claim it pinned). A second symptom of the same cause, not a separate defect.
- `gate` (both runs) — the aggregate: `FAIL tests / fast (3.14)`, `tests / mutation`, `pr-contract`. Clears with them.
- `pr-contract / pr-contract` (both runs) — `check tests / fast (3.14) is red and ## Red checks does not name it` (and the same for `tests / mutation` and `tests / mutation-autofix`). Cause: the previous body said `none`. This body names them.
- `tests / nightly-status` — `NIGHTLY FAILED: slow failed last night` (scheduled run 41943946464, head 499162c). Main's, not required, outside this diff; the cause is not in this pull request and is the orchestrator's to dispatch.
- `governance / delivery-status` — overdue rows on main (#3189, #3204, #3203, #3202, #3174, …); not required, and this diff adds only its own row, `dev/programme/delivery/3231.md`. Main's, the orchestrator's to drain.
- `tests / replay` concluded `skipped` on that head, not red; if it reds on the final head, its `cycle_cost` runner-class band miss is main's, owned by R10-REPLAY-COST-BUDGET.

## Forward-carry

none

## Friction

none
