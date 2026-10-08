Closes #1745.

The entry's merged data and options are parsed once, at coordinator construction, into a frozen `EntryConfig`: one default and one coercion per declared key. Readers in the migrated modules take the parsed field, and `tests/entities.py` names the modules that still take the mapping, with the reason for each. Quiet-window service calls apply live by swapping in a new parse, as on main. Round 4 re-cut: this body replaces the earlier one.

## Head

b21ed75e17d3307db11590b41173a151cfc695bf

Since c27b616d, two commits merge main 6b91e238:
- b29e4ee4 merges it. The `pump_arbiter.py` conflict with #2007 (SW-2 actuation) keeps both sides: SW-2's fourth slot, the silent switch, and its silent and off specs now read the parsed `heat_pump_capacity_limited_entity`, `quiet_silent_windows` and `quiet_off_windows`. Where nothing is stored those read `""`, which `_silent_rows` and `step_actions` treat as no rows, the same as `None`. SW-2's `features.py` stand-ins wrote items into the frozen configuration; they now rebuild it through `with_config`.
- b21ed75e drops two killed_by pins main had just recorded, `_dhw_probe_temperature` GUARD_OFF and `_silent_target` RETURN_DEL. Their anchors name the mapping-read text this branch rewrites, so the ledger refused them. The rewritten lines are listed under Unpinned sites, for `mutation-autofix` to pin again.

Changes since round 5's head, 0662bd8e, in two commits. Both are tests plus one production simplification. They answer the eight mutants R9-CI-1's sharded proof left alive, and the two its second proof could not confirm:
- cd7948e3: one `entities.py` check drives each parsed gate on both arms. It covers the lower-floor learner's sensor guard, open-window relax's `and`, the rain weighting's switch, the comfort-learning switch, `from_mapping`'s pass-through, and an unreadable silent fraction. `_optional_number`'s `if value == "": return None` is removed: an empty string is refused by the float parse and falls to the default, which is None for every optional field, so that branch changed nothing (an equivalent mutant).
- c27b616d: the capacity curve's two guards (`_fold_capacity_envelope`, `_capacity_caps`) join that check. The silent-mode arm now catches a raise, so a mutant that crashes it fails the check instead of the script.

## Mutation proof

Each survivor's exact `mutation_table.py` rewrite (`GUARD_OFF` -> `if False:`, `BOOLOP` -> `or`) was applied in place. `PYTHONPATH=tests/hastub python3 tests/entities.py` was run, then `git checkout -- custom_components`, and the tree was clean after each. The unmutated baseline at c27b616d is `ALL 2218 ENTITY CHECKS PASSED`. Every mutant fails exactly 1 of 2218, the gate check "each parsed gate closes on its off arm and opens on its on arm ...", on its own arm:

| survivor at the proof head | here | the arm that moved |
|---|---|---|
| coordinator.py:5048 GUARD_OFF | :5051 | lower floor learns without a sensor: (1, 1) |
| coordinator.py:5459 BOOLOP | :5462 | relax without the detector: ((1.0,), (1.0,)) |
| coordinator.py:6855 GUARD_OFF | :6840 | no rain weighting with the switch on: (2.0, 2.0) |
| coordinator.py:6855 BOOLOP | :6840 | weighting with the switch off: (0.5714, 0.5714) |
| coordinator.py:10817 GUARD_OFF | :10776 | the learned weight with learning off: (9.0, 9.0) |
| coordinator.py:8975 GUARD_OFF | :8901 and :8934 | fold: ((False, 1), (True, 1)); caps: ((True, 0), (True, 1)) |
| entry_config.py:255 GUARD_OFF | :256 | a parsed config re-parsed: (False, True) |
| silent_mode.py:104 GUARD_OFF | :104 | an unreadable fraction raises: ('TypeError', True) |
| entry_config.py:52 GUARD_OFF | removed | equivalent; the branch is gone (above) |

The 6840 GUARD_OFF run measured at c27b616d. Its first attempt, at cd7948e3, sat behind the shared gate lease for 1h46m and was stopped; that one entities run is not cited. The 5051, 5462, 6840 BOOLOP, 10776 and 255 kills were measured at cd7948e3, before c27b616d added the capacity arms. The proof head's `coordinator.py:8975` is matched by its text, `if not ctx._config.capacity_curve_enabled:`, and both guards with that text are covered.

