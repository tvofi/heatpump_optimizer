"""Revert one line of #1756's production fix in a tree copy.
Usage: fix_mutants.py <tree-root> <mutant>"""

import pathlib
import sys

root = pathlib.Path(sys.argv[1])
m = sys.argv[2]
P = root / "custom_components/heatpump_optimizer"
MUT = {
    "FIX-service-expiry": (
        "services.py",
        "expires_at = utc_shift(now, timedelta(hours=MANUAL_PLAN_WINDOW_HOURS))",
        "expires_at = now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS)",
    ),
    "FIX-build-cap": (
        "manual_plan.py",
        "cap = utc_shift(now, timedelta(hours=MANUAL_PLAN_WINDOW_HOURS))",
        "cap = now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS)",
    ),
    "FIX-step-end": (
        "manual_plan.py",
        "step_end = _instant(utc_shift(ref, step_length))",
        "step_end = _instant(ref + step_length)",
    ),
    "FIX-instants": ("manual_plan.py",
        "        return when.timestamp()\n",
        "        return when.replace(tzinfo=timezone.utc).timestamp()\n"),
    }
f, old, new = MUT[m]
p = P / f
s = p.read_text()
assert s.count(old) == 1, (m, s.count(old))
p.write_text(s.replace(old, new))
print("applied", m, f)
