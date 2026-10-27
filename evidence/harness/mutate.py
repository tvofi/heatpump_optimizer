#!/usr/bin/env python3
"""Reviewer-built mutator: apply one production edit, run the committed
self-test, report the arm(s) that went red, restore. Never leaves the tree
mutated: the original bytes are held in memory and written back in a finally."""
import subprocess, sys, pathlib
WT = pathlib.Path("/private/tmp/rev-2883-r2/wt")
F = WT / "tools/audit/merge_throughput.py"
orig = F.read_text()

MUTANTS = [
 ("M1-flow_moves-window", "        if not a <= when <= b:",
  "        if not a <= when < b:"),
 ("M2-flow_verdicts-window", "if a <= v[1] <= b]",
  "if a <= v[1] < b]"),
 ("M3-flow_closed-window", "        if not a <= rs.when(stamp) <= b:",
  "        if not a <= rs.when(stamp) < b:"),
 ("M4-flow_wip-none-guard", "    if roster is None or critical is None:",
  "    if roster is None:"),
 ("M5-flow_closed-json-state",
  '''        try:
            roster = json.loads(rr.stdout)
        except ValueError as e:
            return None, f"{path} at {sha[:12]} is not JSON: {e}"''',
  '''        try:
            roster = json.loads(rr.stdout)
        except ValueError:
            return {}, ""'''),
 ("M6-flow_main-json-catch",
  '''        except ValueError as e:         # json.loads: malformed JSON, not a crash
            roster, why = None, (f"roster unreadable: {roster_ref} is not "
                                 f"JSON: {e}")
''', ""),
 ("M7-board-until-none", "    if until is None:\n        why = (f\"no window end:",
  "    if False:\n        why = (f\"no window end:"),
]

def run():
    return subprocess.run([sys.executable, "-I", str(WT/"tools/audit/merge_throughput.py"),
                           "--self-test"], capture_output=True, text=True, timeout=600)

for name, old, new in MUTANTS:
    if orig.count(old) != 1:
        print(f"SKIP {name}: anchor count {orig.count(old)}")
        continue
    try:
        F.write_text(orig.replace(old, new))
        r = run()
        bad = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
        print(f"RESULT {name}: exit={r.returncode} failing_arms={len(bad)}")
        for l in bad[:4]:
            print("    ", l)
        if r.returncode != 0 and not bad:
            print("     (aborted: traceback/exception)", (r.stderr.strip().splitlines() or [""])[-1][:160])
    finally:
        F.write_text(orig)

print("RESULT restored_clean =", subprocess.run(["git","-C",str(WT),"status","--porcelain"],
      capture_output=True,text=True).stdout.strip() == "")
