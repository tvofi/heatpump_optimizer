"""R10-OUTSIDE-DHW-START-HYSTERESIS: the named mutants of the start-hysteresis build.

Applies each mutant, one at a time, to the production file it names under a
checkout, runs ``tests/block_duty.py`` there, prints KILLED or SURVIVED with
the failing check names, and restores the file.

    python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py WORKTREE [M1 M4 NULL ...]

WORKTREE is a checkout to mutate in place: a ``git worktree`` of the head,
never the tree a gate is running in. With no names every mutant runs. A
mutant whose anchor text is not found exactly once prints ANCHOR and is not
run, so a moved line reads as unproven, never as killed.
Null control: the NULL mutant changes a comment only and must print SURVIVED;
a harness that kills it is failing for a reason of its own.
"""
import subprocess, sys, os
W = sys.argv[1]
CC = os.path.join(W, "custom_components/heatpump_optimizer")
M = [
 ("M1 lift owner returns the configured lift", "thermal_model.py", "    return lift if hysteresis is None else max(lift, hysteresis)\n", "    return lift\n"),
 ("M2 drop_unstartable >= to >", "dhw_planner.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
 ("M3 ledger not-startable branch removed", "pump_arbiter.py", '    if planned == "dhw" and actual == "idle" and _not_startable(row):\n        return "not-startable"\n', ""),
 ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]\n", ""),
 ("M5 startable_steps < to <=", "dhw_planner.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
 ("M6 a zero hysteresis is a start condition", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis < 0.0:"),
 ("M7 the difference reader ignores the unit's scale", "inputs.py", "    delta_k = value * scale\n", "    delta_k = value\n"),
 ("M8 the cycle step judged against the everyday target", "dhw_planner.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)\n", "        pass\n"),
 ("M9 notice at a minimum equal to the start temperature", "setpoint_check.py", "start is not None and floor > start,", "start is not None and floor >= start,"),
 ("M10 place_startable returns without the final drop", "dhw_planner.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of)\n", "        plan = fixed\n    return plan\n"),
 ("M11 coordinator does not read the options", "coordinator.py", "        read_start_hysteresis(state, self.hass, self.effective_config)\n", ""),
 ("M12 the floor write ignores the hysteresis", "pump_arbiter.py", 'start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),', "start_flow_min_lift_k(inp.config, None),"),
 ("M13 the planner ignores the hysteresis", "dhw_planner.py", "dhw_start_temps(params, initial_state, n_steps, legionella_step)", "dhw_start_temps(params, type(initial_state)(), n_steps, legionella_step)"),
 ("M14 ledger start ignores the written target", "pump_arbiter.py", "dhw_start_below_c(_dhw_target(inp), hysteresis)", "dhw_start_below_c(dhw_step_target_c(inp.params, False), hysteresis)"),
 ("M15 delta reader accepts above the maximum", "inputs.py", "    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None", "    return delta_k if 0.0 <= delta_k else None"),
 ("M16 a run at step 0 is judged too", "dhw_planner.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on & ~np.append(False, on[:-1])):\n"),
 ("M17 the round bound is nine", "dhw_planner.py", "STARTABLE_ROUNDS = 8\n", "STARTABLE_ROUNDS = 9\n"),
 ("M18 a cycle on the first step is not a cycle step", "dhw_planner.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 < cycle_step < n_steps:"),
 ("M19 a run at the second step is not judged", "dhw_planner.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on[2:] & ~on[1:-1]) + 2:\n"),
 ("M20 the loop never ends early", "dhw_planner.py", "        if np.array_equal(fixed, plan):\n", "        if False:\n"),
 ("M21 a cycle past the horizon is written", "dhw_planner.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 <= cycle_step <= n_steps:"),
 ("M22 the shared clamp zeroes a step on the runnable block", "dhw_planner.py", "        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)\n", "        return np.where(plan <= ctx.min_run_power - 1e-9, 0.0, plan)\n"),
 ("M23 no step is a cycle step for the write or the ledger", "pump_arbiter.py", '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting\n', "    cycle = False\n"),
 ("M24 the set-point check never reaches the start notice", "setpoint_check.py", "    _dhw_start(hass, config, params)\n", "    pass\n"),
 ("M25 the notice judges the cycle's target", "setpoint_check.py", "    target = dhw_step_target_c(params, False, setpoint_grid(", "    target = dhw_step_target_c(params, True, setpoint_grid("),
 ("M26 a hysteresis under one kelvin is none", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis <= 1.0:"),
 ("M27 pinned hot water is not held to the tank's capacity", "dhw_planner.py", "            schedule = self._ctx_clamp(\n                ctx, initial_state.dhw_temperature, draw_rates, max_temp, schedule)\n", "            pass\n"),
 ("M28 the write and the ledger ignore the entity's grid", "pump_arbiter.py", 'return dhw_step_target_c(inp.params, cycle, _grid(inp, "dhw_setpoint"))', "return dhw_step_target_c(inp.params, cycle, None)"),
 ("M29 the planner ignores the entity's grid", "dhw_planner.py", "hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid\n", "hysteresis_k, grid = state.dhw_start_hysteresis_k, None\n"),
 ("M30 the notice ignores the entity's grid", "setpoint_check.py", "dhw_step_target_c(params, False, setpoint_grid(hass, cfg.dhw_setpoint_entity))", "dhw_step_target_c(params, False)"),
 ("M31 the notice is raised with hot water disabled", "setpoint_check.py", "bool(params.dhw_enabled) and start is not None", "start is not None"),
 ("M32 the everyday target ignores the charge limit", "thermal_model.py", "(params.dhw_setpoint, params.dhw_max_temp) if target is None", "(params.dhw_setpoint, 1e9) if target is None"),
 ("M33 the cycle's target ignores the hard maximum", "thermal_model.py", "else (target, params.dhw_hard_max_temp)", "else (target, 1e9)"),
 ("M34 the input read leaves the grid off the state", "inputs.py", "    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_setpoint_entity)\n", ""),
 ("M35 the step after a charge the pump would not start is startable", "dhw_planner.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(on[i])\n"),
 ("M36 a charge at the first step carries nothing on", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = False\n"),
 ("M37 no charge under way carries on", "dhw_planner.py", "        ok[i] |= under_way\n", "        pass\n"),
 ("M38 an entity with no state has a grid", "inputs.py", "    if not entity_id or hass.states.get(entity_id) is None:\n        return None\n    return _grid_of", "    if not entity_id:\n        return None\n    return _grid_of"),
 ("M39 with no entity the target ignores its bound", "thermal_model.py", "        return min(float(value), float(limit))\n", "        return float(value)\n"),
 ("M40 the hot-water write goes to an entity with no state", "pump_arbiter.py", 'return None if _grid(inp, "dhw_setpoint") is None else _dhw_target(inp)', "return _dhw_target(inp)"),
 ("M41 the bound is handed to the grid as the value's own", "thermal_model.py", "grid.bounded(float(value), hi=limit)", "grid.bounded(float(value), hi=float(value))"),
 ("M42 a charge kept at the first step is itself startable on a warm tank", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = bool(on[:1].any())\n    ok[:1] |= on[:1]\n"),
 ("M43 the notice is never raised", "setpoint_check.py", "        bool(params.dhw_enabled) and start is not None and floor > start,\n", "        False,\n"),
 ("NULL comment-only change", "dhw_planner.py", "    on = plan > 0.0\n    for i in", "    on = plan > 0.0  # null mutant\n    for i in"),
]
only = sys.argv[2:] 
for name, f, old, new in M:
    if only and name.split()[0] not in only: continue
    p = os.path.join(CC, f); src = open(p).read()
    if src.count(old) != 1:
        print(f"{name}: ANCHOR x{src.count(old)}"); continue
    open(p, "w").write(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tests/block_duty.py"], cwd=W, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=600)
        fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
        tail = (r.stdout + r.stderr).strip().splitlines()[-1][:160] if not fails else ""
        print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {len(fails)} failing")
        for l in fails[:6]: print("    " + l[:170])
        if r.returncode and not fails: print("    " + tail)
    finally:
        open(p, "w").write(src)
