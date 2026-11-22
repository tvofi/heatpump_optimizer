"""Reviewer's mutant driver for PR #3728 delta round at 8e98867.
Usage: python3 reviewer_mutant_driver.py <worktree> <mutant-id> <test-script>
Applies one textual mutant, runs the test, prints RESULT and restores."""
import subprocess, sys, os, pathlib
P = "custom_components/heatpump_optimizer/"
MUTANTS = {
 "D1": (P+"wood_fuel.py", "return utc_instant(ts).astimezone(local_tz) if local_tz is not None else ts",
        "return ts.astimezone(local_tz) if local_tz is not None else ts"),
 "D2": (P+"wood_fuel.py", "        return _in_zone(ts, local_tz).date()",
        "        return (ts.astimezone(local_tz) if local_tz is not None else ts).date()"),
 "D3": (P+"wood_fuel.py", "        return _in_zone(ts, local_tz).isoformat()",
        "        return (ts.astimezone(local_tz) if local_tz is not None else ts).isoformat()"),
 "D4": (P+"manual_plan.py", "return utc_instant(value).replace(tzinfo=None)",
        "return value.astimezone().replace(tzinfo=None)"),
 "D5": (P+"sensor.py", 'terms["dhw_extra_kwh"] = volume * band * WATER_SPECIFIC_HEAT * 30.0',
        'terms["dhw_extra_kwh"] = volume * band * (4.187 / 3600.0) * 30.0'),
 "D6": (P+"sensor.py", "    if dhw_enabled_from_config(config):\n        terms[\"dhw_extra_kwh\"]",
        "    if True:\n        terms[\"dhw_extra_kwh\"]"),
}
wt, mid, test = sys.argv[1:4]
path, old, new = MUTANTS[mid]
f = pathlib.Path(wt, path); src = f.read_text()
assert src.count(old) == 1, (mid, src.count(old))
f.write_text(src.replace(old, new))
try:
    r = subprocess.run([sys.executable, test], cwd=wt, capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": "tests/hastub"})
    out = r.stdout + r.stderr
    fails = [l for l in out.splitlines() if l.lstrip().startswith(("FAIL", "✗")) or " FAILED" in l or "Traceback" in l]
    verdict = "KILLED" if r.returncode != 0 else "SURVIVED"
    print(f"RESULT mutant {mid} {test} rc={r.returncode} {verdict}")
    for l in fails[:8]: print("   ", l[:300])
    print("   tail:", out.strip().splitlines()[-1][:300] if out.strip() else "")
finally:
    f.write_text(src)
