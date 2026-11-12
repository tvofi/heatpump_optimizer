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
 ("M1 lift owner returns the configured lift", "thermal_model.py", "    return lift if hysteresis is None or hysteresis <= lift else hysteresis\n", "    return lift\n"),
 ("M2 drop_unstartable >= to >", "dhw_planner.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
 ("M3 ledger not-startable branch removed", "pump_arbiter.py", '    if planned == "dhw" and actual == "idle" and _not_startable(row):\n        return "not-startable"\n', ""),
 ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]\n", ""),
 ("M5 startable_steps < to <=", "dhw_planner.py", "[: on.size] < start_below[: on.size]) | on", "[: on.size] <= start_below[: on.size]) | on"),
 ("M6 a zero hysteresis is a start condition", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis < 0.0:"),
 ("M7 the difference reader applies the unit's zero", "inputs.py", "    delta_k = value * spec[1]\n", "    delta_k = (value + spec[0]) * spec[1]\n"),
 ("M8 the cycle step judged against the everyday target", "dhw_planner.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True), hysteresis_k)\n", "        pass\n"),
 ("M9 notice at a minimum equal to the start temperature", "setpoint_check.py", "start is not None and floor > start,", "start is not None and floor >= start,"),
 ("M10 place_startable returns without the final drop", "dhw_planner.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of)\n", "        plan = fixed\n    return plan\n"),
 ("M11 coordinator does not read the options", "coordinator.py", "        read_start_hysteresis(state, self.hass, self.effective_config)\n", ""),
 ("M12 the floor write ignores the hysteresis", "pump_arbiter.py", 'start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),', "start_flow_min_lift_k(inp.config, None),"),
 ("M13 the planner ignores the hysteresis", "dhw_planner.py", "params, initial_state.dhw_start_hysteresis_k, n_steps, legionella_step)", "params, None, n_steps, legionella_step)"),
 ("M14 ledger start ignores the written target", "pump_arbiter.py", "        dhw_step_target_c(inp.params, cycle) if written is None else written, hysteresis)", "        dhw_step_target_c(inp.params, False), hysteresis)"),
 ("M15 delta reader accepts above the maximum", "inputs.py", "    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None", "    return delta_k if 0.0 <= delta_k else None"),
 ("M16 a run at step 0 is judged too", "dhw_planner.py", "    on = plan > 0.0\n    i = 1\n", "    on = plan > 0.0\n    i = 0\n"),
 ("NULL comment-only change", "dhw_planner.py", "    on = plan > 0.0\n    i = 1\n", "    on = plan > 0.0  # null mutant\n    i = 1\n"),
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
