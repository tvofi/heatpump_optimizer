import subprocess, sys, pathlib, json
W = pathlib.Path(sys.argv[1]); name = sys.argv[2]
M = {
 "A_comfort_mid_dropped": ("custom_components/heatpump_optimizer/slot_drivers.py",
    "np.clip((floor + half - room) / half, -1.0, 1.0)", "np.clip((floor - room) / half, -1.0, 1.0)"),
 "B_total_signed": ("custom_components/heatpump_optimizer/slot_drivers.py",
    "total = np.abs(push).sum(axis=0)", "total = push.sum(axis=0)"),
 "C_sort_signed": ("custom_components/heatpump_optimizer/slot_drivers.py",
    'rows.sort(key=lambda d: -abs(d["weight"]))', 'rows.sort(key=lambda d: -d["weight"])'),
 "D_coord_away_none": ("custom_components/heatpump_optimizer/coordinator.py",
    "away_floor_drop_c=away_mode.floor_drop_c(ctx._opt_config, self._away_state),", "away_floor_drop_c=None,"),
 "E_margins_out_of_comfort": ("custom_components/heatpump_optimizer/optimizer.py",
    "                comfort_floors = temp_min_bounds\n", ""),
 "F_pk_guard_off": ("custom_components/heatpump_optimizer/slot_drivers.py",
    "    if result.price_known and (i >= len(result.price_known) or not result.price_known[i]):\n        return None\n", ""),
}
path, old, new = M[name]
wt = W / f"m_{name}"
if not wt.exists():
    subprocess.run(["git","-C","/home/user/heatpump_optimizer","worktree","add","--detach",str(wt),"97786d25bf0ba7cc2c56230799a03a919f84da9b","-q"],check=True)
p = wt / path; s = p.read_text(); assert s.count(old) == 1, (name, s.count(old)); p.write_text(s.replace(old, new))
out = {}
for script in sys.argv[3:]:
    r = subprocess.run(["python3", script], cwd=wt, env={**__import__("os").environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True)
    log = r.stdout + r.stderr
    (W/"ev"/f"mut_{name}_{pathlib.Path(script).stem}.log").write_text(log[-20000:])
    fails = [l for l in log.splitlines() if "FAIL" in l][:8]
    out[script] = {"rc": r.returncode, "tail": log.strip().splitlines()[-1:] , "fails": fails}
print(json.dumps({name: out}))
