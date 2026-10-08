Two defects from a live v6.7.17 install, fixed under tvofi's mandate 6067089637 and aligned with the live-fix wave's binding design note (seat 4, "diag"). All evidence is synthetic; the user's diagnostics file was never read.

1. **Diagnostics exported setup data only.** `config` was `dict(entry.data)`, while the coordinator runs on `{**entry.data, **entry.options}`. A dump showed setup-time limits where the running ones had been changed through options. `diagnostics.config_view(data, options)` now returns `config` (the live merge, the same mapping the coordinator parses), `config_setup` (the raw setup data), and `config_overridden_by_options` (the keys whose live value is not the setup one). Both config sections go through the existing `_coarsen` and `async_redact_data` passes, because those run over the whole payload.
2. **A silent floor-return sensor was not reported.** When `floor_return.ok` is false, `_update_current_state` advances the slab open-loop from the plan's trajectory without telling anyone. The pure finding is `notifier.floor_return_silence(problems, since, now)`. It reads the published `input_problems` and returns the start of the silence plus the repair's placeholders, but only once a configured floor-return input has given no usable value for `FLOOR_RETURN_SILENT_MINUTES` (60). Any usable reading restarts the clock. `notifier.FloorReturnWatch` holds that clock. It runs on the notifier's existing coordinator listener and writes the `floor_return_silent` repair through the shared writer `setpoint_check.set_issue`, renamed public from `_set_issue` (design note S6; seat 2 reuses it). That gives a WARNING with `translation_key == issue_id`, not fixable, cleared when readings return. Translations are added in `strings.json`, `en.json` and `sv.json`.

No `coordinator.py` line, and no function taking `coord` (design note Rule A): the finding takes values, and the watch reads the published payload. There is no double report with `_audit_lower_floor_sensor`, which is about the unconfigured *lower-floor room* sensor, a different slot (`CONF_LOWER_FLOOR_TEMP_ENTITY`).

