"""Round-2 reviewer's own mutants on the delta 1884d3885f..abf3b4f9e1 (the reviewer's instrument, not the finder's).
usage: reviewer2_mutants.py WORKTREE [script ...]   (default script tests/block_duty.py)"""
import subprocess, sys, os
W = sys.argv[1]; SCRIPTS = sys.argv[2:] or ["tests/block_duty.py"]
CC = os.path.join(W, "custom_components/heatpump_optimizer")
M = [
 ("P1 bounded: the entity's maximum is no ceiling (the deleted pre-clamp's only heir)", "inputs.py", "        highs = [high] if high is not None else []\n", "        highs = []\n"),
 ("P2 bounded: the entity's minimum is not rounded up as a floor", "inputs.py", "        lows = [v for v in (lo, low) if v is not None]\n", "        lows = [v for v in (lo,) if v is not None]\n"),
 ("P3 bounded: a caller's ceiling under the entity's minimum is kept", "inputs.py", '        if hi is not None and (low is None or hi >= self.on_step(low, rounding="up")):\n', "        if hi is not None:\n"),
 ("P4 the owner puts the value on the step but not in the entity's range", "thermal_model.py", "grid.bounded(float(value), hi=limit)", "grid.on_step(float(value), hi_c=limit)"),
 ("P5 the planner's cycle step ignores the grid", "dhw_planner.py", "dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)", "dhw_start_below_c(dhw_step_target_c(params, True, None), hysteresis_k)"),
 ("P6 the planner's everyday steps ignore the grid", "dhw_planner.py", "dhw_start_below_c(dhw_step_target_c(params, False, grid), hysteresis_k)", "dhw_start_below_c(dhw_step_target_c(params, False, None), hysteresis_k)"),
 ("P7 a held disinfection switch is no cycle step", "pump_arbiter.py", '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting\n', '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA\n'),
 ("P8 a booked cycle is no cycle step", "pump_arbiter.py", '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting\n', '    cycle = bool(inp.disinfecting)\n'),
 ("P9 _bounded drops the caller's floor", "pump_arbiter.py", "    return grid.bounded(value, floor, rounding=rounding, lo=lo, hi=hi)\n", "    return grid.bounded(value, rounding=rounding, lo=lo, hi=hi)\n"),
 ("P10 _bounded drops the caller's rounding", "pump_arbiter.py", "    return grid.bounded(value, floor, rounding=rounding, lo=lo, hi=hi)\n", "    return grid.bounded(value, floor, lo=lo, hi=hi)\n"),
 ("P11 _bounded drops the caller's lo", "pump_arbiter.py", "    return grid.bounded(value, floor, rounding=rounding, lo=lo, hi=hi)\n", "    return grid.bounded(value, floor, rounding=rounding, hi=hi)\n"),
 ("P12 a charge under way is any step that opens below its start, charging or not", "dhw_planner.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(ok[i])\n"),
 ("P13 the first step is startable whenever it charges (the deleted term at step 0 only)", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = bool(on[:1].any()); ok[:1] |= on[:1]\n"),
 ("P14 the state's grid is the hysteresis entity's", "inputs.py", "    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_setpoint_entity)\n", "    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_hysteresis_entity)\n"),
 ("P15 the notice reads hot water as always enabled when the hysteresis is large", "setpoint_check.py", "bool(params.dhw_enabled) and start is not None", "(bool(params.dhw_enabled) or True) and start is not None"),
 ("P16 quantise_setpoint_c drops hi_c", "inputs.py", ".on_step(value_c, rounding=rounding, lo_c=lo_c, hi_c=hi_c)", ".on_step(value_c, rounding=rounding, lo_c=lo_c)"),
 ("P17 on_step: the ceiling rounds to nearest, not down", "inputs.py", 'self.step, "down"))', 'self.step, "nearest"))'),
 ("NULL", "thermal_model.py", "    if grid is None:\n        return min(float(value), float(limit))\n", "    if grid is None:  # null\n        return min(float(value), float(limit))\n"),
]
ONLY = os.environ.get('ONLY', '').split()
for name, f, old, new in M:
    if ONLY and name.split()[0] not in ONLY: continue
    p = os.path.join(CC, f); src = open(p).read()
    if src.count(old) != 1: print(f"{name}: ANCHOR x{src.count(old)}", flush=True); continue
    open(p, "w").write(src.replace(old, new))
    try:
        out = []
        for s in SCRIPTS:
            try:
                r = subprocess.run([sys.executable, s], cwd=W, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=900)
                fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
                rc = r.returncode
            except subprocess.TimeoutExpired:
                fails, rc = ["timeout"], 124
            out.append((s, rc, fails))
        killed = any(rc for _s, rc, _f in out)
        print(f"{name}: {'KILLED' if killed else 'SURVIVED'} " + " ".join(f"{s} rc={rc} {len(fl)} failing" for s, rc, fl in out), flush=True)
        for _s, _rc, fl in out:
            for l in fl[:2]: print("    " + l[:170], flush=True)
    finally:
        open(p, "w").write(src)
