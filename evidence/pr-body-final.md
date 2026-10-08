Closes #1745.

The entry's merged data and options are parsed once, at coordinator construction, into a frozen `EntryConfig`: one default and one coercion per declared key. Readers in the migrated modules take the parsed field, and `tests/entities.py` names the modules that still take the mapping, with the reason for each. Quiet-window service calls apply live by swapping in a new parse, as on main. Round 7: this body is re-taken whole.

## Head

`7a5ca1e400da56da7cac5e64a7a675f9bbbd1115` merges the authored code head `387128bb3de485f48df71bdefff616e1228c51db` and then merges origin/main `0b89f781f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`17bb438f6ecbda20b59582b34b3fb780f81e2187` merges the authored code head `387128bb3de485f48df71bdefff616e1228c51db` and then merges origin/main `0b89f781f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`b2c7cb65a8045b23298248a8da27c15a75c455ce` merges the authored code head `2a7b4d0c4ab1013ec42251b9d5a6050f9bd0332f` and then merges origin/main `4647321d8` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `387128bb3de485f48df71bdefff616e1228c51db` (pushed to `handoff/r9-eg-entry-config`). It is two commits over the round-7 PR head `9c66410942bceb57ccb753b87d74721854d57ce7`, answering the round-7 review's one block (fixer.md step 18).
- 387128bb adds the new file to `tests/harness_headers.py`'s `inert_reads` in `tests/closures.json`, by hand and in sorted order. `harness_headers.py` reads every file under `dev/audit/harnesses/`, and prepr's CI predict refused the push on the `INERT READS UNDER-APPROXIMATED` it predicted. `derive_closures.sh --single tests/harness_headers.py` on this Darwin machine could not add it, because the inert dimension is recorded by Linux strace only. That run changed only `seconds`, and I reverted it. `tools/pr/ci_predict.py` now predicts no closures red.
- 2a7b4d0c adds the 6840 equivalence probe as `dev/audit/harnesses/eg_b11_equiv_6840.py` and points the `survivor_triage` row's `reason` at that path in place of a path on one machine; no production or test code changes. `dev/audit/` is on `tests/closure.py`'s INERT list, so the new file needs no closure.

