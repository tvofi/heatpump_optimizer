"""Reviewer's own mutants for #2445 (out of tree; applied to /tmp/seat/rev2445/mut, restored by git checkout)."""
import sys, pathlib
T = pathlib.Path(sys.argv[1]); name = sys.argv[2]
cc = T / "custom_components/heatpump_optimizer"
OPT, ARB, TM = cc / "optimizer.py", cc / "pump_arbiter.py", cc / "thermal_model.py"
def sub(p, old, new, count=1):
    s = p.read_text(); assert s.count(old) == count, (name, old, s.count(old)); p.write_text(s.replace(old, new))
M = {
 "M1": lambda: sub(ARB, "    return next(\n        (reading.value for reading in readings if reading.ok), None\n    )",
                  "    return getattr(inp.state, 'floor_return_temperature', None)"),
 "M2": lambda: sub(TM, "FLOW_MIN_LIFT_K = 5.0", "FLOW_MIN_LIFT_K = 0.0"),
 "M3": lambda: sub(ARB, "    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,\n    CONF_BUFFER_TANK_TEMP_ENTITY,\n", "    CONF_BUFFER_TANK_TEMP_ENTITY,\n"),
 "M4": lambda: sub(ARB, "    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,\n    CONF_BUFFER_TANK_TEMP_ENTITY,\n", "    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,\n"),
 "M5": lambda: sub(ARB, "    CONF_BUFFER_TANK_TEMP_ENTITY,\n    CONF_FLOOR_RETURN_TEMP_ENTITY,\n    CONF_VALVE", "    CONF_BUFFER_TANK_TEMP_ENTITY,\n    CONF_VALVE"),
 "M6": lambda: sub(ARB, "    CONF_FLOOR_RETURN_TEMP_ENTITY,\n    CONF_VALVE_OUTLET_TEMP_ENTITY,\n)", "    CONF_FLOOR_RETURN_TEMP_ENTITY,\n)"),
 "M7": lambda: sub(OPT, "            cands = _relaxed_starts(self, objective, objective_batch, bounds, first, (),\n                                    cands, maxiter)\n", ""),
 "M8": lambda: sub(OPT, """                move_starts=partial(  # the initial solve's alone: a warm pass adds none
                    _relaxed_starts, self, objective, objective_batch, bounds,
                    len(h.extra_starts or ()) if warm_start is None else len(starts),
                    (dhw_plan,),
                ),
""", ""),
 "M9": lambda: sub(OPT, "    return opt.config.clamp_planned_levels and not opt._levels_relaxed", "    return opt.config.clamp_planned_levels"),
 # reviewer extras
 "X1_swap_tank_floor": lambda: sub(ARB, "    CONF_BUFFER_TANK_TEMP_ENTITY,\n    CONF_FLOOR_RETURN_TEMP_ENTITY,\n    CONF_VALVE", "    CONF_FLOOR_RETURN_TEMP_ENTITY,\n    CONF_BUFFER_TANK_TEMP_ENTITY,\n    CONF_VALVE"),
 "X2_replace_not_append": lambda: sub(OPT, "    return [*cands, np.asarray(moved.x, dtype=float)]", "    cands[first] = np.asarray(moved.x, dtype=float)\n    return cands"),
 "X3_guard_index_dropped": lambda: sub(OPT, "    if not opt.config.clamp_planned_levels or first >= len(cands):", "    if not opt.config.clamp_planned_levels:"),
 "X4_flag_never_reset": lambda: sub(OPT, "    finally:\n        opt._levels_relaxed = False\n    return [*cands", "    finally:\n        pass\n    return [*cands"),
 "X5_dhw_first_zero": lambda: sub(OPT, "len(h.extra_starts or ()) if warm_start is None else len(starts),", "0 if warm_start is None else len(starts),"),
 "X6_dhw_warm_also": lambda: sub(OPT, "len(h.extra_starts or ()) if warm_start is None else len(starts),", "len(h.extra_starts or ()),"),
 "X7_stale_ignored": lambda: sub(ARB, "(reading.value for reading in readings if reading.ok)", "(reading.value for reading in readings if reading.value is not None)"),
 "X8_unclamped_relaxed": lambda: sub(OPT, "    if not opt.config.clamp_planned_levels or first >= len(cands):", "    if first >= len(cands):"),
 "L_CMP_BOUND": lambda: sub(OPT, "first >= len(cands):", "first > len(cands):"),
 "L_CONST10": lambda: sub(TM, "FLOW_MIN_LIFT_K = 5.0", "FLOW_MIN_LIFT_K = 10.0"),
 "L_FLOOR_RETURN_DEL": lambda: sub(TM, "    return None if inlet is None else inlet + FLOW_MIN_LIFT_K", "    pass"),
 "L_RELAXED_RETURN_DEL": lambda: sub(OPT, "    return [*cands, np.asarray(moved.x, dtype=float)]", "    pass"),
}
M[name]()
