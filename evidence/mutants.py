"""Reviewer's own targeted mutants for #2887 (bcffa2649 fold + split, and the
three equivalent triages). Each: one exact-once textual replacement in
thermal_model.py of a copy of the head tree; driver = tests/features.py."""
import os, shutil, subprocess, sys
HEAD = os.path.expanduser("~/hpo-seats/r10s6/rev-prod-s8/2887")
OUT = sys.argv[1]
F = "custom_components/heatpump_optimizer/thermal_model.py"
M = {
 # bcffa2649: the folded fallback on the single-zone stability row
 "R1_row_fallback_dropped": ("                    c_buf = _buffer_capacity(p)\n                valve_row",
                             "                    c_buf = p.buffer_tank_thermal_mass\n                valve_row"),
 "R2_row_reads_zero_cbuf_none_path": ("                if c_buf is None:\n                    c_buf = _buffer_capacity(p)\n",
                             "                if c_buf is None:\n                    c_buf = 1e9\n"),
 # the owner of the fallback itself
 "R3_capacity_fallback_dropped": ("    return 0.04 if c_buf < 1e-6 else c_buf", "    return c_buf"),
 "R4_capacity_fallback_doubled": ("    return 0.04 if c_buf < 1e-6 else c_buf", "    return 0.08 if c_buf < 1e-6 else c_buf"),
 "R5_capacity_CMP_BOUND_triaged": ("    return 0.04 if c_buf < 1e-6 else c_buf", "    return 0.04 if c_buf <= 1e-6 else c_buf"),
 # the split
 "R6_headroom_CLAMP_DROP_botpin": ("    headroom_k = np.maximum(0.0, p.buffer_max_temp - T_buf)", "    headroom_k = (p.buffer_max_temp - T_buf)"),
 "R7_dTcap_floor_CLAMP_DROP_triaged": ("    dT_cap = headroom_k / max(dt_hours, 1e-6)", "    dT_cap = headroom_k / dt_hours"),
 "R8_bounded_draw_floor_CLAMP_DROP_triaged": ("        / max(dt_hours, 1e-6)\n    )\n    return np.minimum(drawn", "        / dt_hours\n    )\n    return np.minimum(drawn"),
 "R9_headroom_unused": ("    dT_cap = headroom_k / max(dt_hours, 1e-6)", "    dT_cap = np.inf + 0.0 * headroom_k"),
}
name = sys.argv[2]
old, new = M[name]
d = os.path.join(OUT, name)
if os.path.exists(d): shutil.rmtree(d)
shutil.copytree(HEAD, d, ignore=shutil.ignore_patterns(".git", ".scratch", "logs", "node_modules"), symlinks=True)
p = os.path.join(d, F)
src = open(p).read()
assert src.count(old) == 1, (name, src.count(old))
open(p, "w").write(src.replace(old, new))
env = dict(os.environ, PYTHONPATH="tests/hastub")
r = subprocess.run([sys.executable, "tests/features.py"], cwd=d, env=env, capture_output=True, text=True)
lines = (r.stdout + r.stderr).splitlines()
fails = [l for l in lines if "FAIL" in l]
with open(os.path.join(OUT, name + ".log"), "w") as fh:
    fh.write(r.stdout + r.stderr)
tail = lines[-1] if lines else ""
print(f"RESULT {name}: rc={r.returncode} FAIL-lines={len(fails)} {'KILLED' if r.returncode else 'SURVIVED'} | {tail[:160]}")
for l in fails[:6]: print("   ", l[:220])
shutil.rmtree(d)
