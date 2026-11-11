import sys, subprocess, os, pathlib, shutil
HEAD = "/root/w/head"; ROOT = pathlib.Path(sys.argv[1]); name = sys.argv[2]
P = "custom_components/heatpump_optimizer/"
M = {
 "control": None,
 "a_schedule_days_none": (P+"whatif.py", "return None if live_targets == sim_targets else (live_kwh, sim_kwh)", "return None"),
 "b_horizon_weather": (P+"optimizer.py", "weather = _day_mean_weather(_horizon_weather(series, n_steps), day)", "weather = _horizon_weather(series, n_steps)"),
 "c_one_pass": (P+"optimizer.py", "comfort_targets, start=settled)", "comfort_targets)"),
 "d_sides_swapped": (P+"price_tiles.py", "round(per_month((sim_kwh - live_kwh) * price", "round(per_month((live_kwh - sim_kwh) * price"),
 "e_shifted_at_mean": (P+"coordinator.py", "price_tiles.realised_price(simulated, dt_hours))", "float(np.mean(inputs.forecast.prices)))"),
 "f_service_no_steady": (P+"services.py", "coord.async_simulate(overrides, steady=True)", "coord.async_simulate(overrides)"),
 "g_first_price": (P+"coordinator.py", "*days, float(np.mean(inputs.forecast.prices)), wood_sek", "*days, float(inputs.forecast.prices[0]), wood_sek"),
 "i_held_start_off": (P+"optimizer.py", "        if inputs.held_start:\n", "        if False:\n"),
 "j_kept_key_dropped": (P+"whatif.py", "kept[0] is anchor and kept[1] == key", "kept[0] is anchor"),
 "k_pair_on_schedule": (P+"coordinator.py", ") if steady and days is None else None", ") if steady else None"),
 "l_fuse_settled": (P+"coordinator.py", '"cost_delta_sek_month": simulated.get(whatif.STEADY_KEY)', '"cost_delta_sek_month": simulated.get("monthly_settled_cost_delta")'),
 "m_tile_no_steady": (P+"coordinator.py", 'steady="power_cap_kw" in overrides', 'steady=False'),
 "n_wood_extra_dropped": (P+"price_tiles.py", "* price * horizon_hours / 24.0 + extra, horizon_hours)", "* price * horizon_hours / 24.0, horizon_hours)"),
 "o_shifted_guard": (P+"price_tiles.py", "priced = math.isfinite(shifted_price) and shifted_price > 0.0", "priced = True"),
}
d = ROOT / name
if d.exists(): shutil.rmtree(d)
d.mkdir(parents=True)
subprocess.run(f"git -C {HEAD} archive HEAD | tar -x -C {d}", shell=True, check=True)
m = M[name]
if m:
    f = d / m[0]; t = f.read_text(); assert t.count(m[1]) == 1, (name, t.count(m[1])); f.write_text(t.replace(m[1], m[2]))
env = dict(os.environ, PYTHONPATH="tests/hastub:tests:custom_components")
r = subprocess.run([sys.executable, "tests/features.py"], cwd=d, env=env, capture_output=True, text=True)
out = pathlib.Path("/root/ev/mut") / f"{name}.log"
bad = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("  ok")]
out.write_text(f"mutant {name}: {m}\nrc={r.returncode}\n" + "\n".join(bad[-80:]) + "\nSTDERR-TAIL\n" + r.stderr[-1500:])
shutil.rmtree(d)
print(name, "rc", r.returncode, flush=True)
