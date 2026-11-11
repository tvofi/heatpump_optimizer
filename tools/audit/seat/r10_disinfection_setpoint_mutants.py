#!/usr/bin/env python3
"""R10-OUTSIDE-DISINFECTION-SETPOINT's named mutants, each run against tests/block_duty.py.

    python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py [NAME ...]

Each mutant is applied to a detached worktree of HEAD (removed after), and
tests/block_duty.py run there under PYTHONPATH=tests/hastub. Prints
<name>: KILLED|SURVIVED and the checks that failed. NULL changes
nothing and must survive; every other mutant must be killed.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = str(Path(__file__).resolve().parents[3])
A = "custom_components/heatpump_optimizer/pump_arbiter.py"
T = "custom_components/heatpump_optimizer/thermal_model.py"
P = "custom_components/heatpump_optimizer/setpoint_check.py"
MUTANTS = [
    ("NULL", A, "", ""),
    ("M1-no-cycle-write", A, "cycle = inp.params.dhw_cycle_temp if booked or inp.disinfecting else None", "cycle = None"),
    ("M2-round-nearest", A, 'return _bounded(inp, "dhw_setpoint", float(cycle), rounding="up")', 'return _bounded(inp, "dhw_setpoint", float(cycle))'),
    ("M3-booking-ignored", A, "if booked or inp.disinfecting else None", "if inp.disinfecting else None"),
    ("M4-hold-ignored", A, "if booked or inp.disinfecting else None", "if booked else None"),
    ("M5-gate-only-excuse", A, 'return not (reading is None or written is None or _differs("dhw_setpoint", reading, written[0]))',
     'return not (reading is None or written is None or _differs("dhw_setpoint", reading, written[0])) and written[0] < float(coord.arbiter_inputs().params.dhw_setpoint) - SETPOINT_TOLERANCE'),
    ("M6-excuse-any-reading", A, 'return not (reading is None or written is None or _differs("dhw_setpoint", reading, written[0]))',
     'return not (reading is None or written is None)'),
    ("M7-flag-ignored", T, "return self.dhw_legionella_temp if self.legionella_cycle_active else None", "return self.dhw_legionella_temp"),
    ("M10-enabled-not-active", T, "return self.dhw_legionella_temp if self.legionella_cycle_active else None",
     "return self.dhw_legionella_temp if self.dhw_legionella_enabled else None"),
    ("M8-cycle-not-max", T, "return None if target is None else max(self.dhw_setpoint, target)", "return target"),
    ("M9-floor-no-disinfection", P, "return floor if disinfection is None else max(floor, float(disinfection))", "return floor"),
]


def main() -> int:
    names = sys.argv[1:] or [m[0] for m in MUTANTS]
    bad = 0
    for name, path, old, new in MUTANTS:
        if name not in names:
            continue
        d = tempfile.mkdtemp()
        subprocess.run(["git", "-C", SRC, "worktree", "add", "-q", "--detach", d, "HEAD"], check=True)
        try:
            f = os.path.join(d, path)
            s = open(f).read()
            if old:
                assert s.count(old) == 1, (name, s.count(old))
                open(f, "w").write(s.replace(old, new))
            r = subprocess.run([sys.executable, "tests/block_duty.py"], cwd=d, capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": "tests/hastub"})
            fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
            print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode}")
            bad += (name == "NULL") == bool(r.returncode)
            for l in fails:
                print("   ", l[:150])
        finally:
            subprocess.run(["git", "-C", SRC, "worktree", "remove", "--force", d])
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
