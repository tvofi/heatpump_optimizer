Builds outside pull request #3443 (Bankaifan, fork head 01188a68b0, kept as the first commit 698f643b65 with the contributor's authorship, date and tree; its message lost only the session-link and co-author trailers `ref_privacy` refuses) into one seam. Home Assistant 2026.11 serves the climate temperatures under the native names and logs every class still defining the old ones (removal stated 2027.11); the supported floor 2025.2.0 reads only the old ones. The contributor's plain rename breaks the climate entity on every core below 2026.11: on 2025.2.0 it reads `AttributeError` for the unit (Figures, harness at 01188a68b0).

The entity's logic lives once, under the native names. `HeatPumpOptimizerEntity._PRE_NATIVE`, beside `_PUBLISHED` in `custom_components/heatpump_optimizer/entity.py`, maps each native member to its pre-native spelling; `__init_subclass__`, after the finite scrub, installs the old name as the same member object only where no `homeassistant` base of the class carries the native member. Detection is on the base class, never a version. On a core whose base carries the native names the class holds none of the old ones, so `migrate_deprecated_entity_members` reports nothing. A later platform with the same deprecation gets its alias from the table.

Alternatives not taken: a module-level patch in `climate.py` after the class statement (the shape #3443's body describes; a second helper outside the mechanism owning the published names, and the scrub would not cover it without repeating it); two property bodies per name (the logic twice); a version comparison (the brief refuses it: the base class is what the core reads); raising the floor (out of scope by the brief).

`tests/nightly_ha.py` gains `log:no_deprecated_member` (OUTSIDE_CHECKS), failing a run whose Home Assistant log carries `provides the deprecated` beside this package's name: the WARNING has no traceback, so no existing scan read it. It runs on both images of CI's `nightly-ha` matrix at this head.

Closes nothing by keyword; the orchestrator closes #3443 after merge.

## Head

094b128ad015a259432dda27af5f500b32122476 (on a merge of the dispatched base a7628041dc into the branch, 259d1427a4; origin/main a7628041dc at 2026-11-11T08:35:06Z). 094b128ad0 is fa82da62a0 with the contributor's commit message re-authored (`git rev-parse HEAD^{tree}` reads e94a886f59 at both). The mutation proof and `tests/finite_boundary.py` were re-run at that tree; the null control, the gate run and the arch score were taken at 259d1427a4, which differs from 094b128ad0 only in `tests/closures.json` and `tests/mutation_ledger/`.

## Mutation proof

Check: `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`, the arm `_native_alias_check`, run at 094b128ad0 (baseline `ALL 113 FINITE BOUNDARY CHECKS PASSED`). Each mutant is a single text substitution in `custom_components/heatpump_optimizer/entity.py`, restored after (`cmp` against the saved original):

- **alias never installed** (`setattr(cls, old, getattr(cls, name))` -> `pass`): `FAIL on a core without native climate names the old names read the scrubbed native values  [read ('base default', 'base default', 'base default')]`, `FAIL on a core without native climate names each old name is the native member object itself`; 2 of 113 failed.
- **alias always installed** (`if any(` -> `if False and any(` on the base-carries-native test): `FAIL on a core with native climate names the class carries none of the old names  [carried ['_attr_temperature_unit', 'current_temperature', 'target_temperature']]`; 1 of 113 failed.
- **scrub dropped on the alias** (the alias set to a property over the unscrubbed getter): `FAIL every climate entity publishes finite values from non-finite input (#1541)`, `FAIL ... the old names read the scrubbed native values  [read (nan, 21.0, ...)]`, `FAIL ... each old name is the native member object itself`; 3 of 113 failed.
- **null mutant** (comment text changed): `ALL 113 FINITE BOUNDARY CHECKS PASSED`.

Failing test first: commit 6d746325fb (the arm alone over 01188a68b0) reads `2 of 113 FINITE BOUNDARY CHECKS FAILED`, the two without-native arms.

`log:no_deprecated_member`: `_scan_pin` driven with the real 2026.11.1 line naming `custom_components.heatpump_optimizer.climate` reads `FAIL log:no_deprecated_member  [1 line(s) ...]`; with an empty log and with the same line naming another integration, `ok ... [0 line(s)]`.

## Null control

Real cores, not stubs: `dev/audit/harnesses/climate_native_alias_realcore.py` (sha1 0fae779985880af8640049319049f59d0e9dd415, in this diff) reads the climate entity's `capability_attributes` and `state_attributes` (current_temperature, temperature, min_temp, max_temp, target_temp_step) under the metric and US-customary systems, for a measured 20.5 °C and a NaN reading, on the real `ClimateEntity` of `homeassistant==2025.2.0` (Python 3.13) and `homeassistant==2026.11.1` (Python 3.14). Trees from `git archive` at a7628041dc (main), 01188a68b0 (author) and this head.

- 2025.2.0: main and head print byte-identical JSON (sha1 prefix c62f6ad272cd both); 0 deprecation lines at either end. The author tree reads `AttributeError: ... '__attr_temperature_unit'` in all four cells.
- 2026.11.1: the attribute block (deprecation lines removed) hashes 32d1adb2a070 at both main and head; main carries 3 deprecation lines (`_attr_temperature_unit`, `current_temperature`, `target_temperature`, each naming `heatpump_optimizer.climate::HeatPumpOptimizerClimate`), head 0.
- A NaN reading publishes `current_temperature: null` at both ends on both cores, metric and US-customary.

Precondition of the finding, checked first: `hasattr(ClimateEntity, "native_current_temperature")` reads True on 2026.11.1 and False on 2025.2.0. The CI `stable` image itself was not reachable from this container (no Docker daemon); the wheel is the same release. The two-image `nightly-ha` run at this head is CI's, past the handoff: its `log:no_deprecated_member` is the stable image's end of this control.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` at the head: `ALL 113 FINITE BOUNDARY CHECKS PASSED`; at 6d746325fb: `2 of 113 FINITE BOUNDARY CHECKS FAILED`.
- `python3 dev/audit/harnesses/climate_native_alias_realcore.py <tree>/custom_components` under each core's interpreter, recipe in its docstring: the hashes and counts in `## Null control`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 24 script(s) run, 9 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`: every scoped script ok but `tests/arch_score.py`, whose one failure was `fatal: '/opt/hpo/runner-temp/base' already exists` (a scratch directory a killed earlier run of mine left); rerun alone after removing it: `ALL 279 ARCHITECTURE SCORE CHECKS PASSED`. `tests/harness_headers.py` alone: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, so its dead-member count did not rise with the renamed properties.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.5850 IMPROVES`, `dead_members 2 -> 1`.

## Architecture score

dead_members 2 -> 1: the gate reads an improvement; no metric rises.

## Unpinned sites

- `custom_components/heatpump_optimizer/entity.py:266 GUARD_OFF` (`if not hasattr(cls, name):`): pinned in this diff by `python3 tests/mutation_table.py --pin-killed --base origin/main` at 259d1427a4, killed by `tests/debug_collect.py` (`PIN KILLED: 5 pinned, 0 left unpinned`; the other four are the renamed climate property sites, `climate.py:137`, `:143`, `:147`, `:159`).

## Red checks

none

## Forward-carry

none

## Friction

- tests/arch_score.py: cost: a second run in the same container failed `arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)` with `fatal: '/opt/hpo/runner-temp/base' already exists`, a directory a passing run leaves behind (present after the clean rerun); removing it cleared the failure. Carry: dismissed: a local-rerun cost only, not traced to its cause in this seat; CI runs once per fresh runner.
