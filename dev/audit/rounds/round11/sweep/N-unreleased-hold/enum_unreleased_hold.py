#!/usr/bin/env python3
"""Enumerator for class N-unreleased-hold (round 11, D14 steps 3-4).

Universe: every actuator write site (tools/audit/enumerate.py d16-writes) x every
exit (off, unload, remove, duty-mode change, each also mid-disinfection and on
the Modbus select; stale plan; failed restore). Behaviour comes from the D16
finders' harnesses, run here on the tree under test:
  m6_restore.py  -> per (exit, entity) whether the entity ends off its baseline
  cells.py       -> baseline_switch_off (stale-plan exit, supply switch)
  m5_holds.py    -> writes_again_off_restore_{,neutral_}failed_while_off (failed-restore exit)
A seam is a cell left at the optimizer's write. Each seam is mapped to its
owning symbol; cells sharing an owner and mechanism fold into one seam.
Usage: PYTHONPATH=tests/hastub python3 enum_unreleased_hold.py [--perturb all] [--null]
"""
from __future__ import annotations
import re, subprocess, sys
from collections import defaultdict

R = "dev/audit/rounds/round11/D16"
PERT = sys.argv[sys.argv.index("--perturb") + 1] if "--perturb" in sys.argv else None
NULL = "--null" in sys.argv


def run(args):
    p = subprocess.run([sys.executable, *args], capture_output=True, text=True, timeout=230)
    return dict(re.findall(r"^RESULT (\S+)=(\S+)", p.stdout, re.M))


static = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d16-writes"], capture_output=True, text=True).stdout
write_sites = [l for l in static.splitlines() if l.startswith("write ")]
m6 = run([f"{R}/s3/m6_restore.py"] + (["--perturb", PERT] if PERT else []))
m5 = run([f"{R}/s3/m5_holds.py"])
cells = run([f"{R}/s1/cells.py", "--no-gates"])

OWNER = {  # entity -> (owning write symbol, register in off_restore?)
    "switch.hp": "pump_arbiter.switch_supply", "number.freq": "coordinator._command_frequency",
    "number.valve": "coordinator._command_valve_target", "switch.vvc": "coordinator._async_set_pump",
    "select.pump_mode": "pump_arbiter._write", "number.dhw_set": "pump_arbiter._write",
    "number.offset": "heat_curve.write_persistent", "mqtt:ecl110/command": "heat_curve.publish_ecl110_topics",
    "mqtt:ecl110/displace/set": "heat_curve.publish_ecl110_topics", "switch.dis": "disinfection.DisinfectionSwitch",
    "number.water_set": "pump_arbiter._write",
}
held = []
for k, v in m6.items():
    m = re.match(r"(null_)?unrestored_([a-z_]+)__(.+)", k)
    if not m or v != "1" or bool(m.group(1)) != NULL:
        continue
    held.append((m.group(2), m.group(3)))
if not NULL:
    if int(cells.get("baseline_switch_off", "0")) > 0:
        held.append(("stale_plan", "switch.hp"))
    for key, ent in (("writes_again_off_restore_failed_while_off", "space_setpoint"),
                     ("writes_again_off_restore_neutral_failed_while_off", "number.offset")):
        if m5.get(key) == "0":
            held.append(("failed_restore_while_off", ent))
seams = defaultdict(list)
for exit_, ent in sorted(held):
    base = exit_.removesuffix("_disinfecting").removesuffix("_modbus")
    owner = "off_restore.async_restore (no retry while Off)" if base == "failed_restore_while_off" else OWNER.get(ent, ent)
    if exit_ in ("unload_disinfecting", "remove_disinfecting") and ent == "number.dhw_set":
        owner = "pump_arbiter.release (baseline row with the disinfection hold live)"
    seams[(owner, base)].append(f"{exit_}:{ent}")
print(f"write_sites={len(write_sites)} exits=off,unload,remove,duty_change(+_disinfecting,+off_modbus),stale_plan,failed_restore")
for (owner, base), cl in sorted(seams.items()):
    print(f"SEAM {owner} | {base} | {' '.join(cl)}")
print(f"held_cells={len(held)} seams={len(seams)}")
