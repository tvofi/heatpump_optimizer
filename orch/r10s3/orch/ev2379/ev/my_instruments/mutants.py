import subprocess, sys, os, shutil
H = "f4e168719d12f071bbc7771944e9430147a223db"
P = "custom_components/heatpump_optimizer/"
M = {
 "R1_bool_test_dropped": (P+"entity.py", "    if isinstance(value, bool) or not isinstance(value, types):", "    if not isinstance(value, types):"),
 "R2_numpy_unwrap_off": (P+"entity.py", "    if isinstance(value, np.generic):\n        value = value.item()\n    if isinstance(value, bool) or not", "    if False:\n        value = value.item()\n    if isinstance(value, bool) or not"),
 "R3_climate_measured_guard_off": (P+"climate.py", "        if measured is not None:\n            return float(measured)", "        if False:\n            return float(measured)"),
 "R4_gap_rate_cmp_bound": (P+"sensor.py", "    if rate is None or rate <= 0.0:\n        rate = EntryConfig", "    if rate is None or rate < 0.0:\n        rate = EntryConfig"),
 "R5_ha_owner_skip_off": (P+"entity.py", "            if owner.__module__.partition(\".\")[0] == \"homeassistant\":\n                continue", "            if False:\n                continue"),
 "R6_scrub_keys_dict": (P+"entity.py", "            prop = getattr(cls, name, None)", "            prop = cls.__dict__.get(name)"),
 "R7_zone_names_swapped": (P+"entity.py", "            (\"upper_setpoint\", \"upper_floor_setpoint\"),\n            (\"lower_setpoint\", \"lower_floor_setpoint\"),", "            (\"upper_setpoint\", \"lower_floor_setpoint\"),\n            (\"lower_setpoint\", \"upper_floor_setpoint\"),"),
}
name = sys.argv[1]; f, old, new = M[name]
wt = f"/tmp/seat/rev2379/mut/{name}"
repo = "/home/user/heatpump_optimizer"
if os.path.exists(wt):
    subprocess.run(["git","-C",repo,"worktree","remove","--force",wt])
subprocess.run(["git","-C",repo,"worktree","add","-q","--detach",wt,H], check=True)
src = open(os.path.join(wt,f)).read()
assert src.count(old) == 1, (name, src.count(old))
open(os.path.join(wt,f),"w").write(src.replace(old,new))
env = dict(os.environ, PYTHONPATH="tests/hastub"); env.pop("BASH_ENV", None)
out = [f"MUTANT {name}: {f}\n--- {old!r}\n+++ {new!r}\n"]
for t in ["tests/finite_boundary.py", "tests/entities.py"]:
    r = subprocess.run([sys.executable, t], cwd=wt, env=env, capture_output=True, text=True)
    lines = (r.stdout+r.stderr).splitlines()
    fails = [l for l in lines if l.lstrip().startswith(("FAIL","fail","✗")) or "FAILED" in l]
    out.append(f"RESULT {name} {t} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}\n" + "\n".join(fails[:8]) + "\n" + "\n".join(lines[-2:]) + "\n")
open(f"/tmp/seat/rev2379/ev/mutant_{name}.txt","w").write("\n".join(out))
subprocess.run(["git","-C",repo,"worktree","remove","--force",wt])
print("\n".join(out))
