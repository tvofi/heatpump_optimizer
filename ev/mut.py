"""Reviewer's mutation driver: one string mutation at a time, run the group's command, restore."""
import subprocess, sys, pathlib
R = pathlib.Path("/home/user/rev/custom_components/heatpump_optimizer")
SH, PA, CO, EC = "supply_hold.py", "pump_arbiter.py", "coordinator.py", "early_cutoff.py"
M = [
 (SH, "else age < MIN_RUN", "else age <= MIN_RUN", "MIN_RUN boundary < -> <="),
 (SH, "(age < MIN_PAUSE or", "(age <= MIN_PAUSE or", "MIN_PAUSE boundary < -> <="),
 (SH, "MIN_RUN = timedelta(minutes=10)", "MIN_RUN = timedelta(minutes=11)", "MIN_RUN 10 -> 11"),
 (SH, "MIN_RUN = timedelta(minutes=10)", "MIN_RUN = timedelta(minutes=9)", "MIN_RUN 10 -> 9"),
 (SH, "MIN_PAUSE = timedelta(minutes=10)", "MIN_PAUSE = timedelta(minutes=11)", "MIN_PAUSE 10 -> 11"),
 (SH, "MIN_PAUSE = timedelta(minutes=10)", "MIN_PAUSE = timedelta(minutes=9)", "MIN_PAUSE 10 -> 9"),
 (SH, "if nxt - now >= MIN_RUN or", "if nxt - now > MIN_RUN or", "rule3 boundary >= -> >"),
 (SH, "if nxt - now >= MIN_RUN or", "if nxt - now >= MIN_RUN - timedelta(minutes=1) or", "rule3 window one tick shorter"),
 (SH, "wait = (age < MIN_PAUSE or _ends_soon(inp, boosts, now))", "wait = (_ends_soon(inp, boosts, now))", "drop MIN_PAUSE"),
 (SH, "if value else age < MIN_RUN", "if value else False", "drop MIN_RUN"),
 (SH, "(age < MIN_PAUSE or _ends_soon(inp, boosts, now))", "(age < MIN_PAUSE)", "drop rule three"),
 (SH, "    held.supply_held = False\n    if value is None:", "    if value is None:", "no reset of supply_held per write"),
 (SH, "step_supply(inp, boosts, nxt) is not False", "step_supply(inp, boosts, nxt) is True", "rule3: next step None treated as off"),
 (SH, "step_supply(inp, boosts, nxt) is not False", "False", "rule3: ignore next step's command"),
 (SH, 'in ("dhw", "both") and tank_reason', '== "dhw" and tank_reason', "rule3 exemption: both dropped"),
 (SH, 'in ("dhw", "both") and tank_reason', 'in ("both",) and tank_reason', "rule3 exemption: dhw dropped"),
 (SH, "return not (step_duty(inp.plan, now) in (\"dhw\", \"both\") and tank_reason(inp))", "return True", "rule3 exemption removed"),
 (SH, "inp.mode not in (MODE_AUTO, MODE_ECONOMY)\n", "inp.mode != MODE_AUTO\n", "passes: economy treated as non-plan"),
 (SH, "inp.mode not in (MODE_AUTO, MODE_ECONOMY)\n", "False\n", "passes: mode never passes"),
 (SH, "boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNEL_DHW, now)", "boosts.active(CHANNEL_DHW, now)", "passes: space boost dropped"),
 (SH, "boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNEL_DHW, now)", "boosts.active(CHANNEL_SPACE, now)", "passes: dhw boost dropped"),
 (SH, '_UNREADABLE = (None, "unavailable", "unknown")', '_UNREADABLE = (None, "unavailable")', "unknown state readable"),
 (SH, '_UNREADABLE = (None, "unavailable", "unknown")', '_UNREADABLE = (None, "unknown")', "unavailable state readable"),
 (SH, "(state != \"off\") is value", "(state == \"on\") is value", "running read as on only"),
 (SH, "return None if since > now else now - since", "return now - since", "future stamp not refused"),
 (SH, "span = 2 * timedelta", "span = 1 * timedelta", "freeze span one interval"),
 (SH, "- at < span", "- at <= span", "freeze span boundary"),
 (SH, "held.supply_held, held.held_at = True, now", "held.supply_held = True", "held_at not stamped"),
 (SH, "nxt = plan_step_start(now) + timedelta", "nxt = now + timedelta", "rule3 next step from now"),
 (SH, "if inp.disinfecting:\n        return \"disinfecting\"\n", "", "disinfection exemption dropped"),
 (SH, "or (inp.action or {}).get(\"mode\") == \"system_identification\"", "", "sysid passes dropped"),
 (PA, "if on is None and held.supply_held and not inp.entry_released:", "if on is None and held.supply_held:", "retry ignores released"),
 (PA, "if on is None and held.supply_held and not inp.entry_released:", "if on is None and not inp.entry_released:", "action retry without held"),
 (PA, "if on is None and held.supply_held and not inp.entry_released:", "if False:", "no action retry"),
 (PA, "if on != last or held.supply_held:", "if on != last:", "no retry of same command"),
 (PA, "        held.supply_held = False  # a held write dies with its command\n", "", "held flag survives a dropped command"),
 (PA, "(held.supply[0] == step and not held.supply_held)", "held.supply[0] == step", "tick never retries within step"),
 (PA, "if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or not inp.action:", "if not inp.action:", "action retry ignores mode/stale"),
 (PA, "if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or not inp.action:", "if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or not inp.action:", "action retry ignores stale plan"),
 (PA, "if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or not inp.action:", "if inp.mode != MODE_AUTO or inp.plan_stale or not inp.action:", "action retry: economy dropped"),
 (PA, "    return inp.hass.states.get(entity) if entity else None\n\n\ndef _pump_off", "    return inp.hass.states.get(entity)\n\n\ndef _pump_off", "supply_switch: no entity guard"),
 (CO, "    if supply_hold.interval_held(pump_arbiter.state_for(coord), config):\n        return supply_hold.FREEZE_HELD\n", "", "no learner freeze"),
 (CO, "elif switch_entity and not held.supply_held:", "elif switch_entity:", "held logged as blocked skip"),
 (EC, "if run is None or run < MIN_ON:", "if run is not None and run < MIN_ON:", "cut-off: unknown run allowed"),
 (EC, "if run is None or run < MIN_ON:", "if run is None or run <= MIN_ON:", "cut-off MIN_ON boundary"),
 (EC, "return tank_reason(inp)", "return None", "cut-off: tank exemption dropped"),
 (EC, "MIN_ON, MIN_OFF = MIN_RUN, MIN_PAUSE", "MIN_ON, MIN_OFF = MIN_RUN, MIN_PAUSE + MIN_PAUSE", "cut-off MIN_OFF doubled"),
]
cmd = sys.argv[1]
only = sys.argv[2:] 
killed = surv = 0
for i, (f, a, b, label) in enumerate(M):
    if only and str(i) not in only: continue
    p = R / f; src = p.read_text()
    n = src.count(a)
    if n != 1:
        print(f"SKIP     {f}: {label} (pattern count {n})"); continue
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run(["bash", cmd], capture_output=True, text=True, timeout=1800)
    finally:
        p.write_text(src)
    out = (r.stdout + r.stderr).strip().splitlines()
    fl = [l for l in out if "FAIL" in l][:1]
    if r.returncode:
        killed += 1; print(f"KILLED   {f}: {label} | {(fl or out[-1:] or ['rc'])[0][:110]}")
    else:
        surv += 1; print(f"SURVIVED {f}: {label} | {' / '.join(out[-2:])}")
print(f"{killed} killed, {surv} survived")
