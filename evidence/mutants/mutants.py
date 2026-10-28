"""Reviewer's mutants for #2894: tests/features.py lines 1..18632 (header to past
the R10-IMMERSION-LATCH block), over a copy of custom_components with one edit."""
import os, shutil, subprocess, sys
HEAD = os.path.expanduser("~/hpo-seats/r10s6/rev-prod-s8/2894"); OUT = sys.argv[1]; name = sys.argv[2]
PS = "custom_components/heatpump_optimizer/pump_signals.py"; CO = "custom_components/heatpump_optimizer/coordinator.py"
M = {
 "NULL": (PS, None, None),
 "BASE": (PS, None, None),
 "NULL2805": (PS, None, None),
 "M3_round_nearest": ("custom_components/heatpump_optimizer/setpoint_check.py", 'floor, rounding="up")', "floor)"),
 "M4_at_threshold": (PS, "actual_kw <= threshold_kw:", "actual_kw < threshold_kw:"),
 "M5_zero_hours": (PS, "hours <= 0.0 or", "hours < 0.0 or"),
 "M6_zero_threshold": (PS, "threshold_kw <= 0.0:", "threshold_kw < 0.0:"),
 "M7_line_guard_off": (CO, "        if resistive_line:\n", "        if False:\n"),
 "M8_epsilon_guard": (CO, "        if resistive_line:\n", "        if resistive_kwh > 1e-6:\n"),
 "X1_both_flags_not_refused": (PS, "        if heat.backup_heater is True:\n            return None\n", ""),
 "X2_no_source_books_immersion": (PS, "    elif immersion_element:\n        line = LINE_IMMERSION\n    else:\n        return None\n", "    else:\n        line = LINE_IMMERSION\n"),
 "X3_latch_ignored": (PS, "    if not latched or hours", "    if hours"),
 "X4_kwh_over_zero": (PS, "    return line, (actual_kw - threshold_kw) * hours", "    return line, actual_kw * hours"),
}
f, old, new = M[name]
d = os.path.join(OUT, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
shutil.copytree(os.path.join(HEAD, "custom_components"), os.path.join(d, "custom_components"))
shutil.copytree(os.path.join(HEAD, "tests"), os.path.join(d, "tests"), ignore=shutil.ignore_patterns("mutation_ledger"))
for x in ("VERSION",): shutil.copy(os.path.join(HEAD, x), d)
if name == "BASE":
    shutil.rmtree(os.path.join(d, "custom_components")); os.makedirs(os.path.join(d, "custom_components"))
    subprocess.run("git -C %s archive 6e5995e51 custom_components | tar -x -C %s" % (HEAD, d), shell=True, check=True)
elif old is not None:
    p = os.path.join(d, f); s = open(p).read(); assert s.count(old) == 1, (name, s.count(old)); open(p, "w").write(s.replace(old, new))
lines = open(os.path.join(HEAD, "tests/features.py")).read().splitlines(True)[:int(os.environ.get("PREFIX", "18632"))]
open(os.path.join(d, "tests/features_prefix.py"), "w").write("".join(lines))
r = subprocess.run([sys.executable, "tests/features_prefix.py"], cwd=d, env=dict(os.environ, PYTHONPATH="tests/hastub"), capture_output=True, text=True, timeout=3000)
out = r.stdout + r.stderr
open(os.path.join(OUT, name + ".log"), "w").write(out)
fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
print(f"RESULT {name}: rc={r.returncode} FAIL={len(fails)} ok={sum(1 for l in out.splitlines() if l.strip().startswith('ok'))}")
for l in fails[:5]: print("   ", l[:200])
shutil.rmtree(d)
