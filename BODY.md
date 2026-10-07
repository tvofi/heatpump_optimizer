Closes #1955. Leaves #201 open.

A switch-plus-setpoint install with no frequency entity cannot duty-cycle. (a) projects a planned level in (0, p_min) up to p_min and leaves off off. (b) the heating flow follows the planned level up to the configured ceiling. (c) the house-heat-loss learner freezes when the probe reports no measured power and no duty-cycle mechanism. (d) planned_draw_runs refuses a sub-minimum level when a modulation floor is set.

## Head

aadd1de4804fac2f71de5c46d3f1f3b092b4de00

`21a62c10a03f5bd684d529aa70d8ff7ef6938471` merges the authored code head `b4172f56f109341f1297ac276529c86d54670785` and then merges origin/main `bcea7488` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

b4172f56f109341f1297ac276529c86d54670785

## Mutation proof

n/a: not re-taken in this pass.

## Null control

n/a: not re-taken in this pass.

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
(b) pump_arbiter.py::<module> — already guarded: the module constant is the default configured_flow_heat_c falls back to.
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
```
PYTHONPATH=tests/hastub:custom_components:tests python3 -c 'from datetime import datetime, timezone; from types import SimpleNamespace as NS; from harness import FakeState; from heatpump_optimizer.const import CONF_FLOW_HEAT_C; from heatpump_optimizer import pump_arbiter as pa; print(pa._flow_target(NS(config={CONF_FLOW_HEAT_C: 48.0}, state=NS(outdoor_temperature=-5.0, return_temperature=35.0, floor_return_temperature=None), thermal=NS(curve_flow_temp=lambda _o: 60.0), plan=None), FakeState("40", attributes={"min": 20, "max": 70}), None, datetime(2026, 1, 10, tzinfo=timezone.utc)))'
```

48.0

## Red checks

`typing`. Cheaper detector: none. The census is `tests/typing_ruler.py --mypy`. The source-only ruler does not see an undeclared field.

`mutation`. Job 112597999835 exited 1 in `pip install --require-hashes -r tests/requirements-ci.txt`. The log line is `No matching distribution found for aiohttp==3.14.3`. No table output was uploaded, so the log names no site. Cheaper detector for an unpinned site: `python3 tests/mutation_table.py --pin-killed --base origin/main`. At this head it prints `PIN KILLED: nothing to pin`. Cheaper detector for the install failure: none.

`mutation-autofix`. Summary line `skip-no-measurement`. Job 112598224753 exited 1 on "Report whether the repair happened". No bot pin is coming. That line's command is the same `--pin-killed` run, and it has nothing to pin. Cheaper detector: none.

`pr-contract`. Job 112598702771 on 47e6dab020c89ffed44e02d4ee05af003f448b22 failed because `## Red checks` did not name `mutation-autofix`. Jobs 112614399885 and 112613659112 on 21a62c10a03f5bd684d529aa70d8ff7ef6938471 succeeded. Cheaper detector: `node tools/policy/policy_lint.mjs --pr-body`. Standing cost is one body lint.

`coverage-ratchet`. Job 112604091360. notifier.py 78.63 %, pump_arbiter.py 79.86 %, sysid.py 92.98 %. `tests/features.py` exited 1 at 358s on `AttributeError` in `_flow_inlet_c` (`inp.state.floor_return_temperature`). Main's coverage job 112591811045 ran the same scripts and `tests/features.py` exited 0 at 856s. notifier.py and sysid.py are absent from this diff; main's artifact has the same statement counts and clears both. Cheaper detector: none.

`env-matrix`. Cheaper detector: the job. It checks `tools/policy/*.mjs` out from the base before it runs.

`delivery-status`. It grades main. `dev/programme/delivery/2006.md` is in this diff, so the red is answered here. Cheaper detector: none. The job is `python -I -S tests/delivery_status.py --check`.

`nightly-status`. It grades main. Cheaper detector: none.

`fast (3.14)`. Job 112578082702 exited 1 in "Run the suite". `tests/entities.py` failed P6 G on `pump_arbiter.py` probing `return_temperature`, which production does not store; the inlet is `floor_return_temperature`. `tests/config_flow_steps.py` failed the absent-key census because `freq_control_mode` was read without its form default, so the census could not prove the key. Cheaper detector: none. Those two scripts are the checks.

## Forward-carry

none

## Friction

none
