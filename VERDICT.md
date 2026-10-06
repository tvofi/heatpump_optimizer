Fix review: blocked af7cf417c9e8ff7a23e0bd82bd4ca32fc5814cbf root-cause-unanswered: typing, mutation and env-matrix went red, unanswered

bus-nonce: 0b8420ac11d9efdcb187444c217d312b

Round 1. Measured `af7cf417c9e8ff7a23e0bd82bd4ca32fc5814cbf`. Live pull-request head at posting is the same SHA. The body ## Head names that SHA. Merge-base and `origin/main` are `6001b09a557259f37319b400d219cf83e02c563f`. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/` is empty.

## Red checks

Commit check-runs, every page, not one run per name. Range `6001b09a..af7cf417` is three commits. `0a589900` has no check runs. On `af7cf417` the completed failures are `typing`, `mutation`, `env-matrix`, `pr-contract` (twice), `delivery-status`, `nightly-status`. `fast (3.14)`, `closures` and `coverage` were still `null` when this was posted. ## Red checks names two `tests/features.py` sentences and does not name `typing`, `mutation` or `env-matrix`.

`typing` job 112527225870, run 37538912237: typing ruler, mypy 2.3.1, `errors did not grow [recorded 0, measured 1 (+1)]`, `by_code[attr-defined] did not grow [recorded 0, measured 1 (+1)]`, module `optimizer.py` 1. The diff's new attribute write is `result.duty_floor_kw = _duty_floor(self)` in `_build_result`. `OptimizationResult` does not declare `duty_floor_kw`.

`mutation` job 112527225658, same run: `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory`, six pins whose `old` text the inventory no longer generates: `coordinator.py` `_learning_frozen` GUARD_OFF `fe0eb2bc`, `pump_arbiter.py` CONST `8278aeb0`, `_flow_target` CLAMP_DROP `46cadb90`, `step_duty` BOOLOP `296c284b` and `399c5f97`, `thermal_model.py` `planned_draw_runs` RETURN_DEL `d42ada6d`. The follow-on pin step printed `measure: skip-not-unpinned, 0 anchor(s)`.

`env-matrix` job 112526801255, run 37538912213: `2 declared outcome(s) held, 14 did not`. `pr / policy_lint rc=0` failed at rc=1. Shallow and since-ref arms fail with `Cannot find module` `.../.claude/workflows/policy_lint.mjs`.

`pr-contract` jobs 112526801164 and 112527489404 print `skip red-history` (no token in that step, so that job's earlier heads are UNCHECKED there) and then ERROR that `env-matrix` is red and ## Red checks does not name it; the later job adds the same ERROR for `mutation`. This review's own check-run walk is the record above, not that skip.

`delivery-status` job 112526801540: `DELIVERY STATUS UNCHECKED — 42 rowed, 2 pending, 0 overdue`, pending #2003 `a28fd0a` and #2001 `1b1bbaa`. The job text says it is not a required context. `nightly-status` job 112527225983: `NIGHTLY FAILED: record-autofix failed last night`, and the job text says it is not a `main-protect` context. Neither grades this diff's row. `docs/delivery/2006.md` is this pull request's own open row.

## Mutation proof

The four production lines the body names, each restored before the next. Instrument: the predicates the named `tests/features.py` checks encode, importing the production functions. Worktree clean after (`git status` empty).

- `projected[gap] = lo` replaced with a no-op assignment. `project_planned_levels` on `[0, 0.3, 0.5, 3, 14, 20]` at `p_min` 3, `p_max` 14 returned `[0.0, 0.3, 0.5, 3.0, 14.0, 14.0]`. Red: "a switch-plus-setpoint install clamps a sub-minimum level up to p_min and keeps off off".
- `return floor + frac * (heat - floor)` replaced with `return heat`. Flow at `p_min` was 55.0. Red: "the heating flow is the ceiling at full power and the inlet at p_min, and a configured ceiling moves it".
- `return UNMETERED_POWER_FREEZE` replaced with `return None`. `learner_unmetered` on the switch-plus-setpoint config was `None`. Red: "the house learner freezes on an unmetered switch-plus-setpoint install and not on a metered one".
- The sub-minimum `return False` in `planned_draw_runs` replaced with `return total > MIN_RUNNING_DRAW_KW`. `planned_draw_runs(0.3, modulation_floor=3.0)` was `True`. Red: the floor arm of "null control: the duty-cycle reading of 0.3 kW still runs when no floor is passed".

At the unmodified head those predicates hold, and `HeatPumpOptimizerCoordinator._learning_frozen` is `unmetered_power` on switch `switch.hp` plus setpoint `number.flow`, and `None` on that config plus power and frequency, and `None` with `clamp_planned_levels: false`. `OptimizationConfig().clamp_planned_levels` is `False`. Those four lines are not a vacuous mutant. They do not delete the call sites in `_optimize_space_only`, `_optimize_with_dhw` or `_flow_target`.

## What the head does

`probe_install` is the only capability probe. Reviewer's enumeration, not a rule the body names (`## Figures` is `none`; #1955 states (a), (b), (c) and (d)):

- empty, switch only, setpoint only, frequency only, power plus frequency: `levels_clamped` false, freeze `None`.
- switch plus setpoint: clamp true, freeze `unmetered_power`.
- switch plus setpoint plus power, no frequency: clamp true, freeze `None`.
- switch plus setpoint plus a frequency entity or sensor: clamp false, freeze `None`.
- `clamp_planned_levels: false` on switch plus setpoint: clamp false, freeze `None`. `can_duty_cycle` stays false.

`step_duty` on the R9-F2.4 plan (0.15 kW space plus 2.0 kW hot water, then 1.5 kW space) is `both` then `space` with no `duty_floor_kw`, and `idle` then `idle` with `duty_floor_kw` 3. `get_current_action` and the schedule builder call `planned_draw_runs` without `modulation_floor`. `_optimize_space_only`'s exception arm sets `optimal_power = initial_power` and does not project; `_build_result` still sets `duty_floor_kw` when the flag is on.

`python3 tests/env_drift.py --all` exited 0: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE`. No claim file is in the diff. No card file is in the diff. `python3 tests/structure.py` exited 0, `STRUCTURE RATCHET PASSED`, no `*_budgets.json` in the diff. Three-dot diff of `VERSION`, the manifest and `RELEASE_NOTES.md` is empty. `git merge-tree --write-tree origin/main af7cf417c9e8ff7a23e0bd82bd4ca32fc5814cbf` exited 0 with empty stderr.

The group brief (feature, R9-SW-6) names a phase-0 measurement for each of (a) solve cost and comfort on a metered and an unmetered-shaped install, (b) the flow-setpoint lever, (c) `house_heat_loss_scale` drift and sample rejection, (d) the write-surface enumeration. None of those is a test in this diff, and ## Figures is `none`. Issue comments contain the (e) fold and no waiver of that phase. (e) is not in the diff, which the body says. R9-UX-9's brief already says it consumes this probe. The probe's fields are writes, measured power and frequency; that brief's condition also names an energy sensor and water mass flow, which this probe does not report.
