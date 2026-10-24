# D8 round 10 -- verifier report (one verifier, three lenses)

Worktree: detached at handoff/audit-r10-register 9355f107d (the branch was checked out elsewhere, so `--detach`). Python 3.14.7, macOS arm64.

## D8-s1-01 -- plan sensors say "heating now" on a step the plan declares off

**Vote: verify. Severity: low** (display/state disagreement on one informational sensor; no command, no cost effect). Class P2 confirmed.

### V1 reproduce
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D8/s1/f1_active_now.py`:
  heating_now_while_off=1 (coord_all_features@17, space draw 0.07 kW, action off), slot_steps_declared_off=4 of 192, snapshots=36. load1=10.33, thread_factor=1.000 (contended box; counts are deterministic, not timing).
- `--perturb`: heating_now_while_off 1 -> 0 (load1=9.42); secondary stays 4, as the header predicts. Moves in the stated direction.
- Null control: the perturbation is the null (gating active_now on heat_pump_on_schedule[0] gives 0). Leave-one-out: the single hit lives in coord_all_features; dropping min+min_modulation leaves 1, dropping coord_all_features leaves 0 -- the headline rests on one cell, one snapshot; the independent measure below shows it is not a grid artefact.

### V2 independent
`dev/audit/rounds/round10/D8/verify_indep_active_now.py`. Metric: over a 0.001 kW grid of space draws in [0, 0.3] (dhw 0), count draws where the active_now predicate `raw > 0.05` (coordinator.py:4161, :4178) is True while `thermal_model.planned_draws_run` (the plan's own running rule, MIN_RUNNING_DRAW_KW=0.1) is False. Result: **50 of 301**, the whole band 0.051..0.100 kW. The divergence is structural, not cell-specific.

### V3 reach and class
- Reachable in real HA: active_now is computed from the solve output in `_build_plan_views` and read by `SpaceHeatingPlanSensor`/`DHWHeatingPlanSensor.native_value` (sensor.py:1523); no stub-divergent symbol (executor, coroutine handling) is on the path.
- Class P2 ("one fact decided twice by divergent predicates") confirmed. Notably the P2 barrier's `plan_running_rule` entry in tests/entities.py did not catch it: its name regex `power|_kw\b|\bp\b|dhw` does not match `raw_space`, and its floor match keys on the running floor, not the 0.05 literal -- a detector hole worth the judge's note.
- seam_rule enumerates **only the demonstrated seams**: it narrows the 0.05 grep to `_plan_slots`, `active_now` and `DHWScheduleSensor`, while the same grep shows sibling literal running thresholds at coordinator.py:4873 (`current_action power > 0.05` -> heating), :10664, and :10962 (`heat_pump_on: override > 0.05`) that it neither includes nor disposes.