The round-4 kills stand: `__reduce__`, `fuse_kw_at` and `fuse_kw`.

## Null control

Every arm the gate check compares has its on side, the null: the gate opens and the value moves (learns 1 sample, relaxes by `OPEN_WINDOW_RELAX_C`, weights rain to 0.5714 mm, plans with the learned 9.0, caps and folds, composes a silent cap). Each mutant above moved only its off side to equal the on side. The unmutated baseline passes all 2218 checks.

## Figures

Merge base `6b91e238f6883af6eedef0fc541bce76b14fc46c` (= `origin/main` 6b91e238). Interpreter: venv-ci python3 3.14.7. Run one at a time.
- At b21ed75e (this head): `tests/entities.py` `ALL 2218 ENTITY CHECKS PASSED`; `python3 tools/pr/ci_predict.py` reports "no closures or fast red predicted against 6b91e238f688" and 63 added unpinned sites, listed below.
- At b29e4ee4 (the merge): `tests/structure.py` `STRUCTURE RATCHET PASSED`; `tests/typing_ruler.py` under `HPO_TYPING_PYTHON`, mypy included, `ALL 12`; `tests/manual_plan.py` `ALL 129`. At b29e4ee4, `entities.py` failed 1 of 2218 on the two refused pins; b21ed75e drops them, and only the ledger changed in between.
- At cd7948e3: `tests/config_flow_steps.py` `ALL 496`; `tests/closure.py selftest` `ALL 39`.

Heavy scripts are CI's under the owner's 2026-10-07 rule.

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

The sites `tools/pr/ci_predict.py` lists as added and unpinned at this head. R9-CI-1's proof survivors carry a value check killed locally (Mutation proof). The rest are left to `mutation-autofix`, which commits the 40 pins R9-CI-1's proof measured once CI-1 merges. Nothing is pinned or triaged by hand here.

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
- custom_components/heatpump_optimizer/coordinator.py:5051 GUARD_OFF: value check, `entities.py`'s gate check (mutant: lower floor learns without a sensor; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/coordinator.py:5462 BOOLOP: value check, `entities.py`'s gate check (mutant: relax without the detector; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/coordinator.py:5483 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6470 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6840 BOOLOP: value check, `entities.py`'s gate check (mutant: weighting with the switch off; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/coordinator.py:6840 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:6840 GUARD_OFF: value check, `entities.py`'s gate check (mutant: no rain weighting with the switch on; 1 of 2218 failed); left for `mutation-autofix` to pin
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
- custom_components/heatpump_optimizer/coordinator.py:8901 GUARD_OFF: value check, `entities.py`'s gate check (mutant: the envelope folds with the curve off; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/coordinator.py:8934 GUARD_OFF: value check, `entities.py`'s gate check (mutant: the plan is capped with the curve off; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/coordinator.py:8965 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:9017 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:9419 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:9809 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10144 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10531 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10604 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10604 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10776 GUARD_OFF: value check, `entities.py`'s gate check (mutant: the learned weight with learning off; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/coordinator.py:10791 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/coordinator.py:10824 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/disinfection.py:116 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/disinfection.py:121 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:37 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:43 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:56 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:76 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:81 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:98 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:256 GUARD_OFF: value check, `entities.py`'s gate check (mutant: a parsed config is re-parsed; 1 of 2218 failed); left for `mutation-autofix` to pin
- custom_components/heatpump_optimizer/entry_config.py:261 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:263 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:267 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:267 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:272 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:272 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:282 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/entry_config.py:296 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/legionella.py:194 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:572 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/sensor.py:704 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/silent_mode.py:104 GUARD_OFF: value check, `entities.py`'s gate check (mutant: an unreadable fraction raises; 1 of 2218 failed); left for `mutation-autofix` to pin

## Forward-carry

none. The modules that still read a mapping are named, with the reason for each, in `tests/entities.py`'s `_EC_RESIDUAL` and `_EC_NOT_ENTRY`.

## Friction

none.
