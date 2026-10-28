import pathlib, subprocess, sys, re
ROOT = pathlib.Path(sys.argv[1]); which = sys.argv[2:]
P = "custom_components/heatpump_optimizer/"
SECTION = """
import sys
sys.path.insert(0, 'tests')
from datetime import timedelta
import numpy as np
from harness import Results
from profiles import solve_inputs
R = Results('2492 section')
src = open('tests/features.py').read()
start = src.index('R.section("3L-G7 \\u2014 monthly savings history")')
end = src.index('import inspect as _sav_inspect', start)
exec(compile(src[start:end], 'features_2492', 'exec'))
sys.exit(R.close('2492'))
"""
MUT = {
 "R0": (None, None, None, "section"),
 "R0F": (None, None, None, "full"),
 "R1": (P+"ledger.py", "1.0 if calibration is None else calibration", "1.0", "section"),
 "R2": (P+"ledger.py", "            planned_kw=pending.get(\"power\"),\n", "", "section"),
 "R3": (P+"ledger.py", "calibrated = SAVINGS_PLAN_LINE in lines or \"savings_baseline\" not in lines", "calibrated = True", "section"),
 "R4": (P+"ledger.py", "if SAVINGS_PLAN_LINE not in lines or plan_kwh < MIN_CALIBRATION_KWH:", "if SAVINGS_PLAN_LINE not in lines or plan_kwh <= 0.0:", "section"),
 "R5": (P+"ledger.py", "actual_sek = self.line(key, \"savings_actual\")[\"sek\"]", "actual_sek = billed_total(self.month_summary(key))[0]", "section"),
 "R6": (P+"ledger.py", "            saved = round(baseline_sek - actual_sek, 2)", "            saved = round(baseline_sek - actual_sek, 2) + 0.01", "section"),
 "R7": (P+"pump_arbiter.py", "    elif row[\"plan\"] is not inp.plan:\n        row[\"planned\"], row[\"plan\"] = duty, inp.plan\n", "", "full"),
 "R8": (P+"optimizer.py", "    if not shortfall > 0.0:\n        return comfort_targets\n    return comfort_targets - shortfall", "    return comfort_targets", "section"),
 "R9": (P+"optimizer.py", "        return max(min(capped, uncapped), -displaced)", "        return capped - min(max(0.0, capped - uncapped), max(0.0, space_baseline_cost))", "section"),
 "R10": (P+"optimizer.py", "        held_cost = float(energy_cost_of(baseline_power))\n", "", "section"),
 "R11": (P+"coordinator.py", "simulated.held_cost - result.held_cost", "simulated.baseline_cost - result.baseline_cost", "full"),
 "R12": (P+"optimizer.py", "        displaced = max(0.0, space_baseline_cost) + max(0.0, -end_cost)", "        displaced = max(0.0, space_baseline_cost)", "section"),
}
def run(kind):
    if kind == "section":
        cmd = [sys.executable, "-c", SECTION]
    else:
        cmd = [sys.executable, "tests/features.py"]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env={"PYTHONPATH": "tests/hastub:tests:custom_components", "PATH": "/usr/bin:/bin:/opt/hpo/venv-ci/bin:/opt/node22/bin", "HOME": str(ROOT)})
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if re.match(r"\s*(FAIL|✗|\[FAIL\])", l)]
    return p.returncode, fails, out
for m in which:
    f, old, new, kind = MUT[m]
    orig = None
    if f:
        path = ROOT / f; orig = path.read_text()
        assert orig.count(old) == 1, (m, orig.count(old))
        path.write_text(orig.replace(old, new))
    try:
        rc, fails, out = run(kind)
        print(f"RESULT {m} {kind} rc={rc} failing={len(fails)}")
        for l in fails[:12]: print("   ", l[:200])
        if rc and not fails: print("   tail:", out[-600:].replace("\n", " | "))
    finally:
        if orig is not None: path.write_text(orig)
    sys.stdout.flush()