**Alternatives considered.** (a) Raise the repair inside `_update_current_state` beside the read, the `pump_mode_unreadable` shape. This lost because it needs coordinator attributes and lines at zero headroom (`max_class_loc`, `coordinator_attrs`, `max_cc` is that method's 45), and the design note puts seat 4 at 0 in-class lines. (b) A generic per-input watch over every reader slot. This lost on scope: a different sustained period per input is a product decision the brief did not make. The finding is keyed on the slot constant, so widening it later is one parameter. (c) Exporting the merged config without the setup data. This lost because the brief asks to keep the raw setup data, and support needs both to see which one a value came from.

**Instrument added (fixer step 18).** `tools/audit/seat/features_block.py` runs one block of `tests/features.py`. The full script runs for tens of minutes on a loaded seat, so the mutation proofs below use it. It has an offline `--self-test` and is listed in `INSTRUMENTS.md`.

## Head

`86c6daf4817c49111248a390b3bb8e71f27eff45`. It merges origin/main twice into the authored commits, most recently `bd59a4af1`. The one conflict was in `setpoint_check._quiet`: main's `EntryConfig` read is kept, and the call uses the renamed `set_issue`.

## Mutation proof

Each mutant was applied to a detached copy of the head `86c6daf48` and then restored.

`floor_return_silence` and its watch, run with `python3 tools/audit/seat/features_block.py "# Live v6.7.17 install: a configured floor-return sensor"` (12 checks):
- M1, the threshold predicate always true (`if now - since < timedelta(...)` -> `if True:`): 5 of 12 fail, including `a configured floor-return sensor silent for the sustained period raises one repair, not before, and it clears when readings return` and `the entry's notifier setup raises and clears the repair on coordinator updates`.
- M1b, the same predicate always false (`-> if False:`): 6 of 12 fail, including `a short gap does not accumulate: a reading in between restarts the period`.
- M2, the clock restarting every cycle (`since = since or now` -> `since = now`): 5 of 12 fail.
- M3, the listener not running the watch (the `floor_return.handle(coordinator.data)` line deleted): 1 of 12 fails, `the entry's notifier setup raises and clears the repair on coordinator updates`.
- M4, a usable reading not resetting the clock (`return None, None` -> `return since, None`): 1 of 12 fails, `a short gap does not accumulate: a reading in between restarts the period`.
- M5, the repair never cleared (`found is not None` -> `True`): 6 of 12 fail, including `a live sensor and an unconfigured slot never raise it, at any age`.
- M7, `FLOOR_RETURN_SILENT_MINUTES = 60.0` -> `600.0`: 1 of 12 fails, `the silence period outlasts a restart's or a brief outage's gap and is shorter than three hours of unannounced open-loop slab estimate`.
- M8, the `problems is None` guard disabled (`if False:`): the block stops with `TypeError: 'NoneType' object is not iterable`.

`config_view`, run with `tests/entities.py` at `de94392d6`, before the merges of main. The one later change to `diagnostics.py` is main's `cop_scale` key spelling in `_coordinator_snapshot`, outside `config_view`:
- M6, `"config": {**data, **options}` -> `"config": dict(data)`: 2 checks fail, `the diagnostics config is the live config, with options laid over setup data` and `the live config's coordinate, from options, is coarsened too`.

## Null control

- The unmutated block passes 12 of 12 at the head (`ALL 12 FEATURES BLOCK PASSED`).
- The new checks were committed before the fix (`30eef4d8c`, `d33dccde0`). Running `tests/entities.py` with those tests and the production package at the merge base `af79f2114`, 6 diagnostics checks fail: `the coordinate survives as a coarse cell rather than as a hole`, `the live config's coordinate, from options, is coarsened too`, `a non-coordinate member of the location dict is left alone`, `the diagnostics config is the live config, with options laid over setup data`, `the setup data is kept beside it, with the keys options override named`, and `the setup data is redacted like the live config`. The block raises `AttributeError: module 'heatpump_optimizer.notifier' has no attribute 'FLOOR_RETURN_SILENT_MINUTES'`: at the base there is no implementation for it to pass against.
- The block contains its own controls on the same clock. A live sensor and an unconfigured slot never raise the repair at ten times the period. A gap shorter than the period restarts it. A payload without `input_problems` leaves the watch alone.

## Figures

- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head. Every metric is unchanged from the merged-in main, and no budget file was touched.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `dS +0.0000 NULL`. An earlier cut read `coord_footprint 2587->2588`, because the listener in `async_setup_notifier` (a function handed the coordinator) passed `dt_util.utcnow()`. The watch now reads the clock itself, so the listener line is plumbing.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 22 script(s) run, 11 scoped out.`
- On the coordinator's instruction, heavy scripts run in CI and are not run locally. Locally I ran only the new and changed checks plus `tests/structure.py`: the features block above at the head, and `tests/entities.py` at `914436caf` (`ALL 2231 ENTITY CHECKS PASSED`). Between `914436caf` and the head, `tests/entities.py` is unchanged, and `diagnostics.py` changes only in main's `cop_scale` key spelling. CI's fast lane at the head is the authority for the rest of `scope.run`. The renamed writer has no stale reference: `git grep -n "_set_issue\b" -- custom_components tests/*.py` prints nothing.
- `python3 tools/audit/seat/features_block.py --self-test`: 1 check, 0 failed.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Seam census (step 8): `git grep -nE "reader\.read(_state|_bool)?\(\s*(CONF_[A-Z_]+)" -- custom_components/heatpump_optimizer` lists 21 reader slots. This PR dispositions one, `CONF_FLOOR_RETURN_TEMP_ENTITY`, the slot whose failure the brief names as silent. The other 20 are outside this fix's scope. Every one of them already reaches the owner through the published `input_problems` attribute and the `input_stale` event, and none is claimed closed here.
- Config-merge census: `git grep -n "{\*\*entry.data, \*\*entry.options}" -- custom_components/heatpump_optimizer` lists the live-config readers (`__init__.py`, `config_flow.py`, `coordinator.py`, `services.py`). `diagnostics.py` was the one reader of `entry.data` alone that presents it as the configuration, and it now uses the same merge.

## Unpinned sites

Each site below is killed by a value check in the features block. The mutation-autofix pins are left to CI.
- `custom_components/heatpump_optimizer/notifier.py:182 CONST`: value check, killed by M7 (`the silence period outlasts a restart's or a brief outage's gap ...`).
- `custom_components/heatpump_optimizer/notifier.py:198 GUARD_OFF`: value check, killed by M4 (`a short gap does not accumulate ...`).
- `custom_components/heatpump_optimizer/notifier.py:201 CMP_BOUND`: value check, killed by M1 and M1b (`... raises one repair, not before ...`).
- `custom_components/heatpump_optimizer/notifier.py:201 GUARD_OFF`: value check, killed by M1 (`the finding is pure: it starts the clock, waits the period, then names the entity`).
- `custom_components/heatpump_optimizer/notifier.py:219 GUARD_OFF`: value check, killed by M8 (the block stops on `TypeError`).

## Red checks

none

## Forward-carry

none new: both constraints this PR places on later seats are already in the wave's binding brief, `live-arch/DESIGN.md`. Section 1 S6 records that seat 2 reuses the public `set_issue` this PR creates. Section 6, "5 vs floor return", records that seat 5's observer runs on the same `floor_return.ok` false path that this repair reports.

## Friction

none
