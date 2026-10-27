#!/usr/bin/env python3
"""Reviewer's re-run of the pin mutation proof (fix-review, PR #2819).

My own driver. For each mutant `mutation_table.py --pin-killed` recorded in
tests/mutation_ledger/killed_by/ for this delta, it checks the recorded `old`
line is present exactly once, applies the mutant, runs tests/guard_pins.py,
restores, and prints rc + failed count. A null control applies a comment-only
edit and must leave rc=0 failed=0. Run from the reviewed worktree root.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path.cwd()
CASES = [
 ("accuracy.py", "            return value if value is not None and value >= lo else None",
                 "            return value if value is not None and value > lo else None"),
 ("const.py", "    if volume is None:", "    if False:"),
 ("coordinator.py", "    return value if value is not None and value >= lo else default",
                    "    return value if value is not None and value > lo else default"),
 ("dhw_schedule.py", "    if run is not None and len(ordered) >= 3:",
                     "    if run is not None and len(ordered) > 3:"),
 ("dhw_schedule.py", "    if run is not None and len(ordered) >= 3:", "    if False:"),
 ("dhw_schedule.py", "    if total_minutes != 24 * 60:", "    if False:"),
 ("optimizer.py", "    return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zip(channel, runs)]",
                  "    return [bool(on and kw >= CHANNEL_ACTIVE_KW) for kw, on in zip(channel, runs)]"),
 ("quiet_windows.py", "    return kw if kw is not None and 0.0 < kw <= p_max else None",
                      "    return kw if kw is not None and 0.0 <= kw <= p_max else None"),
 ("sensor.py", "    return None if value is None else round(value - DHW_MIN_TEMP_SETPOINT_MARGIN, 1)",
               "    pass"),
 ("wood_fuel.py", "        cop = finite_float(cops[i] if i < len(cops) else 0.0, 0.0)",
                  "        cop = finite_float(cops[i] if i <= len(cops) else 0.0, 0.0)"),
 ("wood_fuel.py", "        if wood_sek < finite_float(price, 0.0) / cop_f:",
                  "        if wood_sek <= finite_float(price, 0.0) / cop_f:"),
]
SRC = ROOT / "custom_components" / "heatpump_optimizer"

def run_guard_pins():
    p = subprocess.run([sys.executable, "tests/guard_pins.py"], capture_output=True, text=True,
                       env={**__import__("os").environ, "PYTHONPATH": "tests/hastub"})
    out = p.stdout + p.stderr
    last = [l for l in out.splitlines() if "GUARD PIN" in l or "failed=" in l]
    return p.returncode, (last[-1] if last else out.strip().splitlines()[-1:] or "")

def apply(fname, old, new):
    path = SRC / fname
    text = path.read_text()
    n = text.count(old)
    if n != 1:
        print(f"RESULT mutant={fname} PRECONDITION_FAILED occurrences={n}")
        return None
    path.write_text(text.replace(old, new, 1))
    return path

rc0, tail0 = run_guard_pins()
print(f"RESULT unmutated rc={rc0} tail={tail0!r}")

for fname, old, new in CASES:
    path = apply(fname, old, new)
    if path is None:
        continue
    try:
        rc, tail = run_guard_pins()
    finally:
        subprocess.run(["git", "checkout", "--", str(path)], cwd=ROOT, check=True)
    verdict = "KILLED" if rc != 0 else "SURVIVED"
    print(f"RESULT mutant={fname} rc={rc} {verdict} tail={tail!r}")

# null control: comment-only edit on a production file must not move rc
path = SRC / "accuracy.py"
text = path.read_text()
path.write_text(text.replace("\n", "\n# NULL_CONTROL\n", 1))
try:
    rc, tail = run_guard_pins()
finally:
    subprocess.run(["git", "checkout", "--", str(path)], cwd=ROOT, check=True)
print(f"RESULT null_control_comment rc={rc} tail={tail!r}")
