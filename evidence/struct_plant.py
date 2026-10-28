import os, shutil, subprocess, sys
HEAD = os.path.expanduser("~/hpo-seats/r10s6/rev-prod-s8/2887"); OUT = sys.argv[1]; name = sys.argv[2]
F = "custom_components/heatpump_optimizer/thermal_model.py"
NEW = {"revert_fold": "                    c_buf = p.buffer_tank_thermal_mass\n                    if c_buf < 1e-6:\n                        c_buf = 0.04  # the step's own fallback\n",
       "compact_inline": "                    c_buf = p.buffer_tank_thermal_mass if p.buffer_tank_thermal_mass >= 1e-6 else 0.04\n"}[name]
OLD = "                    c_buf = _buffer_capacity(p)\n                valve_row"
d = os.path.join(OUT, "st_" + name); shutil.rmtree(d, ignore_errors=True)
shutil.copytree(HEAD, d, ignore=shutil.ignore_patterns(".scratch", "logs", "node_modules"), symlinks=True)
p = os.path.join(d, F); s = open(p).read(); assert s.count(OLD) == 1
open(p, "w").write(s.replace(OLD, NEW + "                valve_row"))
r = subprocess.run([sys.executable, "tests/structure.py"], cwd=d, capture_output=True, text=True)
print(f"RESULT {name}: rc={r.returncode}", [l.strip() for l in r.stdout.splitlines() if "class_excess_loc" in l and ("ok" in l or "FAIL" in l or "<=" in l or ">" in l)][-1:])
shutil.rmtree(d)
