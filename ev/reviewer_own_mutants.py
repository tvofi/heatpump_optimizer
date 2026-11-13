import subprocess, sys, os
W = sys.argv[1]; CC = os.path.join(W, "custom_components/heatpump_optimizer")
M = [
 ("O1 startable_steps: the step after a charging step is not startable", "dhw_planner.py", "    ok[1:] |= on[:-1]\n", ""),
 ("O2 startable_steps: a step already charging is not startable", "dhw_planner.py", "[: on.size] < start_below[: on.size]) | on", "[: on.size] < start_below[: on.size])"),
 ("O3 everyday step target ignores the charge limit", "thermal_model.py", "        return min(float(params.dhw_setpoint), float(params.dhw_max_temp))\n", "        return float(params.dhw_setpoint)\n"),
 ("O4 cycle step target ignores the hard maximum", "thermal_model.py", "    return min(float(target), float(params.dhw_hard_max_temp))\n", "    return float(target)\n"),
 ("O5 a unit-less number is no reading", "inputs.py", "[1] if unit else 1.0\n", "[1] if unit else None\n"),
 ("O6 ledger not-startable >= to >", "pump_arbiter.py", "tank is not None and float(tank) >= start", "tank is not None and float(tank) > start"),
 ("O7 place_startable re-buys without dropping first", "dhw_planner.py", "repair(plan=drop_unstartable(plan, start_below, temps_of), start_below=start_below)", "repair(plan=plan, start_below=start_below)"),
 ("O8 the two options are swapped", "inputs.py", "read_temperature_delta_k(hass, cfg.dhw_hysteresis_entity)\n", "read_temperature_delta_k(hass, cfg.space_hysteresis_entity)\n"),
 ("O9 an unstartable run loses only its first step", "dhw_planner.py", "            plan[i:end] = 0.0\n", "            plan[i] = 0.0\n"),
 ("O10 not-startable for any actual", "pump_arbiter.py", 'if planned == "dhw" and actual == "idle" and _not_startable(row):', 'if planned == "dhw" and _not_startable(row):'),
 ("O11 not-startable for any planned duty", "pump_arbiter.py", 'if planned == "dhw" and actual == "idle" and _not_startable(row):', 'if actual == "idle" and _not_startable(row):'),
 ("O12 Kelvin delta read with the absolute offset", "inputs.py", "    delta_k = value * scale\n", "    delta_k = value * scale + (TEMPERATURE_UNIT_TO_C.get(unit) or (0.0, 1.0))[0]\n"),
 ("O13 start_flow lift is the hysteresis alone", "thermal_model.py", "    return lift if hysteresis is None else max(lift, hysteresis)\n", "    return lift if hysteresis is None else hysteresis\n"),
 ("O14 notice placeholder-free: issue never raised", "setpoint_check.py", "        start is not None and floor > start,\n", "        False,\n"),
 ("O15 ledger row start_below not recorded", "pump_arbiter.py", '        row["start_below"] = _dhw_start_below_c(inp)\n', ""),
 ("NULL", "thermal_model.py", "    lift = configured_flow_min_lift_k(config)\n    hysteresis = finite_float(start_hysteresis_k)\n", "    lift = configured_flow_min_lift_k(config)  # null\n    hysteresis = finite_float(start_hysteresis_k)\n"),
]
for name, f, old, new in M:
    p = os.path.join(CC, f); src = open(p).read()
    if src.count(old) != 1: print(f"{name}: ANCHOR x{src.count(old)}"); continue
    open(p, "w").write(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tests/block_duty.py"], cwd=W, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=600)
        fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
        print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {len(fails)} failing", flush=True)
        for l in fails[:2]: print("    " + l[:150])
    finally:
        open(p, "w").write(src)
