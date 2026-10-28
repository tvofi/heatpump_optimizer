fix(learner): freeze house heat-loss learning with no indoor thermometer (#2508)

The house heat-loss learner replays the elapsed interval from
`ThermalState.room_temperature` and compares the result with the same field. With no indoor
temperature entity configured, `_update_current_state` never writes that field, so both sides are
the constructor's 21.0 C default. `_learning_frozen` passes an unconfigured slot on purpose, so the
sample goes through, and the coefficient it persists is fitted to neither temperature.

`thermal_model.learner_room_unread(config)` returns the new freeze reason
`INDOOR_UNCONFIGURED_FREEZE` (`not_configured:indoor_temp_entity`) when the indoor entity is not
configured. It returns `None` when there is no config to inspect. It is a separate predicate, not
a wider `_learning_frozen`. The unconfigured slots that `_learning_frozen` protects (power,
outdoor, thermal power) still pass. The lower-floor learner reads its own zone's sensor, so it
still learns with no indoor entity. Two call sites in `coordinator.py` consult the predicate:

- `_async_learn_house_heat_loss` passes it to `_replay_gate` as the raw freeze, ahead of
  `_learning_frozen`'s reason, so it ranks before the ventilation pass-through and the detector is
  never fed a constant.
- `_run_system_identification` stands its experiment down on it, because it seeds the same
  coefficient.

The reason is published through the existing path: `_learner_freeze_reason`, then
`_input_health_view()`, then `learner_freeze_reason` and `learners_frozen`.

Shape choice, from the fix commit's out-of-tree replay (closed-loop two-zone plant, 42 days,
five plants, which this seat did not re-run): today's learner reaches -26% to -41% UA bias. A
freeze publishes the configured prior. Driving the replay from the lower-floor sensor is wrong by
+44% and -53% at the two ends of the observed zone split. The floor-return proxy reaches -57% to
-72%. With an indoor entity the learner tracks within 1%, so the missing input is the defect, not
the learner.

Refs #2508. The roster group R10-LEARNER-DEFAULT lists #2508 under `issues` with `fixes` empty
(re-read at main `6d86acc90`), so by pr-contract's derived list this pull request is not the
issue's closer. Making it the closer is a roster edit, not a body edit.

## Head

`f37c0dcae3b3b5303f7606a90215e0246d46fa01` (`handoff/r10-learner-default`), over the fix commit
`8553201c54a60d3a656fead7d142524f1cb2f64a`, not a re-cut: merge `091211e11` of origin/main
`edd7e0e14`; `71a763148`, two #2508 checks; `372c510a5`, the call site re-cut to the class budget;
merge `f37c0dcae` of origin/main `6d86acc90` (tooling only since `edd7e0e14`: no path under
`custom_components/`, `tests/features.py` or a budget file). Three-dot against merge base
`6d86acc90`: `coordinator.py` +12/-11, `thermal_model.py` +34, `tests/features.py` +77.

The first merge's one conflict was in `_async_learn_house_heat_loss`, where main replaced
`frozen = replay_freeze(self._learning_frozen(...), ...)` with
`heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw, self._learning_frozen(...))`.
Resolution: `raw = learner_room_unread(ctx._config) or self._learning_frozen(...)`, passed to
`_replay_gate` as its `raw`. `replay_freeze` returns any reason but `UNMETERED_POWER_FREEZE`
unchanged, so the room reason comes out of the gate as `frozen`, ranked first, and
`heat_energy.replay_gate` returns `clean=False` for the cycle, so no heat-counter span closes over
a constant room. The alternative, `frozen = learner_room_unread(...) or frozen` after the gate,
sets the same reason but leaves `clean=True`; the new span check below separates the two.

## Mutation proof

`tests/features.py` with `PYTHONPATH=tests/hastub`, each in a `git archive` tree of `372c510a5`
(the code `f37c0dcae` carries). An archive tree is not a git checkout, so "and the path that
proceeds still stamps a resolvable recorded_at (#363)" fails in every one of them, the unmutated
head included (`recorded_at = 'unknown'`); it is excluded from the counts below.

- Unmutated head: `1 of 4539 FEATURE CHECKS FAILED`, the #363 check only.
- `learner_room_unread` returns `None` (predicate never freezes): `4 of 4539`. Red: "#2508: no
  indoor temperature entity freezes the house heat-loss learner ..." (`samples 1 scale
  1.0061538461538462 reason None`), "#2508: a cycle with no indoor entity leaves no heat-counter
  span clean; a configured one does" (`{'no_indoor': True, 'indoor': True}`), "#2508: a caller that
  cannot see the entry (config None) invents no freeze; ...".
- The merge resolution removed (`raw = self._learning_frozen(...)`): `3 of 4539`, the first two
  #2508 checks above.
- The rejected post-gate ordering (raw back to `_learning_frozen`, `frozen =
  learner_room_unread(ctx._config) or frozen` after the gate): `2 of 4539`, the span check alone.
- The `config is None` guard deleted: `5 of 4539`. Red: the config-None #2508 check, plus three
  sysid checks the stand-down reaches ("the control: with no mode entity the experiment is
  untouched", "#943 wiring: _run_system_identification passes the configured slab pair", "#943:
  the honest sizer leaves a power-limited heavy house ...").

## Null control

Main `edd7e0e14` (production code identical to `6d86acc90`) with this head's `tests/features.py`:
"#2508: no indoor temperature entity freezes ..." red (`samples 1 scale 1.0061538461538462 reason
None`) and the span check red (`{'no_indoor': True, 'indoor': True}`): the defect on main. Both
null controls pass there: "#2508 null control: a configured indoor entity still learns, and its
unconfigured power slot does not freeze it" and "#2508 guard: the lower-floor learner still
learns with no indoor entity". The run then stops at the config-None check's import, since main
has no `learner_room_unread` (`ImportError`, rc 1).

## Figures

- `ALL 4537 FEATURE CHECKS PASSED` at merge `091211e11`, in its worktree:
  `PYTHONPATH=tests/hastub python3 tests/features.py`. The two checks `71a763148` adds were
  measured only in the archive trees above.
- `1 of 4539` / `4 of 4539` / `3 of 4539` / `2 of 4539` / `5 of 4539 FEATURE CHECKS FAILED`: the
  same command in the trees under `## Mutation proof`.
- `tests/structure.py` at `091211e11`: `FAIL class_excess_loc 18041 > 18038 (+3)` and
  `FAIL max_class_loc 8164 > 8161 (+3)`. At `372c510a5`: `STRUCTURE RATCHET PASSED`, exit 0, no
  budget row moved: `python3 tests/structure.py`.

## Red checks

none. `tools/pr/ci_predict.py --base origin/main` runs inside `body_push.sh`, and
`git merge-tree --write-tree origin/main f37c0dcae` is clean at main `6d86acc90`.
- `mutation` at f37c0dcae3b3: red by construction on the 1 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Unpinned sites

none: the `config is None` guard the predictor named at s8's head is now pinned (mutant above).

## Forward-carry

none

## Friction

none
