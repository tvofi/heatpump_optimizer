Closes #1955. Leaves #201 open.

Planner power on a switch-plus-setpoint install that has no frequency entity. One probe, `probe_install` in `thermal_model.py`, reports writes, measured power and frequency. (a), (c) and (d) read it. A fully metered report, and `OptimizationConfig()` with the flag left at its default, keep the duty-cycle bounds, so those plans stay byte-identical. `clamp_planned_levels: false` is the opt-out.

(a) Projects a planned level in `(0, p_min)` up to `p_min` and leaves 0 off. The closed interval `[p_min, p_max]` was refused: it would force the pump on for the horizon. The objective and the published schedule both use the projection, and only when the probe says the surface cannot duty-cycle.

(b) A heating flow follows the planned level, from the return temperature (or the 35 °C hold when no return is configured) at the modulation floor up to `flow_heat_c` (default the existing heating-flow constant) at full power. A non-positive planned level, including a boost over an idle plan, still holds that ceiling. A missing power band keeps the constant, which is what the arbiter stubs pin.

(c) The house-heat-loss learner freezes with reason `unmetered_power` when the probe reports no measured power and no duty-cycle mechanism, ranked with the boost freeze after ventilation. A frequency install without a power meter still learns from the commanded figure, because the compressor can realize it. An install with no write surface configured is not reclassified.

(d) `planned_draw_runs` refuses a level in `(MIN_RUNNING_DRAW_KW, p_min)` when given `modulation_floor`. `step_duty` stays a two-parameter function; the floor rides on the result as `duty_floor_kw` when the solve clamped, so a caller cannot hand it a threshold.

