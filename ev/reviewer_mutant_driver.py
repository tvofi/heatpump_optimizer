"""Reviewer's mutant driver for #3728 at 0bfce347: one textual edit per mutant, run the
named check script, restore with git checkout, record rc and FAIL lines."""
import os, subprocess, sys
WT = os.path.expanduser("~/wt"); P = "custom_components/heatpump_optimizer/"
S = "# -- round-11 ADR-001 (R11-SEAM-kernel-step)"
END = "# -- N-silent-zero (#2233) and P1 D1-s3-02 (#2236): ingress refuses, never empties --"
BLOCK = ["python3", "tools/audit/seat/features_block.py", "--prelude",
         'exec(open("%s").read())' % os.path.expanduser("~/adapt/prelude.py"), S, END]
WOOD = ["python3", "tests/wood_advisor.py"]
DEBUG = ["python3", "tests/debug_collect.py"]
M_ALL = [
 ("M0", None, None, None, BLOCK),
 ("M0w", None, None, None, WOOD),
 ("R1 covering_index end rule", "plan_step.py", "    return i if now < starts[i] + span else None", "    return i", BLOCK),
 ("R2 plan_step_index last_span dropped", "plan_step.py", "return covering_index(stamps, now, PLAN_STEP, PLAN_STEP)", "return covering_index(stamps, now, PLAN_STEP)", BLOCK),
 ("R3 utc_instant naive branch", "drift.py", "        return value.replace(tzinfo=timezone.utc)\n", "        pass\n", BLOCK),
 ("R4 payload_number finite guard", "entity.py", "if isinstance(value, float) and not math.isfinite(value):", "if False:", BLOCK),
 ("R5 EVIDENCE_KEEP 7", "drift.py", "EVIDENCE_KEEP = 6", "EVIDENCE_KEEP = 7", BLOCK),
 ("R6 sensor water literal", "sensor.py", "volume * band * WATER_SPECIFIC_HEAT * 30.0", "volume * band * (4.187 / 3600.0) * 30.0", BLOCK),
 ("R7 manual_plan._instant timestamp", "manual_plan.py", "return utc_instant(when).timestamp()", "return when.timestamp()", BLOCK),
 ("R8 _in_zone without utc_instant", "wood_fuel.py", "return utc_instant(ts).astimezone(local_tz)", "return ts.astimezone(local_tz)", WOOD),
 ("R9 replay_doc.numeric bool guard", "replay_doc.py", "if isinstance(state, bool) or not isinstance(state, (str, in", "if not isinstance(state, (str, in", DEBUG),
]
import os as _o
M = [m for m in M_ALL if not _o.environ.get('ONLY') or m[0].startswith(_o.environ['ONLY'])]
env = dict(os.environ, PYTHONPATH="tests/hastub", PYTHONDONTWRITEBYTECODE="1")
for name, f, old, new, cmd in M:
    path = os.path.join(WT, P + f) if f else None
    if path:
        src = open(path).read(); n = src.count(old)
        if n < 1:
            print(f"{name}: NOT-APPLIED (anchor count {n})", flush=True); continue
        open(path, "w").write(src.replace(old, new, 1))
    subprocess.run("find . -name __pycache__ -type d -prune -exec rm -rf {} +", shell=True, cwd=WT)
    try:
        r = subprocess.run(cmd, cwd=WT, env=env, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if "FAIL" in l][:6]
        print(f"{name}: rc={r.returncode} tail={out.strip().splitlines()[-1] if out.strip() else ''!r}", flush=True)
        for l in fails: print("    " + l[:300], flush=True)
    finally:
        if path: subprocess.run(["git", "checkout", "--", P + f], cwd=WT)
st = subprocess.run(["git", "status", "--short", "--untracked-files=no"], cwd=WT, capture_output=True, text=True).stdout
print("restored-clean:", st == "", repr(st))
