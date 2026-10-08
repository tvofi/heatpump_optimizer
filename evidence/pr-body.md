Closes #1745.

The entry's merged data and options are parsed once, at coordinator construction, into a frozen `EntryConfig`: one default and one coercion per declared key. Readers in the migrated modules take the parsed field, and `tests/entities.py` names the modules that still take the mapping, with the reason for each. Quiet-window service calls apply live by swapping in a new parse, as on main. Round 4 re-cut: this body replaces the earlier one.

## Head

`0662bd8e09b3cc3c57c6d6e79ac069ffaa7b297b` merges the authored code head `9b31227e01c4f2be07603b51eae21e0d9b793b62` and then merges origin/main `2d8cab3f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

9b31227e01c4f2be07603b51eae21e0d9b793b62

Changes since round 4's head, bfaf5486, in two commits:
- bd4ac1df, the `fast (3.14)` red. `EntryConfig.__reduce__` rebuilds an equal, frozen object from a plain dict of the stored values plus the parsed fields, so `copy.deepcopy` and `pickle` work. `tests/boost_drift_replay.py` deep-copies replay state that holds one. A new `entities.py` check pins the round trip.
- bd4ac1df, the payment. The two calls the conflict merge and df9131ab had joined onto one line are wrapped again, exactly as on main. The class is paid by moving the main fuse's continuous capacity (amps x phases x 230 V, None with no fuse) out of `HeatPumpOptimizerCoordinator` into `EntryConfig.fuse_kw()` and `fuse_kw_at()`. `_fuse_kw` now delegates in one line, and the fuse advisor's second copy of the formula is gone. A new `entities.py` check pins both methods.
- 9b31227e records `max_class_loc` 8819 -> 8817, with the reason in the commit. No budget was raised.

## Mutation proof

Each mutant was applied in place at this head, then `PYTHONPATH=tests/hastub python3 tests/entities.py` was run, then `git checkout -- custom_components` (the tree was clean after each). The unmutated baseline was `ALL 2217 ENTITY CHECKS PASSED`.
- `__reduce__` renamed away: 1 of 2217 failed, "an EntryConfig survives deepcopy and a pickle round trip ...", with `TypeError`.
- `fuse_kw_at` without the phase factor: 1 of 2217 failed, "the configured fuse is 20 A x 3 phases = 13.8 kW ...", reading 4.6.
- `fuse_kw` without its `amps > 0` guard: 6 of 2217 failed, among them the same fuse check and "with no fuse and no capacity tariff there is still nothing to report".

## Null control

The unmutated baseline above: all 2217 checks pass, including both new ones, so each kill above is the mutant's. Before the fix, at bfaf5486, the reviewer reproduced `copy.deepcopy(EntryConfig.from_mapping(...))` and `pickle.dumps` raising `TypeError`. The reviewer's plant, which re-wrapped only the two joined calls, read `max_class_loc=8823`. With the same two calls wrapped at this head it reads 8817.

## Figures

Merge base `2d8cab3f75ddc8c2e42877092cd14bd1ffb01d38` (= `origin/main` at measurement, 2026-10-08). Interpreter: venv-ci python3 3.14.7. All scripts were run one at a time at this head:
- `tests/entities.py`: `ALL 2217 ENTITY CHECKS PASSED`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`, `max_class_loc 8817 <= 8817`.
- `HPO_TYPING_PYTHON=<pinned typing venv> python3 tests/typing_ruler.py`: `ALL 12 typing-ruler source checks PASSED`, mypy included.
- `tests/manual_plan.py`: `ALL 129`.
- `tests/config_flow_steps.py`: `ALL 496`.
- `tests/closure.py selftest`: `ALL 39 closure shrink pins PASSED`.
- `python3 tools/pr/ci_predict.py`: "no closures or fast red predicted", and 63 added unpinned sites, listed below.

Heavy scripts, `tests/boost_drift_replay.py` included, are CI's under the owner's 2026-10-07 rule. They were not run locally at this head.

## Red checks

- `fast (3.14)` (job 113048537751, bfaf5486): this PR's. `tests/boost_drift_replay.py` raised `TypeError: cannot pickle 'mappingproxy' object` deep-copying an `EntryConfig`. Fixed in bd4ac1df and pinned in `entities.py`. The cheaper detector is that `entities.py` round-trip check, a few seconds out of a cheap script. The reviewer found no production deepcopy of the coordinator's context; the replay is the only copier.
- `mutation` (bfaf5486): the lane measured nothing ("56 not started for --budget-minutes"), and `mutation-autofix` therefore pinned nothing. Each site this diff adds is listed under Unpinned sites. No cheaper detector exists for an unmeasured lane; the local kills above cover this round's new code.
- `mutation-autofix` (job 113050887311, bfaf5486): it reported nothing to pin because the lane measured nothing. Answered under `mutation`.
- Reds on earlier heads of this branch, each answered in the round named:
  - `typing` (job 112880876862, a390f589): mypy grew 0 -> 9 and is 0 since round 2. The cheaper detector is `typing_ruler.py` under `HPO_TYPING_PYTHON`, green above.
  - `closures` and `closures-autofix` (jobs 112881062368 and 112897209809, a390f589; job 112857717705 at 5947316c): `entry_config.py` was missing from closures that import it. It was added in round 2, and `closures` is green at bfaf5486. The cheaper detector is `closure.py check --partial` against stand-in recordings, plus `ci_predict.py`'s closures arm, which predicts nothing here.
  - `mutation-nightly` (job 112857793518, 5947316c): its baseline raised in `tests/manual_plan.py` on a stand-in fixed in round 2. `manual_plan.py` is green above.
  - `budget-raise-gate` (job 113048531990, bfaf5486): a cancelled twin, not a failure. No budget leaf is raised.
- `delivery-status` and `nightly-status`: not this PR's. They report main's overdue rows and main's nightly, which this diff does not reach.

## Unpinned sites

Every site `tools/pr/ci_predict.py` lists as added and unpinned at this head is left to `mutation-autofix`. It pins each site once CI's mutation lane measures it. None was run, pinned or triaged locally: mutation drives are CI's under the owner's 2026-10-07 rule, and fixer.md step 2 leaves pinning to CI. The local kills under Mutation proof sit next to the `entry_config.py` fuse and `__reduce__` sites but are not these exact mutants.

- custom_components/heatpump_optimizer/__init__.py:179 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/binary_sensor.py:174 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:822 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:1764 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:1801 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:2327 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:3167 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:3275 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:4141 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:4187 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5051 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5462 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:5483 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6470 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6840 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6840 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6840 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6875 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6934 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:7124 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8130 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8160 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8298 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8444 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8628 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8723 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8783 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8814 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8869 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8901 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8934 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:8965 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:9017 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:9419 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:9809 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10144 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10531 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10604 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10604 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10776 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10791 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10824 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/disinfection.py:116 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/disinfection.py:121 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:37 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:43 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:52 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:55 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:75 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:80 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:97 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:255 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:260 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:262 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:266 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:266 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:271 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:271 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:281 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:295 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/legionella.py:194 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/sensor.py:704 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/silent_mode.py:104 GUARD_OFF: pinned by mutation-autofix

## Forward-carry

none. The modules that still read a mapping are named, with the reason for each, in `tests/entities.py`'s `_EC_RESIDUAL` and `_EC_NOT_ENTRY`.

## Friction

none.