(e), the optional thermal-power entity, is not in this diff. The card recommendation is R9-UX-9 (#1956), which already says it consumes this probe and not a second one.

## Head

eb0a8bf97bdbcea0b2b289077b2cc9e9a22e5553

Merged `origin/main` at `1fa713f73740e99a5762019f574ccd6afa45dca2`.

## Mutation proof

Each line restored after the run. The instrument is the production function the features.py check imports.

- `projected[gap] = lo` replaced with a no-op assignment. `project_planned_levels` on `[0, 0.3, 0.5, 3, 14, 20]` at `p_min` 3, `p_max` 14 left `0.3` and `0.5` in place. Check that goes red: "a switch-plus-setpoint install clamps a sub-minimum level up to p_min and keeps off off".
- `return floor + frac * (heat - floor)` replaced with `return heat`. Check that goes red: "the heating flow is the ceiling at full power and the inlet at p_min, and a configured ceiling moves it".
- `return UNMETERED_POWER_FREEZE` replaced with `return None`. Check that goes red: "the house learner freezes on an unmetered switch-plus-setpoint install and not on a metered one".
- The sub-minimum branch of `planned_draw_runs` returned the duty-cycle comparison. Check that goes red: "null control: the duty-cycle reading of 0.3 kW still runs when no floor is passed" (the floor arm).

`stress.py` is left to CI's mutation check. No local `--pin-killed`.

## Null control

`OptimizationConfig()` leaves `clamp_planned_levels` false. `from_mapping` on an empty config and on a config with a power entity plus a frequency entity leaves it false. `planned_draw_runs(0.3)` with no floor is true. `learner_unmetered` on that metered config is `None`. `step_duty` on a plan of 0.15 kW space plus 2.0 kW hot water, then 1.5 kW space, is `both` then `space`, and its signature has two parameters.

## Figures

```
python3 -c 'exec("import ast\nfrom pathlib import Path\nroot = Path(\"custom_components/heatpump_optimizer\")\nfacts = {\"(a)\": {\"project_planned_levels\", \"levels_clamped\", \"_published_levels\", \"_realize_draw\"}, \"(b)\": {\"flow_setpoint_for_level\", \"configured_flow_heat_c\", \"FLOW_HEAT_C\"}, \"(c)\": {\"learner_unmetered\", \"_tail_freeze\"}, \"(d)\": {\"planned_draw_runs\", \"planned_draws_run\"}}\ndef enc(parents, n):\n    own = n.name if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) else \"\"\n    cur, parts = n, []\n    while cur in parents:\n        cur = parents[cur]\n        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):\n            parts.append(cur.name)\n    parts = list(reversed(parts))\n    if own:\n        parts.append(own)\n    return \".\".join(parts) or \"<module>\"\ndef under_import(parents, n):\n    cur = n\n    while cur in parents:\n        cur = parents[cur]\n        if isinstance(cur, (ast.Import, ast.ImportFrom)):\n            return True\n    return False\nrows = set()\nfor path in sorted(root.glob(\"*.py\")):\n    if path.name == \"const.py\":\n        continue\n    tree = ast.parse(path.read_text())\n    parents = {}\n    for n in ast.walk(tree):\n        for c in ast.iter_child_nodes(n):\n            parents[c] = n\n    for n in ast.walk(tree):\n        if under_import(parents, n):\n            continue\n        name = n.name if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) else n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else (n.func.id if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) else n.func.attr if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) else None)\n        if not name:\n            continue\n        for label, keys in facts.items():\n            if name in keys:\n                rows.add(\"%s %s::%s\" % (label, path.name, enc(parents, n)))\nprint(\"\\n\".join(sorted(rows)))\n")' 
```

(a) thermal_model.py::project_planned_levels — closed in this diff: the projection onto {0} union [p_min, p_max].
(a) thermal_model.py::levels_clamped — closed in this diff: the probe gate from_mapping reads.
(a) optimizer.py::_published_levels — closed in this diff: calls project_planned_levels.
(a) optimizer.py::_realize_draw — closed in this diff: calls _published_levels for the objective.
(a) optimizer.py::HeatPumpOptimizer._solve_objectives.objective — closed in this diff: calls _realize_draw.
(a) optimizer.py::HeatPumpOptimizer._solve_objectives.objective_batch — closed in this diff: calls _realize_draw.
(a) optimizer.py::HeatPumpOptimizer._optimize_space_only — closed in this diff: calls _realize_draw.
(a) optimizer.py::HeatPumpOptimizer._optimize_with_dhw — closed in this diff: calls _published_levels on the published levels.
(a) optimizer.py::OptimizationConfig.from_mapping — closed in this diff: calls levels_clamped.
(b) thermal_model.py::flow_setpoint_for_level — closed in this diff: the level-following flow.
(b) thermal_model.py::configured_flow_heat_c — closed in this diff: the configured ceiling.
(b) pump_arbiter.py::_flow_target — closed in this diff: heating steps call flow_setpoint_for_level; the duty-None hold clamps to configured_flow_heat_c.
(b) pump_arbiter.py::<module> — already guarded: FLOW_HEAT_C = 55.0 is the default configured_flow_heat_c falls back to.
(c) thermal_model.py::learner_unmetered — closed in this diff: the unmetered-power freeze.
(c) coordinator.py::_tail_freeze — closed in this diff: calls learner_unmetered.
(c) coordinator.py::HeatPumpOptimizerCoordinator._learning_frozen — closed in this diff: returns _tail_freeze after the boost gate.
(d) thermal_model.py::planned_draw_runs — closed in this diff: the modulation-floor gate.
(d) pump_arbiter.py::step_duty — closed in this diff: sets that floor around the two owner calls.
(d) pump_arbiter.py::_release_duty_floor._wrapped — already guarded: clears the floor step_duty set and does not decide a step.
(d) thermal_model.py::planned_draws_run — already guarded: the batch form of the same comparison; the levels it is handed were projected by _published_levels when the install clamps.
(d) optimizer.py::HeatPumpOptimizer._power_to_heat_pump_schedule — already guarded: calls planned_draws_run on those projected levels.
(d) optimizer.py::HeatPumpOptimizer.get_current_action — already guarded: prefers heat_pump_on_schedule from that call.
(d) coordinator.py::_apply_result_payload — already guarded: prefers heat_pump_on_schedule the same way.

## Red checks

`typing`. On `af7cf417`, job 112527225870, `tests/typing_ruler.py --mypy` recorded errors 0 and measured 1, code attr-defined, in optimizer.py: `duty_floor_kw` was passed on `OptimizationResult` with no field. The field is declared and passed in the constructor. Job 112561792109 on `b71f454` succeeded. Cheaper detector: none. The source-only ruler `tests/run.sh` runs counts ignores and does not see an undeclared field. The census is the check.

`mutation`. Job 112561792227 printed that the ledger agrees, then that no mutant is both generatable and drivable, then `MUTATION TABLE PASSED (empty pool)` over 5 production files. The floor test was a comparison spanned across lines, and `else: return _tail_freeze(self)` was the sole statement of its body, so neither was a site. The restored hold line clamps with the literal `FLOW_HEAT_C`, so `_flow_target` with `flow_heat_c` 48 and a curve of 60 returned 55.0 when duty is None. The floor comparison, the unmetered return and the hold clamp are one-line sites on the lines this diff changes, and the hold uses the configured ceiling. Cheaper detector: `python3 tests/mutation_table.py --scope changed --base origin/main`, which draws those sites before it drives a mutant. Standing cost is one inventory pass, no clone and no solve.

`env-matrix`. Job 112561792593, run 37549638345, held 2 declared outcomes and missed 14. Shallow and since-ref cannot find `.claude/workflows/policy_lint.mjs`. The head blob `d99577da` of `tools/policy/policy_lint_envmatrix.mjs` spawns `tools/policy/`. The base blob `40bac880` still spawns `.claude/workflows/policy_lint.mjs`. `governance.yml` is unchanged against that merge base. The job checks out `tools/policy/*.mjs` from the base, commits that, then runs the script, so the path edit in the head does not run. Cheaper detector: the job. This update merges `1fa713f7` and does not edit the file that job replaces.

`delivery-status`. Ancestor job 112526801540 printed `DELIVERY STATUS UNCHECKED — 42 rowed, 2 pending, 0 overdue`, pending #2003 and #2001, plus unread merge subjects. `docs/delivery/2006.md` is in this diff, so the red is answered here. Cheaper detector: none. The job is `python -I -S tests/delivery_status.py --check` on the base's copy of that script.

`nightly-status`. `nightly-status` grades main. Ancestor job 112527225983 printed `NIGHTLY FAILED: record-autofix failed last night` for scheduled run 37440269774 at head `cff39da`. Cheaper detector: none. The job reads main's last nightly, and this diff leaves that lane alone.

`fast (3.14)`. Ancestor job 112527225858 on `af7cf417` printed `2 TEST SCRIPT(S) FAILED`. `tests/entities.py` failed the `--anchor` re-drive because the mutation ledger completeness refusal named the stale `killed_by` pins; those lines are restored at this head. `tests/config_flow_steps.py` failed `_ABSENT_FALLBACKS` and `_ABSENT_IS_NOT_DEFAULT` on `freq_control_mode`. This diff does not edit `config_flow.py`, and that key is not one it adds, so that pair is not this head's failure. Cheaper detector for the entities failure: the mutation inventory above, one pass before any mutant. For the config-flow pair: none. That script is the check.

`tests/features.py` "R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it" printed the same pair on this branch and on unmodified `origin/main` at `a28fd0ae` (optimizer.py is unchanged from there to `6001b09a`). The branch did not move it. Cheaper detector: none; that check is the measurement.

## Forward-carry

none

## Friction

none
