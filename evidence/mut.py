import subprocess, sys, pathlib
W = sys.argv[1]; root = pathlib.Path(W) / "wt"
SH = "custom_components/heatpump_optimizer/supply_hold.py"
PA = "custom_components/heatpump_optimizer/pump_arbiter.py"
CO = "custom_components/heatpump_optimizer/coordinator.py"
EC = "custom_components/heatpump_optimizer/early_cutoff.py"
M = [
 (SH, "if wait else value", "if False else value", "hold never applied (gate removed)"),
 (SH, "else age < MIN_RUN", "else age <= MIN_RUN", "MIN_RUN bound <= "),
 (SH, "else age < MIN_RUN", "else False", "minimum run removed"),
 (SH, "(age < MIN_PAUSE or", "(False or", "minimum pause removed"),
 (SH, "    held.supply_held = False\n    if value is None", "    if value is None", "held flag not reset on each write"),
 (SH, "span = 2 * timedelta", "span = 1 * timedelta", "interval_held span 2 -> 1"),
 (SH, "- at < span", "- at <= span", "interval_held bound <="),
 (SH, "step_supply(inp, boosts, nxt) is not False", "step_supply(inp, boosts, nxt) is True", "rule three: next-step None treated as OFF"),
 (SH, 'getattr(params, "dhw_enabled", False) and ', "", "tank cold ignores dhw_enabled"),
 (SH, "if nxt - now >= MIN_RUN or", "if nxt - now > MIN_RUN + MIN_RUN or", "rule three window doubled"),
 (SH, "boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNEL_DHW, now))", "False)", "boosts never pass"),
 (SH, 'if since is None:\n        return None', 'if since is None:\n        return timedelta(0)', "missing stamp read as age 0"),
 (SH, "if age is None or _passes", "if _passes", "unknown age not passed (would crash/hold)"),
 (PA, "if on != last or held.supply_held:", "if on != last:", "step tick does not retry a held write"),
 (PA, "on = None if inp.entry_released else step_supply", "on = step_supply", "step tick writes after entry released"),
 (PA, "held.supply_held = False  # a held write dies", "pass  # a held write dies", "held flag survives a dropped command"),
 (PA, "or inp.plan_stale or not inp.action", "or not inp.action", "stale plan retries action"),
]
res = []
for f, a, b, why in M:
    p = root / f; src = p.read_text()
    n = src.count(a)
    if n != 1:
        res.append(f"NOMATCH({n}) {f}: {a!r} | {why}"); continue
    p.write_text(src.replace(a, b, 1))
    try:
        r = subprocess.run(["bash", f"{W}/mutant_cmd.sh"], capture_output=True, text=True, timeout=200)
        out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
        res.append(f"{'KILLED  ' if r.returncode else 'SURVIVED'} {f.split('/')[-1]}: {a[:50]!r} -> {b[:40]!r} | {why} | {out[:160]}")
    finally:
        p.write_text(src)
print("\n".join(res))
print(f"{sum(l.startswith('KILLED') for l in res)} of {len(res)} killed")
