import subprocess, sys, pathlib, os
wt = pathlib.Path(sys.argv[1]); W = sys.argv[2]
M = [
 ("on-gate", "custom_components/heatpump_optimizer/wood_fuel.py", "            bool(on)\n            and cop_f > 0.0", "            True\n            and cop_f > 0.0", "wood_advisor"),
 ("currency-cmp <=", "custom_components/heatpump_optimizer/wood_fuel.py", "and wood_sek < finite_float(price, 0.0) / cop_f", "and wood_sek <= finite_float(price, 0.0) / cop_f", "wood_advisor"),
 ("cop>0 guard off", "custom_components/heatpump_optimizer/wood_fuel.py", "and cop_f > 0.0\n            and wood_sek", "and True\n            and wood_sek", "wood_advisor"),
 ("today break off", "custom_components/heatpump_optimizer/wood_fuel.py", "        if day(ts) != today:\n            break", "        if False:\n            break", "wood_advisor"),
 ("utc day", "custom_components/heatpump_optimizer/wood_fuel.py", "return (ts.astimezone(local_tz) if local_tz is not None else ts).date()", "return ts.date()", "wood_advisor"),
 ("merge off", "custom_components/heatpump_optimizer/wood_fuel.py", "if out and out[-1][1] == ts:", "if False:", "wood_advisor"),
 ("len<2 guard off", "custom_components/heatpump_optimizer/wood_fuel.py", "    if len(timestamps) < 2:\n        return []", "    if False:\n        return []", "wood_advisor"),
 ("lead dropped", "custom_components/heatpump_optimizer/wood_fuel.py", "max(first_start - timedelta(minutes=lead_minutes), now)", "max(first_start, now)", "wood_advisor"),
 ("clip dropped", "custom_components/heatpump_optimizer/wood_fuel.py", "max(first_start - timedelta(minutes=lead_minutes), now)", "first_start - timedelta(minutes=lead_minutes)", "wood_advisor"),
 ("lead clamp max0 dropped", "custom_components/heatpump_optimizer/wood_fuel.py", "    lead = max(\n        0.0,", "    lead = max(\n        -1e9,", "wood_advisor"),
 ("iso local dropped", "custom_components/heatpump_optimizer/wood_fuel.py", "        return (ts.astimezone(local_tz) if local_tz is not None else ts).isoformat()", "        return ts.isoformat()", "wood_advisor"),
 ("count gate (if count)", "custom_components/heatpump_optimizer/wood_fuel.py", "        if count:\n            cheap =", "        if False:\n            cheap =", "wood_advisor"),
 ("cheaper >0 -> >=0", "custom_components/heatpump_optimizer/wood_fuel.py", "cheaper = count > 0", "cheaper = count >= 0", "features"),
 ("coordinator local_tz dropped", "custom_components/heatpump_optimizer/coordinator.py", "            local_tz=dt_util.DEFAULT_TIME_ZONE,\n", "", "wood_advisor"),
 ("sensor windows attr dropped", "custom_components/heatpump_optimizer/binary_sensor.py", "            \"cheaper_windows\": fuel.get(\"cheaper_windows\") or [],\n", "", "wood_advisor"),
 ("bp: count>0 cond dropped", "blueprints/automation/notify_wood_cheaper_window.yaml", "  - \"{{ windows | count > 0 }}\"\n", "", "wood_advisor"),
 ("bp: lighting cond dropped", "blueprints/automation/notify_wood_cheaper_window.yaml", "  - \"{{ state_attr(wood_sensor, 'lighting_start') is not none }}\"\n", "", "wood_advisor"),
 ("bp: future-start dropped", "blueprints/automation/notify_wood_cheaper_window.yaml", "and as_timestamp(w.start) > as_timestamp(now())", "", "wood_advisor"),
 ("bp: notify_on_replan dropped", "blueprints/automation/notify_wood_cheaper_window.yaml", "          - \"{{ notify_on_replan }}\"\n", "", "wood_advisor"),
 ("bp: send-time gate dropped", "blueprints/automation/notify_wood_cheaper_window.yaml", "          - \"{{ now() >= today_at(send_time) }}\"\n", "", "wood_advisor"),
 ("bp: w not in old dropped", "blueprints/automation/notify_wood_cheaper_window.yaml", "if w not in old\n            and", "if", "wood_advisor"),
]
env = dict(os.environ, PYTHONPATH=f"tests/hastub:{W}/jj/site")
for name, f, old, new, t in M:
    p = wt / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"SKIP {name}: anchor count {src.count(old)}"); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, f"tests/{t}.py"], cwd=wt, env=env, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")][:2]
        print(f"{'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {name} [{t}] {fails if fails else out.strip().splitlines()[-1][:120]}", flush=True)
    finally:
        p.write_text(src)
