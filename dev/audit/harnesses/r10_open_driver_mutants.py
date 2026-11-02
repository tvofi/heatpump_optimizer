#!/usr/bin/env python3
"""R10-OPENER-REUSE part 1: each rule of tools/audit/seat/open_driver.py dies alone.

Each mutant is one exact one-occurrence replacement in a COPY of
tools/audit/seat/ (never the tree); the copy's own
`open_driver.py --self-test` is then run and must FAIL. Null control: M0,
nothing mutated, must print failed=0. A pattern not found exactly once aborts.

  M-exact    drop the exact-first rule (P363 (i)): r10-roster-ops-2 resolves to
             R10-ROSTER-OPS and r10-ci-layout-p1 to nothing.
  M-body     drop the body-names-group check on a stripped match.
  M-landed   drop the ledger.py landed check: the on-main topic opens.
  M-omitlast an omitted topic sorts after every listed one (P350).
  M-crit     critical-path topics are not kept ahead of the rest.
  M-seen     mark seen on any rc, not only rc=0 (the stranded-handoff shape).
  M-starved  STARVED prints at any age.
  M-backoff  a failed open is retried every pass.

    python3 dev/audit/harnesses/r10_open_driver_mutants.py

EXPECTED RESULT mutants=8
EXPECTED RESULT survived=0
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEAT = "tools/audit/seat"
TARGET = "open_driver.py"
PLANTS = {
    "M-exact": ("    if up in groups:  # exact match always wins\n", "    if False:\n"),
    "M-body": (" and names_group(body_head, m.group(1).upper())", ""),
    "M-landed": ("        elif main and world.landed(main, sha):\n", "        elif False:\n"),
    "M-omitlast": ("        return max(above, default=-1) + 0.5\n", "        return 1e9\n"),
    "M-crit": ("(cls[x[0]] != 0, pos(x[0])", "(False, pos(x[0])"),
    "M-seen": ("        if rc == 0:\n            seen.add(key)", "        if True:\n            seen.add(key)"),
    "M-starved": ("ct and now - ct > STARVE_S", "ct"),
    "M-backoff": ('fails.get(f"{topic} {sha}", {}).get("next", 0) > now', "False"),
}


def selftest(tree: Path) -> tuple:
    r = subprocess.run([sys.executable, "-I", str(tree / SEAT / TARGET), "--self-test"], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    survived = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["M0", *PLANTS]:
            tree = Path(tmp) / name
            shutil.copytree(ROOT / SEAT, tree / SEAT)
            if name != "M0":
                old, new = PLANTS[name]
                p = tree / SEAT / TARGET
                s = p.read_text()
                if s.count(old) != 1:
                    print(f"ABORT {name}: pattern occurs {s.count(old)} times")
                    return 2
                p.write_text(s.replace(old, new))
            rc, out = selftest(tree)
            failed = sum(1 for l in out.splitlines() if l.startswith("FAIL "))
            if name == "M0":
                print(f"RESULT mutant=M0 failed={failed} verdict={'null-ok' if rc == 0 and not failed else 'NULL-RED'}")
                if rc:
                    return 2
                continue
            dead = rc != 0 and failed > 0
            survived += not dead
            print(f"RESULT mutant={name} failed={failed} verdict={'killed' if dead else 'SURVIVED'}")
    print(f"RESULT mutants={len(PLANTS)}")
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
