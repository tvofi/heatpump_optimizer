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

- `_async_learn_house_heat_loss` ranks it before the ventilation pass-through, so the detector is
  never fed a constant.
- `_run_system_identification` stands its experiment down on it, because it seeds the same
  coefficient.

The reason is published through the existing path: `_learner_freeze_reason`, then
`_input_health_view()`, then `learner_freeze_reason` and `learners_frozen`.

Shape choice, from the commit message's out-of-tree replay (closed-loop two-zone plant, 42 days,
five plants, which this seat did not re-run): today's learner reaches -26% to -41% UA bias. A
freeze publishes the configured prior. Driving the replay from the lower-floor sensor is wrong by
+44% and -53% at the two ends of the observed zone split. The floor-return proxy reaches -57% to
-72%. With an indoor entity the learner tracks within 1%, so the missing input is the defect, not
the learner.

`max_class_loc` is paid back by tightening two comments in the same seam. No budget file is
touched.

Refs #2508. The roster group R10-LEARNER-DEFAULT lists #2508 under `issues` with `fixes` empty,
so by pr-contract's derived list this pull request is not the issue's closer. Making it the
closer is a roster edit, not a body edit.

## Head

`8553201c54a60d3a656fead7d142524f1cb2f64a` (`handoff/r10-learner-default`). One commit over
merge base `6eb552157b63d1e98a9653250789d9fe0027b5bc`. Every diff here is three-dot against that
merge base: `coordinator.py` +10/-9, `thermal_model.py` +34, `tests/features.py` +53.

**This head does not merge into current main.** At main `939f0c642` (2026-10-28),
`git merge-tree --write-tree origin/main 8553201c5` exits 1 with a content conflict in
`custom_components/heatpump_optimizer/coordinator.py`. Main has replaced the
`frozen = replay_freeze(self._learning_frozen(...), ...)` line in `_async_learn_house_heat_loss`
with `heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw,
self._learning_frozen(...))`. The resolution is semantic: `learner_room_unread` has to rank ahead
of the reason that `_replay_gate` now computes. A textual side-pick cannot do that. The handoff
froze this branch, so the merge is the orchestrator's to run, or to hand back to the fixer
(`orchestrator.md` section 7). This seat did not move the head. Steps 2 to 8 below were measured at
`8553201c5` and must be re-run at the merged head.

## Mutation proof

`learner_room_unread`'s return is replaced by `return None`, so the predicate never freezes. The
mutation is applied in a scratch worktree at `8553201c5`, and `tests/features.py` is run there:
`1 of 4475 FEATURE CHECKS FAILED`. The one red check is "#2508: no indoor temperature entity
freezes the house heat-loss learner with a visible reason instead of fitting the 21.0 C default",
with `samples 1 scale 1.0061538461538462 reason None`. The learner admitted the constant and moved
the coefficient. The two #2508 null-control checks stay green, so the red check is not reached by
a path the fix does not own.

## Null control

The unmodified tree is merge base `6eb552157` with only `tests/features.py` taken from this head.
It prints `1 of 4475 FEATURE CHECKS FAILED`: the same #2508 check, with `samples 1 scale
1.006153846153846 reason None`. This is the defect as shipped. Both null controls pass at the base
too: "a configured indoor entity still learns, and its unconfigured power slot does not freeze it"
and "the lower-floor learner still learns with no indoor entity". So the new guard changes only
the no-indoor case.

## Figures

- `ALL 4475 FEATURE CHECKS PASSED` at `8553201c5`:
  `PYTHONPATH=tests/hastub python3 tests/features.py`
- `1 of 4475 FEATURE CHECKS FAILED` with the predicate mutated, and the same at the merge base
  with this head's checks: the same command, in the scratch worktrees described above.

## Red checks

none. `tools/pr/ci_predict.py --base origin/main` passes this head (run inside `body_push.sh`).
The merge conflict described under `## Head` is not one of its arms. GitHub will report the PR
as `DIRTY` until the orchestrator merges main into the head.

## Forward-carry

none

## Friction

none