9c664109 merged `c5e00ae35dcb5f63c31ca66ceb4b66c8e773f278` and origin/main `dcc77dd0` (update script's automatic merge). c5e00ae3 is one ledger-only commit over the bot's `de81043a` (`ci: re-record closures`, `tests/closures.json` only), which sits on `0864a8d2`, the round-7 push of `bf372564`. c5e00ae3 adds the four `killed_by` rows CI's pin run measured at de81043a (see Mutation proof); it touches no production or test code.

`bf372564c17fc947ceae8e5029d66973ad22dbe3` sits over the round-6 head `95b083063f3ebce013d38726bd329c729438bc7c`, which is the bot's `ci: pin killed mutants` commit (ledger only, 58 pins) over `883eed10`. It adds two commits:
- 25612bf3 adds one ledger row, a `survivor_triage` mark for the live survivor `coordinator.py:6840 CMP_BOUND`. It touches no production or test code (see Mutation proof).
- bf372564 merges origin/main `816547ef`. `git merge-tree --write-tree` over its two parents reproduces its tree exactly, and `git show --remerge-diff` prints 0 lines. The ledger driver resolved `tests/closures.json` (`LEDGER-MERGE: resolved tests/closures.json`).

Earlier heads, each reviewed in its own round:
- 883eed10 merges main 0c25836e. 37ac4d84 merges b21ed75e.
- b29e4ee4 merges main 6b91e238. It resolves the `pump_arbiter.py` conflict with #2007 (SW-2 actuation) by hand, keeping both sides: SW-2's fourth slot, the silent switch, and its silent and off specs now read the parsed `heat_pump_capacity_limited_entity`, `quiet_silent_windows` and `quiet_off_windows`. Where nothing is stored those read `""`, which `_silent_rows` and `step_actions` treat as no rows, the same as `None`. SW-2's `features.py` stand-ins wrote items into the frozen configuration; they now rebuild it through `with_config`. The round-6 reviewer judged this resolution equivalent.
- b21ed75e drops two killed_by pins main had just recorded, `_dhw_probe_temperature` GUARD_OFF and `_silent_target` RETURN_DEL. Their anchors name the mapping-read text this branch rewrites, so the ledger refused them.
- cd7948e3 adds one `entities.py` check that drives each parsed gate on both arms. It covers the lower-floor learner's sensor guard, open-window relax's `and`, the rain weighting's switch, the comfort-learning switch, `from_mapping`'s pass-through, and an unreadable silent fraction. It removes `_optional_number`'s `if value == "": return None`: an empty string is refused by the float parse and falls to the default, which is None for every optional field, so that branch changed nothing (an equivalent mutant).
- c27b616d adds the capacity curve's two guards (`_fold_capacity_envelope`, `_capacity_caps`) to that check. The silent-mode arm now catches a raise, so a mutant that crashes it fails the check instead of the script.

## Mutation proof

**The round-6 live survivor, `coordinator.py:6840 CMP_BOUND`, is equivalent, not killable.** The mutant is `np.any(snow_array > 0.0)` -> `np.any(snow_array >= 0.0)`. The two guards differ only when every step's snow is 0. Then the guarded body multiplies the rain by `_liquid_fraction(precip, 0)`. For p > 1e-9 that is `clip(p / p, 0, 1)`, and IEEE gives exactly 1.0 for x/x. For p <= 1e-9 it is the literal 1.0. So the array is unchanged, bit for bit.

The only input that tells the two apart is a non-finite rain, because inf/inf is nan. `_liquid_fraction([0, 1e-9, 2e-9, 0.3, 1e300, 1.7e308, inf], 0)` times that rain prints `[0 1e-9 2e-9 0.3 1e300 1.7e308 nan]`. Non-finite rain cannot reach the line:
- `_weather_series` builds each step as `max(0.0, _as_float(...))`, and `_as_float` maps a non-finite value to its default.
- With no forecast, the rain is zeros. Padding repeats a value already in the series.
- Snow is `max(0.0, float(snow))` per step, or 0.0. It is never negative, and a NaN answer clamps to 0.0.

A test that kills this mutant would have to feed an input that production never builds. So the site is marked `equivalent` under `survivor_triage`, with that argument and the measurement below in its `reason`. The mark is pinned to the line's text.

The measurement is a differential probe, now in the tree: `dev/audit/harnesses/eg_b11_equiv_6840.py`, run as `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/eg_b11_equiv_6840.py <out-dir>`. It was first run at 95b08306 from a seat copy (sha1 `3e661d15`). The tree copy differs only in its header and in finding the repository root from its own path. It was re-run at 9c664109, from the repository root and from another directory, with the same three lines as below. It builds three `git archive` trees:
- the head;
- the operator's mutant;
- a boundary-only control, which also halves the rain when every step's snow is 0.

In each tree it drives the real `_forecast_arrays` and the real `_weather_series` over 552 cases. The inputs are 23 rain values, including None, `"garbage"`, nan, ±inf, -3, -0.0, 0, 1e-12, 1e-9, 1.0000001e-9, 1e300 and 1.7e308. They also span 6 Open-Meteo snow answers (None, 0, -0.0, -2, nan, and Open-Meteo absent), timed and untimed rows, and the flag on and off. Every precipitation float is compared by `repr`. Output, the same at 95b08306 and 9c664109:
- `RESULT mutant: cases=552 differing=0 (flag on 0, flag off 0)`
- `RESULT control: cases=552 differing=264 (flag on 264, flag off 0)`
- `boundary cases (flag on, every step's snow 0)=276, of them with rain on some step=264`

So the probe reaches the boundary, and a change confined to that boundary moves every wet case there. The 12 dry boundary cases cannot move under any multiplier.

**The four `skip-budget` sites are killed, measured by CI.** `mutation-pins (1)` at de81043a (job 113265218115) printed `PIN KILLED: 4 pinned, 0 left unpinned`:
- `entry_config.py:272 CMP_BOUND` -- killed by `tests/entities.py`
- `entry_config.py:282 RETURN_DEL` -- killed by `tests/entities.py`
- `legionella.py:194 GUARD_OFF` -- killed by `tests/features.py`
- `pump_arbiter.py:572 RETURN_DEL` -- killed by `tests/structure.py`

The same shard at 0864a8d2 (job 113253711197) killed the same four, with `tests/features.py` first for `:272`. Its null control, `entry_config.py:111 NULL_COMMENT`, survived every driver. `mutation-autofix` (job 113280999308) then printed `shards merged: skip-no-measurement` and pushed nothing, although the shard's artifact (11547045879) carried status `measured` and head de81043a; why the merge saw no shard was not established. Its own message says to pin by hand when that happens, so c5e00ae3 is that artifact applied with `mutation_table.apply_pins` at the head it measured. Nothing was re-measured locally.

**The round-6 reviewer's kills stand at 883eed10.** Each mutant was applied in place, and the baseline was `ALL 2225 ENTITY CHECKS PASSED`. Every mutant failed exactly 1 of 2225 checks: the gate check, on the arm named below.

| site at this head | mutant | the arm that moved |
|---|---|---|
| coordinator.py:5051 | GUARD_OFF | lower floor learns without a sensor: (1, 1) |
| coordinator.py:5462 | BOOLOP | relax without the detector: ((1.0,), (1.0,)) |
| coordinator.py:6840 | GUARD_OFF | no rain weighting with the switch on: (2.0, 2.0) |
| coordinator.py:6840 | BOOLOP | weighting with the switch off: (0.5714, 0.5714) |
| coordinator.py:8901 | GUARD_OFF | fold: ((False, 1), (True, 1)) |
| coordinator.py:8934 | GUARD_OFF | caps: ((True, 0), (True, 1)) |
| coordinator.py:10776 | GUARD_OFF | the learned weight with learning off: (9.0, 9.0) |
| entry_config.py:256 | GUARD_OFF | a parsed config re-parsed: (False, True) |
| silent_mode.py:104 | GUARD_OFF | an unreadable fraction raises: ('TypeError', True) |

The fixer's own run of the same nine, at c27b616d against a baseline of 2218, read the same arms. The round-4 kills stand: `__reduce__`, `fuse_kw_at` and `fuse_kw`.

## Null control

- Every arm the gate check compares has its on side as the null control. On that side the gate opens and the value moves: it learns 1 sample, relaxes by `OPEN_WINDOW_RELAX_C`, weights rain to 0.5714 mm, plans with the learned 9.0, caps and folds, and composes a silent cap. Each mutant above moved only its off side to equal the on side.
- For the equivalence mark, the control is the probe's boundary-only variant: 264 differing cases where the mutant has 0.
- For CI's pin run, the null control is `entry_config.py:111 NULL_COMMENT`, which survived every driver in both shards (jobs 113253711197 and 113265218115).

## Figures

Each figure below names the head it was measured at. Interpreter: venv-ci python3 3.14.7. Scripts were run one at a time with `PYTHONPATH=tests/hastub`. origin/main was `816547ef` at the merge (2026-10-08).

At 2a7b4d0c, with the same interpreter (at 387128bb, `tests/entities.py` `ALL 2227 ENTITY CHECKS PASSED` and `tests/closure.py selftest` `ALL 39` were re-run after the closures edit):
- `tests/entities.py`: `ALL 2227 ENTITY CHECKS PASSED`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`. This includes the check that every inlined `repo_root` matches `tools/audit/repo_root.py`.
- `tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`.
- `tests/closure.py selftest`: `ALL 39 closure shrink pins PASSED`.
- `tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries at HEAD`.
- `tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 29 script(s) run, 4 scoped out`.
- `tests/mutation_table.py --normalize`: `1223 disposition(s), 0 retired key(s)`; the edited triage row comes out byte-identical.
- `dev/audit/harnesses/eg_b11_equiv_6840.py`: `RESULT mutant: cases=552 differing=0`, `RESULT control: cases=552 differing=264`, boundary 276 with 264 wet.

At c5e00ae3:
- `tests/mutation_table.py --normalize`: `1223 disposition(s), 0 retired key(s) naming no site`, and the four new rows come out byte-identical (`git status` empty after it).

In CI at de81043a, whose tree differs from c5e00ae3 only by the four ledger rows: `fast (3.14)` success (jobs 113264492246, 113264490653), `typing` success, `coverage` and `coverage-ratchet` success, `closures` success, `pr-contract` success. At 0864a8d2: `fast (3.14)` success (job 113253372803), which is the `tests/entities.py` result the local run below could not give.

At bf372564:
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `tests/layout.py`: `layout self-test: ok`.
- `tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`.
- `tests/closure.py selftest`: `ALL 39 closure shrink pins PASSED`.
- `tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 29 script(s) run, 4 scoped out`.
- `tests/mutation_table.py --normalize`: `1203 disposition(s), 0 retired key(s)`, and the new row comes out byte-identical.
- `tests/entities.py` did **not** complete locally at this head. It stopped on `OSError: [Errno 28] No space left on device` while writing an HA storage file, with 142 MiB free on the machine. Its result is CI's `fast (3.14)` at 0864a8d2 and de81043a, both green. The only change since 883eed10 is the ledger row plus main's merge.

At earlier heads:
- At 883eed10, the round-6 reviewer measured `tests/entities.py` `ALL 2225 ENTITY CHECKS PASSED` and `tests/structure.py` `STRUCTURE RATCHET PASSED`.
- At b21ed75e: `tests/entities.py` `ALL 2218 ENTITY CHECKS PASSED`.
- At b29e4ee4: `tests/typing_ruler.py` under `HPO_TYPING_PYTHON`, mypy included, `ALL 12`; `tests/manual_plan.py` `ALL 129`.
- At cd7948e3: `tests/config_flow_steps.py` `ALL 496`.

Heavy scripts (features, golden, stress, the mutation drives) are CI's under the owner's 2026-10-07 rule.

## Red checks

- `mutation` at 95b08306 (job 113224598923): `MUTATION TABLE REFUSED -- 4657 unpinned site(s) against 4670 at the ratchet base 0c25836e, 5 of them added by this diff`. This PR's.
  - `coordinator.py:6840 CMP_BOUND` survived; it is now triaged equivalent (Mutation proof).
  - The other four were `skip-budget`; CI measured them at de81043a and they are pinned in c5e00ae3.
  - The cheaper detector for the survivor is the local probe above. A budget-skipped site has none, because only the drive measures it.
- `mutation` at 883eed10 (job 113187473136): REFUSED with 63 added unpinned sites. This PR's. The bot's 95b08306 pinned 58 of them; the five left are answered just above.
- `fast (3.14)` at bfaf5486 (job 113048537751): this PR's. `tests/boost_drift_replay.py` raised `TypeError: cannot pickle 'mappingproxy' object` while deep-copying an `EntryConfig`. Fixed in bd4ac1df and pinned by `entities.py`'s round-trip check, which is the cheaper detector.
- `mutation` and `mutation-autofix` at bfaf5486 (job 113050887311 for the autofix): the lane measured nothing (`56 not started for --budget-minutes`), so the autofix pinned nothing. Superseded by the runs above.
- Reds on earlier heads, each answered in its round:
  - `typing` (job 112880876862, a390f589): mypy went from 0 to 9, and has been 0 since round 2.
  - `closures` and `closures-autofix` (jobs 112881062368 and 112897209809 at a390f589; 112857717705 at 5947316c): `entry_config.py` was missing from closures; it was added in round 2.
  - `mutation-nightly` (job 112857793518, 5947316c): a stand-in raised in `manual_plan.py`; fixed in round 2.
  - `budget-raise-gate` (job 113048531990, bfaf5486): a cancelled twin. No budget leaf is raised.
- `mutation` at 0864a8d2 (job 113253372899) and de81043a: `MUTATION TABLE REFUSED -- 4656 unpinned site(s) against 4670 at the ratchet base 816547ef, 4 of them added by this diff`. This PR's: the four sites above, pinned in c5e00ae3 from CI's own measurement. The survivor no longer appears.
- `mutation-autofix` at de81043a (job 113280999308): `skip-no-measurement`, so the bot pushed nothing; answered by c5e00ae3 (Mutation proof). Whether the shard merge has a defect is not established here.
- `closures` at 0864a8d2 (job 113253492623): `INERT READS UNDER-APPROXIMATED` for `tests/harness_headers.py` reading `dev/audit/harnesses/git_auto_maintenance_race.sh`, a file this diff does not touch (main's). `closures-autofix` re-recorded it in de81043a; the cheaper detector is that bot.
- `nightly-ha (stable)` and `nightly-ha (2025.2.0)` at de81043a (jobs 113264431176, 113264430896): main's. They fail `a16:debug_inline`, `a16:debug_capped` and `run:exit_status`, the same three main's own nightly failed at 816547ef, this PR's merge base (jobs 113233890742, 113233890376). The cause is #2041's A16 writer call; the fix is #2056.
- `nightly-status` at 9817c40b, a390f589, 0dfb63a8, bfaf5486 and 0662bd8e (job 113069942459 is the latest): main's, not this diff. It reports main's last concluded nightly, scheduled run 37595831734 at main's be0cb82, whose `mutation-ledger`, `mutation-nightly` and `record-autofix` jobs failed. This diff touches none of the reporter's inputs: its only delivery path is its own new row `dev/programme/delivery/2025.md` (status `A` in the three-dot diff). No cheaper detector is owed here; the lane's owner is main's nightly, not this PR.
- `delivery-status` at 883eed10: main's window (`UNCHECKED -- 9 merge commits ...`), not this diff.

## Unpinned sites

Below are the 63 sites `tools/pr/ci_predict.py` listed as added at b21ed75e, each with its disposition at this head. None moved line with the main merge, which `sed -n` at each line confirms. Of the 63, 58 were pinned by the bot in 95b08306, 1 is triaged here, and 4 are pinned in c5e00ae3 from CI's pin run at de81043a.

- custom_components/heatpump_optimizer/__init__.py:179 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/binary_sensor.py:174 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:822 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:1764 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:1801 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:2327 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:3167 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:3275 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:4141 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:4187 BOOLOP: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:5051 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:5462 BOOLOP: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:5483 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:6470 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:6840 BOOLOP: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:6840 CMP_BOUND: triaged equivalent in this round, `tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._forecast_arrays.CMP_BOUND.54c3c7b5.json` (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:6840 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:6875 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:6934 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:7124 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8130 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8160 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8298 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8444 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8628 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8723 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8783 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8814 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8869 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:8901 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:8934 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:8965 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:9017 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:9419 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:9809 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:10144 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:10531 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:10604 BOOLOP: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:10604 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:10776 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/coordinator.py:10791 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/coordinator.py:10824 GUARD_OFF: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/disinfection.py:116 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/disinfection.py:121 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:37 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:43 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:56 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:76 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:81 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:98 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:256 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)
- custom_components/heatpump_optimizer/entry_config.py:261 BOOLOP: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:263 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:267 CLAMP_DROP: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:267 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:272 CMP_BOUND: killed by `tests/entities.py` in CI's pin run at de81043a (job 113265218115), pinned in c5e00ae3 (Mutation proof)
- custom_components/heatpump_optimizer/entry_config.py:272 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/entry_config.py:282 RETURN_DEL: killed by `tests/entities.py` in CI's pin run at de81043a (job 113265218115), pinned in c5e00ae3 (Mutation proof)
- custom_components/heatpump_optimizer/entry_config.py:296 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/legionella.py:194 GUARD_OFF: killed by `tests/features.py` in CI's pin run at de81043a (job 113265218115), pinned in c5e00ae3 (Mutation proof)
- custom_components/heatpump_optimizer/pump_arbiter.py:572 RETURN_DEL: killed by `tests/structure.py` in CI's pin run at de81043a (job 113265218115), pinned in c5e00ae3. The round-7 reviewer found the kill is `structure.py`'s `dead_top_level_symbols` count (deleting the return leaves `_inside_silent` unreferenced), not a behaviour test; main's earlier pin of the same line had `features.py`. Not this PR's defect: it belongs to the pin chain's choice of killer (Mutation proof)
- custom_components/heatpump_optimizer/sensor.py:704 RETURN_DEL: pinned by mutation-autofix in 95b08306
- custom_components/heatpump_optimizer/silent_mode.py:104 GUARD_OFF: pinned by mutation-autofix in 95b08306; also killed by `entities.py`'s gate check (Mutation proof)

## Forward-carry

none. The modules that still read a mapping are named, with the reason for each, in `tests/entities.py`'s `_EC_RESIDUAL` and `_EC_NOT_ENTRY`.

## Friction

none

