#!/usr/bin/env python3
"""Reviewer's check that each NEW pin is the check that kills its mutant.

My own driver (fix-review, PR #2819). For each recorded mutant it prints the
FAIL line guard_pins.py produces, so a pin that passes for a coincidental
reason (killed by some other check) is visible.
"""
import os, pathlib, subprocess, sys
ROOT = pathlib.Path.cwd()
SRC = ROOT / "custom_components" / "heatpump_optimizer"
CASES = [
 ("accuracy.py", "            return value if value is not None and value >= lo else None",
                 "            return value if value is not None and value > lo else None", "zero planned draw"),
 ("const.py", "    if volume is None:", "    if False:", "unreadable tank volume"),
 ("coordinator.py", "    return value if value is not None and value >= lo else default",
                    "    return value if value is not None and value > lo else default", "aperture sum at its floor"),
 ("dhw_schedule.py", "    if run is not None and len(ordered) >= 3:",
                     "    if run is not None and len(ordered) > 3:", "contiguous days"),
 ("dhw_schedule.py", "    if run is not None and len(ordered) >= 3:", "    if False:", "contiguous days"),
 ("dhw_schedule.py", "    if total_minutes != 24 * 60:", "    if False:", "midnight keeps 24:00"),
 ("optimizer.py", "    return [bool(on and kw > CHANNEL_ACTIVE_KW) for kw, on in zip(channel, runs)]",
                  "    return [bool(on and kw >= CHANNEL_ACTIVE_KW) for kw, on in zip(channel, runs)]", "active line"),
 ("quiet_windows.py", "    return kw if kw is not None and 0.0 < kw <= p_max else None",
                      "    return kw if kw is not None and 0.0 <= kw <= p_max else None", "ceiling of zero"),
 ("quiet_windows.py", "    return kw if kw is not None and 0.0 < kw <= p_max else None",
                      "    return kw if kw is not None and 0.0 < kw < p_max else None", "at the nameplate"),
 ("sensor.py", "    return None if value is None else round(value - DHW_MIN_TEMP_SETPOINT_MARGIN, 1)",
               "    pass", "DHW minimum ceiling"),
 ("wood_fuel.py", "        if wood_sek < finite_float(price, 0.0) / cop_f:",
                  "        if wood_sek <= finite_float(price, 0.0) / cop_f:", "wood's price"),
 ("wood_fuel.py", "        cop = finite_float(cops[i] if i < len(cops) else 0.0, 0.0)",
                  "        cop = finite_float(cops[i] if i <= len(cops) else 0.0, 0.0)", "COP series shorter"),
]
env = {**os.environ, "PYTHONPATH": "tests/hastub"}
for fname, old, new, expect in CASES:
    p = SRC / fname
    t = p.read_text()
    if t.count(old) != 1:
        print(f"RESULT mutation={fname} PRECONDITION_FAILED occurrences={t.count(old)}"); continue
    p.write_text(t.replace(old, new, 1))
    try:
        r = subprocess.run([sys.executable, "tests/guard_pins.py"], capture_output=True, text=True, env=env)
    finally:
        subprocess.run(["git", "checkout", "--", str(p)], cwd=ROOT, check=True)
    fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
    hit = any(expect in l for l in fails)
    print(f"RESULT mutation={fname} expect={expect!r} pin_is_killer={hit} fails={fails}")
